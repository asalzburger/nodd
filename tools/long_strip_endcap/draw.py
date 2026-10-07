"""Inventory-driven TDR figures; dimensions are simulation fixtures, not CAD."""
import argparse,json,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Circle,Rectangle,Wedge
import numpy as np
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'DES023','axes.spines.top':False,'axes.spines.right':False})
def save(fig,p):
 fig.savefig(p.with_suffix('.svg'),metadata={'Date':None});fig.savefig(p.with_suffix('.png'),dpi=180);plt.close(fig)
 q=p.with_suffix('.svg');q.write_text('\n'.join(s.rstrip() for s in q.read_text().splitlines())+'\n')
def run(expected,out):
 d=json.loads(expected.read_text());l=d['layout'];out.mkdir(parents=True,exist_ok=True)
 fig,a=plt.subplots(1,2,figsize=(13,6.5),gridspec_kw={'width_ratios':[1,1.1]})
 ax=a[0]
 for i in range(12):ax.add_patch(Wedge((0,0),1130,i*30+.115,(i+1)*30-.115,width=346,facecolor='#c7b58a',edgecolor='#aaa',alpha=.4))
 for m in l['modules']:
  if m['layer'] or m['face']:continue
  o=np.array(m['center_mm'][:2]);u=np.array(m['u'][:2]);v=np.array(m['v'][:2]);corners=[o+x*48*u+y*48*v for x,y in ((-1,-1),(1,-1),(1,1),(-1,1))]
  ax.add_patch(Polygon(corners,facecolor='#32699b',edgecolor='white',lw=.25,alpha=.7))
 for r,col in ((783,'#b44'),(1140,'#555'),(1169,'#d59145')):ax.add_patch(Circle((0,0),r,fill=False,ec=col,lw=1,ls='--'))
 ax.set(aspect='equal',xlim=(-1220,1220),ylim=(-1220,1220),xlabel='x [mm]',ylabel='y [mm]',title='Long-strip endcap · 312 stereo pairs/disc')
 ax.text(0,0,'4 rings\n12 continuous petals\n6 discs per end',ha='center',va='center')
 ax=a[1];p=l['petals'][0];phi=p['phi_rad'];f=np.array([[math.sin(phi),-math.cos(phi)],[-math.cos(phi),-math.sin(phi)]]);origin=np.array([0,0])
 def uv(pos):return f@np.array(pos[:2])
 for e in d['entities']:
  if not e['name'].startswith('L0_P0_'):continue
  role=e['role'];pos=uv(e['center_mm']);kind=e['shape_kind'];dim=e['dimensions_mm']
  if role=='core':
   theta=np.linspace(-math.pi/12+.002,math.pi/12-.002,120);outer=np.column_stack((1130*np.sin(theta),-1130*np.cos(theta)));inner=np.column_stack((784*np.sin(theta[::-1]),-784*np.cos(theta[::-1])));ax.add_patch(Polygon(np.vstack((outer,inner)),fc='#c7b58a',alpha=.5))
  elif role in ('integral_web','sensitive','electronics') and kind=='box':
   if role in ('sensitive','electronics') and e['center_mm'][2]>1470:continue
   frame=np.array(e['frame']);u=f@frame[0,:2];v=f@frame[1,:2];corners=[pos+x*dim['sx']/2*u+y*dim['sy']/2*v for x,y in ((-1,-1),(1,-1),(1,1),(-1,1))];ax.add_patch(Polygon(corners,fc={'integral_web':'#555','sensitive':'#32699b','electronics':'#9462a4'}[role],alpha=.65,ec='white',lw=.3))
  elif role=='cooling_tube':ax.plot([pos[0],pos[0]],[pos[1]-dim['length']/2,pos[1]+dim['length']/2],color='#47a9ba',lw=2)
  elif role=='mount' and '_pin' in e['name']:ax.scatter(*pos,s=70,color='#bc3b46',zorder=10)
 ax.plot([-282,282],[-1116.5,-1116.5],color='#c98131',lw=2,label='outer collection bus (schematic)');ax.set(aspect='equal',xlim=(-305,305),ylim=(-1160,-750),xlabel='petal tangential coordinate [mm]',ylabel='negative radial coordinate [mm]',title='One petal · integral webs / 6 U circuits / 3 contacts')
 ax.text(0,-767,'Inner key: 0.5 mm short-service clearance',ha='center',fontsize=9);ax.text(0,-1150,'2 outer kinematic contacts · outer EoS boards',ha='center',fontsize=9)
 fig.suptitle('DES-023 PROTOTYPE · one sensor face shown · mounts and services unqualified',fontsize=12);fig.tight_layout();save(fig,out/'DES-023-petals')
 fig,ax=plt.subplots(3,1,figsize=(12,9),gridspec_kw={'height_ratios':[1,1.3,1]})
 a=ax[0];a.add_patch(Rectangle((-70,-2.5),140,5,fc='#c7b58a'))
 for w in (-2.75,2.75):a.add_patch(Rectangle((-70,w-.15),140,.3,fc='#555'))
 for u in (-30,-10,10,30):a.add_patch(Circle((u,0),1.25,fc='#999'));a.add_patch(Circle((u,0),1.11,fc='#47a9ba'))
 for i,lift in enumerate((0,1.5,3,4.5)):
  u=-45+30*i
  for sign in (-1,1):a.plot([u-12,u+12],[sign*(3.45+lift)]*2,lw=3,color='#32699b');a.add_patch(Rectangle((u-5,min(sign*2.9,sign*(3+lift))),10,.1+lift,fc='#777'))
 a.set(xlim=(-80,80),ylim=(-11,11),xlabel='illustrative local width [mm]',ylabel='normal [mm]',title='Shared 5 mm core + 0.3 mm skins · 4 outward elevations (shown side by side)');a.text(0,9.8,'Same-pair face separations 6.9 / 9.9 / 12.9 / 15.9 mm',ha='center',fontsize=9)
 a=ax[1]
 for z in (1470,1633.208484,1949.635166,2309.997868,2702.228888,3120):
  a.plot([z,z],[786.46,1108.33],color='#32699b',lw=3);a.add_patch(Rectangle((z+20,1100),110,69,fc='#d59145',alpha=.35))
 a.add_patch(Rectangle((1435,1144),2065,25,fc='#d59145',alpha=.35));a.add_patch(Rectangle((1325,800),110,369,fc='#d59145',alpha=.15));a.plot([1403.65,1403.65],[786.46,1108.33],color='#b44',ls='--',label='old first datum');a.set(xlim=(1280,3550),ylim=(770,1200),xlabel='|z| [mm]',ylabel='r [mm]',title='Routing: core buses / EoS → R50 cable + R25 pipe fan → shared cumulative trunk');a.legend(fontsize=9,loc='lower right')
 a=ax[2];cases=[x for x in d['engineering']['normal_load'] if x['E_GPa']==70];a.bar(['installed axial fixture 0.25g','horizontal handling 1g'],[x['total_with_joint_mm']*1000 for x in cases],color=['#397','#b44'],width=.5);a.axhline(50,color='#555',ls='--',label='50 µm including 10 µm joint allocation');a.set(ylabel='normal displacement screen [µm]',title='Beam proxy with no web/Si stiffness credit · 3-contact plate and joint FEA still required');a.legend(fontsize=9);fig.tight_layout();save(fig,out/'DES-023-structure-routes')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--expected',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.expected,a.output)
