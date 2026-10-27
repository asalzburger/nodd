"""Isolated DES040 XML placement changes; shared exports/factories stay frozen."""
import copy
import math
import re
from pathlib import Path
import xml.etree.ElementTree as ET


def number(value):
    value = float(value.removesuffix("*mm").removesuffix("*rad"))
    if not math.isfinite(value):
        raise ValueError("Nonfinite compact parameter")
    return value


def length(node, key):
    return number(node.get(key))


def put(node, key, value, unit="mm"):
    node.set(key, f"{value:.17g}*{unit}")


def rename(node, suffix):
    for part in node.iter():
        if part.get("name"):
            part.set("name", part.get("name") + suffix)


def stave_radial_extent(stave):
    """Conservative radial support of complete pixel local box assemblies."""
    intervals = []
    for part in stave:
        if part.tag in ("slab", "core"):
            intervals.append((length(part, "w") - length(part, "thickness")/2,
                              length(part, "w") + length(part, "thickness")/2,
                              length(part, "width")/2))
        elif part.tag == "module":
            for item in part:
                if item.tag == "sensor":
                    w = 0.
                elif item.tag in ("die", "passive"):
                    w = length(item, "w")
                else:
                    continue
                intervals.append((w-length(item, "thickness")/2, w+length(item, "thickness")/2,
                                  abs(length(item, "u"))+length(item, "width")/2))
    r = length(stave, "radius")
    offset = abs(length(stave, "offset_u")) if stave.get("offset_u") else 0.
    return min(r+a for a, b, u in intervals), max(math.hypot(r+b, u+offset) for a, b, u in intervals)


