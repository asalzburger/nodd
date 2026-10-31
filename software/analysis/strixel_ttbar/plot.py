#!/usr/bin/env python3
"""Unrooted scientific plots of the DES042 ttbar+200PU portable report."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import tempfile

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "nodd-strixel-ttbar-mpl"))
os.environ.setdefault("XDG_CACHE_HOME", str(Path(tempfile.gettempdir()) / "nodd-strixel-ttbar-cache"))
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import unrooted
from unrooted import ScatterData
from unrooted.plot.mpl.scatter import plot as scatter_plot
from unrooted.plot.style import HistogramStyle

PITCHES = (.5, 1., 1.5, 2.)
COLORS = { .5: "#536474", 1.: "#007e87", 1.5: "#bd7716", 2.: "#9253a2" }


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def value(v):
    return np.nan if v is None else float(v)


def points(ax, x, y, pitch, intervals=None, linestyle="-"):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    valid = np.isfinite(x) & np.isfinite(y)
    if valid.any():
        scatter_plot(ScatterData(x[valid], y[valid]), ax=ax,
                     style=HistogramStyle.as_scatter(marker="o", marker_color=COLORS[pitch], marker_size=3.5),
                     set_axis_labels=False)
    ax.plot(x, y, color=COLORS[pitch], lw=1.2, ls=linestyle)
    if intervals is not None:
        bounds = np.asarray([[np.nan, np.nan] if b is None else b for b in intervals], dtype=float)
        defined = valid & np.isfinite(bounds).all(axis=1)
        centre = bounds[defined].mean(axis=1)
        half = (bounds[defined, 1] - bounds[defined, 0]) / 2
        # Percentile intervals may exclude the observed point. Keep true endpoints.
        ax.errorbar(x[defined], centre, yerr=half, fmt="none", color=COLORS[pitch], lw=.8, capsize=2)


def frame(report, title, selection):
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.8))
    fig.subplots_adjust(left=.09, right=.97, bottom=.22, top=.78, hspace=.42, wspace=.32)
    fig.suptitle(title, x=.09, y=.975, ha="left", weight="bold", fontsize=18)
    window = report.get("benchmark", {}).get("gbts_z0_range_mm")
    window_label = "" if window is None else f" · GBTS z0 [{window[0]:g}, {window[1]:g}] mm"
    fig.text(.09, .925, f"Fatras qqbar-only ttbar + 200 pileup · {report['events_per_pitch']} paired events/length · {selection} selection{window_label}", fontsize=10, color="#536474")
    handles = [Line2D([], [], color=COLORS[p], marker="o", lw=1.2, label=f"{p:g} mm local-v pitch") for p in PITCHES]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(.08, .89), ncol=4, frameon=False, fontsize=9)
    fig.text(.09, .125, "Pointwise 95% paired event-block bootstrap. Constant intervals can be degenerate; they do not establish equivalence.", fontsize=8, color="#536474")
    fig.text(.09, .095, "Scaled local-v Gaussian response, fixed material. Boundary retries may change non-target noise and seeds; see pairing audit.", fontsize=8, color="#536474")
    fig.text(.09, .055, "PROTOTYPE · balanced tracker · constant 3 T · measured-pixel GBTS + full-sensor CKF + frozen ambiguity resolution", fontsize=9, color="#536474")
    graphs = report.get("benchmark", {}).get("gbts_graph_audit", {})
    if graphs:
        details = "; ".join(f"{pitch:g} mm: {graphs[f'{pitch:g}']['cap_reached_events']}/{graphs[f'{pitch:g}']['events']} events" for pitch in PITCHES)
        limits = sorted({graph["edge_cap"] for graph in graphs.values()})
        fig.text(.09, .025, f"GBTS graph edge limit {', '.join(f'{limit:,}' for limit in limits)} reached - {details}. Resource-limited chain.", fontsize=8, color="#536474")
    return fig, axes


def finish_axis(ax, xlabel, ylabel):
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.set_ylim(bottom=0)
    if "efficiency" in ylabel.lower():
        ax.set_ylim(0, 100)
    elif ax.get_ylim()[1] < 1:
        ax.set_ylim(top=1)
    ax.grid(axis="y", color="#dde4e8", lw=.7)
    ax.spines[["top", "right"]].set_visible(False)


def metrics(report, pitch):
    return report["cases"][f"{pitch:g}"]["metrics"]


def profile(report, pitch, selection, family, axis, category="inclusive"):
    edges = np.asarray(report["pt_edges_GeV"] if axis == "pt" else report["eta_edges"], dtype=float)
    x = np.sqrt(edges[:-1]*edges[1:]) if axis == "pt" else (edges[:-1]+edges[1:])/2
    if family == "eff":
        keys = [f"{selection}/ambi/effprofile/{category}/{axis}/{i}" for i in range(len(x))]
    else:
        keys = [f"{selection}/ambi/candidateprofile/{axis}/{i}/{category}" for i in range(len(x))]
    rows = [metrics(report, pitch)[k] for k in keys]
    return x, [100*value(r["value"]) for r in rows], [None if r["event_bootstrap95"] is None else [100*v for v in r["event_bootstrap95"]] for r in rows], [r["denominator"] for r in rows]


def overview(report, selection):
    fig, axes = frame(report, "Reconstruction efficiency and candidate composition", selection)
    specs = [("eff/hardscatter/fiducial", "Hard-scatter efficiency", "Efficiency [%]"),
             ("eff/pileup/fiducial", "Pileup efficiency", "Efficiency [%]"),
             ("fraction/fake", "Unmatched fake candidates", "Accepted-candidate fraction [%]"),
             ("fraction/duplicates", "Additional matched candidates", "Accepted-candidate fraction [%]")]
    for ax, (suffix, title, ylabel) in zip(axes.flat, specs):
        for pitch in PITCHES:
            row = metrics(report, pitch)[f"{selection}/ambi/{suffix}"]
            interval = row["event_bootstrap95"]
            points(ax, [pitch], [100*value(row["value"])], pitch,
                   [None if interval is None else [100*v for v in interval]])
        ax.set_title(title, loc="left", fontsize=11, weight="bold")
        finish_axis(ax, "Strixel local-v pitch [mm]", ylabel)
        ax.set_xticks(PITCHES)
    fig.text(.09, .16, "After ambiguity resolution. Generated fiducial charged particles form efficiency denominators; all accepted tracks form candidate denominators.", fontsize=8, color="#536474")
    return fig


def efficiency_profiles(report, selection):
    fig, axes = frame(report, "Efficiency versus truth kinematics", selection)
    specs = [("eta", "hardscatter", "Hard scatter"), ("pt", "hardscatter", "Hard scatter"),
             ("eta", "pileup", "Pileup"), ("pt", "pileup", "Pileup")]
    for ax, (axis, scope, title) in zip(axes.flat, specs):
        for pitch in PITCHES:
            x, y, intervals, denominators = profile(report, pitch, selection, "eff", axis, scope)
            points(ax, x, y, pitch, intervals)
        finish_axis(ax, "Truth pT [GeV]" if axis == "pt" else "Truth eta", "Unique-particle efficiency [%]")
        if axis == "pt":
            ax.set_xscale("log")
            ax.set_xlim(report["pt_edges_GeV"][0], report["pt_edges_GeV"][-1])
        else:
            ax.set_xlim(report["eta_edges"][0], report["eta_edges"][-1])
        ax.set_title(title, loc="left", fontsize=11, weight="bold")
    fig.text(.09, .16, "Fiducial charged generated particles before hit cuts; gaps have zero denominator. All bin counts, profile overflow and exact intervals are retained.", fontsize=8, color="#536474")
    return fig


def candidate_profiles(report, selection):
    fig, axes = frame(report, "Fake and duplicate fractions versus reconstructed kinematics", selection)
    specs = [("eta", "fake", "Unmatched fakes"), ("pt", "fake", "Unmatched fakes"),
             ("eta", "duplicates", "Additional matched candidates"), ("pt", "duplicates", "Additional matched candidates")]
    for ax, (axis, category, title) in zip(axes.flat, specs):
        for pitch in PITCHES:
            x, y, intervals, denominators = profile(report, pitch, selection, "candidate", axis, category)
            points(ax, x, y, pitch, intervals)
        finish_axis(ax, "Reconstructed pT [GeV]" if axis == "pt" else "Reconstructed eta", "Accepted-candidate fraction [%]")
        if axis == "pt":
            ax.set_xscale("log")
            ax.set_xlim(report["pt_edges_GeV"][0], report["pt_edges_GeV"][-1])
        else:
            ax.set_xlim(report["eta_edges"][0], report["eta_edges"][-1])
        ax.set_title(title, loc="left", fontsize=11, weight="bold")
    fig.text(.09, .16, "After ambiguity resolution; denominators contain all accepted tracks in each reconstructed bin. Out-of-range and undefined kinematics stay in global rates.", fontsize=8, color="#536474")
    return fig


def render(report, data_path, output):
    output = Path(output)
    if report["provenance"]["analyzer_sha256"] != sha256(Path(__file__).with_name("analyze.py")):
        raise ValueError("Analyzer source changed; replay statistics before plotting")
    output.mkdir(parents=True, exist_ok=True)
    existing = output / "manifest.json"
    if existing.exists() and json.loads(existing.read_text())["profiles_sha256"] != sha256(data_path):
        raise ValueError("Refusing to overwrite plots from different evidence")
    files = {}
    for selection in ("frozen", "guide"):
        for suffix, maker in (("overview", overview), ("efficiency-profiles", efficiency_profiles), ("candidate-profiles", candidate_profiles)):
            fig = maker(report, selection)
            try:
                for extension in ("png", "pdf"):
                    path = output / f"{selection}-{suffix}.{extension}"
                    metadata = {"CreationDate": None, "ModDate": None} if extension == "pdf" else None
                    fig.savefig(path, dpi=170, bbox_inches="tight", metadata=metadata)
                    files[path.name] = sha256(path)
            finally:
                plt.close(fig)
    manifest = {"schema_version": 1, "status": "PROTOTYPE", "profiles_sha256": sha256(data_path),
                "plot_sha256": sha256(__file__), "versions": {"matplotlib": matplotlib.__version__, "numpy": np.__version__, "unrooted": unrooted.__version__},
                "files_sha256": files, "figures": 6,
                "intervals": "Actual pointwise percentile endpoints, including intervals excluding the observed point; degenerate distributions flagged in retained report",
                "zero_fake_event_bound": "Reported separately in results.md; never used as a candidate-fraction limit"}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = json.loads(gzip.decompress(args.data.read_bytes()))
    manifest = render(report, args.data, args.output)
    print(json.dumps({"outcome": "completed", "figures": manifest["figures"], "files": len(manifest["files_sha256"])}))


if __name__ == "__main__":
    main()
