#!/usr/bin/env python3
"""Export isolated physical HCAL geometry; all artifacts stay in the chosen directory."""
import argparse
import csv
import json
import math
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from model import ROOT, CONFIG, I, DESCRIPTOR, build, common, endcap_helpers, placements, sha, transform, barrel_row_units


def write(path,node):
    ET.indent(node,space='  ');ET.ElementTree(node).write(path,encoding='utf-8',xml_declaration=True)


def dim(node,**kw):
    for k,v in kw.items():node.set(k,f'{v:.17g}*mm')


def pose(node,xyz,frame=I):
    dim(node,**dict(zip(('x','y','z'),xyz)))
    for i in range(3):
        for j in range(3):node.set(f'a{i}{j}',f'{frame[j][i]:.17g}')


def piece_shape(parent,p):
    q=ET.SubElement(parent,'shape',kind=p['shape_kind']);dim(q,**p['dimensions_mm'])
    for cut in p['cuts']:
        d=ET.SubElement(q,'cut',kind=cut['kind']);dim(d,**cut['dimensions_mm']);pose(d,cut['center_mm'],cut['frame'])
    return q


def shape(parent,kind,**kw):
    q=ET.SubElement(parent,'shape',kind=kind);dim(q,**kw);return q


def polygon(parent,points,depth):
    q=shape(parent,'xtru',depth=depth)
    for x,y in points:dim(ET.SubElement(q,'vertex'),x=x,y=y)
    return q


def ring(parent,inner,outer,depth,sides=16):
    q=shape(parent,'ring',inner=inner,outer=outer,depth=depth);q.set('sides',str(sides));return q


def trapezoid(parent,front,back,half_y,depth,tangent,inset=1,left=None,right=None):
    q=shape(parent,'arb8',half_z=depth/2)
    for radius in (front,back):
        lo=-radius*tangent+inset if left is None else radius*tangent+left
        hi=radius*tangent-inset if right is None else radius*tangent+right
        for x,y in ((lo,-half_y),(hi,-half_y),(hi,half_y),(lo,half_y)):
            dim(ET.SubElement(q,'vertex'),x=x,y=y)
    return q


def template(root,name,material='Air'):
    return ET.SubElement(root,'template',name=name,material=material)


def place(parent,ref,xyz=(0,0,0),frame=I,**ids):
    q=ET.SubElement(parent,'place',ref=ref);pose(q,xyz,frame)
    for key,value in ids.items():q.set(key,str(value))
    return q


def carrier(root,name,unit,uid=0):
    ca=template(root,name);ca.set('compound_tiles','true');ca.set('unit',str(uid))
    w,h,d=unit['fixture']['carrier_size_mm'];shape(ca,'box',sx=w,sy=h,sz=d)
    for p in unit['parts']:
        q=ET.SubElement(ca,'piece',name=p['name'],material=p['material'],role=p['role'])
        piece_shape(q,p);pos=p['center_mm'][:];pos[2]-=6;pose(q,pos,p['frame'])
        if p['role']=='sensitive':q.set('module',str(p['module']));q.set('sensor',str(p['sensor']))
    return ca


