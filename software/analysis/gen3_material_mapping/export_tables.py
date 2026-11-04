#!/usr/bin/env python3
"""Export the complete surface/remote-region tables from retained survey JSON."""
import argparse
import csv
import io
import json
from pathlib import Path


def csv_text(fields, rows):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def tables(survey, geometry):
    by_id = {p['surface_id']: p for p in geometry['portals']}
    fields = ['surface_id', 'geometry_id', 'type', 'r1_mm', 'z1_mm', 'r2_mm',
              'z2_mm', 'candidate_steps', 'near_selected_steps', 'candidate_mean_X0',
              'near_mean_X0', 'after_steps', 'before_steps', 'selected_far_steps']
    rows = []
    for item in sorted(survey['assignments'], key=lambda a: -a['near_selected_sum_X0']):
        p = by_id[item['surface_id']]
        (r1, z1), (r2, z2) = p['rz_segment_mm']
        rows.append(dict(surface_id=p['surface_id'], geometry_id=p['geometry_id'],
                         type=p['type'], r1_mm=r1, z1_mm=z1, r2_mm=r2, z2_mm=z2,
                         candidate_steps=item['steps'],
                         near_selected_steps=item['near_selected_steps'],
                         candidate_mean_X0=item['sum_X0']/survey['tracks'],
                         near_mean_X0=item['near_selected_sum_X0']/survey['tracks'],
                         after_steps=item['after_steps'], before_steps=item['before_steps'],
                         selected_far_steps=item['selected_far_steps']))
    remote_fields = ['region_id', 'path', 'steps', 'flagged_steps', 'sum_X0',
                     'remote_sum_X0', 'weighted_r_mm', 'weighted_z_mm', 'r_rms_mm',
                     'z_rms_mm', 'suggested_new_surface', 'within_near_of_fit_fraction_X0']
    remote_rows = [{k: r[k] for k in remote_fields} for r in survey['remote_regions']]
    return {'proposed-surfaces.csv': csv_text(fields, rows),
            'remote-regions.csv': csv_text(remote_fields, remote_rows)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--output', type=Path)
    ap.add_argument('--check', action='store_true', help='Require exact equality with retained CSVs')
    args = ap.parse_args()
    result = tables(json.loads((args.data/'survey.json').read_text()),
                    json.loads((args.data/'geometry-summary.json').read_text()))
    if args.check:
        for name, text in result.items():
            if (args.data/name).read_text() != text:
                raise RuntimeError(f'Retained table differs: {name}')
        print('PASS: both complete CSV tables reproduce exactly from retained JSON')
    else:
        if args.output is None:
            ap.error('--output is required without --check')
        args.output.mkdir(parents=True, exist_ok=True)
        for name, text in result.items():
            (args.output/name).write_text(text)
        print('Exported complete candidate and remote-region tables')


if __name__ == '__main__':
    main()
