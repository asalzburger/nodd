#!/usr/bin/env python3
"""Reduce pinned ODD and existing nODD prototypes to isolated IdRes surfaces."""
import argparse
import copy
import gzip
import hashlib
import json
import math
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/validation/ODD-idres"
ODD_PIN = "c167363f3d4ad1540a577af99071283caf54f3a6"
FAMILIES = ("pixel", "short_strip", "long_strip")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    p = Path(path)
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == ".gz" else p.read_bytes())


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def extract_odd(source):
    """Extract placement radii/layer annuli; collapse module gaps and offsets."""
    revision = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if revision != ODD_PIN:
        raise ValueError("Expected pinned ODD study revision " + ODD_PIN)
    paths = ["xml/detectors/Tracker" + x + ".xml" for x in ("Pixels", "ShortStrips", "LongStrips")]
    paths += ["factory/tracker/ODDModuleHelper.cpp", "factory/tracker/ODDPixelBarrel_geo.cpp",
              "factory/tracker/ODDStripBarrel_geo.cpp", "factory/tracker/ODDPixelEndcap_geo.cpp",
              "factory/tracker/ODDStripEndcap_geo.cpp"]
    if subprocess.check_output(["git", "-C", str(source), "diff", "HEAD", "--", *paths], text=True):
        raise ValueError("ODD source files have local modifications")
    layers = []
    for family, path in zip(FAMILIES, paths[:3]):
        tree = ET.parse(source / path)
        constants = {c.get("name"): c.get("value") for c in tree.findall(".//constant")}

        def mm(expression):
            return float(expression.removesuffix("*mm"))

        for detector in tree.findall(".//detector"):
            name = detector.get("name")
            if detector.find("layer") is None:
                continue
            barrel = name.endswith("Barrel")
            if barrel:
                components = detector.findall("module/module_component")
                module_length = max(mm(c.get("dy")) + 2 * abs(mm(c.get("y_offset"))) for c in components)
                stave = detector.find("stave")
                count = int(constants[stave.get("nmodules")])
                outer_center = (count - 1) / 2 * (module_length + mm(stave.get("gap")))
                sensitive = [c for c in components if c.get("sensitive") == "true"]
                zmin = -outer_center + min(mm(c.get("y_offset")) - mm(c.get("dy")) / 2 for c in sensitive)
                zmax = outer_center + max(mm(c.get("y_offset")) + mm(c.get("dy")) / 2 for c in sensitive)
            for layer in detector.findall("layer"):
                item = dict(id=layer.get("name"), subsystem=family, kind="cylinder" if barrel else "disc",
                            source_locator=path + " detector=" + name + " layer=" + layer.get("id"))
                if barrel:
                    item.update(r_m=mm(layer.get("r")) / 1000, z_min_m=zmin / 1000, z_max_m=zmax / 1000)
                else:
                    item.update(r_min_m=mm(layer.get("rmin")) / 1000, r_max_m=mm(layer.get("rmax")) / 1000,
                                z_m=mm(layer.get("z_offset")) / 1000)
                layers.append(item)
    return dict(revision=revision, public_url="https://gitlab.cern.ch/acts/OpenDataDetector",
                files={p: digest(source / p) for p in paths}, layers=layers,
                reduction="Nominal cylinder radii; continuous outer sensitive barrel z bounds from module placement; disc layer envelope annuli, not finite active sensors. Gaps, stereo separation, stagger and phi tilt omitted.")


def patch_bounds(patches):
    """Exact radial min/max over each active rectangle, then union envelope."""
    lower, upper = [], []
    for p in patches:
        center, u, v = p["center_mm"], p["u"], p["v"]
        a, b = p["half_u_mm"], p["half_v_mm"]
        # u,v are orthonormal in the transverse plane.
        cu = sum(center[i] * u[i] for i in (0, 1))
        cv = sum(center[i] * v[i] for i in (0, 1))
        lower.append(math.hypot(max(abs(cu) - a, 0), max(abs(cv) - b, 0)))
        upper.extend(math.hypot(*(center[i] + su*a*u[i] + sv*b*v[i] for i in (0, 1)))
                     for su in (-1, 1) for sv in (-1, 1))
    return min(lower) / 1000, max(upper) / 1000


