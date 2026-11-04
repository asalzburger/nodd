#!/usr/bin/env python3
"""Accumulate Geant4 physical steps and thin ACTS interactions per origin ray."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def slice_indices(eta, edges):
    eta = np.abs(np.asarray(eta, dtype=float))
    index = np.searchsorted(edges, eta, side='right') - 1
    index[eta == edges[-1]] = len(edges) - 2
    if not np.all(np.isfinite(eta)) or np.any((index < 0) | (index >= len(edges) - 1)):
        raise ValueError('Ray outside configured absolute-eta support')
    return index


def cumulative_at(grid, owner, start, end, weight, tracks, distributed):
    """Evaluate exact per-ray prefix budgets without a steps × checkpoints array.

    A uniform segment contributes w*clip((q-a)/(b-a),0,1). Its two changes
    of slope/intercept form difference arrays. Point interactions contribute
    at their first checkpoint q>=a. Zero-projection segments are points too.
    """
    grid = np.asarray(grid, dtype=float)
    owner = np.asarray(owner, dtype=int)
    start, end, weight = (np.asarray(a, dtype=float) for a in (start, end, weight))
    if (grid.ndim != 1 or len(grid) < 2 or not np.all(np.isfinite(grid))
            or np.any(np.diff(grid) <= 0) or tracks < 0):
        raise ValueError('Finite increasing checkpoint grid required')
    if not (owner.shape == start.shape == end.shape == weight.shape):
        raise ValueError('Step-vector shapes differ')
    if (np.any((owner < 0) | (owner >= tracks)) or not all(np.all(np.isfinite(a)) for a in (start, end, weight))
            or np.any(weight < 0) or np.any(start < grid[0]) or np.any(end < start)
            or np.any(end > grid[-1])):
        raise ValueError('Invalid/out-of-grid material segment')
    width = len(grid) + 1
    left = np.searchsorted(grid, start, side='left')
    right = np.searchsorted(grid, end, side='left')
    def changes(index, values):
        return np.bincount(owner * width + index, weights=values,
                           minlength=tracks * width).reshape(tracks, width)
    continuous = (end > start) if distributed else np.zeros(len(start), dtype=bool)
    slope = np.divide(weight, end - start, out=np.zeros_like(weight), where=continuous)
    gradient = changes(left, slope) - changes(right, slope)
    intercept = changes(left, np.where(continuous, -slope * start, weight)) + changes(right, slope * end)
    result = (np.cumsum(gradient, axis=1)[:, :-1] * grid
              + np.cumsum(intercept, axis=1)[:, :-1])
    total = np.bincount(owner, weights=weight, minlength=tracks)
    if not np.allclose(result[:, -1], total, rtol=1.e-8, atol=1.e-9):
        raise ValueError('Per-ray cumulative endpoint does not conserve material')
    if np.any(np.diff(result, axis=1) < -1.e-8 * np.maximum(1, total[:, None])):
        raise ValueError('Cumulative material decreases')
    return result


def finalize(count, total, square):
    if count <= 0:
        raise ValueError('Empty eta slice cannot supply a profile')
    mean = total / count
    return {'mean': mean.tolist(),
            'variance': (np.maximum(0, square / count - mean * mean) / count).tolist()}


def validate_config(config):
    edges = np.asarray(config['abs_eta_edges'], dtype=float)
    if (config['schema_version'] != 1 or edges[0] != 0 or len(edges) < 2
            or not np.all(np.isfinite(edges)) or np.any(np.diff(edges) <= 0)
            or set(config['axes']) != {'r', 'abs_z', 'd'}):
        raise ValueError('Invalid cumulative diagnostic configuration')
    grids = {}
    for axis, setting in config['axes'].items():
        maximum, step = setting['maximum_mm'], setting['step_mm']
        if (not np.isfinite(maximum) or not np.isfinite(step) or maximum <= 0 or step <= 0
                or not np.isclose(maximum / step, round(maximum / step))):
            raise ValueError('Grid maximum must be a positive integer multiple of spacing')
        slices = setting['eta_slices']
        if (not slices or len(set(slices)) != len(slices)
                or any(type(s) is not int or not 0 <= s < len(edges) - 1 for s in slices)):
            raise ValueError('Invalid/repeated eta slice')
        grids[axis] = np.linspace(0, maximum, round(maximum / step) + 1)
    return edges, grids


def reduce_sample(path, config, distributed, expected_tracks):
    import awkward as ak
    import uproot
    edges, grids = validate_config(config)
    accum = {axis: {s: {'count': 0, **{q: [np.zeros(len(grid)), np.zeros(len(grid))]
                                    for q in ('X0', 'L0')}}
                    for s in config['axes'][axis]['eta_slices']}
             for axis, grid in grids.items()}
    tracks = steps = 0
    slice_counts = np.zeros(len(edges) - 1, dtype=np.int64)
    totals = {'X0': 0., 'L0': 0.}
    max_root_residual = {'X0': 0., 'L0': 0.}
    branches = ['v_eta', 'v_x', 'v_y', 'v_z', 'v_px', 'v_py', 'v_pz',
                't_X0', 't_L0', 'mat_x', 'mat_y', 'mat_z',
                'mat_step_length', 'mat_X0', 'mat_L0']
    if distributed:
        branches += ['mat_dx', 'mat_dy', 'mat_dz']
    with uproot.open(path) as root:
        for batch in root['material_tracks'].iterate(branches, step_size=1000, library='ak'):
            flat = lambda name: np.asarray(ak.to_numpy(ak.flatten(batch[name])), dtype=float)
            ray = lambda name: np.asarray(ak.to_numpy(batch[name]), dtype=float)
            n = len(batch)
            membership = slice_indices(ray('v_eta'), edges)
            slice_counts += np.bincount(membership, minlength=len(slice_counts))
            if any(np.any(np.abs(ray('v_' + c)) > 1.e-9) for c in ('x', 'y', 'z')):
                raise ValueError('Only origin rays are supported')
            lengths = np.asarray(ak.to_numpy(ak.num(batch['mat_x'])), dtype=int)
            for branch in branches:
                if branch.startswith('mat_') and not np.array_equal(ak.to_numpy(ak.num(batch[branch])), lengths):
                    raise ValueError('Misaligned material-step vectors')
            owner = np.repeat(np.arange(n), lengths)
            position = np.column_stack([flat('mat_' + c) for c in ('x', 'y', 'z')])
            length = flat('mat_step_length')
            if not np.all(np.isfinite(position)) or not np.all(np.isfinite(length)) or np.any(length < 0):
                raise ValueError('Invalid position/material path length')
            momentum = np.column_stack([ray('v_p' + c) for c in ('x', 'y', 'z')])
            norm = np.linalg.norm(momentum, axis=1)
            if np.any(norm <= 0) or not np.all(np.isfinite(norm)):
                raise ValueError('Invalid ray momentum')
            direction = momentum / norm[:, None]
            projection = np.sum(position * direction[owner], axis=1)
            if (np.any(projection < -1.e-4)
                    or np.any(np.linalg.norm(position - projection[:, None] * direction[owner], axis=1) > .01)):
                raise ValueError('Material positions are not on origin straight rays within float32 precision')
            if distributed:
                step_direction = np.column_stack([flat('mat_d' + c) for c in ('x', 'y', 'z')])
                if not np.all(np.isfinite(step_direction)) or np.any(np.linalg.norm(step_direction - direction[owner], axis=1) > 1.e-5):
                    raise ValueError('Non-straight/unit Geant4 step direction')
                endpoint = position + length[:, None] * step_direction
            else:
                endpoint = position
            weights = {}
            for q in ('X0', 'L0'):
                scale = flat('mat_' + q)
                if np.any(scale <= 0):
                    raise ValueError('Nonpositive radiation/interaction length')
                weights[q] = length / scale
                if not np.all(np.isfinite(weights[q])):
                    raise ValueError('Invalid material budget')
                total = np.bincount(owner, weights=weights[q], minlength=n)
                observed = ray('t_' + q)
                if not np.all(np.isfinite(observed)) or not np.allclose(total, observed, rtol=5.e-6, atol=1.e-7):
                    raise ValueError('Step sum differs from recorded per-ray total')
                max_root_residual[q] = max(max_root_residual[q], float(np.max(abs(total - observed), initial=0)))
                totals[q] += float(total.sum())
            coordinates = lambda p, axis: (np.hypot(p[:, 0], p[:, 1]) if axis == 'r'
                                          else np.abs(p[:, 2]) if axis == 'abs_z'
                                          else np.linalg.norm(p, axis=1))
            for axis, grid in grids.items():
                eligible = np.isin(membership, list(accum[axis]))
                selected_tracks = np.flatnonzero(eligible)
                selected_steps = eligible[owner]
                local = np.cumsum(eligible) - 1
                local_owner = local[owner[selected_steps]]
                start = coordinates(position[selected_steps], axis)
                end = coordinates(endpoint[selected_steps], axis)
                for s in accum[axis]:
                    accum[axis][s]['count'] += int(np.count_nonzero(membership[selected_tracks] == s))
                for q in ('X0', 'L0'):
                    curves = cumulative_at(grid, local_owner, start, end, weights[q][selected_steps],
                                           len(selected_tracks), distributed)
                    for s in accum[axis]:
                        values = curves[membership[selected_tracks] == s]
                        accum[axis][s][q][0] += values.sum(axis=0)
                        accum[axis][s][q][1] += (values * values).sum(axis=0)
            tracks += n
            steps += int(lengths.sum())
    if tracks != expected_tracks or int(slice_counts.sum()) != tracks:
        raise ValueError('Sample track count/support differs from requested input')
    return {'tracks': tracks, 'steps': steps, 'eta_slice_counts': slice_counts.tolist(),
            'global_mean': {q: totals[q] / tracks for q in totals},
            'maximum_step_sum_minus_root_total_absolute': max_root_residual,
            'axes': {axis: {'grid_mm': grid.tolist(), 'slices': [
                {'eta_index': s, 'tracks': item['count'], 'quantities': {
                    q: finalize(item['count'], *item[q]) for q in ('X0', 'L0')}}
                for s, item in accum[axis].items()]} for axis, grid in grids.items()}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--geant4', type=Path, required=True)
    ap.add_argument('--validation', type=Path, required=True)
    ap.add_argument('--config', type=Path, default=Path(__file__).with_name('cumulative_config.json'))
    ap.add_argument('--expected-tracks', type=int, default=100000)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    config = json.loads(args.config.read_text())
    out = {'schema_version': 1, 'status': 'PROTOTYPE cumulative material diagnostic',
           'configuration': config,
           'normalization': 'Per-ray cumulative values; every ray in each eta slice including zeros; population SEM squared=M2/N^2',
           'position_convention': 'Geant4: homogeneous physical pre-step to pre-step+length*direction; partial steps integrated at checkpoints. ACTS validation: thin budget jump at recorded portal interaction. Last eta upper edge inclusive; others half-open.',
           'sampling_tolerances': {'origin_mm': 1.e-9, 'float32_ray_position_mm': .01,
                                   'unit_direction_absolute': 1.e-5, 'root_total_relative': 5.e-6},
           'provenance': {'exporter_sha256': sha256(__file__), 'configuration_sha256': sha256(args.config),
                          'geant4_sha256': sha256(args.geant4), 'validation_sha256': sha256(args.validation)},
           'samples': {}}
    for name, path, distributed in [('geant4', args.geant4, True), ('validation', args.validation, False)]:
        out['samples'][name] = reduce_sample(path, config, distributed, args.expected_tracks)
        print(name, out['samples'][name]['tracks'], 'rays,', out['samples'][name]['steps'], 'steps', flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
