"""Export complete DES031 barrel with reused logical square-board hardware."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from assembly import BARREL_FRAME, frame_rotation, wedge
from assembly_export import transform
from barrel_layout import build, coverage
from edge_export import capacity, encode_geometry
from edge_layout import rectangle
from export import write
from model import ROOT, I, materials, sha


def hardware(report,base):
    cfg=json.loads((ROOT/'tools/calorimeter_hardware/cassettes.json').read_text());e=cfg['ecal'];c=report['config'];a=report['assembly_config'];mat=materials(cfg)
    board=[];layers=[];totals=defaultdict(lambda:dict(volume_mm3=0.,mass_g=0.))
    def add(target,name,role,material,kind,center,poly=None,depth=None,dims=None,cuts=None):
        p=dict(name=name,role=role,material=material,shape_kind=kind,center_mm=center,frame=I,cuts=cuts or [])
        if kind=='xtru':p.update(vertices_mm=poly,depth_mm=depth)
        else:p['dimensions_mm']=dims
        volume=capacity(p)-sum(capacity(q) for q in p['cuts'])
        if volume<=0:raise ValueError('nonpositive part')
        p.update(volume_mm3=volume,mass_g=volume*mat.recipes[material]['density_g_cm3']/1000);target.append(p);return p
    def box(target,name,role,material,center,size):return add(target,name,role,material,'box',center,dims=dict(zip(('sx','sy','sz'),size)))
    def prism(target,name,role,material,poly,z,depth,cuts=None):return add(target,name,role,material,'xtru',[0,0,z],poly=poly,depth=depth,cuts=cuts)
    size=e['sensor_outer_mm'];active=report['active_mask_mm'];sensor=rectangle(-size/2,-size/2,size,size);pcb=rectangle(-report['board_size_mm']/2,-report['board_size_mm']/2,report['board_size_mm'],report['board_size_mm'])
    add(board,'square_active','sensitive','Silicon','xtru',[0,0,e['sensor_center_z_mm']],poly=active,depth=e['sensor_mm'])
    cut=dict(shape_kind='xtru',vertices_mm=active,depth_mm=e['sensor_mm'],center_mm=[0,0,0],frame=I,cuts=[])
    add(board,'square_guard','sensor_edge','Silicon','xtru',[0,0,e['sensor_center_z_mm']],poly=sensor,depth=e['sensor_mm'],cuts=[cut])
    for p in e['sensor_layers']:add(board,'square_'+p['name'],p['name'],p['material'],'xtru',[0,0,p['center_z_mm']],poly=active if p['name']=='pad' else sensor,depth=p['thickness_mm'])
    t=e['pcb_mm']-e['pcb_copper_equivalent_mm'];z=e['pcb_front_mm']
    add(board,'square_PCB_G10','pcb','G10','xtru',[0,0,z+t/2],poly=pcb,depth=t)
    add(board,'square_PCB_Cu','pcb','Copper','xtru',[0,0,z+t+e['pcb_copper_equivalent_mm']/2],poly=pcb,depth=e['pcb_copper_equivalent_mm'])
    for j,(x,y) in enumerate(((-22,-22),(-22,22),(22,-22),(22,22))):
        for p in e['asic_stack']:box(board,f'square_a{j}_'+p['name'],p['role'],p['material'],[x,y,p['center_z_mm']],e['asic_package_xy_mm']+[p['thickness_mm']])
    tangent=math.tan(math.pi/a['sectors']);side=a['seam_half_gap_mm']+a['edge_rail_mm'];half=a['barrel_half_z_mm']
    for q in report['layers']:
        pieces=[];r=q['front_mm'];body=r+e['absorber_mm'];runs=[]
        prism(pieces,f"barrel_l{q['index']}_absorber",'absorber','TungstenDens24',wedge(r,body,tangent,side),0,2*half)
        for p in q['panels']:
            idx=p['index'];usable=p['length_mm']-2*c['panel_end_frame_mm'];prefix=f"barrel_l{q['index']}_p{idx}_"
            for tag,z in (('front_skin',.1),('back_skin',7.9)):
                prism(pieces,prefix+tag,'skin','Aluminium',wedge(body+z-.1,body+z+.1,tangent,side),p['center_mm'],usable)
            for sign in (-1,1):
                prism(pieces,prefix+'end_frame'+str(sign),'slab_frame','Aluminium',wedge(body,body+e['body_depth_mm'],tangent,side),p['center_mm']+sign*(p['length_mm']-c['panel_end_frame_mm'])/2,c['panel_end_frame_mm'])
            coldfront=body+4.8;coldcenter=coldfront+c['cooling_plate_mm']/2;length=usable-2*c['cooling_port_inset_mm'];cuts=[]
            for j,u in enumerate(q['column_centers_mm']):
                dims=dict(rmin=0,rmax=cfg['tube_outer_radius_mm'],length=length)
                cuts.append(dict(shape_kind='tube',dimensions_mm=dims,center_mm=[coldcenter,u,0],frame=I,cuts=[]))
                for tag,role,material,r0,r1 in [('pipe','pipe','Titanium',cfg['tube_inner_radius_mm'],cfg['tube_outer_radius_mm']),('water','water','Water',0,cfg['tube_inner_radius_mm'])]:
                    add(pieces,prefix+f'run{j}_'+tag,role,material,'tube',[coldcenter,u,p['center_mm']],dims=dict(rmin=r0,rmax=r1,length=length))
                runs.append(dict(panel=idx,column=j,center_mm=[coldcenter,u,p['center_mm']],length_mm=length))
            prism(pieces,prefix+'cold_plate','spreader','Copper',wedge(coldfront,coldfront+c['cooling_plate_mm'],tangent,side),p['center_mm'],usable,cuts)
            width=2*((body+e['pcb_front_mm'])*tangent-side)
            box(pieces,prefix+'shared_PCB','interface','G10',[body+e['pcb_front_mm']+e['pcb_mm']/2,0,p['bay_center_mm']],[e['pcb_mm'],width,c['service_bay_mm']])
            for interface in (v for v in q['interfaces'] if v['panel']==idx):
                u=sum(q['column_centers_mm'][j] for j in interface['lanes'])/len(interface['lanes']);ip=prefix+f"interface{interface['index']}_"
                for tag,role,material,z,depth in [('chip','interface','HCalPackage',3.28,1.4),('pad','thermal_pad','Graphite',4.08,.2),('post','thermal_post','Aluminium',4.49,.62)]:box(pieces,ip+tag,role,material,[body+z,u,p['bay_center_mm']],[depth,20,20])
        layers.append(dict(index=q['index'],parts=pieces,cooling_runs=runs))
        for p in pieces:
            for k in ('volume_mm3','mass_g'):totals[p['material']][k]+=a['sectors']*p[k]
        for p in board:
            for k in ('volume_mm3','mass_g'):totals[p['material']][k]+=a['sectors']*len(q['modules'])*p[k]
    frames=[p for p in base['regions'][0]['parts'] if p['role']!='absorber']
    for p in frames:
        for k in ('volume_mm3','mass_g'):totals[p['material']][k]+=a['sectors']*p[k]
    return dict(board_parts=board,layers=layers,frame_parts=frames,material_totals=dict(totals),mass_g=sum(q['mass_g'] for q in totals.values()),materials=mat.recipes),mat


def export(output):
    output.mkdir(parents=True,exist_ok=True);report,base=build();hw,mat=hardware(report,base);write(output/'materials.xml',mat.root)
    doc=ET.Element('lccdd');ET.SubElement(doc,'info',name='SiWBarrel',title='DES031 isolated prototype',author='nODD',version='0.1',status='prototype');ET.SubElement(ET.SubElement(doc,'includes'),'gdmlFile',ref='materials.xml');define=ET.SubElement(doc,'define')
    for key,value in dict(world_x=5000,world_y=5000,world_z=6000).items():ET.SubElement(define,'constant',name=key,value=f'{value}*mm')
    ro=ET.SubElement(ET.SubElement(doc,'readouts'),'readout',name='BARRELHits');ids=sorted({m['index'] for q in report['layers'] for m in q['modules']});polys=[]
    for idx in ids:polys += [idx,4]+[v for p in report['active_mask_mm'] for v in p]
    pitch=report['ecal']['pitch_mm'];ET.SubElement(ro,'segmentation',type='nODDEdgeGrid',grid_size_x=f'{pitch}*mm',grid_size_y=f'{pitch}*mm',offset_x=f'{pitch/2}*mm',offset_y=f'{pitch/2}*mm',sensor_polygons_mm=' '.join(format(v,'.17g') for v in polys));ET.SubElement(ro,'id').text='system:8,side:2,sector:4,layer:6,module:10,x:-6,y:-6'
    det=ET.SubElement(ET.SubElement(doc,'detectors'),'detector',name='BARREL',id='8',type='nODDEcalBarrelPrototype',readout='BARRELHits');ET.SubElement(det,'sensitive',type='calorimeter');board=ET.SubElement(det,'board',name='square')
    def piece(node,p):child=ET.SubElement(node,'piece',name=p['name'],role=p['role'],material=p['material']);encode_geometry(child,p)
    for p in hw['board_parts']:piece(board,p)
    regions=[dict(name='barrel_frame',parts=hw['frame_parts'],modules=[],index=0)]
    for q,h in zip(report['layers'],hw['layers']):regions.append(dict(name=f"barrel_layer{q['index']}",parts=h['parts'],modules=q['modules'],index=q['index']))
    replicas=[]
    for region in regions:
        node=ET.SubElement(det,'region',name=region['name'])
        for p in region['parts']:piece(node,p)
        for q in region['modules']:
            layer=report['layers'][region['index']];m={**q,'frame':BARREL_FRAME if q['center_mm'][1]>=0 else [[0,-1,0],[0,0,-1],[1,0,0]],'center_mm':[layer['front_mm']+report['ecal']['absorber_mm'],*q['center_mm']]};n=ET.SubElement(node,'board_instance',template='square',module=str(q['index']));transform(n,m)
        for sector in range(report['assembly_config']['sectors']):
            p=dict(region=region['name'],side=0,sector=sector,layer=region['index'],center_mm=[0,0,0],frame=frame_rotation(sector*2*math.pi/16));replicas.append(p);n=ET.SubElement(det,'replica',region=p['region'],side='0',sector=str(sector),layer=str(p['layer']));transform(n,p)
    write(output/'calorimeter.xml',doc)
    paths=[Path(__file__),ROOT/'tools/calorimeter_hardware/barrel_layout.py',ROOT/'tools/calorimeter_hardware/barrel.json',ROOT/'prototypes/calorimeter/BarrelCalorimeter.cpp',ROOT/'prototypes/calorimeter/EdgeCalorimeter.cpp',ROOT/'prototypes/calorimeter/CMakeLists.txt',ROOT/'tools/calorimeter_hardware/edge_export.py',ROOT/'tools/calorimeter_hardware/edge_layout.py',ROOT/'tools/calorimeter_hardware/assembly_export.py',ROOT/'tools/calorimeter_hardware/export.py',ROOT/'tools/pixel_barrel_dd4hep/materials.py',ROOT/'detector/config/elements.json']
    expected=dict(status='DRAFT / PROTOTYPE',layout_report=report,hardware=hw,regions=regions,replicas=replicas,coverage=coverage(report),execution=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],text=True))),source_sha256={**report['source_sha256'],**{str(p.relative_to(ROOT)):sha(p) for p in paths}})
    (output/'expected.json').write_text(json.dumps(expected,indent=2)+'\n');print(report['summary']['sensors'],'sensors',hw['mass_g']/1e6,'tonnes',report['summary']['continuous_heat_W']/1000,'kW');return expected


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();export(a.output)
