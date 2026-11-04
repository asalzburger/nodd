#!/usr/bin/env python3
"""DES042 PROTOTYPE: independent multiparticle matching and paired event inference.

No native truth-matcher output is used. Portable event chunks retain the truth,
measurement associations and raw candidate links required to replay matching.
"""
import argparse
from collections import Counter, defaultdict
import copy
import gzip
import hashlib
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
PITCHES = (.5, 1., 1.5, 2.)
STAGES = ("ckf", "ambi")
SELECTIONS = ("frozen", "guide")
SCOPES = ("inclusive", "hardscatter", "pileup")
DENOMINATORS = ("fiducial", "guide9", "reconstructable")
PT_EDGES = (1., 2., 5., 10., 20., 50., 100., 1000.)
ETA_EDGES = (-3., -2.5, -2., -1.5, -1., -.5, 0., .5, 1., 1.5, 2., 2.5, 3.)
CATEGORIES = ("eligible_generated", "out_of_scope_generated", "simulated_secondary", "fake")
BOOTSTRAP_SEED = 153044


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def write_json(path, value):
    payload = json.dumps(value, indent=2, sort_keys=True, allow_nan=False).encode() + b"\n"
    if str(path).endswith(".gz"):
        Path(path).write_bytes(gzip.compress(payload, mtime=0))
    else:
        Path(path).write_bytes(payload)


def read_json(path):
    payload = Path(path).read_bytes()
    return json.loads(gzip.decompress(payload) if str(path).endswith(".gz") else payload)


def sanitize(value):
    """Use the established DES042 logical-path scheme; raw bytes stay hashed."""
    if isinstance(value, dict):
        clean = {}
        for key, item in value.items():
            label = sanitize(key)
            if label in clean:
                raise ValueError("Sanitized metadata key collision")
            clean[label] = sanitize(item)
        return clean
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, str):
        if value.startswith("/"):
            path = Path(value)
            for base, role in ((ROOT, "repository"), (ROOT.parent, "workspace")):
                try:
                    return role + "/" + str(path.relative_to(base))
                except ValueError:
                    pass
            return "external/" + hashlib.sha256(value.encode()).hexdigest()[:12] + "/" + path.name
        if "=/" in value:
            prefix, path = value.split("=", 1)
            return prefix + "=" + sanitize(path)
    return value


def invariant_configuration(config):
    result = copy.deepcopy(config)
    for section in ("strixel_crosscheck", "ttbar_pileup"):
        if section in result:
            result[section].pop("pitch_mm", None)
    return result


def native_identity(report):
    """Hash original identities before path sanitation, avoiding alias collapse."""
    keys = ("source_revision", "source_sha256", "runtime_sha256", "sample_report_sha256", "seed", "profile")
    return {**{key: digest(report[key]) for key in keys},
            "invariant_campaign": digest(invariant_configuration(report["campaign"]))}


def identity(particle):
    result = tuple(particle["id"])
    if len(result) != 5 or any(type(x) is not int or not 0 <= x < 2**32 for x in result):
        raise ValueError("Invalid native five-component particle identity")
    return result


def finite(value):
    return value is not None and math.isfinite(value)


def fiducial(p):
    position = p["position_mm"]
    return (finite(p["charge"]) and p["charge"] != 0 and all(finite(v) for v in (*position, p["pt"], p["eta"]))
            and p["pt"] >= 1. and abs(p["eta"]) <= 3.
            and math.hypot(*position[:2]) <= 24. and abs(position[2]) <= 1000.)


def reco_coordinates(track):
    parameters = track["parameters"]
    if len(parameters) != 6 or not all(finite(x) for x in parameters):
        return None, None
    theta, qop = parameters[3:5]
    if not 0 < theta < math.pi or qop == 0:
        return None, None
    pt = math.sin(theta) / abs(qop)
    eta = -math.log(math.tan(theta / 2))
    return (pt, eta) if finite(pt) and finite(eta) else (None, None)


def quality_reason(track, minimum):
    indices = set(track["measurements"])
    if not track["reference"]:
        return "no_reference"
    if len(indices) < minimum:
        return "too_few_measurements"
    if not track.get("covariance_positive_definite", False):
        return "invalid_covariance"
    if not finite(track["chi2"]) or not finite(track["ndf"]) or track["ndf"] <= 0:
        return "invalid_fit"
    if len(track["parameters"]) != 6 or not all(finite(x) for x in track["parameters"]):
        return "invalid_parameters"
    if len(track["variance"]) != 6 or not all(finite(x) and x > 0 for x in track["variance"]):
        return "invalid_variance"
    # Preserve frozen ordering: keep raw rejected tracks, but verify the native
    # summary for every candidate otherwise accepted by the unique-link cuts.
    if len(indices) != track["nMeasurements"]:
        raise ValueError("Accepted candidate nMeasurements differs from unique inlier links")
    return None


def shared_max(tracks):
    """Native strict shared-hit gate before selection, including repeated links."""
    links = [t["shared_measurements"] for t in tracks]
    usage = Counter(i for values in links for i in set(values))
    return max((sum(usage[i] > 1 for i in values) for values in links), default=0)


def in_bin(value, edges, index):
    return (finite(value) and edges[index] <= value
            and (value < edges[index + 1] or index == len(edges) - 2 and value == edges[-1]))


def count_name(selection, stage, kind, *parts):
    return "/".join((selection, stage, kind, *map(str, parts)))


