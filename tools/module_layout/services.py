#!/usr/bin/env python3
"""DES-010 service-space PROTOTYPE; repeatable row removal, never optimization."""
from __future__ import annotations
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess

try:
    from .geometry import generate_layout, body_overlap_diagnostics
    from .services_geometry import (apply_reservations, body_envelope,
                                    reservation_diagnostics, route_connectivity)
except ImportError:
    from geometry import generate_layout, body_overlap_diagnostics
    from services_geometry import (apply_reservations, body_envelope,
                                    reservation_diagnostics, route_connectivity)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SUBSYSTEMS = ("pixel", "short_strip", "long_strip")


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+"\n")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def snapshot_inputs(inputs, output):
    """Preserve exact source bytes so retained files match their declared hashes."""
    hashes = {}
    for name, path in inputs.items():
        content = Path(path).read_bytes()
        (Path(output)/name).write_bytes(content)
        hashes[name] = hashlib.sha256(content).hexdigest()
    return hashes


def route(name, sub, kind, bounds, sign, **extra):
    r0, r1, z0, z1 = bounds
    z0, z1 = (z0, z1) if sign > 0 else (-z1, -z0)
    return dict(id=f"{name}-{'P' if sign>0 else 'N'}", subsystem=sub, kind=kind,
                r_min_mm=r0, r_max_mm=r1, z_min_mm=z0, z_max_mm=z1,
                side="positive" if sign > 0 else "negative",
                **extra)


def basic_routes(layout, config):
    result = []
    for sign in (-1, 1):
        for sub in SUBSYSTEMS:
            result.append(route(sub+"-trunk", sub, "axial", config["trunks_mm"][sub], sign))
            layers = sorted((l for l in layout["layers"] if l["subsystem"] == sub and
                             l["kind"] == "cylinder"), key=lambda l:l["r_m"])
            starts = []
            for layer in layers:
                starts.append(min(body_envelope(b)["r_min_mm"] for b in layout["bodies"]
                                  if b["layer_id"] == layer["id"]))
            ends = starts[1:]+[config["trunks_mm"][sub][1]]
            for index, (r0,r1) in enumerate(zip(starts,ends)):
                result.append(route(f"{sub}-barrel-turn-{index}", sub, "radial",
                    [r0,r1,*config["barrel_bays_abs_z_mm"][sub]], sign,
                    layer_ids=[l["id"] for l in layers[:index+1]], regions=["barrel"]))
    return result


def complete_routes(layout, config, routes):
    routes = list(routes)
    supports = {s["layer_id"]:s for s in layout["metadata"]["services"]["supports"]}
    host_end_mm = layout["metadata"]["host"]["abs_z_max_m"]*1000
    for layer in layout["layers"]:
        if layer["kind"] != "disc":
            continue
        sub, lid = layer["subsystem"], layer["id"]
        s = supports[lid]
        sign = 1 if layer["z_m"] > 0 else -1
        z0 = max(abs(s["z_min_mm"]),abs(s["z_max_mm"]))+config["clearance_mm"]
        routes.append(route(lid+"-collector",sub,"radial",
            [s["r_min_mm"],config["trunks_mm"][sub][1],z0,
             z0+config["disc_collector_depth_mm"][sub]],sign,
            layer_ids=[lid],regions=["endcap"],
            conditional_interface=z0+config["disc_collector_depth_mm"][sub]>host_end_mm))
    for sign in (-1,1):
        inner = [config["trunks_mm"][sub][0] for sub in SUBSYSTEMS]
        outer = [*inner[1:], config["trunks_mm"]["long_strip"][1]]
        for index, (name, r0, r1) in enumerate(zip(
                ("rear-pixel", "rear-pixel-short", "rear-all"), inner, outer)):
            owners = list(SUBSYSTEMS[:index+1])
            routes.append(route(name,"shared","radial",[r0,r1,*config["rear_collector_abs_z_mm"]],sign,
                                owners=owners,conditional_interface=True))
        routes.append(route("common-bore","shared","axial",config["shared_bore_mm"],sign,
                            owners=list(SUBSYSTEMS),conditional_interface=True))
        routes.append(route("vessel-end-handoff","shared","radial",config["vessel_end_exit_mm"],sign,
                            owners=list(SUBSYSTEMS),conditional_interface=True,exit=True))
    # A declared routing tree distinguishes intended flow from incidental
    # geometric contact between envelopes. Every required join is still checked.
    for r in routes:
        side = "P" if r["side"] == "positive" else "N"
        sub = r["subsystem"]
        rid = r["id"]
        target = None
        if "-barrel-turn-" in rid:
            index = int(rid.split("-barrel-turn-")[1].split("-")[0])
            following = f"{sub}-barrel-turn-{index+1}-{side}"
            target = following if any(x["id"] == following for x in routes) else f"{sub}-trunk-{side}"
        elif "-collector-" in rid:
            target = f"{sub}-trunk-{side}"
        elif "-trunk-" in rid:
            target = {"pixel":"rear-pixel", "short_strip":"rear-pixel-short", "long_strip":"rear-all"}[sub]+"-"+side
        elif rid.startswith("rear-pixel-short-"):
            target = "rear-all-"+side
        elif rid.startswith("rear-pixel-"):
            target = "rear-pixel-short-"+side
        elif rid.startswith("rear-all-"):
            target = "common-bore-"+side
        elif rid.startswith("common-bore-"):
            target = "vessel-end-handoff-"+side
        r["connects_to"] = [target] if target else []
    return routes


