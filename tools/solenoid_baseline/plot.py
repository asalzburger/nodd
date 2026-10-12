"""Scientific schematic from committed DES026 sizing + DES025 sensor bounds."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
import numpy as np
from model import axis_field

ROOT=Path(__file__).resolve().parents[2]
plt.rcParams.update({'svg.fonttype':'none','font.size':10})
sizing=ROOT/'docs/validation/DES-026/sizing.json'
tracker=ROOT/'docs/validation/DES-026/tracker-rz.json'
r=json.loads(sizing.read_text())['result']; t=json.loads(tracker.read_text())
fig=plt.figure(figsize=(13,8),layout='constrained')
grid=fig.add_gridspec(3,2,height_ratios=[.38,3,1.2],width_ratios=[4,1])
header=fig.add_subplot(grid[0,:]); header.axis('off')
ax=fig.add_subplot(grid[1,0]); zoom=fig.add_subplot(grid[1,1]); field=fig.add_subplot(grid[2,:])
colors={'pixel':'#9b59b6','short_barrel':'#2571a5','short_endcap':'#2571a5',
        'long_barrel':'#258460','long_endcap':'#258460'}
for g in t['groups']:
    ax.add_patch(Rectangle((g['z_min_m'],g['r_min_m']),g['z_max_m']-g['z_min_m'],
                          g['r_max_m']-g['r_min_m'],facecolor=colors[g['component']],alpha=.6))
ax.add_patch(Rectangle((-3.6,0),7.2,1.2,fill=False,linestyle='--',edgecolor='#59636b',linewidth=1.2))
# Vessel envelope is an allocation; no vessel wall / gap material is invented.
for a in (ax,zoom):
    a.add_patch(Rectangle((-3.85,r['vessel_inner_radius_m']),7.7,
                         r['vessel_outer_radius_m']-r['vessel_inner_radius_m'],
                         facecolor='#f4f0e7',edgecolor='#4a4a4a',linewidth=1.3,hatch='..'))
    a.add_patch(Rectangle((-3.6,r['cold_inner_radius_m']),7.2,
                         r['cold_outer_radius_m']-r['cold_inner_radius_m'],
                         facecolor='#c77823',edgecolor='none'))
    a.add_patch(Rectangle((-3.6,r['cold_inner_radius_m']),7.2,
                         r['winding_outer_radius_m']-r['cold_inner_radius_m'],
                         facecolor='#f4b342',edgecolor='none'))
    a.axhline(1.64,color='#6b6b6b',ls='-.',lw=1)
    a.axhline(1.70,color='#ae4934',ls='--',lw=1)
ax.set(xlim=(-4.15,4.15),ylim=(0,1.85),xlabel='z [m]',ylabel='r [m]',
       title='Tracker + inner solenoid: positive-r meridional schematic')
ax.grid(alpha=.15)
ax.text(0,1.08,'Tracker planning reservation: r ≤ 1.20 m, |z| ≤ 3.60 m',ha='center',fontsize=9)
ax.annotate('Vessel full length 7.70 m',xy=(3.85,1.56),xytext=(1.5,1.79),arrowprops={'arrowstyle':'->'},fontsize=9)
zoom.set(xlim=(-.1,.1),ylim=(1.18,1.74),xticks=[],ylabel='r [m]',title='Radial detail\nat z = 0')
for y,label in [(1.20,'tracker 1.200'),(1.24,'vessel inner 1.240'),
                (r['cold_inner_radius_m'],'cold inner 1.328'),
                (r['winding_outer_radius_m'],'winding outer 1.379'),
                (r['cold_outer_radius_m'],'cold outer 1.405'),
                (r['vessel_outer_radius_m'],'vessel outer 1.559'),
                (1.64,'assembly reserve 1.640'),(1.70,'ECAL ≥ 1.700')]:
    zoom.text(0,y,label,ha='center',va='bottom',fontsize=8,
              bbox={'facecolor':'white','alpha':.85,'edgecolor':'none','pad':1})
zoom.grid(axis='y',alpha=.15)
z=np.linspace(-4.15,4.15,401)
b=[axis_field(float(v),r['cold_inner_radius_m'],r['winding_outer_radius_m'],7.2,3) for v in z]
field.plot(z,b,color='#a15e14',lw=2)
field.axvspan(-3.6,3.6,color='#c9d2dc',alpha=.15)
field.set(xlim=(-4.15,4.15),ylim=(0,3.4),xlabel='z [m]',ylabel='Bz on axis [T]',
          title='Vacuum control: 3 T at the centre; field decreases towards the ends')
field.grid(alpha=.2)
handles=[Patch(color='#9b59b6',label='Pixel sensor bounds'),Patch(color='#2571a5',label='Short strips'),
         Patch(color='#258460',label='Long strips'),Patch(color='#f4b342',label='Uniform winding pack'),
         Patch(color='#c77823',label='Cold support allocation'),
         Patch(facecolor='#f4f0e7',edgecolor='#4a4a4a',hatch='..',label='Vessel / cryogenic allowance')]
header.text(.5,.95,'nODD DES-026 • 3 T solenoid baseline • DRAFT / PROTOTYPE',ha='center',va='top',fontsize=15)
header.legend(handles=handles,loc='lower center',ncol=3,fontsize=9,bbox_to_anchor=(.5,-.4))
fig.supxlabel('45,646 sensitive planes grouped into bounds; passive tracker solids omitted. Hatched volume is reserved space, not solid material.',fontsize=9)
outputs=[]
for ext in ('svg','png'):
    p=ROOT/f'docs/design/figures/DES-026-tracker-solenoid-rz.{ext}'
    fig.savefig(p,dpi=180,metadata={'Creator':'nODD tools/solenoid_baseline/plot.py'} if ext=='svg' else {})
    outputs.append(p)
report={'status':'DRAFT schematic','matplotlib':matplotlib.__version__,'numpy':np.__version__,
        'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (sizing,tracker,Path(__file__))},
        'output_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in outputs}}
(ROOT/'docs/validation/DES-026/figure.json').write_text(json.dumps(report,indent=2)+'\n')
print('Rendered SVG and PNG; metadata in docs/validation/DES-026/figure.json')
