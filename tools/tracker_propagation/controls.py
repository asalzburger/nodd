#!/usr/bin/env python3
"""Repeat paired numerical refinements and an independent-seed tracker sample."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=ROOT / "build/tracker-propagation")
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build/dd4hep")
    parser.add_argument("--plot-python", type=Path, default=ROOT / "software/build/unrooted-venv/bin/python")
    parser.add_argument("--paired-tracks", type=int, default=512)
    parser.add_argument("--independent-tracks", type=int, default=2048)
    args = parser.parse_args()
    nominal = json.loads((args.directory / "study.json").read_text())
    for name in ("half-step", "fine-map", "independent-seed"):
        output = args.directory / "controls" / name
        output.mkdir(parents=True, exist_ok=True)
        config = json.loads(json.dumps(nominal))
        config["tracks_per_pt"] = args.paired_tracks
        if name == "half-step":
            config["maximum_step_mm"] /= 2
        elif name == "fine-map":
            for key in ("r_step_mm", "z_step_mm"):
                config["field"][key] /= 2
        else:
            config["seed"] += 1
            config["tracks_per_pt"] = args.independent_tracks
        source = output / "input.json"
        source.write_text(json.dumps(config, indent=2) + "\n")
        command = [sys.executable, str(ROOT / "tools/tracker_propagation/run.py"),
                   "--config", str(source), "--output", str(output),
                   "--build-dir", str(args.build_dir), "--plot-python", str(args.plot_python)]
        if name == "fine-map":
            subprocess.run(command + ["--stage", "field"], check=True)
        else:
            (output / "field").mkdir(exist_ok=True)
            for file in ("field.txt", "field-report.json"):
                shutil.copyfile(args.directory / "field" / file, output / "field" / file)
        subprocess.run(command + ["--stage", "propagate"], check=True)
    subprocess.run([str(args.plot_python.absolute()), "-I",
                    str(ROOT / "tools/tracker_propagation/diagnostics.py"),
                    "--directory", str(args.directory)], check=True)


if __name__ == "__main__":
    main()
