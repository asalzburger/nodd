#!/usr/bin/env python3
"""Native guard controls only, without detector construction or transport.

Run once in a fresh process with the matching ACTS bindings and sidecar.
"""
import argparse
import json
from pathlib import Path
import sys


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native-module-dir',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():p.error('Output exists; choose a fresh file')
    import acts.examples.geant4
    sys.path.insert(0,str(a.native_module_dir.resolve()))
    import nodd_material_recording_native as native
    checks={}
    try:native.persistent_handle(0)
    except (ValueError,RuntimeError):checks['nonpositive_expected_events_rejected']=True
    else:checks['nonpositive_expected_events_rejected']=False
    handle=native.persistent_handle(1)
    try:native.persistent_handle(1)
    except RuntimeError:checks['duplicate_manager_rejected']=True
    else:checks['duplicate_manager_rejected']=False
    before=dict(native.report(handle))
    try:native.finish(handle)
    except RuntimeError:checks['unstarted_incomplete_completion_rejected']=True
    else:checks['unstarted_incomplete_completion_rejected']=False
    checks['rejection_preserves_unstarted_state']=before==dict(native.report(handle))
    native.finish(handle,False)
    checks['unstarted_cleanup_preserves_state']=before==dict(native.report(handle))
    assert all(checks.values()),checks
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps(checks))


if __name__=='__main__':main()
