#!/usr/bin/env python3
"""Render original preliminary pixel figures/tables from the bundled, hashed snapshot.
Run from any directory: python3 scripts/pixel_figures.py. No DD4hep, network,
TeX shell escape, or files outside this report are required. Python + matplotlib.
"""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/nodd-tdr-matplotlib')
import argparse,hashlib,json,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon,Circle,FancyArrowPatch,Wedge,Patch
from matplotlib.lines import Line2D
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--balanced', action='store_true', help='Use the maintained balanced extraction; preserve imported historical snapshots.')
parser.add_argument('--endcap-only', action='store_true', help='Preserve existing barrel/carrier drawings; refresh current endcap figures and tables.')
args=parser.parse_args()
D=json.loads((ROOT/'data/pixel-layout.json').read_text())
M=json.loads((ROOT/'data/pixel-provenance.json').read_text())
assert hashlib.sha256((ROOT/'data/pixel-layout.json').read_bytes()).hexdigest()==M['snapshot_sha256']
S=json.loads((ROOT/'data/pixel-endcap-baseline.json').read_text())
SM=json.loads((ROOT/'data/pixel-endcap-provenance.json').read_text())
assert hashlib.sha256((ROOT/'data/pixel-endcap-baseline.json').read_bytes()).hexdigest()==SM['snapshot_sha256']
if args.balanced:
 CURRENT=json.loads((ROOT/'data/balanced-baseline.json').read_text())
 D=CURRENT['pixel']; S=CURRENT['endcap']
D['discs']=S['discs']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.titlesize':9,'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'savefig.transparent':False})
BLUE='#174382'; CYAN='#0479C1'; ORANGE='#ba6928'; GREEN='#7ca084'; GREY='#65717d'; LIGHT='#dae2ea'; RED='#934c67'
OUT=ROOT/'figures'; GEN=ROOT/'generated'; OUT.mkdir(exist_ok=True);GEN.mkdir(exist_ok=True)
def save(fig,name):
 if args.balanced and name not in ('pixel-overview','pixel-barrels'):
  plt.close(fig);return
 fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight',pad_inches=.04,metadata={'Creator':'nODD PubDoc pixel_figures.py','CreationDate':None,'ModDate':None});plt.close(fig)
def box(ax,x,y,w,h,c,**kw):
 ax.add_patch(Rectangle((x,y),w,h,facecolor=c,edgecolor=kw.pop('edgecolor',c),linewidth=kw.pop('lw',.5),**kw))
def poly(b,axes=('u','n'),half=('half_u_mm','half_w_mm')):
 return [[b['center_mm'][j]+s*b[axes[0]][j]*b[half[0]]+t*b[axes[1]][j]*b[half[1]] for j in range(2)] for s,t in [(-1,-1),(1,-1),(1,1),(-1,1)]]
def label(ax,text,x,y):ax.text(x,y,text,ha='center',va='center',fontsize=8)
def arrow(ax,a,b,c=GREY):ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':c,'lw':1})
# Positive-side barrel services: exact cable envelope bounds, schematic coolant paths.
E=json.loads((ROOT/'data/pixel-editorial-routing.json').read_text())
EP=json.loads((ROOT/'data/pixel-editorial-provenance.json').read_text())
assert hashlib.sha256((ROOT/'data/pixel-editorial-routing.json').read_bytes()).hexdigest()==EP['routing_snapshot_sha256']
if args.balanced:E=CURRENT['editorial']
fig,(ax,detail)=plt.subplots(1,2,figsize=(7.0,3.0),gridspec_kw={'width_ratios':[1.7,1]})
for a in [ax,detail]:
 for q in E['column_zero_positive']:
  box(a,q['abs_z_min_mm'],q['r_min_mm'],q['abs_z_max_mm']-q['abs_z_min_mm'],q['r_max_mm']-q['r_min_mm'],ORANGE,alpha=.6)
 for B in D['barrels']:
  r=B['layer']['r_m']*1000;a.plot([-550,550],[r,r],lw=1.5,c=BLUE)
  a.plot([0,552.8,580,580,605],[r+3,r+3,r+3,212,212],c=CYAN,lw=.9,ls='--')
  a.plot([555,575,575,605],[next(q['r_max_mm'] for q in E['terminal_positive'] if q['layer_id']==B['layer']['id'])]*2+[212,212],c=ORANGE,lw=.8)
 for disc in D['discs']:a.plot([disc['z_mm']]*2,disc['active_radial_span_mm'],lw=1.2,c=BLUE)
 box(a,555,27,50,207,RED,alpha=.14)
 box(a,605,190,3136-605,44,ORANGE,alpha=.18)
 a.plot([609,3136],[232,232],c=GREY,lw=1)
 a.set(xlabel='z [mm]',ylabel='r [mm]');a.grid(alpha=.12)
