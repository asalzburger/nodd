"""Native shape/material/mass/overlap and joint-navigation audit of isolated routes."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import subprocess

from routing import ROOT, dot, save, sha


def inputs(compact, expected):
    data = json.loads(expected.read_text())
    for path, digest in data['source_sha256'].items():
        if sha(ROOT/path) != digest: raise ValueError('Stale routing source: '+path)
    for name, digest in data['artifact_sha256'].items():
        if sha(compact.parent/name) != digest: raise ValueError('Stale routing artifact: '+name)
    if sha(compact) != data['artifact_sha256']['routing.xml']: raise ValueError('Unexpected routing compact')
    return data


def audit(args):
    import ROOT as R
    import dd4hep
    data = inputs(args.compact, args.expected)
    R.gROOT.SetBatch(True); R.EnableImplicitMT(1); R.gRandom.SetSeed(data['config']['overlap_seed'])
    if R.gSystem.Load(str(args.library.resolve())) < 0: raise RuntimeError('Routing factory load failed')
    detector = dd4hep.Detector.getInstance(); detector.fromXML(str(args.compact.resolve()))
    mm = float(dd4hep.mm); manager = R.gGeoManager
    root = detector.detector('LArRouting'+data['variant'].title()).placement().ptr().GetVolume()
    expected_pieces = [(path, segment, core) for path in data['paths'] for segment in path['segments'] for core in (False, True)]
    errors = []; totals = defaultdict(lambda: dict(volume_mm3=0., mass_g=0.)); max_error = 0.
    def check(actual, expected, label, tolerance=1e-7):
        nonlocal max_error
        error = abs(float(actual)-expected); max_error = max(max_error, error)
        if not math.isfinite(float(actual)) or error > tolerance: errors.append(label)
    if root.GetNdaughters() != len(expected_pieces): raise ValueError('Native route placement count differs')
    for index, (path, segment, core) in enumerate(expected_pieces):
        node = root.GetNode(index); volume = node.GetVolume(); solid = volume.GetShape(); material = volume.GetMaterial()
        name = path['name']+f'_s{segment["index"]}'+('_core' if core else '_wall')
        if str(volume.GetName()) != name or str(solid.ClassName()) != 'TGeoCtub': raise ValueError('Native routing name/shape differs')
        if volume.GetNdaughters() or dd4hep.Volume(volume).isSensitive(): raise ValueError('Unexpected routing daughter or sensitivity')
        matrix = node.GetMatrix(); translation = matrix.GetTranslation(); rotation = matrix.GetRotationMatrix()
        for i in range(3):
            check(translation[i]/mm, segment['center_mm'][i], 'translation')
            for j in range(3): check(rotation[3*i+j], segment['frame'][j][i], 'rotation', 1e-12)
        determinant = dot(segment['frame'][0], [segment['frame'][1][1]*segment['frame'][2][2]-segment['frame'][1][2]*segment['frame'][2][1],
            segment['frame'][1][2]*segment['frame'][2][0]-segment['frame'][1][0]*segment['frame'][2][2],
            segment['frame'][1][0]*segment['frame'][2][1]-segment['frame'][1][1]*segment['frame'][2][0]])
        check(determinant, 1., 'proper transform', 1e-12)
        inner = 0. if core else data['adjusted_radii_mm']['inner']
        outer = data['adjusted_radii_mm']['inner' if core else 'outer']
        check(solid.GetRmin()/mm, inner, 'inner radius'); check(solid.GetRmax()/mm, outer, 'outer radius')
        check(solid.GetDz()/mm, segment['length_mm']/2, 'half length')
        for i in range(3):
            check(solid.GetNlow()[i], segment['low_normal_local'][i], 'lower miter normal', 1e-12)
            check(solid.GetNhigh()[i], segment['high_normal_local'][i], 'upper miter normal', 1e-12)
        # Centered circular annuli integrate each tilted end-plane's linear
        # contribution to zero. The exact volume is cross section x axis length.
        capacity = math.pi*((solid.GetRmax()/mm)**2-(solid.GetRmin()/mm)**2)*2*solid.GetDz()/mm
        native_capacity = solid.Capacity()/mm**3
        if abs(native_capacity-capacity) > max(1e-7, capacity*1e-10): errors.append('native CutTube capacity')
        expected_material = 'PrototypeNitrogenTwoPhase' if core else 'lArCaloSteel'
        if str(material.GetName()) != expected_material: errors.append('native material name')
        recipe = data['materials'][expected_material]; check(material.GetDensity(), recipe['density_g_cm3'], 'density', 1e-12)
        fractions = ({int(material.GetElement(i).Z()):float(material.GetWmixt()[i]) for i in range(material.GetNelements())}
                     if material.IsMixture() else {int(material.GetZ()):1.})
        wanted = {7:1.} if core else {26:.7175, 24:.19, 28:.0925}
        if set(fractions) != set(wanted) or any(abs(fractions[z]-v)>1e-12 for z,v in wanted.items()): errors.append('native elemental mass fractions')
        totals[expected_material]['volume_mm3'] += capacity
        totals[expected_material]['mass_g'] += capacity*material.GetDensity()/1000
    for name, actual in totals.items():
        for key in ('volume_mm3', 'mass_g'):
            expected = data['material_totals'][name][key]
            if abs(actual[key]-expected) > max(1e-6, expected*1e-10): errors.append('material total:'+name+':'+key)
    probes = 0; crossings = 0; maximum_step_error = 0.
    for probe in data['joint_probes']:
        point = probe['point_mm']; node = manager.FindNode(*(x*mm for x in point))
        if not node or str(node.GetVolume().GetMaterial().GetName()) != probe['material']:
            errors.append('joint point material'); continue
        probes += 1
        if probe['sign'] == -1:
            normal = probe['crossing_normal']; distance = probe['expected_boundary_distance_mm']
            manager.InitTrack(*(x*mm for x in point), *normal)
            manager.FindNextBoundaryAndStep(2*distance*mm)
            error = abs(manager.GetStep()/mm-distance); maximum_step_error = max(maximum_step_error, error)
            if error > 1e-6: errors.append('joint boundary distance')
            crossings += 1
    manager.CheckOverlaps(data['config']['overlap_tolerance_mm']*mm)
    overlaps = int(manager.GetListOfOverlaps().GetEntries())
    if overlaps: errors.append('native overlaps/extrusions')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    root_file = args.output.with_suffix('.root'); manager.Export(str(root_file))
    result = dict(status='PASS' if not errors else 'FAIL', errors=errors,
        scope='Isolated pipe component; explicit cut tubes, material recipes/masses, all joints and full native overlaps; no integrated fit',
        variant=data['variant'], route_count=data['route_count'], physical_material_pieces=len(expected_pieces),
        material_totals=dict(totals), joint_material_points_checked=probes, joint_boundary_crossings_checked=crossings,
        maximum_joint_boundary_distance_error_mm=maximum_step_error, maximum_shape_pose_numeric_delta=max_error,
        overlaps=overlaps, overlap_tolerance_mm=data['config']['overlap_tolerance_mm'], overlap_seed=data['config']['overlap_seed'],
        root_sha256=sha(root_file), compact_sha256=sha(args.compact), expected_sha256=sha(args.expected),
        library_sha256=sha(args.library), auditor_sha256=sha(__file__),
        source_revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        ROOT_version=R.gROOT.GetVersion(), constituent_volume_method='Native CutTube radii/normals, exact centered-annulus integral, checked against native Capacity()')
    save(args.output, result); print(json.dumps(result, indent=2))
    # Destroy native geometry while ROOT's thread state still exists. The
    # retained initial probe exposed the known interpreter-shutdown mutex error.
    R.DisableImplicitMT(); dd4hep.Detector.destroyInstance()
    return not not errors


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('compact', 'expected', 'library', 'output'): p.add_argument('--'+name, type=Path, required=True)
    raise SystemExit(audit(p.parse_args()))
