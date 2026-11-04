#!/usr/bin/env python3
"""Offline integrity audit linking reduced comparisons to portable native reports."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

ROOT=Path(__file__).resolve().parents[3]


def load(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def require(condition,message):
    if not condition:raise ValueError(message)


def audit(data,reports,prefix):
    source=subprocess.check_output(["git","-C",str(ROOT),"show",data["source_revision"]+
        ":software/analysis/tracker_optimization/analyze.py"])
    require(hashlib.sha256(source).hexdigest()==data["source_sha256"],"Reduced analysis source identity differs")
    native={r["case"]:r for r in reports["reports"]}
    for label,s in data["samples"].items():
        record=native[prefix+"/"+label];r=record["report"]
        require(record["source_report_sha256"]==s["run_report_sha256"],"Native report fingerprint differs")
        require(r["outcome"]=="completed" and r["events"]==s["events"],"Incomplete native denominator")
        require(r["campaign"]["field_Bz_T"]==3 and r["simulation"]=="fatras","Field/backend differs")
        require(r["compiled_ACTS_source_revision"]=="355ea68493b326956756c9386d2fd9eaf9328568","Compiled ACTS pin differs")
        for name,digest in r["executed_source_sha256"].items():
            raw=subprocess.check_output(["git","-C",str(ROOT),"show",r["scientific_input_revision"]+":"+name])
            require(hashlib.sha256(raw).hexdigest()==digest,"Executed native source differs: "+name)
        for name,digest in s["source_files"].items():
            require(r["output_sha256"][name]==digest,"Reduced/native ROOT fingerprint differs")
        for key,value in s["counts"].items():require(r["counts"][key]==value,"Reduced/native stage count differs")
        require(s["global"]["generated"]==s["events"],"Global generated denominator differs")
        for axis in ("eta","abs_eta","phi"):
            require(sum(x["generated"] for x in s[axis])==s["events"],"Profile denominator differs")
        require(sum(x["generated"] for x in s["eta_phi_coverage"])==s["events"],"Joint eta/phi denominator differs")
        for row in [s["global"],*s["eta"],*s["abs_eta"],*s["phi"]]:
            for stage,values in row["stages"].items():
                counts=values["hit_counts"]
                require(sum(counts.values())==row["generated"],"Hit distribution lost generated events")
                good=sum(n for k,n in counts.items() if int(k)>=10)
                fraction=good/row["generated"] if row["generated"] else None
                require(values["ge10"]["value"]==fraction,"Ten-hit fraction differs from hit histogram")
                require(values["sum"]==sum(int(k)*n for k,n in counts.items()),"Hit stage sum differs")
        for category,edge_name in (("pulls","pull_edges"),("residuals","residual_edges")):
            for q,h in s.get(category,{}).items():
                edges=data[edge_name][q]
                require(len(h["counts"])+1==len(edges) and np.all(np.diff(edges)>0),"Invalid histogram edges")
                require(sum(h["counts"])+h["underflow"]+h["overflow"]==h["entries"],"Histogram count closure failed")
                require(h["entries"]+h["nonfinite"]==s["events"],"Histogram lost generated/missing-fit accounting")
                require(h["underflow"]==h["overflow"]==0,"Observed finite tail escaped histogram")
        require(s["measurement_error_audit"]["status"]=="PASS","Missing measurement variance audit")
        for carrier in r["material_transport"]:
            require(max(abs(v) for v in carrier["relative_inventory_residuals"].values())<=3e-6,"Material inventory closure failed")
        manifest_count=r["native_decoration"]["map_key_count"]
        require(manifest_count==len(r["material_transport"]),"Native material carrier count differs")
        if r["digitization_model"]=="gaussian":
            require(r["native_boundary_contract"]["effective_max_retries"]==10,"Gaussian retry contract changed")
    return len(data["samples"])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data",type=Path,required=True);p.add_argument("--reports",type=Path,required=True)
    p.add_argument("--prefix",required=True,help="phase/response")
    args=p.parse_args();n=audit(load(args.data),load(args.reports),args.prefix)
    print(f"PASS: {n} comparisons, exact native/source/output identities, complete denominators and full histograms")


if __name__=="__main__":main()
