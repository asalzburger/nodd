"""PROTOTYPE: group actual retained modules and test service-space capacity.

Cable envelopes are engineering comparators. A capacity PASS establishes only
an area inequality under named packing/grouping hypotheses. It does not qualify
power, bandwidth, bends, cooling or manufacture. No production geometry changes.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import copy
import hashlib
import json
import math
from pathlib import Path

INPUTS_PATH = Path(__file__).with_name("services_budget_inputs.json")
SUBSYSTEMS = ("pixel", "short_strip", "long_strip")
SIDES = ("positive", "negative")
_EPS = 1e-9


def load_inputs(path=INPUTS_PATH):
    return json.loads(Path(path).read_text())


def _number(value, label, *, allow_zero=False, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} must be finite numeric")
    if value < 0 or (not allow_zero and value == 0) or (integer and int(value) != value):
        raise ValueError(f"{label} must be {'nonnegative' if allow_zero else 'positive'}"
                         + (" integer" if integer else ""))
    return value


def _validate_inputs(inputs):
    if inputs.get("schema_version") != 1:
        raise ValueError("service budget schema_version must be 1")
    for group in ("pixel", "strip", "capacity"):
        for key, value in inputs[group].items():
            _number(value, f"{group}.{key}", allow_zero=group == "capacity",
                    integer=(key.startswith("max_") or key.endswith("_per_leaf")))
    if set(inputs["scenarios"]) != {"reference", "conservative", "stress"}:
        raise ValueError("require reference, conservative and stress scenarios")
    for name, scenario in inputs["scenarios"].items():
        for key, value in scenario.items():
            _number(value, name+"."+key, allow_zero=key.startswith("pixel_"),
                    integer=key.startswith("pixel_"))
            if key.endswith("_fraction") and value > 1:
                raise ValueError("fractions must not exceed one")
        if scenario["demand_multiplier"] < 1 or scenario["short_harness_multiplier"] < 1:
            raise ValueError("demand multipliers must be at least one")
        if (scenario["pixel_uplinks_per_module"] == 0) == (scenario["pixel_uplinks_per_chip"] == 0):
            raise ValueError("choose exactly one positive pixel uplink counting method")
    return inputs


def _area(diameter):
    return math.pi*diameter*diameter/4


def _groups(layout, inputs):
    """One half-stave or disc radial row, retaining homogeneous pixel families."""
    patches = defaultdict(set)
    seen_patch_ids = set()
    for patch in layout.get("modules", []):
        if patch["subsystem"] == "pixel":
            if patch["id"] in seen_patch_ids:
                raise ValueError("duplicate pixel patch ID")
            seen_patch_ids.add(patch["id"])
            patches[patch["module_id"]].add(patch["id"])
    grouped = defaultdict(list)
    seen = set()
    for body in layout["bodies"]:
        mid = body["module_id"]
        if mid in seen:
            raise ValueError("duplicate module body ID")
        seen.add(mid)
        sub, region = body["subsystem"], body["region"]
        if sub not in SUBSYSTEMS or region not in ("barrel", "endcap"):
            raise ValueError("service budget supports named cylindrical/disc tracker subsystems")
        z = body["center_mm"][2]
        if not math.isfinite(z):
            raise ValueError("body centre z must be finite")
        side = "positive" if z >= 0 else "negative"
        key = (side, sub, region, body["layer_id"],
               body["col"] if region == "barrel" else body["row"], body["family"])
        chips = len(patches[mid]) if sub == "pixel" else 0
        if sub == "pixel" and chips == 0:
            raise ValueError("pixel body must retain its chip patches")
        footprint = 4*_number(body["half_u_mm"], "half_u_mm")*_number(body["half_v_mm"], "half_v_mm")
        grouped[key].append(dict(module_id=mid, chips=chips, footprint_mm2=footprint))
    output = []
    pix, strip = inputs["pixel"], inputs["strip"]
    for key, modules in sorted(grouped.items()):
        side, sub, region, layer, local_index, family = key
        count = len(modules)
        item = dict(side=side, subsystem=sub, region=region, layer_id=layer,
                    local_index=local_index, family=family, modules=count,
                    module_ids=sorted(m["module_id"] for m in modules),
                    chips=sum(m["chips"] for m in modules),
                    module_footprint_mm2=sum(m["footprint_mm2"] for m in modules))
        if sub == "pixel":
            distinct = {m["chips"] for m in modules}
            if len(distinct) != 1:
                raise ValueError("homogeneous pixel family has differing chip counts")
            per_module = distinct.pop()
            chain_size = min(pix["max_chain_modules"], pix["max_chain_chips"]//per_module)
            if chain_size < 1:
                raise ValueError("one pixel module exceeds the chain chip ceiling")
            item.update(power_chains=math.ceil(count/chain_size), chain_capacity_modules=chain_size,
                        reference_power_W=item["chips"]*pix["power_per_chip_W"])
            item["cooling_leaf_loops"] = math.ceil(item["reference_power_W"]/pix["cooling_power_per_circuit_W"])
            item["harnesses"] = 0
        else:
            limit = (strip["endcap_modules_per_leaf"] if region == "endcap" else
                     strip["short_barrel_modules_per_leaf"] if sub == "short_strip" else
                     strip["long_barrel_modules_per_leaf"])
            item.update(power_chains=0, harnesses=math.ceil(count/strip["max_modules_per_harness"]),
                        cooling_leaf_loops=math.ceil(count/limit),
                        reference_power_W=count*strip[("short" if sub == "short_strip" else "long")
                                                     +"_reference_module_power_W"])
        output.append(item)
    return output


def _inventory(groups, inputs):
    """Co-located manifold banks aggregate at most eight leaves within each layer."""
    pix, strip = inputs["pixel"], inputs["strip"]
    counts = Counter()
    for group in groups:
        for key in ("modules", "chips", "power_chains", "harnesses", "cooling_leaf_loops"):
            counts[key] += group[key]
    leaves = defaultdict(int)
    for group in groups:
        leaves[group["layer_id"]] += group["cooling_leaf_loops"]
    sub = groups[0]["subsystem"] if groups else None
    trunks = (sum(math.ceil(n/strip["max_leaves_per_trunk"]) for n in leaves.values())
              if sub not in (None, "pixel") else counts["cooling_leaf_loops"])
    scenarios = {}
    for name, scenario in inputs["scenarios"].items():
        if sub == "pixel":
            data = (counts["modules"]*scenario["pixel_uplinks_per_module"]
                    +counts["chips"]*scenario["pixel_uplinks_per_chip"])
            command = counts["modules"]*scenario["pixel_commands_per_module"]
            cable = ((data+command)*pix["differential_link_area_mm2"]
                     +counts["power_chains"]*pix["ancillary_chain_area_mm2"])
            feed = trunks*_area(pix["feed_outer_diameter_mm"])
            ret = trunks*_area(pix["return_outer_diameter_mm"])
            harnesses = 0
        else:
            factor = scenario["short_harness_multiplier"] if sub == "short_strip" else 1
            harnesses = sum(math.ceil(g["harnesses"]*factor) for g in groups)
            cable = harnesses*(_area(strip["power_cable_outer_diameter_mm"])
                              +_area(strip["fibre_cable_outer_diameter_mm"] ))
            feed = trunks*_area(strip["trunk_feed_outer_diameter_mm"])
            ret = trunks*_area(strip["trunk_return_outer_diameter_mm"])
            data = command = 0
        bare = cable+feed+ret
        scenarios[name] = dict(harnesses=harnesses, data_uplinks=data, command_links=command,
                               cables_mm2=cable, feed_mm2=feed, return_mm2=ret,
                               bare_demand_mm2=bare,
                               reserved_demand_mm2=bare*scenario["demand_multiplier"])
    return dict(counts={key:counts[key] for key in ("modules", "chips", "power_chains", "harnesses", "cooling_leaf_loops")},
                cooling_trunk_pairs=trunks,
                module_footprint_m2=sum(g["module_footprint_mm2"] for g in groups)/1e6,
                reference_power_W=sum(g["reference_power_W"] for g in groups),
                local_leaf_pipe_area_mm2=(counts["cooling_leaf_loops"]
                    *(_area(strip["leaf_feed_outer_diameter_mm"])+_area(strip["leaf_return_outer_diameter_mm"])))
                    if sub not in (None, "pixel") else 0.,
                scenarios=scenarios)


def _owners(route):
    if "owners" in route:
        owners = route["owners"]
        if not isinstance(owners, list) or not owners or not set(owners) <= set(SUBSYSTEMS):
            raise ValueError("route owners must be a nonempty list of named subsystems")
        return set(owners)
    sub = route["subsystem"]
    if sub == "shared":
        return set(SUBSYSTEMS)
    if sub not in SUBSYSTEMS:
        raise ValueError("route has unknown service owner")
    return {sub}


def _side(route):
    if route["z_min_mm"] >= 0:
        side = "positive"
    elif route["z_max_mm"] <= 0:
        side = "negative"
    else:
        raise ValueError("route crosses z=0; split into signed-end routes")
    if route.get("side", side) != side:
        raise ValueError("route side contradicts z bounds")
    return side


def _routes(routes):
    result = copy.deepcopy(list(routes))
    seen = set()
    for route in result:
        if not isinstance(route.get("id"), str) or not route["id"] or route["id"] in seen:
            raise ValueError("route IDs must be nonempty and unique")
        seen.add(route["id"])
        _owners(route)
        if route["kind"] not in ("axial", "radial", "collector"):
            raise ValueError("route kind must be axial, radial or collector")
        for key in ("r_min_mm", "r_max_mm", "z_min_mm", "z_max_mm"):
            val = route[key]
            if isinstance(val, bool) or not isinstance(val, (float, int)) or not math.isfinite(val):
                raise ValueError("route bounds must be finite")
        if not 0 <= route["r_min_mm"] < route["r_max_mm"] or not route["z_min_mm"] < route["z_max_mm"]:
            raise ValueError("route bounds have invalid width")
        _side(route)
        if not set(route.get("regions", ["barrel", "endcap"])) <= {"barrel", "endcap"}:
            raise ValueError("unknown demand region")
        if "layer_ids" in route and (not isinstance(route["layer_ids"], list) or
                any(not isinstance(layer, str) for layer in route["layer_ids"])):
            raise ValueError("layer_ids must be a list of layer names")
    return result


def _declared_edges(routes):
    """Validate a complete explicit graph, or retain the historical all-contact mode."""
    specified = ["connects_to" in route for route in routes]
    if not any(specified):
        return None
    if not all(specified):
        raise ValueError("connects_to must be present on every route or none")
    by_id = {r["id"]: r for r in routes}
    adjacency = {route_id:set() for route_id in by_id}
    edges = set()
    for route in routes:
        targets = route["connects_to"]
        if not isinstance(targets, list) or any(not isinstance(target, str) for target in targets):
            raise ValueError("connects_to must be a list of route IDs")
        if len(targets) != len(set(targets)):
            raise ValueError("connects_to contains duplicate targets")
        for target in targets:
            if target not in by_id:
                raise ValueError("connects_to selects an unknown route ID")
            if target == route["id"]:
                raise ValueError("a route cannot connect to itself")
            if _side(route) != _side(by_id[target]):
                raise ValueError("a declared edge cannot join different detector ends")
            edge = tuple(sorted((route["id"], target)))
            edges.add(edge)
            adjacency[edge[0]].add(edge[1])
            adjacency[edge[1]].add(edge[0])
    for side in SIDES:
        ids = {r["id"] for r in routes if _side(r) == side}
        if not ids:
            continue
        reached, pending = set(), [min(ids)]
        while pending:
            node = pending.pop()
            if node in reached:
                continue
            reached.add(node)
            pending.extend(adjacency[node]-reached)
        if reached != ids:
            raise ValueError(f"declared route graph is disconnected on {side} end")
    return edges


def _cross_section(route, boundary):
    r0, r1 = route["r_min_mm"]+boundary, route["r_max_mm"]-boundary
    dz = route["z_max_mm"]-route["z_min_mm"]-2*boundary
    annulus = math.pi*(r1*r1-r0*r0) if r1 > r0 else 0.
    radial = 2*math.pi*route["r_min_mm"]*max(0., dz)
    # A collector is a bend/interface pocket: both directions constrain it.
    return annulus if route["kind"] == "axial" else radial if route["kind"] == "radial" else min(annulus, radial)


def _selected(groups, route):
    side, owners = _side(route), _owners(route)
    regions = set(route.get("regions", ["barrel", "endcap"]))
    layers = set(route["layer_ids"]) if "layer_ids" in route else None
    return [g for g in groups if g["side"] == side and g["subsystem"] in owners
            and g["region"] in regions and (layers is None or g["layer_id"] in layers)]


def _demand(selected, inputs):
    # Keep inventory owners distinct: pixel and strip power/control topology differs.
    inventories = [_inventory([g for g in selected if g["subsystem"] == sub], inputs)
                   for sub in SUBSYSTEMS]
    return {name:sum(i["scenarios"][name]["reserved_demand_mm2"] for i in inventories)
            for name in inputs["scenarios"]}


def _capacity_result(section, demand, inputs):
    result = {}
    for name, scenario in inputs["scenarios"].items():
        capacity = section*scenario["available_phi_fraction"]*scenario["packing_fraction"]
        result[name] = dict(demand_mm2=demand[name], capacity_mm2=capacity,
                            utilization=(demand[name]/capacity if capacity else None),
                            status="PASS" if demand[name] <= capacity+_EPS else "FAIL")
    return result


def estimate_budget(layout, inputs, routes):
    """Return counts, source-controlled demands, route and adjoining-throat capacities.

    ``layout`` is geometry.generate_layout() or a services_geometry filtered copy.
    A route's optional ``regions`` and ``layer_ids`` restrict source groups.
    Otherwise the complete owner's signed-end demand is conservatively carried.
    Shared routes accumulate all subsystem owners. ``collector`` uses the smaller
    axial/radial section. With connects_to on every route only declared joins
    are required throats; raw geometric contacts remain informational. Without
    connects_to, historical all-contact auditing is preserved. Explicit graphs
    must be connected per signed end, every declared join must touch, and its
    downstream source selection must contain every upstream source module.
    """
    _validate_inputs(inputs)
    routes = _routes(routes)
    declared_edges = _declared_edges(routes)
    groups = _groups(layout, inputs)
    known_layers = ({layer["id"] for layer in layout["layers"]} if "layers" in layout else
                    {body["layer_id"] for body in layout["bodies"]})
    for route in routes:
        if not set(route.get("layer_ids", [])) <= known_layers:
            raise ValueError("route selects an unknown layer_id")
    if declared_edges is not None:
        carried = {r["id"]:{mid for group in _selected(groups, r) for mid in group["module_ids"]}
                   for r in routes}
        for route in routes:
            for target in route["connects_to"]:
                missing = carried[route["id"]]-carried[target]
                if missing:
                    raise ValueError(f"declared flow loses {len(missing)} source modules: "
                                     f"{route['id']} -> {target}; downstream scope must preserve upstream sources")
    ends = {}
    for side in SIDES:
        ends[side] = {}
        for sub in SUBSYSTEMS:
            selected = [g for g in groups if g["side"] == side and g["subsystem"] == sub]
            inventory = _inventory(selected, inputs)
            inventory["regions"] = {r:_inventory([g for g in selected if g["region"] == r], inputs)
                                    for r in ("barrel", "endcap")}
            ends[side][sub] = inventory
    boundary = inputs["capacity"]["boundary_allowance_mm"]
    capacities = []
    for route in routes:
        side, owners = _side(route), _owners(route)
        regions = set(route.get("regions", ["barrel", "endcap"]))
        area = _cross_section(route, boundary)
        selected = _selected(groups, route)
        demand = _demand(selected, inputs)
        capacities.append(dict(id=route["id"], side=side, subsystem=route["subsystem"],
                               owners=sorted(owners), regions=sorted(regions),
                               layer_ids=sorted({g["layer_id"] for g in selected}),
                               modules_carried=sum(g["modules"] for g in selected),
                               usable_geometric_cross_section_mm2=area,
                               scenarios=_capacity_result(area, demand, inputs)))
    potential_contacts = []
    for i, a in enumerate(routes):
        for b in routes[i+1:]:
            if _side(a) != _side(b):
                continue
            r0, r1 = max(a["r_min_mm"], b["r_min_mm"]), min(a["r_max_mm"], b["r_max_mm"])
            z0, z1 = max(a["z_min_mm"], b["z_min_mm"]), min(a["z_max_mm"], b["z_max_mm"])
            dr, dz = r1-r0, z1-z0
            if dr < -_EPS or dz < -_EPS or max(dr, dz) <= _EPS:
                continue
            side = _side(a)
            # A branch joins a trunk through its own traffic; already joined
            # traffic is tested on the shared route, not forced through the branch.
            a_groups = _selected(groups, a)
            b_module_ids = {mid for g in _selected(groups, b) for mid in g["module_ids"]}
            selected = [g for g in a_groups if g["module_ids"][0] in b_module_ids]
            owners = {g["subsystem"] for g in selected}
            demand = _demand(selected, inputs)
            if abs(dz) <= _EPS:
                rlo, rhi = r0+boundary, r1-boundary
                area = math.pi*(rhi*rhi-rlo*rlo) if rhi > rlo else 0.
                direction = "axial face"
            elif abs(dr) <= _EPS:
                area = 2*math.pi*r0*max(0., dz-2*boundary)
                direction = "radial face"
            else:
                overlap = dict(r_min_mm=r0, r_max_mm=r1, z_min_mm=z0, z_max_mm=z1,
                               kind="collector")
                area = _cross_section(overlap, boundary)
                direction = "overlap pocket, minimum axial/radial area"
            edge = tuple(sorted((a["id"], b["id"])))
            required = declared_edges is None or edge in declared_edges
            potential_contacts.append(dict(routes=[a["id"], b["id"]], required=required,
                                side=side, owners=sorted(owners),
                                direction=direction, modules_carried=sum(g["modules"] for g in selected),
                                usable_geometric_cross_section_mm2=area,
                                scenarios=_capacity_result(area, demand, inputs)))
    contacts = {tuple(sorted(c["routes"])) for c in potential_contacts}
    if declared_edges is not None and declared_edges-contacts:
        missing = sorted(declared_edges-contacts)
        raise ValueError(f"declared route edge has no finite geometric contact: {missing}")
    throats = [c for c in potential_contacts if c["required"]]
    return dict(schema_version=1, status="PROTOTYPE geometry capacity only; no electrical/hydraulic qualification",
                inputs_sha256=hashlib.sha256(json.dumps(inputs, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                local_groups=groups, ends=ends, routes=capacities, throats=throats,
                potential_contacts=potential_contacts,
                stress_cooling=dict(reference_counts_and_pipe_sizes_retained=True,
                                    thermal_load_rescaled=False,
                                    status="OPTIMISTIC reference cooling retained; high-load thermal/hydraulic feasibility unqualified"),
                routing_graph=dict(mode="declared" if declared_edges is not None else "all_geometric_contacts",
                                   declared_edges=[list(e) for e in sorted(declared_edges)] if declared_edges is not None else None,
                                   connected_per_signed_end=True if declared_edges is not None else None),
                all_routes_and_throats_pass={name:all(r["scenarios"][name]["status"] == "PASS" for r in capacities+throats)
                                             for name in inputs["scenarios"]},
                limitations=["A PASS is only an area inequality, not bend, connector or assembly validation.",
                             "Demand defaults to complete owner per signed end; optional layer_ids/regions select routed source groups.",
                             "A joining throat carries source groups shared by its two routes; a shared trunk separately sums all owner demand.",
                             "Explicit connects_to edges define required handoffs; incidental geometric contacts are retained as information only.",
                             "Central module centres z>=0 route to positive end; unequal end counts are retained.",
                             "Leaf pipe sections are reported separately; larger downstream trunk pairs replace them after manifolding.",
                             "Manifolds aggregate only within a layer/side; detailed manifold boxes and pressures are unresolved.",
                             "Stress changes cable demand but retains nominal cooling: no high-load hydraulic claim.",
                             "Module footprints are projected local box areas, not engineered support area or material mass."])
