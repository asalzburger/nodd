#!/usr/bin/env python3
"""Regenerate DES-002 dimensioned concept drawings; units mm, no engineering CAD."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
ROOT=Path(__file__).resolve().parents[2]
c=json.loads(Path(__file__).with_name('inputs.json').read_text());s=c['stack_mm'];out=ROOT/'docs/validation/DES-002'
plt.rcParams.update({'font.size':9,'svg.fonttype':'none','pdf.fonttype':42})
fig,axes=plt.subplots(2,2,figsize=(12,7.5),layout='constrained')
colors={'foam':'#e9c990','carbon':'#444e59','graphite':'#809097','tube':'#8399a5','glue':'#c67437'}
for row,typ in enumerate(['single','quad']):
 f=c['families'][typ];w=23 if typ=='single' else 43.2;bw=f['spine_mm']
 for col,concept in enumerate(['A','B']):
  ax=axes[row,col];ax.add_patch(Rectangle((-w/2,-1),w,1,fc='#669a65',ec='black',lw=.6))
  y=0
  for key,color in [('interface',colors['glue']),('insulation','#ddc94b'),('graphite',colors['graphite']),('top_skin',colors['carbon'])]:
   ax.add_patch(Rectangle((-w/2,y),w,s[key],fc=color,ec='none'));y+=s[key]
  if concept=='A':ax.add_patch(Rectangle((-bw/2,y),bw,s['core'],fc=colors['foam'],ec=colors['carbon'],lw=.7))
  else:
   for sign in [-1,1]:
    x=sign*(bw/2-s['B_web']/2)
    ax.add_patch(Rectangle((x-s['B_web']/2,y),s['B_web'],s['core'],fc=colors['carbon']))
    x=sign*f['tube_offset_mm'];saddle_w=(c['B_foam_fraction']*(bw*s['core']-2*3.141592653589793*f['tube_OD_mm']**2/4)+2*3.141592653589793*f['tube_OD_mm']**2/4)/(2*s['core'])
    ax.add_patch(Rectangle((x-saddle_w/2,y),saddle_w,s['core'],fc=colors['foam'],ec='none'))
  for sign,color in [(-1,'#1e8ac3'),(1,'#cf5148')]:
   centre=(sign*f['tube_offset_mm'],y+s['core']/2)
   ax.add_patch(Circle(centre,f['tube_OD_mm']/2,fc=colors['tube'],ec='black',lw=.6))
   ax.add_patch(Circle(centre,(f['tube_OD_mm']-2*f['tube_wall_mm'])/2,fc=color,ec='none'))
  y+=s['core'];ax.add_patch(Rectangle((-bw/2,y),bw,s['bottom_skin'],fc=colors['carbon']));y+=s['bottom_skin']
  ax.annotate('',(-bw/2,5.5),(bw/2,5.5),arrowprops={'arrowstyle':'<->','color':'black','lw':.7});ax.text(0,5.65,f'{bw:g} mm spine',ha='center',va='top')
  ax.text(0,-2.0,f'Module body: {w:g} mm; unchanged placement',ha='center',va='bottom')
  ax.set_title(f'{concept}: '+('foam sandwich' if concept=='A' else 'hollow ribbed stave')+f' — {typ}')
  ax.set_xlim(-w/2-3,w/2+3);ax.set_ylim(9,-4);ax.set_aspect('equal');ax.set_xlabel('tangential coordinate [mm]');ax.set_ylabel('depth behind module [mm]')
  ax.text(.02,.03,f'Two Ti tubes: OD {f["tube_OD_mm"]:g}, wall {f["tube_wall_mm"]:g} mm',transform=ax.transAxes,fontsize=8)
fig.suptitle('DES-002 | Dimensioned pixel-stave concepts | PROTOTYPE',fontsize=15)
fig.supxlabel('Both: 0.10 interface + 0.025 insulation + 0.20 graphite + 0.15 CFRP + 4.10 core + 0.15 CFRP = 4.725 mm.\nCFRP dark grey; graphite grey; foam tan; coolant blue/red. B saddles schematic; volume allowance 30% of A. Manufacturing tolerances unqualified.',fontsize=9)
for ext in ['png','pdf','svg']:fig.savefig(out/f'cross-sections.{ext}',dpi=180)
plt.close(fig)
fig,axes=plt.subplots(3,1,figsize=(12,8),layout='constrained',gridspec_kw={'height_ratios':[1.4,1,1.2]})
ax=axes[0]
for z in c['bearing_z_mm']:ax.axvspan(z-4,z+4,color='#566574',alpha=.35)
for z in range(-550,540,23):ax.add_patch(Rectangle((z,1),21,.3,fc='#669a65',ec='white',lw=.5))
ax.plot([-552,553],[.6,.6],color='#444e59',lw=3)
for y,cs,direction in [(.3,'#1e8ac3',1),(0,'#cf5148',-1)]:
 ax.plot([-552,553],[y,y],color=cs,lw=2)
 ax.annotate('',(300*direction,y),(-300*direction,y),arrowprops={'arrowstyle':'->','color':cs,'lw':2})
ax.text(-585,.3,'feed A',ha='right',color='#1e8ac3');ax.text(585,.3,'return A',color='#1e8ac3')
ax.text(-585,0,'return B',ha='right',color='#cf5148');ax.text(585,0,'feed B',color='#cf5148')
ax.set_xlim(-740,740);ax.set_ylim(-.5,2);ax.set_yticks([]);ax.set_xlabel('z [mm]; transverse separation enlarged for legibility')
ax.set_title('Two straight independent CO₂ circuits per stave, flowing in opposite directions — no central U-bend')
ax.text(0,1.65,'Unchanged active module rows; six bearing planes, 224 mm between planes',ha='center')
ax=axes[1];ax.axis('off')
ax.text(.02,.90,'Mounting and load path',fontweight='bold',fontsize=12)
ax.text(.02,.65,'One axial locator; remaining bearings slide or flex axially during cooldown. Ribs support radial/tangential loads.\nFour intermediate shared CFRP rib planes plus end flanges; rib positions are a proposal, not installed geometry.\nHardpoints, stagger-height brackets and the global support-shell connection require CAD/FEA and material scans.',va='top')
ax=axes[2];ax.set_xlim(530,625);ax.set_ylim(0,3);ax.set_yticks([])
ax.axvspan(530,552.8,color='#669a65',alpha=.35);ax.axvspan(552.8,607,color='#e9c990',alpha=.45);ax.axvspan(607,616,color='#888888',alpha=.3)
ax.axvline(611.7,ls='--',color='black');ax.text(612,2.7,'First pixel disc centre\n611.7 mm',ha='left',va='top')
ax.text(540,2,'Barrel\nmodules',ha='center');ax.text(577,2.45,'Existing larger service pocket\njoint + bend + strain relief: to qualify',ha='center')
ax.plot([550,566,570,598],[.5,.5,1.15,1.15],color='#1e8ac3',lw=2)
ax.plot([550,562,569,598],[.25,.25,.85,.85],color='#cf5148',lw=2)
ax.text(579,.2,'Transition to reserved 4 mm OD transport lines',ha='center',fontsize=8)
ax.set_xlabel('z [mm]; end routing schematic — disc band illustrative, see retained geometry for exact bodies')
fig.suptitle('DES-002 | Support spacing and service handoff | PROTOTYPE',fontsize=15)
for ext in ['png','pdf','svg']:fig.savefig(out/f'longitudinal-routing.{ext}',dpi=180)
