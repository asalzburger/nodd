#!/usr/bin/env python3
"""Run the pinned ACTS hit-error script and audit its native overflow groups."""

import argparse
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess

import numpy as np


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def reconcile_table(measurements, original, minimum_entries=2):
    """Preserve raw vector lengths except explicitly merged unsupported tails.

    Native lookup clamps size >= K onto entry K. The untouched script records
    exact size K even when its plot uses a pooled tail. Recompute that last
    entry from >=K; never derive errors from fitted-track pulls.
    """
    table = json.loads(json.dumps(original))
    groups = []
    for entry in table["entries"]:
        volume = entry["volume"]
        volume_mask = np.asarray(measurements["volume_id"]) == volume
        for coordinate in entry["value"]:
            index = coordinate["index"]
            sizes = np.asarray(measurements["clus_size_loc" + str(index)])[volume_mask]
            residuals = (np.asarray(measurements["rec_loc" + str(index)], dtype=float)[volume_mask]
                         - np.asarray(measurements["true_loc" + str(index)], dtype=float)[volume_mask])
            if not np.all(np.isfinite(residuals)) or np.any(sizes < 1):
                raise ValueError("Nonfinite residual or empty measured cluster")
            raw_rms = list(coordinate["rms"])
            k = len(raw_rms)
            if not k:
                raise ValueError("Empty raw RMS vector")
            merged = None
            for size in range(1, k):
                if np.sum(sizes == size) < minimum_entries:
                    merged = size
                    k = size
                    break
            corrected = []
            for size in range(1, k + 1):
                tail = size == k
                selected = residuals[sizes >= size if tail else sizes == size]
                if selected.size < minimum_entries:
                    raise ValueError(f"Unsupported training group volume={volume}, coordinate={index}, size={size}")
                width = float(np.std(selected, ddof=0))
                if not np.isfinite(width) or width <= 0:
                    raise ValueError("Training group has nonpositive population SD")
                corrected.append(width)
                groups.append({
                    "volume": volume, "index": index, "cluster_size": size,
                    "upper_inclusive": None if tail else size,
                    "tail": tail, "entries": int(selected.size),
                    "mean_mm": float(np.mean(selected)), "population_sd_mm": width,
                    "uncentered_rms_mm": float(np.sqrt(np.mean(selected ** 2))),
                    "raw_rms_mm": raw_rms[size - 1] if np.isfinite(raw_rms[size - 1]) else None,
                    "raw_vector_length": len(raw_rms), "corrected_vector_length": k,
                    "unsupported_tail_merged_at": merged,
                })
            coordinate["rms"] = corrected
    return table, groups


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training", type=Path, required=True,
                        help="Independent Fatras training case containing measurements.root")
    parser.add_argument("--acts-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parents[3]
    cache = root / "build/truth-tracking-baseline/plot-cache"
    os.environ["MPLBACKEND"] = "Agg"
    os.environ.setdefault("MPLCONFIGDIR", str(cache / "matplotlib"))
    os.environ.setdefault("XDG_CACHE_HOME", str(cache / "xdg"))
    import pandas as pd
    import uproot
    import matplotlib.pyplot as plt
    source = args.acts_source / "Examples/Scripts/Digitization/error_parameterisation.py"
    report = json.loads((args.training / "run-report.json").read_text())
    if report["outcome"] != "completed" or report["simulation"] != "fatras":
        raise ValueError("Require a complete independent Fatras training run")
    expected_events = report["campaign"]["error_training"]["events"]
    if report["events"] != expected_events:
        raise ValueError("Training event count differs from campaign")
    source_revision = subprocess.check_output(
        ["git", "-C", str(args.acts_source), "rev-parse", "HEAD"], text=True).strip()
    if source_revision != report["provenance"]["ACTS_source_revision"]:
        raise ValueError("Calibration script source differs from native ACTS source")
    path = args.training / "measurements.root"
    expected_hash = [f["sha256"] for f in report["provenance"]["files"] if f["name"] == path.name]
    if expected_hash != [sha256(path)]:
        raise ValueError("Training measurement hash differs from native report")
    columns = ["volume_id", "rec_gx", "rec_gy", "rec_gz", "true_x", "true_y", "true_z"]
    columns += [prefix + str(index) for index in (0, 1)
                for prefix in ("rec_loc", "true_loc", "var_loc", "clus_size_loc")]
    with uproot.open(path) as stream:
        measurements = stream["measurements"].arrays(columns, library="pd")
    config = json.loads((args.training / "digitization.json").read_text())
    expected = {}
    for item in config["entries"]:
        geo = item["value"].get("geometric")
        if geo:
            expected.setdefault(item["volume"], set()).update(geo["indices"])
    observed = set(int(v) for v in measurements["volume_id"].unique())
    if observed != set(expected):
        raise ValueError("Training measurements do not cover every configured sensitive volume")
    for volume, coordinates in expected.items():
        selected = measurements[measurements["volume_id"] == volume]
        actual = {index for index in (0, 1)
                  if np.all(np.isfinite(selected["rec_loc" + str(index)]))}
        if actual != coordinates:
            raise ValueError("Training measured-coordinate dimensions differ from configuration")
    spec = importlib.util.spec_from_file_location("acts_hit_error_parameterisation", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    raw_path = args.output / "hit-error-parameterization-raw.json"
    settings = report["campaign"]["error_training"]
    class ScalarMeasurementTree:
        def arrays(self, library):
            if library != "pd":
                raise ValueError("Upstream script requested an unexpected representation")
            return measurements.copy()

    # Supply exactly the scalar columns used by the unchanged upstream function.
    # Unrelated jagged barcode branches would require awkward-pandas merely to
    # discard them; this projection preserves every calibration observation.
    module.run_error_parametriation(
        {"measurements": ScalarMeasurementTree()}, None,
        [(v, "Gen3 volume " + str(v)) for v in sorted(expected)],
        output_dir=root / "build/truth-tracking-baseline/error-parameterization-upstream",
        json_out=str(raw_path),
        break_min_stat=settings["break_min_stat"],
        break_rms_change=settings["break_rms_change"],
        break_cluster_size=settings["break_cluster_size"],
        plot_pulls=False)
    plt.close("all")
    original = json.loads(raw_path.read_text())
    if {e["volume"] for e in original["entries"]} != set(expected):
        raise ValueError("Raw ACTS parameterization omitted sensitive volumes")
    corrected, groups = reconcile_table(measurements, original)
    final_path = args.output / "hit-error-parameterization.json"
    final_path.write_text(json.dumps(corrected, indent=2, allow_nan=False) + "\n")
    audit = {
        "schema_version": 1, "status": "PROTOTYPE",
        "method": "Unmodified ACTS error_parameterisation.py output retained; independently recompute each exact-size group before the final vector entry, and pool all sizes >= final entry to match native overflow. Merge an unsupported exact group and all subsequent sizes into an explicit tail. Centered population SD, not uncentered RMS. No residual cuts or pull tuning.",
        "ACTS_source_revision": source_revision, "ACTS_script_sha256": sha256(source),
        "coordinator_source_sha256": sha256(Path(__file__)),
        "training_report_sha256": sha256(args.training / "run-report.json"),
        "training_measurements_sha256": sha256(path),
        "raw_table_sha256": sha256(raw_path), "table_sha256": sha256(final_path),
        "training": settings, "configuration": report["campaign"],
        "measurements": len(measurements), "volumes": len(expected),
        "scalar_columns": columns,
        "versions": {"numpy": np.__version__, "pandas": pd.__version__, "uproot": uproot.__version__},
        "groups": groups,
    }
    (args.output / "hit-error-training-audit.json").write_text(
        json.dumps(audit, indent=2, allow_nan=False) + "\n")
    print(f"Retained raw ACTS output and audited {len(groups)} volume/coordinate/cluster groups; "
          f"frozen table SHA256 {audit['table_sha256']}")


if __name__ == "__main__":
    main()