def classify_event(row, sensors, config):
    """Return exhaustive all-candidate identities and event sufficient counts."""
    generated = {identity(p): p for p in row["generated"]}
    if len(generated) != len(row["generated"]):
        raise ValueError("Duplicate generated particle identity")
    simulated = {identity(p): p for p in row["simulated_particles"]}
    if len(simulated) != len(row["simulated_particles"]):
        raise ValueError("Duplicate simulated particle identity")
    truth = set(generated) | set(simulated)
    ms = {m["index"]: m for m in row["measurements"]}
    if len(ms) != len(row["measurements"]):
        raise ValueError("Duplicate measurement index")
    if row["ckf_input_measurements"] != len(ms):
        raise ValueError("CKF input is not the complete measurement collection")
    associated = defaultdict(set)
    for m in ms.values():
        if m["geometry_id"] not in sensors:
            raise ValueError("Unknown sensitive geometry ID")
        pids = [tuple(p) for p in m["particles"]]
        if len(pids) != len(set(pids)) or not set(pids) <= truth:
            raise ValueError("Measurement truth associations missing or duplicated")
        for pid in pids:
            associated[pid].add(m["index"])
    particles = []
    for pid, p in sorted(generated.items()):
        if type(p.get("hard_scatter")) is not bool:
            raise ValueError("Hard-scatter label must be explicitly verified native boolean")
        linked = associated[pid]
        sensor_ids = {ms[i]["geometry_id"] for i in linked}
        groups = {tuple(sensors[gid][:2]) for gid in sensor_ids if sensors[gid][0] <= 3}
        particles.append({"id": list(pid), "pt": p["pt"], "eta": p["eta"],
                          "hard_scatter": p["hard_scatter"], "fiducial": fiducial(p),
                          "guide9": len(linked) >= 9,
                          "reconstructable": len(sensor_ids) >= 6 and len(groups) >= 3,
                          "measurements": len(linked), "sensors": len(sensor_ids),
                          "pixel_groups": len(groups)})
    eligible = {tuple(p["id"]) for p in particles if p["fiducial"]}
    # Same pure-seed definition as the frozen one-primary analyzer, applied
    # independently to every generated particle without descendant grouping.
    seed_coverage = {}
    for seed_stage in ("seeds", "estimated_seeds"):
        covered = set()
        for seed in row[seed_stage]:
            indices = set(seed["measurements"])
            if not indices <= ms.keys():
                raise ValueError("Seed references an absent measurement")
            if any(sensors[ms[i]["geometry_id"]][0] > 3 for i in indices):
                raise ValueError("Nonpixel seed source link")
            groups = {tuple(sensors[ms[i]["geometry_id"]][:2]) for i in indices}
            if len(groups) >= 3:
                common = set.intersection(*({tuple(p) for p in ms[i]["particles"]} for i in indices))
                covered.update(common & eligible)
        seed_coverage[seed_stage] = covered
    maximum = shared_max(row["ambi"])
    if maximum >= config["ambiguity"]["maximum_shared_hits"]:
        raise ValueError(f"Unconverged ambiguity survivors in event {row['event']}: {maximum}")
    classified = {}
    counts = {}
    for seed_stage, covered in seed_coverage.items():
        counts[count_name("seeding", seed_stage, "raw")] = len(row[seed_stage])
        for scope in SCOPES:
            population = [p for p in particles if p["fiducial"] and (scope == "inclusive" or p["hard_scatter"] == (scope == "hardscatter"))]
            for denominator in DENOMINATORS:
                subset = [p for p in population if denominator == "fiducial" or p[denominator]]
                stem = count_name("seeding", seed_stage, "eff", scope, denominator)
                counts[stem + "/den"] = len(subset)
                counts[stem + "/num"] = sum(tuple(p["id"]) in covered for p in subset)
    match = config["matching"]
    if match["purity"] != .5 or match["completeness"] != .5 or config["quality"]["minimum_measurements"] != 7:
        raise ValueError("Frozen matching or quality protocol changed")
    if config["ambiguity"] != {"maximum_shared_hits": 3, "maximum_iterations": 4294967295}:
        raise ValueError("Frozen converged ambiguity configuration changed")
    for stage in STAGES:
        tracks = row[stage]
        if len({t["index"] for t in tracks}) != len(tracks):
            raise ValueError("Duplicate stable candidate index")
        all_candidates = []
        for t in tracks:
            if not set(t["measurements"]) <= ms.keys() or not set(t["shared_measurements"]) <= ms.keys():
                raise ValueError("Candidate references an absent measurement")
            reason = quality_reason(t, 7)
            pt, eta = reco_coordinates(t)
            indices = set(t["measurements"])
            contributions = Counter(pid for i in indices for pid in {tuple(p) for p in ms[i]["particles"]})
            winner, overlap = (sorted(contributions.items(), key=lambda item: (-item[1], item[0]))[0]
                               if contributions else (None, 0))
            purity = overlap / len(indices) if indices else 0.
            completeness = overlap / len(associated[winner]) if winner is not None else 0.
            matched = winner is not None and purity >= .5 and completeness >= .5
            category = ("eligible_generated" if winner in eligible else "out_of_scope_generated"
                        if winner in generated else "simulated_secondary") if matched else "fake"
            guide = reason is None and pt is not None and pt >= 1. and abs(eta) <= 3. and abs(t["parameters"][0]) <= 4. and t["nHoles"] <= 2 and t["nOutliers"] <= 2
            all_candidates.append({"index": t["index"], "reason": reason, "pt": pt, "eta": eta,
                "winner": list(winner) if matched else None, "overlap": overlap,
                "purity": purity, "completeness": completeness, "category": category,
                "frozen": reason is None, "guide": guide,
                "representative": {}, "duplicate": {},
                "wrong_charge": bool(matched and winner in generated and len(t["parameters"]) == 6
                                     and finite(t["parameters"][4]) and t["parameters"][4] * generated[winner]["charge"] < 0)})
        by_index = {t["index"]: t for t in tracks}
        classified[stage] = all_candidates
        for selection in SELECTIONS:
            accepted = [t for t in all_candidates if t[selection]]
            matches = defaultdict(list)
            for t in accepted:
                if t["winner"] is not None:
                    matches[tuple(t["winner"])].append(t)
            for pid, candidates in matches.items():
                representative = min(candidates, key=lambda t: (-by_index[t["index"]]["nMeasurements"],
                    by_index[t["index"]]["chi2"] / by_index[t["index"]]["ndf"], t["index"]))
                for t in candidates:
                    t["representative"][selection] = t is representative
                    t["duplicate"][selection] = t is not representative
            prefix = (selection, stage)
            counts[count_name(*prefix, "raw")] = len(tracks)
            counts[count_name(*prefix, "accepted")] = len(accepted)
            counts[count_name(*prefix, "quality_rejected")] = sum(t["reason"] is not None for t in all_candidates)
            counts[count_name(*prefix, "raw_inlier_count_mismatch")] = sum(len(set(t["measurements"])) != t["nMeasurements"] for t in tracks)
            counts[count_name(*prefix, "quality_rejected_inlier_count_mismatch")] = sum(t["reason"] is not None and len(set(by_index[t["index"]]["measurements"])) != by_index[t["index"]]["nMeasurements"] for t in all_candidates)
            counts[count_name(*prefix, "selection_rejected")] = sum(t["reason"] is None and not t[selection] for t in all_candidates)
            for category in CATEGORIES:
                counts[count_name(*prefix, category)] = sum(t["category"] == category for t in accepted)
            duplicates = sum(t["duplicate"].get(selection, False) for t in accepted)
            fakes = counts[count_name(*prefix, "fake")]
            counts[count_name(*prefix, "duplicates")] = duplicates
            counts[count_name(*prefix, "fake_event")] = int(fakes > 0)
            counts[count_name(*prefix, "duplicate_event")] = int(duplicates > 0)
            representatives = [t for t in accepted if t["representative"].get(selection, False) and t["winner"] and tuple(t["winner"]) in eligible]
            counts[count_name(*prefix, "wrong_charge")] = sum(t["wrong_charge"] for t in representatives)
            counts[count_name(*prefix, "eligible_representatives")] = len(representatives)
            for scope in SCOPES:
                population = [p for p in particles if p["fiducial"] and (scope == "inclusive" or p["hard_scatter"] == (scope == "hardscatter"))]
                for denominator in DENOMINATORS:
                    subset = [p for p in population if denominator == "fiducial" or p[denominator]]
                    counts[count_name(*prefix, "eff", scope, denominator, "den")] = len(subset)
                    counts[count_name(*prefix, "eff", scope, denominator, "num")] = sum(tuple(p["id"]) in matches for p in subset)
                for axis, edges in (("pt", PT_EDGES), ("eta", ETA_EDGES)):
                    for b in range(len(edges) - 1):
                        subset = [p for p in population if in_bin(p[axis], edges, b)]
                        counts[count_name(*prefix, "effprofile", scope, axis, b, "den")] = len(subset)
                        counts[count_name(*prefix, "effprofile", scope, axis, b, "num")] = sum(tuple(p["id"]) in matches for p in subset)
                    outside = [p for p in population if not any(in_bin(p[axis], edges, b) for b in range(len(edges) - 1))]
                    counts[count_name(*prefix, "effprofile", scope, axis, "outside", "den")] = len(outside)
                    counts[count_name(*prefix, "effprofile", scope, axis, "outside", "num")] = sum(tuple(p["id"]) in matches for p in outside)
            for axis, edges in (("pt", PT_EDGES), ("eta", ETA_EDGES)):
                for b in range(len(edges) - 1):
                    subset = [t for t in accepted if in_bin(t[axis], edges, b)]
                    counts[count_name(*prefix, "candidateprofile", axis, b, "den")] = len(subset)
                    counts[count_name(*prefix, "candidateprofile", axis, b, "fake")] = sum(t["category"] == "fake" for t in subset)
                    counts[count_name(*prefix, "candidateprofile", axis, b, "duplicates")] = sum(t["duplicate"].get(selection, False) for t in subset)
                counts[count_name(*prefix, "candidateprofile", axis, "outside")] = sum(not any(in_bin(t[axis], edges, b) for b in range(len(edges) - 1)) for t in accepted)
            if sum(counts[count_name(*prefix, category)] for category in CATEGORIES) != len(accepted):
                raise AssertionError("Accepted candidate partition is not exhaustive")
    return {"event": row["event"], "counts": counts, "particles": particles,
            "candidates": classified, "ambiguity_shared_max": maximum}


