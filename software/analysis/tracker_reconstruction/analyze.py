"""Independent all-event reconstruction metrics; no native matcher omissions."""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
import math
from pathlib import Path
import numpy as np
import species


def interval(k,n,z=1.):
    if not n: return None
    p=k/n;den=1+z*z/n;centre=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0.,centre-half),min(1.,centre+half)]


def rate(k,n):
    return {"numerator":int(k),"denominator":int(n),"value":k/n if n else None,
            "wilson68":interval(k,n),"wilson95":interval(k,n,1.959963984540054),
            "zero_one_sided95_upper":1-0.05**(1/n) if n and not k else None}


def ambiguity_shared_max(tracks):
    """Replay ACTS GreedyAmbiguityResolution's final shared-measurement test.

    Usage is a set of tracks per source link, while a track's measurement
    vector can contain repeated links. Check all native survivors, before any
    analysis quality selection; a quality cut must not hide solver truncation.
    """
    links=[[s["measurement"] for s in t["states"] if s["inlier"]] for t in tracks]
    usage=Counter(i for indices in links for i in set(indices))
    return max((sum(usage[i]>1 for i in indices) for indices in links),default=0)


def classify_event(row,sensors,config):
    if len(row["generated"])!=1: raise ValueError("Benchmark requires exactly one generated primary")
    primary=row["generated"][0];pid=tuple(primary["id"])
    truth={tuple(x) for x in row["simulated_ids"]}|{pid}
    ms={m["index"]:m for m in row["measurements"]}
    associated=defaultdict(set)
    for m in ms.values():
        for p in m["particles"]: associated[tuple(p)].add(m["index"])
    primary_ms=associated[pid]
    primary_sensors={ms[i]["geometry_id"] for i in primary_ms}
    groups={tuple(sensors[ms[i]["geometry_id"]][:2]) for i in primary_ms if sensors[ms[i]["geometry_id"]][0]<=3}
    match=config["matching"];quality=config["quality"]
    def pure_seed(seed):
        indices=set(seed["measurements"])
        layers={tuple(sensors[ms[i]["geometry_id"]][:2]) for i in indices}
        return len(layers)>=3 and bool(indices) and indices<=primary_ms
    result={"event":row["event"],"eta":primary["eta"],"pt":primary["pt"],"charge":primary["charge"],
        "simhits":row["simhits"],"measurements":len(ms),"primary_measurements":len(primary_ms),
        "primary_sensors":len(primary_sensors),"pixel_groups":len(groups),
        "reconstructable":int(len(primary_sensors)>=match["reconstructable_measurements"] and len(groups)>=match["reconstructable_pixel_groups"]),
        "reconstructable4":int(len(primary_sensors)>=match["reconstructable_measurements"] and len(groups)>=max(4,match["reconstructable_pixel_groups"])),
        "spacepoints":len(row["spacepoints"]),"seeds":len(row["seeds"]),"estimated_seeds":len(row["estimated_seeds"]),
        "pure_seed":int(any(map(pure_seed,row["seeds"]))),
        "pure_estimated_seed":int(any(map(pure_seed,row["estimated_seeds"]))),"truth":primary["truth"]}
    for stage in ("ckf","ambi"):
        candidates=[];matches=defaultdict(list);fake=0;secondary=0;bad=0
        for t in row[stage]:
            indices=set(t["measurements"])
            if (not t["reference"] or len(indices)<quality["minimum_measurements"] or
                not t.get("covariance_positive_definite",True) or
                t["chi2"] is None or not math.isfinite(t["chi2"]) or t["ndf"]<=0 or
                len(t["parameters"])!=6 or len(t["variance"])!=6 or
                any(x is None or not math.isfinite(x) for x in t["parameters"]) or
                any(x is None or not math.isfinite(x) or x<=0 for x in t["variance"])):
                bad+=1;continue
            if len(indices)!=t["nMeasurements"]: raise ValueError("Track inlier count differs from unique source links")
            candidates.append(t)
            contributions=Counter(tuple(p) for i in indices for p in ms[i]["particles"])
            if contributions:
                winner,count=sorted(contributions.items(),key=lambda x:(-x[1],x[0]))[0]
                if (winner in truth and count/len(indices)>=match["purity"] and
                    count/len(associated[winner])>=match["completeness"]):
                    matches[winner].append(t)
                    if winner!=pid: secondary+=1
                    continue
            fake+=1
        primary_tracks=matches[pid]
        representative=min(primary_tracks,key=lambda t:(-len(t["measurements"]),t["chi2"]/max(t["ndf"],1),t["index"])) if primary_tracks else None
        duplicates=sum(max(0,len(ts)-1) for ts in matches.values())
        result[stage]={"raw":len(row[stage]),"accepted":len(candidates),"quality_rejected":bad,
            "matched":int(bool(primary_tracks)),"primary_candidates":len(primary_tracks),
            "secondary":secondary,"fake":fake,"duplicates":duplicates,"duplicate_event":int(duplicates>0),
            "fake_event":int(fake>0),"representative":representative,
            "wrong_charge":int(bool(representative) and representative["parameters"][4]*primary["truth"][4]<0)}
    return result


