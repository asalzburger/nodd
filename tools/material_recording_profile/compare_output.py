#!/usr/bin/env python3
"""Require exact values in every ROOT branch after canonical track ordering."""
import argparse
import json
from pathlib import Path

import awkward as ak
import numpy as np
import uproot


def read(path, events=None):
    tree=uproot.open(path)['material_tracks']
    arrays=tree.arrays(library='ak')
    if events is not None:
        arrays=arrays[arrays.event_id<events]
    keys=['event_id','v_phi','v_eta','v_px','v_py','v_pz']
    order=np.lexsort(tuple(ak.to_numpy(arrays[key]) for key in reversed(keys)))
    return arrays[order]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('baseline',type=Path)
    p.add_argument('candidate',type=Path)
    p.add_argument('output',type=Path)
    p.add_argument('--events',type=int)
    args=p.parse_args()
    before=read(args.baseline,args.events)
    after=read(args.candidate,args.events)
    assert set(before.fields)==set(after.fields)
    assert len(before)==len(after)
    checks={field:ak.almost_equal(before[field],after[field],rtol=0,atol=0)
            for field in before.fields}
    result={'tracks':len(before),'branches':len(checks),
            'exact_value_equality':all(checks.values()),'branch_checks':checks}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    assert result['exact_value_equality'],result
    print(args.output)


if __name__=='__main__':
    main()