def pack_event(row, path):
    """Lossless matching inputs in numeric, allow_pickle=False, bounded event chunks."""
    generated = {identity(p): p for p in row["generated"]}
    simulated = {identity(p): p for p in row["simulated_particles"]}
    pids = sorted(set(generated) | set(simulated))
    pindex = {pid: i for i, pid in enumerate(pids)}
    particle_values = []
    for pid in pids:
        p = generated.get(pid)
        particle_values.append(([1., float(p["hard_scatter"]), p["charge"], p["pt"], p["eta"], *p["position_mm"]]
                                if p is not None else [0.] * 8))
    measurements = sorted(row["measurements"], key=lambda m: m["index"])
    mindex = {m["index"]: i for i, m in enumerate(measurements)}
    assoc_offsets, associations = [0], []
    for m in measurements:
        associations.extend(pindex[tuple(p)] for p in m["particles"])
        assoc_offsets.append(len(associations))
    tracks, stages, indices = [], [], []
    link_offsets, links, shared_offsets, shared_links = [0], [], [0], []
    for s, stage in enumerate(STAGES):
        for t in row[stage]:
            stages.append(s); indices.append(t["index"])
            values = [float(t["reference"]), float(t["covariance_positive_definite"]), t["nMeasurements"],
                      t["nHoles"], t["nOutliers"], t["chi2"], t["ndf"]]
            values += list(t["parameters"]) if len(t["parameters"]) == 6 else [None] * 6
            values += list(t["variance"]) if len(t["variance"]) == 6 else [None] * 6
            tracks.append([np.nan if x is None else x for x in values])
            links.extend(mindex[i] for i in t["measurements"]); link_offsets.append(len(links))
            shared_links.extend(mindex[i] for i in t["shared_measurements"]); shared_offsets.append(len(shared_links))
    seed_stages, seed_offsets, seed_links = [], [0], []
    for s, stage in enumerate(("seeds", "estimated_seeds")):
        for seed in row[stage]:
            seed_stages.append(s)
            seed_links.extend(mindex[i] for i in seed["measurements"])
            seed_offsets.append(len(seed_links))
    np.savez_compressed(path, event=np.asarray([row["event"]], dtype=np.int64),
        particle_ids=np.asarray(pids, dtype=np.uint32).reshape((-1, 5)),
        particle_values=np.asarray(particle_values, dtype=np.float64).reshape((-1, 8)),
        measurement_indices=np.asarray([m["index"] for m in measurements], dtype=np.uint32),
        measurement_geometry=np.asarray([m["geometry_id"] for m in measurements], dtype=np.uint64),
        association_offsets=np.asarray(assoc_offsets, dtype=np.uint64), association_particles=np.asarray(associations, dtype=np.uint32),
        track_stage=np.asarray(stages, dtype=np.uint8), track_indices=np.asarray(indices, dtype=np.uint32),
        track_values=np.asarray(tracks, dtype=np.float64).reshape((-1, 19)),
        track_link_offsets=np.asarray(link_offsets, dtype=np.uint64), track_links=np.asarray(links, dtype=np.uint32),
        shared_link_offsets=np.asarray(shared_offsets, dtype=np.uint64), shared_links=np.asarray(shared_links, dtype=np.uint32),
        seed_stage=np.asarray(seed_stages, dtype=np.uint8), seed_link_offsets=np.asarray(seed_offsets, dtype=np.uint64), seed_links=np.asarray(seed_links, dtype=np.uint32))


