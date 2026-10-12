#!/usr/bin/env python3
"""DES018: remove only whole rings proved outside a continuous eta envelope."""
import argparse
from collections import Counter
import copy
import datetime
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('support_baseline', ROOT/'tools/pixel_disc_support_variants/study.py')
baseline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(baseline)
sys.path.insert(0, str(ROOT/'tools/module_layout'))
import intersections
sys.path.pop(0)
VARIANTS = ['eight-single', 'four-single-two-quad']


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def inputs():
    own = json.loads(Path(__file__).with_name('inputs.json').read_text())
    for path, expected in own['input_sha256'].items():
        if digest(ROOT/path) != expected:
            raise ValueError(f'Stale frozen input: {path}')
    support, cfg, limits, _ = baseline.inputs()
    if cfg['luminous_half_z_mm'] != own['luminous_half_z_mm']:
        raise ValueError('Luminous envelope disagrees with baseline')
    return own, support, cfg, limits


def control(name):
    return json.loads((ROOT/f'docs/validation/DES-017/{name}-layout.json').read_text())


def placed(name, datum, cfg):
    source = control(name)
    modules = baseline.placed_modules(source['raw_modules'], cfg, datum)
    if datum == cfg['disc_datum_mm'] and modules != source['modules']:
        raise ValueError('Full baseline reconstruction changed retained transforms')
    return modules, source['rings']


def inner_bound(z, own, mode='selected'):
    """Lower track radius at this actual sensor plane, before numerical buffer."""
    dz = abs(z) - own['luminous_half_z_mm']
    if dz <= 0:
        raise ValueError('Sensor plane overlaps luminous envelope')
    arc = dz/math.sinh(own['eta_max'])
    vertex_radius = math.sqrt(2)*own['transverse_vertex_half_box_mm']
    k = intersections.KAPPA_MM*own['max_abs_field_T']/own['pt_min_GeV']
    if mode == 'straight-on-axis':
        return arc
    if mode == 'all-pt-half-turn':
        return 2*arc/math.pi-vertex_radius
    if mode != 'selected':
        raise ValueError('Unknown envelope mode')
    if k*arc >= math.pi:
        raise ValueError('Eta-boundary arc exceeds first half-turn proof domain')
    chord = arc if k == 0 else 2*math.sin(k*arc/2)/k
    return chord-vertex_radius


def corners(patch, inset=0.):
    c, u, v = (np.asarray(patch[key]) for key in ['center_mm', 'u', 'v'])
    return [c+su*(patch['half_u_mm']-inset)*u+sv*(patch['half_v_mm']-inset)*v
            for su in [-1, 1] for sv in [-1, 1]]


def ring_screens(modules, rings, cfg, own, mode='selected'):
    patches = baseline.radial.active_patches(modules, cfg)
    result = []
    for ring in rings:
        selected = [p for p in patches if p['row'] == ring['row']]
        values = [(inner_bound(p['center_mm'][2], own, mode)-max(math.hypot(*c[:2]) for c in corners(p)), p) for p in selected]
        margin, limiting = min(values, key=lambda value: value[0])
        result.append(dict(row=ring['row'], physical_ring=ring['row']+1,
                           minimum_exclusion_margin_mm=margin,
                           retention_buffer_mm=own['radial_retention_buffer_mm'],
                           removable=margin >= own['radial_retention_buffer_mm'],
                           limiting_patch_id=limiting['id'],
                           limiting_plane_z_mm=limiting['center_mm'][2],
                           limiting_inner_bound_mm=inner_bound(limiting['center_mm'][2], own, mode),
                           maximum_active_corner_radius_mm=max(math.hypot(*c[:2]) for p in selected for c in corners(p))))
    return result


def prefix(screens):
    removed = []
    for row in screens:
        if not row['removable']:
            break
        removed.append(row['row'])
    return removed


def first_retained_witness(modules, row, cfg, own):
    """In-scope straight ray to an interior point proves the next ring is needed."""
    choices = []
    for p in baseline.radial.active_patches(modules, cfg):
        if p['row'] != row:
            continue
        for point in corners(p, own['proof_corner_inset_mm']):
            xy = [-math.copysign(own['transverse_vertex_half_box_mm'], value) for value in point[:2]]
            origin = [*xy, math.copysign(own['luminous_half_z_mm'], point[2])]
            delta = point-np.asarray(origin)
            eta = math.asinh(delta[2]/math.hypot(*delta[:2]))
            if abs(eta) <= own['eta_max']:
                choices.append((abs(eta), dict(target_patch_id=p['id'], target_point_mm=point.tolist(),
                    origin_mm=origin, eta=eta, phi=math.atan2(delta[1], delta[0]), pt_GeV=own['pt_min_GeV'], field_T=0., charge=1., cohort='first-retained-ring-witness')))
    if not choices:
        raise ValueError('No reachable witness for first retained ring; do not claim maximal prefix')
    return min(choices, key=lambda value: value[0])[1]


