#!/usr/bin/env python3
"""Replot nODD/control raw silicon energy summaries; no simulation required."""
import argparse
import json
import math
import os
from pathlib import Path
import tempfile

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "nodd-issue117-matplotlib"))
ECAL = "#cccc00"
CONTROL = "#777700"


def statistics(sample):
    """Mean, unbiased RMS, SEM and whole-event-bootstrap error of RMS/mean.

    The optional delta-method cross-check retains the distribution's
    covariance between its mean and variance. This is an asymptotic MC error,
    without physics, geometry or rare-tail systematic uncertainty.
    """
    m = sample["moments"]
    n = m["n"]
    if n < 2:
        raise ValueError("Need at least two generated events per sample")
    raw = [m[k] / n for k in ("sum_E", "sum_E2", "sum_E3", "sum_E4")]
    if not all(math.isfinite(x) for x in raw) or raw[0] < 0:
        raise ValueError("Invalid event-energy moments")
    mean, second, third, fourth = raw
    if mean == 0 and any(x != 0 for x in raw[1:]):
        raise ValueError("Zero nonnegative energy sum requires all higher moments zero")
    v = max(0., second - mean**2)
    sigma = math.sqrt(v * n / (n - 1))
    sem = sigma / math.sqrt(n)
    c3 = third - 3 * mean * second + 2 * mean**3
    c4 = fourth - 4 * mean * third + 6 * mean**2 * second - 3 * mean**4
    error2 = 0.
    if v and mean:
        error2 = ((c4 - v**2) / (4 * v * mean**2)
                  + v**2 / mean**4 - c3 / mean**3) / n
    return dict(n=n, mean_GeV=mean, rms_GeV=sigma, mean_error_GeV=sem,
                relative_width=sigma / mean if mean else None,
                relative_width_error=sample["bootstrap"]["relative_width_standard_error"],
                relative_width_delta_error=math.sqrt(max(0., error2)) if mean else None)


def independent_ratio(a, b):
    if not b["mean_GeV"]:
        return None, None
    ratio = a["mean_GeV"] / b["mean_GeV"]
    error = math.hypot(a["mean_error_GeV"] / b["mean_GeV"],
                       a["mean_GeV"] * b["mean_error_GeV"] / b["mean_GeV"]**2)
    return ratio, error


def wilson(successes, n):
    """Two-sided 95% Wilson binomial interval, conditional on the fixed cut."""
    if not 0 <= successes <= n or n < 1:
        raise ValueError("Invalid tail numerator/denominator")
    p = successes / n
    z = 1.959963984540054
    centre = (p + z*z / (2*n)) / (1 + z*z / n)
    half = z * math.sqrt(p * (1 - p) / n + z*z / (4*n*n)) / (1 + z*z / n)
    # Include exact boundary estimates despite roundoff at p=0 or p=1.
    return p, max(0., min(p, centre - half)), min(1., max(p, centre + half))


def validate(data):
    samples = {}
    points = {p["id"]: p for p in data["points"]}
    if len(points) != len(data["points"]):
        raise ValueError("Duplicate scan point IDs")
    for s in data["samples"]:
        key = (s["geometry"], s["point_id"], s["energy_GeV"])
        if key in samples or s["point_id"] not in points or s["geometry"] not in ("tiled", "continuous"):
            raise ValueError("Unexpected or duplicated sample")
        samples[key] = s
        n = s["moments"]["n"]
        h = s["histogram"]
        if (len(h["edges_GeV"]) != len(h["counts"]) + 1
                or any(not math.isfinite(v) for v in h["edges_GeV"])
                or any(v < 0 for v in h["counts"] + [h["underflow"], h["overflow"]])
                or any(a >= b for a, b in zip(h["edges_GeV"], h["edges_GeV"][1:]))
                or sum(h["counts"]) + h["underflow"] + h["overflow"] != n):
            raise ValueError("Histogram bins/denominator do not reconcile")
        if len(s["layer_energy"]["sum_GeV"]) != 48 or not math.isclose(
                sum(s["layer_energy"]["sum_GeV"]), s["moments"]["sum_E"], rel_tol=1e-8, abs_tol=1e-10):
            raise ValueError("Longitudinal deposit sums do not reconcile")
        statistics(s)
    if any(("continuous" if g == "tiled" else "tiled", p, e) not in samples for g, p, e in samples):
        raise ValueError("Every tiled point/energy needs its continuous control")
    return points, samples


