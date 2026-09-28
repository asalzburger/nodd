#!/usr/bin/env python3
"""PROTOTYPE: run an externally supplied IdRes checkout on DES-006 trial surfaces.

No upstream code or detector examples are distributed. Uniform fields only;
each field uses a separate process to avoid the observed multi-field defect.
"""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys


PIN = "d54d0e3c465cc0308becb737b04364ce5c68ce16"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def geometry(candidate, field, material_scale):
    """Export full explicitly signed surfaces, with one uniform field per file."""
    if not math.isfinite(field) or field <= 0:
        raise ValueError("This adapter requires one positive uniform field")
    if not math.isfinite(material_scale) or material_scale <= 0:
        raise ValueError("IdRes cannot safely represent exactly zero material")
    lines = ["! PROTOTYPE: unsigned nODD DES-006 trial surfaces",
             f"B {field:g} end", "z -.15 0 .15 end", "pt 1 10 100 end",
             "eta 0 4 .05 end"]
    ids = set()
    for layer in candidate["layers"]:
        if layer["id"] in ids:
            raise ValueError("Duplicate layer ID")
        ids.add(layer["id"])
        if layer["kind"] not in ("cylinder", "disc"):
            raise ValueError("Only finite cylinders/discs are supported")
    for kind in ("cylinder", "disc"):
        lines.append(kind)
        for layer in candidate["layers"]:
            if layer["kind"] != kind:
                continue
            if kind == "cylinder":
                dims = [layer["r_m"], layer["z_min_m"], layer["z_max_m"]]
                valid = dims[0] > 0 and dims[1] < dims[2]
            else:
                dims = [layer["r_min_m"], layer["r_max_m"], layer["z_m"]]
                valid = 0 < dims[0] < dims[1] and dims[2] != 0
            response = [layer["x0_percent"] * material_scale,
                        layer["sigma_rphi_m"], layer["sigma_second_m"]]
            values = dims + response
            if not valid or not all(math.isfinite(x) for x in values):
                raise ValueError("Invalid finite surface bounds")
            if not all(x > 0 for x in response) or response[1] >= 1:
                raise ValueError("This adapter exports positive material/sensitive surfaces only")
            lines.append(" ".join(format(x, ".12g") for x in values))
        lines.append("end")
    return "\n".join(lines) + "\n"


def read_table(path):
    with path.open() as handle:
        rows = [{k: float(v) for k, v in row.items()}
                for row in csv.DictReader(handle, delimiter="\t")]
    if not all(math.isfinite(x) for row in rows for x in row.values()):
        raise ValueError(f"Non-finite output in {path.name}")
    return rows


def convert(row, hits):
    return {"eta": row["Eta"], "vertex_z_m": row["z"],
            "pt_GeV": row["Pt"], "sigma_d0_um": row["Sig_d0"],
            "sigma_z0_um": row["Sig_z0"], "sigma_phi_rad": row["Sig_phi"],
            "sigma_cot_theta": row["Sig_cotT"],
            "sigma_inverse_pt_GeV_inverse": row["Sig_invPt"] / 1000,
            "transverse_lever_arm_m": row["LeverArm"],
            "upstream_hit_count": int(hits["nHits"]),
            "upstream_pixel_hit_count": int(hits["nPixHits"]),
            "upstream_strip_hit_count": int(hits["nStripHits"]),
            "effective_station_count": int(hits["nPixHits"] + hits["nStripHits"] / 2)}