def sufficient_record(result):
    """Keep only event sufficient statistics alive across a case."""
    return {key: result[key] for key in ("event", "counts", "ambiguity_shared_max")}


def unpack_event(path):
    with np.load(path, allow_pickle=False) as archive:
        # NpzFile is lazy and does not cache decompressed arrays. Materialize
        # each array once; repeated per-measurement lookup would be quadratic.
        data = {key: archive[key] for key in archive.files}
        pids = data["particle_ids"].astype(int).tolist()
        generated = []
        for pid, values in zip(pids, data["particle_values"]):
            if values[0]:
                generated.append({"id": pid, "hard_scatter": bool(values[1]), "charge": float(values[2]),
                                  "pt": float(values[3]), "eta": float(values[4]), "position_mm": values[5:8].tolist()})
        measurements = []
        for i, (index, gid) in enumerate(zip(data["measurement_indices"], data["measurement_geometry"])):
            a, b = map(int, data["association_offsets"][i:i+2])
            measurements.append({"index": int(index), "geometry_id": int(gid),
                                 "particles": [pids[int(j)] for j in data["association_particles"][a:b]]})
        row = {"event": int(data["event"][0]), "generated": generated, "simulated_particles": [{"id": pid} for pid in pids],
               "measurements": measurements, "ckf_input_measurements": len(measurements), "ckf": [], "ambi": [], "seeds": [], "estimated_seeds": []}
        for i, stage in enumerate(data["seed_stage"]):
            a, b = map(int, data["seed_link_offsets"][i:i+2])
            row[("seeds", "estimated_seeds")[int(stage)]].append({"measurements": [int(data["measurement_indices"][int(j)]) for j in data["seed_links"][a:b]]})
        for i, values in enumerate(data["track_values"]):
            a, b = map(int, data["track_link_offsets"][i:i+2]); c, d = map(int, data["shared_link_offsets"][i:i+2])
            track = {"index": int(data["track_indices"][i]), "reference": bool(values[0]),
                     "covariance_positive_definite": bool(values[1]), "nMeasurements": int(values[2]),
                     "nHoles": int(values[3]), "nOutliers": int(values[4]), "chi2": float(values[5]), "ndf": float(values[6]),
                     "parameters": values[7:13].tolist(), "variance": values[13:19].tolist(),
                     "measurements": [int(data["measurement_indices"][int(j)]) for j in data["track_links"][a:b]],
                     "shared_measurements": [int(data["measurement_indices"][int(j)]) for j in data["shared_links"][c:d]]}
            row[STAGES[int(data["track_stage"][i])]].append(track)
        return row


def fingerprints(row, sensors):
    controls = {k: digest(row[k]) for k in ("generated", "simulated_particles", "spacepoints", "seeds", "estimated_seeds")}
    # Hit identity must come from the full native source, not an aggregate count.
    source = row["sample_fingerprints"]
    for key in ("generated", "simulated", "hits"):
        value = source[key]
        if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            raise ValueError("Missing complete native source fingerprint: " + key)
        controls["source_" + key] = value
    controls["pixels"] = digest([m for m in row["measurements"] if sensors[m["geometry_id"]][0] <= 3])
    # Compare physical multisets, avoiding downstream source-link renumbering.
    non_target = []
    for m in row["measurements"]:
        system = sensors[m["geometry_id"]][0]
        values = m["values"][:1] if system in (4, 5) else m["values"]
        variance = m["variance"][:1] if system in (4, 5) else m["variance"]
        non_target.append([m["geometry_id"], sorted(m["particles"]), values, variance])
    controls["non_target"] = digest(sorted(non_target, key=canonical))
    return controls


