#!/usr/bin/env python3
"""Standalone DES-020 compact; explicit constituents and conserved service cells."""
import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

from model import ROOT, INPUT, build, load, frame, sha
sys.path.insert(0,str(ROOT/"tools/pixel_barrel_dd4hep"))
from materials import Materials


def xmlwrite(path,node):
    ET.indent(node,space="  ")
    ET.ElementTree(node).write(path,encoding="utf-8",xml_declaration=True)


def export(c,output):
    layout=build(c)
    materials=Materials(dict(coolant_density_g_cm3=1.0,cfrp_carbon_mass_fraction=.70,
                             module=dict(flex_copper_coverage=.5)),
        dict(density_g_cm3=dict(titanium=4.51,graphite=2.21,insulation=1.42,
                               glue=2.0,CFRP=1.73,foam=.20)))
    materials.add("Aluminium",2.70,{"Al":1})
    materials.add("Silica",2.20,{"Si":1,"O":2},atoms=True)
    # Explicit conductive carbon-foam core; thermal conductivity is a hypothesis.
    materials.add("CarbonFoam",.20,{"C":1})
    materials.effective("BumpFixture",{"Copper":.15},1)
    materials.effective("SignalFlex",{"Copper":.085,"Polyimide":.915},1)
    materials.effective("ElectronicsFixture",{"Silicon":.04,"Copper":.01,"Polyimide":.10},1)
    doc=ET.Element("lccdd")
    ET.SubElement(doc,"info",name="nODDShortStripBarrel",title="DES-020 isolated prototype",author="nODD",version="0.1",status="prototype")
    ET.SubElement(ET.SubElement(doc,"includes"),"gdmlFile",ref="materials.xml")
    defs=ET.SubElement(doc,"define")
    for axis,size in zip("xyz",c["world_half_size_mm"]):
        ET.SubElement(defs,"constant",name="world_"+axis,value=f"{size}*mm")
    # MC-truth region bounds enclose all active barrel sensors; match the
    # finite-plane validation host. Off-stave passive services are outside it.
    ET.SubElement(defs,"constant",name="tracker_region_rmax",value="800*mm")
    ET.SubElement(defs,"constant",name="tracker_region_zmax",value="1400*mm")
    readout=ET.SubElement(ET.SubElement(doc,"readouts"),"readout",name="ShortStripBarrelHits")
    ET.SubElement(readout,"segmentation",type="CartesianGridXY",grid_size_x=f"{c['cell_mm'][0]}*mm",
        grid_size_y=f"{c['cell_mm'][1]}*mm",offset_x=f"{c['cell_mm'][0]/2}*mm",offset_y=f"{c['cell_mm'][1]/2}*mm")
    ET.SubElement(readout,"id").text="system:5,layer:3,stave:7,module:5,sensor:1,x:-11,y:-10"
    detector=ET.SubElement(ET.SubElement(doc,"detectors"),"detector",name="ShortStripBarrel",
        id=str(c["system_id"]),type="nODDShortStripBarrel",readout="ShortStripBarrelHits")
    ET.SubElement(detector,"sensitive",type="tracker")
    entities=[]; totals=defaultdict(lambda:dict(volume_mm3=0.,mass_g=0.))

    def entity(name,role,center,volume=None,material=None,**extra):
        item=dict(name=name,role=role,center_mm=center,**extra)
        if volume is not None:
            item.update(volume_mm3=volume,material=material,
                        mass_g=volume*materials.recipes[material]["density_g_cm3"]/1000)
            totals[material]["volume_mm3"]+=volume
            totals[material]["mass_g"]+=item["mass_g"]
        entities.append(item)
        return item

    def piece(parent,name,role,kind,material,center,dims,phi=0,r=0,ids=None,**extra):
        node=ET.SubElement(parent,"piece",name=name,kind=kind,material=material,role=role,
                           **{k:format(float(v),".17g")+"*mm" for k,v in zip(("u","v","w"),center)})
        for k,v in dims.items():
            node.set(k,format(float(v),".17g")+("*rad" if k in ("start","angle") else "*mm"))
        if kind=="box":volume=dims["sx"]*dims["sy"]*dims["sz"]
        elif kind in ("tube","sector"):
            volume=(dims.get("angle",2*math.pi)/2)*(dims["rmax"]**2-dims["rmin"]**2)*dims["length"]
        elif kind=="torus":
            volume=dims["angle"]*math.pi*dims["major"]*(dims["rmax"]**2-dims["rmin"]**2)
        else:raise ValueError(kind)
        if ids is not None:
            node.set("sensitive","true");node.set("sensor",str(ids["sensor"]))
        item=entity(name,role,frame(phi,r,center),volume,material,**extra)
        if ids is not None:
            item.update(ids=ids,normal=[math.cos(phi),math.sin(phi),0],
                u=[-math.sin(phi),math.cos(phi),0],v=[0,0,1],
                size_mm=[dims["sx"],dims["sy"],dims["sz"]])
        return node,item

    by_stave=defaultdict(list)
    for m in layout["modules"]:by_stave[m["layer"],m["stave"]].append(m)
    for layer_info in layout["layers"]:
        lid=layer_info["layer"];r0=layer_info["nominal_radius_mm"]
        lname=f"L{lid}"
        layer=ET.SubElement(detector,"layer",name=lname,id=str(lid))
        entity(lname,"layer",[0,0,0])
        for s in [s for s in layout["staves"] if s["layer"]==lid]:
            name=s["name"];phi=s["phi_rad"];r=s["radius_mm"]
            stave=ET.SubElement(layer,"stave",name=name,id=str(s["stave"]),
                phi=format(phi,".17g")+"*rad",radius=str(r)+"*mm")
            entity(name,"stave",frame(phi,r,[0,0,0]))
            def add(suffix,role,mat,center,size):
                return piece(stave,name+"_"+suffix,role,"box",mat,center,
                    dict(zip(("sx","sy","sz"),size)),phi,r)
            for label,w,thickness,mat in (("front_skin",-1.375,.15,"CFRP"),
                    ("front_glue",-1.5,.1,"Epoxy"),("back_glue",-6.6,.1,"Epoxy"),
                    ("back_skin",-6.725,.15,"CFRP")):
                add(label,"support",mat,[0,0,w],[c["stave_width_mm"],2420,thickness])
            core,item=add("core","core","CarbonFoam",[0,0,-4.05],[c["stave_width_mm"],2420,5])
            removed=0
            for side in (-1,1):
                for leg in (-1,1):
                    center=[leg*c["tube_offset_u_mm"],side*(c["loop_start_mm"]+1210)/2,c["tube_w_mm"]]
                    dims=dict(rmin=0,rmax=c["tube_OD_mm"]/2,length=1210-c["loop_start_mm"])
                    hole=ET.SubElement(core,"cut",kind="tube",**{k:str(v)+"*mm" for k,v in dims.items()},
                        u=str(center[0])+"*mm",v=str(center[1])+"*mm",w="0*mm")
                    removed+=math.pi*dims["rmax"]**2*dims["length"]
                    for role,mat,rmin,rmax in (("cooling_tube","Titanium",c["tube_OD_mm"]/2-c["tube_wall_mm"],c["tube_OD_mm"]/2),
                            ("coolant","CO2",0,c["tube_OD_mm"]/2-c["tube_wall_mm"])):
                        piece(stave,f"{name}_{side}_{leg}_{role}",role,"tube",mat,center,
                              dict(rmin=rmin,rmax=rmax,length=dims["length"]),phi,r)
                start=math.pi if side>0 else 0
                center=[0,side*c["loop_start_mm"],c["tube_w_mm"]]
                hole=ET.SubElement(core,"cut",kind="torus",major=str(c["tube_offset_u_mm"])+"*mm",
                    rmin="0*mm",rmax=str(c["tube_OD_mm"]/2)+"*mm",angle=str(math.pi)+"*rad",
                    start=str(start)+"*rad",u="0*mm",v=str(center[1])+"*mm",w="0*mm")
                removed+=math.pi**2*c["tube_offset_u_mm"]*(c["tube_OD_mm"]/2)**2
                for role,mat,rmin,rmax in (("cooling_bend","Titanium",c["tube_OD_mm"]/2-c["tube_wall_mm"],c["tube_OD_mm"]/2),
                        ("coolant_bend","CO2",0,c["tube_OD_mm"]/2-c["tube_wall_mm"])):
                    piece(stave,f"{name}_{side}_{role}",role,"torus",mat,center,
                        dict(major=c["tube_offset_u_mm"],rmin=rmin,rmax=rmax,start=start,angle=math.pi),phi,r)
            item["volume_mm3"]-=removed
            delta=removed*materials.recipes["CarbonFoam"]["density_g_cm3"]/1000
            item["mass_g"]-=delta;totals["CarbonFoam"]["volume_mm3"]-=removed;totals["CarbonFoam"]["mass_g"]-=delta
            # Power bus is deliberately behind the cold sandwich, separate from pickups.
            add("power_insulation","power_bus","Polyimide",[0,0,-6.875],[26,2420,.15])
            for side in (-1,1):
                add(f"power_{side}","power_bus","Copper",[side*6.25,0,-7.05],[12,2420,c["power_bus_copper_mm"]])
            add("signal_bus","signal_bus","SignalFlex",[20,0,-6.85],[8,2420,.1])
            for m in by_stave[lid,s["stave"]]:
                mid=m["name"];z=m["center_mm"][2];w=m["lift_mm"]
                module=ET.SubElement(stave,"module",name=mid,id=str(m["row"]),z=str(z)+"*mm",lift=str(w)+"*mm")
                entity(mid,"module",m["center_mm"])
                def mod(label,role,mat,u,v,dw,size,sensitive=False):
                    node,item=piece(module,mid+"_"+label,role,"box",mat,[u,v,dw],
                        dict(zip(("sx","sy","sz"),size)),phi,0,
                        ids=dict(system=c["system_id"],layer=lid,stave=s["stave"],module=m["row"],sensor=0) if sensitive else None)
                    item["center_mm"]=frame(phi,r,[u,v+z,dw+w])
                    return node,item
                mod("active","sensitive","Silicon",0,0,0,c["active_mm"],True)
                for side in (-1,1):
                    mod(f"guard_u{side}","guard","Silicon",side*24.25,0,0,[.5,97,.2])
                    mod(f"guard_v{side}","guard","Silicon",0,side*48.25,0,[48,.5,.2])
                mod("bumps","interconnect","BumpFixture",0,0,-.1125,[48,96,.025])
                for ix in (-1,1):
                    for iy in (-3,-1,1,3):
                        mod(f"ASIC_{ix}_{iy}","readout","Silicon",ix*12,iy*12,-.2,[23.4,23.4,.15])
                for label,mat,dw,thickness in (("ASIC_glue","Epoxy",-.325,.1),
                        ("spreader","Graphite",-.475,.2),("isolation","Polyimide",-.5875,.025),
                        ("backing_glue","Epoxy",-.65,.1),("backing","CFRP",-.8,.2)):
                    mod(label,"module_passive",mat,0,0,dw,[48,96,thickness])
                for side in (-1,1):
                    mod(f"flex{side}","module_flex","SignalFlex",0,side*50,-.5,[49,3,.1])
                    # Wrap outside the 52 mm core; front/back bridges meet the
                    # vertical tail at disjoint faces. Never drive flex through foam.
                    top=w-.55;bottom=-6.8
                    add(f"M{m['row']}_tail{side}","module_tail","SignalFlex",
                        [26.30,side*50+z,(top+bottom)/2],[.1,3,top-bottom])
                    add(f"M{m['row']}_front_bridge{side}","module_tail","SignalFlex",
                        [(24.5+26.35)/2,side*50+z,w-.5],[26.35-24.5,3,.1])
                    add(f"M{m['row']}_back_bridge{side}","module_tail","SignalFlex",
                        [(24+26.35)/2,side*50+z,-6.85],[26.35-24,3,.1])
                    height=w+.4
                    add(f"M{m['row']}_pickup{side}","thermal_pickup","Graphite",
                        [side*10, z,-1.3+height/2],[20,c["pickup_mm"][1],height])
            for side in (-1,1):
                add(f"end_board{side}","end_board","ElectronicsFixture",[0,side*1230,4],[52,30,8])
            for index,z in enumerate(c["bearing_z_mm"]):
                # Feet meet the circular ring tangentially; no coincident mother solids.
                inner=r0-c["ring_inset_mm"]+c["ring_radial_mm"]
                back=r-7.15
                add(f"foot{index}","foot","CFRP",[0,z,(inner+back)/2-r],
                    [c["foot_width_mm"],c["ring_axial_mm"],back-inner])
        for index,z in enumerate(c["bearing_z_mm"]):
            inner=r0-c["ring_inset_mm"]
            # Rings use global cylindrical coordinates, not the local stave frame.
            piece(layer,f"{lname}_ring{index}","ring","sector","CFRP",[0,0,z],
                dict(rmin=inner,rmax=inner+c["ring_radial_mm"],length=c["ring_axial_mm"],start=0,angle=2*math.pi))
            entities[-1]["center_mm"]=[0,0,z]
    for side in (-1,1):
        for sector in layout["sectors"]:
            i=sector["sector"]
            phi=(i+.5)*2*math.pi/c["sectors"]
            angle=c["phi_fraction"]*2*math.pi/c["sectors"]
            selected=[r for r in layout["routes"] if r["side"]==side and r["sector"]==i]
            for zone,bounds in (("collector",c["collector_mm"]),("trunk",c["trunk_mm"])):
                rin,rout,zlo,zhi=bounds
                wall=c["tray_wall_mm"]
                cap=angle/2*((rout-wall)**2-(rin+wall)**2)*(zhi-zlo)
                constituents=defaultdict(float)
                if zone=="collector":
                    # Radial collection plus two R50 quarter-turn reservations.
                    staves={(s["layer"],s["stave"]):s for s in layout["staves"]}
                    cable_volume=sum(r["harnesses"]*(750-staves[r["layer"],r["stave"]]["radius_mm"]+math.pi*50)
                        *math.pi/4*c["power_cable_OD_mm"]**2 for r in selected)
                    fibre_volume=cable_volume*(c["fibre_cable_OD_mm"]/c["power_cable_OD_mm"])**2
                    pipe_length=sum(750-staves[r["layer"],r["stave"]]["radius_mm"]+math.pi*25 for r in selected)*2
                    constituents["Titanium"]+=pipe_length*math.pi/4*(c["tube_OD_mm"]**2-(c["tube_OD_mm"]-2*c["tube_wall_mm"])**2)
                    constituents["CO2"]+=pipe_length*math.pi/4*(c["tube_OD_mm"]-2*c["tube_wall_mm"])**2
                else:
                    cable_volume=sum(r["harnesses"] for r in selected)*(zhi-zlo)*math.pi/4*c["power_cable_OD_mm"]**2
                    fibre_volume=cable_volume*(c["fibre_cable_OD_mm"]/c["power_cable_OD_mm"])**2
                    for od,diameter in zip(c["trunk_pipe_OD_mm"],c["trunk_pipe_ID_mm"]):
                        constituents["Titanium"]+=sector["manifolds"]*(zhi-zlo)*math.pi/4*(od*od-diameter*diameter)
                        constituents["CO2"]+=sector["manifolds"]*(zhi-zlo)*math.pi/4*diameter*diameter
                constituents["Copper"]+=cable_volume*.2
                constituents["Polyimide"]+=cable_volume*.3+fibre_volume*.5
                constituents["Air"]+=cable_volume*.5
                constituents["Silica"]+=fibre_volume*.5
                mat=materials.effective(f"SS_{zone}_{side}_{i}",constituents,cap)
                name=f"{zone}_{side}_{i}"
                dims=dict(rmin=rin+wall,rmax=rout-wall,length=zhi-zlo,start=phi-angle/2,angle=angle)
                piece(detector,name,"service_cell","sector",mat,[0,0,side*(zlo+zhi)/2],dims)
                entities[-1]["center_mm"]=[0,0,side*(zlo+zhi)/2]
                entities[-1]["constituent_volumes_mm3"]=dict(constituents)
                for face in (0,1):
                    wr=rin if face==0 else rout-wall
                    piece(detector,name+f"_wall{face}","tray","sector","Aluminium",[0,0,side*(zlo+zhi)/2],
                        dict(rmin=wr,rmax=wr+wall,length=zhi-zlo,start=phi-angle/2,angle=angle))
                    entities[-1]["center_mm"]=[0,0,side*(zlo+zhi)/2]
    output.mkdir(parents=True,exist_ok=True)
    xmlwrite(output/"short-strip-barrel.xml",doc)
    xmlwrite(output/"materials.xml",materials.root)
    expected=dict(status="PROTOTYPE",counts=dict(Counter(e["role"] for e in entities)),entities=entities,
        materials=materials.recipes,material_totals=dict(totals),readout="ShortStripBarrelHits",cell_mm=c["cell_mm"],
        provenance=dict(input_sha256=sha(INPUT),producer_sha256=sha(__file__),
                        model_sha256=sha(Path(__file__).with_name("model.py")),pins=c["input_sha256"]))
    (output/"expected.json").write_text(json.dumps(expected,separators=(",",":"))+"\n")
    print(json.dumps(expected["counts"],sort_keys=True))
    return expected


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,default=INPUT)
    p.add_argument("--output",type=Path,default=ROOT/"build/short-strip-barrel/compact")
    a=p.parse_args();export(load(a.input),a.output)
