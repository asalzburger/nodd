"""Source-faithful 2D shape inventories; no detector geometry is changed."""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import numpy as np

BLUE = (0., .375, .996094)  # Same diffuse colour as the retained blue ACTS MTL.
GROUP_GRID_M = 1e-9


def dimensions(panel):
    vertices = np.asarray(panel['vertices_m'], float)
    depth = float(panel['depth_m'])
    if panel['kind'] == 'barrel':
        return dict(tangential_width_m=float(np.ptp(vertices[:, 0])),
                    longitudinal_length_m=float(np.ptp(vertices[:, 1])), depth_m=depth)
    radial = vertices[:, 0]
    low, high = radial.min(), radial.max()
    inner = vertices[abs(radial-low) < 1e-12, 1]
    outer = vertices[abs(radial-high) < 1e-12, 1]
    if len(inner) != 2 or len(outer) != 2:
        raise ValueError('expected two parallel radial bases: '+panel['id'])
    return dict(radial_span_m=float(high-low), inner_base_m=float(np.ptp(inner)),
                outer_base_m=float(np.ptp(outer)),
                outer_base_offset_m=float(outer.mean()-inner.mean()), depth_m=depth)


def inventory(geometry, kind):
    families = {}
    panels = []
    for panel in geometry['panels']:
        if panel['kind'] != kind:
            continue
        actual = dimensions(panel)
        key = tuple(int(round(v/GROUP_GRID_M)) for v in actual.values())
        ident = ('B-' if kind == 'barrel' else 'E-')+hashlib.sha256(json.dumps(key).encode()).hexdigest()[:8].upper()
        if ident not in families:
            families[ident] = dict(shape_id=ident, dimension_grid_key=list(key),
                                  dimensions_m={k: v*GROUP_GRID_M for k, v in zip(actual, key)},
                                  panel_ids=[], station_counts=Counter(), side_counts=Counter())
        family = families[ident]
        assert family['dimension_grid_key'] == list(key)
        family['panel_ids'].append(panel['id'])
        family['station_counts'][str(panel['station'])] += 1
        if kind == 'endcap':
            family['side_counts']['plus' if panel['side'] > 0 else 'minus'] += 1
        panels.append(dict(panel_id=panel['id'], shape_id=ident, station=panel['station'],
                           side=panel.get('side'), actual_dimensions_m=actual))
    ordered = sorted(families.values(), key=lambda f: tuple(f['dimension_grid_key']))
    for family in ordered:
        family['quantity'] = len(family['panel_ids'])
    return dict(kind=kind, total_panels=len(panels), shape_families=len(ordered),
                shape_group_dimension_grid_m=GROUP_GRID_M,
                scope='Envelope footprint/depth in source local axes; display families, not manufacturing tolerances.',
                families=ordered, panels=panels)


