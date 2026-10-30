#!/usr/bin/env python3
"""DES041 same-seed electron replay with the isolated SafeFatras transport.

Inject only the task-owned Python runner's transport dependency. The shared
ACTS modules, native helper and original Geant4 runner remain untouched.
"""
import importlib
from pathlib import Path
import sys
from types import SimpleNamespace

import nodd_tracker_reconstruction as runner

ROOT=runner.ROOT
original_transport=runner.transport
original_fingerprints=runner.fingerprints


def schedule(seq,acts,detector,geometry,field,rnd,observer,config,events,level):
    if (config.get("simulation")!="fatras" or config.get("particle")!="electron" or
        not config.get("species_extension",{}).get("fatras_numerical_guard") or
        config.get("transport",{})!={} or events<=0):
        raise ValueError("SafeFatras replay requires its declared electron/Fatras campaign without transport overrides")
    sys.path.insert(0,str(ROOT/"build/tracker-reconstruction-species/native-safe-fatras"))
    safe=importlib.import_module("nodd_safe_fatras")
    # Exactly one simulation algorithm, in the original sequencer slot. ACTS
    # random streams depend on algorithm number as well as seed/event number.
    effective=safe.schedule(seq,geometry,field,rnd,level)
    return {"simulation":"fatras","truth_selection":None,"enableInteractions":True,
        **effective,"numerical_sidecar":original_transport._module_identity(safe),
        "upstream_source_revision":safe.source_revision,"upstream_sha256":dict(safe.upstream_sha256),
        "generated_header_sha256":safe.generated_header_sha256,
        "generated_source_sha256":safe.generated_source_sha256,
        "pybind11_version":safe.pybind11_version,"pybind11_internals_version":safe.pybind11_internals_version,
        "lifecycle":"Native Fatras algorithm, same sequencer position and collections; no persistent handle"},lambda:None


def fingerprints():
    result=original_fingerprints()
    files=[Path(__file__),*sorted((ROOT/"software/source/ActsExamples/SafeFatras").glob("*.cpp")),
        *sorted((ROOT/"software/source/ActsExamples/SafeFatras").glob("*.hpp")),
        ROOT/"software/source/ActsExamples/SafeFatras/CMakeLists.txt",
        *sorted((ROOT/"build/tracker-reconstruction-species/native-safe-fatras").glob("*.so"))]
    result.update({str(p.resolve()):runner.sha256(p) for p in files})
    return result


if __name__=="__main__":
    runner.transport=SimpleNamespace(schedule=schedule)
    runner.fingerprints=fingerprints
    runner.main()
