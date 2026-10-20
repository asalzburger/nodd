"""Audit native paired-wheel ACTS events without losing generated denominators.

CLI: ``analyze.py --work WORK --run RUN --output OUTPUT``. WORK contains the
prepared inputs.json/primaries.npz; RUN contains native CSVs and metadata.json.
This isolated postprocessor deliberately reuses the legacy, tested literal
face/event counters. It does not synthesize trajectories or missing events.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.muon_layout import geometry as geo
from tools.muon_layout.acts.analyze import face_catalog, read_hits, count_events

COUNTERS = ('outer_unique_faces', 'active_unique_faces', 'outer_paired_stations',
            'active_paired_stations', 'numerical_duplicates', 'reentries',
            'side_events', 'orphan_transitions', 'open_visits', 'tangent_events')
METRICS = {name: threshold for prefix in ('', 'endcap_')
           for name, threshold in ((prefix+'outer_unique_faces', 6),
                                   (prefix+'active_unique_faces', 6),
                                   (prefix+'outer_paired_stations', 3),
                                   (prefix+'active_paired_stations', 3))}
METRICS.update({f'endcap_station_{station}_{border}_paired': 1
                for station in (1, 2, 3) for border in ('outer', 'active')})
SCOPE = ('Native ACTS vacuum boundary-event availability proxies; every generated '
         'track is retained. No scattering, energy loss, detector response, fitted '
         'segments, reconstruction efficiency or installed-field certification.')


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8*1024*1024), b''):
            value.update(block)
    return value.hexdigest()


def save(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')


def source_state():
    files = [Path(__file__), Path(__file__).with_name('draw.py'),
             Path(__file__).with_name('compare.py'),
             ROOT/'tools/muon_layout/wheels_acts/prepare.py',
             ROOT/'tools/muon_layout/acts/analyze.py',
             ROOT/'tools/muon_layout/acts/prepare.py',
             ROOT/'tools/muon_layout/geometry.py']
    return dict(source_revision=subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        worktree_status=subprocess.check_output(
            ['git', 'status', '--short'], cwd=ROOT, text=True).splitlines(),
        source_files_sha256={str(path.relative_to(ROOT)): sha(path)
                             for path in files if path.exists()},
        scope='Source hashes describe executed working-tree bytes; HEAD alone does not include local changes.')


def regions(data, c):
    """Disjoint banks and fixed angular regions; never select by observed hits."""
    sample, eta = data['sample'], data['eta_pos']
    cut = c['endcap_abs_eta_min']
    sphere, caps = sample == 1, np.isin(sample, [2, 3])
    return {
        'eta_display': sample == 0,
        'full_sphere': sphere,
        'full_sphere_endcap': sphere & (abs(eta) >= cut),
        'full_sphere_endcap_positive': sphere & (eta >= cut),
        'full_sphere_endcap_negative': sphere & (eta <= -cut),
        'endcap_caps': caps,
        'endcap_cap_positive': sample == 2,
        'endcap_cap_negative': sample == 3,
    }


def sampling_error(values, weights, samples):
    """Sampling SE for iid banks; pooled +/- caps use independent strata.

    The eta display has one jittered draw per unequal-area cell, so it has no
    estimated sampling error here. This SE never includes unresolved outcomes.
    """
    values, weights, samples = map(np.asarray, (values, weights, samples))
    if not len(values) or np.any(samples == 0):
        return None
    total = float(weights.sum())
    variance = 0.
    for bank in np.unique(samples):
        take = samples == bank
        if take.sum() < 2 or not np.allclose(weights[take], weights[take][0], rtol=1e-12, atol=0):
            return None
        fraction = float(weights[take].sum()/total)
        variance += fraction*fraction*float(np.var(values[take].astype(float), ddof=1))/int(take.sum())
    return float(np.sqrt(variance))


def availability(passed, incomplete, weights, samples):
    passed, incomplete = np.asarray(passed, bool), np.asarray(incomplete, bool)
    weights = np.asarray(weights, float)
    if not len(passed) or not (passed.shape == incomplete.shape == weights.shape == np.asarray(samples).shape):
        raise ValueError('Nonempty, equally sized availability vectors required')
    possible = passed | incomplete
    return dict(proven_lower_fraction=float(weights[passed].sum()/weights.sum()),
                possible_upper_fraction=float(weights[possible].sum()/weights.sum()),
                proven_tracks=int(passed.sum()),
                possible_tracks=int(possible.sum()),
                unqualified_below_threshold=int((incomplete & ~passed).sum()),
                sampling_standard_error_lower=sampling_error(passed, weights, samples),
                sampling_standard_error_upper=sampling_error(possible, weights, samples),
                scope='Upper minus lower is unresolved-event uncertainty, not a confidence interval; sampling SE is separate.')


def _case(data, momentum, charge):
    return ((data['momentum_GeV'] == momentum) & (data['charge'] == charge))


def validate_primaries(data, c):
    n = len(data['track_id'])
    if not n or not np.array_equal(data['track_id'], np.arange(n)):
        raise ValueError('Primary IDs must preserve every generated row')
    scalar = ('direction_id', 'momentum_GeV', 'charge', 'sample', 'eta_pos',
              'phi_pos_deg', 'eta_bin', 'phi_bin', 'solid_angle_weight_sr')
    if any(data[key].shape != (n,) for key in scalar):
        raise ValueError('Primary row shape mismatch')
    if any(data[key].shape != (n, 3) or not np.isfinite(data[key]).all()
           for key in ('direction', 'entrance_position_m', 'start_m')):
        raise ValueError('Invalid primary vector')
    if not np.isin(data['sample'], [0, 1, 2, 3]).all() or not np.isin(data['charge'], c['charge_e']).all():
        raise ValueError('Unexpected primary bank/charge')
    if not np.allclose(np.linalg.norm(data['direction'], axis=1), 1, rtol=0, atol=1e-12):
        raise ValueError('Primary direction is not a unit vector')
    if not np.allclose(np.arctanh(data['direction'][:, 2]), data['eta_pos'], rtol=1e-11, atol=1e-11):
        raise ValueError('Endcap region must use initial direction eta')
    if not np.isfinite(data['solid_angle_weight_sr']).all() or np.any(data['solid_angle_weight_sr'] <= 0):
        raise ValueError('Positive finite solid-angle weights required')
    grid = c['map_grid']; expected = {0: grid['eta_bins']*grid['phi_bins'],
                                    1: c['full_sphere_directions'],
                                    2: c['endcap_cap_directions_per_side'],
                                    3: c['endcap_cap_directions_per_side']}
    reference = None
    repeated = ('direction_id', 'direction', 'entrance_position_m', 'start_m',
                'sample', 'eta_pos', 'phi_pos_deg', 'eta_bin', 'phi_bin',
                'solid_angle_weight_sr')
    for momentum in c['momentum_GeV']:
        for charge in c['charge_e']:
            take = _case(data, momentum, charge)
            if any(int(np.count_nonzero(take & (data['sample'] == bank))) != size
                   for bank, size in expected.items()):
                raise ValueError('Generated momentum/charge/bank denominator mismatch')
            if reference is None:
                reference = {key: data[key][take] for key in repeated}
            elif any(not np.array_equal(data[key][take], reference[key]) for key in repeated):
                raise ValueError('Momentum/charge cases do not share identical primary IDs/directions')
    if n != sum(expected.values())*len(c['momentum_GeV'])*len(c['charge_e']):
        raise ValueError('Unexpected primary cases')
    cut = c['endcap_abs_eta_min']
    if np.any(data['eta_pos'][data['sample'] == 2] < cut) or np.any(data['eta_pos'][data['sample'] == 3] > -cut):
        raise ValueError('Cap bank lies outside the frozen angular region')


def summarize(c, data):
    cases = []
    masks = regions(data, c)
    for momentum in c['momentum_GeV']:
        for charge in c['charge_e']:
            case = dict(momentum_GeV=momentum, charge=charge, samples={})
            for name, region in masks.items():
                take = _case(data, momentum, charge) & region
                weights, bad = data['solid_angle_weight_sr'][take], data['incomplete'][take]
                if not take.any():
                    raise ValueError('Empty declared analysis region: '+name)
                stats = dict(tracks=int(take.sum()), weight_sr=float(weights.sum()),
                             incomplete_tracks=int(bad.sum()),
                             statuses={str(k): int(v) for k, v in zip(*np.unique(data['status'][take], return_counts=True))})
                for metric, threshold in METRICS.items():
                    stats[metric] = availability(data[metric][take] >= threshold, bad, weights, data['sample'][take])
                for prefix in ('', 'endcap_'):
                    for counter in COUNTERS[4:]:
                        stats[prefix+counter] = int(data[prefix+counter][take].sum())
                case['samples'][name] = stats
            cases.append(case)
    return cases


def write_table(summary, path):
    with Path(path).open('w', newline='') as stream:
        fields = ('system', 'momentum_GeV', 'charge', 'region', 'metric', 'tracks',
                  'incomplete_tracks', 'weight_sr', 'proven_lower_fraction',
                  'possible_upper_fraction', 'sampling_standard_error_lower',
                  'sampling_standard_error_upper')
        writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader()
        for case in summary['cases']:
            for region, stats in case['samples'].items():
                for metric in METRICS:
                    writer.writerow(dict(system=summary['configuration']['system'],
                        momentum_GeV=case['momentum_GeV'], charge=case['charge'],
                        region=region, metric=metric, tracks=stats['tracks'],
                        incomplete_tracks=stats['incomplete_tracks'], weight_sr=stats['weight_sr'],
                        **{key: stats[metric][key] for key in fields[8:]}))


def analyze(work, run, output):
    work, run, output = map(Path, (work, run, output))
    inputs = json.loads((work/'inputs.json').read_text()); c = inputs['configuration']
    for key in ('geometry', 'map'):
        if sha(ROOT/c[key]) != c[key+'_sha256']:
            raise ValueError('Prepared physical input changed: '+key)
    if sha(work/'primaries.npz') != inputs['files']['primaries.npz']:
        raise ValueError('Prepared primary bank changed')
    with np.load(work/'primaries.npz', allow_pickle=False) as source:
        data = dict(source)
    validate_primaries(data, c)
    panels = json.loads((ROOT/c['geometry']).read_text())['panels']
    if any(panel['kind'] not in ('barrel', 'endcap') or panel['station'] not in (1, 2, 3) for panel in panels):
        raise ValueError('Unexpected chamber family/logical station')
    catalog, geocheck = face_catalog(run/'geometry.csv', panels)
    metadata = json.loads((run/'metadata.json').read_text())
    actual_parameters = {
        'world_radius_m': c['world']['radius_m'], 'world_half_z_m': c['world']['half_z_m'],
        'entrance_radius_m': c['entrance']['radius_m'], 'entrance_half_z_m': c['entrance']['half_z_m'],
        'max_step_m': c['max_step_m'], 'surface_tolerance_m': c['surface_tolerance_m'],
        'rk_tolerance_m': c['rk_tolerance_m'], 'path_limit_m': c['path_limit_m'],
        'max_steps': c['max_steps'], 'chambers': len(panels), 'native_chamber_faces': 6*len(panels),
        'native_large_faces': 2*len(panels), 'tracks': len(data['track_id'])}
    for key, expected in actual_parameters.items():
        if key not in metadata or not np.isclose(metadata[key], expected, rtol=1e-13, atol=0):
            raise ValueError('Native metadata differs from prepared configuration: '+key)
    if metadata.get('mode') != c['navigation_mode'] or metadata.get('field') != 'map':
        raise ValueError('Expected native surface-audit in the prepared joint field map')
    hits = read_hits(run/'hits.csv'); n = len(data['track_id'])
    # Convert strings only after reading their actual lengths, preserving every
    # character without allocating a large fixed-width error buffer per track.
    status = ['missing']*n; error = ['']*n
    steps = np.zeros(n, 'i4'); final = np.full((n, 3), np.nan); path = np.zeros(n)
    corrections = np.zeros(n, 'i4'); guards = np.zeros(n, 'i4'); ambiguities = np.zeros(n, 'i4'); min_guard = np.full(n, np.nan)
    seen = set()
    with (run/'tracks.csv').open(newline='') as stream:
        for row in csv.DictReader(stream):
            i = int(row['track_id'])
            if i in seen or not 0 <= i < n:
                raise ValueError('Duplicate/unknown native track')
            seen.add(i); status[i] = row['status']; error[i] = row['error']; steps[i] = int(row['steps']); path[i] = float(row['path_m'])
            final[i] = [float(row[axis+'_m']) for axis in ('x', 'y', 'z')]
            corrections[i] = int(row['native_corrections']); guards[i] = int(row['guard_caps']); ambiguities[i] = int(row['parallel_ambiguities'])
            if row['min_guard_m']:
                min_guard[i] = float(row['min_guard_m'])
    if len(seen) != n:
        raise ValueError('Generated track denominator not retained')
    status, error = np.asarray(status, dtype=str), np.asarray(error, dtype=str)
    if not np.isfinite(final).all() or not np.isfinite(path).all():
        raise ValueError('Nonfinite native final state')
    if len(hits) and (np.any(np.diff(hits['track_id']) < 0) or hits['track_id'].min() < 0 or hits['track_id'].max() >= n):
        raise ValueError('Unordered/unknown native hit track')
    if metadata.get('raw_native_hits') != len(hits):
        raise ValueError('Native metadata/raw boundary-event count differs')
    actual_statuses = {str(key): int(value) for key, value in zip(*np.unique(status, return_counts=True))}
    if metadata.get('track_status_counts') != actual_statuses:
        raise ValueError('Native metadata/raw status counts differ')
    if len(hits) and np.any((hits['panel_index'] < 0) | (hits['panel_index'] >= len(panels))):
        raise ValueError('Unknown native hit panel')
    xyz = np.column_stack([hits[axis+'_m'] for axis in ('x', 'y', 'z')])
    direction = np.column_stack([hits[axis] for axis in ('dx', 'dy', 'dz')])
    if not np.isfinite(xyz).all() or not np.isfinite(direction).all() or not np.isfinite(hits['path_m']).all():
        raise ValueError('Nonfinite native boundary event')
    active = np.zeros(len(hits), bool); residual = np.zeros(len(hits)); excess = np.zeros(len(hits))
    station = np.zeros(len(hits), 'i1'); endcap = np.zeros(len(hits), bool); side = np.zeros(len(hits), 'i1')
    tol = max(10*c['surface_tolerance_m'], 1e-5)
    for j, body in enumerate(panels):
        ids = np.flatnonzero(hits['panel_index'] == j)
        if not len(ids):
            continue
        points = xyz[ids]; normals, bounds = geo.planes3(body)
        local = (points-body['origin_m'])@np.asarray(body['basis']); pn, pb = geo.polygon_planes(body['vertices_m'])
        active[ids] = (local[:, :2]@pn.T <= pb-c['active_border_m']+c['surface_tolerance_m']).all(axis=1)
        excess[ids] = np.maximum(0, (points@normals.T-bounds).max(axis=1)); station[ids] = body['station']; endcap[ids] = body['kind'] == 'endcap'
        if body['kind'] == 'endcap':
            side[ids] = 1 if body['origin_m'][2] > 0 else -1
        for face in range(6):
            ii = ids[hits['face_index'][ids] == face]
            if not len(ii):
                continue
            info = catalog[j, face]; residual[ii] = abs(xyz[ii]@info['normal']-info['bound'])
            if not np.all(hits['geometry_id'][ii] == info['id']) or not np.all(hits['is_large'][ii] == info['large']):
                raise ValueError('Native face ownership/64-bit ID changed')
    if len(hits) and max(residual.max(), excess.max()) > tol:
        raise ValueError('Native boundary position/finite bounds failed unchanged 10 um audit gate')
    counters = {prefix+key: np.zeros(n, 'i4') for prefix in ('', 'endcap_') for key in COUNTERS}
    counters.update({key: np.zeros(n, 'i1') for key in METRICS if '_station_' in key})
    offsets = np.searchsorted(hits['track_id'], np.arange(n+1)); clean = np.zeros(len(hits), bool)
    for i in range(n):
        lo, hi = offsets[i:i+2]; events = hits[lo:hi]
        if len(events) > 1 and (np.any(np.diff(events['path_m']) < -2*tol) or np.any(np.diff(events['sequence']) <= 0)):
            raise ValueError('Nonmonotonic native path/sequence')
        for prefix, pick in (('', np.ones(hi-lo, bool)), ('endcap_', endcap[lo:hi])):
            value = count_events(events[pick], catalog, active[lo:hi][pick], 2*c['surface_tolerance_m'])
            for key in COUNTERS:
                counters[prefix+key][i] = value[key]
            if not prefix:
                clean[lo+value['keep_indices']] = True
        for wheel in np.unique(station[lo:hi][endcap[lo:hi]]):
            pick = endcap[lo:hi] & (station[lo:hi] == wheel)
            value = count_events(events[pick], catalog, active[lo:hi][pick], 2*c['surface_tolerance_m'])
            for border in ('outer', 'active'):
                counters[f'endcap_station_{wheel}_{border}_paired'][i] = value[border+'_paired_stations'] > 0
    completed = np.isin(status, ['completed', 'returned_to_entrance'])
    uncertain = (counters['orphan_transitions'] > 0) | (completed & (counters['open_visits'] > 0)) | (ambiguities > 0)
    data.update(counters, status=status, error=error, steps=steps, final_position_m=final,
                path_m=path, native_corrections=corrections, guard_caps=guards,
                parallel_ambiguities=ambiguities, min_guard_step_m=min_guard,
                navigation_unqualified=uncertain, incomplete=(~completed) | uncertain)
    h = {key: hits[key] for key in hits.dtype.names}
    h.update(active=active, station=station, is_endcap=endcap, endcap_side=side,
             numerical_unique_event=clean, plane_residual_m=residual, finite_excess_m=excess,
             panel_source_id=np.asarray([panel['id'] for panel in panels]))
    output.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output/'tracks.npz', **data); np.savez_compressed(output/'hits.npz', **h)
    for filename in ('tracks.npz', 'hits.npz'):
        if (output/filename).stat().st_size >= 100_000_000:
            raise ValueError('Retained compressed artifact exceeds 100 MB; partition without dropping events')
    raw = {name: sha(run/name) for name in ('hits.csv', 'tracks.csv', 'geometry.csv', 'geometry-corners.csv', 'metadata.json')}
    summary = dict(configuration=c, cases=summarize(c, data),
        analysis_regions=dict(endcap_abs_eta_min=c['endcap_abs_eta_min'],
            cut_scope='Frozen initial-direction |eta| cut, independent of observed chambers; conditional endcap regions are not 4pi fractions.',
            full_sphere_sr=float(4*np.pi), cap_pair_sr=float(4*np.pi*(1-np.tanh(c['endcap_abs_eta_min']))),
            bank_scope='Samples 1 (sphere), 2 (+cap), 3 (-cap) are separate independent banks; cap precision rows are never added to sphere rows.'),
        native_metadata=metadata,
        audit=dict(geocheck, tracks=n, raw_boundary_hits=len(hits),
            unique_crossing_events=int(clean.sum()),
            max_hit_plane_residual_m=float(residual.max()) if len(hits) else 0.,
            max_finite_face_excess_m=float(excess.max()) if len(hits) else 0.,
            orphan_transitions=int(counters['orphan_transitions'].sum()),
            parallel_tolerance_ambiguities=int(ambiguities.sum()),
            navigation_unqualified_tracks=int(uncertain.sum()),
            tangent_events=int(counters['tangent_events'].sum()),
            statuses={str(k): int(v) for k, v in zip(*np.unique(status, return_counts=True))}),
        inputs=dict(geometry_sha256=c['geometry_sha256'], map_sha256=c['map_sha256'],
                    prepared_inputs_sha256=sha(work/'inputs.json'), primaries_sha256=sha(work/'primaries.npz'),
                    prepared_files_sha256=inputs['files'], native_files_sha256=raw),
        artifacts={name: dict(sha256=sha(output/name), bytes=(output/name).stat().st_size)
                   for name in ('tracks.npz', 'hits.npz')},
        postprocessing=source_state(), scope=SCOPE)
    write_table(summary, output/'availability.csv')
    summary['artifacts']['availability.csv'] = dict(sha256=sha(output/'availability.csv'), bytes=(output/'availability.csv').stat().st_size)
    save(output/'summary.json', summary)
    print(json.dumps(summary['audit'], indent=2))
    return data, h, summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    analyze(args.work, args.run, args.output)
