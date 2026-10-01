#!/usr/bin/env python3
"""Audit the pixel import and make portable nodehammer projects (display only)."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/pixel_barrel_dd4hep"))
from export_root import style_name

MM_PER_CM = 10.0
METRES_PER_CM = 0.01
CENTRE_TOLERANCE_MM = 1e-8


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mv(matrix, vector):
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def transforms(nodes):
    """Compose the documented column-major semantic matrices, in ROOT cm."""
    result = {}

    def visit(key):
        if key in result:
            return result[key]
        node = nodes[key]
        flat = node.get("locRot", [1, 0, 0, 0, 1, 0, 0, 0, 1])
        rotation = [[flat[c * 3 + r] for c in range(3)] for r in range(3)]
        translation = node.get("locTrl", [0, 0, 0])
        if "parentId" in node:
            parent_rotation, parent_translation = visit(node["parentId"])
            translation = [a + b for a, b in zip(mv(parent_rotation, translation), parent_translation)]
            rotation = [[sum(parent_rotation[r][k] * rotation[k][c] for k in range(3))
                         for c in range(3)] for r in range(3)]
        result[key] = rotation, translation
        return result[key]

    for key in nodes:
        visit(key)
    return result


def entity_name(node, nodes):
    name = node["name"]
    if name == "substrate":
        return nodes[node["parentId"]]["name"] + "_substrate"
    if name.startswith("sensor_"):
        return nodes[nodes[node["parentId"]]["parentId"]]["name"] + "_" + name
    if node["sourceSystem"] == "dd4hep/tgeo":
        return re.sub(r"_\d+$", "", name)
    return name


def audit(scene, expected, palette):
    if scene["header"] != {"version": 1, "type": "semantic"}:
        raise ValueError("unsupported nodehammer semantic schema")
    content = scene["content"]
    nodes = {n["id"]: n for n in content["nodes"]}
    volumes = {v["id"]: v for v in content["logVols"]}
    materials = {m["id"]: m for m in content["materials"]}
    shapes = {s["id"]: s for s in content["shapes"]}
    world = transforms(nodes)
    mapped = {}
    physical = set()
    for key, node in nodes.items():
        name = entity_name(node, nodes)
        if name in mapped:
            raise ValueError(f"duplicate entity {name}")
        mapped[name] = key
        material = materials[volumes[node["logVolId"]]["materialId"]]
        if material["name"] not in ("Air", "dummy"):
            physical.add(key)
            if style_name(material["name"]) not in palette:
                raise ValueError(f"unclassified display material: {material['name']}")
        if node.get("degradation", 0):
            raise ValueError(f"degraded import: {name}")
    expected_names = {e["name"] for e in expected["entities"]}
    if set(mapped) != expected_names | {"world", "PixelBarrel"}:
        raise ValueError("imported entity inventory differs from expected.json")
    max_centre_error = max_normal_error = 0.0
    for entity in expected["entities"]:
        key = mapped[entity["name"]]
        rotation, centre = world[key]
        error = max(abs(a * MM_PER_CM - b) for a, b in zip(centre, entity["center_mm"]))
        max_centre_error = max(max_centre_error, error)
        if "normal" in entity:
            max_normal_error = max(max_normal_error, max(abs(a - b) for a, b in
                                   zip(mv(rotation, [0, 0, 1]), entity["normal"])))
        material = materials[volumes[nodes[key]["logVolId"]]["materialId"]]["name"]
        if "material" in entity and material != entity["material"]:
            raise ValueError(f"wrong material: {entity['name']}")
        tagged = nodes[key].get("tags", {}).get("sensitive") == "true"
        if tagged != (entity["role"] == "sensitive"):
            raise ValueError(f"wrong sensitive tag: {entity['name']}")
    if max_centre_error > CENTRE_TOLERANCE_MM or max_normal_error > 1e-12:
        raise ValueError("imported placement transforms differ from expected.json")
    return {
        "entities_checked": len(expected_names), "nodes": len(nodes),
        "physical_placements": len(physical), "counts": expected["counts"],
        "max_centre_error_mm": max_centre_error, "centre_tolerance_mm": CENTRE_TOLERANCE_MM,
        "max_sensor_normal_error": max_normal_error,
        "physical_shape_counts": dict(Counter(shapes[volumes[nodes[k]["logVolId"]]["shapeId"]]["type"] for k in physical)),
        "material_rgb_checked": False,
        "display_rgb_source": "config palette, independent of imported ROOT colour",
        "semantic_length_unit": "cm",
        "gltf_unit_scale": METRES_PER_CM,
    }, nodes, physical


def config_text(palette, materials, selection=None):
    lines = ["# Generated display settings; not detector material definitions.",
             "hoist_orphans = true", "[export.gltf]", f"unit_scale = {METRES_PER_CM}",
             "bake_unit_scale = true"]
    if selection:
        lines += ["[[selection_rules]]", "drop_if = 'name ~= \"*\"'",
                  "[[selection_rules]]", f"keep_if = '{selection}'"]
    for name, style in palette.items():
        lines += [f"[materials.{name}]", f"base_color = {json.dumps(style['rgb'] + [style['alpha']])}",
                  'alpha_mode = "blend"' if style["alpha"] < 1 else 'alpha_mode = "opaque"',
                  "metallic = 0.0", "roughness = 0.7"]
    for material in materials:
        name = material["name"]
        if name in ("Air", "dummy"):
            lines += ["[[rules]]", f"match = 'material == {json.dumps(name)}'",
                      "[rules.tessellation]", "skip_geometry = true"]
        else:
            if style_name(name) not in palette:
                raise ValueError(f"unclassified display material: {name}")
            lines += ["[[rules]]", f"match = 'material == {json.dumps(name)}'",
                      f'material = "{style_name(name)}"']
    lines += ["[[rules]]", "[rules.tessellation]", "max_segments_circle = 96", 'fallback = "fail"']
    return "\n".join(lines) + "\n"


def audit_glb(path, render, palette, semantic):
    with path.open("rb") as stream:
        magic, version, _ = struct.unpack("<III", stream.read(12))
        length, kind = struct.unpack("<II", stream.read(8))
        if (magic, version, kind) != (0x46546C67, 2, 0x4E4F534A):
            raise ValueError("unsupported GLB container")
        gltf = json.loads(stream.read(length))
    if len(gltf["nodes"]) != len(render["nodes"]):
        raise ValueError("GLB node inventory differs")
    nodes = {n["id"]: n for n in semantic["nodes"]}
    volumes = {v["id"]: v for v in semantic["logVols"]}
    shapes = {s["id"]: s for s in semantic["shapes"]}
    boxes = 0
    for node, reference in zip(gltf["nodes"], render["nodes"]):
        if node["name"] != reference["name"]:
            raise ValueError("GLB node ordering/names changed; reassess export audit")
        matrix = reference["localTransform"].copy()
        for i in (12, 13, 14):
            matrix[i] *= METRES_PER_CM
        if max(abs(a - b) for a, b in zip(node["matrix"], matrix)) > 1e-7:
            raise ValueError("GLB transform/length unit differs")
        shape = shapes[volumes[nodes[reference["semanticNodeId"]]["logVolId"]]["shapeId"]]
        if "mesh" in node and shape["type"] == "box":
            primitive = gltf["meshes"][node["mesh"]]["primitives"][0]
            accessor = gltf["accessors"][primitive["attributes"]["POSITION"]]
            half_sizes = [shape[k] * METRES_PER_CM for k in ("dx", "dy", "dz")]
            for bound, sign in (("min", -1), ("max", 1)):
                if max(abs(a - sign * b) for a, b in zip(accessor[bound], half_sizes)) > 1e-7:
                    raise ValueError("GLB box size differs from semantic cm to metre conversion")
            boxes += 1
    for material in gltf["materials"]:
        style = palette[material["name"]]
        actual = material["pbrMetallicRoughness"]["baseColorFactor"]
        if max(abs(a - b) for a, b in zip(actual, style["rgb"] + [style["alpha"]])) > 1e-6:
            raise ValueError("GLB material RGBA differs")
        if style["alpha"] < 1 and material.get("alphaMode") != "BLEND":
            raise ValueError("GLB transparent material is not marked BLEND")
    return {"node_transforms_checked": len(gltf["nodes"]), "box_dimensions_checked": boxes,
            "length_tolerance_m": 1e-7, "material_rgba_and_blend_checked": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nodehammer", type=Path, default=ROOT / "build/nodehammer/native/nodehammer")
    parser.add_argument("--compact", type=Path, default=ROOT / "build/dd4hep/detector/compact/pixel-barrel.xml")
    parser.add_argument("--output", type=Path, default=ROOT / "build/nodehammer/pixel")
    args = parser.parse_args()
    build_manifest = json.loads((args.nodehammer.resolve().parent.parent / "build-manifest.json").read_text())
    if build_manifest["nodehammer_sha256"] != sha(args.nodehammer):
        raise ValueError("binary differs from build-manifest.json; rerun build.py")
    pin = json.loads(Path(__file__).with_name("upstream.json").read_text())
    if build_manifest["upstream_revision"] != pin["revision"]:
        raise ValueError("binary source revision differs from upstream.json")
    compact, out = args.compact.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    commands = []

    def run(*arguments, json_output=False):
        command = [str(args.nodehammer.resolve()), *map(str, arguments)]
        commands.append(command)
        result = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE)
        return json.loads(result.stdout) if json_output else result.stdout.strip()

    summary = run("inspect", "--output-format", "json", "summary", "-i", compact, json_output=True)
    if summary["schema"] != 1 or summary["diagnostics"] != {"warnings": 0, "errors": 0}:
        raise ValueError("import has warnings/errors or unsupported summary schema")
    run("convert", "-i", compact, "-o", out / "pixel.json", "-o", out / "pixel.nhb")
    scene = json.loads((out / "pixel.json").read_text())
    palette = json.loads((ROOT / "detector/config/display.json").read_text())["styles"]
    expected = json.loads(compact.with_name("expected.json").read_text())
    report, nodes, physical = audit(scene, expected, palette)
    # NHB reindexes nodes breadth-first. Re-audit the portable representation
    # and use its IDs for render checks; IDs are not persistent detector IDs.
    run("convert", "-i", out / "pixel.nhb", "-o", out / "roundtrip.json")
    portable = json.loads((out / "roundtrip.json").read_text())
    roundtrip_report, nodes, physical = audit(portable, expected, palette)
    report["nhb_roundtrip"] = roundtrip_report
    views = {"full": None, "sensitive": 'tag.sensitive == "true"',
             "stave": 'path ~= "**/layer1_stave0" || path ~= "**/layer1_stave0/**"'}
    report["views"] = {}
    for name, selection in views.items():
        config = out / f"{name}.toml"
        config.write_text(config_text(palette, scene["content"]["materials"], selection))
        run("config", "validate", "-c", config)
        render_file = out / f"{name}.render.json"
        run("convert", "-i", out / "pixel.nhb", "-c", config,
            "--output-format", "render-json", "-o", render_file)
        render = json.loads(render_file.read_text())
        bindings = {n["semanticNodeId"] for n in render["nodes"] if n["meshBindings"]}
        wanted = physical
        if name == "sensitive":
            wanted = {k for k in physical if nodes[k].get("tags", {}).get("sensitive") == "true"}
        elif name == "stave":
            root = next(k for k, n in nodes.items() if n["name"] == "layer1_stave0")
            descendants, pending = set(), [root]
            while pending:
                key = pending.pop()
                descendants.add(key)
                pending.extend(nodes[key].get("children", []))
            wanted = physical & descendants
        if bindings != wanted:
            raise ValueError(f"{name}: tessellated placements differ: {len(bindings)} != {len(wanted)}")
        run("convert", "-i", out / "pixel.nhb", "-c", config, "-o", out / f"{name}.glb")
        glb_report = audit_glb(out / f"{name}.glb", render, palette, portable["content"])
        run("project", "pack", "-i", out / "pixel.nhb", "-c", config, "-o", out / f"{name}.nhproj")
        run("project", "info", out / f"{name}.nhproj")
        report["views"][name] = {"mesh_placements": len(bindings), "mesh_assets": len(render["meshAssets"]),
                                "glb_audit": glb_report,
                                "project_bytes": (out / f"{name}.nhproj").stat().st_size,
                                "glb_bytes": (out / f"{name}.glb").stat().st_size}
    report.update({"recorded_at": datetime.now(timezone.utc).isoformat(),
                   "nodd_revision": subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip(),
                   "upstream_pin": json.loads(Path(__file__).with_name("upstream.json").read_text()),
                   "build_manifest": build_manifest,
                   "workflow_sha256": {name: sha(Path(__file__).with_name(name))
                                       for name in ("prepare.py", "build.py", "upstream.json", "conan.lock")},
                   "nodehammer_version": run("--version"), "nodehammer_sha256": sha(args.nodehammer),
                   "import_diagnostics": summary["diagnostics"], "commands": commands,
                   "inputs_sha256": {p.name: sha(p) for p in compact.parent.iterdir() if p.is_file()},
                   "palette_sha256": sha(ROOT / "detector/config/display.json"),
                   "outputs_sha256": {p.name: sha(p) for p in out.iterdir() if p.suffix in (".nhb", ".nhproj", ".glb", ".toml")}})
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(out / "report.json")


if __name__ == "__main__":
    main()
