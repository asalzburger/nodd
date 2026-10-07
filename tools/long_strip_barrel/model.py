"""DES-022 deterministic paired-strip stave and full-load bending/shear screen."""
import hashlib,json,math,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
INPUT=Path(__file__).with_name('inputs.json')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(path=INPUT):
 c=json.loads(Path(path).read_text())
 if c['schema_version']!=1:raise ValueError('Unsupported schema')
 for p,h in c['input_sha256'].items():
  if sha(ROOT/p)!=h:raise ValueError('Pinned source changed: '+p)
 for k in ('core_mm','skin_mm','tube_OD_mm','tube_wall_mm','pitch_mm','gravity_budget_mm'):
  if not math.isfinite(c[k]) or c[k]<=0:raise ValueError('Invalid '+k)
 if not 0<2*c['tube_wall_mm']<c['tube_OD_mm']<c['core_mm']:raise ValueError('Pipe does not fit core')
 if c['rows']%4 or c['rows']//4>c['pairs_per_circuit']:raise ValueError('Cooling circuits exceed paired-module cap')
 if c['active_mm']!=[96,96,.3] or c['pitch_mm']!=.08:raise ValueError('Retain 1200 true strips per face')
 if not c['stereo_rad'] or c['row_lift_mm']<1.5:raise ValueError('Unsupported stereo or row clearance')
 return c

def axes(phi,tilt=0,stereo=0,side=None):
 if side is None:
  a=phi+tilt;u=[-math.sin(a),math.cos(a),0];v=[0,0,1];n=[math.cos(a),math.sin(a),0]
 else:
  u=[-side*math.sin(phi),side*math.cos(phi),0];v=[-math.cos(phi),-math.sin(phi),0];n=[0,0,side]
 co,si=math.cos(stereo),math.sin(stereo)
 return [[co*u[i]+si*v[i] for i in range(3)],[-si*u[i]+co*v[i] for i in range(3)],n]
def point(center,frame,local):return [center[i]+sum(frame[j][i]*local[j] for j in range(3)) for i in range(3)]
def execution():return dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()))
def build(c):
 p=(2*c['active_half_length_mm']-96*(math.cos(.02)+math.sin(.02)))/(c['rows']-1)
 staves=[];sensors=[];pairs=[]
 for layer,r in enumerate(c['radii_mm']):
  n=2*math.ceil(math.pi/(2*math.atan((96-c['phi_margin_mm'])*math.cos(math.radians(c['tilt_deg']))/(2*(r+5)))))
  for k in range(n):
   phi=k*2*math.pi/n;f=axes(phi,math.radians(c['tilt_deg']));center=[r*math.cos(phi),r*math.sin(phi),0];name=f'L{layer}_S{k}'
   staves.append(dict(name=name,layer=layer,stave=k,center_mm=center,frame=f,phi_rad=phi,radius_mm=r))
   for row in range(c['rows']):
    z=(row-(c['rows']-1)/2)*p;lift=row%2*c['row_lift_mm'];w=c['core_mm']/2+c['core_glue_mm']+c['skin_mm']+c['low_pickup_mm']+c['spreader_mm']+lift+c['sensor_glue_mm']+.15
    pair=len(pairs);pairs.append(dict(id=pair,name=f'{name}_M{row}',layer=layer,stave=k,row=row,z_mm=z,lift_mm=lift,separation_mm=2*w))
    for face in (0,1):
     stereo=(face-.5)*c['stereo_rad'];sf=axes(phi,math.radians(c['tilt_deg']),stereo)
     sensors.append(dict(id=len(sensors),sensor_id=len(sensors),module_id=pair,face=face,layer=layer,layer_id=layer,station_id=layer,name=f'{name}_M{row}_F{face}',center_mm=point(center,f,[0,z,(2*face-1)*w]),u=sf[0],v=sf[1],n=sf[2],half_u_mm=48,half_v_mm=48,subsystem='long_strip'))
 return dict(staves=staves,pairs=pairs,modules=sensors,row_pitch_mm=p,scope='PROTOTYPE paired one-dimensional sensors')

def deflection(c,payload,count,E=70,G=5,factor=2):
 """Independent released-span bound with actual continuous/discrete gravity loads.
 No silicon stiffness credit. Include support reaction/overhang moment allowance.
 """
 H=c['half_length_mm'];ends=H-10;anchors=[-ends+i*2*ends/(count-1) for i in range(count)]
 b=c['stave_width_mm'];t=c['skin_mm'];d=c['core_mm']/2+c['core_glue_mm']+t/2
 I=2*(b*t**3/12+b*t*d*d);EI=E*1000*I
 S=G*(b*c['core_mm']-4*math.pi*(c['tube_OD_mm']/2)**2-c['mount_width_mm']*c['core_mm'])*5/6
 q=payload['continuous_g']/1000*c['gravity_mm_s2']/1000/(2*H)*factor
 points=payload['point_loads'];worst=dict(total_mm=0)
 for a,bb in zip(anchors,anchors[1:]):
  L=bb-a;loads=[(z-a,m/1000*9.80665*factor) for z,m in points if a<=z<=bb]
  outside=sum(m/1000*9.80665*factor for z,m in points if abs(z)>ends)
  # An overhang moment can deflect the adjacent released span. Bound every span
  # by both end moments; core-only overhang weight and discrete overhang payload.
  moment=q*10**2/2+outside*10
  extra=2*moment*L**2/(9*math.sqrt(3)*EI)+q*10**4/(8*EI)+q*10**2/(2*S)+outside*10**3/(3*EI)+outside*10/S
  for k in range(101):
   x=L*k/100
   bend=q*x*(L**3-2*L*x*x+x**3)/(24*EI);shear=q*x*(L-x)/(2*S)
   for pos,P in loads:
    if x<=pos:
     bend+=P*(L-pos)*x*(L*L-(L-pos)**2-x*x)/(6*L*EI);shear+=P*(L-pos)*x/(L*S)
    else:
     bend+=P*pos*(L-x)*(L*L-pos*pos-(L-x)**2)/(6*L*EI);shear+=P*pos*(L-x)/(L*S)
   total=bend+shear+extra
   if total>worst['total_mm']:worst=dict(total_mm=total,bending_mm=bend,core_shear_mm=shear,overhang_allowance_mm=extra,span_mm=L,z_mm=a+x)
 return dict(count=count,anchors_z_mm=anchors,EI_N_mm2=EI,shear_rigidity_N=S,E_GPa=E,G_MPa=G,load_factor=factor,**worst,gravity_budget_passed=worst['total_mm']<=c['gravity_budget_mm'])
def anchors(c,payload):
 scan=[deflection(c,payload,n) for n in range(2,33)]
 passing=[s for s in scan if s['gravity_budget_passed']]
 if not passing:raise ValueError('No tested anchor count passes')
 minimum=passing[0];recommended=next(x for x in scan if x['count']>=minimum['count'] and x['count']%2 and x['total_mm']<=.8*c['gravity_budget_mm'])
 return dict(minimum=minimum,recommended=recommended,scan=scan,sensitivity=[deflection(c,payload,recommended['count'],E,G,F) for E,G,F in ((70,5,1),(70,5,2),(100,10,2),(140,20,2))],load=payload)
