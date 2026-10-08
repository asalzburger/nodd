#!/usr/bin/env python3
"""DES021 vector drawings generated from exact placements and cooling paths."""
import argparse
import json
import math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle,Wedge,Circle
import numpy as np
from model import ROOT,load,build,cooling,screen,execution,sha

COL=['#326c93','#799d87','#cf984a','#8c75a4','#688590']
def draw(out):
    c=load();l=build(c);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Serif','font.size':10,'svg.fonttype':'none','svg.hashsalt':'DES021','axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(1,2,figsize=(16,8),layout='constrained')
    ax=axs[0]
    for p in range(12):ax.add_patch(Wedge((0,0),685,p*30+.08,(p+1)*30-.08,width=449,fc='#e5ebe4',ec='#aaa',lw=.3))
    for m in [m for m in l['modules'] if m['layer']==0]:
        p=np.array(m['center_mm'][:2]);u=np.array(m['u'][:2]);v=np.array(m['v'][:2]);corners=[p+a*24*u+b*48*v for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        ax.add_patch(Polygon(corners,fc=COL[m['ring']],ec='#163449',lw=.4,alpha=.50))
    for r in c['annulus_mm']:ax.add_patch(Circle((0,0),r,fill=False,ec='#b83a3a',lw=1,ls='--'))
    ax.set(xlim=(-720,720),ylim=(-720,720),aspect='equal',xlabel='x [mm]',ylabel='y [mm]',title='Short-strip disc · 360 rectangular modules\nFive rings on twelve removable petals')
    ax.text(.02,.02,'Fine U: tangential · coarse V: radial\nDashed: nominal active annulus',transform=ax.transAxes,fontsize=9,bbox=dict(fc='white',ec='none',alpha=.8))
    ax=axs[1]
    ax.add_patch(Wedge((0,0),685,.08,29.92,width=449,fc='#edf0eb',ec='#677b68',lw=1))
    for m in [m for m in l['modules'] if m['layer']==0 and m['petal']==0]:
        p=np.array(m['center_mm'][:2]);u=np.array(m['u'][:2]);v=np.array(m['v'][:2]);corners=[p+a*24*u+b*48*v for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        ax.add_patch(Polygon(corners,fc=COL[m['ring']],ec='#163449',lw=.5,alpha=.28))
    for seg in cooling(c):
        d=seg['dims'];center=np.array(seg['center'][:2])
        if seg['kind']=='torus':
            a=np.linspace(d['start'],d['start']+d['angle'],100);pts=center+d['major']*np.stack([np.cos(a),np.sin(a)],axis=1)
        else:
            dr=np.array([math.cos(seg['rz']),math.sin(seg['rz'])])*d['length']/2;pts=np.stack([center-dr,center+dr])
        ax.plot(*pts.T,c='#b23e65',lw=1.6)
    for phi,color,label in [(15,'#b57f27','LV bus on back'),(22,'#795584','HV / signal on back')]:
        a=math.radians(phi);r=np.array([250,678]);ax.plot(r*np.cos(a),r*np.sin(a),c=color,lw=4,label=label)
    a=math.radians(15);p=np.array([695*math.cos(a),695*math.sin(a)]);u=np.array([-math.sin(a),math.cos(a)]);v=np.array([-math.cos(a),-math.sin(a)])
    ax.add_patch(Polygon([p+su*26*u+sv*10*v for su,sv in [(-1,-1),(1,-1),(1,1),(-1,1)]],fc='#606e83'))
    ax.text(470,75,'Embedded Ti/CO₂ serpentine\nOD 2.5 / wall 0.14 mm',color='#a5345c',fontsize=9)
    ax.annotate('Outer interface\nboard + fan',xy=p,xytext=(440,360),arrowprops=dict(arrowstyle='->'),fontsize=9)
    ax.set(aspect='equal',xlim=(200,730),ylim=(-15,390),xlabel='x [mm]',ylabel='y [mm]',title='One petal · 30 modules, one cooling loop\nSupply at 29° · return at 28°')
    ax.legend(loc='lower right',fontsize=8)
    fig.suptitle('nODD · DES-021 · detailed short-strip endcap PROTOTYPE',fontsize=15)
    for ext in ('svg','png'):fig.savefig(out/f'layout.{ext}',dpi=170,metadata={'Date':None} if ext=='svg' else None)
    plt.close(fig)
    fig,axs=plt.subplots(2,1,figsize=(15,9),layout='constrained');ax=axs[0]
    for label,lo,hi,color in [('back bus',-7.15,-6.8,'#b57f27'),('back skin',-6.8,-6.65,'#516c56'),('core',-6.55,-1.55,'#dce3d4'),('front skin',-1.45,-1.3,'#516c56')]:
        ax.add_patch(Rectangle((lo,236),hi-lo,449,fc=color,ec='none',label=label))
    for i,(lo,hi) in enumerate(c['frame_mm']):
        ax.add_patch(Rectangle((-13.5,lo),3,hi-lo,fc='#516c56',label='mounting frames' if i==0 else None))
        ax.add_patch(Rectangle((-10.5,(lo+hi)/2-3),3.7,6,fc='#6e786b'))
    for ring in l['rings']:
        r=ring['radius_mm'];lift=(ring['ring']%2)*3
        ax.add_patch(Rectangle((lift-.9,r-48),1.,96,fc=COL[ring['ring']],ec='#243c4c',lw=.5))
        ax.add_patch(Rectangle((-1.3,r-c["pickup_mm"][1]/2),lift+.4,c["pickup_mm"][1],fc='#827e78',alpha=.8))
        for offset in (-20,20):ax.add_patch(Circle((-4.05,r+offset),1.25,fc='#b23e65'))
    ax.add_patch(Rectangle((0,685),8,20,fc='#606e83'));ax.add_patch(Rectangle((9,236),.5,449,fc='#c1a66b',alpha=.5))
    ax.set(xlim=(-15,12),ylim=(225,715),xlabel='w relative to disc datum [mm] (outward from IP)',ylabel='radius [mm]',title='Petal section (selected azimuth; aspect expanded)\nNeighbouring phi modules are lifted by 1.5 mm')
    ax.text(1,235,'Effective fanout at w=9..9.5 mm\nIndividual vias / connectors not modeled',fontsize=9)
    ax.legend(ncols=5,loc='upper left',fontsize=8)
    ax=axs[1]
    for r in (260,340,480,660):ax.plot([0,1200],[r,r],c='#698471',lw=2)
    ax.add_patch(Rectangle((1245,244),65,506,fc='#dab47d',alpha=.5,label='barrel collector'))
    ax.add_patch(Rectangle((1310,710),2190,73,fc='#daba8d',alpha=.5,label='fixed trunk'))
    for j,z in enumerate(c['disc_z_mm']):
        ax.add_patch(Rectangle((z-13.5,236),23,464,fc=COL[j%5],alpha=.8))
        ax.add_patch(Rectangle((z+15,685),70,25,fc='#c49543',alpha=.8))
        ax.text(z,205,f'D{j}',ha='center',fontsize=9)
    ax.axvline(c['old_first_z_mm'],c='#b33f3f',ls='--',lw=1)
    ax.annotate('First disc: 1295.5 → 1335 mm\n11.5 mm minimum collector clearance',xy=(1335,700),xytext=(1500,910),arrowprops=dict(arrowstyle='->'),fontsize=10)
    ax.set(xlim=(0,3520),ylim=(180,1010),xlabel='positive z [mm]',ylabel='radius [mm]',title='Barrel–endcap interface and service accumulation')
    ax.legend(loc='upper right',fontsize=8)
    fig.suptitle('Support, mounting and service interfaces · DES-021 DRAFT',fontsize=14)
    for ext in ('svg','png'):fig.savefig(out/f'section-services.{ext}',dpi=170,metadata={'Date':None} if ext=='svg' else None)
    plt.close(fig)
    for file in out.glob('*.svg'):
        file.write_text('\n'.join(line.rstrip() for line in file.read_text().splitlines())+'\n')
    (out/'drawing-provenance.json').write_text(json.dumps(dict(execution=execution(),input_sha256=sha(Path(__file__).with_name('inputs.json')),producer_sha256=sha(__file__),artifacts={f.name:sha(f) for f in out.glob('*.svg')}),indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'docs/validation/DES-021/figures');a=p.parse_args();draw(a.output)
