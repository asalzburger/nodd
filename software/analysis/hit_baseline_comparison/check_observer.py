#!/usr/bin/env python3
"""Check that the passive hit observer leaves native material recording unchanged."""
import argparse
import json
from pathlib import Path

import awkward as ak
import uproot

from reduce import sha


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--observed',type=Path,required=True)
    ap.add_argument('--reference',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    with uproot.open(args.observed) as a,uproot.open(args.reference) as b:
        observed=a['material_tracks'].arrays()
        reference=b['material_tracks'].arrays(entry_stop=len(observed))
    if set(ak.fields(observed))!=set(ak.fields(reference)):
        raise ValueError('Material recording branches changed')
    checks={k:bool(ak.all(observed[k]==reference[k])) for k in ak.fields(observed)}
    report={'rays':len(observed),'branches':checks,'exact_numeric_equality':all(checks.values()),
        'observed_sha256':sha(args.observed),'reference_sha256':sha(args.reference),'checker_sha256':sha(__file__),
        'scope':'First matching generated rays, unchanged current compact/factories and seed228; passive direct hit observer versus prior material-only recording'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    if not all(checks.values()):raise ValueError('Observer changed native material recording')
    print(f'PASS: {len(checks)} branches, {len(observed)} rays exactly equal')


if __name__=='__main__':main()