def retain_case(directory, output, expected_events=None):
    directory, output = Path(directory), Path(output)
    analyzer_hash, report_hash = sha256(__file__), sha256(directory / "run-report.json")
    report = read_json(directory / "run-report.json")
    if report["outcome"] != "completed":
        raise ValueError("Native case did not complete")
    config = report["campaign"]
    if expected_events is not None and report["events"] != expected_events:
        raise ValueError("Unexpected generated-event count")
    for name, value in report["output_sha256"].items():
        item = (directory / name).resolve()
        if not item.is_relative_to(directory.resolve()) or sha256(item) != value:
            raise ValueError("Native output changed: " + name)
    native = read_json(directory / "native-report.json")
    native_sensors = {s["geometry_id"]: s for s in native["sensors"]}
    sensors = {gid: (s["ids"]["system"], s["ids"]["layer"]) for gid, s in native_sensors.items()}
    widths = read_json(directory / "error-table.json")
    baseline_widths = read_json(directory / "baseline-error-table.json")
    pitch = report["pitch_mm"]
    if pitch not in PITCHES:
        raise ValueError("Unsupported strixel response configuration")
    expected_widths = copy.deepcopy(baseline_widths)
    volumes = {}
    for gid, sensor in sensors.items():
        volume = (gid >> 56) & 255
        if volume in volumes and volumes[volume] != sensor[0]:
            raise ValueError("A native volume spans physical detector systems")
        volumes[volume] = sensor[0]
    scaled = 0
    for group in expected_widths["groups"]:
        if volumes[group["volume"]] in (4, 5) and group["index"] == 1:
            group["sigma_mm"] *= pitch / .5; scaled += 1
    if not scaled or expected_widths != widths:
        raise ValueError("Response is not exclusively the prescribed strixel local-v scaling")
    variance = {(g["volume"], g["index"]): g["sigma_mm"]**2 for g in widths["groups"]}
    if output.exists() and any(output.iterdir()):
        raise ValueError("Choose a fresh retained directory; partial evidence is preserved")
    output.mkdir(parents=True, exist_ok=True); (output / "audit").mkdir(exist_ok=True)
    records, audits, controls, marginal_count, systems = [], {}, [], 0, Counter()
    spacepoint_count, maximum_spacepoint_error, hypotheses, hypothesis_masses = 0, 0., 0, set()
    with gzip.open(directory / "events.jsonl.gz", "rt") as stream:
        for line in stream:
            row = json.loads(line)
            for m in row["measurements"]:
                system = sensors[m["geometry_id"]][0]; systems[system] += 1
                if m["dimension"] != (1 if system >= 6 else 2) or len(m["values"]) != m["dimension"] or len(m["variance"]) != m["dimension"]:
                    raise ValueError("Measurement dimension changed")
                for index, value in enumerate(m["variance"]):
                    if value != variance[((m["geometry_id"] >> 56) & 255, index)]:
                        raise ValueError("Native variance differs from explicit response")
                    marginal_count += 1
            ms = {m["index"]: m for m in row["measurements"]}
            for point in row["spacepoints"]:
                if len(point["measurements"]) != 1:
                    raise ValueError("Pixel space point must have one source measurement")
                m = ms[point["measurements"][0]]; sensor = native_sensors[m["geometry_id"]]
                if sensor["ids"]["system"] > 3:
                    raise ValueError("Nonpixel measurement entered GBTS")
                expected = np.asarray(sensor["center_mm"]) + m["values"][0]*np.asarray(sensor["u"]) + m["values"][1]*np.asarray(sensor["v"])
                maximum_spacepoint_error = max(maximum_spacepoint_error, float(np.linalg.norm(expected - point["position"])))
                if not np.array_equal(expected.astype(np.float32).astype(float), point["position"]):
                    raise ValueError("Space point differs from measured float32 local-to-global position")
                spacepoint_count += 1
            if len(row["estimated_hypotheses"]) != len(row["estimated_seeds"]):
                raise ValueError("Estimated seed/hypothesis coverage differs")
            for hypothesis in [*row["estimated_hypotheses"], *(t["hypothesis"] for stage in STAGES for t in row[stage])]:
                if hypothesis["absolute_pdg"] != 13 or not finite(hypothesis["mass_GeV"]) or hypothesis["mass_GeV"] <= 0:
                    raise ValueError("Inclusive muon reconstruction hypothesis changed")
                hypotheses += 1; hypothesis_masses.add(hypothesis["mass_GeV"])
            result = classify_event(row, sensors, config)
            records.append(sufficient_record(result)); controls.append({"event": row["event"], **fingerprints(row, sensors)})
            name = f"audit/event-{row['event']:06d}.npz"
            pack_event(row, output / name); audits[name] = sha256(output / name)
    records.sort(key=lambda r: r["event"]); controls.sort(key=lambda r: r["event"])
    event_ids = [r["event"] for r in records]
    if len(records) != report["events"] or len(set(event_ids)) != len(records) or event_ids != list(range(report["events"])):
        raise ValueError("Lost, duplicated or noncontiguous generated events")
    names = sorted(records[0]["counts"]) if records else []
    if any(sorted(r["counts"]) != names for r in records):
        raise ValueError("Inconsistent sufficient-count schema")
    np.savez_compressed(output / "events.npz", event=np.asarray(event_ids, dtype=np.int64),
                        counts=np.asarray([[r["counts"][k] for k in names] for r in records], dtype=np.int64),
                        metric_names=np.asarray(names), ambiguity_shared_max=np.asarray([r["ambiguity_shared_max"] for r in records], dtype=np.int64))
    result = {"schema_version": 1, "status": "PROTOTYPE", "events": len(records),
              "analyzer_sha256": analyzer_hash, "native_report": sanitize(report),
              "original_native_identity_sha256": native_identity(report),
              "native_report_sha256": report_hash,
              "invariant_input_sha256": {name: sha256(directory / name) for name in
                  ("native-report.json", "material-map.json", "pixel-selection.json", "baseline-error-table.json")},
              "sensors": {str(k): list(v) for k, v in sensors.items()}, "fingerprints": controls,
              "audit_chunks_sha256": audits, "events_npz_sha256": sha256(output / "events.npz"),
              "measurement_audit": {"systems": {str(k): v for k, v in systems.items()}, "variance_marginals": marginal_count,
                  "full_ckf_input": True, "explicit_variance_identity": True,
                  "exclusive_prescribed_sigma_scaling": True,
                  "measured_pixel_spacepoints_checked": spacepoint_count,
                  "maximum_spacepoint_error_mm": maximum_spacepoint_error,
                  "inclusive_muon_hypotheses_checked": hypotheses,
                  "native_muon_hypothesis_masses_GeV": sorted(hypothesis_masses),
                  "all_native_ambiguity_survivors_converged": True},
              "matching": "unique inlier purity>=0.5 and completeness>=0.5; overlap then barcode ties; representative most inliers, chi2/ndf, index",
              "retention": "Numeric per-event matching inputs; no pickle. Source raw outputs remain separate."}
    if sha256(__file__) != analyzer_hash or sha256(directory / "run-report.json") != report_hash:
        raise ValueError("Analyzer or native report changed during retention")
    write_json(output / "summary.json.gz", result)
    return result


