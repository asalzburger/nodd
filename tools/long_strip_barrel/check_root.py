#!/usr/bin/env python3
"""Fresh-process ROOT geometry persistence check; no detector factory loading."""
import argparse
from array import array
from collections import Counter,defaultdict
import json
import math
from pathlib import Path

from model import sha
from validate import capacity


def check(rootfile,expectedfile,output):
    import ROOT
    ROOT.gROOT.SetBatch(True)
    expected=json.loads(expectedfile.read_text())
    by_name={e['name']:e for e in expected['entities']}
    manager=ROOT.TGeoManager.Import(str(rootfile.resolve()))
    if not manager:raise ValueError('ROOT import failed')
    errors=[];counts=Counter();materials=defaultdict(lambda:dict(volume_mm3=0.,mass_g=0.))
    pending=[(manager.GetTopNode(),ROOT.TGeoHMatrix())];sensors=0;maximum=0.;max_axis=0.
    # DD4hep's persisted native geometry is in cm; expected values are mm.
    while pending:
        node,parent=pending.pop();volume=node.GetVolume();name=str(volume.GetName())
        transform=ROOT.TGeoHMatrix(parent);transform.Multiply(node.GetMatrix())
        e=by_name.get(name)
        if e:
            counts[e['role']]+=1
            point=array('d',[0.,0.,0.]);transform.LocalToMaster(array('d',[0.,0.,0.]),point)
            residual=math.dist([v*10 for v in point],e['center_mm']);maximum=max(maximum,residual)
            if residual>1e-7:errors.append(name+': persisted centre mismatch')
            if e['role']=='sensitive':
                sensors+=1
                for key,axis in (('u',[1.,0.,0.]),('v',[0.,1.,0.]),('normal',[0.,0.,1.])):
                    vector=array('d',[0.,0.,0.]);transform.LocalToMasterVect(array('d',axis),vector)
                    residual=math.dist(vector,e[key]);max_axis=max(max_axis,residual)
                    if residual>1e-9:errors.append(name+': persisted sensor axis mismatch')
            if 'volume_mm3' in e:
                v=capacity(volume.GetShape())*1000
                mat=str(volume.GetMaterial().GetName());mass=v*float(volume.GetMaterial().GetDensity())/1000
                if mat!=e['material'] or not math.isclose(v,e['volume_mm3'],rel_tol=1e-6):errors.append(name+': persisted solid mismatch')
                if not math.isclose(mass,e['mass_g'],rel_tol=1e-6):errors.append(name+': persisted mass mismatch')
                materials[mat]['volume_mm3']+=v;materials[mat]['mass_g']+=mass
        pending.extend((volume.GetNode(i),transform) for i in range(volume.GetNdaughters()))
    if counts!=expected['counts']:errors.append('Persisted role counts differ')
    report=dict(status='PASS' if not errors else 'FAIL',errors=errors,scope='Fresh ROOT process; no XML or factory load; names/centres/solids/materials, not packed ID persistence',
        root_version=str(ROOT.gROOT.GetVersion()),counts=dict(counts),sensors=sensors,
        maximum_center_residual_mm=maximum,maximum_axis_residual=max_axis,materials=dict(materials),
        root_sha256=sha(rootfile),expected_sha256=sha(expectedfile),validator_sha256=sha(__file__))
    output.write_text(json.dumps(report,indent=2)+'\n')
    manager.Delete()
    print(f"{report['status']}: persisted {sensors} sensor placements")
    return 0 if not errors else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('root','expected','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();raise SystemExit(check(a.root,a.expected,a.output))