for disc in D['discs']:ax.text(disc['z_mm'],265 if disc['index']!=10 else 285,str(disc['index']),ha='center',fontsize=7)
ax.set(xlim=(-650,3250),ylim=(0,305),title='Pixel detector and positive-side services')
detail.set(xlim=(0,700),ylim=(0,270),title='Barrel extraction detail')
detail.annotate('end collection',xy=(580,140),xytext=(360,254),ha='center',fontsize=7,arrowprops={'arrowstyle':'->','color':RED})
fig.legend(handles=[Line2D([0],[0],c=BLUE,label='Sensitive layers'),Patch(facecolor=ORANGE,alpha=.6,label='Cable envelope / trunk'),Line2D([0],[0],c=CYAN,ls='--',label='Cooling path (schematic)'),Line2D([0],[0],c=GREY,label='Carrier')],loc='lower center',bbox_to_anchor=(.5,-.02),ncol=2,fontsize=7)
fig.tight_layout(rect=(0,.15,1,1));save(fig,'pixel-overview')
if not args.endcap_only:
 # Module plane, actual body/sensor/matrix dimensions.
 fig,aa=plt.subplots(1,2,figsize=(6.1,3.2))
 for ax,idx in zip(aa,[0,2]):
  b=D['barrels'][idx];s=b['shape'];uoff=s['offset_phi']
  box(ax,-s['body_phi']/2+uoff,-s['body_z']/2,s['body_phi'],s['body_z'],LIGHT,edgecolor=GREY)
  box(ax,-s['sensor_phi']/2,-s['sensor_z']/2,s['sensor_phi'],s['sensor_z'],'#a8c7df',edgecolor=CYAN)
  for u,v,hu,hv in s['patches']:box(ax,u-hu,v-hv,2*hu,2*hv,BLUE)
  ax.set_aspect('equal');ax.set(xlim=(-26,26),ylim=(-26,26),xlabel='u, tangential [mm]',ylabel='v, beam direction [mm]',title=f"{b['family'].capitalize()}: {s['body_phi']:g} × {s['body_z']:g} mm body")
  ax.grid(alpha=.12);ax.text(0,0,'active silicon',c='white',ha='center',fontsize=7)
 fig.tight_layout();save(fig,'pixel-modules')
 # True central z packing; phases and gaps visible in second zoom panel.
 fig,aa=plt.subplots(2,1,figsize=(6.1,2.85))
 for ax,idx in zip(aa,[0,2]):
  b=D['barrels'][idx];s=b['shape']
  for r in b['rows']:
   z=r['center_mm'][2]
   if abs(z)>95:continue
   box(ax,z-s['body_z']/2,0,s['body_z'],1,LIGHT,edgecolor=GREY)
   for zz in sorted({p[1] for p in s['patches']}):box(ax,z+zz-10,.18,20,.64,BLUE)
  ax.set(xlim=(-65,65),ylim=(-.25,1.3),yticks=[],title=f"{b['family'].capitalize()} stave: {s['body_z']+.2:g} mm body pitch")
  ax.axvline(0,c=ORANGE,lw=.8,ls='--');ax.set_xlabel('z [mm]')
 fig.tight_layout();save(fig,'pixel-packing')
 # Barrel end view with exact projected body/support and ring extents.
 fig,ax=plt.subplots(figsize=(5.6,5.2))
 for q in E['terminal_positive']:
  phi=math.degrees(q['phi_center_rad']);half=math.degrees(q['phi_width_rad'])/2
  ax.add_patch(Wedge((0,0),q['r_max_mm'],phi-half,phi+half,width=q['r_max_mm']-q['r_min_mm'],facecolor=ORANGE,alpha=.55,edgecolor=ORANGE,lw=.25))
 for B in D['barrels']:
  for b in B['columns']:
   ax.add_patch(Polygon(poly(b),facecolor=BLUE,lw=.3,edgecolor=BLUE))
   c=b['center_mm'];u=b['u'];n=b['n'];w=D['support']['families'][b['family']]['spine_mm']
   corners=[[c[j]+s*w/2*u[j]+d*n[j] for j in range(2)] for s,d in [(-1,.5),(1,.5),(1,5.225),(-1,5.225)]]
   ax.add_patch(Polygon(corners,facecolor=GREEN,lw=.3,edgecolor=GREY))
 for x in D['rings']['layers']:ax.add_patch(Circle((0,0),x['ring_outer_radius_mm'],fill=False,lw=.6,edgecolor=GREY))
 ax.set(aspect='equal',xlim=(-204,204),ylim=(-204,204),xlabel='x [mm]',ylabel='y [mm]');ax.legend(handles=[Patch(facecolor=BLUE,label='Module bodies'),Patch(facecolor=GREEN,label='Outward spines'),Patch(facecolor=ORANGE,alpha=.55,label='Cable envelopes (+z end)'),Line2D([0],[0],c=GREY,label='Mounting rings')],loc='upper center',bbox_to_anchor=(.5,1.18),ncol=2,fontsize=8);save(fig,'pixel-barrels')
 # Scale supports: thin surface layers inset table supplies exact thicknesses.
 fig,aa=plt.subplots(2,1,figsize=(6.1,3.0))
 for ax,idx in zip(aa,[0,2]):
  B=D['barrels'][idx];s=B['shape'];f=D['support']['families'][B['family']];width=s['body_phi'];sp=f['spine_mm']
  box(ax,-width/2,-.5,width,1,BLUE)
  y=.5
  for name,c in [('interface',ORANGE),('insulation','#dcc781'),('graphite',GREY),('top_skin',GREY),('core',GREEN),('bottom_skin',GREY)]:
   h=D['support']['stack_mm'][name];w=width if name in ['interface','insulation','graphite','top_skin'] else sp
   box(ax,-w/2,y,w,h,c);y+=h
  tube_w=.5+sum(D['support']['stack_mm'][k] for k in ['interface','insulation','graphite','top_skin'])+D['support']['stack_mm']['core']/2
  for x in [-f['tube_offset_mm'],f['tube_offset_mm']]:
   ax.add_patch(Circle((x,tube_w),f['tube_OD_mm']/2,facecolor=GREY,edgecolor=GREY));ax.add_patch(Circle((x,tube_w),f['tube_OD_mm']/2-f['tube_wall_mm'],facecolor=CYAN,edgecolor=CYAN))
  ax.set(xlim=(-25,25),ylim=(-1,6),xlabel='tangential coordinate [mm]',ylabel='w [mm]',title=f"{B['family'].capitalize()} support: {sp:g} mm spine");ax.invert_yaxis()
 fig.tight_layout();save(fig,'pixel-stave')
