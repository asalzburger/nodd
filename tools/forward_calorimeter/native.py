#!/usr/bin/env python3
"""DES039 isolated ROOT geometry audit; no DD4hep or Geant4 integration.

The native geometry contains the finite sampling holes, enclosure, sensor
footprints/pixels, cold plates and straight water-line allocations. Curved
optical fanout and the collar's radial collector are deliberately absent.
Lengths enter ROOT in centimetres; all JSON dimensions and paths are mm.
"""
from __future__ import annotations

import argparse
from array import array
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

from model import ROOT as REPO, build, collar_config, inventory, load_config, ray_sample, sha

HERE = Path(__file__).resolve().parent
PINNED_REVISION = '0964b60a3d19b13b91abc48e30bd18d66feb66d2'
MM = 0.1
MATERIAL_KEYS = ('tungsten', 'fused_silica', 'buffer_proxy', 'air_insertion_gap')


def capacity(shape):
    """Analytical capacities read from actual native primitive dimensions."""
    kind = str(shape.ClassName())
    if kind == 'TGeoBBox':
        return 8 * shape.GetDX() * shape.GetDY() * shape.GetDZ() / MM**3
    if kind in ('TGeoTube', 'TGeoTubeSeg'):
        fraction = (shape.GetPhi2() - shape.GetPhi1()) / 360 if kind == 'TGeoTubeSeg' else 1.
        return 2 * math.pi * (shape.GetRmax()**2 - shape.GetRmin()**2) * shape.GetDz() * fraction / MM**3
    raise ValueError('Unsupported native shape ' + kind)


