#!/usr/bin/env python3
"""Finite pixel patch straight-ray coverage screen; never a tracking result.

Unchanged strip counts are borrowed from a stated reference Fatras sample.
Pixel counts are computed from XML patch rectangles, without material, curvature
or energy loss. This proxy selects schedules to test with native Fatras.
"""
import argparse
import gzip
import json
import math
from pathlib import Path
import sys
import subprocess
import xml.etree.ElementTree as ET

import awkward as ak
import numpy as np
import uproot

sys.path.insert(0,str(Path(__file__).resolve().parents[3]/"software/analysis/truth_tracking"))
from export_profiles import event_indices, flat, sha256


def number(node,key,default=0.):
    return float(node.get(key,str(default)).removesuffix("*mm").removesuffix("*rad"))


def disk_patches(disk):
    values=[]
    for m in disk.findall("module"):
        s=m.find("sensor")
        ux,uy,vx,vy=(number(m,k) for k in ("ux","uy","vx","vy"))
        for patch in s.findall("patch"):
            u=number(s,"u")+number(patch,"u");v=number(s,"v")+number(patch,"v")
            values.append((number(m,"x")+u*ux+v*vx,number(m,"y")+u*uy+v*vy,
                           number(m,"z"),ux,uy,vx,vy,number(patch,"width")/2,number(patch,"length")/2))
    return np.array(values)


def disk_hits(patches,z,eta,phi):
    hits=np.zeros(len(eta),dtype=np.int16)
    if not len(eta):return hits
    # Avoid a gigantic event x patch scratch matrix on full reference samples.
    for start in range(0,len(eta),256):
        e=eta[start:start+256,None];p=phi[start:start+256,None]
        with np.errstate(divide="ignore",invalid="ignore"):
            r=(z+patches[None,:,2])/np.sinh(e)
        x=r*np.cos(p)-patches[None,:,0];y=r*np.sin(p)-patches[None,:,1]
        u=x*patches[None,:,3]+y*patches[None,:,4]
        v=x*patches[None,:,5]+y*patches[None,:,6]
        hits[start:start+len(e)]=np.sum((r>0)&(np.abs(u)<=patches[None,:,7])&(np.abs(v)<=patches[None,:,8]),axis=1)
    return hits


def barrel_hits(pixel,controls,eta,phi):
    result=np.zeros(len(eta),dtype=np.int16)
    for layer in pixel.findall("layer"):
        staves=layer.findall("stave");key=layer.get("id")
        oldr=np.mean([number(s,"radius") for s in staves])
        settings=controls.get(key,{})
        delta=settings.get("radius_mm",oldr)-oldr;n=settings.get("staves",len(staves))
        for j in range(n):
            s=staves[j if j<len(staves) else j%2]
            angle=2*math.pi*j/n
            denom=np.cos(phi-angle)
            distance=(number(s,"radius")+delta)/denom
            tangent=distance*np.sin(phi-angle)-number(s,"offset_u")
            z=distance*np.sinh(eta)
            forward=denom>0
            for m in s.findall("module"):
                sensor=m.find("sensor")
                for patch in sensor.findall("patch"):
                    uc=number(sensor,"u")+number(patch,"u")
                    vc=number(m,"z")+number(sensor,"v")+number(patch,"v")
                    result+=forward&(np.abs(tangent-uc)<=number(patch,"width")/2)&(np.abs(z-vc)<=number(patch,"length")/2)
    return result


