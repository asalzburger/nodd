#!/usr/bin/env python3
"""DES-011 bounded finite-module placement search; no production geometry.

The search uses a fixed training measure. Selection is frozen before the dense
holdout and native ACTS checks. All service loads are recalculated after refill.
"""
from __future__ import annotations

import argparse
import copy
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import subprocess

if __package__:
    from . import geometry, services, services_budget, services_geometry
    from .optimization_metrics import evaluate_spacing, summarize_cohort
    from .optimization_placement import refill_candidate
    from .optimization_services import build_optimized_services, default_policy
    from .intersections import SurfaceIndex, evaluate
    from .sampling import directions, tracks_for, native_sample
else:
    import geometry, services, services_budget, services_geometry
    from optimization_metrics import evaluate_spacing, summarize_cohort
    from optimization_placement import refill_candidate
    from optimization_services import build_optimized_services, default_policy
    from intersections import SurfaceIndex, evaluate
    from sampling import directions, tracks_for, native_sample

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SUBS = services.SUBSYSTEMS
MODES = ("straight", "positive", "negative")


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+"\n")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_config(config):
    if (config["candidate"],config["variant"],config["pixel_family"]) != ("cobe","review_default","mixed"):
        raise ValueError("This constrained refiller supports cobe/review_default/mixed only")
    for key in ("pixel_trunk_inner_mm","short_trunk_inner_mm","long_barrel_half_z_mm",
                "barrel_radius_offsets_mm","last_disc_bypass","disc_spacing","movable_barrels"):
        values=config[key]
        if not values or len(set(values)) != len(values):
            raise ValueError(key+" must contain unique, nonempty scan values")
    if not set(config["disc_spacing"]) <= {"inherited","uniform","front_loaded"}:
        raise ValueError("Unknown disc-spacing schedule")
    if any(not isinstance(value,bool) for value in config["last_disc_bypass"]):
        raise ValueError("last_disc_bypass must contain booleans")
    for key in ("pixel_trunk_inner_mm","short_trunk_inner_mm","long_barrel_half_z_mm","barrel_radius_offsets_mm"):
        if any(isinstance(value,bool) or not math.isfinite(value) for value in config[key]):
            raise ValueError(key+" must contain finite dimensions")
    if config["training"]["seed"] == config["holdout"]["seed"]:
        raise ValueError("Training and random validation seeds must differ")
    for name in ("training","holdout"):
        sample=config[name]
        if sample["eta_points"]<2 or sample["stress_eta_points"]<2 or min(sample["phi_points"],sample["stress_phi_points"],sample["random_tracks"])<1:
            raise ValueError("Sampling needs nonempty angular grids and random cohort")
        if sample["eta_max"]<=0 or sample["momentum_GeV"]<=0:
            raise ValueError("Sampling needs positive eta range and momentum")
    if config["fixed_point_iterations"]<1 or config["native_tracks_per_case"]<3:
        raise ValueError("Iteration/native sample limits must be positive and cover all modes")


def policy_for(parameters):
    policy = default_policy()
    policy["trunk_r_min_mm"] = dict(zip(SUBS, parameters["trunk_inner_mm"]))
    policy["bypass_last_disc"] = parameters["last_disc_bypass"]
    policy["exit_r_min_mm"] = 1040.
    policy["rear_all_r_min_mm"] = 1040.
    if not parameters.get("original_pocket_floors", False):
        policy["barrel_bay_floor_mm"] = dict.fromkeys(SUBS, 10.)
        policy["disc_collector_floor_mm"] = dict.fromkeys(SUBS, 10.)
    return policy


def shift_discs(layout, coordinates):
    """Translate signed discs only, retaining the exact module inventory."""
    result = copy.deepcopy(layout)
    shifts = {}
    for layer in result["layers"]:
        if layer["kind"] == "disc":
            new_z = math.copysign(coordinates[layer["id"]], layer["z_m"])
            shifts[layer["id"]] = new_z-layer["z_m"]*1000
            layer["z_m"] = new_z/1000
    for record in itertools.chain(result["bodies"], result["modules"]):
        if record["layer_id"] in shifts:
            record["center_mm"][2] += shifts[record["layer_id"]]
    result["metadata"]["host_diagnostics"] = geometry.host_diagnostics(result)
    result["metadata"]["summary"] = geometry.summarize(result)
    return result