class Builder:
    def __init__(self, R, manager):
        self.R, self.manager = R, manager
        self.roles, self.material_keys, self.keep = {}, {}, []
        self.media = {}
        self.medium_id = 0

    def medium(self, component, key, config=None):
        name = component + '_' + key
        if name in self.media:
            return self.media[name]
        R = self.R
        self.medium_id += 1
        q = config['materials'].get(key) if config else None
        if key in ('air', 'air_insertion_gap', 'envelope_guard'):
            material = R.TGeoMaterial(name, 14., 7., 0.0012)
            material.SetRadLen(-1.e12 * MM, -1.e12 * MM)
        elif key in ('tungsten', 'aluminium', 'silicon'):
            a, z = {'tungsten': (183.84, 74), 'aluminium': (26.9815, 13), 'silicon': (28.0855, 14)}[key]
            material = R.TGeoMaterial(name, a, z, q['density_g_cm3'])
            material.SetRadLen(-q['x0_mm'] * MM, -q['lambda_nuclear_mm'] * MM)
        else:
            elements = {'fused_silica': [(28.0855, 14, 1), (15.999, 8, 2)],
                        'buffer_proxy': [(12.011, 6, 1), (1.008, 1, 2)],
                        'water': [(1.008, 1, 2), (15.999, 8, 1)]}[key]
            material = R.TGeoMixture(name, len(elements), q['density_g_cm3'])
            total = sum(a * n for a, z, n in elements)
            for i, (a, z, n) in enumerate(elements):
                material.DefineElement(i, a, z, a * n / total)
            material.SetRadLen(-q['x0_mm'] * MM, -q['lambda_nuclear_mm'] * MM)
        if q:
            for field, getter in [('x0_mm', material.GetRadLen), ('lambda_nuclear_mm', material.GetIntLen)]:
                if not math.isclose(float(getter()) / MM, q[field], rel_tol=1.e-12):
                    raise RuntimeError('Native material reference length differs: ' + name)
        medium = R.TGeoMedium(name, self.medium_id, material)
        self.keep.extend([material, medium])
        self.media[name] = medium
        self.material_keys[name] = key
        return medium

    def volume(self, name, shape, component, material, role, config=None):
        v = self.R.TGeoVolume(name, shape, self.medium(component, material, config))
        self.roles[name] = role
        self.keep.extend([shape, v])
        return v

    def tube(self, name, inner, outer, length, component, material, role, config):
        return self.volume(name, self.R.TGeoTube(name + '_shape', inner*MM, outer*MM, length*MM/2),
                           component, material, role, config)

    def box(self, name, sizes, component, material, role, config=None):
        return self.volume(name, self.R.TGeoBBox(name + '_shape', *(s*MM/2 for s in sizes)),
                           component, material, role, config)

    def assembly(self, name):
        v = self.R.TGeoVolumeAssembly(name)
        self.roles[name] = 'assembly'
        self.keep.append(v)
        return v

    def place(self, parent, child, number, x=0., y=0., z=0., phi=0., negative=False):
        if phi or negative:
            rotation = self.R.TGeoRotation()
            if negative:
                rotation.RotateX(180.)
            if phi:
                rotation.RotateZ(phi)
            transform = self.R.TGeoCombiTrans(x*MM, y*MM, z*MM, rotation)
            self.keep.append(rotation)
        else:
            transform = self.R.TGeoTranslation(x*MM, y*MM, z*MM)
        parent.AddNode(child, number, transform)
        self.keep.append(transform)

    def component(self, model, name, pipe_end_local):
        c, z = model['config'], model['zones_mm']
        m, f, r, t = (c[k] for k in ('module', 'fibres', 'readout', 'thermal'))
        result = self.assembly(name)
        sf, sb = z['sampling']; length = sb-sf
        matrices = []
        gap = m['half_seam_half_angle_deg']
        for half, (a, b) in enumerate(((-90+gap, 90-gap), (90+gap, 270-gap))):
            shape = self.R.TGeoTubeSeg(name+'_matrix_shape_'+str(half),
                                      m['sampling_inner_radius_mm']*MM,
                                      m['sampling_outer_radius_mm']*MM, length*MM/2, a, b)
            v = self.volume(name+'_matrix_'+str(half), shape, name, 'tungsten', 'matrix_half', c)
            matrices.append(v)
            self.place(result, v, half+1, z=(sf+sb)/2)
        holes = []
        for population in (0, 1):
            front = sf + (f['short_start_mm'] if population else 0.)
            ln = sb-front
            tag = name+('_short' if population else '_long')
            hole = self.tube(tag+'_hole', 0., f['hole_radius_mm'], ln, name, 'air_insertion_gap', 'hole', c)
            buffer = self.tube(tag+'_buffer', 0., f['buffer_outer_radius_mm'], ln, name, 'buffer_proxy', 'buffer', c)
            core = self.tube(tag+'_silica', 0., f['core_radius_mm'], ln, name, 'fused_silica', 'silica_core', c)
            self.place(hole, buffer, 1)
            self.place(buffer, core, 1)
            holes.append(hole)
        for fibre in model['fibres']:
            center = (fibre['z0_mm']+fibre['z1_mm'])/2 - (sf+sb)/2
            self.place(matrices[fibre['half']], holes[fibre['population']], fibre['index']+1,
                       x=fibre['x_mm'], y=fibre['y_mm'], z=center)
        structural = [
            ('inner_sleeve', m['bore_radius_mm'], m['inner_shell_outer_mm'], 0., m['length_mm']),
            ('sampling_shell', m['sampling_shell_inner_mm'], m['outer_radius_mm'], 0., sb),
            ('rear_shell', m['rear_shell_inner_mm'], m['outer_radius_mm'], sb, m['length_mm']),
            ('front_cap', m['inner_shell_outer_mm'], m['sampling_shell_inner_mm'], 0., m['cover_thickness_mm']),
            ('rear_cap', m['inner_shell_outer_mm'], m['rear_cover_outer_mm'], m['length_mm']-m['cover_thickness_mm'], m['length_mm']),
            ('rear_load_ring', m['sampling_outer_radius_mm'], m['sampling_shell_inner_mm'], sb, sb+18.),
        ]
        for label, ri, ro, za, zb in structural:
            v = self.tube(name+'_'+label, ri, ro, zb-za, name, 'aluminium', 'structural_aluminium', c)
            self.place(result, v, 1, z=(za+zb)/2)
        rib_size = m['sampling_shell_inner_mm']-m['sampling_outer_radius_mm']-.2
        rib = self.box(name+'_rib', (rib_size, 6., length), name, 'aluminium', 'structural_aluminium', c)
        rib_radius = (m['sampling_shell_inner_mm']+m['sampling_outer_radius_mm'])/2
        for i in range(4):
            phi = i*math.pi/2
            self.place(result, rib, i+1, x=rib_radius*math.cos(phi), y=rib_radius*math.sin(phi),
                       z=(sf+sb)/2, phi=math.degrees(phi))
        sensor_front, sensor_back = z['sensors']
        cartridge = self.box(name+'_cartridge', (r['cartridge_side_mm'], r['cartridge_side_mm'], sensor_back-sensor_front), name, 'air', 'sensor_cartridge', c)
        device = self.box(name+'_device_footprint', (r['device_side_mm'], r['device_side_mm'], r['device_depth_mm']), name, 'air', 'device_footprint', c)
        self.place(cartridge, device, 1, z=-(sensor_back-sensor_front)/2+r['device_depth_mm']/2)
        pixel = self.box(name+'_silicon_pixel', (r['pixel_side_mm'], r['pixel_side_mm'], .3), name, 'silicon', 'silicon_pixel', c)
        for iy in range(4):
            for ix in range(4):
                self.place(device, pixel, 4*iy+ix+1,
                           x=(ix-1.5)*r['pixel_pitch_mm'], y=(iy-1.5)*r['pixel_pitch_mm'],
                           z=-(r['device_depth_mm']-.3)/2)
        for ch in model['channels']:
            self.place(result, cartridge, ch['channel']+1, x=ch['x_mm'], y=ch['y_mm'],
                       z=(sensor_front+sensor_back)/2, phi=math.degrees(ch['phi_rad']))
        fe_front = z['electronics_cooling'][0]
        coldplate = self.tube(name+'_coldplate', m['inner_shell_outer_mm'], m['rear_shell_inner_mm']-1.,
                              6., name, 'aluminium', 'coldplate', c)
        self.place(result, coldplate, 1, z=fe_front+3.)
        pipe_front = fe_front+6.
        pipe = self.tube(name+'_coolant_wall', t['pipe_inner_diameter_mm']/2, t['pipe_outer_diameter_mm']/2,
                         pipe_end_local-pipe_front, name, 'aluminium', 'coolant_wall', c)
        coolant = self.tube(name+'_coolant_water', 0., t['pipe_inner_diameter_mm']/2,
                            pipe_end_local-pipe_front, name, 'water', 'coolant_water', c)
        for i, degrees in enumerate(t['pipe_phi_deg']):
            phi=math.radians(degrees); x=t['pipe_radius_mm']*math.cos(phi); y=t['pipe_radius_mm']*math.sin(phi)
            self.place(result, pipe, i+1, x=x, y=y, z=(pipe_front+pipe_end_local)/2)
            self.place(result, coolant, i+1, x=x, y=y, z=(pipe_front+pipe_end_local)/2)
        return result

    def ledger(self, volume):
        """Inventory actual logical placements; repeated children scale once each."""
        cache, materials = {}, {}

        def visit(v):
            name = str(v.GetName())
            if name in cache:
                return cache[name]
            counts, volumes, roles = Counter(), defaultdict(float), defaultdict(float)
            children = [v.GetNode(i).GetVolume() for i in range(v.GetNdaughters())]
            role = self.roles[name]
            if not v.IsAssembly():
                own = capacity(v.GetShape()) - sum(capacity(ch.GetShape()) for ch in children if not ch.IsAssembly())
                if own < -1.e-6:
                    raise RuntimeError('Negative exclusive volume '+name)
                key = self.material_keys[str(v.GetMaterial().GetName())]
                material = v.GetMaterial()
                materials[key] = {'density_g_cm3':float(material.GetDensity()),
                                  'radiation_length_mm':float(material.GetRadLen())/MM,
                                  'nuclear_length_mm':float(material.GetIntLen())/MM}
                counts[role] += 1
                volumes[key] += max(0., own)
                roles[role+'|'+key] += max(0., own)
            for child in children:
                cc, vv, rr = visit(child)
                counts.update(cc)
                for k, value in vv.items(): volumes[k] += value
                for k, value in rr.items(): roles[k] += value
            cache[name] = counts, dict(volumes), dict(roles)
            return cache[name]
        counts, volumes, roles = visit(volume)
        return {'counts':dict(counts), 'exclusive_volumes_mm3':volumes,
                'exclusive_role_volumes_mm3':roles,'native_material_properties':materials}


