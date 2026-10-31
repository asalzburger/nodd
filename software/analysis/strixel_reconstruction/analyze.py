#!/usr/bin/env python3
"""Retain and replay the DES042 frozen-GBTS longitudinal-response prototype.

The maintained DES041 analyzer is invoked unchanged before retention. Native
JSONL/ROOT files can then stay in ignored storage: their hashes and per-event
fingerprints accompany all generated-event metric arrays in portable evidence.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
NATIVE = ROOT / "software/analysis/tracker_reconstruction"
INPUT_REVISION = "4ea4af17727020bac2ba8f5e2f6172378711c15a"
NATIVE_ANALYZER_SHA256 = "972a4ebea1c402a2d5d22d07c90508b6f1a722628d3886a70e9d896a8c2339ab"
FROZEN_REFERENCES = {
    "docs/validation/tracker-reconstruction/native-validation-reports.json.gz": "a025fca6b3582560fac2fa1d8e68ae391836e7bf49594eada1e859e374e7cf33",
    "docs/validation/tracker-reconstruction-species/fatras/electron/pt1/summary.json.gz": "a0118f6f411679813867cb8f2b0cb6a7abf61380830db46114b67fb703eddd5f",
    "docs/validation/tracker-reconstruction-species/geant4/muon/pt1/summary.json.gz": "d08938705721dd9ead8776ed1060c29277fa607605d9780031ef08cc94b3e2a1",
    "docs/validation/tracker-reconstruction-species/geant4/pion/pt1/summary.json.gz": "0480a12469bdd9f5853f44343e29bac9e78c22009cf1ea276eee0ceaa8a5c325"}
PITCHES = (.5, 1., 1.5, 2.)
PTS = (1., 5., 10., 100.)
POPULATIONS = (("fatras", "muon"), ("fatras", "electron"),
               ("geant4", "muon"), ("geant4", "electron"), ("geant4", "pion"))
PROBABILITY = .6826894921370859
QUANTILES = ((1 - PROBABILITY) / 2, (1 + PROBABILITY) / 2)
BOOTSTRAP_SEED = 842042
MINIMUM_WIDTH_ENTRIES = 30
PARAMETERS = ("d0", "z0", "phi", "theta", "q_over_p", "time_ns", "relative_pt")
UNITS = ("mm", "mm", "rad", "rad", "GeV^-1", "ns", "1")
TAILS = ((.1, 1.), (.1, 1.), (.001, .01), (.001, .01), (.01, .1), (1., 10.), (.1, .5, 1.))
FINGERPRINTS = ("generated", "simulated_particles", "simulated_ids", "simhit_count",
                "simhits_payload", "pixel_measurements", "spacepoints", "seeds",
                "estimated_seeds", "primary_measurement_associations", "ckf_inputs",
                "pixel_physical", "strixel_fine_u", "long_strip_physical")
PHYSICAL_INPUTS = ("pixel_physical", "strixel_fine_u", "long_strip_physical")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def fingerprint(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def dump_gzip(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(canonical(value) + b"\n", mtime=0))


def read_gzip(path):
    return json.loads(gzip.decompress(Path(path).read_bytes()))


def sanitize(value):
    """Replace machine-local paths with logical roles; original bytes are hashed."""
    if isinstance(value, dict):
        clean = {}
        for key, item in value.items():
            label = sanitize(key)
            if label in clean:
                raise ValueError("Sanitized metadata key collision")
            clean[label] = sanitize(item)
        return clean
    if isinstance(value, list):
        return [sanitize(x) for x in value]
    if isinstance(value, str):
        if value.startswith("/"):
            path = Path(value)
            for base, role in ((ROOT, "repository"), (ROOT.parent, "workspace")):
                try:
                    return role + "/" + str(path.relative_to(base))
                except ValueError:
                    pass
            return "external/" + hashlib.sha256(value.encode()).hexdigest()[:12] + "/" + path.name
        # Command arguments can contain --option=/absolute/path.
        if "=/" in value:
            prefix, path = value.split("=", 1)
            return prefix + "=" + sanitize(path)
    return value


def native_analyzer():
    path = NATIVE / "analyze.py"
    if digest(path) != NATIVE_ANALYZER_SHA256:
        raise ValueError("Frozen DES041 analyzer changed; independent review required")
    if str(NATIVE) not in sys.path:
        sys.path.insert(0, str(NATIVE))
    spec = importlib.util.spec_from_file_location("des041_frozen_analyzer", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frozen_contract():
    """Retain a portable contract extracted from exact input-revision evidence."""
    for name, expected in FROZEN_REFERENCES.items():
        if digest(ROOT / name) != expected:
            raise ValueError("Frozen engine reference changed: " + name)
    selected = read_gzip(ROOT / next(iter(FROZEN_REFERENCES)))["selected/pt1"]
    keys = ("baseline_revision", "geometry", "particles_per_event", "randomize_charge", "vertex_mm",
            "field_Bz_T", "pt_GeV", "eta_range", "phi_range_rad", "digitization", "material",
            "parameter_estimation", "ckf", "quality", "matching", "profiles", "reconstruction", "truth_use")
    campaign = {key: selected["campaign"][key] for key in keys}
    campaign["ambiguity"] = {"maximum_iterations": 4294967295, "maximum_shared_hits": 3}
    species = {read_gzip(ROOT / name)["particle_configuration"]["name"]:
               read_gzip(ROOT / name)["particle_configuration"] for name in list(FROZEN_REFERENCES)[1:]}
    return {"reference_sha256": FROZEN_REFERENCES, "source_revision": INPUT_REVISION,
            "campaign_fields": campaign, "effective_gbts_configuration": selected["gbts_statistics"]["effective_configuration"],
            "species": species, "eta_edges": selected["campaign"]["tuning_protocol"]["eta_edges"]}


def validate_engine(report, contract):
    config, stats = report["campaign"], report["gbts_statistics"]
    for key, expected in contract["campaign_fields"].items():
        if config.get(key) != expected:
            raise ValueError("Frozen engine configuration differs: " + key)
    if config["tuning_protocol"]["eta_edges"] != contract["eta_edges"]:
        raise ValueError("Frozen signed-eta bins changed")
    if stats["effective_configuration"] != contract["effective_gbts_configuration"]:
        raise ValueError("Effective native GBTS configuration differs from frozen selected validation")
    if stats["particle_configuration"] != contract["species"][config["particle"]]:
        raise ValueError("Native species/hypothesis differs from frozen reference")
    if stats["effective_two_way"] != (config["particle"] != "electron"):
        raise ValueError("Native two-way species setting differs")
    if stats["events"] != report["events"] or stats["mapped_spacepoints"] != stats["input_spacepoints"]:
        raise ValueError("Native GBTS event/pixel mapping count differs")
    if config["simulation"] == "geant4":
        mapping = stats["geant4_mapping_audit"]
        if (stats["transport_configuration"]["native_geant4_events"] != report["events"] or
                mapping["expected"] != 46250 or mapping["mapped"] != 46250 or
                mapping["all_sensitive_surfaces_mapped"] is not True or mapping["duplicate_geometry_ids"]):
            raise ValueError("Native Geant4 full active-sensor mapping/event gate failed")


def case_identity(report):
    config = report["campaign"]
    return (config["simulation"], config["particle"], float(report["pt_GeV"]), float(report["pitch_mm"]))


def case_name(identity):
    simulation, particle, pt, pitch = identity
    return f"{simulation}-{particle}-pt{pt:g}-pitch{pitch:g}"


def validate_matrix(reports, pilot=False):
    identities = [case_identity(r) for r in reports]
    if len(identities) != len(set(identities)):
        raise ValueError("Repeated population/momentum/pitch identity")
    if not identities:
        raise ValueError("No native cases")
    if any((s, p) not in POPULATIONS or pt not in PTS or pitch not in PITCHES
           for s, p, pt, pitch in identities):
        raise ValueError("Case outside frozen study matrix")
    if pilot:
        groups = {(s, p, pt) for s, p, pt, pitch in identities}
        if len(groups) != 1 or {i[3] for i in identities} != set(PITCHES):
            raise ValueError("Pilot requires exactly four pitches at one population and momentum")
        if len({r["events"] for r in reports}) != 1:
            raise ValueError("Pilot denominators differ")
    else:
        expected = {(s, p, pt, pitch) for s, p in POPULATIONS for pt in PTS for pitch in PITCHES}
        if set(identities) != expected or any(r["events"] != 1000 for r in reports):
            raise ValueError("Production requires exact 80-case matrix with 1000 generated events/case")


def simhit_fingerprints(path, event_ids):
    """Hash every persisted ROOT hit branch, including empty generated events.

    The native writer's precision is the precision tested here. The original
    ROOT hash and branch schema remain in the inventory; no claim about
    unpersisted native double bits follows from equality of these records.
    """
    import uproot
    import awkward as ak
    with uproot.open(path) as source:
        trees = [obj for _, obj in source.items() if hasattr(obj, "arrays")]
        if len(trees) != 1:
            raise ValueError("Require one native simhit ROOT tree")
        tree = trees[0]
        branches = tree.arrays(library="ak")
        names = sorted(branches.fields)
        event_key = next((key for key in ("event_nr", "event_id", "event") if key in names), None)
        if event_key is None:
            raise ValueError("Simhit ROOT has no event identity branch")
        records = {int(event): [] for event in event_ids}
        for row in ak.to_list(branches):
            event = int(row.pop(event_key))
            if event not in records:
                raise ValueError("Simhit ROOT contains unknown generated event")
            records[event].append(row)
        # ACTS writers can use a row per hit or a vector of hits per event.
        # Preserve native order/structure, every branch and numerical value.
        result = {event: fingerprint(records[event]) for event in records}
        schema = {}
        for name in names:
            column = np.asarray(ak.flatten(branches[name], axis=None))
            finite = column[np.isfinite(column)]
            maxabs = float(np.max(np.abs(finite.astype(float)))) if finite.size else None
            schema[name] = {"dtype": str(column.dtype), "interpretation": str(tree[name].interpretation),
                            "maximum_absolute_value": maxabs,
                            "maximum_float32_ulp": float(np.spacing(np.float32(maxabs)))
                            if column.dtype.kind == "f" and column.dtype.itemsize == 4 and maxabs is not None else None}
    return result, {"file_sha256": digest(path), "branches": schema,
                    "hits_by_event": {str(event): len(records[event]) for event in records},
                    "tt_unit": "ct_mm (header time_ns label is incorrect; writer divides native ct by mm)",
                    "comparison_precision": "Exact persisted float32 hit position/ct/momentum/delta and integer identity/index branches; all secondary hits; row order. Does not establish native float64 simhit identity."}


def covariance_invalid(track):
    variance = track.get("variance", [])
    return (not track.get("covariance_positive_definite", True) or len(variance) != 6 or
            any(v is None or not math.isfinite(v) or v <= 0 for v in variance))


def physical_measurements(measurements, sensors, systems, fine_only=False):
    """Index-free multisets preserve repeated hits and physical associations."""
    payload, groups = [], {}
    for measurement in measurements:
        if sensors[measurement["geometry_id"]][0] not in systems:
            continue
        item = {key: measurement[key] for key in ("geometry_id", "particles", "dimension", "values", "variance")}
        if fine_only:
            item = {**item, "dimension": 1, "values": item["values"][:1], "variance": item["variance"][:1]}
        payload.append(item)
        key = fingerprint({key: item[key] for key in ("geometry_id", "particles")})
        groups[key] = groups.get(key, 0) + 1
    payload.sort(key=canonical)
    return payload, (len(payload), sum(count > 1 for count in groups.values()), sum(max(0, count - 1) for count in groups.values()))


def augment_arrays(directory, arrays, native_report, module, hit_hashes, hit_counts):
    """Add diagnostics after the unchanged native audit/classifier passed."""
    sensors = {s["geometry_id"]: (s["ids"]["system"], s["ids"]["layer"])
               for s in native_report["sensors"]}
    extra = {name: [] for name in FINGERPRINTS}
    values = {key: [] for key in ("simhits", "measurements", "primary_sensors", "spacepoints")}
    values.update({name + "_" + suffix: [] for name in PHYSICAL_INPUTS for suffix in ("count", "ambiguous_groups", "duplicate_entries")})
    for stage in ("ckf", "ambi"):
        values.update({stage + "_" + key: [] for key in ("raw", "quality_rejected", "invalid_covariance", "fake_event", "duplicate_event")})
    stream = gzip.open(directory / "events.jsonl.gz", "rt")
    seen = []
    for line in stream:
        row = json.loads(line)
        event = row["event"]
        seen.append(event)
        if int(hit_counts[str(event)]) != row["simhits"]:
            raise ValueError("Persisted ROOT-hit count differs from complete native simhit count")
        classified = module.classify_event(row, sensors, native_report["campaign"])
        if "ckf_input_measurements" not in row or row["ckf_input_measurements"] != len(row["measurements"]):
            raise ValueError("Explicit complete CKF-input audit missing or unequal")
        primary = row["generated"][0]["id"]
        associations = [{"geometry_id": m["geometry_id"], "particles": m["particles"]}
                        for m in row["measurements"] if primary in m["particles"]]
        associations.sort(key=lambda value: canonical(value))
        payload = {"generated": row["generated"], "simulated_particles": row["simulated_particles"],
                   "simulated_ids": row["simulated_ids"], "simhit_count": row["simhits"],
                   "pixel_measurements": [m for m in row["measurements"] if sensors[m["geometry_id"]][0] <= 3],
                   "spacepoints": row["spacepoints"], "seeds": row["seeds"],
                   "estimated_seeds": row["estimated_seeds"],
                   "primary_measurement_associations": associations,
                   "ckf_inputs": {"count": row["ckf_input_measurements"], "measurements": row["measurements"]}}
        for name, systems, fine_only in (("pixel_physical", (1, 2, 3), False), ("strixel_fine_u", (4, 5), True), ("long_strip_physical", (6, 7), False)):
            payload[name], counts = physical_measurements(row["measurements"], sensors, systems, fine_only)
            for suffix, count in zip(("count", "ambiguous_groups", "duplicate_entries"), counts):
                values[name + "_" + suffix].append(count)
        for name in FINGERPRINTS:
            extra[name].append(hit_hashes[int(event)] if name == "simhits_payload" else fingerprint(payload[name]))
        for name in ("simhits", "measurements", "primary_sensors", "spacepoints"):
            values[name].append(classified[name])
        for stage in ("ckf", "ambi"):
            for key in ("raw", "quality_rejected", "fake_event", "duplicate_event"):
                values[stage + "_" + key].append(classified[stage][key])
            values[stage + "_invalid_covariance"].append(sum(covariance_invalid(t) for t in row[stage]))
    stream.close()
    if seen != arrays["event"].tolist():
        raise ValueError("Native JSONL order/identities differ from retained event order")
    arrays.update({"fingerprint_" + key: np.asarray(value, dtype="U64") for key, value in extra.items()})
    arrays.update({key: np.asarray(value, dtype=np.int64) for key, value in values.items()})
    return arrays


def retain(source, output, pilot=False, pattern="*"):
    source, output = Path(source), Path(output)
    if (output / "native-reports.json.gz").exists():
        raise ValueError("Evidence inventory already exists; omit --source to replay or select fresh output")
    paths = sorted(source.glob(pattern + "/run-report.json"))
    reports = [json.loads(path.read_text()) for path in paths]
    validate_matrix(reports, pilot)
    contract = frozen_contract()
    for report in reports:
        validate_engine(report, contract)
    module = native_analyzer()
    inventory = []
    for path, report in zip(paths, reports):
        if report["outcome"] != "completed":
            raise ValueError("Incomplete native case: " + str(path))
        directory = path.parent
        identity = case_identity(report)
        name = case_name(identity)
        if report.get("case_id", name) != name:
            raise ValueError("Native case_id differs from declared scientific identity")
        for key in ("prepared_input_sha256", "output_sha256"):
            for relative, expected in report[key].items():
                target = directory / relative
                if not target.is_relative_to(directory) or digest(target) != expected:
                    raise ValueError("Changed/unsafe native prepared input or output: " + relative)
        with tempfile.TemporaryDirectory(prefix="des042-native-reduction-") as temporary:
            summary = module.analyze(directory, temporary)
            with np.load(Path(temporary) / "events.npz", allow_pickle=False) as data:
                arrays = {key: data[key] for key in data.files}
        if not np.array_equal(arrays["event"], np.arange(report["events"])):
            raise ValueError("Require contiguous unique all-generated event identities")
        roots = [directory / name for name in ("hits.root", "simhits.root", "simhits-pairing.root") if (directory / name).exists()]
        if len(roots) != 1:
            raise ValueError("Require native full-hit ROOT pairing evidence")
        hit_hashes, hit_provenance = simhit_fingerprints(roots[0], arrays["event"])
        native = json.loads((directory / "native-report.json").read_text())
        arrays = augment_arrays(directory, arrays, {**native, "campaign": report["campaign"]}, module, hit_hashes,
                                hit_provenance.pop("hits_by_event"))
        target = output / "cases" / name
        if target.exists() and any(target.iterdir()):
            raise ValueError("Refusing to overwrite retained case: " + name)
        target.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(target / "events.npz", **arrays)
        dump_gzip(target / "summary.json.gz", sanitize(summary))
        configs = {filename: json.loads((directory / filename).read_text()) for filename in
                   ("error-table.json", "digitization.json", "gbts/config.json")}
        configs["volume_system"] = {str((s["geometry_id"] >> 56) & 255): s["ids"]["system"] for s in native["sensors"]}
        dump_gzip(target / "configuration.json.gz", sanitize(configs))
        inventory.append({"case": name, "report": sanitize(report), "run_report_sha256": digest(path),
                          "native_summary_sha256": fingerprint(summary), "simhit_provenance": hit_provenance,
                          "files": {str(p.relative_to(output)): digest(p) for p in sorted(target.iterdir())},
                          "events_file": str((target / "events.npz").relative_to(output)),
                          "summary_file": str((target / "summary.json.gz").relative_to(output)),
                          "configuration_file": str((target / "configuration.json.gz").relative_to(output))})
    result = {"schema_version": 1, "status": "PROTOTYPE", "input_revision": INPUT_REVISION,
              "native_analyzer_sha256": NATIVE_ANALYZER_SHA256, "retention_source_sha256": digest(__file__),
              "frozen_contract": contract,
              "reports": inventory, "fingerprint_policy": "Per generated event; canonical sorted-key JSON; full native precision for JSONL and writer precision for all ROOT hit branches"}
    dump_gzip(output / "native-reports.json.gz", result)
    return result


def interval(k, n, z=1.):
    if not n:
        return None
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [max(0., centre - half), min(1., centre + half)]


def rate(k, n):
    k, n = int(k), int(n)
    return {"numerator": k, "denominator": n, "value": k / n if n else None,
            "wilson68": interval(k, n), "wilson95": interval(k, n, 1.959963984540054),
            "zero_one_sided95_upper": 1 - .05 ** (1 / n) if n and k == 0 else None}


def bootstrap_interval(values, probabilities=QUANTILES):
    finite = np.asarray(values)[np.isfinite(values)]
    return np.quantile(finite, probabilities).tolist() if finite.size > 1 else None


def distribution(values, thresholds=(), minimum=MINIMUM_WIDTH_ENTRIES):
    values = np.asarray(values, dtype=float)
    finite = values[np.isfinite(values)]
    result = {"entries": int(values.size), "finite_entries": int(finite.size),
              "nonfinite_entries": int(values.size - finite.size), "mean": None, "median": None,
              "population_sd": None, "rms": None, "width68": None, "min": None, "max": None,
              "quantile_probabilities": [.001, .01, QUANTILES[0], .5, QUANTILES[1], .99, .999],
              "quantiles": None, "absolute_tail_counts": {str(t): int(np.sum(np.abs(finite) > t)) for t in thresholds}}
    if finite.size:
        qs = np.quantile(finite, result["quantile_probabilities"])
        result.update(mean=float(finite.mean()), median=float(np.median(finite)),
                      population_sd=float(finite.std()), rms=float(np.sqrt(np.mean(finite ** 2))),
                      min=float(finite.min()), max=float(finite.max()), quantiles=qs.tolist())
        if finite.size >= minimum:
            result["width68"] = float((qs[4] - qs[2]) / 2)
    return result


def paired_widths(values, indices, minimum=MINIMUM_WIDTH_ENTRIES):
    """Four pitch rows; all resamples use the same generated-event columns."""
    values = np.asarray(values, dtype=float)
    if values.ndim != 2 or values.shape[0] != 4:
        raise ValueError("Require four paired pitch rows")
    stats = [distribution(row, minimum=minimum) for row in values]
    boot = np.full((4, len(indices)), np.nan)
    for pitch, row in enumerate(values):
        if row.size == 0 or stats[pitch]["width68"] is None:
            continue
        draw = row[indices]
        valid = np.sum(np.isfinite(draw), axis=1) >= minimum
        if np.any(valid):
            quantiles = np.nanquantile(draw[valid], QUANTILES, axis=1)
            boot[pitch, valid] = (quantiles[1] - quantiles[0]) / 2
    baseline = stats[0]["width68"]
    for pitch, stat in enumerate(stats):
        valid = np.isfinite(boot[pitch]) & np.isfinite(boot[0]) & (boot[0] > 0)
        ratio = boot[pitch, valid] / boot[0, valid]
        finite = boot[pitch, np.isfinite(boot[pitch])]
        stat.update(width_interval68=bootstrap_interval(finite),
                    width_bootstrap_defined=int(finite.size),
                    width_se=float(finite.std(ddof=1)) if finite.size > 1 else None,
                    ratio_to_baseline=stat["width68"] / baseline if baseline and stat["width68"] is not None else None,
                    ratio_interval68=bootstrap_interval(ratio), ratio_bootstrap_defined=int(ratio.size))
    return stats


def observables(arrays, stage):
    residual = np.array(arrays[stage + "_residual"], copy=True)
    residual[:, 5] /= 299.792458
    truth, reco = arrays["truth"], arrays[stage + "_reco"]
    with np.errstate(divide="ignore", invalid="ignore"):
        true_pt = np.abs(np.sin(truth[:, 3]) / truth[:, 4])
        reco_pt = np.abs(np.sin(reco[:, 3]) / reco[:, 4])
        relative = (true_pt - reco_pt) / true_pt
    relative[~np.isfinite(relative)] = np.nan
    return np.column_stack((residual, relative))


def verify_arrays(arrays, summary):
    n = summary["events"]
    if not np.array_equal(arrays["event"], np.arange(n)):
        raise ValueError("Retained all-generated event denominator changed")
    for stage in ("ckf", "ambi"):
        for key, expected in summary["stages"][stage]["counts"].items():
            name = stage + "_" + key
            if name in arrays and int(np.sum(arrays[name])) != expected:
                raise ValueError("Retained classifier count changed: " + name)
        residual = arrays["truth"] - arrays[stage + "_reco"]
        residual[:, 2] = (residual[:, 2] + math.pi) % (2 * math.pi) - math.pi
        for name, expected in (("residual", residual), ("pull", residual / np.sqrt(arrays[stage + "_variance"]))):
            if not np.array_equal(arrays[stage + "_" + name], expected, equal_nan=True):
                raise ValueError("Retained residual/pull formula changed")
        matched = arrays[stage + "_matched"].astype(bool)
        if np.any(np.isfinite(arrays[stage + "_reco"][~matched])):
            raise ValueError("Unmatched event contains representative parameters")
    if any(len(value) != n for value in arrays.values()):
        raise ValueError("Retained array length mismatch")
    for key in FINGERPRINTS:
        if "fingerprint_" + key not in arrays:
            raise ValueError("Missing retained event fingerprint: " + key)


def stage_summary(arrays, mask, stage, indices):
    n = int(mask.sum())
    keys = ("raw", "accepted", "quality_rejected", "invalid_covariance", "matched", "fake", "duplicates", "secondary", "wrong_charge", "fake_event", "duplicate_event")
    counts = {key: int(arrays[stage + "_" + key][mask].sum()) for key in keys}
    counts["primary_candidates"] = counts["accepted"] - counts["fake"] - counts["secondary"]
    result = {"counts": counts, "efficiency": rate(counts["matched"], n),
              "failure": rate(n - counts["matched"], n), "wrong_charge": rate(counts["wrong_charge"], counts["matched"]),
              "fake_event": rate(counts["fake_event"], n), "duplicate_event": rate(counts["duplicate_event"], n)}
    for key in ("reconstructable", "reconstructable4"):
        selected = mask & arrays[key].astype(bool)
        result[key + "_conditional"] = rate(arrays[stage + "_matched"][selected].sum(), selected.sum())
    for key in ("fake", "duplicates", "secondary", "quality_rejected", "invalid_covariance"):
        denominator_key = "raw" if key in ("quality_rejected", "invalid_covariance") else "accepted"
        numerator = arrays[stage + "_" + key][mask]
        denominator = arrays[stage + "_" + denominator_key][mask]
        ratios = np.full(len(indices), np.nan)
        if n:
            totals = denominator[indices].sum(axis=1)
            valid = totals > 0
            ratios[valid] = numerator[indices[valid]].sum(axis=1) / totals[valid]
        result[key + "_candidate_fraction"] = {"numerator": counts[key], "denominator": counts[denominator_key],
            "value": counts[key] / counts[denominator_key] if counts[denominator_key] else None,
            "event_bootstrap68": bootstrap_interval(ratios), "event_bootstrap95": bootstrap_interval(ratios, (.025, .975))}
    return result


def paired_bin(arrays, mask, replicates, seed):
    n = int(mask.sum())
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, n, (replicates, n)) if n else np.empty((replicates, 0), dtype=int)
    cases = [{"events": n, "seed_coverage": rate(a["pure_seed"][mask].sum(), n),
              "estimated_seed_coverage": rate(a["pure_estimated_seed"][mask].sum(), n),
              "reconstructable": rate(a["reconstructable"][mask].sum(), n),
              "stage_counts": {key: int(a[key][mask].sum()) for key in ("simhits", "measurements", "primary_measurements", "primary_sensors", "spacepoints", "seeds", "estimated_seeds")},
              "stages": {}} for a in arrays]
    for stage in ("ckf", "ambi"):
        stats = [stage_summary(a, mask, stage, indices) for a in arrays]
        efficiencies = np.stack([a[stage + "_matched"][mask] for a in arrays])
        for pitch, stat in enumerate(stats):
            diff = efficiencies[pitch] - efficiencies[0]
            draws = diff[indices].mean(axis=1) if n else np.full(replicates, np.nan)
            stat["efficiency_difference_to_baseline"] = {"value": float(diff.mean()) if n else None,
                "discordant_events": int(np.count_nonzero(diff)), "paired_bootstrap68": bootstrap_interval(draws),
                "paired_bootstrap95": bootstrap_interval(draws, (.025, .975)),
                "both_success": int(np.sum((efficiencies[pitch] == 1) & (efficiencies[0] == 1))),
                "both_failure": int(np.sum((efficiencies[pitch] == 0) & (efficiencies[0] == 0))),
                "gain": int(np.sum(diff == 1)), "loss": int(np.sum(diff == -1))}
            stat["quantities"] = {}
        values = np.stack([observables(a, stage)[mask] for a in arrays])
        pulls = [a[stage + "_pull"][mask] for a in arrays]
        for qi, quantity in enumerate(PARAMETERS):
            own = values[:, :, qi]
            all_stats = paired_widths(own, indices)
            # Keep generated-event indices even in common-success resampling.
            common = np.all(np.isfinite(own), axis=0)
            common_values = np.where(common[None, :], own, np.nan)
            common_stats = paired_widths(common_values, indices)
            for pitch, stat in enumerate(stats):
                all_stats[pitch]["absolute_tail_counts"] = distribution(own[pitch], TAILS[qi])["absolute_tail_counts"]
                stat["quantities"][quantity] = {"unit": UNITS[qi], "residual": all_stats[pitch],
                    "common_success_residual": common_stats[pitch], "common_success_events": int(common.sum()),
                    "pull": distribution(pulls[pitch][:, qi], (3., 5.)) if qi < 6 else None}
        for case, stat in zip(cases, stats):
            case["stages"][stage] = stat
    return cases


def compare_pairing(arrays):
    required = ("generated", "simulated_particles", "simulated_ids", "simhit_count", "simhits_payload")
    result = {}
    for name in FINGERPRINTS:
        key = "fingerprint_" + name
        mismatches = [int(np.count_nonzero(a[key] != arrays[0][key])) for a in arrays]
        result[name] = {"all_pitches_equal": not any(mismatches), "mismatch_events_by_pitch": mismatches,
                        "baseline_event_fingerprints_sha256": fingerprint(arrays[0][key].tolist())}
        if name in required and any(mismatches):
            raise ValueError("Transport pairing failed: " + name + " mismatches " + str(mismatches))
    result["measurement_noise_attribution"] = ("Pixel inputs and seeds identical across all pitches" if
        all(result[k]["all_pitches_equal"] for k in ("pixel_measurements", "spacepoints", "seeds", "estimated_seeds")) else
        "Measured pixel inputs or seeds differ; bounded Gaussian retries can shift random draws. Differences cannot be attributed uniquely to longitudinal covariance.")
    result["physical_inputs"] = {}
    for name in PHYSICAL_INPUTS:
        counts = [a[name + "_count"] for a in arrays]
        result["physical_inputs"][name] = {
            "definition": "Index-free sorted multiset of geometry_id, particle associations, measured values and variances; fine-u projection for strixels; repeated entries preserved",
            "measurement_counts_by_pitch": [int(value.sum()) for value in counts],
            "measurement_losses_vs_baseline_by_pitch": [int(np.maximum(0, counts[0] - value).sum()) for value in counts],
            "measurement_gains_vs_baseline_by_pitch": [int(np.maximum(0, value - counts[0]).sum()) for value in counts],
            "ambiguous_physical_groups_by_pitch": [int(a[name + "_ambiguous_groups"].sum()) for a in arrays],
            "duplicate_physical_entries_by_pitch": [int(a[name + "_duplicate_entries"].sum()) for a in arrays],
            "changed_events_by_pitch": result[name]["mismatch_events_by_pitch"]}
    return result


def validate_configurations(items, configs):
    reports = [item["report"] for item in items]
    campaigns = []
    for report in reports:
        if report.get("input_revision") != INPUT_REVISION or report["profile"] != "pt4-nominal-triplet":
            raise ValueError("Unexpected scientific input revision or GBTS profile")
        if not all(report.get("postrun_immutability", {}).get(key) is True for key in ("native_supplier_runtime", "prepared_inputs", "source")):
            raise ValueError("Native postrun immutability checks missing or failed")
        equivalence = report.get("baseline_equivalence", {})
        if any(equivalence.get(key, {}).get("matched") is not True for key in ("selection.json", "material-map.json", "error-table.json", "digitization.json")):
            raise ValueError("Frozen balanced-baseline equivalence missing or failed")
        audit = report.get("event_audit", {})
        if audit.get("all_generated_events_retained") is not True or audit.get("all_native_survivors_converged") is not True:
            raise ValueError("Native all-event/converged ambiguity gate missing or failed")
        campaign = copy.deepcopy(report["campaign"])
        # The wrapper's declared response metadata is the only allowed change.
        extension = campaign.get("strixel_crosscheck", {})
        if extension:
            extension["pitch_mm"] = .5
        campaigns.append(campaign)
    expected_seed = 123042 if reports[0]["campaign"]["particle"] == "muon" and reports[0]["campaign"]["simulation"] == "fatras" else (133042 if reports[0]["campaign"]["simulation"] == "fatras" else 143042)
    if any(r["seed"] != expected_seed for r in reports):
        raise ValueError("Frozen population seed differs")
    if any(value != campaigns[0] for value in campaigns[1:]):
        raise ValueError("A campaign setting other than declared strixel pitch changed")
    for field in ("source_revision", "source_sha256", "runtime_sha256", "baseline_input_sha256", "supplier_identity"):
        if field not in reports[0] or any(r.get(field) != reports[0][field] for r in reports[1:]):
            raise ValueError("Native/source/configuration identity differs or absent: " + field)
    for field in ("selection.json", "material-map.json", "native-report.json", "pixel-selection.json", "gbts/config.json", "gbts/mapping.csv", "gbts/layers.csv", "gbts/connections.csv"):
        hashes = [r["prepared_input_sha256"].get(field) for r in reports]
        if None in hashes or len(set(hashes)) != 1:
            raise ValueError("Detector/material/GBTS prepared identity changed: " + field)
    if any(c["gbts/config.json"] != configs[0]["gbts/config.json"] for c in configs[1:]):
        raise ValueError("GBTS effective configuration changed")
    # Compare entire error tables and digitization after reversing only local-v
    # Gaussian widths for systems4/5. The native variance audit already checks
    # every observed measurement against its actual table, without tolerances.
    base = configs[0]
    volume_system = base["volume_system"]
    if any(c["volume_system"] != volume_system for c in configs[1:]):
        raise ValueError("Physical volume/system mapping changed")
    baseline_widths = {(g["volume"], g["index"]): g for g in base["error-table.json"]["groups"]}
    for report, config in zip(reports, configs):
        scale = float(report["pitch_mm"]) / .5
        current = config["error-table.json"]
        baseline = base["error-table.json"]
        if set(current) != set(baseline):
            raise ValueError("Error-table schema changed")
        if {key: value for key, value in current.items() if key != "groups"} != {key: value for key, value in baseline.items() if key != "groups"}:
            raise ValueError("Error-table metadata changed")
        if len(current["groups"]) != len(baseline_widths) or {(g["volume"], g["index"]) for g in current["groups"]} != set(baseline_widths):
            raise ValueError("Error-table groups changed")
        for group in current["groups"]:
            key = group["volume"], group["index"]
            original = baseline_widths[key]
            is_longitudinal = volume_system[str(group["volume"])] in (4, 5) and group["index"] == 1
            expected = original["sigma_mm"] * (scale if is_longitudinal else 1.)
            if not math.isclose(group["sigma_mm"], expected, rel_tol=2e-15, abs_tol=0.):
                raise ValueError("Response changed beyond systems4/5 local-v sigma")
            normalized = copy.deepcopy(group)
            normalized["sigma_mm"] = original["sigma_mm"]
            if normalized != original:
                raise ValueError("Error-table field beyond sigma changed")
        normal_digi = copy.deepcopy(config["digitization.json"])
        base_digi = base["digitization.json"]
        # Recursive pairwise comparison allows only Gaussian stddev fields which
        # correspond to a scaled local-v error-table volume; all else is exact.
        allowed = {volume for (volume, index), g in baseline_widths.items() if index == 1 and volume_system[str(volume)] in (4, 5)}
        def walk(own, original, volume=None):
            if isinstance(own, dict) and isinstance(original, dict):
                if own.keys() != original.keys():
                    raise ValueError("Digitization schema changed")
                volume = own.get("volume", volume)
                for key in own:
                    if key == "stddev" and volume in allowed and own.get("index") == 1:
                        if not math.isclose(own[key], original[key] * scale, rel_tol=2e-15):
                            raise ValueError("Digitization longitudinal width differs")
                    else:
                        walk(own[key], original[key], volume)
            elif isinstance(own, list) and isinstance(original, list):
                if len(own) != len(original):
                    raise ValueError("Digitization entries changed")
                for x, y in zip(own, original):
                    walk(x, y, volume)
            elif own != original:
                raise ValueError("Digitization changed beyond local-v Gaussian stddev")
        walk(normal_digi, base_digi)


def analyze(output, inventory, *, replicates=400, pilot=False):
    output = Path(output)
    items = inventory["reports"]
    validate_matrix([item["report"] for item in items], pilot)
    for item in items:
        validate_engine(item["report"], inventory["frozen_contract"])
    # Detector/material/GBTS identity is common to all populations and momenta.
    for name in ("selection.json", "material-map.json", "native-report.json", "pixel-selection.json", "gbts/config.json", "gbts/mapping.csv", "gbts/layers.csv", "gbts/connections.csv"):
        values = [item["report"]["prepared_input_sha256"].get(name) for item in items]
        if None in values or len(set(values)) != 1:
            raise ValueError("Detector/material/GBTS identity differs across matrix: " + name)
    if not pilot and len({item["report"]["source_revision"] for item in items}) != 1:
        raise ValueError("Production source revision differs across matrix")
    groups = []
    identities = sorted({case_identity(item["report"])[:3] for item in items})
    for gi, identity in enumerate(identities):
        selected = sorted((item for item in items if case_identity(item["report"])[:3] == identity),
                          key=lambda item: item["report"]["pitch_mm"])
        arrays, configs, summaries = [], [], []
        for item in selected:
            for name, expected in item["files"].items():
                target = output / name
                if not target.is_relative_to(output) or digest(target) != expected:
                    raise ValueError("Retained evidence changed: " + name)
            with np.load(output / item["events_file"], allow_pickle=False) as data:
                own = {key: data[key] for key in data.files}
            summary = read_gzip(output / item["summary_file"])
            verify_arrays(own, summary)
            arrays.append(own)
            summaries.append(summary)
            configs.append(read_gzip(output / item["configuration_file"]))
        validate_configurations(selected, configs)
        for own in arrays[1:]:
            for key in ("event", "eta", "pt", "charge", "truth"):
                if not np.array_equal(own[key], arrays[0][key], equal_nan=True):
                    raise ValueError("Generated-event pairing differs: " + key)
        pairing = compare_pairing(arrays)
        eta = arrays[0]["eta"]
        cases = [{"pitch_mm": pitch, "case": item["case"], "eta_bins": [], "abs_eta_bins": [], "summary_regions": []}
                 for pitch, item in zip(PITCHES, selected)]
        bins = [("global", None, None, np.ones(len(eta), dtype=bool))]
        for projection, edges, values in (("eta_bins", summaries[0]["eta_edges"], eta),
                                           ("abs_eta_bins", np.linspace(0, 4, 9), np.abs(eta)),
                                           ("summary_regions", (0, 1, 2.5, 4), np.abs(eta))):
            for bi, (lo, hi) in enumerate(zip(edges, edges[1:])):
                mask = (values >= lo) & (values <= hi if bi == len(edges) - 2 else values < hi)
                bins.append((projection, float(lo), float(hi), mask))
        for bi, (projection, lo, hi, mask) in enumerate(bins):
            stats = paired_bin(arrays, mask, replicates, BOOTSTRAP_SEED + gi * 1000 + bi)
            for case, stat in zip(cases, stats):
                if projection == "global":
                    case["global"] = stat
                else:
                    case[projection].append({"low": lo, "high": hi, **stat})
        groups.append({"simulation": identity[0], "particle": identity[1], "pt_GeV": identity[2],
                       "pairing": pairing, "cases": cases})
    return {"schema_version": 1, "status": "PROTOTYPE", "design": "DES041/DES042 DRAFT; no detector acceptance inferred",
            "response": "Frozen pooled Gaussian baseline; only systems4/5 local-v sigma scaled by pitch/0.5; no merging; finite boundary retries",
            "residual_convention": "truth minus reconstruction; phi wrapped; relative pT derived from true/reco theta and q/p",
            "uncertainty": "Statistical only; no physical sensor calibration or detector/material/field model systematics; populations are never pooled",
            "tail_policy": "All finite matched-primary representatives including wrong charge; no residual/pull cuts; nonfinite slots explicit",
            "bootstrap": {"replicates": replicates, "seed": BOOTSTRAP_SEED, "minimum_width_entries": MINIMUM_WIDTH_ENTRIES,
                          "probability": PROBABILITY, "pairing": "Same generated-event indices across pitches; common-success intersection of all four pitches"},
            "width_convention": "(q0.8413447460685429 - q0.15865525393145707)/2, exact Gaussian central 68.268949%; frozen native summary separately retains its historical q0.84/q0.16 convention",
            "provenance": {"analyzer_sha256": digest(__file__), "native_reports_sha256": digest(output / "native-reports.json.gz"),
                           "native_analyzer_sha256": inventory["native_analyzer_sha256"], "input_revision": INPUT_REVISION,
                           "source_revisions": sorted({item["report"]["source_revision"] for item in items})},
            "groups": groups}


def markdown(payload):
    def percent(value):
        return "—" if value is None else f"{100 * value:.2f}%"
    lines = ["# Frozen GBTS strixel longitudinal-response sensitivity", "",
             "DES042 / isolated PROTOTYPE. Statistical comparison of a scaled frozen Gaussian response; no physical coarse-sensor calibration or detector acceptance.", "",
             "All generated primaries remain in efficiency denominators. Pixel-only measured space points seed GBTS; the full seven-system measurement collection enters CKF. Native covariance, ambiguity, dimensions, variances and measured-spacepoint checks run unchanged before compact retention.", "",
             "| Transport / species | pT [GeV] | Pitch [mm] | Primary efficiency [95% Wilson] | Reconstructable conditional | Fake events | Duplicates | Quality rejected | Invalid covariance |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for group in payload["groups"]:
        for case in group["cases"]:
            stat = case["global"]["stages"]["ambi"]
            rate_ = stat["efficiency"]
            bounds = rate_["wilson95"]
            efficiency = percent(rate_["value"]) + (f" [{100 * bounds[0]:.2f}, {100 * bounds[1]:.2f}]" if bounds else "")
            c = stat["counts"]
            lines.append(f"| {group['simulation']} / {group['particle']} | {group['pt_GeV']:g} | {case['pitch_mm']:g} | {efficiency} | {percent(stat['reconstructable_conditional']['value'])} | {c['fake_event']} | {c['duplicates']} | {c['quality_rejected']} | {c['invalid_covariance']} |")
    lines += ["", "The compressed [machine report](profiles.json.gz) retains all rates, Wilson 68/95 intervals, exact one-sided 95% upper limits for zero failure/fake events, whole-event candidate-fraction bootstrap intervals and paired efficiency differences. Reconstructability requires six unique sensor measurements and three physical pixel groups; the nested four-group result is retained.", "",
              "Residuals are truth−reconstruction, with wrapped φ; relative pT is derived from θ and q/p. Central 68.27% half-widths need at least 30 finite entries. Bias, SD/RMS, quantiles, extrema and tails keep all finite matched entries, including wrong charge. All six bound pulls remain retained; time is prior dominated. Paired bootstrap uses 400 fixed-seed event resamples; the common-success control conditions on success at all four pitches. Unavailable widths/bins are null, never zero or NaN.", "",
              "Per-case compressed native summaries/configurations and all-event NPZ arrays are under `cases/`. The native inventory retains source/data/runtime/configuration hashes, original report hashes and per-event fingerprints. ROOT-hit pairing compares all persisted branches at native-writer precision; generated and transported JSONL records use their full persisted precision.", "",
              "| Transport / species | pT [GeV] | Pixel inputs / space points / seeds equal across pitches | Primary measurement-association changes vs 0.5 mm |", "|---|---:|---|---|"]
    for group in payload["groups"]:
        pair = group["pairing"]
        equal = all(pair[k]["all_pitches_equal"] for k in ("pixel_measurements", "spacepoints", "seeds", "estimated_seeds"))
        changes = pair["primary_measurement_associations"]["mismatch_events_by_pitch"]
        lines.append(f"| {group['simulation']} / {group['particle']} | {group['pt_GeV']:g} | {equal} | {changes} |")
    lines += ["", "Generated particles, transported particle records/identities and complete persisted simhit payloads must agree event by event or analysis stops. Bounded Gaussian rejection near sensor edges can consume different random draws and change pixel inputs or seeds. Where those differ, the reconstruction change cannot be attributed uniquely to longitudinal covariance.", "",
              "Geant4 uses detailed DD4hep transport; Fatras and reconstruction use the retained effective material map. Electron transport/CKF, finite Geant4 time and volume limits, single-particle occupancy and unmerged Gaussian response retain the DES041 qualifications. There is no pooling across species, transport or momenta and no new GBTS tuning.", "",
              "Figures in `figures/` aggregate the matrix by population; PNG and PDF show statistical intervals and physical units. Full raw tails remain in the retained arrays."]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="Native parent directory; omit to replay retained evidence")
    parser.add_argument("--pattern", default="*", help="Explicit native case-directory glob, e.g. fatras-muon-* for a mixed smoke parent")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pilot", action="store_true", help="Exactly four pitches at one population/momentum")
    parser.add_argument("--replicates", type=int, default=400)
    parser.add_argument("--verify", action="store_true", help="Recompute point statistics and bootstrap, compare stored report exactly")
    args = parser.parse_args()
    if args.replicates != 400:
        parser.error("Frozen study requires exactly 400 bootstrap replicates")
    if args.verify and args.source:
        parser.error("--verify replays retained evidence; omit --source")
    inventory = retain(args.source, args.output, args.pilot, args.pattern) if args.source else read_gzip(args.output / "native-reports.json.gz")
    result = analyze(args.output, inventory, replicates=args.replicates, pilot=args.pilot)
    destination = args.output / "profiles.json.gz"
    if args.verify:
        if canonical(read_gzip(destination)) != canonical(result):
            raise ValueError("Deterministic retained-evidence replay differs from stored statistics/bootstrap")
        if (args.output / "results.md").read_text() != markdown(result):
            raise ValueError("Stored Markdown differs from replay")
        print("Verified exact point-statistic, bootstrap and Markdown replay")
    else:
        if destination.exists() and read_gzip(destination).get("provenance", {}).get("native_reports_sha256") != result["provenance"]["native_reports_sha256"]:
            raise ValueError("Refusing to overwrite report with a different native case inventory")
        dump_gzip(destination, result)
        (args.output / "results.md").write_text(markdown(result))
        print("Analyzed", len(inventory["reports"]), "cases;", len(result["groups"]), "paired population/momentum groups")


if __name__ == "__main__":
    main()
