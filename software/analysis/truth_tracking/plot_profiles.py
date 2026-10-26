#!/usr/bin/env python3
"""Replay retained truth-tracking performance profiles as scientific figures."""

import argparse
import csv
import gzip
import hashlib
import json
import os
from pathlib import Path

import numpy as np

from metrics import QUANTITIES


LABELS = {
    "d0": (r"$d_0$", r"[$\mu$m]", 1000.),
    "z0": (r"$z_0$", r"[$\mu$m]", 1000.),
    "phi": (r"$\phi$", "[mrad]", 1000.),
    "theta": (r"$\theta$", "[mrad]", 1000.),
    "q_over_p": (r"$q/p$", r"[$10^{-3}$ GeV$^{-1}$]", 1000.),
    "pt_relative": (r"$(p_T^{fit}-p_T^{truth})/p_T^{truth}$", "[%]", 100.),
}


def audit_training(config):
    root = Path(__file__).resolve().parents[3]
    table_path = root / config["error_training"]["error_table"]
    directory = table_path.parent
    training = json.loads((directory / "hit-error-training-audit.json").read_text())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    if training["configuration"] != config or training["training"] != config["error_training"]:
        raise ValueError("Training and performance campaign identities differ")
    for key, path in [
        ("table_sha256", table_path),
        ("raw_table_sha256", directory / "hit-error-parameterization-raw.json"),
        ("coordinator_source_sha256", Path(__file__).with_name("calibrate_errors.py")),
    ]:
        if training[key] != digest(path):
            raise ValueError("Retained training source/table identity differs: " + key)
    table = json.loads(table_path.read_text())
    expected = {(entry["volume"], row["index"], size): value
                for entry in table["entries"] for row in entry["value"]
                for size, value in enumerate(row["rms"], 1)}
    actual = {}
    for group in training["groups"]:
        key = group["volume"], group["index"], group["cluster_size"]
        if key in actual or group["entries"] <= 0:
            raise ValueError("Repeated or unsupported training group")
        actual[key] = group["population_sd_mm"]
        if group["tail"] != (group["cluster_size"] == group["corrected_vector_length"]):
            raise ValueError("Training overflow group differs from native lookup")
        if not np.isclose(group["uncentered_rms_mm"] ** 2,
                          group["population_sd_mm"] ** 2 + group["mean_mm"] ** 2,
                          rtol=1e-12, atol=1e-24):
            raise ValueError("Training bias/SD/RMS identity differs")
    if actual != expected:
        raise ValueError("Training group statistics differ from frozen table")
    print("Retained training source/table/group audit PASS (native ROOT audit is separate)")


def audit_native_reports(data):
    root = Path(__file__).resolve().parents[3]
    directory = (root / data["configuration"]["error_training"]["error_table"]).parent
    path = directory / "native-run-reports.json.gz"
    if hashlib.sha256(path.read_bytes()).hexdigest() != data["provenance"]["native_reports_sha256"]:
        raise ValueError("Retained native report inventory differs")
    inventory = json.loads(gzip.decompress(path.read_bytes()))
    reports = {item["case"]: item for item in inventory["reports"]}
    if len(reports) != len(inventory["reports"]):
        raise ValueError("Repeated retained native case")
    source_identities = []
    for sample in data["samples"]:
        case = f"{sample['simulation']}-pt{sample['pt_GeV']:g}"
        item = reports[case]
        report = item["report"]
        if (item["role"] != "performance" or report["outcome"] != "completed" or
                item["source_report_sha256"] != sample["run_report_sha256"] or
                report["counts"] != sample["native_counts"] or
                report["campaign"] != data["configuration"] or
                report["provenance"] != sample["native_provenance"] or
                report["original_proto_reference"]["enabled"]):
            raise ValueError("Native performance report differs from retained profile")
        identities = report["executed_source_sha256"]
        source_identities.append(identities)
        for name, expected in identities.items():
            if name.startswith("software/") and hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
                raise ValueError("Executed native source differs from repository: " + name)
    if not all(identity == source_identities[0] for identity in source_identities):
        raise ValueError("Performance samples executed different native source/binary bytes")
    training = json.loads((directory / "hit-error-training-audit.json").read_text())
    if reports["training-fatras"]["source_report_sha256"] != training["training_report_sha256"]:
        raise ValueError("Retained training report differs from training audit")
    print("Native report/source/common-binary identity audit PASS")