def disc_coordinates(layout, constraints, pattern, exponent):
    """Keep last discs fixed; distribute residual space above service minima."""
    if pattern not in ("inherited","uniform","front_loaded"):
        raise ValueError("Unknown disc-spacing schedule")
    coordinates = {}
    for side in ("negative", "positive"):
        for sub in SUBS:
            group = constraints[side][sub]
            discs = sorted((l for l in layout["layers"] if l["kind"] == "disc"
                            and l["subsystem"] == sub
                            and (l["z_m"] > 0) == (side == "positive")),
                           key=lambda l: abs(l["z_m"]))
            old = [abs(l["z_m"])*1000 for l in discs]
            first = group["minimum_first_disc_center_abs_z_mm"]
            if first >= old[-1]:
                raise ValueError("First-disc service bay reaches final disc")
            # The service builder checks every collector against every body;
            # spacing schedules are proposed here and rejected if they collide.
            for i, layer in enumerate(discs):
                fraction = (old[i]-old[0])/(old[-1]-old[0]) if pattern == "inherited" else i/(len(old)-1)
                if pattern == "front_loaded":
                    fraction = fraction**exponent
                coordinates[layer["id"]] = first+(old[-1]-first)*fraction
    return coordinates


def build_candidate(parameters, config, paths, *, diagnostics=True):
    catalogue, models = read(paths["layouts"]), read(paths["models"])
    candidate = copy.deepcopy(next(c for c in catalogue["candidates"] if c["id"] == config["candidate"]))
    for layer in candidate["layers"]:
        if layer["id"] in config["movable_barrels"]:
            layer["r_m"] += parameters.get("barrel_offset_mm", 0.)/1000
        if layer["kind"] == "cylinder" and layer["subsystem"] == "long_strip":
            layer["z_min_m"] = -parameters["long_barrel_half_z_mm"]/1000
            layer["z_max_m"] = parameters["long_barrel_half_z_mm"]/1000
    policy = policy_for(parameters)
    inputs = read(paths["budget"])
    inner = policy["trunk_r_min_mm"]
    # Conservative monotone fixed point: a later lower demand never shrinks an
    # already allocated width and thereby triggers a row-count oscillation.
    widths = {sub: 0. for sub in SUBS}
    history = []
    for iteration in range(config["fixed_point_iterations"]):
        annuli = {"pixel": [27., inner["pixel"]-policy["clearance_mm"]],
                  "short_strip": [inner["pixel"]+widths["pixel"]+policy["clearance_mm"],
                                  inner["short_strip"]-policy["clearance_mm"]],
                  "long_strip": [inner["short_strip"]+widths["short_strip"]+policy["clearance_mm"], 1138.]}
        filled = refill_candidate(candidate, models, annuli, layouts_path=paths["layouts"])
        layout = filled["layout"]
        proposal = build_optimized_services(layout, inputs, policy, diagnostics=False)
        actual = {}
        for sub in SUBS:
            trunks = [r for r in proposal["routes"] if r["subsystem"] == sub and "-trunk-" in r["id"]]
            if not trunks:
                raise ValueError("Service builder produced no main trunk for "+sub)
            actual[sub] = max(r["r_max_mm"]-inner[sub] for r in trunks)
        history.append(dict(iteration=iteration, allocated_widths_mm=dict(widths),
                            required_widths_mm=actual, annuli_mm=annuli,
                            modules=len(layout["bodies"])))
        enlarged = {sub: max(widths[sub], actual[sub]) for sub in SUBS}
        if max(enlarged[sub]-widths[sub] for sub in SUBS) <= config["radial_convergence_mm"]:
            break
        widths = enlarged
    else:
        raise ValueError("Inventory/corridor fixed point did not converge")
    coordinates = disc_coordinates(layout, proposal["placement_constraints"],
                                   parameters["disc_spacing"], config["front_loaded_exponent"])
    layout = shift_discs(layout, coordinates)
    proposal = build_optimized_services(layout, inputs, policy, diagnostics=diagnostics)
    interface = services.interface_checks(proposal["routes"], paths["envelopes"], policy["clearance_mm"])
    proposal["interface"] = interface
    for key in ("allocated_volume_conflicts", "disconnected_from_handoff"):
        if interface[key]:
            proposal["failures"].append(key)
    layout["metadata"]["optimization"] = dict(parameters=parameters, policy=policy,
        fixed_point_history=history, annuli_mm=annuli, refill=filled.get("diagnostics", {}),
        interpretation="Complete refill and candidate-local IDs; no original evidence overwritten")
    layout["metadata"]["services"] = dict(routes=proposal["routes"], supports=proposal["supports"])
    return layout, proposal


