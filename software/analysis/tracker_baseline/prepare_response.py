#!/usr/bin/env python3
"""Prepare the selected strixel Gaussian surrogate from explicitly remapped widths.

This is JSON preparation only; it neither imports ACTS nor runs reconstruction.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'software/analysis/truth_tracking'))
from smearing import build_config, COORDINATES

spec = importlib.util.spec_from_file_location('_selected_strixel_runtime',
    ROOT / 'software/analysis/strixel_reconstruction/runtime.py')
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


def prepare(sensors, widths, selection):
    if selection.get('pitch_mm') != [.075, 2.] or selection.get('previous_pitch_mm') != [.075, .5]:
        raise ValueError('Require registered2mm selection and0.5mm reference')
    systems = {s['ids']['system'] for s in sensors}
    if systems != set(range(1, 8)):
        raise ValueError('Require all seven physical tracker systems')
    scaled, volumes = runtime.scale_widths(widths, sensors, 2.)
    settings = dict(model='gaussian_smearing', merge=False,
                    measured_coordinates_by_system=COORDINATES)
    digitization, counts = build_config(sensors, settings, scaled)
    return scaled, digitization, dict(scaled_strixel_volumes=volumes, sensors_by_system=counts)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native-report', type=Path, required=True)
    p.add_argument('--baseline-error-table', type=Path, required=True)
    p.add_argument('--reference-pitch-mm', type=float, choices=[.5], required=True,
                   help='Explicitly identify the input as0.5mm widths remapped to these native sensor IDs')
    p.add_argument('--selection', type=Path, default=ROOT/'docs/design/inputs/DES-042-strixel-selection.json')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        p.error('Choose a fresh output directory')
    selection = json.loads(a.selection.read_text())
    widths = json.loads(a.baseline_error_table.read_text())
    report = json.loads(a.native_report.read_text())
    scaled, digi, audit = prepare(report['sensors'], widths, selection)
    sources = [a.native_report, a.baseline_error_table, a.selection, Path(__file__),
               Path(runtime.__file__), ROOT/'software/analysis/truth_tracking/smearing.py',
               ROOT/'software/analysis/truth_tracking/digitization.py']
    audit.update(input_sha256={str(p): runtime.sha256(p) for p in sources},
                 reference_pitch_mm=a.reference_pitch_mm, selected_pitch_mm=2.,
                 response='Only systems4/5 local-v sigma scaled by4; other widths unchanged; no merging.',
                 limits='Uncalibrated2mm Gaussian surrogate; native-ID remapping of reference widths must precede this preparation. No reconstruction execution claimed.')
    a.output.mkdir(parents=True)
    for name, data in [('error-table.json',scaled), ('digitization.json',digi), ('preparation.json',audit)]:
        runtime.write_json(a.output/name, data)
    print(json.dumps(audit, indent=2))


if __name__ == '__main__':
    main()
