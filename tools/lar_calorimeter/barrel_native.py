"""Native DES032 shape, placement, exclusive mass, raw-ID/readout and ray audit.

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
from barrel_geometry import ROOT, annular_area, canonical_reference, point_on_gap, sha


def run(args):
    import ROOT as R
    import dd4hep
    R.gROOT.SetBatch(True)
    R.EnableImplicitMT(1)
    R.gRandom.SetSeed(37)
    if R.gSystem.Load(str(args.library.resolve())) < 0:
        raise RuntimeError('LAr factory library load failed')
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
            if str(boolean.ClassName()) != 'TGeoIntersection':
                raise ValueError('Expected circular annulus intersection')
            a = boolean.GetRightShape()
            if str(a.ClassName()) not in ('TGeoTube', 'TGeoTubeSeg'):
                raise ValueError('Expected native annular clipping tube')
            if str(a.ClassName()) == 'TGeoTubeSeg':
                agree(a.GetPhi2()-a.GetPhi1(), 360, 'clip full azimuth')
            radii = piece['clip_annulus_mm']
            agree(a.GetRmin()/mm, radii['rmin'], 'clip inner circle')
            agree(a.GetRmax()/mm, radii['rmax'], 'clip outer circle')
            agree(a.GetDz()/mm, piece['depth_mm']/2, 'clip depth')
            matrix = boolean.GetRightMatrix()
            if matrix:
                for i in range(3):
                    agree(matrix.GetTranslation()[i], 0, 'clip translation')
                    for j in range(3): agree(matrix.GetRotationMatrix()[3*i+j], int(i == j), 'clip rotation')
            matrix = boolean.GetLeftMatrix()
            if matrix:
                for i in range(3):
                    agree(matrix.GetTranslation()[i], 0, 'primitive translation')
                    for j in range(3): agree(matrix.GetRotationMatrix()[3*i+j], int(i == j), 'primitive rotation')
            primitive = boolean.GetLeftShape()
            plain = dict(piece); plain.pop('clip_annulus_mm')
            shape_capacity(primitive, plain)
            vertices = [[float(primitive.GetX(i))/mm, float(primitive.GetY(i))/mm] for i in range(primitive.GetNvert())]
            return annular_area(vertices, a.GetRmin()/mm, a.GetRmax()/mm)*(primitive.GetZ(primitive.GetNz()-1)-primitive.GetZ(0))/mm
        kind = piece['shape_kind']
        if kind == 'xtru':
            if str(shape.ClassName()) != 'TGeoXtru': raise ValueError('Expected extrusion')
            if shape.GetNz() != 2: raise ValueError('Extrusion must have exactly two sections')
            for section in range(2):
                agree(shape.GetXOffset(section)/mm, 0, 'extrusion x offset')
                agree(shape.GetYOffset(section)/mm, 0, 'extrusion y offset')
                agree(shape.GetScale(section), 1, 'extrusion section scale')
            if shape.GetNvert() != len(piece['vertices_mm']): raise ValueError('Extrusion vertex count')
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
        detector.fromXML(str(args.compact.resolve()))
        manager = detector.manager()
        top = next(manager.GetTopVolume().GetNode(i) for i in range(manager.GetTopVolume().GetNdaughters()) if str(manager.GetTopVolume().GetNode(i).GetVolume().GetName()) == 'LArBarrel')
        system = expected['readout']['system_id']
        if fields(top) != {'system':system}: errors.append('root system ID')
        assembly = top.GetVolume()
        period = None
        ro = detector.readout(expected['readout']['name'])
        decoder, segmentation = ro.idSpec().decoder(), ro.segmentation()
        if not segmentation.cellsSpanVolumes(): errors.append('segmentation missing multi-volume flag')
        def packed(ids):
            vector = R.std.vector('pair<string,int>')()
            for k,v in ids.items(): vector.emplace_back(k,v)
            result = int(ro.idSpec().encode(vector))
            for k,v in ids.items():
                if int(decoder.get(result,k)) != v: errors.append('raw field roundtrip:'+k)
            return result
        physical_raw = set(); replicas = {}
        for i, replica in enumerate(expected['replicas']):
            node = assembly.GetNode(i); pose(node,replica)
            if fields(node) != {'plane':replica['plane']}: errors.append('replica plane ID')
            replicas[replica['plane']] = node
            p = node.GetVolume()
            if period is None: period = p
            if str(p.GetName()) != 'LArInclinedPeriod' or p.GetNdaughters() != len(expected['pieces']): errors.append('period physical inventory')
            for k,piece in enumerate(expected['pieces']):
                leaf = p.GetNode(k); name = str(leaf.GetVolume().GetName())
                if name != piece['name']: errors.append('period piece name')
                if i == 0:
                    pose(leaf,piece)
                    material(leaf.GetVolume(),piece)
                volume = checked_shapes[name]
                totals[piece['material']]['volume_mm3'] += volume
                totals[piece['material']]['mass_g'] += volume*leaf.GetVolume().GetMaterial().GetDensity()/1000
                counters[piece['role']] += 1
                sensitive = bool(dd4hep.Volume(leaf.GetVolume()).isSensitive())
                if sensitive != (piece['role'] == 'sensitive'): errors.append('sensitive flag:'+name)
                if sensitive:
                    ids = dict(system=system,plane=replica['plane'],**fields(leaf))
                    if fields(leaf) != {'layer':piece['layer'],'gap':piece['gap']}: errors.append('leaf physical IDs')
                    raw = packed(ids)
                    if raw in physical_raw: errors.append('duplicate native raw volume ID')
                    physical_raw.add(raw)
                    raw_ids[(replica['plane'],piece['layer'],piece['gap'])] = raw
                    path = '/'+str(manager.GetTopNode().GetName())+'/'+str(top.GetName())+'/'+str(node.GetName())+'/'+str(leaf.GetName())
                    sensor_paths[path] = dict(ids=ids)
                elif fields(leaf): errors.append('passive plate has sensitive IDs')
        if len(physical_raw) != expected['physical_sensitive_elements']: errors.append('native raw sensitive count')
        passive_by_name = {p['name']:p for p in expected['passive']}
        visited = set()
        def passive(node, parent_name=None):
            piece = passive_by_name[str(node.GetVolume().GetName())]
            if piece.get('parent_name') != parent_name: errors.append('passive parent:'+piece['name'])
            if piece['name'] in visited: errors.append('duplicate physical passive placement')
            visited.add(piece['name']); pose(node,piece)
            full = material(node.GetVolume(),piece)
            displacement = 0.
            for i in range(node.GetVolume().GetNdaughters()):
                child = node.GetVolume().GetNode(i)
                child_piece = passive_by_name[str(child.GetVolume().GetName())]
                displacement += material(child.GetVolume(),child_piece)
                passive(child,piece['name'])
            exclusive = full-displacement
            agree(exclusive,piece.get('exclusive_volume_mm3',piece['volume_mm3']),'exclusive daughter capacity:'+piece['name'])
            if 'displaced_volume_mm3' in piece: agree(displacement,piece['displaced_volume_mm3'],'displaced capacity')
            mass = exclusive*node.GetVolume().GetMaterial().GetDensity()/1000
            agree(mass,piece['mass_g'],'exclusive mass:'+piece['name'])
            totals[piece['material']]['volume_mm3'] += exclusive
            totals[piece['material']]['mass_g'] += mass
            counters[piece['role']] += 1
        for i in range(len(expected['replicas']),assembly.GetNdaughters()): passive(assembly.GetNode(i))
        if visited != set(passive_by_name): errors.append('passive inventory names/counts')
        for name,want in expected['material_totals'].items():
            for key in ('volume_mm3','mass_g'): agree(totals[name][key],want[key],'material total:'+name)
        if set(totals) != set(expected['material_totals']): errors.append('material names ledger')

        # Check each reference key against its actual canonical native shape.
        # Exact shared-volume placement/rotation is verified for every plane;
        # raw hits on first/last electrode pairs exercise canonical inverses.
        reference_checks = grouped_hit_checks = boundary_checks = 0
        canonical_ids = set()
        for layer in expected['readout']['layers']:
            li = layer['layer']
            canonical_piece = next(p for p in expected['pieces'] if p.get('gap') == 0 and p['layer'] == li)
            native_piece = next(period.GetNode(i).GetVolume() for i,p in enumerate(expected['pieces']) if p['name'] == canonical_piece['name'])
            for reference in layer['reference_points']:
                index = reference['theta_index']
                ids = dict(system=system,plane=0,layer=li,gap=0,theta=index)
                canonical = packed(ids); canonical_ids.add(canonical)
                pos = segmentation.position(canonical)
                xy = [pos.x()/mm,pos.y()/mm,pos.z()/mm]
                for k in range(3): agree(xy[k],reference['position_mm'][k],'native cell reference')
                if not native_piece.GetShape().Contains(array('d',[v*mm for v in xy])): errors.append('canonical reference outside native LAr')
                if int(segmentation.volumeID(canonical)) != raw_ids[(0,li,0)]: errors.append('canonical raw-volume inverse')
                reference_checks += 1
                radius = math.hypot(*xy[:2])
                for plane in (0,1,1534,1535):
                    for gap in (0,1):
                        piece = next(p for p in expected['pieces'] if p.get('gap') == gap and p['layer'] == li)
                        point = point_on_gap(piece,radius)+[xy[2]]
                        local = array('d',[v*mm for v in point]); global_point = array('d',[0,0,0])
                        replicas[plane].GetMatrix().LocalToMaster(local,global_point)
                        raw = raw_ids[(plane,li,gap)]
                        actual = int(segmentation.cellID(dd4hep.Position(*local),dd4hep.Position(*global_point),raw))
                        wanted = packed(dict(system=system,plane=plane//2*2,layer=li,gap=0,theta=index))
                        if actual != wanted: errors.append('grouped hit mapping')
                        if int(segmentation.volumeID(actual)) != raw_ids[(plane//2*2,li,0)]: errors.append('grouped inverse volume')
                        grouped_hit_checks += 1
            step = expected['readout']['theta_merging'][li]
            for invalid in (layer['indices'][0]-step,layer['indices'][-1]+step):
                try: segmentation.position(packed(dict(system=system,plane=0,layer=li,gap=0,theta=invalid)))
                except Exception: boundary_checks += 1
                else: errors.append('ghost theta cell accepted')
        derived_channels = reference_checks*(expected['readout']['planes']//expected['readout']['phi_merge'])
        if derived_channels != expected['logical_channels']: errors.append('derived grouped channel count')

        manager.CheckOverlaps(expected['config']['overlap_tolerance_mm']*mm)
        overlaps = [dict(description=str(x.GetTitle()),penetration_mm=float(x.GetOverlap())/mm) for x in manager.GetListOfOverlaps()]
        if overlaps: errors.append('native overlaps/extrusions:'+str(len(overlaps)))
        specification = importlib.util.spec_from_file_location('tracker_ray_audit',ROOT/'tools/pixel_barrel_dd4hep/validate.py')
        audit = importlib.util.module_from_spec(specification); specification.loader.exec_module(audit)
        rays = []
        for eta in (-2,-1.4,-1,-.5,0,.5,1,1.4,2):
            for phi in (0.,.001,math.pi/1536,.37,1.11):
                direction = [math.cos(phi)/math.cosh(eta),math.sin(phi)/math.cosh(eta),math.tanh(eta)]
                ray = audit.trace_ray(manager,dd4hep,[0,0,0],direction,sensor_paths,max_length_mm=7000)
                ray.update(eta=eta,phi_rad=phi)
                # A second navigation integral separates active gaps from passive
                # LAr core/baths, which share the same physical material recipe.
                manager.InitTrack(0,0,0,*direction); nav=manager.GetCurrentNavigator(); distance=active=0.;steps=0
                while not nav.IsOutside() and distance < 7000:
                    path=str(nav.GetPath());nav.FindNextBoundaryAndStep((7000-distance)*mm);length=float(nav.GetStep())/mm
                    if not math.isfinite(length) or length <= 0: raise RuntimeError('Invalid active-LAr ray step')
                    if path in sensor_paths: active += length
                    distance += length;steps+=1
                    if steps > 100000: raise RuntimeError('Ray navigation did not terminate')
                ray['active_LAr_path_mm'] = active
                rays.append(ray)
        root_file = args.output.with_suffix('.root')
        args.output.parent.mkdir(parents=True,exist_ok=True)
        manager.Export(str(root_file.resolve()))
        report = dict(status='FAIL' if errors else 'PASS', errors=errors, scope='Native isolated barrel. Every physical electrode replica/raw ID and all shared shape/reference keys checked; shared rotation symmetry derives full channel count. No engineering/performance acceptance.', execution=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),python=platform.python_version(),ROOT=R.gROOT.GetVersion(),compact_sha256=sha(args.compact),expected_sha256=sha(args.expected),library_sha256=sha(args.library),factory_sha256=sha(ROOT/'prototypes/calorimeter/LArBarrel.cpp'),validator_sha256=sha(__file__),geometry_sha256=sha(ROOT/'tools/lar_calorimeter/barrel_geometry.py'),ray_helper_sha256=sha(ROOT/'tools/pixel_barrel_dd4hep/validate.py')), physical_sensitive_volume_ids=len(physical_raw), physical_electrode_periods=len(replicas), native_shared_shapes=len(checked_shapes), passive_nodes=len(visited), counts=dict(counters), material_totals=dict(totals), mass_g=sum(v['mass_g'] for v in totals.values()),material_elemental_mass_fractions=composition,composition_max_abs_delta=max_composition_delta,capacity_method='Analytic integration of native primitive vertices/circles with verified native Boolean hierarchy; mother mass excludes actual daughter shapes.', canonical_reference_keys_checked=reference_checks, canonical_unique_keys=len(canonical_ids), grouped_hit_inverse_checks=grouped_hit_checks, ghost_boundary_rejections=boundary_checks, derived_logical_channels=derived_channels, overlap_seed=37,overlap_tolerance_mm=expected['config']['overlap_tolerance_mm'],overlaps=overlaps,material_rays=rays,root_sha256=sha(root_file))
        args.output.write_text(json.dumps(report,indent=2)+'\n')
        print(report['status'],len(physical_raw),'raw IDs;',derived_channels,'derived cells;',len(overlaps),'overlaps;',len(rays),'rays;',errors[:6])
        return bool(errors)
    finally:
        R.DisableImplicitMT()
        dd4hep.Detector.destroyInstance()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compact',type=Path,required=True)
    parser.add_argument('--expected',type=Path,required=True)
    parser.add_argument('--library',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    raise SystemExit(run(parser.parse_args()))
