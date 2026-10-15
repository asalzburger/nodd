"""Independent DD4hep/ROOT shape, material, electrode and replica audit (DES030)."""
import argparse
from array import array
from collections import Counter, defaultdict
import importlib.util
import json
import math
from pathlib import Path
import platform
import subprocess

from model import ROOT, sha
from edge_layout import centroid
from materials import ELEMENTS

spec=importlib.util.spec_from_file_location('material_audit',ROOT/'tools/pixel_barrel_dd4hep/validate.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)


def primitive_capacity(s):
    kind=str(s.ClassName())
    if kind=='TGeoXtru':
        p=[[float(s.GetX(i)),float(s.GetY(i))] for i in range(s.GetNvert())]
        return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))/2*(s.GetZ(1)-s.GetZ(0))
    if kind=='TGeoBBox':return 8*s.GetDX()*s.GetDY()*s.GetDZ()
    if kind in ('TGeoTube','TGeoTubeSeg'):
        if kind=='TGeoTubeSeg' and abs(s.GetPhi2()-s.GetPhi1()-360)>1e-8:raise ValueError('partial cylinder not supported')
        return math.pi*(s.GetRmax()**2-s.GetRmin()**2)*2*s.GetDz()
    raise ValueError(kind)


def native_capacity(s):
    if str(s.ClassName())!='TGeoCompositeShape':return primitive_capacity(s)
    cuts=[];base=s
    while str(base.ClassName())=='TGeoCompositeShape':
        node=base.GetBoolNode()
        if str(node.ClassName())!='TGeoSubtraction' or not node.GetLeftMatrix().IsIdentity():raise ValueError('unsupported Boolean operation')
        cuts.append((node.GetRightShape(),node.GetRightMatrix()));base=node.GetLeftShape()
    # Restricted contract: every cutter lies in the native polygon prism and
    # their transformed bounding boxes are disjoint. Touching boundaries allowed.
    if str(base.ClassName())!='TGeoXtru':raise ValueError('expected polygon Boolean base')
    p=[[float(base.GetX(i)),float(base.GetY(i))] for i in range(base.GetNvert())];boxes=[]
    for cut,matrix in cuts:
        kind=str(cut.ClassName());points=[]
        if kind=='TGeoXtru':local=[[cut.GetX(i),cut.GetY(i),z] for i in range(cut.GetNvert()) for z in (cut.GetZ(0),cut.GetZ(1))]
        elif kind in ('TGeoTube','TGeoTubeSeg'):local=[[x,y,z] for x in (-cut.GetRmax(),cut.GetRmax()) for y in (-cut.GetRmax(),cut.GetRmax()) for z in (-cut.GetDz(),cut.GetDz())]
        else:raise ValueError('unsupported cutter')
        for q in local:
            a=array('d',q);b=array('d',[0,0,0]);matrix.LocalToMaster(a,b);points.append(list(b))
            if b[2]<base.GetZ(0)-1e-10 or b[2]>base.GetZ(1)+1e-10:raise ValueError('cut depth outside base')
            for u,v in zip(p,p[1:]+p[:1]):
                if (v[0]-u[0])*(b[1]-u[1])-(v[1]-u[1])*(b[0]-u[0])<-1e-9:raise ValueError('cut outside polygon')
        boxes.append(([min(q[i] for q in points) for i in range(3)],[max(q[i] for q in points) for i in range(3)]))
    for i,(lo,hi) in enumerate(boxes):
        for lo2,hi2 in boxes[i+1:]:
            if all(min(a,b)-max(c,d)>1e-10 for a,b,c,d in zip(hi,hi2,lo,lo2)):raise ValueError('cutters overlap')
    return primitive_capacity(base)-sum(primitive_capacity(cut) for cut,_ in cuts)


