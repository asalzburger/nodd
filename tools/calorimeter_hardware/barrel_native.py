"""Independent native dimensions, CSG, material, placement, ID and ray audit."""
import argparse
from array import array
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import platform
import subprocess

from edge_native import audit
from native_prism import check_sections, native_capacity
from model import ROOT, sha
from materials import ELEMENTS


def run(args):
    import ROOT as R,dd4hep
    R.gROOT.SetBatch(True);R.gRandom.SetSeed(args.overlap_seed);R.EnableImplicitMT(1)
    if R.gSystem.Load(str(args.library.resolve()))<0:raise RuntimeError('factory load')
    d=dd4hep.Detector.getInstance();e=json.loads(args.expected.read_text());report=e['layout_report'];mm=float(dd4hep.mm);errors=[];counts=Counter();totals=defaultdict(lambda:dict(volume_mm3=0.,mass_g=0.));parents={};board_names={};volume_ids=set();templates={};composition={};shape_checks=0;placement_checks=0
    for path,h in e['source_sha256'].items():
        if sha(ROOT/path)!=h:raise ValueError('stale expected source '+path)
    atom={x['name']:x for x in ELEMENTS}
    def elements(name):
        if name in atom:return {atom[name]['Z']:1.}
        recipe=e['hardware']['materials'][name];weights={k:v*atom[k]['A'] if recipe['basis']=='atom_count' else v for k,v in recipe['composition'].items()};norm=sum(weights.values());out=defaultdict(float)
        for k,v in weights.items():
            for z,w in elements(k).items():out[z]+=v/norm*w
        return dict(out)
    def agree(a,b,label):
        if not math.isclose(a,b,rel_tol=1e-8,abs_tol=1e-6):errors.append(label)
    def ids(node):return {str(q.first):int(q.second) for q in dd4hep.PlacedVolume(node).volIDs()}
    def pose(matrix,p):
        nonlocal placement_checks
        t=matrix.GetTranslation();rot=matrix.GetRotationMatrix()
        for i in range(3):
            agree(t[i]/mm,p['center_mm'][i],'translation')
            for j in range(3):agree(rot[3*i+j],p['frame'][j][i],'rotation')
        agree(rot[0]*(rot[4]*rot[8]-rot[5]*rot[7])-rot[1]*(rot[3]*rot[8]-rot[5]*rot[6])+rot[2]*(rot[3]*rot[7]-rot[4]*rot[6]),1,'proper transform');placement_checks+=1
    def shape(s,p):
        nonlocal shape_checks
        base=s;cuts=[]
        while str(base.ClassName())=='TGeoCompositeShape':
            node=base.GetBoolNode()
            if str(node.ClassName())!='TGeoSubtraction' or not node.GetLeftMatrix().IsIdentity():raise ValueError('unsupported Boolean')
            cuts.append((node.GetRightShape(),node.GetRightMatrix()));base=node.GetLeftShape()
        if len(cuts)!=len(p.get('cuts',[])):errors.append('cut count')
        for (cut,matrix),q in zip(reversed(cuts),p.get('cuts',[])):shape(cut,q);pose(matrix,q)
        kind=str(base.ClassName())
        if p['shape_kind']=='xtru':
            check_sections(base)
            if kind!='TGeoXtru':errors.append('prism type');return
            if base.GetNvert()!=len(p['vertices_mm']):errors.append('vertex count')
            for i,(x,y) in enumerate(p['vertices_mm']):agree(base.GetX(i)/mm,x,'vertex x');agree(base.GetY(i)/mm,y,'vertex y')
            agree((base.GetZ(1)-base.GetZ(0))/mm,p['depth_mm'],'prism depth')
        elif p['shape_kind']=='box':
            if kind!='TGeoBBox':errors.append('box type');return
            for key,value in zip(('sx','sy','sz'),(base.GetDX(),base.GetDY(),base.GetDZ())):agree(2*value/mm,p['dimensions_mm'][key],'box '+key)
        elif p['shape_kind']=='tube':
            if kind not in ('TGeoTube','TGeoTubeSeg'):errors.append('tube type');return
            if kind=='TGeoTubeSeg':agree(base.GetPhi2()-base.GetPhi1(),360,'full tube angle')
            for key,value in zip(('rmin','rmax','length'),(base.GetRmin(),base.GetRmax(),2*base.GetDz())):agree(value/mm,p['dimensions_mm'][key],'tube '+key)
        else:raise ValueError('unknown expected primitive')
        shape_checks+=1
    def parts(volume,pieces):
        result=[]
        for j,p in enumerate(pieces):
            node=volume.GetNode(j);v=node.GetVolume();pose(node.GetMatrix(),p);shape(v.GetShape(),p)
            if str(v.GetName())!=p['name'] or str(v.GetMaterial().GetName())!=p['material']:errors.append('part/material identity')
            cap=native_capacity(v.GetShape())/mm**3;mass=cap*v.GetMaterial().GetDensity()/1000;agree(cap,p['volume_mm3'],'native capacity');agree(mass,p['mass_g'],'native mass')
            name=p['material'];m=v.GetMaterial()
            if name not in composition:
                actual={int(m.GetElement(k).Z()):float(m.GetWmixt()[k]) for k in range(m.GetNelements())} if m.IsMixture() else {int(m.GetZ()):1.};want=elements(name);delta=max(abs(actual.get(z,0)-want.get(z,0)) for z in set(actual)|set(want));composition[name]=delta
                if delta>1e-8:errors.append('elemental composition')
            sensitive=dd4hep.Volume(v).isSensitive()
            if sensitive!=(p['role']=='sensitive'):errors.append('sensitive role')
            result.append(dict(material=name,role=p['role'],volume_mm3=cap,mass_g=mass))
        return result
    def accumulate(items,mult=1):
        for p in items:
            counts[p['role']]+=mult
            for k in ('volume_mm3','mass_g'):totals[p['material']][k]+=mult*p[k]
    try:
        d.fromXML(str(args.compact.resolve()));manager=d.manager();top=next(manager.GetTopVolume().GetNode(i) for i in range(manager.GetTopVolume().GetNdaughters()) if str(manager.GetTopVolume().GetNode(i).GetVolume().GetName())=='BARREL');assembly=top.GetVolume();ro=d.readout('BARRELHits');seg=ro.segmentation();decoder=ro.idSpec().decoder()
        if ids(top)!={'system':8} or assembly.GetNdaughters()!=len(e['replicas']):errors.append('top/replica IDs')
        board_items=None;board_volume=None;vec=R.std.vector('pair<string,int>')()
        for k,v in dict(system=8,side=0,sector=0,layer=0,module=0).items():vec.emplace_back(k,v)
        for i,p in enumerate(e['replicas']):
            node=assembly.GetNode(i);pose(node.GetMatrix(),p);parent=ids(node)
            if parent!={k:p[k] for k in ('side','sector','layer')}:errors.append('native parent fields')
            region=p['region'];v=node.GetVolume();region_data=next(q for q in e['regions'] if q['name']==region);pieces=region_data['parts'];modules=region_data['modules'];parents[str(node.GetName())]=dict(ids=parent,region=region)
            if region not in templates:
                if v.GetNdaughters()!=len(pieces)+len(modules):errors.append('logical region children')
                templates[region]=parts(v,pieces);board_names[region]={}
                for j,q in enumerate(modules):
                    b=v.GetNode(len(pieces)+j);board_names[region][str(b.GetName())]=q['index'];layer=report['layers'][p['layer']];negative=q['center_mm'][1]<0;frame=[[0,-1,0],[0,0,-1],[1,0,0]] if negative else [[0,1,0],[0,0,1],[1,0,0]]
                    want=dict(center_mm=[layer['front_mm']+report['ecal']['absorber_mm'],*q['center_mm']],frame=frame);pose(b.GetMatrix(),want)
                    if ids(b)!={'module':q['index']} or str(b.GetVolume().GetName())!='barrel_board_square':errors.append('board parent ID/template')
                    if board_items is None:
                        board_volume=b.GetVolume()
                        if board_volume.GetNdaughters()!=len(e['hardware']['board_parts']):errors.append('board part count')
                        board_items=parts(board_volume,e['hardware']['board_parts'])
                    # Independent corner audit of actual native PCB/board transform.
                    pcb=next(board_volume.GetNode(k) for k in range(board_volume.GetNdaughters()) if str(board_volume.GetNode(k).GetVolume().GetName())=='square_PCB_G10');s=pcb.GetVolume().GetShape();matrix=R.TGeoHMatrix(b.GetMatrix());matrix.Multiply(pcb.GetMatrix());panel=layer['panels'][q['panel']]
                    for k in range(s.GetNvert()):
                        for z in (s.GetZ(0),s.GetZ(1)):
                            local=array('d',[s.GetX(k),s.GetY(k),z]);world=array('d',[0,0,0]);matrix.LocalToMaster(local,world);r,t,a=[u/mm for u in world]
                            if abs(t)>r*math.tan(math.pi/16)-41+1e-6 or not panel['center_mm']-panel['length_mm']/2+5-1e-6<=a<=panel['center_mm']+panel['length_mm']/2-5+1e-6:errors.append('native PCB containment')
            accumulate(templates[region]);accumulate(board_items or [],len(modules))
            vec[2].second=p['sector'];vec[3].second=p['layer']
            for q in modules:
                vec[4].second=q['index'];vid=int(ro.idSpec().encode(vec))
                if vid in volume_ids:errors.append('duplicate physical volume ID')
                volume_ids.add(vid)
                for k,val in dict(system=8,**parent,module=q['index']).items():
                    if int(decoder.get(vid,k))!=val:errors.append('volume ID roundtrip')
        for name,want in e['hardware']['material_totals'].items():
            for k in ('volume_mm3','mass_g'):agree(totals[name][k],want[k],'full inventory '+name)
        # Every pad of the shared square-board prototype, with all closed ties.
        vec[2].second=0;vec[3].second=0;vec[4].second=0;vid=int(ro.idSpec().encode(vec));active=board_volume.GetNode(0).GetVolume().GetShape();cells=set();pitch=report['ecal']['pitch_mm']
        for ix in range(-8,8):
            for iy in range(-8,8):
                x,y=(ix+.5)*pitch,(iy+.5)*pitch;point=dd4hep.Position(x*mm,y*mm,0);cid=int(seg.cellID(point,point,vid));back=seg.position(cid)
                if cid in cells or [int(decoder.get(cid,k)) for k in ('x','y')]!=[ix,iy]:errors.append('pad ID')
                cells.add(cid);agree(back.x()/mm,x,'pad x');agree(back.y()/mm,y,'pad y')
                if not active.Contains(array('d',[back.x(),back.y(),0])):errors.append('pad outside active silicon')
        boundary=0
        for x,y in [(-44,-44),(-44,44),(44,-44),(44,44),(-44,0),(44,0),(0,-44),(0,44)]:
            point=dd4hep.Position(x*mm,y*mm,0);cid=int(seg.cellID(point,point,vid));back=seg.position(cid)
            if cid not in cells or not active.Contains(array('d',[back.x(),back.y(),0])):errors.append('boundary ghost cell')
            boundary+=1
        print('Native shapes',shape_checks,'placements',placement_checks,'sensor IDs',len(volume_ids),'checked',flush=True)
        manager.CheckOverlaps(report['config']['overlap_tolerance_mm']*mm);overlaps=[dict(description=str(q.GetTitle()),penetration_mm=float(q.GetOverlap())/mm) for q in manager.GetListOfOverlaps()]
        if overlaps:errors.append('overlaps:'+str(len(overlaps)))
        class Paths:
            def __contains__(self,path):return path.rsplit('/',1)[-1].startswith('square_active_')
            def __getitem__(self,path):
                nodes=path.split('/');p=next(parents[n] for n in nodes if n in parents);module=next(board_names[p['region']][n] for n in nodes if n in board_names[p['region']]);return dict(ids=dict(system=8,**p['ids'],module=module))
        rays=[]
        for eta in (0,.25,.5,.75,1,1.25,1.5,1.6):
            for sign in ((1,) if eta==0 else (-1,1)):
                for phi in (0,.03,math.pi/16-.003,math.pi/16+.003):
                    E=sign*eta;direction=[math.cos(phi)/math.cosh(E),math.sin(phi)/math.cosh(E),math.tanh(E)];ray=audit.trace_ray(manager,dd4hep,[0,0,0],direction,Paths(),max_length_mm=6000);ray.update(eta=E,phi=phi);rays.append(ray)
        rootfile=args.output.with_suffix('.root');manager.Export(str(rootfile.resolve()));result=dict(status='PASS' if not errors else 'FAIL',errors=errors[:100],scope='Complete isolated SiW barrel; native dimensions/CSG/materials, logical placements, all physical sensor volume IDs, logical electrodes/boundaries and full overlap check. No engineering or performance acceptance.',execution=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],text=True)),python=platform.python_version(),ROOT=R.gROOT.GetVersion(),compact_sha256=sha(args.compact),expected_sha256=sha(args.expected),validator_sha256=sha(__file__),helper_sha256={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'tools/calorimeter_hardware/native_prism.py',ROOT/'tools/calorimeter_hardware/edge_native.py',ROOT/'tools/pixel_barrel_dd4hep/validate.py',ROOT/'tools/calorimeter_hardware/edge_layout.py')},factory_sha256=sha(ROOT/'prototypes/calorimeter/BarrelCalorimeter.cpp'),segmentation_source_sha256=sha(ROOT/'prototypes/calorimeter/EdgeCalorimeter.cpp'),library_sha256=sha(args.library)),native_shape_checks=shape_checks,native_placement_checks=placement_checks,physical_sensor_volume_ID_roundtrips=len(volume_ids),logical_electrodes_checked=len(cells),boundary_points_checked=boundary,physical_counts=dict(counts),material_totals=dict(totals),mass_g=sum(q['mass_g'] for q in totals.values()),composition_max_abs_delta=max(composition.values()),overlap_tolerance_mm=report['config']['overlap_tolerance_mm'],overlap_random_seed=args.overlap_seed,overlaps=overlaps,material_rays=rays,root_sha256=sha(rootfile));args.output.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(overlaps),'overlaps',errors[:8]);return 0 if not errors else 1
    finally:R.DisableImplicitMT();dd4hep.Detector.destroyInstance()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--compact',type=Path,required=True);p.add_argument('--expected',type=Path,required=True);p.add_argument('--library',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--overlap-seed',type=int,default=31);raise SystemExit(run(p.parse_args()))
