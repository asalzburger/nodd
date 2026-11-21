"""Annotate existing compact-layout service allocations without changing geometry."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

import draw_rz

ROOT=Path(__file__).resolve().parents[2]
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def capture():
    path=ROOT/'docs/layouts/LAYOUT-002-HCAL-compact-proposal.json'
    d=json.loads(path.read_text())
    if d['proposal']['id']!='HCAL-AXIAL-COMPACT-ALLOW80':
        raise ValueError('Need the screened compact proposal')
    screen=json.loads((ROOT/d['source']['screen_path']).read_text())
    if sha(ROOT/d['source']['screen_path'])!=d['source']['screen_sha256']:
        raise ValueError('Changed compaction screen')
    for source,wanted in screen['source_sha256'].items():
        if sha(ROOT/source)!=wanted:
            raise ValueError('Changed service/geometry source: '+source)
    b,e,h,r=(d[k] for k in ('barrel','endcaps','hcal','route_reservation'))
    gap_b=h['front_mm']-b['outer_radius_mm'];gap_e=h['front_mm']-e['warm_outer_radius_mm']
    rear=h['endcap_front_mm']-e['warm_back_z_mm'];offset=h['half_z_mm']-e['warm_back_z_mm']
    exit_width=h['endcap_front_mm']-h['half_z_mm']
    lane=r['lanes']['utility'];lane_height=lane['outer_radius_mm']-lane['inner_radius_mm']
    lower=lane['inner_radius_mm']-e['warm_outer_radius_mm'];upper=h['front_mm']-lane['outer_radius_mm']
    front=e['warm_front_z_mm']-b['warm_half_z_mm']
    if (round(gap_b,1),gap_e,rear,offset,exit_width,lane_height,lower,upper,front)!=(488.3,181,580,80,500,140,20.5,20.5,400):
        raise ValueError('Changed gap dimensions; revise annotations')
    cards=[
        dict(number=1,title='Barrel radial gap — 488.3 mm',lines=[
            'Outside warm ECAL: R 2.6417–3.1300 m.',
            'Needs side ports, jacketed cryogenic lines, warm water,',
            'power/HV, data/fibres, control and grounding trays.',
            'Dashed neck box: |z| 3.0–4.0 m; wall/board passages',
            'and connected headers still need engineering.',
            'Cold electronics and local cooling sit inside the ECAL.']),
        dict(number=2,title='Endcap radial corridor — 181 mm',lines=[
            'R 2.949–3.130 m: 140 mm lane + 20.5 mm on each side.',
            'Shared longitudinal bus for barrel/endcap services:',
            'N₂ jackets (~80 mm), LAr utilities (~100 mm),',
            'warm water (~25 mm), power/HV, data and fibres.',
            'Lane widths and utility stations are sectorized in φ.',
            'This is a bundle allowance, not a filled annular wall.']),
        dict(number=3,title='Rear axial space — 580 mm = 80 + 500',lines=[
            'ECAL warm rear |z| 5.660 → HCAL front 6.240 m.',
            '80 mm axial offset + 500 mm outward-exit window.',
            'The 500 mm part sits at |z| 5.740–6.240 m.',
            'Needs pipe elbows, cable turns, connectors/access',
            'and connection to the outer handoff at R 5.950 m.',
            'Current largest elbow allowance: 490 mm within 500 mm.']),
        dict(number=4,title='ECAL barrel/endcap break — 400 mm',lines=[
            'Warm barrel/endcap gap: |z| 4.100–4.500 m.',
            'Mechanical separation and connection/tool clearance.',
            'This is separate from the 500 mm HCAL exit window.',
            'Main pipes use the pre-end side-neck concept;',
            'the original R 400 mm front S-bend cannot fit here.',
            'Connections and access still require physical design.'])]
    sources=['tools/lar_calorimeter/services.json','tools/lar_calorimeter/gap400-prototype.json',
        'docs/design/inputs/DES-032-gap400-prototype.md','docs/design/DES-032-allegro-lar-barrel.md',
        'docs/design/DES-033-allegro-lar-endcaps.md','docs/design/DES-046-hcal-sector-edge-coverage.md']
    return dict(schema_version=1,status='Service-allocation drawing; no geometry or routing implementation',
        input_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        capture_worktree_dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),
        parent_layout=str(path.relative_to(ROOT)),parent_layout_sha256=sha(path),
        parent_renderer_sha256=sha(Path(draw_rz.__file__)),generator_sha256=sha(__file__),
        source_sha256={p:sha(ROOT/p) for p in sources},cards=cards,
        dimensions_mm=dict(barrel_radial=gap_b,endcap_radial=gap_e,rear_axial=rear,
            rear_layout_offset=offset,outward_exit=exit_width,endcap_lane=lane_height,
            endcap_lane_clearances=[lower,upper],ecal_barrel_endcap=front),
        limits=['External service routes/ports/headers are unconstructed allocations, not installed material.',
            'R-Z projection does not represent individual phi-sector pipes or certify physical packing/access.',
            'Cold boards/supports/local cooling are inside warm ECAL bounds; external gaps do not duplicate them.',
            'The80mm rear axial offset is a layout difference, not an extra80mm equipment allocation.'])


def draw(a):
    path=ROOT/a['parent_layout']
    if sha(path)!=a['parent_layout_sha256'] or sha(Path(draw_rz.__file__))!=a['parent_renderer_sha256']:
        raise ValueError('Changed parent drawing input or renderer')
    d=json.loads(path.read_text());root=ET.fromstring(draw_rz.draw(d))
    root.set('height','1450');root.set('viewBox','0 0 1900 1450')
    tag=lambda name:'{'+NS+'}'+name
    for node in list(root):
        if node.tag==tag('rect') and node.get('width')=='1900' and node.get('height')=='1130':
            node.set('height','1450')
        if node.tag==tag('rect') and node.get('stroke-dasharray')=='8 5':
            root.remove(node)  # Previous-layout comparison belongs in the first plot.
        if node.tag==tag('text'):
            yy=float(node.get('y','0'))
            if yy>=899:
                root.remove(node)
            elif yy==52:
                node.text='nODD — what the ECAL–HCAL spaces are for'
            elif yy==89:
                node.text='Compact layout • numbered bands show service allocations and connection requirements'
            elif yy==125:
                node.text='Positive-z examples are labelled; the layout is mirrored at negative z. Dimensions use warm envelopes and face apothems.'
        if node.tag==tag('title'):
            node.text='ECAL-HCAL service spaces in the proposed compact nODD layout'
        if node.tag==tag('desc'):
            node.text='Four numbered regions and callouts explain external service gaps. Geometry is unchanged. Routes and ports are unconstructed reservations.'
    g=ET.SubElement(root,tag('g'),{'id':'service-annotations'})
    x=lambda z:105+(z+10)*84
    y=lambda r:730-r*84
    def rect(z0,z1,r0,r1,opacity='.12',dash=None):
        attrs=dict(x=f'{x(z0):.3f}',y=f'{y(r1):.3f}',width=f'{(z1-z0)*84:.3f}',
            height=f'{(r1-r0)*84:.3f}',fill='#cccc00',**{'fill-opacity':opacity,'stroke':'#898900','stroke-width':'1.2'})
        if dash:attrs['stroke-dasharray']=dash
        ET.SubElement(g,tag('rect'),attrs)
    def text(xx,yy,value,size=20,weight='normal'):
        ET.SubElement(g,tag('text'),dict(x=str(xx),y=str(yy),fill='#25312e',
            **{'font-family':'Arial,Helvetica,sans-serif','font-size':str(size),'font-weight':weight})).text=value
    def badge(n,z,r,point=None):
        if point:
            ET.SubElement(g,tag('path'),dict(d=f'M{x(z):.3f},{y(r):.3f} L{x(point[0]):.3f},{y(point[1]):.3f}',
                fill='none',stroke='#25312e',**{'stroke-width':'1.8'}))
            ET.SubElement(g,tag('circle'),dict(cx=str(x(point[0])),cy=str(y(point[1])),r='3',fill='#25312e'))
        ET.SubElement(g,tag('circle'),dict(cx=str(x(z)),cy=str(y(r)),r='15',fill='white',stroke='#25312e',**{'stroke-width':'1.6'}))
        t=ET.SubElement(g,tag('text'),dict(x=str(x(z)),y=str(y(r)+7),fill='#25312e',
            **{'font-family':'Arial,Helvetica,sans-serif','font-size':'21','font-weight':'bold','text-anchor':'middle'}));t.text=str(n)
    b,e,h,r=(d[k] for k in ('barrel','endcaps','hcal','route_reservation'))
    for side in (-1,1):
        def pair(z0,z1,r0,r1,**kw):
            rect(z0 if side>0 else -z1,z1 if side>0 else -z0,r0,r1,**kw)
        pair(0,b['warm_half_z_mm']/1000,b['outer_radius_mm']/1000,h['front_mm']/1000)
        pair(e['warm_front_z_mm']/1000,e['warm_back_z_mm']/1000,e['warm_outer_radius_mm']/1000,h['front_mm']/1000,opacity='.22')
        pair(e['warm_back_z_mm']/1000,h['endcap_front_mm']/1000,e['warm_inner_radius_mm']/1000,e['warm_outer_radius_mm']/1000,opacity='.06',dash='4 3')
        pair(b['warm_half_z_mm']/1000,e['warm_front_z_mm']/1000,b['inner_radius_mm']/1000,e['warm_outer_radius_mm']/1000,opacity='.06',dash='4 3')
        lo,hi=r['side_neck_band_abs_z_mm'];rlo,rhi=r['radial_single_jacket_bounds_mm']
        pair(lo/1000,hi/1000,rlo/1000,rhi/1000,opacity='0',dash='5 3')
    badge(1,1.8,2.88);badge(2,5.05,3.57,point=(5.05,3.04));badge(3,5.95,1.8);badge(4,4.3,2.1)
    for i,card in enumerate(a['cards']):
        xx=65+(i%2)*905;yy=895+(i//2)*240
        ET.SubElement(g,tag('rect'),dict(x=str(xx),y=str(yy),width='865',height='220',rx='8',
            fill='#fafbf7',stroke='#bbc2b6',**{'stroke-width':'1.2'}))
        text(xx+20,yy+34,str(card['number'])+'  '+card['title'],24,'bold')
        for j,line in enumerate(card['lines']):text(xx+20,yy+65+j*25,line,20)
    text(65,1391,'Service bands are allocations, not installed material. Pressure/vacuum ports, connected routes, supports and access remain to be designed.',18)
    text(65,1423,'HCAL external collectors/manifolds and shared supports still need location/routing assignments; local ECAL hardware is inside its warm package.',18)
    return ET.tostring(root,encoding='unicode')+'\n'


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--capture',action='store_true')
    p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.capture:a.input.write_text(json.dumps(capture(),indent=2)+'\n')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(draw(json.loads(a.input.read_text())))
