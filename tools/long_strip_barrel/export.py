"""Standalone DD4hep long-strip barrel, conserved physical material and routes."""
import argparse,json,math
from collections import defaultdict
from pathlib import Path
from model import ROOT,INPUT,load,build,axes,point,anchors,deflection
from mechanics import solve
from components import Export,I,TUBE,compose,volume

def carrier(c,x,s,anchor_z=()):
 name=s['name'];o=s['center_mm'];f=s['frame'];H=c['half_length_mm'];b=c['stave_width_mm']
 def box(tag,role,mat,local,size,rot=None):return x.box(name+'_'+tag,role,mat,o,f,local,size,rot=rot)
 core,ce=box('core','core','CarbonFoam',[0,0,0],[b,2*H,c['core_mm']])
 for side in (-1,1):
  for tag,w,t,mat in [('glue',2.55,.1,'Epoxy'),('skin',2.7,.2,'CFRP')]:box(f'{side}_{tag}','support',mat,[0,0,side*w],[b,2*H,t])
  box(f'{side}_bus_PI','bus','Polyimide',[c['bus_u_mm'],0,side*2.875],[10,2*H,.15])
  box(f'{side}_bus_Cu','bus','Copper',[c['bus_u_mm'],0,side*3.01],[10,2*H,.12])
  for zside in (-1,1):
   box(f'{side}_{zside}_board','end_board','Electronics',[0,zside*1305,side*6.5],[20,25,2])
   box(f'{side}_{zside}_board_tail','flex','Polyimide',[27.5,zside*1305,side*4],[35,10,.15])
 for side in (-1,1):
  for circuit,uc in enumerate(c['loop_centers_u_mm']):
   for leg in (-1,1):
    local=[uc+leg*10,side*(20+H)/2,0];d=dict(rmin=0,rmax=1.25,length=H-20)
    x.cut(core,ce,'tube',local,TUBE,d)
    for role,mat,rmin,rmax in [('cooling_tube','Titanium',1.11,1.25),('coolant','CO2',0,1.11)]:
     x.add(f'{name}_{side}_{circuit}_{leg}_{role}',role,mat,point(o,f,local),compose(f,TUBE),'tube',dict(rmin=rmin,rmax=rmax,length=H-20))
   local=[uc,side*20,0];d=dict(major=10,rmin=0,rmax=1.25,start=math.pi if side>0 else 0,angle=math.pi)
   x.cut(core,ce,'torus',local,I,d)
   for role,mat,rmin,rmax in [('cooling_bend','Titanium',1.11,1.25),('coolant','CO2',0,1.11)]:
    x.add(f'{name}_{side}_{circuit}_{role}',role,mat,point(o,f,local),f,'torus',dict(d,rmin=rmin,rmax=rmax))
 # One edge web is on the inward shingle edge: an opposite web would cut the
 # neighbouring stave. Two potted lands/bolts provide a keyed contact per station.
 a=math.radians(c['tilt_deg']);r=s['radius_mm'];u=c['mount_u_mm'];R=r-42
 w0=-r*math.cos(a)+math.sqrt(R*R-(u-r*math.sin(a))**2)
 p=point(o,f,[u,0,w0]);theta=math.atan2(p[1],p[0])-s['phi_rad'];slope=math.tan(a-theta)
 for j,z in enumerate(anchor_z):
  for k,zz in enumerate((z-3,z+3)):
   loc=[u,zz,0];d=dict(sx=4,sy=4,sz=5);x.cut(core,ce,'box',loc,I,d)
   po,pe=box(f'A{j}_pot{k}','mount','Epoxy',loc,[4,4,5]);x.cut(po,pe,'tube',[0,0,0],I,dict(rmin=0,rmax=.6,length=5))
   x.add(f'{name}_A{j}_pin{k}','mount','Titanium',point(o,f,loc),f,'tube',dict(rmin=0,rmax=.6,length=5))
  box(f'A{j}_joint','mount','Epoxy',[u,z,-2.9],[4,12,.2]);box(f'A{j}_clamp','mount','Titanium',[u,z,-3.1],[4,12,.2])
  # Tangent bottom shoe meets a cylindrical ring without penetration.
  height=-3.2-w0
  x.add(f'{name}_A{j}_web','mount','CFRP',point(o,f,[u,z,(w0-3.2)/2]),compose(f,TUBE),'shoe',dict(sx=4,sy=12,sz=height,slope=slope))
 return core,ce

