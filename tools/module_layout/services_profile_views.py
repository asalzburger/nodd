#!/usr/bin/env python3
"""Plot retained DES-010 cumulative service loads without changing corridors."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def render(run, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    run, output = Path(run), Path(output)
    data = json.loads((run / "profile.json").read_text())
    producer = Path(__file__).with_name("services_profile.py")
    if digest(producer) != data["provenance"]["profile_code_sha256"]:
        raise RuntimeError("Profile producer differs from retained evidence")
    if digest(run / "budget_inputs.json") != data["provenance"]["source_inputs_sha256"]["budget_inputs.json"]:
        raise RuntimeError("Budget input snapshot differs from retained evidence")
    by_key = {(p["subsystem"], p["side"]): p for p in data["profiles"]}
    subs = [("pixel", "Pixels"), ("short_strip", "Short strips"), ("long_strip", "Long strips")]
    colors = {"reference": "#0072b2", "conservative": "#c57800", "stress": "#bb3344"}
    fig, axes = plt.subplots(3, 2, figsize=(14, 11), sharex=True)
    fig.suptitle("DES-010 · Services accumulate towards the outermost endcap", fontsize=17, y=.985)
    fig.text(.5, .95, "PROTOTYPE · Constant route geometry unchanged · Full branch load enters at near edge of each shaded pickup interval",
             ha="center", fontsize=10)
    x0 = min(p["abs_z_min_mm"] for p in data["profiles"])
    x1 = max(p["abs_z_max_mm"] for p in data["profiles"])
    for row, (sub, title) in enumerate(subs):
        left, right = axes[row]
        plus = by_key[(sub, "positive")]
        for ax in (left, right):
            for event in plus["pickup_events"]:
                ax.axvspan(*event["pickup_abs_z_interval_mm"], color="black", alpha=.045, lw=0)
            ax.grid(alpha=.2)
            ax.set_xlim(x0-30, x1+30)
        left.set_title(title + " — accumulated reference demand")
        right.set_title(f"{title} — width (fixed corridor {plus['reserved_width_mm']:g} mm)")
        for side, style in (("positive", "-"), ("negative", "--")):
            profile = by_key[(sub, side)]
            segments = profile["segments"]
            edges = [segments[0]["abs_z_min_mm"]] + [s["abs_z_max_mm"] for s in segments]
            left.stairs([s["scenarios"]["reference"]["demand_mm2"]/1000 for s in segments], edges,
                        baseline=None, color=colors["reference"], linestyle=style, lw=2)
            for scenario, color in colors.items():
                right.stairs([s["scenarios"][scenario]["required_annular_width_mm"] for s in segments], edges,
                             baseline=None, color=color, linestyle=style, lw=2)
        left.axhline(plus["terminal"]["scenarios"]["reference"]["demand_mm2"]/1000,
                     color=".35", ls=":", lw=1.7)
        right.axhline(plus["reserved_width_mm"], color=".35", ls=":", lw=1.7)
        left.set_ylabel("Cables + cooling section [10³ mm²]")
        right.set_ylabel("Equivalent annular width [mm]\n(including edge allowances)")
        for ax in (left, right):
            ax.set_ylim(bottom=0)
    for ax in axes[-1]:
        ax.set_xlabel("Distance from interaction point |z| [mm]")
    handles = [Line2D([], [], color=color, lw=2, label=name.capitalize()) for name, color in colors.items()]
    handles += [Line2D([], [], color=".2", lw=2, label="Positive end"),
                Line2D([], [], color=".2", lw=2, ls="--", label="Negative end"),
                Line2D([], [], color=".35", lw=1.7, ls=":", label="Retained maximum / fixed corridor")]
    fig.legend(handles=handles, loc="lower center", ncol=3, bbox_to_anchor=(.5, .03), fontsize=10)
    fig.text(.5, .012, "Equivalent width is a capacity diagnostic at fixed inner radius; bends, connectors and support clearance still govern. No taper or layer optimization.",
             ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .09, 1, .925))
    output.mkdir(parents=True, exist_ok=False)
    for ext in ("png", "pdf"):
        fig.savefig(output / ("cumulative-services." + ext), dpi=160)
    plt.close(fig)
    metadata = dict(status="PROTOTYPE diagnostic; unchanged geometry", profile_sha256=digest(run / "profile.json"),
                    renderer_sha256=digest(__file__), matplotlib_version=matplotlib.__version__,
                    artifacts_sha256={p.name: digest(p) for p in sorted(output.iterdir()) if p.is_file()})
    (output / "views.json").write_text(json.dumps(metadata, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    render(args.run, args.output)
