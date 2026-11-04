"""Native Gaussian digitization controls for the isolated PR101 cross-check."""
from collections import Counter
import json
import math
from pathlib import Path

from digitization import geometry_fields


COORDINATES = {str(i): ([0, 1] if i < 6 else [0]) for i in range(1, 8)}


def native_boundary_contract(acts):
    # ACTS355ea684 DigitizationAlgorithm.hpp:86. Some bindings omit this field;
    # retain the verified C++ default explicitly rather than reporting zero.
    exposed = getattr(acts.examples.DigitizationAlgorithm.Config(), "minMaxRetries", None)
    minimum = 10 if exposed is None else int(exposed)
    return {"configured_smearer_max_retries": 0, "algorithm_min_max_retries": minimum,
            "effective_max_retries": max(minimum, 0), "maximum_draw_attempts": max(minimum, 0) + 1,
            "retry_evidence": "Pinned ACTS355ea684 C++ default; field unavailable in Python binding" if exposed is None else "Native Python Config.minMaxRetries",
            "boundary": "Outside-sensitive-bounds draws retried up to effective limit; exhausted attempts discard measurement"}


def load_campaign(path):
    config = json.loads(Path(path).read_text())
    if config.get("schema_version") != 1 or config.get("status") != "PROTOTYPE":
        raise ValueError("Expected prototype smearing campaign schema1")
    if (config.get("simulations") != ["fatras"] or config.get("particles_per_event") != 1
            or config.get("vertex_mm") != [0., 0., 0.] or config.get("randomize_charge") is not True):
        raise ValueError("Require Fatras and one randomized-charge origin muon")
    if not math.isfinite(config["field_Bz_T"]) or config["field_Bz_T"] == 0:
        raise ValueError("Require finite nonzero constant field")
    for key in ("eta_range", "phi_range_rad"):
        bounds = config[key]
        if len(bounds) != 2 or not all(math.isfinite(x) for x in bounds) or bounds[0] >= bounds[1]:
            raise ValueError("Invalid generator bounds")
    digi = config["digitization"]
    if (digi.get("model") != "gaussian_smearing" or digi.get("merge") is not False
            or digi.get("measured_coordinates_by_system") != COORDINATES):
        raise ValueError("Require unmerged Gaussian response with native coordinate dimensions")
    if config["truth_tracking"].get("particle_hypothesis") != "muon":
        raise ValueError("Require native muon fitter hypothesis")
    return config


def width_groups(table):
    if (table.get("schema_version") != 1 or table.get("status") != "PROTOTYPE"
            or not table.get("width_convention")):
        raise ValueError("Expected prototype pooled-width schema1 and convention")
    groups = {}
    for item in table.get("groups", []):
        volume, index = item.get("volume"), item.get("index")
        if (type(volume) is not int or not 0 < volume < 256 or type(index) is not int
                or index not in (0, 1) or (volume, index) in groups):
            raise ValueError("Widths require unique positive ACTS volume/coordinate identities")
        if (type(item.get("entries")) is not int or item["entries"] <= 0
                or item.get("sensor_family") not in ("pixel", "short_strip", "long_strip")):
            raise ValueError("Widths require training entries and sensor family")
        for name in ("mean_mm", "sigma_mm", "uncentered_rms_mm"):
            value = item.get(name)
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError("Width moments must be finite")
        if item["sigma_mm"] <= 0 or item["uncentered_rms_mm"] <= 0:
            raise ValueError("Gaussian sigma must be positive")
        groups[volume, index] = item
    if not groups:
        raise ValueError("No pooled widths")
    return groups


def build_config(sensors, settings, table):
    if (settings.get("model") != "gaussian_smearing" or settings.get("merge") is not False
            or settings.get("measured_coordinates_by_system") != COORDINATES):
        raise ValueError("Unsupported Gaussian coordinate/merge contract")
    groups = width_groups(table)
    identities, expected, entries, counts = set(), set(), [], Counter()
    for sensor in sorted(sensors, key=lambda item: item["geometry_id"]):
        identity, system = sensor["geometry_id"], sensor["ids"]["system"]
        if identity in identities or type(system) is not int or str(system) not in COORDINATES:
            raise ValueError("Duplicate or unsupported sensitive identity/system")
        identities.add(identity)
        fields = geometry_fields(identity)
        volume = fields["volume"]
        family = "pixel" if system < 4 else "short_strip" if system < 6 else "long_strip"
        smearers = []
        for index in COORDINATES[str(system)]:
            key = volume, index
            expected.add(key)
            if key not in groups or groups[key]["sensor_family"] != family:
                raise ValueError("Pooled widths differ from native sensor coordinates/family")
            smearers.append({"index": index, "type": "Gauss", "mean": 0.,
                             "stddev": groups[key]["sigma_mm"], "forcePositiveValues": False})
        entries.append({**fields, "value": {"smearing": smearers}})
        counts[str(system)] += 1
    if set(counts) != set(COORDINATES):
        raise ValueError("Require complete native tracker systems 1–7")
    if expected != set(groups):
        raise ValueError("Pooled width identities differ from native measured volume/coordinates")
    return {"acts-geometry-hierarchy-map": {"format-version": 0,
            "value-identifier": "digitization-configuration"}, "entries": entries}, dict(counts)


