"""Native sampling/upstream/downstream X0 scan; no event transport."""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(a):
    import ROOT as R, dd4hep
    R.gROOT.SetBatch(True)
    for library in a.library:
        if R.gSystem.Load(str(library.resolve()))<0:raise RuntimeError('Factory load failed')
    models=[json.loads(p.read_text()) for p in a.expected]
    names={}
    for model in models:
        if 'wheels' in model:
            pieces=[p for w in model['wheels'] for p in w['pieces']];domain='endcap'
        else:pieces=model['pieces'];domain='barrel'
        for piece in pieces:
            if piece['name'] in names:raise ValueError('Ambiguous sampling name')
            names[piece['name']]=domain
    d=dd4hep.Detector.getInstance();d.fromXML(str(a.compact.resolve()));g=d.manager();mm=float(dd4hep.mm)
    vectors=[]
    for i in range(61):
        eta=i*.05
        for j in range(16):vectors.append((eta,.001+j*2*math.pi/16,'angular'))
    count=models[0]['config']['planes']
    for j in range(64):vectors.append((0.,j*2*math.pi/count/64,'barrel_phase'))
    for eta in (1.5,1.8,2.3,2.8,3.):
        for j in range(48):vectors.append((eta,.001+j*2*math.pi/48,'endcap_phase'))
    rays=[];sensitive={}
    for eta,phi,kind in vectors:
        g.InitTrack(0,0,0,math.cos(phi)/math.cosh(eta),math.sin(phi)/math.cosh(eta),math.tanh(eta))
        nav=g.GetCurrentNavigator();segments=[];distance=0.;steps=0
        while not nav.IsOutside() and distance<12000:
            node=nav.GetCurrentNode();volume=node.GetVolume();name=str(volume.GetName())
            material=volume.GetMaterial();world=volume==g.GetTopVolume()
            if name not in sensitive:sensitive[name]=bool(dd4hep.Volume(volume).isSensitive())
            nav.FindNextBoundaryAndStep((12000-distance)*mm);length=float(nav.GetStep())/mm
            if not math.isfinite(length) or length<=0:raise ValueError('Invalid native step')
            rad=float(material.GetRadLen())/mm
            segments.append(dict(domain=names.get(name),x0=0. if world or rad<=0 else length/rad,
                length=length,active=sensitive[name],start=distance,material=str(material.GetName())))
            distance+=length;steps+=1
            if steps>100000:raise ValueError('Native ray guard')
        hits=[i for i,s in enumerate(segments) if s['domain']]
        groups=defaultdict(float);paths=defaultdict(float)
        for i,s in enumerate(segments):
            domain=s['domain']
            if not domain:domain='upstream' if hits and i<hits[0] else 'downstream' if hits and i>hits[-1] else 'between_or_no_sampling'
            groups[domain]+=s['x0']
            if s['active']:paths[s['domain'] or 'other']+=s['length']
        rays.append(dict(eta=eta,phi_rad=phi,grid=kind,x0=dict(groups),sampling_x0=groups['barrel']+groups['endcap'],
            total_x0=sum(s['x0'] for s in segments),active_path_mm=dict(paths)))
    report=dict(status='PASS',scope='Actual native material lengths; sampling means explicit absorber/electrode/active/glue/skin pieces only. Walls, supports, baths and service boards are separate.',
        compact_sha256=sha(a.compact),materials_sha256=sha(a.compact.parent/'materials.xml'),
        expected_sha256={p.name+str(i):sha(p) for i,p in enumerate(a.expected)},
        library_sha256={p.name:sha(p) for p in a.library},extractor_sha256=sha(__file__),ROOT=R.gROOT.GetVersion(),
        rays=rays,summary={})
    for key,selection in [('barrel_phase',[r for r in rays if r['grid']=='barrel_phase']),
                          ('barrel_core',[r for r in rays if r['grid']=='angular' and r['eta']<=1.2]),
                          ('endcap_core',[r for r in rays if r['grid']=='endcap_phase' and r['eta']>=1.5])]:
        values=[r['sampling_x0'] for r in selection];report['summary'][key]=dict(rays=len(values),min_sampling_x0=min(values),max_sampling_x0=max(values))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['summary']))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--compact',type=Path,required=True)
    p.add_argument('--expected',type=Path,action='append',required=True);p.add_argument('--library',type=Path,action='append',required=True)
    p.add_argument('--output',type=Path,required=True);run(p.parse_args())
