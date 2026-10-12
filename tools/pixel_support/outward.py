#!/usr/bin/env python3
"""DES-002: exact barrel sections with candidate A on the outward module side.

Isolated PROTOTYPE. No module transforms, materials or production files changed.
"""
import argparse
import copy
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/module_layout'))
from geometry import _obb_overlap


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_layout(config):
    path = ROOT / config['baseline']
    if sha(path) != config['baseline_sha256']:
        raise ValueError('Baseline changed: review input provenance before drawing')
    return json.loads(gzip.decompress(path.read_bytes()))


def stave_span(column, config):
    """Passive endpoints may stay fixed when an approved active row set shrinks."""
    occupied = [min(b['center_mm'][2]-b['half_v_mm'] for b in column),
                max(b['center_mm'][2]+b['half_v_mm'] for b in column)]
    span = config.get('passive_stave_z_mm', {}).get(column[0]['layer_id'], occupied)
    if len(span) != 2 or not all(math.isfinite(x) for x in span) or span[0] > occupied[0]+1e-9 or span[1] < occupied[1]-1e-9:
        raise ValueError('Passive stave span must contain every occupied module body')
    return tuple(span)


def corners(box):
    return [tuple(box['center_mm'][j] + su*box['half_u_mm']*box['u'][j]
                  + sn*box['half_w_mm']*box['n'][j] for j in range(2))
            for su, sn in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]


def point_segment_distance(p, a, b):
    d = [b[i]-a[i] for i in range(2)]
    t = max(0., min(1., sum((p[i]-a[i])*d[i] for i in range(2)) /
                   sum(x*x for x in d)))
    return math.hypot(*(p[i]-a[i]-t*d[i] for i in range(2)))


def gap(a, b, tolerance):
    """Euclidean x-y gap, or zero for touching/overlapping extruded boxes."""
    if _obb_overlap(a, b, tolerance=tolerance):
        return 0.
    pa, pb = corners(a), corners(b)
    return min(point_segment_distance(p, q[i], q[(i+1) % 4])
               for points, q in [(pa, pb), (pb, pa)] for p in points for i in range(4))


def section(layout, config, settings):
    """Select actual modules at z; extrude the repeated column for x-y checks."""
    z = settings['section_z_mm']
    barrel = [b for b in layout['bodies']
              if b['subsystem'] == 'pixel' and b['region'] == 'barrel']
    # The repeating cross-section argument requires fixed transforms along z.
    for _, group in itertools.groupby(sorted(barrel, key=lambda b: (b['layer_id'], b['col'])),
                                     key=lambda b: (b['layer_id'], b['col'])):
        group = list(group)
        first = group[0]
        if any(b['tilt_degrees'] != 0 or b['z_stagger'] or
               b['center_mm'][:2] != first['center_mm'][:2] or
               any(b[k] != first[k] for k in ['u', 'v', 'n', 'half_u_mm', 'half_w_mm', 'family'])
               for b in group):
            raise ValueError('Section screen requires untilted z-uniform stave columns')
    selected = [b for b in barrel if abs(b['center_mm'][2]-z) < b['half_v_mm']]
    columns = {(b['layer_id'], b['col']) for b in barrel}
    if {(b['layer_id'], b['col']) for b in selected} != columns or len(selected) != len(columns):
        raise ValueError('Requested section must intersect exactly one module per stave')
    selected_ids = {b['module_id'] for b in selected}
    sensors = [m for m in layout['modules'] if m['module_id'] in selected_ids
               and abs(m['center_mm'][2]-z) < m['half_v_mm']]
    if {m['module_id'] for m in sensors} != selected_ids:
        raise ValueError('Requested section must intersect active silicon in every stave')
    bodies = copy.deepcopy(selected)
    parts, tubes = [], []
    stack = config['stack_mm']
    for b in bodies:
        # Equal arbitrary extrusion for an exclusively transverse intersection test.
        b['center_mm'][2] = 0.
        b['half_v_mm'] = 1.
        family = config['families'][b['family']]
        depth = 0.
        for kind in ['interface', 'insulation', 'graphite', 'top_skin', 'core', 'bottom_skin']:
            p = copy.deepcopy(b)
            p['kind'] = kind
            p['half_u_mm'] = family['spine_mm']/2 if kind in ['core', 'bottom_skin'] else b['half_u_mm']
            p['half_w_mm'] = stack[kind]/2
            p['center_mm'] = [c+(b['half_w_mm']+depth+p['half_w_mm'])*n
                              for c, n in zip(b['center_mm'], b['n'])]
            parts.append(p)
            if kind == 'core':
                for sign in [-1, 1]:
                    tubes.append(dict(module_id=b['module_id'], layer_id=b['layer_id'],
                                      center_mm=[p['center_mm'][j]+sign*family['tube_offset_mm']*b['u'][j]
                                                 for j in range(2)],
                                      outer_radius_mm=family['tube_OD_mm']/2,
                                      inner_radius_mm=family['tube_OD_mm']/2-family['tube_wall_mm'],
                                      flow_sign=sign))
            depth += stack[kind]
    return bodies, sensors, parts, tubes


