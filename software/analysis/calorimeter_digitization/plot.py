#!/usr/bin/env python3
"""Replot issue117 compact evidence without event files or a simulation runtime."""
import argparse
import json
import math
import os
from pathlib import Path
import tempfile

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "nodd-issue117-matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def statistics(sample):
    m = sample["moments"]
    n = m["n"]
    if n < 2:
        raise ValueError("At least two events are needed for a response-width plot")
    mean = m["sum_digitized"] / n
    variance = max(0, (m["sum_digitized_squared"] - n * mean * mean) / (n - 1))
    sigma = math.sqrt(variance)
    population_variance = variance * (n - 1) / n
    if mean <= 0 or population_variance <= 0:
        raise ValueError("Relative-width uncertainty requires positive mean and variance")
    higher_moments = ("sum_digitized_cubed" in m, "sum_digitized_fourth" in m)
    if higher_moments[0] != higher_moments[1]:
        raise ValueError("Third and fourth moments must be supplied together")
    if not higher_moments[0]:
        # Preserve the explicitly labelled approximation used by the existing
        # pre-deferral preview, whose retained summaries contain only moments1/2.
        return mean, sigma, math.sqrt(variance / n), sigma / mean / math.sqrt(2 * (n - 1))
    central3 = m["sum_digitized_cubed"] / n - 3 * mean * m["sum_digitized_squared"] / n + 2 * mean**3
    central4 = m["sum_digitized_fourth"] / n - 4 * mean * m["sum_digitized_cubed"] / n + 6 * mean**2 * m["sum_digitized_squared"] / n - 3 * mean**4
    # Delta-method uncertainty of RMS/mean, retaining covariance of the mean
    # and variance and the observed non-Gaussian third/fourth central moments.
    relative_variance = (central4 - population_variance**2) / (4 * population_variance * mean**2)
    relative_variance += population_variance**2 / mean**4 - central3 / mean**3
    rms_error = math.sqrt(max(0, relative_variance / n))
    return mean, sigma, math.sqrt(variance / n), rms_error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    shower_samples = [s for s in data["samples"] if s["particle"] in ("e-", "gamma")]
    args.output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.6))
    fig.subplots_adjust(left=.085, right=.985, bottom=.21, top=.79, wspace=.30)
    shades = ["#cccc00", "#999900", "#666600"]
    for particle, marker, linestyle in [("e-", "o", "-"), ("gamma", "s", "--")]:
        etas = sorted({s["eta"] for s in data["samples"] if s["particle"] == particle})
        for eta, color in zip(etas, shades):
            samples = sorted((s for s in data["samples"] if s["particle"] == particle and s["eta"] == eta), key=lambda s: s["beam_energy_GeV"])
            energy = [s["beam_energy_GeV"] for s in samples]
            values = [statistics(s) for s in samples]
            label = f"ECAL {particle}, η={eta:g}"
            axes[0].errorbar(energy, [v[0] / e for v,e in zip(values,energy)],
                             yerr=[v[2] / e for v,e in zip(values,energy)],
                             marker=marker, ls=linestyle, color=color, label=label, capsize=3)
            axes[1].errorbar(energy, [v[1]/v[0] for v in values],
                             yerr=[v[3] for v in values],
                             marker=marker, ls=linestyle, color=color, capsize=3)
    axes[0].set(ylabel="Mean deposit-equivalent digitized energy /\nbeam energy", xlabel="Beam energy [GeV]")
    axes[1].set(ylabel="Digitized event-energy RMS / mean", xlabel="Beam energy [GeV]")
    # SRC-CALICE-SIW-ELECTRONS-2008, arXiv:0811.2354v1 section6.2.
    # The published 6--45 GeV range and different geometry are explicit.
    context_energy = [6 + 39 * i / 100 for i in range(101)]
    axes[1].plot(context_energy, [math.hypot(.166 / math.sqrt(e), .011) for e in context_energy],
                 color="#777777", ls=":", label="CALICE 2008: different geometry, scale context")
    axes[1].legend(fontsize=8)
    for axis in axes:
        axis.grid(alpha=.2)
        axis.set_xticks([5,20,50])
    axes[0].legend(fontsize=8, ncol=2)
    counts = sorted({s["moments"]["n"] for s in shower_samples})
    count_text = str(counts[0]) if len(counts) == 1 else "/".join(map(str, counts))
    settings = sorted({(s["configuration"]["noise_MIP"], s["configuration"]["threshold_MIP"]) for s in shower_samples})
    setting_text = "; ".join(f"{noise:g} MIP noise, {threshold:g} MIP threshold" for noise, threshold in settings)
    fig.suptitle(f"ODD Si–W ECAL · original Marlin silicon energy kernel · PROTOTYPE\nSparse signal cells; {setting_text}; {count_text} events / point", fontsize=11)
    moment_modes = {"sum_digitized_fourth" in s["moments"] for s in shower_samples}
    if moment_modes == {False}:
        width_error_note = "Gaussian approximation; shower tails and systematics unquantified."
    elif moment_modes == {True}:
        width_error_note = "empirical-moment delta approximation; rare tails remain statistically limited."
    else:
        width_error_note = "empirical moments where available, otherwise Gaussian approximation."
    fig.text(.03,.025,f"Mean errors: standard error. RMS errors: {width_error_note}\nNo shower-energy calibration, detector-wide noise, pileup, or original full-processor agreement established.",fontsize=8)
    fig.savefig(args.output / "response.png", dpi=170)
    plt.close(fig)

    central = next(s for s in data["samples"] if s["particle"]=="mu-" and s["eta"]==0)
    mip = data["calibration"]["mip_energy_GeV"]
    fig, axes = plt.subplots(1,2,figsize=(11,4.9))
    fig.subplots_adjust(left=.075, right=.985, bottom=.23, top=.80, wspace=.25)
    for axis, key, scale, label in [(axes[0],"sim_cell_energy",1/mip,"Held-out simulated silicon cell deposits"),
                                   (axes[1],"digitized_cell_energy",1,"Held-out digitized ECAL cells")]:
        h=central[key]
        axis.stairs(h["counts"],[x*scale for x in h["edges"]],fill=True,color="#cccc00",label="ECAL")
        axis.axvline(1,color="#444444",ls="--",lw=1,label="Frozen calibration MIP")
        axis.set(xlabel="Cell energy [MIP]",ylabel="Cell counts",title=label,xlim=(0,3))
        axis.legend(fontsize=8)
    fig.suptitle(f"{central['beam_energy_GeV']:g} GeV central muons · {central['moments']['n']} held-out events · PROTOTYPE",fontsize=11)
    calibration_count = data["calibration"]["calibration_events"][1] - data["calibration"]["calibration_events"][0]
    calibration_width = 2 * data["calibration"]["bin_quantization_half_width_GeV"] * 1e6
    fig.text(.03,.025,f"MIP scale {mip*1e6:.2f} keV, frozen from {calibration_count} separate events using a {calibration_width:g} keV binned mode.\nNo Landau–Gaussian fit, angular calibration or systematic uncertainty established.",fontsize=8)
    fig.savefig(args.output / "mip.png",dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    main()
