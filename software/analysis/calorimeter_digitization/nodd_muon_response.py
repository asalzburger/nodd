#!/usr/bin/env python3
"""Geometry-aware held-out muon characterization for the frozen nODD study.

Cell maps, event payloads and native-ray intersections are local ignored evidence.
Missing primary deposits are unknown transported crossings. Nominal opportunity
yields and conditional identified-crossing efficiencies are reported separately.
"""
from collections import Counter, defaultdict
import hashlib
import importlib
import json
import math
from pathlib import Path

import numpy as np

MIP = .00014875
STAGES = ("raw", "off", "on")
THRESHOLDS = np.array([0, .2, .4, .6, .8, 1., 1.2, 1.5, 2.])
REPLICATES = 1000
HELPERS = {"muon_response": "42145336e7f01adae2175d5d2fedf406d6a25674d678328f36b60a4cd1f240db",
           "digitized_response": "c76c5698d6acf713566343b7b4711d2d06c3dbb781862328cc938510f14f0552"}
SEEDS = {("nodd", 0): 126100, ("nodd", 2): 126101,
         ("odd-zero", 0): 126102, ("odd-zero", 2): 126103,
         ("nodd", -2): 126104, ("odd-zero", -2): 126105}
LOADED_SOURCE = Path(__file__).read_bytes()


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def helpers():
    result = {}
    for name, expected in HELPERS.items():
        module = importlib.import_module(name)
        if sha(module.__file__) != expected:
            raise ValueError("Pinned muon analysis helper changed: " + name)
        result[name] = module
    return result["muon_response"], result["digitized_response"]


class Descriptor:
    """DD4hep bitfield strings, including explicit offsets and signed widths."""
    def __init__(self, text):
        self.text, self.fields = text, {}
        offset, mask = 0, 0
        for token in text.split(","):
            pieces = token.strip().split(":")
            if len(pieces) not in (2, 3):
                raise ValueError("Invalid descriptor field")
            name = pieces[0]
            start = offset if len(pieces) == 2 else int(pieces[1])
            width = int(pieces[-1]); bits = abs(width)
            if not bits or start < 0 or start + bits > 64 or name in self.fields:
                raise ValueError("Invalid descriptor extent/name")
            fieldmask = ((1 << bits) - 1) << start
            if fieldmask & mask:
                raise ValueError("Overlapping descriptor fields")
            self.fields[name] = (start, bits, width < 0)
            mask |= fieldmask; offset = start + bits
        self.mask = mask

    def decode(self, cid):
        if not 0 <= cid < 1 << 64 or cid & ~self.mask:
            raise ValueError("CellID outside descriptor")
        result = {}
        for name, (start, bits, signed) in self.fields.items():
            value = (cid >> start) & ((1 << bits) - 1)
            result[name] = value - (1 << bits) if signed and value & (1 << (bits - 1)) else value
        return result


def collection_roles(geometry):
    if geometry == "nodd":
        return {"BARRELHits": "barrel", "EDGEHits": "endcap"}
    if geometry == "odd-zero":
        return {"ECalBarrelCollection": "barrel", "ECalEndcapCollection": "endcap"}
    raise ValueError("Unknown geometry")


def plane_key(geometry, collection, fields):
    roles = collection_roles(geometry)
    side = fields["side" if geometry == "nodd" else "barrel"]
    sector = fields["sector" if geometry == "nodd" else "module"]
    layer = fields["layer"]
    if side not in ((0,) if roles[collection] == "barrel" else (1, 2)):
        raise ValueError("Collection and side disagree")
    if not (0 <= layer < 48 if geometry == "nodd" else 1 <= layer <= 48):
        raise ValueError("Unexpected physical layer ID")
    if not 0 <= sector < 16:
        raise ValueError("Unexpected sector ID")
    return (collection, side, sector, layer)


def key_text(key):
    return ":".join(map(str, key))


def encode_physical_ids(id_spec, descriptor, physical_ids, ROOT):
    """Use the actual native readout encoder before interpreting physical IDs.

    ODD's pinned factory numbers modules 1..16, while its four-bit field encodes
    physical module 16 as zero. Do not emulate this with range relaxation or
    hand masking: preserve all physical and decoded fields for the crosswalk.
    """
    ids = ROOT.std.vector("pair<string,int>")()
    for name, value in sorted(physical_ids.items()):
        if name not in descriptor.fields:
            raise ValueError("Physical ID absent from actual readout descriptor: " + name)
        ids.emplace_back(name, int(value))
    encoded = int(id_spec.encode(ids))
    decoded = descriptor.decode(encoded)
    native_decoder = id_spec.decoder()
    if any(value != int(native_decoder.get(encoded, name)) for name, value in decoded.items()):
        raise ValueError("Native and independent descriptor decoding disagree")
    return encoded, decoded


def register_physical_plane(geometry, collection, physical_ids, id_spec, descriptor, ROOT, crosswalk):
    encoded, decoded = encode_physical_ids(id_spec, descriptor, physical_ids, ROOT)
    key = plane_key(geometry, collection, decoded)
    if key in crosswalk:
        raise ValueError("Physical-to-encoded plane collision")
    crosswalk[key] = dict(physical_ids=dict(physical_ids), encoded_volume_id=encoded,
                         decoded_fields=decoded, plane=list(key))
    return key


