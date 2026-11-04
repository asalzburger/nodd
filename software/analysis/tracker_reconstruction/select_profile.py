"""Predeclared tuning selection; held-out results are never inputs."""
import argparse
import hashlib
import gzip
import json
from pathlib import Path
import numpy as np


def select(directory,output,campaign):
    directory=Path(directory);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    config=json.loads(Path(campaign).read_text());profiles=config["profiles"];pts=config["pt_GeV"]
    data={};files={}
    for path in sorted([*directory.glob("pt*/*/summary.json"),*directory.glob("pt*/*/summary.json.gz")]):
        summary=json.loads(gzip.decompress(path.read_bytes()) if path.suffix==".gz" else path.read_bytes())
        if summary["phase"]!="tuning":raise ValueError("Selection may only consume tuning data")
        key=(summary["profile"],summary["pt_GeV"])
        if key in data:raise ValueError("Duplicate tuning case")
        data[key]=summary;files[key]=path
    if set(data)!={(p,pt) for p in profiles for pt in pts}:raise ValueError("Incomplete declared scan")
    for pt in pts:
        if len({data[p,pt]["sample_sha256"] for p in profiles})!=1:
            raise ValueError("Profiles did not use identical generated/smeared samples")
        if len({data[p,pt]["events"] for p in profiles})!=1:raise ValueError("Unequal event denominators")
    table=[]
    for profile in profiles:
        cases=[data[profile,pt] for pt in pts]
        efficiency=[x["stages"]["ambi"]["efficiency"]["value"] for x in cases]
        counts={key:sum(x["stages"]["ambi"]["counts"][key] for x in cases) for key in
                ("accepted","matched","fake_event","fake","duplicates","secondary","wrong_charge")}
        row={"profile":profile,"efficiency_by_pt":dict(zip(map(str,pts),efficiency)),
             "worst_efficiency":min(efficiency),"mean_efficiency":sum(efficiency)/len(efficiency),
             "events":sum(x["events"] for x in cases),"counts":counts,
             "sequencer_seconds":sum(x["sequencer_seconds"] for x in cases),
             "configuration":profiles[profile]}
        row["selection_key"]=[-row["worst_efficiency"],-row["mean_efficiency"],counts["fake_event"],
                              counts["duplicates"],row["sequencer_seconds"]]
        table.append(row)
    table.sort(key=lambda r:r["selection_key"])
    selected=table[0]["profile"]
    def dominates(a,b):
        x=[-a["worst_efficiency"],-a["mean_efficiency"],a["counts"]["fake_event"],a["counts"]["duplicates"]]
        y=[-b["worst_efficiency"],-b["mean_efficiency"],b["counts"]["fake_event"],b["counts"]["duplicates"]]
        return all(u<=v for u,v in zip(x,y)) and any(u<v for u,v in zip(x,y))
    paired={}
    for pt in pts:
        a=np.load(files[selected,pt].with_name("events.npz"));b=np.load(files["control",pt].with_name("events.npz"))
        if not np.array_equal(a["event"],b["event"]) or not np.array_equal(a["truth"],b["truth"]):raise ValueError("Paired sample mismatch")
        am=a["ambi_matched"].astype(bool);bm=b["ambi_matched"].astype(bool)
        paired[str(pt)]={"both":int(np.sum(am&bm)),"selected_only":int(np.sum(am&~bm)),
                         "control_only":int(np.sum(~am&bm)),"neither":int(np.sum(~am&~bm))}
    result={"schema_version":1,"status":"PROTOTYPE","selected_profile":selected,
            "selection_rule":config["tuning_protocol"]["selection_order"],
            "ranking":table,"pareto_profiles":[a["profile"] for a in table if not any(dominates(b,a) for b in table)],
            "paired_control_comparison":paired,"validation_seed":config["sample_seeds"]["validation"],
            "validation_events_per_pt":config["tuning_protocol"]["validation_events_per_pt"],
            "campaign_sha256":hashlib.sha256(Path(campaign).read_bytes()).hexdigest(),
            "analysis_inputs_sha256":{str(p.relative_to(directory)).removesuffix(".gz"):
                hashlib.sha256(gzip.decompress(p.read_bytes()) if p.suffix==".gz" else p.read_bytes()).hexdigest() for p in files.values()},
            "selection_source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "limits":"500 events/pT tune; scan ranking does not establish statistically significant differences between near-tied profiles. No held-out input."}
    (output/"selection.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    frozen=dict(config);frozen["selected_profile"]=selected;frozen["selection_sha256"]=hashlib.sha256((output/"selection.json").read_bytes()).hexdigest()
    (output/"selected-campaign.json").write_text(json.dumps(frozen,indent=2)+"\n")
    print(json.dumps({"selected_profile":selected,"pareto_profiles":result["pareto_profiles"],"ranking":[{k:r[k] for k in ("profile","efficiency_by_pt","counts","sequencer_seconds")} for r in table]}))
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--campaign",type=Path,default=Path(__file__).with_name("campaign.json"))
    a=p.parse_args();select(a.input,a.output,a.campaign)
