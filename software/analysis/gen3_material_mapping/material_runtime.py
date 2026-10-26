"""Shared controls for the isolated native Gen3 mapping/validation prototype.

ACTS, DD4hep and ROOT imports are deliberately lazy so manifest checks need no
native installation. No Python implementation of material mapping is supplied.
"""

import ctypes
import hashlib
import importlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_manifest(path):
    manifest = json.loads(Path(path).read_text())
    if manifest.get("schema_version") != 1:
        raise ValueError("Expected selection schema_version=1")
    surfaces = manifest.get("surfaces", [])
    if not surfaces:
        raise ValueError("No selected surfaces")
    ids, keys = set(), set()
    for surface in surfaces:
        identity = surface.get("geometry_id")
        key = surface.get("material_key")
        if type(identity) is not int or identity <= 0 or identity in ids:
            raise ValueError("Geometry IDs must be positive unique integers")
        if not isinstance(key, str) or not key or key in keys:
            raise ValueError("Material keys must be nonempty unique strings")
        ids.add(identity)
        keys.add(key)
        kind = surface.get("type")
        if kind not in ("cylinder", "disc"):
            raise ValueError("Only cylinder/disc portals are supported")
        expected_axes = {"phi", "z" if kind == "cylinder" else "r"}
        bins = surface.get("bins", {})
        if set(bins) != expected_axes or any(
                type(value) is not int or value <= 0 for value in bins.values()):
            raise ValueError("Expected positive integer phi and z/r bin counts")
        segment = surface.get("rz_segment_mm")
        if not isinstance(segment, list) or len(segment) != 2 or any(
                not isinstance(point, list) or len(point) != 2 for point in segment):
            raise ValueError("Expected two finite [r,z] segment endpoints")
        if any(type(value) not in (int, float) or not math.isfinite(value)
               for point in segment for value in point):
            raise ValueError("Non-finite portal bounds")
    return manifest


def native_imports(module_dir):
    ctypes.CDLL("libDDG4.dylib" if sys.platform == "darwin" else "libDDG4.so",
                mode=ctypes.RTLD_GLOBAL)
    import ROOT
    import acts
    import acts.examples
    import acts.json
    sys.path.insert(0, str(Path(module_dir).resolve()))
    sidecar = importlib.import_module("nodd_portal_material")
    ROOT.gROOT.SetBatch(True)
    return ROOT, acts, sidecar


def audit_material_inventory(manifest, inventory, phase):
    """Require exact native types/counts, including finalized 1x1 slabs.

    ACTS finalizes a 1x1 accumulator as HomogeneousSurfaceMaterial. A request
    with either axis above one must still finalize as binned material.
    """
    if phase not in ("proto", "mapped"):
        raise ValueError("Expected proto or mapped inventory phase")
    by_id = {item["geometry_id"]: item for item in inventory}
    expected_ids = {surface["geometry_id"] for surface in manifest["surfaces"]}
    if set(by_id) != expected_ids or len(inventory) != len(expected_ids):
        raise RuntimeError("Native material inventory identities/counts differ from the manifest")
    for requested in manifest["surfaces"]:
        actual = by_id[requested["geometry_id"]]
        axis = "z" if requested["type"] == "cylinder" else "r"
        counts = [requested["bins"]["phi"], requested["bins"][axis]]
        expected_type = "proto" if phase == "proto" else (
            "homogeneous" if counts == [1, 1] else "binned")
        if actual.get("type") != expected_type or actual.get("axis_bin_counts") != counts:
            raise RuntimeError("Native material type/binning differs from requested ProtoSurfaceMaterial")
        if phase == "proto":
            if (actual.get("material_key") != requested["material_key"]
                    or actual.get("core_material_key") != requested["material_key"]):
                raise RuntimeError("Native/core ProtoSurfaceMaterial key differs from the manifest")
        else:
            total = counts[0] * counts[1]
            empty = actual.get("empty_bins")
            if (actual.get("material_bins") != total or type(empty) is not int
                    or not 0 <= empty <= total):
                raise RuntimeError("Native mapped material-bin inventory is inconsistent")


def prepare_geometry(args, manifest, acts, sidecar, map_path=None):
    from acts.examples.nodd import getNoddDetector
    detector = getNoddDetector(
        nodd_dir=args.nodd_dir.resolve(), build_dir=args.build_dir.resolve(),
        logLevel=acts.logging.WARNING)
    geometry = detector.trackingGeometry()
    context = detector.nominalGeometryContext()
    decoration = sidecar.configure(geometry, context, manifest["surfaces"])
    selected = decoration.pop("surfaces")
    expected = {surface["geometry_id"] for surface in manifest["surfaces"]}
    extracted = geometry.extractMaterialSurfaces()
    if {surface.geometryId.value for surface in extracted} != expected or len(extracted) != len(expected):
        raise RuntimeError("Native material extraction differs from the manifest")
    actual = sidecar.material_inventory(geometry)
    audit_material_inventory(manifest, actual, "proto")
    decoration["proto_inventory"] = actual
    if map_path:
        decoration.update(apply_saved_map(geometry, manifest, acts, map_path, sidecar))
    return detector, geometry, context, selected, decoration