def envelopes(bodies, config):
    """Two bounding rectangles per stave; internal layer contacts are intentional."""
    result = []
    plate = sum(config['stack_mm'][k] for k in ['interface', 'insulation', 'graphite', 'top_skin'])
    for b in bodies:
        for kind, width, start, depth in [
            ('plate', 2*b['half_u_mm'], 0., plate),
            ('spine', config['families'][b['family']]['spine_mm'], plate,
             config['stack_mm']['core']+config['stack_mm']['bottom_skin'])]:
            p = copy.deepcopy(b)
            p.update(kind=kind, half_u_mm=width/2, half_w_mm=depth/2)
            p['center_mm'] = [c+(b['half_w_mm']+start+depth/2)*n
                              for c, n in zip(b['center_mm'], b['n'])]
            result.append(p)
    return result


def screen(layout, config, settings, assembly):
    bodies, sensors, parts, tubes = assembly
    boxes = envelopes(bodies, config)
    tol = settings['overlap_tolerance_mm']
    bp = [(a, b, gap(a, b, tol)) for a in boxes for b in bodies if a['module_id'] != b['module_id']]
    pp = [(a, b, gap(a, b, tol)) for i, a in enumerate(boxes) for b in boxes[i+1:]
          if a['module_id'] != b['module_id']]
    def conflicts(pairs):
        return [dict(first=[a['layer_id'], a['col'], a.get('kind', 'module')],
                     second=[b['layer_id'], b['col'], b.get('kind', 'module')])
                for a, b, _ in pairs if _obb_overlap(a, b, tolerance=tol)]
    layers = []
    for layer in layout['layers']:
        lid = layer['id']
        bs = [b for b in bodies if b['layer_id'] == lid]
        if not bs:
            continue
        support = [p for p in boxes if p['layer_id'] == lid]
        radial_max = max(math.hypot(*p) for b in bs+support for p in corners(b))
        layers.append(dict(layer=lid, nominal_radius_mm=layer['r_m']*1000, staves=len(bs),
                           family=bs[0]['family'], tubes=2*len(bs),
                           active_patches_at_cut=sum(m['layer_id'] == lid for m in sensors),
                           assembly_r_max_mm=radial_max,
                           support_other_module_gap_mm=min(g for a, b, g in bp if a['layer_id'] == lid),
                           support_other_support_gap_mm=min(g for a, b, g in pp
                                                           if a['layer_id'] == lid or b['layer_id'] == lid)))
    trunk = next(r for r in layout['metadata']['services']['routes'] if r['id'] == 'pixel-trunk-P')
    return dict(status='PROTOTYPE nominal transverse clearance screen; no engineering approval',
                section_z_mm=settings['section_z_mm'], overlap_tolerance_mm=tol, layers=layers,
                staves=len(bodies), cooling_tubes=len(tubes),
                support_body_conflicts=conflicts(bp), support_support_conflicts=conflicts(pp),
                pixel_trunk=dict(inner_radius_mm=trunk['r_min_mm'], positive_z_start_mm=trunk['z_min_mm'],
                                 radial_headroom_mm=trunk['r_min_mm']-max(l['assembly_r_max_mm'] for l in layers),
                                 note='Projected radius only: trunk does not occupy this z cut; end joints untested'),
                limitations=['Exact module/sensitive transforms retained; unresolved internal module stack.',
                             'No assembly tolerances, shared rings/frame, flex, connectors or end joints in the screen.',
                             'Prior inward annular support reservation is not an outward envelope approval.',
                             'No new tracking, thermal, hydraulic or FEA results.'])


