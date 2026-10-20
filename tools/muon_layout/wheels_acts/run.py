"""Run each paired system only after its executed native control gate passes."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import json
from pathlib import Path
import subprocess
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.muon_layout.acts.prepare import sha, save, write_tracks
from tools.muon_layout.acts.controls import repository_paths
from tools.muon_layout.wheels_acts.controls import prepared, dimension_args


def run(work, executable, output, controls, workers=4):
    work, executable, output, controls = [Path(p).resolve() for p in (work, executable, output, controls)]
    inputs = prepared(work)
    c = inputs['configuration']
    gate = json.loads(controls.read_text())
    if not gate.get('passed') or gate['executable_sha256'] != sha(executable):
        raise ValueError('Executed native control gate failed or executable changed')
    if gate['preparation_sha256'] != sha(work/'inputs.json'):
        raise ValueError('Prepared input changed after native controls')
    for name, digest in gate['source_sha256'].items():
        if sha(ROOT/name) != digest:
            raise ValueError('Native control source changed: '+name)
    sources = [p for p in Path(__file__).parent.iterdir() if p.suffix in ('.py', '.json', '.txt')]
    sources += [ROOT/'tools/muon_layout/acts/propagate.cpp', ROOT/'tools/muon_layout/acts/controls.py',
                ROOT/'tools/muon_layout/acts/prepare.py', ROOT/'tools/muon_layout/acts/analyze.py',
                ROOT/'tools/muon_layout/geometry.py']
    fingerprints = {str(p.relative_to(ROOT)): sha(p) for p in sources}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    clean = True
    for name, digest in fingerprints.items():
        result = subprocess.run(['git', 'show', revision+':'+name], cwd=ROOT, capture_output=True)
        if result.returncode or __import__('hashlib').sha256(result.stdout).hexdigest() != digest:
            clean = False
    if not clean:
        raise ValueError('Freeze the executed source in Git before the production scan')
    with np.load(work/'primaries.npz', allow_pickle=False) as source:
        data = dict(source)
    output.mkdir(parents=True, exist_ok=True)
    cases = [(p, q) for p in c['momentum_GeV'] for q in c['charge_e']]
    commands = []
    for index, (p, q) in enumerate(cases):
        target = output/f'case-{index:02d}'
        target.mkdir(exist_ok=True)
        ids = np.flatnonzero((data['momentum_GeV'] == p) & (data['charge'] == q))
        write_tracks(target/'input.dat', data, ids)
        commands.append([str(executable), '--geometry', str(work/'geometry.dat'),
                         '--map', str(work/'map.bin'), '--tracks', str(target/'input.dat'),
                         '--output-dir', str(target), '--mode', 'surface-audit',
                         '--max-step-m', str(c['max_step_m']),
                         '--tolerance-m', str(c['surface_tolerance_m']),
                         '--rk-tolerance-m', str(c['rk_tolerance_m']),
                         '--path-limit-m', str(c['path_limit_m']),
                         '--max-steps', str(c['max_steps']), *dimension_args(c)])

    def execute(command):
        destination = Path(command[command.index('--output-dir')+1])
        start = time.perf_counter()
        result = subprocess.run(command, text=True, capture_output=True, cwd=ROOT)
        (destination/'execution.log').write_text(result.stdout+result.stderr)
        if result.returncode:
            raise RuntimeError(f'Native shard failed {result.returncode}: {destination}')
        return time.perf_counter()-start

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        durations = list(pool.map(execute, commands))
    shards = [output/f'case-{i:02d}' for i in range(len(cases))]
    for name in ('hits.csv', 'tracks.csv'):
        with (output/name).open('w') as target:
            header = None
            for directory in shards:
                with (directory/name).open() as source:
                    actual = next(source)
                    if header is None:
                        header = actual
                        target.write(header)
                    elif actual != header:
                        raise ValueError('Native shard schema changed')
                    for line in source:
                        target.write(line)
    for name in ('geometry.csv', 'geometry-corners.csv'):
        if len({sha(d/name) for d in shards}) != 1:
            raise ValueError('Native shard geometry differs')
        (output/name).write_bytes((shards[0]/name).read_bytes())
    metadata = [json.loads((d/'metadata.json').read_text()) for d in shards]
    combined = dict(metadata[0])
    for key in ['tracks', 'raw_native_hits', 'field_queries', 'navigation_refreshes', 'navigation_candidates',
                'native_root_events', 'native_finite_face_checks', 'outside_footprint_chamber_support_roots',
                'native_negative_corrections_preserved', 'curvature_guard_caps', 'curvature_guard_plane_checks',
                'near_tolerance_parallel_face_ambiguities']:
        combined[key] = sum(m[key] for m in metadata)
    mins = [m['minimum_curvature_guard_step_m'] for m in metadata if m['minimum_curvature_guard_step_m'] is not None]
    combined['minimum_curvature_guard_step_m'] = min(mins) if mins else None
    combined['max_track_curvature_bound_per_m'] = max(m['max_track_curvature_bound_per_m'] for m in metadata)
    combined['track_status_counts'] = {}
    for m in metadata:
        for key, count in m['track_status_counts'].items():
            combined['track_status_counts'][key] = combined['track_status_counts'].get(key, 0)+count
    combined.update(system=c['system'], source_revision=revision, source_files_match_revision=clean,
                    source_files_sha256=fingerprints, executable_sha256=sha(executable),
                    controls_sha256=sha(controls), preparation_sha256=sha(work/'inputs.json'),
                    elapsed_seconds=time.perf_counter()-started, independent_workers=workers,
                    serial_shard_elapsed_seconds=durations, argv=commands, shard_metadata=metadata,
                    analysis_runtime=dict(python=sys.version.split()[0], numpy=np.__version__))
    if any(sha(ROOT/name) != digest for name, digest in fingerprints.items()):
        raise ValueError('Executed source changed during acquisition')
    with (output/'tracks.csv').open() as stream:
        ids = [int(row['track_id']) for row in csv.DictReader(stream)]
    if ids != data['track_id'].tolist():
        raise ValueError('Generated denominator/order not retained')
    save(output/'metadata.json', repository_paths(combined))
    print(json.dumps(dict(system=c['system'], tracks=len(ids), raw_native_hits=combined['raw_native_hits'],
                          elapsed_seconds=combined['elapsed_seconds'], source_revision=revision), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--controls', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    run(args.work, args.executable, args.output, args.controls, args.workers)