def bootstrap_ratio(numerator,denominator):
    n=np.asarray(numerator);d=np.asarray(denominator)
    if not d.sum():return None
    if not n.sum():return [0.,0.]  # Degenerate bootstrap; event-level exact bound is reported separately.
    rng=np.random.default_rng(1729);ratios=[]
    for _ in range(2000):
        indices=rng.integers(0,len(n),len(n));total=d[indices].sum()
        if total:ratios.append(n[indices].sum()/total)
    return np.quantile(ratios,[.025,.975]).tolist()


def summarize(events,stage):
    n=len(events);counts={k:sum(e[stage][k] for e in events) for k in
        ("raw","accepted","quality_rejected","matched","primary_candidates","secondary","fake","duplicates","duplicate_event","fake_event","wrong_charge")}
    result={"events":n,"counts":counts,"efficiency":rate(counts["matched"],n)}
    for label,key in (("conditional", "reconstructable"),("conditional4","reconstructable4")):
        subset=[e for e in events if e[key]]
        result[label]=rate(sum(e[stage]["matched"] for e in subset),len(subset))
    for key in ("fake_event","duplicate_event"):
        result[key]=rate(counts[key],n)
    result["wrong_charge"]=rate(counts["wrong_charge"],counts["matched"])
    for key in ("fake","duplicates","secondary"):
        result[key+"_candidate_fraction"]={"numerator":counts[key],"denominator":counts["accepted"],
            "value":counts[key]/counts["accepted"] if counts["accepted"] else None,
            "event_bootstrap95":bootstrap_ratio([e[stage][key] for e in events],[e[stage]["accepted"] for e in events])}
    return result


