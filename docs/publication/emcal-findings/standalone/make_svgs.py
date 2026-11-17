#!/usr/bin/env python3
"""Two standalone nODD SVGs; the accepted report and its inputs stay frozen."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
REPORT = HERE.parent
ROOT = Path(__file__).resolve().parents[4]
SOURCE = 'd04614575e8fc3aed41ed79798def3fc461e3dc6'
KEYS = ('siw_original', 'siw_staggered', 'lar400')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def frozen_report():
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', SOURCE,
                                    '--', 'docs/publication/emcal-findings'], cwd=ROOT, text=True).splitlines()
    hashes = {}
    for path in paths:
        expected = subprocess.check_output(['git', 'show', SOURCE + ':' + path], cwd=ROOT)
        actual = (ROOT / path).read_bytes()
        if actual != expected:
            raise ValueError('Existing report file changed: ' + path)
        hashes[path] = sha(actual)
    return hashes


def original_module():
    spec = importlib.util.spec_from_file_location('frozen_response_comparison', REPORT / 'response_comparison.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def derive(args):
    import numpy as np
    hashes = frozen_report()
    original = original_module()
    primary = None
    responses = {}
    sources = {}
    for name, (digest, field) in original.LEDGERS.items():
        raw = getattr(args, name).read_bytes()
        if sha(raw) != digest:
            raise ValueError('Unexpected retained ledger: ' + name)
        rows = sorted((json.loads(line) for line in raw.splitlines()), key=lambda r: r['event'])
        if [r['event'] for r in rows] != list(range(10000)):
            raise ValueError('Incomplete or duplicated primary identities')
        coords = np.array([[r[k] for k in ('energy_GeV', 'eta', 'phi')] for r in rows])
        signal = np.array([r[field] for r in rows])
        if (not np.all(np.isfinite(coords)) or not np.all(np.isfinite(signal))
                or np.any(coords[:, 0] <= 0) or np.any(signal < 0)):
            raise ValueError('Invalid primary or saved-hit response')
        if primary is not None and not np.array_equal(primary, coords):
            raise ValueError('Unmatched primary coordinates')
        primary = coords
        responses[name] = signal / coords[:, 0]
        sources[name] = {'ledger_sha256': digest, 'signal_field': field}

    eta = np.abs(primary[:, 1])
    if np.any(eta > 3):
        raise ValueError('Primary outside the declared eta range')
    band = np.minimum(np.searchsorted([0., 1., 2., 3.], eta, side='right') - 1, 2)
    hist_edges = np.arange(121) / 40
    panels = []
    for i in range(3):
        take = band == i
        n = int(np.count_nonzero(take))
        models = {}
        for key, values in responses.items():
            r = values[take]
            mean = float(np.mean(r)); sd = float(np.std(r, ddof=1))
            z = r / mean
            counts = np.histogram(z, hist_edges)[0]
            under = int(np.count_nonzero(z < 0)); over = int(np.count_nonzero(z > 3))
            if int(counts.sum()) + under + over != n:
                raise ValueError('Histogram lost events')
            np.testing.assert_allclose(np.std(z, ddof=1) / np.mean(z), sd / mean, rtol=2e-14, atol=0)
            models[key] = {'label': original.LABELS[key], 'events': n,
                           'zero_events': int(np.count_nonzero(r == 0)),
                           'mean_R': mean, 'sample_SD_R': sd, 'SD_over_mean': sd / mean,
                           'counts': counts.tolist(), 'underflow': under, 'overflow': over}
        panels.append({'eta_range': [i, i + 1], 'right_endpoint_included': i == 2,
                       'events_per_model': n, 'models': models})
    if sum(p['events_per_model'] for p in panels) != 10000:
        raise ValueError('Broad eta bands do not partition all primaries')

    curve = json.loads((REPORT / 'response-comparison.json').read_text())
    fine = np.minimum(np.searchsorted(curve['edges'], eta, side='right') - 1, 59)
    for key, values in responses.items():
        for i, expected in enumerate(curve['models'][key]['bins']):
            r = values[fine == i]
            if len(r) != expected['events'] or int(np.count_nonzero(r == 0)) != expected['zero_events']:
                raise ValueError('Fine-bin source populations changed')
            actual = [np.mean(r), np.std(r, ddof=1), np.std(r, ddof=1) / np.mean(r)]
            np.testing.assert_allclose(actual, [expected[k] for k in ('mean_response', 'sample_sd', 'fractional_width')], rtol=2e-14, atol=0)
        if sum(p['models'][key]['zero_events'] for p in panels) != sum(b['zero_events'] for b in curve['models'][key]['bins']):
            raise ValueError('Zeros were lost between views')
    result = {'schema_version': 1, 'source_revision': SOURCE,
              'observable': 'R=H/Etrue; unbinned sample SD(R)/mean(R)',
              'curve_data_sha256': sha((REPORT / 'response-comparison.json').read_bytes()),
              'source_ledgers': sources, 'matched_primary_events': 10000,
              'primary_coordinates_exact': True, 'eta_edges': [0, 1, 2, 3],
              'histogram_edges': hist_edges.tolist(),
              'histogram_coordinate': 'R / mean(R) of this model and broad eta band',
              'histogram_normalization': 'counts / all events in the band; overflow is not renormalized away',
              'moments': 'computed from all unbinned R values, including zeros and overflow',
              'panels': panels, 'report_files_unchanged': hashes,
              'checks': {'all_180_fine_bin_statistics_reproduced': True,
                         'all_events_and_zeros_retained': True, 'unit_mean_scaling_preserves_CV': True},
              'limits': ['Broad eta-band histograms provide context; their pooled widths are not the 0.05-bin curve points.',
                         'Log-y omits empty histogram bins; zero-valued responses are retained in the first bin.',
                         'No ODD, calibration, new bootstrap, transport or report modification.'],
              'producer_sha256': sha(Path(__file__).read_bytes()), 'numpy_version': np.__version__}
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'bands': [p['events_per_model'] for p in panels],
                      'zeros': {key: sum(p['models'][key]['zero_events'] for p in panels) for key in KEYS},
                      'fine_bin_crosscheck': 'PASS', 'report_files_unchanged': len(hashes)}))


def width_drawing(data):
    """Keep the accepted three nODD curve primitives exactly, remove ODD only."""
    from reportlab.graphics.shapes import Circle, Line, String, PolyLine, Group
    drawing = original_module().drawing(data)
    points = [tuple(node.points) for node in drawing.contents if isinstance(node, PolyLine)]
    removed = {'circles': 0, 'errorbars': 0, 'label': 0}
    kept = []
    legends = {}
    for node in drawing.contents:
        if isinstance(node, Circle): removed['circles'] += 1; continue
        if isinstance(node, Line) and node.strokeWidth == 1.8: removed['errorbars'] += 1; continue
        if isinstance(node, String) and node.text.startswith('ODD:'): removed['label'] += 1; continue
        if isinstance(node, String) and '. ODD:' in node.text:
            node.text = node.text.split('. ODD:', 1)[0] + '.'
        if isinstance(node, String) and node.text == 'EM calorimeter response comparison':
            node.text = 'nODD EM calorimeter response comparison'
        x0, y0, x1, y1 = node.getBounds()
        if 350 <= (y0 + y1) / 2 <= 395:
            slot = (int((x0 + x1) / 2 >= 500), int((y0 + y1) / 2 >= 370))
            legends.setdefault(slot, []).append(node)
        else:
            kept.append(node)
    if removed != {'circles': 4, 'errorbars': 3, 'label': 1} or set(legends) != {(1, 1), (0, 0), (1, 0)}:
        raise ValueError('Unexpected frozen drawing structure; do not silently remove data')
    for slot, delta in [((1, 1), (-475, 0)), ((0, 0), (475, 23)), ((1, 0), (-475, 0))]:
        group = Group(*legends[slot]); group.translate(*delta); kept.append(group)
    drawing.contents = kept
    if [tuple(node.points) for node in drawing.contents if isinstance(node, PolyLine)] != points:
        raise ValueError('nODD curve coordinates changed')
    return drawing


def reference_drawing(data):
    from reportlab.graphics.shapes import Drawing, String, Line, PolyLine, Group, Rect, Polygon
    from reportlab.lib.colors import HexColor
    d = Drawing(1000, 560)
    ink = HexColor('#172b3a'); grid = HexColor('#d8dfe3'); gold = HexColor('#cccc00')
    styles = {'siw_original': [7, 4], 'siw_staggered': [1.5, 3], 'lar400': []}
    def text(x, y, value, size=12, **kwargs):
        d.add(String(x, y, value, fontName='CaloPlot', fontSize=size, fillColor=ink, **kwargs))
    def marker(key, x, y):
        props = dict(fillColor=gold, strokeColor=ink, strokeWidth=.65)
        if key == 'siw_original': d.add(Rect(x - 2.8, y - 2.8, 5.6, 5.6, **props))
        elif key == 'siw_staggered': d.add(Polygon([x, y + 3.8, x - 3.5, y - 2.8, x + 3.5, y - 2.8], **props))
        else: d.add(Polygon([x, y + 3.1, x - 3.1, y, x, y - 3.1, x + 3.1, y], **props))
    text(76, 537, 'Response distributions behind the nODD width curves', 22)
    text(76, 516, 'Same matched saved-hit events; unit-mean scaling within each model and broad eta band', 13)
    for i, key in enumerate(KEYS):
        x = 76 + 312 * i
        d.add(Line(x, 490, x + 25, 490, strokeColor=gold, strokeWidth=2, strokeDashArray=styles[key]))
        marker(key, x + 12, 490)
        text(x + 33, 486, data['panels'][0]['models'][key]['label'], 13)
    edges = data['histogram_edges']
    short = {'siw_original': 'Si-W', 'siw_staggered': 'Si-W stag.', 'lar400': 'LAr400'}
    for i, panel in enumerate(data['panels']):
        left, bottom, w, h = 76 + i * 312, 184, 270, 236
        X = lambda x: left + x / 3 * w
        Y = lambda percent: bottom + (math.log10(percent) + 2) / 4 * h
        text(left + w / 2, 457, '|eta|: [' + str(i) + ',' + str(i + 1) + (']' if i == 2 else ')'), 16, textAnchor='middle')
        text(left + w / 2, 439, f"{panel['events_per_model']} events per model", 12, textAnchor='middle')
        for value in (.01, .1, 1, 10, 100):
            d.add(Line(left, Y(value), left + w, Y(value), strokeColor=grid, strokeWidth=.6))
            if i == 0: text(left - 9, Y(value) - 4, f'{value:g}', 11, textAnchor='end')
        d.add(Line(left, bottom, left, bottom + h, strokeColor=ink))
        d.add(Line(left, bottom, left + w, bottom, strokeColor=ink))
        d.add(Line(X(1), bottom, X(1), bottom + h, strokeColor=grid, strokeDashArray=[2, 3]))
        for value in range(4): text(X(value), bottom - 18, str(value), 12, textAnchor='middle')
        for j, key in enumerate(KEYS):
            model = panel['models'][key]
            percentages = [100 * n / model['events'] for n in model['counts']]
            segment = []
            for k, value in enumerate(percentages):
                if value == 0:
                    if segment: d.add(PolyLine(segment, strokeColor=gold, strokeWidth=1.8, strokeDashArray=styles[key])); segment = []
                    continue
                segment.extend([X(edges[k]), Y(value), X(edges[k + 1]), Y(value)])
            if segment: d.add(PolyLine(segment, strokeColor=gold, strokeWidth=1.8, strokeDashArray=styles[key]))
            for k in range(0, len(percentages), 8):
                if percentages[k] > 0: marker(key, X((edges[k] + edges[k + 1]) / 2), Y(percentages[k]))
            y = 117 - j * 29
            marker(key, left + 3, y + 3)
            text(left + 13, y, f"{short[key]}: mean R={model['mean_R']:.4g}; SD={model['sample_SD_R']:.4g}", 9.8)
            text(left + 13, y - 12, f"SD/mean={100 * model['SD_over_mean']:.2f}%; zeros={model['zero_events']}; >3={model['overflow']}", 9.8)
    ylabel = Group(String(0, 0, 'Events per bin [%] (log)', fontName='CaloPlot', fontSize=13, fillColor=ink, textAnchor='middle'))
    ylabel.translate(20, 302); ylabel.rotate(90); d.add(ylabel)
    text(523, 143, 'R / mean(R) within the shown broad eta band', 14, textAnchor='middle')
    text(76, 22, 'Reference panels pool broad eta bands; the width curves use 0.05-wide bins. Moments use all unbinned R, including tails.', 11)
    text(76, 7, 'Equal response bins of width 0.025; percentages use all band events. Empty bins are omitted on log-y; >3 counts are explicit.', 11)
    return d


def render(args):
    from reportlab.graphics import renderSVG, renderPDF
    import reportlab
    hashes = frozen_report()
    data = json.loads(args.data.read_text())
    curve = json.loads((REPORT / 'response-comparison.json').read_text())
    if data['curve_data_sha256'] != sha((REPORT / 'response-comparison.json').read_bytes()):
        raise ValueError('Wrong accepted width data')
    drawings = [('nodd-width.svg', width_drawing(curve)),
                ('nodd-response-distributions.svg', reference_drawing(data))]
    outputs = {}
    for name, drawing in drawings:
        path = HERE / name
        renderSVG.drawToFile(drawing, str(path))
        outputs[name] = {'sha256': sha(path.read_bytes()), 'width': drawing.width, 'height': drawing.height}
        if args.preview:
            args.preview.mkdir(parents=True, exist_ok=True)
            renderPDF.drawToFile(drawing, str(args.preview / (path.stem + '.pdf')))
    if outputs['nodd-width.svg']['width'] != outputs['nodd-response-distributions.svg']['width']:
        raise ValueError('SVG widths differ')
    if frozen_report() != hashes:
        raise ValueError('Existing report changed during rendering')
    (HERE / 'render.json').write_text(json.dumps({'source_revision': SOURCE, 'producer_sha256': sha(Path(__file__).read_bytes()),
        'data_sha256': sha(args.data.read_bytes()), 'report_files_unchanged': hashes,
        'nodd_curve_coordinates_unchanged': True, 'outputs': outputs, 'reportlab_version': reportlab.Version}, indent=2) + '\n')
    print(json.dumps(outputs))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest='command', required=True)
    a = sub.add_parser('derive')
    for key in KEYS: a.add_argument('--' + key.replace('_', '-'), type=Path, required=True)
    a.add_argument('--output', type=Path, default=HERE / 'reference-data.json')
    a = sub.add_parser('render'); a.add_argument('--data', type=Path, default=HERE / 'reference-data.json')
    a.add_argument('--preview', type=Path)
    args = p.parse_args(); (derive if args.command == 'derive' else render)(args)
