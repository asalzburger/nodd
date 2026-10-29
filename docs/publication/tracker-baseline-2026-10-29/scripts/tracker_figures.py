#!/usr/bin/env python3
"""Self-contained tracker review drawings from hashed report snapshots.

No nODD checkout, native runtime, network or TeX shell escape is required.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/nodd-tracker-tdr-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, Rectangle, Circle, Wedge, Patch
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--balanced', action='store_true', help='Refresh only current pixel-dependent overall views; preserve strip assets.')
args=parser.parse_args()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((ROOT/'data/tracker-provenance.json').read_text())
assert sha(ROOT/'data/tracker-baseline.json')==manifest['snapshot_sha256']
D=json.loads((ROOT/'data/tracker-baseline.json').read_text())
P=json.loads((ROOT/'data/pixel-layout.json').read_text())
PE=json.loads((ROOT/'data/pixel-endcap-baseline.json').read_text())
for f,m in [('pixel-layout.json','pixel-provenance.json'),('pixel-endcap-baseline.json','pixel-endcap-provenance.json')]:
    assert sha(ROOT/'data'/f)==json.loads((ROOT/'data'/m).read_text())['snapshot_sha256']
if args.balanced:
    current=json.loads((ROOT/'data/balanced-baseline.json').read_text())
    P=current['pixel']; PE=current['endcap']
BLUE='#174382'; TEAL='#168586'; PURPLE='#835c93'; GOLD='#ba6928'; GREY='#65717d'; GREEN='#91aa8e'; LIGHT='#e4e9e2'; RED='#aa4658'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.titlesize':9,'axes.labelsize':8,
    'xtick.labelsize':7,'ytick.labelsize':7,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
artifacts=[]
def save(fig,name):
    p=ROOT/'figures'/(name+'.pdf')
    fig.savefig(p,bbox_inches='tight',pad_inches=.04,metadata={'CreationDate':None,'ModDate':None,'Creator':'nODD tracker_figures.py'})
    plt.close(fig);artifacts.append(p)
def rect(ax,x,y,w,h,col,**kw):ax.add_patch(Rectangle((x,y),w,h,facecolor=col,edgecolor=kw.pop('ec',col),lw=kw.pop('lw',.5),**kw))
def corners(m):
    p=np.array(m['center_mm'][:2]);u=np.array(m['u'][:2]);v=np.array(m['v'][:2])
    return np.array([p+a*m['half_u_mm']*u+b*m['half_v_mm']*v for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]])
def note(ax,s):
    # Scope explanations belong in the manuscript captions, keeping data clear.
    pass

# The nominal support datums are shown; finite sensor depth is documented in the text.
fig,ax=plt.subplots(figsize=(7.0,3.5))
for b in P['barrels']:
    ax.plot([-550,550],[1000*b['layer']['r_m']]*2,color=BLUE,lw=1.5)
for b in D['short_barrel']['layers']:ax.plot([-1200,1200],[b['nominal_radius_mm']]*2,color=TEAL,lw=2)
for r in D['long_barrel']['input']['radii_mm']:ax.plot([-1287.333333333,1287.333333333],[r]*2,color=PURPLE,lw=2.3)
for q in PE['discs']:ax.plot([q['z_mm']]*2,q['active_radial_span_mm'],color=BLUE,lw=1.7)
for key,col in [('short_endcap',TEAL),('long_endcap',PURPLE)]:
    c=D[key]['input']
    for z in c['disc_z_mm']:ax.plot([z,z],c['annulus_mm'],color=col,lw=2)
for eta in (1,2,3,4):
    z=np.linspace(0,3500,300);r=z/np.sinh(eta);a=r<1200
    ax.plot(z[a],r[a],color=GREY,lw=.65,ls='--')
    x=min(3370,1110*np.sinh(eta));ax.text(x,x/np.sinh(eta)+25,fr'$\eta={eta}$',fontsize=7,color=GREY)
rect(ax,-150,0,300,17,RED,alpha=.25)
ax.set(xlim=(-1450,3550),ylim=(0,1220),xlabel='z [mm]',ylabel='r [mm]')
ax.legend(handles=[Line2D([0],[0],color=c,lw=2,label=l) for c,l in [(BLUE,'Pixels'),(TEAL,'Short strips / strixels'),(PURPLE,'Long strips / stereo pairs')]],loc='lower center',bbox_to_anchor=(.5,1.02),ncol=3,fontsize=7)
note(ax,'Nominal layer/disc layout; negative discs follow the signed-end geometry.\nDashed rays: straight tracks from z = 0. Red: z₀ = ±150 mm hypothesis.')
fig.tight_layout();save(fig,'tracker-layout')

fig,ax=plt.subplots(figsize=(7.0,3.2))
for col,boxes in [(BLUE,[(555,27,50,207),(605,190,3136-605,44)]),
    (TEAL,[(1245,244,65,506),(1310,710,2190,73)]),
    (PURPLE,[(1325,800,110,369),(1435,1144,2065,25)])]:
    for x,y,w,h in boxes:rect(ax,x,y,w,h,col,alpha=.23)
for key,col in [('short_endcap',TEAL),('long_endcap',PURPLE)]:
    c=D[key]['input'];lo,hi,dz0,dz1=c['fan_mm']
    for z in c['disc_z_mm']:
        rect(ax,z+dz0,lo,dz1-dz0,hi-lo,col,alpha=.25)
        ax.plot([z,z],c['annulus_mm'],color=col,lw=1)
for q in PE['discs']:ax.plot([q['z_mm']]*2,q['active_radial_span_mm'],color=BLUE,lw=.9)
ax.text(3500,1158,'1144–1169',va='center',ha='right',fontsize=7)
ax.text(3500,748,'710–783',va='center',ha='right',fontsize=7)
ax.text(2990,212,'190–234',va='center',ha='right',fontsize=7)
ax.set(xlim=(450,3550),ylim=(0,1230),xlabel='|z| [mm]',ylabel='r [mm]')
ax.legend(handles=[Patch(fc=c,alpha=.25,label=l) for c,l in [(BLUE,'Pixel'),(TEAL,'Short-strip'),(PURPLE,'Long-strip')]],loc='upper right',ncols=3,fontsize=7)
note(ax,'Filled regions are fixed service reservations and disc fans, not occupied solid material.\nSeparate subsystem inventories do not demonstrate combined installation clearance.')
fig.tight_layout();save(fig,'tracker-services')

if args.balanced:
    print('Rendered balanced tracker layout/services; preserved all six strip figures/table.')
    raise SystemExit(0)

fig,aa=plt.subplots(1,2,figsize=(7.0,3.6),gridspec_kw={'width_ratios':[1,1]})
for m in D['short_barrel']['xy_modules']:
    p=np.array(m['center_mm'][:2]);u=np.array(m['u'][:2])
    aa[0].plot(*np.stack([p-24*u,p+24*u]).T,color=TEAL,lw=.7)
for L in D['short_barrel']['layers']:
    r=L['nominal_radius_mm'];aa[0].add_patch(Circle((0,0),r-18.5,fill=False,ec=GREY,lw=.6))
    aa[0].text(.65*r,.65*r,str(L['staves']),fontsize=7,bbox=dict(fc='white',ec='none',alpha=.9,pad=1))
aa[0].set(aspect='equal',xlim=(-720,720),ylim=(-720,720),xlabel='x [mm]',ylabel='y [mm]',title='44 / 56 / 80 / 108 staves')
ax=aa[1];c=D['short_barrel']['input'];alpha=math.radians(15)
def xybox(phi,u0,w0,du,dw,col,alpha_fill=1):
    er=np.array([math.cos(phi),math.sin(phi)]);ep=np.array([-math.sin(phi),math.cos(phi)])
    u=math.cos(alpha)*ep-math.sin(alpha)*er;n=math.cos(alpha)*er+math.sin(alpha)*ep;p=260*er
    ax.add_patch(Polygon([p+(u0+s*du/2)*u+(w0+t*dw/2)*n for s,t in [(-1,-1),(1,-1),(1,1),(-1,1)]],fc=col,ec=col,lw=.3,alpha=alpha_fill))
for i in range(-1,2):
    phi=i*2*math.pi/44
    xybox(phi,0,-4.05,52,5,LIGHT)
    for w in (-1.375,-6.725):xybox(phi,0,w,52,.15,GREY)
    for lift in (0,1.5):xybox(phi,0,lift,48,.2,TEAL,1 if lift==0 else .45)
    er=np.array([math.cos(phi),math.sin(phi)]);ep=np.array([-math.sin(phi),math.cos(phi)])
    u=math.cos(alpha)*ep-math.sin(alpha)*er;n=math.cos(alpha)*er+math.sin(alpha)*ep
    for offset in (-12,12):
        p=260*er+offset*u-4.05*n;ax.add_patch(Circle(p,1.25,fc=GREY));ax.add_patch(Circle(p,1.11,fc=BLUE))
    # Contact foot profile from the declared tangent-plane equation.
    p=260*er+14.5*u;theta=math.atan2(p[1],p[0]);erf=np.array([math.cos(theta),math.sin(theta)])
    nd=np.dot(n,erf);ud=np.dot(u,erf);inner=(243-np.dot(p,erf))/nd
    ax.add_patch(Polygon([p+x*u+w*n for x,w in [(-1,inner+ud/nd),(1,inner-ud/nd),(1,-6.8),(-1,-6.8)]],fc=PURPLE))
    xybox(phi,0,-7.05,24.5,.2,GOLD)
for r in (240,243):ax.add_patch(Circle((0,0),r,fill=False,ec=PURPLE,lw=.8))
ax.set(aspect='equal',xlim=(225,278),ylim=(-55,55),xlabel='x [mm]',ylabel='y [mm]',title='L0 cold-stack projection')
note(ax,'15° common tilt\nBoth row heights projected\nRing contact on bare skin land')
fig.tight_layout();save(fig,'short-strip-barrel')

fig,aa=plt.subplots(2,1,figsize=(7.0,3.3),gridspec_kw={'height_ratios':[1.6,1]})
ax=aa[0]
rect(ax,-26,-6.55,52,5,LIGHT)
for w in (-6.8,-1.45):rect(ax,-26,w,52,.15,GREY)
for x in (-12,12):ax.add_patch(Circle((x,-4.05),1.25,fc=GREY));ax.add_patch(Circle((x,-4.05),1.11,fc=BLUE))
for lift,style in [(0,'-'),(1.5,'--')]:
    ax.plot([-24,24],[lift,lift],color=TEAL,lw=2,ls=style)
for x in (-10,10):rect(ax,x-10,-1.3,20,.4,GREY,alpha=.45)
rect(ax,-12.25,-7.15,24.5,.35,GOLD)
ax.set(xlim=(-30,30),ylim=(-8,3),xlabel='u [mm]',ylabel='w [mm]')
ax.text(0,2.2,'48 × 96 mm² sensor; raised rows at w = 1.5 mm',ha='center',fontsize=7)
note(ax,'Core + skins form the stave. Pipes: OD 2.5 mm / wall 0.14 mm.\nLayer drawing omits thin module films; dimensions are given in the text.')
ax=aa[1];ax.plot([-1210,1210],[0,0],color=GREY,lw=4)
ax.scatter(c['bearing_z_mm'],[0]*9,color=PURPLE,s=25,zorder=3)
for sign in (-1,1):ax.plot([sign*16,sign*1210],[.35,.35],color=BLUE,lw=2);ax.plot([sign*1215,sign*1245],[.35,.35],color=GOLD,lw=4)
ax.set(xlim=(-1320,1320),ylim=(-.3,.8),yticks=[],xlabel='z [mm]')
ax.text(0,-.25,'Nine bearing stations; centre fixes z, other joints allow axial motion',ha='center',fontsize=7)
fig.tight_layout();save(fig,'short-strip-stave')

def disc_plan(ax,modules,lo,hi,color,limit):
    for m in modules:ax.add_patch(Polygon(corners(m),fc=color,ec='white',lw=.2,alpha=.6))
    for r in (lo,hi):ax.add_patch(Circle((0,0),r,fill=False,ec=GREY,lw=.6,ls='--'))
    ax.set(aspect='equal',xlim=(-limit,limit),ylim=(-limit,limit),xlabel='x [mm]',ylabel='y [mm]')
fig,aa=plt.subplots(1,2,figsize=(7.0,3.5))
se=D['short_endcap'];c=se['input'];disc_plan(aa[0],se['disc_modules'],*c['annulus_mm'],TEAL,730)
aa[0].set_title('360 strixels / disc · 12 petals')
ax=aa[1];ax.add_patch(Wedge((0,0),685,.08,29.92,width=449,fc=LIGHT,ec=GREY,lw=.6))
for m in se['disc_modules']:
    if m['petal']==0:ax.add_patch(Polygon(corners(m),fc=TEAL,ec='white',lw=.3,alpha=.35))
for q in se['cooling']:
    d=q['dims'];p=np.array(q['center'][:2])
    if q['kind']=='torus':
        t=np.linspace(d['start'],d['start']+d['angle'],80);pts=p+d['major']*np.stack([np.cos(t),np.sin(t)],axis=1)
    else:
        v=np.array([math.cos(q['rz']),math.sin(q['rz'])])*d['length']/2;pts=np.stack([p-v,p+v])
    ax.plot(*pts.T,color=BLUE,lw=1)
for phi,col in [(15,GOLD),(22,PURPLE)]:
    t=math.radians(phi);ax.plot(np.array([250,678])*math.cos(t),np.array([250,678])*math.sin(t),color=col,lw=2)
ax.set(aspect='equal',xlim=(205,725),ylim=(-15,385),xlabel='x [mm]',ylabel='y [mm]',title='30 strixels / petal · one loop')
note(ax,'Blue: embedded cooling\nGold: LV · purple: HV/data\nAll module heights projected')
fig.tight_layout();save(fig,'short-strip-endcap')

fig,aa=plt.subplots(1,2,figsize=(7.0,3.6))
cols={'core':LIGHT,'support':GREY,'sensitive':PURPLE,'guard':'#c5b5ce','pickup':GREY,'spreader':GREY,'module_glue':'#dcafa4','bus':GOLD,'electronics':GOLD,'flex':GOLD,'cooling_tube':GREY,'coolant':BLUE,'bearing_ring':TEAL,'mount':TEAL}
for ax in aa:
    for q in D['long_barrel']['xy_sections']:
        col=cols[q['role']]
        if q['kind']=='polygon':ax.add_patch(Polygon(q['data'],fc=col,ec='none'))
        else:
            p,ri,ro=q['data'];ax.add_patch(Wedge(p,ro,0,360,width=ro-ri,fc=col,ec='none'))
aa[0].set(aspect='equal',xlim=(-1150,1150),ylim=(-1150,1150),xlabel='x [mm]',ylabel='y [mm]',title='86 / 108 structural staves')
aa[1].set(aspect='equal',xlim=(785,883),ylim=(-85,85),xlabel='x [mm]',ylabel='y [mm]',title='L0 at bearing z = 166.50 mm')
note(aa[1],'Purple: true sensor sections\nTeal: ring / potted mount\nGrey: skins / embedded Ti pipes\nGold: insulated buses on opposite edge')
fig.tight_layout();save(fig,'long-strip-barrel')

fig,aa=plt.subplots(2,1,figsize=(7.0,3.6),gridspec_kw={'height_ratios':[1,1.4]})
b=D['long_barrel']['engineering']['beam'];ax=aa[0]
ax.plot([-1320,1320],[0,0],lw=5,color=GREEN)
ax.scatter(b['recommended']['anchors_z_mm'],[0]*17,color=PURPLE,s=22,zorder=3)
ax.set(xlim=(-1390,1390),ylim=(-.4,.6),yticks=[],xlabel='z [mm]')
ax.text(0,.3,'17 stations at 163.75 mm pitch; one centre datum and 16 sliding stations',ha='center',fontsize=7)
ax=aa[1];q=[q for q in b['scan'] if 12<=q['count']<=20]
ax.plot([q['count'] for q in q],[q['total_mm']*1000 for q in q],'o-',color=PURPLE,label='Released-span bending + shear + overhang')
ax.axhline(40,color=GREY,ls='--',label='40 µm gravity allocation')
ax.scatter([17],[b['continuous_beam']['maximum_deflection_mm']*1000],marker='s',color=TEAL,label='Continuous Timoshenko check')
ax.set(xlabel='Bearing stations per stave',ylabel='Displacement [µm]',xticks=list(range(12,21,2)),ylim=(0,100))
ax.legend(fontsize=7,loc='upper right');note(ax,'Worst attached load 1.8004 kg · E = 70 GPa · Gcore = 5 MPa · 2g\nJoint allocation adds 10 µm; joint/ring/torsion qualification remains open.')
fig.tight_layout();save(fig,'long-strip-anchors')

fig,aa=plt.subplots(1,2,figsize=(7.0,3.5))
le=D['long_endcap'];c=le['input'];disc_plan(aa[0],[m for m in le['disc_modules'] if m['face']==0],*c['annulus_mm'],PURPLE,1220)
aa[0].set_title('312 stereo pairs / disc · 12 petals')
ax=aa[1];phi=math.pi/12;f=np.array([[math.sin(phi),-math.cos(phi)],[-math.cos(phi),-math.sin(phi)]])
t=np.linspace(-phi+.002,phi-.002,80)
outer=np.column_stack((1130*np.sin(t),-1130*np.cos(t)));inner=np.column_stack((784*np.sin(t[::-1]),-784*np.cos(t[::-1])))
ax.add_patch(Polygon(np.vstack((outer,inner)),fc=LIGHT,ec=GREY,lw=.5))
for e in le['petal_entities']:
    role=e['role'];d=e['dimensions_mm'];p=f@np.array(e['center_mm'][:2]);frame=np.array(e['frame'])
    if role in ('integral_web','sensitive','electronics') and e['shape_kind']=='box':
        if role in ('sensitive','electronics') and e['center_mm'][2]>1470:continue
        u=f@frame[0,:2];v=f@frame[1,:2]
        ax.add_patch(Polygon([p+x*d['sx']/2*u+y*d['sy']/2*v for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]],fc={'integral_web':GREY,'sensitive':PURPLE,'electronics':GOLD}[role],ec='white',lw=.2,alpha=.65))
    elif role=='cooling_tube':ax.plot([p[0],p[0]],[p[1]-d['length']/2,p[1]+d['length']/2],color=BLUE,lw=1)
    elif role=='mount' and '_pin' in e['name']:ax.scatter(*p,s=20,color=RED,zorder=10)
ax.set(aspect='equal',xlim=(-310,310),ylim=(-1160,-750),xlabel='Petal tangential [mm]',ylabel='Negative radial [mm]',title='26 pairs / petal · six U-loops')
note(ax,'One sensor face projected\nGrey: four integral webs\nRed: three mounting contacts')
fig.tight_layout();save(fig,'long-strip-endcap')

rows=[]
for i,(z0,z1) in enumerate(zip(D['short_endcap']['input']['disc_z_mm'],D['long_endcap']['input']['disc_z_mm']),1):rows.append(f'{i} & {z0:.2f} & {z1:.2f} \\\\')
p=ROOT/'generated/strip-disc-rows.tex';p.write_text('\n'.join(rows)+'\n');artifacts.append(p)
(ROOT/'data/tracker-render-manifest.json').write_text(json.dumps(dict(generator='scripts/tracker_figures.py',generator_sha256=sha(Path(__file__)),matplotlib=matplotlib.__version__,snapshot_sha256=manifest['snapshot_sha256'],artifacts=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in artifacts]),indent=2)+'\n')
print(f'Rendered {len(artifacts)-1} vector figures and one disc table from verified snapshots.')