def barrel(root,r,unit):
    c=r['config'];b=c['barrel'];n=c['sectors'];t=math.tan(math.pi/n);depth=r['depth']['total_mm'];a=b['front_apothem_mm'];zmid=a+depth/2
    carrier(root,'BarrelCarrier',r['units']['0'])
    for uid,u in sorted(r['units'].items(),key=lambda kv:int(kv[0])):
        if uid!='0':carrier(root,f'BarrelEdgeU{uid}',u,int(uid))
    sector=template(root,'BarrelSector');trapezoid(sector,a,b['outer_apothem_mm'],b['half_z_mm'],depth,t,b['sector_half_seam_mm'])
    usable=b['half_z_mm']-b['end_flange_mm'];inset=b['sector_half_seam_mm']+b['edge_rail_mm']
    # Volumes must be defined before their parent to keep native graph construction deterministic.
    defs=[]
    for layer in r['barrel_layers']:
        li=layer['layer'];front=layer['steel_front_mm'];name=f'BarrelSteel{li}'
        steel=template(root,name,'Steel235');trapezoid(steel,front,front+c['steel_mm'],usable,c['steel_mm'],t,inset)
        place(sector,name,[0,0,front+c['steel_mm']/2-zmid])
        entries=barrel_row_units(layer)
        for row,y in enumerate(layer['rows_mm']):
            for col,entry in enumerate(entries):
                uid=entry['unit'];ref='BarrelCarrier' if uid==0 else f'BarrelEdgeU{uid}'
                place(sector,ref,[entry['x'],y+layer['axial_phase_mm'],layer['carrier_front_mm']+6-zmid],
                      layer=li,carrier=row*len(entries)+col)
    sampling=c['layers']*(c['steel_mm']+12+c['installation_gap_mm']);back=a+sampling
    for sign in (-1,1):
        name=f'BarrelRail{sign}';q=template(root,name,'Aluminium')
        if sign==1:trapezoid(q,a,back,usable,sampling,t,left=-inset,right=-b['sector_half_seam_mm'])
        else:
            # Reflect all x vertices of the right rail; retain polygon vertex ordering.
            sh=trapezoid(q,a,back,usable,sampling,t,left=-inset,right=-b['sector_half_seam_mm'])
            vertices=list(sh)
            for i in range(0,8,4):
                section=vertices[i:i+4];vals=[(-float(v.get('x')[:-3]),float(v.get('y')[:-3])) for v in section]
                for v,(x,y) in zip(section,reversed(vals)):dim(v,x=x,y=y)
        place(sector,name,[0,0,a+sampling/2-zmid])
    cover=template(root,'BarrelRearCover','Aluminium');trapezoid(cover,back,b['outer_apothem_mm'],usable,c['back_cover_mm'],t,b['sector_half_seam_mm'])
    place(sector,'BarrelRearCover',[0,0,back+c['back_cover_mm']/2-zmid])
    flange=template(root,'BarrelFlange','Aluminium');trapezoid(flange,a,b['outer_apothem_mm'],b['end_flange_mm']/2,depth,t,b['sector_half_seam_mm'])
    for sign in (-1,1):place(sector,'BarrelFlange',[0,sign*(b['half_z_mm']-b['end_flange_mm']/2),0])
    full=template(root,'BarrelRoot');ring(full,a,b['outer_apothem_mm'],2*b['half_z_mm'])
    for s in range(n):
        phi=s*2*math.pi/n;f=[[-math.sin(phi),math.cos(phi),0],[0,0,1],[math.cos(phi),math.sin(phi),0]]
        place(full,'BarrelSector',transform([0,0,zmid],[0,0,0],f),f,sector=s,side=0)
    root.set('root_template','BarrelRoot')


def endcaps(root,r,unit):
    c=r['config'];e=c['endcap'];helper=endcap_helpers();pitch=c['steel_mm']+12+c['installation_gap_mm'];depth=r['depth']['total_mm']
    inner=e['inner_apothem_mm']+e['inner_frame_mm'];outer=e['outer_apothem_mm']-e['outer_frame_mm'];sampling=c['layers']*pitch
    carrier(root,'EndcapCarrier',unit)
    steel=template(root,'EndcapQuarterSteel','Steel235')
    sh=polygon(steel,helper.quarter_polygon(outer,e['quarter_gap_mm'],c['sectors']),c['steel_mm'])
    cut=ET.SubElement(sh,'cut',kind='xtru');dim(cut,depth=c['steel_mm'])
    for x,y in helper.quarter_polygon(inner,e['quarter_gap_mm'],c['sectors']):dim(ET.SubElement(cut,'vertex'),x=x,y=y)
    pose(cut,[0,0,0])
    for name,lo,hi in (('EndcapInnerFrame',e['inner_apothem_mm'],inner),('EndcapOuterFrame',outer,e['outer_apothem_mm'])):
        q=template(root,name,'Aluminium');ring(q,lo,hi,sampling)
    cover=template(root,'EndcapRearCover','Aluminium');ring(cover,e['inner_apothem_mm'],e['outer_apothem_mm'],c['back_cover_mm'])
    for side in (1,2):
        sign=1 if side==1 else -1
        for index,phase in enumerate(e['phases_deg']):
            name=f'EndcapLayerS{side}P{index}';q=template(root,name);ring(q,inner,outer,pitch)
            for quarter in range(4):place(q,'EndcapQuarterSteel',[0,0,sign*(c['steel_mm']/2-pitch/2)],helper.frame_for(phase+90*quarter,side))
            counters={}
            for p in r['endcap_pattern']['carriers']:
                x,y=helper.rotate_xy(p['center_xy_mm'],phase);y*=sign;sector=helper.sector_of(x,y,c['sectors']);cid=counters.get(sector,0);counters[sector]=cid+1
                place(q,'EndcapCarrier',[x,y,sign*(c['steel_mm']+6-pitch/2)],helper.frame_for(phase,side),sector=sector,carrier=cid)
        q=template(root,f'EndcapSide{side}');ring(q,e['inner_apothem_mm'],e['outer_apothem_mm'],depth)
        for layer in range(c['layers']):place(q,f'EndcapLayerS{side}P{layer%len(e["phases_deg"])}',[0,0,sign*(layer*pitch+pitch/2-depth/2)],layer=layer)
        for name in ('EndcapInnerFrame','EndcapOuterFrame'):place(q,name,[0,0,sign*(sampling/2-depth/2)])
        place(q,'EndcapRearCover',[0,0,sign*(sampling+c['back_cover_mm']/2-depth/2)])
    full=template(root,'EndcapRoot');shape(full,'assembly')
    for side in (1,2):
        sign=1 if side==1 else -1
        place(full,f'EndcapSide{side}',[0,0,sign*(e['front_abs_z_mm']+depth/2)],side=side)
    root.set('root_template','EndcapRoot')


