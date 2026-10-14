#!/usr/bin/env python3
"""Inspect persisted calorimeter job output; numerical controls live in CTest."""
import argparse
import json
from pathlib import Path
import uproot

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--input', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
files = sorted(a.input.glob('*.root'))
if not files:
    p.error(f'No ROOT output files found in {a.input}')
report = {'input': str(a.input.resolve()), 'files': []}
for path in files:
    with uproot.open(path) as file:
        trees = {}
        for key in file.keys(cycle=False):
            obj = file[key]
            if hasattr(obj, 'num_entries'):
                trees[key] = {'entries': int(obj.num_entries)}
        report['files'].append({'name': path.name, 'trees': trees})
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
