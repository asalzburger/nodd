"""DES-011 PROTOTYPE: inventory-sized, constant-width tracker services.

This additive builder never moves, removes or repopulates a module. It returns
placement constraints and rejects insufficient space through explicit failures.
Sizing is minimal only for the supplied inventory, topology, area model, floors
and rounding; connector bends and hydraulic/electrical feasibility are unsigned.
The DES-010 producer and its reference evidence remain unchanged.
"""
from __future__ import annotations

from collections import defaultdict
import copy
import math

try:
    from .services_budget import (
        SUBSYSTEMS, SIDES, _demand, _groups, _selected, _validate_inputs,
        estimate_budget,
    )
    from .services_geometry import body_envelope, support_envelopes, reservation_diagnostics
except ImportError:
    from services_budget import (
        SUBSYSTEMS, SIDES, _demand, _groups, _selected, _validate_inputs,
        estimate_budget,
    )
    from services_geometry import body_envelope, support_envelopes, reservation_diagnostics

_EPS = 1e-8


def default_policy():
    """Return independent, explicitly unsigned DES-011 study choices, in mm.

    Original DES-010 barrel/disc depth floors are retained by default. Setting
    those named floors to 10 mm defines an *unqualified* lower-space sensitivity,
    not an engineered minimum. The separate area boundary skins come from the
    budget input, not from assembly clearance. capacity_factor=1.1 means capacity
    at least 1.1 times demand (9.09% of capacity remains), not 10% unused capacity.
    """
    return dict(
        trunk_r_min_mm=dict(pixel=170., short_strip=635., long_strip=1144.),
        support_depths_mm=dict(pixel=5., short_strip=6.6, long_strip=6.6),
        clearance_mm=2., minimum_barrel_disc_clearance_mm=10.,
        capacity_factor=1.1, rounding_mm=1., sizing_scenario="reference",
        bypass_last_disc=False,
        barrel_bay_floor_mm=dict(pixel=50., short_strip=80., long_strip=90.),
        disc_collector_floor_mm=dict(pixel=50., short_strip=90., long_strip=90.),
        rear_collector_floor_mm=150., exit_floor_mm=90.,
        rear_start_abs_z_mm=3150., common_bore_r_min_mm=1040.,
        rear_all_r_min_mm=1040., outer_radius_limit_mm=1220.,
        exit_r_min_mm=1040., exit_r_max_mm=1680.,
        exit_abs_z_window_mm=[3555., 3645.],
    )


def _policy(policy, inputs):
    p = copy.deepcopy(default_policy() if policy is None else policy)
    required = set(default_policy())
    if set(p) != required:
        raise ValueError(f"policy keys differ: missing={sorted(required-set(p))}, "
                         f"unknown={sorted(set(p)-required)}")
    maps = ("trunk_r_min_mm", "support_depths_mm", "barrel_bay_floor_mm", "disc_collector_floor_mm")
    for name in maps:
        if set(p[name]) != set(SUBSYSTEMS):
            raise ValueError(name+" must specify all three subsystems")
    numbers = [(name+"."+sub, p[name][sub]) for name in maps for sub in SUBSYSTEMS]
    numbers += [(name, value) for name, value in p.items()
                if name not in (*maps, "sizing_scenario", "bypass_last_disc", "exit_abs_z_window_mm")]
    if not isinstance(p["exit_abs_z_window_mm"], (list, tuple)) or len(p["exit_abs_z_window_mm"]) != 2:
        raise ValueError("exit_abs_z_window_mm must have two bounds")
    numbers += [("exit_abs_z_window_mm", v) for v in p["exit_abs_z_window_mm"]]
    for name, value in numbers:
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or value < 0:
            raise ValueError(name+" must be finite and nonnegative")
    if not isinstance(p["bypass_last_disc"], bool):
        raise ValueError("bypass_last_disc must be boolean")
    if p["rounding_mm"] <= 0 or p["capacity_factor"] < 1:
        raise ValueError("positive rounding_mm and capacity_factor >= 1 are required")
    if p["sizing_scenario"] not in inputs["scenarios"]:
        raise ValueError("unknown sizing_scenario")
    if p["minimum_barrel_disc_clearance_mm"] < 10:
        raise ValueError("DES-011 requires at least 10 mm barrel/disc clearance")
    inner = [p["trunk_r_min_mm"][s] for s in SUBSYSTEMS]
    if not 0 < inner[0] < inner[1] < p["rear_all_r_min_mm"] <= inner[2] < p["outer_radius_limit_mm"]:
        raise ValueError("trunk/rear radial anchors must have ordered positive spacing")
    if not 0 < p["common_bore_r_min_mm"] < p["outer_radius_limit_mm"] or not 0 < p["exit_r_min_mm"] < p["exit_r_max_mm"]:
        raise ValueError("common/exit radial anchors must have positive spacing")
    if not 0 < p["rear_start_abs_z_mm"] < p["exit_abs_z_window_mm"][0] < p["exit_abs_z_window_mm"][1]:
        raise ValueError("rear and exit axial anchors must be ordered")
    scenario = inputs["scenarios"][p["sizing_scenario"]]
    if scenario["available_phi_fraction"]*scenario["packing_fraction"] <= 0:
        raise ValueError("sizing scenario must provide nonzero packing and azimuth")
    return p


