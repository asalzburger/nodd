"""Explicit logical-role transport of the retained effective PR100 profiles."""
import copy
import math
import re


def role_key(role):
    return tuple((k,role[k]) for k in ("kind","system","layer","detector","side","volume") if k in role)


def roles(surface):
    return tuple(sorted(role_key(r) for r in surface["roles"]))


def area(surface):
    (r0,z0),(r1,z1)=surface["rz_segment_mm"]
    return 2*math.pi*r0*(z1-z0) if surface["type"]=="cylinder" else math.pi*(r1*r1-r0*r0)


def bin_areas(material,surface):
    if material["type"]=="homogeneous":return [area(surface)]
    data=material["data"]
    if any(len(row)!=1 for row in data):raise ValueError("Only retained phi1 carrier profiles supported")
    n=len(data);(r0,z0),(r1,z1)=surface["rz_segment_mm"]
    if surface["type"]=="cylinder":return [area(surface)/n]*n
    return [math.pi*((r0+(r1-r0)*(i+1)/n)**2-(r0+(r1-r0)*i/n)**2) for i in range(n)]


def integrated_budget(material,surface,helper):
    weights=bin_areas(material,surface);result={"X0_mm2":0.,"L0_mm2":0.,"mass_g":0.}
    for row,a in zip(material["data"],weights):
        b=helper.budget(row[0])
        for key,quantity in (("X0_mm2","X0"),("L0_mm2","L0"),("mass_g","areal_mass_g_mm2")):
            result[key]+=a*b[quantity]
    return result


def select_candidate(geometry, config, variant, selector):
    manifest=selector(geometry,config)
    extra=variant.get("additional_pixel_disk")
    if not extra:return manifest
    for system,sign in ((2,-1),(3,1)):
        layer=extra["layer_id"]
        record=next(s for s in manifest["surfaces"] if any(r.get("kind")=="sensitive_layer" and r.get("system")==system and r.get("layer")==layer for r in s["roles"]))
        record["roles"]=[r for r in record["roles"] if not (r.get("kind")=="sensitive_layer" and r.get("system")==system and r.get("layer")==layer)]
        if not record["roles"]:manifest["surfaces"].remove(record)
        volume=next(v for v in geometry["volumes"] if v["name"]==f"System{system}Layer{layer}")
        target_z=volume["z_min_mm"] if sign<0 else volume["z_max_mm"]
        choices=[s for s in geometry["portals"] if s["surface_id"] in volume["portal_surface_ids"] and s["type"]=="disc" and abs(s["z_mm"]-target_z)<1.e-8]
        if len(choices)!=1:raise ValueError("Additional disk downstream portal is ambiguous")
        p=choices[0]
        if any(s["geometry_id"]==p["geometry_id"] for s in manifest["surfaces"]):
            raise ValueError("Additional homogeneous disk shares an already assigned material carrier")
        manifest["surfaces"].append({"geometry_id":p["geometry_id"],"surface_id":p["surface_id"],
            "material_key":f'nodd-gen3-portal-{p["geometry_id"]}',"type":"disc","rz_segment_mm":p["rz_segment_mm"],
            "bins":{"phi":1,"r":1},"owners":p["owners"],"roles":[{"kind":"sensitive_layer","system":system,"layer":layer,"detector":"pixel","side":"after","binning_family":"additional_pixel_homogeneous","requested_bins":{"phi":1,"r":1}}]})
    manifest["surfaces"].sort(key=lambda s:s["geometry_id"])
    manifest["counts"].update(unique_surfaces=len(manifest["surfaces"]),
        material_bins=sum(s["bins"]["phi"]*s["bins"].get("z",s["bins"].get("r")) for s in manifest["surfaces"]))
    return manifest


def homogenize(material, helper):
    data=material["data"]
    binning=material["binUtility"]["binningdata"]
    radial=next(b for b in binning if b["value"]=="AxisR")
    phi=next(b for b in binning if b["value"]=="AxisPhi")
    if phi["bins"]!=1 or len(data)!=radial["bins"] or any(len(r)!=1 for r in data):
        raise ValueError("Homogeneous reference requires the retained phi1/radial profile")
    lo,hi,n=radial["min"],radial["max"],radial["bins"]
    weights=[(lo+(hi-lo)*(i+1)/n)**2-(lo+(hi-lo)*i/n)**2 for i in range(n)]
    return helper.homogenize([row[0] for row in data],weights)