def run(configuration, checkout, work, output):
    revision = subprocess.check_output(["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True).strip()
    if revision != PIN:
        raise ValueError(f"Unvalidated upstream revision {revision}; expected {PIN}")
    if subprocess.check_output(["git", "-C", str(checkout), "diff", "HEAD", "--", "src"], text=True):
        raise ValueError("Upstream source modifications must be separately qualified")
    binary = checkout / "bin/idres"
    config = json.loads(configuration.read_text())
    work.mkdir(parents=True, exist_ok=True)
    report = {"status": "PROTOTYPE; ideal covariance estimates, not validated tracking performance",
              "upstream_revision": revision, "upstream_source_modified": False,
              "public_reproducibility": "BLOCKED: anonymous access and redistribution licence unresolved",
              "configuration_sha256": sha256(configuration), "adapter_sha256": sha256(__file__),
              "binary_sha256": sha256(binary), "platform": platform.platform(),
              "python": platform.python_version(),
              "adapter_command": ["python3", "-B"] + sys.argv,
              "project_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
              "project_worktree": "DES-006 study files uncommitted during generation; exact input and adapter hashes retained",
              "random_seed": None, "sampling": "deterministic eta 0..4 step0.05; z=-0.15,0,0.15m; pT1,10,100GeV",
              "build": "make -C <checkout>/src CPPFLAGS=-I/opt/homebrew/opt/gsl/include LDFLAGS=-L/opt/homebrew/opt/gsl/lib",
              "compiler": "Apple clang17.0.0 (clang-1700.6.4.2)", "gsl": "2.8",
              "limitations": ["Straight-line intersections; field affects covariance, not curved trajectories",
                  "No beam pipe, remote services, gaps, inefficiency, occupancy or reconstruction",
                  "Effective two-coordinate stereo station, not two independent 2D hits; physical separation omitted",
                  "No vertex prior; positive charge only; point vertex and two stress vertices, not a luminous distribution",
                  "No zero-material run: use two small positive material scales for convergence",
                  "Uniform field only; separate process per field required by observed upstream multi-field defect",
                  "Raw Sig_invPt has units TeV^-1 and is divided by1000; output precision1e-6GeV^-1",
                  "Upstream counts one pixel hit but two strip hits per input surface; effective_station_count removes that reporting convention",
                  "Upstream uses0.3 for curvature conversion versus exact0.299792458",
                  "Material projection only reported at z0 and lowest pT; no composition or interaction lengths"],
              "runs": []}
    scenarios = [(b, m) for b in [2, 3, 4] for m in [.5, 1, 2]] + [(3, 1e-8), (3, 1e-6)]
    for candidate in config["candidates"]:
        for field, scale in scenarios:
            name = f"{candidate['id']}_b{field}_m{scale:g}"
            geom = work / f"{name}.geom"
            geom.write_text(geometry(candidate, field, scale))
            proc = subprocess.run([str(binary), geom.name], cwd=work, capture_output=True, text=True)
            log = work / f"{name}.log"
            log.write_text(proc.stdout + proc.stderr)
            if proc.returncode or "No result" in proc.stdout or "Unable to invert" in proc.stdout:
                raise RuntimeError(f"IdRes failure in {name}; inspect {log}")
            raw = read_table(work / f"{geom.name}.res")
            hits = read_table(work / f"{geom.name}.hits")
            material = read_table(work / f"{geom.name}.X0")
            if len(raw) != 729 or len(hits) != 729 or len(material) != 81:
                raise ValueError(f"Unexpected output denominator in {name}")
            key = lambda r: (r["B"], r["z"], r["Pt"], r["Eta"])
            expected = {(0., z, p, round(i * .05, 3)) for z in [-.15, 0., .15]
                        for p in [1., 10., 100.] for i in range(81)}
            if set(map(key, raw)) != expected or set(map(key, hits)) != expected:
                raise ValueError(f"Missing or unexpected sample keys in {name}")
            hit_index = {key(r): r for r in hits}
            rows = [convert(r, hit_index[key(r)]) for r in raw]
            entry = {"candidate": candidate["id"], "field_T": field, "material_scale": scale,
                     "expected_rows": 729, "result_rows": len(raw), "missing_rows": 0,
                     "exit_code": 0, "command": ["<checkout>/bin/idres", geom.name],
                     "artifact_sha256": {p.name: sha256(p) for p in
                         [geom, log, work / f"{geom.name}.res", work / f"{geom.name}.hits", work / f"{geom.name}.X0"]},
                     "samples": [r for r in rows if r["eta"] in [0., 2., 3., 4.]]}
            if field == 3 and scale == 1:
                entry["origin_profile"] = [r for r in rows if r["vertex_z_m"] == 0]
                entry["material_origin_percent_x0"] = [{"eta": r["Eta"], "percent_x0": r["%X0"]} for r in material]
            report["runs"].append(entry)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(f"PASS: {len(report['runs'])} runs, 729 complete rows each; {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--configuration", type=Path, default=Path("docs/design/DES-006-layouts.json"))
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("docs/validation/DES-006-idres-results.json"))
    args = parser.parse_args()
    run(args.configuration, args.checkout.resolve(), args.work.resolve(), args.output)
