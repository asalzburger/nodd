#!/usr/bin/env python3
"""Reduce native ACTS truth-associated tracking outputs without a ROOT runtime."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

import awkward as ak
import numpy as np
import uproot

from metrics import (QUANTITIES, binomial_interval, interval_mask,
                     perigee_observables, statistics)

PARAMETERS = ("eLOC0", "eLOC1", "ePHI", "eTHETA", "eQOP")
BARCODE = ("vertex_primary", "vertex_secondary", "particle", "generation", "sub_particle")
AUDIT = ("generated", "simhits", "measurements", "selected", "fit_attempts",
         "fit_tracks", "invalid_covariance", "primary_measurements")


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def flat(table, name):
    return ak.to_numpy(ak.flatten(table[name], axis=None))


def event_indices(events, requested):
    """Exact event identity lookup, never positional alignment or interpolation."""
    events, requested = np.asarray(events), np.asarray(requested)
    if events.size != np.unique(events).size:
        raise ValueError("Repeated generated event ID")
    order = np.argsort(events)
    indices = np.searchsorted(events[order], requested)
    if np.any(indices >= len(events)):
        raise ValueError("Track/audit event absent from generated particles")
    result = order[indices]
    if not np.array_equal(events[result], requested):
        raise ValueError("Track/audit event absent from generated particles")
    return result


def audit_measurement_errors(path, table):
    """Compare every recorded measured marginal against the frozen native lookup."""
    lookup = {(entry["volume"], row["index"]): np.asarray(row["rms"], dtype=float)
              for entry in table["entries"] for row in entry["value"]}
    with uproot.open(path) as stream:
        data = stream["measurements"].arrays(
            ["volume_id"] + [prefix + str(index) for index in (0, 1)
                             for prefix in ("rec_loc", "var_loc", "clus_size_loc")],
            library="np")
    checked, maximum = 0, 0.
    observed = set()
    for volume in np.unique(data["volume_id"]):
        for index in (0, 1):
            mask = (data["volume_id"] == volume) & np.isfinite(data["rec_loc" + str(index)])
            if not np.any(mask):
                continue
            key = (int(volume), index)
            if key not in lookup:
                raise ValueError("Measured volume/coordinate absent from frozen hit-error table")
            observed.add(key)
            rms = lookup[key]
            sizes = data["clus_size_loc" + str(index)][mask].astype(int)
            if np.any(sizes < 1):
                raise ValueError("Measured cluster has no physical cells")
            expected = rms[np.minimum(sizes, len(rms)) - 1] ** 2
            actual = data["var_loc" + str(index)][mask]
            # ROOT writer stores float32 marginals. Require the exact expected
            # stored representation, rather than a loose physics tolerance.
            if not np.array_equal(actual, expected.astype(actual.dtype)):
                raise ValueError("Written measurement covariance differs from frozen RMS squared")
            checked += len(actual)
            maximum = max(maximum, float(np.max(np.abs(actual - expected) / expected)))
    if observed != set(lookup):
        raise ValueError("Performance measurements do not cover every trained coordinate")
    return {"measured_coordinates": checked,
            "volume_coordinate_pairs": len(observed),
            "comparison": "Exact equality after ROOT branch dtype conversion",
            "max_relative_storage_roundoff": maximum}


def read_case(directory, campaign, production=True):
    directory = Path(directory)
    report = json.loads((directory / "run-report.json").read_text())
    if report["outcome"] != "completed" or report["campaign"] != campaign:
        raise ValueError("Native run incomplete or effective campaign differs")
    events = report["events"]
    if production and events != campaign["events_per_case"]:
        raise ValueError("Production event count differs from campaign")
    source_files = [directory / name for name in
                    ("particles.root", "audit.root", "tracksummary_kf.root")]
    error_audit = None
    table_hash = None
    if production:
        root = Path(__file__).resolve().parents[3]
        table_path = root / campaign["error_training"]["error_table"]
        table_hash = sha256(table_path)
        recorded = [f["sha256"] for f in report["provenance"]["files"]
                    if f["name"] == table_path.name]
        if recorded != [table_hash]:
            raise ValueError("Native performance case did not load the frozen training table")
        source_files.append(directory / "measurements.root")
        error_audit = audit_measurement_errors(
            directory / "measurements.root", json.loads(table_path.read_text()))
    for path in source_files:
        recorded = [f["sha256"] for f in report["provenance"]["files"]
                    if f["name"] == path.name]
        if recorded != [sha256(path)]:
            raise ValueError("Native output hash differs from run provenance: " + path.name)
    if report["native_decoration"].get("map_key_count") != 65:
        raise ValueError("Missing exact PR100 keyed map reload")
    with uproot.open(directory / "particles.root") as stream:
        generated = stream["particles"].arrays(library="ak")
    if len(generated) != events or not np.all(ak.to_numpy(ak.num(generated["pt"])) == 1):
        raise ValueError("Require exactly one generated primary muon per event")
    generated_ids = ak.to_numpy(generated["event_id"])
    if len(np.unique(generated_ids)) != events:
        raise ValueError("Repeated generated event ID")
    eta = flat(generated, "eta")
    pt = flat(generated, "pt")
    if (not np.all(np.isfinite(eta)) or
            not np.allclose(pt, report["pt_GeV"], rtol=2.e-6, atol=1.e-7)):
        raise ValueError("Generated pT or eta differs from declared gun")
    if not np.all(np.abs(flat(generated, "particle_type")) == 13):
        raise ValueError("Non-muon in generated baseline sample")
    if not np.all(np.abs(flat(generated, "q")) == 1):
        raise ValueError("Require unit-charge generated muons")
    # This first campaign is explicitly an origin-vertex fixture. With that
    # restriction generated phi/theta/qOverP are the perigee truth parameters.
    if any(np.any(flat(generated, coordinate) != 0) for coordinate in ("vx", "vy", "vz")):
        raise ValueError("Non-origin truth requires proper field extrapolation to perigee")
    truth = np.column_stack([np.zeros(events), np.zeros(events),
                             flat(generated, "phi"), flat(generated, "theta"),
                             flat(generated, "q_over_p")])
    with uproot.open(directory / "audit.root") as stream:
        audit_raw = stream["audit"].arrays(["event_nr", *AUDIT], library="np")
    audit_order = event_indices(audit_raw["event_nr"], generated_ids)
    audit = {name: audit_raw[name][audit_order].astype(np.int64) for name in AUDIT}
    if not np.all(audit["generated"] == 1):
        raise ValueError("Native audit denominator differs from generated tree")
    if any(np.any(audit[name] < 0) for name in AUDIT):
        raise ValueError("Negative native stage count")
    if (np.any(audit["selected"] > 1) or np.any(audit["fit_attempts"] > audit["selected"])
            or np.any(audit["fit_tracks"] > audit["fit_attempts"])):
        raise ValueError("Truth candidate/fit stages do not partition this single-muon sample")
    for name in AUDIT:
        if int(audit[name].sum()) != report["counts"][name]:
            raise ValueError("Native report/audit count mismatch: " + name)
    branches = ["event_nr", "track_nr", "hasFittedParams", "nMeasurements", "t_eta",
                "t_pT", "t_d0", "t_z0", "t_phi", "t_theta", "t_charge", "t_p"]
    branches += ["majorityParticleId_" + key for key in BARCODE]
    branches += [key + "_fit" for key in PARAMETERS]
    branches += ["cov_" + a + "_" + b for a in PARAMETERS for b in PARAMETERS]
    with uproot.open(directory / "tracksummary_kf.root") as stream:
        tracks = stream["tracksummary"].arrays(branches, library="ak")
    track_events = ak.to_numpy(ak.flatten(ak.broadcast_arrays(
        tracks["event_nr"], tracks["track_nr"])[0]))
    track_to_generated = event_indices(generated_ids, track_events)
    track_counts = np.bincount(track_to_generated, minlength=events)
    if np.any(track_counts > 1):
        raise ValueError("Duplicate fitted tracks for a single generated muon; investigate before reduction")
    if not np.array_equal(track_counts, audit["fit_tracks"]):
        raise ValueError("Native fit audit differs from written track multiplicities")
    for key in BARCODE:
        if not np.array_equal(flat(tracks, "majorityParticleId_" + key),
                              flat(generated, key)[track_to_generated]):
            raise ValueError("Fitted track is not associated to the generated primary")
    np.testing.assert_allclose(flat(tracks, "t_eta"), eta[track_to_generated], atol=2.e-6, rtol=2.e-6)
    np.testing.assert_allclose(flat(tracks, "t_pT"), pt[track_to_generated], atol=1.e-6, rtol=2.e-6)
    fitted = np.column_stack([flat(tracks, key + "_fit") for key in PARAMETERS])
    covariance = np.empty((len(fitted), 5, 5))
    for i, a in enumerate(PARAMETERS):
        for j, b in enumerate(PARAMETERS):
            covariance[:, i, j] = flat(tracks, "cov_" + a + "_" + b)
    values, flags = perigee_observables(fitted, truth[track_to_generated], covariance)
    has_parameters = flat(tracks, "hasFittedParams").astype(bool)
    for pair in values.values():
        for name in pair:
            pair[name][~has_parameters] = np.nan
    # Inflate per-track results back onto all generated events. Thus a missing
    # fit has an explicit row and can never vanish from an eta denominator.
    aligned = {}
    for quantity, pair in values.items():
        aligned[quantity] = {}
        for name, data in pair.items():
            array = np.full(events, np.nan)
            array[track_to_generated] = data
            aligned[quantity][name] = array
    aligned_flags = {}
    for name, data in flags.items():
        aligned_flags[name] = np.zeros(events, dtype=bool)
        aligned_flags[name][track_to_generated] = data & has_parameters
    fitted_mask = track_counts.astype(bool)
    finite_fit = aligned_flags["finite_fitted_parameters"]
    metadata = {
        "simulation": report["simulation"], "pt_GeV": report["pt_GeV"],
        "events": events, "native_counts": report["counts"],
        "run_report_sha256": sha256(directory / "run-report.json"),
        "input_files": [{"name": path.name, "sha256": sha256(path)} for path in source_files],
        "native_provenance": report["provenance"],
        "digitization_sensors_by_system": report["digitization_sensors_by_system"],
        "digitization_native_defaults": report["digitization_native_defaults"],
        "hit_error_table_sha256": table_hash, "measurement_error_audit": error_audit,
        "wall_seconds": report["wall_seconds"],
        "generated_truth_sha256": hashlib.sha256(np.column_stack(
            [eta, pt, truth[:, 2:]]).astype("<f8").tobytes()).hexdigest(),
    }
    return metadata, eta, audit, aligned, aligned_flags, fitted_mask, finite_fit


def summarize_bin(mask, audit, values, flags, fitted_mask, finite_fit, settings, rng):
    generated = int(mask.sum())
    counts = {"generated": generated}
    counts.update({name: int(data[mask].sum()) for name, data in audit.items()
                   if name not in ("generated", "invalid_covariance")})
    counts["native_invalid_covariance"] = int(audit["invalid_covariance"][mask].sum())
    counts["finite_fit"] = int(finite_fit[mask].sum())
    counts["invalid_covariance"] = int(np.sum(mask & fitted_mask & ~flags["valid_covariance"]))
    counts["fit_failures"] = counts["fit_attempts"] - counts["fit_tracks"]
    counts["not_selected"] = generated - counts["selected"]
    counts["wrong_charge"] = int(np.sum(mask & finite_fit & flags["wrong_charge"]))
    result = {"counts": counts,
              "fit_fraction": binomial_interval(counts["finite_fit"], generated),
              "selected_fraction": binomial_interval(counts["selected"], generated),
              "quantities": {}}
    selected = mask & fitted_mask
    for quantity, pair in values.items():
        result["quantities"][quantity] = {
            name: statistics(data[selected],
                             probability=settings["central_probability"],
                             minimum_entries=settings["minimum_entries"],
                             bootstrap_replicates=settings["bootstrap_replicates"], rng=rng)
            for name, data in pair.items()
        }
        pull = pair["pull"][selected]
        finite_pull = pull[np.isfinite(pull)]
        result["quantities"][quantity]["pull_tail_abs_gt3"] = binomial_interval(
            int(np.sum(np.abs(finite_pull) > 3)), len(finite_pull))
    return result


def reduce_case(directory, campaign, rng, production=True):
    metadata, eta, audit, values, flags, fitted_mask, finite_fit = read_case(
        directory, campaign, production)
    settings = campaign["analysis"]
    args = audit, values, flags, fitted_mask, finite_fit, settings, rng
    metadata["global"] = summarize_bin(np.ones(len(eta), dtype=bool), *args)
    for name, edges, absolute in [
        ("eta_profiles", np.linspace(*campaign["eta_range"],
            round(np.diff(campaign["eta_range"])[0] / settings["eta_bin_width"]) + 1), False),
        ("abs_eta_profiles", np.asarray(settings["absolute_eta_slices"]), True),
    ]:
        metadata[name] = []
        for index, (low, high) in enumerate(zip(edges[:-1], edges[1:])):
            mask = interval_mask(eta, low, high, final=index == len(edges) - 2, absolute=absolute)
            item = summarize_bin(mask, *args)
            item.update(low=float(low), high=float(high))
            metadata[name].append(item)
        if sum(item["counts"]["generated"] for item in metadata[name]) != len(eta):
            raise ValueError("Display eta intervals do not partition generated events")
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Parent of six simulation-pt directories")
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("campaign.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pilot", action="store_true", help="Reduce available pilot directories without production-count claim")
    args = parser.parse_args()
    campaign = json.loads(args.config.read_text())
    rng = np.random.default_rng(campaign["analysis"]["bootstrap_seed"])
    samples = []
    cases = (sorted(p for p in args.input.glob("pilot-*-pt*")
                    if (p / "run-report.json").is_file() and
                    "control" not in p.name and "default-materials" not in p.name) if args.pilot else [
        args.input / f"{simulation}-pt{pt:g}"
        for simulation in campaign["simulations"] for pt in campaign["pt_GeV"]])
    for case in cases:
        sample = reduce_case(case, campaign, rng, production=not args.pilot)
        samples.append(sample)
        print(sample["simulation"], sample["pt_GeV"], sample["global"]["counts"], flush=True)
    root = Path(__file__).resolve().parents[3]
    data = {
        "schema_version": 1, "status": "PROTOTYPE", "pilot": args.pilot,
        "configuration": campaign,
        "provenance": {
            "source_revision": subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(),
            "configuration_sha256": sha256(args.config),
            "exporter_sha256": sha256(Path(__file__)),
            "metrics_sha256": sha256(Path(__file__).with_name("metrics.py")),
            "versions": {"numpy": np.__version__, "uproot": uproot.__version__, "awkward": ak.__version__},
        },
        "statistics": "No tail cuts. Perigee parameters at origin. Five-dimensional fitted covariance must be positive-definite for pulls. Width68 is half the central empirical interval. Errors are event-bootstrap standard deviations conditional on the frozen independent Fatras hit-error table; training and detector-model systematics are omitted. Mean SE is sample SD/sqrt(N). Wilson z=1 intervals for fractions.",
        "samples": samples,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(data, indent=2, allow_nan=False) + "\n").encode()
    args.output.write_bytes(gzip.compress(encoded, mtime=0) if args.output.suffix == ".gz" else encoded)


if __name__ == "__main__":
    main()