def sensors(c,x,l):
 staves={(s['layer'],s['stave']):s for s in l['staves']}
 for m in l['modules']:
  p=l['pairs'][m['module_id']];s=staves[m['layer'],p['stave']];o=s['center_mm'];f=s['frame'];sf=[m['u'],m['v'],m['n']];sign=2*m['face']-1;z=p['z_mm'];lift=p['lift_mm'];name=m['name']
  _,e=x.add(name,'sensitive','Silicon',m['center_mm'],sf,'box',dict(sx=96,sy=96,sz=.3),dict(system=c['system_id'],layer=m['layer'],stave=p['stave'],module=p['row'],sensor=m['face']))
  node,g=x.add(name+'_guard','guard','Silicon',m['center_mm'],sf,'box',dict(sx=97,sy=97,sz=.3));x.cut(node,g,'box',[0,0,0],I,dict(sx=96,sy=96,sz=.3))
  thick=c['low_pickup_mm']+lift
  x.box(name+'_pickup','pickup','Graphite',o,f,[0,z,sign*(2.8+thick/2)],[42,42,thick])
  x.add(name+'_spreader','spreader','Graphite',point(o,f,[0,z,sign*(2.8+thick+.05)]),sf,'box',dict(sx=96,sy=96,sz=.1))
  x.box(name+'_glue','module_glue','Epoxy',o,f,[0,z,sign*(2.8+thick+.2)],[42,42,.2])
  # Separate positive edge: bus lies below the hybrid, bond ribbons bridge the
  # die to it in z-local rows. Effective electronics explicitly contains air.
  x.box(name+'_hybrid','electronics','Electronics',o,f,[c['hybrid_u_mm'],z,sign*(4.5+lift)],[10,30,1])
  x.box(name+'_tail','flex','Polyimide',o,f,[c['hybrid_u_mm']+4,z,sign*(3.7+lift)],[6,20,.15])

def payload(x,H):
 continuous=0.;points=[];by_role=defaultdict(float)
 for e in x.entities:
  by_role[e['role']]+=e['mass_g']
  if e['role'] in ('core','support','bus','cooling_tube') or (e['role']=='coolant' and e['shape_kind']=='tube'):continuous+=e['mass_g']
  else:points.append([e['center_mm'][2],e['mass_g']])
 return dict(continuous_g=continuous,point_loads=points,total_mass_g=continuous+sum(p[1] for p in points),mass_by_role_g=dict(by_role),load_note='All attached components and coolant; gravity in worst transverse direction, rings excluded as grounded supports.')

