"""Native DES033 turbine shape, placement, exclusive mass, raw-ID/readout and ray audit.

Analytic capacity is derived from native primitive vertices and circular bounds;
ROOT's stochastic Boolean Capacity() is not treated as exact mass evidence.
"""
import argparse
from array import array
from collections import Counter, defaultdict
import importlib.util
import json
import math
from pathlib import Path
import platform
import subprocess
from endcap_geometry import ROOT, gap_point, volume as integrated_volume, polygon_at, sha
from barrel_geometry import annular_area


def run(args):
    import ROOT as R
    import dd4hep
    R.gROOT.SetBatch(True)
    R.EnableImplicitMT(1)
    R.gRandom.SetSeed(41)
    if R.gSystem.Load(str(args.library.resolve())) < 0:
        raise RuntimeError('Turbine factory library load failed')
    expected = json.loads(args.expected.read_text())
    errors = []
    for name, wanted in expected['source_sha256'].items():
        path = ROOT/name
        if not path.is_file() or sha(path) != wanted:
            raise ValueError('Expected inventory has a stale source binding: '+name)
    for name, wanted in expected.get('artifact_sha256', {}).items():
        path = args.compact.parent/name
        if not path.is_file() or sha(path) != wanted:
            raise ValueError('Expected inventory has a stale compact/material binding: '+name)
    mm = float(dd4hep.mm)
    detector = dd4hep.Detector.getInstance()
    checked_shapes = {}
    totals = defaultdict(lambda: dict(volume_mm3=0., mass_g=0.))
    composition = {}
    max_composition_delta = 0.
    counters = Counter()
    raw_ids = {}
    sensor_paths = {}
    report = {}

    def agree(actual, wanted, label, rel=1e-8, absolute=1e-6):
        if not math.isclose(float(actual), float(wanted), rel_tol=rel, abs_tol=absolute):
            errors.append(label)

    def fields(node):
        return {str(f.first):int(f.second) for f in dd4hep.PlacedVolume(node).volIDs()}

    def pose(node, piece):
        matrix = node.GetMatrix()
        t, a = matrix.GetTranslation(), matrix.GetRotationMatrix()
        for i in range(3):
            agree(t[i]/mm, piece['center_mm'][i], 'translation:'+piece.get('name', 'replica'))
            for j in range(3):
                agree(a[3*i+j], piece['frame'][j][i], 'rotation:'+piece.get('name', 'replica'))
        determinant = a[0]*(a[4]*a[8]-a[5]*a[7])-a[1]*(a[3]*a[8]-a[5]*a[6])+a[2]*(a[3]*a[7]-a[4]*a[6])
        agree(determinant, 1, 'improper transform')

    def shape_capacity(shape, piece):
        # Validate the entire native Boolean hierarchy, including exact cutter
        # poses. Exclusive daughter displacement is separately audited below.
        if piece.get('cuts'):
            node = shape.GetBoolNode()
            if str(node.ClassName()) != 'TGeoSubtraction':
                raise ValueError('Expected subtraction shape')
            cut = piece['cuts'][-1]
            left = dict(piece); left['cuts'] = piece['cuts'][:-1]
            right = shape_capacity(node.GetRightShape(), cut)
            matrix = node.GetRightMatrix()
            if matrix:
                t, a = matrix.GetTranslation(), matrix.GetRotationMatrix()
                for i in range(3):
                    agree(t[i]/mm, cut['center_mm'][i], 'cut translation')
                    for j in range(3):
                        agree(a[3*i+j], cut['frame'][j][i], 'cut rotation')
            return shape_capacity(node.GetLeftShape(), left)-right
        if 'clip_annulus_mm' in piece:
            boolean = shape.GetBoolNode()
            if str(boolean.ClassName()) != 'TGeoIntersection': raise ValueError('Expected circular turbine intersection')
            tube = boolean.GetRightShape()
            if str(tube.ClassName()) not in ('TGeoTube','TGeoTubeSeg'): raise ValueError('Expected native annulus')
            if str(tube.ClassName()) == 'TGeoTubeSeg': agree(tube.GetPhi2()-tube.GetPhi1(),360,'full clipping circle')
            a = piece['clip_annulus_mm'];half=piece['half_z_mm'] if piece['shape_kind']=='arb8' else piece['depth_mm']/2
            agree(tube.GetRmin()/mm,a['rmin'],'clip inner circle');agree(tube.GetRmax()/mm,a['rmax'],'clip outer circle');agree(tube.GetDz()/mm,half,'clip half depth')
            left_matrix=boolean.GetLeftMatrix()
            if left_matrix:
                for i in range(3):
                    agree(left_matrix.GetTranslation()[i],0,'clip left translation')
                    for j in range(3):agree(left_matrix.GetRotationMatrix()[3*i+j],int(i==j),'clip left rotation')
            matrix=boolean.GetRightMatrix()
            if matrix:
                for i in range(3):
                    agree(matrix.GetTranslation()[i],0,'clip translation')
                    for j in range(3):agree(matrix.GetRotationMatrix()[3*i+j],int(i==j),'clip rotation')
            primitive=boolean.GetLeftShape();plain=dict(piece);plain.pop('clip_annulus_mm');shape_capacity(primitive,plain)
            if piece['shape_kind']=='arb8':
                values=primitive.GetVertices();vertices=[[float(values[2*i])/mm,float(values[2*i+1])/mm] for i in range(8)]
                n=piece['capacity_convergence']['fine_steps']
                value=integrated_volume(vertices,primitive.GetDz()/mm,tube.GetRmin()/mm,tube.GetRmax()/mm,n)
                coarse=integrated_volume(vertices,primitive.GetDz()/mm,tube.GetRmin()/mm,tube.GetRmax()/mm,n//2)
                if abs(value-coarse)/value>piece['capacity_convergence']['tolerance']:errors.append('native analytic capacity refinement')
                return value
            vertices=[[float(primitive.GetX(i))/mm,float(primitive.GetY(i))/mm] for i in range(primitive.GetNvert())]
            return annular_area(vertices,tube.GetRmin()/mm,tube.GetRmax()/mm)*(primitive.GetZ(primitive.GetNz()-1)-primitive.GetZ(0))/mm
        kind = piece['shape_kind']
        if kind == 'arb8':
            if str(shape.ClassName()) != 'TGeoArb8':raise ValueError('Expected native turbine Arb8')
            agree(shape.GetDz()/mm,piece['half_z_mm'],'Arb8 half depth')
            values=shape.GetVertices();vertices=[]
            for i,wanted in enumerate(piece['vertices_mm']):
                point=[float(values[2*i])/mm,float(values[2*i+1])/mm]
                for k in range(2):agree(point[k],wanted[k],'Arb8 vertex')
                vertices.append(point)
            def area(z):
                p=polygon_at(vertices,shape.GetDz()/mm,z)
                return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))/2
            half=shape.GetDz()/mm
            return 2*half/6*(area(-half)+4*area(0)+area(half))
        if kind == 'xtru':
            if str(shape.ClassName()) != 'TGeoXtru': raise ValueError('Expected extrusion')
            if shape.GetNz() != 2: raise ValueError('Extrusion must have exactly two sections')
            for section in range(2):
                agree(shape.GetXOffset(section)/mm, 0, 'extrusion x offset')
                agree(shape.GetYOffset(section)/mm, 0, 'extrusion y offset')
                agree(shape.GetScale(section), 1, 'extrusion section scale')
            if shape.GetNvert() != len(piece['vertices_mm']): raise ValueError('Extrusion vertex count')
            if shape.GetNz() != 2: raise ValueError('Xtru requires exactly two sections')
            for section in range(2):
                agree(shape.GetXOffset(section)/mm,0,'Xtru x offset')
                agree(shape.GetYOffset(section)/mm,0,'Xtru y offset')
                agree(shape.GetScale(section),1,'Xtru unit scale')
            vertices = []
            for i, want in enumerate(piece['vertices_mm']):
                xy = [float(shape.GetX(i))/mm, float(shape.GetY(i))/mm]
                for k in range(2): agree(xy[k], want[k], 'extrusion vertex')
                vertices.append(xy)
            agree(shape.GetZ(0)/mm, -piece['depth_mm']/2, 'extrusion first face')
            agree(shape.GetZ(shape.GetNz()-1)/mm, piece['depth_mm']/2, 'extrusion last face')
            area = abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(vertices,vertices[1:]+vertices[:1])))/2
            return area*piece['depth_mm']
        if kind == 'tube':
            if str(shape.ClassName()) not in ('TGeoTube','TGeoTubeSeg'): raise ValueError('Expected tube')
            if str(shape.ClassName()) == 'TGeoTubeSeg': agree(shape.GetPhi2()-shape.GetPhi1(), 360, 'tube full azimuth')
            dims = piece['dimensions_mm']
            for actual, key in ((shape.GetRmin()/mm, 'rmin'), (shape.GetRmax()/mm, 'rmax'), (2*shape.GetDz()/mm, 'length')):
                agree(actual, dims[key], 'tube '+key)
            return math.pi*((shape.GetRmax()/mm)**2-(shape.GetRmin()/mm)**2)*2*shape.GetDz()/mm
        if kind == 'box':
            if str(shape.ClassName()) != 'TGeoBBox': raise ValueError('Expected box')
            dims = piece['dimensions_mm']
            for actual,key in ((2*shape.GetDX()/mm,'sx'),(2*shape.GetDY()/mm,'sy'),(2*shape.GetDZ()/mm,'sz')):
                agree(actual,dims[key],'box '+key)
            return 8*shape.GetDX()*shape.GetDY()*shape.GetDZ()/mm**3
        raise ValueError('Unknown native primitive')

    elements = json.loads((ROOT/'detector/config/elements.json').read_text())['elements']
    element_map = {e['name']:e for e in elements}
    def elemental(name):
        if name in element_map:
            return {element_map[name]['Z']:1.}
        recipe = expected['materials'][name]
        weights = {k:v*element_map[k]['A'] if recipe['basis'] == 'atom_count' else v for k,v in recipe['composition'].items()}
        norm = sum(weights.values()); result = defaultdict(float)
        for name, weight in weights.items():
            for z, fraction in elemental(name).items(): result[z] += weight/norm*fraction
        return dict(result)

    def material(volume, piece):
        nonlocal max_composition_delta
        name = str(volume.GetName())
        if name in checked_shapes: return checked_shapes[name]
        capacity = shape_capacity(volume.GetShape(), piece)
        agree(capacity, piece['volume_mm3'], 'full capacity:'+name)
        native_material = volume.GetMaterial(); mat_name = str(native_material.GetName())
        if mat_name != piece['material']: errors.append('material name:'+name)
        agree(native_material.GetDensity(), expected['materials'][piece['material']]['density_g_cm3'], 'density:'+name)
        if mat_name not in composition:
            want = elemental(mat_name)
            if native_material.IsMixture():
                actual = {int(native_material.GetElement(i).Z()):float(native_material.GetWmixt()[i]) for i in range(native_material.GetNelements())}
            else: actual = {int(native_material.GetZ()):1.}
            delta = max(abs(want.get(z,0)-actual.get(z,0)) for z in set(want)|set(actual))
            max_composition_delta = max(max_composition_delta,delta)
            if delta > 1e-8: errors.append('elemental composition:'+mat_name)
            composition[mat_name] = actual
        checked_shapes[name] = capacity
        return capacity

    try:
        detector.fromXML(str(args.compact.resolve()));manager=detector.manager()
        top=next(manager.GetTopVolume().GetNode(i) for i in range(manager.GetTopVolume().GetNdaughters()) if str(manager.GetTopVolume().GetNode(i).GetVolume().GetName())=='LArEndcaps')
        system=expected['readout']['system_id'];assembly=top.GetVolume()
        if fields(top)!={'system':system}:errors.append('system ID')
        ro=detector.readout(expected['readout']['name']);decoder=ro.idSpec().decoder();segmentation=ro.segmentation()
        if not segmentation.cellsSpanVolumes():errors.append('missing two-gap merged readout flag')
        def packed(ids):
            vec=R.std.vector('pair<string,int>')()
            for k,v in ids.items():vec.emplace_back(k,v)
            result=int(ro.idSpec().encode(vec))
            for k,v in ids.items():
                if int(decoder.get(result,k))!=v:errors.append('ID field roundtrip:'+k)
            return result
        wheel_models={w['wheel']:w for w in expected['wheels']};native_wheels={};native_replicas={};raw_set=set();mass_by_role=defaultdict(float)
        role_by_name={p['name']:p['role'] for w in expected['wheels'] for p in w['pieces']}
        role_by_name.update({p['name']:p['role'] for p in expected['passive']})
        for i,r in enumerate(expected['replicas']):
            node=assembly.GetNode(i);pose(node,r);ids={k:r[k] for k in ('side','wheel','plane')}
            if fields(node)!=ids:errors.append('physical turbine replica IDs')
            w=wheel_models[r['wheel']];native=node.GetVolume();native_wheels[r['wheel']]=native;native_replicas[(r['side'],r['wheel'],r['plane'])]=node
            if str(native.GetName())!='TurbineWheel'+str(r['wheel']) or native.GetNdaughters()!=len(w['pieces']):errors.append('wheel period inventory')
            for k,p in enumerate(w['pieces']):
                leaf=native.GetNode(k);name=str(leaf.GetVolume().GetName())
                if name!=p['name']:errors.append('wheel piece name')
                if name not in checked_shapes:pose(leaf,p);material(leaf.GetVolume(),p)
                capacity=checked_shapes[name];mass=capacity*leaf.GetVolume().GetMaterial().GetDensity()/1000
                agree(mass,p['mass_g'],'piece analytic mass')
                totals[p['material']]['volume_mm3']+=capacity;totals[p['material']]['mass_g']+=mass;mass_by_role[p['role']]+=mass;counters[p['role']]+=1
                sensitive=bool(dd4hep.Volume(leaf.GetVolume()).isSensitive())
                if sensitive!=(p['role']=='sensitive'):errors.append('sensitive flag')
                if sensitive:
                    if fields(leaf)!={'gap':p['gap']}:errors.append('physical gap ID')
                    f=dict(system=system,**ids,**fields(leaf));raw=packed(f)
                    if raw in raw_set:errors.append('duplicate raw turbine volume ID')
                    raw_set.add(raw);raw_ids[(r['side'],r['wheel'],r['plane'],p['gap'])]=raw
                    path='/'+str(manager.GetTopNode().GetName())+'/'+str(top.GetName())+'/'+str(node.GetName())+'/'+str(leaf.GetName())
                    # Shared tracker-ray helper's layer aggregation is renamed to
                    # wheel explicitly below; this adds no physical ID field.
                    sensor_paths[path]=dict(ids=dict(f,layer=r['wheel']))
                elif fields(leaf):errors.append('passive wheel leaf has readout IDs')
        if len(raw_set)!=expected['physical_sensitive_elements']:errors.append('raw sensitive count')
        if len(native_replicas)!=2*sum(w['periods'] for w in expected['wheels']):errors.append('physical wheel/plane count')
        passive_models={p['name']:p for p in expected['passive']};visited=set()
        def passive(node,parent=None):
            name=str(node.GetVolume().GetName());p=passive_models[name]
            if p.get('parent_name')!=parent:errors.append('passive mother identity')
            if name in visited:errors.append('duplicate passive placement')
            visited.add(name);pose(node,p);full=material(node.GetVolume(),p);displaced=0.
            for k in range(node.GetVolume().GetNdaughters()):
                child=node.GetVolume().GetNode(k);cp=passive_models[str(child.GetVolume().GetName())];displaced+=material(child.GetVolume(),cp);passive(child,name)
            exclusive=full-displaced;agree(exclusive,p.get('exclusive_volume_mm3',p['volume_mm3']),'exclusive mother capacity')
            if 'displaced_volume_mm3' in p:agree(displaced,p['displaced_volume_mm3'],'declared displacement')
            mass=exclusive*node.GetVolume().GetMaterial().GetDensity()/1000;agree(mass,p['mass_g'],'exclusive passive mass')
            totals[p['material']]['volume_mm3']+=exclusive;totals[p['material']]['mass_g']+=mass;mass_by_role[p['role']]+=mass;counters[p['role']]+=1
        for i in range(len(expected['replicas']),assembly.GetNdaughters()):passive(assembly.GetNode(i))
        if visited!=set(passive_models):errors.append('passive inventory')
        for name,wanted in expected['material_totals'].items():
            for key in ('volume_mm3','mass_g'):agree(totals[name][key],wanted[key],'material ledger:'+name)
        if set(totals)!=set(expected['material_totals']):errors.append('material names')
        reference_checks=inverse_checks=boundary_checks=0
        for wi,w in wheel_models.items():
            native=native_wheels[wi];gap0=next(p for p in w['pieces'] if p.get('gap')==0)
            volume0=next(native.GetNode(i).GetVolume() for i,p in enumerate(w['pieces']) if p['name']==gap0['name'])
            for ref in w['reference_points']:
                cell=packed(dict(system=system,side=1,wheel=wi,plane=0,gap=0,rho=ref['rho'],z=ref['z']));pos=segmentation.position(cell);point=[pos.x()/mm,pos.y()/mm,pos.z()/mm]
                for k in range(3):agree(point[k],ref['position_mm'][k],'canonical turbine reference')
                if not volume0.GetShape().Contains(array('d',[v*mm for v in point])):errors.append('reference outside canonical native gap')
                if int(segmentation.volumeID(cell))!=raw_ids[(1,wi,0,0)]:errors.append('canonical physical-volume inverse')
                reference_checks+=1;r=math.hypot(*point[:2])
                for side in (1,2):
                    for plane in (0,w['periods']-1):
                        for gap in (0,1):
                            p=next(p for p in w['pieces'] if p.get('gap')==gap);hit=gap_point(p,r,point[2]);local=array('d',[v*mm for v in hit]);global_point=array('d',[0,0,0]);native_replicas[(side,wi,plane)].GetMatrix().LocalToMaster(local,global_point)
                            actual=int(segmentation.cellID(dd4hep.Position(*local),dd4hep.Position(*global_point),raw_ids[(side,wi,plane,gap)]))
                            wanted=packed(dict(system=system,side=side,wheel=wi,plane=plane,gap=0,rho=ref['rho'],z=ref['z']))
                            if actual!=wanted or int(segmentation.volumeID(actual))!=raw_ids[(side,wi,plane,0)]:errors.append('native two-gap/readout inverse')
                            inverse_checks+=1
            # Exercise internal radial and axial boundaries from both sides.
            for ir in range(1,w['radial_bins']):
                boundary=w['inner_radius_mm']+ir*(w['outer_radius_mm']-w['inner_radius_mm'])/w['radial_bins']
                for sign in (-1,1):
                    point=gap_point(gap0,boundary+sign*1e-6,0);p=dd4hep.Position(*[v*mm for v in point]);cell=int(segmentation.cellID(p,p,raw_ids[(1,wi,0,0)]))
                    if int(decoder.get(cell,'rho'))!=ir-(sign<0):errors.append('radial boundary mapping')
                    boundary_checks+=1
            for iz in range(1,expected['readout']['axial_bins']):
                boundary=-expected['readout']['sampling_depth_mm']/2+iz*expected['readout']['sampling_depth_mm']/expected['readout']['axial_bins']
                for sign in (-1,1):
                    point=gap_point(gap0,(w['inner_radius_mm']+w['outer_radius_mm'])/2,boundary+sign*1e-6);p=dd4hep.Position(*[v*mm for v in point]);cell=int(segmentation.cellID(p,p,raw_ids[(1,wi,0,0)]))
                    if int(decoder.get(cell,'z'))!=iz-(sign<0):errors.append('axial boundary mapping')
                    boundary_checks+=1
            for key,index in (('rho',w['radial_bins']),('z',expected['readout']['axial_bins'])):
                ids=dict(system=system,side=1,wheel=wi,plane=0,gap=0,rho=0,z=0);ids[key]=index
                try:segmentation.position(packed(ids))
                except Exception:boundary_checks+=1
                else:errors.append('ghost turbine grid address accepted')
        derived=2*sum(w['periods']*len(w['reference_points']) for w in expected['wheels'])
        if derived!=expected['logical_channels']:errors.append('derived cell count')
        manager.CheckOverlaps(expected['config']['overlap_tolerance_mm']*mm)
        overlaps=[dict(description=str(x.GetTitle()),penetration_mm=float(x.GetOverlap())/mm) for x in manager.GetListOfOverlaps()]
        if overlaps:errors.append('native overlaps/extrusions:'+str(len(overlaps)))
        specification=importlib.util.spec_from_file_location('tracker_ray_audit',ROOT/'tools/pixel_barrel_dd4hep/validate.py');audit=importlib.util.module_from_spec(specification);specification.loader.exec_module(audit)
        rays=[]
        for absolute in (1.3,1.8,2.3,2.8,3.2,4.):
            for sign in (-1,1):
                eta=absolute*sign
                for phi in (0.,.001,.007,.37,1.11):
                    direction=[math.cos(phi)/math.cosh(eta),math.sin(phi)/math.cosh(eta),math.tanh(eta)]
                    ray=audit.trace_ray(manager,dd4hep,[0,0,0],direction,sensor_paths,max_length_mm=9000);ray.update(eta=eta,phi_rad=phi)
                    ray['hits_by_wheel']=ray.pop('hits_by_layer');ray['hits_by_detector_wheel']=ray.pop('hits_by_detector_layer');ray['crossed_wheels']=ray.pop('crossed_layers')
                    manager.InitTrack(0,0,0,*direction);nav=manager.GetCurrentNavigator();distance=0.;active=0.;support=0.;steps=0
                    while not nav.IsOutside() and distance<9000:
                        path=str(nav.GetPath());name=str(nav.GetCurrentNode().GetVolume().GetName());nav.FindNextBoundaryAndStep((9000-distance)*mm);length=float(nav.GetStep())/mm
                        if not math.isfinite(length) or length<=0:raise RuntimeError('Invalid turbine material navigation step')
                        if path in sensor_paths:active+=length
                        if role_by_name.get(name)=='wheel_support':support+=length
                        distance+=length;steps+=1
                        if steps>100000:raise RuntimeError('Turbine material ray did not terminate')
                    ray.update(active_LAr_path_mm=active,wheel_support_path_mm=support);rays.append(ray)
        root_file=args.output.with_suffix('.root');args.output.parent.mkdir(parents=True,exist_ok=True);manager.Export(str(root_file.resolve()))
        report=dict(status='FAIL' if errors else 'PASS',errors=errors,scope='Every physical wheel period/raw gap ID, shared primitive/material and canonical virtual-cell reference. Proper signed-end transforms. No response/engineering acceptance.',execution=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),python=platform.python_version(),ROOT=R.gROOT.GetVersion(),compact_sha256=sha(args.compact),expected_sha256=sha(args.expected),library_sha256=sha(args.library),factory_sha256=sha(ROOT/'prototypes/calorimeter/LArEndcap.cpp'),validator_sha256=sha(__file__),geometry_sha256=sha(ROOT/'tools/lar_calorimeter/endcap_geometry.py'),ray_helper_sha256=sha(ROOT/'tools/pixel_barrel_dd4hep/validate.py')),physical_sensitive_volume_ids=len(raw_set),physical_wheel_periods=len(native_replicas),native_shared_shapes=len(checked_shapes),passive_nodes=len(visited),counts=dict(counters),mass_by_role_g=dict(mass_by_role),material_totals=dict(totals),mass_g=sum(v['mass_g'] for v in totals.values()),material_elemental_mass_fractions=composition,composition_max_abs_delta=max_composition_delta,capacity_method='Native Arb8 vertices/circular bounds with exact cross-sectional area and converged Simpson integral; passive mothers exclude actual daughters.',canonical_reference_keys_checked=reference_checks,grouped_gap_inverse_checks=inverse_checks,boundary_and_ghost_checks=boundary_checks,derived_logical_channels=derived,overlap_seed=41,overlap_tolerance_mm=expected['config']['overlap_tolerance_mm'],overlaps=overlaps,material_rays=rays,root_sha256=sha(root_file))
        args.output.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(raw_set),'raw IDs;',derived,'virtual cells;',len(overlaps),'overlaps;',errors[:6]);return bool(errors)
    finally:
        R.DisableImplicitMT();dd4hep.Detector.destroyInstance()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--compact',type=Path,required=True);p.add_argument('--expected',type=Path,required=True);p.add_argument('--library',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    raise SystemExit(run(p.parse_args()))
