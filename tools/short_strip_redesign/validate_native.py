#!/usr/bin/env python3
"""Actual ROOT solid/placement/identifier/overlap audit for DES043 PROTOTYPE.

No composite Capacity() is used: windows and pipe cuts intersect or extend
outside parents, so subtracting their individual volumes would be incorrect.
"""
import argparse
from array import array
from collections import Counter
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

from model import ROOT, sha


def construction_errors(expected):
    """Finite geometry failures are hard gates even if ROOT sees no overlaps."""
    errors = []
    if any(check['failed_rays'] for check in expected['source_coverage']['checks']):
        errors.append('Finite full-phi source coverage screen failed')
    if expected['guard_clearance']['intersecting_rectangle_pairs']:
        errors.append('Finite insert/neighbor-guard footprint collision')
    if expected['thermal_contact_screen']['definite_missing_contacts']:
        errors.append('Missing finite pipe contacts; pipe-plane reach is insufficient')
    return errors


def identifiers(detector, root, dd4hep, sensors, cells):
    readout = detector.readout('ShortStripRedesignHits')
    decoder, segmentation = readout.idSpec().decoder(), readout.segmentation()
    packed = set(); errors = []; checked = 0
    for sensor in sensors:
        fields = root.std.vector('pair<string,int>')()
        for key, value in sensor['ids'].items(): fields.emplace_back(key, value)
        vid = int(readout.idSpec().encode(fields))
        if vid in packed: errors.append('Repeated sensitive volume ID')
        packed.add(vid)
        for key, value in sensor['ids'].items():
            if int(decoder.get(vid, key)) != value: errors.append('Sensitive ID round-trip mismatch')
        for ix, iy in ((-320, -24), (319, 23), (-320, 23), (319, -24), (0, 0)):
            point = dd4hep.Position((ix + .5) * cells[0] * dd4hep.mm, (iy + .5) * cells[1] * dd4hep.mm, 0.)
            cid = int(segmentation.cellID(point, point, vid)); back = segmentation.position(cid)
            if (int(decoder.get(cid, 'x')), int(decoder.get(cid, 'y'))) != (ix, iy):
                errors.append('75um x 2mm cell index mismatch')
            if math.hypot(back.x() - point.x(), back.y() - point.y()) > 1e-9 * dd4hep.mm:
                errors.append('Cell position mismatch')
            checked += 1
    return dict(passed=not errors, errors=errors, unique_volume_ids=len(packed), grid=[640, 48], cells_checked=checked)


def inventory(detector, root, dd4hep, expected):
    lookup = {e['name']: e for e in expected['entities']}; found = {}; sensors = []; counts = Counter(); errors = []
    unit = float(dd4hep.mm)
    def visit(node, parent, inherited):
        volume = node.GetVolume(); name = str(volume.GetName())
        matrix = root.TGeoHMatrix(parent); matrix.Multiply(node.GetMatrix())
        ids = dict(inherited)
        for field in dd4hep.PlacedVolume(node).volIDs(): ids[str(field.first)] = int(field.second)
        if name in lookup:
            if name in found: errors.append('Repeated physical name: ' + name)
            point = array('d', [0., 0., 0.]); matrix.LocalToMaster(array('d', [0., 0., 0.]), point)
            centre = [x / unit for x in point]; entity = lookup[name]; shape = volume.GetShape()
            if any(not math.isfinite(x) for x in centre) or math.dist(centre, entity['center_mm']) > 1e-7:
                errors.append('Nonfinite/mismatched actual centre: ' + name)
            if str(volume.GetMaterial().GetName()) != entity['material']:
                errors.append('Actual material differs: ' + name)
            if bool(shape.IsA().InheritsFrom('TGeoCompositeShape')) != (entity['cuts'] > 0):
                errors.append('Expected explicit CSG windows/cuts differ: ' + name)
            found[name] = dict(shape=shape, node=node, centre_mm=centre)
            counts[entity['role']] += 1
            if dd4hep.Volume(volume).isSensitive():
                rotation = matrix.GetRotationMatrix()
                sensor = dict(name=name, center_mm=centre, ids=ids,
                    u=[float(rotation[3 * j]) for j in range(3)],
                    v=[float(rotation[3 * j + 1]) for j in range(3)],
                    normal=[float(rotation[3 * j + 2]) for j in range(3)])
                if ids != entity['ids']: errors.append('Actual physical IDs differ: ' + name)
                for axis in ('u', 'v', 'normal'):
                    if math.dist(sensor[axis], entity[axis]) > 1e-9: errors.append('Sensor frame differs: ' + name)
                actual_size = [2 * float(shape.GetDX()) / unit, 2 * float(shape.GetDY()) / unit, 2 * float(shape.GetDZ()) / unit]
                if math.dist(actual_size, entity['size_mm']) > 1e-7: errors.append('Active silicon dimensions differ: ' + name)
                sensors.append(sensor)
        for index in range(volume.GetNdaughters()): visit(volume.GetNode(index), matrix, ids)
    visit(detector.manager().GetTopNode(), root.TGeoHMatrix(), {})
    if set(found) != set(lookup): errors.append('Missing required module/cooling/support solids')
    if dict(counts) != expected['counts']: errors.append('Actual component payload counts differ')
    probes = 0
    for probe in expected['probes']:
        actual = found.get(probe['name'])
        if actual is None: continue
        contains = bool(actual['shape'].Contains(array('d', [x * unit for x in probe['point_mm']])))
        if contains != probe['inside']: errors.append('Cold/backing window is not open: ' + probe['name'])
        probes += 1
    return dict(counts=dict(counts), sensors=sensors, errors=errors, window_probes=probes,
                probe_counts=dict(Counter(p['reason'] for p in expected['probes'])),
                solid_count=len(found), composite_count=sum(e['cuts'] > 0 for e in expected['entities']))


