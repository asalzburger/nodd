#!/usr/bin/env python3
"""Read-only central HCAL material integration for DES037/DES036.

This deliberately bounded study intersects unchanged finite common-module
primitives (including disjoint cuts) with straight eta=0 IP rays in sector 0.
It adds 36 steel plates and the regional 10 mm rear aluminium cover. Rays are
restricted to |phi| <= 0.1 rad, away from regional sector-edge rails and seams;
eta=0 misses regional end flanges. Common-carrier rails are intersected normally.
It does not establish full native assembly validation or engineering acceptance.

No repository files are written. Optional --element-x0 accepts a JSON mapping
of atomic-number strings to mass radiation lengths in g/cm2; each entry may be
a number or {"X0_g_cm2": number, "source_url": "...", ...}. Mixture radiation
lengths use 1/X0 = sum(w_i/X0_i), with retained native elemental mass fractions.
Absent supplied constants remain explicitly unavailable.
"""
import argparse
import collections
import hashlib
import importlib.util
import json
import math
import subprocess
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def subtract(segment, cut):
    a, b = segment
    c, d = cut
    if d <= a or c >= b:
        return [segment]
    out = []
    if c > a:
        out.append((a, min(b, c)))
    if d < b:
        out.append((max(a, d), b))
    return out


def primitive_intervals(kind, dimensions, origin, direction):
    lo, hi = -math.inf, math.inf
    sizes = ([dimensions[k] for k in ('sx', 'sy', 'sz')] if kind == 'box'
             else [None, None, dimensions['length']])
    for axis, size in enumerate(sizes):
        if size is None:
            continue
        if abs(direction[axis]) < 1e-15:
            if abs(origin[axis]) > size / 2:
                return []
        else:
            a, b = sorted(((-size / 2 - origin[axis]) / direction[axis],
                           (size / 2 - origin[axis]) / direction[axis]))
            lo, hi = max(lo, a), min(hi, b)
    if kind == 'tube':
        a = direction[0] ** 2 + direction[1] ** 2
        b = 2 * (origin[0] * direction[0] + origin[1] * direction[1])
        c = origin[0] ** 2 + origin[1] ** 2 - dimensions['rmax'] ** 2
        if a < 1e-20:
            if c > 0:
                return []
        else:
            discriminant = b * b - 4 * a * c
            if discriminant < 0:
                return []
            root = math.sqrt(discriminant)
            a0, b0 = sorted(((-b - root) / (2 * a), (-b + root) / (2 * a)))
            lo, hi = max(lo, a0), min(hi, b0)
    if hi <= lo:
        return []
    segments = [(lo, hi)]
    if kind == 'tube' and dimensions['rmin'] > 0:
        inner = dict(dimensions, rmin=0, rmax=dimensions['rmin'])
        for cut in primitive_intervals(kind, inner, origin, direction):
            segments = [s for segment in segments for s in subtract(segment, cut)]
    return segments


def into_frame(frame, vector):
    return [sum(a * b for a, b in zip(row, vector)) for row in frame]


def part_intervals(part, origin, direction):
    origin = into_frame(part['frame'], [a-b for a,b in zip(origin, part['center_mm'])])
    direction = into_frame(part['frame'], direction)
    intervals = primitive_intervals(part['shape_kind'], part['dimensions_mm'], origin, direction)
    for cut in part['cuts']:
        cut_origin = into_frame(cut['frame'], [a-b for a,b in zip(origin, cut['center_mm'])])
        cut_direction = into_frame(cut['frame'], direction)
        for cut_interval in primitive_intervals(cut['kind'], cut['dimensions_mm'], cut_origin, cut_direction):
            intervals = [s for segment in intervals for s in subtract(segment, cut_interval)]
    return intervals


def controls():
    assert primitive_intervals('box', dict(sx=2,sy=2,sz=2), [0,0,-2], [0,0,1]) == [(1,3)]
    assert primitive_intervals('tube', dict(rmin=0,rmax=1,length=4), [-2,0,0], [1,0,0]) == [(1,3)]
    assert primitive_intervals('tube', dict(rmin=.5,rmax=1,length=4), [-2,0,0], [1,0,0]) == [(1,1.5),(2.5,3)]
    assert subtract((0,4),(1,3)) == [(0,1),(3,4)]
    assert not primitive_intervals('tube', dict(rmin=0,rmax=1,length=4), [2,0,0], [0,0,1])
    return 5