def track_sets(sampling):
    samples = directions(sampling)
    return {mode: tracks_for(samples, mode, sampling) for mode in MODES}


def spacing_reports(layout, tracks, reference):
    index = SurfaceIndex(layout)
    return {mode: evaluate_spacing(layout, values, reference_layers=reference,
                                   index=index, return_per_track=False)
            for mode, values in tracks.items()}


def score(spacing, area):
    totals = [spacing[mode]["total"] for mode in MODES]
    if any(t["stations"]["mean"] is None or t["missing_ideal_station_fraction"] is None
           or t["station_spacing"]["max_inter_hit_gap_mm"]["p95"] is None for t in totals):
        raise ValueError("Ranking requires eligible tracks and at least two reached stations")
    return dict(mean_stations=sum(t["stations"]["mean"] for t in totals)/len(totals),
                worst_mode_mean_stations=min(t["stations"]["mean"] for t in totals),
                mean_fixed_missing_fraction=sum(t["missing_ideal_station_fraction"] for t in totals)/len(totals),
                worst_mode_p95_inter_station_gap_mm=max(t["station_spacing"]["max_inter_hit_gap_mm"]["p95"] for t in totals),
                worst_mode_p95_boundary_gap_mm=max(t["station_spacing"]["max_boundary_gap_mm"]["p95"] for t in totals),
                sensor_area_m2=area["total"]["sensor_area_m2"],
                active_area_m2=area["total"]["active_area_m2"])


def no_mean_hit_loss(spacing, baseline):
    """No train-mode/subsystem mean station loss relative to the PR25 control."""
    return all(spacing[mode]["per_subdetector"][sub]["stations"]["mean"]+1e-12 >=
               baseline[mode]["per_subdetector"][sub]["stations"]["mean"]
               for mode in MODES for sub in SUBS)


def trial(parameters, config, paths, reference, baseline):
    try:
        layout, service = build_candidate(parameters, config, paths)
        failures = list(service["failures"])
        overlap = geometry.body_overlap_diagnostics(layout)
        if overlap["overlapping_body_pairs"]:
            failures.append("overlapping_body_pairs")
        if layout["metadata"]["host_diagnostics"]["host_overflow_modules"]:
            failures.append("host_overflow_modules")
        record = dict(id=parameters["id"], parameters=parameters, feasible=not failures,
                      failures=failures, area=geometry.summarize(layout),
                      sizing=service["sizing"], fixed_point=layout["metadata"]["optimization"]["fixed_point_history"])
        if not failures:
            spacing = spacing_reports(layout, track_sets(config["training"]), reference)
            record.update(spacing=spacing, score=score(spacing, record["area"]),
                          no_subsystem_mean_hit_loss=no_mean_hit_loss(spacing, baseline))
        return record
    except (ValueError, RuntimeError) as error:
        return dict(id=parameters["id"], parameters=parameters, feasible=False,
                    failures=[type(error).__name__+": "+str(error)])


def select(records):
    feasible = [r for r in records if r["feasible"] and r["no_subsystem_mean_hit_loss"]
                and not r.get("parameters", {}).get("original_pocket_floors", False)]
    if not feasible:
        raise RuntimeError("No feasible candidate preserves every subsystem's mean training hit count")
    coverage = max(feasible, key=lambda r:(r["score"]["worst_mode_mean_stations"],
                     r["score"]["mean_stations"],-r["score"]["worst_mode_p95_boundary_gap_mm"],
                     r["score"]["active_area_m2"],r["id"]))
    gap = min(feasible, key=lambda r:(r["score"]["worst_mode_p95_inter_station_gap_mm"],
                  r["score"]["worst_mode_p95_boundary_gap_mm"],-r["score"]["mean_stations"],r["id"]))
    area = max(feasible, key=lambda r:(r["score"]["active_area_m2"],r["score"]["mean_stations"],r["id"]))
    return dict(coverage=coverage["id"], spacing=gap["id"], area=area["id"])


