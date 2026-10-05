#!/usr/bin/env python3
"""Export a fresh, compact, reviewable DES-009 evidence bundle and figures."""
import argparse
import copy
import csv
import gzip
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection


def read(path):
    return json.loads(Path(path).read_text())


def write_csv(path, rows):
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with Path(path).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def flattened(stats):
    result = {}
    for key, value in stats.items():
        if isinstance(value, dict):
            result.update({key+"_"+k: v for k, v in value.items() if k != "histogram"})
        elif isinstance(value, (str, int, float)) or value is None:
            result[key] = value
    return result


def pct(value):
    return "n/a" if value is None else f"{100*value:.2f}"


def trajectory_label(config):
    momentum = "pT" if config["momentum_convention"] == "pt" else "p"
    return f"{momentum} = {config['momentum_GeV']:g} GeV, Bz = {config['field_T']:g} T"


def variant_label(variant, multiline=False):
    names = {"review_default": "default", "review_pixel_z": "pixel z staggering",
             "review_short_tilt": "short-strip phi tilt",
             "review_pixel_z_short_tilt": "pixel z + short-strip phi tilt"}
    label = names.get(variant, variant.replace("_", " "))
    if multiline:
        import textwrap
        return "\n".join(textwrap.wrap(label, width=16, break_long_words=False))
    return label


def primary_cases(cases):
    """Use the cases actually present, including one-candidate review runs."""
    return [case for case in cases if case["cohort"] == "main"]


def visual_cases(bundle):
    cases = primary_cases([result["case"] for result in bundle["cases"]])
    if any(case["variant"].startswith("review_") for case in cases):
        return cases
    cleared = [case for case in cases if case["variant"] in
               ("hybrid_clearance", "staggered_clearance")]
    return cleared or cases


