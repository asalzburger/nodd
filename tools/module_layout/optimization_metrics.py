"""PROTOTYPE coverage and path-spacing diagnostics for constrained layout scans.

These are sampled geometric measurements, not a resolution model or an optimizer.
Use a frozen reference_layers denominator and identical tracks/host across cases.
Keep coverage constraints ahead of gap comparisons: an inter-hit statistic alone
can improve simply because a track lost its first or last hit. Boundary-anchored
gaps include the origin and fixed host exit, including for zero/one-hit tracks.
"""

from collections import defaultdict
import hashlib
import json
import math

import numpy as np

if __package__:
    from .intersections import (BOUND_TOLERANCE_MM, SurfaceIndex, ideal_layer_hits,
                                positions, traversal_limit)
else:
    from intersections import (BOUND_TOLERANCE_MM, SurfaceIndex, ideal_layer_hits,
                               positions, traversal_limit)


COUNT_FIELDS = ("sensor_hits", "stations", "ideal_stations", "missing_stations",
                "extra_stations", "complete_long_strip_pairs", "orphan_long_strip_faces")
SPACING_FIELDS = ("max_inter_hit_gap_mm", "mean_inter_hit_gap_mm",
                  "max_inter_hit_chord_mm", "max_boundary_gap_mm",
                  "first_path_mm", "last_path_mm", "origin_to_first_mm", "last_to_exit_mm")
# DES-011 SO-C16 diagnostic choices, not detector dimensions or statistical bins.
COVERAGE_ETA_EDGES = tuple(-4. + .5*i for i in range(17))
COVERAGE_VERTEX_PLANES_MM = (-150., 0., 150.)


def _distribution(values):
    """Null is undefined, never a zero gap or a successfully covered track."""
    data = np.asarray([v for v in values if v is not None], dtype=float)
    if not len(data):
        return dict(count=0, min=None, mean=None, median=None, p95=None, p99=None, max=None)
    return dict(count=len(data), min=float(data.min()), mean=float(data.mean()),
                median=float(np.median(data)), p95=float(np.quantile(data, .95)),
                p99=float(np.quantile(data, .99)), max=float(data.max()))


def _validate_identity(layout, reference):
    """Reject ambiguous station/sensor identities rather than mix subsystems."""
    stations, layer_stations, sensors, assemblies = {}, {}, {}, {}
    for layer in [*reference, *layout.get("layers", [])]:
        lid = layer["id"]
        station = layer.get("station_group", lid)
        if lid in layer_stations and layer_stations[lid] != station:
            raise ValueError("A layer changed station identity relative to its reference")
        layer_stations[lid] = station
        if station in stations and stations[station] != layer["subsystem"]:
            raise ValueError("A station cannot belong to different subsystems")
        stations[station] = layer["subsystem"]
    for module in layout["modules"]:
        station = module.get("station_id", layer_stations.get(module["layer_id"], module["layer_id"]))
        if module["layer_id"] in layer_stations and layer_stations[module["layer_id"]] != station:
            raise ValueError("Module station differs from its ideal-layer station identity")
        layer_stations[module["layer_id"]] = station
        if station in stations and stations[station] != module["subsystem"]:
            raise ValueError("A station cannot belong to different subsystems")
        stations[station] = module["subsystem"]
        sensor = module.get("sensor_id", module["id"])
        identity = (module["module_id"], module["layer_id"], station, module["subsystem"], module.get("face", 0))
        if sensor in sensors and sensors[sensor] != identity:
            raise ValueError("A physical sensor ID has inconsistent identity")
        sensors[sensor] = identity
        pair = module["module_id"]
        assembly = (station, module["subsystem"])
        if pair in assemblies and assemblies[pair] != assembly:
            raise ValueError("A module assembly cannot span stations or subsystems")
        assemblies[pair] = assembly
        if module["subsystem"] == "long_strip" and module.get("face") not in (0, 1):
            raise ValueError("Long-strip paired sensors require face 0 or 1")
    return stations, layer_stations