def analyze(directory,output):
    directory=Path(directory);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    report=json.loads((directory/"run-report.json").read_text())
    if report["outcome"]!="completed":raise ValueError("Native campaign did not complete")
    for name,digest in report["output_sha256"].items():
        if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=digest:
            raise ValueError("Recorded native output changed: "+name)
    config=report["campaign"]
    native_sensors={s["geometry_id"]:s for s in json.loads((directory/"native-report.json").read_text())["sensors"]}
    sensors={gid:(s["ids"]["system"],s["ids"]["layer"]) for gid,s in native_sensors.items()}
    widths=json.loads((directory/"error-table.json").read_text())
    variances={(g["volume"],g["index"]):g["sigma_mm"]**2 for g in widths["groups"]}
    events=[];sample=hashlib.sha256();systems=Counter();dimensions=Counter();marginals=0;max_sp_error=0.
    identity=report["gbts_statistics"].get("particle_configuration")
    generated_pdgs=Counter();secondary_pdgs=Counter();primary_diagnostics={};outcomes=Counter();processes=Counter();ambiguity_maxima={}
    if identity and identity["name"]!=config["particle"]:raise ValueError("Species report/campaign mismatch")
    with gzip.open(directory/"events.jsonl.gz","rt") as stream:
        for line in stream:
            row=json.loads(line)
            if config.get("species_extension"):
                maximum=ambiguity_shared_max(row["ambi"])
                ambiguity_maxima[row["event"]]=maximum
                if maximum>=config["ambiguity"]["maximum_shared_hits"]:
                    raise ValueError(f"Ambiguity resolution did not converge in event {row['event']}: {maximum} shared measurements")
            if identity:
                fraction,secondaries=species.audit_event(row,identity)
                secondary_pdgs.update(secondaries)
                generated_pdgs[row["generated"][0]["pdg"]]+=1
                primary=next((p for p in row["simulated_particles"] if p["id"]==row["generated"][0]["id"]),None)
                primary_diagnostics[row["event"]]=(fraction,primary)
                if primary:outcomes[primary["outcome"]]+=1
                processes.update(p["process"] for p in row["simulated_particles"] if p["id"]!=row["generated"][0]["id"])
            if row.get("ckf_input_measurements",len(row["measurements"]))!=len(row["measurements"]):
                raise ValueError("CKF did not receive the complete measurement collection")
            for m in row["measurements"]:
                system=sensors[m["geometry_id"]][0];systems[system]+=1;dimensions[m["dimension"]]+=1
                if m["dimension"]!=(1 if system>=6 else 2):raise ValueError("Measurement dimension changed")
                for index,var in enumerate(m["variance"]):
                    expected=variances[((m["geometry_id"]>>56)&255,index)]
                    if var!=expected:raise ValueError("Frozen native double variance changed")
                    marginals+=1
            for point in row["spacepoints"]:
                if len(point["measurements"])!=1:raise ValueError("Pixel point must have one source measurement")
                m=row["measurements"][point["measurements"][0]];s=native_sensors[m["geometry_id"]]
                if s["ids"]["system"]>3:raise ValueError("Nonpixel space point in GBTS")
                expected=np.asarray(s["center_mm"])+m["values"][0]*np.asarray(s["u"])+m["values"][1]*np.asarray(s["v"])
                error=float(np.linalg.norm(expected-np.asarray(point["position"])))
                max_sp_error=max(max_sp_error,error)
                if not np.array_equal(np.asarray(expected,dtype=np.float32).astype(float),np.asarray(point["position"])):
                    raise ValueError("Space point differs from float32 measured local-to-global position")
            sample.update(json.dumps({k:row[k] for k in ("event","generated","measurements","spacepoints")},sort_keys=True,separators=(",",":")).encode())
            events.append(classify_event(row,sensors,config))
    events.sort(key=lambda e:e["event"])
    if len(events)!=report["events"] or len({e["event"] for e in events})!=len(events):raise ValueError("Lost or duplicate native event")
    edges=config["tuning_protocol"]["eta_edges"]
    result={"schema_version":1,"status":"PROTOTYPE","profile":report["profile"],"phase":report["phase"],
        "parameter_units":["mm","mm","rad","rad","GeV^-1","ct_mm"],"native_time_mm_per_ns":299.792458,
        "pt_GeV":report["pt_GeV"],"events":len(events),"seed":report["seed"],"wall_seconds":report["wall_seconds"],
        "sequencer_seconds":report["gbts_statistics"].get("sequencer_seconds"),
        "native_source_revision":report["source_revision"],"sample_sha256":sample.hexdigest(),
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "run_report_sha256":hashlib.sha256((directory/"run-report.json").read_bytes()).hexdigest(),
        "events_sha256":hashlib.sha256((directory/"events.jsonl.gz").read_bytes()).hexdigest(),
        "stages":{stage:summarize(events,stage) for stage in ("ckf","ambi")},
        "stage_counts":{k:sum(e[k] for e in events) for k in ("simhits","measurements","primary_measurements","spacepoints","seeds","estimated_seeds","pure_seed","pure_estimated_seed","reconstructable","reconstructable4")},
        "measurement_audit":{"systems":dict(systems),"dimensions":dict(dimensions),"checked_marginals":marginals,"frozen_native_double_variances":True,"max_measured_spacepoint_position_error_mm":max_sp_error},
        "eta_edges":edges,"eta_bins":[]}
    for lo,hi in zip(edges,edges[1:]):
        subset=[e for e in events if lo<=e["eta"]<hi or (hi==edges[-1] and e["eta"]==hi)]
        result["eta_bins"].append({"eta":[lo,hi],"events":len(subset),
            "stages":{stage:summarize(subset,stage) for stage in ("ckf","ambi")},
            "pure_seed":rate(sum(e["pure_seed"] for e in subset),len(subset))})
    arrays={k:np.asarray([e[k] for e in events]) for k in ("event","eta","pt","charge","primary_measurements","pixel_groups","reconstructable","reconstructable4","seeds","estimated_seeds","pure_seed","pure_estimated_seed","truth")}
    if identity:
        result["particle_configuration"]=identity
        result["simulation"]=config["simulation"]
        result["species_audit"]={"generated_pdgs":dict(generated_pdgs),"secondary_pdgs":dict(secondary_pdgs),
            "all_native_hypotheses_verified":True,"primary_outcomes":dict(outcomes),"secondary_creator_processes":dict(processes),
            "primary_simulated_entries":sum(p is not None for _,p in primary_diagnostics.values()),
            "outcome_codes":{"0":"Alive","1":"KilledInteraction","2":"KilledVolumeExit","3":"KilledTime","4":"KilledSecondaryParticle"}}
        result["species_analysis_sha256"]=hashlib.sha256(Path(species.__file__).read_bytes()).hexdigest()
        arrays["primary_final_p_fraction"]=np.asarray([primary_diagnostics[e["event"]][0] for e in events])
        for label,key,default in (("outcome","outcome",-1),("final_ct_mm","final_ct_mm",np.nan),
            ("path_X0","path_X0",np.nan),("path_L0","path_L0",np.nan),
            ("final_position_mm","final_position_mm",[np.nan]*3)):
            arrays["primary_"+label]=np.asarray([primary_diagnostics[e["event"]][1].get(key,default)
                if primary_diagnostics[e["event"]][1] is not None else default for e in events])
    if ambiguity_maxima:
        arrays["ambiguity_max_shared_measurements"]=np.asarray([ambiguity_maxima[e["event"]] for e in events])
        result["ambiguity_audit"]={"all_native_survivors_converged":True,
            "maximum_shared_measurements":int(arrays["ambiguity_max_shared_measurements"].max()),
            "strict_upper_bound":config["ambiguity"]["maximum_shared_hits"],
            "maximum_iterations":config["ambiguity"]["maximum_iterations"]}
    for stage in ("ckf","ambi"):
        for key in ("matched","accepted","fake","duplicates","secondary","wrong_charge"):
            arrays[stage+"_"+key]=np.asarray([e[stage][key] for e in events])
        reco=[];variance=[];hits=[]
        for e in events:
            t=e[stage]["representative"]
            reco.append(t["parameters"] if t else [np.nan]*6);variance.append(t["variance"] if t else [np.nan]*6)
            hits.append(t["nMeasurements"] if t else 0)
        arrays[stage+"_reco"]=np.asarray(reco);arrays[stage+"_variance"]=np.asarray(variance);arrays[stage+"_inliers"]=np.asarray(hits)
        residual=arrays["truth"]-arrays[stage+"_reco"]
        residual[:,2]=(residual[:,2]+math.pi)%(2*math.pi)-math.pi
        arrays[stage+"_residual"]=residual;arrays[stage+"_pull"]=residual/np.sqrt(arrays[stage+"_variance"])
        valid=residual[np.isfinite(residual).all(axis=1)]
        result["stages"][stage]["residual_summary"]={"entries":len(valid),
            "mean":np.mean(valid,axis=0).tolist() if len(valid) else None,
            "population_sd":np.std(valid,axis=0).tolist() if len(valid) else None,
            "central68_halfwidth":((np.quantile(valid,.84,axis=0)-np.quantile(valid,.16,axis=0))/2).tolist() if len(valid) else None}
    (output/"summary.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    np.savez_compressed(output/"events.npz",**arrays)
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("directory",type=Path);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();r=analyze(a.directory,a.output)
    print(json.dumps({"profile":r["profile"],"pt":r["pt_GeV"],"events":r["events"],"seed_events":r["stage_counts"]["pure_seed"],"ambi":r["stages"]["ambi"]["counts"]}))