def transform(source, variant):
    if variant.get("schema_version") != 1 or not isinstance(variant.get("id"), str):
        raise ValueError("Expected named candidate schema1")
    if set(variant)-{"schema_version", "id", "pixel_barrel", "pixel_disks_abs_z_mm", "additional_pixel_disk"}:
        raise ValueError("Unsupported candidate controls")
    tree = ET.parse(source)
    root = tree.getroot()
    pixel = root.find('./detectors/detector[@id="1"]')
    changes, ratios = [], {}
    pipe = root.find('./detectors/detector[@id="0"]/dimensions')
    pipe_outer = length(pipe, "rmax")
    baseline_outer = max(stave_radial_extent(s)[1] for s in pixel.findall('./layer/stave'))
    for key, settings in variant.get("pixel_barrel", {}).items():
        if set(settings)-{"radius_mm", "staves"}:
            raise ValueError("Unsupported barrel control")
        layer = pixel.find(f'layer[@id="{int(key)}"]')
        if layer is None:
            raise ValueError("Unknown pixel barrel layer")
        staves = layer.findall("stave")
        old_count = len(staves)
        nominal = sum(length(s, "radius") for s in staves)/old_count
        new_r = settings.get("radius_mm", nominal)
        new_count = settings.get("staves", old_count)
        if type(new_count) is not int or not 2 <= new_count <= 64 or new_count % 2:
            raise ValueError("Pixel counts require even alternating staves within six-bit ID field")
        if type(new_r) not in (int, float) or not math.isfinite(new_r) or new_r <= 0:
            raise ValueError("Invalid pixel radius")
        delta = new_r - nominal
        ratios[1, int(key)] = new_count/old_count
        if abs(delta) < 1.e-12 and new_count == old_count:
            continue
        feet = layer.findall("foot")
        grouped_feet = []
        for stave in staves:
            phi = length(stave, "phi")
            grouped_feet.append([f for f in feet if abs(math.remainder(length(f,"phi")-phi, 2*math.pi)) < 1.e-8])
        for item in staves + feet:
            layer.remove(item)
        for j in range(new_count):
            k = j if j < old_count else j % 2
            stave = copy.deepcopy(staves[k])
            old_phi = length(staves[k], "phi")
            phi = 2*math.pi*j/new_count
            stave.set("id", str(j)); put(stave, "radius", length(stave,"radius")+delta)
            put(stave, "phi", phi, "rad")
            if new_count != old_count:
                rename(stave, f"_opt{j}")
            lo, hi = stave_radial_extent(stave)
            if lo <= pipe_outer or hi > baseline_outer + 1.e-8:
                raise ValueError("Candidate complete stave exceeds pipe/subsystem radial allocation")
            layer.append(stave)
            for old in grouped_feet[k]:
                foot = copy.deepcopy(old)
                for attr in ("back_radius", "outer_radius"):
                    put(foot, attr, length(foot,attr)+delta)
                put(foot, "phi", length(foot,"phi") + phi-old_phi, "rad")
                if new_count != old_count:
                    rename(foot, f"_opt{j}")
                layer.append(foot)
        for ring in layer.findall("ring"):
            for attr in ("rmin", "rmax"):
                put(ring, attr, length(ring,attr)+delta)
        # Column-owned longitudinal cable pieces move with the full layer.
        # Global end manifolds, cages and transport trunks remain untouched.
        services = pixel.findall("service")
        by_column = {}
        pattern = re.compile(rf"cable_A-pixel-B{int(key)}-c(\d+)-")
        for service in services:
            match = pattern.match(service.get("name", ""))
            if match:
                by_column.setdefault(int(match.group(1)), []).append(service)
                pixel.remove(service)
        if by_column and set(by_column) != set(range(old_count)):
            raise ValueError("Local cable column ownership differs from staves")
        for j in range(new_count):
            k = j if j < old_count else j % 2
            for old in by_column.get(k, []):
                service = copy.deepcopy(old)
                a, b = length(old,"rmin"), length(old,"rmax")
                new_a, new_b = a+delta, b+delta
                if new_a <= pipe_outer:
                    raise ValueError("Local service intrudes into pipe")
                put(service,"rmin",new_a);put(service,"rmax",new_b)
                # Preserve exact wedge volume when its radius changes.
                width = length(old,"phi_width")*(b*b-a*a)/(new_b*new_b-new_a*new_a)
                if width >= 2*math.pi/new_count:
                    raise ValueError("Local cable wedges overlap adjacent columns")
                put(service,"phi_width",width,"rad")
                put(service,"phi",length(old,"phi")+2*math.pi*j/new_count-length(staves[k],"phi"),"rad")
                if new_count != old_count:
                    service.set("name", pattern.sub(f"cable_A-pixel-B{int(key)}-c{j:02d}-", old.get("name")))
                pixel.append(service)
        changes.append({"system":1,"layer":int(key),"old_radius_mm":nominal,"radius_mm":new_r,
                        "old_staves":old_count,"staves":new_count,"inventory_ratio":new_count/old_count})
    # Full-phi rings can intersect another layer's continuous stave support.
    # Check its actual radial support and z interval, not nominal sensor radii.
    layers=pixel.findall("layer")
    for owner in layers:
        for ring in owner.findall("ring"):
            a,b=length(ring,"rmin"),length(ring,"rmax")
            zlo,zhi=length(ring,"z")-length(ring,"length")/2,length(ring,"z")+length(ring,"length")/2
            for other in layers:
                if other is owner:continue
                for stave in other.findall("stave"):
                    r=length(stave,"radius")
                    for part in stave:
                        if part.tag not in ("slab","core"):continue
                        cz=length(part,"center_y");half=length(stave,"length")/2
                        if zhi<=cz-half or zlo>=cz+half:continue
                        lo=r+length(part,"w")-length(part,"thickness")/2
                        hi=math.hypot(r+length(part,"w")+length(part,"thickness")/2,length(part,"width")/2+abs(length(stave,"offset_u")))
                        if min(b,hi)-max(a,lo)>1.e-8:
                            raise ValueError(f"Annular ring from pixel layer{owner.get('id')} intersects layer{other.get('id')} stave support")
    # Existing readout layer IDs are retained even if z ordering changes.
    new_disk = variant.get("additional_pixel_disk")
    donors = {}
    for system, sign in ((2,-1),(3,1)):
        detector = root.find(f'./detectors/detector[@id="{system}"]')
        discs = detector.findall("disc")
        max_z = max(abs(length(d,"z")) for d in discs)
        for key, absolute_z in variant.get("pixel_disks_abs_z_mm", {}).items():
            disc = detector.find(f'disc[@id="{int(key)}"]')
            if disc is None or not 614.936 <= absolute_z <= max_z:
                raise ValueError("Pixel disc outside frozen barrel/endcap allocation or unknown ID")
            put(disc,"z",sign*absolute_z)
        if new_disk:
            if set(new_disk) != {"abs_z_mm","donor_layer","layer_id"}:
                raise ValueError("Invalid additional disk controls")
            donor, identity, z = new_disk["donor_layer"], new_disk["layer_id"], new_disk["abs_z_mm"]
            if type(identity) is not int or not 0 <= identity < 16 or detector.find(f'disc[@id="{identity}"]') is not None:
                raise ValueError("Additional disc ID conflicts or exceeds four-bit field")
            source_disc = detector.find(f'disc[@id="{donor}"]')
            if source_disc is None or not 614.936 <= z <= max_z:
                raise ValueError("Invalid additional disc donor/allocation")
            cloned = copy.deepcopy(source_disc)
            cloned.set("id",str(identity));rename(cloned,f"_added{identity}");put(cloned,"z",sign*z)
            detector.append(cloned);donors[system,identity]=(system,donor)
        datums = sorted(abs(length(d,"z")) for d in detector.findall("disc"))
        if any(b-a < 77.636 for a,b in zip(datums,datums[1:])):
            raise ValueError("Pixel disc assemblies/collectors have less than 77.636mm axial separation")
    return tree, {"variant":variant,"barrel_changes":changes,
        "inventory_ratios":{f"{s}:{l}":v for (s,l),v in ratios.items()},
        "calibration_donors":{f"{s}:{l}":list(v) for (s,l),v in donors.items()},
        "pipe_outer_mm":pipe_outer,
        "mechanical_checks":"Conservative complete-stave pipe/allocation, cable wedge and disc separation screens; native full overlap check remains separate",
        "fixed_interfaces":"Cages, global end manifolds, transport trunks, readout descriptors and world constants untouched",
        "ring_interpretation":"Both global radii shifted; wall/radial span and local width/length preserved; circumference and foot clipping curvature change"}


def export(source, variant, output):
    tree, audit = transform(source, variant)
    output = Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    if not audit["barrel_changes"] and not variant.get("pixel_disks_abs_z_mm") and not variant.get("additional_pixel_disk"):
        output.write_bytes(Path(source).read_bytes())
    else:
        tree.write(output, encoding="utf-8", xml_declaration=True)
    return audit