def run(args):
    import ROOT as R,dd4hep
    R.gROOT.SetBatch(True);R.EnableImplicitMT(1)
    if R.gSystem.Load(str(args.library.resolve()))<0:raise RuntimeError('factory load failed')
    d=dd4hep.Detector.getInstance();e=json.loads(args.expected.read_text());mm=float(dd4hep.mm);errors=[];templates={};regions={};totals=defaultdict(lambda:dict(volume_mm3=0.,mass_g=0.));native_roles=Counter();replica_paths={};native_sensors={};compositions={};max_composition=0.
    atom={x['name']:x for x in ELEMENTS}
    def elements(name):
        if name in atom:return {atom[name]['Z']:1.}
        material=e['hardware']['materials'][name];weights={k:v*atom[k]['A'] if material['basis']=='atom_count' else v for k,v in material['composition'].items()};norm=sum(weights.values());out=defaultdict(float)
        for k,v in weights.items():
            for z,w in elements(k).items():out[z]+=v/norm*w
        return dict(out)
    def agree(x,y,label):
        if not math.isclose(x,y,rel_tol=1e-8,abs_tol=1e-6):errors.append(label)
    def volids(node):return {str(q.first):int(q.second) for q in dd4hep.PlacedVolume(node).volIDs()}
    def pose(node,p):
        matrix=node.GetMatrix();t=matrix.GetTranslation();rot=matrix.GetRotationMatrix()
        for i in range(3):
            agree(t[i]/mm,p['center_mm'][i],'translation:'+p.get('name',p.get('region')))
            for j in range(3):agree(rot[3*i+j],p['frame'][j][i],'rotation')
        det=rot[0]*(rot[4]*rot[8]-rot[5]*rot[7])-rot[1]*(rot[3]*rot[8]-rot[5]*rot[6])+rot[2]*(rot[3]*rot[7]-rot[4]*rot[6]);agree(det,1,'proper rotation')
    try:
        d.fromXML(str(args.compact.resolve()));manager=d.manager();top=next(manager.GetTopVolume().GetNode(i) for i in range(manager.GetTopVolume().GetNdaughters()) if str(manager.GetTopVolume().GetNode(i).GetVolume().GetName())=='EDGE');agree(volids(top).get('system'),8,'system ID');assembly=top.GetVolume();observed_parents=set();sample_vids=set();ro=d.readout('EDGEHits');seg=ro.segmentation();decoder=ro.idSpec().decoder()
        if assembly.GetNdaughters()!=len(e['replicas']):errors.append('replica count')
        for i,p in enumerate(e['replicas']):
            node=assembly.GetNode(i);pose(node,p);fields=volids(node)
            if fields!={k:p[k] for k in ('side','sector','layer')}:errors.append('native parent fields')
            key=(p['region'],p['side'],p['sector'],p['layer'])
            if key in observed_parents:errors.append('duplicate parent')
            observed_parents.add(key);replica_paths[str(node.GetName())]=dict(system=8,**fields);v=node.GetVolume();region=p['region'];parts=e['hardware']['layer_parts' if region=='edge_layer' else 'frame_parts'];regions.setdefault(region,dict(replicas=0,logical_parts=len(parts)));regions[region]['replicas']+=1
            if region not in templates:
                if v.GetNdaughters()!=len(parts):errors.append('logical daughter count')
                templates[region]=[]
                for j,q in enumerate(parts):
                    leaf=v.GetNode(j);pose(leaf,q);volume=leaf.GetVolume();shape=volume.GetShape();vol=native_capacity(shape)/mm**3;mat=volume.GetMaterial();mass=vol*mat.GetDensity()/1000;agree(vol,q['volume_mm3'],'capacity:'+q['name']);agree(mass,q['mass_g'],'mass:'+q['name'])
                    if str(volume.GetName())!=q['name'] or str(mat.GetName())!=q['material']:errors.append('name/material')
                    name=q['material']
                    if name not in compositions:
                        actual={int(mat.GetElement(k).Z()):float(mat.GetWmixt()[k]) for k in range(mat.GetNelements())} if mat.IsMixture() else {int(mat.GetZ()):1.};want=elements(name);delta=max(abs(actual.get(z,0)-want.get(z,0)) for z in set(actual)|set(want));max_composition=max(max_composition,delta);compositions[name]=actual
                        if delta>1e-8:errors.append('composition:'+name)
                    templates[region].append(dict(material=name,volume_mm3=vol,mass_g=mass,role=q['role']))
                    if 'module' in q:
                        if not dd4hep.Volume(volume).isSensitive() or volids(leaf)!={'module':q['module']}:errors.append('sensitive/ID field')
                        native_sensors[q['module']]=shape
                        native_sensors[str(leaf.GetName())]=q['module']
            for q in templates[region]:
                for k in ('volume_mm3','mass_g'):totals[q['material']][k]+=q[k]
                native_roles[q['role']]+=1
            if region=='edge_layer':
                # All physical sensor volume IDs round trip. Cell uniqueness also
                # follows the independently checked disjoint parent field ranges.
                for module in e['modules']:
                    fields2=dict(system=8,**fields,module=module['index']);vec=R.std.vector('pair<string,int>')()
                    for k,val in fields2.items():vec.emplace_back(k,val)
                    vid=int(ro.idSpec().encode(vec))
                    if vid in sample_vids:errors.append('duplicate volume ID')
                    sample_vids.add(vid)
                    if any(int(decoder.get(vid,k))!=val for k,val in fields2.items()):errors.append('volume ID round trip')
        for name,want in e['hardware']['material_totals'].items():
            if args.expected and e['layers']==48:
                for k in ('volume_mm3','mass_g'):agree(totals[name][k],want[k],'full total '+name)
        cells=members=boundary_points=0;seen=set()
        for module in e['modules']:
            idx=module['index'];vec=R.std.vector('pair<string,int>')()
            for k,val in dict(system=8,side=1,sector=0,layer=0,module=idx).items():vec.emplace_back(k,val)
            vid=int(ro.idSpec().encode(vec));shape=native_sensors[idx]
            for g in module['pads']:
                x,y=g['reference_mm'];point=dd4hep.Position(x*mm,y*mm,0);cid=int(seg.cellID(point,point,vid));back=seg.position(cid)
                if [int(decoder.get(cid,k)) for k in ('x','y')]!=g['key']:errors.append('pad anchor ID')
                agree(back.x()/mm,x,'pad x');agree(back.y()/mm,y,'pad y');dims=seg.cellDimensions(cid)
                for j,v in enumerate(g['bbox_mm']):agree(dims[j]/mm,v,'pad bounds')
                if cid in seen:errors.append('duplicate pad ID')
                seen.add(cid)
                if not shape.Contains(array('d',[back.x(),back.y(),0])):errors.append('reference outside native mask')
                for polygon in g['polygons']:
                    a,b=centroid(polygon);pt=dd4hep.Position(a*mm,b*mm,0)
                    if int(seg.cellID(pt,pt,vid))!=cid or not shape.Contains(array('d',[a*mm,b*mm,0])):errors.append('merged/raw electrode mapping')
                    members+=1
                cells+=1
            vertices=module['active'];points=vertices+[[sum(p[i] for p in (a,b))/2 for i in (0,1)] for a,b in zip(vertices,vertices[1:]+vertices[:1])]
            for x,y in points:
                point=dd4hep.Position(x*mm,y*mm,0);cid=int(seg.cellID(point,point,vid));back=seg.position(cid)
                if cid not in seen or not shape.Contains(array('d',[back.x(),back.y(),0])):errors.append('boundary ghost electrode')
                boundary_points+=1
        print('Native parts, compositions, replicas and',cells,'electrode references checked',flush=True)
        manager.CheckOverlaps(1e-5*mm);overlaps=[dict(description=str(q.GetTitle()),penetration_mm=float(q.GetOverlap())/mm) for q in manager.GetListOfOverlaps()]
        if overlaps:errors.append('overlaps:'+str(len(overlaps)))
        class SensitivePaths:
            def __contains__(self,path):return path.rsplit('/',1)[-1] in native_sensors
            def __getitem__(self,path):
                leaf=path.rsplit('/',1)[-1];parent=next(q for q in path.split('/') if q in replica_paths);return dict(ids=dict(**replica_paths[parent],module=native_sensors[leaf]))
        rays=[]
        for eta in (1.6,2.,2.5,3.,3.5,3.9,4.,4.05):
            for sign in (-1,1):
                # Sample wedge centres and both sides of a physical seam.
                for phi in (.03,math.pi/16-.003,math.pi/16+.003,math.pi/8-.003):
                    E=sign*eta;direction=[math.cos(phi)/math.cosh(E),math.sin(phi)/math.cosh(E),math.tanh(E)];ray=audit.trace_ray(manager,dd4hep,[0,0,0],direction,SensitivePaths(),max_length_mm=7000);ray.update(eta=E,phi=phi);rays.append(ray)
        rootfile=args.output.with_suffix('.root');manager.Export(str(rootfile.resolve()));result=dict(status='PASS' if not errors else 'FAIL',errors=errors[:100],scope='Complete isolated ECAL endcaps; all native parts/replicas/volume IDs; all logical electrodes/raw mask fragments and polygon boundary ties; restricted Boolean containment; no engineering or performance acceptance.',execution=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],text=True)),python=platform.python_version(),ROOT=R.gROOT.GetVersion(),compact_sha256=sha(args.compact),expected_sha256=sha(args.expected),validator_sha256=sha(__file__),factory_sha256=sha(ROOT/'prototypes/calorimeter/EdgeCalorimeter.cpp'),library_sha256=sha(args.library)),regions=regions,physical_volume_ID_roundtrips=len(sample_vids),logical_electrodes_checked=cells,raw_electrode_fragments_checked=members,boundary_points_checked=boundary_points,physical_counts=dict(native_roles),material_totals=dict(totals),mass_g=sum(q['mass_g'] for q in totals.values()),composition_max_abs_delta=max_composition,overlap_tolerance_mm=1e-5,overlaps=overlaps,material_rays=rays,root_sha256=sha(rootfile));args.output.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(overlaps),'overlaps',errors[:8]);return 0 if not errors else 1
    finally:R.DisableImplicitMT();dd4hep.Detector.destroyInstance()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--compact',type=Path,required=True);p.add_argument('--expected',type=Path,required=True);p.add_argument('--library',type=Path,required=True);p.add_argument('--output',type=Path,required=True);raise SystemExit(run(p.parse_args()))
