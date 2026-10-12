"""Native complete assembly audit using reusable logical inventories.

Every native logical placement/replica is checked. Capacities are audited once
per shared volume, then multiplied by actual placement counts; sensitive-ID
uniqueness follows checked disjoint parent fields and the unit sensor inventory.
"""
import argparse,json,math,platform,subprocess
from collections import Counter,defaultdict
from pathlib import Path
from model import ROOT,sha
from native import capacity as primitive_capacity,audit

def ids(node,dd4hep):return {str(f.first):int(f.second) for f in dd4hep.PlacedVolume(node).volIDs()}

def capacity(shape):
    if str(shape.ClassName())=='TGeoXtru':
        n=shape.GetNvert();x=[shape.GetX(i) for i in range(n)];y=[shape.GetY(i) for i in range(n)]
        a=abs(sum(float(x[i]*y[(i+1)%n]-x[(i+1)%n]*y[i]) for i in range(n)))/2
        return a*(shape.GetZ(shape.GetNz()-1)-shape.GetZ(0))
    return primitive_capacity(shape)

def run(args):
    import ROOT as R,dd4hep
    R.gROOT.SetBatch(True);R.EnableImplicitMT(1)
    if R.gSystem.Load(str(args.library.resolve()))<0:raise RuntimeError('library load')
    d=dd4hep.Detector.getInstance();expected=json.loads(args.expected.read_text());mm=float(dd4hep.mm)
    errors=[];native_regions={};replica_paths={};unit_inventory={};totals=defaultdict(lambda:dict(volume_mm3=0.,mass_g=0.));parents=0;sample_ids=set()
    def agree(actual,want,label):
        if not math.isclose(actual,want,rel_tol=1e-8,abs_tol=1e-6):errors.append(label)
    def check_pose(node,p):
        matrix=node.GetMatrix();t=matrix.GetTranslation();rot=matrix.GetRotationMatrix()
        for i in range(3):
            agree(t[i]/mm,p['center_mm'][i],'translation')
            for j in range(3):agree(rot[3*i+j],p['frame'][j][i],'rotation')
    def material_part(node,p):
        v=node.GetVolume();vol=capacity(v.GetShape())/mm**3;mat=v.GetMaterial();mass=vol*mat.GetDensity()/1000
        agree(vol,p['volume_mm3'],'capacity:'+p['name']);agree(mass,p['mass_g'],'mass:'+p['name'])
        if str(mat.GetName())!=p['material']:errors.append('material:'+p['name'])
        return dict(material=p['material'],volume_mm3=vol,mass_g=mass)
    try:
        d.fromXML(str(args.compact.resolve()));manager=d.manager()
        for top in [manager.GetTopVolume().GetNode(i) for i in range(manager.GetTopVolume().GetNdaughters())]:
            unit_name=str(top.GetVolume().GetName()).lower();u=next((u for u in expected['units'] if u['name']==unit_name),None)
            if not u:continue
            if ids(top,dd4hep)!={'system':u['system_id']}:errors.append('system identifier')
            for i in range(top.GetVolume().GetNdaughters()):
                replica=top.GetVolume().GetNode(i);volume=replica.GetVolume();name=str(volume.GetName());r=next(r for r in expected['regions'] if r['name']==name);rid=ids(replica,dd4hep)
                p=next(p for p in expected['replicas'] if p['region']==name and p['side']==rid['side'] and p['sector']==rid['sector']);check_pose(replica,p)
                replica_paths[str(replica.GetName())]=dict(system=u['system_id'],**rid)
                if name not in native_regions:
                    structural=[];placements={};seen=set();offset=len(r['parts'])
                    if volume.GetNdaughters()!=offset+len(r['placements']):errors.append('region daughter count')
                    for j,part in enumerate(r['parts']):
                        node=volume.GetNode(j);check_pose(node,part)
                        if str(node.GetVolume().GetName())!=part['name']:errors.append('structural name')
                        structural.append(material_part(node,part))
                    for j,placement in enumerate(r['placements']):
                        node=volume.GetNode(offset+j);check_pose(node,placement);pid=ids(node,dd4hep)
                        if pid!={k:placement[k] for k in ('layer','cassette')}:errors.append('parent ID')
                        key=(pid['layer'],pid['cassette'])
                        if key in seen:errors.append('duplicate cassette parent')
                        seen.add(key);placements[str(node.GetName())]=pid
                        if unit_name not in unit_inventory:
                            unit=node.GetVolume();parts=[p for p in u['parts'] if p['owner']=='cassette'];material=[];sensitive={}
                            if unit.GetNdaughters()!=len(parts):errors.append('absorber ownership or unit count')
                            for k,part in enumerate(parts):
                                leaf=unit.GetNode(k);check_pose(leaf,part);material.append(material_part(leaf,part))
                                if dd4hep.Volume(leaf.GetVolume()).isSensitive():
                                    sid=ids(leaf,dd4hep)
                                    if sid!={'sensor':part['sensor']}:errors.append('sensor identifier')
                                    sensitive[str(leaf.GetName())]=sid
                            if len(sensitive)!=u['sensitive_count']:errors.append('unit sensitive count')
                            unit_inventory[unit_name]=dict(material=material,sensitive=sensitive)
                    native_regions[name]=dict(structural=structural,placements=placements,replicas=0)
                nr=native_regions[name];nr['replicas']+=1;n=len(nr['placements']);parents+=n
                for part in nr['structural']:
                    for k in ('volume_mm3','mass_g'):totals[part['material']][k]+=part[k]
                for part in unit_inventory[unit_name]['material']:
                    for k in ('volume_mm3','mass_g'):totals[part['material']][k]+=n*part[k]
                # Native inherited-ID round trips for first/last parent and
                # first/last sensor of every physical sector replica.
                ro=d.readout(unit_name.upper()+'Hits');decoder=ro.idSpec().decoder();pids=list(nr['placements'].values());sids=list(unit_inventory[unit_name]['sensitive'].values())
                for pid in (pids[0],pids[-1]):
                    for sid in (sids[0],sids[-1]):
                        fields=dict(system=u['system_id'],**rid,**pid,**sid);vec=R.std.vector('pair<string,int>')()
                        for k,v in fields.items():vec.emplace_back(k,v)
                        vid=int(ro.idSpec().encode(vec))
                        if vid in sample_ids:errors.append('duplicate sampled ID')
                        sample_ids.add(vid)
                        for k,v in fields.items():
                            if decoder.get(vid,k)!=v:errors.append('sample ID decode')
        for r in expected['regions']:
            n=native_regions[r['name']];want=sum(p['region']==r['name'] for p in expected['replicas'])
            if n['replicas']!=want:errors.append('replica count')
        if parents!=sum(s['cassettes'] for s in expected['summary']):errors.append('physical cassette count')
        for m,t in expected['material_totals'].items():
            for key in ('volume_mm3','mass_g'):agree(totals[m][key],t[key],'full total '+m)
        manager.CheckOverlaps(1e-5*mm)
        overlaps=[dict(description=str(x.GetTitle()),penetration_mm=float(x.GetOverlap())/mm) for x in manager.GetListOfOverlaps()]
        if overlaps:errors.append('overlaps:'+str(len(overlaps)))
        class SensitivePaths:
            def __contains__(self,path):return any(path.rsplit('/',1)[-1] in unit_inventory[u]['sensitive'] for u in unit_inventory)
            def __getitem__(self,path):
                chunks=path.split('/');region_node=next(x for x in chunks if x in replica_paths);parent=replica_paths[region_node];name=next(r for r in native_regions if region_node.startswith(r+'_'));cassette=next(x for x in chunks if x in native_regions[name]['placements'])
                return {'ids':dict(**parent,**native_regions[name]['placements'][cassette])}
        rays=[]
        for eta in (0,.5,1.,1.4,1.7,2.,2.4,2.8,3.2,3.6):
            for sign in (-1,1) if eta else (1,):
                for phi in (.03,math.pi/16-.003,math.pi/16+.003):
                    e=sign*eta;direction=[math.cos(phi)/math.cosh(e),math.sin(phi)/math.cosh(e),math.tanh(e)]
                    ray=audit.trace_ray(manager,dd4hep,[0,0,0],direction,SensitivePaths(),max_length_mm=10000);ray.update(eta=e,phi=phi);rays.append(ray)
        rootfile=args.output.with_suffix('.root');manager.Export(str(rootfile.resolve()))
        report=dict(status='PASS' if not errors else 'FAIL',errors=errors,scope='Every native logical cassette/structural placement and physical sector replica; shared capacities scaled by actual counts. IDs bounded/proved by parent/sensor fields,384 sample round trips; no engineering/performance acceptance.',
            execution=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),python=platform.python_version(),ROOT=R.gROOT.GetVersion(),compact_sha256=sha(args.compact),expected_sha256=sha(args.expected),factory_sha256=sha(ROOT/'prototypes/calorimeter/Calorimeter.cpp'),library_sha256=sha(args.library),validator_sha256=sha(__file__),shared_ray_sha256=sha(ROOT/'tools/pixel_barrel_dd4hep/validate.py')),
            physical_cassettes=parents,physical_sensitive_elements=sum(s['sensitive_elements'] for s in expected['summary']),sampled_native_ID_roundtrips=len(sample_ids),regions={k:dict(logical_cassettes=len(v['placements']),replicas=v['replicas'],structural_parts=len(v['structural'])) for k,v in native_regions.items()},material_totals=dict(totals),mass_g=sum(t['mass_g'] for t in totals.values()),overlap_tolerance_mm=1e-5,overlaps=overlaps,material_rays=rays,root_sha256=sha(rootfile))
        args.output.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],parents,'cassettes',len(overlaps),'overlaps',len(rays),'rays',errors[:5]);return 1 if errors else 0
    finally:R.DisableImplicitMT();dd4hep.Detector.destroyInstance()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--compact',type=Path,required=True);p.add_argument('--expected',type=Path,required=True);p.add_argument('--library',type=Path,required=True);p.add_argument('--output',type=Path,required=True);raise SystemExit(run(p.parse_args()))
