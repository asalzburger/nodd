#!/usr/bin/env python3
"""Draw pinned LAr routing hypotheses; no detector export or route-fit claim."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Polygon, Rectangle
from matplotlib.lines import Line2D
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
FILES = ['tools/lar_calorimeter/'+x for x in
         ('barrel.json', 'endcaps.json', 'services.json', 'barrel_services.py')]
FILES += ['docs/design/inputs/DES-032-side-rear-routing.md',
          'docs/design/DES-032-allegro-lar-barrel.md',
          'docs/design/DES-033-allegro-lar-endcaps.md']
C = dict(warm='#cce2ec', active='#3d8798', hcal='#d5d7d9', edge='#52616a',
         old='#bc5c21', new='#7846a0', support='#aa8660', clear='#70777d')


def pipe(start, reference, bus, radius, rear_start, handoff):
    """Centreline and unit normals for two-arc S, axial bus, rear elbow, radial exit."""
    alpha = math.acos(1-(bus-reference)/(2*radius))
    end = start+2*radius*math.sin(alpha)
    a = np.linspace(0, alpha, 101)
    b = np.linspace(alpha, 0, 101)[1:]
    z = list(start+radius*np.sin(a)) + list(end-radius*np.sin(b))
    r = list(reference+radius*(1-np.cos(a))) + list(bus-radius*(1-np.cos(b)))
    angles = list(a)+list(b)
    z += [rear_start]; r += [bus]; angles += [0.]
    a = np.linspace(0, math.pi/2, 101)[1:]
    z += list(rear_start+radius*np.sin(a))
    r += list(bus+radius*(1-np.cos(a))); angles += list(a)
    z += [rear_start+radius]; r += [handoff]; angles += [math.pi/2]
    return np.array(z), np.array(r), -np.sin(angles), np.cos(angles)


def band(ax, route, half_width, color, clearance=False):
    z,r,nz,nr = route
    upper=np.column_stack((z+half_width*nz, r+half_width*nr))
    lower=np.column_stack((z-half_width*nz, r-half_width*nr))
    if clearance:
        for points in (upper,lower):
            ax.plot(*points.T,color=C['clear'],lw=.7,ls=(0,(3,2)),zorder=7)
    else:
        ax.add_patch(Polygon(np.concatenate((upper,lower[::-1])),closed=True,
                             facecolor=color,edgecolor=color,lw=.6,alpha=.85,zorder=6))
        ax.plot(z,r,color='white',lw=.65,zorder=8)


def box(ax, z0,z1,r0,r1, **kw):
    ax.add_patch(Rectangle((z0,r0),z1-z0,r1-r0,**kw))


def dimension(ax,z0,z1,r,label):
    ax.annotate('',xy=(z1,r),xytext=(z0,r),
                arrowprops=dict(arrowstyle='<->',color=C['edge'],lw=.9),zorder=12)
    for z in (z0,z1): ax.plot([z,z],[r-.035,r+.035],color=C['edge'],lw=.7,zorder=12)
    ax.text((z0+z1)/2,r+.055,label,ha='center',va='bottom',fontsize=9,
            bbox=dict(facecolor='white',edgecolor='none',alpha=.9,pad=1.3),zorder=13)


def callout(ax,text,xy,at,color=C['edge']):
    ax.annotate(text,xy=xy,xytext=at,fontsize=9,color=color,
                bbox=dict(facecolor='white',edgecolor='none',alpha=.94,pad=3),
                arrowprops=dict(arrowstyle='->',color=color,lw=.9),zorder=15)


def panel(ax,b,e,s,new=False,shift=0):
    f=e['warm_front_z_mm']/1000-shift; back=e['warm_back_z_mm']/1000-shift
    b_end=b['warm_half_z_mm']/1000
    active_end=(b['warm_half_z_mm']-sum(b[k] for k in
               ('end_warm_mm','end_vacuum_mm','end_cold_mm','end_bath_mm')))/1000
    outer=sum(b[k] for k in ('sampling_outer_radius_mm','rear_bath_mm','rear_cold_mm',
                             'rear_vacuum_mm','rear_warm_mm'))/1000
    h_inner=s['hcal_barrel_front_apothem_mm']/1000
    h_end=s['hcal_barrel_half_z_mm']/1000; h_front=s['hcal_endcap_front_z_mm']/1000
    h_outer=(s['hcal_barrel_front_apothem_mm']+s['hcal_total_depth_mm'])/1000
    h_corner=h_outer/math.cos(math.pi/16)
    # A face-centre HCAL section, with the larger outer-corner envelope dashed.
    box(ax,2.70,h_end,h_inner,h_outer,facecolor=C['hcal'],edgecolor=C['edge'],lw=.8)
    box(ax,h_front,6.75,s['hcal_endcap_inner_radius_mm']/1000,
        s['hcal_endcap_outer_apothem_mm']/1000,facecolor=C['hcal'],edgecolor=C['edge'],lw=.8)
    ax.plot([2.70,h_end],[h_corner,h_corner],ls=':',color=C['edge'],lw=.9)
    ax.text(4.55,4.25,'HCAL barrel',ha='center',fontsize=12,color=C['edge'])
    ax.text(6.56,3.65,'HCAL\nendcap',ha='center',fontsize=10,color=C['edge'])
    # Warm package envelopes and sampling envelopes (no fine plate structure).
    box(ax,2.70,b_end,b['warm_inner_radius_mm']/1000,outer,
        facecolor=C['warm'],edgecolor=C['edge'],lw=.9)
    box(ax,2.70,active_end,b['sampling_inner_radius_mm']/1000,
        b['sampling_outer_radius_mm']/1000,facecolor=C['active'],edgecolor='none')
    if shift:
        box(ax,e['warm_front_z_mm']/1000,e['warm_back_z_mm']/1000,
            e['warm_inner_radius_mm']/1000,e['warm_outer_radius_mm']/1000,
            facecolor='none',edgecolor=C['edge'],ls='--',lw=1.1,zorder=4)
        box(ax,back,h_end,2.05,h_inner,facecolor='#f7e7b7',edgecolor='none',alpha=.55,zorder=1)
    box(ax,f,back,e['warm_inner_radius_mm']/1000,e['warm_outer_radius_mm']/1000,
        facecolor=C['warm'],edgecolor=C['edge'],lw=.9,zorder=2)
    box(ax,e['sampling_front_z_mm']/1000-shift,
        (e['sampling_front_z_mm']+e['sampling_depth_mm'])/1000-shift,.410,2.790,
        facecolor=C['active'],edgecolor='none',zorder=3)
    # Projected obstructions only: detailed azimuthal board packing is omitted.
    for z in (3.25,3.75):
        box(ax,z-.05,z+.05,2.5833,2.7033,facecolor=C['support'],edgecolor='white',lw=.5,zorder=4)
    for z in (3.0,3.5):
        box(ax,z-.175,z+.175,2.5933,2.6733,facecolor='none',edgecolor=C['support'],
            hatch='////',lw=.5,zorder=4)
    ax.text(3.32,2.35,'LAr barrel\nsampling envelope',ha='center',va='center',fontsize=10,color='white')
    ax.text((f+back)/2,2.40,'LAr EC\nsampling',ha='center',va='center',fontsize=10,color='white',zorder=5)
    # Drawing-only centreline placement seeds, explicitly recorded in the receipt.
    start=3.300 if new else 4.170
    route=pipe(start,2.7353,3.029,.400,5.880,4.800)
    band(ax,route,.070,C['clear'],clearance=True)
    band(ax,route,.050,C['new'] if new else C['old'])
    ax.plot([3.0 if new else b_end,start],[2.7353,2.7353],
            color=C['new'] if new else C['old'],ls='--',lw=1.1,zorder=8)
    ax.plot(start,2.7353,'o',mfc='white',mec=C['new'] if new else C['old'],ms=4,zorder=9)
    if new:
        box(ax,3.0,4.0,2.6653,3.099,facecolor='#eadff1',alpha=.28,
            edgecolor=C['new'],ls='--',lw=1.1,zorder=5)
        callout(ax,'Proposed side neck\nPorts / boards / supports: redesign',
                (3.55,2.83),(2.88,3.55),C['new'])
    else:
        box(ax,b_end,f,2.6653,3.099,facecolor='none',edgecolor=C['old'],ls='--',lw=1,zorder=5)
        callout(ax,'Outward offset\nin front service gap',(4.48,2.87),(3.9,3.55),C['old'])
    callout(ax,'Straight outer bus\nR = 3.029 m',(5.15,3.029),(4.75,3.45))
    callout(ax,'Rear bend: R = 0.400 m\nRadial exit / handoff: R = 4.8 m',
            (6.28,4.8),(4.72,4.95))
    dimension(ax,b_end,f,2.04,f'{(f-b_end)*1000:.0f} mm front gap')
    dimension(ax,h_end,h_front,4.67,'500 mm radial-exit window')
    if shift:
        dimension(ax,back,h_front,2.10,'900 mm behind EC; radial exit still 500 mm')
        callout(ax,'Previous EC outline\n400 mm inward study only',
                (5.86,2.89),(5.02,2.64))
    ax.set(xlim=(2.70,6.75),ylim=(1.97,5.20),xlabel=r'$|z|$ [m]',ylabel=r'$R$ [m]')
    ax.set_aspect('equal',adjustable='box')
    ax.grid(alpha=.15,lw=.5);ax.set_axisbelow(True)
    return dict(s_bend_start_mm=start*1000,
        s_bend_end_mm=float(route[0][200])*1000,front_gap_mm=(f-b_end)*1000,
        endcap_back_mm=back*1000,radial_exit_window_mm=(h_front-h_end)*1000)


def save(fig,out,name):
    for ext in ('png','svg'):
        metadata={'Software':'nODD conceptual routing diagram'} if ext=='png' else {'Date':None,'Creator':'nODD conceptual routing diagram'}
        path=out/(name+'.'+ext)
        fig.savefig(path,dpi=190,metadata=metadata)
        if ext=='svg':
            # Matplotlib path lines carry trailing spaces; preserve XML/path meaning.
            path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=ROOT)
    p.add_argument('--source-revision',required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    revision=subprocess.check_output(['git','rev-parse',a.source_revision+'^{commit}'],cwd=a.repo,text=True).strip()
    if revision != '21d2f01f99156034f7a80257fa642f1c2a4d9548':
        p.error('Use the pinned PR142 proposal revision21d2f01f99156034f7a80257fa642f1c2a4d9548; changed source needs drawing review.')
    contents={name:subprocess.check_output(['git','show',revision+':'+name],cwd=a.repo) for name in FILES}
    b,e,s=[json.loads(contents[x]) for x in FILES[:3]]
    # These source-matched dimensions define this drawing, not a generic exporter.
    if (b['warm_half_z_mm'],e['warm_front_z_mm'],e['warm_back_z_mm'],
        s['external_route_radius_mm'],s['hcal_barrel_half_z_mm'],s['hcal_endcap_front_z_mm']) != (4100,4900,5860,3029,5860,6360):
        p.error('This drawing requires the documented PR142 baseline; review geometry changes before redrawing.')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'nodd-lar-routing-rz'})
    fig,axes=plt.subplots(1,2,figsize=(15.8,8.8))
    fig.subplots_adjust(left=.045,right=.985,bottom=.22,top=.87,wspace=.10)
    panels=[]
    for ax,new,title in zip(axes,(False,True),('A  Old routing hypothesis','B  Proposed side-neck routing')):
        panels.append(panel(ax,b,e,s,new=new));ax.set_title(title,loc='left',fontsize=14,pad=13)
    handles=[Patch(facecolor=C['active'],label='Sampling envelope'),Patch(facecolor=C['warm'],label='Warm package'),
             Patch(facecolor=C['hcal'],label='HCAL at face centre'),Patch(facecolor=C['support'],label='Support / board-row projections'),
             Line2D([],[],color=C['old'],lw=5,label='Old 100 mm jacket'),Line2D([],[],color=C['new'],lw=5,label='Proposed 100 mm jacket')]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,.075),ncol=3,frameon=False,fontsize=10)
    fig.suptitle('LAr service routing: isolate the route change at fixed detector positions',fontsize=17,y=.97)
    fig.text(.5,.025,'Positive-z outer-region detail, equal scale; opposite end mirrored. Dashed pipe edges add 20 mm clearance.\n'
             'Conceptual centreline seeds: no validated ports, bundle fit or endcap rear connections. HCAL corner radius is dotted.',
             fontsize=10,ha='center',va='bottom')
    save(fig,a.output,'routing-rz-comparison')
    fig,ax=plt.subplots(figsize=(11.8,8.5),layout='constrained')
    target=panel(ax,b,e,s,new=True,shift=.4)
    ax.set_title('C  Conditional 400 mm front-gap target',loc='left',fontsize=16,pad=16)
    fig.supxlabel('Separate geometry study: EC moves inward 400 mm; HCAL boundaries stay fixed.\n'
                  'Forward-collar conflict is off-screen and unresolved. This is not a validated layout or route.',fontsize=11)
    save(fig,a.output,'routing-rz-gap-target')
    receipt=dict(status='PROTOTYPE / conceptual RZ drawing; no route or engineering acceptance',
        source_revision=revision,source_sha256={k:hashlib.sha256(v).hexdigest() for k,v in contents.items()},
        drawing_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        matplotlib_version=matplotlib.__version__,numpy_version=np.__version__,
        drawing_choices=dict(old_s_bend_start_mm=4170,new_s_bend_start_mm=3300,
            rear_elbow_start_mm=5880,pipe_jacket_od_mm=100,clearance_mm=20,bend_radius_mm=400,
            external_handoff_radius_mm=4800,conditional_endcap_inward_shift_mm=400,
            classification='NODD DESIGN CHOICES / drawing seeds; not installed port coordinates'),
        panels=panels,conditional_target=target,
        limitations=['RZ outer-region crop, representative100mm barrel line; complete bundles omitted.',
                     'Closed vessel penetrations, endcap rear connections, headers and supports remain undefined.',
                     'Neck overlaps existing package/board space and requires redesign; no native overlap check.',
                     'HCAL shown at face centre with outer corner reference; azimuthal packing omitted.',
                     'Conditional shift is separate from routing comparison; forward collar off-screen.',
                     'No detector configuration, exported geometry or response result changed.'],
        outputs={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(a.output.glob('*.png'))+sorted(a.output.glob('*.svg'))})
    (a.output/'routing-rz.json').write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':main()