def prepare(odd_snapshot, output):
    sources = {}

    def load(path):
        sources[path] = digest(ROOT / path)
        return read(ROOT / path)

    odd = read(odd_snapshot)
    sources[str(odd_snapshot.relative_to(ROOT))] = digest(odd_snapshot)
    pb = load("detector/config/pixel-barrel.json")
    sb = load("tools/short_strip_barrel/inputs-phi-tilted.json")
    se = load("tools/short_strip_endcap/inputs.json")
    lb = load("tools/long_strip_barrel/inputs.json")
    le = load("tools/long_strip_endcap/inputs.json")
    packed = load("docs/validation/DES-013-pixel-z/data/packed-200um/layout.json.gz")
    template = load("docs/validation/DES-017/four-single-two-quad-layout.json")
    pixel_endcap = load("tools/pixel_endcap_support/inputs.json")
    apertures = load("docs/validation/DES-018/screening.json")["variants"]["four-single-two-quad"]["positive_discs"]
    load("detector/config/pixel-detector-trimmed.json")
    load("docs/design/DES-006-layouts.json")
    response = {
        "pixel": dict(pitch_rphi_m=pb["module"]["pixel_pitch_mm"] / 1000,
                      pitch_second_m=pb["module"]["pixel_pitch_mm"] / 1000, x0_percent=1.0),
        "short_strip": dict(pitch_rphi_m=sb["cell_mm"][0] / 1000,
                            pitch_second_m=sb["cell_mm"][1] / 1000, x0_percent=1.5),
        "long_strip": dict(pitch_per_face_m=lb["pitch_mm"] / 1000,
                           full_stereo_angle_rad=lb["stereo_rad"], x0_percent=2.0)}
    for f, r in response.items():
        if f == "long_strip":
            sigma = r["pitch_per_face_m"] / math.sqrt(12)
            half_angle = r["full_stereo_angle_rad"] / 2
            r.update(sigma_rphi_m=sigma / (math.sqrt(2) * math.cos(half_angle)),
                     sigma_second_m=sigma / (math.sqrt(2) * math.sin(half_angle)))
        else:
            r.update(sigma_rphi_m=r["pitch_rphi_m"] / math.sqrt(12),
                     sigma_second_m=r["pitch_second_m"] / math.sqrt(12))
    extended = []
    for layer in packed["layers"]:
        if layer["subsystem"] != "pixel" or layer["kind"] != "cylinder":
            continue
        item = {k: layer[k] for k in ("id", "subsystem", "kind", "r_m")}
        modules = [m for m in packed["modules"] if m["layer_id"] == layer["id"]]
        zs = [m["center_mm"][2] + su*m["u"][2]*m["half_u_mm"] + sv*m["v"][2]*m["half_v_mm"]
              for m in modules for su in (-1, 1) for sv in (-1, 1)]
        item.update(z_min_m=min(zs)/1000, z_max_m=max(zs)/1000,
                    source_locator="DES013 packed-200um pixel layer and active corner z extrema")
        extended.append(item)
    for family, config, key in (("short_strip", sb, "nominal_radii_mm"), ("long_strip", lb, "radii_mm")):
        for i, r in enumerate(config[key], 1):
            extended.append(dict(id=f"{family}-B{i}", subsystem=family, kind="cylinder", r_m=r/1000,
                                 z_min_m=-config["active_half_length_mm"]/1000,
                                 z_max_m=config["active_half_length_mm"]/1000,
                                 source_locator="DES020/022 nominal radius and active_half_length_mm; phi tilt collapsed"))
    aperture_table = []
    for i, disc in enumerate(apertures, 1):
        full_bounds = patch_bounds(template["active_patches"])
        kept = [p for p in template["active_patches"] if p["row"] in disc["retained_rows"]]
        adapted_bounds = patch_bounds(kept)
        # DES019 uses rounded whole-mm DES015 datums; DES018 proof datums are historical.
        z = pixel_endcap["placement"]["disc_abs_z_mm"][i-1]
        aperture_table.append(dict(disc=i, abs_z_mm=z, full_inner_mm=full_bounds[0]*1000,
                                   adapted_inner_mm=adapted_bounds[0]*1000,
                                   outer_mm=full_bounds[1]*1000, removed_rows=disc["removed_rows"],
                                   proof_datum_mm=disc["datum_mm"]))
        for sign in (-1, 1):
            extended.append(dict(id=f"pixel-{'N' if sign < 0 else 'P'}{i}", subsystem="pixel", kind="disc",
                                 z_m=sign*z/1000, r_min_m=full_bounds[0], r_max_m=full_bounds[1],
                                 source_locator="DES017 mixed active-patch radial envelope; DES019 whole-mm disc datum"))
    for family, config in (("short_strip", se), ("long_strip", le)):
        for i, z in enumerate(config["disc_z_mm"], 1):
            for sign in (-1, 1):
                extended.append(dict(id=f"{family}-{'N' if sign < 0 else 'P'}{i}", subsystem=family, kind="disc",
                                     z_m=sign*z/1000, r_min_m=config["annulus_mm"][0]/1000,
                                     r_max_m=config["annulus_mm"][1]/1000,
                                     source_locator="DES021/023 annulus_mm and disc_z_mm; stereo pair collapsed"))
    adapted = copy.deepcopy(extended)
    for layer in adapted:
        if layer["subsystem"] == "pixel" and layer["kind"] == "disc":
            row = aperture_table[int(layer["id"].split("-")[1][1:])-1]
            layer["r_min_m"] = row["adapted_inner_mm"]/1000
            layer["source_locator"] += "; DES018 retained_rows"
    geometries = []
    for id_, title, layers in (("odd", "Original ODD", odd["layers"]),
                               ("extended", "Extended ODD prototype", extended),
                               ("aperture", "Extended + adapted pixel aperture", adapted)):
        for layer in layers:
            r = response[layer["subsystem"]]
            layer.update({k: r[k] for k in ("sigma_rphi_m", "sigma_second_m", "x0_percent")})
        geometries.append(dict(id=id_, name=title, layers=layers))
    result = dict(schema_version=1, status="PROTOTYPE; ideal layer reduction, no production geometry or sign-off",
                  units=dict(length="m", momentum="GeV", field="T", material="percent X0"),
                  source_sha256=sources, response=response, aperture_table=aperture_table,
                  scan=dict(eta_min=-4, eta_max=4, eta_step=0.01, vertex_z_m=[-0.15, 0, 0.15],
                            pt_GeV=[1, 10, 100], field_T=[2, 3, 4], plot_field_T=3),
                  material_basis="Common DES006 C05 layer fixtures: pixel 1%, short strip 1.5%, collapsed long-strip pair 2%; excludes beam pipe, remote services and detailed supports. Not a DD4hep material budget.",
                  response_basis="Common current DES012/020/022 prototype pitch/sqrt(12), applied to all layouts to isolate geometry; not original ODD digitization. Long-strip full stereo opening 0.04 rad.",
                  candidates=geometries)
    write(output, result)
    print("Prepared", output, "; layers:", [(c["id"], len(c["layers"])) for c in geometries])


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--extract-odd", type=Path, help="Optional clean pinned ODD checkout; refresh extracted source JSON")
    p.add_argument("--odd-snapshot", type=Path, default=OUT / "odd-source.json")
    p.add_argument("--output", type=Path, default=OUT / "geometries.json")
    a = p.parse_args()
    if a.extract_odd:
        write(a.odd_snapshot, extract_odd(a.extract_odd.resolve()))
    prepare(a.odd_snapshot.resolve(), a.output.resolve())
