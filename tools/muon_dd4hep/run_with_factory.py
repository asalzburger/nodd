#!/usr/bin/env python3
"""Load a task factory, run an installed DD4hep CLI, and release geometry safely.

Explicit cleanup before interpreter shutdown avoids the installed ROOT6.40
TGeo thread-data mutex teardown failure. CLI SystemExit codes propagate.
"""
from pathlib import Path
import runpy
import sys


def main():
    import ROOT
    import dd4hep
    library, script, *arguments = sys.argv[1:]
    if ROOT.gSystem.Load(str(Path(library).resolve())) < 0:
        raise RuntimeError('Factory load failed')
    sys.argv = [script, *arguments]
    try:
        runpy.run_path(script, run_name='__main__')
    finally:
        ROOT.DisableImplicitMT()
        dd4hep.Detector.destroyInstance()
        if ROOT.gGeoManager:
            ROOT.gGeoManager.Delete()


if __name__ == '__main__':
    main()
