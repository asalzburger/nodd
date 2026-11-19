#!/usr/bin/env python3
"""Source-bound fine-eta rebinning and a single four-series vector comparison.

NumPy is needed only for derive; ReportLab only for render/PDF embedding.
No transport, calibration or per-event payload is written to public outputs.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASE = '79a967aa3fe78a525f15ede780c26be0cd73aeae'
COMMENT = 'https://github.com/asalzburger/nodd/pull/145#issuecomment-6951330371'
LEDGERS = {
    'siw_original': ('3ecf01973de2df1daae144d5179d2c465567af5f436168c2f785b77b892f0574', 'signal_GeV'),
    'siw_staggered': ('4fac66babe25d8a5e08821610b5122fd6219c6dce634f7b0db92034f93ba6907', 'signal_GeV'),
    'lar400': ('a591c521afffde7fe75ae8d2e6651918cde4e9dbaea0971d8a84646b5b12e74d', 'H_GeV'),
}
LABELS = {'siw_original': 'nODD Si-W', 'siw_staggered': 'nODD Si-W (staggered)', 'lar400': 'nODD LAr (400 mm)'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def frozen(path):
    return subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT)


def derive(args):
    import numpy as np
    sys.path.insert(0, str(ROOT))
    from software.analysis.lar_response.compare import binned_moments, index

    primary = None
    responses = {}
    sources = {}
    for name, (expected, field) in LEDGERS.items():
        raw = getattr(args, name).read_bytes()
        if sha(raw) != expected:
            raise ValueError('Unexpected retained ledger: ' + name)
        rows = sorted((json.loads(line) for line in raw.splitlines()), key=lambda r: r['event'])
        if [r['event'] for r in rows] != list(range(10000)):
            raise ValueError('Incomplete or duplicate primary identities')
        coords = np.array([[r[k] for k in ('energy_GeV', 'eta', 'phi')] for r in rows])
        signal = np.array([r[field] for r in rows])
        if not np.all(np.isfinite(coords)) or not np.all(np.isfinite(signal)) or np.any(signal < 0) or np.any(coords[:, 0] <= 0):
            raise ValueError('Invalid primary or saved-hit energy')
        if primary is not None and not np.array_equal(primary, coords):
            raise ValueError('Unmatched primary illumination')
        primary = coords
        responses[name] = signal / coords[:, 0]
        sources[name] = {'ledger_sha256': expected, 'signal_field': field, 'events': len(rows)}

    edges = np.arange(61) / 20
    categories = index(np.abs(primary[:, 1]), edges)
    counts = np.bincount(categories, minlength=60)
    boot = {name: np.empty((1000, 60)) for name in responses}
    # Every replicate resamples the complete shared primary, including all zeros.
    rng = np.random.default_rng(13001000)
    for replicate in range(1000):
        weights = np.bincount(rng.integers(10000, size=10000), minlength=10000)
        for name, response in responses.items():
            boot[name][replicate] = binned_moments(response, categories, weights, 60)[1]
    models = {}
    for name, response in responses.items():
        bins = []
        for i in range(60):
            selected = response[categories == i]
            sample_sd = float(np.std(selected, ddof=1))
            mean = float(np.mean(selected))
            interval = np.quantile(boot[name][:, i], [.025, .975])
            if len(selected) < 2 or mean <= 0 or not np.all(np.isfinite(interval)):
                raise ValueError('Undefined retained bin or bootstrap interval')
            bins.append({'events': len(selected), 'zero_events': int(np.count_nonzero(selected == 0)),
                         'mean_response': mean, 'sample_sd': sample_sd,
                         'fractional_width': sample_sd / mean, 'ci95': interval.tolist()})
        if sum(b['events'] for b in bins) != 10000 or sum(b['zero_events'] for b in bins) != int(np.count_nonzero(response == 0)):
            raise ValueError('Lost events or zeros in rebinning')
        models[name] = {'label': LABELS[name], 'bins': bins, **sources[name]}

    # Reproduce the retained ten fine LAr bins, rather than splicing projections.
    gap = json.loads(frozen('docs/validation/lar-gap10k/summary.json'))
    old_fine = gap['views']['H']['models']['candidate']['projections']['fine_transition']['bins']
    for actual, expected in zip(models['lar400']['bins'][22:32], old_fine):
        if actual['events'] != expected['events'] or actual['zero_events'] != expected['zero_events']:
            raise ValueError('Fine LAr count cross-check failed')
        np.testing.assert_allclose(actual['fractional_width'], expected['fractional_width'], rtol=2e-12, atol=1e-14)
        np.testing.assert_allclose(actual['ci95'], expected['fractional_width_bootstrap']['ci95'], rtol=2e-12, atol=1e-14)

    odd_path = 'docs/validation/issue117/previews/nodd-digitized-response.json'
    odd_raw = frozen(odd_path)
    population = json.loads(odd_raw)['showers']['populations']
    odd = []
    for eta in (0, 1, 2):
        matches = [r for r in population if r['geometry'] == 'odd-zero' and r['particle'] == 'e-'
                   and r['momentum_GeV'] == 20 and r['eta'] == eta]
        if len(matches) != 1 or matches[0]['n'] != 200:
            raise ValueError('Ambiguous fixed-point ODD source')
        row = matches[0]['stages']['raw']
        odd.append({'eta': eta, 'events': 200, 'fractional_width': row['visible_fraction']['RMS_over_mean'],
                    'ci95': row['SD_over_mean_bootstrap']['CI95']})
    result = {'schema_version': 1, 'review_comment': COMMENT, 'date': '2026-11-17',
              'observable': 'sigma(E)/E raw-response proxy: sample SD(R)/mean(R), R=H/Etrue',
              'axis': 'absolute primary pseudorapidity', 'edges': edges.tolist(),
              'matched_primary_events': 10000, 'matched_primary_coordinates_exact': True,
              'events_per_bin_range': [int(counts.min()), int(counts.max())],
              'bootstrap': {'replicates': 1000, 'seed': 13001000, 'resampling': 'shared whole-primary multiplicities',
                            'interval': 'pointwise 95% percentile'},
              'models': models, 'odd_reference': {'label': 'ODD (20 GeV/c reference points)', 'points': odd,
                  'source_revision': BASE, 'source_path': odd_path, 'source_sha256': sha(odd_raw),
                  'phi_rad': .123, 'bootstrap_replicates': 5000, 'connected_curve': False},
              'checks': {'all_events_and_zeros_retained': True, 'existing_LAr_H_fine_bins_reproduced': True},
              'limits': ['ODD is an unmatched fixed-momentum/fixed-direction reference, not a fourth matched10k sample.',
                         'The three matched samples span10-80GeV, full phi and eta-3..3, ECAL-only B=0.',
                         'No digitization or calibrated fixed-energy resolution; zeros and tails are included.',
                         'LAr uses saved H, not complete sensitive deposit A; original readout omissions remain separately documented.',
                         'Uniform fine bins were fixed in the review response before derivation; no new simulation or calibration.'],
              'producer_sha256': sha(Path(__file__).read_bytes()),
              'statistics_helper_sha256': sha((ROOT / 'software/analysis/lar_response/compare.py').read_bytes()),
              'numpy_version': np.__version__}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'output': str(args.output), 'bins': 60, 'events': 10000,
                      'events_per_bin': result['events_per_bin_range'], 'LAr_fine_crosscheck': 'PASS'}))


def drawing(data, width=1000):
    """ReportLab vector drawing, shared by the standalone SVG and report PDF."""
    from reportlab.graphics.shapes import Drawing, Line, PolyLine, Circle, String, Group, Rect, Polygon
    from reportlab.lib.colors import HexColor
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import reportlab

    if 'CaloPlot' not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont('CaloPlot', str(Path(reportlab.__file__).parent / 'fonts/Vera.ttf')))
    d = Drawing(1000, 450)
    ink = HexColor('#172b3a'); grid = HexColor('#d8dfe3')
    def text(x, y, value, size=14, **kwargs):
        d.add(String(x, y, value, fontName='CaloPlot', fontSize=size, fillColor=ink, **kwargs))
    text(76, 428, 'EM calorimeter response comparison', 23)
    text(76, 407, 'Human-selected nODD ECAL baseline: ALLEGRO-style LAr, 400 mm warm gap', 14)
    # All series are ECAL: retain the human-specified component colour and
    # distinguish configurations by line/marker shape, including the legend.
    color = HexColor('#cccc00')
    dashes = {'siw_original': [7, 4], 'siw_staggered': [1.5, 3], 'lar400': [], 'odd': []}
    def marker(key, x, y):
        style = dict(fillColor=color, strokeColor=ink, strokeWidth=.7)
        if key == 'siw_original': d.add(Rect(x - 2.8, y - 2.8, 5.6, 5.6, **style))
        elif key == 'siw_staggered': d.add(Polygon([x, y + 3.8, x - 3.5, y - 2.8, x + 3.5, y - 2.8], **style))
        elif key == 'lar400': d.add(Polygon([x, y + 3.1, x - 3.1, y, x, y - 3.1, x + 3.1, y], **style))
        else: d.add(Circle(x, y, 4.2, **style))
    legend = [('odd', 'ODD: 20 GeV/c, 200 events/direction (unmatched)'),
              ('siw_original', 'nODD Si-W: matched 10k'),
              ('siw_staggered', 'nODD Si-W (staggered): matched 10k'),
              ('lar400', 'nODD LAr: 400 mm, matched 10k')]
    for i, (key, label) in enumerate(legend):
        x = 76 + (i % 2) * 475; y = 380 - (i // 2) * 23
        if key != 'odd': d.add(Line(x, y + 4, x + 24, y + 4, strokeColor=color, strokeWidth=2, strokeDashArray=dashes[key]))
        marker(key, x + 12, y + 4)
        text(x + 32, y, label, 13)
    high = max(100 * b['ci95'][1] for m in data['models'].values() for b in m['bins'])
    ymax = math.ceil(high / 20) * 20
    left, bottom, w, h = 76, 92, 894, 245
    X = lambda x: left + x / 3 * w
    Y = lambda y: bottom + y / ymax * h
    for value in range(0, ymax + 1, 20):
        d.add(Line(left, Y(value), left + w, Y(value), strokeColor=grid, strokeWidth=.6))
        text(left - 9, Y(value) - 4, str(value), 12, textAnchor='end')
    d.add(Line(left, bottom, left, bottom + h, strokeColor=ink))
    d.add(Line(left, bottom, left + w, bottom, strokeColor=ink))
    for i in range(7):
        value = i / 2
        text(X(value), bottom - 21, f'{value:g}', 13, textAnchor='middle')
    text(left + w / 2, bottom - 43, '|eta|', 15, textAnchor='middle')
    ylabel = Group(String(0, 0, 'SD(R) / mean(R) [%]', fontName='CaloPlot',
                          fontSize=15, fillColor=ink, textAnchor='middle'))
    ylabel.translate(20, bottom + h / 2); ylabel.rotate(90); d.add(ylabel)
    centers = [(a + b) / 2 for a, b in zip(data['edges'], data['edges'][1:])]
    for key, model in data['models'].items():
        points = []
        for x, b in zip(centers, model['bins']):
            y = 100 * b['fractional_width']; lo, hi = [100 * z for z in b['ci95']]
            if not all(math.isfinite(z) for z in (y, lo, hi)) or not 0 <= lo <= hi <= ymax or not 0 <= y <= ymax:
                raise ValueError('Nonfinite/out-of-axis comparison point')
            xx = X(x); points.extend([xx, Y(y)])
            d.add(Line(xx, Y(lo), xx, Y(hi), strokeColor=color, strokeWidth=.65, strokeOpacity=.55))
        d.add(PolyLine(points, strokeColor=color, strokeWidth=1.9, fillColor=None, strokeDashArray=dashes[key]))
        for i in range(0, len(centers), 3): marker(key, X(centers[i]), Y(100 * model['bins'][i]['fractional_width']))
    for b in data['odd_reference']['points']:
        xx = X(b['eta']); lo, hi = [100 * z for z in b['ci95']]
        d.add(Line(xx, Y(lo), xx, Y(hi), strokeColor=color, strokeWidth=1.8))
        marker('odd', xx, Y(100 * b['fractional_width']))
    text(76, 28, 'sigma(E)/E response-width proxy: R = summed saved active-hit energy / primary total energy.', 12)
    text(76, 10, 'Matched curves: 0.05-wide |eta| bins, all events/zeros, 95% intervals. ODD: fixed energy and original detector scope; unmatched.', 11)
    d.scale(width / 1000, width / 1000); d.width = width; d.height = 450 * width / 1000
    return d


def render(args):
    from reportlab.graphics import renderSVG, renderPDF
    data = json.loads(args.data.read_text())
    d = drawing(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    renderSVG.drawToFile(d, str(args.output))
    if args.preview:
        renderPDF.drawToFile(d, str(args.preview))
    args.output.with_suffix('.render.json').write_text(json.dumps({
        'data_sha256': sha(args.data.read_bytes()), 'renderer_sha256': sha(Path(__file__).read_bytes()),
        'svg_sha256': sha(args.output.read_bytes()), 'width': d.width, 'height': d.height,
        'renderer': 'ReportLab ' + __import__('reportlab').Version}, indent=2) + '\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    a = sub.add_parser('derive')
    for name in LEDGERS: a.add_argument('--' + name.replace('_', '-'), type=Path, required=True)
    a.add_argument('--output', type=Path, default=HERE / 'response-comparison.json')
    a = sub.add_parser('render'); a.add_argument('--data', type=Path, default=HERE / 'response-comparison.json')
    a.add_argument('--output', type=Path, default=HERE / 'response-comparison.svg'); a.add_argument('--preview', type=Path)
    args = p.parse_args(); (derive if args.command == 'derive' else render)(args)
