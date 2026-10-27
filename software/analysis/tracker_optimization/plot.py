#!/usr/bin/env python3
"""Render comparative coverage, residual resolution and full pull distributions."""
import argparse
import gzip
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def save(fig, output, name):
    fig.savefig(output/(name+".png"),dpi=160)
    fig.savefig(output/(name+".pdf"))
    plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    data=json.loads(gzip.decompress(args.input.read_bytes()))
    samples=data["samples"]
    variants=list(dict.fromkeys(label.rpartition("-pt")[0] for label in samples))
    pts=sorted(set(s["pt_GeV"] for s in samples.values()))
    args.output.mkdir(parents=True,exist_ok=True)
    colors={v:plt.get_cmap("tab10")(i) for i,v in enumerate(variants)}
    plt.rcParams.update({"font.size":10,"axes.grid":True,"grid.alpha":.2})
    fig,axes=plt.subplots(1,len(pts),figsize=(14,4),squeeze=False,layout="constrained")
    for ax,pt in zip(axes[0],pts):
        for variant in variants:
            s=samples.get(f"{variant}-pt{pt:g}")
            if not s:continue
            rows=s["eta"]; x=np.array([(r["low"]+r["high"])/2 for r in rows])
            y=np.array([r["stages"]["created"]["ge10"]["value"] or 0 for r in rows])
            low=np.array([r["stages"]["created"]["ge10"]["low"] or 0 for r in rows])
            hi=np.array([r["stages"]["created"]["ge10"]["high"] or 0 for r in rows])
            ax.errorbar(x,100*y,yerr=100*np.maximum(0,np.array([y-low,hi-y])),label=variant,color=colors[variant],lw=1.1)
        ax.set(xlabel="generated η",ylabel="≥10 physical measurements [%]",title=f"pT = {pt:g} GeV",ylim=(0,103))
    axes[0,0].legend(fontsize=8)
    fig.suptitle("PROTOTYPE · Fatras, truth tracking, constant 3 T · all generated muons · pointwise 95% intervals")
    save(fig,args.output,"coverage_eta")

    for observable,title in (("width68","Central 68.27% half-width"),("std","Full residual standard deviation")):
        fig,axes=plt.subplots(4,len(pts),figsize=(14,12),squeeze=False,layout="constrained")
        for row,(q,unit,scale) in enumerate((("d0","μm",1000),("z0","μm",1000),("pt_relative","%",100),("q_over_pt_relative","%",100))):
            for ax,pt in zip(axes[row],pts):
                for variant in variants:
                    s=samples.get(f"{variant}-pt{pt:g}")
                    if not s:continue
                    rows=s["abs_eta"]; x=[(r["low"]+r["high"])/2 for r in rows]
                    y=[r["quantities"][q]["residual"][observable] for r in rows]
                    se=[r["quantities"][q]["residual"][observable+"_se"] for r in rows]
                    ax.errorbar(x,np.array(y,dtype=float)*scale,yerr=np.array(se,dtype=float)*scale,
                                label=variant,color=colors[variant],marker=".",lw=1)
                ax.set(xlabel="|generated η|",ylabel=f"{q} [{unit}]",title=f"pT = {pt:g} GeV",yscale="log")
        axes[0,0].legend(fontsize=8)
        fig.suptitle("PROTOTYPE · "+title+" · no residual/quality cuts · conditional on fit")
        save(fig,args.output,"resolution_"+observable)

    if "residual_edges" in data:
        for view in ("core","full"):
            fig,axes=plt.subplots(2,2,figsize=(12,8),layout="constrained")
            for ax,(q,limit) in zip(axes.flat,(("d0",.25),("z0",5.),("pt_relative",.5),("q_over_pt_relative",.5))):
                edges=np.array(data["residual_edges"][q])
                for label,s in samples.items():
                    variant=label.rpartition("-pt")[0];pt=s["pt_GeV"];h=s["residuals"][q]
                    density=np.array(h["counts"])/(max(1,h["entries"])*np.diff(edges))
                    ax.stairs(density,edges,label=f"{variant}, {pt:g} GeV",color=colors[variant],
                              linestyle={1:"-",10:"--",100:":"}.get(pt,"-"),lw=1)
                ax.set(xlabel="fit − truth [mm]" if q in ("d0","z0") else "signed fractional residual",ylabel="density",title=q,yscale="log")
                if view=="core":ax.set_xlim(-limit,limit)
                else:ax.set_xscale("symlog",linthresh=limit)
            axes.flat[0].legend(fontsize=7)
            fig.suptitle("PROTOTYPE · full all-η residual distributions · no tail cuts")
            save(fig,args.output,"residuals_"+view)

    for view in ("core","full"):
        fig,axes=plt.subplots(2,4,figsize=(16,8),layout="constrained")
        for ax,q in zip(axes.flat,("d0","z0","phi","theta","q_over_p","time","pt_relative")):
            edges=np.array(data["pull_edges"][q])
            for label,s in samples.items():
                variant=label.rpartition("-pt")[0]; pt=s["pt_GeV"]
                h=s["pulls"][q]
                density=np.array(h["counts"])/(max(1,h["entries"])*np.diff(edges))
                style={1:"-",10:"--",100:":"}.get(pt,"-")
                ax.stairs(density,edges,label=f"{variant}, {pt:g} GeV",color=colors[variant],linestyle=style,lw=1)
            ax.set(xlabel="(truth − fit) / fitted σ",ylabel="density",title=q,yscale="log",ylim=(1e-7,2))
            if view=="core":ax.set_xlim(-5,5)
            else:ax.set_xscale("symlog",linthresh=5)
        axes.flat[-1].axis("off")
        handles,labels=axes.flat[0].get_legend_handles_labels()
        axes.flat[-1].legend(handles,labels,loc="center",fontsize=8)
        fig.suptitle("PROTOTYPE · all η · full finite-entry normalization · time is prior dominated")
        save(fig,args.output,"pulls_"+view)


if __name__=="__main__":main()
