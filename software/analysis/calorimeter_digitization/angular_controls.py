"""Render the unbinned response populations underlying ECAL10K width points.

No fits, re-calibration, cuts or transport reruns. Histogram bins are only a
display; the annotations are the unchanged, unbinned published moments.
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np

from angular_sample import sha, save
from angular_analyze import bin_index, folded_phi


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--events",type=Path,required=True)
    p.add_argument("--summary",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=json.loads(args.summary.read_text())
    if sha(args.events)!=result["readback"]["event_summary_sha256"]:
        raise ValueError("Event ledger differs from the published analysis")
    rows=sorted([json.loads(line) for line in args.events.read_text().splitlines()],key=lambda r:r["event"])
    if len(rows)!=result["events"] or len({r["event"] for r in rows})!=len(rows):
        raise ValueError("Incomplete/repeated event identities")
    response=np.array([r["response"] for r in rows]);eta=np.array([r["eta"] for r in rows]);phi=np.array([r["phi"] for r in rows])
    if not np.all(np.isfinite(response)) or np.any(response<0):raise ValueError("Invalid response")
    for r in rows:
        if not math.isclose(r["response"],r["signal_GeV"]/r["energy_GeV"],rel_tol=1e-13):
            raise ValueError("Response/energy inconsistency")
    args.output.mkdir(parents=True,exist_ok=True)
    metadata=args.output/"response-histograms.json"
    if metadata.exists():raise ValueError("Choose fresh control output; evidence is not overwritten")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False,"savefig.dpi":170})
    # A common range and identical histogram edges for all 20 populations.
    # Rounded upward for readable ticks; all events, including zeros, must fit.
    upper=max(.5,math.ceil(response.max()*100*2)/2)
    histogram_edges=np.linspace(0,upper,41)
    output=dict(events=len(rows),source_summary_sha256=sha(args.summary),
      source_event_ledger_sha256=sha(args.events),producer_sha256=sha(__file__),
      definition="R=sum(raw sensitive-silicon deposits)/primary total energy",
      estimator="Unbinned sample SD(R), ddof=1; fractional width=SD(R)/mean(R); no Gaussian fit",
      histogram_edges_response_percent=histogram_edges.tolist(),projections={})
    for name,projection in result["projections"].items():
        edges=np.asarray(projection["edges"])
        category=bin_index(np.abs(eta) if name=="abs_eta" else folded_phi(phi),edges)
        fig,axes=plt.subplots(5,2,figsize=(11.8,13.8),layout="constrained",sharex=True)
        records=[]
        for i,(ax,reference) in enumerate(zip(axes.flat,projection["bins"])):
            values=response[category==i]
            mean=float(values.mean());sd=float(values.std(ddof=1));width=sd/mean
            if len(values)!=reference["events"] or np.count_nonzero(values==0)!=reference["zero_events"]:
                raise ValueError("Population count differs from published bin")
            for actual,key in ((mean,"mean_response"),(sd,"sample_sd"),(width,"fractional_width")):
                if not math.isclose(actual,reference[key],rel_tol=1e-12,abs_tol=1e-15):
                    raise ValueError(f"Unbinned moment differs: {name}:{i}:{key}")
            counts,_=np.histogram(values*100,bins=histogram_edges)
            if counts.sum()!=len(values):raise ValueError("Histogram dropped an event")
            ax.stairs(counts,histogram_edges,color="#6e7200",fill=True,facecolor="#cccc00",alpha=.85,linewidth=.9)
            ax.axvline(mean*100,color="#30372b",ls="--",lw=1.3)
            ax.set_xlim(0,upper);ax.set_ylim(0,max(counts.max()*1.35,1));ax.grid(axis="y",alpha=.17);ax.set_axisbelow(True)
            factor=180/math.pi if name=="folded_phi" else 1
            label=(rf"${edges[i]:.1f}\leq|\eta|<{edges[i+1]:.1f}$" if name=="abs_eta" else
                   rf"${edges[i]*factor:.2f}\leq\phi_{{fold}}<{edges[i+1]*factor:.2f}^\circ$")
            if name=="abs_eta" and i==9:label=rf"${edges[i]:.1f}\leq|\eta|\leq{edges[i+1]:.1f}$"
            ax.set_title(label,loc="left",fontsize=10,pad=7)
            annotation=(f"N = {len(values):,} · zero = {reference['zero_events']}\n"
                        f"mean = {mean*100:.3f}% · s = {sd*100:.3f}%\n"
                        f"s / mean = {width*100:.2f}%")
            ax.text(.98,.95,annotation,transform=ax.transAxes,ha="right",va="top",fontsize=8.4,
                    bbox=dict(facecolor="white",edgecolor="none",alpha=.86,pad=3))
            if i%2==0:ax.set_ylabel("Electrons / bin")
            if i>=8:ax.set_xlabel(r"Raw silicon response $R=E_{Si}/E_{true}$ [%]")
            records.append(dict(bin=i,low=reference["low"],high=reference["high"],events=len(values),
                                zero_events=reference["zero_events"],counts=counts.tolist(),
                                mean_response=mean,sample_sd=sd,fractional_width=width))
        title="Ten |η| populations" if name=="abs_eta" else "Ten signed sector-folded φ populations"
        fig.suptitle(f"nODD · {title}\nUnbinned moments underlying the published width points",fontsize=15)
        fig.supxlabel("All events retained · Dashed line: mean · s: sample standard deviation (ddof = 1)\n"
                      "No Gaussian fit · 10–80 GeV spectrum · Histogram bins do not enter the width calculation",fontsize=9)
        for extension in ("png","pdf"):fig.savefig(args.output/f"response-distributions-{name}.{extension}")
        plt.close(fig)
        output["projections"][name]=dict(angular_edges=projection["edges"],angular_unit=projection["unit"],bins=records)
    save(metadata,output)
    print(f"Matched all 20 published unbinned moments and histogram totals; {len(rows)} events per projection.")


if __name__=="__main__":main()