def physical_neighbors(key, inventory):
    """Use constructed planes, never the next observed primary deposit."""
    siblings = sorted(k for k in inventory if k[:3] == key[:3])
    if key not in siblings:
        raise ValueError("Observed plane absent from native inventory")
    i = siblings.index(key)
    return (siblings[i-1] if i else None, siblings[i+1] if i+1 < len(siblings) else None)


def thin_axis(half_extents_mm):
    extents = np.asarray(half_extents_mm, float)
    candidates = np.flatnonzero(np.isclose(extents, .25, rtol=0, atol=1e-7))
    if extents.shape != (3,) or len(candidates) != 1 or np.any(extents <= 0):
        raise ValueError("Actual solid has no unique 0.5-mm thin axis")
    return int(candidates[0])


def solid_axis(shape, mm):
    # TGeoTrd2's DY bounding box is max(Dy1,Dy2); require both faces thin.
    dimensions = [float(shape.GetDX()) / mm, float(shape.GetDY()) / mm, float(shape.GetDZ()) / mm]
    axis = thin_axis(dimensions)
    if axis == 1 and hasattr(shape, "GetDy1"):
        if any(abs(float(getattr(shape, method)()) / mm - .25) > 1e-7 for method in ("GetDy1", "GetDy2")):
            raise ValueError("Trapezoid thickness changes across sensor")
    return axis


def silicon_name(name):
    return name == "Silicon" or name.endswith("_Silicon")


def source_identity(args, manifest, samples):
    for path, expected in manifest["immutable"].items():
        if sha(path) != expected:
            raise ValueError("Transport immutable dependency changed: " + path)
    if samples["manifest_sha256"] != sha(args.transport_manifest):
        raise ValueError("Raw sample/transport manifest identity changed")
    for receipt in samples.get("receipts", []):
        if sha(receipt["path"]) != receipt["sha256"]:
            raise ValueError("Raw transport receipt changed")
    selected = [s for s in samples["samples"] if s["geometry"] == args.geometry and s["kind"] == "muons"]
    if {s["eta"] for s in selected} != {0, 2, -2} or len(selected) != 3:
        raise ValueError("Expected three held-out muon populations per geometry")
    for sample in selected:
        if sample["exit_code"] or sample["requested_events"] <= 0 or sha(sample["path"]) != sample["sha256"]:
            raise ValueError("Muon raw input failed/changed")
    geom = manifest["geometries"][args.geometry]
    return dict(transport_manifest_sha256=sha(args.transport_manifest), samples_sha256=sha(args.samples),
                compact_sha256=sha(geom["compact"]), libraries={p: sha(p) for p in geom["libraries"]},
                inputs={s["path"]: s["sha256"] for s in selected},
                source_sha256=hashlib.sha256(LOADED_SOURCE).hexdigest(), helper_sha256=HELPERS), selected


def populated_volume_manager(detector, dd4hep):
    # DD4hep 1.38 VolumeManager.h specifies that this accessor invokes the
    # DD4hepVolumeManager plugin when necessary. Detector.volumeManager() alone
    # only retrieves the handle; composed roots need not contain that plugin.
    manager = dd4hep.VolumeManager.getVolumeManager(detector)
    if not manager.isValid():
        raise RuntimeError("Native DD4hep VolumeManager population failed")
    return manager


