#!/usr/bin/env python3
"""Isolated native DES040 Fatras candidate preparation and truth tracking."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import importlib

ROOT_DIR=Path(__file__).resolve().parents[2]
# Load the task runtime under a distinct name: baseline has its own runtime.py.
sys.path.insert(0,str(ROOT_DIR/"software/analysis/tracker_optimization"))
import importlib.util
spec=importlib.util.spec_from_file_location("tracker_candidate_runtime",ROOT_DIR/"software/analysis/tracker_optimization/runtime.py")
runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
from material_runtime import common_arguments,provenance,sha256,write_report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    common_arguments(parser)
    parser.add_argument("--variant",type=Path,required=True)
    parser.add_argument("--compact",type=Path,required=True)
    parser.add_argument("--pt",type=float,default=10.)
    parser.add_argument("--seed",type=int,default=42042)
    parser.add_argument("--threads",type=int,default=1)
    parser.add_argument("--digitization",choices=("geometric","gaussian"),default="geometric")
    parser.add_argument("--prepare-only",action="store_true")
    parser.add_argument("--observer-module-dir",type=Path,default=ROOT_DIR/"build/truth-tracking-baseline/native")
    parser.add_argument("--material-module-dir",type=Path,default=ROOT_DIR/"build/tracker-resolution-optimization/native")
    args=parser.parse_args()
    for name in ("variant","compact","manifest","nodd_dir","build_dir","output","native_module_dir","observer_module_dir","material_module_dir"):
        setattr(args,name,getattr(args,name).resolve())
    if args.events<=0 or args.threads!=1 or args.pt not in (1.,10.,100.):
        parser.error("Require positive events, one thread and pT1/10/100GeV")
    args.output.mkdir(parents=True,exist_ok=True)
    if (args.output/"run-report.json").exists() or any(args.output.glob("*.root")):
        parser.error("Output already contains a report/native output; use a fresh case")
    variant=json.loads(args.variant.read_text())
    start=time.monotonic()
    revision=subprocess.check_output(["git","-C",str(ROOT_DIR),"rev-parse","HEAD"],text=True).strip()
    sources=[Path(__file__).resolve(),*[ROOT_DIR/"software/analysis/tracker_optimization"/n for n in ("compact.py","material.py","runtime.py")],
        ROOT_DIR/"software/source/ActsExamples/TrackerOptimization/MaterialTools.cpp",ROOT_DIR/"software/source/ActsExamples/TrackerOptimization/CMakeLists.txt",
        *[ROOT_DIR/"software/running"/n for n in ("nodd_truth_tracking.py","nodd_truth_tracking_smearing.py")],
        *[ROOT_DIR/"software/analysis/truth_tracking"/n for n in ("runtime.py","digitization.py","smearing.py")],
        *[ROOT_DIR/"software/analysis/gen3_material_mapping"/n for n in ("material_runtime.py","export_geometry.py","select_surfaces.py")],
        ROOT_DIR/"software/env/truth_tracking.sh"]
    hashes={str(p.relative_to(ROOT_DIR)):sha256(p) for p in sources}
    report={"schema_version":1,"status":"PROTOTYPE","outcome":"started","variant":variant,
        "events":args.events,"simulation":"fatras","pt_GeV":args.pt,"seed":args.seed,"threads":1,
        "digitization_model":args.digitization,"scientific_input_revision":revision,"executed_source_sha256":hashes,"command":sys.argv}
    try:
        ROOT,acts,sidecar,observer,helper,detector,geometry,config,info,files=runtime.prepare(args,variant)
        for name in ("acts.examples.ActsExamplesPythonBindings", "acts.examples.ActsExamplesPythonBindingsGeant4"):
            files.append(("runtime_binding",Path(importlib.import_module(name).__file__)))
        runtime_build=Path(importlib.import_module("acts.ActsPythonBindings").__file__).parents[2]
        for name in ("ActsExamplesFatras","ActsExamplesDigitization","ActsExamplesTrackFitting","ActsExamplesTruthTracking","ActsExamplesIoRoot"):
            library=runtime_build/"lib"/f"lib{name}.dylib"
            if not library.is_file():raise RuntimeError("Missing frozen runtime library "+name)
            files.append(("runtime_library",library))
        files.extend(("observer_source",ROOT_DIR/"software/source/ActsExamples/TruthTracking"/name) for name in ("TruthTracking.cpp","CMakeLists.txt"))
        report.update(info);report["campaign"]=config
        report["provenance"]=provenance(args,sidecar,[*files,("variant",args.variant),
            *[("executed_source",p) for p in sources]])
        report["provenance"]["analysis_source_revision_at_launch"]=revision
        report["compiled_ACTS_source_revision"]="355ea68493b326956756c9386d2fd9eaf9328568"
        report["runtime_source_qualification"]="Existing hashed runtime and isolated helper use sibling ACTS355 source/build; a separate external ACTS checkout HEAD is not the executed runtime identity"
        report["ROOT"]=ROOT.gROOT.GetVersion()
        write_report(args.output/"run-report.json",report)
        if args.prepare_only:
            report["outcome"]="prepared"
        else:
            counts,inventory,names,covariance_audit=runtime.execute(args,config,ROOT,acts,detector,geometry,observer)
            report.update(counts=counts,root_inventory=inventory,measurement_covariance_audit=covariance_audit)
            report["output_sha256"]={name:sha256(args.output/name) for name in names}
            report["provenance"]["files"].extend({"role":"native_output","name":name,"sha256":digest} for name,digest in report["output_sha256"].items())
            if any(sha256(p)!=hashes[str(p.relative_to(ROOT_DIR))] for p in sources):
                raise RuntimeError("Candidate or frozen baseline source changed during execution")
            report["outcome"]="completed"
    except Exception as error:
        report["outcome"]="failed";report["error"]=f"{type(error).__name__}: {error}"
        raise
    finally:
        report["wall_seconds"]=time.monotonic()-start
        write_report(args.output/"run-report.json",report)
    print(json.dumps({"outcome":report["outcome"],"counts":report.get("counts"),"candidate_counts":report.get("candidate_counts"),"wall_seconds":report["wall_seconds"]}))


if __name__=="__main__":main()
