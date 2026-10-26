#!/usr/bin/env python3
"""Compare Gaussian and geometric Fatras pulls with strict native identity checks."""
import argparse
import gzip
import json
from pathlib import Path
import subprocess

import awkward as ak
import numpy as np
import uproot

from export_profiles import PARAMETERS, event_indices, flat, read_case, sha256
from export_pulls import case_values
from pull_histograms import BOUND, bound_pulls, common_edges, histogram

SOURCES = ("export_smearing.py", "plot_smearing.py", "pool_errors.py", "smearing.py", "export_profiles.py",
           "export_pulls.py", "pull_histograms.py", "metrics.py")


def measurement_audit(directory, report, widths):
    path = directory / "measurements.root"
    if [f["sha256"] for f in report["provenance"]["files"] if f["name"] == path.name] != [sha256(path)]:
        raise ValueError("Smearing measurement ROOT hash differs")
    if not any(f["sha256"] == sha256(widths) for f in report["provenance"]["files"]):
        raise ValueError("Native run did not record the fixed pooled width table")
    table = json.loads(widths.read_text())
    columns = ["volume_id", *[p + str(i) for i in (0, 1) for p in ("rec_loc", "true_loc", "var_loc")]]
    with uproot.open(path) as stream:
        data = stream["measurements"].arrays(columns, library="np")
    if len(data["volume_id"]) != report["counts"]["measurements"]:
        raise ValueError("Measurement writer count differs from native audit")
    groups, aggregate, checked = [], {}, 0
    for group in table["groups"]:
        index, volume, sigma = group["index"], group["volume"], group["sigma_mm"]
        mask = data["volume_id"] == volume
        actual = data["var_loc" + str(index)][mask]
        if not len(actual) or not np.all(actual == np.asarray(sigma**2, dtype=actual.dtype)):
            raise ValueError("Native measured variance differs from fixed pooled sigma squared")
        residual = (data["rec_loc" + str(index)][mask].astype(float) -
                    data["true_loc" + str(index)][mask].astype(float)) / sigma
        if not np.all(np.isfinite(residual)):
            raise ValueError("Nonfinite measured standardized residual")
        edges = common_edges([residual], 5., .1, 16)
        result = histogram(residual, edges, 5.)
        groups.append(dict(volume=volume, index=index, sensor_family=group["sensor_family"], sigma_mm=sigma,
                           **{k: v for k, v in result.items() if k != "counts"}))
        aggregate.setdefault(group["sensor_family"] + "_loc" + str(index), []).append(residual)
        checked += len(residual)
    expected = {(g["volume"], g["index"]) for g in table["groups"]}
    actual = {(int(v), i) for v in np.unique(data["volume_id"]) for i in (0, 1)
              if np.any(np.isfinite(data["var_loc" + str(i)][data["volume_id"] == v]))}
    if actual != expected:
        raise ValueError("Measured volume/coordinate coverage differs from pooled width contract")
    return dict(measurements=len(data["volume_id"]), measured_coordinates=checked,
                sigma_squared_comparison="Exact ROOT branch dtype equality", groups=groups,
                input_sha256=sha256(path)), {key: np.concatenate(values) for key, values in aggregate.items()}


