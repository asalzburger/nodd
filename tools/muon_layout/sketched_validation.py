"""Bounded native crossing checks for inward B1 and rotated B2 chambers.

Zero-field ACTS events are compared with independent straight-ray prism tests.
A small unchanged-map run checks finite native events with both charges; every
unfinished track is retained. Neither run measures reconstruction efficiency.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import numpy as np

from . import geometry as geo
from .acts.analyze import count_events, face_catalog, read_hits
from .acts.prepare import entrance, export_geometry, export_map, write_tracks
from .sketched_artifacts import BASELINE, ROOT, SCOPE
from .wheels_artifacts import EXPECTED_PROPAGATOR
from . import sketched_stagger as stagger

SEED = 906320
ETA_MIN, ETA_MAX = 0.0, 1.0
SOURCES = ('tools/muon_layout/sketched_validation.py', 'tools/muon_layout/sketched_stagger.py', 'tools/muon_layout/barrel_overlap.py',
           'tools/muon_layout/sketched_artifacts.py',
           'tools/muon_layout/sketched-stagger-config.json', 'tools/muon_layout/acts/analyze.py',
           'tools/muon_layout/acts/prepare.py', 'tools/muon_layout/geometry.py')
ENTRANCE = dict(radius_m=4.35, half_z_m=6.4684, forward_offset_m=.00001)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')


def bank(n):
    rng = np.random.default_rng(SEED)
    mu = rng.uniform(np.tanh(ETA_MIN), np.tanh(ETA_MAX), n)
    phi = rng.uniform(0, 2 * np.pi, n)
    d = np.column_stack((np.sqrt(1 - mu * mu) * np.cos(phi),
                         np.sqrt(1 - mu * mu) * np.sin(phi), mu))
    return np.concatenate((d, d * [1, 1, -1]))


def expected(panels, directions, border):
    answer = np.zeros((len(directions), 3), bool)
    for panel in panels:
        if panel['kind'] != 'barrel':
            continue
        hits = geo.midplane_hits(panel, directions, border, full_depth=True)
        answer[:, panel['station'] - 1] |= np.isfinite(hits)
    return answer


def station_distances(panels, directions, border):
    """First full-depth same-cassette crossing per distinct station, from the IP."""
    answer = np.full((len(directions), 3), np.inf)
    for panel in panels:
        distances = geo.midplane_hits(panel, directions, border, full_depth=True)
        s = panel['station'] - 1
        answer[:, s] = np.minimum(answer[:, s], distances)
    return answer


def paired(before, after):
    delta = after.astype(int) - before.astype(int)
    return dict(before_count=int(before.sum()), after_count=int(after.sum()),
        before_fraction=float(before.mean()), after_fraction=float(after.mean()),
        delta_percentage_points=float(100 * delta.mean()),
        paired_sampling_standard_error_pp=float(100 * delta.std(ddof=1) / np.sqrt(len(delta))),
        gains=int(np.sum(delta == 1)), losses=int(np.sum(delta == -1)),
        quarter_deltas_pp=[float(100 * part.mean()) for part in np.array_split(delta, 4)])


def spacing(distances):
    valid = np.isfinite(distances).all(axis=1)
    ordered = valid & (distances[:, 1] > distances[:, 0]) & (distances[:, 2] > distances[:, 1])
    take = distances[ordered]
    quantiles = [0, .05, .5, .95, 1]
    def summary(values):
        return np.quantile(values, quantiles).tolist() if len(values) else []
    return dict(three_station_count=int(valid.sum()), station_order_inversions=int(np.sum(valid & ~ordered)),
        quantiles=quantiles, ordered_count=int(ordered.sum()),
        first_to_third_chord_m=summary(take[:, 2] - take[:, 0]),
        first_to_middle_chord_m=summary(take[:, 1] - take[:, 0]),
        middle_to_third_chord_m=summary(take[:, 2] - take[:, 1]),
        middle_fraction_of_total=summary((take[:, 1] - take[:, 0]) / (take[:, 2] - take[:, 0])),
        convention='Earliest full-depth same-cassette mid-plane hit per station. Straight unit IP rays, so distance differences are chord lengths. Conditional geometric spacing, not bending integral or fitted momentum resolution.')


def full_sphere(before, after, output):
    n, seed = 65536, 40088
    rng = np.random.default_rng(seed)
    mu, phi = rng.uniform(-1, 1, n), rng.uniform(0, 2 * np.pi, n)
    directions = np.c_[np.sqrt(1 - mu * mu) * np.cos(phi), np.sqrt(1 - mu * mu) * np.sin(phi), mu]
    data = dict(direction=directions, eta=np.arctanh(mu), phi_rad=phi)
    results = {}
    chambers = after['configuration']['chambers']
    cfg = after['sketched_stagger_revision']
    dimensions = stagger.stagger_dimensions(chambers, cfg)
    template_config = dict(cfg, max_barrel_length_m=2 * max(chambers['barrel_half_z_m']))
    templates = list(stagger.candidates(chambers, template_config, dimensions))
    fixed = [p for p in after['panels'] if not (p['kind'] == 'barrel' and p['station'] in (1, 2))]
    noframe = [p for p in after['without_support_panels'] if p['kind'] == 'barrel' and p['station'] in (1, 2)] + fixed
    for border, label in ((0., 'outline'), (.03, 'border30mm')):
        distances = {name: station_distances(model['panels'], directions, border)
                     for name, model in (('before', before), ('after', after))}
        masks = {name: np.isfinite(value) for name, value in distances.items()}
        noframe_mask = np.isfinite(station_distances(noframe, directions, border))
        template_mask = np.isfinite(station_distances(templates + fixed, directions, border))
        rec = {f'station{s+1}': paired(masks['before'][:, s], masks['after'][:, s]) for s in range(3)}
        for k in (1, 2, 3):
            old, new = masks['before'].sum(axis=1) >= k, masks['after'].sum(axis=1) >= k
            rec[f'at_least_{k}_stations'] = paired(old, new)
        b1_only = masks['before'].copy()
        b1_only[:, 0] = masks['after'][:, 0]
        b2_only = masks['before'].copy()
        b2_only[:, 1] = masks['after'][:, 1]
        rec['three_station_component_controls'] = dict(
            changed_B1_old_B2=paired(masks['before'].all(axis=1), b1_only.all(axis=1)),
            old_B1_changed_B2=paired(masks['before'].all(axis=1), b2_only.all(axis=1)),
            scope='Same-bank mixed-component straight-geometry diagnostics only; no separately exported or selected detector.')
        loss = masks['before'].all(axis=1) & ~masks['after'].all(axis=1)
        classes = dict(fixed_frame_packing=loss & noframe_mask.all(axis=1),
            longitudinal_seams_and_packing=loss & ~noframe_mask.all(axis=1) & template_mask.all(axis=1),
            finite_transverse_or_end_reach=loss & ~template_mask.all(axis=1))
        rec['three_station_loss_localization'] = {}
        for name, mask in classes.items():
            ids = np.flatnonzero(mask)
            rec['three_station_loss_localization'][name] = dict(count=len(ids),
                direction_ids=ids.tolist(),
                witnesses=[dict(direction_id=int(i), eta=float(np.arctanh(mu[i])), phi_deg=float(np.degrees(phi[i]))) for i in ids[:5]])
        assert sum(int(x.sum()) for x in classes.values()) == int(loss.sum())
        rec['spacing'] = {name: spacing(d) for name, d in distances.items()}
        common_three = masks['before'].all(axis=1) & masks['after'].all(axis=1)
        rec['common_three_station_spacing'] = {name: spacing(d[common_three]) for name, d in distances.items()}
        barrel_distances = {name: station_distances(
            [p for p in model['panels'] if p['kind'] == 'barrel'], directions, border)
            for name, model in (('before', before), ('after', after))}
        rec['barrel_only_spacing'] = {name: spacing(value) for name, value in barrel_distances.items()}
        rec['barrel_only'] = {f'B{s+1}': paired(np.isfinite(barrel_distances['before'][:, s]),
            np.isfinite(barrel_distances['after'][:, s])) for s in range(3)}
        results[label] = rec
        for name in ('before', 'after'):
            data[label + '_' + name + '_station_distance_m'] = distances[name]
            data[label + '_' + name + '_barrel_station_distance_m'] = barrel_distances[name]
        for name, mask in classes.items():
            data[label + '_loss_' + name] = mask
    starts = entrance(directions, ENTRANCE)[1]
    inside = [dict(panel_id=p['id'], directions=np.flatnonzero(geo.contains(p, starts)).tolist())
              for p in after['panels'] if geo.contains(p, starts).any()]
    assert not inside, inside
    first_entry = np.full(n, np.inf)
    for p in after['panels']:
        entry, _ = geo.ray_intervals(p, directions)
        first_entry = np.minimum(first_entry, entry)
    start_distances = np.linalg.norm(starts, axis=1)
    finite = np.isfinite(first_entry)
    assert (first_entry[finite] > start_distances[finite]).all()
    data['start_m'] = starts
    np.savez_compressed(output / 'full-sphere-inputs-and-distances.npz', **data)
    return dict(samples=n, seed=seed, distribution='iid uniform cos(theta) and phi over full4pi; unmirrored; no hit selection',
        results=results, entrance=ENTRANCE, starts_inside_chambers=inside,
        minimum_start_to_first_prism_ray_entry_m=float(np.min(first_entry[finite] - start_distances[finite])),
        archive_sha256=sha(output / 'full-sphere-inputs-and-distances.npz'),
        scope='Whole finite same-cassette depth crossing; station OR includes barrel and endcap. No material veto, response, native transport or reconstructed efficiency.')


def analyze_native(directory, panels, data, straight):
    catalog, native = face_catalog(directory / 'geometry.csv', panels)
    hits = read_hits(directory / 'hits.csv')
    rows = list(csv.DictReader((directory / 'tracks.csv').open()))
    assert [int(r['track_id']) for r in rows] == list(range(len(data['track_id'])))
    assert not len(hits) or (np.diff(hits['track_id']) >= 0).all()
    active = np.zeros(len(hits), bool)
    residual = 0.
    for index, panel in enumerate(panels):
        select = np.flatnonzero(hits['panel_index'] == index)
        if not len(select):
            continue
        points = np.column_stack([hits[k + '_m'][select] for k in ('x', 'y', 'z')])
        normals, bounds = geo.planes3(panel)
        assert (points @ normals.T <= bounds + 1e-6).all()
        local = (points - panel['origin_m']) @ np.asarray(panel['basis'])
        n2, b2 = geo.polygon_planes(panel['vertices_m'])
        active[select] = (local[:, :2] @ n2.T <= b2 - .03 + 1e-12).all(axis=1)
        for j in select:
            info = catalog[index, int(hits['face_index'][j])]
            point = np.array([hits[k + '_m'][j] for k in ('x', 'y', 'z')])
            residual = max(residual, abs(float(point @ info['normal'] - info['bound'])))
    assert residual < 1e-6
    outline = np.zeros((len(rows), 3), bool)
    border = np.zeros_like(outline)
    barrel_mask = np.array([p['kind'] == 'barrel' for p in panels])
    station = np.array([p['station'] for p in panels])
    for track in range(len(rows)):
        take = np.flatnonzero(hits['track_id'] == track)
        for s in (1, 2, 3):
            selected = take[barrel_mask[hits['panel_index'][take]] & (station[hits['panel_index'][take]] == s)]
            result = count_events(hits[selected], catalog, active[selected])
            outline[track, s - 1] = result['outer_paired_stations'] > 0
            border[track, s - 1] = result['active_paired_stations'] > 0
    statuses = Counter(r['status'] for r in rows)
    result = dict(tracks=len(rows), statuses=dict(statuses), raw_hits=len(hits),
                  native_faces=native, maximum_native_plane_residual_m=residual,
                  station_paired_counts=outline.sum(axis=0).tolist(),
                  border_station_paired_counts=border.sum(axis=0).tolist(),
                  three_barrel_pairs=int(outline.all(axis=1).sum()),
                  three_border_barrel_pairs=int(border.all(axis=1).sum()),
                  incomplete_track_ids=[int(r['track_id']) for r in rows if r['status'] != 'completed'])
    if straight:
        prediction, inset = expected(panels, data['direction'], 0), expected(panels, data['direction'], .03)
        mismatch = np.argwhere(outline != prediction).tolist()
        border_mismatch = np.argwhere(border != inset).tolist()
        result.update(analytic_outline_mismatches=mismatch, analytic_border_mismatches=border_mismatch)
        assert not mismatch and not border_mismatch, result
        assert not result['incomplete_track_ids'], result
    return result


def run(args):
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    hashes = {}
    for name in SOURCES:
        actual = (ROOT / name).read_bytes()
        assert actual == subprocess.check_output(['git', 'show', revision + ':' + name], cwd=ROOT), name
        hashes[name] = hashlib.sha256(actual).hexdigest()
    assert sha(args.executable) == EXPECTED_PROPAGATOR
    before, after = [json.loads(p.read_text()) for p in (BASELINE, args.geometry)]
    assert before['magnetic_configuration'] == after['magnetic_configuration']
    args.output.mkdir(parents=True, exist_ok=True)
    export_geometry({'geometry': str(args.geometry.resolve().relative_to(ROOT))}, args.output / 'geometry.dat')
    directions = bank(args.directions_per_end)
    starts = entrance(directions, ENTRANCE)[1]
    assert not any(geo.contains(p, starts).any() for p in after['panels'])
    data = dict(track_id=np.arange(len(directions)), momentum_GeV=np.full(len(directions), 100.),
                charge=np.ones(len(directions)), start_m=starts, direction=directions)
    np.savez_compressed(args.output / 'straight-inputs.npz', **data)
    geometry_hash, map_hash = sha(args.geometry), sha(args.map)
    field_source = ROOT / 'docs/validation/DES-040/wheels-2026-10-20/magnetic/candidate-map.npz'
    with tempfile.TemporaryDirectory(prefix='pr90-refined-map-') as temporary:
        regenerated = Path(temporary) / 'map.bin'
        export_map({'map': str(field_source.relative_to(ROOT))}, regenerated)
        assert sha(regenerated) == map_hash, 'Native binary map differs from retained joint-field NPZ'
    common = [str(args.executable.resolve()), '--geometry', str(args.output / 'geometry.dat'),
              '--mode', 'surface-audit', '--world-radius-m', '9.1', '--world-half-z-m', '13.3',
              '--entrance-radius-m', '4.35', '--entrance-half-z-m', '6.4684',
              '--max-step-m', '.1', '--tolerance-m', '1e-8', '--rk-tolerance-m', '1e-11',
              '--path-limit-m', '100', '--max-steps', '20000']
    reports, commands = {}, {}
    for name in ('straight', 'curved-smoke'):
        if name == 'curved-smoke':
            # Fixed, preselected directions: equal numbers on each end, no hit selection.
            chosen = np.r_[np.arange(32), np.arange(args.directions_per_end, args.directions_per_end + 32)]
            dd, ss = directions[chosen], starts[chosen]
            data = dict(track_id=np.arange(256), momentum_GeV=np.repeat([5., 5., 100., 100.], 64),
                        charge=np.repeat([-1, 1, -1, 1], 64), start_m=np.tile(ss, (4, 1)), direction=np.tile(dd, (4, 1)))
            np.savez_compressed(args.output / 'curved-inputs.npz', **data)
        target = args.output / name
        target.mkdir(exist_ok=True)
        write_tracks(target / 'input.dat', data)
        command = common + ['--tracks', str(target / 'input.dat'), '--output-dir', str(target)]
        command += ['--field', 'zero'] if name == 'straight' else ['--map', str(args.map.resolve())]
        result = subprocess.run(command, capture_output=True, text=True)
        (target / 'execution.log').write_text(result.stdout + result.stderr)
        assert result.returncode == 0, result.stderr
        reports[name] = analyze_native(target, after['panels'], data, name == 'straight')
        commands[name] = [str(Path(x).resolve().relative_to(ROOT)) if x.startswith(str(ROOT)) else x for x in command]
    compare_directions = bank(32768)
    geometric = {}
    for label, geometry in (('before', before), ('refined', after)):
        for inset, name in ((0, 'outline'), (.03, 'border30mm')):
            counts = expected(geometry['panels'], compare_directions, inset)
            geometric[label + '_' + name] = dict(station_counts=counts.sum(axis=0).tolist(),
                station_fractions=counts.mean(axis=0).tolist(), three_station_count=int(counts.all(axis=1).sum()),
                three_station_fraction=float(counts.all(axis=1).mean()))
    assert sha(args.geometry) == geometry_hash and sha(args.map) == map_hash
    assert all(sha(ROOT / p) == h for p, h in hashes.items())
    sphere = full_sphere(before, after, args.output)
    report = dict(status='DRAFT bounded geometry/native crossing validation; no response or momentum measurement',
        source_revision=revision, source_sha256=hashes, geometry_sha256=geometry_hash,
        unchanged_field_binary_sha256=map_hash, native_binary_sha256=sha(args.executable),
        unchanged_field_source=str(field_source.relative_to(ROOT)), unchanged_field_npz_sha256=sha(field_source),
        seed=SEED, native_reports=reports, native_commands=commands, full_sphere=sphere,
        geometric_bank=dict(directions=65536, sampling='32768 iid uniform cos(theta) within 0<abs(eta)<1, mirrored to 65536 rows; geometric barrel proxy',
                            eta_abs_range=[ETA_MIN, ETA_MAX], results=geometric),
        limits=['Only geometric_bank uses the declared central barrel band; full_sphere uses the separately declared full4pi iid bank.',
                'Curved run is only a 256-track smoke check; unfinished and field-masked rows are retained.',
                'No material scattering, energy loss, chamber response, segment fit or reconstructed efficiency.'])
    save(args.output / 'validation.json', report)
    print(json.dumps(dict(native=reports, geometric=geometric), indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--geometry', type=Path, default=SCOPE / 'candidate/geometry.json')
    p.add_argument('--output', type=Path, default=SCOPE / 'native-validation')
    p.add_argument('--executable', type=Path, default=ROOT / 'reference/cache/pr90-wheels/build/nodd-muon-wheels-propagate')
    p.add_argument('--map', type=Path, default=ROOT / 'reference/cache/pr90-wheels/after/map.bin')
    p.add_argument('--directions-per-end', type=int, default=512)
    args = p.parse_args()
    if args.directions_per_end < 32:
        p.error('at least 32 fixed smoke directions per end are required')
    run(args)


if __name__ == '__main__':
    main()
