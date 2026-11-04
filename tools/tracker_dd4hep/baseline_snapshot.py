#!/usr/bin/env python3
"""Extract the selected tracker drawing overlay from a maintained inventory.

The FCAL/calorimeter context remains frozen. This separate overlay replaces
only tracker sensitive bounds in the current layout illustrations.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    helper = ROOT / 'tools/solenoid_baseline/tracker_snapshot.py'
    spec = importlib.util.spec_from_file_location('tracker_bounds', helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    bounds = module.extract(args.expected)
    if bounds['total_sensitive'] != 46250 or len(bounds['groups']) != 54:
        raise ValueError('Expected the selected balanced 46250-sensor/54-group tracker')
    selection = ROOT / 'docs/design/inputs/DES-040-balanced-selection.json'
    tracker = dict(display='Reviewer-selected balanced working baseline',
                   sensitive_elements=bounds['total_sensitive'],
                   snapshot_expected_sha256=bounds['expected_sha256'],
                   snapshot_extract_sha256=bounds['extract_sha256'],
                   bound_convention=bounds['bound_convention'],
                   matched_source_sha256=bounds['matched_repository_source_sha256'],
                   sensitive_groups=bounds['groups'])
    result = dict(schema_version=1, baseline='balanced', date='2026-10-29',
                  source_revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  selection='docs/design/inputs/DES-040-balanced-selection.json',
                  selection_sha256=hashlib.sha256(selection.read_bytes()).hexdigest(),
                  producer='tools/tracker_dd4hep/baseline_snapshot.py',
                  producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  tracker=tracker,
                  scope='Sensitive corner bounds only; no passive material, field or combined-detector performance result.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('Extracted 46250 sensitive elements in 54 logical groups')


if __name__ == '__main__':
    main()
