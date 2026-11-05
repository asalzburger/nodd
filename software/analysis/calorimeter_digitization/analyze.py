#!/usr/bin/env python3
"""Run the native prototype and retain compact binwise campaign evidence."""
import argparse
import json
from pathlib import Path
import subprocess

from generate import sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=Path, nargs="+", required=True)
    parser.add_argument("--calibration", type=Path, required=True)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--backend", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    calibration = json.loads(args.calibration.read_text())
    root = Path(__file__).resolve().parents[3]
    source_paths = []
    for directory in (root / "software/source/ActsExamples/Calorimeter", root / "software/source/EDM/include/ActsCalorimeter"):
        source_paths.extend(p for p in directory.rglob("*") if p.is_file() and p.suffix in (".cpp", ".hpp", ".h", ".py", ".txt"))
    source_hashes = {str(p.relative_to(root)): sha256(p) for p in sorted(source_paths)}
    source_revision = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    args.work.mkdir(parents=True, exist_ok=True)
    results = []
    generation_manifests = []
    for manifest_path in args.samples:
        manifest = json.loads(manifest_path.read_text())
        generation_manifests.append(dict(sha256=sha256(manifest_path), metadata=manifest))
        for sample in manifest["samples"]:
            path = Path(sample["path"])
            if sample["exit_code"] != 0 or sha256(path) != sample["sha256"]:
                raise ValueError(f"Failed or changed sample: {path}")
            tag = path.parent.name
            config = dict(mip_energy_GeV=calibration["mip_energy_GeV"],
                          noise_MIP=0.13, threshold_MIP=0.6, dynamic_range_MIP=2500,
                          seed=117017, beam_energy_GeV=sample["energy_GeV"],
                          collections=["ECalBarrelCollection", "ECalEndcapCollection"],
                          skip_events=0)
            if sample["particle"] == "mu-" and sample["eta"] == 0:
                if sha256(path) != calibration["input_sha256"]:
                    raise ValueError("Calibration/validation sample mismatch")
                config["skip_events"] = calibration["validation_events"][0]
            config_path = args.work / f"{tag}-config.json"
            summary_path = args.work / f"{tag}-summary.json"
            config_path.write_text(json.dumps(config, indent=2) + "\n")
            subprocess.run([str(args.binary.resolve()), str(path), str(config_path),
                            str(summary_path), str(args.backend.resolve())], check=True)
            result = json.loads(summary_path.read_text())
            result.update(particle=sample["particle"], beam_energy_GeV=sample["energy_GeV"],
                          eta=sample["eta"], phi_rad=sample["phi_rad"],
                          simulation_seed=sample["seed"], input_sha256=sample["sha256"])
            results.append(result)
    result = dict(status="PROTOTYPE characterization; original full-framework comparison pending",
                  model_revision="255967eb855ebbc8f75ebaac190b268b63332e8b",
                  odd_revision=manifest["odd_revision"], calibration=calibration,
                  native_binary_sha256=sha256(args.binary), backend_sha256=sha256(args.backend),
                  source_revision=source_revision, executed_source_sha256=source_hashes,
                  generation_manifests=generation_manifests,
                  analysis_sha256=sha256(Path(__file__)), samples=results,
                  parameter_provenance={"noise_MIP": "0.13: CALICE arXiv:0811.2354v1 comparator setting; not nODD approval",
                                        "threshold_MIP": "0.6: same CALICE comparator setting; not nODD approval",
                                        "dynamic_range_MIP": "2500: original MarlinReco default",
                                        "seed": "117017: reproducibility test choice"})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Retained {len(results)} binwise samples: {args.output}")


if __name__ == "__main__":
    main()
