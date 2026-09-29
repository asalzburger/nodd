"""PROTOTYPE finite active-patch oracle, independent of the ACTS navigator.

Lengths are mm, momentum GeV and axial field tesla. ``s`` is transverse
arc length, so z(s)=z0+s*sinh(eta). Lorentz bending uses k=-q*B*c/pT.
Only the first host traversal is studied; a curling track stops at its first
transverse half-turn. No material, energy loss, inefficiency or reconstruction
is simulated. A finite sample cannot establish continuous hermeticity.
"""

from collections import defaultdict
import math

import numpy as np


KAPPA_MM = 0.000299792458
ROOT_TOLERANCE_MM = 1e-6
BOUND_TOLERANCE_MM = 1e-6


def _parameters(track):
    origin = np.asarray(track.get("origin_mm", [0., 0., 0.]), dtype=float)
    eta, phi = float(track["eta"]), float(track["phi"])
    pt = float(track.get("pt_GeV", 1.))
    field = float(track.get("field_T", 0.))
    charge = float(track.get("charge", 1.))
    if origin.shape != (3,) or not np.all(np.isfinite(origin)):
        raise ValueError("origin_mm must contain three finite coordinates")
    if not all(math.isfinite(x) for x in (eta, phi, pt, field, charge)) or pt <= 0:
        raise ValueError("Track coordinates must be finite and pT positive")
    return origin, eta, phi, -KAPPA_MM * charge * field / pt


def positions(track, transverse_path_mm):
    """Exact positions, including a numerically stable zero-field limit."""
    origin, eta, phi, k = _parameters(track)
    s = np.asarray(transverse_path_mm, dtype=float)
    half_angle = .5 * k * s
    chord = s * np.sinc(half_angle / np.pi)
    return np.stack((origin[0] + chord * np.cos(phi + half_angle),
                     origin[1] + chord * np.sin(phi + half_angle),
                     origin[2] + s * np.sinh(eta)), axis=-1)


def traversal_limit(track, host_radius_mm=1140., host_half_z_mm=3150.):
    """First outer-host exit or first transverse half-turn, whichever is first."""
    origin, eta, phi, k = _parameters(track)
    if math.hypot(*origin[:2]) >= host_radius_mm or abs(origin[2]) >= host_half_z_mm:
        raise ValueError("Track origin must be inside the host")
    sh = math.sinh(eta)
    z_limit = ((math.copysign(host_half_z_mm, sh) - origin[2]) / sh
               if sh else math.inf)
    if abs(k) < 1e-15:
        projection = origin[0] * math.cos(phi) + origin[1] * math.sin(phi)
        radial = -projection + math.sqrt(projection ** 2 + host_radius_mm ** 2
                                         - float(origin[:2] @ origin[:2]))
        return min(radial, z_limit)
    half_turn = math.pi / abs(k)
    radial = _radial_paths(track, host_radius_mm, half_turn)
    return min([half_turn, z_limit] + radial)


