"""DES023 paired1D strip discs with cooled shared petal carriers."""
import importlib.util,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];INPUT=Path(__file__).with_name('inputs.json')
spec=importlib.util.spec_from_file_location('long_barrel',ROOT/'tools/long_strip_barrel/model.py');barrel=importlib.util.module_from_spec(spec);spec.loader.exec_module(barrel)
sha=barrel.sha;axes=barrel.axes;point=barrel.point;execution=barrel.execution

def load(path=INPUT):
 c=json.loads(Path(path).read_text())
 for p,h in c['input_sha256'].items():
  if sha(ROOT/p)!=h:raise ValueError('Pinned source changed: '+p)
 if c['core_inner_mm']<=783 or c['outer_frame_mm'][1]>1140 or c['fan_mm'][1]>1169:raise ValueError('Fixed service/body bounds violated')
 if c['disc_z_mm'][0]-9<=1435+10:raise ValueError('First disc does not clear barrel collector')
 if c['skin_mm']!=.3 or c['pitch_mm']!=.08 or c['active_mm']!=[96,96,.3]:raise ValueError('Unsupported stack/readout fixture')
 if c['tube_OD_mm']>=c['core_mm'] or c['tube_wall_mm']<=0:raise ValueError('Invalid cooled core')
 return c

def rings(c):
 span=96*(math.cos(.02)+math.sin(.02));a,b=c['annulus_mm'];r0=a+span/2;r1=b-span/2
 return [dict(ring=i,radius_mm=r0+(r1-r0)*i/(c['rings']-1),pairs=12*math.ceil(2*math.pi*(r0+(r1-r0)*i/(c['rings']-1))/(12*(96-c['phi_margin_mm'])))) for i in range(c['rings'])]

def build(c):
 rs=rings(c);sensors=[];pairs=[];petals=[]
 for lid,(side,station) in enumerate((s,j) for s in (1,-1) for j in range(6)):
  z=c['disc_z_mm'][station]
  for p in range(12):petals.append(dict(name=f'L{lid}_P{p}',layer=lid,side=side,station=station,petal=p,phi_rad=(p+.5)*2*math.pi/12,z_mm=side*z))
  local_ids=[0]*12
  for ring in rs:
   n=ring['pairs']
   for k in range(n):
    phi=(k+.5)*2*math.pi/n;petal=k//(n//12);mid=local_ids[petal];local_ids[petal]+=1;lift=(2*(ring['ring']%2)+k%2)*1.5;w=3.45+lift;pair=len(pairs)
    f=axes(phi,side=side);origin=[ring['radius_mm']*math.cos(phi),ring['radius_mm']*math.sin(phi),side*z]
    pairs.append(dict(id=pair,layer=lid,side=side,station=station,petal=petal,local_id=mid,ring=ring['ring'],column=k,phi_rad=phi,radius_mm=ring['radius_mm'],lift_mm=lift,separation_mm=2*w,center_mm=origin,frame=f))
    for face in (0,1):
     sf=axes(phi,stereo=(face-.5)*.04,side=side);sensors.append(dict(id=len(sensors),sensor_id=len(sensors),module_id=pair,face=face,layer=lid,layer_id=lid,station_id=lid,name=f'L{lid}_P{petal}_M{mid}_F{face}',center_mm=point(origin,f,[0,0,(2*face-1)*w]),u=sf[0],v=sf[1],n=sf[2],half_u_mm=48,half_v_mm=48,subsystem='long_strip'))
 return dict(petals=petals,rings=rs,pairs=pairs,modules=sensors,scope='Isolated paired1D long-strip endcap PROTOTYPE')
