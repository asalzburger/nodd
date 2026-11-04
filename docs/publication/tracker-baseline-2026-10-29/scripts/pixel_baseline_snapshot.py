#!/usr/bin/env python3
"""Extract the current endcap baseline without changing the frozen barrel record.

Run the pure-Python combined exporter first, then supply its expected.json.
This is report preparation, not a new DD4hep/Geant4 validation run.
"""
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

REVISION = "e50ae6def313cae3d9be62ff1e299569965c1b35"
REPORT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--expected", type=Path, required=True)
    args = parser.parse_args()
    root = args.source_root.resolve()
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    if revision != REVISION:
        raise SystemExit("Use the pinned main baseline; a different revision needs explicit provenance review.")
    read = lambda name: json.loads((root / name).read_text())
    cfg = read("detector/config/pixel-detector-trimmed.json")
    layout = read(cfg["layout"])
    screen = read(cfg["apertures"])["variants"]["four-single-two-quad"]
    expected = json.loads(args.expected.read_text())
    if expected["provenance"]["combined_config"] != cfg:
        raise SystemExit("Expected inventory does not use the pinned current configuration.")
    if expected["counts"]["module"] != 5362 or expected["counts"]["sensitive"] != 11806:
        raise SystemExit("Unexpected combined inventory.")
    radial = read(cfg["radial_inputs"])
    template = {m["module_id"]: m for m in layout["modules"]}
    discs = []
    positive = [d for d in expected["service_accounting"]["endcap"]["discs"] if d["side"] == 1]
    for service, screening in zip(positive, screen["positive_discs"]):
        index = service["disc"]
        bodies = []
        for entity in expected["entities"]:
            if entity["role"] != "module" or entity["ids"]["system"] != 3 or entity["ids"]["layer"] != index:
                continue
            m = dict(template[entity["template_module_id"]])
            m["center_mm"] = entity["center_mm"]
            m["source_module_id"] = entity["source_module_id"]
            family = radial["families"][m["family"]]
            m["half_u_mm"], m["half_v_mm"] = [v / 2 for v in family["body_mm"]]
            m["body_radial_offset_mm"] = family["periphery_offset_mm"]
            m["foot_height_mm"] = m["level"] * 1.65
            bodies.append(m)
        assert len(bodies) == service["modules"]
        active_bounds = []
        for m in bodies:
            family = radial["families"][m["family"]]
            radius = math.hypot(*m["center_mm"][:2])
            for col in range(family["columns"]):
                a = (col - (family["columns"] - 1) / 2) * 20.2
                for row in range(family["rows"]):
                    b = (row - (family["rows"] - 1) / 2) * 19.4
                    active_bounds.append((math.hypot(radius + b - 9.6, max(abs(a) - 10, 0)),
                                          math.hypot(radius + b + 9.6, abs(a) + 10)))
        discs.append(dict(index=index, z_mm=service["datum_mm"], removed_rows=service["removed_rows"],
                          retained_rows=screening["retained_rows"], bodies=bodies,
                          modules=service["modules"], chips=service["chips"],
                          families=screening["after"]["families"], cooling=service["cooling"],
                          power_chains=screening["after"]["power_chains"],
                          active_radial_span_mm=[min(a for a,b in active_bounds), max(b for a,b in active_bounds)]))
    assert [d["z_mm"] for d in discs] == [615, 795, 1046, 1333, 1645, 1977, 2328, 2692, 3070]
    total_mass = sum(v["mass_g"] for v in expected["material_totals"].values())
    transport_mass = sum(e["volume_mm3"] * expected["materials"][e["material"]]["density_g_cm3"] / 1000
                         for e in expected["entities"] if e["role"] == "transport_services")
    native = read("docs/validation/DES-019/main-integration/native-summary.json")
    assert abs(total_mass - native["mass_g"]) < 1e-6
    data = dict(status="DRAFT; current selected baseline, engineering qualification remains open",
                parent_revision=revision, discs=discs, rings=layout["rings"],
                radial=radial, support_variant=read(cfg["support_variant_inputs"]), config=cfg,
                transport_P=expected["service_accounting"]["endcap"]["transport_P"],
                counts=dict(barrel_modules=3050, barrel_chips=6794,
                            endcap_modules=2 * sum(d["modules"] for d in discs),
                            endcap_chips=2 * sum(d["chips"] for d in discs),
                            combined_modules=5362, combined_chips=11806,
                            endcap_circuits=2 * sum(d["cooling"]["number_circuits"] for d in discs)),
                mass_g=dict(combined=total_mass, downstream_transport=transport_mass),
                native_evidence=dict(execution_state=native["execution_state"],
                                     compact_sha256=native["compact_sha256"],
                                     expected_sha256=native["expected_sha256"],
                                     library_sha256=native["library_sha256"]))
    target = REPORT / "data/pixel-endcap-baseline.json"
    target.write_text(json.dumps(data, indent=2) + "\n")
    sources = ["detector/config/pixel-detector-trimmed.json", cfg["layout"], cfg["apertures"],
               cfg["radial_inputs"], cfg["support_variant_inputs"], cfg["endcap_inputs"],
               "docs/validation/DES-019/main-integration/native-summary.json",
               "docs/validation/DES-019/main-integration/results.md",
               "docs/validation/DES-019/main-integration/inventory-comparison.json"]
    sources += [str(p.relative_to(root)) for p in sorted((root / "tools/pixel_detector_dd4hep").glob("*.py"))]
    provenance = dict(date="2026-10-06", parent_revision=revision,
                      snapshot_sha256=digest(target), expected_inventory_sha256=digest(args.expected),
                      sources=[dict(path=p, sha256=digest(root / p)) for p in sources],
                      generator_sha256=digest(Path(__file__)),
                      classification="Existing NODD DESIGN CHOICE and INFERENCE; documentation only, no new sign-off.",
                      scope="Current main integer disc datums and frozen mixed-ring geometry/IDs; positive-endcap modules, cooling and transport. Negative side is reflected. Frozen barrel/editorial snapshots are preserved separately.",
                      native_evidence="Retained validation ran at its recorded dirty source state, not at this publication revision. The supplied pure-export inventory is report input, not a new native validation.",
                      figures={"pixel-overview.pdf": "Current datums and active radial extents, original barrel routes; r-z projection.",
                               "pixel-endcap.pdf": "Exact first/last module footprints, face/height assignment and active chip patches, all depths projected.",
                               "pixel-disc-section.pdf": "Radial/axial projection of actual module spans and all levels; schematic tube cross-sections, no swept routing claim.",
                               "pixel-endcap-routing.pdf": "Exact face-specific outlines and chip-row cooling radii; conceptual face buses, fans and separated half-ring circuits.",
                               "pixel-service-interfaces.pdf": "Exact effective-cell radial/axial bounds at current first/last datums; connectivity schematic."})
    (REPORT / "data/pixel-endcap-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps(data["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
