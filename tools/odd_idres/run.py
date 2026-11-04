#!/usr/bin/env python3
"""Run IdRes and retain complete, checked, re-plottable ODD comparison data."""
import argparse
import csv
import gzip
import io
import itertools
import json
import math
from pathlib import Path
import platform
import shutil
import subprocess
import sys

from prepare import ROOT, OUT, FAMILIES, digest, read, write

sys.path.insert(0, str(ROOT / "tools/tracker_layout"))
from idres_adapter import PIN
from covariance_control import crossed_measurements, transverse_covariance


def validate_config(config):
    for c in config["candidates"]:
        ids = set()
        for l in c["layers"]:
            if l["id"] in ids:
                raise ValueError("Duplicate layer ID")
            ids.add(l["id"])
            if l["subsystem"] not in FAMILIES:
                raise ValueError("Unknown technology")
            if l["kind"] == "cylinder":
                values = [l["r_m"], l["z_min_m"], l["z_max_m"]]
                valid = values[0] > 0 and values[1] < values[2]
            elif l["kind"] == "disc":
                values = [l["r_min_m"], l["r_max_m"], l["z_m"]]
                valid = 0 < values[0] < values[1] and values[2] != 0
            else:
                raise ValueError("Only cylinders and discs are supported")
            values += [l["sigma_rphi_m"], l["sigma_second_m"], l["x0_percent"]]
            if not valid or not all(math.isfinite(v) for v in values) or not all(v > 0 for v in values[-3:]):
                raise ValueError("Invalid layer bounds, material or precision")


def eta_grid(scan):
    count = round((scan["eta_max"] - scan["eta_min"]) / scan["eta_step"])
    if count <= 0 or not math.isclose(count * scan["eta_step"], scan["eta_max"]-scan["eta_min"]):
        raise ValueError("Eta grid must have an integer number of intervals")
    return [round(scan["eta_min"] + i*scan["eta_step"], 8) for i in range(count+1)]


def geometry(candidate, scan, field, scale=1):
    if field <= 0 or scale <= 0:
        raise ValueError("Positive field and material scale required")
    lines = ["! PROTOTYPE ideal ODD comparison; common response and layer material fixtures",
             f"B {field:g} end", "z " + " ".join(map(str, scan["vertex_z_m"])) + " end",
             "pt " + " ".join(map(str, scan["pt_GeV"])) + " end",
             f"eta {scan['eta_min']:g} {scan['eta_max']:g} {scan['eta_step']:g} end"]
    for kind in ("cylinder", "disc"):
        lines.append(kind)
        for l in candidate["layers"]:
            if l["kind"] != kind:
                continue
            keys = ("r_m", "z_min_m", "z_max_m") if kind == "cylinder" else ("r_min_m", "r_max_m", "z_m")
            values = [l[k] for k in keys] + [l["x0_percent"]*scale, l["sigma_rphi_m"], l["sigma_second_m"]]
            lines.append(" ".join(format(v, ".15g") for v in values))
        lines.append("end")
    return "\n".join(lines) + "\n"


def profile(candidate, eta, vertex):
    """Independent IdRes-compatible straight-ray crossings and path material."""
    cot = math.sinh(eta)
    hits = {f: 0 for f in FAMILIES}
    material = {f: 0. for f in FAMILIES}
    crossed, radii = [], []
    classified_pixel = classified_strip = 0
    for l in candidate["layers"]:
        if l["kind"] == "cylinder":
            r = l["r_m"]
            z = vertex + r*cot
            valid = l["z_min_m"] < z <= l["z_max_m"]
            factor = math.cosh(eta)
        else:
            if abs(cot) < 1e-10:
                continue
            r = (l["z_m"]-vertex)/cot
            valid = l["r_min_m"] < r <= l["r_max_m"]
            factor = 1/abs(math.tanh(eta))
        if not valid:
            continue
        family = l["subsystem"]
        hits[family] += 1
        material[family] += l["x0_percent"]*factor
        crossed.append(l["id"])
        radii.append(r)
        if l["sigma_second_m"] < 0.0002:
            classified_pixel += 1
        else:
            classified_strip += 2
    return dict(geometry=candidate["id"], eta=eta, vertex_z_m=vertex,
                pixel_hits=hits["pixel"], short_strip_hits=hits["short_strip"],
                long_strip_stations=hits["long_strip"], long_strip_sensor_hits=2*hits["long_strip"],
                sensor_hits=hits["pixel"]+hits["short_strip"]+2*hits["long_strip"],
                measurement_stations=sum(hits.values()),
                idres_nPixHits=classified_pixel, idres_nStripHits=classified_strip,
                idres_nHits=classified_pixel+classified_strip,
                material_percent_x0=sum(material.values()),
                **{f+"_percent_x0": material[f] for f in FAMILIES},
                lever_arm_m=max(radii)-min(radii) if radii else 0,
                layer_ids=crossed)


