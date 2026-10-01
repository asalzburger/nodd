#!/usr/bin/env python3
"""Dimensioned module and stave sheets from the generated DD4hep compact."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle


def val(node,key):return float(node.get(key).split('*')[0])

def save(fig,output,name):
    for ext in ('svg','pdf','png'):
        metadata={'Date':None} if ext=='svg' else ({'CreationDate':None,'ModDate':None} if ext=='pdf' else {})
        fig.savefig(output/(name+'.'+ext),dpi=180,metadata=metadata)
    plt.close(fig)


def dimension(ax,a,b,label,offset=(0,0)):
    ax.annotate('',a,b,arrowprops=dict(arrowstyle='<->',lw=.8,color='#263238'))
    ax.text((a[0]+b[0])/2+offset[0],(a[1]+b[1])/2+offset[1],label,ha='center',va='bottom',fontsize=9)


def draw(compact,output):
    output.mkdir(parents=True,exist_ok=True)
    expected=json.loads(compact.with_name('expected.json').read_text())
    manifest=json.loads(compact.with_name('manifest.json').read_text())
    if hashlib.sha256(compact.read_bytes()).hexdigest()!=manifest['artifacts_sha256']['pixel-barrel.xml']:
        raise ValueError('Compact differs from export manifest')
    root=ET.parse(compact).getroot()
    plt.rcParams.update({'font.size':10,'svg.fonttype':'none','svg.hashsalt':'DES012-PR34','pdf.fonttype':42})
    colours=dict(Silicon='#57b8a9',Graphite='#74868c',Epoxy='#d7b6df',Polyimide='#ecc96b',PatternedCopper='#d68b45',CFRP='#384850',FoamGlue='#e6d5aa',Titanium='#889ca8',CO2='#5eaed0')
    cases=[('single',root.find('.//layer[@id="1"]/stave')),('quad',root.find('.//layer[@id="3"]/stave'))]
    for family,stave in cases:
        module=min(stave.findall('module'),key=lambda m:abs(val(m,'z')))
        sensor=module.find('sensor');su,sv=val(sensor,'width'),val(sensor,'length');uc,vc=val(sensor,'u'),val(sensor,'v')
        fig=plt.figure(figsize=(14,10));face=fig.add_axes([.07,.30,.39,.57]);stack=fig.add_axes([.54,.58,.40,.27])
        face.add_patch(Rectangle((uc-su/2,vc-sv/2),su,sv,fc='#edf1f3',ec='#1b587b',lw=1.5))
        for die in module.findall('die'):
            face.add_patch(Rectangle((val(die,'u')-val(die,'width')/2,val(die,'v')-val(die,'length')/2),val(die,'width'),val(die,'length'),fc='#ebb66e',ec='#986720',alpha=.8))
        face.add_patch(Rectangle((uc-su/2,vc-sv/2),su,sv,fill=False,ec='#1b587b',lw=1.5))
        for p in sensor.findall('patch'):
            u,v=uc+val(p,'u'),vc+val(p,'v');w,l=val(p,'width'),val(p,'length')
            face.add_patch(Rectangle((u-w/2,v-l/2),w,l,fc=colours['Silicon'],ec='#236c62',lw=.8))
            face.text(u,v,f"{round(w/val(root.find('.//segmentation'),'grid_size_x'))} × {round(l/val(root.find('.//segmentation'),'grid_size_y'))}\n{w:g} × {l:g} mm",ha='center',va='center',fontsize=9)
        dimension(face,(uc-su/2,vc-sv/2-2),(uc+su/2,vc-sv/2-2),f'{su:g} mm sensor φ width',offset=(0,-2.3))
        dimension(face,(uc+su/2+2,vc-sv/2),(uc+su/2+2,vc+sv/2),f'{sv:g} mm',offset=(3,0))
        face.set(xlim=(uc-su/2-4,uc+su/2+8),ylim=(vc-sv/2-7,vc+sv/2+3),xlabel='Local u / tangential [mm]',ylabel='Local v / beam z [mm]',title='Sensor face and underlying ASIC footprints')
        face.set_aspect('equal');face.grid(alpha=.15)
        cut=val(sensor.findall('patch')[0],'v')+vc
        stack.add_patch(Rectangle((uc-su/2,-val(sensor,'thickness')/2),su,val(sensor,'thickness'),fc=colours['Silicon'],ec='none'))
        for tag in ('die','passive'):
            for p in module.findall(tag):
                if abs(val(p,'v')-cut)<=val(p,'length')/2:
                    stack.add_patch(Rectangle((val(p,'u')-val(p,'width')/2,val(p,'w')-val(p,'thickness')/2),val(p,'width'),val(p,'thickness'),fc=colours[p.get('material')],ec='none'))
        for p in list(stave.findall('slab'))+list(stave.findall('core')):
            w,t=val(p,'width'),val(p,'thickness')
            stack.add_patch(Rectangle((-w/2,val(p,'w')-t/2),w,t,fc=colours['FoamGlue' if p.tag=='core' else p.get('material')],ec='none'))
            if p.tag=='core':
                for sign in (-1,1):
                    stack.add_patch(Circle((sign*val(p,'tube_offset'),val(p,'w')),val(p,'tube_outer'),fc=colours['Titanium'],ec='#263238',lw=.4))
                    stack.add_patch(Circle((sign*val(p,'tube_offset'),val(p,'w')),val(p,'tube_inner'),fc=colours['CO2'],ec='none'))
        stack.set(xlim=(-su/2-3,su/2+3),ylim=(-.8,6),xlabel='Local u [mm]',ylabel='Local w / outward r [mm]',title=f'Actual stack section at local v = {cut:g} mm')
        stack.set_aspect('equal');stack.grid(alpha=.15)
        patches=sensor.findall('patch');asic=module.find('die');contact=next(p for p in module.findall('passive') if p.get('name').startswith('contact'))
        active_u=max(val(p,'u')+val(p,'width')/2 for p in patches)-min(val(p,'u')-val(p,'width')/2 for p in patches)
        active_v=max(val(p,'v')+val(p,'length')/2 for p in patches)-min(val(p,'v')-val(p,'length')/2 for p in patches)
        gu,gv=(su-active_u)/2,(sv-active_v)/2
        periphery=val(asic,'width')-val(patches[0],'width')
        bump=val(asic,'w')-val(asic,'thickness')/2-val(sensor,'thickness')/2
        text=(f"Selected PR34 {family} module · {len(patches)} ASIC{'s' if len(patches)>1 else ''}\n"
              f"Sensor: {su:g} × {sv:g} × {val(sensor,'thickness'):g} mm\n"
              f"ASIC footprint: {val(asic,'width'):g} φ × {val(asic,'length'):g} z mm\n"
              f"ASIC thickness: {val(asic,'thickness'):g} mm; bump standoff: {bump:.3f} mm\n"
              f"Graphite contact: {val(contact,'thickness'):g} mm\n"
              f"Sensor z guard: {gv:.3f} mm per edge; φ guard: {gu:.3f} mm\n"
              f"ASIC peripheral allowance: {periphery:.3f} mm on outer φ edge(s)\n"
              f"Exposed die ledge beyond sensor: {periphery-gu:.3f} mm (approximate model)\n"
              "Front flex: epoxy / patterned Cu / polyimide / patterned Cu.\n"
              "Outward support: interface / insulation / graphite / CFRP /\n"
              "foam+glue with two Ti/CO₂ tubes / CFRP.\n\n"
              "Orange: die footprint; green: active matrix; blue outline: sensor.\n"
              "Bond loops, pads and local pickup connections remain unresolved.\n"
              "No wire bonding or fastening allowance is placed at the z ends.")
        fig.text(.54,.46,text,va='top',fontsize=10,linespacing=1.5)
        fig.suptitle(f'Pixel barrel baseline — {family} module\nTransverse readout periphery; minimum inactive z edges',fontsize=17,y=.97)
        fig.text(.07,.075,'DES012 / DES013 · PROTOTYPE technical layout; dimensions in mm, not manufacturing tolerances.\nSensor faces beam; ASICs and local support are outward. Drawn from the generated DD4hep compact.',fontsize=10)
        save(fig,output,'module-'+family)
    fig,axes=plt.subplots(4,1,figsize=(15,10),sharex=True)
    fig.subplots_adjust(left=.10,right=.97,bottom=.12,top=.90,hspace=.45)
    for layer,ax in zip(root.findall('.//detector/layer'),axes):
        stave=layer.find('stave');ms=stave.findall('module');sensor=ms[0].find('sensor');half=val(sensor,'width')/2
        support=stave.find('slab');length=val(stave,'length');cy=val(support,'center_y')
        ax.add_patch(Rectangle((cy-length/2,-half-1),length,2*half+2,fc='#deddd8',ec='#6b747b',lw=.6))
        for ring in layer.findall('ring'):
            z=val(ring,'z');t=val(ring,'length');ax.axvspan(z-t/2,z+t/2,color='#9575b5',alpha=.35)
        for m in ms:
            z=val(m,'z');s=m.find('sensor');sv,su=val(s,'length'),val(s,'width');vc,uc=val(s,'v'),val(s,'u')
            ax.add_patch(Rectangle((z+vc-sv/2,uc-su/2),sv,su,fc='#c2ced4',ec='#8196a4',lw=.2))
            for p in s.findall('patch'):
                v,u=z+vc+val(p,'v'),uc+val(p,'u');w,l=val(p,'width'),val(p,'length')
                ax.add_patch(Rectangle((v-l/2,u-w/2),l,w,fc='#57b8a9',ec='none'))
        positions=sorted(val(m,'z') for m in ms);pitch=positions[1]-positions[0]
        ax.set_title(f"B{layer.get('id')} · {len(ms)} rows/stave · pitch {pitch:g} mm · passive support [{cy-length/2:.1f}, {cy+length/2:.1f}] mm",loc='left',fontsize=11)
        ax.set_ylabel('u [mm]');ax.set_ylim(-half-3,half+3);ax.grid(alpha=.15)
    axes[-1].set_xlim(-565,565);axes[-1].set_xlabel('Global z [mm] · longitudinal scale compressed relative to transverse width')
    fig.suptitle('Pixel barrel baseline — stave packing and retained mounting span',fontsize=17)
    fig.text(.10,.035,'Green: active silicon; grey: sensor edges/seams; beige: continuous support; purple: ring stations.\nSee z-gap-detail for dimensioned sensor edges and assembly clearance. No z-end bonding allowance is included.',fontsize=10)
    save(fig,output,'stave-packing')
    fig,axes=plt.subplots(1,2,figsize=(13,5))
    for (family,stave),ax in zip(cases,axes):
        modules=sorted(stave.findall('module'),key=lambda m:val(m,'z'))
        a,b=modules[len(modules)//2:len(modules)//2+2]
        sa,sb=a.find('sensor'),b.find('sensor')
        end_a=val(a,'z')+val(sa,'v')+val(sa,'length')/2
        start_b=val(b,'z')+val(sb,'v')-val(sb,'length')/2
        active_a=val(a,'z')+val(sa,'v')+max(val(p,'v')+val(p,'length')/2 for p in sa.findall('patch'))
        active_b=val(b,'z')+val(sb,'v')+min(val(p,'v')-val(p,'length')/2 for p in sb.findall('patch'))
        points=[active_a,end_a,start_b,active_b];origin=(end_a+start_b)/2
        x=[p-origin for p in points]
        ax.add_patch(Rectangle((-1,0),x[1]+1,1,fc='#c2ced4'))
        ax.add_patch(Rectangle((x[2],0),1-x[2],1,fc='#c2ced4'))
        ax.add_patch(Rectangle((-1,0),x[0]+1,1,fc='#57b8a9'))
        ax.add_patch(Rectangle((x[3],0),1-x[3],1,fc='#57b8a9'))
        for i,label in enumerate(['guard','gap','guard']):
            dimension(ax,(x[i],1.15),(x[i+1],1.15),f'{x[i+1]-x[i]:.3f} mm\n{label}',offset=(0,.1))
        dimension(ax,(x[0],-.3),(x[3],-.3),f'{x[3]-x[0]:.3f} mm active gap',offset=(0,-.35))
        ax.set(xlim=(-.7,.7),ylim=(-.8,2),xlabel='z relative to seam centre [mm]',title=family.capitalize()+' module joint',yticks=[])
        ax.grid(axis='x',alpha=.15)
    fig.suptitle('PR34 pixel barrel — longitudinal joint detail',fontsize=16)
    fig.text(.1,.015,'Dimensions from DD4hep sensor/active bounds. Guards and gap require sensor-process and assembly qualification.',fontsize=10)
    fig.tight_layout(rect=(0,.07,1,.94))
    save(fig,output,'z-gap-detail')
    write=dict(status='PROTOTYPE technical layout drawings, not manufacturing drawings',compact_sha256=hashlib.sha256(compact.read_bytes()).hexdigest(),
               expected_sha256=hashlib.sha256(compact.with_name('expected.json').read_bytes()).hexdigest(),
               producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),matplotlib=matplotlib.__version__,
               artifacts_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir()) if p.suffix in ('.svg','.pdf','.png')})
    (output/'manifest.json').write_text(json.dumps(write,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--compact',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();draw(a.compact,a.output)