def draw(report, path, label, common_limits=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon
    families = report['families']
    columns = min(4, len(families))
    rows = math.ceil(len(families)/columns)
    widths, heights = [], []
    polygons = []
    for family in families:
        d = family['dimensions_m']
        if report['kind'] == 'barrel':
            w, h = d['tangential_width_m'], d['longitudinal_length_m']
            polygon = [[-w/2, 0], [w/2, 0], [w/2, h], [-w/2, h]]
        else:
            h, a, b, offset = (d[k] for k in ('radial_span_m', 'inner_base_m', 'outer_base_m', 'outer_base_offset_m'))
            polygon = [[-a/2, 0], [a/2, 0], [offset+b/2, h], [offset-b/2, h]]
            w = 2*max(abs(np.asarray(polygon)[:, 0]))
        polygons.append(polygon)
        widths.append(w)
        heights.append(h)
    width, height = common_limits or (max(widths), max(heights))
    fig, axes = plt.subplots(rows, columns, figsize=(3.5*columns, 3.6*rows), squeeze=False)
    for ax, family, polygon in zip(axes.ravel(), families, polygons):
        d = family['dimensions_m']
        ax.add_patch(Polygon(polygon, facecolor=BLUE, edgecolor='none'))
        ax.set(xlim=(-.6*width, .6*width), ylim=(-.06*height, 1.10*height))
        ax.set_aspect('equal', adjustable='box')
        ax.grid(alpha=.15)
        ax.set_axisbelow(True)
        stations = ', '.join(f'{k}:{v}' for k, v in sorted(family['station_counts'].items()))
        ax.set_title(f"{family['shape_id']} · n={family['quantity']}\nStation quantities {stations}", fontsize=9)
        if report['kind'] == 'barrel':
            text = f"width {d['tangential_width_m']:.6f} m\nlength {d['longitudinal_length_m']:.6f} m"
            ax.set_xlabel('tangential [m]', fontsize=8)
            ax.set_ylabel('longitudinal [m]', fontsize=8)
        else:
            text = f"inner/outer bases {d['inner_base_m']:.6f}/{d['outer_base_m']:.6f} m\nradial span {d['radial_span_m']:.6f} m"
            ax.set_xlabel('tangential [m]', fontsize=8)
            ax.set_ylabel('radial span [m]', fontsize=8)
        ax.text(.5, -.29, text+f" · depth {d['depth_m']:.3f} m", transform=ax.transAxes,
                ha='center', va='top', fontsize=8)
        ax.tick_params(labelsize=8)
    for ax in axes.ravel()[len(families):]:
        ax.axis('off')
    fig.suptitle(f"{label} · {report['kind']} chamber shapes\n"
                 f"{report['total_panels']} envelopes · {len(families)} dimension families · PROTOTYPE", fontsize=14)
    fig.subplots_adjust(top=1-1.3/(3.6*rows), bottom=max(.10, 1.15/(3.6*rows)),
                        hspace=.95, wspace=.55)
    fig.savefig(path, dpi=160, facecolor='white')
    plt.close(fig)
    return dict(shared_plot_limits_m=[width, height], colour_rgb=list(BLUE),
                dimensions='Source local axes; translations removed, all panels on one metric scale.')


def write(geometry_path, output, kind, label, prefix=None, common_limits=None):
    geometry = json.loads(Path(geometry_path).read_text())
    report = inventory(geometry, kind)
    report['source_geometry_sha256'] = hashlib.sha256(Path(geometry_path).read_bytes()).hexdigest()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    stem = prefix or kind
    report['figure'] = draw(report, output/(stem+'.png'), label, common_limits)
    (output/(stem+'.json')).write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    fields = ['shape_id', 'quantity', *report['families'][0]['dimensions_m'], 'station_counts', 'side_counts']
    with (output/(stem+'.csv')).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        for family in report['families']:
            writer.writerow(dict(shape_id=family['shape_id'], quantity=family['quantity'],
                                 **family['dimensions_m'], station_counts=json.dumps(family['station_counts'], sort_keys=True),
                                 side_counts=json.dumps(family['side_counts'], sort_keys=True)))
    names = list(report['families'][0]['dimensions_m'])
    headings = ['Shape', 'Quantity', 'Station: quantity', *[n.removesuffix('_m').replace('_', ' ')+' [m]' for n in names]]
    rows = ['| '+' | '.join(headings)+' |', '| '+' | '.join(['---']*len(headings))+' |']
    for family in report['families']:
        stations = ', '.join(f'{k}: {v}' for k, v in sorted(family['station_counts'].items()))
        rows.append('| '+' | '.join([family['shape_id'], str(family['quantity']), stations,
                                    *[f'{family["dimensions_m"][n]:.9f}' for n in names]])+' |')
    (output/(stem+'.md')).write_text(
        f'# {label}: {kind} chamber inventory\n\n'
        f'{report["total_panels"]} chamber envelopes, {report["shape_families"]} dimension families. '
        'Isolated PROTOTYPE; no chamber internals or manufacturing specification.\n\n'
        f'![Blue chamber shape inventory]({stem}.png)\n\n'
        f'[CSV]({stem}.csv) · [Full panel-to-shape mapping and source hash]({stem}.json). '
        'Dimensions group on a 1 nm grid; the JSON retains every source panel’s unrounded dimensions. '
        'Endcap quantities include both hemispheres. Shape plots share a metric scale within this sheet.\n\n'
        +'\n'.join(rows)+'\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--kind', choices=['barrel', 'endcap', 'both'], default='both')
    parser.add_argument('--label', default='Current PR90')
    args = parser.parse_args()
    for kind in (['barrel', 'endcap'] if args.kind == 'both' else [args.kind]):
        report = write(args.geometry, args.output, kind, args.label)
        print(f"{kind}: {report['total_panels']} panels, {report['shape_families']} shape families")


if __name__ == '__main__':
    main()