def geometry(args):
    """Run in a separate native process for each geometry after raw files exist."""
    import ROOT
    import dd4hep
    from podio import root_io
    helpers()
    args.work = Path(args.work).resolve(); args.work.mkdir(parents=True, exist_ok=True)
    public_path = args.work / f"muon-geometry-{args.geometry}.json"
    cache_path = args.work / f"muon-geometry-{args.geometry}-cells.json"
    if public_path.exists() or cache_path.exists():
        raise ValueError("Choose fresh muon geometry work path; evidence already exists")
    manifest = json.loads(Path(args.transport_manifest).read_text())
    samples = json.loads(Path(args.samples).read_text())
    identity, selected = source_identity(args, manifest, samples)
    geom = manifest["geometries"][args.geometry]
    ROOT.DisableImplicitMT(); ROOT.gROOT.SetBatch(True)
    for library in geom["libraries"]:
        if ROOT.gSystem.Load(library) < 0:
            raise RuntimeError("Cannot load native factory: " + library)
    detector = dd4hep.Detector.getInstance()
    try:
        detector.fromXML(geom["compact"])
        manager = detector.manager(); mm = float(dd4hep.mm)
        volume_manager = populated_volume_manager(detector, dd4hep)
        roles = collection_roles(args.geometry)
        id_specs = {c: detector.readout(c).idSpec() for c in roles}
        descriptors = {c: Descriptor(str(id_specs[c].fieldDescription())) for c in roles}
        # Match readouts to actual root IDs, rather than a legacy ODD bit mask.
        names = {"BARRELHits": "BARREL", "EDGEHits": "EDGE", "ECalBarrelCollection": "ECalBarrel", "ECalEndcapCollection": "ECalEndcap"}
        systems = {int(detector.detector(names[c]).id()): c for c in roles}
        inventory = set(); physical_crosswalk = {}; sensitive_memo = {}; inspected = 0

        def sensitive(volume):
            nonlocal inspected
            address = int(ROOT.addressof(volume))
            if address not in sensitive_memo:
                inspected += 1
                own = bool(dd4hep.Volume(volume).isSensitive())
                sensitive_memo[address] = own or any(sensitive(volume.GetNode(i).GetVolume()) for i in range(volume.GetNdaughters()))
            return sensitive_memo[address]

        def walk(node, inherited):
            ids = dict(inherited)
            ids.update({str(p.first): int(p.second) for p in dd4hep.PlacedVolume(node).volIDs()})
            volume = node.GetVolume()
            if not sensitive(volume):
                return
            collection = systems.get(ids.get("system"))
            required = ("side", "sector", "layer") if args.geometry == "nodd" else ("barrel", "module", "layer")
            if collection and all(k in ids for k in required):
                key = register_physical_plane(args.geometry, collection, ids, id_specs[collection],
                                              descriptors[collection], ROOT, physical_crosswalk)
                inventory.add(key)
                return
            for i in range(volume.GetNdaughters()):
                walk(volume.GetNode(i), ids)

        top = manager.GetTopVolume()
        for i in range(top.GetNdaughters()):
            walk(top.GetNode(i), {})
        if {k[1] for k in inventory} != {0, 1, 2}:
            raise ValueError("Constructed inventory does not cover barrel/both endcaps")
        groups = {}; cells = {}; queries = 0; max_residual = 0.
        for key in sorted(inventory):
            group = groups.setdefault(key_text(key[:3]), dict(region=roles[key[0]], side=key[1], sector=key[2], layers=[],
                                    queries=0, unique_cells=0, maximum_reference_residual_mm=0., materials=[], normals=[], thickness_mm=[]))
            group["layers"].append(key[3])
        ray_results = []
        for sample in selected:
            frames = root_io.Reader(sample["path"]).get("events")
            if len(frames) != sample["requested_events"]:
                raise ValueError("Native muon geometry event count differs")
            ray_truth = None
            for frame in frames:
                primary = [p for p in frame.get("MCParticles") if p.getGeneratorStatus() == 1]
                if len(primary) != 1 or int(primary[0].getPDG()) != 13:
                    raise ValueError("Expected detailed primary muon")
                p = primary[0].getMomentum(); v = primary[0].getVertex()
                truth = np.array([p.x, p.y, p.z], float); truth /= np.linalg.norm(truth)
                this_truth = (tuple([v.x, v.y, v.z]), tuple(truth))
                if ray_truth is None:
                    ray_truth = this_truth
                elif not np.allclose(np.array(this_truth), np.array(ray_truth), rtol=0, atol=1e-10):
                    raise ValueError("Initial ray varies within fixed-gun population")
                for collection in roles:
                    for hit in frame.get(collection):
                        cid = int(hit.getCellID()); fields = descriptors[collection].decode(cid)
                        if systems.get(fields["system"]) != collection:
                            raise ValueError("Observed native root/collection mismatch")
                        key = plane_key(args.geometry, collection, fields)
                        if key not in inventory:
                            raise ValueError("Observed hit outside constructed plane inventory")
                        tag = f"{collection}:{cid}"; point = hit.getPosition()
                        if tag not in cells:
                            context = volume_manager.lookupContext(cid)
                            volume = context.volumePlacement().volume()
                            material = str(volume.material().name())
                            if not volume.isSensitive() or not silicon_name(material):
                                raise ValueError("CellID does not resolve to sensitive silicon")
                            axis = solid_axis(volume.solid().ptr(), mm)
                            origin = context.localToWorld(dd4hep.Position(0, 0, 0))
                            basis = [0., 0., 0.]; basis[axis] = 1.
                            endpoint = context.localToWorld(dd4hep.Position(*basis))
                            normal = np.array([endpoint.x()-origin.x(), endpoint.y()-origin.y(), endpoint.z()-origin.z()])
                            normal /= np.linalg.norm(normal)
                            reference = context.localToWorld(detector.readout(collection).segmentation().position(cid))
                            reference = np.array([reference.x(), reference.y(), reference.z()]) / mm
                            cells[tag] = dict(plane=list(key), normal=normal.tolist(), thickness_mm=.5, thin_axis=axis,
                                              material=material, reference_mm=reference.tolist())
                            group = groups[key_text(key[:3])]; group["unique_cells"] += 1
                            if material not in group["materials"]: group["materials"].append(material)
                            if .5 not in group["thickness_mm"]: group["thickness_mm"].append(.5)
                            if not any(np.linalg.norm(normal-np.asarray(n)) < 1e-9 for n in group["normals"]):
                                group["normals"].append(normal.tolist())
                        info = cells[tag]
                        residual = float(np.max(np.abs(np.array([point.x, point.y, point.z])-info["reference_mm"])))
                        if residual > .002:
                            raise ValueError("Persisted hit reference differs from actual native segmentation")
                        queries += 1; max_residual = max(max_residual, residual)
                        group = groups[key_text(key[:3])]; group["queries"] += 1
                        group["maximum_reference_residual_mm"] = max(group["maximum_reference_residual_mm"], residual)
            ray_results.append(native_ray(manager, dd4hep, systems, args.geometry, ray_truth, sample["eta"], inventory,
                                          id_specs, descriptors, ROOT))
        cache = dict(identity=identity, cells=cells, inventory=[list(k) for k in sorted(inventory)], initial_rays=ray_results,
                     physical_to_encoded=[physical_crosswalk[k] for k in sorted(physical_crosswalk)])
        write(cache_path, cache)
        # Public output deliberately omits per-cell IDs and per-event histories.
        public = dict(identity=identity, geometry=args.geometry, ROOT=ROOT.gROOT.GetVersion(),
                      descriptors={c: d.text for c, d in descriptors.items()},
                      query_method="Actual native DD4hep VolumeManager sensitive-volume lookup; actual solid thin axis and transformed basis; segmentation reference closure",
                      volume_manager_initialization="VolumeManager.getVolumeManager(detector); DD4hep invokes population plugin when absent; valid handle required",
                      unique_logical_volumes_inspected=inspected, constructed_plane_groups=len(inventory),
                      physical_encoding_audit=dict(encoder="Actual readout IDDescriptor.encode(vector<pair<string,int>>); native decoder cross-checked",
                          physical_plane_groups=len(physical_crosswalk), encoded_plane_collisions=0,
                          changed_physical_fields=dict(Counter(name for row in physical_crosswalk.values()
                              for name, value in row["physical_ids"].items() if row["decoded_fields"][name] != value)),
                          crosswalk_storage="Full physical IDs, encoded volume IDs and all decoded fields retained in hashed local geometry cache"),
                      groups=list(groups.values()), cell_reference_queries=queries, unique_cells=len(cells),
                      maximum_reference_residual_mm=max_residual, position_tolerance_mm=.002,
                      local_cache_sha256=sha(cache_path),
                      initial_ray_approximation=[{k: v for k, v in r.items() if k != "planes"} for r in ray_results],
                      limitations=["Native straight rays use fixed initial momentum and ignore scattering, secondary production and energy loss; they do not certify transported crossings.",
                                   "Only persisted muon cell references were queried; absent primary deposits remain unknown transported crossings.",
                                   "Plane adjacency uses actual constructed sensitive descendants grouped by region/side/sector and ordered layer IDs; no missing observed layer is bridged."])
        write(public_path, public)
        print("Muon native geometry audit", args.geometry, len(inventory), "planes;", queries, "cell references", flush=True)
    finally:
        dd4hep.Detector.destroyInstance()
        if ROOT.gGeoManager:
            ROOT.gGeoManager.Delete()