def _route(name, sub, kind, r0, r1, z0, z1, side, role, targets, **extra):
    suffix = "P" if side == "positive" else "N"
    lo, hi = (z0, z1) if side == "positive" else (-z1, -z0)
    return dict(id=name+"-"+suffix, subsystem=sub, kind=kind, side=side, role=role,
                r_min_mm=r0, r_max_mm=r1, z_min_mm=lo, z_max_mm=hi,
                connects_to=[t+"-"+suffix for t in targets], **extra)


def _round_transport_components(groups, inputs):
    """Known round components actually charged by these whole source groups.

    These are the existing DES-010 comparator outer diameters, not new sourced
    component choices. Positive strip leaf counts imply at least one downstream
    manifold trunk pair under the unchanged within-layer rounding rule. Pixel
    ancillary bundles have an area-only normalization and no fixed aspect ratio
    in these inputs; this necessary circular-envelope check does not qualify them.
    """
    pixel = [g for g in groups if g["subsystem"] == "pixel"]
    strip = [g for g in groups if g["subsystem"] in ("short_strip", "long_strip")]
    keys = []
    if any(g["cooling_leaf_loops"] > 0 for g in pixel):
        keys += [("pixel", "feed_outer_diameter_mm"), ("pixel", "return_outer_diameter_mm")]
    if any(g["harnesses"] > 0 for g in strip):
        keys += [("strip", "power_cable_outer_diameter_mm"), ("strip", "fibre_cable_outer_diameter_mm")]
    if any(g["cooling_leaf_loops"] > 0 for g in strip):
        keys += [("strip", "trunk_feed_outer_diameter_mm"), ("strip", "trunk_return_outer_diameter_mm")]
    return [dict(input_key=f"{owner}.{key}", outer_diameter_mm=inputs[owner][key]) for owner, key in keys]


def _round_transport_diameter(groups, inputs):
    return max((c["outer_diameter_mm"] for c in _round_transport_components(groups, inputs)), default=0.)


