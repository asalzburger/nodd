"""Supplemental diagnosis; never substitutes events in the frozen paired scan."""
from __future__ import annotations
import argparse
import csv
import gzip
import json
from pathlib import Path
import subprocess
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.muon_layout.wheels_acts.controls import dimension_args
from tools.muon_layout.acts.prepare import sha, write_tracks


def audit(work_root, executable, output):
    work_root, executable, output = map(lambda p: Path(p).resolve(), (work_root, executable, output))
    output.mkdir(parents=True, exist_ok=True)
    report = dict(scope='Supplemental native root-cycle diagnosis. Frozen scan rows and bounds remain unchanged; no completed result is imputed from refinements.',
                  source_revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  source_sha256=sha(__file__), executable_sha256=sha(executable), systems={})
    for system in ('before', 'after'):
        work, run = work_root/system, work_root/(system+'-run')
        c = json.loads((work/'inputs.json').read_text())['configuration']
        with (run/'tracks.csv').open() as stream:
            rows = [r for r in csv.DictReader(stream) if r['status'] not in ('completed', 'field_masked')]
        with np.load(work/'primaries.npz', allow_pickle=False) as f:
            data = dict(f)
        ids = [int(row['track_id']) for row in rows]
        target = output/system
        target.mkdir(exist_ok=True)
        indices = np.flatnonzero(np.isin(data['track_id'], ids))
        write_tracks(target/'primaries.dat', data, indices)
        records = {}
        variants = {'original': [], 'half-step': ['--max-step-m', '.025'],
                    'tight-surface': ['--tolerance-m', '1e-9'],
                    'tight-rk': ['--rk-tolerance-m', '1e-12'],
                    'exhaustive': ['--policy', 'exhaustive']}
        for name, args in variants.items():
            destination = work_root/'failure-audit'/system/name
            destination.mkdir(parents=True, exist_ok=True)
            command = [str(executable), '--geometry', str(work/'geometry.dat'),
                       '--map', str(work/'map.bin'), '--tracks', str(target/'primaries.dat'),
                       '--output-dir', str(destination), '--mode', 'surface-audit', '--audit-roots',
                       '--max-step-m', str(c['max_step_m']), '--tolerance-m', str(c['surface_tolerance_m']),
                       '--rk-tolerance-m', str(c['rk_tolerance_m']), '--max-steps', str(c['max_steps']),
                       '--path-limit-m', str(c['path_limit_m']), *dimension_args(c), *args]
            executed = subprocess.run(command, capture_output=True, text=True, cwd=ROOT)
            if executed.returncode:
                raise RuntimeError(executed.stderr)
            files = {}
            for filename in ('tracks.csv', 'hits.csv', 'root-audit.csv', 'step-audit.csv', 'metadata.json'):
                original = destination/filename
                retained = target/(name+'-'+filename+'.gz')
                retained.write_bytes(gzip.compress(original.read_bytes(), mtime=0))
                files[retained.name] = dict(sha256=sha(retained), decompressed_sha256=sha(original))
            with (destination/'tracks.csv').open() as stream:
                final = list(csv.DictReader(stream))
            with (destination/'step-audit.csv').open() as stream:
                tail = list(csv.DictReader(stream))[-12:]
            records[name] = dict(argv=command, returncode=executed.returncode, tracks=final,
                                 final_native_steps=tail, files=files)
        report['systems'][system] = dict(primary_failed_rows=rows,
            primary_scan_metadata_sha256=sha(run/'metadata.json'),
            primary_ids=ids, supplemental_runs=records,
            primary_bank_sha256=sha(work/'primaries.npz'))
    # Strip only the checkout prefix; retain all numerical options and actual files.
    text = json.dumps(report, indent=2, allow_nan=False).replace(str(ROOT)+'/', '')
    (output/'audit.json').write_text(text+'\n')
    print(json.dumps({k: {n: [t['status'] for t in v['tracks']] for n, v in r['supplemental_runs'].items()}
                      for k, r in report['systems'].items()}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-root', type=Path, required=True)
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    audit(args.work_root, args.executable, args.output)
