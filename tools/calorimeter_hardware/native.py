"""Actual DD4hep/ROOT construction, constituent mass, IDs and material rays."""
import argparse
from array import array
from collections import Counter,defaultdict
import importlib.util,json,math,platform,subprocess
from pathlib import Path
from model import ROOT,sha
from materials import ELEMENTS
spec=importlib.util.spec_from_file_location('tracker_audit',ROOT/'tools/pixel_barrel_dd4hep/validate.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)

def capacity(s):
    kind=str(s.ClassName())
    if kind=='TGeoBBox':return 8*s.GetDX()*s.GetDY()*s.GetDZ()
    if kind in ('TGeoTube','TGeoTubeSeg'):return 2*math.pi*(s.GetRmax()**2-s.GetRmin()**2)*s.GetDz()*(1 if kind=='TGeoTube' else (s.GetPhi2()-s.GetPhi1())/360)
    if kind=='TGeoCompositeShape':
        n=s.GetBoolNode()
        if str(n.ClassName())!='TGeoSubtraction':raise ValueError('unsupported CSG')
        return capacity(n.GetLeftShape())-capacity(n.GetRightShape())
    raise ValueError(kind)

def box_leaf(s):
    while str(s.ClassName())=='TGeoCompositeShape':s=s.GetBoolNode().GetLeftShape()
    if str(s.ClassName())!='TGeoBBox':raise ValueError('sensitive primitive is not box-backed')
    return s

def run(args):
    import ROOT as R,dd4hep
    R.gROOT.SetBatch(True);R.EnableImplicitMT(1)
    if R.gSystem.Load(str(args.library.resolve()))<0:raise RuntimeError('factory load failed')
    d=dd4hep.Detector.getInstance();expected=json.loads(args.expected.read_text());unit=float(dd4hep.mm)
    errors=[];totals=defaultdict(lambda:dict(volume_mm3=0.,mass_g=0.));counts=Counter();seen=set();sensors={};cells=0;nodes=0
    checked_materials={};composition_delta=0.
    atom={e['name']:e for e in ELEMENTS}
    def elemental(name):
        if name in atom:return {atom[name]['Z']:1.}
        q=expected['materials'][name];f=q['composition'];out=defaultdict(float)
        weights={k:v*atom[k]['A'] if q['basis']=='atom_count' else v for k,v in f.items()};norm=sum(weights.values())
        for k,v in weights.items():
            for z,w in elemental(k).items():out[z]+=v/norm*w
        return dict(out)
    templates={p['name']:p for u in expected['units'] for p in u['parts']}
    try:
        d.fromXML(str(args.compact.resolve()));manager=d.manager()
        def visit(node,parent,ids,path):
            nonlocal cells,nodes,composition_delta
            v=node.GetVolume();name=str(v.GetName());matrix=R.TGeoHMatrix(parent);matrix.Multiply(node.GetMatrix());ids=dict(ids)
            for field in dd4hep.PlacedVolume(node).volIDs():ids[str(field.first)]=int(field.second)
            path+='/'+str(node.GetName());p=templates.get(name)
            if p:
                nodes+=1;counts[p['role']]+=1
                vol=float(capacity(v.GetShape()))/unit**3;density=float(v.GetMaterial().GetDensity());mass=vol*density/1000
                if not math.isclose(vol,p['volume_mm3'],rel_tol=1e-8,abs_tol=1e-7):errors.append('capacity:'+name)
                if not math.isclose(mass,p['mass_g'],rel_tol=1e-8,abs_tol=1e-7):errors.append('mass:'+name)
                material=v.GetMaterial();material_name=str(material.GetName())
                if material_name not in checked_materials:
                    want=elemental(material_name)
                    if material.IsMixture():actual={int(material.GetElement(i).Z()):float(material.GetWmixt()[i]) for i in range(material.GetNelements())}
                    else:actual={int(material.GetZ()):1.}
                    delta=max(abs(want.get(z,0)-actual.get(z,0)) for z in set(want)|set(actual));composition_delta=max(composition_delta,delta)
                    if delta>1e-8:errors.append('composition:'+material_name)
                    checked_materials[material_name]=actual
                t=totals[material_name];t['volume_mm3']+=vol;t['mass_g']+=mass
                if dd4hep.Volume(v).isSensitive():
                    ro=d.readout(('ECAL' if ids['system']==8 else 'HCAL')+'Hits');fields=R.std.vector('pair<string,int>')()
                    for k,val in ids.items():fields.emplace_back(k,val)
                    vid=int(ro.idSpec().encode(fields));decoder=ro.idSpec().decoder()
                    if vid in seen:errors.append('duplicate ID')
                    seen.add(vid)
                    for k,val in ids.items():
                        if int(decoder.get(vid,k))!=val:errors.append('ID decode '+k)
                    u=next(u for u in expected['units'] if u['system_id']==ids['system']);pitch=u['cell_pitch_mm'];ncell=round(expected['config']['ecal']['sensor_active_mm']/pitch) if u['name']=='ecal' else 1
                    # Independently exercise every physical cell of each sensor/tile.
                    for ix in range(-ncell//2,ncell//2) if ncell>1 else (0,):
                        for iy in range(-ncell//2,ncell//2) if ncell>1 else (0,):
                            x=(ix+.5)*pitch if ncell>1 else 0;y=(iy+.5)*pitch if ncell>1 else 0
                            pt=dd4hep.Position(x*unit,y*unit,0);seg=ro.segmentation();cid=int(seg.cellID(pt,pt,vid));back=seg.position(cid)
                            if int(decoder.get(cid,'x'))!=ix or int(decoder.get(cid,'y'))!=iy or abs(back.x()/unit-x)>1e-8 or abs(back.y()/unit-y)>1e-8:errors.append('cell decode:'+name)
                            cells+=1
                    origin=array('d',[0,0,0]);point=array('d',[0,0,0]);matrix.LocalToMaster(origin,point)
                    sensors[path]=dict(ids=ids,center_mm=[x/unit for x in point])
            for i in range(v.GetNdaughters()):visit(v.GetNode(i),matrix,ids,path)
        visit(manager.GetTopNode(),R.TGeoHMatrix(),{},'')
        want=Counter()
        for u in expected['units']:want.update(u['counts'])
        if counts!=want:errors.append('role counts')
        want_totals=defaultdict(lambda:dict(volume_mm3=0.,mass_g=0.))
        for u in expected['units']:
            for m,t in u['material_totals'].items():
                for k in ('volume_mm3','mass_g'):want_totals[m][k]+=t[k]
        for m,t in want_totals.items():
            for k in ('volume_mm3','mass_g'):
                if not math.isclose(t[k],totals[m][k],rel_tol=1e-8,abs_tol=1e-6):errors.append('total '+m+' '+k)
        manager.CheckOverlaps(1e-5*unit)
        overlaps=[dict(description=str(x.GetTitle()),penetration_mm=float(x.GetOverlap())/unit) for x in manager.GetListOfOverlaps()]
        if overlaps:errors.append('overlaps:'+str(len(overlaps)))
        rays=[]
        for system,x in ((8,-400),(9,400)):
            for dx,dy in ((0,0),(15,15),(-45.1,-45.1),(45.1,45.1),(90,0)):
                ray=audit.trace_ray(manager,dd4hep,[x+dx,dy,-60],[0,0,1],sensors,max_length_mm=100)
                ray.update(system=system,offset_mm=[dx,dy]);rays.append(ray)
        rootfile=args.output.with_suffix('.root');args.output.parent.mkdir(parents=True,exist_ok=True);manager.Export(str(rootfile.resolve()))
        report=dict(status='PASS' if not errors else 'FAIL',errors=errors,
                    scope='Isolated native cassette construction; no engineering/performance acceptance',
                    execution=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),python=platform.python_version(),ROOT=R.gROOT.GetVersion(),
                                   compact_sha256=sha(args.compact),expected_sha256=sha(args.expected),factory_sha256=sha(ROOT/'prototypes/calorimeter/Calorimeter.cpp'),library_sha256=sha(args.library),validator_sha256=sha(__file__),shared_ray_sha256=sha(ROOT/'tools/pixel_barrel_dd4hep/validate.py')),
                    counts=dict(counts),physical_material_parts=nodes,sensitive_ids=len(seen),cells_checked=cells,material_totals=dict(totals),mass_g=sum(x['mass_g'] for x in totals.values()),
                    material_elemental_mass_fractions=checked_materials,composition_max_abs_delta=composition_delta,overlap_tolerance_mm=1e-5,overlaps=overlaps,material_rays=rays,root_sha256=sha(rootfile))
        args.output.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],nodes,'parts',len(seen),'sensitive IDs',cells,'cells',len(overlaps),'overlaps');return 0 if not errors else 1
    finally:
        R.DisableImplicitMT();dd4hep.Detector.destroyInstance()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--compact',type=Path,required=True);p.add_argument('--expected',type=Path,required=True);p.add_argument('--library',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    raise SystemExit(run(p.parse_args()))
