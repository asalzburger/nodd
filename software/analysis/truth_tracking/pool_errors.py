#!/usr/bin/env python3
"""Pool independent geometric-training residuals across every cluster size."""
import argparse
import json
from pathlib import Path
import subprocess

import numpy as np
import uproot

from calibrate_errors import sha256


def moments(residuals):
    values = np.asarray(residuals, dtype=float)
    if values.ndim != 1 or len(values) < 2 or not np.all(np.isfinite(values)):
        raise ValueError("Require at least two finite training residuals")
    sigma = float(np.std(values, ddof=0))
    if sigma <= 0:
        raise ValueError("Pooled training width must be positive")
    return dict(entries=len(values), mean_mm=float(np.mean(values)), sigma_mm=sigma,
                uncentered_rms_mm=float(np.sqrt(np.mean(values**2))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report_path = args.training / "run-report.json"
    report = json.loads(report_path.read_text())
    training = report["campaign"]["error_training"]
    path = args.training / "measurements.root"
    if (report["outcome"] != "completed" or report["simulation"] != "fatras" or
            not report["training"] or report["events"] != training["events"] or
            training["seed"] == report["campaign"]["seed"]):
        raise ValueError("Require the complete independent Fatras training sample")
    if [f["sha256"] for f in report["provenance"]["files"] if f["name"] == path.name] != [sha256(path)]:
        raise ValueError("Training ROOT hash differs from recorded native input")
    config_path = args.training / "digitization.json"
    if [f["sha256"] for f in report["provenance"]["files"] if f["name"] == config_path.name] != [sha256(config_path)]:
        raise ValueError("Training digitization hash differs from native report")
    config = json.loads(config_path.read_text())
    expected = {}
    for entry in config["entries"]:
        geo = entry["value"]["geometric"]
        axes = geo["segmentation"]["binningdata"]
        pitch = (axes[0]["max"] - axes[0]["min"]) / axes[0]["bins"]
        settings = report["campaign"]["digitization"]
        if geo["indices"] == [0] and np.isclose(pitch, settings["long_strip_pitch_mm"]):
            family = "long_strip"
        elif geo["indices"] == [0, 1] and np.isclose(pitch, settings["pixel_pitch_mm"][0]):
            family = "pixel"
        elif geo["indices"] == [0, 1] and np.isclose(pitch, settings["short_strip_pitch_mm"][0]):
            family = "short_strip"
        else:
            raise ValueError("Unrecognized training sensor coordinate/pitch contract")
        for index in geo["indices"]:
            key = entry["volume"], index
            if key in expected and expected[key] != family:
                raise ValueError("One volume/coordinate mixes sensor families")
            expected[key] = family
    columns = ["volume_id", *[p + str(i) for i in (0, 1) for p in ("rec_loc", "true_loc", "clus_size_loc")]]
    with uproot.open(path) as stream:
        data = stream["measurements"].arrays(columns, library="np")
    if set(map(int, np.unique(data["volume_id"]))) != {v for v, _ in expected}:
        raise ValueError("Training coverage differs from sensitive-volume inventory")
    groups = []
    for (volume, index), family in sorted(expected.items()):
        mask = data["volume_id"] == volume
        if np.any(data["clus_size_loc" + str(index)][mask] < 1):
            raise ValueError("Empty measured training cluster")
        residual = data["rec_loc" + str(index)][mask].astype(float) - data["true_loc" + str(index)][mask].astype(float)
        groups.append(dict(volume=volume, index=index, sensor_family=family, **moments(residual)))
    root = Path(__file__).resolve().parents[3]
    result = dict(schema_version=1, status="PROTOTYPE",
                  width_convention="Centered population SD of rec_loc - true_loc over ALL cluster sizes, per ACTS volume and measured coordinate. Zero-mean Gaussian cross-check; no cuts or pull tuning.",
                  measurements=len(data["volume_id"]), volumes=len({v for v, _ in expected}), groups=groups,
                  provenance=dict(training_report_sha256=sha256(report_path), training_measurements_sha256=sha256(path),
                                  training_digitization_sha256=sha256(config_path), training=training,
                                  source_sha256=sha256(Path(__file__)),
                                  source_revision=subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(),
                                  versions=dict(numpy=np.__version__, uproot=uproot.__version__)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(f"Pooled {result['measurements']} measurements: {result['volumes']} volumes, {len(groups)} measured coordinates")


if __name__ == "__main__":
    main()
