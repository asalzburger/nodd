"""Sensitive-face diagnosis plot from actual prototype placement coordinates."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'tools/calorimeter_hardware'))
from assembly import inventory
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle
r,_=inventory();fig,axes=plt.subplots(1,2,figsize=(10,8),layout='constrained')
for ax,kind in zip(axes,('ecal','hcal')):
 reg=next(q for q in r['regions'] if q['name']==kind+'_endcap');u=next(u for u in r['units'] if u['name']==kind)
 plate=next(p for p in reg['parts'] if p['role']=='absorber');ax.add_patch(Polygon([[y/1000,x/1000] for x,y in plate['vertices_mm']],facecolor='#f0dcb5',edgecolor='#555',lw=1))
 for p in reg['placements']:
  if p['layer']!=0:continue
  x,y,z=p['center_mm'];w,h=u['width_mm'],u['height_mm'];ax.add_patch(Rectangle(((y-w/2)/1000,(x-h/2)/1000),w/1000,h/1000,facecolor='#c5d0d7',edgecolor='#777',lw=.7))
  for s in u['parts']:
   if s['role']!='sensitive':continue
   # Endcap local x maps to -global y, local y to global x.
   sx,sy,_=s['center_mm'];sw,sh=s['dimensions_mm']['sx'],s['dimensions_mm']['sy']
   ax.add_patch(Rectangle(((y-sx-sw/2)/1000,(x+sy-sh/2)/1000),sw/1000,sh/1000,facecolor='#32885b',edgecolor='white',lw=.15))
 first=min(p['center_mm'][0]+s['center_mm'][1]-s['dimensions_mm']['sy']/2 for p in reg['placements'] if p['layer']==0 for s in u['parts'] if s['role']=='sensitive')
 ax.axhline(first/1000,c='#aa3333',ls='--',lw=1);ax.text(.02,.96,f'First active radius: {first/1000:.3f} m\nNominal aperture: 0.300 m',transform=ax.transAxes,va='top',fontsize=10,bbox=dict(facecolor='white',alpha=.85,edgecolor='none'))
 ax.set(xlim=(-reg['outer_apothem_mm']*.22/1000,reg['outer_apothem_mm']*.22/1000),ylim=(.25,reg['outer_apothem_mm']/1000+.06),xlabel='tangent [m]',ylabel='radial [m]',title=kind.upper()+f" · {reg['coverage'][0]['active_fraction']*100:.1f}% active plate area");ax.set_aspect('equal')
fig.suptitle('Current endcap packing · one sector, one layer\nBeige: uncovered absorber · grey: cassette footprint · green: sensitive material',fontsize=12)
out=Path('docs/design/figures/DES-029');plt.rcParams['svg.hashsalt']='endcap-review';fig.savefig(out/'endcap-coverage-review.png',dpi=170);fig.savefig(out/'endcap-coverage-review.svg',metadata={'Date':None});p=out/'endcap-coverage-review.svg';p.write_text('\n'.join(s.rstrip() for s in p.read_text().splitlines())+'\n')