def transport_envelope_checks(groups, inputs, routes):
    """Check necessary individual cable/pipe fit on routes and declared joins.

    Radial routes need axial depth, axial routes need radial width, and overlap
    pockets need both. At a face handoff the finite transverse opening limits
    the fit. Boundary skins are removed on both sides. Only source groups shared
    by the two joined routes are charged to a throat. Thus a pixel branch joining
    a shared trunk is checked against its own traffic, while the downstream route
    is separately checked against all traffic it carries. This check is necessary
    and not sufficient: bends, fittings, manifolds and non-round bundles remain
    unqualified. It may audit retained DES-010/011 budget groups without rerunning
    geometry or changing an old producer's evidence.
    """
    boundary = inputs["capacity"]["boundary_allowance_mm"]
    by_id = {r["id"]: r for r in routes}
    selected = {rid:_selected(groups, r) for rid, r in by_id.items()}

    def check(label, kind, dimension, source_groups, direction):
        components = _round_transport_components(source_groups, inputs)
        diameter = max((c["outer_diameter_mm"] for c in components), default=0.)
        clear = max(0., dimension-2*boundary)
        return dict(id=label, kind=kind, direction=direction,
            modules_carried=sum(g["modules"] for g in source_groups),
            components=components, largest_known_outer_diameter_mm=diameter,
            gross_transverse_mm=dimension, available_clear_transverse_mm=clear,
            required_gross_transverse_mm=diameter+2*boundary if diameter else 0.,
            status="PASS" if diameter <= clear+_EPS else "FAIL")

    route_checks, throat_checks = [], []
    for r in routes:
        dr = r["r_max_mm"]-r["r_min_mm"]
        dz = r["z_max_mm"]-r["z_min_mm"]
        dimension = dr if r["kind"] == "axial" else dz if r["kind"] == "radial" else min(dr, dz)
        direction = "radial width" if r["kind"] == "axial" else "axial depth" if r["kind"] == "radial" else "minimum radial width/axial depth"
        route_checks.append(check(r["id"], "route", dimension, selected[r["id"]], direction))
    seen = set()
    for a in routes:
        for target in a["connects_to"]:
            edge = tuple(sorted((a["id"], target)))
            if edge in seen:
                continue
            seen.add(edge)
            b = by_id[target]
            dr = min(a["r_max_mm"], b["r_max_mm"])-max(a["r_min_mm"], b["r_min_mm"])
            dz = min(a["z_max_mm"], b["z_max_mm"])-max(a["z_min_mm"], b["z_min_mm"])
            b_ids = {mid for g in selected[target] for mid in g["module_ids"]}
            shared = [g for g in selected[a["id"]] if set(g["module_ids"]) <= b_ids]
            if dr < -_EPS or dz < -_EPS or max(dr, dz) <= _EPS:
                dimension, direction = 0., "no finite contact"
            elif abs(dz) <= _EPS:
                dimension, direction = dr, "axial face: radial width"
            elif abs(dr) <= _EPS:
                dimension, direction = dz, "radial face: axial depth"
            else:
                dimension, direction = min(dr, dz), "overlap: minimum radial width/axial depth"
            throat_checks.append(check(" -> ".join(edge), "throat", dimension, shared, direction))
    return dict(boundary_allowance_mm=boundary, routes=route_checks, throats=throat_checks,
        all_pass=all(c["status"] == "PASS" for c in route_checks+throat_checks),
        definition="Necessary fit of actually charged known round cable/pipe envelopes, including both boundary skins",
        limitations=["Diameter fit does not qualify bend radius, fittings, manifolds or installation.",
                     "Pixel ancillary/control bundle aspect ratios are not fixed by their area normalization.",
                     "The largest charged cable or pipe diameter governs; a power cable can exceed the cooling-pipe diameter."])