def _measurement_events(modules, reached, layer_stations):
    """First physical-sensor encounter and first usable measurement per station.

    Long-strip station path is the mean of the two face paths of the earliest
    complete module. Faces from different assemblies never complete a station.
    Patch ordering, overlap islands and repeated entries cannot add stations.
    """
    sensors = {}
    for patch_index, path in reached:
        module = modules[patch_index]
        sensor_id = module.get("sensor_id", module["id"])
        if sensor_id not in sensors or path < sensors[sensor_id]["transverse_path_mm"]:
            sensors[sensor_id] = dict(id=sensor_id, module_id=module["module_id"],
                                     station_id=layer_stations[module["layer_id"]],
                                     subsystem=module["subsystem"], face=module.get("face", 0),
                                     transverse_path_mm=float(path))
    pair_faces, station_candidates = defaultdict(dict), []
    for event in sensors.values():
        if event["subsystem"] == "long_strip":
            faces = pair_faces[event["module_id"]]
            if event["face"] in faces:
                raise ValueError("A long-strip assembly has multiple physical sensors on one face")
            faces[event["face"]] = event
        else:
            station_candidates.append(event)
    complete, orphan = [], []
    for pair, faces in pair_faces.items():
        if len(faces) == 2:
            event = dict(faces[0], id=faces[0]["station_id"], module_id=pair,
                         transverse_path_mm=(faces[0]["transverse_path_mm"] +
                                             faces[1]["transverse_path_mm"])/2.)
            station_candidates.append(event)
            complete.append(event)
        else:
            orphan.extend(faces.values())
    station_events = {}
    for event in sorted(station_candidates, key=lambda e: (e["transverse_path_mm"], str(e["id"]))):
        station_events.setdefault(event["station_id"], dict(event, id=event["station_id"]))
    ordered_sensors = sorted(sensors.values(), key=lambda e: (e["transverse_path_mm"], str(e["id"])))
    return ordered_sensors, list(station_events.values()), complete, orphan


def _spacing(events, track, limit):
    paths = np.asarray([event["transverse_path_mm"] for event in events], dtype=float)
    # Root tolerance can place a last intersection just beyond the host. Retain
    # that root diagnostically while clipping only the boundary partition.
    factor = math.cosh(track["eta"])
    arc = paths * factor
    gaps = np.diff(arc)
    points = positions(track, paths)
    chords = np.linalg.norm(np.diff(points, axis=0), axis=1)
    boundaries = np.concatenate(([0.], np.clip(arc, 0., limit*factor), [limit*factor]))
    return dict(ids=[event["id"] for event in events], path_mm=arc.tolist(),
                inter_hit_gaps_mm=gaps.tolist(), inter_hit_chords_mm=chords.tolist(),
                max_inter_hit_gap_mm=float(gaps.max()) if len(gaps) else None,
                mean_inter_hit_gap_mm=float(gaps.mean()) if len(gaps) else None,
                max_inter_hit_chord_mm=float(chords.max()) if len(chords) else None,
                max_boundary_gap_mm=float(np.diff(boundaries).max()),
                first_path_mm=float(arc[0]) if len(arc) else None,
                last_path_mm=float(arc[-1]) if len(arc) else None,
                origin_to_first_mm=float(boundaries[1]) if len(arc) else None,
                last_to_exit_mm=float(boundaries[-1]-boundaries[-2]) if len(arc) else None)


def _track_group(sensor_events, station_events, complete, orphan, ideal, track, limit):
    active = {event["id"] for event in station_events}
    return dict(sensor_hits=len(sensor_events), stations=len(active), ideal_stations=len(ideal),
                missing_stations=len(ideal-active), extra_stations=len(active-ideal),
                missing_station_ids=sorted(ideal-active, key=str),
                extra_station_ids=sorted(active-ideal, key=str),
                complete_long_strip_pairs=len(complete), orphan_long_strip_faces=len(orphan),
                sensor_spacing=_spacing(sensor_events, track, limit),
                station_spacing=_spacing(station_events, track, limit))