def replay_case(directory):
    directory = Path(directory); summary = read_json(directory / "summary.json.gz")
    if sha256(directory / "events.npz") != summary["events_npz_sha256"]:
        raise ValueError("Portable event counts changed")
    sensors = {int(k): tuple(v) for k, v in summary["sensors"].items()}
    with np.load(directory / "events.npz", allow_pickle=False) as data:
        names = data["metric_names"].tolist(); expected = data["counts"].copy(); event_ids = data["event"].tolist()
    records = []
    for name, value in sorted(summary["audit_chunks_sha256"].items()):
        if sha256(directory / name) != value:
            raise ValueError("Portable matching chunk changed")
        records.append(sufficient_record(classify_event(unpack_event(directory / name), sensors, summary["native_report"]["campaign"])))
    records.sort(key=lambda r: r["event"])
    if [r["event"] for r in records] != event_ids:
        raise ValueError("Incomplete portable matching coverage")
    observed = np.asarray([[r["counts"][k] for k in names] for r in records], dtype=np.int64)
    if not np.array_equal(observed, expected):
        raise ValueError("Independent portable matching replay differs")
    return summary


def wilson(k, n, z=1.959963984540054):
    if not n:
        return None
    p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return [max(0., c-h), min(1., c+h)]


def bootstrap_weights(events, replicates=2000):
    if events <= 0 or type(replicates) is not int or replicates <= 0:
        raise ValueError("Positive event and replicate counts required")
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    indices = rng.integers(0, events, size=(replicates, events))
    weights = np.zeros((replicates, events), dtype=np.int64)
    for i, sample in enumerate(indices):
        weights[i] = np.bincount(sample, minlength=events)
    return weights


def ratio_estimate(numerators, denominators, weights, reference=None, reference_self=False):
    n, d = np.asarray(numerators, dtype=np.int64), np.asarray(denominators, dtype=np.int64)
    if n.shape != d.shape or len(n) != weights.shape[1] or np.any(n < 0) or np.any(d < n):
        raise ValueError("Invalid event ratio counts")
    total_n, total_d = int(n.sum()), int(d.sum())
    dn = weights @ d; nn = weights @ n
    samples = np.divide(nn, dn, out=np.full(len(weights), np.nan), where=dn > 0)
    valid = np.isfinite(samples)
    result = {"numerator": total_n, "denominator": total_d, "value": total_n/total_d if total_d else None,
              "event_bootstrap95": np.quantile(samples[valid], [.025, .975]).tolist() if valid.any() else None,
              "defined_resamples": int(valid.sum()), "resamples": len(weights),
              "bootstrap_degenerate": bool(valid.any() and np.all(samples[valid] == samples[valid][0]))}
    if reference is not None:
        rn, rd = map(lambda x: np.asarray(x, dtype=np.int64), reference)
        rden = weights @ rd; rnum = weights @ rn
        rs = np.divide(rnum, rden, out=np.full(len(weights), np.nan), where=rden > 0)
        common = valid & np.isfinite(rs); delta = samples[common] - rs[common]
        result["paired_delta"] = {"value": result["value"] - rn.sum()/rd.sum() if total_d and rd.sum() else None,
            "event_bootstrap95": np.quantile(delta, [.025, .975]).tolist() if len(delta) else None,
            "defined_resamples": int(common.sum()),
            "bootstrap_degenerate": bool(len(delta) and np.all(delta == delta[0])),
            "identical_event_counts": bool(np.array_equal(n, rn) and np.array_equal(d, rd)),
            "reference_self": reference_self}
    return result


def ratio_specs(names):
    specs = {}
    for seed_stage in ("seeds", "estimated_seeds"):
        for scope in SCOPES:
            for denominator in DENOMINATORS:
                stem = count_name("seeding", seed_stage, "eff", scope, denominator)
                specs[stem] = (stem + "/num", stem + "/den", False)
    for selection in SELECTIONS:
        for stage in STAGES:
            prefix = (selection, stage)
            for scope in SCOPES:
                for denominator in DENOMINATORS:
                    stem = count_name(*prefix, "eff", scope, denominator)
                    specs[stem] = (stem + "/num", stem + "/den", False)
                for axis, edges in (("pt", PT_EDGES), ("eta", ETA_EDGES)):
                    for b in range(len(edges)-1):
                        stem = count_name(*prefix, "effprofile", scope, axis, b)
                        specs[stem] = (stem + "/num", stem + "/den", False)
            for category in (*CATEGORIES, "duplicates"):
                specs[count_name(*prefix, "fraction", category)] = (count_name(*prefix, category), count_name(*prefix, "accepted"), False)
            for event_rate in ("fake_event", "duplicate_event"):
                specs[count_name(*prefix, event_rate)] = (count_name(*prefix, event_rate), None, True)
            specs[count_name(*prefix, "wrong_charge_fraction")] = (count_name(*prefix, "wrong_charge"), count_name(*prefix, "eligible_representatives"), False)
            for axis, edges in (("pt", PT_EDGES), ("eta", ETA_EDGES)):
                for b in range(len(edges)-1):
                    stem = count_name(*prefix, "candidateprofile", axis, b)
                    for category in ("fake", "duplicates"):
                        specs[stem + "/" + category] = (stem + "/" + category, stem + "/den", False)
    return specs


