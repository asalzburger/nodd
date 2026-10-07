"""Standalone DES023, shared cooled structural carriers and cumulative services."""
import argparse,importlib.util,json,math,sys
from pathlib import Path
from collections import defaultdict
from model import ROOT,INPUT,load,build,axes,point,barrel
sys.path.append(str(ROOT/'tools/long_strip_barrel'))
from components import Export,I,TUBE,compose


def sector(x,name,role,mat,side,z,ri,ro,start,angle,w,thick):return x.add(name,role,mat,[0,0,side*(z+w)],I,'sector',dict(rmin=ri,rmax=ro,length=thick,start=start,angle=angle))

def petal(c,x,p):
 name=p['name'];side=p['side'];z=abs(p['z_mm']);phi=p['phi_rad'];f=axes(phi,side=side);o=[0,0,side*z];start=p['petal']*2*math.pi/12+c['seam_rad'];angle=2*math.pi/12-2*c['seam_rad']
 core,ce=sector(x,name+'_core','core','CarbonFoam',side,z,784,1130,start,angle,0,5)
 for sign in (-1,1):
  sector(x,name+f'_glue{sign}','support','Epoxy',side,z,784,1130,start,angle,sign*2.55,.1)
  sector(x,name+f'_skin{sign}','support','CFRP',side,z,784,1130,start,angle,sign*2.75,.3)
  # Insulated core buses have explicit, disjoint cuts; no material occupies the
  # same volume as foam or the neighbouring outer collection strip.
  for label,ri,ro,sa,ang in [('spine',805,1115,start+angle-.01,.007),('collection',1115,1118,start,angle)]:
   for label2,w,th,mat in [('PI',sign*1.775,.15,'Polyimide'),('Cu',sign*1.875,.05,'Copper')]:
    node,e=sector(x,name+f'_{sign}_{label}_{label2}','bus',mat,side,z,ri,ro,sa,ang,w,th)
    x.cut(core,ce,'sector',[0,0,side*w],I,dict(rmin=ri,rmax=ro,length=th,start=sa,angle=ang))
  board_o=[1123*math.cos(phi),1123*math.sin(phi),side*z]
  x.box(name+f'_board{sign}','end_board','Electronics',board_o,f,[0,0,sign*7.5],[20,12,2])
 for j,u in enumerate(c['web_u_mm']):
  outer=math.sqrt(c['web_outer_radius_mm']**2-(abs(u)+c['web_width_mm']/2)**2);length=outer-c['web_inner_mm'];v=-(outer+c['web_inner_mm'])/2
  center=point([0,0,0],f,[u,v,0]);size=dict(sx=c['web_width_mm'],sy=length,sz=5)
  # Full-height integral web ends before the radial collection bus.
  x.cut(core,ce,'box',center,f,size);x.box(name+f'_web{j}','integral_web','CFRP',o,f,[u,v,0],[c['web_width_mm'],length,5])
 for j,uc in enumerate(c['circuit_centers_u_mm']):
  for leg in (-1,1):
   length=c['pipe_outer_mm']-c['pipe_inner_mm'];local=[uc+leg*10,-(c['pipe_inner_mm']+c['pipe_outer_mm'])/2,0];pos=point(o,f,local);loc=point([0,0,0],f,local);tf=compose(f,TUBE)
   x.cut(core,ce,'tube',loc,tf,dict(rmin=0,rmax=1.25,length=length))
   for role,mat,lo,hi in [('cooling_tube','Titanium',1.11,1.25),('coolant','CO2',0,1.11)]:x.add(name+f'_{j}_{leg}_{role}',role,mat,pos,tf,'tube',dict(rmin=lo,rmax=hi,length=length))
  local=[uc,-805,0];loc=point([0,0,0],f,local);pos=point(o,f,local);dims=dict(major=10,rmin=0,rmax=1.25,start=0,angle=math.pi)
  x.cut(core,ce,'torus',loc,f,dims)
  for role,mat,lo,hi in [('cooling_bend','Titanium',1.11,1.25),('coolant','CO2',0,1.11)]:x.add(name+f'_{j}_{role}',role,mat,pos,f,'torus',dict(dims,rmin=lo,rmax=hi))
 # Continuous rim lands distribute the three kinematic contact reactions.
 for label,ri,ro in [('inner',784.2,785.5),('outer',1119,1137)]:
  sector(x,name+'_'+label+'_land','mount','Epoxy',side,z,ri,min(ro,1130),start,angle,-3,.2)
  sector(x,name+'_'+label+'_shoe','mount','CFRP',side,z,ri,ro,start,angle,-4.1,2)
 contacts=[(784.9,phi,.6,.3),(1123,phi-math.radians(10),1.25,.6),(1123,phi+math.radians(10),1.25,.6)]
 for j,(r,a,outer,inner) in enumerate(contacts):
  pos=[r*math.cos(a),r*math.sin(a),side*z];loc=[pos[0],pos[1],0]
  x.cut(core,ce,'tube',loc,I,dict(rmin=0,rmax=outer,length=5))
  x.add(name+f'_pot{j}','mount','Epoxy',pos,I,'tube',dict(rmin=inner,rmax=outer,length=5))
  x.add(name+f'_pin{j}','mount','Titanium',pos,I,'tube',dict(rmin=0,rmax=inner,length=5))
 return ce