def local_inventory(modules, rings, cfg, support, limits):
    cooling = baseline.cooling(modules, rings, cfg, support)
    services = baseline.service_radius.fixed_services(modules, rings, cfg, limits)
    # Correct physical-ring helper to the actual number of radial chip-row circuits.
    pipe_area = cooling['number_circuits']*2*math.pi*(support['cooling']['transport_OD_mm']/2)**2
    return dict(modules=len(modules), chips=len(baseline.radial.active_patches(modules, cfg)),
                families=dict(Counter(m['family'] for m in modules)),
                cooling=cooling, power_chains=services['power_chains'],
                services=[dict(scenario=s['scenario'], links=s['uplink_command_links'], cables_mm2=s['cables_mm2'], pipes_mm2=pipe_area) for s in services['scenarios']])


def accumulated_services(discs, cfg, limits):
    inp = json.loads((ROOT/cfg['services_input']).read_text())
    barrel = json.loads((ROOT/cfg['barrel_services']).read_text())
    result = []
    inner, outer = limits['trunk_r_mm']
    for name, settings in inp['scenarios'].items():
        local = [next(x for x in d['after']['services'] if x['scenario'] == name) for d in discs]
        sides = []
        for side in ['positive', 'negative']:
            braw = sum(sum(x['scenarios'][name]['terminal_cable_footprint_mm2'].values())+x['scenarios'][name]['terminal_pipe_footprint_mm2'] for x in barrel['sectors'] if x['side'] == side)
            demand = (braw+sum(x['cables_mm2']+x['pipes_mm2'] for x in local[:8]))*settings['demand_multiplier']
            last = (local[8]['cables_mm2']+local[8]['pipes_mm2'])*settings['demand_multiplier']
            cap = math.pi*(outer**2-inner**2)*settings['available_phi_fraction']*settings['packing_fraction']
            neck = math.pi*(limits['flange_neck_outer_mm']**2-inner**2)*settings['available_phi_fraction']*settings['packing_fraction']
            sides.append(dict(side=side, first_eight_disc_demand_mm2=demand, last_disc_bypass_demand_mm2=last,
                              trunk_capacity_mm2=cap, trunk_utilization=demand/cap,
                              inherited_neck_capacity_mm2=neck, inherited_neck_utilization=demand/neck,
                              all_nine_neck_control_utilization=(demand+last)/neck,
                              trunk_pass=demand <= cap, inherited_neck_pass=demand <= neck,
                              all_nine_neck_control_pass=demand+last <= neck))
        result.append(dict(scenario=name, sides=sides))
    return dict(scenarios=result, scope='Actual heterogeneous first eight discs plus barrel, preserving inherited last-disc bypass. All-nine-disc neck is an additional adverse control; bypass routing is unqualified. Fixed capacities, no radius expansion.')


def schedule(name, own, support, cfg, limits):
    result = []
    for datum in cfg['positive_disc_datums_mm']:
        full, rings = placed(name, datum, cfg)
        screens = ring_screens(full, rings, cfg, own)
        removed = prefix(screens)
        kept = [m for m in full if m['row'] not in removed]
        kept_rings = [r for r in rings if r['row'] not in removed]
        witness = first_retained_witness(full, kept_rings[0]['row'], cfg, own)
        check = baseline.support_screen(kept, cfg, limits, support)
        if not check['passed']:
            raise ValueError('Frozen survivor support bounds fail')
        result.append(dict(datum_mm=datum, removed_rows=removed, retained_rows=[r['row'] for r in kept_rings],
                           proof=screens, first_retained_witness=witness,
                           removed_template_module_ids=[m['module_id'] for m in full if m['row'] in removed],
                           survivor_transforms_unchanged=all(m in full for m in kept),
                           before=local_inventory(full, rings, cfg, support, limits),
                           after=local_inventory(kept, kept_rings, cfg, support, limits),
                           support=check,
                           controls={mode:prefix(ring_screens(full, rings, cfg, own, mode)) for mode in ['straight-on-axis', 'all-pt-half-turn']}))
    return dict(positive_discs=result, reflection='Negative discs retain exact z reflection and reversed u as DES017; no renumbering.',
                removed_modules_all_18=2*sum(d['before']['modules']-d['after']['modules'] for d in result),
                removed_chips_all_18=2*sum(d['before']['chips']-d['after']['chips'] for d in result),
                nominal_heat_saved_all_18_W=2*sum(d['before']['cooling']['nominal_W']-d['after']['cooling']['nominal_W'] for d in result),
                accumulated_services=accumulated_services(result, cfg, limits))


