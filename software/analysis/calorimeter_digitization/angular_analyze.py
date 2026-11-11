"""Audit unordered DDSim events and plot spectrum-averaged angular response widths."""
import argparse
import json
import math
from pathlib import Path
import subprocess

import numpy as np

from angular_sample import ROOT, sha, save

PERIOD=math.pi/8
ETA_EDGES=np.linspace(0,3,11)
PHI_EDGES=np.linspace(-PERIOD/2,PERIOD/2,11)


def folded_phi(phi):
    return (np.asarray(phi)+PERIOD/2)%PERIOD-PERIOD/2


def bin_index(values, edges):
    values=np.asarray(values)
    if np.any(values<edges[0]-1e-12) or np.any(values>edges[-1]+1e-12):
        raise ValueError("Angular value outside analysis range")
    return np.clip(np.searchsorted(edges,values,side="right")-1,0,len(edges)-2)


def fractional_width(values):
    values=np.asarray(values,dtype=float)
    if len(values)<2 or values.mean()<=0:return None
    return float(values.std(ddof=1)/values.mean())


def audit(args):
    import edm4hep
    import ROOT as PyROOT
    from podio import root_io
    run=args.run.resolve();sample=args.sample.resolve()
    receipt=json.loads((run/"receipt.json").read_text())
    manifest=json.loads((sample/"sample.json").read_text())
    if receipt["exit_code"] or receipt["disk_abort"] or receipt["sample_sha256"]!=sha(sample/"sample.json"):
        raise ValueError("Incomplete or changed transport")
    if manifest["input_sha256"]!=sha(sample/"particles.HEPEvt") or manifest["truth_sha256"]!=sha(sample/"truth-input.jsonl"):
        raise ValueError("Changed input primary records")
    expected=[json.loads(l) for l in (sample/"truth-input.jsonl").read_text().splitlines()]
    expected_ids=set(range(receipt["skip"],receipt["skip"]+receipt["events"]))
    workers=[json.loads(p.read_text()) for p in sorted((run/"audit").glob("worker-*.json"))]
    tids={w["thread_id"] for w in workers}
    if receipt["threads"]>1 and tids!=set(range(receipt["threads"])):raise ValueError(f"Worker set differs: {tids}")
    if len(workers)!=receipt["threads"] or sum(w["events"] for w in workers)!=receipt["events"]:
        raise ValueError("Worker event totals differ")
    for w in workers:
        if w["status"]!="complete" or w["maximum_abs_magnetic_field_tesla"]!=0 or set(w["sensitive_si"])!={"BARREL","EDGE"}:
            raise ValueError("Incomplete worker native audit")
        if not any(r["mm"]==[.7]*4 for r in w["region_cuts"]):raise ValueError("Worker cuts differ")
        if any(r["max_step_mm"]!=5 or r["Birks_mm_per_MeV"]!=0 for r in w["sensitive_si"].values()):
            raise ValueError("Worker ECAL response/step policy differs")
    output=run/"event-summary.jsonl"
    if output.exists():raise ValueError("Refusing event-summary overwrite")
    seen=set();cells={"BARRELHits":0,"EDGEHits":0};maximum_errors=dict(momentum_GeV=0.,energy_GeV=0.,eta=0.,phi=0.)
    with output.open("w") as stream:
        for frame in root_io.Reader(str(run/"events.root")).get("events"):
            header,=frame.get("EventHeader");event=int(header.getEventNumber())
            if int(header.getRunNumber())!=0 or event not in expected_ids or event in seen:raise ValueError("Unexpected/repeated event identity")
            seen.add(event);primary,=[p for p in frame.get("MCParticles") if p.getGeneratorStatus()==1]
            if primary.getPDG()!=11:raise ValueError("Not a single electron primary")
            v=primary.getVertex()
            if (v.x,v.y,v.z)!=(0,0,0):raise ValueError("Primary vertex not at origin")
            p=primary.getMomentum();momentum=[float(p.x),float(p.y),float(p.z)];energy=float(primary.getEnergy())
            pt=math.hypot(p.x,p.y);eta=math.asinh(p.z/pt);phi=math.atan2(p.y,p.x);ref=expected[event]
            errors=dict(momentum_GeV=max(abs(a-b) for a,b in zip(momentum,ref["momentum_GeV"])),
                        energy_GeV=abs(energy-ref["energy_GeV"]),eta=abs(eta-ref["eta"]),
                        phi=abs((phi-ref["phi"]+math.pi)%(2*math.pi)-math.pi))
            if errors["momentum_GeV"]>1e-7 or errors["energy_GeV"]>1e-7 or errors["eta"]>1e-9 or errors["phi"]>1e-9:
                raise ValueError(f"Saved primary differs from input event {event}: {errors}")
            if not 10<=energy<=80 or not -3<=eta<=3:raise ValueError("Saved primary outside requested phase space")
            for k,error in errors.items():maximum_errors[k]=max(maximum_errors[k],error)
            energies={};counts={}
            for name,system in (("BARRELHits",8),("EDGEHits",9)):
                ids=set();deposits=[]
                for hit in frame.get(name):
                    cell=int(hit.getCellID());deposit=float(hit.getEnergy())
                    if cell in ids or cell&255!=system or not math.isfinite(deposit) or deposit<=0:
                        raise ValueError("Invalid persisted ECAL hit")
                    ids.add(cell);deposits.append(deposit)
                energies[name]=math.fsum(deposits);counts[name]=len(ids);cells[name]+=len(ids)
            signal=math.fsum(energies.values())
            stream.write(json.dumps(dict(event=event,energy_GeV=energy,eta=eta,phi=phi,
                 signal_GeV=signal,response=signal/energy,energies_GeV=energies,counts=counts),separators=(",",":"))+"\n")
    if seen!=expected_ids:raise ValueError("Incomplete persisted event set")
    f=PyROOT.TFile.Open(str(run/"events.root"),"READ")
    if not f or f.IsZombie() or f.Get("events").GetEntries()!=len(seen):raise ValueError("ROOT event count mismatch")
    compression=dict(algorithm=int(f.GetCompressionAlgorithm()),level=int(f.GetCompressionLevel()));f.Close()
    proof=dict(status="PASS",events=len(seen),event_ids=dict(min=min(seen),max=max(seen)),
       identity_order="verified by event ID; physical output order unrestricted",cells_by_collection=cells,
       maximum_input_errors=maximum_errors,compression=compression,root_sha256=sha(run/"events.root"),
       event_summary_sha256=sha(output),receipt_sha256=sha(run/"receipt.json"),
       audit_sha256=sha(__file__),worker_events={str(w["thread_id"]):w["events"] for w in workers},
       workers=workers)
    save(run/"readback.json",proof);print(json.dumps({k:v for k,v in proof.items() if k!="workers"},indent=2))