def panel_grid(count, width=6., height=3.5):
    columns = min(2, max(1, count))
    rows = max(1, (count + columns - 1) // columns)
    fig, axes = plt.subplots(rows, columns, figsize=(width*columns, height*rows),
                             squeeze=False, constrained_layout=True)
    for ax in axes.flat[count:]:
        ax.set_visible(False)
    return fig, list(axes.flat[:count])


def export(run, output):
    run, output = Path(run), Path(output)
    output.mkdir(parents=True, exist_ok=False)
    meta = read(run/"run.json")
    bundle = dict(run=meta, config=read(run/"config.json"), sensor_models=read(run/"sensor_models.json"),
                  definitions=dict(sensor_area="Gross physical sensor-face area, each sensor once; conditional pixel outline",
                                   active_area="Sum of readout islands, excluding seams and guards",
                                   station="Distinct station_id; long-strip requires a same-module complete pair",
                                   missing="Missing ideal eligible station IDs / total ideal eligible station IDs",
                                   all_hit="Fraction of eligible tracks with no missing ideal station ID",
                                   measure="Declared deterministic eta/phi/vertex grid plus seeded uniform off-grid sample; not event weights"), cases=[])
    bundle["export_code_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    coverage, layers, profiles, phi_rows, cohort_rows, geometry_rows = [], [], [], [], [], []
    for case in meta["cases"]:
        path = run/case["id"]
        result = read(path/"summary.json")
        # Model content is retained once; overrides and per-case hash identify changes.
        result["geometry"].pop("models", None)
        for scope, item in result["geometry"]["summary"].items():
            geometry_rows.append(dict(case=case["id"], scope=scope, **item))
        for mode, stats in result["modes"].items():
            groups = {"total": stats["total"], **stats["per_subdetector"], **stats["per_subdetector_region"]}
            for scope, values in groups.items():
                coverage.append(dict(case=case["id"], cohort=case["cohort"], mode=mode, scope=scope,
                                     **flattened(values)))
            for layer, values in stats.pop("per_layer").items():
                layers.append(dict(case=case["id"], mode=mode, layer=layer, **values))
            for values in stats.pop("eta_profiles"):
                common = dict(case=case["id"], mode=mode, eta_min=values["eta_min"], eta_max=values["eta_max"])
                for scope, group in {"total": values, **values["per_subdetector"]}.items():
                    clean = {k: v for k, v in group.items() if k not in ("per_subdetector", "eta_min", "eta_max")}
                    profiles.append(dict(**common, scope=scope, **flattened(clean)))
            for values in stats.pop("phi_profiles"):
                phi_rows.append(dict(case=case["id"], mode=mode, **flattened(values)))
        from intersections import _summarize_columns
        with gzip.open(path/"track_metrics.json.gz", "rt") as stream:
            raw = json.load(stream)
        for mode, columns in raw["modes"].items():
            for cohort in sorted({t["cohort"] for t in raw["directions"]}):
                selection = np.array([t["cohort"] == cohort for t in raw["directions"]])
                groups = {"total": {k: v for k, v in columns.items() if isinstance(v, list)},
                          **columns["per_subdetector"], **columns["per_subdetector_region"]}
                for scope, group in groups.items():
                    cohort_rows.append(dict(case=case["id"], mode=mode, cohort=cohort, scope=scope,
                                            **flattened(_summarize_columns(group, selection))))
        native = path/meta.get("native_audit_report", "acts_validation.json")
        result["native_acts"] = read(native) if native.exists() else {"passed": False, "status": "NOT RUN"}
        result["raw_track_metrics_sha256"] = hashlib.sha256((path/"track_metrics.json.gz").read_bytes()).hexdigest()
        bundle["cases"].append(result)
    for name, rows in (("coverage", coverage), ("layers", layers), ("eta", profiles),
                       ("phi", phi_rows), ("cohorts", cohort_rows), ("silicon", geometry_rows)):
        write_csv(output/f"{name}.csv", rows)
    (output/"summary.json").write_text(json.dumps(bundle, indent=2, allow_nan=False)+"\n")
    plot_profiles(profiles, meta, bundle["config"], output)
    plot_tradeoff(bundle, output)
    plot_maps(run, bundle, output)
    plot_layouts(run, bundle, output)
    markdown(bundle, output)
    print(f"Exported {len(bundle['cases'])} cases to {output}")


def plot_profiles(rows, meta, config, output):
    cases = primary_cases(meta["cases"])
    candidates = list(dict.fromkeys(case["candidate"] for case in cases))
    if not candidates:
        return
    fig, axes = plt.subplots(2, len(candidates), figsize=(6*len(candidates), 8),
                             squeeze=False, constrained_layout=True)
    for column, candidate in enumerate(candidates):
        for case in cases:
            if case["candidate"] != candidate or case["cohort"] != "main":
                continue
            values = [r for r in rows if r["case"] == case["id"] and r["mode"] == "positive" and r["scope"] == "total"]
            eta = [(r["eta_min"]+r["eta_max"])/2 for r in values]
            style = "-" if (case["variant"].endswith("clearance") or case["variant"].startswith("review_")) else "--"
            label = variant_label(case["variant"])
            axes[0, column].plot(eta, [r["sensor_hits_mean"] for r in values], style, label=label)
            axes[1, column].plot(eta, [100*r["missing_ideal_station_fraction"]
                                      if r["missing_ideal_station_fraction"] is not None else np.nan
                                      for r in values], style, label=label)
        axes[0, column].set_title(candidate+": "+trajectory_label(config)+", + charge")
        axes[0, column].set_ylabel("Mean physical sensor hits")
        axes[1, column].set_ylabel("Missing eligible stations [%]")
        axes[1, column].set_xlabel("eta")
        for ax in axes[:, column]:
            ax.grid(alpha=.25)
        axes[1, column].legend(fontsize=8)
    fig.suptitle("PROTOTYPE: finite active modules; sampled luminous region")
    fig.savefig(output/"eta-coverage.png", dpi=160)
    fig.savefig(output/"eta-coverage.pdf")
    plt.close(fig)


def plot_tradeoff(bundle, output):
    candidates = list(dict.fromkeys(case["candidate"] for case in
                                    primary_cases([r["case"] for r in bundle["cases"]])))
    if not candidates:
        return
    fig, axes = plt.subplots(1, len(candidates), figsize=(6*len(candidates), 5),
                             squeeze=False, constrained_layout=True)
    offsets = {"flat": (8, 8), "hybrid": (-48, 24),
               "hybrid_clearance": (12, -30), "staggered": (-70, -23),
               "tilted": (10, -30), "staggered_clearance": (-22, 25),
               "review_default": (12, 15), "review_pixel_z": (-75, -28),
               "review_short_tilt": (12, -35), "review_pixel_z_short_tilt": (12, 20)}
    for ax, candidate in zip(axes.flat, candidates):
        for result in bundle["cases"]:
            case = result["case"]
            if case["candidate"] != candidate or case["cohort"] != "main":
                continue
            area = result["geometry"]["summary"]["total"]["sensor_area_m2"]
            miss = max(result["modes"][m]["total"]["missing_ideal_station_fraction"] for m in ("positive", "negative"))
            clashes = result["body_diagnostics"]["overlapping_body_pairs"]
            ax.scatter(area, 100*miss, marker="x" if clashes else "o", s=65,
                       color="tab:red" if clashes else "tab:blue")
            ax.annotate(variant_label(case["variant"], multiline=True), (area, 100*miss),
                        xytext=offsets.get(case["variant"], (8, 8)), textcoords="offset points",
                        fontsize=8, arrowprops={"arrowstyle": "-", "color": ".55", "lw": .6})
        ax.set(title=candidate, xlabel="Gross sensor surface [m²]", ylabel="Missing eligible stations [%]")
        ax.grid(alpha=.25)
        ax.margins(.22)
    fig.suptitle(trajectory_label(bundle["config"])+"; worse charge sign\n"
                 "x = trial-body clashes, circle = none detected")
    fig.savefig(output/"support-tradeoff.png", dpi=160)
    fig.savefig(output/"support-tradeoff.pdf")
    plt.close(fig)


def plot_maps(run, bundle, output):
    cases = visual_cases(bundle)
    if not cases:
        return
    fig, axes = panel_grid(len(cases))
    im = None
    for ax, case in zip(axes, cases):
        path = run/case["id"]/"track_metrics.json.gz"
        with gzip.open(path, "rt") as stream:
            raw = json.load(stream)
        eta = np.array([t["eta"] for t in raw["directions"]])
        phi = np.mod(np.array([t["phi"] for t in raw["directions"]]), 2*np.pi)
        missing = np.array(raw["modes"]["positive"]["missing_stations"])
        ideal = np.array(raw["modes"]["positive"]["ideal_stations"])
        maximum = bundle["config"]["eta_max"]
        bins = [np.linspace(-maximum, maximum, 33), np.linspace(0, 2*np.pi, 33)]
        a = np.histogram2d(eta, phi, bins=bins, weights=missing)[0]
        b = np.histogram2d(eta, phi, bins=bins, weights=ideal)[0]
        values = np.divide(100*a, b, out=np.full_like(a, np.nan), where=b > 0)
        im = ax.pcolormesh(bins[0], bins[1], values.T, vmin=0, vmax=35, cmap="magma")
        ax.set(title=f"{case['candidate']}: {variant_label(case['variant'])}", xlabel="eta", ylabel="phi [rad]")
    if im is not None:
        fig.colorbar(im, ax=axes, label="Missing eligible stations [%]", extend="max")
    fig.suptitle("Sampled gaps: all luminous vertices; "+trajectory_label(bundle["config"])+", + charge")
    fig.savefig(output/"coverage-map.png", dpi=160)
    plt.close(fig)


def plot_layouts(run, bundle, output):
    from geometry import generate_layout
    cases = visual_cases(bundle)
    if not cases:
        return
    fig, axes = panel_grid(len(cases), width=7.)
    colors = {"pixel": "tab:blue", "short_strip": "tab:orange", "long_strip": "tab:green"}
    for panel, (ax, case) in enumerate(zip(axes, cases)):
        model = copy.deepcopy(bundle["sensor_models"])
        model["pixel"].update(case.get("pixel_override", {}))
        layout = generate_layout(case["candidate"], case["variant"], case["pixel_family"], models=model,
                                 layouts_path=run/"layouts.json")
        for subsystem, color in colors.items():
            polygons = []
            for p in layout["modules"]:
                if p["subsystem"] != subsystem:
                    continue
                c = np.asarray(p["center_mm"])
                if abs(np.arctan2(c[1], c[0])) > .12:
                    continue
                u, v = np.asarray(p["u"])*p["half_u_mm"], np.asarray(p["v"])*p["half_v_mm"]
                corners = [c+a*u+b*v for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
                polygons.append([(q[2], np.hypot(q[0], q[1])) for q in corners])
            ax.add_collection(PolyCollection(polygons, facecolors=color, edgecolors=color,
                                            linewidths=.25, alpha=.7, label=subsystem))
        host = layout["metadata"]["host"]
        ax.set(xlim=(-1000*host["abs_z_max_m"]-50, 1000*host["abs_z_max_m"]+50),
               ylim=(0, 1000*host["r_max_m"]+30), xlabel="z [mm]", ylabel="r [mm]",
               title=f"{case['candidate']}: {variant_label(case['variant'])}")
        ax.grid(alpha=.2)
        if panel == 0:
            ax.legend(fontsize=8)
    fig.suptitle("Finite active rectangles projected into r–z; |module-centre phi| < 0.12 rad")
    fig.savefig(output/"module-layouts.png", dpi=160)
    fig.savefig(output/"module-layouts.pdf")
    plt.close(fig)


def markdown(bundle, output):
    main = [r for r in bundle["cases"] if r["case"]["cohort"] == "main"]
    lines = ["# DES-009 numerical results", "", "**PROTOTYPE.** Draft inputs; finite sampling is not a proof of continuous hermeticity.", "",
             "`coverage.csv` contains all trajectory/subdetector/region summaries; `layers.csv` retains every ideal-layer denominator and missed count. `silicon.csv` separates gross sensor surface and active readout area. `eta.csv` retains directional profiles. Exact configuration, source hashes, distributions and native ACTS audit are in `summary.json`.", "",
             "## Populations and trial occupied bodies", "",
             "| Layout | Modules | Sensors | Gross / active m² | Body clashes | Host overruns |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for r in main:
        g = r["geometry"]["summary"]["total"]
        lines.append(f"| {r['case']['id']} | {g['modules']} | {g['sensors']} | {g['sensor_area_m2']:.2f} / {g['active_area_m2']:.2f} | {r['body_diagnostics']['overlapping_body_pairs']} | {r['geometry']['host_diagnostics']['host_overflow_modules']} |")
    lines += ["", "Body clashes reject the particular trial support envelope; absence of clashes is not full support/services validation.", "",
              "## Total reachable hits and sampled coverage", "",
              "Modes: straight = no field; positive/negative = "+trajectory_label(bundle["config"])+", charge ±1. Means include every sampled direction. Station counts require a complete same-module pair for long strips.", "",
              "| Layout | Mode | Sensor hits min / mean | Stations min / mean | Missing eligible stations % | Tracks with all eligible stations % |",
              "| --- | --- | ---: | ---: | ---: | ---: |"]
    for r in main:
        for mode, s in r["modes"].items():
            s = s["total"]
            lines.append(f"| {r['case']['id']} | {mode} | {s['sensor_hits']['min']} / {s['sensor_hits']['mean']:.2f} | {s['stations']['min']} / {s['stations']['mean']:.2f} | {pct(s['missing_ideal_station_fraction'])} | {pct(s['fraction_all_ideal_stations_hit'])} |")
    lines += ["", "## Per subdetector", "",
              "Each triplet is straight / positive / negative. Areas count both long-strip faces and count a pixel sensor only once across its active islands.", "",
              "| Layout | Subdetector | Gross m² | Mean sensor hits | Missing eligible stations % |",
              "| --- | --- | ---: | ---: | ---: |"]
    detailed = [r for r in main if r["case"]["variant"].endswith("clearance")
                or r["case"]["variant"].startswith("review_")] or main
    for r in detailed:
        for sub in ("pixel", "short_strip", "long_strip"):
            stats = [r["modes"][m]["per_subdetector"][sub] for m in ("straight", "positive", "negative")]
            hits = " / ".join(f"{s['sensor_hits']['mean']:.2f}" for s in stats)
            miss = " / ".join(pct(s["missing_ideal_station_fraction"]) for s in stats)
            lines.append(f"| {r['case']['id']} | {sub} | {r['geometry']['summary'][sub]['sensor_area_m2']:.2f} | {hits} | {miss} |")
    controls = [r for r in bundle["cases"] if r["case"]["cohort"] == "control"]
    if controls:
        lines += ["", "## Pixel-family and outline controls", "",
                  "All control rows use the same smaller sample, including a mixed baseline; do not subtract them from the denser main sample. Strip geometry is unchanged. The body-clash column refers to pixels only; these controls retain the original uncorrected stagger levels.", "",
                  "| Control | Pixel modules | Pixel gross / active m² | Pixel station loss %, straight / + / − | Pixel body clashes |",
                  "| --- | ---: | ---: | ---: | ---: |"]
    for r in controls:
        g = r["geometry"]["summary"]["pixel"]
        misses = " / ".join(pct(r["modes"][m]["per_subdetector"]["pixel"]["missing_ideal_station_fraction"]) for m in ("straight", "positive", "negative"))
        collisions = r["body_diagnostics"]["by_subsystem_pair"].get("pixel/pixel", 0)
        lines.append(f"| {r['case']['id']} | {g['modules']} | {g['sensor_area_m2']:.2f} / {g['active_area_m2']:.2f} | {misses} | {collisions} |")
    audits = [r["native_acts"] for r in bundle["cases"]]
    lines += ["", "## Native ACTS audit", "", f"Passing case audits: {sum(a.get('passed', False) for a in audits)} / {len(audits)}. See exact track lists, actual runtime provenance and mismatches in summary.json; NOT RUN is not a pass."]
    for title, filename in (("Finite module layouts", "module-layouts.png"),
                            ("Hit and coverage profiles", "eta-coverage.png"),
                            ("Support tradeoff", "support-tradeoff.png"),
                            ("Coverage map", "coverage-map.png")):
        if (output/filename).exists():
            lines += ["", f"![{title}]({filename})"]
    lines.append("")
    (output/"results.md").write_text("\n".join(lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    export(args.run, args.output)