def native_ray(manager, dd4hep, systems, geometry_name, truth, eta, inventory, id_specs, descriptors, ROOT):
    origin, direction = truth; mm = float(dd4hep.mm)
    manager.InitTrack(*[float(x)*mm for x in origin], *[float(x) for x in direction])
    nav = manager.GetCurrentNavigator(); distance = 0.; steps = 0; paths = defaultdict(float)
    while not nav.IsOutside() and distance < 12000.:
        node = nav.GetCurrentNode()
        if not node: break
        ids = {}
        for ancestor in [nav.GetMother(i) for i in range(nav.GetLevel(), 0, -1)] + [node]:
            ids.update({str(p.first): int(p.second) for p in dd4hep.PlacedVolume(ancestor).volIDs()})
        collection = systems.get(ids.get("system"))
        key = None
        if collection and dd4hep.Volume(node.GetVolume()).isSensitive():
            _, decoded = encode_physical_ids(id_specs[collection], descriptors[collection], ids, ROOT)
            key = plane_key(geometry_name, collection, decoded)
            if key not in inventory:
                raise ValueError("Native ray crossed unlisted sensitive plane")
        nav.FindNextBoundaryAndStep((12000.-distance)*mm)
        length = float(nav.GetStep())/mm
        if not math.isfinite(length) or length <= 0:
            raise RuntimeError("Invalid native initial-ray boundary step")
        if key is not None: paths[key] += length
        distance += length; steps += 1
        if steps > 100000: raise RuntimeError("Native initial ray exceeded boundary limit")
    return dict(eta=eta, origin_mm=list(origin), direction=list(direction), steps=steps, distance_mm=distance,
                crossed_plane_groups=len(paths), active_path_mm=sum(paths.values()),
                crossed_by_region_side=dict(Counter(key_text(k[:2]) for k in paths)),
                planes=[dict(plane=list(k), length_mm=v) for k, v in sorted(paths.items())],
                convention="Native boundary navigation along initial ray only; separate from transported crossing/efficiency denominator")


