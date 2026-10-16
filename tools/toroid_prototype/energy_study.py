"""Reproduce DES-039 complete vacuum energy and its discretization controls.

Run from the repository root:
    python3 -B -m tools.toroid_prototype.energy_study

The final row is source/target pack orders 6/7, 32 segments per rounded corner,
and 16 target Gauss nodes per straight polygon segment. No map-box truncation,
uniform-bore proxy or wire-radius cutoff enters this stored-energy calculation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import time

import numpy as np

from .energy import integrate_current_dot_potential, magnetic_energy
from .system import (coil_source, load_design, normalize_currents,
                     solenoid_parameters, solenoid_sources, toroid_sources)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STUDY_ROWS = ((4, 5, 16, 4), (6, 7, 16, 4), (6, 7, 32, 4),
              (6, 7, 32, 8), (6, 7, 32, 16))
REFERENCE_TARGETS_T = {"barrel": 1.0, "endcap": 1.0}
METHOD = ("All-space vacuum energy via complete finite-pack J dot A. "
          "Distinct source/target cross-section Gauss rules; every same-coil, "
          "same-family and ordered mutual contribution retained without cutoff. "
          "Exact straight-segment A and longitudinal Gauss integration. "
          "Full twelvefold sources and one representative target per family.")


def source_configuration(config):
    """Only inputs entering the current-source energy integral; excludes cold envelopes."""
    result = {key: config[key] for key in ("folds", "pack", "coil_groups", "stations")}
    # The benchmark station geometry sets normalization. Exclude operating-point
    # commentary that no longer applies after the explicit raw-target override.
    result["field_target"] = {name: {key: target[key] for key in
                             ("eta", "phi_deg", "sagitta_equivalent_B_T")}
                             for name, target in config["field_target"].items()}
    return result


def reference_design():
    """Fixed raw 1 T / 1 T energy reference, independent of the operating target."""
    config = load_design()
    for name, field in REFERENCE_TARGETS_T.items():
        config["field_target"][name]["sagitta_equivalent_B_T"] = field
    return config


def normalize_reference(config):
    """Derive and retain raw 1 T / 1 T currents for the captured source geometry."""
    return normalize_currents(config, order=4, corners=16)


def solenoid_mutual_control(config):
    """Numeric test of the exact zero mutual energy from meridional symmetry."""
    solenoid, factor = solenoid_sources(radial_order=2, z_order=48, segments=192)
    start = time.perf_counter()
    forward = {name: config["folds"]*integrate_current_dot_potential(
        coil_source(config, name, order=3, corners=16), solenoid,
        line_order=16, backend="cpp", by_group=False) for name in config["coil_groups"]}
    toroid = toroid_sources(config, order=3, corners=16)
    reverse = integrate_current_dot_potential(solenoid, toroid, line_order=4,
                                             backend="cpp", by_group=True)
    return {
        "source_solenoid_radial_order": 2, "source_solenoid_z_order": 48,
        "source_solenoid_polygon_segments": 192,
        "polygon_solenoid_central_normalization": factor,
        "target_toroid_pack_order": 3, "target_toroid_corner_segments": 16,
        "target_toroid_line_order": 16, "source_toroid_pack_order": 3,
        "source_toroid_corner_segments": 16, "target_solenoid_line_order": 4,
        "toroid_J_dot_solenoid_A_J": forward,
        "solenoid_J_dot_toroid_A_J": dict(zip(toroid.group_names, reverse.tolist())),
        "elapsed_seconds": time.perf_counter()-start,
        "solenoid_self_energy_J": solenoid_parameters()["stored_energy_MJ"]*1e6,
        "symmetry": ("For an axisymmetric solenoid A is azimuthal. A centered "
                     "meridional loop has no azimuthal tangent; +/- tangential "
                     "finite-pack offsets have opposite linked solenoid flux and "
                     "cancel. Complete solenoid-toroid mutual energy is zero. "
                     "The polygon calculation independently tests cancellation.")}


def finalize_report(report, config, mutual_control):
    """Attach the selected result, convergence comparisons and exact input identity."""
    selected = dict(report["studies"][-1])
    report["selected"] = selected
    report["reference_target_override_T"] = REFERENCE_TARGETS_T
    report["reference_currents_Aturn"] = dict(report["normalization"]["currents_Aturn"])
    report["reference_scope"] = ("Raw 1 T barrel / 1 T eta=2 endcap reference. "
                                  "Later operating currents must be represented by "
                                  "explicit quadratic matrix rescaling, not relabeling these raw integrals.")
    report["source_configuration"] = source_configuration(config)
    report["solenoid_mutual_control"] = mutual_control
    report["coupled_energy"] = {
        "toroid_energy_J": selected["total_energy_J"],
        "solenoid_energy_J": mutual_control["solenoid_self_energy_J"],
        "complete_mutual_energy_J": 0.0,
        "total_energy_J": selected["total_energy_J"]+mutual_control["solenoid_self_energy_J"],
        "scope": "Complete coupled vacuum solenoid and toroids; zero mutual follows the stated symmetry."}
    matrix = np.array(selected["energy_matrix_J"])
    # Symmetric equal sharing of each mutual interaction; this is bookkeeping,
    # not a claim that the energy is spatially confined to its owning cold mass.
    allocation = ((matrix+matrix.T)/2).sum(axis=1)
    report["family_equal_mutual_share_energy_J"] = dict(zip(selected["group_names"], allocation.tolist()))
    report["family_allocation_scope"] = ("Equal sharing of each mutual term between families; "
                                         "not a local energy-density or conductor-stress certification.")
    keyed = {(row["source_cross_section_order"], row["target_cross_section_order"],
              row["corner_segments"], row["line_quadrature_order"]): row for row in report["studies"]}
    comparisons = [((3, 4, 16, 4), (4, 5, 16, 4), "cross-section order"),
                   ((4, 5, 16, 4), (6, 7, 16, 4), "cross-section order"),
                   ((6, 7, 16, 4), (6, 7, 32, 4), "rounded-corner segmentation"),
                   ((6, 7, 32, 4), (6, 7, 32, 8), "longitudinal quadrature"),
                   ((6, 7, 32, 8), (6, 7, 32, 16), "longitudinal quadrature"),
                   ((6, 7, 32, 16), (6, 7, 32, 32), "longitudinal quadrature")]
    report["convergence_comparisons"] = [
        {"varied": kind, "coarse": list(coarse), "fine": list(fine),
         "relative_energy_change": keyed[fine]["total_energy_J"]/keyed[coarse]["total_energy_J"]-1}
        for coarse, fine, kind in comparisons if coarse in keyed and fine in keyed]
    report["convergence_scope"] = ("Empirical stability controls for polygon, pack and line discretizations; "
                                     "successive differences are not rigorous mathematical error bounds. "
                                     "No nonlinear material or field-induced current redistribution is modeled.")
    report["reference_controls"] = [
        {"source_id": "SRC-NBS-CIRC-544-1954", "title": "Formulas for Computing Capacitance and Inductance",
         "author": "Chester Snow", "date": "1954-09-10",
         "url": "https://nvlpubs.nist.gov/nistpubs/Legacy/circ/nbscircular544.pdf",
         "locator": "sec.2.2e, printed p.26, eq.2.15, uniform current b=0; sec.2.2h, printed p.28, eq.2.18",
         "control": "Thin round-wire uniform-DC loop and exact parallel-wire Neumann integrals in test_energy.py."}]
    report["reproduction_command"] = "python3 -B -m tools.toroid_prototype.energy_study"
    names = ("field.py", "field_backend.cpp", "energy.py", "energy_study.py",
             "system.py", "design.json", "solenoid-input.json")
    report["source_files_sha256"] = {str((HERE/name).relative_to(ROOT)):
                                      hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in names}
    return report


def run_study(output):
    config = reference_design()
    normalization = normalize_reference(config)
    report = {"status": "PROTOTYPE / DRAFT; complete vacuum energy, no engineering certification",
              "base_revision": config["base_revision"], "method": METHOD,
              "normalization": normalization,
              "source_configuration": source_configuration(config),
              "software": {"python": platform.python_version(), "numpy": np.__version__},
              "studies": []}
    output.parent.mkdir(parents=True, exist_ok=True)
    for source_order, target_order, corners, line in STUDY_ROWS:
        start = time.perf_counter()
        sources = toroid_sources(config, order=source_order, corners=corners)
        targets = {name: coil_source(config, name, order=target_order, corners=corners)
                   for name in config["coil_groups"]}
        row = magnetic_energy(sources, targets, symmetry_multiplicity=config["folds"],
                              line_order=line, reference_currents_Aturn=normalization["currents_Aturn"],
                              backend="cpp")
        row.update(source_cross_section_order=source_order, target_cross_section_order=target_order,
                   corner_segments=corners, source_segments=len(sources.a),
                   elapsed_seconds=time.perf_counter()-start)
        report["studies"].append(row)
        output.write_text(json.dumps(report, indent=2)+"\n")
        print(json.dumps({"source_order": source_order, "target_order": target_order,
                          "corners": corners, "line_order": line,
                          "energy_MJ": row["total_energy_J"]/1e6,
                          "elapsed_seconds": row["elapsed_seconds"]}), flush=True)
    finalize_report(report, config, solenoid_mutual_control(config))
    output.write_text(json.dumps(report, indent=2)+"\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT/"docs/validation/DES-039/energy.json")
    args = parser.parse_args()
    run_study(args.output)


if __name__ == "__main__":
    main()
