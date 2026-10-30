"""Replay four new species cases and compare all five populations without pooling."""
import argparse
from pathlib import Path
import numpy as np
from plot import plot, save, plt, COLORS
from species_report import MATRIX, PTS, OLD_REFERENCE, case_directory, label, read_summary


def plot_species(data, output, *, muon_reference=OLD_REFERENCE):
    data, output = Path(data), Path(output)
    summaries = {}
    # Validate the full real input matrix before producing any labeled output.
    for simulation, particle in MATRIX:
        for pt in PTS:
            sample, _ = read_summary(case_directory(data, simulation, particle, muon_reference) / f"pt{pt}")
            if (simulation, particle) != ("fatras", "muon") and (
                    sample.get("simulation") != simulation or sample.get("particle_configuration", {}).get("name") != particle):
                raise ValueError("Retained sample identity differs from plot directory")
            summaries[simulation, particle, pt] = sample
    references = {("fatras", "electron"): ("fatras", "muon"),
                  ("geant4", "muon"): ("fatras", "muon"),
                  ("geant4", "electron"): ("fatras", "electron"),
                  ("geant4", "pion"): ("geant4", "muon")}
    for simulation, particle in MATRIX[1:]:
        reference_simulation, reference_particle = references[simulation, particle]
        plot(case_directory(data, simulation, particle, muon_reference), output / simulation / particle,
            particle=particle, simulation="Geant4" if simulation == "geant4" else "Fatras",
            reference_data=case_directory(data, reference_simulation, reference_particle, muon_reference),
            reference_label=label(reference_simulation, reference_particle))

    # Every series carries its own denominator and Wilson interval; there is no
    # concatenation or total-trial counter across these distinct populations.
    colors = (*COLORS, "#8e44ad")
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True, sharey=True)
    fig_pt, ax_pt = plt.subplots(figsize=(9, 5))
    for (simulation, particle), color in zip(MATRIX, colors):
        series = []
        for ax, pt in zip(axes.flat, PTS):
            summary = summaries[simulation, particle, pt]
            bins = summary["eta_bins"]
            x = [sum(b["eta"]) / 2 for b in bins]
            rates = [b["stages"]["ambi"]["efficiency"] for b in bins]
            y = np.asarray([r["value"] if r["value"] is not None else np.nan for r in rates])
            bounds = np.asarray([r["wilson95"] if r["wilson95"] is not None else [np.nan, np.nan] for r in rates])
            ax.errorbar(x, y, yerr=np.maximum(0., [y - bounds[:, 0], bounds[:, 1] - y]),
                fmt="o-", color=color, ms=2, lw=.9, capsize=1.5, label=label(simulation, particle))
            ax.set(title=f"pT = {pt} GeV", xlabel="Generated η", ylabel="Primary reconstruction efficiency",
                   xlim=(-4, 4), ylim=(0, 1.04))
            ax.grid(alpha=.2)
            series.append(summary["stages"]["ambi"]["efficiency"])
        y = np.asarray([r["value"] for r in series])
        bounds = np.asarray([r["wilson95"] for r in series])
        ax_pt.errorbar(PTS, y, yerr=np.maximum(0., [y - bounds[:, 0], bounds[:, 1] - y]),
            fmt="o-", color=color, ms=4, lw=1.1, capsize=3, label=label(simulation, particle))
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=8, loc="lower center", ncol=3)
    fig.suptitle("nODD balanced tracker · frozen GBTS · Gaussian digitization · 3 T\nFive distinct single-particle populations; per-sample 95% Wilson intervals")
    fig.tight_layout(rect=(0, .07, 1, 1))
    output.mkdir(parents=True, exist_ok=True)
    save(fig, output, "efficiency-comparison")
    ax_pt.set(xscale="log", xlabel="Generated pT [GeV]", ylabel="Primary reconstruction efficiency", ylim=(0, 1.04))
    ax_pt.grid(alpha=.2)
    ax_pt.legend(fontsize=8, loc="lower right")
    fig_pt.suptitle("All-generated efficiency · separate population denominators\n95% Wilson intervals; no pooling across species or transports")
    fig_pt.tight_layout()
    save(fig_pt, output, "efficiency-comparison-pt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="Root figure directory")
    parser.add_argument("--muon-reference", type=Path, default=OLD_REFERENCE)
    args = parser.parse_args()
    plot_species(args.data, args.output, muon_reference=args.muon_reference)
