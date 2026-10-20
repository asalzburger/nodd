"""Paired before/after bounds for the shortened-ECT wheel PROTOTYPE.

CLI: ``compare.py --before BEFORE_OUTPUT --after AFTER_OUTPUT --output DIR``.
The physical comparison changes chambers and the ECT field together. It is
therefore not an attribution of every difference to chamber geometry alone.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.muon_layout.wheels_acts.analyze import (
    METRICS, regions, sampling_error, sha, save, source_state, validate_primaries)

PRIMARY_KEYS = ('track_id', 'direction_id', 'momentum_GeV', 'charge', 'sample',
                'direction', 'entrance_position_m', 'start_m', 'entrance_kind',
                'eta_pos', 'phi_pos_deg', 'eta_bin', 'phi_bin',
                'solid_angle_weight_sr', 'eta_edges', 'phi_edges_deg')
PHYSICAL_KEYS = {'system', 'geometry', 'map', 'geometry_sha256', 'map_sha256'}
SCOPE = ('Paired end-to-end vacuum chamber/field comparison with identical '
         'primary IDs, directions, launch, world and numerical settings. '
         'Both chamber layout and ECT field change; chamber-only attribution '
         'is not established. Unresolved-event bounds are not confidence intervals.')


def load(path):
    path = Path(path)
    summary = json.loads((path/'summary.json').read_text())
    for name in ('tracks.npz', 'hits.npz'):
        if sha(path/name) != summary['artifacts'][name]['sha256']:
            raise ValueError('Retained analysis artifact changed: '+str(path/name))
    with np.load(path/'tracks.npz', allow_pickle=False) as data:
        tracks = dict(data)
    validate_primaries(tracks, summary['configuration'])
    return tracks, summary


def paired_metric(before, after, incomplete_before, incomplete_after, weights, samples):
    """Tight per-event [Lafter-Ubefore, Uafter-Lbefore] followed by averaging."""
    before, after, ib, ia = [np.asarray(value, bool) for value in
                            (before, after, incomplete_before, incomplete_after)]
    weights, samples = np.asarray(weights, float), np.asarray(samples)
    if not len(before) or any(value.shape != before.shape for value in (after, ib, ia, weights, samples)):
        raise ValueError('Nonempty equal paired vectors required')
    ub, ua = before | ib, after | ia
    lower = after.astype('i1')-ub.astype('i1')
    upper = ua.astype('i1')-before.astype('i1')
    if np.any(lower > upper):
        raise ValueError('Invalid paired event bounds')
    norm = weights/weights.sum()
    mean = lambda value: float(norm@value.astype(float))
    common = ~ib & ~ia
    # Bound the estimated sampling SE over every allowed assignment of the
    # unresolved outcomes. In each iid stratum, sample var(D)/n is at most
    # sum(max(lower^2, upper^2))/(n*(n-1)); dropping the squared sample mean
    # makes this conservative. This is not a model of unresolved transport.
    conservative_variance = 0.
    conservative = None
    if not np.any(samples == 0):
        for bank in np.unique(samples):
            pick = samples == bank; size = int(pick.sum())
            if size < 2 or not np.allclose(weights[pick], weights[pick][0], rtol=1e-12, atol=0):
                break
            fraction = float(norm[pick].sum())
            conservative_variance += fraction*fraction*float(np.maximum(lower[pick]**2, upper[pick]**2).sum())/(size*(size-1))
        else:
            conservative = float(np.sqrt(conservative_variance))
    gained, lost = after & ~ub, before & ~ua
    return dict(
        before_lower_fraction=mean(before), before_upper_fraction=mean(ub),
        after_lower_fraction=mean(after), after_upper_fraction=mean(ua),
        change_lower_fraction=mean(lower), change_upper_fraction=mean(upper),
        change_lower_sampling_standard_error=sampling_error(lower, weights, samples),
        change_upper_sampling_standard_error=sampling_error(upper, weights, samples),
        conservative_true_change_sampling_standard_error_upper=conservative,
        definitely_gained_tracks=int(gained.sum()), definitely_lost_tracks=int(lost.sum()),
        definitely_gained_fraction=mean(gained), definitely_lost_fraction=mean(lost),
        common_complete_tracks=int(common.sum()),
        common_complete_change_diagnostic=(float(weights[common]@(after[common].astype(float)-before[common].astype(float))/weights[common].sum())
                                           if common.any() else None),
        scope='Bounds keep every unresolved event; sampling errors are separate. Common-complete change is a conditional diagnostic only.')


def contingency(before, after):
    result = {}
    for left in np.unique(before):
        result[str(left)] = {str(right): int(np.count_nonzero((before == left) & (after == right)))
                             for right in np.unique(after)}
    return result


def compare(before_path, after_path, output):
    before_path, after_path, output = map(Path, (before_path, after_path, output))
    before, bs = load(before_path); after, ass = load(after_path)
    bc, ac = bs['configuration'], ass['configuration']
    if {key: value for key, value in bc.items() if key not in PHYSICAL_KEYS} != {key: value for key, value in ac.items() if key not in PHYSICAL_KEYS}:
        raise ValueError('Common launch/world/sampling/numerical configuration differs')
    if any(not np.array_equal(before[key], after[key]) for key in PRIMARY_KEYS):
        raise ValueError('Before/after primary IDs or generated conditions differ')
    cases = []
    masks = regions(before, bc)
    for momentum in bc['momentum_GeV']:
        for charge in bc['charge_e']:
            case = dict(momentum_GeV=momentum, charge=charge, samples={})
            common_case = (before['momentum_GeV'] == momentum) & (before['charge'] == charge)
            for label, mask in masks.items():
                take = common_case & mask
                weights, samples = before['solid_angle_weight_sr'][take], before['sample'][take]
                result = dict(tracks=int(take.sum()), weight_sr=float(weights.sum()),
                    before_incomplete_tracks=int(before['incomplete'][take].sum()),
                    after_incomplete_tracks=int(after['incomplete'][take].sum()),
                    status_contingency=contingency(before['status'][take], after['status'][take]),
                    completion_contingency=contingency(before['incomplete'][take], after['incomplete'][take]))
                for metric, threshold in METRICS.items():
                    result[metric] = paired_metric(before[metric][take] >= threshold, after[metric][take] >= threshold,
                        before['incomplete'][take], after['incomplete'][take], weights, samples)
                case['samples'][label] = result
            cases.append(case)
    output.mkdir(parents=True, exist_ok=True)
    summary = dict(scope=SCOPE, configuration=dict(common={key: value for key, value in bc.items() if key not in PHYSICAL_KEYS},
        before={key: bc[key] for key in sorted(PHYSICAL_KEYS)}, after={key: ac[key] for key in sorted(PHYSICAL_KEYS)}),
        cases=cases, inputs=dict(before_summary_sha256=sha(before_path/'summary.json'),
            after_summary_sha256=sha(after_path/'summary.json'),
            before_tracks_sha256=sha(before_path/'tracks.npz'), after_tracks_sha256=sha(after_path/'tracks.npz'),
            before_native_inputs=bs['inputs'], after_native_inputs=ass['inputs']),
        pairing=dict(tracks=len(before['track_id']), identical_primary_keys=list(PRIMARY_KEYS),
                     bounds_formula='mean(L_after-U_before) <= true change <= mean(U_after-L_before)',
                     standard_errors='Paired endpoint sampling SE; positive/negative precision caps are independent strata. Conservative true-change SE upper bounds the variance using per-event allowed squared differences.'),
        postprocessing=source_state())
    write_csv(summary, output/'comparison.csv')
    write_markdown(summary, output/'comparison.md')
    draw_comparison(summary, output/'paired-change.png')
    summary['artifacts'] = {name: dict(sha256=sha(output/name), bytes=(output/name).stat().st_size)
                            for name in ('comparison.csv', 'comparison.md', 'paired-change.png')}
    save(output/'comparison.json', summary)
    print(json.dumps(dict(paired_tracks=len(before['track_id']), cases=len(cases), output=str(output)), indent=2))
    return summary


def write_csv(summary, path):
    keys = ('before_lower_fraction', 'before_upper_fraction', 'after_lower_fraction', 'after_upper_fraction',
            'change_lower_fraction', 'change_upper_fraction', 'change_lower_sampling_standard_error',
            'change_upper_sampling_standard_error', 'conservative_true_change_sampling_standard_error_upper',
            'definitely_gained_tracks', 'definitely_lost_tracks', 'definitely_gained_fraction', 'definitely_lost_fraction',
            'common_complete_tracks', 'common_complete_change_diagnostic')
    with Path(path).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=('momentum_GeV', 'charge', 'region', 'metric', 'tracks', *keys))
        writer.writeheader()
        for case in summary['cases']:
            for region, stats in case['samples'].items():
                for metric in METRICS:
                    writer.writerow(dict(momentum_GeV=case['momentum_GeV'], charge=case['charge'],
                        region=region, metric=metric, tracks=stats['tracks'], **{key: stats[metric][key] for key in keys}))


def write_markdown(summary, path):
    lines = ['# Paired wheel-layout coverage comparison', '', '**DRAFT / isolated ACTS vacuum PROTOTYPE.** '+SCOPE, '',
             'All momenta are total local entrance momentum. The endcap region is the fixed initial-direction '
             '|eta| cut; precision cap banks are not added to the full-sphere denominator. The cap-pair '
             'estimate combines independent positive and negative strata with their solid-angle weights.', '',
             'Table entries are **proven–possible availability [%]** and paired **change bounds [percentage points]**. '
             'They include all unfinished/native-navigation-uncertain events. These intervals are unresolved-event '
             'bounds, not statistical confidence intervals. Separate endpoint sampling errors, definitely gained/lost '
             'counts, positive/negative ends, per-wheel results and status contingencies are retained in JSON/CSV.', '']
    for region, metric, label in (
            ('full_sphere', 'outer_unique_faces', '4pi: at least six unique large faces, all chamber families'),
            ('full_sphere', 'active_paired_stations', '4pi: three paired logical stations, 30 mm border, all families'),
            ('endcap_caps', 'endcap_outer_unique_faces', 'Fixed endcap region: six endcap-only large faces'),
            ('endcap_caps', 'endcap_active_paired_stations', 'Fixed endcap region: three endcap-only paired stations, 30 mm border')):
        lines += ['## '+label, '', '| Local p [GeV] | q/e | N | Before [%] | After [%] | Paired change [pp] |',
                  '| ---: | ---: | ---: | ---: | ---: | ---: |']
        for case in summary['cases']:
            stats = case['samples'][region]; row = stats[metric]
            interval = lambda a, b: f'{100*row[a]:.2f}–{100*row[b]:.2f}'
            lines.append(f"| {case['momentum_GeV']:g} | {case['charge']:+d} | {stats['tracks']:,} | "
                         f"{interval('before_lower_fraction', 'before_upper_fraction')} | "
                         f"{interval('after_lower_fraction', 'after_upper_fraction')} | "
                         f"{interval('change_lower_fraction', 'change_upper_fraction')} |")
        lines.append('')
    lines += ['These native boundary crossings do not measure reconstruction efficiency. Field-stencil masks '
              'are never filled or extrapolated. A proven pass before a later abort remains proven. '
              'A rise in proven fractions does not by itself prove an improvement when paired change bounds contain zero.', '']
    Path(path).write_text('\n'.join(lines))


def draw_comparison(summary, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    metrics = [('outer_unique_faces', '#206ba7', 'Six large faces: outer'),
               ('active_unique_faces', '#b36c1c', 'Six large faces: 30 mm border'),
               ('outer_paired_stations', '#21855f', 'Three paired stations: outer'),
               ('active_paired_stations', '#915699', 'Three paired stations: 30 mm border')]
    fig, axes = plt.subplots(2, 2, figsize=(13.8, 10), sharex=True, sharey=True)
    fig.subplots_adjust(left=.09, right=.98, top=.82, bottom=.22, hspace=.28, wspace=.13)
    for row, (region, prefix, title) in enumerate((('full_sphere', '', 'Full 4pi: all chamber families'),
                ('endcap_caps', 'endcap_', 'Fixed endcap region: endcap-only'))):
        for col, charge in enumerate((-1, 1)):
            ax = axes[row, col]
            cases = [case for case in summary['cases'] if case['charge'] == charge]
            momenta = np.asarray([case['momentum_GeV'] for case in cases])
            for metric, color, _ in metrics:
                lo = np.asarray([case['samples'][region][prefix+metric]['change_lower_fraction'] for case in cases])*100
                hi = np.asarray([case['samples'][region][prefix+metric]['change_upper_fraction'] for case in cases])*100
                ax.fill_between(momenta, lo, hi, color=color, alpha=.12)
                ax.plot(momenta, lo, color=color, marker='o', ms=3)
                ax.plot(momenta, hi, color=color, ls='--', lw=1)
            ax.axhline(0, color='black', lw=.7); ax.grid(alpha=.2)
            ax.set(xscale='log', ylim=(-100, 100), title=f'{title}; q={charge:+d}e')
            ax.set_xticks(momenta, [f'{p:g}' for p in momenta]); ax.minorticks_off()
            if row == 1:
                ax.set_xlabel('Local entrance momentum [GeV]')
            if col == 0:
                ax.set_ylabel('Paired after − before bounds [pp]')
    handles = [Line2D([], [], color=color, lw=2, label=label) for _, color, label in metrics]
    handles += [Line2D([], [], color='#333333', lw=1.5, label='Solid: lower bound'),
                Line2D([], [], color='#333333', ls='--', label='Dashed: upper bound'),
                Patch(facecolor='#888888', alpha=.2, label='Unresolved-event range; not a confidence interval')]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5, .065), ncol=2, frameon=False)
    fig.suptitle('Paired change in native chamber-boundary availability\nDRAFT / isolated ACTS vacuum PROTOTYPE', y=.97, fontsize=16)
    fig.text(.5, .865, 'Same primary directions, launch, world and numerical settings; both chamber geometry and ECT field change.', ha='center', fontsize=10)
    fig.text(.5, .015, 'Every generated event remains in its denominator. Independent full-sphere and cap banks are shown separately.\n'
             'Sampling errors are separate in CSV/JSON. No material transport, detector response or reconstruction efficiency.', ha='center', fontsize=9)
    fig.savefig(path, dpi=180, facecolor='white'); plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', required=True, type=Path)
    parser.add_argument('--after', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    compare(args.before, args.after, args.output)