def trace(manager, builder, origin, direction, max_length=8700.):
    manager.InitTrack(*(v*MM for v in origin), *direction)
    nav = manager.GetCurrentNavigator()
    distance = 0.; paths = defaultdict(float); cores = defaultdict(set); steps = 0
    while not nav.IsOutside() and distance < max_length:
        node=nav.GetCurrentNode()
        if not node: break
        material=str(node.GetVolume().GetMaterial().GetName())
        path=str(nav.GetPath())
        nav.FindNextBoundaryAndStep((max_length-distance)*MM)
        length=float(nav.GetStep())/MM
        if not math.isfinite(length) or length <= 0:
            raise RuntimeError('Invalid native boundary step '+str(length)+' at '+path)
        distance += length; steps += 1
        if steps > 100000: raise RuntimeError('Native boundary-step ceiling')
        if material.startswith(('core_', 'collar_')):
            paths[material] += length
            if material.endswith('_fused_silica'):
                cores[material.split('_',1)[0]].add(path)
    return {'material_paths_mm':dict(paths), 'core_crossings':{k:len(v) for k,v in cores.items()}, 'boundary_steps':steps}


def component_checks(builder, native, model):
    ledger=builder.ledger(native)
    expected=inventory(model)
    errors=[]; comparisons={}
    for material in MATERIAL_KEYS:
        got=ledger['exclusive_volumes_mm3'].get(material,0.)
        want=expected['volumes_mm3'][material]
        comparisons[material]={'observed_mm3':got,'expected_mm3':want,'residual_mm3':got-want}
        if not math.isclose(got,want,rel_tol=1.e-10,abs_tol=1.e-5): errors.append('exclusive volume '+material)
    got=ledger['exclusive_role_volumes_mm3']['structural_aluminium|aluminium']
    want=expected['volumes_mm3']['aluminium']
    comparisons['structural_aluminium']={'observed_mm3':got,'expected_mm3':want,'residual_mm3':got-want}
    if not math.isclose(got,want,rel_tol=1.e-10,abs_tol=1.e-5):errors.append('structural aluminium volume')
    for role in ('hole','buffer','silica_core'):
        if ledger['counts'][role]!=len(model['fibres']):errors.append('count '+role)
    if ledger['counts']['sensor_cartridge']!=len(model['channels']):errors.append('cartridge count')
    if ledger['counts']['silicon_pixel']!=16*len(model['channels']):errors.append('pixel count')
    ledger['material_masses_g']={k:v*ledger['native_material_properties'][k]['density_g_cm3']/1000
                                 for k,v in ledger['exclusive_volumes_mm3'].items() if k in model['config']['materials']}
    masses={}
    for key in ('tungsten','fused_silica','buffer_proxy','aluminium'):
        native_volume=(ledger['exclusive_role_volumes_mm3']['structural_aluminium|aluminium']
                       if key=='aluminium' else ledger['exclusive_volumes_mm3'][key])
        got=native_volume*ledger['native_material_properties'][key]['density_g_cm3']/1000
        want=expected['partial_masses_g'][key]
        masses[key]={'observed_g':got,'expected_g':want,'residual_g':got-want}
        if not math.isclose(got,want,rel_tol=1.e-10,abs_tol=1.e-6):errors.append('constituent mass '+key)
    ledger['common_constituent_mass_comparisons']=masses
    ledger['mass_excludes_air_g']=sum(ledger['material_masses_g'].values())
    ledger['exclusive_volume_comparisons']=comparisons
    ledger['errors']=errors
    return ledger


