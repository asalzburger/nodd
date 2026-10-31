#!/usr/bin/env python3
"""Unrooted + Matplotlib scientific figures for the portable DES042 GBTS report."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import tempfile

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "nodd-strixel-gbts-mpl"))
os.environ.setdefault("XDG_CACHE_HOME", str(Path(tempfile.gettempdir()) / "nodd-strixel-gbts-cache"))
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import unrooted
from unrooted import ScatterData
from unrooted.plot.mpl.scatter import plot as scatter_plot
from unrooted.plot.style import HistogramStyle

COLORS = {.5: "#536474", 1.: "#007e87", 1.5: "#bd7716", 2.: "#9253a2"}
LABELS = {"d0": (r"$d_0$", "µm", 1000.), "z0": (r"$z_0$", "µm", 1000.),
          "phi": (r"$\phi$", "mrad", 1000.), "theta": (r"$\theta$", "mrad", 1000.),
          "q_over_p": (r"$q/p$", r"$10^{-3}$ GeV$^{-1}$", 1000.),
          "relative_pt": (r"$(p_{T,true}-p_{T,reco})/p_{T,true}$", "%", 100.)}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def number(value):
    return np.nan if value is None else float(value)


def frame(title, subtitle, rows=2, columns=2):
    fig, axes = plt.subplots(rows, columns, figsize=(12.5, 8.8), squeeze=False)
    fig.subplots_adjust(left=.08, right=.97, bottom=.19, top=.78, hspace=.4, wspace=.32)
    fig.suptitle(title, x=.08, y=.975, ha="left", fontsize=18, weight="bold")
    fig.text(.08, .925, subtitle, fontsize=10, color="#536474")
    fig.text(.08, .025, "PROTOTYPE · PR104 balanced tracker · 3 T · pixel GBTS + full-sensor CKF + ambiguity resolution", fontsize=9, color="#536474")
    return fig, axes


def legend(fig):
    handles = [Line2D([], [], color=color, marker="o", lw=1.4, label=f"{pitch:g} mm local-v pitch")
               for pitch, color in COLORS.items()]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(.072, .885), ncol=4, frameon=False, fontsize=9)


def points(ax, x, y, pitch, intervals=None, *, solid=True):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    valid = np.isfinite(x) & np.isfinite(y)
    color = COLORS[pitch]
    if np.any(valid):
        scatter_plot(ScatterData(x[valid], y[valid]), ax=ax,
                     style=HistogramStyle.as_scatter(marker="o", marker_color=color, marker_size=3.3),
                     set_axis_labels=False)
    ax.plot(x, y, color=color, lw=1.2, ls="-" if solid else "--", alpha=.85)
    if intervals is not None:
        bounds = np.asarray([[np.nan, np.nan] if value is None else value for value in intervals], dtype=float)
        errors = np.stack((np.maximum(0, y - bounds[:, 0]), np.maximum(0, bounds[:, 1] - y)))
        ax.errorbar(x, y, yerr=errors, fmt="none", color=color, lw=.7, capsize=1.7)


def save(fig, output, name, manifest):
    for extension in ("png", "pdf"):
        path = output / f"{name}.{extension}"
        metadata = {"CreationDate": None, "ModDate": None} if extension == "pdf" else None
        fig.savefig(path, dpi=170, bbox_inches="tight", metadata=metadata)
        manifest[path.name] = digest(path)
    plt.close(fig)


def positive_width_axis(ax):
    values = [np.asarray(line.get_ydata(), dtype=float) for line in ax.lines]
    if any(np.any(np.isfinite(value) & (value > 0)) for value in values):
        ax.set_yscale("log")
    else:
        ax.set_ylim(0, 1)
        ax.text(.5, .5, "No defined positive widths\n(require ≥30 finite entries)", transform=ax.transAxes,
                ha="center", va="center", fontsize=9, color="#536474")


def efficiency(groups, title, output, name, manifest):
    fig, axes = frame(title + " — primary efficiency", "Every generated event remains in the denominator · 68% Wilson intervals · frozen response and reconstruction")
    for ax, group in zip(axes.flat, groups):
        for case in group["cases"]:
            bins = case["abs_eta_bins"]
            rates = [b["stages"]["ambi"]["efficiency"] for b in bins]
            points(ax, [(b["low"] + b["high"]) / 2 for b in bins],
                   [number(r["value"]) for r in rates], case["pitch_mm"], [r["wilson68"] for r in rates])
        ax.set(title=f"pT = {group['pt_GeV']:g} GeV", xlabel=r"Truth $|\eta|$", ylabel="Matched primary / generated", xlim=(0, 4), ylim=(0, 1.04))
        ax.grid(alpha=.18)
    for ax in list(axes.flat)[len(groups):]:
        ax.set_visible(False)
    legend(fig)
    fig.text(.08, .085, "Single-particle samples. Fake, secondary, duplicate and charge failures remain separate in the report; this is no occupancy benchmark.", fontsize=8, color="#536474")
    save(fig, output, name + "-efficiency", manifest)


def resolutions(groups, title, output, name, manifest, ratio=False):
    fig, axes = frame(title + (" — resolution ratios" if ratio else " — uncut residual widths"),
                      "All truth η · finite matched-primary representatives · paired 68.27% bootstrap intervals · ≥30 entries", rows=2, columns=3)
    for ax, (quantity, (label, unit, scale)) in zip(axes.flat, LABELS.items()):
        for pitch in COLORS:
            if ratio and pitch == .5:
                continue
            stats = [next(c for c in g["cases"] if c["pitch_mm"] == pitch)["global"]["stages"]["ambi"]["quantities"][quantity] for g in groups]
            x = [g["pt_GeV"] for g in groups]
            key = "ratio_to_baseline" if ratio else "width68"
            interval_key = "ratio_interval68" if ratio else "width_interval68"
            factor = 1. if ratio else scale
            ys = [number(s["residual"][key]) * factor for s in stats]
            bounds = [[v * factor for v in s["residual"][interval_key]] if s["residual"][interval_key] else None for s in stats]
            points(ax, x, ys, pitch, bounds)
            if ratio:
                common = [number(s["common_success_residual"][key]) for s in stats]
                ax.plot(x, common, color=COLORS[pitch], ls="--", lw=1., alpha=.8)
        ax.set(title=label, xlabel="Truth pT [GeV]", ylabel="Width / 0.5 mm width" if ratio else f"Central 68.27% half-width [{unit}]", xscale="log")
        ax.set_xticks([1, 5, 10, 100], ["1", "5", "10", "100"])
        ax.grid(alpha=.18)
        if ratio:
            ax.axhline(1., color=COLORS[.5], ls=":", lw=1.)
        else:
            positive_width_axis(ax)
    legend(fig)
    detail = "Solid: each pitch's finite successes. Dashed: common successful events at all four pitches." if ratio else "Widths retain wrong-charge tracks and all finite tails; displayed values are conditional on successful primary matching."
    fig.text(.08, .085, detail, fontsize=8, color="#536474")
    fig.text(.08, .06, "Statistical intervals only. Scaled frozen Gaussian longitudinal response is not physical sensor calibration; boundary retries may alter pixel draws.", fontsize=8, color="#536474")
    save(fig, output, name + ("-ratios" if ratio else "-widths"), manifest)


def longitudinal_eta(groups, title, output, name, manifest):
    selected = [group for group in groups if group["pt_GeV"] in (10., 100.)]
    if not selected:
        return
    fig, axes = frame(title + " — longitudinal response versus η",
                      "Uncut matched-primary residuals · central 68.27% half-width · paired bootstrap 68.27% intervals · ≥30 entries")
    for row, group in enumerate(selected):
        for column, quantity in enumerate(("z0", "theta")):
            ax = axes[row, column]
            label, unit, scale = LABELS[quantity]
            for case in group["cases"]:
                bins = case["abs_eta_bins"]
                stats = [b["stages"]["ambi"]["quantities"][quantity]["residual"] for b in bins]
                points(ax, [(b["low"] + b["high"]) / 2 for b in bins],
                       [number(s["width68"]) * scale for s in stats], case["pitch_mm"],
                       [[value * scale for value in s["width_interval68"]] if s["width_interval68"] else None for s in stats])
            ax.set(title=f"{label} · pT = {group['pt_GeV']:g} GeV", xlabel=r"Truth $|\eta|$",
                   ylabel=f"Central 68.27% half-width [{unit}]", xlim=(0, 4))
            positive_width_axis(ax)
            ax.grid(alpha=.18)
    for row in range(len(selected), 2):
        for ax in axes[row]:
            ax.set_visible(False)
    legend(fig)
    fig.text(.08, .085, "Gaps indicate fewer than 30 finite matched entries. No residual, pull or charge selection; all raw tails remain retained.", fontsize=8, color="#536474")
    fig.text(.08, .06, "Statistical longitudinal-response sensitivity. Gaussian edge retries may also change pixel noise or seed outputs; see pairing diagnostics.", fontsize=8, color="#536474")
    save(fig, output, name + "-longitudinal-eta", manifest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True, help="Retained profiles.json.gz")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(gzip.decompress(args.data.read_bytes()))
    if data["provenance"]["analyzer_sha256"] != digest(Path(__file__).with_name("analyze.py")):
        raise ValueError("Analyzer source changed; replay analysis before plotting")
    args.output.mkdir(parents=True, exist_ok=True)
    existing_manifest = args.output / "manifest.json"
    if existing_manifest.exists() and json.loads(existing_manifest.read_text())["profiles_sha256"] != digest(args.data):
        raise ValueError("Refusing to overwrite plots from a different evidence report")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    manifest = {}
    for simulation, particle in sorted({(g["simulation"], g["particle"]) for g in data["groups"]}):
        groups = sorted([g for g in data["groups"] if (g["simulation"], g["particle"]) == (simulation, particle)], key=lambda g: g["pt_GeV"])
        title = f"{'Geant4' if simulation == 'geant4' else 'Fatras'} single {particle}s"
        name = simulation + "-" + particle
        efficiency(groups, title, args.output, name, manifest)
        resolutions(groups, title, args.output, name, manifest)
        resolutions(groups, title, args.output, name, manifest, ratio=True)
        longitudinal_eta(groups, title, args.output, name, manifest)
    metadata = {"schema_version": 1, "status": "PROTOTYPE", "profiles_sha256": digest(args.data),
                "plot_source_sha256": digest(__file__), "unrooted_version": unrooted.__version__,
                "matplotlib_version": matplotlib.__version__, "numpy_version": np.__version__,
                "renderer": "unrooted.ScatterData / Matplotlib scatter renderer, lines and statistical intervals",
                "figures_sha256": manifest}
    existing_manifest.write_text(json.dumps(metadata, indent=2, allow_nan=False) + "\n")
    print("Rendered", len(manifest), "PNG/PDF files")


if __name__ == "__main__":
    main()