def build_optimized_services(layout, inputs, policy=None, *, diagnostics=True):
    """Return service geometry and constraints without mutating ``layout``.

    ``placement_constraints[side][subsystem]`` gives the bay absolute-z bounds,
    exact first-disc minimum body/nominal-centre position, and ordered per-disc
    front/back offsets and following clearance requirements. ``sizing`` records
    rounded symmetric trunk widths, source partitions and capacity-margin checks.
    ``failures`` includes geometry/space/margin failures; it is never a silent
    fallback to lower inventory or a larger global allocation. With diagnostics
    False only the expensive body/support exclusions are skipped; capacity and
    finite graph/throat checks still run. Such output cannot qualify geometry.

    Each last-disc bypass occupies that disc's radial shadow *behind* its outward
    support, disjoint from the subsystem trunk, and joins the full-inventory rear
    collector through an explicit radial branch. It is conditional reserved space,
    not an assertion that a routed cable is already engineered there.
    """
    _validate_inputs(inputs)
    p = _policy(policy, inputs)
    boundary = inputs["capacity"]["boundary_allowance_mm"]
    scenario = inputs["scenarios"][p["sizing_scenario"]]
    packing = scenario["available_phi_fraction"]*scenario["packing_fraction"]
    margin = p["capacity_factor"]
    quantum = p["rounding_mm"]
    clearance = p["clearance_mm"]

    def rounded(value):
        return math.ceil(value/quantum)*quantum

    def area_demand(groups):
        return _demand(groups, inputs)[p["sizing_scenario"]]

    def outer_for(r0, demand, selected):
        return max(math.sqrt((r0+boundary)**2+margin*demand/(math.pi*packing))+boundary,
                   r0+2*boundary+_round_transport_diameter(selected, inputs))

    def depth_for(r0, demand, selected):
        if r0 <= 0:
            raise ValueError("radial service routes require a positive inner radius")
        return 2*boundary+max(margin*demand/(2*math.pi*r0*packing),
                              _round_transport_diameter(selected, inputs))

    groups = _groups(layout, inputs)
    supports = support_envelopes(layout, p["support_depths_mm"])
    support_by_layer = {s["layer_id"]: s for s in supports}
    bodies = defaultdict(list)
    for body in layout["bodies"]:
        bodies[body["layer_id"]].append(body)
    layers = {}
    for layer in layout["layers"]:
        if layer["id"] in layers:
            raise ValueError("duplicate layer ID")
        if layer["id"] not in bodies:
            raise ValueError("every original layer must retain at least one body")
        if layer["kind"] not in ("cylinder", "disc"):
            raise ValueError("optimization services require cylinders/discs")
        layers[layer["id"]] = layer
    if set(bodies) != set(layers):
        raise ValueError("bodies must refer to known layers")
    envelopes = {lid: [body_envelope(b) for b in bs] for lid, bs in bodies.items()}
    records, constraints = {}, {side:{} for side in SIDES}
    failures = []

    # Inventory and geometric offsets are independent of the caller's z solver.
    for side in SIDES:
        sign = 1 if side == "positive" else -1
        for sub in SUBSYSTEMS:
            barrel = sorted((l for l in layers.values() if l["subsystem"] == sub and l["kind"] == "cylinder"),
                            key=lambda l: min(e["r_min_mm"] for e in envelopes[l["id"]]))
            discs = sorted((l for l in layers.values() if l["subsystem"] == sub and l["kind"] == "disc"
                            and l["z_m"]*sign > 0), key=lambda l: abs(l["z_m"]))
            if not barrel or not discs:
                raise ValueError(f"require barrel and endcap layers for {sub}/{side}")
            end_groups = [g for g in groups if g["side"] == side and g["subsystem"] == sub]
            if not end_groups or any(not any(g["layer_id"] == l["id"] for g in end_groups)
                                     for l in barrel+discs):
                raise ValueError(f"every layer needs routed groups on its detector end: {sub}/{side}")
            bypass_id = discs[-1]["id"] if p["bypass_last_disc"] else None
            main_groups = [g for g in end_groups if g["layer_id"] != bypass_id]
            bypass_groups = [g for g in end_groups if g["layer_id"] == bypass_id]
            starts = [min(e["r_min_mm"] for e in envelopes[l["id"]]) for l in barrel]
            prefixes = [[g for g in end_groups if g["region"] == "barrel"
                         and g["layer_id"] in {l["id"] for l in barrel[:i+1]}]
                        for i in range(len(barrel))]
            prefix_demands = [area_demand(gs) for gs in prefixes]
            bay_depth = rounded(max(p["barrel_bay_floor_mm"][sub],
                                    *(depth_for(r0, demand, gs) for r0, demand, gs in zip(starts, prefix_demands, prefixes))))
            barrel_end = max(sign*e["z_max_mm" if sign > 0 else "z_min_mm"]
                             for l in barrel for e in envelopes[l["id"]])
            bay_start = rounded(barrel_end+clearance)
            body_min = max(barrel_end+p["minimum_barrel_disc_clearance_mm"],
                           bay_start+bay_depth+clearance)
            disc_records = []
            for disc in discs:
                lid = disc["id"]
                ee = envelopes[lid]
                lo = min(sign*e["z_min_mm" if sign > 0 else "z_max_mm"] for e in ee)
                hi = max(sign*e["z_max_mm" if sign > 0 else "z_min_mm"] for e in ee)
                centre = abs(disc["z_m"])*1000
                if lo <= 0:
                    raise ValueError("a disc assembly cannot cross the detector midplane")
                front, back = centre-lo, hi-centre
                r0, r1 = min(e["r_min_mm"] for e in ee), max(e["r_max_mm"] for e in ee)
                selected = [g for g in end_groups if g["layer_id"] == lid]
                demand = area_demand(selected)
                depth = rounded(max(p["disc_collector_floor_mm"][sub], depth_for(r0, demand, selected)))
                support = support_by_layer.get(lid)
                support_end = (max(abs(support["z_min_mm"]), abs(support["z_max_mm"]))
                               if support else hi)
                disc_records.append(dict(layer_id=lid, nominal_center_abs_z_mm=centre,
                    body_min_abs_z_mm=lo, body_max_abs_z_mm=hi, front_offset_mm=front,
                    back_offset_mm=back, body_half_depth_mm=max(front, back),
                    support_depth_mm=p["support_depths_mm"][sub],
                    collector_depth_mm=depth,
                    collector_start_abs_z_mm=support_end+clearance,
                    minimum_gap_to_next_body_mm=p["support_depths_mm"][sub]+depth+2*clearance,
                    r_min_mm=r0, r_max_mm=r1, demand_mm2=demand, bypass=lid == bypass_id))
            constraints[side][sub] = dict(barrel_end_abs_z_mm=barrel_end,
                barrel_bay_abs_z_mm=[bay_start, bay_start+bay_depth],
                minimum_first_disc_body_abs_z_mm=body_min,
                minimum_first_disc_center_abs_z_mm=body_min+disc_records[0]["front_offset_mm"],
                disc_layers=disc_records)
            records[side, sub] = dict(barrel=barrel, discs=disc_records, starts=starts,
                prefix_demands=prefix_demands, bay_depth=bay_depth, end_groups=end_groups,
                main_groups=main_groups, bypass_groups=bypass_groups, bypass_id=bypass_id)
            if disc_records[0]["body_min_abs_z_mm"] < body_min-_EPS:
                failures.append(f"first_disc_clearance:{sub}:{side}")

    # One width for both detector ends. Narrow branch intersections can set the
    # limit even when the full-trunk area inequality would permit less width.
    trunks = {}
    for sub in SUBSYSTEMS:
        inner = p["trunk_r_min_mm"][sub]
        limits = []
        for side in SIDES:
            record = records[side, sub]
            limits.append(dict(source=side+":main_inventory", required_outer_mm=outer_for(inner, area_demand(record["main_groups"]), record["main_groups"])))
            limits.append(dict(source=side+":barrel_join", required_outer_mm=outer_for(
                max(inner, record["starts"][-1]), record["prefix_demands"][-1],
                [g for g in record["end_groups"] if g["region"] == "barrel"])))
            for disc in record["discs"]:
                if not disc["bypass"]:
                    limits.append(dict(source=side+":"+disc["layer_id"], required_outer_mm=outer_for(
                        max(inner, disc["r_min_mm"]), disc["demand_mm2"],
                        [g for g in record["end_groups"] if g["layer_id"] == disc["layer_id"]])))
        width = rounded(max(item["required_outer_mm"] for item in limits)-inner)
        trunks[sub] = dict(r_min_mm=inner, r_max_mm=inner+width, width_mm=width,
                           unrounded_width_mm=max(item["required_outer_mm"] for item in limits)-inner,
                           limiting_requirements=limits)
        if inner+width > p["outer_radius_limit_mm"]+_EPS:
            failures.append("outer_radius_limit:"+sub)
    for left, right in zip(SUBSYSTEMS, SUBSYSTEMS[1:]):
        if trunks[left]["r_max_mm"]+clearance > trunks[right]["r_min_mm"]+_EPS:
            failures.append("overlapping_subsystem_corridors:"+left+":"+right)

    routes, partitions, downstream = [], [], {}
    rear_names = ("rear-pixel", "rear-pixel-short", "rear-all")
    rear_starts = [trunks["pixel"]["r_min_mm"], trunks["short_strip"]["r_min_mm"], p["rear_all_r_min_mm"]]
    for side in SIDES:
        side_groups = [g for g in groups if g["side"] == side]
        rear_demands = [area_demand([g for g in side_groups if g["subsystem"] in SUBSYSTEMS[:i+1]])
                        for i in range(len(SUBSYSTEMS))]
        full_demand = rear_demands[-1]
        common_join_inner = max(p["rear_all_r_min_mm"], p["common_bore_r_min_mm"])
        exit_join_inner = max(p["exit_r_min_mm"], p["common_bore_r_min_mm"])
        common_outer = rounded(max(trunks["long_strip"]["r_max_mm"],
            outer_for(common_join_inner, full_demand, side_groups), outer_for(exit_join_inner, full_demand, side_groups)))
        if common_outer > p["outer_radius_limit_mm"]+_EPS:
            failures.append("outer_radius_limit:common_bore:"+side)
        rear_ends = rear_starts[1:]+[common_outer]
        rear_depths = [depth_for(r0, demand, [g for g in side_groups if g["subsystem"] in SUBSYSTEMS[:i+1]])
                       for i, (r0, demand) in enumerate(zip(rear_starts, rear_demands))]
        rear_depths += [depth_for(common_join_inner, full_demand, side_groups)]
        for sub in SUBSYSTEMS:
            record = records[side, sub]
            if record["bypass_id"]:
                rear_depths.append(depth_for(record["discs"][-1]["r_min_mm"],
                                            area_demand(record["bypass_groups"]), record["bypass_groups"]))
        rear_depth = rounded(max(p["rear_collector_floor_mm"], *rear_depths))
        rear_start = max(p["rear_start_abs_z_mm"], max(
            d["collector_start_abs_z_mm"] for sub in SUBSYSTEMS for d in records[side, sub]["discs"]))
        rear_end = rear_start+rear_depth
        exit_depth = rounded(max(p["exit_floor_mm"], depth_for(p["exit_r_min_mm"], full_demand, side_groups),
                                 depth_for(exit_join_inner, full_demand, side_groups)))
        exit_start = p["exit_abs_z_window_mm"][0]
        exit_end = exit_start+exit_depth
        if exit_end > p["exit_abs_z_window_mm"][1]+_EPS:
            failures.append("exit_window_capacity:"+side)
        if rear_end > exit_start+_EPS:
            failures.append("rear_collector_reaches_exit_window:"+side)
        downstream[side] = dict(rear_collector_abs_z_mm=[rear_start, rear_end],
            common_r_min_mm=p["common_bore_r_min_mm"], common_r_max_mm=common_outer,
            exit_abs_z_mm=[exit_start, exit_end], full_demand_mm2=full_demand)

        for index, sub in enumerate(SUBSYSTEMS):
            rec = records[side, sub]
            trunk = trunks[sub]
            bay_start, bay_end = constraints[side][sub]["barrel_bay_abs_z_mm"]
            main_ids = sorted({g["layer_id"] for g in rec["main_groups"]})
            trunk_end = max([rear_end]+[d["collector_start_abs_z_mm"]+d["collector_depth_mm"]
                                       for d in rec["discs"] if not d["bypass"]])
            routes.append(_route(sub+"-trunk", sub, "axial", trunk["r_min_mm"], trunk["r_max_mm"],
                bay_start, trunk_end, side, "subsystem_trunk", [rear_names[index]], layer_ids=main_ids))
            ends = rec["starts"][1:]+[trunk["r_max_mm"]]
            for i, (r0, r1) in enumerate(zip(rec["starts"], ends)):
                target = f"{sub}-barrel-turn-{i+1}" if i+1 < len(ends) else sub+"-trunk"
                routes.append(_route(f"{sub}-barrel-turn-{i}", sub, "radial", r0, r1,
                    bay_start, bay_end, side, "barrel_turn", [target], regions=["barrel"],
                    layer_ids=[l["id"] for l in rec["barrel"][:i+1]]))
            for disc in rec["discs"]:
                lid = disc["layer_id"]
                if not disc["bypass"]:
                    routes.append(_route(lid+"-collector", sub, "radial", disc["r_min_mm"], trunk["r_max_mm"],
                        disc["collector_start_abs_z_mm"], disc["collector_start_abs_z_mm"]+disc["collector_depth_mm"],
                        side, "disc_collector", [sub+"-trunk"], layer_ids=[lid], regions=["endcap"]))
                else:
                    shadow_outer = min(disc["r_max_mm"], trunk["r_min_mm"]-clearance)
                    if shadow_outer <= disc["r_min_mm"]+_EPS:
                        raise ValueError(f"no disjoint radial shadow for final-disc bypass: {lid}")
                    routes.append(_route(sub+"-last-disc-bypass", sub, "axial", disc["r_min_mm"], shadow_outer,
                        disc["collector_start_abs_z_mm"], rear_end, side, "last_disc_bypass",
                        [sub+"-last-disc-bypass-turn"], layer_ids=[lid], regions=["endcap"],
                        conditional_interface=True))
                    routes.append(_route(sub+"-last-disc-bypass-turn", sub, "radial", disc["r_min_mm"], rear_ends[index],
                        rear_start, rear_end, side, "last_disc_bypass_turn", [rear_names[index]],
                        layer_ids=[lid], regions=["endcap"], conditional_interface=True))
            main_modules = {mid for g in rec["main_groups"] for mid in g["module_ids"]}
            bypass_modules = {mid for g in rec["bypass_groups"] for mid in g["module_ids"]}
            all_modules = {mid for g in rec["end_groups"] for mid in g["module_ids"]}
            if main_modules & bypass_modules or main_modules | bypass_modules != all_modules:
                raise ValueError("main/bypass source partition loses or duplicates modules")
            partitions.append(dict(side=side, subsystem=sub, main_layer_ids=main_ids,
                bypass_layer_id=rec["bypass_id"], main_modules=len(main_modules),
                bypass_modules=len(bypass_modules), all_modules=len(all_modules),
                disjoint_and_complete=True))
        for i, (name, r0, r1) in enumerate(zip(rear_names, rear_starts, rear_ends)):
            target = rear_names[i+1] if i+1 < len(rear_names) else "common-bore"
            routes.append(_route(name, "shared", "radial", r0, r1, rear_start, rear_end,
                side, "rear_collector", [target], owners=list(SUBSYSTEMS[:i+1]), conditional_interface=True))
        routes.append(_route("common-bore", "shared", "axial", p["common_bore_r_min_mm"], common_outer,
            rear_start, exit_end, side, "common_bore", ["vessel-end-handoff"],
            owners=list(SUBSYSTEMS), conditional_interface=True))
        routes.append(_route("vessel-end-handoff", "shared", "radial", p["exit_r_min_mm"], p["exit_r_max_mm"],
            exit_start, exit_end, side, "vessel_end_handoff", [], owners=list(SUBSYSTEMS),
            conditional_interface=True, exit=True))

    # Exact original counting/manifold rounding and all finite declared throats.
    budget = estimate_budget(layout, inputs, routes)
    transport = transport_envelope_checks(groups, inputs, routes)
    for item in transport["routes"]+transport["throats"]:
        if item["status"] == "FAIL":
            failures.append("individual_transport_envelope:"+item["id"])
    checks = []
    for kind in ("routes", "throats"):
        for item in budget[kind]:
            s = item["scenarios"][p["sizing_scenario"]]
            passed = s["capacity_mm2"]+_EPS >= margin*s["demand_mm2"]
            label = item["id"] if kind == "routes" else " -> ".join(item["routes"])
            checks.append(dict(kind=kind, id=label, demand_mm2=s["demand_mm2"],
                required_capacity_mm2=margin*s["demand_mm2"], capacity_mm2=s["capacity_mm2"],
                status="PASS" if passed else "FAIL"))
            if not passed:
                failures.append("sizing_capacity:"+label)
    # Physical route scopes must implement the asserted main/bypass partition.
    for side in SIDES:
        terminal = next(r for r in routes if r["side"] == side and r["role"] == "vessel_end_handoff")
        terminal_ids = {mid for g in _selected(groups, terminal) for mid in g["module_ids"]}
        source_ids = {mid for g in groups if g["side"] == side for mid in g["module_ids"]}
        if terminal_ids != source_ids:
            raise ValueError("terminal route must carry every signed-end source module")
    diagnostic_result = (reservation_diagnostics(layout, routes, supports, clearance) if diagnostics
                         else dict(skipped=True, reason="Caller requested sizing only; geometry is unvalidated"))
    if diagnostics:
        for key in ("route_body_conflicts", "route_support_conflicts", "support_body_conflicts",
                    "support_pair_conflicts", "support_host_violations"):
            if diagnostic_result[key]:
                failures.append(key)
    return dict(status="PROTOTYPE; unqualified service space and unsigned tracker placement",
        policy=p, routes=routes, supports=supports, budget=budget, diagnostics=diagnostic_result,
        placement_constraints=constraints, failures=sorted(set(failures)),
        sizing=dict(scenario=p["sizing_scenario"], capacity_factor=margin,
            boundary_allowance_mm=boundary, trunks=trunks, downstream=downstream,
            source_partitions=partitions, capacity_checks=checks,
            individual_transport_envelopes=transport,
            all_sizing_capacities_pass=all(c["status"] == "PASS" for c in checks),
            method="Minimum rounded widths/depths for this inventory, declared topology and named floors; no global optimum",
            limitations=["Area capacity does not qualify bends, connectors, mechanics or cooling.",
                         "Final-disc bypass occupies its downstream radial shadow as a separate conditional reservation.",
                         "Reference/adverse inventory and manifold rounding use the unchanged DES-010 budget.",
                         "Global allocated-volume exclusions and body OBB checks remain caller obligations."]))
