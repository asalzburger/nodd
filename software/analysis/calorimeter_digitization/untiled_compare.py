"""Compare hash-bound ECAL runs by identical primary IDs and paired bootstrap."""
import argparse
import json
import math
from pathlib import Path
import subprocess

import numpy as np

from angular_analyze import ETA_EDGES, PHI_EDGES, bin_index, folded_phi, summarize
from angular_sample import ROOT, save, sha


def load_run(path):
    proof = json.loads((path / "readback.json").read_text())
    receipt = json.loads((path / "receipt.json").read_text())
    if proof["status"] != "PASS" or receipt["exit_code"] or receipt["disk_abort"]:
        raise ValueError("Unsuccessful run/audit")
    for name, key in (("receipt.json", "receipt_sha256"),
                      ("event-summary.jsonl", "event_summary_sha256")):
        if sha(path / name) != proof[key]:
            raise ValueError(f"Changed {name} after audit")
    rows = sorted((json.loads(line) for line in
                   (path / "event-summary.jsonl").read_text().splitlines()),
                  key=lambda row: row["event"])
    ids = [row["event"] for row in rows]
    if len(rows) != proof["events"] or ids != list(range(len(rows))):
        raise ValueError("Require complete primary IDs starting at zero")
    response = np.asarray([row["response"] for row in rows])
    if not np.all(np.isfinite(response)) or np.any(response < 0):
        raise ValueError("Invalid response")
    for row in rows:
        if not math.isclose(row["response"], row["signal_GeV"] / row["energy_GeV"],
                            rel_tol=1e-13, abs_tol=0):
            raise ValueError("Response/energy inconsistency")
    return rows, response, proof, receipt


def binned_moments(response, category):
    count = np.bincount(category, minlength=10)
    total = np.bincount(category, weights=response, minlength=10)
    squares = np.bincount(category, weights=response ** 2, minlength=10)
    mean = np.divide(total, count, out=np.full(10, np.nan), where=count > 0)
    variance = np.divide(squares - total * mean, count - 1,
                         out=np.full(10, np.nan), where=count > 1)
    width = np.divide(np.sqrt(np.maximum(variance, 0)), mean,
                      out=np.full(10, np.nan), where=mean > 0)
    return mean, width


def paired_bootstrap(responses, categories, replicates, seed):
    """Axes: replica, geometry, projection-major angular bin."""
    rng = np.random.default_rng(seed)
    means = np.full((replicates, 2, 20), np.nan)
    widths = np.full_like(means, np.nan)
    for replica in range(replicates):
        index = rng.integers(len(responses[0]), size=len(responses[0]))
        for geometry, response in enumerate(responses):
            for axis, category in enumerate(categories):
                sl = slice(axis * 10, (axis + 1) * 10)
                means[replica, geometry, sl], widths[replica, geometry, sl] = (
                    binned_moments(response[index], category[index]))
    return means, widths


def interval(values):
    invalid = int(np.count_nonzero(~np.isfinite(values)))
    return dict(ci95=np.quantile(values, [.025, .975]).tolist() if not invalid else None,
                bootstrap_undefined=invalid)


def nullable_difference(left, right):
    return left - right if left is not None and right is not None else None