def summarize_cases(cases, replicates=2000):
    """Joint event resamples across all lengths; ratios of event-count sums."""
    if sorted(cases) != list(PITCHES):
        raise ValueError("Require all four strixel configurations")
    baseline = cases[.5]
    ids, names = baseline["event"], baseline["metric_names"].tolist()
    if len(ids) == 0 or len(set(ids.tolist())) != len(ids):
        raise ValueError("Empty or duplicate generated event IDs")
    for pitch, data in cases.items():
        if not np.array_equal(data["event"], ids) or data["metric_names"].tolist() != names or data["counts"].shape != baseline["counts"].shape:
            raise ValueError("Incomplete event pairing or sufficient-count schema")
    weights = bootstrap_weights(len(ids), replicates)
    columns = {name: i for i, name in enumerate(names)}
    specs = ratio_specs(names)
    def vectors(data, numerator, denominator):
        return (data["counts"][:, columns[numerator]], data["counts"][:, columns[denominator]] if denominator else np.ones(len(ids), dtype=np.int64))
    results = {}
    for pitch, data in cases.items():
        metrics = {}
        for key, (numerator, denominator, event_rate) in specs.items():
            n, d = vectors(data, numerator, denominator)
            result = ratio_estimate(n, d, weights, vectors(baseline, numerator, denominator), reference_self=pitch == .5)
            if event_rate:
                result["wilson95"] = wilson(int(n.sum()), len(ids))
                result["zero_event_one_sided95_upper"] = 1 - .05**(1/len(ids)) if not n.sum() else None
                result["bound_scope"] = "event incidence, not candidate fraction"
            metrics[key] = result
        results[f"{pitch:g}"] = {"events": len(ids), "counts": {name: int(data["counts"][:, i].sum()) for i, name in enumerate(names)}, "metrics": metrics}
    return {"schema_version": 1, "status": "PROTOTYPE", "events_per_pitch": len(ids),
            "pitches_mm": list(PITCHES), "stages": list(STAGES), "selections": list(SELECTIONS),
            "pt_edges_GeV": list(PT_EDGES), "eta_edges": list(ETA_EDGES),
            "bootstrap": {"unit": "generated event block", "replicates": replicates, "seed": BOOTSTRAP_SEED,
                          "paired_across_pitches": True, "ratio_of_sums": True,
                          "interval": "pointwise percentile 95%; no simultaneous or equivalence claim",
                          "degeneracy": "Constant bootstrap distribution flagged; no candidate-fraction upper bound inferred"},
            "cases": results}


def check_pairing(summaries):
    baseline = summaries[.5]
    fields = ("source_generated", "source_simulated", "source_hits", "generated", "simulated_particles")
    control_fields = ("pixels", "spacepoints", "seeds", "estimated_seeds", "non_target")
    results = {}
    for pitch, summary in summaries.items():
        if summary["invariant_input_sha256"] != baseline["invariant_input_sha256"]:
            raise ValueError("Geometry/material/baseline response identity differs")
        report, base_report = summary["native_report"], baseline["native_report"]
        if summary["original_native_identity_sha256"] != baseline["original_native_identity_sha256"]:
            raise ValueError("Original native source/runtime/shared-sample/configuration identity differs")
        if report["pitch_mm"] != pitch or invariant_configuration(report["campaign"]) != invariant_configuration(base_report["campaign"]):
            raise ValueError("Reconstruction configuration differs beyond prescribed pitch")
        reference, current = baseline["fingerprints"], summary["fingerprints"]
        if [r["event"] for r in reference] != [r["event"] for r in current]:
            raise ValueError("Missing event fingerprints")
        for field in fields:
            if any(a[field] != b[field] for a, b in zip(reference, current)):
                raise ValueError("Generated/transported source pairing failed: " + field)
        results[f"{pitch:g}"] = {"full_source_identity": True,
            "control_changed_events": {field: sum(a[field] != b[field] for a, b in zip(reference, current)) for field in control_fields}}
    return {"source_fields": list(fields), "invariant_configuration_and_source_verified": True,
            "geometry_material_baseline_response_verified": True, "cases": results,
            "qualification": "Pixel/seed/non-target differences are measured controls; equal RNG seeds alone do not prove common noise. Boundary retries can couple non-target draws."}


def markdown(report):
    lines = ["# DES042 PROTOTYPE - ttbar plus exactly 200 pileup interactions", "",
        f"Fatras qqbar-only ttbar; {report['events_per_pitch']} paired generated events per length; fixed geometry/material, constant 3 T and common GBTS/CKF/ambiguity settings.", "",
        "Efficiencies count unique charged generated particles with pT >=1 GeV, |eta| <=3, rho <=24 mm and |z| <=1 m, before hit requirements. Candidate fakes exclude matched out-of-scope generated particles and simulated secondaries. Duplicates overlap matched categories.", "",
        "Guide selection is applied after frozen ambiguity resolution: reconstructed pT >=1 GeV, |eta| <=3, |loc0| <=4 mm, <=2 holes and <=2 outliers, in addition to frozen quality. It does not reproduce a different native reconstruction chain.", "",
        "| Pitch [mm] | Selection | Stage | Inclusive efficiency | Hard scatter | Pileup | Fake candidates | Duplicate candidates | Fake events |", "|---:|---|---|---:|---:|---:|---:|---:|---:|"]
    def fmt(metric):
        value, interval = metric["value"], metric["event_bootstrap95"]
        if value is None:
            return "undefined (0 denominator)"
        bound = metric.get("zero_event_one_sided95_upper")
        suffix = f"; exact event upper {100*bound:.3f}%" if bound is not None else ""
        ci = f" [{100*interval[0]:.2f}, {100*interval[1]:.2f}]" if interval is not None else ""
        degenerate = " (degenerate bootstrap)" if metric["bootstrap_degenerate"] else ""
        return f"{100*value:.2f}%{ci} ({metric['numerator']}/{metric['denominator']}){degenerate}{suffix}"
    for pitch in PITCHES:
        case = report["cases"][f"{pitch:g}"]
        for selection in SELECTIONS:
            for stage in STAGES:
                keys = [count_name(selection, stage, "eff", scope, "fiducial") for scope in SCOPES]
                keys += [count_name(selection, stage, "fraction", category) for category in ("fake", "duplicates")]
                keys += [count_name(selection, stage, "fake_event")]
                lines.append(f"| {pitch:g} | {selection} | {stage} | " + " | ".join(fmt(case["metrics"][k]) for k in keys) + " |")
    lines += ["", "Pure measured-pixel seed coverage counts unique eligible generated particles with at least one seed whose links all associate with that particle and span at least three physical pixel groups. This control diagnoses an upstream stage; it does not prove the cause of downstream failures.", "",
              "| Pitch [mm] | Seed stage | Inclusive coverage | Hard scatter | Pileup |", "|---:|---|---:|---:|---:|"]
    for pitch in PITCHES:
        case = report["cases"][f"{pitch:g}"]
        for stage in ("seeds", "estimated_seeds"):
            keys = [count_name("seeding", stage, "eff", scope, "fiducial") for scope in SCOPES]
            lines.append(f"| {pitch:g} | {stage} | " + " | ".join(fmt(case["metrics"][k]) for k in keys) + " |")
    lines += ["", "Intervals resample whole generated events jointly across all four pitches (2,000 deterministic event-block resamples in the production protocol). They are pointwise statistical intervals. Particles/tracks in one event are correlated. Zero fake-event bounds describe event incidence and do not bound candidate fake fractions. Degenerate paired bootstrap differences do not demonstrate equivalence.", "",
        "The response scales only system 4/5 local-v Gaussian sigma relative to 0.5 mm. This is an uncalibrated coarse-response sensitivity with fixed material; Gaussian boundary retries can alter other realized smearing draws. Truth-binned efficiency and reco-binned fake/duplicate profiles, conditional denominators, exhaustive counts and paired differences are retained in profiles.json.gz.", ""]
    if "pairing" in report:
        lines += ["Source particle/hit identity passed for all four configurations. Changed control-event counts:", "", "| Pitch [mm] | Pixel inputs | Space points | Seeds | Estimated seeds | Non-target response |", "|---:|---:|---:|---:|---:|---:|"]
        for pitch in PITCHES:
            changed = report["pairing"]["cases"][f"{pitch:g}"]["control_changed_events"]
            lines.append(f"| {pitch:g} | " + " | ".join(str(changed[k]) for k in ("pixels", "spacepoints", "seeds", "estimated_seeds", "non_target")) + " |")
    graphs = report.get("benchmark", {}).get("gbts_graph_audit", {})
    if graphs:
        lines += ["", "The unchanged GBTS graph limit can truncate the graph. These are resource-limited chain results, not unconstrained detector/seeder performance.", "",
                  "| Pitch [mm] | Edge limit | Events reaching limit | Edges/event range | Edge links/event range |",
                  "|---:|---:|---:|---:|---:|"]
        for pitch in PITCHES:
            graph = graphs[f"{pitch:g}"]
            lines.append(f"| {pitch:g} | {graph['edge_cap']} | {graph['cap_reached_events']}/{graph['events']} | {graph['edges_min']}–{graph['edges_max']} | {graph['edge_links_min']}–{graph['edge_links_max']} |")
    return "\n".join(lines) + "\n"


