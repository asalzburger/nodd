#!/usr/bin/env python3
"""Dimensioned DES-020 figures from the executable model; requires Matplotlib."""
import argparse
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle,Arc
from model import ROOT,load,build,screen

COLORS=dict(sensor='#246aa0',readout='#7594b5',support='#4b6354',cooling='#ba5379',
            copper='#bc772d',pickup='#7d7972',service='#d0aa67',failure='#b43e3e')


def draw(output):
    c=load();layout=build(c);s=screen(c,layout)
    plt.rcParams.update({'font.family':'DejaVu Serif','font.size':10,'svg.fonttype':'none',
                         'axes.spines.top':False,'axes.spines.right':False})
    output.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(2,2,figsize=(15,11),layout='constrained')
    ax=axes[0,0]
    for layer in layout['layers']:
        for m in [m for m in layout['modules'] if m['layer']==layer['layer'] and m['row']==14]:
            x,y,_=m['center_mm'];u=m['u'];w=c['active_mm'][0]/2
            ax.plot([x-w*u[0],x+w*u[0]],[y-w*u[1],y+w*u[1]],color=COLORS['sensor'],lw=1.4)
        r=layer['nominal_radius_mm']
        ax.add_patch(Circle((0,0),r-18.5,fill=False,color=COLORS['support'],lw=.7))
        ax.text(r*.73,r*.73,f"L{layer['layer']}: {layer['staves']} staves",fontsize=9,
                bbox=dict(facecolor='white',edgecolor='none',alpha=.8,pad=2))
    ax.add_patch(Circle((0,0),231.7,fill=False,color='#888888',ls='--',lw=1))
    ax.text(0,-210,'pixel service bound',ha='center',color='#666666',fontsize=8)
    ax.set(xlim=(-730,730),ylim=(-730,730),aspect='equal',xlabel='x [mm]',ylabel='y [mm]',
        title=f"(a) Tangential sensors — {s['staves']} straight staves, {s['modules']:,} modules")
    ax=axes[0,1]
    # Actual local radial depths, enlarged longitudinal interval.
    for y,h,col in ((-6.55,5,'#d8dfd2'),(-1.45,.15,COLORS['support']),
                    (-6.8,.15,COLORS['support']),(-7.15,.2,COLORS['copper'])):
        ax.add_patch(Rectangle((-180,y),360,h,facecolor=col,edgecolor='none'))
    for m in [m for m in layout['modules'] if m['layer']==0 and m['stave']==0 and abs(m['center_mm'][2])<160]:
        z=m['center_mm'][2];w=m['lift_mm']
        for y,h,col in ((w-.1,.2,COLORS['sensor']),(w-.275,.15,COLORS['readout']),
                        (w-.575,.2,COLORS['pickup']),(w-.9,.2,COLORS['support'])):
            ax.add_patch(Rectangle((z-48,y),96,h,facecolor=col,edgecolor='none'))
        ax.add_patch(Rectangle((z-32,-1.3),64,w+.4,facecolor=COLORS['pickup'],alpha=.8,edgecolor='none'))
        ax.annotate('sensor / ASIC / backing' if w==0 else 'raised row +1.5 mm',xy=(z,w+.1),
                    xytext=(z,3.3 if w==0 else 5.1),ha='center',fontsize=8,
                    arrowprops=dict(arrowstyle='-',color='#555555',lw=.6))
    ax.plot([-180,180],[-4.05,-4.05],color=COLORS['cooling'],lw=2)
    ax.text(-175,-3.55,'two cooling legs projected',color=COLORS['cooling'],fontsize=8)
    ax.text(-175,-6.2,'5 mm carbon-foam core + CFRP skins',fontsize=8)
    ax.text(-175,-8.15,'insulated Cu buses on back',color=COLORS['copper'],fontsize=8)
    ax.set(xlim=(-180,180),ylim=(-9,7),xlabel='z on stave [mm]',ylabel='outward depth from datum [mm]',
           title='(b) Shared cold sandwich; short pickups clear adjacent rows')
    ax=axes[1,0]
    for layer in layout['layers']:
        r=layer['nominal_radius_mm']
        ax.fill_between([-1210,1210],r-7.15,r+13.6,color=COLORS['support'],alpha=.45)
        for side in (-1,1):
            ax.add_patch(Rectangle((side*1230-15,r),30,20,color=COLORS['readout'],alpha=.6))
    for side in (-1,1):
        lo,hi,zlo,zhi=c['collector_mm']
        ax.add_patch(Rectangle((zlo if side>0 else -zhi,lo),zhi-zlo,hi-lo,facecolor=COLORS['service'],alpha=.55))
        lo,hi,zlo,zhi=c['trunk_mm']
        ax.add_patch(Rectangle((zlo if side>0 else -zhi,lo),zhi-zlo,hi-lo,facecolor=COLORS['service'],alpha=.55))
        ax.axvline(side*1295.5,color=COLORS['failure'],ls=':',lw=1)
        for r in (260,340,480,660):
            ax.annotate('',xy=(side*1260,730),xytext=(side*1260,r),
                        arrowprops=dict(arrowstyle='->',lw=.8,color='#85662c'))
    ax.text(1800,630,'fixed r710–783 mm trunk\nto |z| = 3500 mm',fontsize=9,ha='center')
    ax.text(1800,260,'65 mm collector candidate\n≥70 mm packing recommendation\nfirst strip disc must be reviewed',color=COLORS['failure'],ha='center',fontsize=9)
    ax.set(xlim=(-3600,3600),ylim=(180,820),xlabel='z [mm]',ylabel='radius [mm]',
        title='(c) Barrel services: end boards → sector fans → downstream trunks')
    ax=axes[1,1]
    loads=[]
    for name in ('CMS_PS_comparator','channel_scaled_proxy'):
        x=next(x for x in s['thermal_electrical_flow'] if x['load']==name and x['lift_mm']==1.5 and x['coolant_C']==-35)
        loads.append(x)
    ax.bar([0,1],[x['sensor_C'] for x in loads],bottom=0,color=[COLORS['sensor'],COLORS['failure']])
    ax.axhline(-20,color='#444444',ls='--',lw=1,label='screening sensor goal −20 °C')
    ax.set(xticks=[0,1],xticklabels=['PS comparator\n9.8 W including leakage','channel-scaled proxy\n33.73 W including leakage'],
           ylabel='screened sensor temperature [°C]',ylim=(-40,20),
           title='(d) Readout qualification remains the limiting gate')
    ax.text(.5,14,'coolant −35 °C; effective 1D thermal path',ha='center',fontsize=9)
    ax.text(.5,-36,'Neither load is a measured nODD power prediction',ha='center',fontsize=8)
    ax.legend(loc='upper left',fontsize=8)
    fig.suptitle('nODD short-strip barrel — detailed DRAFT prototype (DES-020)',fontsize=17)
    for ext in ('svg','png'):fig.savefig(output/f'barrel-overview.{ext}',dpi=160)
    plt.close(fig)
    # Cross-section through a pickup: both cooling tubes, backing and buses.
    fig,ax=plt.subplots(figsize=(12,5),layout='constrained')
    def box(x,y,w,h,color):ax.add_patch(Rectangle((x,y),w,h,facecolor=color,edgecolor='#555555',lw=.3))
    box(-26,-6.55,52,5,'#d8dfd2')
    for y in (-1.45,-6.8):box(-26,y,52,.15,COLORS['support'])
    for u in (-12,12):
        ax.add_patch(Circle((u,-4.05),1.25,facecolor=COLORS['cooling'],edgecolor='black',lw=.4))
        ax.add_patch(Circle((u,-4.05),1.11,facecolor='#f2b9d0',edgecolor='none'))
    for w,offset in ((0,-62),(1.5,0)):
        # Separate side-by-side diagrams, each keeps physical dimensions.
        if offset:
            for y in (-1.45,-6.8):box(offset-26,y,52,.15,COLORS['support'])
            box(offset-26,-6.55,52,5,'#d8dfd2')
            for u in (-12,12):
                ax.add_patch(Circle((offset+u,-4.05),1.25,facecolor=COLORS['cooling'],edgecolor='black',lw=.4))
                ax.add_patch(Circle((offset+u,-4.05),1.11,facecolor='#f2b9d0',edgecolor='none'))
        box(offset-20,-1.3,40,w+.4,COLORS['pickup'])
        for y,h,width,col in ((w-.9,.2,48,COLORS['support']),(w-.7,.1,48,'#bfb092'),
            (w-.6,.025,48,'#d6a14e'),(w-.575,.2,48,COLORS['pickup']),
            (w-.375,.1,48,'#bfb092'),(w-.275,.15,46.8,COLORS['readout']),
            (w-.125,.025,48,'#bfa166'),(w-.1,.2,49,COLORS['sensor'])):
            box(offset-width/2,y,width,h,col)
        box(offset-13,-6.95,26,.15,'#e3bd77')
        for x in (offset-12.25,offset+.25):box(x,-7.15,12,.2,COLORS['copper'])
        ax.text(offset,w+1.1,'Low row' if w==0 else 'Raised row',ha='center',fontsize=11)
    ax.annotate('sensor +8 readout tiles\nspreader / insulation / backing',xy=(20,1.2),xytext=(35,2.5),
                arrowprops=dict(arrowstyle='-',lw=.8),fontsize=9)
    ax.annotate('two graphite pickups\n20 ×64 mm² each',xy=(17,0),xytext=(35,-.8),arrowprops=dict(arrowstyle='-',lw=.8),fontsize=9)
    ax.annotate('Ti wall0.14 mm\nCO₂ bore2.22 mm',xy=(13,-4),xytext=(35,-4.2),arrowprops=dict(arrowstyle='-',lw=.8),fontsize=9)
    ax.annotate('Cu12 ×0.20 mm² each\ninsulated backside bus',xy=(9,-7.1),xytext=(35,-7),arrowprops=dict(arrowstyle='-',lw=.8),fontsize=9)
    ax.set(xlim=(-94,74),ylim=(-9,5),xlabel='tangential u [mm]',ylabel='radial depth w [mm]',
           title='DES-020: local stave cross-section — material layers explicit; interfaces unsigned')
    # Radial exaggeration makes thin layers readable; print that convention.
    ax.text(-91,-8.3,'Radial axis enlarged relative to tangential axis; dimensions in mm',fontsize=8)
    for ext in ('svg','png'):fig.savefig(output/f'stave-section.{ext}',dpi=160)
    plt.close(fig)
    # Matplotlib emits trailing spaces within SVG paths; normalize only text
    # whitespace so published vector assets pass the repository diff check.
    for name in ('barrel-overview.svg', 'stave-section.svg'):
        path = output / name
        path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines()) + '\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'build/short-strip-barrel/figures')
    draw(p.parse_args().output)
