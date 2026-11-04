#!/usr/bin/env python3
"""Make unrooted profiles and figures from complete native ACTS crossing tables."""
from __future__ import annotations

import argparse
import csv
from dataclasses import replace
import gzip
import hashlib
from importlib.metadata import distribution, version
import json
import os
from pathlib import Path

COMPONENTS = {
    "full_tracker": ("Full tracker", tuple(range(1, 8))),
    "pixel": ("Pixel detector", (1, 2, 3)),
    "short_strip": ("Short-strip detector", (4, 5)),
    "long_strip": ("Long-strip detector", (6, 7)),
    "system1": ("Pixel barrel", (1,)),
    "system2": ("Pixel endcap, −z", (2,)),
    "system3": ("Pixel endcap, +z", (3,)),
    "system4": ("Short-strip barrel", (4,)),
    "system5": ("Short-strip endcaps", (5,)),
    "system6": ("Long-strip barrel", (6,)),
    "system7": ("Long-strip endcaps", (7,)),
}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_counts(path, expected, eta_range):
    import numpy as np
    with Path(path).open(newline="") as stream:
        records = list(csv.DictReader(stream))
    if len(records) != expected or not records:
        raise ValueError(f"{path}: expected {expected} complete generated tracks")
    columns = {name: np.array([float(row[name]) for row in records])
               for name in records[0]}
    for name, values in columns.items():
        if not np.all(np.isfinite(values)):
            raise ValueError(f"{path}: nonfinite {name}")
    events = columns["event_nr"]
    if not np.array_equal(np.sort(events), np.arange(expected)) or np.any(columns["track_nr"] != 0):
        raise ValueError("expected each generated event exactly once, with track_nr zero")
    order = np.argsort(events)
    columns = {name: values[order] for name, values in columns.items()}
    if np.any(np.abs(columns["charge"]) != 1) or np.any(columns["pt_GeV"] <= 0):
        raise ValueError("invalid generated charge or transverse momentum")
    if np.any(np.abs(columns["phi"]) > np.pi + 1e-6):
        raise ValueError("invalid generated azimuth")
    eta = columns["eta"]
    if np.any(eta < eta_range[0]) or np.any(eta > eta_range[1]):
        raise ValueError("generated eta outside the study range")
    total = sum(columns[f"nSensitives_system{i}"] for i in range(1, 8))
    if not np.array_equal(total, columns["nSensitives"]):
        raise ValueError("per-system crossing counts do not close to nSensitives")
    for key, (_, systems) in COMPONENTS.items():
        values = sum(columns[f"nSensitives_system{i}"] for i in systems)
        if np.any(values < 0) or not np.array_equal(values, values.astype(int)):
            raise ValueError("crossing counts must be nonnegative integers")
        columns[key] = values
    return columns


def root_profile(eta, values, edges, title):
    """Persist the unweighted sufficient statistics as a standard TProfile."""
    import numpy as np
    from uproot.writing.identify import to_TAxis, to_TProfile
    n, _ = np.histogram(eta, bins=edges)
    total, _ = np.histogram(eta, bins=edges, weights=values)
    squared, _ = np.histogram(eta, bins=edges, weights=values * values)
    flow = lambda x: np.pad(np.asarray(x, dtype=float), (1, 1))
    axis = to_TAxis(fName="xaxis", fTitle="Generated pseudorapidity eta",
                   fNbins=len(edges) - 1, fXmin=edges[0], fXmax=edges[-1])
    return to_TProfile(
        fName=None, fTitle=title, data=flow(total), fEntries=len(eta),
        fTsumw=len(eta), fTsumw2=len(eta), fTsumwx=float(eta.sum()),
        fTsumwx2=float((eta * eta).sum()), fTsumwy=float(values.sum()),
        fTsumwy2=float((values * values).sum()), fSumw2=flow(squared),
        fBinEntries=flow(n), fBinSumw2=flow(n), fXaxis=axis,
    )


def validate_cases(directory, config):
    identity = None
    for pt in config["pt_GeV"]:
        case = directory / f"pt_{pt:g}GeV"
        run = json.loads((case / "run.json").read_text())
        if run["status"] != "PASS" or sha256(case / "counts.csv") != run["artifact_sha256"]["counts.csv"]:
            raise ValueError("plot input has failed accounting or changed counts")
        for name, expected in (("tracks", config["tracks_per_pt"]), ("pt_GeV", pt),
                               ("seed", config["seed"]), ("eta_range", config["eta_range"]),
                               ("maximum_step_mm", config["maximum_step_mm"]),
                               ("energy_loss", False), ("multiple_scattering", False)):
            if run["configuration"][name] != expected:
                raise ValueError(f"plot configuration does not match native {name}")
        if run["field_report"]["configuration"] != config["field"]:
            raise ValueError("plot configuration does not match the executed field map")
        current = {key: run[key] for key in ("field_map_sha256", "tracker_compact_sha256",
                                            "expected_inventory_sha256", "factory_sha256",
                                            "runtime_binary_sha256")}
        if identity is not None and current != identity:
            raise ValueError("momentum samples have different geometry, field or runtime identities")
        identity = current


