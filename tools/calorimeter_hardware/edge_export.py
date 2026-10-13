"""Export DES030 complete ECAL endcaps and real edge-mask readout topology."""
import argparse
import json
import math
import subprocess
from collections import defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

from edge_layout import area, build, contains, intersect, quarter, rectangle, inset
from assembly import frame_rotation
from assembly_export import transform
from model import ROOT, I, materials, sha
from export import write

TUBE_X=[[0,0,-1],[0,1,0],[1,0,0]]


def capacity(p):
    if p['shape_kind']=='xtru':return area(p['vertices_mm'])*p['depth_mm']
    d=p['dimensions_mm']
    if p['shape_kind']=='tube':return math.pi*(d['rmax']**2-d['rmin']**2)*d['length']
    return d['sx']*d['sy']*d['sz']


def hardware(report,layout):
    c=report['config'];config=json.loads((ROOT/'tools/calorimeter_hardware/cassettes.json').read_text());e=config['ecal'];m=materials(config);layer=[];frame=[]
    def add(target,name,role,mat,poly,z,depth,center=None,kind='xtru',dims=None,cuts=None,orientation=I,module=None):
        p=dict(name=name,role=role,material=mat,shape_kind=kind,center_mm=(center or [0,0])+[z],frame=orientation,cuts=cuts or [])
        if kind=='xtru':p.update(vertices_mm=poly,depth_mm=depth)
        else:p['dimensions_mm']=dims
        v=capacity(p)-sum(capacity(q) for q in p['cuts']);assert v>0
        p.update(volume_mm3=v,mass_g=v*m.recipes[mat]['density_g_cm3']/1000)
        if module is not None:p['module']=module
        target.append(p);return p
    def cut_polygon(p,depth):return dict(shape_kind='xtru',vertices_mm=p,depth_mm=depth,center_mm=[0,0,0],frame=I,cuts=[])
    outer=report['outer_polygon_mm'];side=c['carrier_side_reserve_mm'];hole=c['inner_square_apothem_mm']+c['inner_support_mm'];rim=c['inner_support_mm'];A=report['outer_apothem_mm'];depth=report['layers']*report['layer_pitch_mm']
    plate=quarter(inset(outer,rim),side);hole_polygon=intersect(rectangle(-hole,-hole,2*hole,2*hole),plate)
    depth_cut=lambda d:[cut_polygon(hole_polygon,d)]
    body=e['absorber_mm']
    add(layer,'edge_absorber','absorber','TungstenDens24',plate,body/2,body,cuts=depth_cut(body))
    for name,z in (('front_skin',.1),('back_skin',7.9)):
        add(layer,'edge_'+name,'skin','Aluminium',plate,body+z,.2,cuts=depth_cut(.2))
    tube_rows=[];cold_cuts=depth_cut(c['cooling_plate_mm']);zcold=body+4.8+c['cooling_plate_mm']/2
    from edge_layout import planes
    for i in range(math.ceil(A/c['cooling_pipe_pitch_mm'])):
        y=c['cooling_pipe_start_y_mm']+i*c['cooling_pipe_pitch_mm'];r=config['tube_outer_radius_mm'];low=(hole if y-r<hole else side)+c['cooling_port_inset_mm']
        upper=min((offset-b*v)/a for a,b,offset in planes(plate) if a>1e-8 for v in (y-r,y+r))-c['cooling_port_inset_mm']
        if upper-low<20 or not all(contains(plate,x,v) for x,v in rectangle(low,y-r,upper-low,2*r)):continue
        center=[(low+upper)/2,y,0];dims=dict(rmin=0,rmax=r,length=upper-low)
        cold_cuts.append(dict(shape_kind='tube',dimensions_mm=dims,center_mm=center,frame=TUBE_X,cuts=[]));tube_rows.append(dict(center_mm=center[:2]+[zcold],length_mm=upper-low,port_x_mm=[low,upper],y_mm=y))
        for tag,mat,r0,r1 in (('pipe','Titanium',config['tube_inner_radius_mm'],r),('water','Water',0,config['tube_inner_radius_mm'])):
            add(layer,f'cooling_{i}_{tag}',tag,mat,None,zcold,0,center=center[:2],kind='tube',dims=dict(rmin=r0,rmax=r1,length=upper-low),orientation=TUBE_X)
    add(layer,'edge_cold_plate','spreader','Copper',plate,zcold,c['cooling_plate_mm'],cuts=cold_cuts)
    modules=layout['modules']
    for q in modules:
        idx=q['index'];origin=q['center_mm'];prefix=f'edge_m{idx}_';sensor,active,board=q['sensor'],q['active'],q['board']
        add(layer,prefix+'active','sensitive','Silicon',active,body+e['sensor_center_z_mm'],e['sensor_mm'],center=origin,module=idx)
        add(layer,prefix+'guard','sensor_edge','Silicon',sensor,body+e['sensor_center_z_mm'],e['sensor_mm'],center=origin,cuts=[cut_polygon(active,e['sensor_mm'])])
        for p in e['sensor_layers']:
            add(layer,prefix+p['name'],p['name'],p['material'],active if p['name']=='pad' else sensor,body+p['center_z_mm'],p['thickness_mm'],center=origin)
        t=e['pcb_mm']-e['pcb_copper_equivalent_mm'];z=e['pcb_front_mm']
        add(layer,prefix+'PCB_G10','pcb','G10',board,body+z+t/2,t,center=origin)
        add(layer,prefix+'PCB_Cu','pcb','Copper',board,body+z+t+e['pcb_copper_equivalent_mm']/2,e['pcb_copper_equivalent_mm'],center=origin)
        for j,(x,y) in enumerate(q['asics']):
            for p in e['asic_stack']:
                dims=dict(zip(('sx','sy','sz'),e['asic_package_xy_mm']+[p['thickness_mm']]))
                add(layer,prefix+f'a{j}_'+p['name'],p['role'],p['material'],None,body+p['center_z_mm'],0,center=[origin[0]+x,origin[1]+y],kind='box',dims=dims)
    available=quarter(inset(outer,rim+c['outer_service_band_mm']),side)
    # available includes the aperture: separate hole subtraction would overlap it.
    add(layer,'edge_shared_PCB','interface','G10',plate,body+e['pcb_front_mm']+e['pcb_mm']/2,e['pcb_mm'],cuts=[cut_polygon(available,e['pcb_mm'])])
    n=math.ceil(sum(len(q['pads']) for q in modules)/8192)
    for j in range(n):
        phi=(j+.5)*math.pi/(2*n);normal=round(phi/(math.pi/8))*math.pi/8;rad=(A-rim-c['outer_service_band_mm']/2)/math.cos(phi-normal);x,y=rad*math.cos(phi),rad*math.sin(phi);co,si=math.cos(normal),math.sin(normal);rot=[[co,si,0],[-si,co,0],[0,0,1]]
        for tag,role,mat,z,t in (('chip','interface','HCalPackage',3.28,1.4),('pad','thermal_pad','Graphite',4.08,.2),('post','thermal_post','Aluminium',4.49,.62)):
            add(layer,f'interface_{j}_{tag}',role,mat,None,body+z,0,center=[x,y],kind='box',dims=dict(sx=20,sy=20,sz=t),orientation=rot)
    seam=.5
    for tag,p in (('x_rib',rectangle(seam,hole,side-seam,A-rim-hole)),('y_rib',rectangle(hole,seam,A-rim-hole,side-seam)),('inner_x',rectangle(c['inner_square_apothem_mm'],side,rim,hole-side)),('inner_y',rectangle(side,c['inner_square_apothem_mm'],c['inner_square_apothem_mm']-side,rim))):
        add(frame,'frame_'+tag,'support','Aluminium',p,depth/2,depth)
    rim_outer=quarter(outer,side)
    add(frame,'frame_outer_rim','support','Aluminium',rim_outer,depth/2,depth,cuts=[cut_polygon(plate,depth)])
    back=quarter(outer,seam);aperture=intersect(rectangle(-c['inner_square_apothem_mm'],-c['inner_square_apothem_mm'],2*c['inner_square_apothem_mm'],2*c['inner_square_apothem_mm']),back);t=report['back_cover_mm']
    add(frame,'frame_back_cover','back_cover','Aluminium',back,depth+t/2,t,cuts=[cut_polygon(aperture,t)])
    totals=defaultdict(lambda:dict(volume_mm3=0.,mass_g=0.))
    for pieces,mult in ((layer,8*48),(frame,8)):
        for p in pieces:
            for k in ('volume_mm3','mass_g'):totals[p['material']][k]+=mult*p[k]
    return dict(layer_parts=layer,frame_parts=frame,cooling_runs=tube_rows,material_totals=dict(totals),mass_g=sum(q['mass_g'] for q in totals.values()),materials=m.recipes),m


