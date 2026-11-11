"""Assemble compact PR132 evidence after every required native check completes."""
import argparse
import hashlib
import json
from pathlib import Path
from compare_geant4 import compare


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def basenames(hashes):
    result={Path(p).name:h for p,h in hashes.items()}
    if len(result)!=len(hashes):
        raise ValueError('Ambiguous provenance basenames')
    return result


def curate(work):
    artifacts={}
    def read(name):
        path=work/name
        artifacts[name]=dict(sha256=sha(path),bytes=path.stat().st_size)
        return json.loads(path.read_text())
    full=read('baseline-native.json')
    baseline=read('native-baseline-snapshot-report.json')
    timings=read('comparison-timings.json')
    if full['status']!='PASS' or full['overlaps'] or full['errors']:
        raise ValueError('Fresh full baseline validation has not passed')
    if baseline['status']!='SNAPSHOT' or baseline['total_errors'] or baseline['overlaps'] is not None:
        raise ValueError('Baseline identity snapshot is not the expected supplementary checkpoint')
    full_hashes=full['execution']['hashes']
    repo=Path(__file__).resolve().parents[3]
    if full_hashes.get('validate.py')!=sha(repo/'tools/tracker_dd4hep/validate.py'):
        raise ValueError('Full baseline validator bytes differ from the maintained tolerance contract')
    snapshot_hashes=basenames(baseline['provenance']['sha256'])
    for name,digest in full_hashes.items():
        if name!='validate.py' and snapshot_hashes.get(name)!=digest:
            raise ValueError('Baseline full scan and snapshot input identity differs: '+name)
    if full['execution']['root_version']!=baseline['provenance']['root_version']:
        raise ValueError('Baseline full scan and snapshot ROOT versions differ')
    summaries={}
    preparation={}
    common=timings['matched_identity']['common_sha256']
    for name,digest in snapshot_hashes.items():
        if name in common and common[name]!=digest:
            raise ValueError('Native and timing inputs differ: '+name)
    for variant in ('cache','mother'):
        manifest=read(f'{variant}/reuse-manifest.json')
        preparation[variant]={k:manifest[k] for k in ('module_instances','strict_recipe_sha256',
            'compact_sha256','producer_sha256','source_sha256','mother_envelope_mm','mother_notches_mm')}
        if manifest['module_instances']!=8064:
            raise ValueError('Unexpected short-strip module count')
        for name,digest in manifest['source_sha256'].items():
            if snapshot_hashes.get(name)!=digest:
                raise ValueError('Prepared candidate input differs from native control: '+name)
        report=read(f'native-{variant}.json')
        if report['status']!='PASS' or report['total_errors'] or report['overlaps']:
            raise ValueError('Candidate full native checks have not passed: '+variant)
        identity=report['baseline_comparison']
        if not identity['performed'] or any(identity[k] for k in ('missing','extra','changed')):
            raise ValueError('Original constituent identity not preserved: '+variant)
        if report['mother_instances']!=(8064 if variant=='mother' else 0):
            raise ValueError('Unexpected real-mother instance count')
        hashes=basenames(report['provenance']['sha256'])
        if hashes['tracker.xml']!=timings['matched_identity']['variant_compact_sha256'][variant]:
            raise ValueError('Native/timing compact differs: '+variant)
        for name,digest in snapshot_hashes.items():
            if name!='tracker.xml' and name in hashes and hashes[name]!=digest:
                raise ValueError('Native candidate/baseline common input differs: '+name)
        fields=['status','constituent_placements','unique_native_logical_volumes','mother_instances',
                'unique_packed_ids','shape_probes_checked','sensitive_detelements_checked','baseline_comparison']
        summaries[variant]={k:report[k] for k in fields}
        summaries[variant].update(overlaps=0,material_rays_checked=len(report['rays']))
    if snapshot_hashes['tracker.xml']!=timings['matched_identity']['variant_compact_sha256']['baseline']:
        raise ValueError('Timing baseline differs from full native control')
    sensors=work/'matched-runs/baseline-1/geant4-sensors.json'
    control=json.loads(sensors.read_text())
    g4=[]
    for observation in timings['observations']:
        directory=Path(observation['directory'])
        path=directory/'geant4-sensors.json'
        result=compare(control,json.loads(path.read_text()))
        result.update(variant=observation['variant'],directory=str(directory.relative_to(work)),sha256=sha(path))
        if result['sha256']!=observation['artifact_sha256']['geant4-sensors.json']:
            raise ValueError('Geant4 snapshot changed after timing aggregation')
        g4.append(result)
    return dict(report_id='VAL-PR132-TRACKER-COMPARISON-2026-11-11',status='PASS',
        scope='Isolated short-strip barrel reuse PROTOTYPE; maintained geometry unchanged; no design acceptance',
        native_baseline=dict(full_status=full['status'],snapshot_status=baseline['status'],
            full_scan_input_identity_verified=True,constituent_placements=baseline['constituent_placements'],
            unique_native_logical_volumes=baseline['unique_native_logical_volumes'],
            sensitive_detelements_checked=baseline['sensitive_detelements_checked'],
            unique_packed_ids=baseline['unique_packed_ids'],shape_probes_checked=baseline['shape_probes_checked'],
            material_rays_checked=len(baseline['rays']),overlaps=0),
        maintained_geometry_changed=False,prototype_B_transport_boundaries_changed=True,
        preparation=preparation,native_candidates=summaries,geant4_all_observations=g4,timings=timings,artifacts=artifacts,
        limitations=['PASS describes these bounded numerical checks, not detector acceptance.',
          'No exact general-CSG total-mass claim; sparse material rays are not full response validation.',
          'ACTS conversion/navigation, repeated BeamOn(1), stochastic response and integration remain unqualified.',
          'Instrumented subprocess wall includes inventory, JIT, snapshots, I/O and teardown.',
          'Two observations per variant; ranges are descriptive and other host workload is not measured.'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=curate(args.work.resolve())
    args.output.write_text(json.dumps(result,indent=2)+'\n')
