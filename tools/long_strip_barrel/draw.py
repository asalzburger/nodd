"""TDR-style geometry/load figures from the exported prototype inventory."""
import argparse,json,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle,Arc,Polygon
import numpy as np
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'DES022','axes.spines.top':False,'axes.spines.right':False})
def save(fig,p):
 fig.savefig(p.with_suffix('.svg'),metadata={'Date':None});fig.savefig(p.with_suffix('.png'),dpi=180);plt.close(fig)
 # Matplotlib whitespace only; scientific data untouched.
 q=p.with_suffix('.svg');q.write_text('\n'.join(line.rstrip() for line in q.read_text().splitlines())+'\n')
def run(expected,out):
 d=json.loads(expected.read_text());l=d['layout'];b=d['engineering']['beam'];out.mkdir(parents=True,exist_ok=True)
 fig,ax=plt.subplots(3,1,figsize=(13,10),gridspec_kw={'height_ratios':[1.5,1,1]})
 a=ax[0]
 for m in l['modules'][:72]:
  sign=2*m['face']-1;z=m['center_mm'][2];w=sign*l['pairs'][m['module_id']]['separation_mm']/2
  a.add_patch(Rectangle((z-48,w-.15),96,.3,color='#32699b',alpha=.65))
 a.add_patch(Rectangle((-1320,-2.5),2640,5,color='#c7b58a',label='load-bearing core'))
 for w in (-2.7,2.7):a.plot([-1320,1320],[w,w],color='#444',lw=1.5)
 for z in b['recommended']['anchors_z_mm']:a.plot([z,z],[-12,-3.2],color='#8264a8',lw=2);a.scatter(z,-12,s=20,color='#8264a8')
 a.set(xlim=(-1450,1450),ylim=(-17,12),xlabel='z [mm]',ylabel='local normal [mm]',title='Long-strip barrel — continuous sandwich IS the stave (PROTOTYPE)')
 a.text(0,9,f"36 stereo pairs/stave · {l['row_pitch_mm']:.2f} mm pitch · {b['recommended']['count']} bearing stations",ha='center')
 a.text(0,-16,'Central station fixes z; other keyed mounts slide along z. Vertical scale expanded.',ha='center',fontsize=9)
 a=ax[1]
 for w,t,color,label in ((0,5,'#c7b58a','carbon foam'),(2.7,.2,'#555','CFRP'),(-2.7,.2,'#555','CFRP')):a.add_patch(Rectangle((-62,w-t/2),124,t,color=color))
 for u in (-30,-10,10,30):a.add_patch(Circle((u,0),1.25,color='#999'));a.add_patch(Circle((u,0),1.11,color='#62b5cf'))
 for sign in (-1,1):
  for lift,xshift,label in ((0,-25,'low'),(1.5,25,'high')):
   w=sign*(3.35+lift);a.plot([xshift-22,xshift+22],[w,w],color='#32699b',lw=3)
   a.add_patch(Rectangle((xshift-10,min(sign*2.8,sign*(2.9+lift))),20,.1+lift,color='#777',alpha=.8))
 a.set(xlim=(-75,75),ylim=(-9,9),xlabel='u [mm]',ylabel='normal [mm]',title='Transverse sandwich detail — low/high rows shown side by side for clarity')
 a.text(0,7.2,'Two independent 1D strip faces · relative stereo 40 mrad · gaps 6.7 / 9.7 mm',ha='center',fontsize=9)
 a=ax[2]
 for r in (840,1060):a.plot([0,1320],[r,r],color='#b49c6b',lw=4)
 a.add_patch(Rectangle((1325,800),110,369,facecolor='#d59145',alpha=.15))
 a.add_patch(Rectangle((1435,1144),650,25,facecolor='#d59145',alpha=.5))
 for r in (840,1060):a.plot([1305,1340,1380,1435,2085],[r,r,1156.5,1156.5,1156.5],color='#d59145',lw=2)
 a.plot([1470,1470],[786,1108],color='#32699b',ls='--')
 a.set(xlim=(1100,2100),ylim=(780,1190),xlabel='positive z [mm] (negative end mirrored)',ylabel='r [mm]',title='End collection, bend reservation and fixed 25 mm service corridor')
 a.text(1560,1090,'First long-strip disc must move\nto clear the collector (DES-023)',fontsize=9)
 fig.tight_layout();save(fig,out/'DES-022-stave')
 fig,a=plt.subplots(figsize=(9,5))
 scan=b['scan'];a.plot([s['count'] for s in scan],[s['total_mm']*1000 for s in scan],'-o',color='#32699b',ms=3,label='E70 GPa / G5 MPa / 2× gravity')
 a.axhline(40,color='#a33',ls='--',label='40 µm gravity allocation (+10 µm joints)');a.axvline(b['minimum']['count'],color='#777',ls=':',label=f"minimum {b['minimum']['count']}");a.axvline(b['recommended']['count'],color='#397',ls=':',label=f"recommend {b['recommended']['count']}")
 a.set(xlim=(5,25),ylim=(0,200),xlabel='support stations per stave',ylabel='bounded static deflection [µm]',title=f"Full stave load {b['load']['total_mass_g']/1000:.3f} kg — bending + core shear")
 a.legend(fontsize=9);a.text(.98,.94,'PROTOTYPE · moduli, joints and torsion unqualified',transform=a.transAxes,ha='right',va='top',fontsize=9);fig.tight_layout();save(fig,out/'DES-022-anchors')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--expected',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.expected,a.output)
