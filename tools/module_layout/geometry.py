#!/usr/bin/env python3
"""PROTOTYPE finite sensor patches; all study dimensions live in sensor_models.json.

Patch IDs identify ACTS surfaces. sensor_id identifies one physical silicon die,
module_id identifies an assembly (two sensors for a stereo long-strip sandwich).
No masks are cropped to nominal layers or the host. These are conditional trial
occupied boxes, not a DD4hep model or a buildability/material certification.
"""
from __future__ import annotations

import copy
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODELS_PATH = Path(__file__).with_name("sensor_models.json")
REVIEW_MODELS_PATH = Path(__file__).with_name("review_models.json")
LAYOUTS_PATH = ROOT / "docs/design/DES-006-named-layouts.json"
LEGACY_VARIANTS = ("flat", "staggered", "tilted", "hybrid", "hybrid_clearance", "staggered_clearance")
REVIEW_VARIANTS = ("review_default", "review_pixel_z", "review_short_tilt", "review_pixel_z_short_tilt")
VARIANTS = LEGACY_VARIANTS + REVIEW_VARIANTS
PIXEL_FAMILIES = ("single", "double", "quad", "mixed")


def add(a, b):
    return [x + y for x, y in zip(a, b)]


def scale(a, k):
    return [k * x for x in a]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]


def norm(a):
    return math.sqrt(dot(a, a))


def load_models(path=MODELS_PATH):
    return json.loads(Path(path).read_text())


def validate_models(models):
    """Reject unsupported footprints and nonphysical numerical inputs explicitly."""
    if models.get("schema_version") != 1:
        raise ValueError("sensor model schema_version must be 1")
    for subsystem in ("pixel", "short_strip", "long_strip"):
        model = models[subsystem]
        if model.get("shape") != "rectangle":
            raise ValueError("only explicit rectangle sensor models are supported; do not approximate other shapes")
        for key, value in model.items():
            if key.endswith("_mm") and (not math.isfinite(value) or value < 0):
                raise ValueError(f"{subsystem}.{key} must be finite and nonnegative")
        dimensions = ("chip_active_u_mm", "chip_active_v_mm") if subsystem == "pixel" else ("active_u_mm", "active_v_mm")
        if any(model[key] <= 0 for key in dimensions):
            raise ValueError(f"{subsystem} active dimensions must be positive")
    if models["long_strip"]["separation_mm"] <= models["long_strip"]["sensor_thickness_mm"]:
        raise ValueError("long-strip sensor mid-plane separation must exceed silicon thickness")
    if models["long_strip"]["endcap_rings"] < 2:
        raise ValueError("long-strip endcap_rings must be at least two")


def _review_policy(models, variant):
    """Resolve explicit subsystem controls without changing historical models."""
    try:
        register = models["review_placement"]
        policies = copy.deepcopy(register["barrel"])
        overrides = register["variants"][variant]
    except KeyError as error:
        raise ValueError("review variants require a complete review_placement model") from error
    if register["inclined_barrel_sections"]:
        raise ValueError("review default supports no inclined barrel-end sections")
    for subsystem, change in overrides.items():
        policies[subsystem].update(change)
    for policy in policies.values():
        if not all(isinstance(policy[key], bool) for key in ("phi_stagger", "z_stagger")):
            raise ValueError("review phi/z staggering controls must be boolean")
        if policy["phi_method"] not in ("radial", "tilted"):
            raise ValueError("review phi method must be radial or tilted")
        if policy["z_row_policy"] not in ("fit_endpoints", "fixed_body_pitch_cover"):
            raise ValueError("unknown review no-z row policy")
        angle = policy["tilt_degrees"]
        if not math.isfinite(angle) or not 0 <= angle < 90:
            raise ValueError("review tilt must be finite and in [0,90) degrees")
        if policy["phi_method"] == "radial" and angle != 0:
            raise ValueError("radial phi staggering uses tangential modules, without tilt")
        if policy["phi_method"] == "tilted" and (angle == 0 or not policy["phi_stagger"]):
            raise ValueError("tilted phi staggering requires nonzero tilt and phi staggering")
    return policies


