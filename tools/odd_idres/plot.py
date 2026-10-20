#!/usr/bin/env python3
"""Replot retained JSON results without IdRes, ACTS, DD4hep or source checkouts."""
import argparse
import gzip
import json
from pathlib import Path
import re
import textwrap

from prepare import OUT, ROOT, digest, read, write


def plot(data, output, preview=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    plt.rcParams.update({"font.size": 10, "svg.fonttype": "none", "svg.hashsalt": "nodd-odd-idres",
                         "axes.spines.top": False, "axes.spines.right": False})
    config = read(data/"geometries.json")
    profiles = read(data/"profiles.json.gz")
    resolutions = read(data/"resolutions.json.gz")
    candidates = config["candidates"]
    palette = ["#555555", "#166da8", "#d45c1b"]
    styles = ["-", "-", (0, (4, 3))]
    technology = [("pixel", "#3366aa"), ("short_strip", "#c47f00"), ("long_strip", "#21856d")]
    field = config["scan"]["plot_field_T"]
    output.mkdir(parents=True, exist_ok=True)
    artifacts = []

    def save(fig, filename, caption):
        height = fig.get_size_inches()[1]
        handles = labels = None
        for ax in fig.axes:
            legend = ax.get_legend()
            if legend:
                if handles is None:
                    handles = legend.legend_handles
                    labels = [t.get_text() for t in legend.get_texts()]
                legend.remove()
        if handles:
            fig.legend(handles, labels, ncol=len(labels), loc="lower center",
                       bbox_to_anchor=(.5, .34/height), fontsize=9, frameon=False)
        margin = .85 / height
        fig.get_layout_engine().set(rect=(0, margin, 1, 1-margin))
        fig.text(.5, .02/height, textwrap.fill(caption, 155), ha="center", va="bottom", fontsize=9, color="#555555")
        fig.savefig(output/filename, metadata={"Date": None}, bbox_inches="tight")
        # Matplotlib hashes unrounded clip-box floats into IDs. Canonical IDs
        # keep otherwise identical serialized SVGs stable across repeat draws.
        svg = (output/filename).read_text()
        for i, old in enumerate(re.findall(r'<clipPath id="([^"]+)"', svg)):
            new = f"nodd-clip-{i}"
            svg = svg.replace(f'id="{old}"', f'id="{new}"').replace(f'url(#{old})', f'url(#{new})')
        (output/filename).write_text(svg)
        if preview:
            preview.mkdir(parents=True, exist_ok=True)
            fig.savefig(preview/filename.replace(".svg", ".png"), dpi=130, bbox_inches="tight")
        artifacts.append(filename)
        plt.close(fig)

    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True, sharey=True, constrained_layout=True)
    for ax, c in zip(axes, candidates):
        for l in c["layers"]:
            color = dict(technology)[l["subsystem"]]
            if l["kind"] == "cylinder":
                ax.plot([1000*l["z_min_m"], 1000*l["z_max_m"]], [1000*l["r_m"]]*2, color=color, lw=1.5)
            else:
                ax.plot([1000*l["z_m"]]*2, [1000*l["r_min_m"], 1000*l["r_max_m"]], color=color, lw=1.5)
        ax.set_title(c["name"], loc="left", fontsize=11)
        ax.set_ylabel("r [mm]")
        ax.grid(alpha=.15)
    axes[-1].set_xlabel("z [mm]")
    axes[0].legend(handles=[Line2D([0],[0], color=color, label=f.replace("_", " ")) for f,color in technology], ncol=3, loc="upper center")
    fig.suptitle("ODD tracker layouts — ideal IdRes surfaces", fontsize=15)
    save(fig, "layouts.svg", "PROTOTYPE · nominal radii / envelope annuli · tilts, gaps, stagger and separated stereo faces collapsed")

    for observable in ("hits", "material"):
        fig, axes = plt.subplots(1, 3, figsize=(15, 4.4), sharex=True, sharey=True, constrained_layout=True)
        for ax,c in zip(axes, candidates):
            rows = sorted((r for r in profiles if r["geometry"] == c["id"] and r["vertex_z_m"] == 0), key=lambda r:r["eta"])
            x = [r["eta"] for r in rows]
            for f, color in technology:
                key = {"pixel":"pixel_hits", "short_strip":"short_strip_hits", "long_strip":"long_strip_sensor_hits"}[f] if observable == "hits" else f+"_percent_x0"
                ax.plot(x, [r[key] for r in rows], color=color, label=f.replace("_", " "), lw=1.5)
            key = "sensor_hits" if observable == "hits" else "material_percent_x0"
            ax.plot(x, [r[key] for r in rows], color="#222222", lw=1.7, label="total")
            if observable == "hits":
                ax.plot(x, [r["measurement_stations"] for r in rows], color="#222222", lw=1, ls="--", label="stations")
            ax.set_title(c["name"], fontsize=11)
            ax.set_xlabel(r"$\eta$")
            ax.grid(alpha=.18)
        axes[0].set_ylabel("Sensitive sensor crossings" if observable == "hits" else "Layer material [% X₀]")
        axes[0].legend(ncol=2, fontsize=8, loc="upper left")
        fig.suptitle(("Hits" if observable == "hits" else "Material")+" vs pseudorapidity · origin tracks", fontsize=15)
        caption = "One pixel/short-strip hit per surface; two long-strip sensor faces per collapsed stereo station" if observable == "hits" else "Common DES006 layer allowances: pixel 1%, short 1.5%, long-strip pair 2% X₀ · beam pipe and remote services excluded"
        save(fig, observable+"-vs-eta.svg", "PROTOTYPE · "+caption)

    for relative in (False, True):
        fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), sharex=True, sharey=True, constrained_layout=True)
        for ax,pt in zip(axes, config["scan"]["pt_GeV"]):
            for c,color,style in zip(candidates, palette, styles):
                rows = sorted((r for r in resolutions if r["geometry"] == c["id"] and r["field_T"] == field and r["pt_GeV"] == pt and r["vertex_z_m"] == 0), key=lambda r:r["eta"])
                key = "linearized_relative_pt_percent" if relative else "sigma_inverse_pt_TeV_inverse"
                ax.plot([r["eta"] for r in rows], [r[key] for r in rows], color=color, ls=style, label=c["name"], lw=1.7)
            ax.set_title(f"pT = {pt:g} GeV")
            ax.set_xlabel(r"$\eta$")
            ax.set_yscale("log")
            ax.grid(alpha=.18, which="both")
            if relative:
                ax.axhline(100, color="#9c2020", ls=":", lw=1)
        axes[0].set_ylabel("pT × σ(1/pT) [%]" if relative else "σ(1/pT) [TeV⁻¹]")
        axes[0].legend(fontsize=8, loc="upper left")
        fig.suptitle(("Linearized relative pT uncertainty" if relative else "Inverse transverse momentum resolution")+f" · {field:g} T · origin", fontsize=15)
        caption = "PROTOTYPE · common pitch/√12 response + local layer material · no vertex prior"
        if relative:
            caption += " · ≥100% is not a Gaussian relative-momentum resolution"
        save(fig, "relative-pt-vs-eta.svg" if relative else "momentum-resolution-vs-eta.svg", caption)

    fig, axes = plt.subplots(3, 2, figsize=(12, 9), sharex=True, constrained_layout=True)
    for i,z in enumerate(config["scan"]["vertex_z_m"]):
        for c,color,style in zip(candidates,palette,styles):
            rows = sorted((r for r in profiles if r["geometry"] == c["id"] and r["vertex_z_m"] == z), key=lambda r:r["eta"])
            for ax,key in zip(axes[i], ("sensor_hits", "material_percent_x0")):
                ax.plot([r["eta"] for r in rows], [r[key] for r in rows], color=color, ls=style, lw=1.5, label=c["name"])
                ax.grid(alpha=.18)
            axes[i,0].set_ylabel(f"z₀ = {z*1000:g} mm\nSensor hits")
            axes[i,1].set_ylabel(f"z₀ = {z*1000:g} mm\nMaterial [% X₀]")
    for ax in axes[-1]:
        ax.set_xlabel(r"$\eta$")
    axes[0,0].legend(fontsize=8, loc="lower left")
    fig.suptitle("Vertex stress controls — hits and local material", fontsize=15)
    save(fig, "vertex-controls.svg", "PROTOTYPE · ±150 mm are stress vertices, not a beamspot distribution · extended and aperture curves coincide in this scan")

    aperture = config["aperture_table"]
    fig, ax = plt.subplots(figsize=(9, 4.5), constrained_layout=True)
    ax.plot([r["abs_z_mm"] for r in aperture], [r["full_inner_mm"] for r in aperture], "o-", color=palette[1], label="Untrimmed mixed-disc envelope")
    ax.plot([r["abs_z_mm"] for r in aperture], [r["adapted_inner_mm"] for r in aperture], "o--", color=palette[2], label="DES018 retained-ring envelope")
    ax.set(xlabel="Positive disc datum z [mm]", ylabel="Inner active-envelope radius [mm]", title="Adapted outer pixel disc aperture")
    ax.grid(alpha=.18)
    ax.legend(fontsize=9)
    save(fig, "pixel-apertures.svg", "PROTOTYPE · sensitive-envelope change only · DES018 ring removal; retained passive support is not represented by the aperture")

    manifest = dict(inputs={p:digest(data/p) for p in ("geometries.json", "profiles.json.gz", "resolutions.json.gz")},
                    producer_sha256=digest(__file__), matplotlib=matplotlib.__version__,
                    plot_field_T=field, files={p:digest(output/p) for p in artifacts},
                    command="MPLCONFIGDIR=build/odd-idres-mpl python -B tools/odd_idres/plot.py")
    write(output/"manifest.json", manifest)
    print("Plotted", len(artifacts), "SVGs from retained JSON")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", type=Path, default=OUT)
    p.add_argument("--output", type=Path, default=OUT/"figures")
    p.add_argument("--preview", type=Path, help="Optional PNG previews for visual checks")
    a = p.parse_args()
    plot(a.data, a.output, a.preview)