def _summarize(records):
    count = len(records)
    eligible = [r for r in records if r["ideal_stations"] > 0]
    denominator = sum(r["ideal_stations"] for r in records)
    summary = dict(tracks=count, eligible_tracks=len(eligible),
                   ideal_station_opportunities=denominator,
                   missing_station_opportunities=sum(r["missing_stations"] for r in records),
                   fraction_with_any_sensor_hit=sum(r["sensor_hits"] > 0 for r in records)/count if count else None,
                   fraction_all_ideal_stations_hit=sum(r["missing_stations"] == 0 for r in eligible)/len(eligible) if eligible else None,
                   missing_ideal_station_fraction=sum(r["missing_stations"] for r in records)/denominator if denominator else None,
                   tracks_with_at_least_two_stations=sum(r["stations"] >= 2 for r in records),
                   **{key: _distribution(r[key] for r in records) for key in COUNT_FIELDS})
    for kind in ("sensor_spacing", "station_spacing"):
        summary[kind] = {key: _distribution(r[kind][key] for r in records) for key in SPACING_FIELDS}
        # Both a pooled gap distribution and equal-track distributions are kept:
        # tracks crossing more stations must not silently dominate a track score.
        summary[kind]["pooled_inter_hit_gaps_mm"] = _distribution(
            gap for r in records for gap in r[kind]["inter_hit_gaps_mm"])
        summary[kind]["pooled_inter_hit_chords_mm"] = _distribution(
            gap for r in records for gap in r[kind]["inter_hit_chords_mm"])
    summary["worst_boundary_gap_track_index"] = max(
        range(count), key=lambda i: records[i]["station_spacing"]["max_boundary_gap_mm"]) if count else None
    summary["worst_missing_stations_track_index"] = max(
        range(count), key=lambda i: records[i]["missing_stations"]) if count else None
    return summary


def summarize_cohort(records):
    """Summarize saved per-track rows without repeating the intersection oracle.

    Worst-track indices are local to this cohort; ``track_indices`` maps them to
    the original input ordering. All rows must contain the same subsystem keys.
    """
    records = list(records)
    names = set(records[0]["per_subdetector"]) if records else set()
    if any(set(row["per_subdetector"]) != names for row in records):
        raise ValueError("Cohort rows must have homogeneous subsystem keys")
    return dict(total=_summarize([row["total"] for row in records]),
                per_subdetector={name: _summarize([row["per_subdetector"][name] for row in records])
                                 for name in sorted(names)},
                track_indices=[row["track_index"] for row in records],
                index_definition="Worst-track indices are cohort-local; map through track_indices")


def _coverage_counts(records):
    """Integer counts support exact paired comparisons without float tolerances."""
    count = len(records)
    stations = sum(row["stations"] for row in records)
    zero = sum(row["stations"] == 0 for row in records)
    ideal = sum(row["ideal_stations"] for row in records)
    missing = sum(row["missing_stations"] for row in records)
    return dict(tracks=count, station_sum=stations,
                mean_stations=stations/count if count else None,
                min_stations=min((row["stations"] for row in records), default=None),
                zero_station_tracks=zero, fraction_zero_stations=zero/count if count else None,
                eligible_tracks=sum(row["ideal_stations"] > 0 for row in records),
                ideal_station_opportunities=ideal, missing_station_opportunities=missing,
                missing_ideal_station_fraction=missing/ideal if ideal else None)


