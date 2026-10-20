"""Run isolated native ACTS processes; preserve every generated row and event."""
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
from tools.muon_layout.acts.prepare import configuration, save, sha, write_tracks


def run(work, executable, output, controls, workers=4):
    work, output = Path(work).resolve(), Path(output).resolve()
    executable = Path(executable).resolve()
    control = json.loads(Path(controls).read_text())
    if control.get('passed') is not True:
        raise ValueError('executed native controls must pass before the scan')
    if control.get('executable_sha256') != sha(executable):
        raise ValueError('native executable changed since the executed controls')
    if control.get('configuration_sha256') != sha(Path(__file__).parent/'config.json'):
        raise ValueError('study configuration changed since the executed controls')
    c = configuration()
    source_files=[Path(__file__).parent/name for name in ('run.py','prepare.py','config.json','CMakeLists.txt','propagate.cpp')]
    fingerprints={str(p.relative_to(ROOT)):sha(p) for p in source_files}
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    tracked=set(subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines())
    clean=(set(fingerprints)<=tracked and subprocess.run(['git','diff','--quiet','HEAD','--',*fingerprints],cwd=ROOT).returncode==0)
    with np.load(work/'primaries.npz', allow_pickle=False) as f:
        data = dict(f)
    output.mkdir(parents=True, exist_ok=True)
    cases = [(p,q) for p in c['momentum_GeV'] for q in c['charge_e']]
    commands = []
    for index, (p,q) in enumerate(cases):
        ids = np.flatnonzero((data['momentum_GeV']==p)&(data['charge']==q))
        target = output/f'case-{index:02d}'
        target.mkdir(exist_ok=True)
        write_tracks(target/'input.dat', data, ids)
        commands.append([str(executable), '--geometry', str(work/'geometry.dat'),
                         '--map', str(work/'map.bin'), '--tracks', str(target/'input.dat'),
                         '--output-dir', str(target), '--mode', 'surface-audit',
                         '--max-step-m', str(c['max_step_m']),
                         '--tolerance-m', str(c['surface_tolerance_m']),
                         '--rk-tolerance-m', str(c['rk_tolerance_m']),
                         '--path-limit-m', str(c['path_limit_m']),
                         '--max-steps', str(c['max_steps'])])
    def execute(command):
        destination = Path(command[command.index('--output-dir')+1])
        start = time.monotonic()
        result = subprocess.run(command, text=True, capture_output=True)
        (destination/'execution.log').write_text(result.stdout+result.stderr)
        if result.returncode:
            raise RuntimeError(f'native process failed ({result.returncode}): {destination}')
        return time.monotonic()-start
    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        durations = list(pool.map(execute, commands))
    # Concatenate in case/track order, never completion order or success-only order.
    shards = [output/f'case-{i:02d}' for i in range(len(cases))]
    for filename in ('hits.csv','tracks.csv'):
        with (output/filename).open('w') as result:
            header = None
            for directory in shards:
                with (directory/filename).open() as source:
                    actual = next(source)
                    if header is None:
                        header = actual
                        result.write(header)
                    elif actual != header:
                        raise ValueError('native shard CSV schema differs')
                    for line in source:
                        result.write(line)
    for name in ('geometry.csv','geometry-corners.csv'):
        geometry_fingerprints = {sha(d/name) for d in shards}
        if len(geometry_fingerprints) != 1:
            raise ValueError('native shard geometry differs')
        (output/name).write_bytes((shards[0]/name).read_bytes())
    metadata = [json.loads((d/'metadata.json').read_text()) for d in shards]
    def relative_command(command):
        prefix=str(ROOT)+'/'
        return [item[len(prefix):] if item.startswith(prefix) else item for item in command]
    for m in metadata:
        m['argv']=relative_command(m['argv'])
    combined = dict(metadata[0])
    for key in ('tracks','raw_native_hits','field_queries','navigation_refreshes','navigation_candidates',
                'native_root_events','native_finite_face_checks','outside_footprint_chamber_support_roots'):
        combined[key] = sum(m[key] for m in metadata)
    for key in ('native_negative_corrections_preserved','curvature_guard_caps',
                'curvature_guard_plane_checks','near_tolerance_parallel_face_ambiguities'):
        combined[key] = sum(m[key] for m in metadata)
    caps=[m['minimum_curvature_guard_step_m'] for m in metadata if m['minimum_curvature_guard_step_m'] is not None]
    combined['minimum_curvature_guard_step_m']=min(caps) if caps else None
    combined['max_track_curvature_bound_per_m']=max(m['max_track_curvature_bound_per_m'] for m in metadata)
    combined['track_status_counts'] = {}
    for m in metadata:
        for key,value in m['track_status_counts'].items():
            combined['track_status_counts'][key] = combined['track_status_counts'].get(key,0)+value
    combined.update(elapsed_seconds=time.monotonic()-started, argv=[relative_command(cmd) for cmd in commands],
                    argv_paths='repository-relative; executed from repository root',
                    serial_shard_elapsed_seconds=durations, independent_workers=workers,
                    executable_sha256=sha(executable), controls_sha256=sha(controls),
                    source_revision=revision, source_files_match_revision=clean,
                    source_files_sha256=fingerprints, preparation_sha256=sha(work/'inputs.json'),
                    analysis_runtime=dict(python=sys.version.split()[0],numpy=np.__version__),
                    shard_metadata=metadata)
    if fingerprints!={str(p.relative_to(ROOT)):sha(p) for p in source_files}:
        raise ValueError('executed source files changed while the scan was running')
    with (output/'tracks.csv').open() as f:
        ids = [int(row['track_id']) for row in csv.DictReader(f)]
    if ids != data['track_id'].tolist():
        raise ValueError('native denominator/track order differs from generation')
    save(output/'metadata.json', combined)
    print(json.dumps(dict(tracks=len(ids), raw_native_hits=combined['raw_native_hits'],
                          elapsed_seconds=combined['elapsed_seconds']), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--controls', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    run(args.work, args.executable, args.output, args.controls, args.workers)