def services(c,l):
 cables=math.pi/4*(c['power_OD_mm']**2+c['fibre_OD_mm']**2);pipe=math.pi/4*(8**2+12**2);routes=[];counts=defaultdict(lambda:[0,0])
 for s in l['staves']:
  sector=int(s['stave']*12/sum(a['layer']==s['layer'] for a in l['staves']))
  for side in (-1,1):
   ids=[p['id'] for p in l['pairs'] if p['layer']==s['layer'] and p['stave']==s['stave'] and (p['row']<c['rows']//2)==(side<0)]
   routes.append(dict(id=s['name']+str(side),side=side,sector=sector,pairs=ids,harnesses=2,cooling_circuits=[ids[:len(ids)//2],ids[len(ids)//2:]],waypoints_rz_mm=[[s['radius_mm'],side*1305],[s['radius_mm'],side*1340],[1156.5,side*1380],[1156.5,side*1435],[1156.5,side*3500]],signal='face tails → insulated face bus → end board → two pair harnesses → sector collector → longitudinal trunk',cooling='two U loops/half-stave → end coupling → sector manifold → 8/12mm supply/return trunks'))
   if side==1:counts[sector][0]+=2;counts[sector][1]+=2
 cap=math.pi*(1168.5**2-1144.5**2)/12
 pack=[]
 for name,phi,f,spare,bundle in [('reference',.75,.5,1,cables),('adverse',.5,.4,1.25,cables),('CMS_gross_control',.75,.5,1,math.pi/4*(13.4**2+3.6**2))]:
  demands=[spare*(counts[i][0]*bundle+math.ceil(counts[i][1]/8)*pipe) for i in range(12)]
  pack.append(dict(scenario=name,capacity_per_sector_mm2=cap*phi*f,per_sector_demand_mm2=demands,passed=max(demands)<=cap*phi*f))
 power=(5.4+2)*c['rows']/2;flow=(power/2)/200000*1000
 electrical=[dict(scenario=name,pairs=12,power_W=12*7.4,current_A=12*7.4/c['LV_V'],loop_drop_V=12*7.4/c['LV_V']*2*c['oneway_cable_m']*c['resistivity_ohm_mm2_m']/c['lv_conductor_mm2']*fac,return_drop_V=12*7.4/c['LV_V']*c['oneway_cable_m']*c['resistivity_ohm_mm2_m']/c['lv_conductor_mm2']*fac) for name,fac in [('reference',1),('warm_control',1.4)]]
 for q in electrical:q['passed']=q['loop_drop_V']<1 and q['return_drop_V']<.2
 return dict(routes=routes,packing=pack,electrical=electrical,circuits_per_half_stave=2,pairs_per_circuit=c['rows']//4,power_W_per_half_stave=power,proxy_CO2_g_s_per_circuit=flow,thermal=[dict(foam_k_W_mK=k,rise_K=(5.4+2)*.0025/(k*.042*.042),sensor_C=-30+(5.4+2)*.0025/(k*.042*.042)) for k in c['foam_k_W_mK']],limitations=['Cable envelopes benchmark; bend/connectors and electrical gauge not qualified.','Thermal slab lower bound omits spreading, adhesive/contact, boiling and pressure drop; flow uses unsigned200kJ/kg enthalpy fixture.','Combined endcap trunks are evaluated in DES-023; barrel-only packing is not a combined pass.'])

def route_solids(c,x,l):
 ledger=services(c,l)
 for side in (-1,1):
  for sector in range(12):
   selected=[r for r in ledger['routes'] if r['side']==side and r['sector']==sector]
   phi0=sector*2*math.pi/12;angle=2*math.pi/12*.75
   manifolds=math.ceil(sum(len(r['cooling_circuits']) for r in selected)/8)
   for zone,bounds in [('collector',c['collector_mm']),('trunk',c['trunk_mm'])]:
    ri,ro,z0,z1=bounds;cap=angle/2*((ro-.5)**2-(ri+.5)**2)*(z1-z0);const=defaultdict(float)
    if zone=='collector':
     for r in selected:
      radius=next(s['radius_mm'] for s in l['staves'] if s['name']+str(side)==r['id'])
      length=1156.5-radius+math.pi*50
      pv=2*length;fv=2*length
      const['Copper']+=6.14*pv;const['Polyimide']+=5.24*pv+(48*math.pi/4*(.25**2-.125**2)+math.pi*(1.8**2-1.5**2))*fv;const['Silica']+=48*math.pi/4*.125**2*fv
      pl=4*(1156.5-radius+math.pi*25)
      const['Titanium']+=pl*math.pi*(1.25**2-1.11**2);const['CO2']+=pl*math.pi*1.11**2
    else:
     for r in selected:
      pv=2*(z1-z0);fv=2*(z1-z0)
      const['Copper']+=6.14*pv;const['Polyimide']+=5.24*pv+(48*math.pi/4*(.25**2-.125**2)+math.pi*(1.8**2-1.5**2))*fv;const['Silica']+=48*math.pi/4*.125**2*fv
     const['Titanium']+=manifolds*(z1-z0)*math.pi/4*((8**2-6**2)+(12**2-10**2))
     const['CO2']+=manifolds*(z1-z0)*math.pi/4*(6**2+10**2)
    name=f'{zone}_{side}_{sector}';mat=x.materials.effective(name,dict(const),cap)
    x.add(name,'routed_services',mat,[0,0,side*(z0+z1)/2],I,'sector',dict(rmin=ri+.5,rmax=ro-.5,length=z1-z0,start=phi0,angle=angle))
    for j,(a,b) in enumerate(((ri,ri+.5),(ro-.5,ro))):x.add(name+f'_rail{j}','service_tray','Aluminium',[0,0,side*(z0+z1)/2],I,'sector',dict(rmin=a,rmax=b,length=z1-z0,start=phi0,angle=angle))
 return ledger

def export(c,out):
 l=build(c);one=dict(l,staves=l['staves'][:1],pairs=[p for p in l['pairs'] if p['stave']==0 and p['layer']==0],modules=[m for m in l['modules'] if m['layer']==0 and l['pairs'][m['module_id']]['stave']==0])
 # Search actual per-count mounting payload rather than treating silicon as load.
 scans=[]
 for n in range(2,33):
  trials=[]
  for layer in range(2):
   ss=next(s for s in l['staves'] if s['layer']==layer and s['stave']==0);single=dict(l,staves=[ss],modules=[m for m in l['modules'] if m['layer']==layer and l['pairs'][m['module_id']]['stave']==0])
   xx=Export(c,'LongStripBarrel');az=[-1310+i*2620/(n-1) for i in range(n)];carrier(c,xx,ss,az);sensors(c,xx,single);pl=payload(xx,1320);q=deflection(c,pl,n);q['limiting_layer']=layer;trials.append(q)
  scans.append(max(trials,key=lambda q:q['total_mm']))
 passing=[s for s in scans if s['gravity_budget_passed']];minimum=passing[0]
 selected=next(s for s in passing if s['count']%2 and s['total_mm']<=.8*c['gravity_budget_mm'])
 x=Export(c,'LongStripBarrel')
 for s in l['staves']:carrier(c,x,s,selected['anchors_z_mm'])
 sensors(c,x,l)
 for layer,r in enumerate(c['radii_mm']):
  for j,z in enumerate(selected['anchors_z_mm']):x.add(f'Ring_L{layer}_A{j}','bearing_ring','CFRP',[0,0,z],I,'tube',dict(rmin=r-45,rmax=r-42,length=6))
 selected_payload=max((payload(type('Payload',(),dict(entities=[e for e in x.entities if e['name'].startswith(f'L{j}_S0_')]))(),1320) for j in range(2)),key=lambda p:p['total_mass_g'])
 fem=solve(c,selected_payload,selected,20);fem_fine=solve(c,selected_payload,selected,10)
 if abs(fem['maximum_deflection_mm']-fem_fine['maximum_deflection_mm'])>1e-4:raise ValueError('Beam mesh not converged')
 beam=dict(continuous_beam=fem,continuous_beam_refined=fem_fine,minimum=minimum,recommended=selected,scan=scans,load=selected_payload,sensitivity=[deflection(c,selected_payload,selected['count'],E,G,F) for E,G,F in ((70,5,1),(70,5,2),(100,10,2),(140,20,2))])
 eng=dict(beam=beam,services=route_solids(c,x,l),sensor_separation_mm=sorted({p['separation_mm'] for p in l['pairs']}),ideal_binary_resolution_mm=dict(measured=.08/math.sqrt(24)/math.cos(.02),second=.08/math.sqrt(24)/math.sin(.02)))
 return x.save(out,l,eng,INPUT)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=export(load(),a.output);print(json.dumps(dict(counts=r['counts'],beam=r['engineering']['beam']['recommended'],packing=r['engineering']['services']['packing']),indent=2))