def audit(data, config_path):
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    source = Path(__file__).resolve().parent
    if data["schema_version"] != 1 or data["status"] != "PROTOTYPE":
        raise ValueError("Unexpected tracking-profile schema")
    if data["configuration"] != json.loads(config_path.read_text()):
        raise ValueError("Effective campaign differs from replay configuration")
    for key, path in [("configuration_sha256", config_path),
                      ("exporter_sha256", source / "export_profiles.py"),
                      ("metrics_sha256", source / "metrics.py")]:
        if data["provenance"][key] != digest(path):
            raise ValueError("Retained source/configuration hash differs: " + key)
    config = data["configuration"]
    if not data["pilot"]:
        audit_training(config)
        audit_native_reports(data)
    expected = {(s, p) for s in config["simulations"] for p in config["pt_GeV"]}
    actual = {(s["simulation"], s["pt_GeV"]) for s in data["samples"]}
    if not data["pilot"] and (expected != actual or len(actual) != len(data["samples"])):
        raise ValueError("Missing/repeated production simulation and momentum")
    for sample in data["samples"]:
        global_counts = sample["global"]["counts"]
        if (sample["events"] != global_counts["generated"] or
                global_counts["finite_fit"] > global_counts["fit_tracks"]):
            raise ValueError("Invalid global generated/fit counts")
        if not data["pilot"] and sample["events"] != config["events_per_case"]:
            raise ValueError("Production count differs from campaign")
        if not data["pilot"]:
            table = Path(__file__).resolve().parents[3] / config["error_training"]["error_table"]
            if (sample["hit_error_table_sha256"] != digest(table)
                    or sample["measurement_error_audit"]["measured_coordinates"] <= 0):
                raise ValueError("Missing frozen trained-error realization")
        for projection in ("eta_profiles", "abs_eta_profiles"):
            for key in global_counts:
                if sum(b["counts"][key] for b in sample[projection]) != global_counts[key]:
                    raise ValueError("Eta bins do not partition count: " + key)
            for item in sample[projection]:
                count = item["counts"]
                if not 0 <= count["finite_fit"] <= count["fit_tracks"] <= count["fit_attempts"] <= count["selected"] <= count["generated"]:
                    raise ValueError("Invalid per-bin fit attrition")
                for quantity in QUANTITIES:
                    for kind in ("residual", "pull"):
                        stats = item["quantities"][quantity][kind]
                        if stats["entries"] + stats["nonfinite"] != count["fit_tracks"]:
                            raise ValueError("Residual/pull counts differ from fitted-track denominator")
                        measured = stats["entries"] >= config["analysis"]["minimum_entries"]
                        if (stats["status"] == "measured") != measured:
                            raise ValueError("Undersampled-bin status differs")
                        for key, value in stats.items():
                            if key in ("entries", "nonfinite", "status"):
                                continue
                            if measured and (value is None or not np.isfinite(value)):
                                raise ValueError("Missing/nonfinite measured statistic")
                            if not measured and value is not None:
                                raise ValueError("Undersampled bin displays an estimate")
                            if measured and (key.endswith("_se") or key in ("std", "rms", "width68")) and value < 0:
                                raise ValueError("Negative width or uncertainty")
    print("Tracking profile source/configuration/count/statistics audit PASS")