def retain_case(output, case_id, layout, service, tracks, reference, *, native=False,
                acts_source=None, runtime_manifest=None, native_count=36, seed=0):
    directory = output/"cases"/case_id
    directory.mkdir(parents=True, exist_ok=False)
    summary = dict(id=case_id, status="DES-011 PROTOTYPE; no approval", summary=geometry.summarize(layout),
                   services=dict(routes=service["routes"], supports=service["supports"]),
                   service_checks=service, coverage={}, spacing={}, independent_random_spacing={})
    index = SurfaceIndex(layout)
    worst = {}
    for mode, values in tracks.items():
        coverage = evaluate(layout, values, index=index)
        spacing = evaluate_spacing(layout, values, reference_layers=reference, index=index)
        raw = dict(coverage=coverage.pop("per_track"), spacing=spacing.pop("per_track"))
        summary["independent_random_spacing"][mode] = summarize_cohort(
            row for row in raw["spacing"] if row["track"]["cohort"] == "off_grid")
        with gzip.open(directory/(mode+"-tracks.json.gz"), "wt") as stream:
            json.dump(raw, stream, allow_nan=False)
        summary["coverage"][mode], summary["spacing"][mode] = coverage, spacing
        worst[mode] = sorted(range(len(values)), key=lambda i:(-raw["coverage"]["missing_stations"][i],
                            -raw["spacing"][i]["total"]["station_spacing"]["max_boundary_gap_mm"]))[:4]
    with gzip.open(directory/"layout.json.gz", "wt") as stream:
        json.dump(layout, stream, allow_nan=False)
    chosen = native_sample(tracks, native_count, seed, worst)
    write(directory/"native_tracks.json", chosen)
    write(directory/"summary.json", summary)
    if native:
        if __package__:
            from .acts_validate import validate
        else:
            from acts_validate import validate
        audit = validate(layout, chosen, directory/"acts", acts_source=acts_source)
        if runtime_manifest:
            manifest = read(runtime_manifest)
            if audit["runtime"]["acts_extension_sha256"] != manifest["acts_extension_sha256"]:
                raise RuntimeError("Native runtime differs from declared overlay")
            audit["runtime_overlay"] = manifest
        summary["native"] = audit
        write(directory/"summary.json", summary)
        if not audit["passed"]:
            raise RuntimeError("Native finite-patch audit failed for "+case_id)
    return summary


