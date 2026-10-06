#!/usr/bin/env python3
"""DES021 pinned radial-petal model and separate engineering screens (mm)."""
import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
INPUT=Path(__file__).with_name('inputs.json')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(path=INPUT):
    c=json.loads(Path(path).read_text())
    if c['schema_version']!=1:raise ValueError('Unsupported schema')
    for p,h in c['input_sha256'].items():
        if sha(ROOT/p)!=h:raise ValueError('Pinned input changed: '+p)
    if c['active_mm']!=[48,96,.2] or c['cell_mm']!=[.075,.5] or c['guard_mm']!=.5:raise ValueError('Shared module contract changed')
    if c['petals']!=12 or c['rings']!=5 or c['ring_count_multiple']!=12:raise ValueError('Unsupported topology / IDs')
    fixtures=dict(plate_mm=[236,685],petal_gap_mm=.6,pickup_mm=[6,60],pickup_u_mm=5,
        frame_mm=[[236,250],[674,700]],frame_w_mm=-12,frame_thickness_mm=3,lug_mm=[8,6,3.7],
        board_radius_mm=695,board_mm=[52,20,8],fanout_w_mm=[9,9.5],fan_mm=[685,710,15,85],
        board_mount_mm=[4,8,10.5],board_mount_u_mm=15,system_id=4,world_half_size_mm=[1000,1000,3700],phi_reserve_mm=3,
        power_bus_width_mm=12,power_bus_copper_mm=.2,power_bus_pi_mm=.15)
    for key,value in fixtures.items():
        if c[key]!=value:raise ValueError('Unsupported fixture amendment: '+key)
    def finite(value):
        if isinstance(value,dict):return all(finite(x) for x in value.values())
        if isinstance(value,list):return all(finite(x) for x in value)
        return not isinstance(value,(int,float)) or math.isfinite(value)
    if not finite(c):raise ValueError('Nonfinite input')
    if not 0<2*c['tube_wall_mm']<c['tube_OD_mm']:raise ValueError('Invalid tube bore')
    if c['ring_lift_mm']<3 or c['phi_lift_mm']<1.5:raise ValueError('Module staggering cannot shrink')
    if c['disc_z_mm'][0]-13.5<1320:raise ValueError('Barrel collector clearance <10mm')
    if any(a>=b for a,b in zip(c['disc_z_mm'],c['disc_z_mm'][1:])):raise ValueError('Unordered discs')
    if c['trunk_mm']!=[710,783,1310,3500]:raise ValueError('Fixed service corridor changed')
    return c

