#!/usr/bin/env python3
"""Render the retained first-step Gen3 material survey with native portal overlays."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LogNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import numpy as np


COLORS={0:'#66523d',2:'#0077bb',3:'#00446b',4:'#ee7733',5:'#984108',6:'#009988',7:'#00574e'}
LABELS={0:'Beam pipe',2:'Pixel passive',3:'Pixel sensitive',4:'Short strip passive',5:'Short strip sensitive',6:'Long strip passive',7:'Long strip sensitive'}


def save(fig, output, name):
    for suffix in ('png','pdf','svg'):
        path=output/f'{name}.{suffix}'
        fig.savefig(path,dpi=190,bbox_inches='tight',metadata={'Creator':'nODD Gen3 material survey'})
        if suffix=='svg':path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    plt.close(fig)


def lines(ax,portals,**kwargs):
    seg=[[(z,r) for r,z in p['rz_segment_mm']] for p in portals]
    ax.add_collection(LineCollection(seg,**kwargs))


def scatter(ax,data,portals,xlim,ylim,title):
    for category,color in COLORS.items():
        mask=(data['category']==category)&(data['z']>=xlim[0])&(data['z']<=xlim[1])&(data['r']>=ylim[0])&(data['r']<=ylim[1])
        ax.scatter(data['z'][mask],data['r'][mask],s=.6 if category%2==0 else 1.2,c=color,alpha=.22 if category%2==0 else .7,linewidths=0,rasterized=True)
    lines(ax,portals,color='#202020',linewidth=.65,alpha=.8,zorder=3)
    ax.set(xlim=xlim,ylim=ylim,xlabel='z [mm]',ylabel='r [mm]',title=title)
    ax.grid(alpha=.12)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--data',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    survey=json.loads((args.data/'survey.json').read_text());g=json.loads((args.data/'geometry-summary.json').read_text());data=np.load(args.data/'scatter.npz');h=np.load(args.data/'occupancy.npz');portals=g['portals']
    plt.rcParams.update({'font.size':10,'axes.titlesize':12,'svg.hashsalt':'nodd-gen3-map'})
    legend=[Line2D([],[],marker='o',linestyle='',markersize=5,color=COLORS[c],label=LABELS[c]) for c in COLORS]
    legend.append(Line2D([],[],color='#202020',lw=1,label=f"Native Gen3 portals ({len(portals)})"))
    fig,ax=plt.subplots(figsize=(15,5.8));scatter(ax,data,portals,(-4100,4100),(0,1200),'Recorded Geant4 material and native Gen3 Tracker portals — DRAFT')
    ax.legend(handles=legend,loc='upper center',bbox_to_anchor=(.5,-.13),ncol=4,frameon=False)
    fig.text(.5,.01,f"100,000 geantinos · {survey['steps']:,} material steps · displayed every {survey['scatter_stride']}th midpoint ({len(data['r']):,} points)",ha='center',fontsize=9)
    fig.subplots_adjust(bottom=.24);save(fig,args.output,'material-portals-rz')
    fig,axs=plt.subplots(2,1,figsize=(14,9));scatter(axs[0],data,portals,(-650,650),(20,215),'Pixel barrel: sensitive sensors and passive backing')
    scatter(axs[1],data,portals,(530,3170),(25,215),'Positive pixel endcap: both mounting faces are retained')
    axs[1].legend(handles=legend[:3]+legend[-1:],loc='upper center',bbox_to_anchor=(.5,-.15),ncol=4,frameon=False)
    fig.suptitle('Pixel material / portal detail — DRAFT',y=.99);fig.tight_layout(rect=(0,.06,1,.97));save(fig,args.output,'pixel-portals-detail')
    fig,ax=plt.subplots(figsize=(15,5.8));values=h['mean_X0'].T;positive=values[values>0]
    image=ax.pcolormesh(h['z_edges'],h['r_edges'],np.ma.masked_less_equal(values,0),norm=LogNorm(vmin=np.percentile(positive,5),vmax=positive.max()),cmap='magma',rasterized=True)
    lines(ax,portals,color='#777777',linewidth=.45,alpha=.75)
    for item in survey['flag_clusters'][:10]:
        x,y=item['z_min_mm'],item['r_min_mm'];width=item['z_max_mm']-x;height=item['r_max_mm']-y
        ax.add_patch(Rectangle((x,y),width,height,fill=False,edgecolor='#00cfd0',lw=1.2))
        ax.annotate(item['id'],(x+width/2,y+height/2),color='#007d80',fontsize=8,xytext=(3,8),textcoords='offset points',bbox={'fc':'white','ec':'none','alpha':.8,'pad':1})
    ax.set(xlim=(-4100,4100),ylim=(0,1200),xlabel='z [mm]',ylabel='r [mm]',title=f"All-step material budget; largest remote-material clusters (> {survey['near_threshold_mm']:g} mm from every portal)")
    fig.colorbar(image,ax=ax,pad=.01,label='Σ step length / X₀ per generated geantino in 10 × 5 mm cell')
    fig.text(.5,.01,'DRAFT · Full 100k scan, all steps · Cyan boxes: ranked connected 20 mm r × 50 mm z cells · See flag-clusters.csv for every cluster',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.035,1,1));save(fig,args.output,'remote-material-rz')
    fig,ax=plt.subplots(figsize=(15,5.8));scatter(ax,data,[],(-4100,4100),(0,1200),'Nearby passive-material carriers — DRAFT; remote services and unresolved pixel faces require follow-up')
    lines(ax,portals,color='#aaaaaa',linewidth=.45,alpha=.6)
    byid={p['surface_id']:p for p in portals}
    for a in survey['assignments']:
        if not a['near_selected_steps']:continue
        color='#bb3355' if a['after_steps']>0 else '#3366bb'
        lines(ax,[byid[a['surface_id']]],color=color,linewidth=1.0,alpha=.75)
    ax.legend(handles=[Line2D([],[],color='#3366bb',label='Used for before rule'),Line2D([],[],color='#bb3355',label='Used by after rule (may also collect before)'),Line2D([],[],color='#aaaaaa',label='Other native portals')],loc='upper center',bbox_to_anchor=(.5,-.13),ncol=3,frameon=False)
    fig.text(.5,.01,'Closest finite crossing along the recorded ray; sensor silicon and beam-pipe slab retained natively. No map installed.',ha='center',fontsize=9)
    fig.subplots_adjust(bottom=.21);save(fig,args.output,'proposed-carriers-rz')
    print('Rendered 4 figures in PNG, PDF and SVG')


if __name__=='__main__':main()
