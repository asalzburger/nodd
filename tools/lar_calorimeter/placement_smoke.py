"""Audit persisted LAr smoke primaries and canonical IDs against native touchables."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def sha(path):
    with Path(path).open("rb") as stream: return hashlib.file_digest(stream,"sha256").hexdigest()


def audit(directory):
    import edm4hep  # noqa: F401; register dictionaries
    from podio import root_io
    timing=json.loads((directory/"timing.json").read_text())
    if timing["exit_code"]!=0 or timing["smoke_events"]!=7: raise ValueError("Incomplete smoke transport")
    cases=json.loads((directory/"smoke-cases.json").read_text())
    raw_ids={int(line.split("\t",1)[0]) for line in (directory/"sensitive.tsv").read_text().splitlines()}
    if len(raw_ids)!=43648 or sha(directory/"sensitive.tsv")!=timing["sensitive_dump_sha256"]:
        raise ValueError("Changed native raw-ID inventory")
    results=[]
    for case in cases:
        path=directory/(case["label"]+".root")
        reader=root_io.Reader(str(path));events=iter(reader.get("events"));frame=next(events)
        if next(events,None) is not None: raise ValueError("Wrong smoke event count")
        header,=frame.get("EventHeader")
        primary,=[p for p in frame.get("MCParticles") if p.getGeneratorStatus()==1]
        p=primary.getMomentum();v=primary.getVertex();pt=math.hypot(p.x,p.y)
        if ((int(header.getRunNumber()),int(header.getEventNumber()))!=(case["run"],0) or primary.getPDG()!=11 or
            (v.x,v.y,v.z)!=(0,0,0) or abs(math.hypot(pt,p.z)-case["momentum_GeV"])>1e-7 or
            abs(math.asinh(p.z/pt)-case["eta"])>1e-10 or abs(math.atan2(p.y,p.x)-case["phi"])>1e-10):
            raise ValueError("Saved primary differs from smoke case")
        counts={};energies={};target=0
        for collection,system in (("LArBarrelHits",10),("LArEndcapHits",11)):
            seen=set();deposits=[]
            for hit in frame.get(collection):
                cell=int(hit.getCellID());energy=float(hit.getEnergy());pos=hit.getPosition()
                if (cell&255)!=system or cell in seen or cell&((1<<24)-1) not in raw_ids or (cell>>23)&1 or not math.isfinite(energy) or energy<=0 or not all(math.isfinite(x) for x in (pos.x,pos.y,pos.z)):
                    raise ValueError("Invalid canonical persisted LAr hit")
                if system==10 and ((cell>>8)&2047)%2: raise ValueError("Noncanonical barrel electrode group")
                if (system==10 and case["wheel"] is None) or (system==11 and ((cell>>8)&3)==case["side"] and ((cell>>10)&3)==case["wheel"]): target+=1
                seen.add(cell);deposits.append(energy)
            counts[collection]=len(seen);energies[collection]=math.fsum(deposits)
        if not target: raise ValueError("No signal in aimed barrel/wheel/side")
        results.append(dict(case=case,counts=counts,deposited_energy_GeV=energies,target_hits=target,root_sha256=sha(path)))
    proof={"status":"PASS","events":len(results),"scope":"Saved-hit/primary/ID smoke only; no shower-response equivalence or digitization claim",
        "timing_sha256":sha(directory/"timing.json"),"cases_sha256":sha(directory/"smoke-cases.json"),"auditor_sha256":sha(__file__),"results":results}
    (directory/"smoke-readback.json").write_text(json.dumps(proof,indent=2)+"\n")
    print(json.dumps(proof,indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("directory",type=Path);audit(p.parse_args().directory)