def interface_checks(routes, envelope_path, clearance_mm=0.):
    """Coarse allocated-volume exclusions; new route space is separately flagged."""
    envelopes = read(envelope_path)
    conflicts, extensions = [], []
    host = next(e for e in envelopes["regions"] if e["id"] == "tracker")
    host_end_mm = host["z_max_m"]*1000
    for r in routes:
        if max(abs(r["z_min_mm"]),abs(r["z_max_mm"])) > host_end_mm:
            extensions.append(r["id"])
        for e in envelopes["regions"]:
            if e["id"] in ("tracker", "tracker_services"):
                continue
            for sign in (-1,1):
                z0,z1=e["z_min_m"]*1000,e["z_max_m"]*1000
                z0,z1=(z0,z1) if sign>0 else(-z1,-z0)
                if (r["r_min_mm"] < e["r_max_m"]*1000+clearance_mm-1e-9
                    and e["r_min_m"]*1000 < r["r_max_mm"]+clearance_mm-1e-9
                    and r["z_min_mm"] < z1+clearance_mm-1e-9
                    and z0 < r["z_max_mm"]+clearance_mm-1e-9):
                    conflicts.append(dict(route=r["id"],region=e["id"],side=sign))
    graph=route_connectivity(routes,clearance_mm)
    neighbours=defaultdict(set)
    declared = ({frozenset((r["id"],other)) for r in routes for other in r.get("connects_to",[])}
                if all("connects_to" in r for r in routes) else None)
    for a,b in graph["edges"]:
        if declared is not None and frozenset((a,b)) not in declared:
            continue
        neighbours[a].add(b);neighbours[b].add(a)
    exits={r["id"] for r in routes if r.get("exit")}
    reached=set(exits); todo=list(exits)
    while todo:
        for n in neighbours[todo.pop()]-reached:
            reached.add(n);todo.append(n)
    return dict(allocated_volume_conflicts=conflicts,
                proposed_beyond_tracker_host=extensions,
                disconnected_from_handoff=sorted({r["id"] for r in routes}-reached),
                status="Conditional space connection only; new rear allocation and engineered vessel access remain unapproved")


def support_inventory(supports):
    totals=defaultdict(lambda:dict(reservations=0,footprint_m2=0.,envelope_volume_litre=0.))
    for s in supports:
        volume=math.pi*(s["r_max_mm"]**2-s["r_min_mm"]**2)*(s["z_max_mm"]-s["z_min_mm"])
        g=totals[s["subsystem"]];g["reservations"]+=1
        g["envelope_volume_litre"]+=volume*1e-6
        g["footprint_m2"]+=volume/s["thickness_mm"]*1e-6
    return dict(totals)


def build(config, models_path, layouts_path):
    baseline=generate_layout(config["candidate"],config["variant"],config["pixel_family"],
                             models_path=models_path,layouts_path=layouts_path)
    primary=basic_routes(baseline,config)
    modified=apply_reservations(baseline,primary,config["support_depths_mm"],config["clearance_mm"])
    routes=complete_routes(modified,config,primary)
    services=modified["metadata"]["services"]
    services["routes"]=routes
    services["diagnostics"]=reservation_diagnostics(modified,routes,services["supports"],config["clearance_mm"])
    return baseline,modified,routes


def geometry_failures(results):
    """Fatal geometry checks; capacity failures remain separately reported evidence."""
    diagnostics = results["services"]["diagnostics"]
    keys = ("route_body_conflicts", "route_support_conflicts", "support_body_conflicts",
            "support_pair_conflicts", "support_host_violations")
    failures = [key for key in keys if diagnostics[key]]
    if results["body_diagnostics"]["overlapping_body_pairs"]:
        failures.append("overlapping_body_pairs")
    if results["host_diagnostics"]["host_overflow_modules"]:
        failures.append("host_overflow_modules")
    for key in ("allocated_volume_conflicts", "disconnected_from_handoff"):
        if results["interface"][key]:
            failures.append(key)
    return failures