def assembly(name, cfg, discs, *, trimmed):
    patches = []
    for k, (side, number) in enumerate([(s, n) for s in [-1, 1] for n in range(9)]):
        disc = discs[number]
        modules, _ = placed(name, disc['datum_mm'], cfg)
        if trimmed:
            modules = [m for m in modules if m['row'] not in disc['removed_rows']]
        for patch in baseline.radial.active_patches(modules, cfg):
            patch.update(id=patch['id']+k*10000, sensor_id=patch['sensor_id']+k*10000,
                         module_id=patch['module_id']+k*10000, layer_id=f'pixel_disc_{side:+d}_{number+1}')
            patch['center_mm'][2] *= side
            if side < 0:
                patch['u'] = [-x for x in patch['u']]
            patches.append(patch)
    if len({p['id'] for p in patches}) != len(patches):
        raise ValueError('Duplicate patch ID')
    return dict(modules=patches)


def tracks(own):
    result = []
    for eta in own['boundary_etas']:
      for side in [-1, 1]:
       for z in [-150., 0., 150.]:
        for x, y in [(-1., -1.), (-1., 1.), (1., -1.), (1., 1.)]:
         for phi in [.173, 2.381]:
          for field in [0., own['max_abs_field_T']]:
           for charge in [-1., 0., 1.]:
            result.append(dict(eta=side*eta, phi=phi, pt_GeV=own['pt_min_GeV'], field_T=field, charge=charge, origin_mm=[x,y,z], cohort='boundary-grid'))
    rng = np.random.default_rng(own['random_seed'])
    for _ in range(own['random_tracks']):
        result.append(dict(eta=float(rng.uniform(-own['eta_max'], own['eta_max'])), phi=float(rng.uniform(-math.pi, math.pi)),
                           pt_GeV=float(10**rng.uniform(math.log10(own['pt_min_GeV']), 2)),
                           field_T=float(rng.choice(own['native_fields_T'])), charge=float(rng.choice([-1.,0.,1.])),
                           origin_mm=[float(rng.uniform(-1,1)),float(rng.uniform(-1,1)),float(rng.uniform(-150,150))],cohort='seeded-off-grid'))
    return result


def witnesses(name, cfg, discs):
    result = []
    for side in [-1, 1]:
        for number, disc in enumerate(discs):
            track = copy.deepcopy(disc['first_retained_witness'])
            track['origin_mm'][2] *= side
            track['eta'] *= side
            track['target_point_mm'][2] *= side
            k = number+(0 if side < 0 else 9)
            track['target_patch_id'] += k*10000
            result.append(track)
    return result


def compare(name, cfg, own, discs):
    before = assembly(name, cfg, discs, trimmed=False)
    after = assembly(name, cfg, discs, trimmed=True)
    common = {p['id']:p for p in before['modules']}
    if not all(p == common[p['id']] for p in after['modules']):
        raise ValueError('Survivor transform or identifier changed')
    cohort = tracks(own)+witnesses(name,cfg,discs)
    observed = []
    for layout in [before, after]:
        observed.append(intersections.track_sensor_hits(layout, cohort, return_patch_hits=True,
                        host_radius_mm=own['host_radius_mm'], host_half_z_mm=own['host_half_z_mm']))
    lost = [i for i,(a,b) in enumerate(zip(*observed)) if set(a) != set(b)]
    if lost:
        raise ValueError(f'In-scope baseline hits lost on tracks {lost[:10]}')
    for i, track in enumerate(cohort):
        if 'target_patch_id' in track and track['target_patch_id'] not in observed[0][i]:
            raise ValueError('First retained ring witness failed to reach its finite patch')
    return dict(tracks=len(cohort), cohort_counts=dict(Counter(t['cohort'] for t in cohort)),
                changed_hit_sets=lost, all_in_scope_patch_hits_preserved=not lost,
                baseline_patch_hits=sum(map(len,observed[0])), trimmed_patch_hits=sum(map(len,observed[1])),
                before_geometry_sha256=json_digest(before), after_geometry_sha256=json_digest(after),
                tracks_sha256=json_digest(cohort), hit_sets_sha256=json_digest(observed),
                scope='Exact active finite-plane roots, same immutable IDs and transforms. Finite samples supplement the continuous exclusion proof; baseline holes remain.')


def run(out):
    own, support, cfg, limits = inputs()
    out.mkdir(parents=True, exist_ok=True)
    report = dict(status=own['status'], inputs=own, variants={})
    for name in VARIANTS:
        selected = schedule(name, own, support, cfg, limits)
        selected['matched_coverage'] = compare(name, cfg, own, selected['positive_discs'])
        report['variants'][name] = selected
        print(json.dumps(dict(variant=name, removed_modules=selected['removed_modules_all_18'], rings=[d['removed_rows'] for d in selected['positive_discs']], matched=selected['matched_coverage']['tracks'])),flush=True)
    paths = [Path(__file__),Path(__file__).with_name('inputs.json')]
    report['provenance'] = dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                               dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),
                               generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=platform.python_version(),numpy=np.__version__,
                               hashes={str(p.relative_to(ROOT)):digest(p) for p in paths}, frozen_inputs=own['input_sha256'])
    (out/'screening.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args().output)