def compare_saved_native_module_rays(unit, native):
    """Replay saved ROOT rays against independent finite-primitive intersections.

    Regional model imports the common unit without its removable reference
    absorber, so compare every other material and explicitly exclude Steel235.
    """
    results=[]
    for reference in native['material_rays']:
        paths=collections.defaultdict(float)
        for part in unit['parts']:
            for a,b in part_intervals(part,reference['origin_mm'],reference['direction']):
                a=max(a,0)
                b=min(b,reference['distance_mm'])
                if b>a:
                    paths[part['material']]+=b-a
        expected={k:v for k,v in reference['material_path_mm'].items() if k!='Steel235'}
        errors={k:paths[k]-expected.get(k,0) for k in paths.keys()|expected.keys()}
        maximum=max(abs(v) for v in errors.values())
        assert maximum<1e-7,(reference['sample'],errors)
        results.append(dict(sample=reference['sample'],maximum_material_path_difference_mm=maximum,
                            excluded_material='Steel235 reference absorber',passed=True))
    return results


def integrate(phi, summary, unit):
    if abs(phi) > .10000000001:
        raise ValueError('Bounded central-ray study requires |phi| <= 0.1 rad')
    direction = [math.sin(phi), 0, math.cos(phi)]  # carrier (tangent, axial, radial)
    intervals = []
    config = unit['config']['carrier']
    width, height, depth = config['size_mm']
    for layer in summary['layers']:
        front = layer['carrier_front_mm']
        for x in layer['columns_mm']:
            for y in layer['rows_mm']:
                cx = x + layer['tangent_phase_mm']
                cy = y + layer['axial_phase_mm']
                # Conservative swept-ray rejection; exact solids are tested next.
                radial_x = [front * math.tan(phi), (front+depth) * math.tan(phi)]
                if max(radial_x) < cx-width/2 or min(radial_x) > cx+width/2 or abs(cy) > height/2:
                    continue
                origin = [-cx, -cy, -front]
                for part in unit['parts']:
                    for a,b in part_intervals(part, origin, direction):
                        a = max(0, a)
                        if b > a:
                            intervals.append(dict(layer=layer['layer'], name=part['name'],
                                                  material=part['material'], s_start_mm=a,
                                                  s_end_mm=b, path_mm=b-a, owner=part['owner']))
        a = layer['steel_front_mm'] / math.cos(phi)
        b = (layer['steel_front_mm'] + summary['config']['steel_mm']) / math.cos(phi)
        intervals.append(dict(layer=layer['layer'], name='regional_steel_plate', material='Steel235',
                              s_start_mm=a,s_end_mm=b,path_mm=b-a,owner='sector'))
    end = summary['summary']['outer_apothem_mm']
    thickness = summary['config']['back_cover_mm']
    a,b = (end-thickness)/math.cos(phi), end/math.cos(phi)
    intervals.append(dict(layer=None,name='regional_rear_cover',material='Aluminium',
                          s_start_mm=a,s_end_mm=b,path_mm=b-a,owner='sector'))
    intervals.sort(key=lambda item:(item['s_start_mm'],item['s_end_mm']))
    # Explicit overlap diagnostic: constituents should have disjoint interiors.
    overlaps=[]
    for i,left in enumerate(intervals):
        for right in intervals[i+1:]:
            if right['s_start_mm'] >= left['s_end_mm']-1e-7:
                break
            if min(left['s_end_mm'],right['s_end_mm'])-right['s_start_mm'] > 1e-7:
                overlaps.append([left['name'],right['name'],left['layer'],right['layer']])
    if overlaps:
        raise AssertionError(('Overlapping material intervals',overlaps))
    paths=collections.defaultdict(float)
    for interval in intervals:
        paths[interval['material']]+=interval['path_mm']
    columns={k:v/10*unit['materials'][k]['density_g_cm3'] for k,v in paths.items()}
    return dict(eta=0,phi_rad=phi,path_mm=dict(paths),column_g_cm2=columns,
                total_column_g_cm2=sum(columns.values()),intervals=intervals,
                positive_volume_interval_overlaps=overlaps)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,required=True,
                        help='Checkout containing the pinned DES036/DES037 HCAL prototype inputs')
    parser.add_argument('--output',type=Path,required=True,
                        help='Destination for the material-ray evidence JSON')
    parser.add_argument('--element-x0',type=Path)
    parser.add_argument('--phi',type=float,nargs='+',default=[0,.03,.1])
    args=parser.parse_args();repo=args.repo.resolve()
    modulepath=repo/'tools/hcal_readout/readout.py'
    spec=importlib.util.spec_from_file_location('_nodd_hcal_readout_muon_study',modulepath)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    unit,_=module.build(absorber=False)
    summarypath=repo/'docs/validation/DES-037/summary.json'
    nativepath=repo/'docs/validation/DES-036/native.json'
    summary=json.loads(summarypath.read_text());native=json.loads(nativepath.read_text())
    fractions=native['material_elemental_mass_fractions']
    x0input=json.loads(args.element_x0.read_text()) if args.element_x0 else {}
    materials={}
    for name,recipe in unit['materials'].items():
        if name not in fractions:continue
        row=dict(recipe,elemental_mass_fractions_by_Z=fractions[name],X0_g_cm2=None,X0_mm=None,
                 x0_status='UNAVAILABLE: no elemental constants supplied',
                 density_source='tools/hcal_readout/readout.py and config.json; unsigned project material recipe',
                 composition_source='docs/validation/DES-036/native.json:material_elemental_mass_fractions')
        missing=[z for z in fractions[name] if z not in x0input]
        if not missing:
            values={z:(entry['X0_g_cm2'] if isinstance(entry,dict) else entry) for z,entry in x0input.items()}
            inverse=sum(w/values[z] for z,w in fractions[name].items())
            row.update(X0_g_cm2=1/inverse,X0_mm=10/(inverse*recipe['density_g_cm3']),
                       x0_status='INFERENCE: elemental mass-fraction mixture',
                       x0_elemental_sources={z:x0input[z] for z in fractions[name]})
        materials[name]=row
    paths=[modulepath,repo/'tools/hcal_readout/config.json',repo/'tools/pixel_barrel_dd4hep/materials.py',
           repo/'detector/config/elements.json',repo/'tools/hcal_barrel/design.py',
           repo/'tools/hcal_barrel/config.json',summarypath,nativepath]
    hashes={str(p.relative_to(repo)):sha(p) for p in paths}
    # Confirm all common-module source identities against retained execution.
    for path,digest in unit['source_sha256'].items():
        assert hashes[path]==digest
        assert summary['source_sha256'][path]==digest
    rays=[integrate(phi,summary,unit) for phi in args.phi]
    for ray in rays:
        if all(materials[k]['X0_mm'] for k in ray['path_mm']):
            ray['x_over_x0_by_material']={k:v/materials[k]['X0_mm'] for k,v in ray['path_mm'].items()}
            ray['x_over_x0']=sum(ray['x_over_x0_by_material'].values())
        else:
            ray['x_over_x0']=None
    output=dict(status='PROTOTYPE / independent analytical straight central HCAL rays',
                scope=__doc__,repo=repo.name,repo_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),
                retained_regional_geometry_execution=summary['execution'],
                source_sha256=hashes,script_sha256=sha(Path(__file__)),
                controls_passed=controls(),
                saved_native_module_ray_comparisons=compare_saved_native_module_rays(unit,native),
                materials=materials,rays=rays,
                element_X0_input=str(args.element_x0) if args.element_x0 else None,
                element_X0_input_sha256=sha(args.element_x0) if args.element_x0 else None,
                limitations=['No complete HCAL native assembly validation',
                             'eta=0 and ordinary sector-0 directions only',
                             'Straight geometry rays; no helix, transport, energy loss or scattering simulation',
                             'External collectors/cables/mounts and unmodeled hardware excluded'])
    args.output.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(dict(output=str(args.output),controls_passed=output['controls_passed'],
                         rays=[{k:v for k,v in r.items() if k not in ['intervals']} for r in rays]),indent=2))


if __name__=='__main__':
    main()
