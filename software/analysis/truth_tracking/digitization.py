"""Build geometric ACTS digitization for exact native Gen3 sensor identities."""
import math
from collections import Counter


def geometry_fields(identity):
    if type(identity) is not int or not 0 < identity < 2**64:
        raise ValueError("Expected a positive uint64 geometry identity")
    fields = {"volume": (identity >> 56) & 255,
              "boundary": (identity >> 48) & 255,
              "layer": (identity >> 36) & 4095,
              "approach": (identity >> 28) & 255,
              "sensitive": (identity >> 8) & 1048575,
              "extra": identity & 255}
    if not fields["sensitive"]:
        raise ValueError("Digitization identity is not sensitive")
    return {key: value for key, value in fields.items() if value}


def build_config(sensors, settings):
    entries, identities, counts = [], set(), Counter()
    pitches = {1: settings["pixel_pitch_mm"], 2: settings["pixel_pitch_mm"],
               3: settings["pixel_pitch_mm"], 4: settings["short_strip_pitch_mm"],
               5: settings["short_strip_pitch_mm"],
               6: [settings["long_strip_pitch_mm"]],
               7: [settings["long_strip_pitch_mm"]]}
    for sensor in sorted(sensors, key=lambda item: item["geometry_id"]):
        identity, system = sensor["geometry_id"], sensor["ids"]["system"]
        if identity in identities or system not in pitches:
            raise ValueError("Duplicate or unsupported sensitive identity/system")
        identities.add(identity)
        size = sensor["size_mm"]
        if len(size) != 3 or any(not math.isfinite(x) or x <= 0 for x in size):
            raise ValueError("Sensor size must have three positive finite dimensions")
        axes = []
        for index, pitch in enumerate(pitches[system]):
            if not math.isfinite(pitch) or pitch <= 0:
                raise ValueError("Pitch must be positive and finite")
            # Preserve the requested pitch exactly. Centre a grid encompassing
            # the sensor; native geometric stepping clips charge at its bounds.
            bins = math.ceil(size[index] / pitch - 1e-10)
            half = bins * pitch / 2
            axes.append({"bins": bins, "min": -half, "max": half,
                         "option": "open", "type": "equidistant",
                         "value": "binX" if index == 0 else "binY"})
        # Native channelization/clustering requires a two-dimensional cell
        # footprint even for a single measured strip coordinate. One full-length
        # v bin encodes the physical strip extent, without a v measurement.
        if len(axes) == 1:
            axes.append({"bins": 1, "min": -size[1]/2, "max": size[1]/2,
                         "option": "open", "type": "equidistant", "value": "binY"})
        geometric = {"indices": list(range(len(pitches[system]))),
                     "segmentation": {"binningdata": axes},
                     "thickness": size[2], "threshold": settings["threshold"],
                     "digital": settings["digital"],
                     "charge-smearing": {"type": "Exact", "stddev": 0.0}}
        entries.append({**geometry_fields(identity), "value": {"geometric": geometric}})
        counts[str(system)] += 1
    if set(counts) != set(map(str, range(1, 8))):
        raise ValueError("Require complete native tracker systems 1–7")
    return {"acts-geometry-hierarchy-map": {"format-version": 0,
                "value-identifier": "digitization-configuration"}, "entries": entries}, dict(counts)


def apply_variance_table(config, table):
    """Apply native cluster-size RMS vectors to each exact sensor entry."""
    header=table.get("acts-geometry-hierarchy-map",{})
    if header.get("format-version") != 0 or header.get("value-identifier") != "hit-error-parametrisation":
        raise ValueError("Expected native ACTS hit-error-parametrisation table")
    values={}
    for entry in table.get("entries",[]):
        volume=entry.get("volume")
        if type(volume) is not int or volume in values or volume<=0:
            raise ValueError("Error-table volumes must be positive and unique")
        variances=entry.get("value")
        if not isinstance(variances,list) or not variances:
            raise ValueError("Empty error-table coordinate data")
        indices=set()
        for value in variances:
            index=value.get("index");rms=value.get("rms")
            if index not in (0,1) or index in indices or not isinstance(rms,list) or not rms or any(
                    type(x) not in (int,float) or not math.isfinite(x) or x<=0 for x in rms):
                raise ValueError("RMS vectors must be positive finite and uniquely indexed")
            indices.add(index)
        values[volume]=variances
    expected={entry["volume"] for entry in config["entries"]}
    if set(values) != expected:
        raise ValueError("Error-table volume identities differ from native sensitive inventory")
    for entry in config["entries"]:
        geometric=entry["value"]["geometric"]
        variances=values[entry["volume"]]
        if {value["index"] for value in variances} != set(geometric["indices"]):
            raise ValueError("Error-table measured coordinates differ from sensor contract")
        geometric["variances"]=variances
    return config
