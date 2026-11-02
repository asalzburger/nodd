#!/usr/bin/env python3
"""DES043 auditable service/finite-plane design screens; no native simulation."""
import argparse
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from diagnostics import coverage, cooling_routes, copper_profile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load_model(name):
    spec=importlib.util.spec_from_file_location('_des043_'+name,ROOT/'tools'/name/'model.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m


def load(path=HERE/'inputs.json'):
    c=json.loads(Path(path).read_text())
    if c['schema_version']!=1 or c['pitch_mm']!=[.075,2.]:raise ValueError('Expected selected2mm strixels')
    if c['ring_centres_mm']!=sorted(c['ring_centres_mm']) or len(c['ring_centres_mm'])!=5:raise ValueError('Require ordered five-ring design')
    if not 0<c['minimum_delivered_V']<c['supply_V']:raise ValueError('Invalid voltage floor')
    if c['leaf_pipe_OD_mm']!=2.5 or c['leaf_pipe_wall_mm']!=.14:raise ValueError('Hydraulic floor amendment requires review')
    for s in c['packing'].values():
        if not 0<s['phi_fraction']<=1 or not 0<s['packing_fraction']<=1 or s['spare_factor']<1:raise ValueError('Invalid packing')
    if c['thermal']['endcap_pad_mm']!=[6.,60.] or c['thermal']['endcap_pad_u_mm']!=5.:raise ValueError('Pickup envelope requires new finite collision assessment')
    for path,digest in c['baseline_source_sha256'].items():
        if sha(ROOT/path)!=digest:raise ValueError('Historical source changed: '+path)
    return c


def geometry(c):
    b=load_model('short_strip_barrel');e=load_model('short_strip_endcap');l=load_model('long_strip_endcap')
    bc,ec,lc=b.load(),e.load(),l.load();bl,el,ll=b.build(bc),e.build(ec),l.build(lc)
    selected=copy.deepcopy(el);new=[]
    for d in el['discs']:
        side=d['side'];z=abs(d['z_mm']);lid=d['layer']
        for ring,r in enumerate(c['ring_centres_mm']):
            count=12*math.ceil(math.pi/math.atan(45/(2*(r+48)))/12)
            for k in range(count):
                phi=(k+.5)*2*math.pi/count;co,si=math.cos(phi),math.sin(phi);lift=(ring%2)*3+(k%2)*1.5
                new.append(dict(layer=lid,side=side,ring=ring,petal=k//(count//12),radius_mm=r,lift_mm=lift,
                    center_mm=[r*co,side*r*si,side*(z+lift)],u=[-si,side*co,0],v=[-co,-side*si,0],n=[0,0,side],half_u_mm=24,half_v_mm=48))
    selected['modules']=new
    return bc,ec,lc,bl,el,ll,selected


def radial_bounds(sensor):
    p=[]
    for i,j in [(-1,-1),(-1,1),(1,1),(1,-1)]:
        p.append([sensor['center_mm'][a]+i*sensor['half_u_mm']*sensor['u'][a]+j*sensor['half_v_mm']*sensor['v'][a] for a in (0,1)])
    minimum=math.inf
    for a,b in zip(p,p[1:]+p[:1]):
        d=[b[i]-a[i] for i in (0,1)];t=max(0,min(1,-sum(a[i]*d[i] for i in (0,1))/sum(x*x for x in d)))
        minimum=min(minimum,math.hypot(*(a[i]+t*d[i] for i in (0,1))))
    return minimum,max(math.hypot(*x) for x in p)


def bus(taps,entry,watts,voltage,rho,area):
    current=watts/voltage;last=entry;drop=loss=0.
    for i,p in enumerate(sorted(taps,reverse=True)):
        if p>last+1e-9:raise ValueError('Tap beyond supply entry')
        resistance=rho*(last-p)/1000/area;flow=(len(taps)-i)*current
        drop+=flow*resistance;loss+=2*flow*flow*resistance;last=p
    return dict(return_drop_V=drop,round_trip_drop_V=2*drop,loss_W=loss)


def thermal(c,region):
    t=c['thermal'];w,h=t[region+'_pad_mm'];area=2*w*h*1e-6
    terms=dict(TIM=t['insulating_TIM_total_mm']/1000/(t['TIM_k_W_mK']*area),
        spreader_cross=t['spreader_mm']/1000/(t['spreader_perpendicular_k_W_mK']*area),
        spreading=t['hotspot_spreading_mm']/1000/(t['spreader_parallel_k_W_mK']*(t['spreader_mm']/1000)*(h/1000)*2),
        pickup=t['maximum_pickup_height_mm']/1000/(t['pickup_k_W_mK']*area),
        contact=t['contact_R_K_W'],pipe_boiling=t['pipe_boiling_R_K_W'])
    overhang=t['leakage_corner_overhang_mm'][region]
    corner=c['sensor_leakage_W']/(.048*.096)*sum((x/1000)**2 for x in overhang)/(2*t['spreader_parallel_k_W_mK']*t['spreader_mm']/1000)
    return dict(terms_K_W=terms,R_K_W=sum(terms.values()),distributed_leakage_corner_K=corner,scope='Specified contact/TIM/pickup path with backing windows and ASIC re-layout; not measured/FEA performance')


def annulus_capacity(rin,rout,phi,pack,sectors=12,wall=.5):
    if rin+2*wall>=rout:raise ValueError('No wall-clear annulus')
    return phi*math.pi*((rout-wall)**2-(rin+wall)**2)*pack/sectors


def packing(c,bl,ec_modules):
    sectors=[];r0,r1,_,_=c['trunk_mm'];endcap_per_petal=ec_modules//12//12
    for i,b in enumerate(bl['sectors']):
        staves=b['loops'];power=staves+math.ceil(endcap_per_petal/c['maximum_modules_per_power_feed'])*6
        fibres=2*staves+math.ceil(endcap_per_petal/c['maximum_modules_per_optical_group'])*6
        pipepairs=math.ceil(staves/c['maximum_loops_per_manifold'])+math.ceil(6*c['endcap_loops_per_petal']/c['maximum_loops_per_manifold'])
        demand=power*math.pi/4*c['power_cable_OD_mm']**2+fibres*math.pi/4*c['fibre_OD_mm']**2+pipepairs*math.pi/4*sum(x*x for x in c['trunk_pipe_OD_mm'])
        collector=staves*math.pi/4*c['power_cable_OD_mm']**2+2*staves*math.pi/4*c['fibre_OD_mm']**2+math.ceil(staves/8)*math.pi/4*sum(x*x for x in c['trunk_pipe_OD_mm'])
        for name,s in c['packing'].items():
            cap=annulus_capacity(r0,r1,s['phi_fraction'],s['packing_fraction'],wall=c['tray_wall_mm'])
            oldjoin=annulus_capacity(r0,750,s['phi_fraction'],s['packing_fraction'])
            sectors.append(dict(sector=i,scenario=name,power_feeds=power,optical_groups=fibres,pipe_pairs=pipepairs,
                bare_demand_mm2=demand,capacity_mm2=cap,fill_ratio=s['spare_factor']*demand/cap,passed=s['spare_factor']*demand<=cap,
                new_collector_join_fill=s['spare_factor']*collector/cap,old_collector_join_fill=s['spare_factor']*collector/oldjoin))
    return sectors


def routes(c,bl,selected,baseline=False):
    records=[];v=c['minimum_delivered_V'];maxmods=12 if baseline else c['maximum_modules_per_power_feed']
    for r in bl['routes']:
        radius=next(s['radius_mm'] for s in bl['staves'] if s['layer']==r['layer'] and s['stave']==r['stave'])
        records.append(dict(region='barrel',side=r['side'],sector=r['sector'],modules=len(r['modules']),
            power=math.ceil(len(r['modules'])/maxmods),fibres=math.ceil(len(r['modules'])/12),
            length_m=((750 if baseline else c['collector_mm'][1])-radius+math.pi*50+3500-1310)/1000))
    for layer in range(12):
        side=1 if layer<6 else -1;z=abs(selected['discs'][layer]['z_mm'])
        for petal in range(12):
            n=sum(m['layer']==layer and m['petal']==petal for m in selected['modules'])
            records.append(dict(region='endcap',side=side,sector=petal if side>0 else 11-petal,modules=n,
                power=math.ceil(n/maxmods),fibres=math.ceil(n/12),length_m=((750-695) if baseline else (c['trunk_mm'][1]-c['board_radius_mm']))/1000+math.pi*.05+(3500-z-85)/1000))
    return records


def cable_copper(c,modules):
    return 2*c['lv_area_per_conductor_mm2']+2*modules*c['hv_area_per_conductor_mm2']+c['control_copper_mm2']+c['shield_copper_mm2']


def material(c,bc,ec,bl,el,new):
    oldroutes=routes(c,bl,el,True);newroutes=routes(c,bl,new)
    oldgross=math.pi/4*13.4**2;newgross=math.pi/4*c['power_cable_OD_mm']**2
    oldcu=oldgross*.2;newcu=cable_copper(c,c['maximum_modules_per_power_feed'])
    if newcu>=newgross:raise ValueError('Copper exceeds cable envelope')
    oldlength=sum(r['power']*r['length_m'] for r in oldroutes);newlength=sum(r['power']*r['length_m'] for r in newroutes)
    # mm²*m = cm³; litres follow /1000.
    entries=[]
    def add(name,old_g,new_g,scope):entries.append(dict(component=name,old_kg=old_g/1000,new_kg=new_g/1000,delta_kg=(new_g-old_g)/1000,scope=scope))
    add('External LV/HV/control/shield copper',oldcu*oldlength*8.96,newcu*newlength*8.96,'Old20%Cu effective recipe; new explicit pairs/HV/control/shield areas, no optical reduction')
    add('Power cable insulation solids',oldgross*.3*oldlength*1.42,(newgross-newcu)*c['material']['new_power_non_copper_solid_fraction']*newlength*1.42,'PI proxy for unqualified cable insulation; residual area is void, not solid')
    oldfib=sum(r['fibres']*r['length_m'] for r in oldroutes);newfib=sum(r['fibres']*r['length_m'] for r in newroutes)
    add('Optical cable payload',math.pi/4*3.6**2*oldfib*(.5*2.2+.5*1.42),math.pi/4*3.6**2*newfib*(.5*2.2+.5*1.42),'Conservative all-solid50/50silica/PI proxy, no savings from75%channel reduction')
    # Fully retain old module constituents as a positive mass allowance for additions.
    def module_g():
        return (49*97*.2+8*23.4**2*.15)*2.329/1000+48*96*.2*2.21/1000+48*96*.225*2/1000+48*96*.025*1.42/1000+48*96*.2*1.73/1000+49*6*.1*1.42/1000
    oldn=len(bl['modules'])+len(el['modules']);newn=len(bl['modules'])+len(new['modules'])
    add('Conservative complete added modules',oldn*module_g(),newn*module_g(),'Retain8ASIC material per sensor; no ASIC-area credit for proposed2-tile layout')
    add('Extra graphite spreader',0,newn*48*96*(c['thermal']['spreader_mm']-.2)*2.21/1000,'Debit full additional thickness on all sensors')
    old_b=len(bl['modules']); old_e=len(el['modules']); new_e=len(new['modules'])
    insert_volume=(old_b*2*20*64+new_e*2*6*60)*c['thermal']['extra_core_insert_mm']
    added_pickups=(new_e-old_e)*2*6*60*4.9
    add('Direct graphite inserts and added pickups',0,(insert_volume+added_pickups)*2.21/1000,'Debit1.7mm new core insertion for every existing/new pickup plus4.9mm old maximum pickup on added EC sensors; no displaced foam credit')
    add('New TIM and module service reserve',0,newn*(c['material']['new_module_other_passive_reserve_g']+48*96*c['thermal']['insulating_TIM_total_mm']*c['material']['TIM_density_upper_g_cm3']/1000),'Full-area TIM upperdensity and5g/module design reserve; no backing/PI removal credit')
    oldplate=math.pi*(685**2-236**2);newplate=math.pi*(c['petal_outer_plate_mm']**2-236**2)
    add('Endcap support skins/core/glue',12*oldplate*(.3*1.73+5*.2+.2*2)/1000,12*newplate*(.3*1.73+5*.2+.2*2)/1000,'Gross solid stack; no cooling void credit; outer frame treated separately')
    add('Endcap outer frame',12*math.pi*(700**2-674**2)*3*1.73/1000,12*math.pi*(c['outer_frame_mm'][1]**2-c['outer_frame_mm'][0]**2)*3*1.73/1000,'Preserve26mmradial width/3mmaxial frame')
    oldbus=(288*2*1210+144*428)*2*12*.2
    newbus=(288*2*1210+144*(c['endcap_bus_entry_mm']-250))*2*12*c['rail_thickness_mm']
    add('Local LV copper rails',oldbus*8.96/1000,newbus*8.96/1000,'EC3islands split existing total24mm copper width; barrel2rails unchanged width')
    # Debits for extra local serpentine and an additional EC manifold bank per sector/end.
    pipe_screen=cooling_routes(c,ec)
    extra_leaf_length_m=144*max(0,pipe_screen['new_total_length_mm']-pipe_screen['old_total_length_mm'])/1000
    tubearea=math.pi/4*(2.5**2-2.22**2);coolarea=math.pi/4*2.22**2
    add('Extra local cooling length reserve',0,extra_leaf_length_m*(tubearea*4.51+coolarea*1.),'Exact planar source-centreline length increase; extra bank separately budgeted; fittings remain within explicit reserve only')
    bulk_length_m=24*(3500-1310)/1000
    bulkmetal=math.pi/4*sum(od*od-id*id for od,id in zip(c['trunk_pipe_OD_mm'],c['trunk_pipe_ID_mm']))
    bulkfluid=math.pi/4*sum(id*id for id in c['trunk_pipe_ID_mm'])
    add('Additional EC cooling pipe bank',0,bulk_length_m*(bulkmetal*4.51+bulkfluid*1.),'24extra pairs full2190mm; CO2 density1g/cm³ retained transport proxy, not thermodynamic density')
    return dict(entries=entries,delta_kg=sum(x['delta_kg'] for x in entries),delta_without_insulation_credit_kg=sum(x['delta_kg'] for x in entries if x['component']!='Power cable insulation solids'),power_feeds_both_ends=dict(old=sum(r['power'] for r in oldroutes),new=sum(r['power'] for r in newroutes)),optical_groups_both_ends=dict(old=sum(r['fibres'] for r in oldroutes),new=sum(r['fibres'] for r in newroutes)),power_length_m=dict(old=oldlength,new=newlength),power_envelope_L=dict(old=oldgross*oldlength/1000,new=newgross*newlength/1000),old_copper_mm2=oldcu,new_copper_mm2=newcu,
        limits='Scoped engineering proxy, not complete tracker mass/X0. Unknown fittings, thermal materials and manifold hardware remain design gates;5g/module reserve is not supplier qualification.')


def screen(c):
    bc,ec,lc,bl,el,ll,new=geometry(c);oldmax=max(radial_bounds(x)[1] for x in el['modules']);newmax=max(radial_bounds(x)[1] for x in new['modules']);longmin=min(radial_bounds(x)[0] for x in ll['modules'])
    taps_b=[x['center_mm'][2] for x in bl['modules'] if x['layer']==0 and x['stave']==0 and x['center_mm'][2]>0]
    taps_e=[x['radius_mm'] for x in new['modules'] if x['layer']==0 and x['petal']==0]
    rho=c['resistivity_ohm_mm2_m']*c['warm_resistivity_factor'];cases=[]
    for name,fixed in c['fixed_electronics_fraction'].items():
        watts=c['reference_electronics_W']*(fixed+(1-fixed)*.25);q=watts+c['sensor_leakage_W']
        b=bus(taps_b,1210,watts,c['minimum_delivered_V'],rho,12*c['rail_thickness_mm'])
        islands=[sorted(taps_e)[i::3] for i in range(3)]
        e=[bus(t,c['endcap_bus_entry_mm'],watts,c['minimum_delivered_V'],rho,4*c['rail_thickness_mm']) for t in islands]
        feed_current=(14*watts+c['board_W'])/c['minimum_delivered_V'];feed_drop=2*rho*c['maximum_feeder_length_m']/c['lv_area_per_conductor_mm2']*feed_current
        therm={r:dict(thermal(c,r),sensor_C=c['coolant_max_C']+q*thermal(c,r)['R_K_W']+thermal(c,r)['distributed_leakage_corner_K']) for r in ['barrel','endcap']}
        flow=[]
        for region,n,loss,g in [('barrel',14,b['loss_W'],c['flow_g_s']['barrel'][name]),('endcap',17,sum(x['loss_W'] for x in e),c['flow_g_s']['endcap'][name])]:
            heat=n*q+c['board_W']/(1 if region=='barrel' else 2)+loss
            flow.append(dict(region=region,maximum_modules_per_loop=n,heat_W=heat,flow_g_s=g,energy_capacity_W=g*c['latent_J_g']*c['usable_quality_rise'],passed=heat<=g*c['latent_J_g']*c['usable_quality_rise'],scope='Enthalpy-only requirement; pressure drop, dryout and flow balancing unqualified'))
        new_count=len(bl['modules'])+len(new['modules']); old_count=len(bl['modules'])+len(el['modules']); boards=576+144
        electronics_heat=new_count*watts+boards*c['board_W']; sensor_heat=new_count*c['sensor_leakage_W']
        old_heat=old_count*(c['reference_electronics_W']+c['sensor_leakage_W'])+boards*c['board_W']
        # Feeder3.5m upper bound on all feeds; board5W per feed is conservative vs one physical board per route.
        route_loss=sum(r['power']*(r['modules']/r['power']*watts+c['board_W'])**2/c['minimum_delivered_V']**2*2*rho*c['maximum_feeder_length_m']/c['lv_area_per_conductor_mm2'] for r in routes(c,bl,new))
        local_loss=576*b['loss_W']+144*sum(x['loss_W'] for x in e)
        global_budget=dict(nominal_coolant_flow_total_g_s=576*c['flow_g_s']['barrel'][name]+288*c['flow_g_s']['endcap'][name],old_7g_s_comparator_total_g_s=720*7,old_unreduced_reference_heat_W=old_heat,new_electronics_and_boards_W=electronics_heat,new_sensor_leakage_W=sensor_heat,new_local_rail_loss_W=local_loss,new_feeder_loss_upper_W=route_loss,new_connector_loss_upper_W=sum(r['power']*(r['modules']/r['power']*watts+c['board_W'])/c['minimum_delivered_V']*c['connector_protection_drop_V'] for r in routes(c,bl,new)),heat_scope='Module+board heat comparable; new losses separately itemized, old losses not credited. Feeder loss upper bound for all routes at3.5m; LV excludes independent HV leakage.')
        global_budget['new_heat_with_loss_upper_W']=electronics_heat+sensor_heat+local_loss+route_loss+global_budget['new_connector_loss_upper_W']
        cases.append(dict(global_budget=global_budget,scenario=name,fixed_fraction=fixed,electronics_W_module=watts,total_module_heat_W=q,barrel_bus=b,endcap_islands=e,maximum_feeder_round_trip_drop_V=feed_drop,connector_protection_drop_V=c['connector_protection_drop_V'],total_worst_drop_V=c['connector_protection_drop_V']+feed_drop+max(b['round_trip_drop_V'],max(x['round_trip_drop_V'] for x in e)),thermal=therm,cooling=flow,all_local_returns_pass=max(b['return_drop_V'],max(x['return_drop_V'] for x in e))<=c['maximum_local_return_drop_V']))
    packs=packing(c,bl,len(new['modules']));m=material(c,bc,ec,bl,el,new)
    n=len(bl['modules'])+len(new['modules']);legacy_channels=(len(bl['modules'])+len(el['modules']))*122880
    return dict(status='DRAFT PROTOTYPE proposed baseline; source/engineering screens, not qualified hardware',geometry=dict(old_endcap_sensors=len(el['modules']),new_endcap_sensors=len(new['modules']),total_strixel_sensors=n,ring_centres_mm=c['ring_centres_mm'],modules_per_ring=[sum(x['layer']==0 and x['ring']==i for x in new['modules']) for i in range(5)],old_active_outer_mm=oldmax,new_active_outer_mm=newmax,long_active_inner_mm=longmin,old_gap_mm=longmin-oldmax,new_gap_mm=longmin-newmax,channels=n*30720,channel_reduction_vs_0p5=1-n*30720/legacy_channels,new_body_outer_mm=max(math.hypot(x['radius_mm']+51.5,24.5) for x in new['modules']),extra_sensor_area_m2=(len(new['modules'])-len(el['modules']))*48*96/1e6),engineering=cases,packing=packs,material=m,coverage=coverage(c,new),cooling_routes=cooling_routes(c,ec),copper_corridor_profile=copper_profile(c,ec,bl),
        qualifications=['Module ASIC redistribution/thermal windows/TIM contacts need redesign and verification.','No75%data reduction, no automatic coolant pipe shrink.','Pressure/drop/dryout, cold mechanics, dielectric/irradiation/ASIC feasibility, cable package and grounding remain qualification gates.','Straight-ray finite coverage is separate; no newGBTS/ttbar/Geant4 reconstruction or full-tracker X0 claim.'])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,default=HERE/'inputs.json');p.add_argument('--output',type=Path,default=ROOT/'docs/validation/DES-043/summary.json');a=p.parse_args()
    c=load(a.input);r=screen(c);r['provenance']=dict(baseline_revision=c['input_revision'],input_sha256=sha(a.input),producer_sha256=sha(__file__),diagnostics_sha256=sha(HERE/'diagnostics.py'),source_sha256={str(q.relative_to(ROOT)):sha(q) for q in [ROOT/'tools/short_strip_barrel/model.py',ROOT/'tools/short_strip_barrel/inputs-phi-tilted.json',ROOT/'tools/short_strip_endcap/model.py',ROOT/'tools/short_strip_endcap/inputs.json',ROOT/'tools/long_strip_endcap/model.py',ROOT/'tools/long_strip_endcap/inputs.json']})
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(geometry=r['geometry'],max_fill=max(x['fill_ratio'] for x in r['packing']),material_delta_kg=r['material']['delta_kg'],engineering=[dict(scenario=x['scenario'],buspass=x['all_local_returns_pass'],drop=x['total_worst_drop_V'],T=[v['sensor_C'] for v in x['thermal'].values()],cooling=[f['passed'] for f in x['cooling']]) for x in r['engineering']]),indent=2))


if __name__=='__main__':main()