def run(args):
    output=Path(args.output);output.mkdir(parents=True,exist_ok=False)
    inputs={"config.json":args.config,"budget_inputs.json":args.budget,
            "models.json":args.models,"layouts.json":args.layouts,
            "sampling.json":args.sampling,"envelopes.json":args.envelopes}
    input_hashes = snapshot_inputs(inputs, output)
    config=read(args.config)
    baseline,modified,routes=build(config,args.models,args.layouts)
    try:
        from .services_budget import estimate_budget
    except ImportError:
        from services_budget import estimate_budget
    results=dict(status="PROTOTYPE; unapproved working hypothesis",
                 source_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True,cwd=ROOT).strip(),
                 source_dirty=bool(subprocess.check_output(["git","status","--porcelain","--untracked-files=no"],text=True,cwd=ROOT).strip()),
                 recorded_at=datetime.now(timezone.utc).isoformat(),python=platform.python_version(),
                 inputs_sha256=input_hashes,
                 code_sha256={p.name:digest(p) for p in HERE.glob("*.py")},
                 argv=vars(args),services=modified["metadata"]["services"],
                 body_diagnostics=body_overlap_diagnostics(modified),
                 host_diagnostics=modified["metadata"]["host_diagnostics"],
                 interface=interface_checks(routes,args.envelopes,config["clearance_mm"]),
                 support_inventory=support_inventory(modified["metadata"]["services"]["supports"]),
                 budget=estimate_budget(modified,read(args.budget),routes),coverage={},native=None)
    write(output/"summary.json",results)
    failures = geometry_failures(results)
    if failures:
        raise RuntimeError("Service-space geometry checks failed: "+", ".join(failures)+
                           "; retained summary contains diagnostics")
    if args.coverage:
        try:
            from .intersections import SurfaceIndex,evaluate
            from .sampling import directions,tracks_for,native_sample
        except ImportError:
            from intersections import SurfaceIndex,evaluate
            from sampling import directions,tracks_for,native_sample
        sampling=read(args.sampling);samples=directions(sampling)
        alltracks={mode:tracks_for(samples,mode,sampling) for mode in ("straight","positive","negative")}
        worst={}
        for label,layout in (("baseline",baseline),("services",modified)):
            index=SurfaceIndex(layout);stats={};raw={}
            for mode,tracks in alltracks.items():
                s=evaluate(layout,tracks,index=index)
                raw[mode]=s.pop("per_track");stats[mode]=s
                if label=="services":
                    worst[mode]=sorted(range(len(tracks)),key=lambda i:(-raw[mode]["missing_stations"][i],raw[mode]["stations"][i]))[:4]
            with gzip.open(output/(label+"-tracks.json.gz"),"wt") as stream:json.dump(raw,stream)
            results["coverage"][label]=stats
            write(output/"summary.json",results)
            print(label,"coverage complete",flush=True)
        for mode in alltracks:
            for metric in ("sensor_hits","stations"):
                if results["coverage"]["services"][mode]["total"][metric]["mean"] > results["coverage"]["baseline"][mode]["total"][metric]["mean"]+1e-12:
                    raise RuntimeError("Removal increased mean hits unexpectedly")
        native_tracks=native_sample(alltracks,sampling["native_tracks_per_case"],sampling["seed"],worst)
        write(output/"native_tracks.json",native_tracks)
        if args.native:
            try:
                from .acts_validate import validate
            except ImportError:
                from acts_validate import validate
            audit=validate(modified,native_tracks,output/"acts",acts_source=args.acts_source)
            if args.runtime_manifest:
                manifest=read(args.runtime_manifest)
                if audit["runtime"]["acts_extension_sha256"]!=manifest["acts_extension_sha256"]:
                    raise RuntimeError("Native extension does not match declared overlay")
                audit["runtime_overlay"]=manifest
            results["native"]=audit;write(output/"summary.json",results)
            if not audit["passed"]:raise RuntimeError("Native finite-patch audit failed")
    write(output/"summary.json",results)
    print(json.dumps({"output":str(output),"removed_modules":len(results["services"]["removed_module_ids"]),
                      "native_passed":results["native"]["passed"] if results["native"] else None}),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",default=str(HERE/"services_config.json"))
    parser.add_argument("--budget",default=str(HERE/"services_budget_inputs.json"))
    parser.add_argument("--models",default=str(HERE/"review_models.json"))
    parser.add_argument("--layouts",default=str(ROOT/"docs/design/DES-006-named-layouts.json"))
    parser.add_argument("--envelopes",default=str(ROOT/"docs/design/DES-003-envelopes.json"))
    parser.add_argument("--sampling",default=str(HERE/"review_config.json"))
    parser.add_argument("--output",required=True)
    parser.add_argument("--coverage",action="store_true")
    parser.add_argument("--native",action="store_true")
    parser.add_argument("--acts-source")
    parser.add_argument("--runtime-manifest")
    args=parser.parse_args()
    if args.native and not args.coverage:parser.error("--native requires --coverage")
    run(args)


if __name__=="__main__":main()
