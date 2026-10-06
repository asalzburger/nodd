#!/usr/bin/env python3
"""Generate TDR pixel tables/figures from frozen geometry and native evidence."""

import argparse
from collections import Counter
import hashlib
import gzip
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BARREL_LAYOUT = "docs/validation/DES-013-pixel-z/data/packed-200um/layout.json.gz"
SOURCES = [
    "detector/config/pixel-detector-trimmed.json",
    "detector/config/pixel-barrel.json",
    "tools/pixel_disc_optimization/radial-inputs.json",
    "tools/pixel_disc_support_variants/inputs.json",
    "tools/pixel_endcap_support/inputs.json",
    "docs/validation/DES-017/four-single-two-quad-layout.json",
    "docs/validation/DES-018/screening.json",
    "docs/validation/DES-019/summary.json",
    "docs/validation/DES-019/native.json",
    "docs/validation/DES-019/workflow.json",
    BARREL_LAYOUT,
    "docs/design/DES-019-trimmed-mixed-pixel-dd4hep.md",
]


def read(path):
    return json.loads((ROOT / path).read_text())


def source_hashes():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES}


def table():
    discs = read(SOURCES[6])["variants"]["four-single-two-quad"]["positive_discs"]
    rows = read(SOURCES[5])["rings"]
    result = []
    for i, d in enumerate(discs, 1):
        kept = [r for r in rows if r["row"] in d["retained_rows"]]
        counts = Counter()
        for r in kept:
            counts[r["family"]] += r["modules"]
        removed = (
            "none"
            if not d["removed_rows"]
            else (
                "1"
                if len(d["removed_rows"]) == 1
                else "1--" + str(len(d["removed_rows"]))
            )
        )
        result.append(
            f"{i} & \\num{{{d['datum_mm']:.3f}}} & {removed} & {counts['single']} & {counts['quad']} & {d['after']['chips']} & {d['after']['cooling']['number_circuits']} \\\\"
        )
    return (
        "\\begin{tabular}{r r l r r r r}\n\\toprule\nDisc & $|z_d|$ [mm] & Removed & Single & Quad & Chips & Circuits\\\\\n\\midrule\n"
        + "\n".join(result)
        + "\n\\bottomrule\n\\end{tabular}\n"
    )


def facts():
    r = read(SOURCES[7])
    n = read(SOURCES[8])
    data = dict(
        PixelModules=r["counts"]["module"],
        PixelChips=r["counts"]["sensitive"],
        EndcapModules=r["endcap_modules"],
        EndcapChips=r["endcap_chips"],
        CoolingCircuits=r["endcap_cooling_circuits"],
        ModelMassKg=f"{r['total_mass_g']/1000:.3f}",
        CentreResidual=f"{n['sensitive_comparison']['maximum_center_residual_mm']:.3e}",
    )
    ref = next(
        s
        for s in r["inherited_scenario_screens"]["scenarios"]
        if s["scenario"] == "reference"
    )
    for side in ref["sides"]:
        label = "Positive" if side["side"] == "positive" else "Negative"
        data[label + "TrunkUtil"] = f"{side['trunk_utilization']:.4f}"
        data[label + "NeckUtil"] = f"{side['inherited_neck_utilization']:.4f}"
    return "".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in data.items())


def barrel_table():
    source = json.loads(gzip.decompress((ROOT / BARREL_LAYOUT).read_bytes()))
    result = []
    for i, layer in enumerate(source["layers"][:4], 1):
        bodies = [b for b in source["bodies"] if b["layer_id"] == layer["id"]]
        patches = [p for p in source["modules"] if p["layer_id"] == layer["id"]]
        bound = max(abs(p["center_mm"][2]) + p["half_v_mm"] for p in patches)
        result.append(
            f"{i} & {layer['r_m']*1000:.0f} & {bodies[0]['family']} & {len(set(b['col'] for b in bodies))} & {len(bodies)} & {len(patches)} & \\num{{{bound:.3f}}} \\\\"
        )
    return (
        "\\begin{tabular}{r r l r r r r}\n\\toprule\nLayer & $r_d$ [mm] & Family & Staves & Modules & Chips & $|z|_{\\max}$ [mm]\\\\\n\\midrule\n"
        + "\n".join(result)
        + "\n\\bottomrule\n\\end{tabular}\n"
    )