def compare(args):
    loaded = [load_run(args.tiled), load_run(args.continuous)]
    reference = json.loads(args.reference.read_text())
    if sha(args.tiled / "event-summary.jsonl") != reference["readback"]["event_summary_sha256"]:
        raise ValueError("Tiled ledger differs from published baseline")
    a, b = loaded[0][0], loaded[1][0]
    if len(a) != 10000 or len(a) != len(b):
        raise ValueError("Require both complete 10k samples")
    for left, right in zip(a, b):
        if any(left[key] != right[key] for key in ("event", "energy_GeV", "eta", "phi")):
            raise ValueError("Primary pairing differs")
    for key in ("threads", "seed", "skip", "steering_sha256", "geometry_library_sha256",
                "audit_library_sha256"):
        if loaded[0][3][key] != loaded[1][3][key]:
            raise ValueError(f"Transport setting/library differs: {key}")
    for key in ("input_sha256", "truth_sha256"):
        if loaded[0][2]["sample"][key] != loaded[1][2]["sample"][key]:
            raise ValueError(f"Primary source differs: {key}")
    eta = np.asarray([row["eta"] for row in a])
    phi = np.asarray([row["phi"] for row in a])
    energy = np.asarray([row["energy_GeV"] for row in a])
    responses = [run[1] for run in loaded]
    categories = [bin_index(np.abs(eta), ETA_EDGES), bin_index(folded_phi(phi), PHI_EDGES)]
    means, widths = paired_bootstrap(responses, categories, args.bootstrap, args.seed)
    differences = widths[:, 0] - widths[:, 1]
    upper = max(.5, math.ceil(max(r.max() for r in responses) * 200) / 2)
    histogram_edges = np.linspace(0, upper, 61)
    projections = {}
    for axis, (name, edges) in enumerate((("abs_eta", ETA_EDGES), ("folded_phi", PHI_EDGES))):
        bins = []
        for i in range(10):
            mask = categories[axis] == i
            entry = dict(low=float(edges[i]), high=float(edges[i + 1]), events=int(mask.sum()))
            for geometry, label in enumerate(("tiled", "continuous")):
                values = responses[geometry][mask]
                moment = summarize(values, energy[mask])
                for key, boot in (("fractional_width", widths), ("mean_response", means)):
                    moment[key + "_uncertainty"] = interval(boot[:, geometry, 10 * axis + i])
                hist, _ = np.histogram(values * 100, histogram_edges)
                if hist.sum() != mask.sum():
                    raise ValueError("Histogram dropped an event")
                moment["histogram_counts"] = hist.tolist()
                entry[label] = moment
            original = reference["projections"][name]["bins"][i]
            for key in ("mean_response", "sample_sd", "fractional_width", "events", "zero_events"):
                if not math.isclose(entry["tiled"][key], original[key], rel_tol=1e-12, abs_tol=1e-15):
                    raise ValueError(f"Changed published baseline moment: {name}:{i}:{key}")
            entry["width_difference"] = dict(
                value=nullable_difference(entry["tiled"]["fractional_width"], entry["continuous"]["fractional_width"]),
                **interval(differences[:, 10 * axis + i]))
            bins.append(entry)
        projections[name] = dict(edges=edges.tolist(), unit="rad" if axis else "dimensionless", bins=bins)
    finite = np.all(np.isfinite(widths))
    result = dict(status="PROTOTYPE", events=len(a),
        source_revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        producer_sha256=sha(__file__), baseline_summary_sha256=sha(args.reference),
        observable="sample SD(R)/mean(R), ddof=1, R=sum(raw silicon Edep)/true primary energy",
        interpretation="Matched-input counterfactual for continuous sector silicon; no quadrature attribution or intrinsic resolution claim",
        bootstrap=dict(replicates=args.bootstrap, seed=args.seed,
                       method="paired whole-event IDs, joint across both geometries and both projections",
                       interval="95% percentile"),
        histogram_edges_response_percent=histogram_edges.tolist(), projections=projections,
        width_covariance_order=[f"{geometry}:{name}:{i}" for geometry in ("tiled", "continuous")
                                for name in projections for i in range(10)],
        width_covariance=np.cov(widths.reshape(args.bootstrap, 40), rowvar=False).tolist() if finite else None,
        difference_covariance=np.cov(differences, rowvar=False).tolist() if finite else None,
        provenance={label: dict(readback={k: v for k, v in run[2].items() if k != "workers"},
                               execution={key: value for key, value in run[3].items() if key != "command"})
                    for label, run in zip(("tiled", "continuous"), loaded)})
    args.output.mkdir(parents=True, exist_ok=True)
    output = args.output / "comparison.json"
    if output.exists():
        raise ValueError("Choose fresh output; evidence is never overwritten")
    save(output, result)
    plot(result, args.output)
    print(f"Paired {len(a)} identical primary IDs; original 20 moments unchanged; wrote {output}")


