#!/usr/bin/env python3
"""Repeat the current DD4hep/ACTS tracker study and its unrooted profile plots."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def execute(arguments, *, log):
    print("Running:", " ".join(map(str, arguments)), flush=True)
    with log.open("w") as stream:
        subprocess.run(list(map(str, arguments)), cwd=ROOT, stdout=stream,
                       stderr=subprocess.STDOUT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("study.json"))
    parser.add_argument("--output", type=Path, default=ROOT / "build/tracker-propagation")
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build/dd4hep")
    parser.add_argument("--plot-python", type=Path,
                        default=ROOT / "software/build/unrooted-venv/bin/python")
    parser.add_argument("--tracks", type=int, help="Explicit per-momentum sampling override")
    parser.add_argument("--stage", choices=("all", "field", "propagate", "plot"), default="all")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    if args.tracks is not None:
        if args.tracks <= 0:
            parser.error("tracks must be positive")
        config["tracks_per_pt"] = args.tracks
    if config["vertex_mm"] != [0, 0, 0] or config["energy_loss"] or config["multiple_scattering"]:
        parser.error("this study is defined at the origin with material effects disabled")
    if config["phi_range"] != [-3.141592653589793, 3.141592653589793]:
        parser.error("this study requires uniform full-azimuth sampling")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    executed_config = output / "study.json"
    if args.stage == "plot" and executed_config.exists():
        config = json.loads(executed_config.read_text())
    else:
        executed_config.write_text(json.dumps(config, indent=2) + "\n")
    if args.stage in ("all", "field"):
        execute([sys.executable, ROOT / "tools/tracker_propagation/field_map.py",
                 "--config", executed_config, "--output", output / "field"],
                log=output / "field.log")
    if args.stage in ("all", "propagate"):
        field = output / "field/field.txt"
        report = json.loads((output / "field/field-report.json").read_text())
        if report["status"] != "PASS" or hashlib.sha256(field.read_bytes()).hexdigest() != report["map_sha256"]:
            raise ValueError("field map failed validation or changed after validation")
        if report["configuration"] != config["field"]:
            raise ValueError("field map configuration differs from the requested study")
        if report["script_sha256"] != hashlib.sha256(Path(__file__).with_name("field_map.py").read_bytes()).hexdigest():
            raise ValueError("field generator changed; regenerate and validate the map")
        for relative, digest in report["source"].items():
            if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != digest:
                raise ValueError(f"field source changed: {relative}")
        for pt in config["pt_GeV"]:
            target = output / f"pt_{pt:g}GeV"
            execute([
                sys.executable, ROOT / "software/running/tracker_propagation.py",
                "--nodd-dir", ROOT, "--build-dir", args.build_dir.resolve(),
                "--field-map", field, "--output", target, "--pt-gev", pt,
                "--tracks", config["tracks_per_pt"], "--seed", config["seed"],
                "--eta-min", config["eta_range"][0], "--eta-max", config["eta_range"][1],
                "--max-step-mm", config["maximum_step_mm"],
            ], log=output / f"pt_{pt:g}GeV.log")
            execute([args.plot_python.resolve(), "-I", ROOT / "tools/tracker_propagation/counts.py",
                     "--directory", target], log=output / f"pt_{pt:g}GeV-counts.log")
            execute([
                sys.executable, ROOT / "tools/tracker_dd4hep/check_gen3.py",
                "--report", target / "surfaces.json", "--expected",
                args.build_dir.resolve() / "detector/tracker/expected.json",
                "--output", target / "geometry-check.json",
            ], log=output / f"pt_{pt:g}GeV-geometry.log")
    if args.stage in ("all", "plot"):
        if not args.plot_python.is_file():
            parser.error("plotting Python missing; follow software/analysis/README.md to install unrooted")
        execute([args.plot_python.resolve(), "-I", ROOT / "tools/tracker_propagation/plot.py",
                 "--config", executed_config, "--directory", output, "--output", output / "plots"],
                log=output / "plot.log")
    print(f"Completed stage {args.stage}: {output}")


if __name__ == "__main__":
    main()
