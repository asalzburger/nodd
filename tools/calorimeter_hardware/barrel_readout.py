"""Supplemental native check of every logical module mask/electrode address."""
import argparse
from array import array
import json
from pathlib import Path
import platform
import subprocess
from model import ROOT as PROJECT,sha


def run(args):
    import ROOT,dd4hep
    ROOT.gROOT.SetBatch(True)
    if ROOT.gSystem.Load(str(args.library.resolve()))<0:raise RuntimeError('factory load')
    d=dd4hep.Detector.getInstance();expected=json.loads(args.expected.read_text());errors=[];cells=boundaries=0
    try:
        d.fromXML(str(args.compact.resolve()));ro=d.readout('BARRELHits');seg=ro.segmentation();decoder=ro.idSpec().decoder();pitch=expected['layout_report']['ecal']['pitch_mm'];ids=sorted({m['index'] for p in expected['layout_report']['layers'] for m in p['modules']});vec=ROOT.std.vector('pair<string,int>')()
        for k,v in dict(system=8,side=0,sector=0,layer=0,module=0).items():vec.emplace_back(k,v)
        sensitive=d.manager().FindVolumeFast('square_active').GetShape()
        for module in ids:
            vec[4].second=module;vid=int(ro.idSpec().encode(vec));seen=set()
            for ix in range(-8,8):
                for iy in range(-8,8):
                    x,y=(ix+.5)*pitch,(iy+.5)*pitch;p=dd4hep.Position(x*dd4hep.mm,y*dd4hep.mm,0);cid=int(seg.cellID(p,p,vid));back=seg.position(cid);dims=seg.cellDimensions(cid)
                    if cid in seen or [int(decoder.get(cid,k)) for k in ('module','x','y')]!=[module,ix,iy] or abs(back.x()/dd4hep.mm-x)>1e-8 or abs(back.y()/dd4hep.mm-y)>1e-8 or any(abs(v/dd4hep.mm-pitch)>1e-8 for v in dims):errors.append('cell mapping')
                    if not sensitive.Contains(array('d',[back.x(),back.y(),0])):errors.append('cell reference outside native mask')
                    seen.add(cid);cells+=1
            for x,y in [(-44,-44),(-44,44),(44,-44),(44,44),(-44,0),(44,0),(0,-44),(0,44)]:
                p=dd4hep.Position(x*dd4hep.mm,y*dd4hep.mm,0);cid=int(seg.cellID(p,p,vid));back=seg.position(cid)
                if cid not in seen or not sensitive.Contains(array('d',[back.x(),back.y(),0])):errors.append('boundary ghost')
                boundaries+=1
        result=dict(status='PASS' if not errors else 'FAIL',errors=errors[:100],scope='Supplemental all-module native segmentation/electrode address test; physical placement IDs/full overlaps/material are independently retained in native.json.',modules_checked=len(ids),logical_electrodes_checked=cells,boundary_points_checked=boundaries,execution=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],text=True)),python=platform.python_version(),ROOT=ROOT.gROOT.GetVersion(),compact_sha256=sha(args.compact),expected_sha256=sha(args.expected),checker_sha256=sha(__file__),segmentation_source_sha256=sha(PROJECT/'prototypes/calorimeter/EdgeCalorimeter.cpp'),library_sha256=sha(args.library)));args.output.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],cells,'cells',boundaries,'boundaries');return 0 if not errors else 1
    finally:dd4hep.Detector.destroyInstance()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--compact',type=Path,required=True);p.add_argument('--expected',type=Path,required=True);p.add_argument('--library',type=Path,required=True);p.add_argument('--output',type=Path,required=True);raise SystemExit(run(p.parse_args()))
