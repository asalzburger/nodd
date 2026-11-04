"""Numerical headline, charge/tail and coverage diagnostics from retained arrays."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np


def report(data,output):
    data=Path(data);results={}
    for pt in (1,5,10,100):
        directory=data/"selected"/f"pt{pt}";s=json.loads(gzip.decompress((directory/"summary.json.gz").read_bytes()));a=np.load(directory/"events.npz")
        c=json.loads(gzip.decompress((data/"control"/f"pt{pt}"/"summary.json.gz").read_bytes()))
        matched=a["ambi_matched"].astype(bool);reco=a["ambi_reco"]
        delta=(a["pt"]-np.abs(np.sin(reco[:,3])/reco[:,4]))/a["pt"]
        central=matched&(np.abs(a["eta"])<.5)
        width=lambda x:((np.quantile(x,.84,axis=0)-np.quantile(x,.16,axis=0))/2).tolist()
        results[str(pt)]={"events":s["events"],"efficiency":s["stages"]["ambi"]["efficiency"],
            "control_efficiency":c["stages"]["ambi"]["efficiency"],"conditional_efficiency":s["stages"]["ambi"]["conditional"],
            "fake_candidate_fraction":s["stages"]["ambi"]["fake_candidate_fraction"],
            "fake_event_incidence":s["stages"]["ambi"]["fake_event"],"wrong_charge":s["stages"]["ambi"]["wrong_charge"],
            "duplicates_before_ambiguity":s["stages"]["ckf"]["counts"]["duplicates"],
            "duplicates_after_ambiguity":s["stages"]["ambi"]["counts"]["duplicates"],
            "ge10_inliers_all_generated":{"numerator":int(np.sum(a["ambi_inliers"]>=10)),"denominator":s["events"],"value":float(np.mean(a["ambi_inliers"]>=10))},
            "matched_relative_pt_abs_gt50pct":int(np.sum(matched&(np.abs(delta)>.5))),
            "matched_relative_pt_abs_gt100pct":int(np.sum(matched&(np.abs(delta)>1.))),
            "central_abs_eta_lt0p5":{"matched":int(central.sum()),"d0_z0_central68_um":width(a["ambi_residual"][central,:2]*1000),"relative_pt_central68":width(delta[central])},
            "pull_mean":np.mean(a["ambi_pull"][matched],axis=0).tolist(),
            "pull_population_sd":np.std(a["ambi_pull"][matched],axis=0).tolist(),
            "pull_central68_halfwidth":width(a["ambi_pull"][matched]),
            "pull_abs_gt5":np.sum(np.abs(a["ambi_pull"][matched])>5,axis=0).tolist()}
    payload={"schema_version":1,"status":"PROTOTYPE","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"parameter_order":["d0","z0","phi","theta","q/p","t0"],"pt_GeV":results,
             "uncertainty":"Per-momentum independent-event intervals; paired momenta/control and repeated tuning cases are not pooled into an independent-trial count",
             "tail_policy":"No residual/pull/charge cuts; time prior dominated; all raw numerical tails retained"}
    Path(output).write_text(json.dumps(payload,indent=2,allow_nan=False)+"\n")
    return payload


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--data",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args();report(a.data,a.output)
