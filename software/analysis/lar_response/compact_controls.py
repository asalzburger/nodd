"""Compare complete serial/MT saved-cell controls; full event payload stays local."""
import argparse
import hashlib
import json
from pathlib import Path


def digest(p):return hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()


def read(path):
    from podio import root_io
    events={}
    for frame in root_io.Reader(str(path/'events.root')).get('events'):
        header,=frame.get('EventHeader');event=int(header.getEventNumber())
        if event in events:raise ValueError('Duplicate control event')
        cells={}
        for name in ('LArBarrelHits','LArEndcapHits'):
            for h in frame.get(name):
                key=(name,int(h.getCellID()));p=h.getPosition()
                if key in cells:raise ValueError('Duplicate control cell')
                cells[key]=(float(h.getEnergy()),float(p.x),float(p.y),float(p.z))
        events[event]=cells
    return events


def compare(a,b,out):
    for path in (a,b):
        proof=json.loads((path/'readback.json').read_text())
        if proof['status']!='PASS' or proof['root_sha256']!=digest(path/'events.root'):raise ValueError('Unbound control')
    first,second=read(a),read(b)
    if set(first)!=set(range(24)) or set(second)!=set(first):raise ValueError('Incomplete control events')
    mismatches=[i for i in first if first[i]!=second[i]]
    result=dict(status='FAIL' if mismatches else 'PASS',events=24,hits=sum(map(len,first.values())),
        comparison='All canonical cell IDs, saved energies and positions exactly equal by event ID; storage order unrestricted.',
        mismatched_events=mismatches,serial_root_sha256=digest(a/'events.root'),mt_root_sha256=digest(b/'events.root'))
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
    if mismatches:raise ValueError('Serial/MT cell mismatch')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--serial',type=Path,required=True);p.add_argument('--mt',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();compare(a.serial,a.mt,a.output)
