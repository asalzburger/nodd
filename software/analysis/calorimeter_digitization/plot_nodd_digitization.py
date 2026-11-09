#!/usr/bin/env python3
"""Render compact nODD/zero-field-ODD validation summaries without ROOT.

The input is the actual nodd_response/nodd_reference_validation output. This
module never opens event files, evaluates fits or invents missing quantities.
--reference is optional; without it only the four response figures are written.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "nodd-compact-plots"))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np


ECAL = "#cccc00"
ODD_ECAL = "#e6e680"
COLORS = {"nodd": ECAL, "odd-zero": ODD_ECAL}
GEOMETRIES = ("nodd", "odd-zero")
GEOMETRY_LABELS = {"nodd": "nODD tracker + ECAL", "odd-zero": "ODD, B = 0"}
STAGES = ("raw", "off", "on")
STAGE_LABELS = {"raw": "raw", "off": "D", "on": "PN"}
LINESTYLES = {"raw": ":", "off": "--", "on": "-"}
MARKERS = {"raw": "s", "off": "^", "on": "o"}
ETA_COLUMNS = (0, 1, 2)
MUON_COLUMNS = (0, 2, -2)
SETTINGS = "148.75 keV/MIP; Gaussian noise 0.13 MIP; strict threshold 0.6 MIP"
SCOPE = "PROTOTYPE · Zero-field tracker + ECAL stage; nODD field/HCAL/FCAL absent. No detector acceptance."


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def number(value, digits=3):
    return f"{value:.{digits}g}" if finite(value) else "unavailable"


def value_error(value, error, digits=3):
    if not finite(value):
        return "unavailable"
    result = number(value, digits)
    return result + (" ± " + number(error, digits) if finite(error) else " (error unavailable)")


def validate_histogram(histogram, expected_entries=None):
    """Check bin contents and all flow counts before any display normalization."""
    edges = np.asarray(histogram["edges"], dtype=float)
    counts = np.asarray(histogram["counts"], dtype=float)
    if (edges.ndim != 1 or counts.ndim != 1 or len(edges) != len(counts) + 1
            or not len(counts) or not np.isfinite(edges).all()
            or not np.isfinite(counts).all() or np.any(np.diff(edges) <= 0)
            or np.any(counts < 0) or np.any(counts != np.floor(counts))):
        raise ValueError("Invalid histogram edges or integer counts")
    flows = [histogram.get("underflow"), histogram.get("overflow")]
    if any(not finite(v) or v < 0 or int(v) != v for v in flows):
        raise ValueError("Histogram needs explicit nonnegative integer flow counts")
    total = int(counts.sum()) + int(flows[0]) + int(flows[1])
    declared = [histogram[k] for k in ("entries", "n") if k in histogram]
    if expected_entries is not None:
        declared.append(expected_entries)
    for n in declared:
        if not finite(n) or n < 0 or int(n) != n or total != n:
            raise ValueError("Histogram entries/underflow/overflow do not close")
    return edges, counts, total


def validate_histogram_tree(value):
    if isinstance(value, dict):
        if "edges" in value and "counts" in value:
            validate_histogram(value)
        for child in value.values():
            validate_histogram_tree(child)
    elif isinstance(value, list):
        for child in value:
            validate_histogram_tree(child)


def style_axes(ax):
    ax.grid(alpha=.2, linewidth=.65)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=9)


def plot_series(ax, xs, ys, errors=None, *, color=ECAL, linestyle="-", marker="o", label=None):
    """Keep missing estimates/errors missing, rather than substituting zero."""
    x = np.asarray(xs, dtype=float)
    y = np.asarray([v if finite(v) else np.nan for v in ys], dtype=float)
    if x.shape != y.shape or not np.isfinite(x).all():
        raise ValueError("Series coordinates have inconsistent shape/nonfinite x")
    line, = ax.plot(x, y, color=color, ls=linestyle, marker=marker, lw=1.9,
                    ms=4.5, markeredgecolor="black", markeredgewidth=.55,
                    markerfacecolor=color if marker in ("o", "D") else "white", label=label)
    if errors is not None:
        if len(errors) != len(y):
            raise ValueError("Series uncertainty shape differs")
        good = np.array([finite(a) and finite(b) and b >= 0 for a, b in zip(ys, errors)])
        if good.any():
            e = np.asarray([v if finite(v) else np.nan for v in errors], dtype=float)
            ax.errorbar(x[good], y[good], yerr=e[good], fmt="none", color=color,
                        elinewidth=1.2, capsize=2.5)
    return line


def draw_histogram(ax, histogram, denominator, *, color, label, linestyle="-", fill=False):
    edges, counts, entries = validate_histogram(histogram)
    if not finite(denominator) or denominator < 0 or entries > denominator:
        raise ValueError("Histogram normalization is not its declared trial population")
    if denominator == 0:
        if entries:
            raise ValueError("Nonempty histogram has a zero denominator")
        return None
    density = counts / (denominator * np.diff(edges))
    return ax.stairs(density, edges, color=color, label=label, linestyle=linestyle,
                     fill=fill, alpha=.22 if fill else 1, linewidth=1.7)


def flow_text(histogram):
    _, _, entries = validate_histogram(histogram)
    return f"N={entries:,}; under/over={histogram['underflow']:,}/{histogram['overflow']:,}"


def finish(fig, path, title, caption, handles=None, *, ncol=3, bottom=.16):
    fig.suptitle(title, y=.985, fontsize=15)
    fig.text(.5, .014, caption, ha="center", va="bottom", fontsize=8.7, linespacing=1.35)
    if handles:
        fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .065),
                   ncol=ncol, frameon=False, fontsize=9, columnspacing=1.8)
    fig.subplots_adjust(left=.072, right=.985, top=.935, bottom=bottom,
                        hspace=.42, wspace=.32)
    fig.savefig(path, dpi=180, facecolor="white", metadata={"Software": "nODD compact-summary renderer"})
    plt.close(fig)


def stage_handles():
    return [Line2D([], [], color=COLORS[g], ls=LINESTYLES[s], marker=MARKERS[s],
                   markeredgecolor="black", markeredgewidth=.55, ms=4.5, lw=2,
                   label=f"{GEOMETRY_LABELS[g]} · {STAGE_LABELS[s]}")
            for g in GEOMETRIES for s in STAGES]


def population_index(data):
    indexed = {}
    for row in data["showers"]["populations"]:
        key = (row["geometry"], row["particle"], float(row["momentum_GeV"]), float(row["eta"]))
        if key in indexed or row["geometry"] not in GEOMETRIES:
            raise ValueError("Duplicate/unknown shower population")
        if not isinstance(row["n"], int) or row["n"] <= 0:
            raise ValueError("Shower population has no generated-event denominator")
        for stage in STAGES:
            entry = row["stages"][stage]
            for key_name in ("energy_GeV", "visible_fraction"):
                if entry[key_name]["n"] != row["n"]:
                    raise ValueError("Shower stage denominator differs from generated events")
            validate_histogram(entry["visible_fraction_histogram"], row["n"])
            validate_histogram(entry["response_histogram"], row["n"])
        if bool(row.get("mirror_control")) != (row["eta"] == -2):
            raise ValueError("Negative-endcap mirror-control flag differs")
        indexed[(row["geometry"], row["particle"], float(row["momentum_GeV"]), float(row["eta"]))] = row
    expected = {(g, p, float(m), float(e)) for g in GEOMETRIES
                for p in ("e-", "gamma") for m in (5, 20, 50) for e in ETA_COLUMNS}
    expected |= {(g, "e-", 20., -2.) for g in GEOMETRIES}
    if set(indexed) != expected:
        raise ValueError("Expected the full main shower grid plus bounded negative-electron controls")
    return indexed


def undefined_note(ax, rows, metric):
    missing = []
    for geometry, stage, momentum, value in rows:
        if not finite(value):
            missing.append(f"{'nODD' if geometry == 'nodd' else 'ODD'} {STAGE_LABELS[stage]} {momentum:g}")
    if missing:
        ax.text(.02, .03, metric + " undefined: " + "; ".join(missing), transform=ax.transAxes,
                va="bottom", fontsize=7.5, wrap=True,
                bbox=dict(facecolor="white", alpha=.9, edgecolor="none"))


def shower_plot(data, species, path):
    index = population_index(data)
    fig, axes = plt.subplots(3, 3, figsize=(16, 12.2))
    for col, eta in enumerate(ETA_COLUMNS):
        undefined = []
        for geometry in GEOMETRIES:
            samples = [index[(geometry, species, float(p), float(eta))] for p in (5, 20, 50)]
            energy = [s["primary_total_energy_GeV"] for s in samples]
            for stage in STAGES:
                values = [s["stages"][stage] for s in samples]
                style = dict(color=COLORS[geometry], linestyle=LINESTYLES[stage], marker=MARKERS[stage])
                plot_series(axes[0, col], energy,
                            [100 * v["visible_fraction"]["mean"] for v in values],
                            [100 * v["visible_fraction"]["mean_SE"] for v in values], **style)
                plot_series(axes[1, col], energy,
                            [100 * (v["mean_response"] - 1) for v in values],
                            [100 * v["response_bootstrap"]["SE"]
                             if finite(v["response_bootstrap"]["SE"]) else None for v in values], **style)
                widths = [v["energy_GeV"]["RMS_over_mean"] for v in values]
                plot_series(axes[2, col], energy,
                            [100 * v if finite(v) else None for v in widths],
                            [100 * v["SD_over_mean_bootstrap"]["SE"]
                             if finite(v["SD_over_mean_bootstrap"]["SE"]) else None for v in values], **style)
                undefined.extend((geometry, stage, p, width) for p, width in zip((5, 20, 50), widths))
        counts = sorted({index[(g, species, float(p), float(eta))]["n"] for g in GEOMETRIES for p in (5, 20, 50)})
        axes[0, col].set_title(f"η = {eta:g} · N = {'/'.join(map(str, counts))} per point/geometry")
        for row in range(3):
            ax = axes[row, col]
            ax.set_xticks([5, 20, 50])
            ax.set_xlabel("Generated primary total energy [GeV]")
            style_axes(ax)
        axes[0, col].set_ylabel("Unscaled mean Si signal / E generated [%]")
        axes[1, col].set_ylabel("Common-scale mean response − 1 [%]")
        axes[1, col].axhline(0, color="black", lw=.7)
        axes[2, col].set_ylabel("All-event sample SD / mean [%]")
        undefined_note(axes[2, col], undefined, "SD/mean")
    name = "electrons" if species == "e-" else "photons"
    finish(fig, path, f"nODD and zero-field ODD · {name}: raw and digitized response",
           SCOPE + "\n" + SETTINGS + ". All generated events, including zeros; paired raw/D/PN within each geometry.\n"
           "One independent ODD reference factor per η is shared by both geometries, energies, species and stages. "
           "Errors: event SEM (unscaled means), 5,000 paired event/reference bootstrap (response/spread). SD/mean is not reconstructed resolution.",
           stage_handles(), bottom=.205)


def find_comparison(data, particle, momentum, eta):
    matches = [r for r in data["showers"]["geometry_comparisons"]
               if (r["particle"], float(r["momentum_GeV"]), float(r["eta"]))
               == (particle, float(momentum), float(eta))]
    if len(matches) != 1:
        raise ValueError("Missing/duplicate geometry comparison")
    return matches[0]


def comparison_plot(data, path):
    index = population_index(data)
    fig, axes = plt.subplots(3, 3, figsize=(16, 12.5))
    handles = []
    for col, eta in enumerate(ETA_COLUMNS):
        undefined = []
        for particle, marker, title in (("e-", "o", "electron"), ("gamma", "D", "photon")):
            comparisons = [find_comparison(data, particle, p, eta) for p in (5, 20, 50)]
            xs = [index[("nodd", particle, float(p), float(eta))]["primary_total_energy_GeV"] for p in (5, 20, 50)]
            for stage in STAGES:
                rows = [r["stages"][stage] for r in comparisons]
                line = plot_series(axes[0, col], xs, [r["mean_ratio_nodd_over_ODD"] for r in rows],
                                   [r["mean_ratio_bootstrap"]["SE"] for r in rows],
                                   color=ECAL, linestyle=LINESTYLES[stage], marker=marker,
                                   label=f"nODD/ODD · {title} {STAGE_LABELS[stage]}")
                if col == 0:
                    handles.append(line)
                undefined.extend(("nodd", stage, p, r["mean_ratio_nodd_over_ODD"]) for p, r in zip((5, 20, 50), rows))
            for geometry in GEOMETRIES:
                rows = [index[(geometry, particle, float(p), float(eta))]["paired_changes"]["PN_minus_raw"] for p in (5, 20, 50)]
                plot_series(axes[1, col], xs,
                            [100 * r["relative_mean_change_to_raw"] if finite(r["relative_mean_change_to_raw"]) else None for r in rows],
                            [100 * r["relative_change_bootstrap"]["SE"] if finite(r["relative_change_bootstrap"]["SE"]) else None for r in rows],
                            color=COLORS[geometry], linestyle="-" if particle == "e-" else "--", marker=marker,
                            label=f"{GEOMETRY_LABELS[geometry]} · {title}")
        axes[0, col].set(title=f"η = {eta:g}", ylabel="Mean unscaled visible fraction: nODD / ODD")
        axes[0, col].axhline(1, color="black", lw=.7)
        undefined_note(axes[0, col], undefined, "Mean ratio")
        axes[1, col].set_ylabel("Paired (mean PN − mean raw) / mean raw [%]")
        axes[1, col].axhline(0, color="black", lw=.7)
        for ax in axes[:2, col]:
            ax.set_xlabel("Generated primary total energy [GeV]")
            ax.set_xticks([5, 20, 50])
            style_axes(ax)
    axes[1, 0].legend(loc="best", fontsize=7.5)
    mirror = find_comparison(data, "e-", 20, -2)
    plot_series(axes[2, 0], [0, 1, 2], [mirror["stages"][s]["mean_ratio_nodd_over_ODD"] for s in STAGES],
                [mirror["stages"][s]["mean_ratio_bootstrap"]["SE"] for s in STAGES], color=ECAL)
    axes[2, 0].axhline(1, color="black", lw=.7)
    axes[2, 0].set_xticks([0, 1, 2], [STAGE_LABELS[s] for s in STAGES])
    axes[2, 0].set(title="Bounded negative-endcap control: e−, 20 GeV/c, η = −2",
                   xlabel="Same response settings", ylabel="Mean visible fraction: nODD / ODD")
    for i, geometry in enumerate(GEOMETRIES):
        row = index[(geometry, "e-", 20., -2.)]["paired_changes"]["PN_minus_raw"]
        plot_series(axes[2, 1], [i],
                    [100 * row["relative_mean_change_to_raw"] if finite(row["relative_mean_change_to_raw"]) else None],
                    [100 * row["relative_change_bootstrap"]["SE"] if finite(row["relative_change_bootstrap"]["SE"]) else None],
                    color=COLORS[geometry])
    axes[2, 1].set_xticks([0, 1], ["nODD", "ODD B = 0"])
    axes[2, 1].axhline(0, color="black", lw=.7)
    axes[2, 1].set(title="Same bounded η = −2 electron control", ylabel="Paired PN − raw / raw [%]")
    axes[2, 2].axis("off")
    lines = ["Common independent ODD calibration", ""]
    for eta in (0, 1, 2, -2):
        row = data["showers"]["calibration"][str(eta)]
        lines.append(f"η {eta:g}: C = {value_error(row['factor'], row['factor_bootstrap']['SE'], 5)}; N = {row['n']}")
    lines += ["", "The same factor applies to both geometries.",
              "It cancels from the matched mean ratio.", "",
              "η = −2: electrons at 20 GeV/c only.",
              "No negative-photon or full negative-energy grid.",
              "Matched guns; independent geometry transports."]
    axes[2, 2].text(0, 1, "\n".join(lines), va="top", fontsize=9, linespacing=1.45)
    for ax in axes[2, :2]:
        style_axes(ax)
    finish(fig, path, "nODD versus zero-field ODD · geometry response and paired digitization changes",
           SCOPE + "\n" + SETTINGS + ". Both geometries use the same response and common calibration; unscaled ratios retain geometry losses.\n"
           "Error bars: 5,000 whole-event/reference bootstrap replicates. Cross-geometry samples are independent; PN/raw changes pair the same event within a geometry.",
           handles, bottom=.205)


def muon_index(data):
    indexed = {}
    for row in data["muons"]["samples"]:
        key = (row["geometry"], float(row["eta"]))
        if key in indexed:
            raise ValueError("Duplicate muon population")
        n = row["counters"]["qualified_spectrum_crossings"]
        nominal = row["counters"]["nominal_layer_opportunities"]
        if row["nominal_opportunity_yield"]["denominator"] != nominal:
            raise ValueError("Muon nominal trial denominator differs")
        for stage in STAGES:
            hist = row["spectra"][stage]["histogram"]
            validate_histogram(hist, n)
            if "actual_thresholded_output" in row["spectra"][stage]:
                _, _, accepted = validate_histogram(row["spectra"][stage]["actual_thresholded_output"])
                if accepted > n:
                    raise ValueError("Muon accepted spectrum exceeds all qualified trials")
        indexed[key] = row
    if set(indexed) != {(g, float(eta)) for g in GEOMETRIES for eta in MUON_COLUMNS}:
        raise ValueError("Expected central and both-endcap muon populations in both geometries")
    return indexed


def efficiency_curve(ax, sample, geometry, identified):
    x = sample["thresholds_MIP"]
    stats = (sample["identified_crossing_categories"]["identified"] if identified
             else sample["nominal_opportunity_yield"])
    denominator = stats["denominator"]
    label = f"{'nODD' if geometry == 'nodd' else 'ODD'} PN {'identified' if identified else 'nominal'}; N={denominator:,}"
    if not denominator or stats["efficiency"] is None:
        return label + " (undefined)"
    y = stats["efficiency"][1]
    plot_series(ax, x, y, color=COLORS[geometry], linestyle="--" if identified else "-",
                marker="^" if identified else "o", label=label)
    intervals = stats.get("event_cluster_bootstrap_CI95")
    if intervals is not None:
        bounds = np.asarray(intervals, float)[:, 1, :]
        if bounds.shape != (2, len(x)) or not np.isfinite(bounds).all():
            raise ValueError("Muon event-bootstrap interval shape differs")
        ax.fill_between(x, bounds[0], bounds[1], color=COLORS[geometry], alpha=.14)
    else:
        # Conditional Wilson intervals are distinct from missing event errors.
        bounds = stats.get("conditional_crossing_Wilson95")
        if bounds is not None and bounds[0] is not None:
            bounds = np.asarray(bounds, float)[:, 1, :]
            values = np.asarray(y, float)
            ax.errorbar(x, values, yerr=np.maximum(0, [values-bounds[0], bounds[1]-values]),
                        fmt="none", color=COLORS[geometry], capsize=2)
        return label + ": event interval unavailable; conditional Wilson only"
    return None


def muon_plot(data, path):
    index = muon_index(data)
    fig, axes = plt.subplots(3, 3, figsize=(17, 15.2))
    global_handles = {}
    for col, eta in enumerate(MUON_COLUMNS):
        details = []
        flow_lines = []
        unavailable = []
        for geometry in GEOMETRIES:
            sample = index[(geometry, float(eta))]
            count = sample["counters"]["qualified_spectrum_crossings"]
            color = COLORS[geometry]
            label = "nODD" if geometry == "nodd" else "ODD B = 0"
            for stage in ("raw", "on"):
                hist = sample["spectra"][stage]["histogram"]
                if count:
                    artist = draw_histogram(axes[0, col], hist, count, color=color,
                                            label=f"{label} {STAGE_LABELS[stage]} prethreshold",
                                            linestyle=LINESTYLES[stage])
                    global_handles.setdefault(artist.get_label(), artist)
                else:
                    unavailable.append(f"{label}: no qualified spectrum trials")
            pn = sample["spectra"]["on"]
            selected = pn.get("actual_thresholded_output")
            if selected is not None and count:
                artist = draw_histogram(axes[0, col], selected, count, color=color,
                                        label=f"{label} PN actual output", linestyle="--", fill=True)
                global_handles.setdefault(artist.get_label(), artist)
            flow_lines.append(f"{label} qualified {count:,}; PN prethreshold " + flow_text(pn["histogram"]))
            fit = pn.get("fit") or {}
            if fit.get("status") != "unavailable" and "curve_x_MIP" in fit and count:
                x = np.asarray(fit["curve_x_MIP"], float)
                y = np.asarray(fit["curve_counts_per_bin"], float) / (count * fit["bin_width_MIP"])
                if x.shape != y.shape or not np.isfinite(x).all() or not np.isfinite(y).all():
                    raise ValueError("Invalid stored MIP fit curve")
                line, = axes[0, col].plot(x, y, color=color, ls="-.", lw=1.3, label=f"{label} PN fit")
                global_handles.setdefault(line.get_label(), line)
            interval_note = efficiency_curve(axes[1, col], sample, geometry, False)
            identified_note = efficiency_curve(axes[1, col], sample, geometry, True)
            if interval_note:
                unavailable.append(interval_note)
            if identified_note:
                unavailable.append(identified_note)
            counters = sample["counters"]
            ray = sample["initial_ray_approximation"]
            snr = sample["SNR"]
            flags = fit.get("model_diagnostic_flags") or []
            details += [f"{label}: {sample['events']:,} held-out muons; {counters['nominal_layer_opportunities']:,} nominal trials",
                        f"Identified primary layers {counters['identified_primary_layers']:,}; qualified spectra {count:,}",
                        f"Unknown/missing {counters['missing_primary_layer_unknown_crossing']:,}; split {counters['split_primary_layer']:,}; contaminated {counters['contaminated_single_cell_layer']:,}",
                        f"Initial-ray active {ray['active_layers']}/{ray['nominal_layers']}; geometric diagnostic only",
                        "PN Landau MPV: " + value_error(fit.get("underlying_Landau_MPV"), fit.get("MPV_event_cluster_bootstrap_SE")) + " MIP",
                        "Convolved mode: " + value_error(fit.get("convolved_peak"), fit.get("convolved_peak_event_cluster_bootstrap_SE")) + " MIP",
                        "SNR: " + value_error(snr.get("ratio"), snr.get("ratio_SE")),
                        f"Fit {fit.get('status', 'unavailable')}; bootstrap failures {fit.get('bootstrap_failed_fits', 'unknown')}; flags: {', '.join(map(str, flags)) or 'none reported'}",
                        f"Rejected endpoint/chord/angle/sector: {counters['endpoint']}/{counters['chord_unavailable']}/{counters['incidence_rejected']}/{counters['sector_ambiguous']}", ""]
            if fit.get("status") == "unavailable":
                details.insert(len(details) - 1, "Fit reason: " + str(fit.get("reason", "not supplied"))[:78])
        axes[0, col].set(title=f"η = {eta:g} · {'bounded negative control' if eta < 0 else 'held-out muon spectra'}",
                         xlabel="Path-normalized signal [MIP at 0.5 mm equivalent path]",
                         ylabel="Density per ALL qualified crossings [MIP⁻¹]")
        all_edges = [index[(g, float(eta))]["spectra"]["on"]["histogram"]["edges"] for g in GEOMETRIES]
        axes[0, col].set_xlim(min(e[0] for e in all_edges), max(e[-1] for e in all_edges))
        axes[0, col].axvline(1, color="black", lw=.7, ls=":")
        axes[0, col].text(.98, .97, "\n".join(flow_lines), transform=axes[0, col].transAxes,
                          ha="right", va="top", fontsize=7.4,
                          bbox=dict(facecolor="white", alpha=.88, edgecolor="none"))
        axes[1, col].set(xlabel="Strict per-cell threshold [MIP; uncorrected pulse]",
                         ylabel="PN pass fraction / nominal opportunity yield", ylim=(-.025, 1.06), xlim=(0, 2))
        axes[1, col].axvline(.6, color="black", lw=.7, ls=":")
        axes[1, col].legend(fontsize=7.5, loc="lower left")
        if unavailable:
            axes[0, col].text(.02, .04, "\n".join(dict.fromkeys(unavailable)),
                              transform=axes[0, col].transAxes, fontsize=7, wrap=True)
        for ax in axes[:2, col]:
            style_axes(ax)
        axes[2, col].axis("off")
        axes[2, col].text(0, 1, "\n".join(details), va="top", fontsize=8, linespacing=1.18)
    pedestal = data["pedestal"]
    caption = SCOPE + "\n" + SETTINGS + ". Signed model pedestal RMS = " + value_error(
        pedestal.get("SD"), pedestal.get("SD") / math.sqrt(2 * (pedestal["n"] - 1))
        if finite(pedestal.get("SD")) and pedestal.get("n", 0) > 1 else None, 4) + " MIP.\n"
    caption += "Selected-output densities use all qualified crossings, including rejected pulses. Bands: whole-event 95% bootstrap. "
    caption += "Nominal depth opportunities, identified crossings and initial rays are distinct; no unseen crossing inventory is inferred."
    finish(fig, path, "nODD and zero-field ODD · digitized MIP, SNR and threshold response",
           caption, list(global_handles.values()), ncol=4, bottom=.18)


def reference_cases(data):
    rows = []
    for case in data["deterministic"]["samples"]:
        result = case.get("result", case)
        sample = case["sample"]
        validate_histogram(result["normalized_residual"], result["matched_cells"])
        if result["events"] != sample["events"]:
            raise ValueError("Reference case event denominator differs")
        rows.append((sample, result))
    declared = data["deterministic"]
    if declared.get("cases", len(rows)) != len(rows) or declared.get("events", sum(r["events"] for _, r in rows)) != sum(r["events"] for _, r in rows):
        raise ValueError("Declared reference totals differ from cases")
    if len(rows) != 22:
        raise ValueError("Expected all 22 frozen nODD deterministic cases")
    return rows


def reference_plot(data, path):
    rows = reference_cases(data)
    fig, axes = plt.subplots(3, 2, figsize=(16, 14.8))
    histogram = dict(rows[0][1]["normalized_residual"])
    edges = histogram["edges"]
    for _, row in rows:
        if row["normalized_residual"]["edges"] != edges:
            raise ValueError("Cannot aggregate residual histograms with different edges")
    histogram["counts"] = np.sum([r["normalized_residual"]["counts"] for _, r in rows], axis=0).tolist()
    histogram["underflow"] = sum(r["normalized_residual"]["underflow"] for _, r in rows)
    histogram["overflow"] = sum(r["normalized_residual"]["overflow"] for _, r in rows)
    matched = sum(r["matched_cells"] for _, r in rows)
    histogram["entries"] = matched
    validate_histogram(histogram, matched)
    axes[0, 0].stairs(histogram["counts"], edges, color=ECAL, lw=1.8)
    axes[0, 0].set(xlim=(edges[0], edges[-1]), xlabel="(native − original) / declared numerical tolerance",
                   ylabel="Matched cells / stored bin", title="A. D exact-cell residuals · full stored bin range")
    if any(histogram["counts"]):
        axes[0, 0].set_yscale("log")
    for bound in (-1, 1):
        axes[0, 0].axvline(bound, color="black", ls="--", lw=.8)
    axes[0, 0].text(.02, .97, f"{len(rows)} cases; {sum(r['events'] for _, r in rows):,} events; {matched:,} matched cells\n"
                    + flow_text(histogram) + "\nEnergy/selection gate: "
                    + ("PASS" if data["deterministic"]["passed"] else "FAIL"),
                    transform=axes[0, 0].transAxes, va="top", fontsize=9)
    axes[0, 1].axis("off")
    axes[0, 1].set_title("B. Every deterministic case · generated events / cells / accepted", loc="left")
    table = []
    for sample, result in rows:
        tag = f"{sample['particle']} p{sample['energy_GeV']:g} η{sample['eta']:g}"
        table.append([tag, f"{result['events']:,}", f"{result['input_sim_cells']:,}",
                      f"{result['matched_cells']:,}", "PASS" if result["passed"] else "FAIL"])
    artist = axes[0, 1].table(cellText=table, colLabels=["Population", "Events", "Input cells", "Matched", "Gate"],
                              colWidths=[.28, .12, .23, .23, .14], cellLoc="right", loc="center")
    artist.auto_set_font_size(False)
    artist.set_fontsize(7.2)
    artist.scale(1, 1.15)
    for (row, col), cell in artist.get_celld().items():
        cell.set_edgecolor("#dddddd")
        if row == 0:
            cell.set_facecolor(ODD_ECAL)
        if col == 0:
            cell.set_text_props(ha="left")
    comparisons = data["stochastic"]["comparisons"]
    if len(comparisons) != 4:
        raise ValueError("Expected four complete P/PN replay comparisons")
    comparisons = sorted(comparisons, key=lambda s: ("gamma" in s["fixture"], s["mode"] != "P"))
    for index, sample in enumerate(comparisons):
        ax = axes[1 + index // 2, index % 2]
        for side, color, line, label in (("original", ODD_ECAL, "--", "Original Key4hep / ROOT"),
                                         ("native", ECAL, "-", "Native ACTS adapter / CLHEP")):
            measure = sample[side]["event_energy_MIP"]
            validate_histogram(measure["histogram"], measure["n"])
            draw_histogram(ax, measure["histogram"], measure["n"], color=color, label=label, linestyle=line)
        energy_test = sample["tests"]["event_energy_MIP"]
        count_test = sample["tests"]["accepted_cell_count"]
        interval = (energy_test.get("width") or {}).get("percentile95")
        width = f"[{number(interval[0])}, {number(interval[1])}]" if interval is not None else "unavailable"
        combined = energy_test["combined_standard_error"]
        mean_sigma = abs(energy_test["mean_difference_native_minus_original"]) / combined if combined else None
        state = "PASS" if sample["passed"] else "FAIL"
        sigma_text = number(mean_sigma) if combined else "constant (numerical equality gate)"
        lines = [f"Gates {state}; N={sample['events']:,} per framework",
                 f"Energy CDF p={number(energy_test['cdf']['p_value'], 4)}; count CDF p={number(count_test['cdf']['p_value'], 4)}",
                 f"Energy mean |Δ|/combined SE={sigma_text}; gate {'PASS' if energy_test['mean_within_five_SE'] else 'FAIL'}",
                 f"Count mean ≤5 SE: {'PASS' if count_test['mean_within_five_SE'] else 'FAIL'}; energy SD ratio95% {width}"]
        ax.text(.98, .97, "\n".join(lines), transform=ax.transAxes, va="top", ha="right", fontsize=8.5,
                bbox=dict(facecolor="white", alpha=.92, edgecolor="none"))
        lo = min(sample[s]["event_energy_MIP"]["histogram"]["edges"][0] for s in ("original", "native"))
        hi = max(sample[s]["event_energy_MIP"]["histogram"]["edges"][-1] for s in ("original", "native"))
        ax.set(xlim=(lo, hi), title=f"{'CDEF'[index]}. {sample['fixture']} · {sample['mode']}",
               xlabel="Total accepted event signal [MIP]", ylabel="Density per replay event [MIP⁻¹]")
        ax.set_ylim(top=ax.get_ylim()[1] * 1.32)
    for ax in axes.flat:
        if ax.axison:
            style_axes(ax)
    handles = [Line2D([], [], color=ODD_ECAL, ls="--", lw=2, label="Original Key4hep / ROOT"),
               Line2D([], [], color=ECAL, ls="-", lw=2, label="Native ACTS adapter / CLHEP")]
    finish(fig, path, "nODD LAYOUT-001 · original Key4hep versus native silicon digitizer",
           SCOPE + "\n" + SETTINGS + ". D: pairs/noise disabled. P: pairs only; PN: pairs + electronics.\n"
           "Each replay repeats one real nODD event 1,000 times with audited distinct effective seeds. Independent RNG ensembles, not independent showers or stochastic bitwise equality.\n"
           "Gates: mean ≤5 combined SE; event-label CDF p≥0.001; energy SD-ratio95% interval inside [0.85,1.15]. Full stored residual and energy-bin ranges shown.",
           handles, ncol=2, bottom=.155)


def load_summary(path):
    data = json.loads(Path(path).read_text())
    validate_histogram_tree(data)
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = load_summary(args.response)
    population_index(data)
    muon_index(data)
    if not math.isclose(data["settings"]["mip_energy_GeV"], .00014875, rel_tol=0, abs_tol=1e-15):
        raise ValueError("Unexpected shared MIP scale")
    reference = load_summary(args.reference) if args.reference else None
    if reference is not None:
        reference_cases(reference)
    args.output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 10.5, "axes.labelsize": 9.5,
                         "savefig.bbox": None})
    outputs = []
    for species, name in (("e-", "electron"), ("gamma", "photon")):
        output = args.output / f"nodd-digitized-{name}.png"
        shower_plot(data, species, output)
        outputs.append(output)
    for renderer, name in ((muon_plot, "nodd-digitized-mip.png"),
                           (comparison_plot, "nodd-digitized-comparison.png")):
        output = args.output / name
        renderer(data, output)
        outputs.append(output)
    if reference is not None:
        output = args.output / "nodd-digitization-reference.png"
        reference_plot(reference, output)
        outputs.append(output)
    print(json.dumps({"figures": [str(p) for p in outputs],
                      "response_sha256": hashlib.sha256(args.response.read_bytes()).hexdigest(),
                      "reference_sha256": hashlib.sha256(args.reference.read_bytes()).hexdigest() if args.reference else None}))


if __name__ == "__main__":
    main()
