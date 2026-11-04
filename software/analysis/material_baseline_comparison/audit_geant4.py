#!/usr/bin/env python3
"""Audit failed TGeo step lookups in the corresponding native Geant4 geometry.

Initializes the verified immutable persistent recorder with one diagnostic event;
does not replace the training sample. No geometry or navigation tolerances change.
"""
import argparse
import csv
import importlib.util
import json
from pathlib import Path
import sys

from compare import sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recorder', type=Path, required=True)
    parser.add_argument('--native-module-dir', type=Path, required=True)
    parser.add_argument('--compact', type=Path, required=True)
    parser.add_argument('--factory-dir', type=Path, required=True)
    parser.add_argument('--geant4-include', type=Path, required=True)
    parser.add_argument('--recording', type=Path, required=True)
    parser.add_argument('--diagnostics', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Select a fresh output directory')
    args.output.mkdir(parents=True)
    import numpy as np
    import uproot
    rows = [r for r in csv.DictReader(args.diagnostics.open()) if r['issue'] == 'density']
    classification = json.loads((args.diagnostics.parent/'profiles.root.json').read_text())
    if len(rows) != classification['density_mismatches'] or not rows:
        raise RuntimeError('Audit requires every failed density lookup from a completed classification')
    density_unit = classification['density_unit']
    with uproot.open(args.recording) as source:
        data = source['material_tracks'].arrays(['mat_'+k for k in
            ('x','y','z','dx','dy','dz','step_length','rho','X0','L0')], library='np')
    points = args.output/'points.txt'
    with points.open('w') as stream:
        for row in rows:
            i, j = int(row['track']), int(row['step'])
            origin = np.array([data['mat_'+k][i][j] for k in ('x','y','z')], dtype=float)
            direction = np.array([data['mat_'+k][i][j] for k in ('dx','dy','dz')], dtype=float)
            length = float(data['mat_step_length'][i][j])
            for fraction in (.5, .25, .75, .1, .9, .01, .99):
                point = origin + fraction*length*direction
                stream.write(' '.join(str(x) for x in (i, j, fraction, *point))+'\n')
    import acts.examples.geant4
    import dd4hep
    import ROOT
    sys.path.insert(0, str(args.native_module_dir.resolve()))
    import nodd_material_recording_native as native
    ROOT.gInterpreter.AddIncludePath(str(args.geant4_include.resolve()))
    code = Path(__file__).with_name('audit_geant4.C')
    if not ROOT.gInterpreter.Declare(code.read_text()):
        raise RuntimeError('Cannot compile Geant4 audit')
    finish = native.finish
    audited = False
    def finish_with_audit(handle, *rest):
        nonlocal audited
        if not audited:
            ROOT.auditMaterialGeant4(str(points.resolve()), str((args.output/'lookups.json').resolve()))
            audited = True
        return finish(handle, *rest)
    native.finish = finish_with_audit
    spec = importlib.util.spec_from_file_location('verified_geantino_recorder', args.recorder)
    recorder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(recorder)
    sys.argv = [str(args.recorder), '--compact', str(args.compact), '--factory-dir', str(args.factory_dir),
        '--native-module-dir', str(args.native_module_dir), '--events', '1', '--tracks', '1',
        '--output', str(args.output/'initialization')]
    recorder.main()
    if not audited:
        raise RuntimeError('Audit did not execute')
    lookups = json.loads((args.output/'lookups.json').read_text())
    if len(lookups) != 7*len(rows):
        raise RuntimeError('Incomplete native lookups')
    by_step = {}
    for row in lookups:
        by_step.setdefault((row['track'], row['step']), []).append(row)
    certified = []
    for diagnostic in rows:
        i, j = int(diagnostic['track']), int(diagnostic['step'])
        observations = by_step[(i, j)]
        names = {r['g4_volume'] for r in observations}
        if len(names) != 1 or len(observations) != 7:
            raise RuntimeError('Ambiguous logical-volume assignment')
        for r in observations:
            if (not r['dd_volume_found'] or r['dd_name_matches'] != 1 or
                    r['g4_material'] != r['dd_material'] or
                    not np.isclose(r['g4_density_g_cm3'], r['dd_density_g_cm3'], rtol=5e-6, atol=0)):
                raise RuntimeError('Geant4/DD4hep logical-volume identity mismatch')
            for key, expected in [('rho', r['g4_density_g_cm3']*density_unit),
                                  ('X0', r['g4_X0_mm']), ('L0', r['g4_L0_mm'])]:
                if not np.isclose(data['mat_'+key][i][j], expected, rtol=5e-6, atol=0):
                    raise RuntimeError('Recorded/native Geant4 material signature mismatch')
            if 'ShortStripEndcap' not in r['g4_path'] or r['dd_sensitive']:
                raise RuntimeError('This bounded audit requires a passive short-strip endcap piece')
        certified.append({'track': i, 'step': j, 'volume': observations[0]['g4_volume'],
                          'category': 4, 'path': observations[0]['g4_path']})
    initialization = json.loads((args.output/'initialization/metrics.json').read_text())
    if not initialization.get('completed') or not initialization['lifecycle']['finished']:
        raise RuntimeError('Incomplete initialization')
    report = {'recording_sha256': sha(args.recording), 'diagnostics_sha256': sha(args.diagnostics),
        'audit_python_sha256': sha(__file__), 'audit_cpp_sha256': sha(code),
        'rows': len(rows), 'lookups_sha256': sha(args.output/'lookups.json'),
        'compact_sha256': initialization['compact_sha256'], 'materials_sha256': initialization['materials_sha256'],
        'factories': initialization['factories'], 'certified_steps': certified,
        'scope': 'Only failed TGeo lookups; seven strict interior Geant4 queries per step, matching recorded rho/X0/L0 and unique DD4hep logical-volume material/sensitivity. TGeo disagreement remains a geometry-conversion limitation.'}
    (args.output/'provenance.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
