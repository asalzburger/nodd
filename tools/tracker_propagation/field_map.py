#!/usr/bin/env python3
"""Generate an ACTS RZ map of the current DES-026 finite annular vacuum winding."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import platform
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def winding_inputs(root=ROOT):
    """Require the retained sizing solution to match the current source inputs."""
    report_path = root / "docs/validation/DES-026/sizing.json"
    sizing = json.loads(report_path.read_text())
    for path in ("tools/solenoid_baseline/baseline.json",
                 "tools/solenoid_baseline/model.py", "detector/config/tracker.json"):
        if sha256(root / path) != sizing["input_sha256"][path]:
            raise ValueError(f"DES-026 sizing is stale for {path}; regenerate/review it first")
    result = sizing["result"]
    return result, {p: sha256(root / p) for p in (
        "tools/solenoid_baseline/baseline.json", "tools/solenoid_baseline/model.py",
        "docs/validation/DES-026/sizing.json", "detector/config/tracker.json")}


def sheet_parameters(result, radial_order=8):
    """Gauss radial integral of uniform J, represented by finite ACTS sheets."""
    import numpy as np
    if radial_order < 2:
        raise ValueError("radial quadrature order must be at least two")
    a, b = result["cold_inner_radius_m"], result["winding_outer_radius_m"]
    length, target = result["cold_mass_length_m"], result["central_field_T"]
    if not (0 < a < b and length > 0 and 0 < target <= 5):
        raise ValueError("invalid retained winding")
    x, w = np.polynomial.legendre.leggauss(radial_order)
    radii = (a + b) / 2 + (b - a) / 2 * x
    weights = w * (b - a) / 2
    mu0, half = 4e-7 * math.pi, length / 2
    current_density = result["pack_J_A_mm2"] * 1e6
    center = mu0 * current_density * weights * half / np.hypot(radii, half)
    # Compensate only the finite radial quadrature's floating-point residual.
    normalization = target / float(center.sum())
    if abs(normalization - 1) > 1e-10:
        raise ValueError("quadrature does not reproduce the retained current normalization")
    return [(float(r), float(c * normalization)) for r, c in zip(radii, center)]


def providers(result, radial_order, coils):
    import acts
    unit = acts.UnitConstants
    fields = [acts.SolenoidBField(
        radius=radius * unit.m, length=result["cold_mass_length_m"] * unit.m,
        nCoils=coils, bMagCenter=center * unit.T,
    ) for radius, center in sheet_parameters(result, radial_order)]
    context = acts.MagneticFieldContext()
    caches = [f.makeCache(context) for f in fields]

    def evaluate(r_mm, z_mm):
        import numpy as np
        value = np.zeros(3)
        position = acts.Vector3(r_mm * unit.mm, 0, z_mm * unit.mm)
        for field, cache in zip(fields, caches):
            value += np.asarray(field.getField(position, cache)) / unit.T
        return value
    return evaluate


def generate(output, config):
    import acts
    import numpy as np
    result, source_hashes = winding_inputs()
    output.mkdir(parents=True, exist_ok=True)
    field_cfg = config["field"]
    if not math.isclose(field_cfg["central_field_T"], result["central_field_T"], rel_tol=0, abs_tol=1e-12):
        raise ValueError("requested field strength differs from the current DES-026 source")
    dr, dz = field_cfg["r_step_mm"], field_cfg["z_step_mm"]
    rmax, zmax = field_cfg["r_max_mm"], field_cfg["z_max_mm"]
    if min(dr, dz, rmax, zmax) <= 0 or not all(
        math.isclose(v / d, round(v / d)) for v, d in [(rmax, dr), (zmax, dz)]
    ):
        raise ValueError("field extents must be positive integer multiples of grid spacing")
    radial_order, coils = field_cfg["radial_quadrature_order"], field_cfg["axial_coils"]
    direct = providers(result, radial_order, coils)
    rs = np.linspace(0, rmax, round(rmax / dr) + 1)
    zs = np.linspace(-zmax, zmax, 2 * round(zmax / dz) + 1)
    filename = output / "field.txt"
    started = time.monotonic()
    # Exact vacuum symmetries halve map generation; both signs are checked below.
    positive = np.array([[direct(r, z)[[0, 2]] for r in rs]
                         for z in zs[len(zs) // 2:]])
    with filename.open("w") as stream:
        stream.write("# DES-026 vacuum annular winding: r_mm z_mm Br_T Bz_T; r fastest\n")
        for z in zs:
            values = positive[round(abs(z) / dz)].copy()
            if z < 0:
                values[:, 0] *= -1
            for r, (br, bz) in zip(rs, values):
                stream.write(f"{r:.12g} {z:.12g} {br:.16g} {bz:.16g}\n")
    mapped = acts.MagneticFieldMapRz(
        file=str(filename), lengthUnit=acts.UnitConstants.mm,
        bFieldUnit=acts.UnitConstants.T, firstQuadrant=False,
    )
    cache = mapped.makeCache(acts.MagneticFieldContext())

    def mapped_value(r, z):
        return np.asarray(mapped.getField(acts.Vector3(r, 0, z), cache)) / acts.UnitConstants.T

    # Deterministic off-grid samples cover the tracker, both z signs and its ends.
    rng = np.random.default_rng(field_cfg["validation_seed"])
    points = [(float(r), float(z)) for r, z in zip(
        rng.uniform(0, 1201, 128), rng.uniform(-4001, 4001, 128))]
    points += [(r, z) for r in (0, 600.3, 1199.7)
               for z in (-3999.3, -3599.3, -2999.3, 0, 2999.3, 3599.3, 3999.3)]
    map_error = max(float(np.linalg.norm(mapped_value(r, z) - direct(r, z)))
                    for r, z in points)
    finer = providers(result, radial_order, 2 * coils)
    radial_finer = providers(result, 2 * radial_order, coils)
    convergence_points = points[::8]
    coil_error = max(float(np.linalg.norm(direct(r, z) - finer(r, z)))
                     for r, z in convergence_points)
    radial_error = max(float(np.linalg.norm(direct(r, z) - radial_finer(r, z)))
                       for r, z in convergence_points)
    module_path = ROOT / "tools/solenoid_baseline/model.py"
    spec = importlib.util.spec_from_file_location("des026_field_source", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    axis_checks = []
    for z in (0, 1000, 2000, 3000, 3600, 4000):
        expected = module.axis_field(
            z / 1000, result["cold_inner_radius_m"], result["winding_outer_radius_m"],
            result["cold_mass_length_m"], result["central_field_T"],
        )
        actual = float(direct(0, z)[2])
        axis_checks.append(dict(z_mm=z, direct_Bz_T=actual, analytic_Bz_T=expected,
                                error_T=abs(actual - expected)))
    tolerance = field_cfg["validation_tolerance_T"]
    if max(map_error, coil_error, radial_error,
           max(v["error_T"] for v in axis_checks)) > tolerance:
        raise ValueError(f"field validation exceeded {tolerance} T: "
                         f"map={map_error}, coils={coil_error}, radial={radial_error}")
    report = {
        "status": "PASS", "scope": "DES-026 PROTOTYPE vacuum field; no iron or material effects",
        "source": source_hashes, "source_parameters": result,
        "configuration": field_cfg, "grid_shape_r_z": [len(rs), len(zs)],
        "map_sha256": sha256(filename), "script_sha256": sha256(__file__),
        "central_field_T": mapped_value(0, 0).tolist(),
        "maximum_interpolation_error_T": map_error,
        "maximum_axial_coil_refinement_error_T": coil_error,
        "maximum_radial_quadrature_refinement_error_T": radial_error,
        "validation_points_r_z_mm": points, "axis_checks": axis_checks,
        "generation_seconds": time.monotonic() - started,
        "python": platform.python_version(), "acts_version": str(acts.__version__),
        "execution_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    }
    (output / "field-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS field: {len(rs)} x {len(zs)}; interpolation error {map_error:.6g} T")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("study.json"))
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    generate(arguments.output, json.loads(arguments.config.read_text()))
