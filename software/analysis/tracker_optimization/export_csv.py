#!/usr/bin/env python3
"""Export reviewable scalar tables from a loss-accounted comparison."""
import argparse
import csv
import gzip
import json
from pathlib import Path


def write(path,rows):
    with path.open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    args=p.parse_args();x=json.loads(gzip.decompress(args.input.read_bytes()));args.output.mkdir(parents=True,exist_ok=True)
    coverage=[];performance=[];changes=[];pulls=[]
    for label,s in x["samples"].items():
        for axis,rows in [("global",[s["global"]]),*((k,s[k]) for k in ("eta","abs_eta","phi"))]:
            for row in rows:
                for stage,d in row["stages"].items():
                    coverage.append({"case":label,"pt_GeV":s["pt_GeV"],"axis":axis,"low":row.get("low"),"high":row.get("high"),
                        "generated":row["generated"],"fit_tracks":row["fit_tracks"],"stage":stage,"sum":d["sum"],
                        "ge10":d["ge10"]["value"],"ge10_low95":d["ge10"]["low"],"ge10_high95":d["ge10"]["high"]})
                for q,d in row["quantities"].items():
                    for kind,stats in d.items():
                        performance.append({"case":label,"pt_GeV":s["pt_GeV"],"axis":axis,"low":row.get("low"),"high":row.get("high"),
                            "quantity":q,"observable":kind,**{k:stats[k] for k in ("entries","nonfinite","mean","median","std","rms","width68","width68_se")}})
        for q,h in s["pulls"].items():
            pulls.append({"case":label,"pt_GeV":s["pt_GeV"],"quantity":q,**{k:h[k] for k in
                ("entries","nonfinite","mean","std","width68","minimum","maximum","abs_gt3","outside_core","underflow","overflow")}})
    for label,rows in x["paired_comparisons"].items():
        for i,row in enumerate(rows):
            for q,d in row["quantities"].items():
                ci=d["ratio_bootstrap95"] or [None,None]
                changes.append({"case":label,"region":"global" if i==0 else "abs_eta","low":row["low"],"high":row["high"],
                    "generated":row["generated"],"quantity":q,"baseline_width68":d["baseline_width68"],"candidate_width68":d["candidate_width68"],
                    "ratio":d["ratio"],"ratio_low95":ci[0],"ratio_high95":ci[1],"coverage_change":row["coverage_change"],
                    "coverage_change_se":row["coverage_change_se"],"common_survivors":d["common_survivors"]})
    for name,rows in (("coverage",coverage),("performance",performance),("paired-changes",changes),("pulls",pulls)):
        if rows:write(args.output/(name+".csv"),rows)


if __name__=="__main__":main()