class SurfaceIndex:
    """Conservative voxel broad phase followed by exact finite-plane roots.

    Sensor corners populate every occupied voxel. Track segments use exact
    helix endpoints and circular-arc sagitta padding; thus this broad phase
    cannot drop an intersection because of curvature or a finite sensor edge.
    """

    def __init__(self, layout, voxel_mm=100., segment_mm=75.):
        self.layout = layout
        self.modules = layout["modules"]
        self.voxel_mm, self.segment_mm = float(voxel_mm), float(segment_mm)
        if min(self.voxel_mm, self.segment_mm) <= 0:
            raise ValueError("Index lengths must be positive")
        self.centers = np.asarray([m["center_mm"] for m in self.modules], float).reshape(-1, 3)
        self.u = np.asarray([m["u"] for m in self.modules], float).reshape(-1, 3)
        self.v = np.asarray([m["v"] for m in self.modules], float).reshape(-1, 3)
        self.n = np.cross(self.u, self.v)
        self.hu = np.asarray([m["half_u_mm"] for m in self.modules], float)
        self.hv = np.asarray([m["half_v_mm"] for m in self.modules], float)
        if (not np.all(np.isfinite(self.centers)) or np.any(self.hu <= 0)
                or np.any(self.hv <= 0) or not np.all(np.isfinite(self.hu))
                or not np.all(np.isfinite(self.hv))):
            raise ValueError("Finite centers and positive finite active bounds required")
        if (not np.allclose(np.linalg.norm(self.u, axis=1), 1., atol=1e-8)
                or not np.allclose(np.linalg.norm(self.v, axis=1), 1., atol=1e-8)
                or not np.allclose(np.sum(self.u * self.v, axis=1), 0., atol=1e-8)):
            raise ValueError("Module u/v axes must be orthonormal")
        ids = [m["id"] for m in self.modules]
        if len(set(ids)) != len(ids):
            raise ValueError("Active patch IDs must be unique")
        extent = abs(self.u) * self.hu[:, None] + abs(self.v) * self.hv[:, None]
        lo = np.floor((self.centers - extent - BOUND_TOLERANCE_MM) / voxel_mm).astype(int)
        hi = np.floor((self.centers + extent + BOUND_TOLERANCE_MM) / voxel_mm).astype(int)
        cells = defaultdict(list)
        for i, (a, b) in enumerate(zip(lo, hi)):
            for x in range(a[0], b[0] + 1):
                for y in range(a[1], b[1] + 1):
                    for z in range(a[2], b[2] + 1):
                        cells[x, y, z].append(i)
        self.cells = dict(cells)

    def candidates(self, track, limit):
        _, eta, _, k = _parameters(track)
        count = max(1, math.ceil(limit * math.cosh(eta) / self.segment_mm))
        s = np.linspace(0., limit, count + 1)
        points = positions(track, s)
        sagitta = (2. * math.sin(abs(k) * limit / count / 4.) ** 2 / abs(k)
                    if k else 0.)
        padding = np.array([sagitta, sagitta, 0.]) + BOUND_TOLERANCE_MM
        lo = np.floor((np.minimum(points[:-1], points[1:]) - padding) / self.voxel_mm).astype(int)
        hi = np.floor((np.maximum(points[:-1], points[1:]) + padding) / self.voxel_mm).astype(int)
        touched = set()
        for a, b in zip(lo, hi):
            for x in range(a[0], b[0] + 1):
                for y in range(a[1], b[1] + 1):
                    for z in range(a[2], b[2] + 1):
                        touched.add((x, y, z))
        found = [self.cells[key] for key in touched if key in self.cells]
        return np.unique(np.concatenate(found)).astype(int) if found else np.empty(0, int)

    def hits(self, track, *, host_radius_mm=1140., host_half_z_mm=3150., all_surfaces=False):
        """Return (patch index, earliest transverse path) for each reached patch."""
        limit = traversal_limit(track, host_radius_mm, host_half_z_mm)
        indices = np.arange(len(self.modules)) if all_surfaces else self.candidates(track, limit)
        if not len(indices):
            return []
        origin, eta, phi, k = _parameters(track)
        n, center = self.n[indices], self.centers[indices]
        sh = math.sinh(eta)
        offset = np.sum(n * (origin - center), axis=1)

        def residual(s, rows):
            half = .5 * k * s
            chord = s * np.sinc(half / np.pi)
            return (offset[rows] + chord * (n[rows, 0] * np.cos(phi + half)
                    + n[rows, 1] * np.sin(phi + half)) + n[rows, 2] * s * sh)

        roots, root_rows = [], []
        if abs(k) < 1e-15:
            derivative = n @ np.array([math.cos(phi), math.sin(phi), sh])
            valid = abs(derivative) > 1e-14
            rows = np.flatnonzero(valid)
            s = -offset[rows] / derivative[rows]
            valid = (s > ROOT_TOLERANCE_MM) & (s <= limit + ROOT_TOLERANCE_MM)
            roots.append(s[valid])
            root_rows.append(rows[valid])
        else:
            # f'(s)=R*cos(phi+k*s-alpha)+n_z*sinh(eta). Enumerating both
            # stationary angles partitions the entire half-turn into monotonic
            # intervals, including roots that a single end-to-end bracket misses.
            radius = np.hypot(n[:, 0], n[:, 1])
            alpha = np.arctan2(n[:, 1], n[:, 0])
            target = np.divide(-n[:, 2] * sh, radius, out=np.full_like(radius, 2.),
                               where=radius > 1e-14)
            possible = abs(target) <= 1.
            delta = np.arccos(np.clip(target, -1., 1.))
            boundaries = [np.zeros(len(indices)), np.full(len(indices), limit)]
            for angle in (alpha - delta, alpha + delta):
                phase = np.mod(math.copysign(1., k) * (angle - phi), 2. * math.pi)
                s = phase / abs(k)
                boundaries.append(np.where(possible & (s > 0.) & (s < limit), s, limit))
            cuts = np.sort(np.stack(boundaries, axis=1), axis=1)
            for interval in range(3):
                low, high = cuts[:, interval], cuts[:, interval + 1]
                rows = np.flatnonzero(high - low > ROOT_TOLERANCE_MM)
                fl, fh = residual(low[rows], rows), residual(high[rows], rows)
                valid = ((fl * fh <= 0.) | (abs(fl) <= ROOT_TOLERANCE_MM)
                         | (abs(fh) <= ROOT_TOLERANCE_MM))
                rows, fl, fh = rows[valid], fl[valid], fh[valid]
                a, b = low[rows].copy(), high[rows].copy()
                if not len(rows):
                    continue
                # Preserve exact tangent roots at derivative extrema.
                at_a, at_b = abs(fl) <= ROOT_TOLERANCE_MM, abs(fh) <= ROOT_TOLERANCE_MM
                for _ in range(34):
                    mid = .5 * (a + b)
                    fm = residual(mid, rows)
                    same = (fl * fm > 0.)
                    a, fl = np.where(same, mid, a), np.where(same, fm, fl)
                    b = np.where(same, b, mid)
                s = np.where(at_a, low[rows], np.where(at_b, high[rows], .5 * (a + b)))
                valid = ((s > ROOT_TOLERANCE_MM)
                         & (abs(residual(s, rows)) <= 2. * ROOT_TOLERANCE_MM))
                roots.append(s[valid])
                root_rows.append(rows[valid])
        if not roots:
            return []
        s, rows = np.concatenate(roots), np.concatenate(root_rows)
        point_delta = positions(track, s) - center[rows]
        ui = np.sum(point_delta * self.u[indices[rows]], axis=1)
        vi = np.sum(point_delta * self.v[indices[rows]], axis=1)
        inside = ((abs(ui) <= self.hu[indices[rows]] + BOUND_TOLERANCE_MM)
                  & (abs(vi) <= self.hv[indices[rows]] + BOUND_TOLERANCE_MM))
        first = {}
        for i, path in zip(indices[rows[inside]], s[inside]):
            first[int(i)] = min(float(path), first.get(int(i), math.inf))
        return sorted(first.items(), key=lambda item: item[1])


