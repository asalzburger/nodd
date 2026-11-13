"""Matched-primary raw ECAL response statistics; event payloads remain local."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

import numpy as np

PERIOD = math.pi / 8
AXES = {
    "abs_eta": np.linspace(0, 3, 11),
    "siw_folded_phi": np.linspace(-PERIOD / 2, PERIOD / 2, 11),
    "energy": np.linspace(10, 80, 15),
    "full_phi": np.linspace(-math.pi, math.pi, 17),
    "signed_eta": np.linspace(-3, 3, 13),
    "broad_eta": np.array([0., 1.2, 1.5, 3.]),
}
LABELS = {"siw_original": "Si–W original", "siw_staggered": "Si–W staggered", "lar": "LAr"}
WORKSPACE = str(Path(__file__).resolve().parents[4])


def portable(value):
    if isinstance(value, str): return value.replace(WORKSPACE, "$WORKSPACE")
    if isinstance(value, list): return [portable(v) for v in value]
    if isinstance(value, dict): return {portable(k): portable(v) for k, v in value.items()}
    return value


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def load_run(run):
    run = Path(run)
    receipt = json.loads((run / "receipt.json").read_text())
    proof = json.loads((run / "readback.json").read_text())
    if receipt.get("exit_code") != 0 or receipt.get("disk_abort"):
        raise ValueError("Unsuccessful transport")
    if proof.get("status") != "PASS" or proof["receipt_sha256"] != sha(run / "receipt.json"):
        raise ValueError("Unbound readback receipt")
    if proof["event_summary_sha256"] != sha(run / "event-summary.jsonl"):
        raise ValueError("Changed event ledger")
    rows = sorted((json.loads(line) for line in (run / "event-summary.jsonl").read_text().splitlines()), key=lambda r: r["event"])
    ids = [r["event"] for r in rows]
    if len(rows) != receipt["events"] or ids != list(range(receipt["skip"], receipt["skip"] + receipt["events"])):
        raise ValueError("Incomplete or duplicate primary IDs")
    values = np.array([[r[k] for k in ("energy_GeV", "eta", "phi", "signal_GeV", "response")] for r in rows])
    if not np.all(np.isfinite(values)) or np.any(values[:, 0] <= 0) or np.any(values[:, 3:] < 0):
        raise ValueError("Invalid primary or response")
    if not np.allclose(values[:, 4], values[:, 3] / values[:, 0], rtol=2e-14, atol=0):
        raise ValueError("Response differs from deposited energy / primary energy")
    sample = proof.get("sample", {})
    sample_summary = {k: sample[k] for k in ("source_revision", "source_primary_revision", "geometry_scope", "original_geometry_revision", "events", "input_seed", "distributions", "electron_mass_GeV", "input_sha256", "truth_sha256", "hashes", "source_baseline_sha256", "source_compact_sha256", "source_primary_manifest_sha256", "collections") if k in sample}
    return rows, values, portable({"receipt_sha256": sha(run / "receipt.json"), "readback_sha256": sha(run / "readback.json"),
                          "ledger_sha256": proof["event_summary_sha256"], "root_sha256": proof["root_sha256"],
                          "transport": receipt, "input": sample_summary})


def index(values, edges):
    if np.any(values < edges[0] - 1e-12) or np.any(values > edges[-1] + 1e-12):
        raise ValueError("Primary outside declared bins")
    return np.clip(np.searchsorted(edges, values, side="right") - 1, 0, len(edges) - 2)


def validate_contract(run, name):
    """Reject mislabeled samples and incompatible executed transport policies."""
    run = Path(run)
    receipt = json.loads((run / "receipt.json").read_text())
    proof = json.loads((run / "readback.json").read_text())
    lar = name == "lar"
    collections = {"LArBarrelHits", "LArEndcapHits"} if lar else {"BARRELHits", "EDGEHits"}
    if set(proof.get("cells_by_collection", {})) != collections:
        raise ValueError("Wrong detector collections: " + name)
    for key, value in dict(events=10000, skip=0, threads=12, seed=133812341).items():
        if receipt.get(key) != value:
            raise ValueError("Incompatible production policy: " + key)
    command = receipt["command"]
    for flag, value in (("--physics.list", "FTFP_BERT"), ("--physics.rangecut", "0.7")):
        if flag not in command or command[command.index(flag)+1] != value:
            raise ValueError("Incompatible physics command: " + flag)
    if "--random.enableEventSeed" not in command or (lar and receipt.get("max_step_mm") != 5):
        raise ValueError("Missing event seeding or LAr step policy")
    workers = proof["workers"]
    if len(workers) != 12 or {w["thread_id"] for w in workers} != set(range(12)) or sum(w["events"] for w in workers) != 10000:
        raise ValueError("Incomplete worker population")
    hashes = {}
    for worker in workers:
        path = run / "audit" / f'worker-{worker["thread_id"]}.json'
        if json.loads(path.read_text()) != worker:
            raise ValueError("Changed worker audit")
        hashes[path.name] = sha(path)
        if (worker["status"] != "complete" or worker["events"] <= 0 or
                worker["maximum_abs_magnetic_field_tesla"] != 0 or
                worker["rng_engine"] != "MixMaxRng" or worker["begin_run_rng_seed"] != 133812341):
            raise ValueError("Incompatible worker field/RNG/status")
        if not worker["region_cuts"] or any(r["mm"] != [.7]*4 for r in worker["region_cuts"]):
            raise ValueError("Incompatible native cuts")
        if any("StepLimiter" not in worker["processes"][p] for p in ("e-", "e+")):
            raise ValueError("Missing native StepLimiter")
        sensitive = worker["sensitive_lar" if lar else "sensitive_si"]
        if set(sensitive) != ({"LArBarrel", "LArEndcaps"} if lar else {"BARREL", "EDGE"}):
            raise ValueError("Wrong native sensitive detectors")
        for item in sensitive.values():
            volumes = item["volumes"] if lar else [item]
            if not volumes or any(v["max_step_mm"] is None or not 0 < v["max_step_mm"] <= 5 or v["Birks_mm_per_MeV"] != 0 for v in volumes):
                raise ValueError("Incompatible active step/Birks policy")
    if sha(run / "events.root") != proof["root_sha256"]:
        raise ValueError("Changed raw ROOT artifact")
    return dict(status="PASS", worker_audit_sha256=hashes, root_rehashed=True)


def moments(values):
    if len(values) < 2 or np.mean(values) <= 0:
        raise ValueError("Undefined sample width")
    mean = float(np.mean(values))
    sd = float(np.std(values, ddof=1))
    return {"events": len(values), "mean_response": mean, "sample_sd": sd,
            "fractional_width": sd / mean, "zero_events": int(np.count_nonzero(values == 0)),
            "below_half_mean_fraction": float(np.mean(values < .5 * mean)),
            "central_quantile_width": float((np.quantile(values, .84)-np.quantile(values, .16))/(2*np.median(values))) if np.median(values)>0 else None,
            "quantiles": dict(zip(("q01", "q16", "q50", "q84", "q99"), map(float, np.quantile(values, [.01, .16, .5, .84, .99]))))}


def binned_moments(response, categories, weights, bins):
    counts = np.bincount(categories, weights=weights, minlength=bins)
    sums = np.bincount(categories, weights=weights * response, minlength=bins)
    squares = np.bincount(categories, weights=weights * response ** 2, minlength=bins)
    means = np.divide(sums, counts, out=np.full(bins, np.nan), where=counts > 0)
    variance = np.divide(squares - sums * means, counts - 1, out=np.full(bins, np.nan), where=counts > 1)
    widths = np.divide(np.sqrt(np.maximum(variance, 0)), means, out=np.full(bins, np.nan), where=means > 0)
    return means, widths


def interval(values):
    if not np.all(np.isfinite(values)):
        return {"ci95": None, "undefined": int(np.count_nonzero(~np.isfinite(values)))}
    return {"ci95": np.quantile(values, [.025, .975]).tolist(), "undefined": 0}


def analyze(args):
    paths = {"siw_original": args.siw_original, "siw_staggered": args.siw_staggered, "lar": args.lar}
    loaded = {name: load_run(path) for name, path in paths.items()}
    contracts = {name: validate_contract(path, name) for name, path in paths.items()}
    base = loaded["lar"][1]
    n = len(base)
    if n != 10000:
        raise ValueError("This protocol requires exactly 10,000 primaries")
    for name, (_, array, _) in loaded.items():
        if array.shape != base.shape or not np.allclose(array[:, :3], base[:, :3], rtol=0, atol=1e-9):
            raise ValueError("Unmatched primary illumination: " + name)
        if loaded[name][2]["input"].get("input_sha256") != loaded["lar"][2]["input"].get("input_sha256") or loaded[name][2]["input"].get("truth_sha256") != loaded["lar"][2]["input"].get("truth_sha256"):
            raise ValueError("Different matched-primary manifest hashes")
    categories = {"global": np.zeros(n, dtype=int)}
    raw_coords = {"abs_eta": np.abs(base[:, 1]), "broad_eta": np.abs(base[:, 1]), "signed_eta": base[:, 1], "energy": base[:, 0],
                  "full_phi": base[:, 2], "siw_folded_phi": (base[:, 2] + PERIOD / 2) % PERIOD - PERIOD / 2}
    categories.update({name: index(raw_coords[name], edges) for name, edges in AXES.items()})
    counts = {name: 1 if name == "global" else len(AXES[name]) - 1 for name in categories}
    responses = {name: value[1][:, 4] for name, value in loaded.items()}
    boot = {name: {axis: np.empty((args.bootstrap, counts[axis], 2)) for axis in categories} for name in loaded}
    rng = np.random.default_rng(args.seed)
    for b in range(args.bootstrap):
        weights = np.bincount(rng.integers(n, size=n), minlength=n)
        for name, response in responses.items():
            for axis, cat in categories.items():
                mean, width = binned_moments(response, cat, weights, counts[axis])
                boot[name][axis][b, :, 0] = mean
                boot[name][axis][b, :, 1] = width
    models = {}
    for name, response in responses.items():
        entry = {"label": LABELS[name], "evidence": loaded[name][2], "comparison_contract": contracts[name], "global": moments(response), "projections": {}}
        for axis, cat in categories.items():
            rows = [moments(response[cat == i]) for i in range(counts[axis])]
            for i, row in enumerate(rows):
                for j, statistic in enumerate(("mean_response", "fractional_width")):
                    row[statistic + "_bootstrap"] = interval(boot[name][axis][:, i, j])
                row["response_uniformity"] = row["mean_response"] / float(response.mean())
                row["response_uniformity_bootstrap"] = interval(boot[name][axis][:, i, 0] / boot[name]["global"][:, 0, 0])
            if axis == "global":
                entry["global"] = rows[0]
            else:
                entry["projections"][axis] = {"edges": AXES[axis].tolist(), "bins": rows,
                                              "unit": "GeV" if axis == "energy" else "rad" if "phi" in axis else "dimensionless"}
        # Histograms use each detector's inclusive mean solely for display.
        edges = np.linspace(0, 3, 121)
        scaled = response / response.mean()
        hist, _ = np.histogram(scaled, edges)
        entry["normalized_response_histogram"] = {"edges": edges.tolist(), "counts": hist.tolist(), "events": n,
            "underflow": int(np.count_nonzero(scaled < edges[0])), "overflow": int(np.count_nonzero(scaled > edges[-1])),
            "normalization": "R / inclusive sample mean(R); diagnostic display, no fitted calibration"}
        for axis in ("abs_eta", "siw_folded_phi"):
            for i, row in enumerate(entry["projections"][axis]["bins"]):
                selected = scaled[categories[axis] == i]
                row["normalized_response_histogram"] = {"edges": edges.tolist(), "counts": np.histogram(selected, edges)[0].tolist(),
                    "events": len(selected), "underflow": int(np.count_nonzero(selected < edges[0])),
                    "overflow": int(np.count_nonzero(selected > edges[-1]))}
        models[name] = entry
    contrasts = {}
    for comparator in ("siw_original", "siw_staggered"):
        contrasts[comparator + "_minus_lar"] = {}
        for axis in categories:
            values = boot[comparator][axis][:, :, 1] - boot["lar"][axis][:, :, 1]
            records = []
            for i in range(counts[axis]):
                a = models[comparator]["global"] if axis == "global" else models[comparator]["projections"][axis]["bins"][i]
                c = models["lar"]["global"] if axis == "global" else models["lar"]["projections"][axis]["bins"][i]
                records.append({"difference": a["fractional_width"] - c["fractional_width"], **interval(values[:, i])})
            contrasts[comparator + "_minus_lar"][axis] = records
    order = []
    columns = []
    for name in models:
        for axis in ("global", "abs_eta", "siw_folded_phi"):
            for i in range(counts[axis]):
                order.append(f"{name}:{axis}:{i}")
                columns.append(boot[name][axis][:, i, 1])
    matrix = np.array(columns)
    if not np.all(np.isfinite(matrix)):
        raise ValueError("Undefined principal bootstrap covariance")
    result = {"status": "PROTOTYPE", "events": n, "observable": "sample SD(R)/mean(R); R=active ECAL deposited energy / primary total energy",
        "interpretation": "Spectrum-averaged raw response including zeros and geometry/material/leakage effects; no intrinsic-resolution or digitization claim",
        "source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "analysis_sha256": sha(__file__), "protocol_sha256": sha(args.protocol),
        "bootstrap": {"replicates": args.bootstrap, "seed": args.seed, "resampling": "shared whole-primary-event multiplicities across all detectors and projections", "intervals": "pointwise 95% percentile"},
        "models": models, "width_contrasts": contrasts, "width_covariance_order": order,
        "width_covariance": np.cov(matrix, ddof=1).tolist()}
    args.output.mkdir(parents=True, exist_ok=False)
    write(args.output / "summary.json", result)
    print(json.dumps({name: model["global"] for name, model in models.items()}, indent=2))


def plot(args):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    result = json.loads(args.summary.read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "svg.hashsalt": "nodd-lar10k-v1"})
    styles = {"siw_original": dict(color="#e5e580", ls=":", marker="s"),
              "siw_staggered": dict(color="#cccc00", ls="--", marker="o"),
              "lar": dict(color="#cccc00", ls="-", marker="^", markeredgecolor="#222222")}
    def export(fig, name):
        fig.text(.02, .01, "PROTOTYPE · same 10,000 origin electrons · E=10–80 GeV, η=−3…3 · B=0 · raw deposits; no digitization", fontsize=8)
        fig.tight_layout(rect=(0, .04, 1, .94))
        for ext in ("png", "pdf", "svg"):
            fig.savefig(args.output / f"{name}.{ext}", dpi=160, metadata={"Date": None} if ext in ("pdf", "svg") else {})
        plt.close(fig)
    def projection(ax, axis, quantity, normalized=False):
        for name, model in result["models"].items():
            proj = model["projections"][axis]
            edges = np.array(proj["edges"])
            x = (edges[:-1] + edges[1:]) / 2
            field = "response_uniformity" if normalized else quantity
            y = np.array([row[field] for row in proj["bins"]])
            ci = np.array([row[field + "_bootstrap"]["ci95"] for row in proj["bins"]])
            scale = .01 if quantity == "fractional_width" else 1.
            ax.errorbar(x, y / scale, yerr=np.maximum(np.array([y - ci[:, 0], ci[:, 1] - y]), 0) / scale,
                        label=model["label"], capsize=2, markersize=4, **styles[name])
        ax.grid(alpha=.22)
        ax.set_xlabel({"abs_eta": "|η|", "siw_folded_phi": "φ folded with Si–W sector period [rad]", "energy": "Primary total energy [GeV]", "full_phi": "φ [rad]", "signed_eta": "η"}[axis])
        ax.set_ylabel("SD(R) / mean(R) [%]" if quantity == "fractional_width" else "Mean R / inclusive mean R" if normalized else "Mean active deposited fraction")
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.5))
    for ax, axis in zip(axs, ("abs_eta", "siw_folded_phi")): projection(ax, axis, "fractional_width")
    axs[0].legend(); fig.suptitle("Raw ECAL response width · matched primary illumination")
    export(fig, "angular-comparison")
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.5))
    for ax, axis in zip(axs, ("abs_eta", "siw_folded_phi")): projection(ax, axis, "mean_response", normalized=True)
    axs[0].legend(); fig.suptitle("Directional response uniformity · each detector normalized by its own inclusive mean")
    export(fig, "angular-means")
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.5))
    projection(axs[0], "energy", "fractional_width"); projection(axs[1], "energy", "mean_response", normalized=True)
    axs[0].legend(); fig.suptitle("Energy-slice controls · spectrum and directions remain mixed within each slice")
    export(fig, "energy-controls")
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    for col, axis in enumerate(("signed_eta", "full_phi")):
        projection(axs[0, col], axis, "fractional_width"); projection(axs[1, col], axis, "mean_response", normalized=True)
    axs[0, 0].legend(); fig.suptitle("Signed direction and absolute-azimuth controls")
    export(fig, "direction-controls")
    fig, ax = plt.subplots(figsize=(9, 5))
    for name, model in result["models"].items():
        hist = model["normalized_response_histogram"]
        style = {k: v for k, v in styles[name].items() if k in ("color", "ls")}
        ax.stairs(np.array(hist["counts"]) / hist["events"], hist["edges"], label=f'{model["label"]}: width {100*model["global"]["fractional_width"]:.2f}%, zeros {model["global"]["zero_events"]}', **style)
    ax.set(xlabel="R / inclusive sample mean(R)", ylabel="Fraction of all generated events / bin", yscale="log", ylim=(5e-5, .3))
    ax.legend(); ax.grid(alpha=.2); fig.suptitle("Raw response distributions · global scaling is a display normalization")
    export(fig, "response-distributions")
    for axis in ("abs_eta", "siw_folded_phi"):
        fig, axs = plt.subplots(2, 5, figsize=(16, 7), sharex=True, sharey=True)
        for i, ax in enumerate(axs.flat):
            for name, model in result["models"].items():
                proj = model["projections"][axis]
                hist = proj["bins"][i]["normalized_response_histogram"]
                style = {k: v for k, v in styles[name].items() if k in ("color", "ls")}
                ax.stairs(np.array(hist["counts"])/hist["events"], hist["edges"], label=model["label"], **style)
            ax.set(title=f'{proj["edges"][i]:.3f}…{proj["edges"][i+1]:.3f}', yscale="log", ylim=(3e-4, .5))
            ax.grid(alpha=.2)
        axs.flat[0].legend(fontsize=8)
        fig.supxlabel("R / detector's inclusive sample mean(R)")
        fig.supylabel("Fraction of all events in angular bin / response bin")
        fig.suptitle("Response distributions in " + ("|η| bins" if axis == "abs_eta" else "Si–W sector-phase bins [rad]"))
        export(fig, "distributions-" + axis)
    write(args.output / "render.json", {"summary_sha256": sha(args.summary), "plotter_sha256": sha(__file__),
        "figures": {p.name: sha(p) for p in sorted(args.output.iterdir()) if p.suffix in (".png", ".pdf", ".svg")}})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="stage", required=True)
    p = sub.add_parser("analyze")
    for name in ("siw-original", "siw-staggered", "lar"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--protocol", type=Path, default=Path("docs/validation/lar10k/protocol.md"))
    p.add_argument("--bootstrap", type=int, default=1000); p.add_argument("--seed", type=int, default=13001000)
    p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("plot"); p.add_argument("--summary", type=Path, required=True); p.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    globals()[args.stage](args)


if __name__ == "__main__":
    main()