def run_layout(args):
    import ROOT as R
    R.gROOT.SetBatch(True)
    R.EnableImplicitMT(1)
    c=load_config(args.config)
    contexts=json.loads(args.contexts.read_text()); context=contexts[args.layout]
    executed_hashes={str(path.resolve().relative_to(REPO)):sha(path)
                     for path in (HERE/'model.py',args.config,args.contexts,Path(__file__))}
    model=build(c); models={'core':model}
    manager=R.TGeoManager('DES039_'+args.layout, 'Isolated FCAL native ROOT prototype')
    b=Builder(R,manager)
    world=b.box('world',(12000.,12000.,18000.),'world','air','world')
    manager.SetTopVolume(world)
    front=c['layouts'][args.layout]['package_front_abs_z_mm']
    handoff=1000*context['hcal']['endcap_back_abs_z_m']+c['layouts'][args.layout]['external_handoff_clearance_mm']
    core=b.component(model,'core',handoff-front)
    components={'core':core}; fronts={'core':front}
    if args.layout=='LAYOUT-002':
        cm=build(collar_config(c));models['collar']=cm
        collar=b.component(cm,'collar',cm['config']['module']['length_mm'])
        components['collar']=collar
        fronts['collar']=c['collar']['package_front_abs_z_mm']
    for name, component in components.items():
        for side in (-1,1):
            b.place(world,component,1 if side>0 else 2,z=side*fronts[name],negative=side<0)
    neck_count=0; neck_ledger=None
    if args.layout=='LAYOUT-002':
        neck=b.assembly('collar_neck')
        start=4883.
        for key,ri,ro,role in [('aluminium',2.,3.,'neck_coolant_wall'),('water',0.,2.,'neck_coolant_water')]:
            pipe=b.tube('collar_neck_'+key,ri,ro,handoff-start,'collar',key,role,c)
            for i, degrees in enumerate(c['thermal']['pipe_phi_deg']):
                phi=math.radians(degrees); radius=c['collar']['neck_pipe_center_radius_mm']
                b.place(neck,pipe,i+1,x=radius*math.cos(phi),y=radius*math.sin(phi),z=(start+handoff)/2)
        for side in (-1,1): b.place(world,neck,1 if side>0 else 2,negative=side<0)
        neck_count=4
        neck_ledger=b.ledger(neck)
        neck_ledger['material_masses_g']={key:volume*neck_ledger['native_material_properties'][key]['density_g_cm3']/1000
                                           for key,volume in neck_ledger['exclusive_volumes_mm3'].items()}
    guards=[]
    for system in ('ecal','hcal'):
        q=context[system]
        ri=1000*q.get('endcap_inner_radius_m',q.get('endcap_inner_apothem_m'))
        ro=1000*q.get('endcap_outer_radius_m',q.get('endcap_outer_apothem_m'))
        za=1000*q['endcap_front_abs_z_m'];zb=1000*q['endcap_back_abs_z_m']
        guard=b.tube(system+'_annular_guard',ri,ro,zb-za,'guard','envelope_guard','envelope_guard',c)
        for side in (-1,1): b.place(world,guard,1 if side>0 else 2,z=side*(za+zb)/2,negative=side<0)
        guards.append({'system':system,'inner_mm':ri,'outer_mm':ro,'abs_z_mm':[za,zb],
                       'scope':'Circular annular guard using minimum apothem where polygonal; conservative for bore intrusion, not complete neighbouring geometry.'})
    print(args.layout,'constructed',flush=True)
    manager.CloseGeometry()
    ledgers={name:component_checks(b,components[name],models[name]) for name in components}
    errors=[name+':'+e for name in ledgers for e in ledgers[name]['errors']]
    for name,component in components.items():
        for i in range(world.GetNdaughters()):
            node=world.GetNode(i)
            if str(node.GetVolume().GetName())==name and node.GetNumber()==2:
                rot=node.GetMatrix().GetRotationMatrix()
                det=(rot[0]*(rot[4]*rot[8]-rot[5]*rot[7])-rot[1]*(rot[3]*rot[8]-rot[5]*rot[6])+rot[2]*(rot[3]*rot[7]-rot[4]*rot[6]))
                if abs(det-1)>1.e-12 or abs(rot[4]+1)>1.e-12 or abs(rot[8]+1)>1.e-12:errors.append('negative rotation '+name)
    print(args.layout,'checking full native overlaps',flush=True)
    started=time.monotonic()
    manager.CheckOverlaps(c['validation']['overlap_tolerance_mm']*MM)
    overlap_seconds=time.monotonic()-started
    overlaps=[{'description':str(x.GetTitle()),'penetration_mm':float(x.GetOverlap())/MM} for x in manager.GetListOfOverlaps()]
    if overlaps: errors.append('native overlaps/extrusions '+str(len(overlaps)))
    print(args.layout,'overlaps',len(overlaps),'seconds',round(overlap_seconds,3),flush=True)
    navigation=[]; max_delta=0.
    for eta in (3.3,3.6,4.,4.5,5.,5.2):
        for side in (-1,1):
            for phi in (.37,1.11,math.pi/2):
                signed=side*eta
                direction=[math.cos(phi)/math.cosh(eta),math.sin(phi)/math.cosh(eta),math.tanh(signed)]
                actual=trace(manager,b,[0.,0.,0.],direction)
                comparisons={}
                for name in models:
                    sf=fronts[name]+models[name]['zones_mm']['sampling'][0]
                    expected=ray_sample(models[name],signed,phi,sf,side)
                    deltas={key:actual['material_paths_mm'].get(name+'_'+key,0.)-expected['paths_mm'][key] for key in MATERIAL_KEYS}
                    delta=max(abs(v) for v in deltas.values()); max_delta=max(max_delta,delta)
                    if delta>1.e-5: errors.append('ray material '+name+' '+str((signed,phi)))
                    observed_cores=actual['core_crossings'].get(name,0)
                    if observed_cores!=expected['fibre_core_crossings']:errors.append('ray core count '+name+' '+str((signed,phi)))
                    comparisons[name]={'expected_paths_mm':expected['paths_mm'],'residuals_mm':deltas,
                                       'observed_core_crossings':observed_cores,'expected_core_crossings':expected['fibre_core_crossings']}
                navigation.append({'signed_eta':signed,'phi_rad':phi,'observed':actual,'comparisons':comparisons})
    axial=[]
    for name,model in models.items():
        sf,sb=model['zones_mm']['sampling']; ln=sb-sf
        fibres=[min((v for v in model['fibres'] if v['population']==pop),key=lambda v:abs(math.hypot(v['x_mm'],v['y_mm'])-100.)) for pop in (0,1)]
        controls=[('long_core',fibres[0]['x_mm'],fibres[0]['y_mm'],0),('short_core',fibres[1]['x_mm'],fibres[1]['y_mm'],1),('absorber',100.,0.,None)]
        for side in (-1,1):
            for label,x,y,pop in controls:
                origin=[x,side*y,side*(fronts[name]+sf-1.)]
                observed=trace(manager,b,origin,[0.,0.,float(side)],max_length=ln+2.)
                expected={key:0. for key in MATERIAL_KEYS}
                if pop is None: expected['tungsten']=ln
                else:
                    plug=model['config']['fibres']['short_start_mm'] if pop else 0.
                    expected['tungsten']=plug;expected['fused_silica']=ln-plug
                deltas={key:observed['material_paths_mm'].get(name+'_'+key,0.)-expected[key] for key in MATERIAL_KEYS}
                if max(abs(v) for v in deltas.values())>1.e-5:errors.append('axial control '+name+' '+label+' '+str(side))
                axial.append({'component':name,'side':side,'control':label,'expected_paths_mm':expected,
                              'observed':observed,'residuals_mm':deltas})
    rootfile=args.build_dir/(args.layout+'.root')
    manager.Export(str(rootfile.resolve()))
    report={'layout_id':args.layout,'status':'PASS' if not errors else 'FAIL','errors':errors,
            'ROOT_version':R.gROOT.GetVersion(),'python_version':platform.python_version(),
            'executed_source_sha256':executed_hashes,
            'component_replicas':{name:2 for name in components},'negative_side_rotation':'Rx(180deg), determinant +1 checked',
            'native_component_ledgers_per_end':ledgers,'external_collar_neck_tubes_physical':neck_count,
            'external_collar_neck_ledger_per_end':neck_ledger,
            'mass_ledger_scope':'Common-constituent comparisons include sampling materials and structural aluminium only, matching the analytical partial ledger. Native component ledgers additionally include silicon pixels, coldplates and water-line walls/contents. Core line lengths reach the HCAL rear +50 mm; collar local lines end at the collar rear. External collar neck is tabulated separately. Air, envelope guards and omitted parts are excluded from mass totals.',
            'guard_envelopes':guards,'overlap_tolerance_mm':c['validation']['overlap_tolerance_mm'],
            'overlap_seconds':overlap_seconds,'overlaps':overlaps,'ip_navigation':navigation,'axial_controls':axial,
            'maximum_ip_material_path_residual_mm':max_delta,'navigation_tolerance_mm':1.e-5,
            'root_sha256':sha(rootfile)}
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(args.layout,report['status'],len(navigation),'IP rays',len(axial),'axial controls',errors[:5],flush=True)
    R.DisableImplicitMT()
    # TGeoManager owns registered geometry; Python must not free its objects a
    # second time when the keep-alive references leave scope after deletion.
    for obj in b.keep:
        R.SetOwnership(obj, False)
    R.SetOwnership(manager, False)
    manager.Delete()
    return 1 if errors else 0


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,default=HERE/'inputs.json')
    p.add_argument('--contexts',type=Path,default=HERE/'layout-contexts.json')
    p.add_argument('--output',type=Path,default=REPO/'docs/validation/DES-039/native.json')
    p.add_argument('--build-dir',type=Path,default=REPO/'build/forward_calorimeter/native')
    p.add_argument('--layout',choices=('LAYOUT-001','LAYOUT-002'))
    args=p.parse_args();args.build_dir.mkdir(parents=True,exist_ok=True);args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.layout: return run_layout(args)
    reports={};commands=[]
    for layout in ('LAYOUT-001','LAYOUT-002'):
        output=args.build_dir/(layout+'.json');log=args.build_dir/(layout+'.log')
        command=[sys.executable,'-B',str(Path(__file__).resolve()),'--layout',layout,'--config',str(args.config.resolve()),
                 '--contexts',str(args.contexts.resolve()),'--build-dir',str(args.build_dir.resolve()),'--output',str(output.resolve())]
        print('Running',layout,'native audit; log:',log,flush=True)
        output.unlink(missing_ok=True)
        with log.open('w') as stream:result=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT)
        commands.append(command)
        if not output.exists():raise RuntimeError(layout+' failed before report; see '+str(log))
        reports[layout]=json.loads(output.read_text())
        reports[layout]['process_exit_code']=result.returncode
        if result.returncode:
            reports[layout]['status']='FAIL'
            reports[layout]['errors'].append('native process exit '+str(result.returncode))
        print(layout,reports[layout]['status'],'exit',result.returncode,flush=True)
    source_files=[HERE/'model.py',args.config,args.contexts,Path(__file__)]
    pinned_hashes={}
    for path in source_files[:-1]:
        relative=str(path.resolve().relative_to(REPO))
        data=subprocess.check_output(['git','show',PINNED_REVISION+':'+relative],cwd=REPO)
        pinned_hashes[relative]=hashlib.sha256(data).hexdigest()
    report={'schema_version':1,'design_id':'DES-039','status':'PASS' if all(v['status']=='PASS' for v in reports.values()) else 'FAIL',
            'scope':'Executed isolated native ROOT/TGeo geometry; both signs in both layouts, collar in 02. Envelope guards are not complete adjacent detectors.',
            'execution':{'source_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
                         'scientific_input_revision':PINNED_REVISION,'working_tree_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=REPO)),
                         'source_sha256':{str(x.resolve().relative_to(REPO)):sha(x) for x in source_files},
                         'pinned_source_sha256':pinned_hashes,'python_executable':sys.executable,'commands':commands},
            'layouts':reports,
            'material_model':'Named source densities and reference X0/nuclear lengths assigned explicitly; silica SiO2, buffer CH2 mass proxy, water H2O. Air has a negligible reference length for navigation. Device envelopes carry air; only 0.3 mm Si pixel slabs have sensor material.',
            'included':['Both matrix halves, exact finite long/short bores, nested buffer/silica','Sleeves, shells, closure caps, rear load ring and four cradle ribs','96 air cartridge/device footprint envelopes and 1536 silicon pixels per component/end','Rear coldplate and two straight OD6/ID4 water-equivalent coolant pipes per component/end','02 straight external collar-neck pipes at R294 after |z|4883','Conservative circular ECAL/HCAL envelope guards'],
            'not_implemented':['Individual optical fanout curves, ferrules and optical connectors','Collar radial collector, elbows and connection from collar R444 pipes to R294 neck','Dry-gas/electrical bundles, detailed front-end boards, device packages, outboard manifolds and external load frame','Full neighbouring calorimeters, downstream beam pipe/shielding and magnetic structures','DD4hep factories, sensitive detectors/readout identifiers, Geant4 transport, optical response, shower performance and engineering qualification'],
            'limitations':['Native mass is partial and excludes omitted parts; direct comparison to the analytical partial ledger isolates common represented structural parts.','Sparse deterministic boundary rays validate navigation and finite-cylinder calculations; they do not establish efficiency, containment or hermeticity.','Reference material X0/nuclear lengths are assigned inputs, not independently calculated transport cross sections.','ROOT numerical overlap tolerance is not a mechanical assembly clearance.']}
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],str(args.output),flush=True)
    return 0 if report['status']=='PASS' else 1


if __name__=='__main__':
    raise SystemExit(main())