def track_sensor_hits(layout, tracks, *, return_patch_hits=False, index=None,
                      host_radius_mm=1140., host_half_z_mm=3150.):
    """Per-track reached IDs; physical sensor IDs deduplicate pixel chip islands."""
    index = index or SurfaceIndex(layout)
    result = []
    for track in tracks:
        reached = index.hits(track, host_radius_mm=host_radius_mm,
                             host_half_z_mm=host_half_z_mm)
        result.append(list(dict.fromkeys(
            layout["modules"][i]["id"] if return_patch_hits else
            layout["modules"][i].get("sensor_id", layout["modules"][i]["id"])
            for i, _ in reached)))
    return result


def _radial_paths(track, radius_mm, limit):
    """All ideal-cylinder crossings within this track's first traversal."""
    origin, _, phi, k = _parameters(track)
    if abs(k) < 1e-15:
        projection = origin[0] * math.cos(phi) + origin[1] * math.sin(phi)
        discriminant = projection ** 2 + radius_mm ** 2 - float(origin[:2] @ origin[:2])
        if discriminant < 0:
            return []
        values = [-projection - math.sqrt(discriminant), -projection + math.sqrt(discriminant)]
    else:
        cx, cy = origin[0] - math.sin(phi) / k, origin[1] + math.cos(phi) / k
        a, b = 2. * cx / k, -2. * cy / k
        target = (radius_mm ** 2 - cx ** 2 - cy ** 2 - 1. / k ** 2) / math.hypot(a, b)
        if abs(target) > 1. + 1e-12:
            return []
        alpha, delta = math.atan2(a, b), math.acos(max(-1., min(1., target)))
        values = [(math.copysign(1., k) * (angle - phi)) % (2. * math.pi) / abs(k)
                  for angle in (alpha - delta, alpha + delta)]
    return sorted(set(s for s in values if ROOT_TOLERANCE_MM < s <= limit + ROOT_TOLERANCE_MM))