def table(path):
    with path.open() as handle:
        rows = [{k.strip(): float(v) for k, v in r.items()} for r in csv.DictReader(handle, delimiter="\t")]
    if not all(math.isfinite(v) for r in rows for v in r.values()):
        raise ValueError("Nonfinite IdRes result: " + str(path))
    return rows


def key(row):
    return (row["B"], row["z"], row["Pt"], row["Eta"])


def check_keys(rows, expected):
    keys = [key(r) for r in rows]
    if len(keys) != len(expected) or set(keys) != expected:
        raise ValueError("Missing, duplicate or unexpected IdRes sample keys")


def convert(row, geometry_id, field):
    sigma = row["Sig_invPt"] / 1000
    relative = row["Pt"] * sigma
    return dict(geometry=geometry_id, field_T=field, vertex_z_m=row["z"], pt_GeV=row["Pt"], eta=row["Eta"],
                sigma_inverse_pt_GeV_inverse=sigma, sigma_inverse_pt_TeV_inverse=row["Sig_invPt"],
                linearized_sigma_pt_GeV=row["Pt"]*relative,
                linearized_relative_pt_percent=100*relative,
                linearized_relative_pt_below_one=relative < 1,
                sigma_d0_um=row["Sig_d0"], sigma_z0_um=row["Sig_z0"],
                sigma_phi_rad=row["Sig_phi"], sigma_cot_theta=row["Sig_cotT"],
                idres_lever_arm_m=row["LeverArm"])


def compressed_json(path, data):
    path.write_bytes(gzip.compress((json.dumps(data, separators=(",", ":"), allow_nan=False)+"\n").encode(), mtime=0))


def compressed_csv(path, rows):
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    for r in rows:
        writer.writerow({k: json.dumps(v, separators=(",", ":")) if isinstance(v, list) else v for k,v in r.items()})
    path.write_bytes(gzip.compress(handle.getvalue().encode(), mtime=0))


