#!/usr/bin/env python3
"""Verify native TProfiles against per-track sums, then export compact plot data."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import uproot
from unrooted.io.root import load

COMPONENTS = [f"{d}_{s}" for d in ("beam_pipe", "pixel", "short_strip", "long_strip")
              for s in ("nonsensitive", "sensitive")]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Categorized profiles.root")
    parser.add_argument("--output", type=Path, required=True, help="Compact profiles.json")
    parser.add_argument("--expected-tracks", type=int)
    args = parser.parse_args()
    report = json.loads(Path(str(args.input) + ".json").read_text())
    if args.expected_tracks is not None:
        assert report["tracks"] == args.expected_tracks
    assert report["tracks"] > 0
    assert report["unassigned_steps"] == report["density_mismatches"] == 0
    with uproot.open(args.input) as source:
        data = source["categorized_tracks"].arrays(library="np")
        assert len(data["eta"]) == report["tracks"]
        occupancy = {axis: source[f"tracks_{axis}"].values() for axis in ("eta", "abs_eta", "phi")}
    result = {"schema_version": 1, "components": COMPONENTS,
              "classification": {k: v for k, v in report.items() if k != "materials"},
              "source_profiles_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
              "axes": {}, "sensitivity_allocation_bound": {}, "checks": {}}
    for axis, counts in occupancy.items():
        assert counts.sum() == report["tracks"]
        assert np.all(counts > 1)
        coordinate = np.abs(data["eta"]) if axis == "abs_eta" else data[axis]
        group = {"counts": counts.astype(int).tolist(), "quantities": {}}
        for quantity in ("X0", "L0"):
            summed = sum(data[f"{c}_{quantity}"] for c in COMPONENTS)
            np.testing.assert_allclose(summed, data[f"recorded_{quantity}"], rtol=6e-6, atol=2e-6)
            result["checks"][f"maximum_per_track_{quantity}_closure_absolute"] = float(np.max(np.abs(summed-data[f"recorded_{quantity}"])))
            native_total = load(args.input, f"total_{quantity}_vs_{axis}")
            edges = native_total.axes[0].edges
            index = np.searchsorted(edges, coordinate, side="right") - 1
            assert np.all((index >= 0) & (index < len(counts)))
            np.testing.assert_array_equal(np.bincount(index, minlength=len(counts)), counts)
            group["edges"] = edges.tolist()
            quantities = {}
            for name in [*COMPONENTS, "total"]:
                key = f"{name}_{quantity}_vs_{axis}"
                profile = load(args.input, key)
                with uproot.open(args.input) as source:
                    np.testing.assert_array_equal(source[key].counts(flow=False), counts)
                samples = summed if name == "total" else data[f"{name}_{quantity}"]
                mean = np.bincount(index, weights=samples, minlength=len(counts))/counts
                variance = (np.bincount(index, weights=samples*samples, minlength=len(counts))/counts-mean*mean)/counts
                np.testing.assert_allclose(profile.values, mean, rtol=1e-12, atol=1e-13)
                np.testing.assert_allclose(profile.variances, np.maximum(0, variance), rtol=1e-8, atol=1e-14)
                quantities[name] = {"mean": profile.values.tolist(), "variance": profile.variances.tolist()}
            np.testing.assert_allclose(sum(np.asarray(quantities[c]["mean"]) for c in COMPONENTS), native_total.values,
                                       rtol=2e-13, atol=2e-14)
            group["quantities"][quantity] = quantities
            bound = np.bincount(index, weights=data[f"rounding_ambiguous_{quantity}"], minlength=len(counts))/counts
            result["sensitivity_allocation_bound"][f"{quantity}_vs_{axis}_maximum_bin_mean"] = float(bound.max())
        result["axes"][axis] = group
    result["checks"].update({
        "all_tracks_filled_in_every_component": True,
        "common_counts": True, "all_bins_populated": True,
        "native_means_and_variances_match_independent_per_track_reduction": True,
        "variance_convention": "ROOT population SEM squared: M2/N^2",
        "total_uncertainty": "Calculated from per-track totals, including component covariance",
    })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(f"PASS: {report['tracks']:,} tracks; native profiles and per-track reductions agree")


if __name__ == "__main__":
    main()