def encode_geometry(node,p):
    node.set('kind',p['shape_kind']);transform(node,p)
    if p['shape_kind']=='xtru':
        node.set('depth',f"{p['depth_mm']:.17g}*mm")
        for x,y in p['vertices_mm']:ET.SubElement(node,'vertex',x=f'{x:.17g}*mm',y=f'{y:.17g}*mm')
    else:
        for k,v in p['dimensions_mm'].items():node.set(k,f'{v:.17g}*mm')
    for q in p.get('cuts',[]):encode_geometry(ET.SubElement(node,'cut'),q)


def export(output,name='edges',layers=48):
    if layers!=48:raise ValueError('Complete DES030 export requires48 layers; use edge_fixture.py for sparse transport.')
    output.mkdir(parents=True,exist_ok=True);report,layouts,_=build();layout=layouts[name];hw,m=hardware(report,layout)
    write(output/'materials.xml',m.root);doc=ET.Element('lccdd');ET.SubElement(doc,'info',name='EdgeECAL',title='DES030 isolated prototype',author='nODD',version='0.1',status='prototype');ET.SubElement(ET.SubElement(doc,'includes'),'gdmlFile',ref='materials.xml');define=ET.SubElement(doc,'define')
    for k,v in dict(world_x=6000,world_y=6000,world_z=8000).items():ET.SubElement(define,'constant',name=k,value=f'{v}*mm')
    ro=ET.SubElement(ET.SubElement(doc,'readouts'),'readout',name='EDGEHits');cells=[];polys=[];pitch=5.5
    for q in layout['modules']:
        polys += [q['index'],len(q['active'])]+[v for p in q['active'] for v in p]
        if q['full']:continue
        for g in q['pads']:
            for raw in g['members']:cells += [q['index'],*raw,*g['key'],*g['reference_mm'],*g['bbox_mm']]
    ET.SubElement(ro,'segmentation',type='nODDEdgeGrid',grid_size_x='5.5*mm',grid_size_y='5.5*mm',offset_x='2.75*mm',offset_y='2.75*mm',cell_table_mm=' '.join(format(v,'.17g') for v in cells),sensor_polygons_mm=' '.join(format(v,'.17g') for v in polys));ET.SubElement(ro,'id').text='system:8,side:2,sector:3,layer:6,module:10,x:-6,y:-6'
    d=ET.SubElement(ET.SubElement(doc,'detectors'),'detector',name='EDGE',id='8',type='nODDEcalEdgePrototype',readout='EDGEHits');ET.SubElement(d,'sensitive',type='calorimeter')
    for region,pieces in (('edge_layer',hw['layer_parts']),('edge_frame',hw['frame_parts'])):
        node=ET.SubElement(d,'region',name=region)
        for p in pieces:
            child=ET.SubElement(node,'piece',name=p['name'],role=p['role'],material=p['material']);encode_geometry(child,p)
            if 'module' in p:child.set('module',str(p['module']))
    replicas=[]
    for side in (1,2):
        for sector in range(4):
            rot=frame_rotation(sector*math.pi/2,side==2)
            for region,ls in (('edge_layer',range(layers)),('edge_frame',(0,))):
                for layer in ls:
                    z=report['front_mm']+(layer*report['layer_pitch_mm'] if region=='edge_layer' else 0);p=dict(region=region,side=side,sector=sector,layer=layer,center_mm=[0,0,z if side==1 else -z],frame=rot);replicas.append(p)
                    node=ET.SubElement(d,'replica',region=region,side=str(side),sector=str(sector),layer=str(layer));transform(node,p)
    write(output/'calorimeter.xml',doc)
    expected=dict(status='DRAFT / PROTOTYPE',layout_name=name,layout_report=report,modules=layout['modules'],hardware=hw,replicas=replicas,layers=layers,execution=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],text=True))),source_sha256={str(p.relative_to(ROOT)):sha(p) for p in (Path(__file__),ROOT/'prototypes/calorimeter/EdgeCalorimeter.cpp',ROOT/'tools/calorimeter_hardware/edge_layout.py',ROOT/'tools/calorimeter_hardware/edge_sensors.json',ROOT/'tools/pixel_barrel_dd4hep/materials.py',ROOT/'detector/config/elements.json')})
    (output/'expected.json').write_text(json.dumps(expected,indent=2)+'\n');print(name,len(layout['modules']),'modules/quarter/layer',hw['mass_g']/1e6,'t both complete endcaps');return expected


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--layout',choices=('squares','edges'),default='edges');p.add_argument('--layers',type=int,default=48);a=p.parse_args();export(a.output,a.layout,a.layers)
