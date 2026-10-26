#!/usr/bin/env python3
"""Replay complete all-eta pull distributions, with three momenta overlaid."""

import argparse
import csv
import gzip
import hashlib
import json
import os
from pathlib import Path

import numpy as np

from export_pulls import SOURCES
from plot_profiles import audit as audit_profiles, save_figure
from pull_histograms import BOUND


LABELS = {"d0": r"$d_0$", "z0": r"$z_0$", "phi": r"$\phi$",
          "theta": r"$\theta$", "q_over_p": r"$q/p$",
          "time": r"$t_0$ (unmeasured; prior)", "pt_relative": r"$p_T$ (derived)"}


def audit(data):
    source = Path(__file__).resolve().parent
    root = source.parents[2]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    config = json.loads((source / "pulls_config.json").read_text())
    campaign_path = source / "campaign.json"
    if (data["schema_version"] != 1 or data["status"] != "PROTOTYPE" or
            data["configuration"] != config or config["sign"] != "truth_minus_reconstructed" or
            data["campaign"] != json.loads(campaign_path.read_text()) or
            data["provenance"]["configuration_sha256"] != digest(source / "pulls_config.json") or
            data["provenance"]["campaign_sha256"] != digest(campaign_path)):
        raise ValueError("Pull configuration/sign identity differs")
    for name in SOURCES:
        if data["provenance"]["source_sha256"][name] != digest(source / name):
            raise ValueError("Pull exporter/helper source differs: " + name)
    baseline = root / "docs/validation/truth-tracking-baseline/profiles.json.gz"
    profiles = json.loads(gzip.decompress(baseline.read_bytes()))
    audit_profiles(profiles, campaign_path)
    old = {(s["simulation"], s["pt_GeV"]): s for s in profiles["samples"]}
    keys = [(s["simulation"], s["pt_GeV"]) for s in data["samples"]]
    if set(keys) != set(old) or len(keys) != len(old):
        raise ValueError("Pull histogram case coverage differs")
    for sample in data["samples"]:
        reference = old[sample["simulation"], sample["pt_GeV"]]
        for key in ("run_report_sha256", "native_counts", "input_files", "native_provenance",
                    "native_unmatched_event_ids", "hit_error_table_sha256"):
            if sample[key] != reference[key]:
                raise ValueError("Pull cohort/native identity differs: " + key)
        if sample["fit_tracks"] != reference["global"]["counts"]["fit_tracks"]:
            raise ValueError("Pull fitted-track denominator differs")
        if set(sample["quantities"]) != {*BOUND, "pt_relative"}:
            raise ValueError("Missing fitted parameter distribution")
        for name, result in sample["quantities"].items():
            edges = np.asarray(data["bin_edges"][name])
            counts = np.asarray(result["counts"])
            if (len(edges) != len(counts) + 1 or np.any(np.diff(edges) <= 0) or
                    not np.all(np.isfinite(edges)) or np.any(counts < 0) or
                    not np.issubdtype(counts.dtype, np.integer) or
                    result["underflow"] != 0 or result["overflow"] != 0 or
                    int(counts.sum()) != result["entries"] or
                    result["entries"] + result["nonfinite"] != sample["fit_tracks"] or
                    not 0 <= result["outside_core"] <= result["entries"]):
                raise ValueError("Pull histogram count/edge closure differs")
            if result["entries"]:
                density = counts / result["entries"] / np.diff(edges) if result["entries"] else np.zeros_like(counts, dtype=float)
                if not np.isclose(np.sum(density * np.diff(edges)), 1., rtol=0., atol=1e-12):
                    raise ValueError("Variable-bin density is not normalized")
                if result["minimum"] < edges[0] or result["maximum"] > edges[-1]:
                    raise ValueError("A finite observed tail is outside the full axis")
    print("Full pull source/cohort/normalization/finite-tail/count audit PASS")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    data = json.loads(gzip.decompress(args.data.read_bytes()))
    audit(data)
    args.output.mkdir(parents=True, exist_ok=True)
    cache = Path(__file__).resolve().parents[3] / "build/truth-tracking-baseline/plot-cache"
    os.environ["MPLBACKEND"] = "Agg"
    os.environ.setdefault("MPLCONFIGDIR", str(cache / "matplotlib"))
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "svg.hashsalt": "nodd-full-pulls"})
    colors = {1.: "#3168a5", 10.: "#ca7436", 100.: "#3b8762"}
    core = data["configuration"]["core_limit"]

    def panel(ax, simulation, name, view):
        edges = np.asarray(data["bin_edges"][name])
        outside = []
        for sample in (s for s in data["samples"] if s["simulation"] == simulation):
            result = sample["quantities"][name]
            counts = np.asarray(result["counts"])
            density = counts / result["entries"] / np.diff(edges) if result["entries"] else np.zeros_like(counts, dtype=float)
            low, high = (np.searchsorted(edges, -core), np.searchsorted(edges, core))
            values, bins = (density[low:high], edges[low:high+1]) if view == "core" else (density, edges)
            ax.stairs(values, bins, color=colors[sample["pt_GeV"]], lw=1.5)
            outside.append(f"{sample['pt_GeV']:g}: {100 * result['outside_core'] / result['entries']:.2f}%" if result["entries"] else f"{sample['pt_GeV']:g}: N=0")
        normal_x = np.linspace(-core, core, 501)
        ax.plot(normal_x, np.exp(-normal_x**2 / 2) / np.sqrt(2*np.pi),
                color="#56636e", ls=":", lw=1.2)
        if view == "full":
            ax.set_xscale("symlog", linthresh=core)
            ax.set_yscale("log")
            ax.set_xlim(edges[0], edges[-1])
        else:
            ax.set_xlim(-core, core)
            ax.set_ylim(bottom=0)
        ax.set_title(LABELS[name], fontsize=11)
        ax.set_xlabel(r"$(a^{truth}-a^{reco})/\sigma_a^{fit}$")
        ax.set_ylabel("Probability density per unit pull")
        ax.grid(alpha=.2, which="both")
        ax.set_axisbelow(True)
        ax.text(.02, .97, f"Outside ±{core:g}: " + " · ".join(outside),
                transform=ax.transAxes, va="top", fontsize=7.5,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": .8})

    def frame(title, view, rows=2, columns=3):
        fig, axes = plt.subplots(rows, columns, figsize=(15, 9 if rows == 2 else 5.5), squeeze=False)
        fig.subplots_adjust(left=.07, right=.98, bottom=.105, top=.79, hspace=.4, wspace=.3)
        fig.suptitle("nODD Gen3 — " + title, x=.07, y=.98, ha="left", fontsize=18, weight="bold")
        fig.text(.07, .935, "PROTOTYPE · constant 3 T · all −4 ≤ η ≤ 4 · truth − reconstructed · 20,000 generated muons per momentum",
                 color="#52606b", fontsize=10)
        fig.text(.07, .89, "Full finite range: symmetric-log pull axis / log density; all tails retained."
                 if view == "full" else f"Core view ±{core:g}; density remains normalized to every finite pull, including tails outside this view.",
                 color="#52606b", fontsize=9)
        handles = [Line2D([], [], color=color, label=f"pT = {pt:g} GeV", lw=1.7)
                   for pt, color in colors.items()]
        handles.append(Line2D([], [], color="#56636e", ls=":", label="N(0,1) reference"))
        fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(.98, .855), ncol=4, frameon=False, fontsize=9)
        fig.text(.07, .025, "No quality or tail cuts; wrapped φ; fitted covariance. Native Fake partial fits retained by verified seed identity. Time has no measurement constraint.",
                 fontsize=8, color="#52606b")
        return fig, axes

    for view in ("full", "core"):
        for simulation in data["campaign"]["simulations"]:
            fig, axes = frame(f"{simulation.capitalize()} parameter pulls ({view})", view)
            for ax, name in zip(axes.flat, BOUND):
                panel(ax, simulation, name, view)
            save_figure(fig, args.output, f"pulls_{simulation}_{view}")
            plt.close(fig)
        fig, axes = frame(f"derived pT pulls ({view})", view, rows=1, columns=2)
        for ax, simulation in zip(axes.flat, data["campaign"]["simulations"]):
            panel(ax, simulation, "pt_relative", view)
            ax.set_title(simulation.capitalize() + r" — $p_T$ (full θ–q/p covariance)")
        save_figure(fig, args.output, f"pulls_pt_{view}")
        plt.close(fig)

    with (args.output / "pull-summary.csv").open("w", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        fields = ["entries", "nonfinite", "underflow", "overflow", "outside_core", "abs_gt3",
                  "mean", "std", "width68", "minimum", "maximum"]
        writer.writerow(["simulation", "pt_GeV", "parameter", *fields])
        for sample in data["samples"]:
            for name, result in sample["quantities"].items():
                writer.writerow([sample["simulation"], sample["pt_GeV"], name,
                                 *[result[key] for key in fields]])
    print("Rendered full/core distributions for all six bound parameters and derived pT; 42 histogram summaries retained")


if __name__ == "__main__":
    main()
