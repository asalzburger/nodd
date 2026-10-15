"""Scientific design drawings from actual DES037 layout and mask exports."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

ROOT=Path(__file__).resolve().parents[2]


def draw(directory,output):
    directory,output=Path(directory),Path(output);output.mkdir(parents=True,exist_ok=True)
    d=json.loads((directory/"summary.json").read_text());v=json.loads((directory/"coverage.json").read_text())
    c=d["config"];s=d["summary"];t=math.tan(math.pi/16)
    plt.rcParams.update({"font.size":10,"svg.fonttype":"none","svg.hashsalt":"DES037"})
    fig,axes=plt.subplots(2,2,figsize=(15,10),constrained_layout=True)
    fig.suptitle("Barrel HCAL · common-module design · 14 TeV · DRAFT / PROTOTYPE",fontsize=19,weight="bold")
    a,b,z,m=axes.flat
    for layer in d['layers']:
        r=layer['steel_front_mm'];front=layer['carrier_front_mm'];e=c['edge_rail_mm']+c['sector_half_seam_mm']
        a.add_patch(Polygon([(r/1000,(-r*t+e)/1000),(front/1000,(-front*t+e)/1000),
                             (front/1000,(front*t-e)/1000),(r/1000,(r*t-e)/1000)],fc='#b99b78',ec='none',alpha=.55))
        for x in layer['columns_mm']:
            a.add_patch(Rectangle((front/1000,(x+layer['tangent_phase_mm']-190)/1000),.012,.380,
                                  fc='#3e8eac',ec='#28647b',lw=.4))
    a.set(xlim=(2.57,4.19),ylim=(-.88,.88),xlabel='Face-normal radius [m]',ylabel='Tangential coordinate [m]',
          title='One sector: steel and complete carrier envelopes')
    a.text(.03,.97,'36 × (30 mm steel + 12 mm carrier + 1 mm gap)\n10 mm rear cover · actual phases bounded to fit',
           transform=a.transAxes,va='top',fontsize=9,bbox=dict(fc='white',alpha=.9,ec='none'))
    layer=d['layers'][0]
    for y in layer['rows_mm']:
        for x in layer['columns_mm']:
            cx=x+layer['tangent_phase_mm'];cy=y+layer['axial_phase_mm']
            b.add_patch(Rectangle(((cy-120)/1000,(cx-190)/1000),.240,.380,fc='#d5e7ee',ec='#63808c',lw=.4))
            for mx in (-93,93):
                b.add_patch(Rectangle(((cy-12-89.85)/1000,(cx+mx-89.85)/1000),.1797,.1797,
                                      fc='#6bad98',ec='none'))
    b.axvline(0,color='#b25050',lw=.8,ls='--')
    b.set(xlim=(-4.5,4.5),ylim=(-.65,.65),xlabel='Axial z [m]',ylabel='Tangential coordinate [m]',
          title='Layer 0: 33 rows, 20 mm empty collector strips')
    b.text(.02,.03,'Green: projected tile fields; individual 0.3 mm tile gaps are in the mask.\nFixed sector-edge losses remain; no sheet fills them.',
           transform=b.transAxes,fontsize=9,bbox=dict(fc='white',alpha=.9,ec='none'))
    context=json.loads((ROOT/'docs/layouts/LAYOUT-001.json').read_text());h=context['hcal'];e=context['ecal']
    z.add_patch(Rectangle((-4.4832,2.6),8.9664,1.558,fc='#8ebed3',ec='#246c8e',label='Barrel proposal'))
    z.add_patch(Rectangle((-4.4832,2.6),8.9664,1.4959,fill=False,ec='#9c6645',ls='--',lw=1.5,label='DES034 outline'))
    z.add_patch(Rectangle((-e['barrel_flange_half_length_m'],e['barrel_front_apothem_m']),2*e['barrel_flange_half_length_m'],
                          e['barrel_outer_apothem_m']-e['barrel_front_apothem_m'],fc='#efc876',ec='none'))
    for sign in (-1,1):
        lo,hi=h['endcap_front_abs_z_m'],h['endcap_back_abs_z_m']
        z.add_patch(Rectangle((lo if sign>0 else -hi,.3),hi-lo,h['endcap_outer_apothem_m']-.3,
                              fill=False,ec='#879198',ls='--'))
        z.add_patch(Rectangle((3.95 if sign>0 else -4.4832,.3),.5332,1.9232,fc='#efc876',ec='none'))
        z.add_patch(Rectangle((4.5332 if sign>0 else -6.3791,.08),1.8459,.21,fc='#f2b7bd',ec='#b65760',lw=.5))
    z.set(xlim=(-6.7,6.7),ylim=(0,4.5),xlabel='z [m]',ylabel='Face-centre apothem [m]',title='R–Z context: companion endcaps remain an outline')
    z.legend(loc='upper center',fontsize=8);z.grid(alpha=.15)
    for scenario,color,label in [('staggered','#237ca3','Selected mean'),('aligned_zero','#ba7d35','Aligned-zero mean'),
                                 ('aligned_midplane_gap','#8b8f96','Adverse +130 mm mean')]:
        rows=[r for r in v['rows'] if r['scenario']==scenario]
        m.plot([r['eta'] for r in rows],[r['mean'] for r in rows],color=color,label=label,lw=1.6)
        if scenario=='staggered':
            m.fill_between([r['eta'] for r in rows],[r['p10'] for r in rows],[r['maximum'] for r in rows],color=color,alpha=.12,label='Selected p10–maximum')
    m.set(xlim=(-1.5,1.5),ylim=(0,37),xlabel='Signed η from IP',ylabel='Core-plane crossings / 36',
          title='Actual tile-plane masks; 720 uniform φ probes')
    m.legend(fontsize=8,loc='upper right');m.grid(alpha=.15)
    fig.supxlabel(f"{s['tiles']:,} tiles · partial mass {s['material_mass_g']/1e6:,.1f} t · nominal local heat {d['services']['power_scenarios'][0]['total_heat_W']/1000:.1f} kW\n"
                  '62.1 mm outline amendment · collectors/loads/response unqualified · no combined detector acceptance',fontsize=10)
    for suffix in ('svg','png'):
        fig.savefig(output/('barrel-design.'+suffix),dpi=170,metadata={'Date':None} if suffix=='svg' else {})
    plt.close(fig)
    p=output/'barrel-design.svg';p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')
    sources=[directory/'summary.json',directory/'coverage.json',ROOT/'docs/layouts/LAYOUT-001.json',Path(__file__)]
    (output/'inputs.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},indent=2)+'\n')
    print('Rendered DES037 drawing')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();draw(a.directory,a.output)