def plot(result, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patheffects as pe
    plt.rcParams.update({"font.size":11, "axes.spines.top":False,
                         "axes.spines.right":False, "savefig.dpi":180,
                         "svg.hashsalt":"nodd-ecal10k-untiled"})
    styles = dict(tiled=dict(color="#cccc00", marker="o", ls="-", markeredgecolor="#545400"),
                  continuous=dict(color="#e6e680", marker="s", ls="--", markeredgecolor="#545400"))
    labels = dict(tiled="Tiled ECAL", continuous="Continuous sector silicon")
    def percent(value):
        return value * 100 if value is not None else np.nan

    def bounds(uncertainty):
        return uncertainty["ci95"] if uncertainty["ci95"] is not None else [np.nan, np.nan]

    def width_label(value):
        return f"{value * 100:.1f}%" if value is not None else "undefined"

    fig, axes = plt.subplots(2, 2, figsize=(13, 8), layout="constrained",
                             gridspec_kw=dict(height_ratios=[2.2, 1]))
    meanfig, meanaxes = plt.subplots(1, 2, figsize=(13, 4.8), layout="constrained")
    for column, (name, projection) in enumerate(result["projections"].items()):
        factor = 180 / math.pi if name == "folded_phi" else 1
        bins = projection["bins"]
        x = np.asarray([(b["low"] + b["high"]) / 2 * factor for b in bins])
        xlabel = r"$|\eta|$" if name == "abs_eta" else r"Signed sector-folded $\phi$ [deg]"
        for geometry in styles:
            for ax, key in ((axes[0, column], "fractional_width"), (meanaxes[column], "mean_response")):
                y = [percent(b[geometry][key]) for b in bins]
                ci = np.asarray([bounds(b[geometry][key + "_uncertainty"]) for b in bins]) * 100
                ax.vlines(x, ci[:, 0], ci[:, 1], color="#404030", lw=1)
                ax.plot(x, y, lw=2, ms=5, label=labels[geometry], **styles[geometry])
        for ax in (axes[0, column], meanaxes[column]):
            ax.set_ylim(bottom=0)
        delta = [percent(b["width_difference"]["value"]) for b in bins]
        ci = np.asarray([bounds(b["width_difference"]) for b in bins]) * 100
        axes[1, column].axhline(0, color="#777777", ls=":", lw=1)
        axes[1, column].vlines(x, ci[:, 0], ci[:, 1], color="#404030")
        axes[1, column].plot(x, delta, "o-", color="#cccc00", markeredgecolor="#545400", ms=4)
        axes[0, column].set_title("Pseudorapidity dependence" if not column else "Azimuth within one 22.5° sector")
        axes[0, column].set_ylabel(r"$\sigma(R)/\langle R\rangle$ [%]")
        axes[1, column].set_ylabel("Tiled − continuous\n[percentage points]")
        meanaxes[column].set_ylabel("Mean silicon response [%]")
        for ax in (*axes[:, column], meanaxes[column]):
            ax.set_xlim(projection["edges"][0] * factor, projection["edges"][-1] * factor)
            ax.set_xlabel(xlabel)
            ax.grid(alpha=.18)
            ax.set_axisbelow(True)
    axes[0, 0].legend(frameon=False, fontsize=10)
    meanaxes[0].legend(frameon=False, fontsize=10)
    fig.suptitle("nODD ECAL · tiled versus continuous silicon\n10,000 identical electron primaries · flat E = 10–80 GeV", fontsize=16)
    fig.supxlabel("R = silicon energy / true energy · All events retained · 95% paired whole-event bootstrap intervals\nRaw response width; full-sector control fills module, guard and service-margin losses together", fontsize=9)
    meanfig.suptitle("Mean-response control · same primaries and transport settings", fontsize=15)
    meanfig.supxlabel("All valid events, including zeros · 95% paired whole-event bootstrap intervals", fontsize=9)
    for extension in ("png", "pdf", "svg"):
        metadata = {"Date":None} if extension == "svg" else None
        fig.savefig(output / f"resolution-overlay.{extension}", metadata=metadata)
        meanfig.savefig(output / f"mean-response-overlay.{extension}", metadata=metadata)
    plt.close(fig)
    plt.close(meanfig)
    for name, projection in result["projections"].items():
        fig, axes = plt.subplots(5, 2, figsize=(12, 14), sharex=True, layout="constrained")
        for ax, entry in zip(axes.flat, projection["bins"]):
            for geometry, color, ls in (("tiled", "#cccc00", "-"), ("continuous", "#e6e680", "--")):
                moment = entry[geometry]
                line = ax.stairs(moment["histogram_counts"], result["histogram_edges_response_percent"],
                                 color=color, ls=ls, lw=1.6, label=labels[geometry])
                line.set_path_effects([pe.Stroke(linewidth=2.1, foreground="#777744"), pe.Normal()])
            factor = 180 / math.pi if name == "folded_phi" else 1
            ax.set_title(f"{entry['low'] * factor:.2f} to {entry['high'] * factor:.2f}"
                         + (" deg" if name == "folded_phi" else " |η|"), loc="left", fontsize=10)
            ax.text(.98, .95,
                    f"N = {entry['events']}\n"
                    f"width: {width_label(entry['tiled']['fractional_width'])} → {width_label(entry['continuous']['fractional_width'])}\n"
                    f"zeros: {entry['tiled']['zero_events']} → {entry['continuous']['zero_events']}",
                    transform=ax.transAxes, ha="right", va="top", fontsize=8,
                    bbox=dict(facecolor="white", alpha=.85, edgecolor="none"))
            ax.set_ylim(0, max(max(entry[g]["histogram_counts"]) for g in styles) * 1.3)
            ax.set_ylabel("Electrons / bin")
            ax.grid(alpha=.15)
        axes[0, 0].legend(fontsize=8, loc="upper left", frameon=False)
        for ax in axes[-1]:
            ax.set_xlabel("Raw silicon response R [%]")
        fig.suptitle("Tiled and continuous silicon · " + ("ten |η| populations" if name == "abs_eta" else "ten folded φ populations"), fontsize=15)
        fig.supxlabel("Common histogram bins retain every event · Widths use unbinned sample SD / mean · No fits or cuts", fontsize=9)
        for extension in ("png", "pdf", "svg"):
            metadata = {"Date":None} if extension == "svg" else None
            fig.savefig(output / f"response-distributions-{name}.{extension}", metadata=metadata)
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tiled", type=Path)
    parser.add_argument("--continuous", type=Path)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bootstrap", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=1335000)
    parser.add_argument("--replot", type=Path)
    args = parser.parse_args()
    if args.replot:
        args.output.mkdir(parents=True, exist_ok=True)
        plot(json.loads(args.replot.read_text()), args.output)
    else:
        if any(v is None for v in (args.tiled, args.continuous, args.reference)):
            parser.error("Comparison requires --tiled, --continuous and --reference")
        if args.bootstrap < 2:
            parser.error("Require at least two bootstrap replicas")
        compare(args)


if __name__ == "__main__":
    main()
