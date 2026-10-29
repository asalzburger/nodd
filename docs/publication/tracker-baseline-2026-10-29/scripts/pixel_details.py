"""Detailed sensor and service drawings; all geometry is from bundled inputs.
Dotted lines are explicitly conceptual interconnections, never manufactured routes.
"""
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon,Circle,Wedge,Arc
from matplotlib.lines import Line2D

def render(D,ROOT):
 B='#174382';C='#0479C1';O='#ba6928';G='#65717d';L='#dae2ea';K='#7ca084';V='#934c67'
 def box(ax,x,y,w,h,c,**kw):ax.add_patch(Rectangle((x,y),w,h,facecolor=c,edgecolor=kw.pop('edgecolor',c),linewidth=kw.pop('lw',.5),**kw))
 def save(fig,name):fig.savefig(ROOT/'figures'/f'{name}.pdf',bbox_inches='tight',pad_inches=.06,metadata={'Creator':'nODD PubDoc pixel_details.py','CreationDate':None,'ModDate':None});plt.close(fig)
 def arrow(ax,a,b,c=G,style='-'):ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':c,'lw':1,'linestyle':style})
 def polygon(b):return [[b['center_mm'][j]+s*b['u'][j]*b['half_u_mm']+t*b['v'][j]*b['half_v_mm'] for j in range(2)] for s,t in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 # Physical stack: micrometre vertical scale; exact implementation ordering.
 m=D['module'];fig,ax=plt.subplots(figsize=(6.1,3.6));s=D['barrels'][2]['shape'];w=s['sensor_phi']
 layers=[];z=-m['sensor_mm']/2
 for key,title,color in [('epoxy_mm','Flex-to-sensor epoxy',V),('flex_copper_layer_mm','Inner patterned copper',O),('flex_polyimide_mm','Polyimide films (combined)', '#dcc781'),('flex_copper_layer_mm','Outer patterned copper',O)]:
  t=m[key];layers.append((z-t,z,title,t,color));z-=t
 layers.append((-m['sensor_mm']/2,m['sensor_mm']/2,'Planar silicon sensor',m['sensor_mm'],B))
 for lo,hi,title,t,color in layers:box(ax,-w/2,lo*1000,w,(hi-lo)*1000,color)
 back=m['sensor_mm']/2+m['bump_standoff_mm']+m['asic_mm']
 for u in [-10.6,10.6]:
  box(ax,u-10.5,(m['sensor_mm']/2+m['bump_standoff_mm'])*1000,21,m['asic_mm']*1000,G,edgecolor='white',lw=.7)
  box(ax,u-10.5,back*1000,21,(.5-back)*1000,K,edgecolor='white',lw=.7)
 box(ax,-22.1,-500,44.2,1000,'none',edgecolor=G,lw=.6,linestyle='--')
 # Leaders at independent label y to keep thin films legible.
 names=[('Outer Cu: 18 µm',-177,-350),('Polyimide: 50 µm',-143,-280),('Inner Cu: 18 µm',-109,-210),('Epoxy: 25 µm',-87.5,-140),('Sensor: 150 µm',0,-35),('Bump standoff: 20 µm',85,65),('ASIC silicon: 150 µm',170,170),('Graphite contact: 255 µm',372.5,370)]
 for txt,yy,ty in names:
  ax.plot([20 if yy<80 else 21,25,26],[yy,ty,ty],c=G,lw=.55)
  ax.text(27,ty,txt,va='center',fontsize=8)
 arrow(ax,(-26,-55),(-26,450),C);ax.text(-28,180,'heat to local support',rotation=90,ha='center',va='center',fontsize=8,c=C)
 ax.text(0,-430,'sensor-backside flex',ha='center',fontsize=8);ax.text(0,560,'local support begins at w = +500 µm',ha='center',fontsize=8)
 ax.set(xlim=(-32,66),ylim=(600,-540),xlabel='u [mm] — quad section; axes have independent scales',ylabel='w [µm]');ax.set_xticks([-20,0,20]);save(fig,'pixel-module-stack')
 # Guard/seam close-up and electronic pixel pitch: dimensions exact, implant artwork absent.
 fig,aa=plt.subplots(1,2,figsize=(6.1,3.2));ax=aa[0]
 box(ax,-19.8,-20.3,39.6,40.6,L,edgecolor=G)
 for u,v,hu,hv in s['patches']:box(ax,u-hu,v-hv,2*hu,2*hv,B)
 ax.set(aspect='equal',xlim=(-22,22),ylim=(-23,23),xlabel='tangential u [mm]',ylabel='longitudinal v [mm]',title='One sensor, four readout regions')
 for x,y,txt in [(9.7,10.1,'384 × 400'),(-9.7,-10.1,'384 × 400')]:ax.text(x,y,txt,color='white',fontsize=6.8,ha='center')
 ax=aa[1];ax.set(aspect='equal',xlim=(-.03,.23),ylim=(-.03,.23),title='Readout grid detail (schematic)',xlabel='local coordinate [mm]',ylabel='local coordinate [mm]')
 pitch=m['pixel_pitch_mm']
 for i in range(5):ax.plot([i*pitch,i*pitch],[0,.2],c=B,lw=.65);ax.plot([0,.2],[i*pitch,i*pitch],c=B,lw=.65)
 ax.annotate('',xy=(.1,.215),xytext=(.05,.215),arrowprops={'arrowstyle':'<->','color':O});ax.text(.075,.227,'50 µm',ha='center',fontsize=7,c=O)
 ax.scatter([.025,.075,.125,.175],[.025]*4,s=8,c=O);ax.text(.10,-.02,'channel centres; no implant mask implied',ha='center',fontsize=6)
 fig.tight_layout();save(fig,'pixel-sensor-detail')
 # Exact B1 reference bundle growth and physical ring overflight.
 fig,aa=plt.subplots(2,1,figsize=(6.1,4.0),gridspec_kw={'height_ratios':[1.5,1]});ax=aa[0];bar=D['barrels'][0];body=bar['columns'][0];r=sum(body['center_mm'][i]*body['n'][i] for i in range(2));rings=D['rings']['layers'][0];z0,z1=D['support']['passive_stave_z_mm'][bar['layer']['id']]
 box(ax,z0,r+.5,z1-z0,4.725,K,alpha=.35)
 for b in bar['rows']:box(ax,b['center_mm'][2]-b['half_v_mm'],r-.5,2*b['half_v_mm'],1,B)
 for zz in D['mounting']['bearing_z_mm']:
  box(ax,zz-4,rings['ring_inner_radius_mm'],8,1,G)
  box(ax,zz-4,r+5.225,8,rings['ring_inner_radius_mm']-r-5.225,G,alpha=.3)
 for q in D['routing']['longitudinal']:
  if q['layer_id']!=bar['layer']['id']:continue
  a,b=q['abs_z_min_mm'],q['abs_z_max_mm'];a,b=(-b,-a) if q['side']=='negative' else (a,b)
  box(ax,a,q['r_min_mm'],b-a,q['r_max_mm']-q['r_min_mm'],O,alpha=.45)
  if q['counts']['modules'] in [1,10,17,26,27]:ax.plot([a if a>=0 else b]*2,[r+.5,q['r_min_mm']],c=O,lw=.5,ls=':')
 # Two tubes shown as separate conceptual tracks since a single radial slice would overlay them.
 for yy,start,end in [(r+2,z0,z1),(r+3.7,z1,z0)]:ax.plot([z0,z1],[yy,yy],c=C,lw=.9);arrow(ax,(start*.8,yy),(end*.8,yy),C)
 for a,b in [(-605,-555),(555,605)]:box(ax,a,27,b-a,34,V,alpha=.10)
 ax.set(xlim=(-610,610),ylim=(27,61),ylabel='r [mm]',title='B1 column 0: module, support, rings and cable envelope');ax.text(0,58,'cable flow to each end',ha='center',fontsize=7,c=O);ax.axvline(0,c=G,lw=.5,ls='--')
 ax=aa[1]
 for name,color in [('A-pixel-B1',O),('A-pixel-B3',B)]:
  qs=sorted([q for q in D['routing']['longitudinal'] if q['layer_id']==name and q['side']=='positive'],key=lambda q:q['abs_z_min_mm'])
  xx=[q['abs_z_min_mm'] for q in qs]+[qs[-1]['abs_z_max_mm']]; yy=[sum(q['footprint_mm2'].values()) for q in qs];ax.step(xx,yy+[yy[-1]],where='post',c=color,label=name[-2:]+' positive half-stave')
 ax.set(xlim=(0,555),ylim=(0,140),xlabel='z [mm]',ylabel='cable footprint [mm²]');ax.legend(fontsize=7,loc='lower right');ax.grid(alpha=.15);fig.tight_layout();save(fig,'pixel-barrel-routing')
 # Twelve-sector collection with selected counts and r-z handoff geometrical schematic.
 fig,aa=plt.subplots(1,2,figsize=(6.1,3.3));ax=aa[0]
 sectors=[x for x in D['service_summary']['sectors'] if x['side']=='positive']
 for q in sectors:
  phi=q['sector']*30;ax.add_patch(Wedge((0,0),234,phi-11.25,phi+11.25,width=44,facecolor=O,alpha=.3,edgecolor=O,lw=.4));t=math.radians(phi);ax.text(263*math.cos(t),263*math.sin(t),str(q['staves']),ha='center',va='center',fontsize=7)
 for layer in D['barrels']:
  for b in layer['columns']:
   t=math.atan2(b['center_mm'][1],b['center_mm'][0]);sec=round(t/(math.pi/6));dest=sec*math.pi/6;rad=math.hypot(*b['center_mm'][:2]);ax.plot([rad*math.cos(t),212*math.cos(dest)],[rad*math.sin(t),212*math.sin(dest)],c=G,lw=.3,alpha=.6);ax.plot(rad*math.cos(t),rad*math.sin(t),'.',ms=2,c=B)
 ax.set(aspect='equal',xlim=(-290,290),ylim=(-290,290),xlabel='x [mm]',ylabel='y [mm]',title='Twelve end sectors; counts are staves')
 ax=aa[1]
 for rr in D['rings']['layers']:ax.plot([520,552.8],[rr['nominal_radius_mm']]*2,c=B,lw=2)
 box(ax,555,27,50,207,V,alpha=.12);box(ax,580,192,25,40,O,alpha=.35)
 for rr in [x['segments'][i]['r_min_mm'] for x in D['routing']['radial'] for i in range(len(x['segments']))]:
  ax.plot([550,580,580,605],[rr,rr,212,212],c=O,lw=.8,ls=':')
 arrow(ax,(580,160),(580,210),O);arrow(ax,(582,212),(610,212),O)
 ax.set(xlim=(520,620),ylim=(20,260),xlabel='|z| [mm]',ylabel='r [mm]',title='One sector: radial collection → trunk');ax.text(577,248,'50 mm bay',ha='center',fontsize=7);ax.text(599,185,'handoff\nr = 212 mm',ha='center',fontsize=7)
 fig.tight_layout();save(fig,'pixel-sector-handoff')
