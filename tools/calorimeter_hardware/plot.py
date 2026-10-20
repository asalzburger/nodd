"""Publication figure from the same cassette inventory (existing matplotlib)."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from model import build,extent

COLORS={'sensitive':'#3a9d75','sensor_edge':'#9ccba9','absorber':'#666b78','skin':'#acb2bc','frame':'#687786','pcb':'#bd8952','interface':'#d59d61','readout':'#6062ad','sipm':'#6062ad','spreader':'#cd7945','thermal_pad':'#403c45','thermal_post':'#b0b4bd','pipe':'#277aa0','coolant':'#2eaada'}
def plot(out):
    data,_=build();fig,axes=plt.subplots(2,2,figsize=(12,9),layout='constrained')
    for row,u in enumerate(data['units']):
        a,b=axes[row]
        for p in u['parts']:
            dims=extent(p['shape_kind'],p['dimensions_mm']);ext=[sum(abs(p['frame'][i][j])*dims[i] for i in range(3)) for j in range(3)]
            x,y,z=p['center_mm'];color=COLORS.get(p['role'],'#b4b4b4')
            # Plan shows the sensor/tile face, frame and service allocation;
            # behind-face boards/cold plate are omitted for readability.
            if p['role'] in ('sensitive','sensor_edge','frame','interface','pipe'):
                a.add_patch(Rectangle((x-ext[0],y-ext[1]),2*ext[0],2*ext[1],facecolor=color,edgecolor='white',lw=.3,alpha=.85))
            # Bounding projection of parts; Boolean recess/guard contours are
            # shown by the readout face, not claimed as hidden engineering CAD.
            slice_y=-67.5 if u['name']=='ecal' else -89.8
            if p['role']!='sensor_edge' and abs(y-slice_y)<=ext[1]:
                b.add_patch(Rectangle((x-ext[0],z-ext[2]),2*ext[0],2*ext[2],facecolor=color,edgecolor='white',lw=.25,alpha=.6))
        a.set(xlim=(-u['width_mm']/2-5,u['width_mm']/2+5),ylim=(-u['height_mm']/2-5,u['height_mm']/2+5),xlabel='x [mm]',ylabel='y [mm]',title=f"{u['name'].upper()} cassette face: {u['channels']:,} channels")
        a.set_aspect('equal');b.set(xlim=a.get_xlim(),ylim=(-u['absorber_mm']-1 if u['name']=='ecal' else -1,u['body_depth_mm']+1),xlabel='x [mm]',ylabel='depth z [mm]',title=f'Local x–z section at y={slice_y:g} mm (depth expanded)')
        b.text(.02,.98,f"Body {u['body_depth_mm']:g} mm · cassette {u['cassette_mass_g']/1000:.3f} kg\nSector absorber {u['absorber_mm']:g} mm · heat {u['power']['total_heat_W']:.2f} W",transform=b.transAxes,va='top',fontsize=9,bbox=dict(facecolor='white',alpha=.85,edgecolor='none'))
    fig.suptitle('DES028 · ECAL and HCAL physical cassette prototypes\nDRAFT dimensions and continuous-power hypotheses; no fabrication or performance acceptance',fontsize=13)
    handles=[Rectangle((0,0),1,1,color=COLORS[k]) for k in ('sensitive','pcb','readout','spreader','pipe','absorber')]
    fig.legend(handles,['Sensor / tile','PCB / interface','Readout package','Copper spreader','Titanium / water','Sector absorber'],loc='outside lower center',ncol=6)
    out.mkdir(parents=True,exist_ok=True);plt.rcParams['svg.hashsalt']='DES028'
    fig.savefig(out/'cassettes.png',dpi=180);fig.savefig(out/'cassettes.svg',metadata={'Date':None});plt.close(fig)
    p=out/'cassettes.svg';p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);plot(p.parse_args().output)