# Current endcap figures and station/ring tables.
from pixel_endcap_figures import render as render_endcap
if not args.balanced:render_endcap(S,D,ROOT)
if not args.endcap_only:
 # Load-path schematic, deliberately schematic.
 fig,ax=plt.subplots(figsize=(6.1,2.8));ax.axis('off');ax.set(xlim=(0,12),ylim=(0,5.2))
 for x in [1.8,3.1,4.8,6.5,8.2,9.9]:box(ax,x,1.45,.09,2.4,BLUE)
 for yy in [1.2,3.95]:box(ax,1.2,yy,9.5,.16,GREY)
 for x in [1.1,10.6]:box(ax,x,.85,.2,3.5,GREY)
 label(ax,'closed CFRP shell, 0.30 mm',5.9,4.8);arrow(ax,(5.9,4.5),(5.9,4.1))
 label(ax,'three longitudinal box rails',5.8,.3);arrow(ax,(5.8,.55),(5.8,1.2))
 ax.text(6,2.6,'disc tongues → couplings → rails → shell → end flanges',ha='center',va='center',fontsize=8,bbox={'facecolor':'white','edgecolor':'none','pad':3})
 label(ax,'|z| = 609 mm',1.2,.15);label(ax,'3136 mm',10.6,.15);save(fig,'pixel-carrier')
 # Electrical/cooling topology separate from manufacturing route.
 fig,ax=plt.subplots(figsize=(6.1,3.6));ax.axis('off');ax.set(xlim=(0,12),ylim=(0,7))
 items=[(.3,4.6,3,1.1,'barrel half-staves\nlongitudinal pickups'),(.3,1.6,3,1.1,'disc face flexes\nand half-ring circuits'),(4.2,4.6,3,1.1,'12 barrel sectors\n|z| = 555–605 mm'),(4.2,1.6,3,1.1,'disc rim collectors\n50 mm depth'),(8.2,3.2,3.2,1.2,'trunk reservation\nr = 190–234 mm')]
 for x,y,w,h,t in items:box(ax,x,y,w,h,LIGHT,edgecolor=GREY);label(ax,t,x+w/2,y+h/2)
 for a,b in [((3.3,5.15),(4.2,5.15)),((3.3,2.15),(4.2,2.15)),((7.2,5.15),(8.2,4)),((7.2,2.15),(8.2,3.6)),((9.8,3.2),(9.8,1.6))]:arrow(ax,a,b,ORANGE)
 label(ax,'last-disc adapter / rear turn',9,1.15);label(ax,'to |z| = 3300 mm, r = 680 mm',8.6,.65)
 ax.text(.02,.94,'SCHEMATIC • positive and negative ends served separately',transform=ax.transAxes,fontsize=7,c=GREY);save(fig,'pixel-services')
