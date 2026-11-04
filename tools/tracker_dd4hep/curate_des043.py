#!/usr/bin/env python3
"""Retain compact DES043 integration evidence, without geometry/run payloads."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def check(path):
    data = read(path)
    assert data['status'] == 'PASS'
    for name, digest in data['source_hashes'].items():
        assert sha(ROOT / name) == digest, 'Executing source changed: ' + name
    for name, digest in data['audit_sources'].items():
        assert sha(ROOT / name) == digest, 'Evidence producer changed: ' + name
    n = data['native']
    assert n['unique_volume_ids'] == 46682 and n['overlaps'] == 0
    assert n['shape_probes_checked'] == 180288
    assert sum(row['cell_checks'] for row in n['identifiers']) == 64080
    assert data['gen3']['checks']['sensitive_surfaces'] == 46682
    assert data['gen3']['checks']['volumes'] == 120
    assert data['gen3']['checks']['sensor_groups'] == 54
    assert data['geant4']['events'] == 3
    assert data['navigation']['status'] == 'PASS' and data['navigation']['tracks'] == 128
    assert data['navigation_source_comparison']['unique_geometry_ids'] == 46682
    assert data['payload_audit']['status'] == 'PASS'
    print('PASS: compact DES043 native, payload, Gen3 and Geant4 evidence bindings')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build-dir', type=Path)
    p.add_argument('--output', type=Path, default=ROOT / 'docs/validation/DES-043/integration/summary.json')
    p.add_argument('--check', action='store_true')
    a = p.parse_args()
    if a.check:
        check(a.output)
        return
    if not a.build_dir:
        p.error('--build-dir is required for curation')
    b = a.build_dir
    paths = dict(native=b / 'native.json', payload=b / 'payload-audit.json',
                 expected=b / 'detector/tracker/expected.json', compact=b / 'detector/tracker/tracker.xml',
                 materials=b / 'detector/tracker/materials.xml', gen3=b / 'gen3/geometry.json',
                 gen3_comparison=b / 'gen3/source-comparison.json',
                 gen3_native=b / 'gen3/native-report.json',
                 navigation=b / 'navigation-check.json',
                 navigation_comparison=b / 'navigation-source-comparison.json',
                 navigation_surfaces=b / 'navigation/surfaces.json',
                 navigation_steps=b / 'navigation/steps.root',
                 navigation_summary=b / 'navigation/summary.root',
                 geant4_output=b / 'geant4-smoke.root', geant4_log=b / 'geant4-smoke.log')
    n, audit, expected, gen3, comparison = [read(paths[k]) for k in ('native', 'payload', 'expected', 'gen3', 'gen3_comparison')]
    assert all(q['status'] == 'PASS' and not q.get('errors') for q in (n, audit, comparison))
    assert n['execution']['hashes']['expected.json'] == sha(paths['expected'])
    assert n['execution']['hashes']['tracker.xml'] == sha(paths['compact'])
    navigation, navigation_comparison = [read(paths[k]) for k in ('navigation', 'navigation_comparison')]
    assert all(q['status'] == 'PASS' and not q['errors'] for q in (navigation, navigation_comparison))
    # Imported only for curation in the documented analysis environment.
    import uproot
    with uproot.open(paths['geant4_output']) as file:
        events = file['events'].num_entries
        runs = file['runs'].num_entries
    text = paths['geant4_log'].read_text()
    assert events == 3 and runs == 1 and 'Finished run 0 after 3 events' in text
    sources = dict(expected['assembly_source_hashes'])
    for component in expected['components']:
        sources.update(component.get('provenance', {}).get('source_hashes', {}))
    bounded = defaultdict(lambda: dict(placements=0, volume_upper_mm3=0., mass_upper_g=0.))
    for item in n['material_comparison']['bounded_csg']:
        row = bounded[item['material']]
        row['placements'] += 1
        row['volume_upper_mm3'] += item['volume_bounds_mm3'][1]
        row['mass_upper_g'] += item['mass_bounds_g'][1]
    services = expected['service_reconciliation'][0]
    result = dict(
        schema_version=1, id='VAL-DES043-INTEGRATION-2026-11-03', status='PASS',
        source_revision=n['execution']['revision'], source_hashes=sources,
        audit_sources={name: sha(ROOT / name) for name in (
            'tools/tracker_dd4hep/curate_des043.py', 'tools/tracker_dd4hep/audit_payload.py',
            'tools/tracker_dd4hep/export_gen3.py', 'tools/tracker_dd4hep/check_gen3.py',
            'tools/tracker_dd4hep/navigation_smoke.py', 'tools/tracker_dd4hep/check_navigation.py')},
        raw_artifacts_sha256={key: sha(value) for key, value in paths.items()},
        native={key: n[key] for key in ('execution', 'sensitive_comparison', 'identifiers',
            'unique_volume_ids', 'shape_probes_checked', 'probe_counts', 'counts', 'physical_placements',
            'minimum_pixel_passive_clearance_mm', 'mass_policy')},
        payload_audit=audit,
        gen3=dict(checks=gen3['checks'], provenance=gen3['provenance'],
                  source_comparison={key: comparison[key] for key in (
                      'status', 'errors', 'sensitive_comparison', 'unique_geometry_ids', 'volumes')}),
        navigation=navigation,
        navigation_source_comparison={key: navigation_comparison[key] for key in (
            'status', 'errors', 'sensitive_comparison', 'unique_geometry_ids', 'volumes')},
        geant4=dict(status='PASS', events=events, runs=runs, particle='geantino', energy_GeV=1,
                    direction=[1, 0, 1], physics_list='FTFP_BERT', random_seed=62043003,
                    DD4hep='1.38', Geant4='11.4.3', ROOT='6.40.04',
                    evidence='Saved ROOT event/run entries and completed-run log inspected.'),
        services={key: services[key] for key in ('route_totals', 'allocated_payload_mm3',
                  'new_route_payload_oracle_mm3', 'spine_only_payload_mm3')},
        limitations=[
            'Working simulation prototype; no engineering sign-off or acceptance.',
            'Only exact primitive/exclusive material quantities are measured. General CSG lower bound is zero; upper bounds are per primitive. No exact tracker total mass is asserted.',
            'Three geantinos and sparse straight navigation rays are construction/transport smoke checks, not directional material maps, field navigation or tracking performance.',
            'The installed ACTS binaries are fingerprinted; external source HEAD is not asserted as their compiled revision.',
            'ASIC, 8 mm cable, cold thermal interfaces, irradiation and two-phase hydraulics remain unqualified; adverse analytical thermal margin is only 0.333 K.',
            'Existing 2 mm single-particle/ttbar evidence uses the prior physical geometry.',
            'ROOT overlap checker used its default random sampling; no user seed was supplied. Native overlap tolerance is 1e-5 mm.',
            'Full XML, entity inventories, ROOT files, Gen3 JSON and run logs stay local and ignored.'
        ])
    result['native'].update(overlaps=len(n['overlaps']), overlap_tolerance_mm=1e-5,
                            bounded_csg_by_material=dict(bounded))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    check(a.output)


if __name__ == '__main__':
    main()
