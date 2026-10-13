"""Native material rays and drawn physical transverse support/board geometry."""
import argparse
import json
from pathlib import Path
from barrel_geometry import ROOT
def plot(native,expected,output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle,Polygon
    r=json.loads(native.read_text());e=json.loads(expected.read_text());output.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(2,1,figsize=(9,7),sharex=True)
    for phi in sorted({x['phi_rad'] for x in r['material_rays']}):
        rows=sorted((x for x in r['material_rays'] if x['phi_rad']==phi),key=lambda x:x['eta'])
        axes[0].plot([x['eta'] for x in rows],[x['x_over_x0'] for x in rows],'.-',label=f'φ={phi:.4g}')
        axes[1].plot([x['eta'] for x in rows],[x['active_LAr_path_mm'] for x in rows],'.-')
    axes[0].set(ylabel='Whole package t/X₀');axes[0].legend(ncol=3)
    axes[1].set(ylabel='Active LAr path [mm]',xlabel='η')
    for ax in axes:ax.grid(alpha=.25)
    fig.suptitle('LAYOUT-002 · native isolated LAr barrel PROTOTYPE\n45 sparse fixed rays; no angular average, shower response or combined detector')
    fig.tight_layout();fig.savefig(output/'barrel-material.png',dpi=150);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,8))
    for radius in (2172.8,2578.3,2583.3,2703.3,2748.3,2830,3130):
        ax.add_patch(Circle((0,0),radius,fill=False,edgecolor='#748094',linewidth=1))
    for p in e['passive']:
        if p['role']=='cold_board_envelope' and p['parent_name']=='rear_bath' and p['name'].endswith('_7'):
            d=p['dimensions_mm'];verts=[]
            for x,y in ((-d['sx']/2,-d['sy']/2),(d['sx']/2,-d['sy']/2),(d['sx']/2,d['sy']/2),(-d['sx']/2,d['sy']/2)):
                verts.append([p['center_mm'][i]+p['frame'][0][i]*x+p['frame'][1][i]*y for i in range(2)])
            ax.add_patch(Polygon(verts,facecolor='#bd7b38',edgecolor='none'))
        if p['role']=='cooling_wall' and p['name'].startswith('N2wall_1_'):
            ax.add_patch(Circle(p['center_mm'][:2],10,color='#247fa3'))
    ax.set(aspect='equal',xlim=(-3200,3200),ylim=(-3200,3200),xlabel='x [mm]',ylabel='y [mm]')
    ax.set_title('Physical rear-bath slice between H-rings\nTwo flat CFEB banks, outer N₂ lane, cryostat and HCAL front reservation')
    fig.tight_layout();fig.savefig(output/'barrel-service-packing.png',dpi=150);plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--expected',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plot(a.native,a.expected,a.output)