def basic(values):
    x = np.asarray(values, float); n = len(x)
    if not np.isfinite(x).all(): raise ValueError("Nonfinite descriptive input")
    mean = float(x.mean()) if n else None
    sd = float(x.std(ddof=1)) if n > 1 else None
    return dict(n=n, mean=mean, SD=sd, mean_SE=sd/math.sqrt(n) if sd is not None else None,
                RMS_over_mean=sd/mean if sd is not None and mean else None,
                zero_count=int(np.sum(x == 0)), sums_powers=[float(np.sum(x**k)) for k in range(1, 5)])


def wilson(k, n):
    k = np.asarray(k, float)
    if n == 0: return [None, None]
    z = 1.959963984540054; p = k/n; den = 1+z*z/n
    center = (p+z*z/(2*n))/den; half = z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [np.maximum(0, center-half).tolist(), np.minimum(1, center+half).tolist()]


def crossing_statistics(counts, denominators, indices):
    counts = np.asarray(counts, int); denominators = np.asarray(denominators, int)
    denominator = int(denominators.sum()); total = counts.sum(axis=0)
    bden = denominators[indices].sum(axis=1)
    bootstrap = np.full((len(indices), *total.shape), np.nan)
    np.divide(counts[indices].sum(axis=1), bden[:, None, None], out=bootstrap, where=bden[:, None, None] > 0)
    undefined = int(np.sum(bden == 0)); valid = undefined == 0
    _, response = helpers()
    return dict(accepted_counts=total.tolist(), denominator=denominator,
                efficiency=(total/denominator).tolist() if denominator else None,
                conditional_crossing_Wilson95=wilson(total, denominator),
                event_cluster_bootstrap_undefined_replicates=undefined,
                event_cluster_bootstrap_SE=bootstrap.std(axis=0, ddof=1).tolist() if valid else None,
                event_cluster_bootstrap_CI95=np.quantile(bootstrap, [.025, .975], axis=0).tolist() if valid else None,
                joint_covariance=response.covariance(bootstrap.reshape(len(indices), -1)),
                joint_order="off thresholds ascending, then on thresholds ascending")


def pure_primary_contributions(hit, primary_oid):
    selected = []
    contributions = list(hit.getContributions())
    for contribution in contributions:
        particle = contribution.getParticle()
        if (int(contribution.getPDG()) == 13 and particle.isAvailable()
                and (int(particle.getObjectID().collectionID), int(particle.getObjectID().index)) == primary_oid):
            selected.append(contribution)
    return selected, bool(selected) and len(selected) == len(contributions)


def depth_trials(depths, nominal_layers, signed):
    """One depth trial, even when the primary splits across cells/sectors."""
    counts = {name: np.zeros((2, len(THRESHOLDS)), int)
              for name in ("identified", "identified_single", "identified_split")}
    denominators = Counter(); counters = Counter()
    if set(depths)-set(nominal_layers):
        raise ValueError("Primary depth outside constructed nominal inventory")
    for layer in nominal_layers:
        hits = depths.get(layer, [])
        if not hits:
            counters["missing_primary_layer_unknown_crossing"] += 1
            continue
        counters["identified_primary_layers"] += 1
        category = "identified_single" if len(hits) == 1 else "identified_split"
        counters["identified_single_primary_layers" if len(hits) == 1 else "split_primary_layer"] += 1
        counters["contaminated_identified_layer"] += int(any(not h[2] for h in hits))
        counters["known_zero_identified_primary_signal"] += int(sum(float(c.getEnergy()) for _, cs, _, _ in hits for c in cs) == 0)
        denominators["identified"] += 1; denominators[category] += 1
        for j, mode in enumerate(("off", "on")):
            maximum = max(signed[mode][int(h[0].getCellID())] for h in hits)
            passes = maximum > THRESHOLDS.astype(np.float32)
            counts["identified"][j] += passes; counts[category][j] += passes
    return counts, denominators, counters


def chord_qualification(key, centers, inventory, normal):
    previous, following = physical_neighbors(key, inventory)
    if previous is None or following is None:
        return None, "endpoint"
    if previous not in centers or following not in centers:
        return None, "chord_unavailable"
    chord = np.asarray(centers[following])-np.asarray(centers[previous])
    length = float(np.linalg.norm(chord))
    if not length > 0:
        return None, "chord_unavailable"
    cosine = abs(float((chord/length) @ np.asarray(normal)))
    if cosine < .9:
        return None, "incidence_rejected"
    return cosine, None


