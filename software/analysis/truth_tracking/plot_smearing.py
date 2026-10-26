#!/usr/bin/env python3
"""Replay the measured-width Gaussian Fatras sanity check and its reference."""
import argparse
import csv
import gzip
import json
import os
from pathlib import Path

import numpy as np

from export_profiles import sha256
from export_smearing import SOURCES, comparison_identity
from plot_profiles import save_figure
from plot_pulls import LABELS, audit as audit_original
from pull_histograms import BOUND


def audit(data):
    source = Path(__file__).resolve().parent
    root = source.parents[2]
    campaign = json.loads((source / "smearing_campaign.json").read_text())
    reference = json.loads((source / "campaign.json").read_text())
    if data["campaign"] != campaign or data["reference_campaign"] != reference:
        raise ValueError("Smearing/reference campaign identity differs")
    for key in set(reference) - {"simulations", "digitization", "error_training"}:
        if campaign[key] != reference[key]:
            raise ValueError("Comparison changes more than digitization: " + key)
    for name in SOURCES:
        if data["provenance"]["source_sha256"][name] != sha256(source / name):
            raise ValueError("Retained smearing analysis source differs: " + name)
    for name, key in [("smearing_campaign.json", "campaign_sha256"), ("pulls_config.json", "configuration_sha256")]:
        if data["provenance"][key] != sha256(source / name):
            raise ValueError("Retained configuration fingerprint differs")
    widths_path = root / campaign["digitization"]["width_table"]
    if data["provenance"]["widths_sha256"] != sha256(widths_path) or data["widths"] != json.loads(widths_path.read_text()):
        raise ValueError("Fixed pooled width table differs")
    if data["widths"]["provenance"]["source_sha256"] != sha256(source / "pool_errors.py"):
        raise ValueError("Pooled training reducer source differs")
    original = json.loads(gzip.decompress((root / "docs/validation/truth-tracking-baseline/pulls/distributions.json.gz").read_bytes()))
    audit_original(original)
    old = {s["pt_GeV"]: s for s in original["samples"] if s["simulation"] == "fatras"}
    if {(s["mode"], s["pt_GeV"]) for s in data["samples"]} != {(m, p) for m in ("geometric", "gaussian") for p in campaign["pt_GeV"]} or len(data["samples"]) != 6:
        raise ValueError("Comparison sample coverage differs")
    identities = []
    for sample in data["samples"]:
        if sample["simulation"] != "fatras" or sample["events"] != campaign["events_per_case"]:
            raise ValueError("Unexpected comparison simulation/denominator")
        if sample["generated_truth_sha256"] != old[sample["pt_GeV"]]["generated_truth_sha256"]:
            raise ValueError("Comparison gun/event identity differs")
        if sample["mode"] == "geometric":
            if sample["run_report_sha256"] != old[sample["pt_GeV"]]["run_report_sha256"]:
                raise ValueError("Geometric reference source changed")
        else:
            report = sample["native_report"]
            if report["campaign"] != campaign or report["outcome"] != "completed" or report["counts"] != sample["native_counts"]:
                raise ValueError("Portable native smearing report differs")
            identity = report["executed_source_sha256"]
            for name, value in identity.items():
                if name.startswith("software/") and sha256(root / name) != value:
                    raise ValueError("Executed smearing source differs: " + name)
            identities.append(identity)
            comparison_identity(sample["native_provenance"], old[sample["pt_GeV"]]["native_provenance"])
            groups = sample["measurement_error_audit"]["groups"]
            if {(g["volume"], g["index"]) for g in groups} != {(g["volume"], g["index"]) for g in data["widths"]["groups"]}:
                raise ValueError("Measurement width coverage differs")
            if sum(g["entries"] for g in groups) != sample["measurement_error_audit"]["measured_coordinates"]:
                raise ValueError("Measurement standardized-residual count differs")
        if set(sample["quantities"]) != {*BOUND, "pt_relative"}:
            raise ValueError("Missing track parameter")
        for name, result in sample["quantities"].items():
            check_histogram(result, data["bin_edges"][name], sample["fit_tracks"])
    if not all(i == identities[0] for i in identities):
        raise ValueError("Gaussian cases ran different native source/binary bytes")
    for sample in data["measurement_samples"]:
        total = 0
        for name, result in sample["quantities"].items():
            check_histogram(result, data["measurement_bin_edges"][name], result["entries"])
            total += result["entries"]
        match = next(s for s in data["samples"] if s["mode"] == "gaussian" and s["pt_GeV"] == sample["pt_GeV"])
        if total != match["measurement_error_audit"]["measured_coordinates"]:
            raise ValueError("Aggregate measured-coordinate counts differ")
    print("Gaussian/reference source, native identity, covariance-width, count and full-tail audits PASS")


