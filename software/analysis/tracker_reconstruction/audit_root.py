"""Cross-check optional native ROOT persistence against independent event arrays."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import awkward as ak
import numpy as np
import uproot


def audit(native,analysis,output):
    native,analysis=Path(native),Path(analysis);result={}
    reports=sorted(native.glob("*/*/run-report.json"))
    if not reports:raise ValueError("No native ROOT cases found; require a nonempty campaign")
    for report_path in reports:
        case=report_path.parent;relative=case.relative_to(native);r=json.loads(report_path.read_text())
        if r["outcome"]!="completed":raise ValueError("ROOT audit requires completed native run")
        summary=json.loads((analysis/relative/"summary.json").read_text());a=np.load(analysis/relative/"events.npz")
        widths=json.loads((case/"error-table.json").read_text());checked=0
        with uproot.open(case/"measurements.root") as f:
            m=f["measurements"].arrays(["volume_id","var_loc0","var_loc1","clus_size"],library="np")
        if len(m["volume_id"])!=summary["stage_counts"]["measurements"]:raise ValueError("ROOT measurement count differs from audit")
        for group in widths["groups"]:
            actual=m["var_loc"+str(group["index"])][m["volume_id"]==group["volume"]]
            if not np.all(actual==np.float32(group["sigma_mm"]**2)):raise ValueError("Persisted ROOT variance changed")
            checked+=len(actual)
        if np.any(m["clus_size"]!=0):raise ValueError("Gaussian digitization unexpectedly has geometric clusters")
        stages={}
        for stage in ("ckf","ambi"):
            with uproot.open(case/("tracksummary_"+stage+".root")) as f:
                fields=["event_nr","track_nr",*["e"+x+"_fit" for x in ("LOC0","LOC1","PHI","THETA","QOP","T")],*["err_e"+x+"_fit" for x in ("LOC0","LOC1","PHI","THETA","QOP","T")]]
                t=f["tracksummary"].arrays(fields,library="ak")
            if len(t)!=summary["events"]:raise ValueError("ROOT dropped zero-track events")
            count=int(ak.sum(ak.num(t["track_nr"],axis=1)))
            if count!=summary["stages"][stage]["counts"]["raw"]:raise ValueError("ROOT candidate count differs from native audit")
            rows={int(e):i for i,e in enumerate(ak.to_numpy(t["event_nr"]))};parameters=0
            for i,event in enumerate(a["event"]):
                if not a[stage+"_matched"][i]:continue
                j=rows[int(event)]
                # CKF can contain duplicates even when ambiguity removes them.
                # Join the complete persisted perigee+uncertainty tuple within
                # the same event, rather than assuming the first candidate.
                target=np.asarray(a[stage+"_reco"][i],dtype=np.float32)
                sigma=np.asarray(np.sqrt(a[stage+"_variance"][i]),dtype=np.float32)
                matches=[]
                for candidate in range(len(t["track_nr"][j])):
                    values=np.asarray([t["e"+x+"_fit"][j][candidate] for x in ("LOC0","LOC1","PHI","THETA","QOP","T")])
                    errors=np.asarray([t["err_e"+x+"_fit"][j][candidate] for x in ("LOC0","LOC1","PHI","THETA","QOP","T")])
                    if np.array_equal(values,target) and np.array_equal(errors,sigma):matches.append(candidate)
                if not matches:raise ValueError("Native representative perigee+sigma tuple absent from ROOT event")
                candidate=matches[0]
                for k,name in enumerate(("LOC0","LOC1","PHI","THETA","QOP","T")):
                    if t["e"+name+"_fit"][j][candidate]!=target[k]:raise ValueError("ROOT perigee differs from native audit")
                    if t["err_e"+name+"_fit"][j][candidate]!=sigma[k]:raise ValueError("ROOT fitted uncertainty differs from native audit")
                    parameters+=1
            stages[stage]={"events":len(t),"candidates":count,"matched_parameter_marginals":parameters,"exact_float32_perigee_and_sigma_match":True}
        result[str(relative)]={"measurement_rows":len(m["volume_id"]),"checked_variance_marginals":checked,"exact_float32_variance_match":True,"stages":stages,
            "root_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in case.glob("*.root")}}
    payload={"schema_version":1,"status":"PASS","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"cases":result}
    Path(output).write_text(json.dumps(payload,indent=2)+"\n")
    print("PASS:",len(result),"native ROOT cases; all event/measurement/candidate counts and persisted covariance marginals agree")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--native",type=Path,required=True);p.add_argument("--analysis",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args();audit(a.native,a.analysis,a.output)