def compact(report,out):
    unit,_=common();doc=ET.Element('lccdd');ET.SubElement(doc,'info',name='StandaloneHCAL',title='DES046 physical edge-filled standalone HCAL',author='nODD',version='0.2',status='prototype')
    ET.SubElement(ET.SubElement(doc,'includes'),'gdmlFile',ref='materials.xml');defs=ET.SubElement(doc,'define')
    for name,v in zip(('world_x','world_y','world_z'),report['config']['world_half_xyz_mm']):ET.SubElement(defs,'constant',name=name,value=f'{v}*mm')
    readouts=ET.SubElement(doc,'readouts');detectors=ET.SubElement(doc,'detectors')
    for system,name,ro,producer in ((13,'HCALBarrel','HCALBarrelHits',barrel),(14,'HCALEndcaps','HCALEndcapHits',endcaps)):
        readout=ET.SubElement(readouts,'readout',name=ro)
        table=[]
        selected=report['units'] if system==13 else {'0':report['units']['0']}
        for uid,u in sorted(selected.items(),key=lambda kv:int(kv[0])):
            anchor=u['active_offset_from_carrier_front_mm']
            for tile in u['channel_map']:
                table += [int(uid),tile['module'],tile['sensor']]+[v-a for v,a in zip(tile['tile_center_mm'],anchor)]+tile['tile_size_mm']
        ET.SubElement(readout,'segmentation',type='nODDHCALTileGrid',tile_table_mm=' '.join(format(v,'.17g') for v in table))
        ET.SubElement(readout,'id').text=DESCRIPTOR
        root=ET.SubElement(detectors,'detector',name=name,id=str(system),type='nODDHCALResponsePrototype',readout=ro)
        ET.SubElement(root,'sensitive',type='calorimeter');producer(root,report,unit)
    write(out/'detector.xml',doc)
    return doc


def export(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);report=build();unit,mat=common()
    write(out/'materials.xml',mat.root);doc=compact(report,out)
    fields=['system','side','sector','layer','carrier','unit','volume_id','x_mm','y_mm','z_mm']+[f'a{i}{j}' for i in range(3) for j in range(3)]
    with (out/'placements.csv').open('w',newline='') as fp:
        writer=csv.DictWriter(fp,fieldnames=fields);writer.writeheader()
        for p in placements(report['config'],report['barrel_layers'],report['endcap_pattern']):
            row={k:p[k] for k in fields[:7]};row.update(dict(zip(fields[7:10],(format(v,'.17g') for v in p['origin_mm']))))
            row.update({f'a{i}{j}':format(p['frame'][i][j],'.17g') for i in range(3) for j in range(3)});writer.writerow(row)
    report['raw_sensitive_volumes']=report['counts']['carriers']
    report['active_offset_from_carrier_center_mm']=[-168,-87,-4]
    report['active_offset_from_carrier_front_mm']=[-168,-87,2]
    report['sensitive_representation']='Exact disjoint union of original/new physically backed recessed cores per unit, one raw sensitive volume; explicit unit-specific logical tile channels retained by custom segmentation; identity-left unions, final active frame anchored at original first core'
    report['template_counts']={d.get('name'):len(d.findall('template')) for d in doc.findall('detectors/detector')}
    report['source_sha256'].update({str(p.relative_to(ROOT)):sha(p) for p in (Path(__file__),ROOT/'prototypes/hcal_response/HCAL.cpp',ROOT/'prototypes/hcal_response/CMakeLists.txt')})
    report['execution']=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)))
    report['export_sha256']={name:sha(out/name) for name in ('detector.xml','materials.xml','placements.csv')}
    report['placement_table']='placements.csv';report['placement_frame_convention']='aij CSV: row i is carrier-local basis i expressed in world coordinates; xyz is original carrier front-face origin'
    (out/'expected.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(output=str(out/'detector.xml'),counts={k:v for k,v in report['counts'].items() if k!='physical_parts_per_unit'},units=len(report['units']),templates=report['template_counts'])))
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();export(a.output)
