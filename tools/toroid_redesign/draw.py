"""Deterministic SVG schematic and coverage chart; no plotting dependencies."""
from __future__ import annotations
import json
from pathlib import Path
from html import escape
import numpy as np
from tools.toroid_prototype.geometry import coil_mask
from tools.toroid_redesign.study import OUTPUT, crossings

COLORS = ['#cbd5e1', '#e7b060', '#68b4c7', '#1f866e']


def render(output=OUTPUT):
    config = json.loads((output/'configuration.json').read_text())
    report = json.loads((output/'results.json').read_text())
    a = ['<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1060" viewBox="0 0 1440 1060">',
         '<rect width="1440" height="1060" fill="#f8fafc"/>',
         '<style>text{font-family:Arial,sans-serif;fill:#173149} .title{font-size:28px;font-weight:bold}.sub{font-size:17px}.small{font-size:14px}.axis{stroke:#9aabba;stroke-width:1}</style>',
         '<text x="60" y="47" class="title">Separated toroids · schematic three-station muon proposal</text>',
         '<text x="60" y="77" class="sub">Issue #105 | DRAFT / PROTOTYPE | fixed 3 T solenoid | no engineering sign-off</text>']
    def text(x,y,value,cls='small',**attrs):
        att=' '.join(f'{k.replace("_", "-")}="{v}"' for k,v in attrs.items())
        a.append(f'<text x="{x:g}" y="{y:g}" class="{cls}" {att}>{escape(value)}</text>')
    def line(x,y,xx,yy,color,width=1):
        a.append(f'<line x1="{x:g}" y1="{y:g}" x2="{xx:g}" y2="{yy:g}" stroke="{color}" stroke-width="{width}"/>')
    def rect(x,y,w,h,color,opacity=1):
        a.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{color}" opacity="{opacity}"/>')
    # Two genuine meridional slices; raster membership is the exact sweep mask,
    # not an axial projection of all coils into one plane.
    for panel, angle in enumerate((0., 15.)):
        left, top, w, h = 70+panel*690, 142, 620, 365
        def xy(z,r): return left+(z+15)/30*w,top+h-r/9.6*h
        text(left,top-20,f'True R–Z slice at φ={angle:g}°','sub')
        def box(z1,z2,r1,r2,color,opacity=1):
            x,y=xy(z1,r2);rect(x,y,(z2-z1)*w/30,(r2-r1)*h/9.6,color,opacity)
        # Pinned HCAL envelope, central solenoid host.
        box(-4.4832,4.4832,2.6,4.23946,'#9aa6b3',.65)
        for sign in (-1,1):
            z1,z2=sorted([sign*4.8832,sign*6.4412]);box(z1,z2,.3,4.229264,'#9aa6b3',.65)
        box(-3.85,3.85,1.24,1.558656,'#8b78bd',.8)
        z = np.linspace(-15,15,601);r=np.linspace(0,9.6,193)
        zz,rr=np.meshgrid(z,r,indexing='ij');ph=np.radians(angle)
        p=np.column_stack((rr.ravel()*np.cos(ph),rr.ravel()*np.sin(ph),zz.ravel()))
        mask=coil_mask(p,config).reshape(zz.shape)
        # Merge consecutive radial raster cells into one rectangle.
        for i in range(len(z)-1):
            indices=np.flatnonzero(np.diff(np.r_[False,mask[i],False].astype(int)))
            for lo,hi in indices.reshape(-1,2):
                box(z[i],z[i+1],r[max(0,lo)],r[min(hi,len(r)-1)],'#a5acb5')
        s=config['stations'];hh=.25
        for i,(radius,length,depthz,outer) in enumerate(zip(s['barrel_radii_m'],s['barrel_half_lengths_m'],s['disk_abs_z_m'],s['disk_outer_radii_m'])):
            color=('#1f866e','#0673a2','#d07727')[i]
            # Clip every plotted local normal-depth fragment with the same
            # conservative depth mask as the acceptance study.
            from tools.toroid_prototype.geometry import chamber_depth_mask
            zs=np.linspace(-length,length,600)
            ps=np.column_stack((np.full(600,radius*np.cos(ph)),np.full(600,radius*np.sin(ph)),zs))
            ok=~chamber_depth_mask(ps,config,'barrel')
            for j in range(599):
                if ok[j] and ok[j+1]:box(zs[j],zs[j+1],radius-hh,radius+hh,color,.9)
            rs=np.linspace(s['disk_inner_radius_m'],outer,300)
            for sign in (-1,1):
                ps=np.column_stack((rs*np.cos(ph),rs*np.sin(ph),np.full(300,sign*depthz)))
                ok=~chamber_depth_mask(ps,config,'disk')
                for j in range(299):
                    if ok[j] and ok[j+1]:box(sign*depthz-hh,sign*depthz+hh,rs[j],rs[j+1],color,.9)
            x,y=xy(0,radius);text(x-10,y-12,f'S{i+1}')
        for tick in (-15,-10,-5,0,5,10,15):
            x,y=xy(tick,0);line(x,y,x,y+6,'#173149');text(x-11,y+23,str(tick))
        for tick in (0,2,4,6,8):
            x,y=xy(-15,tick);line(x-5,y,x,y,'#173149');text(x-25,y+5,str(tick))
        x,y=xy(-15,0);line(x,y,*xy(15,0),'#173149');line(x,y,*xy(-15,9.6),'#173149')
        text(left+w/2-20,top+h+47,'z [m]');text(left-41,top+16,'R [m]')
    text(70,575,'Grey: warm coil reservations + HCAL  |  Violet: retained solenoid  |  Green / blue / orange: S1 / S2 / S3')
    text(70,600,'BT warm end |z|=6.25 m; ECT warm front/rear |z|=7.05 / 13.55 m; family separation 0.80 m.','sub')
    # Refined eta/phi count heatmap.
    cov=report['coverage_refined'];counts=np.array(cov['station_count_eta_phi'])
    left,top,w,h=80,675,630,270
    text(left,top-30,'Local shell availability · retained 33,600-cell grid','sub')
    for i in range(counts.shape[0]):
        changes=np.r_[0,np.flatnonzero(np.diff(counts[i]))+1,counts.shape[1]]
        for j,end in zip(changes[:-1],changes[1:]):
            rect(left+j*w/counts.shape[1],top+h-(i+1)*h/counts.shape[0],(end-j)*w/counts.shape[1]+.1,h/counts.shape[0]+.1,COLORS[counts[i,j]])
    for tick in (0,5,10,15,20,25,30):text(left+tick/30*w-5,top+h+22,str(tick))
    for tick in (0,.5,1,1.5,2,2.5,3,3.5):text(left-35,top+h-tick/3.5*h+5,str(tick))
    text(left+w/2-20,top+h+45,'φ [degree]');text(left-40,top-10,'|η|')
    refinement=json.loads((output/'refinement.json').read_text())
    text(780,660,'Schematic results · denser 134,400-cell bank','sub')
    fine=refinement['nested_transition_chambers']['three_station'];short=refinement['short_barrel_chambers']['three_station']
    values=[f"Flat η/φ, |η|&lt;3.5: {100*fine['flat_eta_phi_fraction']:.2f}%",
            f"Solid angle, |η|&lt;3.5: {100*fine['conditional_solid_angle_fraction']:.2f}%",
            f"Short-chamber control: {100*short['conditional_solid_angle_fraction']:.2f}% solid angle",
            f"Barrel current: {report['normalization']['currents_Aturn']['barrel']/1e6:.3f} MA-turn / coil",
            f"Endcap current: {report['normalization']['currents_Aturn']['endcap_plus']/1e6:.3f} MA-turn / coil",
            f"Exterior samples: 3.50 T; higher-order subset 3.64 T"]
    for i,value in enumerate(values):text(780,700+i*32,value.replace('&lt;','<'))
    for i,color in enumerate(COLORS):rect(790+i*140,909,22,16,color);text(820+i*140,923,f'{i} stations')
    text(60,1003,'Continuous clipped shells are a coverage ceiling. Finite panels, borders, supports and services are not yet placed.','sub')
    text(60,1032,'Vacuum field only; conductor peak, nonlinear iron, cryostats, forces and muon reconstruction require subsequent review.','small')
    a.append('</svg>')
    (output/'schematic.svg').write_text('\n'.join(a)+'\n')


if __name__ == '__main__':
    render()