def pair_parts(c,x,l):
 for m in l['modules']:
  p=l['pairs'][m['module_id']];o=p['center_mm'];f=p['frame'];sf=[m['u'],m['v'],m['n']];sign=2*m['face']-1;lift=p['lift_mm'];name=m['name']
  x.add(name,'sensitive','Silicon',m['center_mm'],sf,'box',dict(sx=96,sy=96,sz=.3),dict(system=6,layer=p['layer'],stave=p['petal'],module=p['local_id'],sensor=m['face']))
  g,e=x.add(name+'_guard','guard','Silicon',m['center_mm'],sf,'box',dict(sx=97,sy=97,sz=.3));x.cut(g,e,'box',[0,0,0],I,dict(sx=96,sy=96,sz=.3))
  x.box(name+'_pickup','pickup','Graphite',o,f,[0,0,sign*(2.9+(.1+lift)/2)],[42,42,.1+lift])
  x.add(name+'_spreader','spreader','Graphite',point(o,f,[0,0,sign*(3.05+lift)]),sf,'box',dict(sx=96,sy=96,sz=.1))
  x.box(name+'_glue','module_glue','Epoxy',o,f,[0,0,sign*(3.2+lift)],[42,42,.2])
  x.add(name+'_edge_land','spreader','Graphite',point(o,sf,[*c['edge_land_uv_mm'],sign*(3.05+lift)]),sf,'box',dict(zip(('sx','sy','sz'),c['edge_land_mm'])))
  x.box(name+'_hybrid_post','pickup','Graphite',o,f,[55,c['hybrid_v_mm'],sign*(3.25+lift)],[4,12,.3])
  x.box(name+'_hybrid_bond','module_glue','Epoxy',o,f,[55,c['hybrid_v_mm'],sign*(3.425+lift)],[4,12,.05])
  x.box(name+'_hybrid','electronics','Electronics',o,f,[55,c['hybrid_v_mm'],sign*(c['hybrid_normal_base_mm']+lift)],c['hybrid_size_mm'])
  x.box(name+'_tail','flex','Polyimide',o,f,[c['tail_u_mm'],c['hybrid_v_mm'],sign*(3.8+lift)],[c['tail_width_mm'],12,.15])

def routes(c,l):
 import gzip
 background=json.load(gzip.open(ROOT/'docs/validation/DES-022/inventory.json.gz'))['engineering']['services']['routes'];sectors=[]
 for i in range(12):
  selected=[r for r in background if r['side']==1 and r['sector']==i];sectors.append([sum(r['harnesses'] for r in selected),sum(len(r['cooling_circuits']) for r in selected)])
 result=[]
 for p in l['petals']:
  members=[pair['id'] for pair in l['pairs'] if pair['layer']==p['layer'] and pair['petal']==p['petal']]
  f=axes(p['phi_rad'],side=p['side']);circuits=[[] for _ in c['circuit_centers_u_mm']]
  for mid in members:
   u=sum(l['pairs'][mid]['center_mm'][i]*f[0][i] for i in range(2));j=min(range(len(circuits)),key=lambda j:min(abs(u-c['circuit_centers_u_mm'][j]-s*10) for s in (-1,1)));circuits[j].append(mid)
  harnesses=[members[j:j+12] for j in range(0,len(members),12)]
  if any(len(a)>12 for a in circuits+harnesses):raise ValueError('Group cap exceeded')
  result.append(dict(id=p['name'],side=p['side'],station=p['station'],sector=p['petal'],pairs=members,circuits=circuits,harnesses=harnesses,waypoints_rz_mm=[[1059.38,p['z_mm']],[1123,p['z_mm']+p['side']*7.5],[1106.5,p['z_mm']+p['side']*20],[1156.5,p['z_mm']+p['side']*70],[1156.5,p['z_mm']+p['side']*130],[1156.5,p['side']*3500]],topology='paired faces → insulated core buses → outer EoS → 3 pair harnesses / 6 U circuits → fan → cumulative shared corridor'))
 return result,sectors