def apply_saved_map(geometry, manifest, acts, map_path, sidecar=None):
    config = acts.json.MaterialMapJsonConverter.Config()
    decorator = acts.json.JsonMaterialDecorator(config, str(map_path), acts.logging.WARNING)
    maps = decorator.materialMaps
    expected_keys = {surface["material_key"] for surface in manifest["surfaces"]}
    expected_ids = {surface["geometry_id"] for surface in manifest["surfaces"]}
    if set(maps.keyedSurfaces) != expected_keys or maps.surfaceMaterials or maps.volumeMaterials:
        raise RuntimeError("Serialized map identities differ from the selected portal keys")
    maps.apply(geometry)
    extracted = geometry.extractMaterialSurfaces()
    if len(extracted) != len(expected_ids) or {s.geometryId.value for s in extracted} != expected_ids:
        raise RuntimeError("Reloaded map changed the material-surface inventory")
    if any(isinstance(surface.surfaceMaterial, acts.ProtoSurfaceMaterial) for surface in extracted):
        raise RuntimeError("Reload left a ProtoSurfaceMaterial instead of mapped material")
    report = {"map_reload": "PASS: exact keyed map applied to the same native portal inventory",
              "map_key_count": len(maps.keyedSurfaces)}
    if sidecar:
        inventory = sidecar.material_inventory(geometry)
        audit_material_inventory(manifest, inventory, "mapped")
        report["mapped_inventory"] = inventory
        report["material_bins"] = sum(item.get("material_bins", 1) for item in inventory)
        report["empty_bins"] = sum(item.get("empty_bins", 0) for item in inventory)
    return report


def provenance(args, sidecar, extra_files=()):
    root = Path(__file__).resolve().parents[3]
    nodd = args.nodd_dir.resolve()
    build = args.build_dir.resolve()
    detector_dir = build / "detector" if (build / "detector").is_dir() else build
    suffix = ".dylib" if sys.platform == "darwin" else ".so"
    files = [("selection_manifest", args.manifest.resolve()),
             ("sidecar", Path(sidecar.__file__)),
             ("runtime_helper", Path(__file__).resolve()),
             ("sidecar_source", root / "software/source/ActsExamples/MaterialMapping/PortalMaterial.cpp"),
             ("sidecar_build_controls", root / "software/source/ActsExamples/MaterialMapping/CMakeLists.txt"),
             ("steering", Path(sys.argv[0]).resolve()),
             ("compact", detector_dir / "tracker/tracker.xml"),
             ("materials", detector_dir / "tracker/materials.xml")]
    files += [("factory", detector_dir / f"lib{name}{suffix}") for name in (
        "nODDBeamPipe", "nODDPixelBarrel", "nODDShortStripBarrel",
        "nODDShortStripEndcap", "nODDLongStrip")]
    for name in ("acts.ActsPythonBindings", "acts.examples.ActsExamplesPythonBindingsNodd"):
        files.append(("runtime_binding", Path(importlib.import_module(name).__file__)))
    runtime_build = Path(importlib.import_module("acts.ActsPythonBindings").__file__).parents[2]
    for name in ("ActsCore", "ActsExamplesFramework", "ActsExamplesMaterialMapping", "ActsPluginJson", "ActsPluginRoot"):
        path = runtime_build / "lib" / f"lib{name}{suffix}"
        if path.is_file():
            files.append(("runtime_library", path))
    files += list(extra_files)

    def git_revision(directory):
        return subprocess.check_output(["git", "-C", str(directory), "rev-parse", "HEAD"], text=True).strip()

    return {
        "analysis_source_revision": git_revision(root),
        "native_adapter_revision": git_revision(nodd),
        "ACTS_source_revision": git_revision(nodd / "software/submodules/acts"),
        "native_adapter_dirty_paths": subprocess.check_output(
            ["git", "-C", str(nodd), "status", "--short", "--", "software/source/ActsExamples/Nodd"],
            text=True).splitlines(),
        "ACTS_source_dirty_paths": subprocess.check_output(
            ["git", "-C", str(nodd / "software/submodules/acts"), "status", "--short"],
            text=True).splitlines(),
        "recording_geometry_revision": None,
        "python": platform.python_version(), "platform": platform.platform(),
        "sidecar_pybind11_version": sidecar.pybind11_version,
        "sidecar_pybind11_internals_version": sidecar.pybind11_internals_version,
        "command": sys.argv,
        "files": [{"role": role, "name": path.name, "sha256": sha256(path)} for role, path in files],
    }


