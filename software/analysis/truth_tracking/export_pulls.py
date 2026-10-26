#!/usr/bin/env python3
"""Export full all-eta truth-minus-reconstructed pull distributions."""

import argparse
import gzip
import json
from pathlib import Path
import subprocess

import awkward as ak
import numpy as np
import uproot

from export_profiles import PARAMETERS, event_indices, flat, read_case, sha256
from pull_histograms import BOUND, bound_pulls, common_edges, histogram


SOURCES = ("export_pulls.py", "pull_histograms.py", "export_profiles.py", "metrics.py")


def case_values(directory, campaign):
    metadata, eta, audit, old_values, old_flags, fitted_mask, finite_fit = read_case(
        directory, campaign, production=True)
    with uproot.open(directory / "particles.root") as stream:
        generated = stream["particles"].arrays(
            ["event_id", "phi", "theta", "q_over_p", "vt"], library="ak")
    parameters = (*PARAMETERS, "eT")
    branches = ["event_nr", "track_nr", "hasFittedParams"]
    branches += [name + "_fit" for name in parameters]
    branches += ["cov_" + a + "_" + b for a in parameters for b in parameters]
    with uproot.open(directory / "tracksummary_kf.root") as stream:
        tracks = stream["tracksummary"].arrays(branches, library="ak")
    track_events = ak.to_numpy(ak.flatten(ak.broadcast_arrays(
        tracks["event_nr"], tracks["track_nr"])[0]))
    indices = event_indices(ak.to_numpy(generated["event_id"]), track_events)
    truth = np.column_stack([np.zeros(len(eta)), np.zeros(len(eta)),
                             flat(generated, "phi"), flat(generated, "theta"),
                             flat(generated, "q_over_p"), flat(generated, "vt")])
    # Both ROOT writers retain bound time in ACTS length units (ct/mm), so the
    # generated vt and fitted eT/cov_eT_eT are directly compatible. Current vt=0.
    fitted = np.column_stack([flat(tracks, name + "_fit") for name in parameters])
    covariance = np.empty((len(fitted), 6, 6))
    for i, a in enumerate(parameters):
        for j, b in enumerate(parameters):
            covariance[:, i, j] = flat(tracks, "cov_" + a + "_" + b)
    pulls, flags = bound_pulls(fitted, truth[indices], covariance)
    has_parameters = flat(tracks, "hasFittedParams").astype(bool)
    pulls[~has_parameters] = np.nan
    aligned = np.full((len(eta), 6), np.nan)
    aligned[indices] = pulls
    values = {name: aligned[fitted_mask, i] for i, name in enumerate(BOUND)}
    valid6 = np.zeros(len(eta), dtype=bool)
    valid6[indices] = flags["valid_covariance"] & flags["finite_parameters"] & has_parameters
    pt = -old_values["pt_relative"]["pull"].copy()
    pt[~valid6] = np.nan
    values["pt_relative"] = pt[fitted_mask]
    if np.any(eta < campaign["eta_range"][0]) or np.any(eta > campaign["eta_range"][1]):
        raise ValueError("Generated eta outside the declared all-eta sample")
    time_variance = covariance[:, 5, 5]
    time_sigma = np.sqrt(time_variance[np.isfinite(time_variance) & (time_variance > 0)])
    metadata.update(
        fit_tracks=int(fitted_mask.sum()), finite_fitted_parameters=int(finite_fit.sum()),
        invalid_six_parameter_covariance=int((~flags["valid_covariance"]).sum()),
        nonfinite_six_parameter_fit=int((~flags["finite_parameters"]).sum()),
        generated_time_range_native=[float(truth[:, 5].min()), float(truth[:, 5].max())],
        fitted_time_sigma_range_native=[float(time_sigma.min()), float(time_sigma.max())] if len(time_sigma) else [None, None])
    return metadata, values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("pulls_config.json"))
    parser.add_argument("--campaign", type=Path, default=Path(__file__).with_name("campaign.json"))
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    config, campaign = [json.loads(path.read_text()) for path in (args.config, args.campaign)]
    if (config["sign"] != "truth_minus_reconstructed" or tuple(config["bound_parameters"]) != BOUND
            or config["derived_parameters"] != ["pt_relative"] or config["eta_range"] != campaign["eta_range"]):
        raise ValueError("Unexpected pull-distribution contract")
    cases = [case_values(args.input / f"{sim}-pt{pt:g}", campaign)
             for sim in campaign["simulations"] for pt in campaign["pt_GeV"]]
    quantities = [*BOUND, "pt_relative"]
    edges = {name: common_edges([values[name] for _, values in cases],
                               config["core_limit"], config["core_bin_width"],
                               config["tail_bins_per_decade"]) for name in quantities}
    samples = []
    for metadata, values in cases:
        metadata["quantities"] = {name: histogram(values[name], edges[name], config["core_limit"])
                                  for name in quantities}
        for result in metadata["quantities"].values():
            if result["underflow"] or result["overflow"]:
                raise ValueError("A finite pull escaped the full-range histogram")
            if result["entries"] + result["nonfinite"] != metadata["fit_tracks"]:
                raise ValueError("Pull histogram no longer accounts for every fitted track")
        samples.append(metadata)
        print(metadata["simulation"], metadata["pt_GeV"], metadata["fit_tracks"],
              "invalid6cov", metadata["invalid_six_parameter_covariance"], flush=True)
    source = Path(__file__).resolve().parent
    root = source.parents[2]
    data = {"schema_version": 1, "status": "PROTOTYPE", "configuration": config,
            "campaign": campaign, "bin_edges": {key: value.tolist() for key, value in edges.items()},
            "samples": samples,
            "provenance": {"source_revision": subprocess.check_output(
                ["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(),
                "configuration_sha256": sha256(args.config), "campaign_sha256": sha256(args.campaign),
                "source_sha256": {name: sha256(source / name) for name in SOURCES},
                "versions": {"numpy": np.__version__, "uproot": uproot.__version__, "awkward": ak.__version__}},
            "method": "All eta, no residual/quality/tail cuts. Truth-minus-fit with wrapped phi and fitted marginal sigma; full six-dimensional covariance must be positive definite. pT uses full theta/qOverP propagation. Unique seed-associated native Fake partial fits retained. Density=count/(all finite entries*bin width), including tails outside the companion core view. Time is unconstrained by measurements and remains a seed/fitter-prior diagnostic."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(gzip.compress((json.dumps(data, indent=2, allow_nan=False) + "\n").encode(), mtime=0))


if __name__ == "__main__":
    main()
