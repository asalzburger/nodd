"""Replay full-acceptance reconstruction performance from retained event arrays."""
import argparse
import json
import gzip
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PTS=(1,5,10,100)
COLORS=("#1565c0","#00897b","#e69f00","#b2182b")
PARAMETERS=(r"$d_0$ [µm]",r"$z_0$ [µm]",r"$\phi$ [mrad]",r"$\theta$ [mrad]",r"$q/p$ [GeV$^{-1}$]",r"$t_0$ [ns]")
SCALES=np.asarray([1000.,1000.,1000.,1000.,1.,1/299.792458])


def summary(path):
    path=Path(path)
    if path.exists():return json.loads(path.read_text())
    return json.loads(gzip.decompress(path.with_suffix(".json.gz").read_bytes()))


def save(fig,output,name):
    fig.savefig(output/(name+".png"),dpi=170,bbox_inches="tight")
    fig.savefig(output/(name+".pdf"),bbox_inches="tight")
    plt.close(fig)


def plot(data,output):
    data=Path(data);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    selected={pt:(summary(data/"selected"/f"pt{pt}"/"summary.json"),
                  np.load(data/"selected"/f"pt{pt}"/"events.npz")) for pt in PTS}
    control={pt:(summary(data/"control"/f"pt{pt}"/"summary.json"),
                 np.load(data/"control"/f"pt{pt}"/"events.npz")) for pt in PTS}
    fig,axes=plt.subplots(2,2,figsize=(12,8),sharex=True,sharey=True)
    for ax,pt in zip(axes.flat,PTS):
        for label,collection,color in (("Selected GBTS",selected,"#1565c0"),("Initial control",control,"#888888")):
            s,_=collection[pt];bins=s["eta_bins"];x=[sum(b["eta"])/2 for b in bins]
            r=[b["stages"]["ambi"]["efficiency"] for b in bins]
            y=np.asarray([b["value"] for b in r]);bounds=np.asarray([b["wilson95"] for b in r])
            ax.errorbar(x,y,yerr=[y-bounds[:,0],bounds[:,1]-y],fmt="o-",ms=3,lw=1,color=color,label=label,capsize=2)
        s,_=selected[pt];r=[b["stages"]["ambi"]["conditional"] for b in s["eta_bins"]]
        ax.plot(x,[b["value"] if b["value"] is not None else np.nan for b in r],"--",color="#00897b",label="Selected, reconstructable")
        ax.set_title(f"pT = {pt} GeV; {s['events']:,} muons");ax.set_ylim(0,1.04);ax.set_xlim(-4,4);ax.grid(alpha=.2)
        ax.set_xlabel("Generated η");ax.set_ylabel("Primary reconstruction efficiency")
    axes[0,0].legend(fontsize=8,loc="lower left")
    fig.suptitle("nODD balanced tracker · Fatras · Gaussian digitization · 3 T\nHeld-out single muons; ≥7 inliers; 95% Wilson intervals")
    fig.tight_layout();save(fig,output,"efficiency")
    fig,axes=plt.subplots(2,3,figsize=(14,8))
    tails={}
    for pt,color in zip(PTS,COLORS):
        _,arrays=selected[pt];pulls=arrays["ambi_pull"];valid=arrays["ambi_matched"].astype(bool)
        tails[str(pt)]=[]
        for i,ax in enumerate(axes.flat):
            values=pulls[valid,i];finite=values[np.isfinite(values)]
            counts,edges=np.histogram(finite,bins=np.linspace(-6,6,97));width=edges[1]-edges[0]
            ax.stairs(counts/(len(finite)*width),edges,color=color,lw=1.4,label=f"{pt} GeV")
            x=np.linspace(-6,6,301);ax.plot(x,np.exp(-x*x/2)/np.sqrt(2*np.pi),color="black",alpha=.35,lw=.8)
            ax.set_title(PARAMETERS[i].split(" [")[0]);ax.set_xlabel("(truth − reco) / σreco");ax.set_ylabel("Density per generated matched entry");ax.set_xlim(-6,6);ax.grid(alpha=.15)
            tails[str(pt)].append({"parameter":i,"entries":len(finite),"underflow":int(np.sum(finite< -6)),"overflow":int(np.sum(finite>6)),"abs_gt3":int(np.sum(np.abs(finite)>3)),"abs_gt5":int(np.sum(np.abs(finite)>5)),"mean":float(np.mean(finite)),"sd":float(np.std(finite)),"min":float(np.min(finite)),"max":float(np.max(finite))})
    axes[0,0].legend(fontsize=9)
    fig.suptitle("Full integrated pull distributions · deterministic primary representative\nDisplay −6…6; full tails retained; time has no measured timing constraint")
    fig.tight_layout();save(fig,output,"pulls")
    fig,axes=plt.subplots(2,3,figsize=(14,8))
    for pt,color in zip(PTS,COLORS):
        s,arrays=selected[pt];eta=arrays["eta"];valid=arrays["ambi_matched"].astype(bool);edges=np.asarray(s["eta_edges"])
        for i,ax in enumerate(axes.flat):
            x=[];y=[]
            for lo,hi in zip(edges[:-1],edges[1:]):
                values=arrays["ambi_residual"][(eta>=lo)&(eta<hi)&valid,i]*SCALES[i]
                x.append((lo+hi)/2);y.append((np.quantile(values,.84)-np.quantile(values,.16))/2 if len(values)>=10 else np.nan)
            ax.plot(x,y,"o-",ms=2.5,color=color,label=f"{pt} GeV");ax.set_xlabel("Generated η");ax.set_ylabel("Central 68% half-width, "+PARAMETERS[i]);ax.grid(alpha=.2)
            ax.set_yscale("log")
    axes[0,0].legend(fontsize=9)
    fig.suptitle("Held-out perigee residual resolution · all matched primaries\nHalf-width (q84 − q16)/2; no residual or pull cuts; time prior dominated")
    fig.tight_layout();save(fig,output,"resolution-eta")
    for quantity in ("residual","pull"):
        fig,axes=plt.subplots(2,3,figsize=(14,8))
        for (lo,hi),color in zip(((0,1.5),(1.5,2.5),(2.5,4.)),COLORS):
            for i,ax in enumerate(axes.flat):
                values=[]
                for pt in PTS:
                    _,a=selected[pt];mask=(np.abs(a["eta"])>=lo)&(np.abs(a["eta"])<hi)&a["ambi_matched"].astype(bool)
                    r=a["ambi_"+quantity][mask,i]*(SCALES[i] if quantity=="residual" else 1.)
                    values.append((np.quantile(r,.84)-np.quantile(r,.16))/2)
                ax.plot(PTS,values,"o-",ms=4,color=color,label=f"{lo:g} ≤ |η| < {hi:g}")
                ax.set_xscale("log");ax.set_xlabel("Generated pT [GeV]");ax.grid(alpha=.2)
                ax.set_ylabel(("Central 68% half-width, "+PARAMETERS[i]) if quantity=="residual" else ("Pull central 68% half-width, "+PARAMETERS[i].split(" [")[0]))
                if quantity=="residual":ax.set_yscale("log")
                else:ax.axhline(1,color="black",ls="--",lw=.8)
        axes[0,0].legend(fontsize=8)
        fig.suptitle("Held-out "+("residual resolution" if quantity=="residual" else "pull width")+" versus transverse momentum\nNo residual/pull cuts; time prior dominated")
        fig.tight_layout();save(fig,output,"resolution-pt" if quantity=="residual" else "pull-width-pt")
    fig,axes=plt.subplots(2,3,figsize=(14,8))
    for pt,color in zip(PTS,COLORS):
        s,a=selected[pt];edges=s["eta_edges"]
        for i,ax in enumerate(axes.flat):
            widths=[]
            for lo,hi in zip(edges[:-1],edges[1:]):
                values=a["ambi_pull"][(a["eta"]>=lo)&(a["eta"]<hi)&a["ambi_matched"].astype(bool),i]
                widths.append((np.quantile(values,.84)-np.quantile(values,.16))/2 if len(values)>=10 else np.nan)
            ax.plot([(lo+hi)/2 for lo,hi in zip(edges[:-1],edges[1:])],widths,"o-",ms=3,color=color,label=f"{pt} GeV")
            ax.axhline(1,color="black",ls="--",lw=.8);ax.set_xlabel("Generated η");ax.set_ylabel("Pull central 68% half-width, "+PARAMETERS[i].split(" [")[0]);ax.grid(alpha=.2)
    axes[0,0].legend(fontsize=8);fig.suptitle("Held-out pull widths versus η · no pull cuts\nTime prior dominated without timing measurements")
    fig.tight_layout();save(fig,output,"pull-width-eta")
    fig,axes=plt.subplots(1,3,figsize=(14,4))
    for pt,color in zip(PTS,COLORS):
        s,a=selected[pt];eta=a["eta"];valid=a["ambi_matched"].astype(bool);reco=a["ambi_reco"]
        pt_reco=np.abs(np.sin(reco[:,3])/reco[:,4]);delta=(a["pt"]-pt_reco)/a["pt"]
        x=[];widths=[];coverage=[];fake=[]
        for b in s["eta_bins"]:
            lo,hi=b["eta"];mask=(eta>=lo)&(eta<hi);values=delta[mask&valid]
            x.append((lo+hi)/2);widths.append((np.quantile(values,.84)-np.quantile(values,.16))/2 if len(values)>=10 else np.nan)
            coverage.append(float(np.mean(a["ambi_inliers"][mask&valid])) if np.any(mask&valid) else np.nan)
            fake.append(b["stages"]["ambi"]["fake_event"]["zero_one_sided95_upper"] or b["stages"]["ambi"]["fake_event"]["wilson95"][1])
        axes[0].plot(x,widths,"o-",ms=3,color=color,label=f"{pt} GeV")
        axes[1].plot(x,coverage,"o-",ms=3,color=color)
        axes[2].plot(x,np.asarray(fake)*100,"o-",ms=3,color=color)
    for ax in axes:ax.set_xlabel("Generated η");ax.grid(alpha=.2)
    axes[0].set_ylabel("Central 68% half-width of ΔpT/pT");axes[0].set_yscale("log");axes[0].legend(fontsize=8)
    axes[1].set_ylabel("Mean inlier measurements / matched track");axes[1].axhline(10,color="black",ls="--",lw=.8)
    axes[2].set_ylabel("Fake-event 95% upper bound [%]")
    fig.suptitle("Single-muon momentum, hit coverage and fake-event bounds\nZero observed fakes retain finite limits; no pile-up claim")
    fig.tight_layout();save(fig,output,"momentum-hits-fakes")
    (output/"pull-tails.json").write_text(json.dumps(tails,indent=2,allow_nan=False)+"\n")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--data",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args();plot(a.data,a.output)
