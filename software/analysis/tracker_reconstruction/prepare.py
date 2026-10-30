"""Build the maintained PR104 geometry; transport frozen inputs by physical role."""
import gzip
import importlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
for directory in ("gen3_material_mapping", "truth_tracking", "tracker_optimization"):
    sys.path.append(str(ROOT / "software/analysis" / directory))
from material_runtime import native_imports, apply_saved_map, write_report, sha256
from export_geometry import build_export
from select_surfaces import select
from material import select_candidate, transport, remap_errors
import smearing


def prepare(args):
    ROOTmod, acts, portal = native_imports(ROOT / "build/gen3-material-map-run/native")
    sys.path.insert(0, str(ROOT / "build/truth-tracking-baseline/native"))
    observer = importlib.import_module("nodd_truth_tracking")
    sys.path.insert(0, str(ROOT / "build/tracker-resolution-optimization/native"))
    helper = importlib.import_module("nodd_tracker_material")
    from acts.examples.nodd import getNoddDetector
    compact = ROOT / "build/balanced-baseline/dd4hep/detector/tracker/tracker.xml"
    if sha256(compact) != "81e2d439a66f0978d0613929842cf6aa4658cd0e0300ede7513d30caae296023":
        raise RuntimeError("Current reconstruction requires the registered PR104 compact")
    detector = getNoddDetector(nodd_dir=ROOT, build_dir=ROOT / "build/balanced-baseline/dd4hep",
                              compact_file=compact, logLevel=acts.logging.WARNING)
    geometry, context = detector.trackingGeometry(), detector.nominalGeometryContext()
    report = json.loads(detector.geometryReport())
    converter = acts.json.TrackingGeometryJsonConverter(level=acts.logging.WARNING)
    exported = build_export(json.loads(converter.toJson(context, geometry)), report,
                           lambda x: acts.GeometryIdentifier(**(x or {})).value)
    source_manifest = json.loads((ROOT / "docs/validation/gen3-material-map-run/selection.json").read_text())
    variant = json.loads((ROOT / "software/analysis/tracker_optimization/variants/balanced.json").read_text())
    manifest = select_candidate(exported, source_manifest["configuration"], variant, select)
    with gzip.open(ROOT / "docs/validation/gen3-material-map-run/material_map.json.gz", "rt") as stream:
        mapped, material_audit = transport(source_manifest, manifest, json.load(stream), variant, helper)
    write_report(args.output / "selection.json", manifest)
    write_report(args.output / "material-map.json", mapped)
    decoration = portal.configure(geometry, context, manifest["surfaces"])
    decoration.pop("surfaces")
    decoration.update(apply_saved_map(geometry, manifest, acts, args.output / "material-map.json", portal))
    source_widths = ROOT / "docs/validation/truth-tracking-baseline/smearing/pooled-widths.json"
    old_geometry = json.loads((ROOT / "docs/validation/gen3-material-mapping/geometry-summary.json").read_text())
    widths = remap_errors(json.loads(source_widths.read_text()), old_geometry, exported,
                          {(2,10): (2,2), (3,10): (3,2)}, pooled=True)
    settings = {"model": "gaussian_smearing", "merge": False,
                "measured_coordinates_by_system": smearing.COORDINATES}
    digi, counts = smearing.build_config(report["sensors"], settings, widths)
    for name, value in (("error-table.json", widths), ("digitization.json", digi),
                        ("native-report.json", report)):
        write_report(args.output / name, value)
    pixel_volumes = sorted({(s["geometry_id"] >> 56) & 255 for s in report["sensors"] if s["ids"]["system"] <= 3})
    selection = [{"volume": v} for v in pixel_volumes]
    write_report(args.output / "pixel-selection.json", selection)
    # This comparison anchors the effective map and response to the maintained
    # balanced Gaussian confirmation; use fresh native IDs, never copied IDs.
    previous = ROOT / "build/tracker-resolution-optimization/confirmation/gaussian/balanced-pt10"
    equivalence = {}
    for name in ("selection.json", "material-map.json", "error-table.json", "digitization.json"):
        if (previous / name).exists():
            equivalence[name] = json.loads((args.output/name).read_text()) == json.loads((previous/name).read_text())
    def same_geometry(a, b):
        if isinstance(a, dict) and isinstance(b, dict):
            return a.keys() == b.keys() and all(same_geometry(a[k],b[k]) for k in a)
        if isinstance(a, list) and isinstance(b, list):
            return len(a)==len(b) and all(same_geometry(x,y) for x,y in zip(a,b))
        if isinstance(a, float) and isinstance(b, float): return abs(a-b) < 1.e-9
        return a==b
    if "selection.json" in equivalence:
        equivalence["selection_geometry_within_1e-9_mm"] = same_geometry(manifest,json.loads((previous/"selection.json").read_text()))
    required = [v for k,v in equivalence.items() if k!="selection.json"]
    if required and not all(required):
        raise RuntimeError(f"Maintained baseline differs from retained balanced confirmation: {equivalence}")
    info = {"compact_sha256": sha256(compact), "native_geometry": exported["checks"],
            "material_transport": material_audit, "material_decoration": decoration,
            "digitization_sensors_by_system": counts, "pixel_volumes": pixel_volumes,
            "baseline_semantic_equivalence": equivalence,
            "digitization_defaults": smearing.native_boundary_contract(acts),
            "native_modules": {str(Path(m.__file__).resolve()): sha256(m.__file__) for m in (portal, observer, helper)}}
    return ROOTmod, acts, observer, detector, geometry, report, info