def run(configuration, source, binary, work, output):
    import numpy
    config = read(configuration)
    validate_config(config)
    source = source.resolve()
    if subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip() != PIN:
        raise ValueError("IdRes source revision must be " + PIN)
    if subprocess.check_output(["git", "-C", str(source), "diff", "HEAD", "--", "src"], text=True):
        raise ValueError("IdRes source modifications require separate qualification")
    src_hashes = {p.name: digest(p) for p in (source/"src").iterdir() if p.suffix in (".cpp", ".cc", ".h") or p.name == "Makefile"}
    build_src = binary.parent.parent/"src"
    if any(digest(build_src/p) != sha for p,sha in src_hashes.items()):
        raise ValueError("Disposable IdRes build inputs differ from pinned source")
    output.mkdir(parents=True, exist_ok=True)
    rawdir = output/"raw"
    rawdir.mkdir(exist_ok=True)
    profiles, results, controls, runs = [], [], [], []
    scan = config["scan"]
    grid = eta_grid(scan)
    for c in config["candidates"]:
        current_profiles = [profile(c, eta, z) for z,eta in itertools.product(scan["vertex_z_m"], grid)]
        profiles += current_profiles
        pindex = {(r["vertex_z_m"], r["eta"]): r for r in current_profiles}
        scenarios = [(b, 1, False) for b in scan["field_T"]] + [(3, scale, True) for scale in (1e-6, 1e-8)]
        for field, scale, control in scenarios:
            local_scan = dict(scan, eta_min=0, eta_max=4, eta_step=2, pt_GeV=[100]) if control else scan
            expected = {(0., z, pt, eta) for z,pt,eta in itertools.product(local_scan["vertex_z_m"], local_scan["pt_GeV"], eta_grid(local_scan))}
            name = f"{c['id']}_b{field}_m{scale:g}"
            scratch = work/name
            scratch.mkdir(parents=True, exist_ok=True)
            geom = scratch/(name+".geom")
            geom.write_text(geometry(c, local_scan, field, scale))
            process = subprocess.run([str(binary), geom.name], cwd=scratch, capture_output=True, text=True, timeout=180)
            log = scratch/(name+".log")
            log.write_text(process.stdout+process.stderr)
            if process.returncode or any(s in log.read_text() for s in ("No result", "Unable to invert", "Error in geometry")):
                raise RuntimeError("IdRes failed; inspect " + str(log))
            res, hits, material = (table(Path(str(geom)+suffix)) for suffix in (".res", ".hits", ".X0"))
            check_keys(res, expected)
            check_keys(hits, expected)
            if len(material) != len(eta_grid(local_scan)) or {r["Eta"] for r in material} != set(eta_grid(local_scan)):
                raise ValueError("Incomplete material profile")
            for h in hits:
                p = pindex[h["z"], h["Eta"]]
                if any(h[k] != p["idres_"+k] for k in ("nHits", "nPixHits", "nStripHits")):
                    raise ValueError("Independent hit count disagrees with IdRes")
            material_diff = max(abs(m["%X0"] - pindex[0, m["Eta"]]["material_percent_x0"]*scale) for m in material)
            if material_diff > 0.00000051:
                raise ValueError("Independent material sum disagrees with IdRes")
            if control:
                for r in res:
                    fit = transverse_covariance(crossed_measurements(c, r["Eta"], r["z"]))
                    predicted = fit["sigma_kappa_per_m"] / (0.3*field)
                    difference = abs(r["Sig_invPt"]/1000-predicted)
                    controls.append(dict(geometry=c["id"], field_T=field, material_scale=scale,
                                         eta=r["Eta"], vertex_z_m=r["z"],
                                         independent_sigma_inverse_pt_GeV_inverse=predicted,
                                         idres_sigma_inverse_pt_GeV_inverse=r["Sig_invPt"]/1000,
                                         absolute_difference_GeV_inverse=difference,
                                         within_half_printed_unit=difference <= 0.0000005))
                if not all(r["within_half_printed_unit"] for r in controls):
                    raise ValueError("Measurement-only covariance control failed")
            else:
                results += [convert(r, c["id"], field) for r in res]
            retained = {}
            for p in [geom, log] + [Path(str(geom)+s) for s in (".res", ".hits", ".X0")]:
                target = rawdir/p.name
                if p.suffix in (".geom", ".log"):
                    shutil.copyfile(p, target)
                else:
                    target = target.with_suffix(target.suffix+".gz")
                    target.write_bytes(gzip.compress(p.read_bytes(), mtime=0))
                retained[str(target.relative_to(output))] = dict(sha256=digest(target), uncompressed_sha256=digest(p))
            runs.append(dict(geometry=c["id"], field_T=field, material_scale=scale, control=control,
                             command=["<idres-binary>", geom.name], exit_code=process.returncode,
                             expected_rows=len(expected), result_rows=len(res), hit_rows=len(hits),
                             material_rows=len(material), independent_material_max_difference_percent_x0=material_diff,
                             files=retained))
            print("PASS", name, len(res), "rows", flush=True)
    compressed_json(output/"profiles.json.gz", profiles)
    compressed_csv(output/"profiles.csv.gz", profiles)
    compressed_json(output/"resolutions.json.gz", results)
    compressed_csv(output/"resolutions.csv.gz", results)
    write(output/"controls.json", controls)
    report = dict(status="Executed PROTOTYPE; ideal parametric covariance, not reconstructed performance",
                  project_revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  dirty_worktree=True, configuration_sha256=digest(configuration),
                  producer_sha256={str(p.relative_to(ROOT)): digest(p) for p in [Path(__file__), ROOT/"tools/odd_idres/prepare.py", ROOT/"tools/tracker_layout/covariance_control.py"]},
                  idres_revision=PIN, idres_source_sha256=src_hashes, binary_sha256=digest(binary),
                  source_modified=False, python=platform.python_version(), platform=platform.platform(),
                  compiler=subprocess.check_output(["c++", "--version"], text=True).splitlines()[0],
                  gsl=subprocess.check_output(["gsl-config", "--version"], text=True).strip(),
                  numpy=numpy.__version__,
                  build_log_sha256=digest(output/"build.log") if (output/"build.log").exists() else None,
                  build_command="python3 -B software/env/build_idres.py --source <pinned-idres-checkout> --build build/odd-idres-engine",
                  command="python -B tools/odd_idres/run.py --source <pinned-idres-checkout> --binary build/odd-idres-engine/bin/idres",
                  deterministic=True, random_seed=None, scan=scan, runs=runs,
                  resolution_rows=len(results), profile_rows=len(profiles), covariance_controls=len(controls),
                  limitations=[config["material_basis"], config["response_basis"],
                               "Original ODD is an ideal layer-envelope reduction of the pinned study source, not a DD4hep/Geant4 run.",
                               "nODD prototypes are reduced to cylinders/discs; phi tilts, stagger, seams, finite sensor gaps, pair separation and local disc z levels omitted.",
                               "Current short strips have second sigma 144um, below IdRes 200um threshold: raw nPixHits combines pixel and short-strip surfaces. Technology counts use input metadata.",
                               "No vertex prior; positive q/pT; straight intersections; uniform fields, one field per process. No energy loss, inefficiency or pattern recognition.",
                               "pT*sigma(1/pT) is a linearized proxy; values >=1 are not Gaussian relative-pT resolutions. Full momentum covariance unavailable.",
                               "IdRes source access/licence remains an external dependency; all nODD inputs, raw numeric outputs and plot data are retained without upstream code."])
    write(output/"provenance.json", report)
    print("Retained", len(results), "resolution rows,", len(profiles), "profiles,", len(controls), "controls")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--configuration", type=Path, default=OUT/"geometries.json")
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--binary", type=Path, required=True)
    p.add_argument("--work", type=Path, default=ROOT/"build/odd-idres-runs")
    p.add_argument("--output", type=Path, default=OUT)
    a = p.parse_args()
    run(a.configuration.resolve(), a.source, a.binary.resolve(), a.work.resolve(), a.output.resolve())
