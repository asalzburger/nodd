"""Prepare/run local PR133-geometry angular samples; never overwrite evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import random
import resource
import shutil
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
ELECTRON_MASS_GEV = 0.00051099895


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def prepare(args):
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    source=args.source.resolve()
    prior=json.loads((source/"timing.json").read_text())
    hashes={}
    for name in ("detector.xml","materials.xml"):
        hashes[name]=sha(source/name)
        if hashes[name]!=prior["sha256"][name]:raise ValueError("Changed PR133 geometry")
        shutil.copyfile(source/name,out/name)
    tree=ET.parse(out/"detector.xml")
    if tree.find("fields") is not None or {int(d.get("id")) for d in tree.findall("./detectors/detector")}!={8,9}:
        raise ValueError("Expected exact zero-field ECAL-only compact")
    rng=random.Random(args.input_seed)
    with (out/"particles.HEPEvt").open("w") as events,(out/"truth-input.jsonl").open("w") as truth:
        for i in range(args.events):
            energy=rng.uniform(10.,80.);eta=rng.uniform(-3.,3.);phi=rng.uniform(-math.pi,math.pi)
            p=math.sqrt(energy*energy-ELECTRON_MASS_GEV**2)
            momentum=[p*math.cos(phi)/math.cosh(eta),p*math.sin(phi)/math.cosh(eta),p*math.tanh(eta)]
            events.write("1\n1 11 0 0 "+" ".join(f"{x:.17g}" for x in momentum+[ELECTRON_MASS_GEV])+"\n")
            truth.write(json.dumps(dict(event=i,energy_GeV=energy,eta=eta,phi=phi,momentum_GeV=momentum),separators=(",",":"))+"\n")
    manifest=dict(status="PROTOTYPE",source_revision=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
      original_geometry_revision=prior["environment"]["source_revision"],events=args.events,input_seed=args.input_seed,
      distributions=dict(total_energy_GeV=[10,80],eta=[-3,3],phi_rad=[-math.pi,math.pi],independent_uniform=True),
      electron_mass_GeV=ELECTRON_MASS_GEV,hashes=hashes,
      geometry_source="PR133 exact retained ECAL-only compact; no tracker/beam pipe/field",
      input_sha256=sha(out/"particles.HEPEvt"),truth_sha256=sha(out/"truth-input.jsonl"),
      producer_sha256=sha(__file__),disk_free_bytes=shutil.disk_usage(out).free)
    save(out/"sample.json",manifest)
    print(json.dumps(manifest,indent=2))


def run(args):
    sample=args.sample.resolve();manifest=json.loads((sample/"sample.json").read_text())
    for name,digest in manifest["hashes"].items():
        if sha(sample/name)!=digest:raise ValueError("Changed geometry input")
    if sha(sample/"particles.HEPEvt")!=manifest["input_sha256"]:raise ValueError("Changed primary input")
    count=min(args.events,manifest["events"]-args.skip)
    reserve=args.reserve_gib*1024**3
    free=shutil.disk_usage(sample).free
    if args.bytes_per_event:
        count=min(count,max(0,int((free-reserve)/(2*args.bytes_per_event))))
    if count<args.threads or free<reserve:raise ValueError("Insufficient disk margin or events for worker audit")
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);(out/"audit").mkdir()
    env=os.environ.copy();env["NODD_ANGULAR_AUDIT"]=str(out/"audit")
    for name in ("DD4HEP_LIBRARY_PATH","DYLD_LIBRARY_PATH","LD_LIBRARY_PATH"):
        env[name]=os.pathsep.join([str(args.geometry_library.resolve().parent),str(args.audit_library.resolve().parent),env.get(name,"")])
    steering=Path(__file__).with_name("angular_transport.py")
    command=[sys.executable,"-u",shutil.which("ddsim"),"--compactFile",str(sample/"detector.xml"),
      "--steeringFile",str(steering),"--runType","batch","--inputFiles",str(sample/"particles.HEPEvt"),
      "--numberOfEvents",str(count),"--skipNEvents",str(args.skip),"--numberOfThreads",str(args.threads),
      "--random.seed",str(args.seed),"--random.enableEventSeed","--physics.list","FTFP_BERT", "--physics.rangecut","0.7",
      "--part.userParticleHandler","","--outputConfig.forceEDM4HEP","--outputFile",str(out/"events.root")]
    start=time.monotonic();started=datetime.now(timezone.utc).isoformat();before=resource.getrusage(resource.RUSAGE_CHILDREN)
    save(out/"started.json",dict(command=command,started_at=started,requested_events=args.events,actual_events=count,free_bytes=free,reserve_bytes=reserve))
    disk_abort=False;last_status=start
    with (out/"transport.log").open("w") as log:
        with subprocess.Popen(command,env=env,cwd=out,stdout=log,stderr=subprocess.STDOUT) as child:
            while child.poll() is None:
                now=time.monotonic()
                if shutil.disk_usage(out).free<reserve:
                    disk_abort=True;child.send_signal(signal.SIGINT)
                if now-last_status>=30:
                    last_status=now
                    size=(out/"events.root").stat().st_size if (out/"events.root").exists() else 0
                    print(f"DDSim {args.threads} threads: {now-start:.1f}s, ROOT {size/1e6:.1f} MB, free {shutil.disk_usage(out).free/1024**3:.1f} GiB",flush=True)
                time.sleep(1)
            code=child.returncode
    usage=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt=dict(command=command,started_at=started,ended_at=datetime.now(timezone.utc).isoformat(),exit_code=code,
      disk_abort=disk_abort,events=count,threads=args.threads,skip=args.skip,seed=args.seed,wall_seconds=time.monotonic()-start,
      cpu_seconds=usage.ru_utime+usage.ru_stime-before.ru_utime-before.ru_stime,
      peak_rss_bytes=usage.ru_maxrss*(1 if sys.platform=="darwin" else 1024),
      output_bytes=(out/"events.root").stat().st_size if (out/"events.root").exists() else 0,
      free_bytes_after=shutil.disk_usage(out).free,sample_sha256=sha(sample/"sample.json"),
      steering_sha256=sha(steering),runner_sha256=sha(__file__),
      geometry_library_sha256=sha(args.geometry_library),audit_library_sha256=sha(args.audit_library))
    save(out/"receipt.json",receipt);print(json.dumps(receipt,indent=2),flush=True)
    if code or disk_abort:raise RuntimeError("Transport failed; retained all diagnostics")


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest="stage",required=True)
    p=sub.add_parser("prepare");p.add_argument("--source",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    p.add_argument("--events",type=int,default=10000);p.add_argument("--input-seed",type=int,default=13310000)
    p=sub.add_parser("run");p.add_argument("--sample",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    p.add_argument("--geometry-library",type=Path,required=True);p.add_argument("--audit-library",type=Path,required=True)
    p.add_argument("--events",type=int,default=10000);p.add_argument("--skip",type=int,default=0);p.add_argument("--threads",type=int,default=12)
    p.add_argument("--seed",type=int,default=133812341);p.add_argument("--reserve-gib",type=float,default=30)
    p.add_argument("--bytes-per-event",type=float,default=None)
    args=parser.parse_args();globals()[args.stage](args)


if __name__=="__main__":main()