def ideal_layer_hits(layers, track, *, host_radius_mm=1140., host_half_z_mm=3150.):
    """Reached original DES-006 ideal layers (m inputs; returned stable IDs).

    Inclined rings are surfaces of revolution of their finite r-z segments,
    not enlarged to match the finite modules placed on them. Coverage beyond
    these segments is reported separately by ``evaluate``.
    """
    limit = traversal_limit(track, host_radius_mm, host_half_z_mm)
    origin, eta, _, _ = _parameters(track)
    sh, hits = math.sinh(eta), []
    radial_cache = {}
    for layer in layers:
        kind = layer["kind"]
        if kind == "cylinder":
            radius = 1000. * layer["r_m"]
            if radius not in radial_cache:
                radial_cache[radius] = _radial_paths(track, radius, limit)
            found = any(1000. * layer["z_min_m"] - BOUND_TOLERANCE_MM
                        <= origin[2] + s * sh
                        <= 1000. * layer["z_max_m"] + BOUND_TOLERANCE_MM
                        for s in radial_cache[radius])
        elif kind in ("disc", "disk"):
            s = (1000. * layer["z_m"] - origin[2]) / sh if sh else -1.
            found = False
            if ROOT_TOLERANCE_MM < s <= limit + ROOT_TOLERANCE_MM:
                radius = float(np.linalg.norm(positions(track, s)[:2]))
                found = (1000. * layer["r_min_m"] - BOUND_TOLERANCE_MM <= radius
                         <= 1000. * layer["r_max_m"] + BOUND_TOLERANCE_MM)
        elif kind == "inclined_ring":
            z1, z2 = 1000. * layer["z1_m"], 1000. * layer["z2_m"]
            r1, r2 = 1000. * layer["r1_m"], 1000. * layer["r2_m"]
            nr, nz = layer["normal_r"], layer["normal_z"]
            r0, z0 = 1000. * layer["r0_m"], 1000. * layer["z0_m"]
            if nr <= 0 or not math.isclose(nr * nr + nz * nz, 1., abs_tol=1e-8):
                raise ValueError("Ideal inclined ring requires unit normal with positive radial component")
            if min(r1, r2) <= math.hypot(*origin[:2]):
                raise ValueError("Ideal inclined ring must lie radially outside the track origin")
            if max(abs(nr * (r1-r0) + nz * (z1-z0)),
                   abs(nr * (r2-r0) + nz * (z2-z0))) > BOUND_TOLERANCE_MM:
                raise ValueError("Inclined ideal endpoints are inconsistent with their declared r-z plane")
            found = False
            if sh:
                low, high = sorted(((z1 - origin[2]) / sh, (z2 - origin[2]) / sh))
                low, high = max(0., low), min(limit, high)
                if high >= low:
                    def value(s):
                        point = positions(track, s)
                        return (nr * (np.hypot(point[..., 0], point[..., 1]) - 1000. * layer["r0_m"])
                                + nz * (point[..., 2] - 1000. * layer["z0_m"]))

                    # In the declared pint rings, outward radial motion and
                    # signed longitudinal motion both increase this residual.
                    # Endpoint bracketing is therefore complete for those rings.
                    if nz * sh < 0:
                        raise ValueError("Inclined-ring orientation outside the supported outward ideal contract")
                    fl, fh = float(value(low)), float(value(high))
                    found = (low > 0. and min(abs(fl), abs(fh)) <= ROOT_TOLERANCE_MM) or fl * fh < 0.
            elif min(z1, z2) <= origin[2] <= max(z1, z2):
                radius = 1000. * layer["r0_m"] - nz * (origin[2] - 1000. * layer["z0_m"]) / nr
                found = bool(_radial_paths(track, radius, limit))
        else:
            raise ValueError(f"Unsupported ideal layer kind: {kind}")
        if found:
            hits.append(layer["id"])
    return hits


def _distribution(values):
    values = np.asarray(values)
    if not len(values):
        return {"min": None, "mean": None, "p01": None, "p05": None,
                "median": None, "max": None, "histogram": {}}
    unique, count = np.unique(values, return_counts=True)
    return {"min": int(values.min()), "mean": float(values.mean()),
            "p01": float(np.quantile(values, .01)), "p05": float(np.quantile(values, .05)),
            "median": float(np.median(values)), "max": int(values.max()),
            "histogram": {str(int(v)): int(n) for v, n in zip(unique, count)}}


