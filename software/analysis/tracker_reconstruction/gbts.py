"""nODD geometry adapter for native ACTS GBTS, DES-041 PROTOTYPE.

The graph/seed finder/filter are ACTS355ea684 implementations. This adapter only
provides physical-layer numbering and geometry-derived connections: no ITk table,
truth grouping, response model, or seeding algorithm is substituted. Initial cuts
are study controls, not optimized or accepted performance choices.
"""
from collections import defaultdict
import copy
import csv
import hashlib
import importlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
ACTS_REVISION = "355ea68493b326956756c9386d2fd9eaf9328568"
# Defaults taken from ACTS Core GraphBasedTrackSeeder.hpp/GbtsTrackingFilter.hpp.
# Explicit study overrides open pT to 0.5 GeV (below the 1 GeV target), use the
# origin benchmark's generous +/-15 mm z window and |eta|4.1, and disable cluster
# cuts because Gaussian digitization has no pixel channel/cluster-width data.
DEFAULTS = {
    "input_spacepoints": "spacepoints", "output_seeds": "seeds",
    "b_field_T": 3.0, "eta_range": [-4.1, 4.1], "z0_range_mm": [-15., 15.],
    "eta_bin_width": 0.2, "max_seeds_per_event": 0,
    "seed_finder": {"minPt": 0.5, "minZ0": -15., "maxZ0": 15.,
                    "useClusterWidthCuts": False, "useStripConnections": False},
    "tracking_filter": {"maxZ0": 15.},
}
SEED_FIELDS = set("beamSpotCorrection useStripConnections useClusterWidthCuts matchBeforeCreate validateTriplets useAdaptiveCuts addTriplets tauRatioCut tauRatioPrecut tauRatioCorr tauRatioCorrStrip maxAbsEtaAddTriplets nMaxPhiSlice minPt tripletPtFraction useEtaBinning doubletFilterRZ nMaxEdges minDeltaRadius maxAbsTau d0Max cutDPhiMax cutDCurvMax minZ0 maxZ0 tuningPt maxCurvatureHighEta maxCurvatureLowEta curvatureSplitAbsTau phiWindowSplitDeltaRadius phiWindowNearOffset phiWindowNearSlope phiWindowFarOffset phiWindowFarSlope matchBeforeCreateMaxEdges z0HistogramMaxBarrelOrder matchBeforeCreateMaxBarrelOrder z0Resolution maxOuterRadius calibrateStrips maxStripLengthFraction ccaMaxIterations minSeedLevel minSplitSeedSize maxSplitSeedSize edgeMaskMinEta hitShareThreshold maxSeedSplitEta maxInvRadDiff maxEndcapClusterWidth moduleHalfLengthY moduleEdgeTolerance tauLutBinWidth phiIndexMargin phiSortBuckets".split())
FILTER_FIELDS = set("sigmaMS radLen sigmaX sigmaY sigmaXStrip weightX weightY maxDChi2X maxDChi2Y addHit maxCurvature maxZ0 initialVarianceX initialVarianceY".split())


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def configuration(settings=None):
    settings = copy.deepcopy(settings or {})
    # This path only locates the sidecar; it cannot change the reconstruction.
    settings.pop("native_module_dir", None)
    unknown = set(settings) - set(DEFAULTS)
    if unknown:
        raise ValueError(f"Unknown GBTS settings: {sorted(unknown)}")
    result = copy.deepcopy(DEFAULTS)
    for key, value in settings.items():
        if key in ("seed_finder", "tracking_filter"):
            allowed = SEED_FIELDS if key == "seed_finder" else FILTER_FIELDS
            if set(value) - allowed:
                raise ValueError(f"Unknown {key} fields: {sorted(set(value)-allowed)}")
            result[key].update(value)
        else:
            result[key] = value
    if result["seed_finder"].get("useClusterWidthCuts") or result["seed_finder"].get("useStripConnections"):
        raise ValueError("Gaussian pixel GBTS requires cluster-width and strip-connection cuts disabled")
    for key in ("eta_range", "z0_range_mm"):
        interval = result[key]
        if len(interval) != 2 or not all(math.isfinite(v) for v in interval) or interval[0] >= interval[1]:
            raise ValueError(f"Invalid {key}")
    if not math.isfinite(result["b_field_T"]) or result["b_field_T"] == 0:
        raise ValueError("Require finite nonzero longitudinal field")
    if not 0 < result["eta_bin_width"] <= 1:
        raise ValueError("Require positive eta bin width <=1")
    if type(result["max_seeds_per_event"]) is not int or result["max_seeds_per_event"] < 0:
        raise ValueError("Seed cap is nonnegative integer; zero means unlimited")
    if result["seed_finder"]["minPt"] <= 0:
        raise ValueError("Require positive minPt in GeV")
    if (result["seed_finder"]["minZ0"], result["seed_finder"]["maxZ0"]) != tuple(result["z0_range_mm"]):
        raise ValueError("Graph z0 cuts and geometry/ROI z0 range must agree")
    _canonical(result)  # Reject NaN/Inf before writing/native initialization.
    return result