def fit_spectra(event_values, selected_values, seed, label, workers):
    fitter, response = helpers(); spectra = {}
    n = len(event_values["raw"]); edges = np.linspace(0, 5, 201)
    # Shared whole-event indices preserve raw/off/on sampling correlation.
    indices = np.random.Generator(np.random.PCG64(seed)).integers(0, n, (REPLICATES, n))
    for stage in STAGES:
        values = [x for event in event_values[stage] for x in event]
        histogram = response.histogram(values, edges, "MIP at 0.5 mm equivalent path")
        spectrum = dict(histogram=histogram, empirical_quantiles_MIP=np.quantile(values, [.1, .25, .5, .75, .9]).tolist() if values else None,
                        empirical_mode_MIP=float((edges[np.argmax(histogram["counts"])]+edges[np.argmax(histogram["counts"])+1])/2) if values else None)
        try:
            # Do not retune the frozen model/range for a sparse or invalid sample.
            fit = fitter.fit_landau_gaussian(histogram, label+"_"+stage)
        except RuntimeError as error:
            fit = dict(status="unavailable", reason=str(error), fit_range_MIP=[.25, 2.5], bin_width_MIP=.025,
                       bootstrap_failed_fits=REPLICATES, MPV_event_cluster_bootstrap_SE=None,
                       MPV_event_cluster_bootstrap_CI95=None, underlying_Landau_MPV=None, convolved_peak=None)
        else:
            by_event = np.array([response.histogram(v, edges, "MIP")["counts"] for v in event_values[stage]])
            tasks = [(dict(histogram, counts=by_event[index].sum(axis=0).tolist()), f"{label}_{stage}_b{b}") for b, index in enumerate(indices)]
            fitted = fitter.bootstrap_fits(tasks, workers)
            success = [v for v in fitted if v is not None]
            failed = REPLICATES-len(success)
            fit.update(status="available", bootstrap_failed_fits=failed, bootstrap_replications=REPLICATES,
                       bootstrap_successful_fits=len(success), bootstrap_seed=seed, bootstrap_workers=workers,
                       bootstrap_interval_convention="Conditional on converged fixed-model fits; quote intervals only with at least 950/1000 successful fits")
            for parameter, prefix in (("underlying_Landau_MPV", "MPV"), ("convolved_peak", "convolved_peak")):
                estimates = [v[parameter] for v in success]
                fit[prefix+"_event_cluster_bootstrap_SE"] = float(np.std(estimates, ddof=1)) if failed <= 50 else None
                fit[prefix+"_event_cluster_bootstrap_CI95"] = np.quantile(estimates, [.025, .975]).tolist() if failed <= 50 else None
        spectrum["fit"] = fit
        if stage in selected_values:
            spectrum["actual_thresholded_output"] = response.histogram(selected_values[stage], edges, "MIP at 0.5 mm equivalent path")
        spectra[stage] = spectrum
        print("MIP", label, stage, len(values), "qualified cells; fit", fit["status"], flush=True)
    return spectra