def run(args):
    import ROOT as R
    import dd4hep
    R.gROOT.SetBatch(True)
    if R.gSystem.Load(str(args.library.resolve())) < 0: raise RuntimeError('Cannot load isolated generic factory')
    expected = json.loads(args.expected.read_text())
    expected_digest = sha(args.expected)
    if sha(args.compact) != expected['compact_sha256']: raise ValueError('Generated compact changed')
    for name, digest in expected['generated_artifact_sha256'].items():
        if sha(args.compact.parent/name) != digest: raise ValueError('Generated compact/materials changed: '+name)
    for relative, digest in expected['provenance'].items():
        if sha(ROOT / relative) != digest: raise ValueError('Generated source/input provenance changed: ' + relative)
    detector = dd4hep.Detector.getInstance()
    try:
        detector.fromXML(str(args.compact.resolve()))
        actual = inventory(detector, R, dd4hep, expected)
        ids = identifiers(detector, R, dd4hep, actual['sensors'], expected['cell_mm'])
        errors = actual['errors'] + ids['errors']
        manager = detector.manager(); manager.CheckOverlaps(1e-5 * dd4hep.mm)
        overlaps = [dict(description=str(x.GetTitle()), penetration_mm=float(x.GetOverlap()) / dd4hep.mm)
                    for x in manager.GetListOfOverlaps()]
        if overlaps: errors.append(f'{len(overlaps)} actual ROOT overlaps')
        errors.extend(construction_errors(expected))
        thermal_misses = expected['thermal_contact_screen']['definite_missing_contacts']
        for relative,digest in expected['provenance'].items():
            if sha(ROOT/relative) != digest: errors.append('Executing source changed during native validation: '+relative)
        if sha(args.expected) != expected_digest: errors.append('Expected geometry record changed during validation')
        report = dict(status='PASS' if not errors else 'FAIL', errors=errors,
            engineering_status='BLOCKED missing pipe contacts' if thermal_misses else 'UNQUALIFIED',
            scope='Actual isolated module and cold-petal construction; geometry PASS is separate from engineering/thermal qualification',
            counts=actual['counts'], solid_count=actual['solid_count'], composite_count=actual['composite_count'],
            window_probes=actual['window_probes'], identifiers=ids, disc_layers=expected['disc_layers'],
            probe_counts=actual['probe_counts'],
            overlap_tolerance_mm=1e-5, overlaps=overlaps, source_coverage=expected['source_coverage'],
            thermal_contact_screen=expected['thermal_contact_screen'],
            guard_clearance=expected['guard_clearance'],
            capacity_policy='No stochastic composite capacities or invalid sum-of-cuts mass claims. No native total mass is asserted.',
            provenance=dict(source_revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                initial_contract_revision=expected['initial_contract_revision'], generation_source_revision=expected['generation_source_revision'],
                compact_sha256=sha(args.compact), expected_sha256=sha(args.expected), library_sha256=sha(args.library),
                validator_sha256=sha(__file__), generated_source=expected['provenance'],
                root_version=str(R.gROOT.GetVersion()), python=platform.python_version(), command=sys.argv),
            limitations=expected['limitations'])
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if args.export_root:
            path = args.output.with_suffix('.root'); manager.Export(str(path.resolve())); report['root_sha256'] = sha(path)
        args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
        print(json.dumps(dict(status=report['status'], sensors=len(actual['sensors']), overlaps=len(overlaps), missing_pipe_contacts=thermal_misses)))
        return 0 if not errors else 1
    finally:
        dd4hep.Detector.destroyInstance()
        if R.gGeoManager: R.gGeoManager.Delete()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('compact', 'expected', 'library', 'output'): parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--export-root', action='store_true')
    raise SystemExit(run(parser.parse_args()))