def campaign(data, output, replicates=2000, verify=False):
    data, output = Path(data), Path(output)
    summaries, cases = {}, {}
    for pitch in PITCHES:
        directory = data / f"pitch{pitch:g}"
        summary = replay_case(directory)
        if summary["analyzer_sha256"] != sha256(__file__):
            raise ValueError("Analyzer changed after retention; create fresh evidence")
        summaries[pitch] = summary
        with np.load(directory / "events.npz", allow_pickle=False) as arrays:
            cases[pitch] = {k: arrays[k].copy() for k in ("event", "counts", "metric_names")}
    report = summarize_cases(cases, replicates)
    report["pairing"] = check_pairing(summaries)
    native = summaries[.5]["native_report"]
    physics = native["campaign"]["ttbar_pileup"]
    report["benchmark"] = {
        "hard_process": physics["hard_process"], "pileup": physics["pileup"],
        "cms_energy_GeV": physics["cms_energy_GeV"],
        "vertex_sigma_mm": physics["vertex_sigma_mm"],
        "gbts_z0_range_mm": native["gbts_statistics"]["effective_configuration"]["z0_range_mm"],
        "fit_hypothesis": physics["reconstruction_hypothesis"]}
    graphs = {}
    for pitch, summary in summaries.items():
        graph = summary["native_report"]["gbts_statistics"].get("graph_audit")
        if graph is None:
            continue
        rows = graph["events"]
        if ([row["event"] for row in rows] != list(range(summary["events"])) or
                sum(row["cap_reached"] for row in rows) != graph["cap_reached_events"]):
            raise ValueError("Incomplete GBTS graph audit")
        graphs[f"{pitch:g}"] = {"edge_cap": graph["edge_cap"], "events": len(rows),
            "cap_reached_events": graph["cap_reached_events"],
            "edges_min": min(row["edges"] for row in rows),
            "edges_max": max(row["edges"] for row in rows),
            "edge_links_min": min(row["edge_links"] for row in rows),
            "edge_links_max": max(row["edge_links"] for row in rows),
            "log_sha256": graph["log_sha256"]}
    if graphs:
        if len(graphs) != len(PITCHES):
            raise ValueError("Missing GBTS graph diagnostics for a pitch")
        report["benchmark"]["gbts_graph_audit"] = graphs
    report["provenance"] = {"analyzer_sha256": sha256(__file__), "case_summaries_sha256": {
        f"{pitch:g}": sha256(data / f"pitch{pitch:g}" / "summary.json.gz") for pitch in PITCHES}}
    prose = markdown(report)
    if verify:
        if read_json(output / "profiles.json.gz") != report or (output / "results.md").read_text() != prose:
            raise ValueError("Exact statistics/bootstrap/Markdown replay differs")
    else:
        output.mkdir(parents=True, exist_ok=True)
        write_json(output / "profiles.json.gz", report)
        (output / "results.md").write_text(prose)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    retain = sub.add_parser("retain"); retain.add_argument("source", type=Path); retain.add_argument("--output", type=Path, required=True); retain.add_argument("--events", type=int)
    replay = sub.add_parser("replay"); replay.add_argument("directory", type=Path)
    stats = sub.add_parser("statistics"); stats.add_argument("--data", type=Path, required=True); stats.add_argument("--output", type=Path, required=True); stats.add_argument("--replicates", type=int, default=2000); stats.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.command == "retain":
        result = retain_case(args.source, args.output, args.events)
    elif args.command == "replay":
        result = replay_case(args.directory)
    else:
        result = campaign(args.data, args.output, args.replicates, args.verify)
    print(json.dumps({"outcome": "passed", "command": args.command, "events": result.get("events", result.get("events_per_pitch"))}))


if __name__ == "__main__":
    main()
