"""Reproducible DES031 physical slab and native material/coverage figures."""
import argparse
import copy
import json
import math
from pathlib import Path
from barrel_layout import build, coverage, crossings
from model import sha


def plot(directory,output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon,Rectangle
    r,base=build();native=json.loads((directory/'native.json').read_text());output.mkdir(parents=True,exist_ok=True);plt.rcParams.update({'font.size':10,'svg.hashsalt':'DES031'})
    fig,axes=plt.subplots(1,2,figsize=(13,7),gridspec_kw={'width_ratios':[1,1.1]});ax=axes[0];a=r['assembly_config'];t=math.tan(math.pi/16)
    for sector in range(16):
        phi=sector*2*math.pi/16;co,si=math.cos(phi),math.sin(phi)
        for layer in r['layers']:
            front=layer['front_mm'];outer=front+1.9;poly=[[front,-front*t+21],[outer,-outer*t+21],[outer,outer*t-21],[front,front*t-21]];p=[[(x*co-y*si)/1000,(x*si+y*co)/1000] for x,y in poly];ax.add_patch(Polygon(p,color='#c9a45a',linewidth=0))
        for radius in (1700,2233.2):
            p=[[radius/math.cos(math.pi/16)*math.cos(phi+sign*math.pi/16)/1000,radius/math.cos(math.pi/16)*math.sin(phi+sign*math.pi/16)/1000] for sign in (-1,1)];ax.plot(*zip(*p),color='#566678',lw=.8)
    ax.set(xlim=(-2.5,2.5),ylim=(-2.5,2.5),xlabel='x [m]',ylabel='y [m]',title='Sixteen sectors · 48 Si–W layers\nRetained 1.700–2.233 m package apothems');ax.set_aspect('equal');ax.grid(alpha=.2);ax.text(0,0,'Tracker / inner solenoid\nplanning space\n(not constructed here)',ha='center',va='center',color='#566678')
    ax=axes[1];layer=r['layers'][0];p=layer['panels'][4];centre=p['center_mm'];width=2*((layer['front_mm']+1.9)*t-21)
    ax.add_patch(Rectangle((-p['length_mm']/2,-width/2),p['length_mm'],width,facecolor='#fbefe0',edgecolor='#a68d70'))
    for sign in (-1,1):ax.add_patch(Rectangle((sign*p['length_mm']/2-(5 if sign>0 else 0),-width/2),5,width,color='#9aa5af'))
    bay=p['bay_center_mm']-centre;ax.add_patch(Rectangle((bay-20,-width/2),40,width,facecolor='#cfb8ec',edgecolor='#7b59a9'))
    for m in layer['modules']:
        if m['panel']!=p['index']:continue
        u,z=m['center_mm'];z-=centre;ax.add_patch(Rectangle((z-47,u-47),94,94,facecolor='#d4dce1',edgecolor='#85939b',lw=.4));ax.add_patch(Rectangle((z-45,u-45),90,90,facecolor='#bdcebd',edgecolor='#769076',lw=.4));ax.add_patch(Rectangle((z-44,u-44),88,88,facecolor='#82b68e',edgecolor='none'))
    for q in layer['interfaces']:
        if q['panel']!=p['index']:continue
        u=sum(layer['column_centers_mm'][j] for j in q['lanes'])/len(q['lanes']);ax.add_patch(Rectangle((bay-10,u-10),20,20,color='#79569f'))
    for u in layer['column_centers_mm']:ax.plot([-490+5,490-5],[u,u],color='#b4744e',ls='--',lw=.7,alpha=.7)
    ax.set(xlim=(-540,540),ylim=(-355,355),xlabel='Axial position within slab [mm]',ylabel='Tangential position [mm]',title='One 1000 mm slab · inner layer\n54 sensors, shared lane interfaces and cooling');ax.set_aspect('equal');ax.grid(alpha=.15)
    fig.suptitle('DES031 · detailed isolated SiW barrel prototype',fontsize=15);fig.text(.06,.055,'Green: active silicon with guards; grey: PCB/frame; purple: shared bay. Dashed cooling runs lie behind the sensors.\n48-layer slab shifts alternate −96/+96 mm; 276/468 mm end slabs preserve ±3880 mm bounds. External headers/ports are absent.',fontsize=10);fig.subplots_adjust(bottom=.16,top=.85,wspace=.3)
    for ext in ('svg','png'):fig.savefig(output/('barrel-layout.'+ext),dpi=160,metadata={'Date':None} if ext=='svg' else None)
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(13,5));colours=['#355f9b','#cf8644','#48926e','#915b9f']
    for phi,color in zip(sorted({q['phi'] for q in native['material_rays']}),colours):
        values=sorted((q for q in native['material_rays'] if q['phi']==phi),key=lambda q:q['eta']);label=f'φ = {phi:.3f}'
        axes[0].plot([q['eta'] for q in values],[q['x_over_x0'] for q in values],'.-',label=label,color=color);axes[1].plot([q['eta'] for q in values],[q['crossed_layers'] for q in values],'.-',label=label,color=color)
    axes[0].set(xlabel='η',ylabel=r'$t/X_0$',title='Native ROOT material rays · barrel only');axes[1].set(xlabel='η',ylabel='Sensitive layers crossed',ylim=(-1,50),title='Native finite-silicon intersections');axes[1].axhline(48,color='#777',ls=':',lw=.8)
    for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=8)
    fig.text(.07,.015,'Includes barrel absorber, local readout/cooling and supports; excludes tracker, solenoid, endcaps and external services. Geometric sampling, not efficiency.',fontsize=9);fig.tight_layout(rect=(0,.06,1,1))
    for ext in ('svg','png'):fig.savefig(output/('barrel-material.'+ext),dpi=160,metadata={'Date':None} if ext=='svg' else None)
    plt.close(fig)
    # Matplotlib emits trailing spaces inside multiline SVG paths. Normalize
    # them without changing the XML geometry, so retained figures pass Git QA.
    for path in output.glob('barrel-*.svg'):
        path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    current=coverage(r);c=copy.deepcopy(r['config']);c['layer_panel_phases_mm']=[0];aligned,_=build(c);control=coverage(aligned);witness=dict(status='INFERENCE / geometric samples only',summary=r['summary'],aligned_control=control,staggered=current,native_rays= len(native['material_rays']),native_source_sha256=sha(directory/'native.json'),plotter_sha256=sha(__file__),source_sha256=r['source_sha256']);(output/'plot-inputs.json').write_text(json.dumps(witness,indent=2)+'\n')
    print('Wrote layout and native material/coverage SVG/PNG, plus source-bound plot inputs.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plot(a.directory,a.output)
