"""DES038 face/inner-aperture/outline/core-plane figures from actual exports."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle

ROOT=Path(__file__).resolve().parents[2]


def polygon(a):
    radius=a/math.cos(math.pi/16)
    return [(radius*math.cos((2*i+1)*math.pi/16),radius*math.sin((2*i+1)*math.pi/16)) for i in range(16)]


def draw(directory,output):
    directory,output=Path(directory),Path(output);output.mkdir(parents=True,exist_ok=True)
    d=json.loads((directory/'summary.json').read_text());l=json.loads((directory/'layout.json').read_text());cv=json.loads((directory/'coverage.json').read_text())
    c,s=d['config'],d['summary'];plt.rcParams.update({'font.size':10,'svg.fonttype':'none','svg.hashsalt':'DES038'})
    fig,axes=plt.subplots(2,2,figsize=(15,11),constrained_layout=True)
    fig.suptitle('Endcap HCAL · intact common carriers · 14 TeV · DRAFT / PROTOTYPE',fontsize=19,weight='bold')
    a,b,z,m=axes.flat
    a.add_patch(Polygon(polygon(4148),fc='#edf0f0',ec='#435665',lw=1.4))
    for q in l['patterns']['adaptive']['carriers']:
        x,y=q['center_xy_mm']
        a.add_patch(Rectangle((x-190,y-120),380,240,fc='#b2d6cb',ec='#578778',lw=.35))
    a.add_patch(Polygon(polygon(310),fc='white',ec='#7f4d4d'))
    a.set(xlim=(-4400,4400),ylim=(-4400,4400),xlabel='x [mm]',ylabel='y [mm]',title='Phase 0 face: 472 whole carriers, empty route strips')
    a.set_aspect('equal');a.text(.02,.02,'Layer rotations: 0°, 22.5°, 45°, 67.5°\nSteel quarter joints and reservations rotate together.',transform=a.transAxes,fontsize=8,bbox=dict(fc='white',alpha=.9,ec='none'))
    for name,color,ls in [('uniform','#a9afb5','--'),('adaptive','#256c91','-')]:
        for q in l['patterns'][name]['carriers']:
            x,y=q['center_xy_mm']
            if abs(x)<1000 and abs(y)<1000:
                b.add_patch(Rectangle((x-190,y-120),380,240,fc='none',ec=color,ls=ls,lw=1.2))
                if name=='adaptive':
                    for mx in (-93,93):b.add_patch(Rectangle((x+mx-89.85,y-12-89.85),179.7,179.7,fc='#70b39f',ec='none',alpha=.65))
    b.add_patch(Polygon(polygon(310),fc='#f7e8e7',ec='#a15e5a',lw=1.1));b.add_patch(Polygon(polygon(300),fc='white',ec='#a15e5a',ls=':'))
    b.set(xlim=(-850,850),ylim=(-850,850),xlabel='x [mm]',ylabel='y [mm]',title='Inner repair: adaptive rows keep every board intact');b.set_aspect('equal')
    b.text(.02,.02,'Core radius: 418.10 → 328.60 mm\nBlue: adaptive; dashed grey: uniform control\nGreen tile fields retain micro gaps in the mask.',transform=b.transAxes,fontsize=8,bbox=dict(fc='white',alpha=.95,ec='none'))
    context=json.loads((ROOT/'docs/layouts/LAYOUT-001.json').read_text());h=context['hcal']
    z.add_patch(Rectangle((-h['barrel_half_length_m'],h['barrel_front_apothem_m']),2*h['barrel_half_length_m'],h['barrel_outer_apothem_m']-h['barrel_front_apothem_m'],fill=False,ec='#89949d',ls='--'))
    for sign in (-1,1):
        z.add_patch(Rectangle((4.8832 if sign>0 else -6.4412,.3),1.558,3.848,fc='#93c5d8',ec='#2c799a'))
        z.add_patch(Rectangle((4.8832 if sign>0 else -6.3791,.3),1.4959,3.7859,fill=False,ec='#b47849',ls='--',lw=1.4))
        z.add_patch(Rectangle((3.95 if sign>0 else -4.4832,.3),.5332,1.9232,fc='#edc77e',ec='none'))
        z.add_patch(Rectangle((4.5332 if sign>0 else -6.3791,.08),1.8459,.21,fc='#efb8c0',ec='#b75766',lw=.5))
    z.set(xlim=(-6.8,6.8),ylim=(0,4.5),xlabel='z [m]',ylabel='Face-centre apothem [m]',title='Endcap amendment; barrel remains companion outline')
    z.text(.02,.03,'Blue: proposal; brown dashed: DES034\nPink: unchanged empty FCal reservation',transform=z.transAxes,fontsize=8,bbox=dict(fc='white',alpha=.9,ec='none'));z.grid(alpha=.15)
    for name,color,label in [('staggered','#237ca3','Selected staggered mean'),('adaptive','#c1873e','Aligned adaptive mean'),('uniform','#949a9d','Uniform mean')]:
        rows=[r for r in cv['rows'] if r['scenario']==name]
        m.plot([r['eta'] for r in rows],[r['mean'] for r in rows],color=color,label=label,lw=1.6)
        if name=='staggered':m.fill_between([r['eta'] for r in rows],[r['minimum'] for r in rows],[r['maximum'] for r in rows],color=color,alpha=.13,label='Selected minimum–maximum')
    m.set(xlim=(.9,4.1),ylim=(0,37),xlabel='|η| from IP',ylabel='Core-plane crossings / 36',title='720 φ probes · residual forward gaps remain')
    m.legend(fontsize=8,loc='upper right');m.grid(alpha=.15)
    fig.supxlabel(f"Both ends: {s['tiles']:,} tiles · partial mass {s['mass_g']/1e6:,.1f} t · nominal local heat {s['power_scenarios'][0]['total_heat_W']/1000:.1f} kW\n"
                  '55.03% full-face core area · no η = 4 HCAL core crossings · collectors, loads and response unqualified',fontsize=10)
    for suffix in ('svg','png'):fig.savefig(output/('endcap-design.'+suffix),dpi=170,metadata={'Date':None} if suffix=='svg' else {})
    plt.close(fig)
    p=output/'endcap-design.svg';p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')
    sources=[directory/'summary.json',directory/'layout.json',directory/'coverage.json',ROOT/'docs/layouts/LAYOUT-001.json',Path(__file__)]
    (output/'inputs.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},indent=2)+'\n')
    print('Rendered DES038 drawing')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();draw(a.directory,a.output)