def barrel(c):
    spec=importlib.util.spec_from_file_location('barrel_model',ROOT/'tools/short_strip_barrel/model.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    b=m.load(ROOT/c['barrel_input']);return b,m.build(b)

def rings(c):
    lo=c['annulus_mm'][0]+48-c['radial_margin_mm'];hi=c['annulus_mm'][1]-48+c['radial_margin_mm']
    result=[]
    for i in range(c['rings']):
        r=lo+i*(hi-lo)/(c['rings']-1)
        required=math.pi/math.atan((48-c['phi_reserve_mm'])/(2*(r+48)))
        n=c["ring_count_multiple"]*math.ceil(required/c["ring_count_multiple"])
        result.append(dict(ring=i,radius_mm=r,modules=n,modules_per_petal=n//c['petals']))
    return result

def build(c,old_datum=False):
    rr=rings(c);modules=[];discs=[];routes=[]
    for side in (1,-1):
        for station,z in enumerate(c['disc_z_mm']):
            if old_datum and station==0:z=c['old_first_z_mm']
            lid=len(discs);discs.append(dict(layer=lid,side=side,station=station,z_mm=side*z))
            for petal in range(c['petals']):
                for ring in rr:
                    n=ring['modules'];r=ring['radius_mm'];per=ring['modules_per_petal']
                    for j in range(per):
                        k=petal*per+j;phi=(k+.5)*2*math.pi/n;lift=(ring['ring']%2)*c['ring_lift_mm']+(k%2)*c['phi_lift_mm']
                        co,si=math.cos(phi),math.sin(phi)
                        name=f'D{lid}_P{petal}_R{ring["ring"]}_M{j}'
                        modules.append(dict(id=len(modules),module_id=len(modules),sensor_id=len(modules),name=name,
                            layer=lid,layer_id=lid,station_id=lid,petal=petal,ring=ring['ring'],module=j,
                            phi_rad=phi,radius_mm=r,lift_mm=lift,
                            center_mm=[r*co,side*r*si,side*(z+lift)],u=[-si,side*co,0],v=[-co,-side*si,0],n=[0,0,side],
                            half_u_mm=24,half_v_mm=48))
                members=[m['name'] for m in modules if m['layer']==lid and m['petal']==petal]
                angle=(petal+.5)*math.pi/6
                routepoints=[[289.5,side*z],[695,side*(z+4)],[700,side*(z+50)],[746.5,side*(z+85)],[746.5,side*3500]]
                routes.append(dict(id=f'D{lid}_P{petal}',layer=lid,petal=petal,side=side,modules=members,
                    global_trunk_sector=petal if side>0 else 11-petal,
                    waypoints_xyz_mm=[[r*math.cos(angle),side*r*math.sin(angle),zz] for r,zz in routepoints],
                    harnesses=math.ceil(len(members)/c['modules_per_harness']),cooling_loops=1,
                    graph=['module flex ledge','effective local fanout / LV and signal buses','outer interface board',
                           'disc outer fan and manifold','cumulative longitudinal trunk','downstream handoff'],
                    waypoints_rz_mm=[[289.5,side*z],[695,side*(z+4)],[700,side*(z+50)],
                        [746.5,side*(z+85)],[746.5,side*3500]],
                    continuity='Connectivity ledger; individual vias, connectors and transitions not explicit native solids'))
    return dict(rings=rr,discs=discs,modules=modules,routes=routes)

def cooling(c):
    """Tangent circular legs/U turns/entry fillets. One connected centreline."""
    radii=[r['radius_mm']+offset for r in rings(c) for offset in (-c['cooling_offset_mm'],c['cooling_offset_mm'])]
    a,b=map(math.radians,c['cooling_angles_deg']);pieces=[]
    def arc(label,center,major,start,angle):
        pieces.append(dict(label=label,kind='torus',center=center,rx=0,ry=0,rz=0,
            dims=dict(major=major,start=start,angle=angle)))
    def line(label,phi,low,high):
        r=(low+high)/2
        pieces.append(dict(label=label,kind='tube',center=[r*math.cos(phi),r*math.sin(phi),c['tube_w_mm']],
            rx=0,ry=math.pi/2,rz=phi,dims=dict(length=high-low)))
    for i,r in enumerate(radii):
        end=b
        if i in (0,len(radii)-1):
            phi=math.radians(c['feed_phi_deg'] if i==0 else c['return_phi_deg']);bend=c['entry_bend_mm']
            delta=math.asin(bend/(r+bend));cx=math.sqrt(r*r+2*r*bend)
            end=phi-delta
            center=[cx*math.cos(phi)+bend*math.sin(phi),cx*math.sin(phi)-bend*math.cos(phi),c['tube_w_mm']]
            arc(f'entry{i}',center,bend,phi+math.pi/2,math.pi/2-delta)
            line(f'port{i}',phi,cx,c['port_radius_mm'])
        arc(f'leg{i}',[0,0,c['tube_w_mm']],r,a,end-a)
        if i<len(radii)-1:
            right=i%2==1;phi=b if right else a;mid=(r+radii[i+1])/2
            arc(f'U{i}',[mid*math.cos(phi),mid*math.sin(phi),c['tube_w_mm']],(radii[i+1]-r)/2,
                phi if right else phi+math.pi,math.pi)
    return pieces

def execution(input=INPUT):
    return dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),
        input_sha256=sha(input),producer_sha256=sha(__file__))

def screen(c,l):
    bc,bl=barrel(c);barrel_by_sector=[sum(r['harnesses'] for r in bl['routes'] if r['side']==1 and r['sector']==i) for i in range(12)]
    barrel_loops=[s['loops'] for s in bl['sectors']]
    cable=math.pi/4*(c['power_cable_OD_mm']**2+c['fibre_cable_OD_mm']**2)
    pipes=math.pi/4*sum(x*x for x in c['trunk_pipe_OD_mm'])
    rin,rout,_,_=c['trunk_mm'];packing=[]
    for scenario,phi,pack,spare,scale in [('nominal',.75,.5,1,1),('adverse',.5,.4,1.25,1),('channel_scaled',.75,.5,1,122880/30208)]:
        for n in range(7):
            cap=phi*math.pi*(rout*rout-rin*rin)*pack/12
            demands=[spare*(math.ceil((h+n*3)*scale)*cable+math.ceil((loops+n)/8)*pipes) for h,loops in zip(barrel_by_sector,barrel_loops)]
            packing.append(dict(scenario=scenario,discs_joined_per_end=n,maximum_fill_ratio=max(demands)/cap,
                passed=max(demands)<=cap,capacity_per_sector_mm2=cap,demands_mm2=demands))
    area=2*c['pickup_mm'][0]*c['pickup_mm'][1]*1e-6
    base=(.00035/(.5*area)+.000025/(.12*area)+.0003/area+.005/(20*area)+.020/(400*.0002*(c['pickup_mm'][1]/1000)*2)+c['contact_R_K_W'])
    thermal=[];electrical=[]
    taps=[m for m in l['modules'] if m['layer']==0 and m['petal']==0]
    for name,p in [('CMS_PS_comparator',7.8),('channel_scaled_proxy',7.8*122880/30208)]:
        q=p+c['leakage_W_module'];current=p/12;drop=loss=0;last=678
        for k,m in enumerate(sorted(taps,key=lambda m:m['radius_mm'],reverse=True)):
            r=m['radius_mm'];res=2*c['resistivity_ohm_mm2_m']*(last-r)/1000/(12*.2)
            seg=(len(taps)-k)*current;drop+=seg*res;loss+=seg*seg*res;last=r
        heat=q*len(taps)+5+loss
        electrical.append(dict(load=name,round_trip_drop_V=drop,return_drop_V=drop/2,loss_W=loss,
            passed=drop<1 and drop/2<.2,petal_W=heat,
            flow=[dict(g_s=g,capacity_W=g*200*.35,passed=heat<=g*200*.35) for g in c['flow_g_s']]))
        for lift in (0,1.5,3,4.5):
            R=base+(lift+.4)/1000/(100*area)
            for cool in c['coolant_C']:
                t=cool+q*R;thermal.append(dict(load=name,lift_mm=lift,coolant_C=cool,R_K_W=R,sensor_C=t,passed=t<=-20))
    data=[]
    for rate in (1e6,40e6):
        for occ in (1e-5,1e-4,1e-3):
            payload=122880*len(taps)*occ*rate*32*1.2/1e9
            data.append(dict(accepted_events_s=rate,cell_occupancy=occ,petal_payload_Gbps=payload,
                required_uplinks=math.ceil(payload/8.96),two_uplink_comparator_passed=payload<=2*8.96,
                fibres_per_harness_qualified=None))
    legs=cooling(c);length=sum(p['dims']['major']*p['dims']['angle'] if p['kind']=='torus' else p['dims']['length'] for p in legs)
    corners=[math.hypot(m['radius_mm']+51.5,24.5) for m in l['modules']]
    return dict(status='SCREEN; no engineering qualification',execution=execution(),rings=l['rings'],discs=l['discs'],modules=len(l['modules']),
        modules_per_disc=len(l['modules'])//len(l['discs']),modules_per_petal=len(taps),channels_per_module=122880,channels=len(l['modules'])*122880,
        active_area_m2=len(l['modules'])*48*96/1e6,projected_area_to_nominal_annulus_ratio=len(l['modules'])*48*96/(len(l['discs'])*math.pi*(c['annulus_mm'][1]**2-c['annulus_mm'][0]**2)),
        cooling_length_mm_per_petal=length,pickup_area_mm2=area*1e6,maximum_module_corner_radius_mm=max(corners),
        board_corner_radius_mm=math.hypot(695+10,26),minimum_collector_axial_clearance_mm=c['disc_z_mm'][0]-13.5-1310,
        endcap_harnesses_per_end=216,endcap_loops_per_end=72,barrel_harnesses_per_end=sum(barrel_by_sector),barrel_loops_per_end=sum(barrel_loops),
        combined_trunk_packing=packing,thermal=thermal,electrical_flow=electrical,data_link_sensitivity=data,
        external_bends=[dict(bend_mm=b,required_axial_mm=max(b+13.4/2,25),available_axial_mm=70,required_radial_mm=b+13.4/2,available_radial_mm=25,passed=max(b+13.4/2,25)<=70 and b+13.4/2<=25) for b in c['bend_radius_mm']],
        limitations=['Thermal/contact conductivities are hypotheses, no FEA or CTE qualification.',
        f"Local{c['entry_bend_mm']}mm entry bend and multi-metre serpentine pressure drop require review.",
        'Effective fanout omits individual vias and connector transitions; no installation claim.',
        'Standalone native material excludes barrel; combined trunk demand explicitly includes barrel.',
        'Finite vacuum coverage is not full tracking efficiency or reconstruction.'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'build/short-strip-endcap');a=p.parse_args()
    c=load();l=build(c);a.output.mkdir(parents=True,exist_ok=True)
    (a.output/'screening.json').write_text(json.dumps(screen(c,l),indent=2)+'\n')
    print(len(l['modules']),'modules')