def schedule_digitization(sequencer, acts, geometry, rnd, path, observer, level):
    from acts.examples import json as acts_json
    algorithm = acts.examples.DigitizationAlgorithm(
        acts.examples.DigitizationAlgorithm.Config(
            digitizationConfigs=acts_json.readDigiConfigFromJson(str(path)),
            surfaceByIdentifier=geometry.geoIdSurfaceMap(), randomNumbers=rnd,
            inputSimHits="simhits", outputMeasurements="measurements",
            outputMeasurementParticlesMap="measurement_particles_map_raw",
            outputMeasurementSimHitsMap="measurement_simhits_map",
            outputParticleMeasurementsMap="particle_measurements_map_raw",
            outputSimHitMeasurementsMap="simhit_measurements_map",
            doMerge=False, mergeCommonCorner=False, minEnergyDeposit=0.), level)
    sequencer.addAlgorithm(algorithm)
    sequencer.addAlgorithm(observer.UniqueAssociations())


def audit_measurements(ROOT, path, table):
    """Check every written marginal and retain uncut Gaussian residual moments.

    The writer stores float32 positions/variances. Residuals recomputed here use
    those persisted positions, so their rounding is included in diagnostics.
    Native BoundParametersSmearer rejects draws outside the sensitive bounds.
    """
    import numpy as np
    groups = width_groups(table)
    names = ["volume_id", "rec_loc0", "rec_loc1", "true_loc0", "true_loc1",
             "var_loc0", "var_loc1", "clus_size"]
    arrays = ROOT.RDataFrame("measurements", str(path)).AsNumpy(names)
    result = []
    for volume in sorted(set(int(x) for x in arrays["volume_id"])):
        mask = arrays["volume_id"] == volume
        for index in (0, 1):
            rec, truth, var = (arrays[f"{kind}_loc{index}"][mask] for kind in ("rec", "true", "var"))
            item = groups.get((volume, index))
            if item is None:
                if np.any(np.isfinite(rec)) or np.any(np.isfinite(var)):
                    raise RuntimeError("Native output introduced an unmeasured coordinate")
                continue
            if not np.all(np.isfinite(rec)) or not np.all(np.isfinite(truth)):
                raise RuntimeError("Native measurement/truth coordinate is nonfinite")
            expected = np.float32(item["sigma_mm"] ** 2)
            if not np.all(var == expected):
                raise RuntimeError("Native measurement variance differs from Gaussian sigma squared")
            z = (rec.astype(float) - truth.astype(float)) / item["sigma_mm"]
            result.append({"volume": volume, "index": index, "entries": len(z),
                "mean": float(z.mean()), "population_sd": float(z.std()),
                "rms": float(np.sqrt(np.mean(z*z))), "minimum": float(z.min()),
                "maximum": float(z.max()), "abs_gt3": int(np.sum(np.abs(z) > 3)),
                "abs_gt5": int(np.sum(np.abs(z) > 5)), "abs_gt10": int(np.sum(np.abs(z) > 10)),
                "max_absolute_variance_difference": float(np.max(np.abs(var.astype(float) - float(expected))))})
    if np.any(arrays["clus_size"] != 0):
        raise RuntimeError("Smearing-only writer unexpectedly contains geometric channels")
    return {"measurement_rows": len(arrays["volume_id"]), "coordinate_rows": sum(x["entries"] for x in result),
        "variance_matches_float32_sigma_squared": True, "groups": result,
        "unobserved_width_groups": [list(key) for key in sorted(set(groups) - {(x["volume"], x["index"]) for x in result})],
        "residual_convention": "(persisted float32 reconstructed minus truth local coordinate) / frozen sigma",
        "native_boundary_behavior": "See effective run-level retry contract; outside-sensitive-bounds attempts can be redrawn, exhaustion discards measurement",
        "cluster_writer_contract": "inputClusters empty; cluster/channel fields remain empty or zero"}
