#!/usr/bin/env python3
"""LAYOUT-001 covariance-only proxy, native tracker not reconstructed."""
import csv, hashlib, json, math, pathlib, platform, subprocess, sys
import numpy as np
import argparse
parser=argparse.ArgumentParser()
parser.add_argument("--source",type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[2])
parser.add_argument("--idres",type=pathlib.Path,required=True)
parser.add_argument("--idres-source",type=pathlib.Path,required=True)
parser.add_argument("--output",type=pathlib.Path,required=True)
args=parser.parse_args()
SOURCE=args.source.resolve()
TRACKER_REV='7c6d453fef12c3207b468c4fc99633fb393072a4'
LAYOUT_REV='5b4e5d9e563505aea17e9b792458708c3175ec4a'
IDRES=args.idres.resolve()
IDRES_SOURCE=args.idres_source.resolve()
OUT=args.output.resolve();OUT.mkdir(parents=True,exist_ok=True)
P_VALUES=[3,5,10,20,50,100]
read=lambda p: json.loads(subprocess.check_output(['git','-C',str(SOURCE),'show',TRACKER_REV+':'+p],text=True))
sha=lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
layout_bytes=subprocess.check_output(['git','-C',str(SOURCE),'show',LAYOUT_REV+':docs/layouts/LAYOUT-001.json'])
layout=json.loads(layout_bytes)
# These current source files are pinned at the tracker revision, not DES006.
sb=read('tools/short_strip_barrel/inputs-phi-tilted.json');lb=read('tools/long_strip_barrel/inputs.json')
se=read('tools/short_strip_endcap/inputs.json');le=read('tools/long_strip_endcap/inputs.json')
pixel=read('detector/config/pixel-barrel.json')
resolutions={'pixel': [pixel['module']['pixel_pitch_mm']/math.sqrt(12)/1000]*2,
 'short': [s/math.sqrt(12)/1000 for s in sb['cell_mm']],
 'long': [lb['pitch_mm']/math.sqrt(24)/math.cos(lb['stereo_rad']/2)/1000,
          lb['pitch_mm']/math.sqrt(24)/math.sin(lb['stereo_rad']/2)/1000]}
layers=[]
for g in layout['tracker']['sensitive_groups']:
 c=g['component'];family='pixel' if c=='pixel' else ('short' if c.startswith('short') else 'long')
 nominal_x0={'pixel':1.,'short':1.5,'long':2.}[family]
 l=dict(id=f"{c}-S{g['system']}-L{g['layer']}",subsystem=family,kind='cylinder' if g['side']==0 else 'disc',x0_percent=nominal_x0,sigma_rphi_m=resolutions[family][0],sigma_second_m=resolutions[family][1],source_group=g)
 if l['kind']=='cylinder':
  radius=([.034,.060,.106,.182][g['layer']-1] if family=='pixel' else ([r/1000 for r in sb['nominal_radii_mm']] if family=='short' else [r/1000 for r in lb['radii_mm']])[g['layer']])
  l.update(r_m=radius,z_min_m=g['z_min_m'],z_max_m=g['z_max_m'])
 else:
  rmin,rmax=(g['r_min_m'],g['r_max_m']) if family=='pixel' else [(x/1000) for x in (se['annulus_mm'] if family=='short' else le['annulus_mm'])]
  l.update(r_min_m=rmin,r_max_m=rmax,z_m=(g['z_min_m']+g['z_max_m'])/2)
 layers.append(l)
# Passive pipe: 0.8mm Be wall, native retained radiation length from DES025.
pipe=dict(id='Beampipe',kind='cylinder',subsystem='passive',r_m=.0274,z_min_m=-4.,z_max_m=4.,x0_percent=.8/352.7598267*100,sigma_rphi_m=1.,sigma_second_m=1.)
layers.insert(0,pipe)
(OUT/'layer-proxy.json').write_text(json.dumps(dict(status='PROTOTYPE; current nominal layers and binary response, proxy tracker material',layers=layers,resolutions_m=resolutions),indent=2)+'\n')

def intersections(eta):
 sh=math.sinh(eta); ch=math.cosh(eta);hits=[]
 for l in layers:
  if l['kind']=='cylinder':
   r=l['r_m'];z=r*sh;ok=l['z_min_m']<z<=l['z_max_m'];proj=ch
  elif eta==0:continue
  else:
   z=l['z_m'];r=z/sh;ok=l['r_min_m']<r<=l['r_max_m'];proj=1/abs(math.tanh(eta))
  if ok:hits.append((l,r,z,l['x0_percent']/100*proj))
 return sorted(hits,key=lambda h:h[1])

def posterior_control(eta,p,scale):
 # GLS fit to exact IdRes covariance model, including cumulative Highland increments.
 hits=intersections(eta);r=np.array([h[1] for h in hits]);x=np.cumsum([h[3]*scale for h in hits]);f=x*(1+.038*np.log(x))**2
 noise=(.0136/(p/math.cosh(eta)))**2*np.diff(np.r_[0,f])
 n=len(hits);arms=np.maximum(r[:,None]-r[None,:],0.)
 D=np.column_stack([np.ones(n),r,.5*r*r,arms]);W=np.diag([h[0]['sigma_rphi_m']**-2 for h in hits]);prior=np.diag(np.r_[0.,0.,0.,1/noise])
 C=np.linalg.inv(D.T@W@D+prior)
 # Outgoing azimuth=phi+k*r_last+sum(all scattering kicks). Scatter after last hit is retained.
 h=np.r_[0.,1.,r[-1],np.ones(n)];ang=math.sqrt(h@C@h)/math.cosh(eta)
 return dict(independent_sigma_inverse_pt_GeV_inverse=math.sqrt(C[2,2])/.9,independent_sigma_phi0_rad=math.sqrt(C[1,1]),independent_outgoing_projected_angle_rad=ang)

