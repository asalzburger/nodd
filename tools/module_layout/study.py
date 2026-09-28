#!/usr/bin/env python3
"""Repeatable DES-009 prototype. New runs never overwrite retained evidence."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time

import numpy as np

from geometry import MODELS_PATH, LAYOUTS_PATH, generate_layout, body_overlap_diagnostics
from intersections import SurfaceIndex, evaluate
from sampling import directions, tracks_for, control_sample, native_sample

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODES = ("straight", "positive", "negative")


def read(path):
    return json.loads(Path(path).read_text())


def write(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False)+"\n")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cases(config):
    result = []
    for candidate in config["candidates"]:
        for variant in config["variants"]:
            result.append(dict(id=f"{candidate}-{variant}-mixed", candidate=candidate,
                               variant=variant, pixel_family="mixed", cohort="main"))
        for family in config["pixel_controls"]:
            result.append(dict(id=f"{candidate}-staggered-{family}", candidate=candidate,
                               variant="staggered", pixel_family=family, cohort="control"))
        if config["pixel_controls"] or config["pixel_uncertainty"]:
            result.append(dict(id=f"{candidate}-staggered-mixed-control", candidate=candidate,
                               variant="staggered", pixel_family="mixed", cohort="control"))
        for change in config["pixel_uncertainty"]:
            result.append(dict(id=f"{candidate}-staggered-{change['name']}", candidate=candidate,
                               variant="staggered", pixel_family="mixed", cohort="control",
                               pixel_override={k: v for k, v in change.items() if k != "name"}))
    return result


def case_layout(case, models, layouts_path):
    model = copy.deepcopy(models)
    model["pixel"].update(case.get("pixel_override", {}))
    return generate_layout(case["candidate"], case["variant"], case["pixel_family"],
                           models=model, layouts_path=layouts_path)


def run_case(case, config, models, layouts_path, output):
    start = time.monotonic()
    path = Path(output)/case["id"]
    path.mkdir()
    samples = directions(config)
    if case["cohort"] == "control":
        samples = control_sample(samples, config["control_tracks"], config["seed"]+1)
    layout = case_layout(case, models, layouts_path)
    index = SurfaceIndex(layout)
    host = layout["metadata"]["host"]
    host_args = dict(host_radius_mm=1000*host["r_max_m"], host_half_z_mm=1000*host["abs_z_max_m"])
    summary = dict(case=case, geometry=layout["metadata"],
                   body_diagnostics=body_overlap_diagnostics(layout), modes={})
    tracks_by_mode, worst = {}, {}
    raw = dict(directions=samples, modes={})
    for mode in MODES:
        tracks = tracks_for(samples, mode, config)
        tracks_by_mode[mode] = tracks
        stats = evaluate(layout, tracks, index=index, **host_args)
        rows = stats.pop("per_track")
        worst[mode] = sorted(range(len(tracks)), key=lambda i: (
            -rows["missing_stations"][i], rows["stations"][i]))[:4]
        # Separate denominators show that grid phase and vertex populations are not event weights.
        stats["cohort_tracks"] = {name: sum(t["cohort"] == name for t in samples)
                                  for name in sorted({t["cohort"] for t in samples})}
        summary["modes"][mode] = stats
        raw["modes"][mode] = rows
    native = native_sample(tracks_by_mode, config["native_tracks_per_case"], config["seed"], worst)
    write(path/"native_tracks.json", native)
    with gzip.open(path/"track_metrics.json.gz", "wt") as stream:
        json.dump(raw, stream, separators=(",", ":"), allow_nan=False)
    summary["elapsed_seconds"] = time.monotonic()-start
    write(path/"summary.json", summary)
    return dict(id=case["id"], seconds=summary["elapsed_seconds"],
                tracks=sum(s["total"]["tracks"] for s in summary["modes"].values()),
                collisions=summary["body_diagnostics"]["overlapping_body_pairs"])


def run(args):
    config, models = read(args.config), read(args.models)
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    write(output/"config.json", config)
    write(output/"sensor_models.json", models)
    write(output/"layouts.json", read(args.layouts))
    selected = cases(config)
    if args.cases:
        requested = set(args.cases.split(","))
        selected = [case for case in selected if case["id"] in requested]
        if requested != {case["id"] for case in selected}:
            raise ValueError("Unknown case name")
    git = lambda *command: subprocess.check_output(["git", *command], cwd=ROOT, text=True).strip()
    metadata = dict(status="PROTOTYPE; finite sample, no detector acceptance", schema_version=1,
                    created_utc=datetime.now(timezone.utc).isoformat(), project_revision=git("rev-parse", "HEAD"),
                    working_tree_changes=git("status", "--short").splitlines(),
                    command=__import__("sys").argv, python=platform.python_version(), numpy=np.__version__,
                    input_sha256={name: digest(path) for name, path in (
                        ("config", args.config), ("models", args.models), ("layouts", args.layouts))},
                    code_sha256={p.name: digest(p) for p in sorted(HERE.glob("*.py"))}, cases=selected,
                    acts_validation="NOT RUN; use validate-acts or run --native")
    write(output/"run.json", metadata)
    with ProcessPoolExecutor(max_workers=args.jobs) as executor:
        futures = [executor.submit(run_case, case, config, models, output/"layouts.json", output)
                   for case in selected]
        for future in as_completed(futures):
            print(json.dumps(future.result()), flush=True)
    if args.native:
        validate_acts(output, args.acts_source, args.runtime_manifest)
    print(f"Completed {len(selected)} cases in {output}", flush=True)


def validate_acts(output, acts_source=None, runtime_manifest=None):
    from acts_validate import validate
    output = Path(output)
    metadata, models = read(output/"run.json"), read(output/"sensor_models.json")
    overlay = read(runtime_manifest) if runtime_manifest else None
    for name in ("geometry.py", "intersections.py"):
        if digest(HERE/name) != metadata["code_sha256"][name]:
            raise RuntimeError(f"Code changed since scan: {name}; create a fresh run")
    # Adding an audit is allowed; replacing an earlier audit is not.
    for case in metadata["cases"]:
        path = output/case["id"]
        layout = case_layout(case, models, output/"layouts.json")
        native_dir = path/"acts"
        if native_dir.exists():
            raise FileExistsError(f"Retained ACTS evidence already exists: {native_dir}")
        host = layout["metadata"]["host"]
        result = validate(layout, read(path/"native_tracks.json"), native_dir,
                          acts_source=acts_source, host_radius_mm=1000*host["r_max_m"],
                          host_half_z_mm=1000*host["abs_z_max_m"])
        if overlay is not None:
            if result["runtime"]["acts_extension_sha256"] != overlay["acts_extension_sha256"]:
                raise RuntimeError("Runtime extension does not match supplied overlay manifest")
            result["runtime_overlay"] = overlay
        write(path/"acts_validation.json", result)
        print(json.dumps(dict(case=case["id"], passed=result["passed"],
                              mismatches=len(result["mismatches"]))), flush=True)
        if not result["passed"]:
            raise RuntimeError(f"Native ACTS disagrees: {case['id']}")
    metadata["acts_validation"] = "PASS; native ACTS target-propagation patch sets on retained samples; global navigation remains unvalidated"
    write(output/"run.json", metadata)


def compare_runs(first, second, requested=None):
    """Exact numerical regression, excluding elapsed time and native audit metadata."""
    first, second = Path(first), Path(second)
    left = {case["id"] for case in read(first/"run.json")["cases"]}
    right = {case["id"] for case in read(second/"run.json")["cases"]}
    chosen = set(requested.split(",")) if requested else left
    if not chosen or not chosen <= left & right or (not requested and left != right):
        raise ValueError("Case sets differ; select explicitly present cases with --cases")
    for case in sorted(chosen):
        a, b = read(first/case/"summary.json"), read(second/case/"summary.json")
        a.pop("elapsed_seconds")
        b.pop("elapsed_seconds")
        if a != b:
            raise AssertionError(f"Geometry or summary changed: {case}")
        for name in ("native_tracks.json", "track_metrics.json.gz"):
            if name.endswith(".gz"):
                with gzip.open(first/case/name, "rt") as stream:
                    a = json.load(stream)
                with gzip.open(second/case/name, "rt") as stream:
                    b = json.load(stream)
            else:
                a, b = read(first/case/name), read(second/case/name)
            if a != b:
                raise AssertionError(f"Track evidence changed: {case}/{name}")
    print(f"PASS: {len(chosen)} cases reproduce exactly, excluding elapsed time/native audit metadata")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    command = sub.add_parser("run")
    command.add_argument("--output", required=True)
    command.add_argument("--config", default=HERE/"study_config.json", type=Path)
    command.add_argument("--models", default=MODELS_PATH, type=Path)
    command.add_argument("--layouts", default=LAYOUTS_PATH, type=Path)
    command.add_argument("--cases", help="Comma-separated case IDs, otherwise whole configured matrix")
    command.add_argument("--jobs", type=int, default=1)
    command.add_argument("--native", action="store_true", help="Also require native ACTS audit")
    command.add_argument("--acts-source", type=Path)
    command.add_argument("--runtime-manifest", type=Path, help="Optional temporary build-overlay provenance; extension hash must match")
    command = sub.add_parser("compare")
    command.add_argument("--first", required=True)
    command.add_argument("--second", required=True)
    command.add_argument("--cases")
    command = sub.add_parser("validate-acts")
    command.add_argument("--output", required=True)
    command.add_argument("--acts-source", type=Path)
    command.add_argument("--runtime-manifest", type=Path)
    args = parser.parse_args()
    if args.action == "run":
        run(args)
    elif args.action == "validate-acts":
        validate_acts(args.output, args.acts_source, args.runtime_manifest)
    else:
        compare_runs(args.first, args.second, args.cases)


if __name__ == "__main__":
    main()