def coverage(hits,eta):
    return [float(np.mean(hits>=10))]+[float(np.mean(hits[(np.abs(eta)>=lo)&(np.abs(eta)<hi)]>=10))
        for lo,hi in zip(np.arange(0,4,.25),np.arange(.25,4.25,.25))]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--compact",type=Path,required=True)
    p.add_argument("--reference",type=Path,required=True)
    p.add_argument("--barrel-variant",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--events",type=int,default=3000)
    p.add_argument("--trials",type=int,default=12000)
    p.add_argument("--donor-layer",type=int,choices=range(1,10),default=1)
    args=p.parse_args()
    root=ET.parse(args.compact).getroot()
    geometry=json.loads((Path(__file__).resolve().parents[3]/"docs/validation/gen3-material-mapping/geometry-summary.json").read_text())
    systems={v["geometry_id_fields"]["volume"]:int(v["name"].split("System")[1].split("Layer")[0])
        for v in geometry["volumes"] if v["name"].startswith("System")}
    with uproot.open(args.reference/"particles.root") as f:g=f["particles"].arrays(library="ak")
    with uproot.open(args.reference/"audit.root") as f:a=f["audit"].arrays(library="ak")
    ao=event_indices(ak.to_numpy(a.event_nr),ak.to_numpy(g.event_id));a=a[ao]
    # Fixed deterministic subset from the historical reference, not hold-out.
    selection=np.random.default_rng(407042).choice(len(g),min(args.events,len(g)),replace=False)
    eta,phi=flat(g,"eta")[selection],flat(g,"phi")[selection]
    strips=np.array([sum(systems[int(i)>>56]>=4 for i in row) for row in ak.to_list(a.measurement_geometry_id[selection])],dtype=np.int16)
    variant=json.loads(args.barrel_variant.read_text())
    barrel=barrel_hits(root.find('./detectors/detector[@id="1"]'),variant.get("pixel_barrel",{}),eta,phi)
    grid=np.arange(615,3071,25,dtype=float)
    # Include the original datums for a faithful geometric control.
    original=np.array([615,795,1046,1333,1645,1977,2328,2692,3070.])
    grid=np.unique(np.r_[grid,original,900,1000,1090,1180,1270,1355,1440,1860,2350,2440])
    cache=np.zeros((10,len(grid),len(eta)),dtype=np.int8)
    for i in range(10):
        donor=i+1 if i<9 else args.donor_layer
        for system,sign in ((2,-1),(3,1)):
            mask=eta*sign>0
            patches=disk_patches(root.find(f'./detectors/detector[@id="{system}"]/disc[@id="{donor}"]'))
            for j,z in enumerate(grid):cache[i,j,mask]=disk_hits(patches,sign*z,eta[mask],phi[mask])
        print("cached disk",i+1,flush=True)
    def counts(indices):return strips+barrel+sum(cache[i,j] for i,j in enumerate(indices))
    def score(indices):
        c=coverage(counts(indices),eta)
        # Screening ranking only: maximise worst quarter-bin then global rate.
        return (min(c[1:]),c[0])
    def valid(indices):
        z=grid[indices]
        return np.all(np.diff(z[:9])>=77.636) and np.min(np.abs(z[:9]-z[9]))>=77.636
    starts=[np.r_[original,900],np.array([900,1090,1180,1270,1355,1440,1860,2350,2440,1000.])]
    rng=np.random.default_rng(408042);records=[];all_trials=[]
    best=None
    for start in starts:
        indices=np.array([np.argmin(abs(grid-z)) for z in start]);current=score(indices)
        for trial in range(args.trials//len(starts)):
            proposal=indices.copy();k=rng.integers(10)
            proposal[k]=np.clip(proposal[k]+rng.integers(-8,9),0,len(grid)-1)
            if not valid(proposal):
                all_trials.append({"trial":len(all_trials),"indices":proposal.tolist(),"status":"rejected_spacing"})
                continue
            value=score(proposal)
            all_trials.append({"trial":len(all_trials),"indices":proposal.tolist(),"score":list(value),"accepted":value>current})
            if value>current:
                indices,current=proposal,value
                records.append({"trial":trial,"datums_mm":grid[indices].tolist(),"score":list(value)})
            if best is None or current>best[0]:best=(current,indices.copy())
        print("screen best",current,grid[indices].tolist(),flush=True)
    ledger=args.output.with_suffix(".trials.json.gz")
    ledger.parent.mkdir(parents=True,exist_ok=True)
    ledger.write_bytes(gzip.compress((json.dumps({"grid_mm":grid.tolist(),"trials":all_trials},separators=(",",":"))+"\n").encode(),mtime=0))
    result={"schema_version":1,"status":"PROTOTYPE_SCREEN_ONLY","method":"Finite XML sensitive patches, straight origin rays, no material/curvature; unchanged strip hit counts borrowed from reference Fatras. Lexicographic worst quarter-eta then global >=10 rate is only schedule-search ranking, not engineering acceptance or resolution.",
        "source_revision":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        "donor_layer":args.donor_layer,"trial_ledger_sha256":sha256(ledger),"trials":len(all_trials),
        "compact_sha256":sha256(args.compact),"reference_audit_sha256":sha256(args.reference/"audit.root"),
        "reference_particles_sha256":sha256(args.reference/"particles.root"),"source_sha256":sha256(__file__),
        "events":len(eta),"subset_seed":407042,"search_seed":408042,"barrel_variant":variant,
        "accepted_improvements":records,"best":{"datums_mm":grid[best[1]].tolist(),"coverage":coverage(counts(best[1]),eta)},
        "limitations":["No native candidate performance or overlap certificate.","Reference subset used for search; final runs need independent seeds.","Retains each original disk module layout; analytic axial spacing only. Service transport not represented in ray counts."]}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+"\n")


if __name__=="__main__":main()
