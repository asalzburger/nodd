#!/usr/bin/env python3
"""Export the pinned DES039/040 PROTOTYPE as empty DD4hep Air reservations.

No production integration, field, sensitive surfaces, tube dimensions or magnet
composition is introduced. XML dimensions carry explicit metre/radian units.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

try:
    from . import templates
except ImportError:
    import templates

ROOT = Path(__file__).resolve().parents[2]
SOURCE_REVISION = "cae3a72f3b1c98edaf9bc28a84d019142606ba25"
SOURCE_PATH = "docs/validation/DES-040/sketched-stagger-2026-10-20/candidate/geometry.json"
SOURCE_SHA256 = "7b2b0de109a5ec4a908e4f91a05e9caf9bdedfa6141b09d7c82a98b56e7cfc02"
ELEMENTS_PATH = "detector/config/elements.json"
ELEMENTS_SHA256 = "22f2968258a363e8bed8bda4aed741485579441926d850ef4b54bbf7aba66c90"
SYSTEM_ID = 9  # Isolated prototype ID; no production readout contract.


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_source():
    data = subprocess.check_output(
        ["git", "show", f"{SOURCE_REVISION}:{SOURCE_PATH}"], cwd=ROOT
    )
    if sha(data) != SOURCE_SHA256:
        raise ValueError("Pinned muon source SHA-256 mismatch")
    return json.loads(data)


def number(value):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("Nonfinite muon parameter")
    return format(value, ".17g")


def metres(value):
    return number(value) + "*m"


def write_xml(path, root):
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def validate_panel(panel):
    p, q = panel["vertices_m"], panel["basis"]
    if len(p) != 4 or any(len(v) != 2 for v in p):
        raise ValueError("Chamber must have four face vertices")
    if len(q) != 3 or any(len(row) != 3 for row in q):
        raise ValueError("Chamber basis must be 3x3")
    values = [x for v in p for x in v] + [x for row in q for x in row]
    values += panel["origin_m"] + [panel["depth_m"]]
    if not all(math.isfinite(x) for x in values) or panel["depth_m"] <= 0:
        raise ValueError("Invalid finite positive-depth chamber")
    for i in range(3):
        for j in range(3):
            if abs(sum(q[k][i] * q[k][j] for k in range(3)) - (i == j)) > 1e-12:
                raise ValueError("Chamber basis is not orthonormal")
    determinant = sum(q[0][i] * (q[1][(i+1)%3]*q[2][(i+2)%3] -
                       q[1][(i+2)%3]*q[2][(i+1)%3]) for i in range(3))
    if abs(determinant - 1) > 1e-12:
        raise ValueError("Chamber basis is not right handed")
    cross = []
    for i in range(4):
        a,b,c = p[i],p[(i+1)%4],p[(i+2)%4]
        cross.append((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]))
    if min(cross) <= 0:
        raise ValueError("Chamber footprint must be strictly convex CCW")


def materials():
    """Same provisional Air/Vacuum recipes as the existing prototype tools."""
    root = ET.Element("materials")
    # Complete pinned table is required by ROOT's mixture/element registration;
    # sparse Z tables fail in TGeoMixture::AddElement on the supported runtime.
    data = subprocess.check_output(["git","show",f"{SOURCE_REVISION}:{ELEMENTS_PATH}"],cwd=ROOT)
    if sha(data)!=ELEMENTS_SHA256:
        raise ValueError("Pinned natural-element table SHA-256 mismatch")
    for item in json.loads(data)["elements"]:
        name,z,a=item["name"],item["Z"],item["A"]
        node = ET.SubElement(root,"element",name=name,formula=name,Z=str(z))
        ET.SubElement(node,"atom",type="A",value=str(a),unit="g/mol")
    for name,density,composition in (
        ("Air",.0012,{"N":.754,"O":.234,"Ar":.012}),
        ("Vacuum",1e-12,{"H":1.0}),
    ):
        node = ET.SubElement(root,"material",name=name)
        ET.SubElement(node,"D",value=number(density),unit="g/cm3")
        for ref,fraction in composition.items():
            ET.SubElement(node,"fraction",n=number(fraction),ref=ref)
    return root


def export(output, source=None):
    source = load_source() if source is None else source
    panels = sorted(source["panels"],key=lambda x:x["id"])
    if len(panels)!=936 or len({p["id"] for p in panels})!=936:
        raise ValueError("Expected 936 unique pinned chamber IDs")
    magnetic = source["magnetic_configuration"]
    if magnetic["folds"]!=12 or set(magnetic["coil_groups"])!={"barrel","endcap_plus","endcap_minus"}:
        raise ValueError("Expected three C12 toroid groups")
    output = Path(output)
    output.mkdir(parents=True,exist_ok=True)
    root = ET.Element("lccdd")
    ET.SubElement(root,"info",name="nODDMuon",title="DES039/040 empty Air PROTOTYPE",
                  author="nODD",version="0.1",status="prototype")
    ET.SubElement(ET.SubElement(root,"includes"),"gdmlFile",ref="materials.xml")
    define = ET.SubElement(root,"define")
    # Computational world only: 1m beyond the source's 9.4m radial /13.05m z bound.
    for axis,size in zip("xyz",(10.4,10.4,14.05)):
        ET.SubElement(define,"constant",name="world_"+axis,value=metres(size))
    display = ET.SubElement(root,"display")
    ET.SubElement(display,"vis",name="MuonChamberVis",r="0.15",g="0.35",b="0.85",alpha="0.35",visible="true",showDaughters="true")
    ET.SubElement(display,"vis",name="MuonWarmVis",r="0.85",g="0.25",b="0.15",alpha="0.35",visible="true",showDaughters="true")
    detector = ET.SubElement(ET.SubElement(root,"detectors"),"detector",
        id=str(SYSTEM_ID),name="MuonSystem",type="nODDMuonPrototype")
    for panel in panels:
        validate_panel(panel)
    model,entities = templates.factor(panels,SYSTEM_ID)
    templates.to_xml(detector,model,number,metres)
    groups = []
    for index,key in enumerate(("barrel","endcap_plus","endcap_minus"),1):
        group = magnetic["coil_groups"][key]
        a,b = magnetic["warm"]["normal_m"]/2,magnetic["warm"]["tangent_m"]/2
        rho,hr,hz = (group[k] for k in ("corner_radius_m","half_r_m","half_z_m"))
        if not all(math.isfinite(x) for x in group.values()) or not 0<a<rho<min(hr,hz) or b<=0:
            raise ValueError("Invalid rounded-racetrack warm reservation")
        attrs = dict(name="MuonWarm_"+key,group=str(index),folds="12",phi=number(math.radians(group["phi_offset_deg"]))+"*rad")
        attrs.update({out:metres(group[original]) for out,original in (
            ("center_r","center_r_m"),("center_z","center_z_m"),("half_r","half_r_m"),
            ("half_z","half_z_m"),("corner","corner_radius_m"))})
        attrs.update(normal=metres(2*a),tangent=metres(2*b))
        ET.SubElement(detector,"toroid",**attrs)
        groups.append(dict(name=attrs["name"],source_group=key,ids=dict(system=SYSTEM_ID,group=index),
            coil_ids=[f"{key}/C{k:02d}" for k in range(12)],configuration=group))
    write_xml(output/"muon-system.xml",root)
    write_xml(output/"materials.xml",materials())
    expected = dict(schema_version=1,status="PROTOTYPE; empty Air reservations only",
        source=dict(revision=SOURCE_REVISION,path=SOURCE_PATH,sha256=SOURCE_SHA256),
        elements_source=dict(revision=SOURCE_REVISION,path=ELEMENTS_PATH,sha256=ELEMENTS_SHA256),
        generator_sha256=sha(Path(__file__).read_bytes()),
        templates_sha256=sha(Path(templates.__file__).read_bytes()),
        chamber_templates=model,
        template_summary=dict(template_count=len(model["templates"]),barrel_templates=15,endcap_templates=7,
            phi_orbits=len(model["orbits"]),rows=sum(len(o["rows"]) for o in model["orbits"]),
            longitudinal_loop_rows=sum(r["count"]>1 for o in model["orbits"] for r in o["rows"]),
            explicit_placements=len(model["explicit"]),
            maximum_group_shape_residual_m=max(t["maximum_shape_residual_m"] for t in model["templates"]),
            maximum_expansion_vertex_residual_m=templates.compare_expansion(templates.expand(model,SYSTEM_ID),entities,model["templates"]),
            matching_tolerance_m=templates.MATCH_M),
        counts=dict(chambers=936,warm_groups=3,warm_coil_definitions=36,sensitive=0),
        chamber_counts=dict(sorted(Counter(p["id"].split("/")[0] for p in panels).items())),
        entities=entities,groups=groups,warm_widths_m=magnetic["warm"],
        exported_sha256={p:sha((output/p).read_bytes()) for p in ("muon-system.xml","materials.xml")},
        scope="Exact source chamber prisms and shared union warm reservations; supports, HCAL, coils' material, magnetic field and MDT internals absent.")
    (output/"expected.json").write_text(json.dumps(expected,indent=2,sort_keys=True)+"\n")
    return expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    expected = export(args.output)
    print(json.dumps(expected["counts"],sort_keys=True))


if __name__=="__main__":
    main()