# Generated table rows; precision is display only.
bar=[]
for B in D['barrels']:
 bs=B['columns'];off=abs(bs[0]['normal_offset_mm']);bar.append(f"{B['layer']['id'][-2:]} & {B['layer']['r_m']*1000:g} & {off:.3f} & {len(bs)} & {len(B['rows'])} & {B['modules']} \\\\")
(GEN/'pixel-barrel-rows.tex').write_text('\n'.join(bar)+'\n')
if not args.endcap_only:
 from pixel_details import render
 render(D,ROOT,preserve_local=args.balanced)
artifacts=[p for p in sorted(OUT.glob('pixel-*.pdf'))]+list(sorted(GEN.glob('pixel-*.tex')))
if not args.balanced:(ROOT/'data/pixel-render-manifest.json').write_text(json.dumps({'generator':'scripts/pixel_figures.py','generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'detail_generator_sha256':hashlib.sha256((ROOT/'scripts/pixel_details.py').read_bytes()).hexdigest(),'endcap_generator_sha256':hashlib.sha256((ROOT/'scripts/pixel_endcap_figures.py').read_bytes()).hexdigest(),'mode':'endcap-only' if args.endcap_only else 'all','matplotlib':matplotlib.__version__,'snapshot_sha256':M['snapshot_sha256'],'endcap_snapshot_sha256':SM['snapshot_sha256'],'artifacts':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in artifacts]},indent=2)+'\n')
print(f'Rendered {len(artifacts)} figures/tables from verified snapshot.')