def summarize_coverage_strata(records, *, eta_bin_edges=COVERAGE_ETA_EDGES,
                              vertex_z_planes_mm=COVERAGE_VERTEX_PLANES_MM):
    """Retain local coverage, including an exact eta=0, vertex-z=0 control.

    Structured tracks are grouped by eta band and exact sampled vertex plane;
    off-grid and other interior vertices are separate diagnostics. Eta bins are
    left-closed/right-open, except the last includes its upper endpoint. Tracks
    outside the eta range are explicitly retained. This is a finite-sample
    diagnostic, not an estimate of a blind region's continuous angular extent.
    Hashes include ordered physical track parameters and cohort membership.
    """
    records = list(records)
    edges = tuple(float(v) for v in eta_bin_edges)
    planes = tuple(float(v) for v in vertex_z_planes_mm)
    if (len(edges) < 2 or not all(math.isfinite(v) for v in edges)
            or any(a >= b for a, b in zip(edges, edges[1:]))):
        raise ValueError("Eta bin edges must be finite and strictly increasing")
    if not planes or not all(math.isfinite(v) for v in planes) or len(set(planes)) != len(planes):
        raise ValueError("Vertex planes must be finite, nonempty and unique")
    names = sorted(records[0]["per_subdetector"]) if records else []
    if any(sorted(row["per_subdetector"]) != names for row in records):
        raise ValueError("Coverage strata require homogeneous subsystem keys")
    tracks = []
    for row in records:
        track = row["track"]
        identity = dict(origin_mm=[float(v) for v in track["origin_mm"]],
                        eta=float(track["eta"]), phi=float(track["phi"]),
                        charge=float(track.get("charge", 1.)),
                        pt_GeV=float(track.get("pt_GeV", 1.)),
                        field_T=float(track.get("field_T", 0.)),
                        cohort=track.get("cohort", "unlabelled"))
        if len(identity["origin_mm"]) != 3:
            raise ValueError("A track origin must have three coordinates")
        tracks.append(identity)

    def sample_hash(indices):
        encoded = json.dumps([tracks[i] for i in indices], sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode()
        return hashlib.sha256(encoded).hexdigest()

    central_id = "central_eta0_z0"
    groups = {central_id: []}
    identities = {central_id: dict(kind="central", eta=0., vertex_z_mm=0.)}
    for i, track in enumerate(tracks):
        eta, z = track["eta"], track["origin_mm"][2]
        if eta == 0. and z == 0.:
            groups[central_id].append(i)
        if eta < edges[0]:
            band, bounds = "below_range", [None, edges[0]]
        elif eta > edges[-1]:
            band, bounds = "above_range", [edges[-1], None]
        else:
            j = min(int(np.searchsorted(edges, eta, side="right"))-1, len(edges)-2)
            band, bounds = f"eta_{j:02d}", [edges[j], edges[j+1]]
        if track["cohort"] == "off_grid":
            key, kind, plane = f"off_grid/{band}", "off_grid", None
        elif z in planes:
            key, kind, plane = f"grid/{band}/vertex_{planes.index(z)}", "eta_vertex_plane", z
        else:
            key, kind, plane = f"other_interior/{band}", "other_interior", None
        groups.setdefault(key, []).append(i)
        identities[key] = dict(kind=kind, eta_bounds=bounds, vertex_z_mm=plane,
                               upper_endpoint_included=bounds[1] == edges[-1])
    strata = {}
    for key, indices in sorted(groups.items()):
        chosen = [records[i] for i in indices]
        strata[key] = dict(identity=identities[key], tracks=len(indices),
                           sample_sha256=sample_hash(indices),
                           total=_coverage_counts([row["total"] for row in chosen]),
                           per_subdetector={name: _coverage_counts(
                               [row["per_subdetector"][name] for row in chosen]) for name in names})
    return dict(schema_version=1, tracks=len(records), sample_sha256=sample_hash(range(len(records))),
                eta_bin_edges=list(edges), vertex_z_planes_mm=list(planes),
                central_stratum_id=central_id, strata=strata,
                definition="DES-011 SO-C16 paired finite-sample local coverage; exact central rays and eta/vertex-plane bands",
                bin_boundary="left-closed/right-open; final upper endpoint included; out-of-range and interior tracks retained separately")


def coverage_strata_regressions(candidate_spacing, baseline_spacing):
    """Compare one mode's matched samples under the DES-011 SO-C16 guard.

    Central station means must not decrease and zero-station fractions must not
    increase, separately in total and per subsystem. Elsewhere only a newly
    completely blind structured eta/vertex-plane stratum is a hard failure.
    Smaller local losses and interior/off-grid changes remain explicit. Exact
    integer sums/counts on identical samples avoid numerical guard tolerances.
    Missing ideal opportunities are reported; they are not an eligibility gate
    that could excuse losing a previously reached station.
    """
    candidate, baseline = candidate_spacing["local_coverage"], baseline_spacing["local_coverage"]
    for key in ("schema_version", "tracks", "sample_sha256", "eta_bin_edges",
                "vertex_z_planes_mm", "central_stratum_id"):
        if candidate[key] != baseline[key]:
            raise ValueError(f"Coverage comparisons require identical paired samples and strata: {key}")
    if candidate["strata"].keys() != baseline["strata"].keys():
        raise ValueError("Coverage comparisons require identical stratum identities")
    central_id = baseline["central_stratum_id"]
    tested = baseline["strata"][central_id]["tracks"] > 0
    central_failures, blind, regressions, changes = [], [], [], []
    for key, old in baseline["strata"].items():
        new = candidate["strata"][key]
        if any(new[field] != old[field] for field in ("identity", "tracks", "sample_sha256")):
            raise ValueError(f"Coverage comparisons require identical paired stratum samples: {key}")
        if new["per_subdetector"].keys() != old["per_subdetector"].keys():
            raise ValueError("Coverage comparisons require identical subsystem identities")
        scopes = [("total", old["total"], new["total"])] + [
            (name, old["per_subdetector"][name], new["per_subdetector"][name])
            for name in sorted(old["per_subdetector"])]
        for scope, before, after in scopes:
            if before["tracks"] != old["tracks"] or after["tracks"] != new["tracks"]:
                raise ValueError("Coverage counts must describe the paired stratum")
            change = dict(stratum_id=key, identity=old["identity"], subsystem=scope,
                          tracks=old["tracks"], sample_sha256=old["sample_sha256"],
                          baseline=before, candidate=after,
                          station_sum_delta=after["station_sum"]-before["station_sum"],
                          zero_station_tracks_delta=after["zero_station_tracks"]-before["zero_station_tracks"],
                          missing_station_opportunities_delta=after["missing_station_opportunities"]-before["missing_station_opportunities"])
            change["mean_stations_delta"] = change["station_sum_delta"]/old["tracks"] if old["tracks"] else None
            change["fraction_zero_stations_delta"] = change["zero_station_tracks_delta"]/old["tracks"] if old["tracks"] else None
            changes.append(change)
            coverage_loss = change["station_sum_delta"] < 0 or change["zero_station_tracks_delta"] > 0
            if coverage_loss or change["missing_station_opportunities_delta"] > 0:
                regressions.append(change)
            if key == central_id and coverage_loss:
                central_failures.append(change)
            if (old["identity"]["kind"] == "eta_vertex_plane"
                    and before["station_sum"] > 0 and after["station_sum"] == 0):
                blind.append(change)
    central_pass = tested and not central_failures
    return dict(passed=central_pass and not blind, central_tested=tested,
                central_pass=central_pass, no_new_blind_strata_pass=not blind,
                central_failure_reason=None if tested else "No exact eta=0, vertex-z=0 tracks; central guard untested",
                sample_sha256=baseline["sample_sha256"], central_failures=central_failures,
                newly_blind_strata=blind, local_regressions=regressions, local_changes=changes,
                definition="Strict central mean/zero-station nonloss; no new fully blind structured eta/vertex-plane stratum; all smaller changes reported")


def evaluate_spacing(layout, tracks, *, reference_layers=None, index=None,
                     host_radius_mm=1140., host_half_z_mm=3150., return_per_track=True):
    """Measure coverage and spacing in one finite-surface oracle pass per track.

    Supply the same frozen ``reference_layers`` for moved candidates; the default
    uses this layout's ideal layers and is explicitly labelled as candidate-local.
    ``total`` and ``per_subdetector`` include coverage counts/fractions and gap
    distributions; ``per_track`` optionally retains ordered identities/distances.
    Arc lengths are 3D path lengths, not transverse arc or chord lengths. Stereo
    faces remain separate in sensor diagnostics but form only one usable station.

    Sample generation remains the caller's responsibility: use sampling.directions
    and tracks_for for common straight/positive/negative samples, with pT=1 GeV,
    B=3 T, x/y in [0,1] mm and z in [-150,150] mm for the declared study. Freeze a
    separate-seed off-grid holdout before ranking; do not optimize on that holdout.
    A finite scan and finite sample never establish a global or continuous optimum.
    """
    if not all(math.isfinite(v) and v > 0 for v in (host_radius_mm, host_half_z_mm)):
        raise ValueError("Host dimensions must be finite and positive")
    tracks = list(tracks)
    reference = list(layout.get("layers", []) if reference_layers is None else reference_layers)
    station_subsystem, layer_stations = _validate_identity(layout, reference)
    index = index if index is not None else SurfaceIndex(layout)
    subsystem_names = sorted(set(station_subsystem.values()))
    rows, totals, subsystems = [], [], {name: [] for name in subsystem_names}
    for track_index, track in enumerate(tracks):
        limit = traversal_limit(track, host_radius_mm, host_half_z_mm)
        reached = index.hits(track, host_radius_mm=host_radius_mm, host_half_z_mm=host_half_z_mm)
        if any(not math.isfinite(s) or s <= 0 or s > limit+BOUND_TOLERANCE_MM for _, s in reached):
            raise ValueError("Oracle hits must lie within the first host traversal")
        sensors, stations, complete, orphan = _measurement_events(layout["modules"], reached, layer_stations)
        ideal = {layer_stations[lid] for lid in ideal_layer_hits(
            reference, track, host_radius_mm=host_radius_mm, host_half_z_mm=host_half_z_mm)}
        total = _track_group(sensors, stations, complete, orphan, ideal, track, limit)
        totals.append(total)
        by_subsystem = {}
        for name in subsystem_names:
            chosen = [[event for event in events if event["subsystem"] == name]
                      for events in (sensors, stations, complete, orphan)]
            sub_ideal = {sid for sid in ideal if station_subsystem[sid] == name}
            by_subsystem[name] = _track_group(*chosen, sub_ideal, track, limit)
            subsystems[name].append(by_subsystem[name])
        rows.append(dict(track_index=track_index, track=dict(track),
                         traversal_path_mm=limit*math.cosh(track["eta"]),
                         total=total, per_subdetector=by_subsystem))
    result = dict(schema_version=1, definition="PROTOTYPE geometric coverage and 3D path spacing",
                  reference_basis="candidate_local" if reference_layers is None else "external_fixed",
                  path_limit="first common-host exit or first transverse half-turn",
                  station_path="first physical sensor; long strips: midpoint of earliest complete same-module pair",
                  repeat_policy="earliest finite hit per patch, then sensor and station deduplication; no multi-turn tracking",
                  spacing_boundary="common origin-to-host traversal, including for each subsystem; not a subsystem active envelope",
                  selection_guard="Compare fixed-reference coverage before spacing; undefined inter-hit gaps are null, never zero",
                  host_radius_mm=host_radius_mm, host_half_z_mm=host_half_z_mm,
                  local_coverage=summarize_coverage_strata(rows),
                  total=_summarize(totals),
                  per_subdetector={name: _summarize(data) for name, data in subsystems.items()})
    if return_per_track:
        result["per_track"] = rows
    return result