report=dict(status='PROTOTYPE; covariance estimates on current nominal tracker with assumed material; not tracking reconstruction performance',
 tracker_source_revision=TRACKER_REV, layout_source_revision=LAYOUT_REV,layout_input_sha256=hashlib.sha256(layout_bytes).hexdigest(),source_checkout_revision=subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','HEAD'],text=True).strip(),
 idres_revision=subprocess.check_output(['git','-C',str(IDRES_SOURCE),'rev-parse','HEAD'],text=True).strip(),binary_sha256=sha(IDRES),
 script_sha256=sha(__file__),platform=platform.platform(),python=platform.python_version(),numpy=np.__version__,
 field_T=3.,raw_B_column='Field-case index, not Tesla: IdRes src/main.cpp prints bIndex; 0 is first configured 3 T case.',resolutions_m=resolutions,
 material_assumption='Normal1%,1.5%,2%X0 per current pixel/short/long effective station. Sensitivity scales0.5/1/2; these are proxies inherited from old concept, not measured current material map. Be pipe0.8mm/native X0=352.7598267mm.',
 limitations=['No full tracker passive material map available.','Nominal effective cylinders and discs; finite sensor tiling/overlap/stereo separation omitted.','Current long pair has two 1D measurements represented by one diagonal effective 2D station.','Current strixel sigma_z<200um is counted pixel-like by upstream IdRes; do not infer physical pixel counts.','Uniform3T; straight reference crossings; no energy loss, inefficiency, occupancy, pattern recognition.','p is total momentum; pT=p/cosh eta.','Raw IdRes prints pT to0.01GeV, inverse pT sigma to1e-6GeV^-1; calculations use exact input pT.','Independent outgoing angle control uses IdRes thin scatterer/cumulative Highland model including last layer scatter; it is not an IdRes output.','Low-p eta2 straight crossing assumption may overstate final tracker lever arm.'],runs=[])
for eta in [0.,1.,2.]:
 for scale in [.5,1.,2.,1e-8]:
  name=f'e{eta:g}_m{scale:g}.geom';lines=['! PROTOTYPE LAYOUT-001 nominal layers, explicit material proxy','B 3 end','z 0 end','pt '+' '.join(f'{p/math.cosh(eta):.14g}' for p in P_VALUES)+' end',f'eta {eta:g} {eta:g} .1 end']
  for kind in ['cylinder','disc']:
   lines.append(kind)
   for l in layers:
    if l['kind']!=kind:continue
    values=([l['r_m'],l['z_min_m'],l['z_max_m']] if kind=='cylinder' else [l['r_min_m'],l['r_max_m'],l['z_m']])+[l['x0_percent']*scale,l['sigma_rphi_m'],l['sigma_second_m']]
    lines.append(' '.join(f'{v:.14g}' for v in values))
   lines.append('end')
  geom=OUT/name;geom.write_text('\n'.join(lines)+'\n')
  proc=subprocess.run([str(IDRES),name],cwd=OUT,text=True,capture_output=True);(OUT/(name+'.log')).write_text(proc.stdout+proc.stderr)
  if proc.returncode or 'No result' in proc.stdout or 'Unable to invert' in proc.stdout:raise RuntimeError(proc.stdout+proc.stderr)
  rows=list(csv.DictReader((OUT/(name+'.res')).open(),delimiter='\t'))
  if len(rows)!=len(P_VALUES):raise RuntimeError('denominator')
  x0=list(csv.DictReader((OUT/(name+'.X0')).open(),delimiter='\t'))
  parsed=[]
  for p,row in zip(P_VALUES,rows):
   pt=p/math.cosh(eta);sig=float(row['Sig_invPt'])/1000
   e=dict(p_GeV=p,pt_GeV=pt,eta=eta,sigma_inverse_pt_GeV_inverse=sig,fractional_pt_resolution=sig*pt,
     sigma_phi0_rad=float(row['Sig_phi']),sigma_cot_theta=float(row['Sig_cotT']),lever_arm_m=float(row['LeverArm']),**posterior_control(eta,p,scale))
   e['idres_independent_inverse_pt_difference']=sig-e['independent_sigma_inverse_pt_GeV_inverse'];parsed.append(e)
  assert all(abs(e['idres_independent_inverse_pt_difference']) <= .5e-6 for e in parsed), 'GLS agreement exceeds printed IdRes precision'
  report['runs'].append(dict(eta=eta,material_scale=scale,normal_layers=len(layers),crossed_effective_sensitive_stations=len(intersections(eta))-1,projected_x0_fraction=float(x0[0]['%X0'])/100,geometry_sha256=sha(geom),raw_sha256=sha(OUT/(name+'.res')),samples=parsed))
(OUT/'results.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
for run in report['runs']:
 if run['material_scale']==1:
  print('eta',run['eta'],'n',run['crossed_effective_sensitive_stations'],'X0',run['projected_x0_fraction'])
  for e in run['samples']:print(e['p_GeV'],round(e['fractional_pt_resolution']*100,4),e['sigma_phi0_rad'],e['independent_outgoing_projected_angle_rad'])
print('max difference',max(abs(e['idres_independent_inverse_pt_difference']) for run in report['runs'] for e in run['samples']))
print(OUT/'results.json')
