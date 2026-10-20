"""RZ/sector drawings and native calorimeter material scans."""
import argparse,json,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon
from assembly import inventory

def plot(out,native=None):
    report,_=inventory();fig,(a,b)=plt.subplots(1,2,figsize=(14,6),layout='constrained');colors={'ecal':'#d59a3a','hcal':'#538ca1'}
    for r in report['regions']:
        color=colors[r['unit']];cfg=report['config'];depth=r['stack_depth_mm']
        if r['kind']=='barrel':
            a.add_patch(Rectangle((-cfg['barrel_half_z_mm']/1000,r['front_mm']/1000),2*cfg['barrel_half_z_mm']/1000,depth/1000,facecolor=color,alpha=.85,label=r['unit'].upper()))
        else:
            for sign in (-1,1):
                lo=sign*(r['front_mm']+(depth if sign<0 else 0))/1000
                a.add_patch(Rectangle((lo,cfg['endcap_inner_apothem_mm']/1000),depth/1000,(r['outer_apothem_mm']-cfg['endcap_inner_apothem_mm'])/1000,facecolor=color,alpha=.85))
    for box,label,color in [((-3.6,0,7.2,1.2),'Tracker planning envelope','#999999'),((-3.85,1.24,7.7,.319),'PR64 conditional solenoid','#826da1')]:
        a.add_patch(Rectangle(box[:2],box[2],box[3],facecolor='none',edgecolor=color,ls='--',lw=1.3,label=label))
    a.set(xlim=(-6.3,6.3),ylim=(0,4.1),xlabel='z [m]',ylabel='sector apothem [m]',title='Complete barrel and both endcap stacks\nSupports add10–20 mm outside the shown sampling stacks')
    a.legend(fontsize=8,loc='upper left');a.grid(alpha=.2)
    r=next(r for r in report['regions'] if r['name']=='ecal_endcap');u=next(u for u in report['units'] if u['name']=='ecal')
    for p in r['parts']:
        if p['role']=='absorber' and not p['name'].endswith('absorber0'):continue
        b.add_patch(Polygon([[y/1000,x/1000] for x,y in p['vertices_mm']],facecolor='#e4c797' if p['role']=='absorber' else '#777777',edgecolor='white',lw=.5))
    for p in r['placements']:
        if p['layer']!=0:continue
        radial,tangent,_=p['center_mm'];b.add_patch(Rectangle(((tangent-u['width_mm']/2)/1000,(radial-u['height_mm']/2)/1000),u['width_mm']/1000,u['height_mm']/1000,facecolor='#458766',edgecolor='white',lw=.6))
    b.set(xlabel='tangent [m]',ylabel='radial [m]',title='One ECAL endcap sector, first layer\nCassette footprints; active silicon occupies31.9% of plate area');b.set_aspect('equal');b.set(xlim=(-.5,.5),ylim=(.25,2.3));b.grid(alpha=.2)
    fig.suptitle('DES029 · complete calorimeter assembly PROTOTYPE\nUniform cassette packing, continuous power and structural dimensions remain under review',fontsize=12)
    out.mkdir(parents=True,exist_ok=True);save(fig,out/'assemblies');plt.close(fig)
    if native:
        rays=json.loads(native.read_text())['material_rays'];fig,axes=plt.subplots(2,1,figsize=(10,7),sharex=True,layout='constrained')
        phis=sorted({r['phi'] for r in rays})
        for phi in phis:
            sample=sorted((r for r in rays if r['eta']>=0 and r['phi']==phi),key=lambda r:r['eta']);x=[r['eta'] for r in sample]
            for ax,key in zip(axes,('x_over_x0','l_over_lambda')):ax.plot(x,[r[key] for r in sample],'-o',ms=4,label=f'φ={phi:.4f} rad')
        axes[0].set(ylabel='Whole calorimeter t/X₀',title='Actual ROOT boundary navigation from the IP\nSparse fixed-φ paths expose sector frames and module gaps; no averaging or shower response')
        axes[1].set(ylabel='Whole calorimeter t/λI',xlabel='η');axes[0].legend();fig.suptitle('DES029 · native material scan · DRAFT prototype')
        for ax in axes:ax.grid(alpha=.2)
        save(fig,out/'material');plt.close(fig)

def save(fig,p):
    plt.rcParams['svg.hashsalt']='DES029';fig.savefig(p.with_suffix('.png'),dpi=170);fig.savefig(p.with_suffix('.svg'),metadata={'Date':None});q=p.with_suffix('.svg');q.write_text('\n'.join(s.rstrip() for s in q.read_text().splitlines())+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--native',type=Path);a=p.parse_args();plot(a.output,a.native)
