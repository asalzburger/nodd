"""Replay the fixed-direction figure from its compact published summary only."""
import argparse
import json
from pathlib import Path
from analyze import fixed_plot

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.summary.read_text())
    required = {'raw_energy', 'raw_fractional', 'corrected_residual'}
    if 'statistics' not in data or not required.issubset(data.get('histograms', {})):
        parser.error('Expected a fixed-direction response summary')
    fixed_plot(data, args.output)