def check_histogram(result, bins, expected):
    edges, counts = np.asarray(bins), np.asarray(result["counts"])
    if (len(edges) != len(counts) + 1 or not np.all(np.isfinite(edges)) or np.any(np.diff(edges) <= 0) or
            not np.issubdtype(counts.dtype, np.integer) or np.any(counts < 0) or
            result["underflow"] or result["overflow"] or counts.sum() != result["entries"] or
            result["entries"] + result["nonfinite"] != expected):
        raise ValueError("Histogram finite-tail/count closure failed")
    if result["entries"]:
        density = counts / result["entries"] / np.diff(edges)
        if not np.isclose(np.sum(density * np.diff(edges)), 1., rtol=0., atol=1e-12):
            raise ValueError("Full density is not normalized")
        if result["minimum"] < edges[0] or result["maximum"] > edges[-1]:
            raise ValueError("Observed tail escaped retained range")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(gzip.decompress(args.data.read_bytes()))
    audit(data)
    args.output.mkdir(parents=True, exist_ok=True)
    os.environ["MPLBACKEND"] = "Agg"
    os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[3] / "build/truth-tracking-baseline/plot-cache/matplotlib"))
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.hashsalt": "nodd-smearing"})
    colors = {1.: "#3168a5", 10.: "#ca7436", 100.: "#3b8762"}
    core = data["configuration"]["core_limit"]

    def frame(title, view, rows=2, cols=3, compare=False, measured=False):
        fig, axes = plt.subplots(rows, cols, figsize=(15, 9), squeeze=False)
        fig.subplots_adjust(left=.075, right=.98, bottom=.11, top=.79, hspace=.42, wspace=.31)
        fig.suptitle("nODD Gen3 — " + title, x=.075, y=.98, ha="left", fontsize=18, weight="bold")
        fig.text(.075, .936, "PROTOTYPE · Fatras · constant 3 T · all −4 ≤ η ≤ 4 · 20,000 generated muons per momentum", color="#52606b")
        fig.text(.075, .895, "Full finite range; symmetric-log pull axis and log density; every tail retained." if view == "full" else "Core ±5; density normalized to all finite entries, including those outside this view.", fontsize=9, color="#52606b")
        handles = [Line2D([], [], color=c, label=f"pT = {p:g} GeV") for p, c in colors.items()]
        if compare:
            handles += [Line2D([], [], color="#56636e", ls="-", label="Gaussian"), Line2D([], [], color="#56636e", ls="--", label="Geometric")]
        handles += [Line2D([], [], color="#56636e", ls=":", label="N(0,1) reference")]
        fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(.98, .858), ncol=len(handles), frameon=False, fontsize=8.5)
        footer = "All training cluster sizes pooled by volume/coordinate; no fitted-pull tuning. Native out-of-bounds Gaussian draws discarded without retry."
        if not measured:
            footer += " Time is unmeasured."
        fig.text(.075, .025, footer, fontsize=7.6, color="#52606b")
        return fig, axes

    def panel(ax, name, view, samples, bins, measured=False):
        edges = np.asarray(bins[name])
        tail_labels = []
        for sample in samples:
            result = sample["quantities"][name]
            n = result["entries"]
            density = np.asarray(result["counts"]) / n / np.diff(edges) if n else np.zeros(len(edges)-1)
            lo, hi = np.searchsorted(edges, [-core, core])
            y, x = (density[lo:hi], edges[lo:hi+1]) if view == "core" else (density, edges)
            mode = sample.get("mode", "gaussian")
            ax.stairs(y, x, color=colors[sample["pt_GeV"]], lw=1.45 if mode == "gaussian" else 1.05, ls="-" if mode == "gaussian" else "--", alpha=1. if mode == "gaussian" else .7)
            if mode == "gaussian" or all(s.get("mode") == "geometric" for s in samples):
                tail_labels.append(f"{sample['pt_GeV']:g}: {100*result['outside_core']/n:.2f}%" if n else f"{sample['pt_GeV']:g}: N=0")
        x = np.linspace(-5, 5, 501)
        ax.plot(x, np.exp(-x*x/2)/np.sqrt(2*np.pi), color="#56636e", ls=":", lw=1.1)
        if view == "full":
            ax.set_xscale("symlog", linthresh=core)
            ax.set_yscale("log")
            ax.set_xlim(edges[0], edges[-1])
            powers = np.arange(1, int(np.floor(np.log10(max(abs(edges[0]), abs(edges[-1])))))+1)
            ticks = np.r_[-10.**powers[::-1], 0., 10.**powers] if len(powers) else [-5., 0., 5.]
            ax.set_xticks(ticks)
        else:
            ax.set_xlim(-core, core)
            ax.set_ylim(bottom=0)
        ax.set_title(name.replace("_", " ") if measured else LABELS[name], fontsize=11)
        ax.set_xlabel(r"$(m^{reco}-m^{truth})/\sigma_m$" if measured else r"$(a^{truth}-a^{reco})/\sigma_a^{fit}$")
        ax.set_ylabel("Probability density per unit pull")
        ax.grid(alpha=.2, which="both")
        ax.set_axisbelow(True)
        ax.text(.02, .97, ("Gaussian outside ±5: " if {s.get("mode") for s in samples} == {"geometric", "gaussian"} else "Outside ±5: ") + " · ".join(tail_labels), transform=ax.transAxes, va="top", fontsize=7.2,
                bbox=dict(facecolor="white", edgecolor="none", alpha=.8))

    gaussian = [s for s in data["samples"] if s["mode"] == "gaussian"]
    for view in ("core", "full"):
        for compare in (False, True):
            fig, axes = frame("Gaussian / geometric track pulls" if compare else "Gaussian track pulls", view, compare=compare)
            for ax, name in zip(axes.flat, BOUND):
                panel(ax, name, view, data["samples"] if compare else gaussian, data["bin_edges"])
            save_figure(fig, args.output, ("comparison_" if compare else "pulls_gaussian_") + view)
            plt.close(fig)
        fig, axes = frame("derived pT comparison", view, rows=1, cols=2)
        for ax, mode in zip(axes.flat, ("geometric", "gaussian")):
            panel(ax, "pt_relative", view, [s for s in data["samples"] if s["mode"] == mode], data["bin_edges"])
            ax.set_title(mode.capitalize() + r" — $p_T$ (full θ–q/p covariance)")
        save_figure(fig, args.output, "pt_" + view)
        plt.close(fig)
    fig, axes = frame("measurement standardized residuals", "core", measured=True)
    for ax, name in zip(axes.flat, data["measurement_bin_edges"]):
        panel(ax, name, "core", data["measurement_samples"], data["measurement_bin_edges"], measured=True)
    axes.flat[-1].axis("off")
    save_figure(fig, args.output, "measurements_core")
    plt.close(fig)
    fields = ["mode", "pt_GeV", "quantity", "entries", "nonfinite", "underflow", "overflow", "mean", "std", "width68", "minimum", "maximum", "outside_core", "abs_gt3"]
    with (args.output / "summary.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for sample in data["samples"]:
            for quantity, result in sample["quantities"].items():
                writer.writerow(dict(mode=sample["mode"], pt_GeV=sample["pt_GeV"], quantity=quantity, **{k: result[k] for k in fields[3:]}))
    print("Retained seven PNG/PDF/SVGZ figure sets and 42-row comparison CSV")


if __name__ == "__main__":
    main()