def service_solids(c,x,l):
 rr,background=routes(c,l);segments=[];packing=[]
 for side in (-1,1):
  cumulative=[list(a) for a in background];prev=1435
  def segment(zone,a,b,ri,ro,new=None):
   counts=[list(v) for v in cumulative]
   if new is not None:
    for i in range(12):counts[i][0]+=len(new[i]['harnesses']);counts[i][1]+=len(new[i]['circuits'])
   for i,(h,loops) in enumerate(counts):
    manifolds=math.ceil(loops/8);angle=2*math.pi/12*.75;cap=angle/2*((ro-.5)**2-(ri+.5)**2)*(b-a);const=defaultdict(float)
    # All upstream loads pass through each service section. Incoming current-disc
    # harnesses additionally reserve radial travel +R50 and R25 quarter turns.
    length=b-a;extra=0 if new is None else len(new[i]['harnesses'])*(1123-1106.5+math.pi*50/2)
    cable_length=h*length+extra;fibre_length=cable_length
    const['Copper']=6.14*cable_length;const['Polyimide']=5.24*cable_length+(48*math.pi/4*(.25**2-.125**2)+math.pi*(1.8**2-1.5**2))*fibre_length;const['Silica']=48*math.pi/4*.125**2*fibre_length
    const['Titanium']=manifolds*length*math.pi/4*((8**2-6**2)+(12**2-10**2));const['CO2']=manifolds*length*math.pi/4*(6**2+10**2)
    if new is not None:
     pl=len(new[i]['circuits'])*2*(25+math.pi*25/2);const['Titanium']+=pl*math.pi*(1.25**2-1.11**2);const['CO2']+=pl*math.pi*1.11**2
    name=f'{zone}_{side}_{a:.6f}_{i}';mat=x.materials.effective(name,dict(const),cap);x.add(name,'routed_services',mat,[0,0,side*(a+b)/2],I,'sector',dict(rmin=ri+.5,rmax=ro-.5,length=b-a,start=i*2*math.pi/12,angle=angle))
    for j,(r0,r1) in enumerate(((ri,ri+.5),(ro-.5,ro))):x.add(name+f'_rail{j}','service_tray','Aluminium',[0,0,side*(a+b)/2],I,'sector',dict(rmin=r0,rmax=r1,length=b-a,start=i*2*math.pi/12,angle=angle))
   segments.append(dict(side=side,zone=zone,z_mm=[a,b],r_mm=[ri,ro],sector_counts=counts))
   if side==1:
    for scenario,phi,pack,spare,power in [('reference',.75,.5,1,6),('adverse',.5,.4,1.25,6),('CMS_gross_control',.75,.5,1,13.4)]:
     cap2=phi*pack*math.pi*((1169-.5)**2-(1144+.5)**2)/12;demands=[spare*(h*math.pi/4*(power**2+3.6**2)+math.ceil(lo/8)*math.pi/4*(8**2+12**2)) for h,lo in counts]
     packing.append(dict(zone=zone,z_mm=[a,b],scenario=scenario,capacity_per_sector_mm2=cap2,sector_demand_mm2=demands,passed=max(demands)<=cap2))
  for station,z in enumerate(c['disc_z_mm']):
   a=z+20;b=z+130
   if a<=prev:raise ValueError('Service fan overlaps previous fan')
   segment('trunk',prev,a,1144,1169)
   new=sorted([r for r in rr if r['side']==side and r['station']==station],key=lambda r:r['sector']);segment('fan',a,b,1100,1169,new)
   for i,r in enumerate(new):cumulative[i][0]+=len(r['harnesses']);cumulative[i][1]+=len(r['circuits'])
   prev=b
  segment('trunk',prev,3500,1144,1169)
 return dict(routes=rr,segments=segments,packing=packing,scope='Combined barrel+endcap cumulative corridor, replacing the barrel-only standalone trunk',bend_reservation=dict(cable_R_mm=50,pipe_R_mm=25,fan_radial_width_mm=69,fan_axial_width_mm=110,qualified=False))