def _summarize_columns(columns, selection=None):
    selection = slice(None) if selection is None else selection
    arrays = {key: np.asarray(value)[selection] for key, value in columns.items()}
    count = len(arrays["sensor_hits"])
    eligible = arrays["ideal_stations"] > 0
    missing = arrays["missing_stations"]
    denominator = int(arrays["ideal_stations"].sum())
    return {"tracks": count, **{key: _distribution(value) for key, value in arrays.items()},
            "eligible_tracks": int(eligible.sum()),
            "fraction_with_any_sensor_hit": float(np.mean(arrays["sensor_hits"] > 0)) if count else None,
            "fraction_all_ideal_stations_hit": float(np.mean(missing[eligible] == 0)) if np.any(eligible) else None,
            "missing_ideal_station_fraction": float(missing.sum()) / denominator if denominator else None}


def evaluate(layout, tracks, *, host_radius_mm=1140., host_half_z_mm=3150.,
             return_track_hits=False, eta_bin_edges=None, phi_bin_count=12,
             index=None):
    """JSON-safe finite-sensor and ideal-reference coverage report.

    ``per_track`` contains parallel columns (one entry per input track), plus
    the same columns under ``per_subdetector`` for pixel, short_strip and
    long_strip. Stations deduplicate station_id; long-strip stations require
    both faces of the *same* module_id. Ideal missing stations use set
    subtraction rather than total-count subtraction, so an extra hit cannot
    conceal a hole in another layer. The field is pT, explicitly not total p.
    """
    tracks = list(tracks)
    index = index or SurfaceIndex(layout)
    layers = layout.get("layers", [])
    modules = layout["modules"]
    layer_station = {layer["id"]: layer.get("station_group", layer["id"]) for layer in layers}
    layer_subsystem = {layer["id"]: layer["subsystem"] for layer in layers}
    layer_region = {layer["id"]: {"cylinder": "barrel", "disc": "endcap", "disk": "endcap",
                                  "inclined_ring": "inclined"}[layer["kind"]] for layer in layers}
    for module in modules:
        lid = module["layer_id"]
        layer_station[lid] = module.get("station_id", layer_station.get(lid, lid))
        layer_subsystem[lid] = module["subsystem"]
        layer_region[lid] = module.get("region", layer_region.get(lid, "unknown"))
    subsystem_names = sorted(set(layer_subsystem.values()))
    regions = sorted(set(layer_region.values()))
    keys = ("sensor_hits", "complete_long_strip_pairs", "orphan_long_strip_faces", "stations", "ideal_stations",
            "missing_stations", "extra_stations")
    columns = {key: [] for key in keys}
    sub_columns = {name: {key: [] for key in keys} for name in subsystem_names}
    region_columns = {name: {key: [] for key in keys} for name in regions}
    subsystem_layers = {name: {lid for lid, sub in layer_subsystem.items() if sub == name}
                        for name in subsystem_names}
    region_layers = {name: {lid for lid, region in layer_region.items() if region == name}
                     for name in regions}
    combined_layers = {f"{sub}_{region}": subsystem_layers[sub] & region_layers[region]
                       for sub in subsystem_names for region in regions
                       if subsystem_layers[sub] & region_layers[region]}
    combined_columns = {name: {key: [] for key in keys} for name in combined_layers}
    layer_stats = {lid: {"subsystem": layer_subsystem[lid], "region": layer_region[lid],
                         "station_id": layer_station[lid], "sensor_hits": 0,
                         "complete_pairs": 0, "orphan_long_strip_faces": 0,
                         "tracks_with_hit": 0, "ideal_eligible_tracks": 0,
                         "missed_ideal_tracks": 0, "extra_tracks": 0}
                   for lid in layer_subsystem}
    track_patch_hits = []
    track_sensor_ids = []
    for track in tracks:
        reached = index.hits(track, host_radius_mm=host_radius_mm, host_half_z_mm=host_half_z_mm)
        seen_sensors = {}
        pair_faces = defaultdict(set)
        pair_layer = {}
        for i, _ in reached:
            module = modules[i]
            sensor = module.get("sensor_id", module["id"])
            seen_sensors[sensor] = module["layer_id"]
            if module["subsystem"] == "long_strip":
                pair = module["module_id"]
                pair_faces[pair].add(module.get("face", sensor))
                pair_layer[pair] = module["layer_id"]
        complete_pairs = {pair: pair_layer[pair] for pair, faces in pair_faces.items() if len(faces) >= 2}
        active_layers = {lid for lid in seen_sensors.values() if layer_subsystem[lid] != "long_strip"}
        active_layers.update(complete_pairs.values())
        ideal_layers = set(ideal_layer_hits(layers, track, host_radius_mm=host_radius_mm,
                                            host_half_z_mm=host_half_z_mm))

        def append_columns(target, selected_layers):
            active = {layer_station[lid] for lid in active_layers & selected_layers}
            ideal = {layer_station[lid] for lid in ideal_layers & selected_layers}
            pairs = sum(lid in selected_layers for lid in complete_pairs.values())
            long_faces = sum(lid in selected_layers and layer_subsystem[lid] == "long_strip"
                             for lid in seen_sensors.values())
            values = (sum(lid in selected_layers for lid in seen_sensors.values()),
                      pairs, long_faces - 2 * pairs,
                      len(active), len(ideal), len(ideal - active), len(active - ideal))
            for key, value in zip(keys, values):
                target[key].append(value)

        append_columns(columns, set(layer_subsystem))
        for name in subsystem_names:
            append_columns(sub_columns[name], subsystem_layers[name])
        for name in regions:
            append_columns(region_columns[name], region_layers[name])
        for name, selected in combined_layers.items():
            append_columns(combined_columns[name], selected)
        for lid, stats in layer_stats.items():
            stats["sensor_hits"] += sum(x == lid for x in seen_sensors.values())
            stats["complete_pairs"] += sum(x == lid for x in complete_pairs.values())
            if layer_subsystem[lid] == "long_strip":
                stats["orphan_long_strip_faces"] = stats["sensor_hits"] - 2 * stats["complete_pairs"]
            stats["tracks_with_hit"] += int(lid in active_layers)
            stats["ideal_eligible_tracks"] += int(lid in ideal_layers)
            stats["missed_ideal_tracks"] += int(lid in ideal_layers and lid not in active_layers)
            stats["extra_tracks"] += int(lid not in ideal_layers and lid in active_layers)
        if return_track_hits:
            track_patch_hits.append([modules[i]["id"] for i, _ in reached])
            track_sensor_ids.append(list(seen_sensors))
    for stats in layer_stats.values():
        denominator = stats["ideal_eligible_tracks"]
        stats["missing_ideal_fraction"] = stats["missed_ideal_tracks"] / denominator if denominator else None
    eta_edges = list(eta_bin_edges) if eta_bin_edges is not None else list(np.linspace(-4., 4., 17))
    eta = np.asarray([track["eta"] for track in tracks])
    phi = np.mod(np.asarray([track["phi"] for track in tracks]) + np.pi, 2. * np.pi) - np.pi
    directional = []
    for low, high in zip(eta_edges[:-1], eta_edges[1:]):
        selected = (eta >= low) & ((eta <= high) if high == eta_edges[-1] else (eta < high))
        directional.append({"eta_min": float(low), "eta_max": float(high),
                            **_summarize_columns(columns, selected),
                            "per_subdetector": {name: _summarize_columns(data, selected)
                                                for name, data in sub_columns.items()}})
    phi_profiles = []
    for low, high in zip(np.linspace(-np.pi, np.pi, phi_bin_count + 1)[:-1],
                         np.linspace(-np.pi, np.pi, phi_bin_count + 1)[1:]):
        selected = (phi >= low) & (phi < high)
        phi_profiles.append({"phi_min": float(low), "phi_max": float(high),
                             **_summarize_columns(columns, selected)})
    result = {"definition": "PROTOTYPE first host traversal; active patch roots; physical sensor deduplication; same-module stereo pairs",
              "path_limit": "first r=host_radius or abs(z)=host_half_z exit, or transverse half-turn",
              "host_radius_mm": host_radius_mm, "host_half_z_mm": host_half_z_mm,
              "root_tolerance_mm": ROOT_TOLERANCE_MM, "bound_tolerance_mm": BOUND_TOLERANCE_MM,
              "total": _summarize_columns(columns),
              "per_subdetector": {name: _summarize_columns(data) for name, data in sub_columns.items()},
              "per_region": {name: _summarize_columns(data) for name, data in region_columns.items()},
              "per_subdetector_region": {name: _summarize_columns(data) for name, data in combined_columns.items()},
              "per_layer": layer_stats, "eta_profiles": directional, "phi_profiles": phi_profiles,
              "per_track": {**columns, "per_subdetector": sub_columns, "per_region": region_columns,
                            "per_subdetector_region": combined_columns}}
    if return_track_hits:
        result["per_track"]["patch_ids"] = track_patch_hits
        result["per_track"]["sensor_ids"] = track_sensor_ids
    return result
