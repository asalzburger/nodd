#!/usr/bin/env python3
"""Check the installed unrooted APIs and CLI with a synthetic ROOT histogram."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import distribution, distributions
import json
import os
from pathlib import Path
import platform
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("build/unrooted-smoke"))
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.environ["MPLBACKEND"] = "Agg"
    os.environ["MPLCONFIGDIR"] = str(output / "mpl-cache")
    os.environ.setdefault("XDG_CACHE_HOME", str(output / "cache"))

    import matplotlib.pyplot as plt
    import numpy as np
    import uproot

    from unrooted.io.root import load
    from unrooted.plot import StyleSet
    from unrooted.plot.mpl import overlay
    from unrooted.plot.plotly import plot as interactive_plot

    # Check the installed package's recorded Git origin against the source pin.
    requirement = Path(__file__).with_name("requirements-unrooted.in").read_text()
    expected_revision = requirement.strip().rsplit("@", 1)[1]
    origin = json.loads(distribution("unrooted").read_text("direct_url.json"))
    assert origin["vcs_info"]["commit_id"] == expected_revision, origin

    # These fixture counts are arbitrary, deterministic software test data.
    edges = np.arange(9, dtype=float)
    counts = np.array([8, 20, 35, 45, 42, 30, 18, 6], dtype=float)
    comparison = np.array([9, 19, 36, 44, 40, 33, 16, 7], dtype=float)
    source = output / "synthetic.root"
    with uproot.recreate(source) as root_file:
        root_file["fixture"] = (counts, edges)
        root_file["comparison"] = (comparison, edges)
    hist = load(source, "fixture")
    other = load(source, "comparison")
    np.testing.assert_array_equal(hist.values, counts)
    np.testing.assert_array_equal(hist.variances, counts)
    np.testing.assert_array_equal(hist.axes[0].edges, edges)
    hist.axes[0].label = "Synthetic observable [arbitrary units]"

    styles = StyleSet.load("odd")
    ax, ratio = overlay(
        [hist, other], labels=["Fixture A", "Fixture B"],
        styles=[styles[0], styles[1]], ratio=True,
    )
    assert ratio is not None
    ax.set_title("unrooted installation check — synthetic data")
    ax.set_ylabel("Entries / bin")
    ax.figure.set_size_inches(7, 5)
    artifacts = []
    for extension in ("png", "pdf", "svg"):
        target = output / f"histogram.{extension}"
        ax.figure.savefig(target, dpi=160, bbox_inches="tight")
        artifacts.append(target)
    plt.close(ax.figure)
    html = output / "histogram.html"
    interactive_plot(hist).write_html(html, include_plotlyjs=True)
    artifacts.append(html)

    cli = Path(sys.executable).parent / "unrooted"
    subprocess.run([str(cli), "--help"], check=True, capture_output=True, text=True)
    cli_plot = output / "cli.png"
    subprocess.run([
        str(cli), "--input", str(source), "--draw", "hist:fixture",
        "--palette", "odd", "--output", str(cli_plot),
    ], check=True)
    artifacts.append(cli_plot)
    assert (output / "histogram.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert (output / "histogram.pdf").read_bytes().startswith(b"%PDF-")
    assert "<svg" in (output / "histogram.svg").read_text()
    assert "Plotly.newPlot" in html.read_text()
    assert all(path.stat().st_size > 0 for path in artifacts)

    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "issue": "https://github.com/asalzburger/nodd/issues/95",
        "command": "software/build/unrooted-venv/bin/python -I software/analysis/unrooted_smoke.py",
        "upstream_commit": expected_revision,
        "requirements_sha256": hashlib.sha256(
            Path(__file__).with_name("requirements-unrooted.txt").read_bytes()
        ).hexdigest(),
        "smoke_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python": platform.python_version(),
        "platform": platform.system(),
        "machine": platform.machine(),
        "packages": dict(sorted(
            (dist.metadata["Name"], dist.version) for dist in distributions()
        )),
        "fixture": {"edges": edges.tolist(), "counts": counts.tolist(),
                    "comparison": comparison.tolist(), "seed": None},
        "checks": ["installed Git revision", "ROOT values, variances and edges",
                   "ODD palette", "overlay with ratio", "PNG/PDF/SVG export",
                   "self-contained Plotly HTML", "CLI help and PNG export"],
        "artifacts": [
            {"name": path.name, "bytes": path.stat().st_size,
             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in artifacts
        ],
        "scope": "Synthetic installation check; no detector performance result.",
    }
    (output / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: installed unrooted, ROOT I/O, API and CLI; artifacts in {output}")


if __name__ == "__main__":
    main()
