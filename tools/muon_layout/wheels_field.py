"""DES039/040 isolated shortened-ECT vacuum magnetic candidate, SI units.

Run from the repository root with ``python3 -B -m tools.muon_layout.wheels_field``.
Stages are resumable: configuration, energy, maps, controls, or all. The metadata
stage only clarifies already-computed source descriptions and verifies unchanged
energy numbers and array files. Historical
inputs are hash checked against the pinned commit and are never overwritten.
No current normalizer, material magnetization or ACTS runtime is invoked.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import ctypes
import hashlib
import json
import math
from pathlib import Path
import platform
import shutil
import subprocess
import time

import numpy as np

from tools.toroid_prototype import field
from tools.toroid_prototype.energy import magnetic_energy
from tools.toroid_prototype.energy_study import solenoid_mutual_control
from tools.toroid_prototype.geometry import analytic_sweep_union_volumes, coil_mask
from tools.toroid_prototype.map import FieldMap
from tools.toroid_prototype.run import central_check
from tools.toroid_prototype.system import (
    coil_source, solenoid_parameters, solenoid_sources, toroid_sources)

ROOT = Path(__file__).resolve().parents[2]
REVISION = "a32558a419404dfe741182b6713ce1f31062fd37"
DEFAULT_OUT = ROOT / "docs/validation/DES-040/wheels-2026-10-20/magnetic"
BASE_RESULTS = "docs/validation/DES-039/results.json"
BASE_MAP = "docs/validation/DES-039/joint-field.npz"
STUDY_ROWS = ((4, 5, 16, 4), (6, 7, 16, 4), (6, 7, 32, 4),
              (6, 7, 32, 8), (6, 7, 32, 16))
INPUTS = (
    "docs/design/DES-039-twelvefold-toroid.md",
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/validation/DES-040/geometry.json",
    "docs/validation/DES-040/support-input.json",
    "docs/validation/DES-040/wheels-2026-10-20/coverage-plan.md",
    "tools/muon_layout/design.json", "tools/muon_layout/geometry.py",
    "tools/muon_layout/layout.py", BASE_RESULTS, BASE_MAP,
    "tools/toroid_prototype/solenoid-input.json")
SOLVER_FILES = (
    "tools/toroid_prototype/field.py", "tools/toroid_prototype/field_backend.cpp",
    "tools/toroid_prototype/system.py", "tools/toroid_prototype/geometry.py",
    "tools/toroid_prototype/energy.py", "tools/toroid_prototype/energy_study.py",
    "tools/toroid_prototype/map.py", "tools/toroid_prototype/run.py")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def pinned_bytes(path):
    return subprocess.check_output(["git", "-C", str(ROOT), "show", f"{REVISION}:{path}"])


def provenance():
    hashes = {}
    for path in INPUTS + SOLVER_FILES:
        digest = hashlib.sha256(pinned_bytes(path)).hexdigest()
        hashes[path] = digest
        # The selected amendment is intentionally newer than the task base.
        if path not in INPUTS[:2] and sha(ROOT / path) != digest:
            raise ValueError("pinned input or imported solver changed: " + path)
    return {
        "input_revision": REVISION, "pinned_sha256": hashes,
        "selected_amendment_worktree_sha256": {
            p: sha(ROOT / p) for p in INPUTS[:2]},
        "candidate_script_sha256": sha(__file__),
        "software": {"python": platform.python_version(), "numpy": np.__version__,
                     "platform": platform.platform()},
        "scope": "isolated complete vacuum source model; no nonlinear HCAL response or engineering certification"}


def configure(out):
    out.mkdir(parents=True, exist_ok=True)
    p = provenance()
    baseline = json.loads(pinned_bytes(BASE_RESULTS))["configuration"]
    candidate = deepcopy(baseline)
    for name, sign in (("endcap_plus", 1), ("endcap_minus", -1)):
        candidate["coil_groups"][name]["center_z_m"] = sign * 9.5
        candidate["coil_groups"][name]["half_z_m"] = 2.2
    for c in (baseline, candidate):
        c["map"]["z_min_m"], c["map"]["z_max_m"] = -14.3125, 14.3125
    candidate["status"] = "PROTOTYPE / shortened ECT, retained currents, vacuum only"
    tag_historical_station_reference(candidate)
    result = {
        "status": "configuration fixed; energy-sized cold recomputation pending",
        "configuration": candidate, "baseline_configuration": baseline,
        "currents_Aturn": {name: g["ampere_turns_per_coil"]
                           for name, g in candidate["coil_groups"].items()},
        "current_policy": "exact retained operating values; no current retuning or normalizer call",
        "pack_current_density_A_mm2": {name: g["ampere_turns_per_coil"] /
            (candidate["pack"]["normal_m"] * candidate["pack"]["tangent_m"] * 1e6)
            for name, g in candidate["coil_groups"].items()},
        "cold_status": "inherited values provisional until energy stage",
        "source_change": {"endcap_front_centerline_abs_z_m": [6.8, 7.3],
                          "endcap_rear_centerline_abs_z_m": 11.7,
                          "endcap_warm_front_abs_z_m": 7.05},
        "provenance": p}
    write_json(out / "configuration.json", result)
    return result


def tag_historical_station_reference(candidate):
    """Keep old current-selection references outside the magnetic source inputs.

    The finite-pack energy, fields, masks and central-field checks never consume
    station geometry or response targets. Actual candidate chambers are owned by
    wheels.py and its separate geometry artifacts.
    """
    reference = candidate.setdefault("historical_station_normalization_reference", {})
    for key in ("stations", "field_target"):
        if key in candidate:
            reference[key] = candidate.pop(key)
    candidate.pop("historical_station_target_status", None)
    reference.update(
        scope="Historical baseline current-selection metadata only; not candidate chamber coordinates, new targets or achieved response.",
        source_revision=REVISION, source_path=BASE_RESULTS,
        candidate_solver_usage="Neither stations nor field_target is read by this fixed-current energy/field generator.")
    candidate["candidate_chamber_geometry_owner"] = (
        "tools/muon_layout/wheels.py and separately generated candidate/geometry.json; "
        "this magnetic configuration does not define chamber positions or achieved momentum response")


def energy_numbers_digest(report):
    """Canonical exact JSON digest of all energy-result data, excluding descriptions."""
    numbers = {k: v for k, v in report.items() if k not in
               ("provenance", "source_configuration", "metadata_revision")}
    return hashlib.sha256(json.dumps(numbers, sort_keys=True, allow_nan=False,
                                    separators=(",", ":")).encode()).hexdigest()


def metadata_stage(out):
    """Clarify source metadata without evaluating or changing magnetic physics."""
    record = json.loads((out/"configuration.json").read_text())
    energy = json.loads((out/"energy.json").read_text())
    provenance()  # imported solver and immutable baseline input identities
    array_hashes = {p.name: sha(p) for p in sorted(out.glob("*.npz"))}
    energy_digest = energy_numbers_digest(energy)
    source_keys = ("folds", "pack", "cold", "warm", "coil_groups", "map")
    source_before = [{k: deepcopy(c[k]) for k in source_keys}
                     for c in (record["configuration"], energy["source_configuration"])]
    old_source = record["provenance"]["candidate_script_sha256"]
    revision = {
        "scope": "metadata-only historical station/normalization-reference clarification; no magnetic numerical rerun",
        "current_generator_script_sha256": sha(__file__),
        "original_numerical_execution_script_sha256": old_source,
        "energy_numerical_content_sha256": energy_digest,
        "unchanged_array_files_sha256": array_hashes,
        "command": "python3 -B -m tools.muon_layout.wheels_field --stage metadata"}
    tag_historical_station_reference(record["configuration"])
    tag_historical_station_reference(energy["source_configuration"])
    # Preserve the actual calculation's original provenance rather than
    # implying that unchanged numerical arrays were recomputed with new code.
    for document in (record, energy):
        document["metadata_revision"] = revision
    write_json(out/"energy.json", energy)
    record["energy_sha256"] = sha(out/"energy.json")
    write_json(out/"configuration.json", record)
    for name in ("map-metadata.json", "controls.json"):
        document = json.loads((out/name).read_text())
        document["metadata_revision"] = revision
        write_json(out/name, document)
    after_energy = energy_numbers_digest(json.loads((out/"energy.json").read_text()))
    after_arrays = {p.name: sha(p) for p in sorted(out.glob("*.npz"))}
    source_after = [{k: c[k] for k in source_keys}
                    for c in (record["configuration"], energy["source_configuration"])]
    if (energy_digest != after_energy or array_hashes != after_arrays
            or source_before != source_after):
        raise AssertionError("metadata refresh changed energy numbers or magnetic array bytes")
    checks = dict(revision, energy_numbers_unchanged=True, array_files_byte_identical=True,
                  candidate_source_geometry_unchanged=True,
                  configuration_sha256=sha(out/"configuration.json"))
    write_json(out/"metadata-controls.json", checks)
    manifest = json.loads((out/"manifest.json").read_text())
    manifest["candidate_script_sha256"] = sha(__file__)
    manifest["original_numerical_execution_script_sha256"] = old_source
    manifest["metadata_revision"] = revision
    if revision["command"] not in manifest["commands"]:
        manifest["commands"].append(revision["command"])
    manifest["artifact_sha256"] = {
        str(p.relative_to(out)): sha(p) for p in sorted(out.iterdir())
        if p.suffix in (".json", ".npz") and p.name != "manifest.json"}
    write_json(out/"manifest.json", manifest)
    print(json.dumps(checks, indent=2))


def backend(out):
    """Load the unchanged exact kernel from a task-owned build cache only."""
    source = ROOT / "tools/toroid_prototype/field_backend.cpp"
    compiler = shutil.which("c++")
    if compiler is None:
        raise RuntimeError("system C++ compiler unavailable")
    cache = out / ".cache"
    cache.mkdir(exist_ok=True)
    digest = hashlib.sha256(source.read_bytes() + compiler.encode()).hexdigest()[:16]
    library = cache / f"field-{digest}.so"
    command = [compiler, "-std=c++17", "-O3", "-DNDEBUG", "-shared", "-fPIC",
               "-pthread", str(source), "-o", str(library)]
    if not library.exists():
        subprocess.run(command, check=True, capture_output=True, text=True)
    loaded = ctypes.CDLL(str(library))
    pointer = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")
    integers = np.ctypeslib.ndpointer(dtype=np.int32, flags="C_CONTIGUOUS")
    loaded.field_evaluate.argtypes = [ctypes.c_size_t, pointer, ctypes.c_size_t,
        pointer, pointer, pointer, integers, ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, pointer, pointer]
    loaded.field_evaluate.restype = ctypes.c_int
    field._CPP_LIBRARY = loaded
    report = {"source_sha256": sha(source), "library_sha256": sha(library),
              "compile_command": command, "compiler_version": subprocess.check_output(
                  [compiler, "--version"], text=True).splitlines()[0],
              "threads": 8, "cache": str(cache.relative_to(ROOT)),
              "shared_dependency_changes": False}
    write_json(out / "backend.json", report)
    return report


def energy_stage(out, record):
    c = record["configuration"]
    report = {"status": "PROTOTYPE / all-space vacuum energy", "studies": [],
              "source_configuration": deepcopy(c), "provenance": provenance(),
              "current_policy": record["current_policy"],
              "method": "Complete exact-segment A, staggered finite-pack J dot A; every self/mutual term retained; C12 representatives"}
    for source_order, target_order, corners, line in STUDY_ROWS:
        start = time.perf_counter()
        src = toroid_sources(c, order=source_order, corners=corners)
        targets = {name: coil_source(c, name, order=target_order, corners=corners)
                   for name in c["coil_groups"]}
        row = magnetic_energy(src, targets, symmetry_multiplicity=c["folds"],
                              line_order=line, reference_currents_Aturn=record["currents_Aturn"],
                              backend="cpp", threads=8)
        row.update(source_cross_section_order=source_order,
                   target_cross_section_order=target_order, corner_segments=corners,
                   source_segments=len(src.a), elapsed_seconds=time.perf_counter()-start)
        report["studies"].append(row)
        write_json(out / "energy.json", report)
        print(json.dumps({"stage": "energy", "orders": [source_order, target_order, corners, line],
                          "energy_MJ": row["total_energy_J"]/1e6,
                          "elapsed_s": row["elapsed_seconds"]}), flush=True)
    report["selected"] = report["studies"][-1]
    report["convergence_comparisons"] = [
        {"coarse": list(STUDY_ROWS[i-1]), "fine": list(STUDY_ROWS[i]),
         "relative_energy_change": report["studies"][i]["total_energy_J"] /
             report["studies"][i-1]["total_energy_J"] - 1}
        for i in range(1, len(STUDY_ROWS))]
    report["solenoid_mutual_control"] = solenoid_mutual_control(c)
    report["toroid_energy_J"] = report["selected"]["total_energy_J"]
    report["solenoid_self_energy_J"] = solenoid_parameters()["stored_energy_MJ"]*1e6
    report["solenoid_toroid_mutual_energy_J"] = 0.0
    report["complete_energy_J"] = report["toroid_energy_J"] + report["solenoid_self_energy_J"]
    report["limits"] = ("Successive discretization differences are empirical, not rigorous bounds. "
                        "Pinned converged solenoid self-energy; exact zero mutual by axisymmetric/meridional symmetry, checked bidirectionally numerically. "
                        "Uniform vacuum current packs; no conductor, nonlinear iron, forces or quench model.")
    write_json(out / "energy.json", report)
    # Retain the previously established aspect ratio, solve UNIQUE shared cold
    # volume, and stay strictly inside the analytic union solver's guards.
    target = report["toroid_energy_J"]/30e6
    ratio = .24/.35
    def volume(area, order):
        c["cold"] = {"normal_m": math.sqrt(area*ratio), "tangent_m": math.sqrt(area/ratio)}
        return analytic_sweep_union_volumes(c, width="cold", order=order)
    lower, upper = .06001, .133
    vlo, vhi = [volume(a, 128)["sum_group_union_volume_m3"] for a in (lower, upper)]
    if not vlo < target < vhi:
        raise ValueError("cold allocation outside verified analytic-union bracket")
    for _ in range(40):
        mid = (lower+upper)/2
        if volume(mid, 128)["sum_group_union_volume_m3"] < target:
            lower = mid
        else:
            upper = mid
    result = volume((lower+upper)/2, 256)
    result.update(cold_cross_section_m=deepcopy(c["cold"]),
                  target_toroid_volume_m3=target,
                  complete_energy_J=report["complete_energy_J"],
                  complete_cold_volume_m3=result["sum_group_union_volume_m3"] + solenoid_parameters()["cold_volume_m3"],
                  aspect_ratio_normal_to_tangent=ratio,
                  verified_area_bracket_m2=[.06001, .133])
    result["complete_energy_density_MJ_m3"] = report["complete_energy_J"]/result["complete_cold_volume_m3"]/1e6
    result["relative_volume_residual"] = result["sum_group_union_volume_m3"]/target-1
    result["union_quadrature_control"] = {
        "order_128_volume_m3": volume((lower+upper)/2, 128)["sum_group_union_volume_m3"],
        "order_256_volume_m3": result["sum_group_union_volume_m3"]}
    result["fits_retained_warm"] = all(c["pack"][key] < c["cold"][key] < c["warm"][key]
                                       for key in ("normal_m", "tangent_m"))
    result["scope"] = "global coupled vacuum U/V allocation of geometric cold UNION, not spatial local energy density or engineered mass"
    if not result["fits_retained_warm"]:
        raise ValueError("new energy-sized cold allocation does not fit retained warm envelope")
    write_json(out / "cold.json", result)
    record.update(status="fixed-current shortened-ECT configuration with recomputed cold allocation",
                  cold_status="recomputed from complete all-space vacuum energy",
                  energy_sha256=sha(out/"energy.json"), cold_sha256=sha(out/"cold.json"))
    write_json(out / "configuration.json", record)
    print(json.dumps({"stage": "cold", "complete_energy_GJ": report["complete_energy_J"]/1e9,
                      "cold_m": c["cold"]}), flush=True)


def cartesian(r, z, phi):
    rr, zz, pp = np.meshgrid(r, z, np.radians(phi), indexing="ij")
    return np.column_stack((rr.ravel()*np.cos(pp.ravel()), rr.ravel()*np.sin(pp.ravel()), zz.ravel()))


def cylindrical(b, points):
    phi = np.arctan2(points[:, 1], points[:, 0])
    cs, sn = np.cos(phi), np.sin(phi)
    return np.column_stack((b[:, 0]*cs+b[:, 1]*sn, -b[:, 0]*sn+b[:, 1]*cs, b[:, 2]))


def symmetry_control(c, src):
    rng = np.random.default_rng(901020)
    r, z, ph = rng.uniform(.2, 9.5, 80), rng.uniform(.1, 14.3, 80), rng.uniform(0, 15, 80)
    points = np.column_stack((r*np.cos(np.radians(ph)), r*np.sin(np.radians(ph)), z))
    b = cylindrical(field.evaluate(points, src, backend="cpp"), points)
    zm = points.copy(); zm[:, 2] *= -1
    bz = cylindrical(field.evaluate(zm, src, backend="cpp"), zm)
    pm = np.column_stack((r*np.cos(np.radians(30-ph)), r*np.sin(np.radians(30-ph)), z))
    bp = cylindrical(field.evaluate(pm, src, backend="cpp"), pm)
    dz = float(np.max(abs(bz-b*np.array([1, 1, -1]))))
    dp = float(np.max(abs(bp-b*np.array([-1, 1, -1]))))
    if max(dz, dp) > 1e-10:
        raise ValueError("discrete-source symmetry identity failed")
    return {"samples": len(points), "max_z_reflection_absolute_T": dz,
            "max_phi_reflection_absolute_T": dp,
            "identities": "toroid cylindrical z reflection (+,+,-), phi→30deg-phi (-,+,-)",
            "scope": "exact source symmetry verified numerically, not a coarser source approximation"}


def toroid_grid(c, r, z, phi):
    """Evaluate only nonnegative z and half-sector, using verified exact symmetry."""
    src = toroid_sources(c, order=4, corners=16)
    control = symmetry_control(c, src)
    unique_z = np.unique(abs(z))
    unique_phi = phi[phi <= 15]
    points = cartesian(r, unique_z, unique_phi)
    # At R=0 atan2(0,0) cannot identify the requested cylindrical frame. Use
    # explicit grid phi, matching the historical map generator exactly.
    angles = np.broadcast_to(np.radians(unique_phi), (len(r), len(unique_z), len(unique_phi))).ravel()
    values = np.empty((len(points), 3))
    for start in range(0, len(points), 32768):
        stop = min(start+32768, len(points))
        b = field.evaluate(points[start:stop], src, backend="cpp", threads=8)
        cs, sn = np.cos(angles[start:stop]), np.sin(angles[start:stop])
        values[start:stop] = np.column_stack((b[:, 0]*cs+b[:, 1]*sn,
                                             -b[:, 0]*sn+b[:, 1]*cs, b[:, 2]))
        if start % (32768*4) == 0:
            print(json.dumps({"stage": "toroid-grid", "evaluated": stop, "total": len(points)}), flush=True)
    values = values.reshape(len(r), len(unique_z), len(unique_phi), 3)
    # Enforce exact symmetry-plane zeros at floating-point cancellation scale.
    values[:, :, 0, [0, 2]] = 0
    values[:, :, -1, [0, 2]] = 0
    if unique_z[0] == 0:
        values[:, 0, :, 2] = 0
    full = np.empty((len(r), len(z), len(phi), 3))
    zi = np.searchsorted(unique_z, abs(z))
    for k, angle in enumerate(phi):
        pk = int(round(min(angle, 30-angle)/.625))
        full[:, :, k, :] = values[:, zi, pk, :]
        if angle > 15:
            full[:, :, k, 0] *= -1; full[:, :, k, 2] *= -1
    full[:, z < 0, :, 2] *= -1
    return full, control


def solenoid_grid(r, z, phi, sol):
    r2, z2 = np.meshgrid(r, z, indexing="ij")
    points = np.column_stack((r2.ravel(), np.zeros(r2.size), z2.ravel()))
    b = field.evaluate(points, sol, backend="cpp", threads=8).reshape(len(r), len(z), 3)
    b[:, :, 1] = 0
    return np.broadcast_to(b[:, :, None, :], (len(r), len(z), len(phi), 3))


def masks(c, r, z, phi):
    points = cartesian(r, z, phi)
    rr, zz, _ = np.meshgrid(r, z, phi, indexing="ij")
    par = solenoid_parameters()
    dr = np.maximum.reduce((par["cold_inner_radius_m"]-rr, rr-par["winding_outer_radius_m"], np.zeros_like(rr)))
    dz = np.maximum(abs(zz)-par["cold_mass_length_m"]/2, 0)
    valid = (np.hypot(dr, dz) > c["map"]["pack_guard_m"])
    valid &= ~coil_mask(points, c, width="pack", clearance=c["map"]["pack_guard_m"]).reshape(rr.shape)
    warm = coil_mask(points, c, width="warm").reshape(rr.shape)
    return valid, warm


def map_stage(out, record):
    sol, factor = solenoid_sources()
    with np.load(ROOT/BASE_MAP) as f:
        old = {k: f[k] for k in f.files}
    r, phi = old["r_m"], old["phi_deg"]
    z = np.arange(-14.3125, 14.3125+1e-8, .0625)
    old_index = np.searchsorted(z, old["z_m"])
    if not np.array_equal(z[old_index], old["z_m"]):
        raise ValueError("extended grid does not preserve old nodes")
    extension = np.ones(len(z), bool); extension[old_index] = False
    metadata = {"provenance": provenance(), "solenoid_polygon_normalization": factor,
                "source_quadrature": {"toroid_pack_order": 4, "toroid_corner_segments": 16,
                                      "solenoid_radial_order": 3, "solenoid_z_order": 96,
                                      "solenoid_polygon_segments": 192}, "maps": {}}
    for tag, c, selected_z in (("baseline-extended", record["baseline_configuration"], z[extension]),
                               ("candidate", record["configuration"], z)):
        start = time.perf_counter()
        tor, sym = toroid_grid(c, r, selected_z, phi)
        total = tor + solenoid_grid(r, selected_z, phi, sol)
        valid, warm = masks(c, r, selected_z, phi)
        total[:, :, -1] = total[:, :, 0]
        total[~valid] = np.nan
        if tag == "baseline-extended":
            shape = (len(r), len(z), len(phi))
            combined = np.empty(shape+(3,), dtype="f4")
            validity, warmth = np.empty(shape, bool), np.empty(shape, bool)
            combined[:, old_index] = old["B_total_cyl_T"]
            validity[:, old_index] = old["valid_field"]
            warmth[:, old_index] = old["inside_toroid_warm_reservation"]
            combined[:, extension] = total.astype("f4")
            validity[:, extension], warmth[:, extension] = valid, warm
        else:
            combined, validity, warmth = total.astype("f4"), valid, warm
        path = out/f"{tag}-map.npz"
        np.savez_compressed(path, r_m=r, z_m=z, phi_deg=phi,
                            B_total_cyl_T=combined, valid_field=validity,
                            inside_toroid_warm_reservation=warmth)
        if path.stat().st_size >= 100_000_000:
            raise ValueError("map artifact exceeds 100 MB contract")
        metadata["maps"][tag] = {
            "path": str(path.relative_to(ROOT)), "sha256": sha(path), "bytes": path.stat().st_size,
            "shape_r_z_phi_components": list(combined.shape),
            "range_r_z_phi": [[float(r[0]), float(r[-1])], [float(z[0]), float(z[-1])], [float(phi[0]), float(phi[-1])]],
            "spacing_r_z_phi": [.0625, .0625, .625], "valid_nodes": int(validity.sum()),
            "all_nodes": int(validity.size), "symmetry_control": sym,
            "elapsed_seconds": time.perf_counter()-start,
            "query_policy": "C12 cylindrical trilinear interpolation; ANY invalid corner rejects, no extrapolation or zero filling",
            "mask": "finite uniform current pack plus 0.10m guard; warm envelope stored separately",
            "field_model": "complete joint vacuum field; unchanged axisymmetric solenoid plus all 36 finite-pack toroids"}
        write_json(out/"map-metadata.json", metadata)
        print(json.dumps({"stage": tag, **metadata["maps"][tag]}), flush=True)
    return metadata


def query_one(f, point):
    try:
        return {"status": "valid", "B_cart_T": f.field([point])[0].tolist()}
    except ValueError as error:
        return {"status": "rejected", "reason": str(error)}


def controls_stage(out, record):
    start = time.perf_counter()
    report = {"status": "executed numerical controls, vacuum prototype", "provenance": provenance()}
    sol, factor = solenoid_sources()
    c = record["configuration"]
    src = toroid_sources(c, order=4, corners=16)
    report["central_field"] = central_check(src, sol)
    if not report["central_field"]["passes_sampled_cap"]:
        raise ValueError("complete sampled central field exceeds 5T cap")
    maps = {name: FieldMap(out/f"{name}-map.npz") for name in ("baseline-extended", "candidate")}
    with np.load(ROOT/BASE_MAP) as old, np.load(out/"baseline-extended-map.npz") as new:
        zi = np.searchsorted(new["z_m"], old["z_m"])
        checks = {key: bool(np.array_equal(old[key], new[key][:, zi], equal_nan=True))
                  for key in ("B_total_cyl_T", "valid_field", "inside_toroid_warm_reservation")}
        checks.update(r_axis_exact=bool(np.array_equal(old["r_m"], new["r_m"])),
                      phi_axis_exact=bool(np.array_equal(old["phi_deg"], new["phi_deg"])),
                      z_axis_exact=bool(np.array_equal(old["z_m"], new["z_m"][zi])))
        report["baseline_old_node_parity"] = {"passed": all(checks.values()), "checks": checks,
            "source_map_sha256": sha(ROOT/BASE_MAP), "original_z_nodes": len(zi)}
    if not report["baseline_old_node_parity"]["passed"]:
        raise ValueError("old baseline nodes or masks changed")
    rng = np.random.default_rng(901021)
    rows, convergence = {}, {}
    for name, f in maps.items():
        cfg = record["baseline_configuration"] if name == "baseline-extended" else c
        sources = toroid_sources(cfg, order=4, corners=16)
        points = []
        for _ in range(800):
            radius, zz, phi = rng.uniform(.15, 9.2), rng.uniform(-14.2, 14.2), rng.uniform(0, 360)
            p = [radius*math.cos(math.radians(phi)), radius*math.sin(math.radians(phi)), zz]
            if query_one(f, p)["status"] != "valid":
                continue
            if coil_mask([p], cfg, width="warm", clearance=.30)[0]:
                continue
            # Solenoid finite-loop pack interior is outside this interpolation
            # diagnostic; field availability is checked independently below.
            if radius < 1.8 and abs(zz) < 4.2:
                continue
            points.append(p)
            if len(points) == 160:
                break
        points = np.asarray(points)
        direct = field.evaluate(points, sources, backend="cpp") + axisymmetric_solenoid(points, sol)
        got = f.field(points)
        delta = np.linalg.norm(got-direct, axis=1)
        # Direct field source convergence at the identical retained currents.
        fine = toroid_sources(cfg, order=6, corners=32)
        df = field.evaluate(points, fine, backend="cpp") - field.evaluate(points, sources, backend="cpp")
        convergence[name] = {"samples": len(points), "max_absolute_T": float(np.linalg.norm(df, axis=1).max()),
                            "rms_absolute_T": float(np.sqrt(np.mean(df*df)*3)),
                            "nominal": [4, 16], "fine": [6, 32],
                            "scope": "deterministic clear-volume samples, >=0.30m outside warm; no global or near-source error bound"}
        rows[name] = {"samples": len(points), "points_m": points.tolist(),
                      "max_absolute_T": float(delta.max()), "rms_absolute_T": float(np.sqrt(np.mean(delta**2))),
                      "max_relative_norm": float(np.max(delta/np.linalg.norm(direct, axis=1))),
                      "scope": "whole extended-domain deterministic clear-volume sample; not a maximum error certificate"}
    report["direct_interpolation"] = rows
    report["source_discretization"] = convergence
    probes = []
    # Extension, original z seam, C12 seam and relocated return/mask probes.
    for z in (-14.25, -13.05, -12.500001, -12.5, -12.499999, 6.5, 6.7456, 7.3, 12.499999, 12.5, 12.500001, 13.05, 14.25):
        for phi in (0., 14.999999, 29.999999, 30., 30.000001):
            for r in ((2., 4.6) if z == 7.3 else (3.,)):
                angle = math.radians(phi)
                point = [r*math.cos(angle), r*math.sin(angle), z]
                probes.append({"r_z_phi": [r, z, phi], "point_m": point,
                               **{name: query_one(f, point) for name, f in maps.items()}})
    # Explicit masked current-pack points and domain failures must reject.
    failures = {}
    for name, f in maps.items():
        cfg = record["baseline_configuration"] if name == "baseline-extended" else c
        g = cfg["coil_groups"]["endcap_plus"]
        ph = math.radians(g["phi_offset_deg"])
        tests = {
            "toroid_pack": [g["center_r_m"]*math.cos(ph), g["center_r_m"]*math.sin(ph), g["center_z_m"]-g["half_z_m"]],
            "solenoid_pack": [1.35, 0., 0.], "outside_z": [3., 0., 14.3126], "outside_r": [9.5001, 0., 0.]}
        failures[name] = {key: {"point_m": point, **query_one(f, point)} for key, point in tests.items()}
        if any(v["status"] != "rejected" for v in failures[name].values()):
            raise ValueError("strict masked/domain rejection control failed")
    report["fresh_query_points"] = probes
    report["strict_rejections"] = failures
    report["C12_periodic_endpoint_exact"] = {}
    for name in maps:
        with np.load(out/f"{name}-map.npz") as f:
            report["C12_periodic_endpoint_exact"][name] = bool(np.array_equal(
                f["B_total_cyl_T"][:, :, 0], f["B_total_cyl_T"][:, :, -1], equal_nan=True))
    report["solenoid_polygon_normalization"] = factor
    report["elapsed_seconds"] = time.perf_counter()-start
    report["limitations"] = ["No nonlinear HCAL magnetization, forces, structural, cryogenic, quench or conductor-margin qualification.",
        "Central cap check is a tracker-region sampled control, not peak conductor field certification.",
        "Map masks are numerical field availability; rejected points are not assigned zero field.",
        "Interpolation and discretization controls cover explicit samples, not rigorous whole-domain maxima.",
        "Historical response targets/station metadata are superseded; no new chamber momentum response is inferred here."]
    write_json(out/"controls.json", report)
    print(json.dumps({"stage": "controls", "central_field": report["central_field"],
                      "baseline_parity": report["baseline_old_node_parity"],
                      "interpolation": {k: {a:b for a,b in v.items() if a != "points_m"} for k,v in rows.items()}}), flush=True)
    return report


def axisymmetric_solenoid(points, sol):
    points = np.asarray(points)
    r = np.hypot(points[:, 0], points[:, 1])
    b = field.evaluate(np.column_stack((r, r*0, points[:, 2])), sol, backend="cpp")
    ph = np.arctan2(points[:, 1], points[:, 0])
    return np.column_stack((b[:, 0]*np.cos(ph), b[:, 0]*np.sin(ph), b[:, 2]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--stage", choices=("all", "configuration", "energy", "maps", "controls", "metadata"), default="all")
    args = parser.parse_args()
    out = args.output.resolve()
    if args.stage == "metadata":
        metadata_stage(out)
        return
    if args.stage in ("all", "configuration"):
        record = configure(out)
    else:
        record = json.loads((out/"configuration.json").read_text())
        provenance()  # never resume with changed imported solver/input bytes
    if args.stage == "configuration":
        return
    backend(out)
    if args.stage in ("all", "energy"):
        energy_stage(out, record)
    if args.stage in ("all", "maps"):
        if record["cold_status"] != "recomputed from complete all-space vacuum energy":
            raise ValueError("run energy stage before maps")
        map_stage(out, record)
    if args.stage in ("all", "controls"):
        controls_stage(out, record)


if __name__ == "__main__":
    main()