def _extent(sensor):
    center, u, v = (sensor[k] for k in ("center_mm", "u", "v"))
    a, b = (sensor["size_mm"][i] / 2 for i in (0, 1))
    corners = [[center[i] + x*a*u[i] + y*b*v[i] for i in range(3)]
               for x, y in ((-1,-1), (1,-1), (1,1), (-1,1))]
    radii = [math.hypot(*p[:2]) for p in corners]
    # The closest point on a rectangular boundary may lie inside an edge.
    for p, q in zip(corners, corners[1:] + corners[:1]):
        delta = [q[i]-p[i] for i in (0,1)]
        norm = sum(d*d for d in delta)
        if norm:
            t = max(0., min(1., -sum(p[i]*delta[i] for i in (0,1))/norm))
            radii.append(math.hypot(*(p[i]+t*delta[i] for i in (0,1))))
    return min(radii), max(radii), min(p[2] for p in corners), max(p[2] for p in corners)


def prepare(report, outdir, settings=None):
    """Write exact Gen3 sensor mapping, physical-layer bounds and broad DAG.

    The 176 possible links connect every radially ordered barrel pair, every
    |z|-ordered same-endcap pair and barrel to each disk. Native GbtsGeometry
    prunes incompatible eta-bin pairs. Endcap station ordering uses geometry,
    including stable logical disk10 between2 and3. No training sample is used.
    """
    config = configuration(settings)
    sensors = report["sensors"]
    unique = {s["geometry_id"] for s in sensors}
    if len(unique) != len(sensors):
        raise ValueError("Duplicate native sensitive geometry identity")
    groups = defaultdict(list)
    for sensor in sorted(sensors,key=lambda s:s["geometry_id"]):
        ids = sensor["ids"]
        if ids["system"] in (1,2,3):
            groups[ids["system"],ids["layer"]].append(sensor)
    required = {(1,l) for l in range(1,5)} | {(s,l) for s in (2,3) for l in range(1,11)}
    if set(groups) != required or sum(map(len, groups.values())) != 12410:
        raise ValueError("Expected current balanced nODD 12410 pixel sensors on24 physical layers")
    if len(sensors) != 46250:
        raise ValueError("Expected complete current balanced Gen3 report,46250 sensors")
    layers, mapping = [], []
    for (system, layer), items in sorted(groups.items()):
        extents = [_extent(s) for s in items]
        rmin, rmax = min(e[0] for e in extents), max(e[1] for e in extents)
        zmin, zmax = min(e[2] for e in extents), max(e[3] for e in extents)
        reference = sum(math.hypot(*s["center_mm"][:2]) if system==1 else s["center_mm"][2] for s in items)/len(items)
        item = {"id": system*100+layer, "system": system, "physical_layer": layer,
                "type": "barrel" if system==1 else "endcap", "ref_coord_mm": reference,
                "min_bound_mm": zmin if system==1 else rmin,
                "max_bound_mm": zmax if system==1 else rmax,
                "thickness_mm": rmax-rmin if system==1 else zmax-zmin,
                "sensor_count": len(items), "r_extent_mm": [rmin,rmax], "z_extent_mm": [zmin,zmax]}
        layers.append(item)
        mapping.extend((s["geometry_id"],item["id"]) for s in items)
    barrel = sorted((l for l in layers if l["system"]==1), key=lambda l:l["ref_coord_mm"])
    endcaps = {s:sorted((l for l in layers if l["system"]==s),key=lambda l:abs(l["ref_coord_mm"])) for s in (2,3)}
    if any(min(abs(z) for z in d["z_extent_mm"]) <= max(abs(z) for b in barrel for z in b["z_extent_mm"]) for ds in endcaps.values() for d in ds):
        raise ValueError("This broad connection topology requires disks axially outside the barrel")
    links = []
    for ordered in [barrel,*endcaps.values()]:
        links.extend((outer["id"],inner["id"]) for i,inner in enumerate(ordered) for outer in ordered[i+1:])
    links.extend((disk["id"],b["id"]) for disks in endcaps.values() for disk in disks for b in barrel)
    links = sorted(set(links))
    outdir = Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    (outdir/"config.json").write_text(json.dumps(config,indent=2,sort_keys=True,allow_nan=False)+"\n")
    with (outdir/"mapping.csv").open("w",newline="") as stream:
        csv.writer(stream,lineterminator="\n").writerows(sorted(mapping))
    with (outdir/"layers.csv").open("w",newline="") as stream:
        csv.writer(stream,lineterminator="\n").writerows((l["id"],0 if l["type"]=="barrel" else 1,l["ref_coord_mm"],l["thickness_mm"],l["min_bound_mm"],l["max_bound_mm"]) for l in layers)
    with (outdir/"connections.csv").open("w",newline="") as stream:
        csv.writer(stream,lineterminator="\n").writerows(links)
    audit = {"schema_version":1,"status":"PROTOTYPE","acts_source_revision":ACTS_REVISION,
             "algorithm":"ACTS Core GraphBasedTrackSeeder + GbtsGeometry + GbtsTrackingFilter",
             "pixel_sensors":len(mapping),"pixel_layers":len(layers),"connections":len(links),
             "geometry_sensor_fingerprint":hashlib.sha256(_canonical(sorted(sensors,key=lambda s:s["geometry_id"]))).hexdigest(),
             "layers":layers,"physical_disk_order":{str(s):[l["physical_layer"] for l in ds] for s,ds in endcaps.items()},
             "connection_direction":"src outer, dst inner; same-endcap outward |z|, barrel outward r; no cross-endcap links",
             "connection_origin":"Broad geometry-derived topology; no simulated truth input or ITk connection table",
             "configuration":config,"effective_native_units":"mm, GeV; b_field_T converted to native tesla in C++",
             "producer_sha256":sha256(__file__),
             "files":{name:sha256(outdir/name) for name in ("config.json","mapping.csv","layers.csv","connections.csv")}}
    (outdir/"audit.json").write_text(json.dumps(audit,indent=2,sort_keys=True,allow_nan=False)+"\n")
    return audit


def schedule(sequencer, acts, geometry, configDir, settings=None, level=None):
    """Schedule native GBTS from measured space points; return observable algorithm.

    ``geometry`` remains in the stable scheduling interface; the adapter uses the
    explicitly fingerprinted native-report mapping instead of the legacy surface
    map (which is empty on the Gen3 container). All input points must be mapped
    single-source-link pixels; any unmatched point fails loudly.
    """
    del geometry
    configDir = Path(configDir)
    audit = json.loads((configDir/"audit.json").read_text())
    for name,digest in audit["files"].items():
        if sha256(configDir/name) != digest:
            raise ValueError(f"GBTS prepared input changed: {name}")
    if audit["configuration"] != configuration(settings):
        raise ValueError("Scheduled GBTS settings differ from prepared/fingerprinted configuration")
    module_dir = Path((settings or {}).get("native_module_dir",ROOT/"build/tracker-reconstruction/native-gbts"))
    sys.path.insert(0,str(module_dir.resolve()))
    native = importlib.import_module("nodd_gbts")
    algorithm = native.GbtsSeeding(str(configDir),acts.logging.INFO if level is None else level)
    sequencer.addAlgorithm(algorithm)
    return algorithm