def _linear_centres(lo, hi, width, pitch, cover):
    """Even symmetric rows. Cover uses full-width edges; flat retains honest gaps."""
    span = hi - lo
    if span <= width:
        return [(lo + hi)/2]
    n = max(1, math.ceil((span-width)/pitch)+1) if cover else max(1, math.floor(span/pitch))
    step = (span-width)/(n-1) if cover and n > 1 else pitch
    return [(lo+hi)/2 + (i-(n-1)/2)*step for i in range(n)]


def _family(layer, pixel_family, models):
    if layer["subsystem"] != "pixel":
        return layer["subsystem"]
    if pixel_family != "mixed":
        return pixel_family
    # A1 in the two innermost barrels; B4 elsewhere: only two module families.
    return "single" if layer["kind"] == "cylinder" and layer["r_m"]*1000 < models["placement"]["mixed_single_barrel_radius_max_mm"] else "quad"


def _shape(family, models):
    if family in models["pixel"]["families"]:
        p = models["pixel"]
        nx, ny = p["families"][family]
        au, av, gap = p["chip_active_u_mm"], p["chip_active_v_mm"], p["interchip_gap_mm"]
        width, height = nx*au+(nx-1)*gap, ny*av+(ny-1)*gap
        su, sv = width + 2*p["guard_mm"], height + 2*p["guard_mm"]
        # Outer readout periphery lies on one outer edge for A1/A2, two for B4.
        periphery = p["approximate_die_v_mm"] - av
        die_v = height + min(ny, 2)*periphery
        body_u = max(su, nx*p["approximate_die_u_mm"]+(nx-1)*gap) + 2*p["body_service_u_mm"]
        body_v = max(sv, die_v) + 2*p["body_service_v_mm"]
        patches = [( (ix-(nx-1)/2)*(au+gap), (iy-(ny-1)/2)*(av+gap), au/2, av/2)
                   for ix in range(nx) for iy in range(ny)]
        # A single peripheral ledge shifts the trial body centre, not active patches.
        return dict(width=width, height=height, sensor_u=su, sensor_v=sv,
                    body_u=body_u, body_v=body_v, body_w=p["body_thickness_mm"],
                    body_v_offset=periphery/2 if ny == 1 else 0., patches=patches,
                    spacing=models["placement"]["pixel_level_spacing_mm"], faces=1)
    p = models[family]
    width, height = p["active_u_mm"], p["active_v_mm"]
    su, sv = width + 2*p["guard_mm"], height + 2*p["guard_mm"]
    angle = p.get("relative_stereo_rad", 0.)/2
    bw, bv = su*math.cos(angle)+sv*math.sin(angle), sv*math.cos(angle)+su*math.sin(angle)
    thick = (p["separation_mm"]+p["sensor_thickness_mm"]+2*p["external_allowance_per_face_mm"]
             if family == "long_strip" else p["body_thickness_mm"])
    return dict(width=width, height=height, sensor_u=su, sensor_v=sv,
                body_u=bw+2*p["body_service_u_mm"], body_v=bv+2*p["body_service_v_mm"],
                body_w=thick, body_v_offset=0., patches=[(0., 0., width/2, height/2)],
                spacing=p["level_spacing_mm"], faces=2 if family == "long_strip" else 1)


def _corners(body):
    return [add(body["center_mm"], add(scale(body["u"], a*body["half_u_mm"]),
            add(scale(body["v"], b*body["half_v_mm"]), scale(body["n"], c*body["half_w_mm"]))))
            for a,b,c in itertools.product((-1,1), repeat=3)]


def _extent(body):
    corners = _corners(body)
    rmax = max(math.hypot(p[0],p[1]) for p in corners)
    rmin = min(math.hypot(p[0],p[1]) for p in corners)
    # The radial minimum can lie on an edge, not at a corner.
    for i,a in enumerate(corners):
        for j,b in enumerate(corners):
            if j <= i or (i ^ j) not in (1,2,4):
                continue
            dx,dy = b[0]-a[0], b[1]-a[1]
            den = dx*dx+dy*dy
            t = max(0.,min(1.,-(a[0]*dx+a[1]*dy)/den)) if den else 0.
            rmin = min(rmin,math.hypot(a[0]+t*dx,a[1]+t*dy))
    return rmin,rmax,min(p[2] for p in corners),max(p[2] for p in corners)