def report_markdown(study, retained):
    """Portable numerical summary regenerated with each complete study."""
    lines = ["# DES-011 generated placement results", "",
             "PROTOTYPE. Best tested candidates; no global optimum or engineering approval.", "",
             "Selection was frozen on training rays before dense validation. The dense grids",
             "share some training angles; the separately reported random cohort is independent.", "",
             f"Source revision: `{study['source_commit']}`; tracked source dirty: {study['source_dirty']}.", "",
             "| Role | Candidate |", "| --- | --- |"]
    lines += [f"| {role} | {name} |" for role,name in study["selection"].items()]
    lines += [f"| Original-pocket control | {name} |" for name in study.get("comparison_controls", [])]
    lines += ["", "All areas sum sensor/patch surfaces; overlaps are counted. Gaps are 3D path",
              "distances between distinct usable stations, with complete same-module stereo pairs.", "",
              "| Candidate | Physical silicon, m² | Summed active silicon, m² | Mean stations | Worst-mode p95 maximum inter-station gap, mm | Fixed-reference missed stations |",
              "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for name,value in study["holdout_scores"].items():
        lines.append(f"| {name} | {value['sensor_area_m2']:.3f} | {value['active_area_m2']:.3f} | {value['mean_stations']:.4f} | {value['worst_mode_p95_inter_station_gap_mm']:.2f} | {100*value['mean_fixed_missing_fraction']:.3f}% |")
    lines += ["", "## Per-mode and subsystem dense validation", "",
              "Fixed-reference missing fractions refer to the original cobe ideal layers,",
              "including when a candidate moved or refilled them. Candidate-local missing",
              "fractions remain separately available under `coverage` in each summary JSON.", "",
              "| Candidate | Mode | Subsystem | Mean sensor hits | Mean usable stations | Fixed-reference missing | p95 maximum inter-station gap, mm | p95 boundary gap, mm |",
              "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    def number(value):
        return "undefined" if value is None else f"{value:.3f}"
    def percent(value):
        return "undefined" if value is None else f"{100*value:.3f}%"
    for name, case in retained.items():
        for mode, spacing in case["spacing"].items():
            for sub, values in [("total",spacing["total"]),*spacing["per_subdetector"].items()]:
                gaps=values["station_spacing"]
                lines.append(f"| {name} | {mode} | {sub} | {number(values['sensor_hits']['mean'])} | {number(values['stations']['mean'])} | {percent(values['missing_ideal_station_fraction'])} | {number(gaps['max_inter_hit_gap_mm']['p95'])} | {number(gaps['max_boundary_gap_mm']['p95'])} |")
    lines += ["", "## Independent random cohort", "",
              "| Candidate | Mean stations | Fixed-reference missed stations | Worst-mode p95 maximum inter-station gap, mm |",
              "| --- | ---: | ---: | ---: |"]
    for name,value in study["independent_random_scores"].items():
        lines.append(f"| {name} | {value['mean_stations']:.4f} | {100*value['mean_fixed_missing_fraction']:.3f}% | {value['worst_mode_p95_inter_station_gap_mm']:.2f} |")
    lines += ["", "## Search and constraints", "",
              f"Evaluated {len(study['records'])} bounded candidates; {sum(r['feasible'] for r in study['records'])} passed geometry/capacity constraints.",
              "Every parameter set and rejection reason is retained in `study.json`.",
              "Adverse service-budget failures remain in each case summary. Compact pockets,",
              "connector bends, materials, cooling hydraulics and vessel access remain unqualified.", ""]
    return "\n".join(lines)


def run(args):
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    inputs = {"config":args.config, "models":args.models, "layouts":args.layouts,
              "budget":args.budget, "services":args.services, "envelopes":args.envelopes}
    paths = {}
    for key, path in inputs.items():
        target = output/(key+".json")
        target.write_bytes(Path(path).read_bytes())
        paths[key] = str(target.resolve())
    config = read(paths["config"])
    validate_config(config)
    reference = copy.deepcopy(next(c for c in read(paths["layouts"])["candidates"] if c["id"] == config["candidate"])["layers"])
    uncarved, baseline, routes = services.build(read(paths["services"]), paths["models"], paths["layouts"])
    baseline_checks = dict(services=baseline["metadata"]["services"],
        body_diagnostics=geometry.body_overlap_diagnostics(baseline),
        host_diagnostics=geometry.host_diagnostics(baseline),
        interface=services.interface_checks(routes,paths["envelopes"],read(paths["services"])["clearance_mm"]))
    if services.geometry_failures(baseline_checks):
        write(output/"baseline-failures.json",baseline_checks)
        raise RuntimeError("Regenerated PR25 control fails physical validation; inspect baseline-failures.json")
    train = track_sets(config["training"])
    baseline_spacing = spacing_reports(baseline, train, reference)
    study = dict(schema_version=1, status="PROTOTYPE; bounded search; holdout not used for selection",
        source_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        source_dirty=bool(subprocess.check_output(["git","status","--porcelain","--untracked-files=no"],cwd=ROOT,text=True).strip()),
        recorded_at=datetime.now(timezone.utc).isoformat(), python=platform.python_version(),
        code_sha256={p.name:sha(p) for p in HERE.glob("*.py")}, inputs_sha256={key:sha(path) for key,path in paths.items()},
        command=vars(args), baseline="pr25", selected=[], selection={}, records=[],
        baseline_training=baseline_spacing, baseline_score=score(baseline_spacing,geometry.summarize(baseline)))
    write(output/"study.json", study)
    parameters = []
    for pix, short, bypass, half_z, spacing in itertools.product(config["pixel_trunk_inner_mm"],
            config["short_trunk_inner_mm"],config["last_disc_bypass"],
            config["long_barrel_half_z_mm"],config["disc_spacing"]):
        parameters.append(dict(id=f"p{pix:g}-s{short:g}-b{int(bypass)}-l{half_z:g}-{spacing}",
            trunk_inner_mm=[pix,short,config["long_trunk_inner_mm"]],last_disc_bypass=bypass,
            long_barrel_half_z_mm=half_z,disc_spacing=spacing,barrel_offset_mm=0.))
    if args.limit:
        parameters = parameters[:args.limit]
    if len({p["id"] for p in parameters}) != len(parameters):
        raise ValueError("Formatted scan IDs collide; choose distinct parameter values")
    def execute(items):
        with ProcessPoolExecutor(max_workers=args.jobs) as pool:
            futures = [pool.submit(trial,p,config,paths,reference,baseline_spacing) for p in items]
            for future in as_completed(futures):
                record = future.result()
                study["records"].append(record)
                study["records"].sort(key=lambda r:r["id"])
                write(output/"study.json", study)
                print(record["id"], "feasible" if record["feasible"] else record["failures"], flush=True)
    execute(parameters)
    selection = select(study["records"])
    # A bounded second pass moves only intermediate radii of the training winner.
    winner = next(r for r in study["records"] if r["id"] == selection["coverage"])
    extra = []
    for offset in config["barrel_radius_offsets_mm"]:
        if offset:
            p = copy.deepcopy(winner["parameters"])
            p.update(id=p["id"]+f"-barrel{offset:+g}",barrel_offset_mm=offset)
            extra.append(p)
    original = copy.deepcopy(winner["parameters"])
    original.update(id=original["id"]+"-original-pockets",original_pocket_floors=True)
    extra.append(original)
    execute(extra)
    selection = select(study["records"])
    study["selection"] = selection
    study["comparison_controls"] = [r["id"] for r in study["records"]
                                    if r["parameters"].get("original_pocket_floors") and r["feasible"]]
    study["selected"] = sorted(set(selection.values()) | set(study["comparison_controls"]))
    study["selection_frozen_before_holdout"] = True
    write(output/"study.json", study)
    if args.search_only:
        return
    holdout = track_sets(config["holdout"])
    base_service = dict(routes=routes,supports=baseline["metadata"]["services"]["supports"],
                        budget=services_budget.estimate_budget(baseline,read(paths["budget"]),routes),
                        diagnostics=baseline["metadata"]["services"]["diagnostics"],
                        body_diagnostics=baseline_checks["body_diagnostics"],
                        host_diagnostics=baseline_checks["host_diagnostics"],
                        interface=baseline_checks["interface"])
    retained = {}
    cases = [("pr25", baseline, base_service)]
    for case_id in study["selected"]:
        record = next(r for r in study["records"] if r["id"] == case_id)
        layout, service = build_candidate(record["parameters"],config,paths)
        service["body_diagnostics"] = geometry.body_overlap_diagnostics(layout)
        service["host_diagnostics"] = geometry.host_diagnostics(layout)
        if service["body_diagnostics"]["overlapping_body_pairs"]:
            service["failures"].append("overlapping_body_pairs")
        if service["host_diagnostics"]["host_overflow_modules"]:
            service["failures"].append("host_overflow_modules")
        if service["failures"]:
            raise RuntimeError("Regenerated finalist failed service constraints")
        cases.append((case_id,layout,service))
    for case_id, layout, service in cases:
        retained[case_id] = retain_case(output,case_id,layout,service,holdout,reference,
            native=args.native,acts_source=args.acts_source,runtime_manifest=args.runtime_manifest,
            native_count=config["native_tracks_per_case"],seed=config["holdout"]["seed"])
        print(case_id,"holdout and native checks complete",flush=True)
    study["holdout_scores"] = {key:score(value["spacing"],value["summary"]) for key,value in retained.items()}
    study["holdout_no_subsystem_mean_hit_loss"] = {key:no_mean_hit_loss(value["spacing"],retained["pr25"]["spacing"])
                                                 for key,value in retained.items() if key != "pr25"}
    study["independent_random_scores"] = {key:score(value["independent_random_spacing"],value["summary"])
                                           for key,value in retained.items()}
    if {p.name:sha(p) for p in HERE.glob("*.py")} != study["code_sha256"]:
        raise RuntimeError("Source changed during the study; do not publish mixed-revision evidence")
    if {key:sha(path) for key,path in paths.items()} != study["inputs_sha256"]:
        raise RuntimeError("Input snapshots changed during the study")
    study["source_and_inputs_unchanged_at_completion"] = True
    write(output/"study.json",study)
    (output/"results.md").write_text(report_markdown(study,retained))
    write(output/"artifacts.json",dict(files={str(p.relative_to(output)):sha(p) for p in sorted(output.rglob("*")) if p.is_file() and p.name!="artifacts.json"}))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config",default=str(HERE/"optimization_config.json"))
    p.add_argument("--models",default=str(HERE/"review_models.json"))
    p.add_argument("--layouts",default=str(ROOT/"docs/design/DES-006-named-layouts.json"))
    p.add_argument("--budget",default=str(HERE/"services_budget_inputs.json"))
    p.add_argument("--services",default=str(HERE/"services_config.json"))
    p.add_argument("--envelopes",default=str(ROOT/"docs/design/DES-003-envelopes.json"))
    p.add_argument("--output",required=True)
    p.add_argument("--jobs",type=int,default=3)
    p.add_argument("--limit",type=int,help="Development probe only: restrict first-pass candidates")
    p.add_argument("--search-only",action="store_true")
    p.add_argument("--native",action="store_true")
    p.add_argument("--acts-source")
    p.add_argument("--runtime-manifest")
    args=p.parse_args()
    if args.jobs<1:p.error("--jobs must be positive")
    run(args)


if __name__=="__main__":main()
