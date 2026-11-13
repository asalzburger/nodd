"""Audit persisted LAr smoke primaries and canonical IDs against native touchables."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET


def sha(path):
    with Path(path).open("rb") as stream: return hashlib.file_digest(stream,"sha256").hexdigest()


def inventory(compact):
    result={}
    for ro in ET.parse(compact).findall('readouts/readout'):
        name=ro.get('name');seg=ro.find('segmentation');descriptor=ro.findtext('id')
        if name not in ('LArBarrelHits','LArEndcapHits'): raise ValueError('Unexpected smoke readout')
        values=list(map(float,seg.get('reference_table_mm').split()));stride=5 if name=='LArBarrelHits' else 6
        if len(values)%stride: raise ValueError('Incomplete reference table')
        size=2 if stride==5 else 3
        keys={tuple(int(values[i+j]) for j in range(size)) for i in range(0,len(values),stride)}
        if len(keys)!=len(values)//stride: raise ValueError('Duplicate canonical reference')
        result[name]=dict(descriptor=descriptor,keys=keys)
        if name=='LArBarrelHits':
            result[name].update(planes=int(seg.get('planes')),phi_merge=int(seg.get('phi_merge')))
        else:
            wheels=list(map(float,seg.get('wheel_table_mm').split()))
            if len(wheels)%4: raise ValueError('Incomplete wheel table')
            result[name]['wheel_planes']=[int(wheels[i+2]) for i in range(0,len(wheels),4)]
    if set(result)!={'LArBarrelHits','LArEndcapHits'}: raise ValueError('Missing smoke readout')
    return result


def canonical_cell(cell, collection, item):
    if not isinstance(cell,int) or cell<0: raise ValueError('Invalid cell ID')
    fields={};offset=0
    for field in item['descriptor'].split(','):
        name,bits=field.split(':');bits=int(bits);size=abs(bits);value=(cell>>offset)&((1<<size)-1)
        if bits<0 and value>=(1<<(size-1)): value-=1<<size
        fields[name]=value;offset+=size
    if cell>>offset or fields['gap']!=0: raise ValueError('Unused bits/noncanonical gap')
    if collection=='LArBarrelHits':
        if fields['system']!=10 or not 0<=fields['plane']<item['planes'] or fields['plane']%item['phi_merge'] or (fields['layer'],fields['theta']) not in item['keys']:
            raise ValueError('Noncanonical barrel virtual cell')
    else:
        wheel=fields['wheel']
        if fields['system']!=11 or fields['side'] not in (1,2) or not 0<=wheel<len(item['wheel_planes']) or not 0<=fields['plane']<item['wheel_planes'][wheel] or (wheel,fields['rho'],fields['z']) not in item['keys']:
            raise ValueError('Noncanonical turbine virtual cell')
    return fields


def audit(directory):
    import edm4hep  # noqa: F401; register dictionaries
    from podio import root_io
    timing=json.loads((directory/"timing.json").read_text())
    if timing["exit_code"]!=0 or timing["smoke_events"]!=7: raise ValueError("Incomplete smoke transport")
    cases=json.loads((directory/"smoke-cases.json").read_text())
    raw_ids={int(line.split("\t",1)[0]) for line in (directory/"sensitive.tsv").read_text().splitlines()}
    if len(raw_ids)!=43648 or sha(directory/"sensitive.tsv")!=timing["sensitive_dump_sha256"]:
        raise ValueError("Changed native raw-ID inventory")
    if sha(directory/'detector.xml')!=timing['compact_sha256']: raise ValueError('Changed executed readout')
    cells=inventory(directory/'detector.xml')
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
                canonical_cell(cell,collection,cells[collection])
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