def save_figure(fig, output, name):
    for extension in ("png", "pdf", "svgz"):
        path = output / (name + "." + extension)
        fig.savefig(path, dpi=175, bbox_inches="tight")
        if extension == "svgz":
            raw = gzip.decompress(path.read_bytes()).decode()
            path.write_bytes(gzip.compress(("\n".join(
                line.rstrip() for line in raw.splitlines()) + "\n").encode(), mtime=0))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("campaign.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.data.read_bytes()
    data = json.loads(gzip.decompress(raw) if args.data.suffix == ".gz" else raw)
    audit(data, args.config)
    args.output.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parents[3]
    cache = root / "build/truth-tracking-baseline/plot-cache"
    os.environ["MPLBACKEND"] = "Agg"
    os.environ.setdefault("MPLCONFIGDIR", str(cache / "matplotlib"))
    os.environ.setdefault("XDG_CACHE_HOME", str(cache / "xdg"))
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "svg.hashsalt": "nodd-truth-tracking"})
    config = data["configuration"]
    colors = {1.: "#3168a5", 10.: "#ca7436", 100.: "#3b8762"}
    simulation_style = {"geant4": ("-", "o"), "fatras": ("--", "s")}
    selected_eta_slices = [(0., .5), (1.5, 2.), (3., 3.5)]
    eta_colors = {pair: color for pair, color in zip(selected_eta_slices,
                                                   ("#3168a5", "#ca7436", "#3b8762"))}

    def frame(title, subtitle, panels=True):
        fig, axes = plt.subplots(2, 3, figsize=(15, 9), squeeze=False)
        fig.subplots_adjust(left=.075, right=.98, bottom=.095, top=.79,
                            wspace=.3, hspace=.42)
        fig.suptitle("nODD Gen3 — " + title, x=.075, y=.98, ha="left",
                     fontsize=18, weight="bold")
        fig.text(.075, .935,
                 f"PROTOTYPE · truth-associated Kalman fit · constant {config['field_Bz_T']:g} T · "
                 + ("pilot samples" if data["pilot"] else
                    f"{config['events_per_case']:,} single muons per backend / momentum"),
                 color="#52606b")
        fig.text(.075, .895, subtitle, color="#52606b", fontsize=9)
        fig.text(.075, .02,
                 "Ideal geometric digital response; PR100 map; independent Fatras hit errors. No residual cuts. "
                 "Errors: event-bootstrap SE (mean: SD/√N). Missing bins have <"
                 f"{config['analysis']['minimum_entries']} finite tracks.",
                 fontsize=8, color="#52606b")
        return fig, axes

    for axis_name in ("eta", "pt"):
        for kind, metric, title, filename in [
            ("residual", "width68", "central 68.27% resolution", "resolution"),
            ("pull", "mean", "pull means", "pull_mean"),
            ("pull", "std", "pull widths (full standard deviation)", "pull_width"),
        ] + ([("residual", "std", "residual standard deviation, including tails", "resolution_std")]
             if axis_name == "eta" else []):
            subtitle = ("All three fixed pT samples; signed truth η."
                        if axis_name == "eta" else
                        "Three fixed pT points; selected |η| slices. All eight slices retained in data/CSV.")
            fig, axes = frame(title + " versus " + ("η" if axis_name == "eta" else "pT"), subtitle)
            for ax, quantity in zip(axes.flat, QUANTITIES):
                label, unit, scale = LABELS[quantity]
                if kind == "pull":
                    scale, unit = 1., ""
                if axis_name == "eta":
                    series = []
                    for sample in data["samples"]:
                        series.append((sample["eta_profiles"], colors[sample["pt_GeV"]],
                                       sample["simulation"]))
                else:
                    series = []
                    for simulation in config["simulations"]:
                        ordered = sorted([s for s in data["samples"] if s["simulation"] == simulation],
                                         key=lambda s: s["pt_GeV"])
                        for pair in selected_eta_slices:
                            entries = []
                            for sample in ordered:
                                item = next(b for b in sample["abs_eta_profiles"]
                                            if (b["low"], b["high"]) == pair)
                                entries.append(dict(item, pt=sample["pt_GeV"]))
                            series.append((entries, eta_colors[pair], simulation))
                for entries, color, simulation in series:
                    x, y, error = [], [], []
                    for item in entries:
                        stats = item["quantities"][quantity][kind]
                        x.append((item["low"] + item["high"]) / 2 if axis_name == "eta" else item["pt"])
                        y.append(np.nan if stats[metric] is None else stats[metric] * scale)
                        error.append(np.nan if stats[metric + "_se"] is None else stats[metric + "_se"] * scale)
                    line, marker = simulation_style[simulation]
                    ax.errorbar(x, y, yerr=error, color=color, linestyle=line, marker=marker,
                                ms=3, lw=1.2, capsize=1.5, alpha=.9)
                if kind == "pull":
                    ax.axhline(0 if metric == "mean" else 1, color="#65717a", lw=1, alpha=.7)
                else:
                    ax.set_yscale("log")
                if axis_name == "pt":
                    ax.set_xscale("log")
                    ax.set_xticks(config["pt_GeV"], [f"{p:g}" for p in config["pt_GeV"]])
                else:
                    ax.set_xlim(*config["eta_range"])
                ax.set_title(label, fontsize=11)
                ax.set_xlabel("Truth η" if axis_name == "eta" else r"Truth $p_T$ [GeV]")
                ylabel = ("Central 68.27% half-width" if metric == "width68" else
                          "Standard deviation" if metric == "std" else "Mean")
                ax.set_ylabel(ylabel + (" " + unit if unit else ""))
                ax.grid(alpha=.22, which="both")
                ax.set_axisbelow(True)
            handles = [Line2D([], [], color="#34434e", ls=style[0], marker=style[1],
                             label="Geant4" if sim == "geant4" else "Fatras")
                       for sim, style in simulation_style.items()]
            if axis_name == "eta":
                handles += [Line2D([], [], color=color, lw=2, label=f"pT = {p:g} GeV")
                            for p, color in colors.items()]
            else:
                handles += [Line2D([], [], color=color, lw=2, label=f"{lo:g} ≤ |η| < {hi:g}")
                            for (lo, hi), color in eta_colors.items()]
            fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(.98, .865),
                       ncol=5, frameon=False, fontsize=9)
            save_figure(fig, args.output, filename + "_" + axis_name)
            plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), squeeze=False)
    fig.subplots_adjust(left=.06, right=.985, bottom=.2, top=.72, wspace=.22)
    fig.suptitle("nODD Gen3 — generated-event tracking attrition", x=.06, y=.98,
                 ha="left", weight="bold", fontsize=18)
    fig.text(.06, .91, f"PROTOTYPE · constant {config['field_Bz_T']:g} T · "
             "one muon per event · fractions use every generated primary", color="#52606b")
    for ax, pt in zip(axes.flat, config["pt_GeV"]):
        for sample in (s for s in data["samples"] if s["pt_GeV"] == pt):
            for key, color, label in [("selected_fraction", "#6b7c8c",
                                      f"≥{config['truth_tracking']['minimum_measurements']} measurements"),
                                     ("fit_fraction", colors[pt], "finite fitted parameters")]:
                entries = sample["eta_profiles"]
                x = [(b["low"] + b["high"]) / 2 for b in entries]
                fractions = [b[key] for b in entries]
                y = np.array([f["value"] if f["value"] is not None else np.nan for f in fractions])
                error = np.array([[v - f["low"] if f["low"] is not None else np.nan
                                   for v, f in zip(y, fractions)],
                                  [f["high"] - v if f["high"] is not None else np.nan
                                   for v, f in zip(y, fractions)]])
                line, marker = simulation_style[sample["simulation"]]
                ax.errorbar(x, y, yerr=error, color=color, linestyle=line, marker=marker,
                            ms=3, capsize=1.5, label=sample["simulation"] + " " + label)
        ax.set(title=f"pT = {pt:g} GeV", xlabel="Truth η", ylabel="Fraction of generated muons",
               xlim=config["eta_range"], ylim=(-.02, 1.03))
        ax.grid(alpha=.2)
    axes.flat[0].legend(fontsize=8, loc="lower center")
    fig.text(.06, .025, "Wilson z=1 intervals. Truth-associated fitting only; no CKF/pattern-recognition efficiency claim.", fontsize=9, color="#52606b")
    save_figure(fig, args.output, "fit_fraction_eta")
    plt.close(fig)

    with (args.output / "performance-summary.csv").open("w", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["simulation", "pt_GeV", "projection", "eta_low", "eta_high",
                         "generated", "selected", "fit_attempts", "fit_tracks", "invalid_covariance", "native_unmatched_fit",
                         "quantity", "residual_entries", "residual_mean", "residual_std", "residual_width68",
                         "pull_entries", "pull_mean", "pull_std", "pull_tail_abs_gt3_fraction"])
        for sample in data["samples"]:
            for projection in ("eta_profiles", "abs_eta_profiles"):
                for item in sample[projection]:
                    c = item["counts"]
                    for quantity, values in item["quantities"].items():
                        r, p = values["residual"], values["pull"]
                        writer.writerow([sample["simulation"], sample["pt_GeV"], projection, item["low"], item["high"],
                                         c["generated"], c["selected"], c["fit_attempts"], c["fit_tracks"], c["invalid_covariance"], c["native_unmatched_fit"],
                                         quantity, r["entries"], r["mean"], r["std"], r["width68"],
                                         p["entries"], p["mean"], p["std"], values["pull_tail_abs_gt3"]["value"]])
    print("Rendered eight tracking comparisons as PNG/PDF/SVGZ and retained all eta slices in CSV")


if __name__ == "__main__":
    main()
