#!/usr/bin/env python3
"""Explicit DES021 standalone compact; constituent-conserving service cells."""
import argparse
from collections import Counter,defaultdict
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from model import ROOT,INPUT,load,build,cooling,sha
sys.path.insert(0,str(ROOT/'tools/pixel_barrel_dd4hep'))
from materials import Materials


def write(path,node):
    ET.indent(node,space='  ');ET.ElementTree(node).write(path,encoding='utf-8',xml_declaration=True)

def export(c,out):
    l=build(c);mat=Materials(dict(coolant_density_g_cm3=1,cfrp_carbon_mass_fraction=.70,module=dict(flex_copper_coverage=.5)),
        dict(density_g_cm3=dict(titanium=4.51,graphite=2.21,insulation=1.42,glue=2,CFRP=1.73,foam=.20)))
    mat.add('Aluminium',2.7,{'Al':1});mat.add('Silica',2.2,{'Si':1,'O':2},atoms=True);mat.add('CarbonFoam',.20,{'C':1})
    mat.effective('BumpFixture',{'Copper':.15},1);mat.effective('SignalFlex',{'Copper':.085,'Polyimide':.915},1)
    mat.effective('ElectronicsFixture',{'Silicon':.04,'Copper':.01,'Polyimide':.10},1)
    doc=ET.Element('lccdd');ET.SubElement(doc,'info',name='ShortStripEndcap',title='DES021 isolated prototype',author='nODD',version='0.1',status='prototype')
    ET.SubElement(ET.SubElement(doc,'includes'),'gdmlFile',ref='materials.xml')
    defs=ET.SubElement(doc,'define')
    for a,v in zip('xyz',c['world_half_size_mm']):ET.SubElement(defs,'constant',name='world_'+a,value=f'{v}*mm')
    for k,v in [('rmax',800),('zmax',3300)]:ET.SubElement(defs,'constant',name='tracker_region_'+k,value=f'{v}*mm')
    ro=ET.SubElement(ET.SubElement(doc,'readouts'),'readout',name='ShortStripEndcapHits')
    ET.SubElement(ro,'segmentation',type='CartesianGridXY',grid_size_x='.075*mm',grid_size_y='.5*mm',offset_x='.0375*mm',offset_y='.25*mm')
    ET.SubElement(ro,'id').text='system:5,layer:4,petal:4,ring:3,module:4,sensor:1,x:-11,y:-10'
    det=ET.SubElement(ET.SubElement(doc,'detectors'),'detector',name='ShortStripEndcap',id='4',type='nODDShortStripEndcap',readout='ShortStripEndcapHits')
    ET.SubElement(det,'sensitive',type='tracker')
    entities=[];totals=defaultdict(lambda:dict(volume_mm3=0.,mass_g=0.))
    def entity(name,role,center,volume=None,material=None,**extra):
        e=dict(name=name,role=role,center_mm=center,**extra)
        if volume is not None:
            e.update(volume_mm3=volume,material=material,mass_g=volume*mat.recipes[material]['density_g_cm3']/1000)
            for key in ('volume_mm3','mass_g'):totals[material][key]+=e[key]
        entities.append(e);return e
    def capacity(kind,d):
        if kind=='box':return d['sx']*d['sy']*d['sz']
        if kind in ('tube','sector'):return d.get('angle',2*math.pi)/2*(d['rmax']**2-d['rmin']**2)*d['length']
        if kind=='torus':return d['angle']*math.pi*d['major']*(d['rmax']**2-d['rmin']**2)
        raise ValueError(kind)
    def attrs(center,dims,rot=(0,0,0)):
        r={k:format(float(v),'.17g')+'*mm' for k,v in zip(('u','v','w'),center)}
        for k,v in dims.items():r[k]=format(float(v),'.17g')+('*rad' if k in ('start','angle') else '*mm')
        r.update({k:format(float(v),'.17g')+'*rad' for k,v in zip(('rx','ry','rz'),rot)})
        return r
    def pose(center,side=1,z=0,phi=0):
        x,y,w=center;return [x*math.cos(phi)-y*math.sin(phi),side*(x*math.sin(phi)+y*math.cos(phi)),side*(w+z)]
    def piece(parent,name,role,kind,material,center,dims,side=1,z=0,phi=0,rot=(0,0,0),ids=None):
        node=ET.SubElement(parent,'piece',name=name,kind=kind,material=material,**attrs(center,dims,rot))
        e=entity(name,role,pose(center,side,z,phi),capacity(kind,dims),material)
        if kind=='tube':
            rx,ry,rz=rot
            nx=math.sin(ry)*math.cos(rx)*math.cos(rz)+math.sin(rx)*math.sin(rz)
            ny=math.sin(ry)*math.cos(rx)*math.sin(rz)-math.sin(rx)*math.cos(rz)
            nz=math.cos(ry)*math.cos(rx)
            e['normal']=[nx*math.cos(phi)-ny*math.sin(phi),side*(nx*math.sin(phi)+ny*math.cos(phi)),side*nz]

        if ids:
            node.set('sensitive','true');node.set('sensor','0');e['ids']=ids
        return node,e
    for disc in l['discs']:
        lid=disc['layer'];side=disc['side'];z=abs(disc['z_mm']);dn=f'D{lid}'
        disk=ET.SubElement(det,'disc',name=dn,id=str(lid),z=f'{z}*mm',side=str(side));entity(dn,'disc',[0,0,side*z])
        for i,(rin,rout) in enumerate(c['frame_mm']):
            piece(disk,dn+f'_frame{i}','frame','sector','CFRP',[0,0,-12],dict(rmin=rin,rmax=rout,length=3,start=0,angle=2*math.pi),side,z)
        for petal in range(c['petals']):
            phi=petal*math.pi/6;pn=dn+f'_P{petal}'
            p=ET.SubElement(disk,'petal',name=pn,id=str(petal),phi=f'{phi}*rad');entity(pn,'petal',[0,0,side*z])
            def add(label,role,material,center,size,rz=0):
                return piece(p,pn+'_'+label,role,'box',material,center,dict(zip(('sx','sy','sz'),size)),side,z,phi,rot=(0,0,rz))
            def polar(radius,angle,w):return [radius*math.cos(angle),radius*math.sin(angle),w]
            gap=c['petal_gap_mm']/c['plate_mm'][0];start=gap/2;angle=math.pi/6-gap
            for label,w,thick,material in [('front_skin',-1.375,.15,'CFRP'),('front_glue',-1.5,.1,'Epoxy'),('back_glue',-6.6,.1,'Epoxy'),('back_skin',-6.725,.15,'CFRP')]:
                piece(p,pn+'_'+label,'support','sector',material,[0,0,w],dict(rmin=236,rmax=685,length=thick,start=start,angle=angle),side,z,phi)
            core,e=piece(p,pn+'_core','core','sector','CarbonFoam',[0,0,-4.05],dict(rmin=236,rmax=685,length=5,start=start,angle=angle),side,z,phi)
            removed=0
            for segment in cooling(c):
                dims=dict(segment['dims']);dims.update(rmin=0,rmax=c['tube_OD_mm']/2)
                rot=tuple(segment[k] for k in ('rx','ry','rz'));center=segment['center']
                local=[center[0],center[1],center[2]+4.05]
                ET.SubElement(core,'cut',kind=segment['kind'],**attrs(local,dims,rot));removed+=capacity(segment['kind'],dims)
                for role,material,low,high in [('cooling_tube','Titanium',1.25-.14,1.25),('coolant','CO2',0,1.25-.14)]:
                    solid=dict(segment['dims'],rmin=low,rmax=high)
                    piece(p,pn+'_'+segment['label']+'_'+role,role,segment['kind'],material,center,solid,side,z,phi,rot)
            e['volume_mm3']-=removed;delta=removed*.20/1000;e['mass_g']-=delta
            totals['CarbonFoam']['volume_mm3']-=removed;totals['CarbonFoam']['mass_g']-=delta
            # Copper/PI distribution stays behind the cold sandwich.
            bus_phi=math.radians(15);r=(250+678)/2;length=428
            add('LV_PI','power_bus','Polyimide',polar(r,bus_phi,-6.875),[26,length,.15],bus_phi+math.pi/2)
            for sign in (-1,1):
                center=polar(r,bus_phi,-7.05);center[0]-=sign*6.25*math.sin(bus_phi);center[1]+=sign*6.25*math.cos(bus_phi)
                add('LV_Cu'+str(sign),'power_bus','Copper',center,[12,length,.2],bus_phi+math.pi/2)
            sig=math.radians(22);add('signal_HV','signal_bus','SignalFlex',polar(r,sig,-6.85),[8,length,.1],sig+math.pi/2)
            selected=[m for m in l['modules'] if m['layer']==lid and m['petal']==petal]
            flex_volume=0
            for m in selected:
                theta=m['phi_rad']-phi;r=m['radius_mm'];lift=m['lift_mm'];mn=m['name']
                module=ET.SubElement(p,'module',name=mn,id=str(m['module']),ring=str(m['ring']),radius=f'{r}*mm',phi=f'{theta}*rad',lift=f'{lift}*mm')
                entity(mn,'module',m['center_mm'])
                def mod(label,role,material,u,v,w,size,sensitive=False):
                    node,e=piece(module,mn+'_'+label,role,'box',material,[u,v,w],dict(zip(('sx','sy','sz'),size)))
                    x=r*math.cos(theta)-u*math.sin(theta)-v*math.cos(theta);y=r*math.sin(theta)+u*math.cos(theta)-v*math.sin(theta)
                    e['center_mm']=pose([x,y,w+lift],side,z,phi)
                    if sensitive:
                        node.set('sensitive','true');node.set('sensor','0');e.update(ids=dict(system=4,layer=lid,petal=petal,ring=m['ring'],module=m['module'],sensor=0),u=m['u'],v=m['v'],normal=m['n'],size_mm=size)
                    return e
                mod('active','sensitive','Silicon',0,0,0,[48,96,.2],True)
                for sign in (-1,1):
                    mod('guardU'+str(sign),'guard','Silicon',sign*24.25,0,0,[.5,97,.2])
                    mod('guardV'+str(sign),'guard','Silicon',0,sign*48.25,0,[48,.5,.2])
                mod('bumps','interconnect','BumpFixture',0,0,-.1125,[48,96,.025])
                for ix in (-1,1):
                    for iy in (-3,-1,1,3):mod(f'ASIC_{ix}_{iy}','readout','Silicon',ix*12,iy*12,-.2,[23.4,23.4,.15])
                for label,material,w,t in [('ASICglue','Epoxy',-.325,.1),('spreader','Graphite',-.475,.2),('isolation','Polyimide',-.5875,.025),('backglue','Epoxy',-.65,.1),('backing','CFRP',-.8,.2)]:mod(label,'module_passive',material,0,0,w,[48,96,t])
                for sign in (-1,1):
                    mod('flex'+str(sign),'module_flex','SignalFlex',0,sign*50,-.5,[49,3,.1])
                    h=lift+.4;u=sign*c['pickup_u_mm'];x=r*math.cos(theta)-u*math.sin(theta);y=r*math.sin(theta)+u*math.cos(theta)
                    add(f'R{m["ring"]}_M{m["module"]}_pickup{sign}','thermal_pickup','Graphite',[x,y,-1.3+h/2],[c["pickup_mm"][0],c["pickup_mm"][1],h],theta+math.pi/2)
                # Two3mm-wide0.1mm tails from module edge to outer interface.
                route_length=max(0,685-(r+50))+abs(theta-bus_phi)*(r+50)
                flex_volume+=2*3*.1*route_length
            # Conserved effective fanout; no pretence that individual vias are explicit.
            cap=angle/2*(685**2-236**2)*.5
            recipe={'Copper':flex_volume*.085,'Polyimide':flex_volume*.915}
            fname=mat.effective(pn+'_fanout',recipe,cap)
            _,ef=piece(p,pn+'_fanout','local_fanout','sector',fname,[0,0,9.25],dict(rmin=236,rmax=685,length=.5,start=start,angle=angle),side,z,phi)
            ef['constituent_volumes_mm3']=recipe
            for k,(r,ph) in enumerate([(243,10),(678,10),(678,26)]):
                theta=math.radians(ph);add(f'lug{k}','mount','CFRP',polar(r,theta,(-10.5-6.8)/2),c['lug_mm'],theta+math.pi/2)
            add('board','end_board','ElectronicsFixture',polar(695,bus_phi,4),c['board_mm'],bus_phi+math.pi/2)
            for sign in (-1,1):
                center=polar(695,bus_phi,-5.25)
                center[0]-=sign*c['board_mount_u_mm']*math.sin(bus_phi)
                center[1]+=sign*c['board_mount_u_mm']*math.cos(bus_phi)
                add('board_mount'+str(sign),'mount','CFRP',center,c['board_mount_mm'],bus_phi+math.pi/2)

            # Outer fan uses full quarter-turn path reservations, not reduced fill.
            rin,rout,low,high=c['fan_mm'];span=c['phi_fraction']*math.pi/6;wall=c['tray_wall_mm'];length=high-low
            cap=span/2*((rout-wall)**2-(rin+wall)**2)*length
            route=next(x for x in l['routes'] if x['layer']==lid and x['petal']==petal)
            constituents=defaultdict(float)
            cable_length=750-695+math.pi*50
            cv=route['harnesses']*cable_length*math.pi/4*c['power_cable_OD_mm']**2
            fv=cv*(c['fibre_cable_OD_mm']/c['power_cable_OD_mm'])**2
            constituents.update(Copper=.2*cv,Polyimide=.3*cv+.5*fv,Air=.5*cv,Silica=.5*fv)
            pl=2*(750-678+math.pi*25);constituents['Titanium']=pl*math.pi/4*(2.5**2-2.22**2);constituents['CO2']=pl*math.pi/4*2.22**2
            smat=mat.effective(pn+'_fan',constituents,cap)
            _,ef=piece(p,pn+'_fan','service_cell','sector',smat,[0,0,(low+high)/2],dict(rmin=rin+wall,rmax=rout-wall,length=length,start=math.pi/12-span/2,angle=span),side,z,phi)
            ef['constituent_volumes_mm3']=dict(constituents)
            for index,wr in enumerate((rin,rout-wall)):
                piece(p,pn+f'_fanwall{index}','tray','sector','Aluminium',[0,0,(low+high)/2],dict(rmin=wr,rmax=wr+wall,length=length,start=math.pi/12-span/2,angle=span),side,z,phi)
    # Join points after each fan. Endcap-only cumulative mass; combined capacity
    # is checked independently without double-allocating the barrel corridor.
    joins=[z+85 for z in c['disc_z_mm']]+[3500]
    rin,rout,_,_=c['trunk_mm'];wall=c['tray_wall_mm'];angle=c['phi_fraction']*math.pi/6
    for side in (1,-1):
        for n,(low,high) in enumerate(zip(joins,joins[1:]),1):
            for sector in range(12):
                start=(sector+.5)*math.pi/6-angle/2;length=high-low;h=3*n;manifolds=math.ceil(n/8)
                cap=angle/2*((rout-wall)**2-(rin+wall)**2)*length
                cv=h*length*math.pi/4*c['power_cable_OD_mm']**2;fv=cv*(c['fibre_cable_OD_mm']/c['power_cable_OD_mm'])**2
                constituents=dict(Copper=.2*cv,Polyimide=.3*cv+.5*fv,Air=.5*cv,Silica=.5*fv,Titanium=0.,CO2=0.)
                for od,diam in zip(c['trunk_pipe_OD_mm'],c['trunk_pipe_ID_mm']):
                    constituents['Titanium']+=manifolds*length*math.pi/4*(od*od-diam*diam);constituents['CO2']+=manifolds*length*math.pi/4*diam*diam
                name=f'trunk_{side}_{n}_{sector}';smat=mat.effective(name,constituents,cap)
                _,e=piece(det,name,'service_cell','sector',smat,[0,0,side*(low+high)/2],dict(rmin=rin+wall,rmax=rout-wall,length=length,start=start,angle=angle));e['constituent_volumes_mm3']=constituents
                for i,wr in enumerate((rin,rout-wall)):piece(det,name+f'_wall{i}','tray','sector','Aluminium',[0,0,side*(low+high)/2],dict(rmin=wr,rmax=wr+wall,length=length,start=start,angle=angle))
    out.mkdir(parents=True,exist_ok=True);write(out/'short-strip-endcap.xml',doc);write(out/'materials.xml',mat.root)
    expected=dict(status='PROTOTYPE',counts=dict(Counter(e['role'] for e in entities)),entities=entities,material_totals=dict(totals),materials=mat.recipes,readout='ShortStripEndcapHits',cell_mm=c['cell_mm'],provenance=dict(input_sha256=sha(INPUT),producer_sha256=sha(__file__),model_sha256=sha(Path(__file__).with_name('model.py')),pins=c['input_sha256']))
    (out/'expected.json').write_text(json.dumps(expected,separators=(',',':'))+'\n')
    print(json.dumps(expected['counts']));return expected

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'build/short-strip-endcap/compact');a=p.parse_args();export(load(),a.output)