def draw(assembly, result, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Circle, Patch, Polygon
    plt.rcParams.update({'font.size': 10, 'svg.fonttype': 'none', 'pdf.fonttype': 42,
                         'svg.hashsalt': 'DES002-outward-A'})
    bodies, sensors, parts, tubes = assembly
    colors = dict(interface='#bc693e', insulation='#c9a629', graphite='#78919c',
                  top_skin='#303c49', core='#ead5a3', bottom_skin='#303c49')

    def paint(ax, layer_ids, module_ids=None, detail=False):
        def included(b):
            return b['layer_id'] in layer_ids and (module_ids is None or b['module_id'] in module_ids)
        for b in bodies:
            if included(b):
                ax.add_patch(Polygon(corners(b), facecolor='#dfebe3', edgecolor='#819a88', linewidth=.35))
        for p in parts:
            if included(p):
                ax.add_patch(Polygon(corners(p), facecolor=colors[p['kind']], edgecolor='none'))
        for t in tubes:
            if included(t):
                ax.add_patch(Circle(t['center_mm'], t['outer_radius_mm'], fc='#8399a5', ec='#38434d', lw=.35))
                ax.add_patch(Circle(t['center_mm'], t['inner_radius_mm'],
                                    fc='#267eb7' if t['flow_sign'] == -1 else '#ce6058', ec='none'))
        for m in sensors:
            if included(m):
                ends = [[m['center_mm'][j]+s*m['half_u_mm']*m['u'][j] for j in range(2)] for s in [-1, 1]]
                ax.plot([p[0] for p in ends], [p[1] for p in ends], c='#187943', lw=1.1 if detail else .8)
        ax.set_aspect('equal')
        ax.set_xlabel('x [mm]')
        ax.set_ylabel('y [mm]')
        ax.grid(alpha=.15, linewidth=.5)

    handles = [Line2D([], [], color='#187943', label='Active sensor plane (fixed)'),
               Patch(fc='#dfebe3', ec='#819a88', label='Module body envelope: 1 mm'),
               Patch(fc='#303c49', label='CFRP skins'), Patch(fc='#ead5a3', label='Conductive carbon foam'),
               Patch(fc='#78919c', label='Graphite + interface / insulation'),
               Patch(fc='#8399a5', ec='#38434d', label='Titanium tube wall'),
               Patch(fc='#267eb7', label='CO₂ circuit 1 (+z)'),
               Patch(fc='#ce6058', label='CO₂ circuit 2 (−z)'),
               Line2D([], [], color='#a1a8ac', ls=':', label='Nominal layer radius')]
    for layer in result['layers'] + [None]:
        chosen = [layer] if layer else result['layers']
        lids = {l['layer'] for l in chosen}
        tag = layer['layer'].split('-')[-1] if layer else 'all'
        fig = plt.figure(figsize=(13.2, 9.5), facecolor='white')
        ax = fig.add_axes([.07, .18, .59, .70])
        paint(ax, lids)
        limit = max(l['assembly_r_max_mm'] for l in chosen)*1.12
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.plot(0, 0, '+', color='#59616b', ms=9)
        ax.annotate('beam axis', (0, 0), (6, -14), textcoords='offset points', fontsize=9, color='#59616b')
        for l in chosen:
            ax.add_patch(Circle((0, 0), l['nominal_radius_mm'], fill=False, ls=':', lw=.65, ec='#a1a8ac', zorder=0))
        if layer is None or tag == 'B4':
            ax.add_patch(Circle((0, 0), result['pixel_trunk']['inner_radius_mm'], fill=False,
                                ls='--', lw=.8, ec='#b87631'))
        title = (f"{tag} | nominal r = {layer['nominal_radius_mm']:g} mm | {layer['staves']} staves" if layer
                 else f"All four barrels | {result['staves']} staves | {result['cooling_tubes']} cooling tubes")
        fig.suptitle('Candidate A — sensors inward, support outward\n'+title, fontsize=17, y=.97)
        fig.text(.075, .885, f"x–y section at z = +{result['section_z_mm']:g} mm · actual radial staggering · no local tilt", fontsize=10)
        fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(.69, .885), frameon=False, fontsize=9.5)
        detail_layer = layer or result['layers'][0]
        b = next(b for b in bodies if b['layer_id'] == detail_layer['layer'] and b['col'] == 0)
        detail = fig.add_axes([.73, .37, .23, .25])
        paint(detail, {b['layer_id']}, {b['module_id']}, detail=True)
        r = b['center_mm'][0]
        # Column zero has its radial axis along +x in the retained layout.
        detail.set_xlim(r-3, r+7)
        detail.set_ylim(-b['half_u_mm']-2, b['half_u_mm']+2)
        detail.set_title(f"{detail_layer['layer'].split('-')[-1]} stave detail (same x–y axes)", fontsize=9)
        detail.tick_params(labelsize=7)
        detail.xaxis.label.set_size(8)
        detail.yaxis.label.set_size(8)
        detail.annotate('', (r-2, 0), (r+6, 0), arrowprops=dict(arrowstyle='->', color='#575d65', lw=.8))
        fig.text(.715, .325, '← beam / sensor side     support / +r →', fontsize=9)
        if layer:
            text = (f"{layer['family'].capitalize()} modules; {layer['tubes']} cooling tubes\n"
                    f"Outer assembly radius: {layer['assembly_r_max_mm']:.2f} mm\n"
                    f"Closest support-to-other-module gap:\n{layer['support_other_module_gap_mm']:.3f} mm (nominal boxes)")
        else:
            text = '\n'.join(f"{l['layer'].split('-')[-1]}: r {l['nominal_radius_mm']:g} mm · {l['staves']} staves · {l['family']}" for l in chosen)
        fig.text(.715, .295, text, va='top', fontsize=9.5, linespacing=1.55)
        if layer is None or tag == 'B4':
            trunk = result['pixel_trunk']
            fig.text(.715, .175, f"Dashed orange: projected r = {trunk['inner_radius_mm']:g} mm\n"
                     f"service-trunk boundary (|z| ≥ {trunk['positive_z_start_mm']:g} mm).\n"
                     f"B4 radial headroom: {trunk['radial_headroom_mm']:.3f} mm; no joint allowance.", fontsize=8.5, va='top')
        fig.text(.075, .055, 'PROTOTYPE · Dimensions in mm, true aspect ratio; sensor line width is symbolic.\n'
                 'Module / active-plane positions unchanged; internal sensor–ASIC stack unresolved.\n'
                 'Section is between bearings: global frame, ribs, end joints and flex are not shown or qualified.', fontsize=9, color='#515964')
        for ext in ['png', 'pdf', 'svg']:
            metadata = {'Date': None} if ext == 'svg' else ({'CreationDate': None, 'ModDate': None} if ext == 'pdf' else {})
            target = output/f'barrel-{tag}.{ext}'
            fig.savefig(target, dpi=200, metadata=metadata)
            if ext == 'svg':
                # Matplotlib's path coordinates include trailing spaces.
                target.write_text('\n'.join(line.rstrip() for line in target.read_text().splitlines())+'\n')
        plt.close(fig)
    return matplotlib.__version__


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'docs/validation/DES-002/outward-A')
    args = parser.parse_args()
    config = json.loads(Path(__file__).with_name('inputs.json').read_text())
    settings = json.loads(Path(__file__).with_name('outward.json').read_text())
    layout = load_layout(config)
    assembly = section(layout, config, settings)
    result = screen(layout, config, settings, assembly)
    args.output.mkdir(parents=True, exist_ok=True)
    version = draw(assembly, result, args.output)
    producers = ['tools/pixel_support/outward.py', 'tools/pixel_support/outward.json',
                 'tools/pixel_support/inputs.json', 'tools/module_layout/geometry.py']
    result['provenance'] = dict(baseline=config['baseline'], baseline_sha256=config['baseline_sha256'],
                                producer_files_sha256={p: sha(ROOT/p) for p in producers},
                                starting_revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                                python=sys.version, matplotlib=version,
                                command='python3 -B '+' '.join(sys.argv), random_seed=None)
    (args.output/'screening.json').write_text(json.dumps(result, indent=2)+'\n')
    files = sorted(args.output.glob('barrel-*.*'))+[args.output/'screening.json']
    (args.output/'artifacts.json').write_text(json.dumps({
        'status': 'PROTOTYPE outward candidate A; separate from earlier inward evidence',
        'artifacts_sha256': {p.name: sha(p) for p in files},
        'producer_files_sha256': result['provenance']['producer_files_sha256']}, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'provenance'}, indent=2))
    if result['support_body_conflicts'] or result['support_support_conflicts']:
        raise SystemExit('Nominal support collision found; drawings retained for diagnosis')


if __name__ == '__main__':
    main()