def render(directory, output, config):
    import numpy as np
    import uproot
    output.mkdir(parents=True, exist_ok=True)
    os.environ["MPLBACKEND"] = "Agg"
    os.environ["MPLCONFIGDIR"] = str(directory / "plot-cache")
    os.environ.setdefault("XDG_CACHE_HOME", str(directory / "cache"))
    import matplotlib.pyplot as plt
    from unrooted.io.root import load, load_branch
    from unrooted.plot import StyleSet
    from unrooted.plot.mpl import overlay
    from unrooted.plot.plotly import overlay as interactive_overlay

    pts = config["pt_GeV"]
    edges = np.linspace(*config["eta_range"], config["eta_bins"] + 1)
    validate_cases(directory, config)
    data = {pt: load_counts(directory / f"pt_{pt:g}GeV/counts.csv",
                            config["tracks_per_pt"], config["eta_range"])
            for pt in pts}
    for pt, columns in data.items():
        if not np.allclose(columns["pt_GeV"], pt, rtol=1e-6, atol=0):
            raise ValueError(f"the {pt:g} GeV sample does not have the requested transverse momentum")
        if set(np.unique(columns["charge"])) != {-1.0, 1.0}:
            raise ValueError("the study must contain both requested muon charge signs")
    reference = data[pts[0]]
    for pt in pts[1:]:
        for key in ("event_nr", "eta", "phi", "charge"):
            # ROOT kinematics may be float32; angular agreement must respect
            # serialization precision even for the same seeded directions.
            tolerance = 1e-6 if key in ("eta", "phi") else 0
            if not np.allclose(reference[key], data[pt][key], rtol=0, atol=tolerance):
                raise ValueError(f"pT samples do not share generated {key}")
    root_path = output / "profiles.root"
    with uproot.recreate(root_path) as root_file:
        for pt, columns in data.items():
            tree = root_file.mktree(f"tracks/pt_{pt:g}GeV",
                                   {key: "float64" for key in columns})
            tree.extend(columns)
            for key, (title, _) in COMPONENTS.items():
                root_file[f"profiles/pt_{pt:g}GeV/{key}"] = root_profile(
                    columns["eta"], columns[key], edges, title)
    profiles = {}
    statistics = {}
    for pt, columns in data.items():
        entries = np.histogram(columns["eta"], bins=edges)[0]
        if np.any(entries == 0):
            raise ValueError("empty eta profile bins; increase track sample or reduce bins")
        statistics[str(pt)] = {}
        for key in COMPONENTS:
            from_tree = load_branch(
                root_path, f"tracks/pt_{pt:g}GeV", "eta", key,
                n_bins=config["eta_bins"], range=tuple(config["eta_range"]),
            )
            profile = load(root_path, f"profiles/pt_{pt:g}GeV/{key}")
            np.testing.assert_allclose(profile.values, from_tree.values, rtol=0, atol=1e-12)
            np.testing.assert_allclose(profile.variances, from_tree.variances, rtol=0, atol=1e-12)
            independent_mean = np.histogram(columns["eta"], bins=edges,
                                            weights=columns[key])[0] / entries
            np.testing.assert_allclose(profile.values, independent_mean, rtol=0, atol=1e-12)
            profile.axes[0].label = r"Generated pseudorapidity $\eta$"
            profiles[pt, key] = profile
            statistics[str(pt)][key] = {
                "entries": entries.tolist(), "mean": profile.values.tolist(),
                "standard_error": np.sqrt(profile.variances).tolist(),
                "global_mean": float(columns[key].mean()),
                "zero_crossing_tracks": int(np.count_nonzero(columns[key] == 0)),
            }
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11, "axes.titlesize": 13,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.labelcolor": "#24364a", "text.color": "#24364a",
        "xtick.color": "#43556a", "ytick.color": "#43556a",
        "figure.facecolor": "white", "savefig.facecolor": "white",
    })
    palette = StyleSet.load("odd")
    styles = [replace(palette[i], marker=None, fill_alpha=None,
                      line_width=2.0, line_style=("-", "--", ":")[i],
                      error_display="band", error_alpha=0.18, spread_display=None)
              for i in range(len(pts))]
    labels = [rf"$p_T = {pt:g}$ GeV" for pt in pts]
    caption = (f"{config['tracks_per_pt']:,} generated muons / momentum · origin vertex · both charges\n"
               "Mean ± standard error in each η bin; zero crossings included · material effects off")
    figures = []

    def figure(name, keys, shape, size):
        fig, axes = plt.subplots(*shape, figsize=size, sharex=True, squeeze=False)
        for ax, key in zip(axes.flat, keys):
            overlay([profiles[pt, key] for pt in pts], ax=ax, labels=labels, styles=styles)
            ax.set_title(COMPONENTS[key][0], loc="left", fontweight="bold")
            ax.set_ylabel("Mean sensitive crossings")
            ax.set_xlim(*config["eta_range"])
            ax.set_ylim(bottom=0)
            ax.grid(axis="y", alpha=0.15)
            ax.get_legend().remove()
        for ax in list(axes.flat)[len(keys):]:
            ax.axis("off")
        fig.suptitle("nODD Tracker  |  Sensitive crossings", fontsize=19, fontweight="bold", x=0.07, ha="left")
        handles, legend_labels = axes.flat[0].get_legend_handles_labels()
        fig.legend(handles, legend_labels, loc="upper right", bbox_to_anchor=(0.99, 0.985),
                   frameon=False, fontsize=10, ncol=3)
        fig.text(0.07, 0.928, "PROTOTYPE · Native DD4hep → ACTS TrackingGeometry  ·  DES-026 finite-winding map, B₀ = 3 T", fontsize=11)
        fig.text(0.07, 0.025, caption, fontsize=9, color="#526477")
        fig.subplots_adjust(left=0.07, right=0.98, top=0.88, bottom=0.12,
                            hspace=0.35, wspace=0.23)
        for suffix in ("svg", "pdf", "png"):
            path = output / f"{name}.{suffix}"
            fig.savefig(path, dpi=180)
            figures.append(path)
        plt.close(fig)

    figure("sensitive-crossings", ["full_tracker", "pixel", "short_strip", "long_strip"], (2, 2), (13, 9))
    figure("sensitive-crossings-systems", [f"system{i}" for i in range(1, 8)], (4, 2), (13, 15))
    interactive = interactive_overlay([profiles[pt, "full_tracker"] for pt in pts],
                                      labels=labels, styles=styles)
    # Histogram overlays return a Plotly Figure, including the optional ratio mode.
    if isinstance(interactive, tuple):
        interactive = interactive[0]
    interactive.update_layout(title="nODD Tracker · DES-026 3 T map · mean sensitive crossings",
                              xaxis_title="Generated pseudorapidity η",
                              yaxis_title="Mean sensitive crossings", template="plotly_white")
    for trace in interactive.data:
        for pt in pts:
            if trace.name == rf"$p_T = {pt:g}$ GeV":
                trace.name = f"pT = {pt:g} GeV"
    html = output / "sensitive-crossings.html"
    interactive.write_html(html, include_plotlyjs=True)
    figures.append(html)
    # Retain compact full per-track evidence, without large native step ROOT files.
    for pt in pts:
        source = directory / f"pt_{pt:g}GeV/counts.csv"
        with (output / f"counts-pt-{pt:g}GeV.csv.gz").open("wb") as stream:
            with gzip.GzipFile(filename="", fileobj=stream, mode="wb", mtime=0) as compressed:
                compressed.write(source.read_bytes())
    origin = json.loads(distribution("unrooted").read_text("direct_url.json"))
    report = {
        "configuration": config, "eta_edges": edges.tolist(), "profiles": statistics,
        "uncertainty": "Population-profile standard error sqrt(M2/N^2), unweighted generated probes",
        "checks": "PASS: all tracks, paired directions, eventwise count closure, nonempty bins; TProfile = unrooted branch profile = independent sums",
        "unrooted_version": version("unrooted"), "unrooted_origin": origin,
        "script_sha256": sha256(__file__), "profiles_root_sha256": sha256(root_path),
        "figures": {p.name: sha256(p) for p in figures},
        "input_counts_sha256": {str(pt): sha256(directory / f"pt_{pt:g}GeV/counts.csv") for pt in pts},
    }
    (output / "profiles.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: unrooted profiles, TProfiles and {len(figures)} figures in {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("study.json"))
    args = parser.parse_args()
    render(args.directory, args.output, json.loads(args.config.read_text()))