def transport(source_manifest, target_manifest, source_map, variant, helper, ratios=None):
    ratios=ratios or {}
    old_by_role={roles(s):s for s in source_manifest["surfaces"]}
    if len(old_by_role)!=len(source_manifest["surfaces"]):raise ValueError("Ambiguous old logical material roles")
    source_entries={x["key"]:x for x in source_map["KeyedSurfaces"]}
    if set(source_entries)!={s["material_key"] for s in source_manifest["surfaces"]}:
        raise ValueError("Source profile keys differ from frozen manifest")
    seen=set();payload=[];audit=[]
    extra=variant.get("additional_pixel_disk")
    for target in target_manifest["surfaces"]:
        key=roles(target);added=False
        if key in old_by_role:
            old=old_by_role[key];seen.add(key)
        else:
            rr=target["roles"]
            if not extra or len(rr)!=1 or rr[0].get("layer")!=extra["layer_id"] or rr[0].get("system") not in (2,3) or rr[0].get("side")!="after":
                raise ValueError(f"Missing/ambiguous candidate material role: {key}")
            system=rr[0]["system"]
            donors=[s for s in source_manifest["surfaces"] if any(r.get("kind")=="sensitive_layer" and r.get("system")==system and r.get("layer")==extra["donor_layer"] for r in s["roles"])]
            if len(donors)!=1:raise ValueError("Additional material donor is ambiguous")
            old=donors[0];added=True
        original=source_entries[old["material_key"]]["material"]
        material=copy.deepcopy(original)
        inventory=[]
        for role in target["roles"]:
            sy,ly=role.get("system"),role.get("layer")
            inventory.append(ratios.get(f"{sy}:{ly}",1.) if role["kind"]=="sensitive_layer" else 1.)
        if max(inventory)-min(inventory)>1.e-12:
            raise ValueError("Conflicting inventory scaling on indivisible shared layer/gap carrier")
        ratio=inventory[0]
        old_area,new_area=area(old),area(target)
        if old["type"]!=target["type"]:raise ValueError("Logical carrier changed surface type")
        if added:
            slab=homogenize(material,helper)
            material={"type":"homogeneous","mappingType":material.get("mappingType",0),"mapMaterial":True,"data":[[slab]]}
            scale=1.
        else:
            scale=ratio*old_area/new_area
            if abs(scale-1.)<1.e-12:scale=1.
            scales=[ratio*a/b for a,b in zip(bin_areas(original,old),bin_areas(material,target))]
            scales=[1. if abs(x-1.)<1.e-12 else x for x in scales]
            for row,bin_scale in zip(material["data"],scales):
                if bin_scale!=1.:
                    for slab in row:slab["thickness"]*=bin_scale
            if target["rz_segment_mm"]!=old["rz_segment_mm"]:
                utility=material["binUtility"]
                (r0,z0),(r1,z1)=target["rz_segment_mm"]
                axis=next(b for b in utility["binningdata"] if b["value"] in ("AxisR","AxisZ"))
                if target["type"]=="disc":axis.update(min=r0,max=r1)
                else:axis.update(min=z0,max=z1)
                # The native utility transform maps global to the local carrier
                # coordinates, and serialized translation is its surface centre.
                utility["transform"]={"rotation":None,"translation":[0.,0.,z0 if target["type"]=="disc" else 0.]}
        payload.append({"geometry_id":target["geometry_id"],"key":target["material_key"],"material":material})
        slabs=[x for row in material["data"] for x in row]
        source_budget=integrated_budget(original,old,helper)
        target_budget=integrated_budget(material,target,helper)
        expected_ratio=new_area/old_area if added else ratio
        residuals={k:(target_budget[k]/(value*expected_ratio)-1. if value else target_budget[k]) for k,value in source_budget.items()}
        if any(abs(v)>3.e-6 for v in residuals.values()):
            raise ValueError("Effective carrier X0/L0/mass inventory failed area-Jacobian closure")
        audit.append({"target_key":target["material_key"],"source_key":old["material_key"],"roles":target["roles"],
            "source_area_mm2":old_area,"target_area_mm2":new_area,"inventory_ratio":ratio,
            "thickness_scale":(scales[0] if max(scales)-min(scales)<1.e-12 else None) if not added else 1.,
            "whole_carrier_area_ratio":old_area/new_area,"added_inventory":added,
            "per_bin_area_jacobian":not added,"bin_scale_range":[min(scales),max(scales)] if not added else [1.,1.],
            "source_integrated_budget":source_budget,"target_integrated_budget":target_budget,"relative_inventory_residuals":residuals,
            "homogeneous_budget":helper.budget(slabs[0]) if added else None})
    if seen!=set(old_by_role):raise ValueError("Candidate omitted a retained material role")
    return {"KeyedSurfaces":sorted(payload,key=lambda x:x["key"]),"Surfaces":source_map.get("Surfaces",{}),"Volumes":source_map.get("Volumes",{})},audit


def group_volumes(geometry):
    result={}
    for v in geometry["volumes"]:
        match=re.fullmatch(r"System(\d+)Layer(\d+)",v["name"])
        if match:result[tuple(map(int,match.groups()))]=(v["geometry_id"]>>56)&255
    if not result or len(set(result.values()))!=len(result):raise ValueError("Nonunique logical layer/volume identities")
    return result


def remap_errors(table, old_geometry, new_geometry, donors, pooled=False):
    old,new=group_volumes(old_geometry),group_volumes(new_geometry)
    if pooled:
        by_volume={v:[g for g in table["groups"] if g["volume"]==v] for v in old.values()}
    else:
        by_volume={e["volume"]:e for e in table["entries"]}
    result=copy.deepcopy(table);entries=[]
    for logical,volume in sorted(new.items(),key=lambda x:x[1]):
        source=donors.get(logical,logical)
        if source not in old or old[source] not in by_volume:raise ValueError("Missing logical calibration source")
        if pooled:
            for entry in by_volume[old[source]]:
                e=copy.deepcopy(entry);e["volume"]=volume;entries.append(e)
        else:
            e=copy.deepcopy(by_volume[old[source]]);e["volume"]=volume;entries.append(e)
    result["groups" if pooled else "entries"]=entries
    if pooled:result["volumes"]=len(new)
    return result
