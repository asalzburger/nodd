#!/usr/bin/env python3
"""Run native ACTS example propagation through the current DD4hep-backed tracker."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nodd-dir", type=Path, required=True)
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--field-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pt-gev", type=float, required=True)
    parser.add_argument("--tracks", type=int, default=8192)
    parser.add_argument("--seed", type=int, default=20261023)
    parser.add_argument("--eta-min", type=float, default=-4)
    parser.add_argument("--eta-max", type=float, default=4)
    parser.add_argument("--max-step-mm", type=float, default=50)
    args = parser.parse_args()
    if args.pt_gev <= 0 or args.tracks <= 0 or args.max_step_mm <= 0 or args.eta_min >= args.eta_max:
        parser.error("positive momentum/count/step and increasing eta bounds required")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    # A failed or interrupted rerun must never retain a previous PASS report.
    (output / "run.json").write_text(json.dumps({"status": "NATIVE_RUNNING_ACCOUNTING_PENDING"}) + "\n")
    import acts
    import acts.examples as examples
    from acts.examples.nodd import getNoddDetector
    from acts.examples.root import RootPropagationSummaryWriter, RootPropagationStepsWriter
    from acts.examples.simulation import addParticleGun, EtaConfig, PhiConfig, ParticleConfig, MomentumConfig
    level, unit = acts.logging.WARNING, acts.UnitConstants
    started = time.monotonic()
    detector = getNoddDetector(nodd_dir=args.nodd_dir, build_dir=args.build_dir, logLevel=level)
    world = detector.trackingGeometry().highestTrackingVolume
    if not isinstance(world.volumeBounds, acts.CylinderVolumeBounds):
        raise ValueError("this study requires the current cylindrical tracking world")
    bounds = world.volumeBounds.values()
    world_report = {"name": world.volumeName, "volume_id": int(world.geometryId.volume),
                    "center_mm": list(world.center(detector.nominalGeometryContext())),
                    "r_min_mm": bounds[0], "r_max_mm": bounds[1], "half_z_mm": bounds[2]}
    if any(abs(value) > 1e-9 for value in world_report["center_mm"]):
        raise ValueError("this study requires the current origin-centered tracking world")
    geometry = json.loads(detector.geometryReport())
    (output / "surfaces.json").write_text(json.dumps(geometry))
    field_path = args.field_map.resolve()
    field = acts.MagneticFieldMapRz(file=str(field_path), lengthUnit=unit.mm,
                                    bFieldUnit=unit.T, firstQuadrant=False)
    sequence = examples.Sequencer(events=args.tracks, numThreads=1,
                                  logLevel=level, trackFpes=False)
    addParticleGun(
        sequence,
        particleConfig=ParticleConfig(num=1, pdg=acts.PdgParticle.eMuon, randomizeCharge=True),
        momentumConfig=MomentumConfig(args.pt_gev * unit.GeV, args.pt_gev * unit.GeV, transverse=True),
        etaConfig=EtaConfig(args.eta_min, args.eta_max, uniform=True),
        phiConfig=PhiConfig(-3.141592653589793, 3.141592653589793),
        rnd=examples.RandomNumbers(seed=args.seed), outputDirRoot=output,
        logLevel=level,
    )
    sequence.addAlgorithm(examples.ParticleTrackParamExtractor(
        level=level, inputParticles="particles_generated", outputTrackParameters="start_parameters"))
    navigator = acts.Navigator(trackingGeometry=detector.trackingGeometry())
    propagator = examples.ConcretePropagator(acts.Propagator(acts.EigenStepper(field), navigator))
    sequence.addAlgorithm(examples.PropagationAlgorithm(
        propagatorImpl=propagator, level=level, sterileLogger=False,
        energyLoss=False, multipleScattering=False, recordMaterialInteractions=False,
        maxStepSize=args.max_step_mm * unit.mm,
        inputTrackParameters="start_parameters", outputSummaryCollection="propagation_summary"))
    sequence.addWriter(RootPropagationSummaryWriter(
        level=level, inputSummaryCollection="propagation_summary", filePath=str(output / "summary.root")))
    sequence.addWriter(RootPropagationStepsWriter(
        level=level, collection="propagation_summary", filePath=str(output / "steps.root")))
    sequence.run()
    libraries = args.build_dir.resolve() / "detector"
    factory_hashes = {p.name: digest(p) for p in libraries.glob("libnODD*") if p.is_file()}
    install = Path(acts.__file__).resolve().parents[2]
    runtime_hashes = {p.name: digest(p) for p in (install / "lib").glob("libActs*.*")
                      if p.is_file() and any(s in p.name for s in ("Core", "Nodd", "Root", "DD4hep"))}
    for cls in (acts.SolenoidBField, examples.PropagationAlgorithm, RootPropagationSummaryWriter):
        module = importlib.import_module(cls.__module__)
        path = getattr(module, "__file__", None)
        if path and Path(path).is_file():
            runtime_hashes[Path(path).name] = digest(path)
    config = {
        "tracks": args.tracks, "pt_GeV": args.pt_gev, "seed": args.seed,
        "eta_range": [args.eta_min, args.eta_max], "eta_uniform": True,
        "phi_range": [-3.141592653589793, 3.141592653589793], "vertex_mm": [0, 0, 0],
        "randomize_charge": True, "maximum_step_mm": args.max_step_mm,
        "energy_loss": False, "multiple_scattering": False, "one_probe_per_event": True,
    }
    report = {
        "status": "NATIVE_COMPLETED_ACCOUNTING_PENDING", "configuration": config,
        "field_map_sha256": digest(field_path),
        "field_report": json.loads(field_path.with_name("field-report.json").read_text()),
        "tracker_compact_sha256": digest(libraries / "tracker/tracker.xml"),
        "expected_inventory_sha256": digest(libraries / "tracker/expected.json"),
        "factory_sha256": factory_hashes, "runtime_binary_sha256": runtime_hashes,
        "script_sha256": digest(__file__), "acts_version": str(acts.__version__),
        "python": platform.python_version(), "platform": platform.system(), "machine": platform.machine(),
        "execution_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=args.nodd_dir, text=True).strip(),
        "execution_dirty_paths": subprocess.check_output(["git", "status", "--porcelain"], cwd=args.nodd_dir, text=True).splitlines(),
        "elapsed_native_seconds": time.monotonic() - started,
        "native_sensitive_surfaces": len(geometry["sensors"]), "native_volumes": len(geometry["volumes"]),
        "tracking_world": world_report,
    }
    (output / "run.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Native completed: {args.tracks} probes at pT={args.pt_gev:g} GeV; accounting remains required")


if __name__ == "__main__":
    main()
