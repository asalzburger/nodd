#!/usr/bin/env python3
"""Deterministic comparison of unchanged tangential and phi-tilted DES-020 inputs."""
import argparse
import math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Polygon
from model import ROOT,CONTROL_INPUT,load,build,frame,foot_profile
from draw import COLORS


def draw(output):
    base=load(CONTROL_INPUT);alt=load(Path(__file__).with_name('inputs-phi-tilted.json'))
    plt.rcParams.update({'font.family':'DejaVu Serif','font.size':10,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,2,figsize=(13,10),layout='constrained')
    for col,(c,label) in enumerate(((base,'Tangential control · alternating 12 mm lanes'),(alt,'Alternative · common radius, +15° phi tilt'))):
        layout=build(c);ax=axes[0,col]
        for layer in layout['layers']:
            for m in (m for m in layout['modules'] if m['layer']==layer['layer'] and m['row']==14):
                x,y,_=m['center_mm'];u=m['u'];ax.plot([x-24*u[0],x+24*u[0]],[y-24*u[1],y+24*u[1]],color=COLORS['sensor'],lw=1.4)
            r=layer['nominal_radius_mm'];ax.add_patch(Circle((0,0),r-18.5,fill=False,color=COLORS['support'],lw=.7))
            ax.text(.72*r,.72*r,f"L{layer['layer']}: {layer['staves']}",fontsize=9,bbox=dict(facecolor='white',edgecolor='none',alpha=.8,pad=1))
        ax.add_patch(Circle((0,0),231.7,fill=False,color='#888888',ls='--',lw=.8))
        ax.set(xlim=(-720,720),ylim=(-720,720),aspect='equal',xlabel='x [mm]',ylabel='y [mm]',title=label)
        ax.text(.5,.015,f"{len(layout['staves'])} staves · {len(layout['modules']):,} modules",transform=ax.transAxes,ha='center',fontsize=9)
        ax=axes[1,col];n=layout['layers'][0]['staves'];r=260
        # Occupied transverse projection of low/high rows, not coincident 3D modules.
        def box(phi,r,tilt,u0,w0,du,dw,color,alpha=1):
            pts=[frame(phi,r,[u0+u,0,w0+w],tilt)[:2] for u,w in ((-du/2,-dw/2),(du/2,-dw/2),(du/2,dw/2),(-du/2,dw/2))]
            ax.add_patch(Polygon(pts,closed=True,facecolor=color,edgecolor=color,lw=.4,alpha=alpha))
        for j in range(-2,3):
            s=layout['staves'][j%n];phi=s['phi_rad'];radius=s['radius_mm'];tilt=s.get('tilt_rad',0)
            box(phi,radius,tilt,0,-4.05,52,5,'#d8dfd2')
            for w in (-1.375,-6.725):box(phi,radius,tilt,0,w,52,.15,COLORS['support'])
            box(phi,radius,tilt,0,-7.05,24.5,.2,COLORS['copper'])
            for lift in (0,1.5):
                box(phi,radius,tilt,0,lift,48,.2,COLORS['sensor'],.9 if lift==0 else .55)
                box(phi,radius,tilt,0,lift-.2,48,.15,COLORS['readout'])
                for u in (-10,10):box(phi,radius,tilt,u,-1.3+(lift+.4)/2,20,lift+.4,COLORS['pickup'],.4)
            for u in (-12,12):
                xy=frame(phi,radius,[u,0,-4.05],tilt)[:2];ax.add_patch(Circle(xy,1.25,color=COLORS['cooling']));ax.add_patch(Circle(xy,1.11,color='white'))
            if tilt:
                f=foot_profile(c,radius);h=f['height_mm'];wm=f['center_w_mm'];k=f['bottom_slope']
                a=c['foot_width_mm']/2
                pts=[frame(phi,radius,[c['foot_u_mm']+u,0,w],tilt)[:2] for u,w in ((-a,wm-h/2-a*k),(a,wm-h/2+a*k),(a,wm+h/2),(-a,wm+h/2))]
                ax.add_patch(Polygon(pts,color=COLORS['support']))
            else:
                inner=243;back=radius-7.15;box(phi,radius,0,0,(inner+back)/2-radius,4,back-inner,COLORS['support'])
        for radius in (240,243):ax.add_patch(Circle((0,0),radius,fill=False,color=COLORS['support'],lw=1))
        ax.set(xlim=(225,308),ylim=(-78,78),aspect='equal',xlabel='x [mm]',ylabel='y [mm]',title='L0 detail · cold stack, cooling and feet')
        if col:
            ax.annotate('',xy=(280,5.36),xytext=(260,0),arrowprops=dict(arrowstyle='->',color='#333333'))
            ax.text(283,3,'N: +15°',fontsize=8)
            ax.annotate('',xy=(254,22.4),xytext=(260,0),arrowprops=dict(arrowstyle='->',color=COLORS['sensor']))
            ax.annotate('U: 75 µm',xy=(255,19),xytext=(278,34),arrowprops=dict(arrowstyle='-',color=COLORS['sensor']),fontsize=8,color=COLORS['sensor'])
        ax.text(.02,.02,'Both row heights projected.\nz is out of the page.',transform=ax.transAxes,fontsize=8,bbox=dict(facecolor='white',edgecolor='none',alpha=.9))
    fig.suptitle('nODD short-strip barrel · DES-020 DRAFT prototype',fontsize=15)
    fig.supxlabel('Blue: sensors · grey-blue: readout · green: cold support / mounting · magenta: cooling · ochre: buses\nTilted assembly repeats at every stave pitch. Sector services and engineering qualification remain separate.',fontsize=9)
    output.mkdir(parents=True,exist_ok=True)
    stem=output/'DES-020-phi-tilted-comparison'
    fig.savefig(stem.with_suffix('.svg'),metadata={'Date':None});fig.savefig(stem.with_suffix('.png'),dpi=150)
    plt.close(fig)
    # Matplotlib occasionally leaves spaces on blank SVG lines.
    svg=stem.with_suffix('.svg');svg.write_text('\n'.join(s.rstrip() for s in svg.read_text().splitlines())+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'docs/design/figures');a=p.parse_args();draw(a.output)