def summarize(values,energy):
    mean=float(values.mean()) if len(values) else None
    return dict(events=len(values),energy_mean_GeV=float(energy.mean()) if len(energy) else None,
      energy_range_GeV=[float(energy.min()),float(energy.max())] if len(energy) else None,
      mean_response=mean,sample_sd=float(values.std(ddof=1)) if len(values)>1 else None,
      fractional_width=fractional_width(values),zero_events=int(np.count_nonzero(values==0)),
      quantiles=dict(zip(["q16","q50","q84"],map(float,np.quantile(values,[.16,.50,.84])))) if len(values) else None)


def analyze(args):
    run=args.run.resolve();proof=json.loads((run/"readback.json").read_text());receipt=json.loads((run/"receipt.json").read_text())
    if sha(run/"receipt.json")!=proof["receipt_sha256"]:raise ValueError("Changed transport receipt after readback")
    if sha(run/"event-summary.jsonl")!=proof["event_summary_sha256"]:raise ValueError("Changed event summary")
    rows=sorted([json.loads(l) for l in (run/"event-summary.jsonl").read_text().splitlines()],key=lambda r:r["event"])
    if len(rows)!=proof["events"]:raise ValueError("Event ledger count mismatch")
    eta=np.array([r["eta"] for r in rows]);phi=np.array([r["phi"] for r in rows]);energy=np.array([r["energy_GeV"] for r in rows]);response=np.array([r["response"] for r in rows])
    categories=[bin_index(np.abs(eta),ETA_EDGES),bin_index(folded_phi(phi),PHI_EDGES)]
    rng=np.random.default_rng(args.bootstrap_seed);width_boot=np.full((args.bootstrap,20),np.nan);mean_boot=np.full_like(width_boot,np.nan)
    for b in range(args.bootstrap):
        index=rng.integers(len(rows),size=len(rows));sampled=response[index]
        for axis,category in enumerate(categories):
            counts=np.bincount(category[index],minlength=10)
            sums=np.bincount(category[index],weights=sampled,minlength=10)
            squares=np.bincount(category[index],weights=sampled**2,minlength=10)
            means=np.divide(sums,counts,out=np.full(10,np.nan),where=counts>0)
            variance=np.divide(squares-sums*means,counts-1,out=np.full(10,np.nan),where=counts>1)
            widths=np.divide(np.sqrt(np.maximum(variance,0)),means,out=np.full(10,np.nan),where=means>0)
            width_boot[b,axis*10:(axis+1)*10]=widths;mean_boot[b,axis*10:(axis+1)*10]=means
    projections={}
    for axis,(name,edges) in enumerate((("abs_eta",ETA_EDGES),("folded_phi",PHI_EDGES))):
        bins=[]
        for i in range(10):
            selected=categories[axis]==i;entry=summarize(response[selected],energy[selected]);entry.update(low=float(edges[i]),high=float(edges[i+1]))
            for key,boot in (("fractional_width",width_boot),("mean_response",mean_boot)):
                values=boot[:,10*axis+i];bad=int(np.count_nonzero(~np.isfinite(values)))
                entry[key+"_bootstrap_undefined"]=bad
                entry[key+"_ci95"]=[float(x) for x in np.quantile(values,[.025,.975])] if not bad else None
            bins.append(entry)
        projections[name]=dict(edges=edges.tolist(),unit="rad" if axis else "dimensionless",bins=bins)
    controls={}
    for name,categories_control in [("eta_sign",np.where(eta<0,0,1)),("sector",np.floor((phi+PERIOD/2)%(2*math.pi)/PERIOD).astype(int))]:
        controls[name]={str(i):summarize(response[categories_control==i],energy[categories_control==i]) for i in sorted(set(categories_control.tolist()))}
    result=dict(status="PROTOTYPE",observable="sample SD(R)/mean(R), R=sum(raw sensitive-silicon ECAL deposits)/primary total energy",
       interpretation="Spectrum-averaged raw visible-response width, including gaps/leakage/angular variation; not intrinsic reconstructed energy resolution",
       events=len(rows),source_revision=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
       bootstrap=dict(replicates=args.bootstrap,seed=args.bootstrap_seed,resampling="whole-event joint resampling across both projections",interval="95% percentile"),
       projections=projections,controls=controls,
       width_covariance_order=[f"{name}:{i}" for name in projections for i in range(10)],
       width_covariance=np.cov(width_boot,rowvar=False,ddof=1).tolist() if np.all(np.isfinite(width_boot)) else None,
       execution={k:receipt[k] for k in ("events","threads","seed","wall_seconds","cpu_seconds","peak_rss_bytes","output_bytes","free_bytes_after","steering_sha256","runner_sha256","geometry_library_sha256","audit_library_sha256")},
       readback={k:v for k,v in proof.items() if k!="workers"},analysis_sha256=sha(__file__))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists():raise ValueError("Refusing summary overwrite")
    save(args.output,result);plot(result,args.output.parent)
    print(f"Summarized {len(rows)} events, {args.bootstrap} bootstrap replicates; wrote {args.output}")