def smeared_case(directory, campaign, widths):
    metadata, eta, audit, old_values, flags, fitted_mask, finite_fit = read_case(directory, campaign, production=False)
    if metadata["events"] != campaign["events_per_case"]:
        raise ValueError("Smearing event count differs from configured production sample")
    report = json.loads((directory / "run-report.json").read_text())
    measured, shifts = measurement_audit(directory, report, widths)
    with uproot.open(directory / "particles.root") as stream:
        generated = stream["particles"].arrays(["event_id", "phi", "theta", "q_over_p", "vt"], library="ak")
    parameters = (*PARAMETERS, "eT")
    branches = ["event_nr", "track_nr", "hasFittedParams", *[p + "_fit" for p in parameters],
                *["cov_" + a + "_" + b for a in parameters for b in parameters]]
    with uproot.open(directory / "tracksummary_kf.root") as stream:
        tracks = stream["tracksummary"].arrays(branches, library="ak")
    events = ak.to_numpy(ak.flatten(ak.broadcast_arrays(tracks["event_nr"], tracks["track_nr"])[0]))
    indices = event_indices(ak.to_numpy(generated["event_id"]), events)
    truth = np.column_stack([np.zeros(len(eta)), np.zeros(len(eta)), flat(generated, "phi"),
                             flat(generated, "theta"), flat(generated, "q_over_p"), flat(generated, "vt")])
    fitted = np.column_stack([flat(tracks, p + "_fit") for p in parameters])
    cov = np.stack([flat(tracks, "cov_" + a + "_" + b) for a in parameters for b in parameters], axis=1).reshape(-1, 6, 6)
    pulls, valid = bound_pulls(fitted, truth[indices], cov)
    has = flat(tracks, "hasFittedParams").astype(bool)
    pulls[~has] = np.nan
    values = {name: pulls[:, i] for i, name in enumerate(BOUND)}
    aligned_valid = np.zeros(len(eta), dtype=bool)
    aligned_valid[indices] = valid["valid_covariance"] & valid["finite_parameters"] & has
    pt = -old_values["pt_relative"]["pull"].copy()
    pt[~aligned_valid] = np.nan
    values["pt_relative"] = pt[fitted_mask]
    if np.any(eta < campaign["eta_range"][0]) or np.any(eta > campaign["eta_range"][1]):
        raise ValueError("Generated eta outside configured range")
    metadata.update(mode="gaussian", fit_tracks=int(fitted_mask.sum()),
                    invalid_six_parameter_covariance=int((~valid["valid_covariance"]).sum()),
                    nonfinite_six_parameter_fit=int((~valid["finite_parameters"]).sum()),
                    wrong_charge=int(flags["wrong_charge"].sum()), measurement_error_audit=measured,
                    selection_losses=int((audit["selected"] == 0).sum()),
                    fit_failures=int((audit["fit_attempts"] - audit["fit_tracks"]).sum()))
    selected_report = {k: v for k, v in report.items() if k not in ("command", "provenance", "width_table", "gaussian_widths", "error_table")}
    selected_report["provenance"] = metadata["native_provenance"]
    # Report writers may add explicit input paths. Retain their hashes, never a
    # machine-local home path in the portable public copy.
    def portable(value):
        if isinstance(value, dict):
            return {k: portable(v) for k, v in value.items() if k != "path"}
        if isinstance(value, list):
            return [portable(v) for v in value]
        return Path(value).name if isinstance(value, str) and value.startswith("/Users/") else value
    metadata["native_report"] = portable(selected_report)
    return metadata, values, shifts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    root = source.parents[2]
    campaign_path = source / "smearing_campaign.json"
    campaign = json.loads(campaign_path.read_text())
    original = json.loads((source / "campaign.json").read_text())
    config_path = source / "pulls_config.json"
    config = json.loads(config_path.read_text())
    widths = root / campaign["digitization"]["width_table"]
    cases, measurement_values = [], []
    for pt in campaign["pt_GeV"]:
        metadata, values = case_values(args.reference / f"fatras-pt{pt:g}", original)
        metadata["mode"] = "geometric"
        cases.append((metadata, values))
        metadata, values, shifts = smeared_case(args.input / f"fatras-pt{pt:g}", campaign, widths)
        if metadata["generated_truth_sha256"] != cases[-1][0]["generated_truth_sha256"]:
            raise ValueError("Gaussian and geometric samples have different generated truth")
        cases.append((metadata, values))
        measurement_values.append((pt, shifts))
        print(pt, "GeV Gaussian counts", metadata["native_counts"], flush=True)
    edges = {name: common_edges([values[name] for _, values in cases], config["core_limit"],
                               config["core_bin_width"], config["tail_bins_per_decade"])
             for name in (*BOUND, "pt_relative")}
    samples = []
    for metadata, values in cases:
        metadata["quantities"] = {name: histogram(v, edges[name], config["core_limit"]) for name, v in values.items()}
        for result in metadata["quantities"].values():
            if result["underflow"] or result["overflow"] or result["entries"] + result["nonfinite"] != metadata["fit_tracks"]:
                raise ValueError("Full track-pull histogram count closure differs")
        samples.append(metadata)
    measurement_edges = {name: common_edges([shifts[name] for _, shifts in measurement_values], 5., .1, 16)
                         for name in measurement_values[0][1]}
    measured = [dict(pt_GeV=pt, quantities={name: histogram(values, measurement_edges[name], 5.) for name, values in shifts.items()})
                for pt, shifts in measurement_values]
    data = dict(schema_version=1, status="PROTOTYPE", configuration=config, campaign=campaign,
                reference_campaign=original, widths=json.loads(widths.read_text()),
                bin_edges={k: v.tolist() for k, v in edges.items()}, samples=samples,
                measurement_bin_edges={k: v.tolist() for k, v in measurement_edges.items()}, measurement_samples=measured,
                provenance=dict(source_revision=subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(),
                                source_sha256={name: sha256(source / name) for name in SOURCES},
                                campaign_sha256=sha256(campaign_path), configuration_sha256=sha256(config_path),
                                widths_sha256=sha256(widths), versions=dict(numpy=np.__version__, uproot=uproot.__version__, awkward=ak.__version__)))
    payload = json.dumps(data, indent=2, allow_nan=False) + "\n"
    if "/Users/" in payload:
        raise ValueError("Unexpected local path in portable retained evidence")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(gzip.compress(payload.encode(), mtime=0))


if __name__ == "__main__":
    main()
