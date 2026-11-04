#!/usr/bin/env python3
"""Map the complete recorded nODD inventory onto selected native Gen3 portals.

Isolated PROTOTYPE. Requires the explicitly selected ACTS/DD4hep runtime and
task-local nodd_portal_material sidecar. No physical geometry is modified.
"""

import argparse
import gc
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis/gen3_material_mapping"))
from material_runtime import (apply_saved_map, budget_partition, common_arguments, load_manifest, native_imports,
                              prepare_geometry, provenance, root_summary, write_report)


def run_mapping(args, detector, geometry, context, surfaces, acts, sidecar):
    from acts.examples.root import RootMaterialTrackReader, RootMaterialTrackWriter
    from acts.examples.json import JsonMaterialWriter, JsonFormat
    level = acts.logging.WARNING
    sequencer = acts.examples.Sequencer(events=args.events, numThreads=1)
    sequencer.addReader(RootMaterialTrackReader(
        level=level, outputMaterialTracks="material_recorded", treeName="material_tracks",
        fileList=[str(args.input.resolve())], readCachedSurfaceInformation=False))
    sequencer.addAlgorithm(sidecar.midpoint_algorithm("material_recorded", "material_midpoints"))
    assign_config = acts.IntersectionMaterialAssigner.Config()
    assign_config.surfaces = surfaces
    accumulator_config = acts.BinnedSurfaceMaterialAccumulator.Config()
    accumulator_config.materialSurfaces = surfaces
    accumulator_config.emptyBinCorrection = True
    mapper_config = acts.MaterialMapper.Config()
    mapper_config.assignmentFinder = acts.IntersectionMaterialAssigner(assign_config, level)
    mapper_config.surfaceMaterialAccumulator = acts.BinnedSurfaceMaterialAccumulator(accumulator_config, level)
    converter = acts.json.MaterialMapJsonConverter.Config(
        processSensitives=True, processApproaches=True, processRepresenting=True,
        processBoundaries=True, processVolumes=False)
    writer = JsonMaterialWriter(level=level, converterCfg=converter,
        fileName=str(args.output / "material_map"), writeFormat=JsonFormat.Json)
    mapping = acts.examples.MaterialMapping.Config(context)
    mapping.materialMapper = acts.MaterialMapper(mapper_config, level)
    mapping.inputMaterialTracks = "material_midpoints"
    mapping.mappedMaterialTracks = "material_mapped"
    mapping.unmappedMaterialTracks = "material_unmapped"
    mapping.materialWriters = [writer]
    sequencer.addAlgorithm(acts.examples.MaterialMapping(mapping, level))
    for collection, filename in (("material_mapped", "mapped.root"), ("material_unmapped", "unmapped.root")):
        sequencer.addWriter(RootMaterialTrackWriter(
            level=level, inputMaterialTracks=collection, treeName="material_tracks",
            filePath=str(args.output / filename), storeSurface=True, storeVolume=False))
    sequencer.run()
    # The pinned native algorithm finalizes/writes its maps in its destructor.
    del sequencer
    gc.collect()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    common_arguments(parser)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    if args.events <= 0:
        parser.error("--events must be positive")
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest(args.manifest)
    ROOT, acts, sidecar = native_imports(args.native_module_dir)
    start = time.monotonic()
    detector, geometry, context, surfaces, decoration = prepare_geometry(args, manifest, acts, sidecar)
    run_mapping(args, detector, geometry, context, surfaces, acts, sidecar)
    map_path = args.output / "material_map.json"
    if not map_path.is_file():
        raise RuntimeError("Native mapper did not serialize a material map")
    # Validate the exact serialized identities and reload onto native geometry.
    reload_report = apply_saved_map(geometry, manifest, acts, map_path, sidecar)
    summaries = {"input": root_summary(ROOT, args.input.resolve(), args.events),
                 "mapped": root_summary(ROOT, args.output / "mapped.root"),
                 "unmapped": root_summary(ROOT, args.output / "unmapped.root")}
    closure = {axis: summaries["mapped"][f"sum_{axis}"] + summaries["unmapped"][f"sum_{axis}"]
               - summaries["input"][f"sum_{axis}"] for axis in ("X0", "L0")}
    for axis in ("X0", "L0"):
        if abs(closure[axis]) > 1.e-5 * max(1., summaries["input"][f"sum_{axis}"]):
            raise RuntimeError(f"Mapped/unmapped material budget does not close for {axis}")
    if any(summaries[name]["tracks"] != summaries["input"]["tracks"] for name in ("mapped", "unmapped")):
        raise RuntimeError("Mapped/unmapped files lost input tracks")
    partition = budget_partition(ROOT, args.input.resolve(), args.output / "mapped.root",
                                 args.output / "unmapped.root", args.events)
    report = {"schema_version": 1, "status": "PROTOTYPE", "algorithm": "ACTS MaterialMapper + IntersectionMaterialAssigner + BinnedSurfaceMaterialAccumulator",
              "position_convention": "Recorded Geant4 pre-step positions moved to position + 0.5 * slab thickness * recorded unit direction before native mapping; original recording unchanged.",
              "assignment_rule": "Closest intersected selected surface along the straight ray. Carrier selection is before/after a layer; this mapper does not enforce strict per-step pre/post assignment.",
              "empty_bin_correction": True, "events_requested": args.events,
              "native_decoration": decoration, "serialized_reload": reload_report,
              "track_budgets": summaries, "budget_closure_absolute": closure,
              "per_track_budget_partition": partition,
              "wall_seconds": time.monotonic() - start,
              "provenance": provenance(args, sidecar, [("recording", args.input.resolve()),
                  ("material_map", map_path), ("mapped_tracks", args.output / "mapped.root"),
                  ("unmapped_tracks", args.output / "unmapped.root")])}
    report["provenance"]["ROOT"] = ROOT.gROOT.GetVersion()
    write_report(args.output / "mapping-report.json", report)
    print({"selected_portals": len(surfaces), "budgets": summaries, "closure": closure})


if __name__ == "__main__":
    main()