def figures(output):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon, Circle

    plt.rcParams.update({"font.size": 11, "pdf.fonttype": 42, "svg.fonttype": "none"})
    layout = read(SOURCES[5])
    discs = read(SOURCES[6])["variants"]["four-single-two-quad"]["positive_discs"]
    frozen = {m["module_id"]: m for m in layout["modules"]}
    raw = {m["module_id"]: m for m in layout["raw_modules"]}
    config = read(SOURCES[2])
    support = read(SOURCES[4])["plate"]
    colors = {"single": "#2271a8", "quad": "#da7c30"}
    fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.9), layout="constrained")
    for ax, index in zip(axes, (0, 6, 8)):
        disc = discs[index]
        z = disc["datum_mm"]
        anchor = (z * z - 150 * 150) / z
        for p in layout["active_patches"]:
            if p["row"] in disc["removed_rows"]:
                continue
            m = frozen[p["module_id"]]
            r = raw[p["module_id"]]
            c = [
                r["center_mm"][j] * (1 + m["local_z_mm"] / anchor)
                + p["center_mm"][j]
                - m["center_mm"][j]
                for j in range(2)
            ]
            corners = [
                [
                    c[j]
                    + a * p["half_u_mm"] * p["u"][j]
                    + b * p["half_v_mm"] * p["v"][j]
                    for j in range(2)
                ]
                for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))
            ]
            ax.add_patch(
                Polygon(
                    corners,
                    facecolor=colors[p["family"]],
                    edgecolor="white",
                    linewidth=0.2,
                    alpha=0.8,
                )
            )
        for radius in (support["r_min_mm"], support["r_max_mm"]):
            ax.add_patch(
                Circle(
                    (0, 0),
                    radius,
                    fill=False,
                    color="#555",
                    linewidth=0.7,
                    linestyle="--",
                )
            )
        ax.set(
            xlim=(-200, 200),
            ylim=(-200, 200),
            aspect="equal",
            xlabel="x [mm]",
            title=f"Disc {index+1}: {disc['after']['modules']} modules",
        )
        ax.set_xticks((-180, 0, 180))
        ax.set_yticks((-180, 0, 180))
    axes[0].set_ylabel("y [mm]")
    from matplotlib.lines import Line2D

    fig.legend(
        handles=[
            Line2D([], [], color=c, lw=5, label=f.capitalize() + " modules")
            for f, c in colors.items()
        ],
        loc="outside lower center",
        ncol=2,
        frameon=False,
    )
    fig.savefig(
        output / "disc-layouts.pdf", metadata={"CreationDate": None, "ModDate": None}
    )
    fig.savefig(output / "disc-layouts.png", dpi=170)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7.1, 3.3), layout="constrained")
    for side in (-1, 1):
        for i, d in enumerate(discs):
            ax.plot(
                [side * d["datum_mm"]] * 2, [27, 188.5], color="#aaa", lw=5, zorder=1
            )
            for ring in layout["rings"]:
                if ring["row"] not in d["retained_rows"]:
                    continue
                ax.scatter(
                    side * d["datum_mm"],
                    ring["radius_mm"],
                    color=colors[ring["family"]],
                    s=35,
                    zorder=2,
                )
    ax.axvspan(-150, 150, color="#e7e7ec", zorder=0, label="luminous z envelope")
    ax.set(
        xlabel="disc datum z [mm]",
        ylabel="nominal ring radius [mm]",
        ylim=(0, 205),
        xlim=(-3300, 3300),
    )
    ax.grid(alpha=0.15)
    ax.legend(frameon=False, loc="lower center")
    fig.savefig(
        output / "longitudinal-layout.pdf",
        metadata={"CreationDate": None, "ModDate": None},
    )
    fig.savefig(output / "longitudinal-layout.png", dpi=170)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/publication/tdr")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = args.output
    hashes = source_hashes()
    generated = {
        "generated/disc-inventory.tex": table(),
        "generated/pixel-facts.tex": facts(),
        "generated/barrel-inventory.tex": barrel_table(),
    }
    if args.check:
        manifest = json.loads((output / "evidence.json").read_text())
        if manifest["source_sha256"] != hashes:
            raise ValueError("Stale TDR evidence source")
        for path, content in generated.items():
            if (output / path).read_text() != content:
                raise ValueError("Stale generated table: " + path)
        for path, digest in manifest["generated_sha256"].items():
            if hashlib.sha256((output / path).read_bytes()).hexdigest() != digest:
                raise ValueError("Changed generated asset: " + path)
        print("TDR source pins, generated tables/facts and figure hashes match.")
        return
    for path, content in generated.items():
        p = output / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    (output / "figures").mkdir(parents=True, exist_ok=True)
    figures(output / "figures")
    assets = [
        *generated,
        *[
            "figures/" + n + ext
            for n in ("disc-layouts", "longitudinal-layout")
            for ext in (".pdf", ".png")
        ],
    ]
    manifest = dict(
        status="DRAFT / preliminary pixel baseline",
        template_revision="7783ea3e3235c0fe9da641db3d303a6f211b3073",
        contract_revision="63e030f2b517bdbe526a1860c0f32a3012a712b4",
        model_deliverable_revision="9a4632d8262fb7667be80c168635d4c9eac8317e",
        source_sha256=hashes,
        generated_sha256={
            p: hashlib.sha256((output / p).read_bytes()).hexdigest() for p in assets
        },
        note="Model deliverable commit is not the native execution revision. Native dirty input/producer hashes remain in DES019.",
    )
    (output / "evidence.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
