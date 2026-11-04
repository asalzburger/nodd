#!/usr/bin/env python3
"""Plot native sensitive positions, reference versus a prepared candidate."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def coordinates(path):
    g=json.loads(path.read_text());s=g["sensors"]
    xyz=np.array([x["center_mm"] for x in s]);system=np.array([x["ids"]["system"] for x in s])
    return np.abs(xyz[:,2]),np.hypot(xyz[:,0],xyz[:,1]),system


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline",type=Path,required=True);p.add_argument("--candidate",type=Path,required=True)
    p.add_argument("--label",required=True);p.add_argument("--output",type=Path,required=True)
    args=p.parse_args();base=coordinates(args.baseline);candidate=coordinates(args.candidate)
    fig=plt.figure(figsize=(14,9),layout="constrained");grid=fig.add_gridspec(2,2)
    axes=[fig.add_subplot(grid[0,:]),fig.add_subplot(grid[1,0]),fig.add_subplot(grid[1,1])]
    for ax in axes:
        ax.scatter(base[0],base[1],s=1,color=".65",alpha=.25,label="reference sensitive centres",rasterized=True)
        for lo,hi,color,name in [(1,3,"#df7725","pixel"),(4,5,"#269d88","short strip"),(6,7,"#7564b4","long strip")]:
            mask=(candidate[2]>=lo)&(candidate[2]<=hi)
            ax.scatter(candidate[0][mask],candidate[1][mask],s=1.5,color=color,alpha=.6,label=args.label+" "+name,rasterized=True)
        ax.set(xlabel="|z| [mm]",ylabel="r [mm]");ax.grid(alpha=.2)
    axes[0].set(xlim=(0,3350),ylim=(0,1200),title="Native ACTS/DD4hep sensitive positions; passive structures omitted")
    axes[0].axhline(1140,color="k",ls=":",lw=.8,label="fixed tracker host radius")
    axes[0].legend(loc="upper left",markerscale=4,fontsize=9,ncols=3)
    axes[1].set(xlim=(0,3350),ylim=(0,240),title="Pixel barrel and disks")
    axes[2].set(xlim=(0,650),ylim=(20,240),title="Pixel barrel detail")
    for ax in axes[1:]:
        ax.axhline(232,color="k",ls=":",lw=.8)
        ax.axhline(27.8,color="k",lw=.8)
    fig.suptitle("PROTOTYPE · "+args.label+" · fixed envelopes and module types · symmetric signed endcaps")
    args.output.mkdir(parents=True,exist_ok=True)
    for suffix in ("png","pdf"):fig.savefig(args.output/("layout."+suffix),dpi=170)
    plt.close(fig)


if __name__=="__main__":main()
