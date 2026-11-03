#!/usr/bin/env python3
"""Export the selected balanced baseline using the installed native Gen3 adapter.

The historical material-mapping exporter keeps its original count guards. This
entry point checks the maintained expected inventory before producing an export.
It does not create or qualify a material map.
"""
import argparse
import ctypes
import hashlib
import importlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from software.analysis.gen3_material_mapping.export_geometry import build_export, sha256
from tools.tracker_dd4hep.check_gen3 import compare


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build-dir', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    a = p.parse_args()
    build = a.build_dir.resolve()
    directory = build / 'detector'
    compact = directory / 'tracker/tracker.xml'
    expected_path = compact.with_name('expected.json')
    expected = json.loads(expected_path.read_text())
    if sum(e['role'] == 'sensitive' for e in expected['entities']) != 46250:
        raise ValueError('Expected selected balanced inventory of 46250 sensors')
    a.output_dir.mkdir(parents=True, exist_ok=True)
    ctypes.CDLL('libDDG4.dylib' if sys.platform == 'darwin' else 'libDDG4.so', mode=ctypes.RTLD_GLOBAL)
    import ROOT
    import acts
    import acts.json
    from acts.examples.nodd import getNoddDetector
    ROOT.gROOT.SetBatch(True)
    detector = getNoddDetector(nodd_dir=REPO, build_dir=build, logLevel=acts.logging.WARNING)
    report = json.loads(detector.geometryReport())
    comparison = compare(report, expected)
    if comparison['status'] != 'PASS' or comparison['volumes'] != 120:
        raise ValueError(comparison)
    converter = acts.json.TrackingGeometryJsonConverter(level=acts.logging.WARNING)
    context = detector.nominalGeometryContext()
    serialized = converter.toJson(context, detector.trackingGeometry())
    native = json.loads(serialized)
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / 'geometry.json'
        path.write_text(serialized)
        decoded = converter.fromFile(context, path)
        if native != json.loads(converter.toJson(context, decoded)):
            raise ValueError('Native serialized Gen3 round trip changed payload')
    result = build_export(native, report, lambda encoded: acts.GeometryIdentifier(**(encoded or {})).value)
    if result['checks']['sensitive_surfaces'] != 46250 or result['checks']['volumes'] != 120:
        raise ValueError('Unexpected balanced Gen3 inventory')
    result['checks']['native_json_round_trip'] = 'PASS: complete serialized payload identical'
    files = [compact, compact.with_name('materials.xml'), expected_path, Path(__file__),
             REPO / 'tools/tracker_dd4hep/check_gen3.py',
             REPO / 'software/analysis/gen3_material_mapping/export_geometry.py']
    suffix = '.dylib' if sys.platform == 'darwin' else '.so'
    files.extend(directory / ('lib' + name + suffix) for name in (
        'nODDBeamPipe', 'nODDPixelBarrel', 'nODDShortStripBarrel', 'nODDShortStripEndcap', 'nODDLongStrip'))
    module = importlib.import_module('acts.ActsPythonBindings')
    runtime = Path(module.__file__).parents[2]
    files.extend(Path(importlib.import_module(name).__file__) for name in (
        'acts.ActsPythonBindings', 'acts.examples.ActsExamplesPythonBindingsNodd', 'acts.examples.nodd'))
    files.extend(runtime / 'lib' / ('lib' + name + suffix) for name in (
        'ActsCore', 'ActsExamplesNodd', 'ActsPluginDD4hep', 'ActsPluginJson'))
    result['provenance'] = dict(
        source_revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
        baseline='balanced', ROOT=ROOT.gROOT.GetVersion(), python=platform.python_version(),
        native_serialization_sha256=hashlib.sha256(serialized.encode()).hexdigest(),
        files=[dict(name=q.name, sha256=sha256(q)) for q in files],
        runtime_scope='Binary fingerprints identify the installed runtime; current external source HEAD is not asserted as its compiled revision.',
        material_scope='Geometry export only. No new Geant4 material map or tracking performance is claimed.')
    for name, payload in [('geometry.json', result), ('native-report.json', report), ('source-comparison.json', comparison)]:
        (a.output_dir / name).write_text(json.dumps(payload, indent=2, allow_nan=False) + '\n')
    print(json.dumps(result['checks'], indent=2))


if __name__ == '__main__':
    main()
