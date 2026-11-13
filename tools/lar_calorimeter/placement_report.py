"""Collect bound placement, native and first-event evidence; raw artifacts stay local."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def sha(path):
    with Path(path).open("rb") as stream: return hashlib.file_digest(stream,"sha256").hexdigest()


def load(path): return json.loads(Path(path).read_text())


def first_event_time(log):
    for line in log.splitlines():
        if "ParticleHandler" in line and "Begin event action" in line:
            match=re.match(r"^\[\s*([0-9.]+)\]",line)
            if not match: raise ValueError("Missing first-event timestamp")
            return float(match[1])
    raise ValueError("Missing first event")


def run_record(directory):
    timing=load(directory/"timing.json");smoke=load(directory/"smoke-readback.json")
    if timing["exit_code"] or timing["smoke_events"]!=7 or not timing.get("launch_identity_unchanged"):
        raise ValueError("Incomplete or changed first-event probe")
    if smoke["status"]!="PASS" or smoke["events"]!=7 or smoke["timing_sha256"]!=sha(directory/"timing.json"):
        raise ValueError("Unbound smoke readback")
    if smoke["cases_sha256"]!=sha(directory/"smoke-cases.json") or timing["log_sha256"]!=sha(directory/"probe.log"):
        raise ValueError("Changed macro cases or run log")
    for name,key in (("detector.xml","compact_sha256"),("materials.xml","materials_sha256")):
        if sha(directory/name)!=timing[key]: raise ValueError("Changed executed compact/material artifact")
    for name,key in (("sensitive.tsv","sensitive_dump_sha256"),("leaves.tsv","leaf_dump_sha256")):
        if sha(directory/name)!=timing[key]: raise ValueError("Changed native inventory")
    for row in smoke["results"]:
        if sha(directory/(row["case"]["label"]+".root"))!=row["root_sha256"]:
            raise ValueError("Changed persisted smoke event")
    elapsed=first_event_time((directory/"probe.log").read_text())
    return {"timing":timing,"timing_sha256":sha(directory/"timing.json"),"smoke":smoke,
        "smoke_sha256":sha(directory/"smoke-readback.json"),"first_event_begin_seconds":elapsed,
        "post_run_initialize_to_first_event_seconds":elapsed-timing["stages"]["LAR_PLACE_RUN_INITIALIZE_END"]}


def collect(args):
    stock,candidate=run_record(args.work/args.stock),run_record(args.work/args.candidate)
    for key in ("materials_sha256","library_sha256","probe_sha256","audit_sha256","steering_sha256","source_revision"):
        if stock["timing"][key]!=candidate["timing"][key]: raise ValueError("Unmatched probe configuration: "+key)
    for key in ("sensitive_paths","material_leaves","sensitive_dump_sha256","leaf_dump_sha256"):
        if stock["timing"][key]!=candidate["timing"][key]: raise ValueError("Changed physical leaf inventory: "+key)
    if [r["case"] for r in stock["smoke"]["results"]]!=[r["case"] for r in candidate["smoke"]["results"]]:
        raise ValueError("Unmatched smoke primary cases")
    native={}
    for folder in ("barrel-final","endcaps-final","combined-final"):
        p=args.work/folder/"native.json";r=load(p)
        if r["status"]!="PASS" or r["overlaps"] or r["overlap_tolerance_mm"]!=1e-5:
            raise ValueError("Native geometry gate failed")
        root_file=p.with_suffix(".root")
        if sha(root_file)!=r["root_sha256"]: raise ValueError("Changed native ROOT geometry")
        keys=("status","execution","mass_g","physical_sensitive_volume_ids","derived_logical_channels",
              "canonical_reference_keys_checked","grouped_hit_inverse_checks","grouped_gap_inverse_checks","canonical_inverse_checks",
              "ghost_boundary_rejections","overlap_seed","overlap_tolerance_mm","overlaps","ray_count","root_sha256","native_detector_roots")
        native[folder]={k:r[k] for k in keys if k in r}
        native[folder]["report_sha256"]=sha(p)
    rays=load(args.work/"ray-comparison.json")
    if rays["rays"]!=65 or rays["maximum_material_path_delta_mm"]>=1e-5 or rays["maximum_radiation_length_delta"]>=1e-6 or rays["maximum_interaction_length_delta"]>=1e-6:
        raise ValueError("Material path comparison failed")
    variant=load(args.work/"candidate-v2/variant.json")
    if not variant["unchanged_after_stripping_only_envelopes"] or variant["added_envelopes"]!=4:
        raise ValueError("Physical XML preservation failed")
    if stock["timing"]["source_compact_sha256"]!=variant["source_sha256"] or candidate["timing"]["source_compact_sha256"]!=variant["candidate_sha256"]:
        raise ValueError("Unbound stock/candidate compacts")
    partitions={name:load(args.work/name/"expected.json")["placement"] for name in ("barrel-final","endcaps-final")}
    result={"status":"PROTOTYPE","scope":"Opt-in real period mothers, complete ECAL-only B=0 serial probes; unchanged physical geometry/readout",
        "implementation_revision":"8d74a4c1221a19d314881c4deccb2b5986ff425d","probe_revision":stock["timing"]["source_revision"],
        "metric":"Child launch to first ParticleHandler event-begin message, including fixed mapping/audit overhead; not isolated voxelization or throughput",
        "run_count":"One fresh-process matched actual-event pair; no timing confidence interval or stable-speedup claim",
        "stock":stock,"candidate":candidate,"first_event_speedup_observed":stock["first_event_begin_seconds"]/candidate["first_event_begin_seconds"],
        "ddg4_map_speedup_observed":stock["timing"]["g4_mapping_seconds"]/candidate["timing"]["g4_mapping_seconds"],
        "smoke_counts_and_summed_energy_exactly_equal":all(a["counts"]==b["counts"] and a["deposited_energy_GeV"]==b["deposited_energy_GeV"] for a,b in zip(stock["smoke"]["results"],candidate["smoke"]["results"])),
        "native_validation":native,"material_ray_comparison":rays,"xml_preservation":variant,"partition_proofs":partitions,
        "reporter_sha256":sha(__file__),"limitations":["Legacy assembly export remains the default; this is an opt-in placement investigation.",
            "Added navigation boundaries can change shower histories; no response-equivalence or digitization claim.",
            "Seven persisted electrons are startup/ID smoke evidence only.","Twelve-worker initialization and the previously failed MT pilot are separate configurations.",
            "The post-run-initialize interval includes gun/output UI setup, physics and navigation preparation; voxelization is not separately timed.",
            "Large XML, ROOT, inventories and full logs are local ignored artifacts; hashes and exact reproduction commands are retained."]}
    workspace=str(Path(__file__).resolve().parents[3])
    def portable(x):
        if isinstance(x,str): return x.replace(workspace,"$WORKSPACE")
        if isinstance(x,list): return [portable(v) for v in x]
        if isinstance(x,dict): return {portable(k):portable(v) for k,v in x.items()}
        return x
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(portable(result),indent=2,allow_nan=False)+"\n")
    print(json.dumps({"stock_first_event_seconds":stock["first_event_begin_seconds"],"candidate_first_event_seconds":candidate["first_event_begin_seconds"],"speedup_observed":result["first_event_speedup_observed"]},indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--work",type=Path,required=True)
    p.add_argument("--stock",default="stock-smoke1");p.add_argument("--candidate",default="candidate-smoke2")
    p.add_argument("--output",type=Path,required=True);collect(p.parse_args())
