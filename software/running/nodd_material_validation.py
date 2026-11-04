#!/usr/bin/env python3
"""Validate a selected nODD Gen3 material map with independent straight rays.

Uses native ACTS MaterialValidator. The independent particle gun samples eta
and phi uniformly from configurable ranges; no Geant4 simulation is rerun.
"""

import argparse
import math
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis/gen3_material_mapping"))
from material_runtime import (common_arguments, load_manifest, native_imports,
                              prepare_geometry, provenance, root_summary, write_report)


def run_validation(args, surfaces, acts):
    from acts.examples.simulation import addParticleGun, EtaConfig, PhiConfig, ParticleConfig
    from acts.examples.root import RootMaterialTrackWriter
    level = acts.logging.WARNING
    sequencer = acts.examples.Sequencer(events=args.events, numThreads=args.threads)
    addParticleGun(sequencer,
        ParticleConfig(num=args.tracks, pdg=acts.PdgParticle.eMuon, randomizeCharge=True),
        EtaConfig(*args.eta_range, uniform=True), PhiConfig(*args.phi_range),
        rnd=acts.examples.RandomNumbers(seed=args.seed), logLevel=level)
    sequencer.addAlgorithm(acts.examples.ParticleTrackParamExtractor(
        level=level, inputParticles="particles_generated", outputTrackParameters="material_parameters"))
    assign_config = acts.IntersectionMaterialAssigner.Config()
    assign_config.surfaces = surfaces
    validator_config = acts.MaterialValidator.Config()
    validator_config.materialAssigner = acts.IntersectionMaterialAssigner(assign_config, level)
    sequencer.addAlgorithm(acts.examples.MaterialValidation(
        level=level, inputTrackParameters="material_parameters",
        materialValidator=acts.MaterialValidator(validator_config, level),
        outputMaterialTracks="material_validation"))
    sequencer.addWriter(RootMaterialTrackWriter(
        level=level, inputMaterialTracks="material_validation", treeName="material_tracks",
        filePath=str(args.output / "material_validation.root"), storeSurface=True, storeVolume=False))
    sequencer.run()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    common_arguments(parser)
    parser.add_argument("--map", dest="map_path", type=Path, required=True)
    parser.add_argument("--tracks", type=int, default=100, help="Tracks per event")
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--seed", type=int, default=43)
    parser.add_argument("--eta-range", nargs=2, type=float, default=(-4.5, 4.5))
    parser.add_argument("--phi-range", nargs=2, type=float, default=(-math.pi, math.pi),
                        help="Phi range in radians")
    args = parser.parse_args()
    if args.events <= 0 or args.tracks <= 0 or args.threads == 0 or args.threads < -1:
        parser.error("Events/tracks must be positive and threads must be -1 or positive")
    if any(not all(math.isfinite(x) for x in pair) or pair[0] >= pair[1]
           for pair in (args.eta_range, args.phi_range)):
        parser.error("Finite increasing eta/phi ranges required")
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest(args.manifest)
    ROOT, acts, sidecar = native_imports(args.native_module_dir)
    start = time.monotonic()
    detector, geometry, context, surfaces, decoration = prepare_geometry(
        args, manifest, acts, sidecar, args.map_path.resolve())
    run_validation(args, surfaces, acts)
    summary = root_summary(ROOT, args.output / "material_validation.root")
    if summary["tracks"] != args.events * args.tracks:
        raise RuntimeError("Validation track count differs from the configured gun")
    report = {"schema_version": 1, "status": "PROTOTYPE", "algorithm": "ACTS MaterialValidator + IntersectionMaterialAssigner",
              "sampling": {"events": args.events, "tracks_per_event": args.tracks,
                           "seed": args.seed, "threads": args.threads,
                           "eta_uniform": args.eta_range, "phi_uniform_rad": args.phi_range,
                           "vertex_mm": [0., 0., 0.], "straight_rays": True},
              "native_decoration": decoration, "track_budgets": summary,
              "wall_seconds": time.monotonic() - start,
              "provenance": provenance(args, sidecar, [("material_map", args.map_path.resolve()),
                  ("validation_tracks", args.output / "material_validation.root")])}
    report["provenance"]["ROOT"] = ROOT.gROOT.GetVersion()
    write_report(args.output / "validation-report.json", report)
    print({"selected_portals": len(surfaces), "budgets": summary})


if __name__ == "__main__":
    main()