def plot(data, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    points, samples = validate(data)
    primary = 20
    ids = [p for p in points if ("tiled", p, primary) in samples]
    values = {k: statistics(s) for k, s in samples.items()}
    x = np.arange(len(ids))
    labels = ids
    counts = sorted({s["moments"]["n"] for s in samples.values()})
    count_text = str(counts[0]) if len(counts) == 1 else f"{min(counts)}–{max(counts)}"
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    output.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.subplots_adjust(left=.075, right=.98, bottom=.18, top=.86, hspace=.54, wspace=.27)
    a, b, c, d = axes.flat
    ratios = [independent_ratio(values["tiled", p, primary], values["continuous", p, primary]) for p in ids]
    finite = lambda value: np.nan if value is None else value
    # The predeclared common mechanical seam has negligible energy and mostly
    # zero events. Its formal ratio is retained in the numerical output, while
    # spectra/profiles expose that population without an unstable ratio axis.
    a.errorbar(x, [finite(r[0]) if p != "S" else np.nan for p, r in zip(ids, ratios)],
               yerr=[finite(r[1]) if p != "S" else np.nan for p, r in zip(ids, ratios)], color=CONTROL,
               marker="o", markerfacecolor=ECAL, markeredgecolor=CONTROL, capsize=3, ls="none")
    a.axhline(1, ls="--", lw=1, color="#888888")
    a.set(title="A  Mean raw silicon signal: tiled / continuous", ylabel="Ratio of means", ylim=(0, max(1.1, max((r[0]+r[1] for p,r in zip(ids,ratios) if r[0] is not None and p != "S"), default=1)*1.08)))
    for i, (p, r) in enumerate(zip(ids, ratios)):
        if p == "S" or r[0] is None:
            a.text(i, .03, "near-zero signal" if p == "S" else "undefined", transform=a.get_xaxis_transform(), rotation=90, ha="center", va="bottom", fontsize=8)
    for geometry, color, marker, shift, label in (("tiled", ECAL, "o", -.09, "ECAL tiled nODD"),
                                                   ("continuous", CONTROL, "s", .09, "ECAL idealized continuous control")):
        vals = [values[geometry, p, primary] for p in ids]
        b.errorbar(x + shift, [finite(None if v["relative_width"] is None else 100*v["relative_width"]) for v in vals],
                   yerr=[finite(None if v["relative_width_error"] is None else 100*v["relative_width_error"]) for v in vals],
                   color=color, marker=marker, markeredgecolor=CONTROL, ls="none", capsize=3, label=label)
        intervals = [wilson(samples[geometry, p, primary]["tail_events"], v["n"]) for p, v in zip(ids, vals)]
        joint = [samples[geometry, p, primary]["bootstrap"]["tail_fraction_with_reference_cut_percentile95"] for p in ids]
        c.vlines(x + shift, [100*v[0] for v in joint], [100*v[1] for v in joint],
                 color=color, linewidth=5, alpha=.3)
        c.errorbar(x + shift, [100*v[0] for v in intervals],
                   yerr=[[100*(v[0]-v[1]) for v in intervals], [100*(v[2]-v[0]) for v in intervals]],
                   color=color, marker=marker, markeredgecolor=CONTROL, ls="none", capsize=3)
    b.set(title="B  Raw event-energy spread (log scale)", ylabel="RMS / mean [%]", yscale="log")
    b.legend(fontsize=8)
    b.text(.03, .5, "Width error unavailable when\nbootstrap means can be zero", transform=b.transAxes, fontsize=8)
    c.set(title="C  Fraction below the common frozen signal cut", ylabel="Events below cut [%]", ylim=(-3, 103))
    for axis in (a, b, c):
        axis.set_xticks(x, labels, rotation=23, ha="right", fontsize=9)
        axis.set_xlabel("First-plane impact point (definitions in scan protocol)", fontsize=9)
        axis.grid(axis="y", alpha=.2)
    multi = [p for p in ids if p != "S" and sum(("tiled", p, e) in samples for e in (5, 20, 50)) > 1]
    shades = [ECAL, "#999900", "#555500"]
    for p, color in zip(multi, shades):
        energies = sorted(e for g, point, e in samples if g == "tiled" and point == p)
        ratio = [independent_ratio(values["tiled", p, e], values["continuous", p, e]) for e in energies]
        d.errorbar(energies, [finite(r[0]) for r in ratio], yerr=[finite(r[1]) for r in ratio], marker="o", color=color,
                   markeredgecolor=CONTROL, capsize=3, label=points[p]["label"])
    d.axhline(1, ls="--", lw=1, color="#888888")
    d.set(title="D  Selected energy dependence", xlabel="Electron beam energy [GeV]", ylabel="Mean tiled / continuous", xticks=[5, 20, 50])
    d.legend(fontsize=8)
    d.text(.03, .45, "S: near-zero signal; see distributions/data", transform=d.transAxes, fontsize=8)
    d.grid(alpha=.2)
    fig.suptitle(f"nODD Si–W endcap · raw Geant4 electron response · PROTOTYPE\n48 layers, all +z wedges; {count_text} independent events / geometry / point; panels A–C:20 GeV", fontsize=14, y=.96)
    fig.text(.025, .02, "Errors: MC standard errors; width: whole-event bootstrap. Tails: thin bars = fixed-cut Wilson95%; wide bars = joint sample/reference bootstrap95%.\nCommon seam S is shown in distributions/profiles; its unstable mean ratio is omitted from A/D. All populations are retained in data.\nIdealized control adds gap silicon and activates guards. No digitization, energy calibration or full-detector performance claim.", fontsize=9, va="bottom")
    fig.savefig(output / "nodd-tiling-response.png", dpi=160)
    plt.close(fig)

    # Representative shapes expose tails hidden by a single mean or width.
    preferred = [p for p in ("C", "G", "K-gap", "S") if p in ids]
    chosen = preferred[:4] if len(preferred) >= 4 else ids[:4]
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.subplots_adjust(left=.08, right=.98, bottom=.16, top=.80, hspace=.52, wspace=.27)
    cut = data["tail_definition"]["visible_fraction_cut"]
    for axis, p in zip(axes.flat, chosen):
        occupied_max = 0.
        for geometry, color, label in (("tiled", ECAL, "ECAL tiled nODD"), ("continuous", CONTROL, "ECAL continuous control")):
            s = samples[geometry, p, primary]
            h = s["histogram"]
            edges = np.asarray(h["edges_GeV"]) / primary * 100
            density = np.asarray(h["counts"]) / s["moments"]["n"] / np.diff(edges)
            axis.stairs(density, edges, color=color, fill=geometry == "tiled", alpha=.65 if geometry == "tiled" else 1, label=label)
            occupied = np.flatnonzero(h["counts"])
            if len(occupied):
                occupied_max = max(occupied_max, edges[occupied[-1]+1])
        axis.axvline(100*cut, color="#444444", ls=":", label="Frozen low-signal cut")
        zero_text = ", ".join(f'{g}:{samples[g,p,primary]["zero_events"]}/{samples[g,p,primary]["moments"]["n"]}' for g in ("tiled", "continuous"))
        axis.set(title=f'{p}: {points[p]["label"]}\nZero signal: {zero_text}',
                 xlabel="Raw silicon energy / beam energy [%]", ylabel="Probability density /\npercentage point",
                 xlim=(0, max(occupied_max*1.05, 110*cut)))
        axis.title.set_fontsize(10)
        axis.grid(alpha=.2)
        axis.legend(fontsize=8)
    fig.suptitle("nODD Si–W endcap · 20 GeV electrons · PROTOTYPE\nRaw deposited energy; all generated events retained", fontsize=14, y=.97)
    fig.text(.025, .035, "Each distribution uses its generated-event denominator. No independent per-point energy rescaling or electronics response.\nFinite statistics and this endcap-only setup do not establish reconstructed energy resolution or general detector acceptance.", fontsize=9)
    fig.savefig(output / "nodd-tiling-spectra.png", dpi=160)
    plt.close(fig)
    profile_ids = [p for p in ("C", "G", "S") if p in ids]
    fig, axes = plt.subplots(1, len(profile_ids), figsize=(15, 5), squeeze=False)
    fig.subplots_adjust(left=.065, right=.98, bottom=.22, top=.77, wspace=.30)
    for axis, p in zip(axes.flat, profile_ids):
        for geometry, color, label in (("tiled", ECAL, "ECAL tiled nODD"), ("continuous", CONTROL, "ECAL continuous control")):
            sample = samples[geometry, p, primary]
            n = sample["moments"]["n"]
            total = np.asarray(sample["layer_energy"]["sum_GeV"])
            square = np.asarray(sample["layer_energy"]["sum_GeV2"])
            mean = total / n / primary * 100
            error = np.sqrt(np.maximum(0., (square-total**2/n)/(n-1)/n)) / primary * 100
            layer = np.arange(48)
            axis.plot(layer, mean, color=color, label=label)
            axis.fill_between(layer, np.maximum(0., mean-error), mean+error, color=color, alpha=.25)
        axis.set(title=f'{p}: {points[p]["label"]}', xlabel="Sensitive layer index",
                 ylabel="Mean silicon energy / beam energy\n[% per layer]")
        axis.grid(alpha=.2)
        axis.legend(fontsize=8)
    fig.suptitle("nODD Si–W endcap · 20 GeV electron longitudinal deposits · PROTOTYPE\nAll sectors summed; all events retained", fontsize=13, y=.96)
    fig.text(.025, .035, "Bands: marginal MC standard error per layer. Total event moments retain longitudinal correlations; layers must not be treated as independent.\nFirst-plane impact labels do not imply a fixed x/y through depth. Escaping energy is not scored; this is not a leakage measurement.", fontsize=9)
    fig.savefig(output / "nodd-tiling-longitudinal.png", dpi=160)
    plt.close(fig)
    return [dict(point_id=p, label=points[p]["label"], tiled_to_continuous=ratios[i][0],
                 ratio_error=ratios[i][1], tiled=values["tiled", p, primary],
                 continuous=values["continuous", p, primary]) for i, p in enumerate(ids)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    rows = plot(json.loads(args.input.read_text()), args.output)
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
