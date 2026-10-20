"""Native ACTS controls for the isolated DES040 vacuum propagation prototype.

This runner never replaces native hits by analytic intersections. Independent
straight-line clips and constant-field helices are control oracles only. Every
native command, failure and discrepancy is retained in the output JSON.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.muon_layout import geometry as geo
from tools.muon_layout.acts.analyze import count_events, face_catalog, read_hits
from tools.muon_layout.acts.prepare import configuration, save, sha, write_tracks


INPUT_REVISION = 'faa544a1fa424906c68b27bcf37db181d783b84e'
EVENT_TOLERANCE_M = 1e-5
ANALYTIC_TOLERANCE_M = 1e-6
GEOMETRY_TOLERANCE_M = 1e-9
ARGV_PATHS = 'repository-relative; executed from repository root'


def repository_paths(value):
    """Normalize presentation paths without changing hashes or numeric data."""
    if isinstance(value, str):
        return '.' if value == str(ROOT) else value.replace(str(ROOT) + '/', '')
    if isinstance(value, dict):
        return {key: repository_paths(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [repository_paths(item) for item in value]
    return value


def csv_rows(path):
    with Path(path).open(newline='') as stream:
        return list(csv.DictReader(stream))


def read_primaries(path):
    lines = Path(path).read_text().splitlines()
    result = {}
    for line in lines[1:]:
        row = line.split()
        result[int(row[0])] = dict(p=float(row[1]), q=float(row[2]),
                                  start=np.array(row[3:6], float),
                                  direction=np.array(row[6:9], float))
    if len(result) != int(lines[0]):
        raise ValueError('Missing/duplicate control primary')
    return result


def analytic_helix(primary, path, bz):
    """Uniform Bz, SI length/GeV: +q, +Bz, +dx curves towards negative y."""
    s = np.asarray(path)
    k = primary['q'] * .299792458 * bz / primary['p']
    start, d = primary['start'], primary['direction']
    if not k:
        return start + s[..., None] * d, np.broadcast_to(d, s.shape + (3,))
    angle = k * s
    sn, cs = np.sin(angle), np.cos(angle)
    # 2*sin(angle/2)^2 is stable at the adverse fixture's very short entry path.
    one_minus_cos = 2 * np.sin(angle / 2) ** 2
    position = start + np.stack((d[0] * sn / k + d[1] * one_minus_cos / k,
                                d[1] * sn / k - d[0] * one_minus_cos / k,
                                d[2] * s), axis=-1)
    direction = np.stack((d[0] * cs + d[1] * sn,
                          d[1] * cs - d[0] * sn,
                          np.full(s.shape, d[2])), axis=-1)
    return position, direction


def analytic_ray_events(primary, panels, catalog):
    """Exact convex halfspace clips from arbitrary origin, without native hits."""
    events = []
    start, direction = primary['start'], primary['direction']
    for panel_index, body in enumerate(panels):
        normals, bounds = geo.planes3(body)
        for face in range(6):
            info = catalog[panel_index, face]
            n, b = normals[info['plane']], bounds[info['plane']]
            denominator = float(n @ direction)
            if abs(denominator) < 1e-13:
                continue
            path = float((b - n @ start) / denominator)
            point = start + path * direction
            if path > 1e-8 and np.all(normals @ point <= bounds + 1e-9):
                events.append((path, panel_index, face, bool(info['large']), point))
    return sorted(events, key=lambda e: (e[0], e[1], e[2]))


def _fixture_panel(identifier, y=0.):
    # Explicit test-only prism; not a detector-layout change.
    return dict(id=identifier, station=1, depth_m=.5, origin_m=[4.61, y, 0.],
                basis=[[0., 0., 1.], [1., 0., 0.], [0., 1., 0.]],
                vertices_m=[[-.5, -.5], [.5, -.5], [.5, .5], [-.5, .5]])


def write_fixture(directory, panels, primaries):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    geometry = directory / 'geometry.dat'
    with geometry.open('w') as stream:
        stream.write(f'{len(panels)}\n')
        for p in panels:
            values = [p['depth_m'], *p['origin_m'], *np.asarray(p['basis']).ravel(),
                      *np.asarray(p['vertices_m']).ravel()]
            stream.write(p['id'] + ' ' + str(p['station']) + ' ' +
                         ' '.join(format(float(x), '.17g') for x in values) + '\n')
    tracks = directory / 'tracks.dat'
    with tracks.open('w') as stream:
        stream.write(f'{len(primaries)}\n')
        for identifier, p in primaries.items():
            values = [p['p'], p['q'], *p['start'], *p['direction']]
            stream.write(str(identifier) + ' ' + ' '.join(format(float(x), '.17g') for x in values) + '\n')
    return geometry, tracks


def _active_flags(hits, panels, border):
    flags = np.zeros(len(hits), bool)
    for j in np.unique(hits['panel_index']):
        ids = np.flatnonzero(hits['panel_index'] == j)
        body = panels[j]
        xyz = np.column_stack([hits[x + '_m'][ids] for x in ('x', 'y', 'z')])
        local = (xyz - body['origin_m']) @ np.asarray(body['basis'])
        normals, bounds = geo.polygon_planes(body['vertices_m'])
        flags[ids] = np.all(local[:, :2] @ normals.T <= bounds - border + 1e-8, axis=1)
    return flags


def audit_run(directory, panels, border=.03):
    directory = Path(directory)
    catalog, geometry_metrics = face_catalog(directory / 'geometry.csv', panels,
                                             tol=GEOMETRY_TOLERANCE_M)
    hits = read_hits(directory / 'hits.csv')
    for field in ('x_m', 'y_m', 'z_m', 'path_m', 'dx', 'dy', 'dz'):
        if not np.isfinite(hits[field]).all():
            raise ValueError('Nonfinite native boundary event: ' + field)
    active = _active_flags(hits, panels, border)
    tracks = {int(x['track_id']): x for x in csv_rows(directory / 'tracks.csv')}
    events, counts = {}, {}
    max_plane, max_excess = 0., 0.
    for identifier in tracks:
        selected = np.flatnonzero(hits['track_id'] == identifier)
        value = count_events(hits[selected], catalog, active[selected], tol=2e-8)
        counts[identifier] = {k: v for k, v in value.items() if k != 'keep_indices'}
        events[identifier] = hits[selected[value['keep_indices']]]
    for hit in hits:
        key = int(hit['panel_index']), int(hit['face_index'])
        info = catalog[key]
        if int(hit['geometry_id']) != info['id'] or bool(hit['is_large']) != info['large']:
            raise ValueError('Native hit ownership/ID differs from native geometry')
        point = np.array([hit[x + '_m'] for x in ('x', 'y', 'z')])
        normals, bounds = geo.planes3(panels[key[0]])
        max_plane = max(max_plane, abs(float(info['normal'] @ point - info['bound'])))
        max_excess = max(max_excess, float(np.max(normals @ point - bounds)))
    if max(max_plane, max_excess) > ANALYTIC_TOLERANCE_M:
        raise ValueError('Native boundary root exceeds finite face/plane tolerance')
    return dict(tracks=tracks, events=events, counts=counts, catalog=catalog,
                metrics={**geometry_metrics, 'raw_hits': len(hits),
                         'unique_events': sum(map(len, events.values())),
                         'max_plane_residual_m': max_plane,
                         'max_finite_face_excess_m': max_excess})


def compare_runs(left, right, tolerance=EVENT_TOLERANCE_M):
    status_differences, sequence_differences, counter_differences = [], [], []
    position_differences, max_position, max_path = [], 0., 0.
    same_ids = set(left['tracks']) == set(right['tracks'])
    counter_keys = ('outer_unique_faces', 'active_unique_faces',
                    'outer_paired_stations', 'active_paired_stations')
    for identifier in sorted(set(left['tracks']) & set(right['tracks'])):
        a, b = left['tracks'][identifier], right['tracks'][identifier]
        if a['status'] != b['status']:
            status_differences.append(dict(track_id=identifier, left=a['status'], right=b['status']))
        ea, eb = left['events'][identifier], right['events'][identifier]
        sa = [(int(e['panel_index']), int(e['face_index']), int(e['geometry_id'])) for e in ea]
        sb = [(int(e['panel_index']), int(e['face_index']), int(e['geometry_id'])) for e in eb]
        if sa != sb:
            sequence_differences.append(dict(track_id=identifier, left=sa, right=sb))
        else:
            da = np.column_stack([ea[x + '_m'] for x in ('x', 'y', 'z')])
            db = np.column_stack([eb[x + '_m'] for x in ('x', 'y', 'z')])
            delta = np.linalg.norm(da - db, axis=1)
            largest = float(delta.max(initial=0))
            max_position = max(max_position, largest)
            max_path = max(max_path, float(np.max(abs(ea['path_m'] - eb['path_m']), initial=0)))
            if largest > tolerance:
                position_differences.append(dict(track_id=identifier, max_position_delta_m=largest))
        ca, cb = left['counts'][identifier], right['counts'][identifier]
        if any(ca[k] != cb[k] for k in counter_keys):
            counter_differences.append(dict(track_id=identifier,
                                           left={k: ca[k] for k in counter_keys},
                                           right={k: cb[k] for k in counter_keys}))
    metrics = dict(same_track_ids=same_ids, tracks=len(left['tracks']),
                   status_differences=status_differences,
                   boundary_sequence_differences=sequence_differences,
                   counter_differences=counter_differences,
                   position_differences=position_differences,
                   max_boundary_position_delta_m=max_position,
                   max_matched_event_path_delta_m=max_path,
                   position_tolerance_m=tolerance,
                   left_audit=left['metrics'], right_audit=right['metrics'])
    passed = same_ids and not any((status_differences, sequence_differences,
                                  counter_differences, position_differences))
    return passed, metrics


class Controls:
    def __init__(self, work, executable, output):
        self.work, self.executable, self.output = Path(work).resolve(), Path(executable).resolve(), Path(output).resolve()
        executable_hash = sha(self.executable)
        self.runs = self.work / 'native-controls' / executable_hash[:12]
        self.runs.mkdir(parents=True, exist_ok=True)
        self.output.parent.mkdir(parents=True, exist_ok=True)
        previous_report = None
        if self.output.exists():
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            archive = self.runs.parent / ('previous-report-' + timestamp + '.json')
            archive.write_bytes(self.output.read_bytes())
            previous_report = dict(path=str(archive), sha256=sha(archive))
        self.config = configuration()
        self.panels = json.loads((ROOT / self.config['geometry']).read_text())['panels']
        self.selection = self.prepare_control_tracks()
        sources = ['controls.py', 'prepare.py', 'analyze.py', 'config.json', 'propagate.cpp']
        self.report = dict(passed=False, input_revision=INPUT_REVISION,
                           repository_head_at_execution=subprocess.check_output(
                               ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                           governing_design_sha256=sha(ROOT / 'docs/design/DES-040-muon-chambers-frame.md'),
                           executable=str(self.executable), executable_sha256=executable_hash,
                           configuration_sha256=sha(Path(__file__).parent / 'config.json'),
                           source_sha256={name: sha(Path(__file__).parent / name) for name in sources},
                           independent_geometry_oracle_sha256=sha(ROOT / 'tools/muon_layout/geometry.py'),
                           source_root=str(ROOT),
                           argv_paths=ARGV_PATHS,
                           source_scope='input_revision pins the assignment start; repository_head_at_execution plus design/source hashes identify actual execution, including recorded numerical-method amendments.',
                           fixed_inputs=dict(geometry_sha256=self.config['geometry_sha256'],
                                             map_sha256=self.config['map_sha256']),
                           prepared_inputs_sha256={p.name: sha(p) for p in self.work.iterdir()
                                                   if p.is_file() and p.suffix in ('.dat', '.bin', '.npz', '.json')},
                           runtime=dict(python=sys.version, numpy=np.__version__), checks=[],
                           previous_report_archive=previous_report,
                           direction_selection=self.selection,
                           limits=['Vacuum chamber-boundary proxies only; no material, detector response or fitted segments.',
                                   'Native infinite-support-plane roots are strictly audited against finite source faces; portal volume switching is not validated.',
                                   'The finite-portal adverse-edge run is a retained negative control, not the primary hit algorithm.'])
        self.flush()

    def prepare_control_tracks(self):
        """Spread unique common direction IDs across both prepared samples."""
        with np.load(self.work / 'primaries.npz', allow_pickle=False) as source:
            data = dict(source)
        cases = [(p, q) for p in self.config['momentum_GeV'] for q in self.config['charge_e']]
        p, q = cases[0]
        first = np.flatnonzero((data['momentum_GeV'] == p) & (data['charge'] == q))
        zero = first[np.linspace(0, len(first) - 1, 256, dtype=int)]
        common = data['direction_id'][first[np.linspace(0, len(first) - 1, 16, dtype=int)]]
        navigation = np.concatenate([
            np.flatnonzero((data['momentum_GeV'] == p) & (data['charge'] == q) &
                           np.isin(data['direction_id'], common)) for p, q in cases])
        if len(np.unique(data['direction_id'][zero])) != 256 or len(navigation) != 160:
            raise ValueError('Prepared direction IDs do not satisfy expanded native controls')
        self.zero_tracks = self.runs / 'zero-unique-256.dat'
        self.navigation_tracks = self.runs / 'navigation-common-160.dat'
        write_tracks(self.zero_tracks, data, zero)
        write_tracks(self.navigation_tracks, data, navigation)
        return dict(method='Integer linspace row selection over first-case map plus iid sphere directions; identical common direction IDs in every p/q case.',
                    source_primaries_sha256=sha(self.work / 'primaries.npz'),
                    zero_field=dict(track_ids=data['track_id'][zero].tolist(),
                                    unique_direction_count=256,
                                    sample_counts={str(k): int(v) for k, v in zip(*np.unique(data['sample'][zero], return_counts=True))},
                                    entrance_kind_counts={str(k): int(v) for k, v in zip(*np.unique(data['entrance_kind'][zero], return_counts=True))},
                                    track_file=str(self.zero_tracks), sha256=sha(self.zero_tracks)),
                    indexed_exhaustive=dict(track_ids=data['track_id'][navigation].tolist(),
                                            common_direction_ids=common.tolist(), unique_direction_count=16,
                                            tracks=160, momentum_charge_cases=cases,
                                            track_file=str(self.navigation_tracks), sha256=sha(self.navigation_tracks)))

    def flush(self):
        save(self.output, repository_paths(self.report))

    def native(self, name, tracks=None, geometry=None, field='map', bz=0.,
               step=.05, tolerance=1e-8, policy='indexed', mode='surface-audit',
               query=False, inspect=False, rk_tolerance=None):
        directory = self.runs / name
        directory.mkdir(parents=True, exist_ok=True)
        command = [str(self.executable), '--output-dir', str(directory),
                   '--map', str(self.work / 'map.bin'), '--field', field,
                   '--mode', mode, '--policy', policy, '--bz', str(bz),
                   '--max-step-m', str(step), '--tolerance-m', str(tolerance),
                   '--rk-tolerance-m', str(self.config['rk_tolerance_m'] if rk_tolerance is None else rk_tolerance),
                   '--max-steps', str(self.config['max_steps']),
                   '--path-limit-m', str(self.config['path_limit_m'])]
        if query:
            command += ['--query-field', str(self.work / 'query-points.dat')]
        else:
            command += ['--geometry', str(geometry or self.work / 'geometry.dat')]
            command += ['--inspect-only'] if inspect else ['--tracks', str(tracks)]
        before = time.perf_counter()
        result = subprocess.run(command, capture_output=True, text=True, cwd=ROOT)
        record = dict(argv=command, returncode=result.returncode,
                      argv_paths=ARGV_PATHS,
                      elapsed_seconds=time.perf_counter() - before,
                      stdout=result.stdout, stderr=result.stderr,
                      output_sha256={p.name: sha(p) for p in directory.iterdir() if p.is_file()})
        if (directory / 'metadata.json').exists():
            record['native_metadata'] = json.loads((directory / 'metadata.json').read_text())
        self.current_commands.append(record)
        return directory, record

    def check(self, name, function):
        self.current_commands = []
        try:
            passed, metrics, commands = function()
            record = dict(name=name, passed=bool(passed), metrics=metrics, commands=commands)
        except Exception as error:
            record = dict(name=name, passed=False, metrics={'exception': repr(error)},
                          commands=self.current_commands)
        self.report['checks'].append(record)
        self.flush()
        print(json.dumps(dict(name=name, passed=record['passed'])), flush=True)
        return record['passed']

    def field(self):
        directory, command = self.native('field-parity', query=True)
        if command['returncode']:
            return False, {'error': 'native field query failed'}, [command]
        rows = csv_rows(directory / 'field.csv')
        with np.load(self.work / 'query-reference.npz', allow_pickle=False) as data:
            expected, statuses = data['field_T'], data['status']
        actual_status = np.array(['ok' if r['status'] == 'valid' else r['status'] for r in rows])
        actual = np.array([[float(r[x + '_T']) for x in ('Bx', 'By', 'Bz')] for r in rows])
        same_count = len(rows) == len(statuses)
        if not same_count:
            return False, {'actual_points': len(rows), 'expected_points': len(statuses)}, [command]
        valid = statuses == 'ok'
        delta = abs(actual[valid] - expected[valid])
        matches = actual_status == statuses
        classes = {str(s): int(n) for s, n in zip(*np.unique(statuses, return_counts=True))}
        metrics = dict(points=len(rows), expected_status_counts=classes,
                       status_mismatch_indices=np.flatnonzero(~matches).tolist(),
                       max_absolute_finite_field_residual_T=float(delta[np.isfinite(delta)].max(initial=0)),
                       nonfinite_valid_field_components=int((~np.isfinite(actual[valid])).sum()),
                       absolute_tolerance_T=1e-10, relative_tolerance=1e-10,
                       all_invalid_queries_remain_nonfinite=bool(np.isnan(actual[~valid]).all()),
                       includes_C12_seams_and_axis_domain_mask_boundaries=True)
        passed = (matches.all() and np.isfinite(actual[valid]).all() and
                  np.allclose(actual[valid], expected[valid], rtol=1e-10, atol=1e-10) and
                  np.isnan(actual[~valid]).all() and
                  {'ok', 'field_masked', 'outside_map'}.issubset(classes))
        return passed, metrics, [command]

    def geometry(self):
        directory, command = self.native('native-geometry', field='zero', inspect=True)
        if command['returncode']:
            return False, {'error': 'native geometry inspection failed'}, [command]
        catalog, metrics = face_catalog(directory / 'geometry.csv', self.panels, tol=GEOMETRY_TOLERANCE_M)
        corners = {}
        for row in csv_rows(directory / 'geometry-corners.csv'):
            key = int(row['panel_index']), int(row['face_index'])
            corners.setdefault(key, []).append([float(row[x + '_m']) for x in ('x', 'y', 'z')])
        max_corner, bad_faces = 0., []
        for key, info in catalog.items():
            points = geo.vertices3(self.panels[key[0]])
            expected = points[abs(points @ info['normal'] - info['bound']) < GEOMETRY_TOLERANCE_M]
            actual = np.asarray(corners.get(key, []))
            if len(actual) != 4 or len(expected) != 4:
                bad_faces.append(list(key))
                continue
            distances = np.linalg.norm(actual[:, None, :] - expected[None, :, :], axis=2)
            residual = max(float(distances.min(axis=0).max()), float(distances.min(axis=1).max()))
            max_corner = max(max_corner, residual)
            if residual > GEOMETRY_TOLERANCE_M:
                bad_faces.append(list(key))
        ids = [x['id'] for x in catalog.values()]
        meta = json.loads((directory / 'metadata.json').read_text())
        metrics.update(chambers=len(self.panels), actual_native_volume_count=meta['visited_native_volumes'],
                       max_corner_set_residual_m=max_corner, failed_faces=bad_faces,
                       exact_uint64_ids_unique=len(set(ids)) == len(ids),
                       all_chamber_face_ids_above_2pow53=min(ids) > 2**53,
                       minimum_geometry_id=min(ids), maximum_geometry_id=max(ids),
                       plane_corner_tolerance_m=GEOMETRY_TOLERANCE_M)
        passed = (not bad_faces and len(corners) == len(catalog) and
                  meta['visited_native_volumes'] == len(self.panels) + 1 and
                  metrics['exact_uint64_ids_unique'] and metrics['all_chamber_face_ids_above_2pow53'])
        return passed, metrics, [command]

    def zero(self):
        tracks = self.zero_tracks
        directory, command = self.native('zero-field-exact', tracks=tracks, field='zero')
        if command['returncode']:
            return False, {'error': 'native zero-field run failed'}, [command]
        actual = audit_run(directory, self.panels)
        primaries = read_primaries(tracks)
        failures, max_position, max_path, sides, no_hit = [], 0., 0., 0, 0
        for identifier, primary in primaries.items():
            expected = analytic_ray_events(primary, self.panels, actual['catalog'])
            returned = actual['events'][identifier]
            a = [(e[1], e[2]) for e in expected]
            b = [(int(e['panel_index']), int(e['face_index'])) for e in returned]
            sides += sum(not e[3] for e in expected)
            no_hit += not bool(expected)
            if a != b:
                failures.append(dict(track_id=identifier, expected=a, actual=b))
                continue
            for oracle, event in zip(expected, returned):
                point = np.array([event[x + '_m'] for x in ('x', 'y', 'z')])
                max_position = max(max_position, float(np.linalg.norm(point - oracle[4])))
                max_path = max(max_path, abs(float(event['path_m']) - oracle[0]))
        statuses = {i: r['status'] for i, r in actual['tracks'].items() if r['status'] != 'completed'}
        metrics = dict(tracks=len(primaries), unique_direction_count=self.selection['zero_field']['unique_direction_count'],
                       entrance_kind_counts=self.selection['zero_field']['entrance_kind_counts'],
                       analytic_side_events=sides, analytic_no_hit_tracks=no_hit,
                       event_sequence_differences=failures, unexpected_statuses=statuses,
                       max_position_residual_m=max_position, max_path_residual_m=max_path,
                       tolerance_m=ANALYTIC_TOLERANCE_M, native_audit=actual['metrics'])
        passed = (set(actual['tracks']) == set(primaries) and not failures and not statuses and
                  sides > 0 and no_hit > 0 and max(max_position, max_path) <= ANALYTIC_TOLERANCE_M)
        return passed, metrics, [command]

    def curved(self):
        commands, cases, audits = [], [], {}
        panel = _fixture_panel('adverse-edge-fixture')
        for bz in (3., -3.):
            primaries = {0: dict(p=5., q=np.sign(bz), start=np.array([4.35, .500001, 0.]), direction=np.array([1., 0., 0.])),
                         1: dict(p=5., q=-np.sign(bz), start=np.array([4.35, -.500001, 0.]), direction=np.array([1., 0., 0.]))}
            geometry, tracks = write_fixture(self.runs / f'curved-input-{bz:g}', [panel], primaries)
            for tolerance in (1e-8, 1e-9):
                name = f'curved-bz{bz:g}-tol{tolerance:g}'
                directory, command = self.native(name, tracks=tracks, geometry=geometry,
                                                  field='constant', bz=bz, tolerance=tolerance)
                commands.append(command)
                if command['returncode']:
                    cases.append(dict(bz_T=bz, tolerance_m=tolerance, passed=False, native_error=True))
                    continue
                audit = audit_run(directory, [panel])
                audits[bz, tolerance] = audit
                for identifier, primary in primaries.items():
                    events = audit['events'][identifier]
                    positions = np.column_stack([events[x + '_m'] for x in ('x', 'y', 'z')])
                    directions = np.column_stack([events[x] for x in ('dx', 'dy', 'dz')])
                    expected_p, expected_d = analytic_helix(primary, events['path_m'], bz)
                    rp = float(np.linalg.norm(positions - expected_p, axis=1).max(initial=0))
                    rd = float(np.linalg.norm(directions - expected_d, axis=1).max(initial=0))
                    passed = (len(events) == 2 and events['is_large'].all() and
                              audit['tracks'][identifier]['status'] == 'completed' and
                              rp <= ANALYTIC_TOLERANCE_M and rd <= 1e-7 and
                              positions[0, 1] * np.sign(primary['start'][1]) < abs(primary['start'][1]))
                    cases.append(dict(bz_T=bz, q=float(primary['q']), local_momentum_GeV=5.,
                                      tolerance_m=tolerance, large_events=int(events['is_large'].sum()),
                                      side_events=int((~events['is_large']).sum()),
                                      max_helix_position_residual_m=rp, max_helix_direction_residual=rd,
                                      passed=bool(passed), native_audit=audit['metrics']))
        symmetry = []
        for tolerance in (1e-8, 1e-9):
            if (3., tolerance) not in audits or (-3., tolerance) not in audits:
                continue
            positive, negative = audits[3., tolerance], audits[-3., tolerance]
            for identifier in (0, 1):
                a, b = positive['events'][identifier], negative['events'][identifier]
                if len(a) != len(b):
                    symmetry.append(dict(tolerance_m=tolerance, track_id=identifier, passed=False))
                    continue
                pa = np.column_stack([a[x + '_m'] for x in ('x', 'y', 'z')])
                pb = np.column_stack([b[x + '_m'] for x in ('x', 'y', 'z')])
                delta = float(np.linalg.norm(pa - pb, axis=1).max(initial=0))
                symmetry.append(dict(tolerance_m=tolerance, track_id=identifier,
                                     qB_flip_position_delta_m=delta, passed=delta <= ANALYTIC_TOLERANCE_M))
            a, b = positive['events'][0], positive['events'][1]
            if len(a) == len(b):
                pa = np.column_stack([a[x + '_m'] for x in ('x', 'y', 'z')]); pa[:, 1] *= -1
                pb = np.column_stack([b[x + '_m'] for x in ('x', 'y', 'z')])
                delta = float(np.linalg.norm(pa - pb, axis=1).max(initial=0))
                symmetry.append(dict(tolerance_m=tolerance, mirror_position_delta_m=delta,
                                     passed=delta <= ANALYTIC_TOLERANCE_M))
        return (len(cases) == 8 and len(symmetry) == 6 and
                all(c['passed'] for c in cases + symmetry)), dict(
                    cases=cases, qB_flip_and_mirror_controls=symmetry,
                    position_tolerance_m=ANALYTIC_TOLERANCE_M, direction_tolerance=1e-7,
                    sign_convention='+q,+Bz,+dx produces negative y deflection'), commands

    def legacy(self):
        panel = _fixture_panel('adverse-edge-fixture')
        primaries = {0: dict(p=5., q=1., start=np.array([4.35, .500001, 0.]), direction=np.array([1., 0., 0.]))}
        geometry, tracks = write_fixture(self.runs / 'legacy-input', [panel], primaries)
        directory, command = self.native('legacy-finite-portals-negative', tracks=tracks, geometry=geometry,
                                          field='constant', bz=3., mode='finite-portals', rk_tolerance=1e-8)
        metrics = dict(negative_control=True, primary_algorithm=False,
                       original_RK_tolerance_m=1e-8,
                       expected_behavior='Finite-tangent portal navigation can miss the first curved-edge entry; this mode is excluded from primary evidence.',
                       finite_portal_run_returncode=command['returncode'])
        if not command['returncode']:
            audit = audit_run(directory, [panel])
            events = audit['events'][0]
            metrics.update(large_events=int(events['is_large'].sum()),
                           side_events=int((~events['is_large']).sum()),
                           two_large_faces_recovered=bool(len(events) == 2 and events['is_large'].all()),
                           status=audit['tracks'][0]['status'], native_audit=audit['metrics'])
        # A reproduced failure is expected evidence, not a failure of the primary method.
        metrics['expected_negative_observed'] = (command['returncode'] == 0 and
                                                not metrics.get('two_large_faces_recovered', True))
        return command['returncode'] == 0, metrics, [command]

    def parallel_tangent(self):
        """A curved side entry whose initial straight tangent is parallel."""
        panel = _fixture_panel('parallel-tangent-fixture')
        primaries = {0: dict(p=5., q=1., start=np.array([4.50, .500001, 0.]),
                             direction=np.array([1., 0., 0.]))}
        geometry, tracks = write_fixture(self.runs / 'parallel-tangent-input', [panel], primaries)
        commands, cases = [], []
        for tolerance in (1e-8, 1e-9):
            directory, command = self.native(f'parallel-tangent-side-entry-{tolerance:g}', tracks=tracks,
                                              geometry=geometry, field='constant', bz=3., tolerance=tolerance)
            commands.append(command)
            if command['returncode']:
                cases.append(dict(tolerance_m=tolerance, passed=False, error='native parallel-tangent run failed'))
                continue
            audit = audit_run(directory, [panel])
            events = audit['events'][0]
            actual = np.column_stack([events[x + '_m'] for x in ('x', 'y', 'z')])
            expected, _ = analytic_helix(primaries[0], events['path_m'], 3.)
            residual = float(np.linalg.norm(actual - expected, axis=1).max(initial=0))
            passed = (len(events) == 2 and not events['is_large'][0] and events['is_large'][1] and
                      audit['tracks'][0]['status'] == 'completed' and residual <= ANALYTIC_TOLERANCE_M)
            cases.append(dict(passed=bool(passed), tolerance_m=tolerance,
                              expected_event_types=['side entry', 'large-face exit'],
                              actual_event_types=['large' if x else 'side' for x in events['is_large']],
                              event_paths_m=events['path_m'].tolist(),
                              max_helix_position_residual_m=residual, native_audit=audit['metrics']))
        return all(case['passed'] for case in cases), {'cases': cases}, commands

    def coplanar(self):
        panels = [_fixture_panel('wrong-coplanar-owner', -1.), _fixture_panel('correct-coplanar-owner', 0.)]
        primaries = {0: dict(p=5., q=1., start=np.array([4.35, 0., 0.]), direction=np.array([1., 0., 0.]))}
        geometry, tracks = write_fixture(self.runs / 'coplanar-input', panels, primaries)
        directory, command = self.native('coplanar-ownership', tracks=tracks, geometry=geometry, field='zero')
        if command['returncode']:
            return False, {'error': 'native coplanar run failed'}, [command]
        audit = audit_run(directory, panels)
        events = audit['events'][0]
        passed = (len(events) == 2 and events['is_large'].all() and
                  (events['panel_index'] == 1).all() and audit['tracks'][0]['status'] == 'completed')
        return passed, dict(actual_owner_indices=events['panel_index'].astype(int).tolist(),
                            large_events=int(events['is_large'].sum()), native_audit=audit['metrics']), [command]

    def navigation(self):
        commands, audits = [], []
        for policy in ('indexed', 'exhaustive'):
            directory, command = self.native('navigation-' + policy,
                                              tracks=self.navigation_tracks, policy=policy)
            commands.append(command)
            if command['returncode']:
                return False, {'error': 'native navigation control failed'}, commands
            audits.append(audit_run(directory, self.panels, self.config['active_border_m']))
        passed, metrics = compare_runs(*audits)
        metrics.update(common_unique_direction_count=16,
                       discovery='Cartesian index versus independent linear scan over every finite AABB, followed by the same conservative reach bound')
        return passed, metrics, commands

    def unbounded_negative(self):
        """Keep the two discovered remote-support failures as bounded witnesses."""
        with np.load(self.work / 'primaries.npz', allow_pickle=False) as source:
            data = dict(source)
        selected = np.array([20854, 28798], dtype=int)
        tracks = self.runs / 'unbounded-witness-tracks.dat'
        write_tracks(tracks, data, selected)
        directory, command = self.native('unbounded-support-negative', tracks=tracks, policy='unbounded')
        if command['returncode']:
            return False, dict(negative_control=True, primary_algorithm=False,
                               error='Unbounded witness executable did not finish normally'), [command]
        audit = audit_run(directory, self.panels, self.config['active_border_m'])
        bounded = audit_run(self.runs / 'navigation-indexed', self.panels, self.config['active_border_m'])
        bounded = {**bounded, **{k: {i: bounded[k][i] for i in map(int, selected)}
                                 for k in ('tracks', 'events', 'counts')}}
        matches, differences = compare_runs(bounded, audit)
        return True, dict(negative_control=True, primary_algorithm=False,
                          track_ids=selected.tolist(), track_file_sha256=sha(tracks),
                          original_discovery='Remote infinite supporting planes caused missing side roots and an exhaustive step limit.',
                          expected_negative_observed=not matches,
                          matches_bounded_primary=matches, differences=differences), [command]

    def refinements(self):
        commands, audits = [], []
        rk = self.config['rk_tolerance_m']
        settings = [('baseline', .05, 1e-8, rk), ('half-step', .025, 1e-8, rk),
                    ('quarter-step', .0125, 1e-8, rk), ('tight-tolerance', .05, 1e-9, rk),
                    ('tight-RK', .05, 1e-8, 1e-12)]
        for name, step, tolerance, rk_tolerance in settings:
            directory, command = self.native('refinement-' + name,
                                              tracks=self.work / 'control-tracks.dat',
                                              step=step, tolerance=tolerance, rk_tolerance=rk_tolerance)
            commands.append(command)
            if command['returncode']:
                return False, {'error': 'native refinement failed', 'setting': name}, commands
            audits.append(audit_run(directory, self.panels, self.config['active_border_m']))
        comparisons = []
        for (name, step, tolerance, rk_tolerance), audit in zip(settings[1:], audits[1:]):
            passed, metrics = compare_runs(audits[0], audit)
            comparisons.append(dict(name=name, max_step_m=step, surface_tolerance_m=tolerance,
                                    RK_tolerance_m=rk_tolerance,
                                    passed=passed, metrics=metrics))
        return all(c['passed'] for c in comparisons), {'comparisons': comparisons}, commands

    def run(self):
        started = time.perf_counter()
        for name, function in [('strict_field_parity', self.field), ('native_geometry_and_uint64_IDs', self.geometry),
                               ('zero_field_exact_clips', self.zero), ('constant_field_adverse_edge_helix', self.curved),
                               ('parallel_tangent_side_entry', self.parallel_tangent),
                               ('finite_portal_negative', self.legacy), ('coplanar_finite_owner', self.coplanar),
                               ('indexed_exhaustive_navigation', self.navigation), ('step_tolerance_refinements', self.refinements)]:
            self.check(name, function)
        self.check('unbounded_support_negative', self.unbounded_negative)
        unchanged = sha(self.executable) == self.report['executable_sha256']
        self.report['executable_unchanged_through_controls'] = unchanged
        self.report['elapsed_seconds'] = time.perf_counter() - started
        self.report['passed'] = unchanged and all(c['passed'] for c in self.report['checks'])
        self.flush()
        return self.report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = Controls(args.work, args.executable, args.output).run()
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