def plot(result,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patheffects as pe
    plt.rcParams.update({"font.size":11,"axes.spines.top":False,"axes.spines.right":False,"savefig.dpi":180})
    fig,axes=plt.subplots(1,2,figsize=(12.6,5.4),layout="constrained")
    for axis,(name,projection) in zip(axes,result["projections"].items()):
        bins=projection["bins"];factor=180/math.pi if name=="folded_phi" else 1
        x=np.array([(b["low"]+b["high"])/2*factor for b in bins]);y=np.array([b["fractional_width"]*100 if b["fractional_width"] is not None else np.nan for b in bins])
        low=np.array([b["fractional_width_ci95"][0]*100 if b["fractional_width_ci95"] else np.nan for b in bins]);high=np.array([b["fractional_width_ci95"][1]*100 if b["fractional_width_ci95"] else np.nan for b in bins])
        axis.vlines(x,low,high,color="#343b22",linewidth=1.4)
        line,=axis.plot(x,y,"o-",color="#cccc00",markeredgecolor="#454500",markersize=6,linewidth=2,label="Si–W ECAL · raw deposits")
        line.set_path_effects([pe.Stroke(linewidth=2.8,foreground="#777744"),pe.Normal()])
        axis.set_xlim(projection["edges"][0]*factor,projection["edges"][-1]*factor);axis.set_ylim(bottom=0)
        axis.grid(alpha=.2);axis.set_axisbelow(True)
        axis.set_xlabel(r"$|\eta|$" if name=="abs_eta" else r"Signed sector-folded $\phi$ [deg]")
        axis.set_ylabel(r"$\sigma(R)/\langle R\rangle$ [%]")
        axis.set_title("Pseudorapidity dependence" if name=="abs_eta" else "Azimuth within one 22.5° sector",fontsize=12,pad=12)
        if name=="folded_phi":axis.axvline(0,color="#8d9885",ls=":",lw=1)
        axis.text(.02,.97,"n/bin: "+" · ".join(str(b["events"]) for b in bins),transform=axis.transAxes,va="top",fontsize=7.1,color="#586052")
    axes[0].legend(loc="lower right",frameon=False,fontsize=9)
    fig.suptitle(f"nODD ECAL · {result['events']:,} electrons · uniform E = 10–80 GeV",fontsize=16)
    fig.supxlabel("R = deposited silicon energy / primary energy · 95% whole-event bootstrap intervals\nSpectrum-averaged visible-response width; includes geometric losses, not calibrated energy resolution",fontsize=9)
    for extension in ("png","pdf"):fig.savefig(out/f"angular-resolution.{extension}")
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12.6,4.8),layout="constrained")
    for axis,(name,projection) in zip(axes,result["projections"].items()):
        factor=180/math.pi if name=="folded_phi" else 1;bins=projection["bins"]
        x=[(b["low"]+b["high"])/2*factor for b in bins];y=[b["mean_response"]*100 if b["mean_response"] is not None else np.nan for b in bins]
        low=[b["mean_response_ci95"][0]*100 if b["mean_response_ci95"] else np.nan for b in bins];high=[b["mean_response_ci95"][1]*100 if b["mean_response_ci95"] else np.nan for b in bins]
        axis.vlines(x,low,high,color="#343b22");axis.plot(x,y,"o-",color="#cccc00",markeredgecolor="#454500")
        axis.set_xlabel(r"$|\eta|$" if name=="abs_eta" else r"Signed sector-folded $\phi$ [deg]");axis.set_ylabel("Mean raw silicon response [%]")
        axis.grid(alpha=.2);axis.set_ylim(bottom=0)
    fig.suptitle("Response-scale control · all valid events, including zero response",fontsize=14)
    fig.supxlabel("No angular calibration or response cuts applied · error bars: 95% whole-event bootstrap",fontsize=9)
    for extension in ("png","pdf"):fig.savefig(out/f"mean-response.{extension}")
    plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest="stage",required=True)
    a=s.add_parser("audit");a.add_argument("--run",type=Path,required=True);a.add_argument("--sample",type=Path,required=True)
    a=s.add_parser("analyze");a.add_argument("--run",type=Path,required=True);a.add_argument("--output",type=Path,required=True)
    a.add_argument("--bootstrap",type=int,default=5000);a.add_argument("--bootstrap-seed",type=int,default=1335000)
    args=p.parse_args();globals()[args.stage](args)


if __name__=="__main__":main()
