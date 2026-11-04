"""Verify retained reconstruction counts, distributions and execution identity."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np

ROOT=Path(__file__).resolve().parents[3]


def read(path):
    path=Path(path)
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix==".gz" else path.read_bytes())


def verify(data):
    data=Path(data)
    manifest=read(data/"manifest.json")
    for relative,digest in manifest["files_sha256"].items():
        if hashlib.sha256((data/relative).read_bytes()).hexdigest()!=digest:raise ValueError("Retained artifact changed: "+relative)
    selection=read(data/"frozen/selection.json")
    for relative,digest in selection["analysis_inputs_sha256"].items():
        path=data/"tuning"/(relative+".gz")
        if hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest()!=digest:raise ValueError("Frozen tuning input changed: "+relative)
    frozen=read(data/"frozen/selected-campaign.json");validation=read(data/"frozen/validation-campaign.json")
    if frozen["profiles"]!=validation["profiles"] or frozen["ckf"]!=validation["ckf"] or frozen["quality"]!=validation["quality"]:
        raise ValueError("Validation changed selected reconstruction")
    selected=selection["selected_profile"]
    n=0;source_pins=set();binary_hashes={};runtime=None;source_cache={}
    for phase in ("tuning","validation"):
        reports=read(data/("native-"+phase+"-reports.json.gz"))
        summaries=list((data/phase).glob("*/*/summary.json.gz"))
        if len(summaries)!=(52 if phase=="tuning" else 8):raise ValueError("Incomplete declared campaign")
        for path in summaries:
            s=read(path);relative=str(path.parent.relative_to(data/phase));r=reports[relative]
            if r["outcome"]!="completed" or s["events"]!=r["events"]:raise ValueError("Failed or incomplete native run")
            if s["seed"]!=r["seed"] or r["phase"]!=phase:raise ValueError("Wrong sample split")
            if phase=="validation" and r["seed"]!=validation["sample_seeds"]["validation"]:raise ValueError("Wrong held-out seed")
            if s["run_report_sha256"]!=hashlib.sha256(json.dumps(r,indent=2,allow_nan=False).encode()+b"\n").hexdigest():
                raise ValueError("Native report identity changed")
            if r["gbts_statistics"]["events"]!=s["events"] or r["gbts_statistics"]["retained_seeds"]!=s["stage_counts"]["seeds"]:
                raise ValueError("Native seed stage counts changed")
            if r["gbts_statistics"]["input_spacepoints"]!=s["stage_counts"]["spacepoints"]:raise ValueError("Native SP count changed")
            if r["gbts_statistics"]["effective_configuration"]["b_field_T"]!=3.:raise ValueError("GBTS field changed")
            if not all(s["measurement_audit"]["systems"].get(str(k),0)>0 for k in range(1,8)):raise ValueError("Missing tracker system")
            if not s["measurement_audit"]["frozen_native_double_variances"]:raise ValueError("Unverified measurement errors")
            for key in ("material-map.json","error-table.json","digitization.json"):
                if not r["preparation"]["baseline_semantic_equivalence"][key]:raise ValueError("Baseline response/material changed")
            # Source HEAD at launch is linked to actual executed file bytes;
            # ignored compiled modules retain separate binary identities.
            revision=r["source_revision"];source_pins.add(revision)
            analysis_key=(revision,"software/analysis/tracker_reconstruction/analyze.py")
            if analysis_key not in source_cache:
                source_cache[analysis_key]=hashlib.sha256(subprocess.check_output(["git","show",revision+":"+analysis_key[1]],cwd=ROOT)).hexdigest()
            if s["source_sha256"]!=source_cache[analysis_key]:raise ValueError("Reduction source differs from preserved execution revision")
            for absolute,digest in r["source_sha256"].items():
                marker="/nodd-gen3-material-mapping/"
                if marker not in absolute:raise ValueError("Unknown execution checkout")
                relative_source=absolute.split(marker,1)[1]
                if relative_source.startswith("build/"):
                    binary_hashes.setdefault(phase,{}).setdefault(relative_source,set()).add(digest);continue
                key=(revision,relative_source)
                if key not in source_cache:
                    source_cache[key]=hashlib.sha256(subprocess.check_output(["git","show",revision+":"+relative_source],cwd=ROOT)).hexdigest()
                if source_cache[key]!=digest:raise ValueError("Executed source not present at launch revision: "+relative_source)
            if runtime is None:runtime=r["runtime_sha256"]
            elif r["runtime_sha256"]!=runtime:raise ValueError("Native ACTS/factory runtime differs across campaign")
            a=np.load(path.with_name("events.npz"));events=s["events"]
            if len(a["event"])!=events or len(np.unique(a["event"]))!=events:raise ValueError("Lost generated events")
            for stage in ("ckf","ambi"):
                c=s["stages"][stage]["counts"]
                for key in ("matched","accepted","fake","duplicates","secondary","wrong_charge"):
                    if int(a[stage+"_"+key].sum())!=c[key]:raise ValueError("Retained count mismatch: "+key)
                if s["stages"][stage]["efficiency"]["value"]!=c["matched"]/events:raise ValueError("All-generated denominator changed")
                matched=a[stage+"_matched"].astype(bool)
                expected=a["truth"]-a[stage+"_reco"]
                expected[:,2]=(expected[:,2]+np.pi)%(2*np.pi)-np.pi
                if not np.array_equal(expected,a[stage+"_residual"],equal_nan=True):raise ValueError("Residual sign/wrapping changed")
                if not np.array_equal(expected/np.sqrt(a[stage+"_variance"]),a[stage+"_pull"],equal_nan=True):raise ValueError("Pull definition changed")
                if np.any(~np.isfinite(a[stage+"_reco"][matched])) or np.any(a[stage+"_variance"][matched]<=0):raise ValueError("Invalid matched fit")
                for label,mask in (("conditional",a["reconstructable"]), ("conditional4",a["reconstructable4"])):
                    denominator=int(mask.sum());numerator=int((matched&mask.astype(bool)).sum())
                    metric=s["stages"][stage][label]
                    if (metric["numerator"],metric["denominator"])!=(numerator,denominator):raise ValueError("Conditional denominator changed")
            n+=events
        if phase=="validation":
            for pt in (1,5,10,100):
                a=read(data/phase/"selected"/f"pt{pt}"/"summary.json.gz");b=read(data/phase/"control"/f"pt{pt}"/"summary.json.gz")
                if a["sample_sha256"]!=b["sample_sha256"] or a["profile"]!=selected:raise ValueError("Unpaired or wrong selected validation")
    if any(len(values)!=1 for modules in binary_hashes.values() for values in modules.values()):raise ValueError("Sidecar changed within a campaign")
    print(f"PASS:60native cases,{n}processed generated-muon entries, all-event counts/residuals/pulls, frozen selection, paired samples, actual source/runtime and baseline response identities; source pins={sorted(source_pins)}")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--data",type=Path,default=ROOT/"docs/validation/tracker-reconstruction");a=p.parse_args();verify(a.data)
