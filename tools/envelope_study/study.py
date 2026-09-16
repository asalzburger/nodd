#!/usr/bin/env python3
"""PROTOTYPE — unsigned DES-003 allocation drawing and straight-ray diagnostics.

No DD4hep geometry is generated. Envelopes are NOT sensitive layers or material.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shlex
import subprocess
import sys


def validate(data):
    if data.get('units') != 'm':
        raise ValueError('Envelope coordinates must be in metres')
    if data.get('reflection_symmetry') != 'z -> -z':
        raise ValueError('This study requires explicit z reflection symmetry')
    for eta in data['study']['eta_samples']:
        if type(eta) not in (int, float) or not math.isfinite(eta):
            raise ValueError('Eta samples must be finite numbers')
    for eta in data['study'].get('eta_guides', []):
        if type(eta) not in (int, float) or not math.isfinite(eta) or eta <= 0:
            raise ValueError('Figure eta guides must be finite and positive')
    seen = set()
    for region in data['regions']:
        if region['id'] in seen:
            raise ValueError('Duplicate region ID')
        seen.add(region['id'])
        for axis in ('r', 'z'):
            low, high = region[f'{axis}_min_m'], region[f'{axis}_max_m']
            if not all(type(v) in (int, float) and math.isfinite(v) for v in (low, high)):
                raise ValueError('Coordinates must be finite numbers')
            if not 0 <= low < high:
                raise ValueError('Require 0 <= minimum < maximum')
        if region.get('classification') != 'NODD DESIGN CHOICE' or not region.get('rationale'):
            raise ValueError('Each candidate allocation needs a design-choice rationale')
    return data


def ray_interval(region, eta):
    """Positive-z ray from origin; return path-length interval in m or None.

    Axisymmetric rectangles, no curvature, phi gaps, scattering or displaced origin.
    Negative eta is mirrored, using the declared z reflection symmetry.
    """
    eta = abs(eta)
    exp_neg = math.exp(-eta)
    dr, dz = 2 * exp_neg / (1 + exp_neg * exp_neg), math.tanh(eta)
    low, high = 0., float('inf')
    for axis, direction in (('r', dr), ('z', dz)):
        a, b = region[f'{axis}_min_m'], region[f'{axis}_max_m']
        if direction == 0:
            if not a <= 0 <= b:
                return None
        else:
            low, high = max(low, a / direction), min(high, b / direction)
    # Discard roundoff-only tangencies: a numerical ULP guard, not a physical tolerance.
    guard = 8 * max(math.ulp(low), math.ulp(high))
    return (low, high) if high - low > guard else None


def report(data):
    overlaps = []
    for i, a in enumerate(data['regions']):
        for b in data['regions'][i+1:]:
            dr = min(a['r_max_m'], b['r_max_m']) - max(a['r_min_m'], b['r_min_m'])
            dz = min(a['z_max_m'], b['z_max_m']) - max(a['z_min_m'], b['z_min_m'])
            if dr > 0 and dz > 0:
                overlaps.append({'regions': [a['id'], b['id']], 'radial_overlap_m': dr, 'axial_overlap_m': dz})
    rows = []
    for eta in data['study']['eta_samples']:
        crossings = []
        for region in data['regions']:
            interval = ray_interval(region, eta)
            if interval:
                crossings.append({'region': region['id'], 'entry_path_m': interval[0], 'exit_path_m': interval[1], 'path_m': interval[1]-interval[0]})
        rows.append({'eta': eta, 'envelope_crossings': sorted(crossings, key=lambda a: a['entry_path_m'])})
    return {'proposal': data['proposal'], 'status': 'DRAFT planning diagnostic',
            'limitations': ['Axisymmetric allocation rectangles, not constructed detector volumes.',
                           'Envelope crossings are NOT layer counts, hits, efficiencies or proof of hermeticity.',
                           'No material assigned: path length is NOT radiation or interaction length.',
                           'Tangencies shorter than eight floating-point ULPs are discarded; this is not a physical clearance tolerance.',
                           'Origin is fixed at r=z=0; no curvature, phi cracks, dead areas or response.'],
            'rectangle_overlaps': overlaps, 'rays': rows}


def draw(data, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Patch
    plt.rcParams.update({'svg.hashsalt': 'nodd-des-003', 'font.size': 9})
    fig, axes = plt.subplots(1, 2, figsize=(15, 7), gridspec_kw={'width_ratios': [2.2, 1]})
    handles = []
    for region in data['regions']:
        color = region['color']
        for ax in axes:
            for sign in (-1, 1):
                z0 = region['z_min_m'] if sign > 0 else -region['z_max_m']
                ax.add_patch(Rectangle((z0, region['r_min_m']), region['z_max_m']-region['z_min_m'],
                                      region['r_max_m']-region['r_min_m'], facecolor=color,
                                      edgecolor=color, alpha=.55, linewidth=.7,
                                      hatch='///' if region.get('reservation') else None))
        handles.append(Patch(facecolor=color, alpha=.55, label=region['label'],
                             hatch='///' if region.get('reservation') else None))
    extent = data['study']['plot_extent_m']
    axes[0].set(xlim=(-extent['z'], extent['z']), ylim=(0, extent['r']), title='Global allocations (both endcaps)')
    zoom = data['study']['plot_zoom_m']
    axes[1].set(xlim=(0, zoom['z']), ylim=(0, zoom['r']), title='Positive-z inner detector / calorimeters')
    for ax in axes:
        ax.set(xlabel='z [m]', ylabel='r [m]')
        ax.set_aspect('equal', adjustable='box')
        ax.grid(alpha=.2)
        for eta in data['study']['eta_guides']:
            # Stable reciprocal sinh also handles very large positive guides.
            e = math.exp(-eta)
            slope = 2 * e / -math.expm1(-2 * eta)
            z = ax.get_xlim()[1] if slope == 0 else min(ax.get_xlim()[1], ax.get_ylim()[1]/slope)
            r = z*slope
            ax.plot([0,z],[0,r], color='#444444', ls=':', lw=.7)
            if ax is axes[0]:
                ax.plot([0,-z],[0,r], color='#444444', ls=':', lw=.7)
            if ax is axes[1]:
                ax.annotate(f'η={eta:g}', (z,r), fontsize=7, xytext=(-30,3), textcoords='offset points')
    fig.suptitle(data['figure_title'], fontsize=15)
    fig.legend(handles=handles, loc='lower center', ncol=4, bbox_to_anchor=(.5,.075), fontsize=8)
    fig.text(.5,.025, 'DRAFT • symmetric planning allocations, not sensitive geometry • gaps are unallocated space, not validated services\n'
             'Straight rays start at the origin; no field curvature or φ structure. All dimensions require review.', ha='center', fontsize=9)
    fig.subplots_adjust(top=.87, bottom=.25, wspace=.28)
    output.mkdir(parents=True, exist_ok=True)
    fig.savefig(output/'DES-003-envelope-rz.svg', metadata={'Date': None}, bbox_inches='tight')
    svg = output/'DES-003-envelope-rz.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
    fig.savefig(output/'DES-003-envelope-rz.png', dpi=180, bbox_inches='tight')
    plt.close(fig)
    return matplotlib.__version__


def project_provenance():
    """Record source checkout identity; hashes identify uncommitted tool/input bytes."""
    root = Path(__file__).resolve().parents[2]
    try:
        revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
        status = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=normal'], cwd=root, text=True)
        return {'project_revision': revision, 'project_worktree_dirty': bool(status.strip())}
    except (OSError, subprocess.CalledProcessError):
        return {'project_revision': None, 'project_worktree_dirty': None,
                'project_provenance_note': 'Git checkout identity unavailable'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--figures', type=Path)
    args = parser.parse_args()
    data = validate(json.loads(args.input.read_text()))
    result = report(data)
    result['provenance'] = {'input': str(args.input), 'input_sha256': hashlib.sha256(args.input.read_bytes()).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'python': sys.version.split()[0],
        'source_revision': data['source_revision'], 'random_seed': 'not applicable; deterministic analytic rays',
        'command': shlex.join([os.path.relpath(sys.executable), *sys.argv]),
        'acceptance_tolerances': 'none selected; descriptive planning diagnostics only',
        **project_provenance()}
    if args.figures:
        result['provenance']['matplotlib'] = draw(data, args.figures)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2)+'\n')
    print(f'{len(data["regions"])} allocations, {len(result["rays"])} sampled rays, {len(result["rectangle_overlaps"])} rectangle intersections; no physical acceptance claimed.')

if __name__ == '__main__':
    main()