def generate_layout(candidate, variant, pixel_family="mixed", *, models=None, models_path=None,
                    layouts_path=None):
    """Return deterministic active patches, trial bodies and unmodified ideal layers.

    ``candidate`` is cobe/pint or a candidate dict with id and layers. ``models``
    overrides the full numerical model; alternatively supply models_path. Source
    paths/hashes and model-content hash remain in returned metadata.
    """
    if variant not in VARIANTS or pixel_family not in PIXEL_FAMILIES:
        raise ValueError("unknown placement variant or pixel family")
    if models is not None and models_path is not None:
        raise ValueError("supply models or models_path, not both")
    review = variant in REVIEW_VARIANTS
    default_models_path = REVIEW_MODELS_PATH if review else MODELS_PATH
    models = copy.deepcopy(models) if models is not None else load_models(models_path or default_models_path)
    layouts_path = Path(layouts_path or LAYOUTS_PATH)
    validate_models(models)
    catalogue = json.loads(layouts_path.read_text())
    chosen = (next(c for c in catalogue["candidates"] if c["id"] == candidate)
              if isinstance(candidate,str) else copy.deepcopy(candidate))
    review_policy = _review_policy(models, variant) if review else None
    if review and any(layer["kind"] == "inclined_ring" for layer in chosen["layers"]):
        raise ValueError("review variants require unshortened cylindrical barrels: use cobe, not inclined pint")
    effective_policy = {}
    result = dict(candidate=chosen["id"], variant=variant, pixel_family=pixel_family,
                  status="PROTOTYPE; unsigned sensor/placement hypotheses", layers=copy.deepcopy(chosen["layers"]),
                  modules=[], bodies=[], metadata={})
    placement = models["placement"]
    mid = sid = pid = 0
    for layer_index,layer in enumerate(chosen["layers"]):
        family = _family(layer,pixel_family,models)
        shape = _shape(family,models)
        region = {"cylinder":"barrel", "disc":"endcap", "inclined_ring":"inclined"}[layer["kind"]]
        clearance = review or variant.endswith("_clearance")
        base_variant = "staggered" if review else variant.removesuffix("_clearance")
        strategy = ("flat" if region == "barrel" else "staggered") if base_variant == "hybrid" else base_variant
        cover = strategy != "flat"
        sub = layer["subsystem"]
        policy = review_policy[sub] if review and region == "barrel" else None
        if policy is not None:
            cover = policy["phi_stagger"]
        longitudinal_cover = policy["z_stagger"] if policy is not None else cover
        ou = placement[sub+"_overlap_u_mm"] if cover else 0.
        ov = placement[sub+"_overlap_v_mm"] if longitudinal_cover else 0.
        pu = shape["width"]-ou if cover else shape["body_u"]+placement["body_clearance_mm"]
        pv = shape["height"]-ov if longitudinal_cover else shape["body_v"]+placement["body_clearance_mm"]
        if pu <= 0 or pv <= 0:
            raise ValueError("overlap must be smaller than active module span")
        tilt = math.radians(placement["tilt_degrees"]) if strategy == "tilted" and region != "inclined" else 0.
        if policy is not None:
            tilt = math.radians(policy["tilt_degrees"])
        pu *= math.cos(tilt)
        if region == "barrel":
            radius = layer["r_m"]*1000
            rows = _linear_centres(layer["z_min_m"]*1000,layer["z_max_m"]*1000,shape["height"],pv,longitudinal_cover)
            if policy is not None and not longitudinal_cover:
                low_z, high_z = layer["z_min_m"]*1000,layer["z_max_m"]*1000
                row_span = high_z-low_z-shape["height"]
                if policy["z_row_policy"] == "fit_endpoints":
                    row_count = max(1,math.floor(row_span/pv)+1)
                    row_pitch = row_span/(row_count-1) if row_count>1 else pv
                else:
                    row_count = max(1,math.ceil(row_span/pv)+1)
                    row_pitch = pv
                rows = [(low_z+high_z)/2+(i-(row_count-1)/2)*row_pitch for i in range(row_count)]
        elif region == "endcap":
            low,high = layer["r_min_m"]*1000,layer["r_max_m"]*1000
            margin = (models["long_strip"]["endcap_radial_margin_mm"] if sub == "long_strip" else placement["end_margin_mm"])
            if cover and sub == "long_strip":
                nr = models[sub]["endcap_rings"]
                rows = [low-margin+shape["height"]/2+i*(high-low+2*margin-shape["height"])/(nr-1) for i in range(nr)]
            else:
                rows = _linear_centres(low-(margin if cover else 0),high+(margin if cover else 0),shape["height"],pv,cover)
        else:
            rows = [layer["z0_m"]*1000]
        for row,q in enumerate(rows):
            radius = q if region == "endcap" else (layer["r_m"] if region == "barrel" else layer["r0_m"])*1000
            phi_radius = (radius+shape["height"]/2 if cover else max(1.,radius-shape["body_v"]/2)) if region == "endcap" else radius
            # Exact tangent-plane angular span for barrel; outer radius controls endcap coverage.
            angular_pitch = 2*math.atan2(pu/2,phi_radius)
            nphi = max(4,math.ceil(2*math.pi/angular_pitch) if cover else math.floor(2*math.pi/angular_pitch))
            colours = placement["clearance_pixel_phi_colours"] if clearance and sub == "pixel" and region == "endcap" else 2
            if policy is not None:
                colours = 2 if cover and policy["phi_method"] == "radial" else 1
            if cover:
                nphi = colours*math.ceil(nphi/colours)  # periodic seam has matching colour cycle
            spacing = shape["spacing"]
            if clearance and cover and region == "barrel":
                sagitta = math.hypot(radius,shape["body_u"]/2)-radius
                spacing = max(spacing,shape["body_w"]+placement["clearance_curvature_sagitta_factor"]*sagitta+placement["clearance_body_gap_mm"])
            if policy is not None:
                radial_half = (shape["body_u"]*abs(math.sin(tilt))+shape["body_w"]*abs(math.cos(tilt)))/2
                tangential_half = (shape["body_u"]*abs(math.cos(tilt))+shape["body_w"]*abs(math.sin(tilt)))/2
                spacing = max(shape["spacing"],2*radial_half+placement["clearance_curvature_sagitta_factor"]*(math.hypot(radius,tangential_half)-radius)+placement["clearance_body_gap_mm"])
                z_levels = 2 if longitudinal_cover and len(rows)>1 else 1
                effective_policy[layer["id"]] = dict(policy,phi_colours=colours,z_levels=z_levels,radial_spacing_mm=spacing if colours*z_levels>1 else 0.,radial_body_projection_mm=2*radial_half,nominal_z_pitch_mm=pv,actual_z_pitch_mm=rows[1]-rows[0] if len(rows)>1 else None,phi_columns=nphi,rows=len(rows),stagger_displacement_direction="radial",unrotated_active_z_extent_mm=[rows[0]-shape["height"]/2,rows[-1]+shape["height"]/2],nominal_z_extent_mm=[layer["z_min_m"]*1000,layer["z_max_m"]*1000])
            elif review:
                effective_policy[layer["id"]] = dict(phi_stagger=True,r_stagger=True,tilt_degrees=0.,method="historical clearance endcap",phi_colours=colours,radial_levels=2,normal_spacing_mm=spacing)
            for col in range(nphi):
                phase = (row%2)*.5 if cover else 0.
                if policy is not None:
                    phase = (row%2)*.5 if longitudinal_cover else 0.
                phi = 2*math.pi*(col+phase)/nphi
                er,eu = [math.cos(phi),math.sin(phi),0.],[-math.sin(phi),math.cos(phi),0.]
                if region == "barrel":
                    v,n,center = [0.,0.,1.],er,[radius*er[0],radius*er[1],q]
                elif region == "endcap":
                    v,n,center = scale(er,-1.),[0.,0.,1.],[radius*er[0],radius*er[1],layer["z_m"]*1000]
                else:
                    nr,nz = layer["normal_r"],layer["normal_z"]
                    v,n = [-nz*er[0],-nz*er[1],nr],[nr*er[0],nr*er[1],nz]
                    center = [radius*er[0],radius*er[1],layer["z0_m"]*1000]
                u = eu
                if tilt:
                    u,n = add(scale(u,math.cos(tilt)),scale(n,math.sin(tilt))),add(scale(n,math.cos(tilt)),scale(u,-math.sin(tilt)))
                level = ((col%colours)-(colours-1)/2 if len(rows) == 1 else ((col%colours)+colours*(row%2))-(2*colours-1)/2) if cover else 0.
                if policy is not None:
                    level = (col%colours)+colours*(row%2 if z_levels>1 else 0)-(colours*z_levels-1)/2
                displacement_axis = er if policy is not None else n
                center = add(center,scale(displacement_axis,level*spacing))
                # Shift rows alternately in the meridional direction, without changing normal.
                shift = ((col%2)-.5)*ov/2 if cover else 0.
                if policy is not None:
                    shift = ((col%2)-.5)*ov/2 if longitudinal_cover else 0.
                if region != "inclined":
                    center = add(center,scale(v,shift))
                mid += 1
                body = dict(module_id=mid, layer_id=layer["id"], station_id=layer.get("station_group",layer["id"]),
                            subsystem=sub,region=region,family=family,level=level,level_spacing_mm=spacing,normal_offset_mm=level*spacing,row=row,col=col,
                            center_mm=add(center,scale(v,shape["body_v_offset"])),u=u,v=v,n=n,
                            half_u_mm=shape["body_u"]/2,half_v_mm=shape["body_v"]/2,half_w_mm=shape["body_w"]/2)
                if policy is not None:
                    body.update(radial_offset_mm=level*spacing,normal_offset_mm=level*spacing*math.cos(tilt),phi_stagger=policy["phi_stagger"],phi_method=policy["phi_method"],z_stagger=policy["z_stagger"],tilt_degrees=policy["tilt_degrees"],stagger_displacement_direction="radial")
                if region == "inclined":
                    rv = -layer["normal_z"]
                    zv = layer["normal_r"]
                    a = ((layer["r1_m"]-layer["r0_m"])*rv+(layer["z1_m"]-layer["z0_m"])*zv)*1000
                    b = ((layer["r2_m"]-layer["r0_m"])*rv+(layer["z2_m"]-layer["z0_m"])*zv)*1000
                    body["ideal_meridional_extent_mm"] = sorted([a,b])
                    body["active_overhang_mm"] = [max(0.,min(a,b)+shape["height"]/2),max(0.,shape["height"]/2-max(a,b))]
                result["bodies"].append(body)
                for face in range(shape["faces"]):
                    sid += 1
                    stereo = (face-.5)*models[sub]["relative_stereo_rad"] if sub == "long_strip" else 0.
                    su = add(scale(u,math.cos(stereo)),scale(v,math.sin(stereo)))
                    sv = add(scale(v,math.cos(stereo)),scale(u,-math.sin(stereo)))
                    face_center = add(center,scale(n,(face-.5)*models[sub]["separation_mm"])) if sub == "long_strip" else center
                    for patch_index,(du,dv,hu,hv) in enumerate(shape["patches"]):
                        pid += 1
                        result["modules"].append(dict(id=pid,sensor_id=sid,module_id=mid,layer_id=layer["id"],
                            station_id=body["station_id"],subsystem=sub,region=region,
                            center_mm=add(face_center,add(scale(su,du),scale(sv,dv))),u=su,v=sv,n=n,
                            half_u_mm=hu,half_v_mm=hv,sensor_area_mm2=shape["sensor_u"]*shape["sensor_v"],
                            active_area_mm2=4*hu*hv,family=family,face=face,patch=patch_index,
                            level=level,row=row,col=col))
    model_hash = hashlib.sha256(json.dumps(models,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    result["metadata"] = dict(model_sha256=model_hash,models=models,
         layout_sha256=hashlib.sha256(Path(layouts_path).read_bytes()).hexdigest(),host=catalogue["host"],
         classification="NODD DESIGN CHOICE — unsigned placement fixtures; source parameters retain original classification",
         pixel_sensor_area_status="Conditional gross sensor-outline fixture; excludes readout-chip silicon",
         hit_contract="Deduplicate id patches by sensor_id; require both faces of same module_id for long-strip pair; station_id deduplicates inclined rings",
         summary=summarize(result),host_diagnostics=host_diagnostics(result,catalogue["host"]))
    if review:
        for layer in chosen["layers"]:
            if layer["kind"] != "cylinder":
                continue
            records = [m for m in result["modules"] if m["layer_id"] == layer["id"]]
            zlow = min(m["center_mm"][2]-m["half_u_mm"]*abs(m["u"][2])-m["half_v_mm"]*abs(m["v"][2]) for m in records)
            zhigh = max(m["center_mm"][2]+m["half_u_mm"]*abs(m["u"][2])+m["half_v_mm"]*abs(m["v"][2]) for m in records)
            info = effective_policy[layer["id"]]
            info["actual_active_z_extent_mm"] = [zlow,zhigh]
            info["active_z_overhang_mm"] = [max(0.,layer["z_min_m"]*1000-zlow),max(0.,zhigh-layer["z_max_m"]*1000)]
            bodies = [b for b in result["bodies"] if b["layer_id"] == layer["id"]]
            body_low = min(min(p[2] for p in _corners(b)) for b in bodies)
            body_high = max(max(p[2] for p in _corners(b)) for b in bodies)
            info["body_z_extent_mm"] = [body_low,body_high]
            info["body_z_overhang_mm"] = [max(0.,layer["z_min_m"]*1000-body_low),max(0.,body_high-layer["z_max_m"]*1000)]
        result["metadata"]["review_placement"] = dict(barrel=review_policy,layers=effective_policy,interpretations=models["review_placement"]["interpretations"])
    return result


def summarize(layout):
    groups = defaultdict(lambda: dict(modules=0,sensors=0,patches=0,sensor_area_m2=0.,active_area_m2=0.))
    sensor_seen,module_seen = set(),set()
    for p in layout["modules"]:
        keys = ["total",p["subsystem"],p["subsystem"]+"/"+p["region"]]
        for key in keys:
            g = groups[key]
            g["patches"] += 1
            g["active_area_m2"] += p["active_area_mm2"]*1e-6
            if p["sensor_id"] not in sensor_seen:
                g["sensors"] += 1
                g["sensor_area_m2"] += p["sensor_area_mm2"]*1e-6
            if p["module_id"] not in module_seen:
                g["modules"] += 1
        sensor_seen.add(p["sensor_id"])
        module_seen.add(p["module_id"])
    return dict(groups)


def host_diagnostics(layout, host=None):
    host = host or layout["metadata"]["host"]
    limits = [host["r_min_m"]*1000,host["r_max_m"]*1000,host["abs_z_max_m"]*1000]
    overflow,by_layer = [],defaultdict(lambda: dict(r_min_mm=math.inf,r_max_mm=0.,abs_z_max_mm=0.,modules=0,overflow_modules=0,normal_min_mm=math.inf,normal_max_mm=-math.inf,normal_levels=[]))
    inclined = []
    for b in layout["bodies"]:
        r0,r1,z0,z1 = _extent(b)
        g = by_layer[b["layer_id"]]
        g["modules"] += 1
        offset = b.get("normal_offset_mm",0.)
        g["normal_min_mm"] = min(g["normal_min_mm"],offset-b["half_w_mm"])
        g["normal_max_mm"] = max(g["normal_max_mm"],offset+b["half_w_mm"])
        if offset not in g["normal_levels"]:
            g["normal_levels"].append(offset)
        g["r_min_mm"] = min(g["r_min_mm"],r0)
        g["r_max_mm"] = max(g["r_max_mm"],r1)
        g["abs_z_max_mm"] = max(g["abs_z_max_mm"],abs(z0),abs(z1))
        excess = [max(0.,limits[0]-r0),max(0.,r1-limits[1]),max(0.,abs(z0)-limits[2],abs(z1)-limits[2])]
        if max(excess)>1e-9:
            g["overflow_modules"] += 1
            overflow.append(dict(module_id=b["module_id"],layer_id=b["layer_id"],excess_r_inner_outer_z_mm=excess))
        if max(b.get("active_overhang_mm",[0.,0.]))>1e-9:
            inclined.append(dict(module_id=b["module_id"],layer_id=b["layer_id"],active_overhang_mm=b["active_overhang_mm"]))
    for g in by_layer.values():
        g["normal_levels"].sort()
        g["normal_envelope_mm"] = g["normal_max_mm"]-g["normal_min_mm"]
    return dict(host_overflow_modules=len(overflow),host_overflow_examples=overflow[:20],layers=dict(by_layer),
                inclined_overhang_modules=len(inclined),inclined_overhang_examples=inclined[:20],
                note="Trial occupied boxes; body periphery may be unsigned. Full module surfaces retained outside ideal segments and host.")


def _obb_overlap(a,b,tolerance=1e-7):
    """Interior intersection of two oriented boxes by all 15 separating axes."""
    aa,bb = [a[k] for k in ("u","v","n")],[b[k] for k in ("u","v","n")]
    ah,bh = [a[k] for k in ("half_u_mm","half_v_mm","half_w_mm")],[b[k] for k in ("half_u_mm","half_v_mm","half_w_mm")]
    delta = [b["center_mm"][i]-a["center_mm"][i] for i in range(3)]
    for axis in aa+bb+[cross(x,y) for x in aa for y in bb]:
        size = norm(axis)
        if size < 1e-10:
            continue
        ra = sum(h*abs(dot(axis,x)) for h,x in zip(ah,aa))
        rb = sum(h*abs(dot(axis,x)) for h,x in zip(bh,bb))
        if abs(dot(delta,axis)) >= ra+rb-tolerance*size:
            return False
    return True


def body_overlap_diagnostics(layout, *, cell_mm=64., tolerance_mm=1e-7):
    """All-body spatial-hash broad phase then exact OBB SAT, incl. cross layers.

    Trial occupied boxes enclose allowances, so overlaps reject a fixture without
    claiming silicon collision. Zero overlap only clears these boxes, not supports.
    """
    bins = defaultdict(list)
    bodies = layout["bodies"]
    aabbs = []
    for i,b in enumerate(bodies):
        corners = _corners(b)
        lo = [min(c[d] for c in corners) for d in range(3)]
        hi = [max(c[d] for c in corners) for d in range(3)]
        aabbs.append((lo,hi))
        for cell in itertools.product(*(range(math.floor(lo[d]/cell_mm),math.floor(hi[d]/cell_mm)+1) for d in range(3))):
            bins[cell].append(i)
    tested = set()
    overlap,same_level,cross_layer = 0,0,0
    examples,by_pair = [],Counter()
    for indices in bins.values():
        for i,j in itertools.combinations(indices,2):
            pair = (min(i,j),max(i,j))
            if pair in tested:
                continue
            tested.add(pair)
            alo,ahi = aabbs[i]
            blo,bhi = aabbs[j]
            if any(ahi[d] <= blo[d]+tolerance_mm or bhi[d] <= alo[d]+tolerance_mm for d in range(3)):
                continue
            a,b = bodies[i],bodies[j]
            if _obb_overlap(a,b,tolerance_mm):
                overlap += 1
                same_level += a["layer_id"] == b["layer_id"] and a["level"] == b["level"]
                cross_layer += a["layer_id"] != b["layer_id"]
                key = "/".join(sorted([a["subsystem"],b["subsystem"]]))
                by_pair[key] += 1
                if len(examples)<30:
                    examples.append(dict(module_ids=[a["module_id"],b["module_id"]],layers=[a["layer_id"],b["layer_id"]],levels=[a["level"],b["level"]]))
    return dict(overlapping_body_pairs=overlap,same_layer_same_level_pairs=same_level,cross_layer_pairs=cross_layer,
                by_subsystem_pair=dict(by_pair),examples=examples,tolerance_mm=tolerance_mm,
                tested_broad_phase_pairs=len(tested),method="3D oriented trial occupied-box SAT, 15 axes; all module pairs spatial-hash filtered; no shared supports/cooling modeled")
