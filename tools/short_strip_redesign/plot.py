#!/usr/bin/env python3
"""DES043 figures from compact source summaries; unrooted + Matplotlib."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
os.environ.setdefault('MPLBACKEND','Agg')
ROOT=Path(__file__).resolve().parents[2]
os.environ.setdefault('XDG_CACHE_HOME',str(ROOT/'build/short-strip-redesign/xdg-cache'))
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'build/short-strip-redesign/mpl-cache'))
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle
from unrooted import ScatterData
from unrooted.plot.mpl.scatter import plot as scatter_plot
from unrooted.plot.style import HistogramStyle
import model
from diagnostics import sample_piece

OLD='#627589';NEW='#007f86';HEAT='#c47623';RED='#b54048'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','pdf.fonttype':42})


def frame(title,sub,cols=2,size=(13,6)):
    fig,axes=plt.subplots(1,cols,figsize=size,squeeze=False)
    fig.subplots_adjust(left=.08,right=.98,bottom=.20,top=.78,wspace=.31)
    fig.suptitle(title,x=.08,y=.97,ha='left',weight='bold',fontsize=17)
    fig.text(.08,.89,sub,fontsize=10,color='#52606b')
    fig.text(.08,.035,'DES043 · DRAFT / PROTOTYPE · source-level engineering screens · no hardware or full-tracker material qualification',fontsize=9,color='#52606b')
    return fig,axes[0]


def save(fig,out,name,manifest):
    for ext in ('png','pdf'):
        p=out/(name+'.'+ext);fig.savefig(p,dpi=160,bbox_inches='tight',metadata={'CreationDate':None,'ModDate':None} if ext=='pdf' else None)
        manifest[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    plt.close(fig)


def points(ax,x,y,color,label):
    scatter_plot(ScatterData(np.asarray(x,dtype=float),np.asarray(y,dtype=float)),ax=ax,style=HistogramStyle.as_scatter(marker='o',marker_color=color,marker_size=2.3),label=label,set_axis_labels=False)
    ax.plot(x,y,color=color,lw=1.4)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--summary',type=Path,default=ROOT/'docs/validation/DES-043/summary.json');p.add_argument('--output',type=Path,default=ROOT/'docs/validation/DES-043/figures');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    c=model.load();s=json.loads(a.summary.read_text());bc,ec,lc,bl,el,ll,new=model.geometry(c);manifest={}
    fig,axes=frame('Short-strip endcaps: more active coverage, a smaller service annulus','One 30° petal, transverse projection. Board and fan sit in front of sensors; projected overlaps are not solid overlaps.',size=(14,7.6))
    for ax,layout,label,color,rin,rout in zip(axes,[el,new],['Merged PR109 · 360 sensors/disc','Proposed DES043 · 396 sensors/disc'],[OLD,NEW],[710,717],[783,781.5]):
        for m in layout['modules']:
            if m['layer']!=0 or m['petal']!=0:continue
            corners=[[m['center_mm'][j]+i*24*m['u'][j]+k*48*m['v'][j] for j in (0,1)] for i,k in [(-1,-1),(-1,1),(1,1),(1,-1)]]
            ax.add_patch(Polygon(corners,facecolor=color,edgecolor='white',lw=.6,alpha=.72))
        phi=np.linspace(0,np.pi/6,150)
        for radius,style,col in [(rin,'-',HEAT),(rout,'-',HEAT),(787.2435,'--','#222222')]:ax.plot(radius*np.cos(phi),radius*np.sin(phi),style,color=col,lw=1.3)
        ax.set(title=label,xlabel='x [mm]',ylabel='y [mm]',xlim=(220,815),ylim=(-5,405));ax.set_aspect('equal');ax.grid(alpha=.13)
        outer=max(model.radial_bounds(m)[1] for m in layout['modules'])
        ax.text(.03,.94,f'Active outer radius {outer:.1f} mm\nGap to long active silicon {787.2435-outer:.1f} mm',transform=ax.transAxes,va='top',bbox=dict(facecolor='white',edgecolor='none',alpha=.9),fontsize=10)
    for key,col in [('inner',NEW),('outer',HEAT)]:
        for piece in s['cooling_routes'][key]:
            xy=np.array(sample_piece(piece,1.));axes[1].plot(xy[:,0],xy[:,1],color=col,lw=.9)
    axes[1].text(.38,.02,'Two separate cooling circuits\n717–781.5 mm service trunk',transform=axes[1].transAxes,fontsize=9)
    save(fig,a.output,'endcap-layout',manifest)

    fig,axes=frame('Radial handoff and service capacity','Long-strip silicon and passive hardware remain fixed. Capacity includes barrel traffic, both petal loops and 25% spare.',size=(13,6.5))
    z=ec['disc_z_mm'];longz=lc['disc_z_mm']
    for zz in z:
        axes[0].plot([zz,zz],[243.5,s['geometry']['old_active_outer_mm']],color=OLD,lw=5,alpha=.38)
        axes[0].plot([zz+10,zz+10],[243.5,s['geometry']['new_active_outer_mm']],color=NEW,lw=2)
    for zz in longz:axes[0].plot([zz,zz],[s['geometry']['long_active_inner_mm'],1050],color='#844b98',lw=2)
    axes[0].add_patch(Rectangle((1310,717),2190,64.5,facecolor=HEAT,alpha=.22,label='Proposed trunk'))
    axes[0].add_patch(Rectangle((1245,244),65,537.5,facecolor=HEAT,alpha=.22))
    axes[0].set(xlabel='|z| [mm]',ylabel='Radius [mm]',ylim=(200,1080),xlim=(1180,3550),title='R–Z source envelope')
    axes[0].plot([],[],color=OLD,lw=4,label='PR109 short strips');axes[0].plot([],[],color=NEW,lw=2,label='DES043 short strips');axes[0].plot([],[],color='#844b98',lw=2,label='Fixed long strips');axes[0].legend(fontsize=8,loc='lower right');axes[0].grid(alpha=.15)
    packs=s['packing'];x=range(1,13)
    for name,col in [('nominal',NEW),('adverse',HEAT)]:points(axes[1],list(x),[q['fill_ratio'] for q in packs if q['scenario']==name],col,name.capitalize())
    axes[1].axhline(1,color=RED,ls='--',label='Capacity limit');axes[1].set(xlabel='Shared service sector',ylabel='Demand / available area',title='Cumulative downstream trunk',ylim=(0,1.15),xticks=list(x));axes[1].grid(alpha=.15);axes[1].legend(fontsize=9)
    save(fig,a.output,'handoff-capacity',manifest)

    fig,axes=frame('Material benefit: cable copper pays for the redesign','Changed-component proxy only. Added sensors, graphite inserts, TIM, cooling branches and a 5 g/module reserve are included.',size=(14,7.5))
    entries=s['material']['entries'];labels=['External cable Cu','Cable insulation','Fibre payload','Added modules','Thicker spreader','Direct thermal inserts','TIM + service reserve','Larger petal support','Outer frames','Local LV rails','Local cooling','Extra bulk pipes']
    delta=[q['delta_kg'] for q in entries]
    axes[0].barh(labels,delta,color=[NEW if x<0 else HEAT for x in delta]);axes[0].invert_yaxis();axes[0].axvline(0,color='#555',lw=.8);axes[0].set(xlabel='Change in modelled mass [kg]',title=f'Net: {sum(delta):.0f} kg; no insulation credit: {s["material"]["delta_without_insulation_credit_kg"]:.0f} kg');axes[0].grid(axis='x',alpha=.15)
    profile=s['copper_corridor_profile'];edges=profile['eta_edges'];x=[(lo+hi)/2 for lo,hi in zip(edges,edges[1:])]
    axes[1].plot(x,np.array(profile['old_X0'])*100,color=OLD,label='Inherited cable geometry');axes[1].plot(x,np.array(profile['new_X0'])*100,color=NEW,label='Proposed cable geometry')
    axes[1].set(xlabel='|η|, straight origin ray',ylabel='Azimuth-averaged Cu [% X₀]',title='Longitudinal power-trunk copper alone',xlim=(.7,3.7));axes[1].grid(alpha=.15);axes[1].legend(fontsize=9)
    axes[1].text(.52,.42,'Excludes other tracker material and collectors.\nRelocation can increase individual η bins.\nA full DD4hep/Geant4 scan is still required.',transform=axes[1].transAxes,fontsize=8.3)
    save(fig,a.output,'material-budget',manifest)

    fig,axes=frame('Power and thermal requirements for the proposed module','Assumed fixed electronics fractions: 25% nominal, 50% adverse, 100% no-scaling stress control. Leakage remains 2 W/module.',size=(13,6.8))
    cases=s['engineering'];labels=['Nominal','Adverse','No power\nscaling'];xx=np.arange(3)
    axes[0].bar(xx,[q['total_module_heat_W'] for q in cases],color=[NEW,HEAT,RED],width=.6)
    axes[0].set(xticks=xx,xticklabels=labels,ylabel='Electronics + leakage [W/module]',title='Conditional load; no measured ASIC claim');axes[0].grid(axis='y',alpha=.15)
    for i,q in enumerate(cases):axes[0].text(i,q['total_module_heat_W']+.6,f"{q['total_module_heat_W']:.2f} W",ha='center')
    for region,col in [('barrel',NEW),('endcap',HEAT)]:points(axes[1],xx.tolist(),[q['thermal'][region]['sensor_C'] for q in cases],col,region.capitalize())
    axes[1].axhline(-20,color=RED,ls='--',label='Sensor requirement');axes[1].set(xticks=xx,xticklabels=labels,ylabel='Maximum sensor screen [°C]',title='−35 °C coolant, 0.35 mm spreader',ylim=(-31,-10));axes[1].grid(alpha=.15);axes[1].legend(fontsize=9)
    fig.text(.08,.11,'Required module redesign: two logical ASIC tiles + redistribution, thermal windows, direct inserts, insulating TIM and new power/flex protection.',fontsize=9)
    save(fig,a.output,'power-thermal',manifest)
    fig,axes=frame('Module redesign: retain the sensor, rebuild the thermal interface','Dimensioned source schematic. Central saddle reaches a physical tube; redistribution and material properties still need qualification.',size=(13,7.2))
    layers=[('Sensor',-.1,.1,OLD),('Bumps',-.125,-.1,HEAT),('Redistribution',-.175,-.125,HEAT),('Two ASIC tiles',-.325,-.175,'#844b98'),('ASIC glue',-.375,-.325,'#888888'),('Graphite spreader',-.725,-.375,NEW),('Insulating TIM',-.825,-.725,'#d6ac58'),('Backing, with window',-1.025,-.825,OLD)]
    for i,(label,lo,hi,col) in enumerate(layers):
        y=8-i;axes[0].add_patch(Rectangle((-24,y-.28),48,.56,facecolor=col,alpha=.75));axes[0].text(27,y,f'{label} · {(hi-lo)*1000:.0f} µm',va='center',fontsize=9)
    axes[0].add_patch(Rectangle((-8,-1),16,1.5,facecolor=NEW,alpha=.6));axes[0].text(27,-.2,'Central 16 × 60 mm saddle\n≤8 mm thermal path to pipe',va='center',fontsize=9)
    axes[0].plot([-15,15],[-1.4,-1.4],color=HEAT,lw=7);axes[0].text(27,-1.4,'Ti tube OD 2.5 mm / wall 0.14 mm',va='center',fontsize=9)
    axes[0].set(xlim=(-30,100),ylim=(-2.2,9),title='Normal stack · exploded spacing',xlabel='Local u [mm]');axes[0].set_yticks([])
    ax=axes[1];ax.add_patch(Rectangle((-24,-48),48,96,facecolor=OLD,alpha=.12,edgecolor=OLD,lw=1.5))
    ax.add_patch(Rectangle((-8,-30),16,60,facecolor=NEW,alpha=.35,label='Central saddle'))
    for v in (-18,18):ax.add_patch(Rectangle((-11.7,v-11.7),23.4,23.4,facecolor='#844b98',alpha=.35,edgecolor='#844b98',label='ASIC tile' if v==-18 else None))
    m=next(m for m in new['modules'] if m['layer']==0 and m['petal']==0 and m['ring']==4);phi=np.arctan2(m['center_mm'][1],m['center_mm'][0]);co,si=np.cos(phi),np.sin(phi);cx,cy=m['center_mm'][:2]
    for piece in s['cooling_routes']['outer']:
        xy=np.array(sample_piece(piece,.25));dx=xy[:,0]-cx;dy=xy[:,1]-cy;u=-si*dx+co*dy;v=-co*dx-si*dy
        ax.plot(u,v,color=HEAT,lw=2)
    ax.plot([],[],color=HEAT,lw=2,label='Actual assigned tube projection')
    ax.set(xlim=(-28,28),ylim=(-52,52),title='Outer edge module · local footprint',xlabel='Local u [mm]',ylabel='Local v [mm]');ax.set_aspect('equal');ax.grid(alpha=.15);ax.legend(fontsize=8,loc='lower right')
    save(fig,a.output,'module-redesign',manifest)
    metadata=dict(schema_version=1,input_sha256=model.sha(a.summary),plot_sha256=model.sha(__file__),versions={name:importlib.metadata.version(name) for name in ['numpy','matplotlib','unrooted']},files=manifest)
    (a.output/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps(metadata['versions']));print(len(manifest),'figure files')


if __name__=='__main__':main()
