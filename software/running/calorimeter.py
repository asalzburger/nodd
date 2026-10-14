#!/usr/bin/env python3
"""Steer the migrated synthetic ActsExamples calorimeter control jobs."""
import argparse
from pathlib import Path
import subprocess

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--mode', choices=('basic', 'jets', 'edm4hep', 'edm4hep-jets'), default='basic')
p.add_argument('--build-dir', type=Path)
p.add_argument('--output', type=Path)
a = p.parse_args()
root = Path(__file__).resolve().parents[2]
build = (a.build_dir or root / 'build/acts').resolve()
output = (a.output or root / 'build/jobs/calorimeter' / a.mode).resolve()
output.mkdir(parents=True, exist_ok=True)
name = {'basic': 'ActsExampleCalorimeter', 'jets': 'ActsExampleCalorimeterJets',
        'edm4hep': 'ActsExampleCalorimeterEDM4hep',
        'edm4hep-jets': 'ActsExampleCalorimeterJetsEDM4hep'}[a.mode]
executable = build / 'bin' / name
if not executable.is_file():
    p.error(f'Build the calorimeter software first: {executable}')
command = [str(executable)]
if a.mode.startswith('edm4hep'):
    command.append(str(output))
subprocess.run(command, cwd=output, check=True)