def engineering(c,x,l):
 masses=[sum(e['mass_g'] for e in x.entities if e['name'].startswith(p['name']+'_')) for p in l['petals']];mass=max(masses);b=2*784*math.sin((2*math.pi/12-.004)/2);t=.3;d=2.75;I2=2*(b*t**3/12+b*t*d*d);A=b*5-12*math.pi*1.25**2-4*2*5;L=1123-784.9;cases=[]
 for g in (.25,1):
  for E,G in ((70,5),(100,10),(140,20)):
   q=mass/1000*9.80665*g/L;bend=5*q*L**4/(384*E*1000*I2);shear=q*L*L/(8*G*A*5/6);cases.append(dict(normal_acceleration_g=g,E_GPa=E,G_MPa=G,mass_per_petal_g=mass,span_mm=L,bending_mm=bend,core_shear_mm=shear,total_with_joint_mm=bend+shear+.01,passed=bend+shear+.01<=.05))
 q=mass/1000*9.80665/L;Iplane=2*t*b**3/12;Splane=70000/(2*1.3)*2*t*b;inplane=5*q*L**4/(384*70000*Iplane)+q*L*L/(8*Splane)
 return dict(normal_load=cases,in_plane_gravity_proxy_mm=inplane,maximum_petal_mass_g=mass,carrier_width_lower_bound_mm=b,limits=['Normal screen assumes distributed full-width rim reactions; three discrete contacts and narrow inner key require plate/joint/global-ring FEA.','0.25g axial load is an unsigned operating hypothesis;1g horizontal handling can fail and needs a handling frame.','No web/silicon stiffness credit; measured skin/foam/bond behavior, CTE and thermal bow unknown.','Thermal/CO2 pressure drop, radiation leakage, readout occupancy and dielectric qualification absent.'])

def export(c,out):
 l=build(c);x=Export(c,'LongStripEndcap')
 for p in l['petals']:petal(c,x,p)
 pair_parts(c,x,l)
 for lid,(side,j) in enumerate((s,j) for s in (1,-1) for j in range(6)):
  for name,ri,ro in [('inner',783.5,785.5),('outer',1130,1140)]:x.add(f'Frame_L{lid}_{name}','bearing_ring','CFRP',[0,0,side*(c['disc_z_mm'][j]-6.1)],I,'tube',dict(rmin=ri,rmax=ro,length=2))
 eng=engineering(c,x,l);eng['services']=service_solids(c,x,l)
 thermal=[]
 for p in l['pairs']:
  f=axes((p['petal']+.5)*2*math.pi/12,side=p['side']);u=sum(p['center_mm'][i]*f[0][i] for i in range(2));v=-sum(p['center_mm'][i]*f[1][i] for i in range(2));distance=min(math.hypot(u-uc-s*10,max(c['pipe_inner_mm']-v,v-c['pipe_outer_mm'],0)) for uc in c['circuit_centers_u_mm'] for s in (-1,1));thermal.append(distance)
 eng['thermal']=[dict(k_W_mK=k,worst_nearest_leg_mm=max(thermal),normal_slab_lower_bound_K=3.7*.0025/(k*.042*.042),pessimistic_lateral_rise_K=3.7*max(thermal)/1000/(k*.005*.042),pessimistic_sensor_C=-30+3.7*max(thermal)/1000/(k*.005*.042),passed=-30+3.7*max(thermal)/1000/(k*.005*.042)<=-10) for k in c['foam_k_W_mK']]
 eng['proxy_CO2_g_s_by_circuit']=[[len(a)*7.4/200 for a in r['circuits']] for r in eng['services']['routes']];eng['separations_mm']=sorted({p['separation_mm'] for p in l['pairs']});result=x.save(out,l,eng,INPUT)
 result['provenance']['endcap_source_hashes']={str(p.relative_to(ROOT)):barrel.sha(p) for p in Path(__file__).parent.glob('*.py')}
 (out/'expected.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=export(load(),a.output);print(json.dumps(dict(counts=r['counts'],normal=r['engineering']['normal_load'],packing=[p for p in r['engineering']['services']['packing'] if p['z_mm'][1]==3500]),indent=2))