def root_budget_frame(ROOT, path, events=None):
    """Recompute per-track double precision budgets from the complete slabs."""
    if not hasattr(ROOT, "noddSlabBudget"):
        ROOT.gInterpreter.Declare("""
          #include <ROOT/RVec.hxx>
          double noddSlabBudget(const ROOT::VecOps::RVec<float>& length,
                                const ROOT::VecOps::RVec<float>& scale) {
            if (length.size() != scale.size()) throw std::runtime_error("Invalid slab vectors");
            double total = 0.;
            for (size_t i=0; i<length.size(); ++i) total += double(length[i])/double(scale[i]);
            return total;
          }
        """)
    frame = ROOT.RDataFrame("material_tracks", str(path))
    if events is not None:
        frame = frame.Filter(f"event_id < {int(events)}")
    frame = frame.Define("nodd_x0", "noddSlabBudget(mat_step_length,mat_X0)")
    frame = frame.Define("nodd_l0", "noddSlabBudget(mat_step_length,mat_L0)")
    frame = frame.Define("nodd_steps", "static_cast<unsigned long long>(mat_step_length.size())")
    return frame


def root_summary(ROOT, path, events=None):
    """Full per-track closure statistics including empty tracks."""
    frame = root_budget_frame(ROOT, path, events)
    tracks = frame.Count()
    x0, l0 = frame.Sum["double"]("nodd_x0"), frame.Sum["double"]("nodd_l0")
    steps = frame.Sum["unsigned long long"]("nodd_steps")
    empty = frame.Filter("nodd_steps == 0").Count()
    return {"tracks": int(tracks.GetValue()), "steps": int(steps.GetValue()),
            "empty_tracks": int(empty.GetValue()), "sum_X0": float(x0.GetValue()),
            "sum_L0": float(l0.GetValue())}


def budget_partition(ROOT, original, mapped, unmapped, events):
    """Verify individual rays, including zeros, rather than only a global sum.

    The source schema has no track ID. The exact event and momentum float bits
    identify these straight recorded rays; duplicate keys are rejected.
    """
    import numpy as np
    columns = ("event_id", "v_px", "v_py", "v_pz", "nodd_x0", "nodd_l0", "nodd_steps")

    def table(path, selected_events=None):
        arrays = root_budget_frame(ROOT, path, selected_events).AsNumpy(list(columns))
        keys = np.rec.fromarrays([arrays[name] for name in columns[:4]], names=columns[:4])
        order = np.argsort(keys, kind="stable")
        keys = keys[order]
        if np.unique(keys).size != keys.size:
            raise RuntimeError("Recording lacks unique event/momentum ray identities")
        return keys, {name: arrays[name][order] for name in columns[4:]}

    keys, source = table(original, events)
    mapped_keys, assigned = table(mapped)
    unmapped_keys, unassigned = table(unmapped)
    if not np.array_equal(keys, mapped_keys) or not np.array_equal(keys, unmapped_keys):
        raise RuntimeError("Mapped/unmapped outputs changed individual ray identities")
    if np.any(assigned["nodd_steps"] + unassigned["nodd_steps"] != source["nodd_steps"]):
        raise RuntimeError("Mapping did not partition each ray's material steps")
    report = {"identity": "Exact event_id and recorded float momentum tuple; duplicate identities rejected",
              "tracks": int(keys.size), "step_partition": "PASS"}
    for axis in ("x0", "l0"):
        column = f"nodd_{axis}"
        residual = assigned[column] + unassigned[column] - source[column]
        maximum = float(np.max(np.abs(residual), initial=0.))
        if maximum > 1.e-10:
            raise RuntimeError(f"Individual ray {axis} budget does not close: {maximum}")
        report[f"max_absolute_{axis}_residual"] = maximum
    return report


def common_arguments(parser):
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--nodd-dir", type=Path, required=True,
                        help="Explicit checkout supplying the built native adapter")
    parser.add_argument("--build-dir", type=Path, required=True,
                        help="Explicit DD4hep compact/factory build directory")
    parser.add_argument("--native-module-dir", type=Path,
                        default=Path(__file__).resolve().parents[3] / "build/gen3-material-map-run/native")
    parser.add_argument("--output", type=Path, required=True, help="Output directory")
    parser.add_argument("--events", type=int, default=1000)


def write_report(path, report):
    Path(path).write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
