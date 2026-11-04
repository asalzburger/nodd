"""Scientific native ECAL material/path plots, not response/efficiency."""
import argparse,json
from pathlib import Path
def plot(combined,endcap_expected,output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle,Polygon
    r=json.loads(combined.read_text());e=json.loads(endcap_expected.read_text());output.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(2,1,figsize=(10,8),sharex=True)
    for phi in sorted({x['phi_rad'] for x in r['material_rays']}):
        rows=sorted((x for x in r['material_rays'] if x['phi_rad']==phi),key=lambda x:x['eta'])
        axes[0].plot([x['eta'] for x in rows],[x['x_over_x0'] for x in rows],'.-',markersize=2,label=f'φ={phi:g}')
    rows=sorted((x for x in r['material_rays'] if x['phi_rad']==.37),key=lambda x:x['eta'])
    for key,label in [('active_barrel_path_mm','Barrel active LAr'),('active_endcap_path_mm','Endcap active LAr')]:
        axes[1].plot([x['eta'] for x in rows],[x[key] for x in rows],'.-',markersize=3,label=label)
    axes[0].set(ylabel='Whole ECAL package t/X₀');axes[0].legend(ncol=5)
    axes[1].set(ylabel='Active LAr path [mm] at φ=0.37',xlabel='η');axes[1].legend()
    for ax in axes:
        ax.grid(alpha=.25)
        for s in (-1,1):ax.axvspan(s*1.204,s*1.424,color='#d99737',alpha=.12)
    fig.suptitle('LAYOUT-002 · actual combined LAr ECAL-only native navigation\n405 fixed rays; shaded transition has partial depth · no tracker/magnet/HCAL/FCal or shower response')
    fig.tight_layout();fig.savefig(output/'ecal-material-paths.png',dpi=150);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,8))
    for radius in (400,410,764.260466660877,774.260466660877,1460.235153217131,1470.235153217131,2790,2800):
        ax.add_patch(Circle((0,0),radius,fill=False,edgecolor='#748094',linewidth=.8))
    for p in e['passive']:
        if p['role']!='cold_board_envelope' or not p['name'].startswith('ECFEB_1_1_'):continue
        d=p['dimensions_mm'];points=[]
        for x,y in ((-d['sx']/2,-d['sy']/2),(d['sx']/2,-d['sy']/2),(d['sx']/2,d['sy']/2),(-d['sx']/2,d['sy']/2)):
            points.append([p['center_mm'][i]+p['frame'][0][i]*x+p['frame'][1][i]*y for i in range(2)])
        ax.add_patch(Polygon(points,facecolor='#bf7f36',edgecolor='none'))
    ax.set(aspect='equal',xlim=(-2900,2900),ylim=(-2900,2900),xlabel='x [mm]',ylabel='y [mm]',title='Endcap rear bath · one of three physical board planes\n528 slots/plane · circles show wheel/support references at sampling depth')
    fig.tight_layout();fig.savefig(output/'endcap-board-packing.png',dpi=150);plt.close(fig)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--combined',type=Path,required=True);p.add_argument('--expected',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plot(a.combined,a.expected,a.output)
