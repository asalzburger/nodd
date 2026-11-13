"""Time unchanged LAr assembly versus real-period initialization and audit IDs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(args):
    output=args.output.resolve(); output.mkdir(parents=True, exist_ok=False)
    tree=ET.parse(args.compact); detectors=tree.find("detectors")
    for d in list(detectors):
        if d.get("id") not in ("10","11"):
            if not 0<=int(d.get("id"))<=7: raise ValueError("Unexpected detector root")
            detectors.remove(d)
    if {d.get("id") for d in detectors}!={"10","11"} or len(detectors)!=2:
        raise ValueError("Both complete LAr components required")
    if tree.find("fields") is not None: raise ValueError("Expected B=0 fixture")
    names={d.get("readout") for d in detectors}; readouts=tree.find("readouts")
    for r in list(readouts):
        if r.get("name") not in names: readouts.remove(r)
    tree.write(output/"detector.xml", encoding="utf-8", xml_declaration=True)
    shutil.copyfile(args.compact.parent/"materials.xml",output/"materials.xml")
    (output/"probe.mac").write_text("/control/echo LAR_PLACE_RUN_INITIALIZE_BEGIN\n/run/initialize\n/control/echo LAR_PLACE_RUN_INITIALIZE_END\n/control/echo LAR_PLACE_STARTUP_DONE\n")
    here=Path(__file__).resolve().parent
    env=os.environ.copy(); env["LAR_PLACE_DIRECTORY"]=str(output)
    env["LAR_PLACE_AUDIT_HEADER"]=str(here/"placement_audit.hpp")
    for key in ("DD4HEP_LIBRARY_PATH","DYLD_LIBRARY_PATH","LD_LIBRARY_PATH"):
        env[key]=os.pathsep.join([*(str(p.resolve().parent) for p in args.library),env.get(key,"")])
    command=[sys.executable,"-u",shutil.which("ddsim"),"--compactFile",str(output/"detector.xml"),
        "--steeringFile",str(here/"placement_steering.py"),"--runType","run","--enableG4Gun",
        "--macroFile",str(output/"probe.mac"),"--numberOfEvents","0","--numberOfThreads","1",
        "--random.seed","13002026","--physics.list","FTFP_BERT","--physics.rangecut","0.7",
        "--part.userParticleHandler","","--outputConfig.forceEDM4HEP","--outputFile",str(output/"unused.root")]
    stages={}; started=time.monotonic(); before=resource.getrusage(resource.RUSAGE_CHILDREN)
    with (output/"probe.log").open("w", buffering=1) as log:
        with subprocess.Popen(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors="replace") as child:
            print(f"Started placement probe PID {child.pid}: {output}",flush=True)
            for line in child.stdout:
                elapsed=time.monotonic()-started; log.write(f"[{elapsed:11.6f}] {line}")
                marker=line.strip()
                if "Populating Geant4 volume manager" in line:
                    stages["DDG4_MAP_BUILD_BEGIN"]=elapsed
                if re.search(r"populated with 43648 sensitive path entries",line):
                    stages["DDG4_MAP_BUILD_END"]=elapsed
                if marker.startswith("LAR_PLACE_"):
                    stages[marker]=elapsed; print(f"{marker} {elapsed:.3f}s",flush=True)
            code=child.wait()
    usage=resource.getrusage(resource.RUSAGE_CHILDREN)
    result={"exit_code":code,"source_revision":subprocess.check_output(["git","rev-parse","HEAD"],cwd=here,text=True).strip(),
        "wall_seconds":time.monotonic()-started,"cpu_seconds":usage.ru_utime+usage.ru_stime-before.ru_utime-before.ru_stime,
        "peak_rss_bytes":usage.ru_maxrss*(1 if sys.platform=="darwin" else 1024),"stages":stages,
        "compact_sha256":sha(output/"detector.xml"),"materials_sha256":sha(output/"materials.xml"),
        "source_compact_sha256":sha(args.compact),"library_sha256":{p.name:sha(p) for p in args.library},
        "probe_sha256":sha(__file__),"audit_sha256":sha(here/"placement_audit.hpp"),"steering_sha256":sha(here/"placement_steering.py"),"log_sha256":sha(output/"probe.log")}
    required={"DDG4_MAP_BUILD_BEGIN","DDG4_MAP_BUILD_END","LAR_PLACE_G4_MAP_BEGIN","LAR_PLACE_G4_MAP_END","LAR_PLACE_NATIVE_MAP_BEGIN","LAR_PLACE_NATIVE_MAP_END","LAR_PLACE_AUDIT_DONE","LAR_PLACE_RUN_INITIALIZE_BEGIN","LAR_PLACE_RUN_INITIALIZE_END","LAR_PLACE_STARTUP_DONE"}
    if not code and required<=set(stages):
        ids,leaves,objects,imprints,centres,axes=(output/"mapping-audit.tsv").read_text().split()
        result.update(sensitive_paths=int(ids),material_leaves=int(leaves),geant4_physical_volume_objects=int(objects),assembly_imprints=int(imprints),
            maximum_native_g4_center_delta_mm=float(centres),maximum_native_g4_axis_delta=float(axes),
            g4_mapping_seconds=stages["DDG4_MAP_BUILD_END"]-stages["DDG4_MAP_BUILD_BEGIN"],
            cached_map_access_seconds=stages["LAR_PLACE_G4_MAP_END"]-stages["LAR_PLACE_G4_MAP_BEGIN"],
            run_initialization_seconds=stages["LAR_PLACE_RUN_INITIALIZE_END"]-stages["LAR_PLACE_RUN_INITIALIZE_BEGIN"],
            native_mapping_seconds=stages["LAR_PLACE_NATIVE_MAP_END"]-stages["LAR_PLACE_NATIVE_MAP_BEGIN"],
            startup_to_audit_seconds=stages["LAR_PLACE_G4_MAP_BEGIN"],
            sensitive_dump_sha256=sha(output/"sensitive.tsv"),leaf_dump_sha256=sha(output/"leaves.tsv"))
    (output/"timing.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    print(json.dumps(result,indent=2))
    if code or not required<=set(stages) or result.get("sensitive_paths")!=43648:
        raise RuntimeError("Placement probe failed; diagnostics retained")


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--compact",type=Path,required=True)
    p.add_argument("--library",type=Path,action="append",required=True);p.add_argument("--output",type=Path,required=True)
    run(p.parse_args())


if __name__=="__main__": main()
