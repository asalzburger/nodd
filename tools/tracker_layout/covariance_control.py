#!/usr/bin/env python3
"""PROTOTYPE: independent, measurement-only transverse curvature control.

No imports from study.py or IdRes: independent straight-ray intersections and
free [d0, phi0, kappa] least squares. NumPy is needed only for covariance algebra.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import shlex
import subprocess
import sys


def crossed_measurements(candidate, eta, vertex_z_m):
    """Return ideal crossed transverse measurements; no material or vertex prior."""
    result = []
    for layer in candidate["layers"]:
        if layer["kind"] == "cylinder":
            radius = layer["r_m"]
            z = vertex_z_m + radius * math.sinh(eta)
            crossed = layer["z_min_m"] <= z <= layer["z_max_m"]
        elif layer["kind"] == "disc":
            if eta == 0:
                continue
            radius = (layer["z_m"] - vertex_z_m) / math.sinh(eta)
            crossed = layer["r_min_m"] <= radius <= layer["r_max_m"]
        else:
            raise ValueError(f"Unsupported layer kind: {layer['kind']}")
        if crossed:
            sigma = layer["sigma_rphi_m"]
            if not math.isfinite(sigma) or sigma <= 0:
                raise ValueError("Transverse precision must be finite and positive")
            result.append({"id": layer["id"], "r_m": radius,
                           "sigma_rphi_m": sigma})
    return sorted(result, key=lambda item: item["r_m"])


def transverse_covariance(measurements):
    """SVD covariance and independent normal-inverse numerical cross-check."""
    import numpy as np

    if len(measurements) < 3:
        raise ValueError("Three distinct measurement radii are required")
    weighted = np.array([
        [1 / m["sigma_rphi_m"], m["r_m"] / m["sigma_rphi_m"],
         0.5 * m["r_m"] ** 2 / m["sigma_rphi_m"]]
        for m in measurements
    ])
    _, singular_values, rotation = np.linalg.svd(weighted, full_matrices=False)
    rank = int(np.linalg.matrix_rank(weighted))
    if rank != 3:
        raise ValueError("Transverse information matrix is rank deficient")
    covariance = (rotation.T / singular_values ** 2) @ rotation
    normal_inverse = np.linalg.inv(weighted.T @ weighted)
    difference = np.max(np.abs(np.diag(covariance) / np.diag(normal_inverse) - 1))
    return {
        "covariance": covariance.tolist(),
        "sigma_d0_m": float(math.sqrt(covariance[0, 0])),
        "sigma_phi0_rad": float(math.sqrt(covariance[1, 1])),
        "sigma_kappa_per_m": float(math.sqrt(covariance[2, 2])),
        "information_rank": rank,
        "weighted_design_condition_number": float(singular_values[0] / singular_values[-1]),
        "max_relative_diagonal_difference_svd_normal_inverse": float(difference),
    }


def calculate(config, field_t=3.0):
    if not math.isfinite(field_t) or field_t == 0:
        raise ValueError("A finite nonzero uniform field is required")
    rows = []
    for candidate in config["candidates"]:
        for eta in (0.0, 4.0):
            for vertex in (0.0, 0.150):
                measurements = crossed_measurements(candidate, eta, vertex)
                row = {"candidate": candidate["id"], "eta": eta,
                       "vertex_z_m": vertex, "station_count": len(measurements),
                       "measurements": measurements,
                       **transverse_covariance(measurements)}
                row["sigma_q_over_pt_per_GeV"] = (
                    row["sigma_kappa_per_m"] / (0.299792458 * abs(field_t))
                )
                rows.append(row)
    return rows


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_idres(rows, artifact, field_t):
    """Compare positive near-zero-material runs at their printed precision."""
    comparisons = []
    for row in rows:
        for scale in (1e-6, 1e-8):
            matches = [sample for run in artifact["runs"]
                       if run["candidate"] == row["candidate"]
                       and run["field_T"] == field_t
                       and run["material_scale"] == scale
                       for sample in run["samples"]
                       if sample["eta"] == row["eta"]
                       and sample["vertex_z_m"] == row["vertex_z_m"]
                       and sample["pt_GeV"] == 100.0]
            if len(matches) != 1:
                raise ValueError(f"Expected one IdRes control for {row['candidate']}, "
                                 f"eta={row['eta']}, z={row['vertex_z_m']}, scale={scale}")
            prediction = row["sigma_q_over_pt_per_GeV"] * 0.299792458 / 0.3
            observed = matches[0]["sigma_inverse_pt_GeV_inverse"]
            difference = observed - prediction
            comparisons.append({
                "candidate": row["candidate"], "eta": row["eta"],
                "vertex_z_m": row["vertex_z_m"], "pt_GeV": 100.0,
                "material_scale": scale,
                "independent_sigma_q_over_pt_with_upstream_0p3_per_GeV": prediction,
                "idres_sigma_q_over_pt_per_GeV": observed,
                "difference_per_GeV": difference,
                "within_half_printed_unit": abs(difference) <= 0.0005 / 1000,
            })
    return {
        "source_upstream_revision": artifact["upstream_revision"],
        "upstream_magnetic_conversion": 0.3,
        "upstream_print_precision_TeV_inverse": 0.001,
        "allowed_rounding_half_unit_GeV_inverse": 0.0005 / 1000,
        "interpretation": "numerical reporting consistency only; no detector acceptance threshold",
        "all_within_half_printed_unit": all(r["within_half_printed_unit"] for r in comparisons),
        "rows": comparisons,
    }


def audit_idres_geometry_material(config, artifact, field_t):
    """Audit baseline origin profiles without using the shared study geometry."""
    result = []
    for candidate in config["candidates"]:
        run = next(run for run in artifact["runs"]
                   if run["candidate"] == candidate["id"]
                   and run["field_T"] == field_t and run["material_scale"] == 1)
        mismatches = []
        for sample in run["origin_profile"]:
            expected = len(crossed_measurements(candidate, sample["eta"], 0.0))
            if expected != sample["effective_station_count"]:
                mismatches.append({"eta": sample["eta"], "pt_GeV": sample["pt_GeV"],
                                   "independent": expected,
                                   "idres_effective": sample["effective_station_count"]})
        layers = {layer["id"]: layer for layer in candidate["layers"]}
        material_rows = []
        for sample in run["material_origin_percent_x0"]:
            eta = sample["eta"]
            expected = 0.0
            for measurement in crossed_measurements(candidate, eta, 0.0):
                layer = layers[measurement["id"]]
                incidence = (math.cosh(eta) if layer["kind"] == "cylinder"
                             else 1 / abs(math.tanh(eta)))
                expected += layer["x0_percent"] * incidence
            material_rows.append({"eta": eta, "independent_percent_x0": expected,
                                  "idres_percent_x0": sample["percent_x0"],
                                  "absolute_difference_percent_x0":
                                      abs(expected - sample["percent_x0"])})
        worst = max(material_rows, key=lambda row: row["absolute_difference_percent_x0"])
        result.append({
            "candidate": candidate["id"],
            "origin_profile_rows_checked": len(run["origin_profile"]),
            "station_count_mismatches": mismatches,
            "material_eta_points_checked": len(material_rows),
            "worst_material_difference": worst,
            "material_allowed_rounding_half_unit_percent_x0": 0.5e-6,
            "all_material_within_half_printed_unit":
                worst["absolute_difference_percent_x0"] <= 0.5e-6,
        })
    return {
        "method": "independent straight-ray crossings; cylinder x0*cosh(eta), disk x0/abs(tanh(eta))",
        "material_ownership": "one input allowance per effective layer; a long-strip pair contributes its 2% once",
        "interpretation": "printed-profile consistency; not material composition or scattering validation",
        "candidates": result,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("docs/design/DES-006-layouts.json"))
    parser.add_argument("--output", type=Path,
                        default=Path("docs/validation/DES-006-covariance-control.json"))
    parser.add_argument("--field-t", type=float, default=3.0)
    parser.add_argument("--idres-results", type=Path,
                        help="Optional retained IdRes artifact for near-zero-material comparison")
    args = parser.parse_args()
    import numpy as np

    config = json.loads(args.input.read_text())
    rows = calculate(config, args.field_t)
    root = Path.cwd()
    executable = Path(sys.executable)
    try:
        executable = executable.relative_to(root)
    except ValueError:
        executable = Path(executable.name)
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], text=True))
    report = {
        "schema_version": 1,
        "status": "PROTOTYPE; unsigned measurement-only numerical control",
        "provenance": {
            "project_revision": revision,
            "working_tree_dirty": dirty,
            "input": str(args.input),
            "input_sha256": sha256(args.input),
            "code": "tools/tracker_layout/covariance_control.py",
            "code_sha256": sha256(Path(__file__)),
            "python_version": platform.python_version(),
            "numpy_version": np.__version__,
            "command": shlex.join([str(executable),
                                    *(["-B"] if sys.dont_write_bytecode else []),
                                    *sys.argv]),
            "exit_status": 0,
            "random_seed": None,
            "randomness": "none; deterministic intersections and linear algebra",
        },
        "units": {"length": "m", "angle": "rad", "field": "T",
                  "curvature": "m^-1", "inverse_transverse_momentum": "GeV^-1"},
        "method": {
            "model": "y(r) = d0 + phi0*r + 0.5*kappa*r^2",
            "parameter_order": ["d0_m", "phi0_rad", "kappa_per_m"],
            "covariance": "inverse(H^T W H), W_ii = 1/sigma_rphi_i^2; evaluated via SVD",
            "geometry": "independent straight rays through ideal cylinders and annuli",
            "field_T": args.field_t,
            "vertex_prior": "none; transverse intercept and slope are free",
            "material": "zero; all input material allowances intentionally disabled",
            "response": "input sigma_rphi_m; second coordinate unused; independent errors",
            "limitations": [
                "small-curvature asymptotic control, not a finite-curvature track fit",
                "no scattering, vertex prior, stereo ambiguity, alignment or reconstruction",
                "inverse-pT errors cannot be interpreted as Gaussian fractional-pT errors when large",
                "condition numbers depend on stated parameter units",
            ],
        },
        "rows": rows,
        "max_relative_diagonal_difference_svd_normal_inverse": max(
            r["max_relative_diagonal_difference_svd_normal_inverse"] for r in rows
        ),
    }
    if args.idres_results:
        report["provenance"]["idres_results"] = str(args.idres_results)
        report["provenance"]["idres_results_sha256"] = sha256(args.idres_results)
        report["idres_comparison"] = compare_idres(
            rows, json.loads(args.idres_results.read_text()), args.field_t
        )
        report["idres_geometry_material_audit"] = audit_idres_geometry_material(
            config, json.loads(args.idres_results.read_text()), args.field_t
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Wrote {len(rows)} independent covariance controls to {args.output}")


if __name__ == "__main__":
    main()
