#!/usr/bin/env python3
"""DES-010 additive downstream service-load profiles; no geometry modification.

A finite collector joins an axial trunk over an interval. The explicitly chosen
``near-edge-full-load`` policy adds its complete source groups at the upstream
edge in |z|. This is conservative within the pickup pocket; it does not locate
individual cables or qualify bends. Existing fixed corridors and their historical
maximum-load budget remain unchanged.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

try:
    from . import services_budget as budget
except ImportError:
    import services_budget as budget

HERE = Path(__file__).resolve().parent
POLICY = "near-edge-full-load"
_EPS = 1e-9


def _hash(content):
    return hashlib.sha256(content).hexdigest()


def _canonical_hash(value):
    return _hash(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def _abs_interval(route):
    return sorted((abs(route["z_min_mm"]), abs(route["z_max_mm"])))


def _group_key(group):
    return (group["side"], group["subsystem"], group["region"], group["layer_id"],
            group["local_index"], group["family"])


def _validated_groups(groups):
    keys, module_ids = set(), set()
    for group in groups:
        key = _group_key(group)
        if key in keys:
            raise ValueError("duplicate retained local-group key")
        keys.add(key)
        mids = group["module_ids"]
        if not mids or len(mids) != len(set(mids)) or len(mids) != group["modules"]:
            raise ValueError("retained local group must contain every unique module exactly once")
        if module_ids.intersection(mids):
            raise ValueError("retained module belongs to more than one local group")
        module_ids.update(mids)


def _acyclic(routes):
    by_id = {r["id"]: r for r in routes}
    visited, active = set(), set()

    def visit(rid):
        if rid in active:
            raise ValueError("cumulative profiles require an acyclic downstream routing graph")
        if rid in visited:
            return
        active.add(rid)
        for target in by_id[rid]["connects_to"]:
            visit(target)
        active.remove(rid)
        visited.add(rid)

    for rid in by_id:
        visit(rid)


def _equivalent_width(demand, route, scenario, boundary):
    """Invert axial annulus capacity at fixed inner radius, including both skins.

    Even zero demand retains two boundary allowances in this equivalent-channel
    convention. This is a diagnostic width, never a proposal to shrink a route.
    """
    fraction = scenario["available_phi_fraction"]*scenario["packing_fraction"]
    if fraction <= 0:
        raise ValueError("equivalent width needs positive packing and azimuth fractions")
    inner = route["r_min_mm"]+boundary
    # Stable difference of squares avoids cancellation for small demand.
    area_over_pi = demand/(fraction*math.pi)
    payload_width = area_over_pi/(math.sqrt(inner*inner+area_over_pi)+inner) if area_over_pi else 0.
    return 2*boundary+payload_width


def _state(groups, route, inputs):
    inventory = budget._inventory(groups, inputs)
    demand = budget._demand(groups, inputs)
    boundary = inputs["capacity"]["boundary_allowance_mm"]
    area = budget._cross_section(route, boundary)
    scenarios = budget._capacity_result(area, demand, inputs)
    for name, record in scenarios.items():
        record["required_annular_width_mm"] = _equivalent_width(
            record["demand_mm2"], route, inputs["scenarios"][name], boundary)
    return dict(module_count=sum(g["modules"] for g in groups), group_count=len(groups),
                layer_ids=sorted({g["layer_id"] for g in groups}),
                counts=dict(inventory["counts"], cooling_trunk_pairs=inventory["cooling_trunk_pairs"]),
                scenarios=scenarios)


def axial_profiles(summary, inputs, *, pickup_policy=POLICY):
    """Profile retained single-owner axial trunks from their immediate feeders.

    Inputs are the retained services summary and its exact budget-input snapshot.
    No layout generator, crossing code or ACTS runtime is invoked. Every whole
    retained local group must enter each profiled trunk exactly once. Cable and
    cooling ceilings are recomputed over the union of those original groups,
    preserving layer/end manifold boundaries and avoiding summed loop ceilings.

    Shared bore routes retain their existing whole-end budget. A profile carries
    accumulated traffic through the trunk's full retained length, including its
    downstream extraction pocket; it does not model traffic draining in that
    pocket. ``terminal`` must reproduce the historical trunk budget exactly.
    """
    if pickup_policy != POLICY:
        raise ValueError("choose the explicit near-edge-full-load pickup policy")
    budget._validate_inputs(inputs)
    retained = summary["budget"]
    if retained["inputs_sha256"] != _canonical_hash(inputs):
        raise ValueError("budget inputs do not match the retained budget hash")
    groups = retained["local_groups"]
    _validated_groups(groups)
    routes = budget._routes(summary["services"]["routes"])
    if budget._declared_edges(routes) is None:
        raise ValueError("cumulative profiles require explicit connects_to on every route")
    _acyclic(routes)
    by_id = {r["id"]: r for r in routes}
    historical = {r["id"]: r for r in retained["routes"]}
    profiles, excluded = [], []
    for trunk in routes:
        if trunk["kind"] != "axial":
            continue
        if len(budget._owners(trunk)) != 1 or trunk["subsystem"] == "shared":
            excluded.append(trunk["id"])
            continue
        if len(trunk["connects_to"]) != 1:
            raise ValueError("a profiled trunk requires one declared downstream handoff")
        original = budget._selected(groups, trunk)
        selected_keys = {_group_key(g) for g in original}
        incoming = [r for r in routes if trunk["id"] in r["connects_to"]]
        if not incoming:
            raise ValueError("profiled trunk has no incoming source branches")
        lo, hi = _abs_interval(trunk)
        assignments = Counter()
        events, event_keys = [], []
        for branch in incoming:
            if "module_ids" in branch:
                raise ValueError("partial per-module selectors are unsupported; preserve whole retained groups")
            if len(branch["connects_to"]) != 1 or branch["kind"] != "radial":
                raise ValueError("profiles require unsplit radial collector/turn feeders")
            selected = budget._selected(groups, branch)
            keys = {_group_key(g) for g in selected}
            if not keys or not keys <= selected_keys:
                raise ValueError("incoming branch must carry whole retained groups inside the trunk's source scope")
            assignments.update(keys)
            blo, bhi = _abs_interval(branch)
            pickup = [max(lo, blo), min(hi, bhi)]
            radial_overlap = min(trunk["r_max_mm"], branch["r_max_mm"])-max(trunk["r_min_mm"], branch["r_min_mm"])
            if pickup[1]-pickup[0] <= _EPS or radial_overlap < -_EPS:
                raise ValueError("incoming branch has no finite longitudinal pickup interval on trunk")
            if budget._side(branch) != budget._side(trunk):
                raise ValueError("incoming branch joins the wrong signed detector end")
            events.append(dict(incoming_route_ids=[branch["id"]],
                               layer_ids=sorted({g["layer_id"] for g in selected}),
                               pickup_abs_z_mm=pickup[0], pickup_abs_z_interval_mm=pickup,
                               modules_added=sum(g["modules"] for g in selected),
                               groups_added=len(selected),
                               module_ids=sorted(mid for g in selected for mid in g["module_ids"])))
            event_keys.append(keys)
        if any(n != 1 for n in assignments.values()):
            raise ValueError("duplicate incoming flow: a retained group enters the trunk more than once")
        if set(assignments) != selected_keys:
            raise ValueError("missing incoming flow: not every retained group enters the trunk")
        order = sorted(range(len(events)), key=lambda i:(events[i]["pickup_abs_z_mm"], events[i]["incoming_route_ids"]))
        events = [events[i] for i in order]
        event_keys = [event_keys[i] for i in order]
        cuts = sorted({lo, hi, *(e["pickup_abs_z_mm"] for e in events)})
        segments = []
        for start, stop in zip(cuts, cuts[1:]):
            present = set().union(*(keys for event, keys in zip(events, event_keys)
                                    if event["pickup_abs_z_mm"] <= start+_EPS))
            chosen = [g for g in original if _group_key(g) in present]
            segments.append(dict(abs_z_min_mm=start, abs_z_max_mm=stop,
                                 **_state(chosen, trunk, inputs)))
        terminal = _state(original, trunk, inputs)
        old = historical[trunk["id"]]
        if terminal["module_count"] != old["modules_carried"]:
            raise ValueError("final module count differs from retained trunk budget")
        for name, state in terminal["scenarios"].items():
            for quantity in ("demand_mm2", "capacity_mm2"):
                if not math.isclose(state[quantity], old["scenarios"][name][quantity], rel_tol=1e-12, abs_tol=1e-9):
                    raise ValueError("final load/capacity differs from retained trunk budget")
            if state["status"] != old["scenarios"][name]["status"]:
                raise ValueError("final capacity status differs from retained trunk budget")
        if not segments or segments[-1]["module_count"] != terminal["module_count"]:
            raise ValueError("full load must be reached before the retained trunk ends")
        target = by_id[trunk["connects_to"][0]]
        tlo, thi = _abs_interval(target)
        handoff = [max(lo, tlo), min(hi, thi)]
        radial_handoff = min(trunk["r_max_mm"], target["r_max_mm"])-max(trunk["r_min_mm"], target["r_min_mm"])
        if (handoff[1] < handoff[0]-_EPS or radial_handoff < -_EPS or
                max(handoff[1]-handoff[0], radial_handoff) <= _EPS):
            raise ValueError("trunk downstream handoff has no finite connection")
        target_keys = {_group_key(g) for g in budget._selected(groups, target)}
        if not selected_keys <= target_keys:
            raise ValueError("downstream handoff loses retained source groups")
        profiles.append(dict(route_id=trunk["id"], subsystem=trunk["subsystem"], side=budget._side(trunk),
                             r_min_mm=trunk["r_min_mm"], r_max_mm=trunk["r_max_mm"],
                             reserved_width_mm=trunk["r_max_mm"]-trunk["r_min_mm"],
                             abs_z_min_mm=lo, abs_z_max_mm=hi, pickup_events=events, segments=segments,
                             full_load_from_abs_z_mm=max(e["pickup_abs_z_mm"] for e in events),
                             downstream_handoff_route_id=target["id"],
                             downstream_handoff_abs_z_interval_mm=handoff,
                             terminal=terminal, matches_retained_maximum=True))
    return dict(schema_version=1, status="PROTOTYPE additive load diagnostic; fixed geometry and budgets unchanged",
                pickup_policy=pickup_policy,
                width_definition="Equivalent annular reservation at fixed inner radius, including two boundary allowances; not a geometry change",
                terminal_policy="Keep accumulated load to retained trunk end; no draining model inside downstream extraction pocket",
                excluded_shared_axial_routes=excluded, profiles=profiles,
                limitations=["Finite pickup interval is recorded; complete branch load enters at its near edge in absolute z.",
                             "Whole retained source groups are unioned before the inherited cable/manifold rounding.",
                             "Constant full-length corridor bounds remain unchanged; this is not taper or layer optimization.",
                             "Feed and return pipe occupancies both accumulate; opposite coolant flow direction does not remove either pipe.",
                             "Shared rear and bore routes retain the previously evaluated full owner demand.",
                             "No new geometry, coverage, material, electrical or hydraulic validation is implied."])


def export(run, output, *, pickup_policy=POLICY):
    """Write a fresh additive evidence bundle after checking retained provenance."""
    run, output = Path(run), Path(output)
    summary_bytes = (run/"summary.json").read_bytes()
    summary = json.loads(summary_bytes)
    for name, expected in summary["inputs_sha256"].items():
        if Path(name).name != name or _hash((run/name).read_bytes()) != expected:
            raise RuntimeError("Retained input hash mismatch: "+name)
    for name in ("geometry.py", "services_geometry.py", "services.py", "services_budget.py"):
        if _hash((HERE/name).read_bytes()) != summary["code_sha256"][name]:
            raise RuntimeError("Retained producer code differs: "+name)
    budget_bytes = (run/"budget_inputs.json").read_bytes()
    result = axial_profiles(summary, json.loads(budget_bytes), pickup_policy=pickup_policy)
    result["provenance"] = dict(
                                profile_source_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=HERE, text=True).strip(),
                                profile_source_dirty=bool(subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=HERE, text=True).strip()),
                                recorded_at=datetime.now(timezone.utc).isoformat(), python=platform.python_version(),
                                source_run=str(run), source_summary_sha256=_hash(summary_bytes),
                                source_commit=summary["source_commit"],
                                source_inputs_sha256=summary["inputs_sha256"],
                                producer_code_sha256={name:summary["code_sha256"][name] for name in
                                                      ("geometry.py", "services_geometry.py", "services.py", "services_budget.py")},
                                profile_code_sha256=_hash(Path(__file__).read_bytes()),
                                command=list(sys.argv))
    output.mkdir(parents=True, exist_ok=False)
    (output/"budget_inputs.json").write_bytes(budget_bytes)
    (output/"profile.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--pickup-policy", required=True, choices=[POLICY])
    args = parser.parse_args()
    export(args.run, args.output, pickup_policy=args.pickup_policy)
