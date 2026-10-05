"""DES-010 PROTOTYPE: conservative service-space exclusions, without materials.

This overlay filters complete original rows after finite-module generation. It
never changes a retained transform or identifier and leaves nominal layers in
place for the later coverage denominator. Annular support volumes reserve space;
they are not structural solids or a material model. All inputs are millimetres.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from collections import defaultdict

try:
    from . import geometry
except ImportError:  # Direct script imports beside the existing study driver.
    import geometry

_EPS = 1e-9
_BOUNDS = ("r_min_mm", "r_max_mm", "z_min_mm", "z_max_mm")


def body_envelope(body):
    """Exact extrema of an OBB's cylindrical projection, including edge minima.

    The convex xy projection can contain the beam axis; in that case its minimum
    radius is zero, even when no corner or box edge lies on the axis.
    """
    corners = geometry._corners(body)
    points = sorted(set((p[0], p[1]) for p in corners))

    def cross2(a, b, c):
        return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])

    lower, upper = [], []
    for point in points:
        while len(lower) >= 2 and cross2(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    for point in reversed(points):
        while len(upper) >= 2 and cross2(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    hull = lower[:-1]+upper[:-1] if len(points) > 1 else points
    rmin = min(math.hypot(*p) for p in points)
    if len(hull) >= 3 and all(cross2(a, b, (0., 0.)) >= -_EPS
                              for a, b in zip(hull, hull[1:]+hull[:1])):
        rmin = 0.
    else:
        for a, b in zip(hull, hull[1:]+hull[:1]):
            dx, dy = b[0]-a[0], b[1]-a[1]
            den = dx*dx+dy*dy
            t = max(0., min(1., -(a[0]*dx+a[1]*dy)/den)) if den else 0.
            rmin = min(rmin, math.hypot(a[0]+t*dx, a[1]+t*dy))
    return dict(r_min_mm=rmin, r_max_mm=max(math.hypot(*p) for p in points),
                z_min_mm=min(p[2] for p in corners), z_max_mm=max(p[2] for p in corners))


def _intersects(a, b, clearance=0.):
    """Conservative r-z interior exclusion; touching at zero clearance is allowed."""
    return (a["r_min_mm"] < b["r_max_mm"]+clearance-_EPS and
            b["r_min_mm"] < a["r_max_mm"]+clearance-_EPS and
            a["z_min_mm"] < b["z_max_mm"]+clearance-_EPS and
            b["z_min_mm"] < a["z_max_mm"]+clearance-_EPS)


def _validated_routes(routes):
    result = copy.deepcopy(list(routes))
    ids = set()
    for route in result:
        if not isinstance(route.get("id"), str) or not route["id"] or route["id"] in ids:
            raise ValueError("route IDs must be nonempty and unique")
        ids.add(route["id"])
        if not route.get("subsystem") or not route.get("kind"):
            raise ValueError("every route requires subsystem and kind")
        if any(not isinstance(route.get(k), (int, float)) or not math.isfinite(route[k])
               for k in _BOUNDS):
            raise ValueError("route bounds must be finite millimetres")
        if not 0 <= route["r_min_mm"] < route["r_max_mm"] or not route["z_min_mm"] < route["z_max_mm"]:
            raise ValueError("route bounds must have positive radial and axial width")
    return result


def _validate_clearance(clearance):
    if not math.isfinite(clearance) or clearance < 0:
        raise ValueError("clearance_mm must be finite and nonnegative")


def _supports(layout, depths, envelopes):
    grouped = defaultdict(list)
    for body in layout["bodies"]:
        grouped[body["layer_id"]].append(body)
    supports = []
    for layer in layout["layers"]:
        bodies = grouped.get(layer["id"], [])
        if not bodies:
            continue
        depth = depths.get(layer["subsystem"], 0.)
        if not math.isfinite(depth) or depth < 0:
            raise ValueError("support depths must be finite and nonnegative")
        if depth == 0:
            continue
        ee = [envelopes[b["module_id"]] for b in bodies]
        r0, r1 = min(e["r_min_mm"] for e in ee), max(e["r_max_mm"] for e in ee)
        z0, z1 = min(e["z_min_mm"] for e in ee), max(e["z_max_mm"] for e in ee)
        if layer["kind"] == "cylinder":
            r0, r1 = r0-depth, r0
            orientation = "inward barrel shell"
        elif layer["kind"] == "disc":
            if layer["z_m"] == 0:
                raise ValueError("a disc support needs a nonzero signed disc z position")
            z0, z1 = (z1, z1+depth) if layer["z_m"] > 0 else (z0-depth, z0)
            orientation = "outward endcap slab"
        else:
            raise ValueError("service support overlay supports cylinders and discs only")
        supports.append(dict(id="support:"+layer["id"], layer_id=layer["id"],
                             subsystem=layer["subsystem"], kind="support_reservation",
                             r_min_mm=r0, r_max_mm=r1, z_min_mm=z0, z_max_mm=z1,
                             thickness_mm=depth, orientation=orientation,
                             status="PROTOTYPE space reservation; not a material or qualified support"))
    return supports


def support_envelopes(layout, support_depths):
    """Reserve inward barrel shells / outward disc slabs around retained bodies."""
    envelopes = {b["module_id"]: body_envelope(b) for b in layout["bodies"]}
    return _supports(layout, support_depths, envelopes)


def route_connectivity(routes, clearance_mm=0.):
    """Report connected route groups per subsystem and signed detector end.

    Face contact with finite transverse opening connects. Point/corner contact
    does not. With nonzero clearance the transverse opening must exceed twice
    that clearance. This graph establishes space connectivity, not bend radii.
    """
    routes = _validated_routes(routes)
    _validate_clearance(clearance_mm)
    by_id = {r["id"]: r for r in routes}
    adjacency = {r["id"]: [] for r in routes}
    edges = []
    for i, a in enumerate(routes):
        for b in routes[i+1:]:
            dr = min(a["r_max_mm"], b["r_max_mm"])-max(a["r_min_mm"], b["r_min_mm"])
            dz = min(a["z_max_mm"], b["z_max_mm"])-max(a["z_min_mm"], b["z_min_mm"])
            if (dr >= -_EPS and dz >= -_EPS and
                    max(dr, dz) > 2*clearance_mm+_EPS):
                adjacency[a["id"]].append(b["id"])
                adjacency[b["id"]].append(a["id"])
                edges.append([a["id"], b["id"]])
    groups = defaultdict(list)
    for r in routes:
        side = "positive" if r["z_min_mm"] >= 0 else "negative" if r["z_max_mm"] <= 0 else "both"
        groups[(r["subsystem"], side)].append(r["id"])
    reported = []
    for (subsystem, side), ids in sorted(groups.items()):
        pending, components = set(ids), []
        while pending:
            reached, todo = set(), [min(pending)]
            while todo:
                current = todo.pop()
                if current in reached:
                    continue
                reached.add(current)
                todo.extend(n for n in adjacency[current] if n in pending and n not in reached)
            pending -= reached
            components.append(sorted(reached))
        reported.append(dict(subsystem=subsystem, side=side, components=components,
                             connected=len(components) == 1,
                             exits=[i for i in ids if by_id[i].get("exit", False)]))
    return dict(edges=edges, groups=reported,
                all_connected_per_subsystem_side=all(g["connected"] for g in reported),
                note="Graph adjacency only; capacity, bend sweep and external access require separate checks")


def reservation_diagnostics(layout, routes, supports, clearance_mm=0.):
    """Report every conservative clash; no intended connection is hidden.

    Own-layer support/body contact is allowed geometrically, but an actual
    interior overlap is still reported. Collector joins belong in separately
    declared local connectors, not an exemption for a blocked trunk.
    """
    routes = _validated_routes(routes)
    _validate_clearance(clearance_mm)
    bodies = layout["bodies"]
    envelopes = {b["module_id"]: body_envelope(b) for b in bodies}
    route_body, route_support, support_body, support_pair, support_host = [], [], [], [], []
    for r in routes:
        for b in bodies:
            if _intersects(r, envelopes[b["module_id"]], clearance_mm):
                route_body.append(dict(route_id=r["id"], module_id=b["module_id"],
                                       layer_id=b["layer_id"], row=b["row"]))
        for s in supports:
            if _intersects(r, s, clearance_mm):
                route_support.append(dict(route_id=r["id"], support_id=s["id"],
                                          own_subsystem=r["subsystem"] == s["subsystem"]))
    host = layout["metadata"].get("host")
    for i, s in enumerate(supports):
        for b in bodies:
            if _intersects(s, envelopes[b["module_id"]]):
                support_body.append(dict(support_id=s["id"], module_id=b["module_id"],
                                         layer_id=b["layer_id"], own_layer=s["layer_id"] == b["layer_id"]))
        for other in supports[i+1:]:
            if _intersects(s, other):
                support_pair.append([s["id"], other["id"]])
        if host:
            excess = [max(0., host["r_min_m"]*1000-s["r_min_mm"]),
                      max(0., s["r_max_mm"]-host["r_max_m"]*1000),
                      max(0., -host["abs_z_max_m"]*1000-s["z_min_mm"],
                          s["z_max_mm"]-host["abs_z_max_m"]*1000)]
            if max(excess) > _EPS:
                support_host.append(dict(support_id=s["id"], excess_inner_outer_z_mm=excess))
    return dict(route_body_conflicts=route_body, route_support_conflicts=route_support,
                support_body_conflicts=support_body, support_pair_conflicts=support_pair,
                support_host_violations=support_host,
                connectivity=route_connectivity(routes),
                method="Conservative full-azimuth cylindrical r-z envelopes; zero clearance permits boundary contact")


def apply_reservations(layout, routes, support_depths, clearance_mm=0., *, removed_rows=None):
    """Return a filtered copy; ``removed_rows`` optionally adds (layer_id,row) pairs.

    Carving repeats after constructing support envelopes: supports can extend
    into a corridor that already clears bodies. Removing an entire layer, or a
    hole inside a support that cannot be freed by edge-row removal, raises
    ValueError. Other diagnostic failures are reported for the caller to reject.
    """
    routes = _validated_routes(routes)
    _validate_clearance(clearance_mm)
    result = copy.deepcopy(layout)
    original_bodies = result["bodies"]
    envelopes = {b["module_id"]: body_envelope(b) for b in original_bodies}
    grouped = defaultdict(list)
    for b in original_bodies:
        grouped[b["layer_id"], b["row"]].append(b)
    removed = {tuple(row) for row in (removed_rows or [])}
    if not removed <= set(grouped):
        raise ValueError("manual removed_rows contains an unknown layer/row")
    reasons = {key: {"manual"} for key in removed}
    iterations = 0
    while True:
        iterations += 1
        kept = [b for b in original_bodies if (b["layer_id"], b["row"]) not in removed]
        if {b["layer_id"] for b in kept} != {b["layer_id"] for b in original_bodies}:
            raise ValueError("reservation would remove every row of a layer; revise the route explicitly")
        result["bodies"] = kept
        supports = _supports(result, support_depths, envelopes)
        new = defaultdict(set)
        for route in routes:
            for body in kept:
                if _intersects(route, envelopes[body["module_id"]], clearance_mm):
                    new[body["layer_id"], body["row"]].add("body:"+route["id"])
            for support in supports:
                if not _intersects(route, support, clearance_mm):
                    continue
                found = False
                for body in kept:
                    if body["layer_id"] != support["layer_id"]:
                        continue
                    projected = dict(support)
                    e = envelopes[body["module_id"]]
                    if support["orientation"] == "inward barrel shell":
                        projected.update(z_min_mm=e["z_min_mm"], z_max_mm=e["z_max_mm"])
                    else:
                        projected.update(r_min_mm=e["r_min_mm"], r_max_mm=e["r_max_mm"])
                    if _intersects(route, projected, clearance_mm):
                        new[body["layer_id"], body["row"]].add("support:"+route["id"])
                        found = True
                if not found:
                    raise ValueError("route crosses an interior hole in a continuous support; edge-row carving cannot clear it")
        if not new:
            break
        if iterations > len(grouped):
            raise RuntimeError("bounded service-row carving did not converge")
        for key, why in new.items():
            removed.add(key)
            reasons.setdefault(key, set()).update(why)
    kept_ids = {b["module_id"] for b in result["bodies"]}
    result["modules"] = [m for m in result["modules"] if m["module_id"] in kept_ids]
    before, after = geometry.summarize(layout), geometry.summarize(result)
    result["metadata"]["summary"] = after
    result["metadata"]["host_diagnostics"] = geometry.host_diagnostics(result)
    register = dict(routes=routes, support_depths_mm=support_depths,
                    clearance_mm=clearance_mm, manual_removed_rows=sorted(tuple(r) for r in (removed_rows or [])))
    records = []
    for layer_id, row in sorted(removed):
        bodies = grouped[layer_id, row]
        records.append(dict(layer_id=layer_id, row=row, module_ids=[b["module_id"] for b in bodies],
                            reasons=sorted(reasons[layer_id, row])))
    result["metadata"]["services"] = dict(
        status="PROTOTYPE unapproved routing/support hypothesis; no layer-position optimization",
        input_sha256=hashlib.sha256(json.dumps(register, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        routes=routes, supports=supports, support_depths_mm=copy.deepcopy(support_depths),
        clearance_mm=clearance_mm, iterations=iterations, removed_rows=records,
        removed_module_ids=[b["module_id"] for b in original_bodies if b["module_id"] not in kept_ids],
        before_summary=before, after_summary=after,
        removed_summary={key: {metric: values[metric]-after.get(key, {}).get(metric, 0.)
                               for metric in values} for key, values in before.items()},
        baseline_model_sha256=layout["metadata"].get("model_sha256"),
        baseline_layout_sha256=layout["metadata"].get("layout_sha256"),
        inherited_placement_metadata="Describes the uncarved baseline; consult removed_rows and retained bodies for final placement",
        diagnostics=reservation_diagnostics(result, routes, supports, clearance_mm))
    return result