def muon_summary(rows, args, pedestal):
    from podio import root_io
    _, response = helpers()
    work = Path(args.work); output = []; compact_geometry = {}; cache_by_geometry = {}
    if sha(__file__) != hashlib.sha256(LOADED_SOURCE).hexdigest():
        raise ValueError("Muon analysis source changed after import")
    for geometry_name in ("nodd", "odd-zero"):
        public_path = work / f"muon-geometry-{geometry_name}.json"
        cache_path = work / f"muon-geometry-{geometry_name}-cells.json"
        public = json.loads(public_path.read_text()); cache = json.loads(cache_path.read_text())
        if public["local_cache_sha256"] != sha(cache_path) or cache["identity"] != public["identity"]:
            raise ValueError("Native muon geometry cache changed")
        if public["identity"]["source_sha256"] != hashlib.sha256(LOADED_SOURCE).hexdigest():
            raise ValueError("Native geometry and muon analysis source differ")
        for path, expected in public["identity"]["inputs"].items():
            if sha(path) != expected: raise ValueError("Muon native geometry input changed")
        if (public["identity"]["transport_manifest_sha256"] != sha(args.transport_manifest)
                or public["identity"]["samples_sha256"] != sha(args.samples)):
            raise ValueError("Muon native geometry manifest changed")
        for path, expected in public["identity"]["libraries"].items():
            if sha(path) != expected: raise ValueError("Muon native factory changed")
        transport = json.loads(Path(args.transport_manifest).read_text())
        for path, expected in transport["immutable"].items():
            if sha(path) != expected: raise ValueError("Muon transport dependency changed: " + path)
        if sha(transport["geometries"][geometry_name]["compact"]) != public["identity"]["compact_sha256"]:
            raise ValueError("Muon native compact changed")
        compact_geometry[geometry_name] = dict(public, summary_sha256=sha(public_path))
        cache_by_geometry[geometry_name] = cache
    selected_rows = [row for row in rows if row["kind"] == "muons"]
    keys = [(r["geometry"], r["sample"]["eta"]) for r in selected_rows]
    if set(keys) != set(SEEDS) or len(keys) != len(SEEDS):
        raise ValueError("Expected six distinct held-out muon populations")
    for row in selected_rows:
        geometry_name = row["geometry"]; eta = row["sample"]["eta"]; seed = SEEDS[(geometry_name, eta)]
        cache = cache_by_geometry[geometry_name]; inventory = {tuple(k) for k in cache["inventory"]}
        roles = collection_roles(geometry_name); target_collection = next(c for c, role in roles.items() if role == ("barrel" if eta == 0 else "endcap"))
        target_side = 0 if eta == 0 else (1 if eta > 0 else 2)
        # A nominal depth plane is one opportunity per event across all sectors;
        # sectors are physical adjacency groups, never multiplicative trials.
        nominal_layers = {k[3] for k in inventory if k[0] == target_collection and k[1] == target_side}
        if not nominal_layers: raise ValueError("Target has no constructed sensitive planes")
        if sha(row["sample"]["path"]) != row["sample"]["sha256"] or cache["identity"]["inputs"].get(row["sample"]["path"]) != row["sample"]["sha256"]:
            raise ValueError("Muon population differs from native geometry audit")
        frames = root_io.Reader(row["sample"]["path"]).get("events"); diagnostics = response.read_events(row)
        if len(frames) != len(diagnostics): raise ValueError("Muon event count differs")
        counters = Counter(nominal_layer_opportunities=len(nominal_layers)*len(frames), identified_primary_layers=0,
                           identified_single_primary_layers=0, split_primary_layer=0, contaminated_single_cell_layer=0,
                           contaminated_identified_layer=0, missing_primary_layer_unknown_crossing=0, other_region_primary_cells=0,
                           qualified_spectrum_crossings=0, chord_unavailable=0, endpoint=0, sector_ambiguous=0,
                           incidence_rejected=0, detailed_primary_muon_contributions=0, nonprimary_contributions=0)
        category_counts = {name: [] for name in ("identified", "identified_single", "identified_split")}
        category_den = {name: [] for name in category_counts}
        nominal_counts = []; event_values = {stage: [] for stage in STAGES}; selected_values = {mode: [] for mode in ("off", "on")}
        paths = []; cosines = []; ratios = []; event_payload = []
        for frame, event in zip(frames, diagnostics):
            headers = frame.get("EventHeader")
            if len(headers) != 1 or [int(headers[0].getRunNumber()), int(headers[0].getEventNumber())] != event["identity"]:
                raise ValueError("Muon diagnostic/header identity changed")
            primaries = [p for p in frame.get("MCParticles") if p.getGeneratorStatus() == 1]
            if len(primaries) != 1 or int(primaries[0].getPDG()) != 13: raise ValueError("Expected one primary muon")
            primary = primaries[0]; oid = primary.getObjectID(); primary_oid = (int(oid.collectionID), int(oid.index))
            momentum = primary.getMomentum(); truth = np.array([momentum.x, momentum.y, momentum.z]); truth /= np.linalg.norm(truth)
            signed = {mode: {int(cid): float(value) for cid, value in event["modes"][mode]["cells"][target_collection]} for mode in ("off", "on")}
            primary_layers = defaultdict(list); centers = {}
            for collection in roles:
                for hit in frame.get(collection):
                    cid = int(hit.getCellID()); info = cache["cells"].get(f"{collection}:{cid}")
                    if info is None: raise ValueError("Unqueried native muon cell")
                    key = tuple(info["plane"]); cs, pure = pure_primary_contributions(hit, primary_oid)
                    counters["detailed_primary_muon_contributions"] += len(cs)
                    counters["nonprimary_contributions"] += len(hit.getContributions())-len(cs)
                    if not cs: continue
                    if key[0] != target_collection or key[1] != target_side:
                        counters["other_region_primary_cells"] += 1; continue
                    primary_layers[key].append((hit, cs, pure, info))
            # Count opportunities once per physical depth even if scattering
            # produces primary deposits in two sectors at the same depth.
            depths = defaultdict(list)
            for key, hits in primary_layers.items():
                depths[key[3]].extend(hits)
                positions = []; weights = []
                for _, cs, _, _ in hits:
                    for c in cs:
                        p = c.getStepPosition(); positions.append([p.x, p.y, p.z]); weights.append(c.getEnergy())
                if sum(weights) > 0: centers[key] = np.average(positions, axis=0, weights=weights)
            counts, den, event_counters = depth_trials(depths, nominal_layers, signed)
            counters.update(event_counters)
            for name in category_counts: category_counts[name].append(counts[name]); category_den[name].append(den[name])
            nominal_counts.append(counts["identified"])
            current = {stage: [] for stage in STAGES}
            for key, hits in primary_layers.items():
                if len(depths[key[3]]) != 1: continue
                hit, cs, pure, info = hits[0]
                if not pure: counters["contaminated_single_cell_layer"] += 1; continue
                cosine, rejection = chord_qualification(key, centers, inventory, info["normal"])
                if rejection: counters[rejection] += 1; continue
                previous, following = physical_neighbors(key, inventory)
                if any(len({k[2] for k in primary_layers if k[3] == neighbor[3]}) > 1 for neighbor in (previous, following)):
                    counters["sector_ambiguous"] += 1; continue
                normal = np.asarray(info["normal"])
                paths.append(info["thickness_mm"]/cosine); cosines.append(cosine)
                ratios.append(abs(float(truth@normal))/cosine); counters["qualified_spectrum_crossings"] += 1
                cid = int(hit.getCellID())
                for stage, value in (("raw", float(hit.getEnergy())/MIP), ("off", signed["off"][cid]), ("on", signed["on"][cid])):
                    current[stage].append(value*cosine)
                    if stage in selected_values and value > np.float32(.6): selected_values[stage].append(value*cosine)
            for stage in STAGES: event_values[stage].append(current[stage])
            event_payload.append(dict(identity=event["identity"], nominal=len(nominal_layers), identified=den["identified"], counts={k: v.tolist() for k, v in counts.items()}, spectra=current))
        if counters["identified_primary_layers"]+counters["missing_primary_layer_unknown_crossing"] != counters["nominal_layer_opportunities"]:
            raise ValueError("Muon opportunity denominator does not close")
        indices = np.random.Generator(np.random.PCG64(seed)).integers(0, len(frames), (REPLICATES, len(frames)))
        categories = {name: crossing_statistics(category_counts[name], category_den[name], indices) for name in category_counts}
        nominal = crossing_statistics(nominal_counts, np.full(len(frames), len(nominal_layers)), indices)
        nominal["convention"] = "Above-threshold identified primary depth planes / constructed nominal depth opportunities; missing primary deposits are unknown crossings, not measured electronic inefficiency"
        efficiencies = {mode: dict(accepted_counts=nominal["accepted_counts"][j], denominator=nominal["denominator"], efficiency=nominal["efficiency"][j],
                                  event_cluster_bootstrap_SE=nominal["event_cluster_bootstrap_SE"][j],
                                  event_cluster_bootstrap_CI95=[x[j] for x in nominal["event_cluster_bootstrap_CI95"]], convention=nominal["convention"])
                        for j, mode in enumerate(("off", "on"))}
        spectra = fit_spectra(event_values, selected_values, seed, geometry_name+"_eta"+str(eta).replace("-", "m"), args.fit_workers)
        signal = spectra["on"]["fit"]["underlying_Landau_MPV"]; signal_se = spectra["on"]["fit"]["MPV_event_cluster_bootstrap_SE"]
        noise = pedestal["SD"]; noise_se = noise/math.sqrt(2*(pedestal["n"]-1)) if pedestal["n"] > 1 else None
        snr = signal/noise if signal is not None and noise > 0 else None
        snr_se = math.hypot(signal_se/noise, signal*noise_se/noise**2) if signal_se is not None and noise_se is not None and snr is not None else None
        payload_path = work / f"muon-trials-{geometry_name}-eta{eta}.json"
        write(payload_path, event_payload)
        ray = next(r for r in cache["initial_rays"] if r["eta"] == eta)
        ray_depths = {p["plane"][3] for p in ray["planes"] if p["plane"][0] == target_collection and p["plane"][1] == target_side}
        output.append(dict(geometry=geometry_name, eta=eta, events=len(frames), counters=dict(counters),
                           constructed_nominal_layers=sorted(nominal_layers), bootstrap=dict(seed=seed, replications=REPLICATES, rng="NumPy PCG64", numpy=np.__version__, resampling_unit="whole generated event"),
                           initial_ray_approximation=dict(nominal_layers=len(nominal_layers), active_layers=len(ray_depths),
                               layers_without_active_intersection=len(nominal_layers-ray_depths),
                               active_path_mm=ray["active_path_mm"],
                               disposition="Geometric initial-ray diagnostic only; passive/guard/gap misses are not transported crossing or electronics-failure counts"),
                           transported_crossing_inventory=dict(known_zero_identified_primary_signal=counters["known_zero_identified_primary_signal"],
                               unknown_missing_primary_deposit=counters["missing_primary_layer_unknown_crossing"],
                               complete_active_crossing_inventory_available=False,
                               reason="Persistent contribution step positions do not reconstruct active/passive traversal for planes with no primary deposit"),
                           native_geometry_sha256=compact_geometry[geometry_name]["summary_sha256"], local_trials_sha256=sha(payload_path),
                           input_sha256=row["sample"]["sha256"], diagnostic_sha256=row["receipt"]["output_sha256"],
                           path_mm=basic(paths), cosine=basic(cosines), chord_over_straight_path=basic(ratios), spectra=spectra,
                           thresholds_MIP=THRESHOLDS.tolist(), efficiency=efficiencies, nominal_opportunity_yield=nominal,
                           identified_crossing_categories=categories, efficiency_joint_covariance=nominal["joint_covariance"], efficiency_joint_order=nominal["joint_order"],
                           SNR=dict(signal_MIP=signal, signal_SE=signal_se, noise_RMS_MIP=noise, noise_RMS_SE=noise_se, ratio=snr, ratio_SE=snr_se,
                                    convention="Conditional path-normalized Landau-component MPV / shared verified signed pedestal RMS; no noise or physical acceptance qualification"),
                           limitations=["Local adjacent-physical-plane primary contribution centroid chord is an incidence approximation; not a reconstructed Geant4 step length.",
                                        "Spectrum is threshold independent, pure-primary single cell, with two immediate physical neighbors, actual 0.5-mm silicon and cosine >=0.9.",
                                        "Nominal yields include missing primary deposits as unknown crossings; identified categories condition on an associated primary contribution.",
                                        "No noise field is added to empty channels in sparse simulation input; threshold efficiency is not detector occupancy."]))
    return dict(samples=output, geometry=compact_geometry, mip_energy_GeV=MIP, helper_sha256=HELPERS,
                source_sha256=hashlib.sha256(LOADED_SOURCE).hexdigest())
