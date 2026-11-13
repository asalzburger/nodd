"""Bind a fresh maintained export to the legacy full model and measured LAr candidate."""

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/lar_calorimeter"))
from placement_variant import canonical, sha


def envelope_normalized(element):
    """Variant appends envelopes; standalone export emits them before pieces.

    Compare all bytes after moving only these declarations to the same sibling
    position. The factory selects an envelope by tag; all daughter/replica order
    and every envelope attribute/vertex remain part of the comparison.
    """
    element = deepcopy(element)
    for parent in element.findall("period") + element.findall("wheel"):
        for envelope in parent.findall("period_envelope"):
            parent.remove(envelope)
            parent.append(envelope)
    return canonical(element)


def check(baseline, legacy, candidate, output):
    paths = [p for compact in (baseline, legacy, candidate)
             for p in (compact, compact.parent / "materials.xml")]
    before = {str(p.resolve()): sha(p) for p in paths}
    doc = ET.parse(baseline).getroot()
    measured = ET.parse(candidate).getroot()
    comparisons = {}
    for system, count in (("10", 1), ("11", 3)):
        current = doc.findall(f"detectors/detector[@id='{system}']")
        prior = measured.findall(f"detectors/detector[@id='{system}']")
        if len(current) != 1 or len(prior) != 1 or envelope_normalized(current[0]) != envelope_normalized(prior[0]):
            raise ValueError("Maintained ECAL differs from measured candidate: " + system)
        envelopes = current[0].findall("period/period_envelope") + current[0].findall("wheel/period_envelope")
        if len(envelopes) != count or any(e.get("policy") != "real-periods-v1" for e in envelopes):
            raise ValueError("Unexpected period policy/count: " + system)
        comparisons[system] = dict(reusable_templates=count,
                                  canonical_xml_sha256=hashlib.sha256(canonical(current[0])).hexdigest())
    restored = deepcopy(doc)
    removed = 0
    for parent in restored.findall("detectors/detector/period") + restored.findall("detectors/detector/wheel"):
        for envelope in parent.findall("period_envelope"):
            parent.remove(envelope)
            removed += 1
    if removed != 4 or canonical(restored) != canonical(ET.parse(legacy).getroot()):
        raise ValueError("Full maintained model changed beyond the four period envelopes")
    materials = [sha(p.parent / "materials.xml") for p in (baseline, legacy, candidate)]
    if len(set(materials)) != 1:
        raise ValueError("Material definitions differ")
    if {str(p.resolve()): sha(p) for p in paths} != before:
        raise ValueError("Comparison inputs changed during check")
    result = dict(status="PASS", input_sha256=before, producer_sha256=sha(__file__),
                  canonical_helper_sha256=sha(ROOT / "tools/lar_calorimeter/placement_variant.py"),
                  ecal_systems=comparisons, removed_envelopes=removed,
                  full_model_restored_to_legacy=True, materials_byte_identical=True,
                  comparison="Full legacy restoration preserves all attributes, child order and text; measured-candidate comparison additionally normalizes only period_envelope sibling position. Indentation whitespace ignored.")
    output.write_text(json.dumps(result, indent=2) + "\n")
    print("PASS full model restored by removing four envelopes; ECAL matches measured candidate")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("baseline", "legacy", "candidate", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    check(args.baseline, args.legacy, args.candidate, args.output)
