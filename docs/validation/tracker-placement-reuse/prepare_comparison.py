"""Prepare isolated PR132 cached-assembly / notched-mother tracker compacts.

The maintained export is the sole input. The output retains all repeated XML:
this experiment changes the factory representation, not XML parsing volume.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

from recipe_counts import recipe

FACTORY = "nODDShortStripBarrelReuse"
FIELDS = {"name", "id", "z", "lift"}
ENVELOPE = dict(umax=24.5, vmax=51.5, wmin=-1.025, wmax=.1)
NOTCHES = [dict(kind="box", u=u, v=0., w=-.925, sx=20.1, sy=64.1, sz=.2)
           for u in (-12., 12.)]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(node, key):
    value = node.get(key, "")
    if not value.endswith("*mm"):
        raise ValueError("Require explicit finite mm: " + key)
    result = float(value[:-3])
    if not math.isfinite(result):
        raise ValueError("Nonfinite dimension")
    return result


def box(node):
    if node.get("kind") != "box":
        raise ValueError("Mother containment requires box module constituents")
    center = [number(node, x) for x in ("u", "v", "w")]
    size = [number(node, x) for x in ("sx", "sy", "sz")]
    if min(size) <= 0:
        raise ValueError("Nonpositive module dimension")
    return [[x-s/2, x+s/2] for x, s in zip(center, size)]


def verify_mother(module):
    """Prove child AABBs fit and notch intersections are removed by child cuts.

    This proves local child containment only. The separate SysArch sibling
    screen and full native overlap/material checks remain required.
    """
    tolerance = 1e-12  # arithmetic comparison only, no geometric padding
    envelope = [[-ENVELOPE["umax"], ENVELOPE["umax"]],
                [-ENVELOPE["vmax"], ENVELOPE["vmax"]],
                [ENVELOPE["wmin"], ENVELOPE["wmax"]]]
    for piece in module:
        bounds = box(piece)
        if any(lo < elo-tolerance or hi > ehi+tolerance
               for (lo, hi), (elo, ehi) in zip(bounds, envelope)):
            raise ValueError("Module child exceeds proposed mother: " + piece.get("name", ""))
        for attrs in NOTCHES:
            notch = box(ET.Element("cut", {k: (v if k == "kind" else f"{v:.17g}*mm")
                                           for k, v in attrs.items()}))
            overlap = [[max(a, c), min(b, d)] for (a, b), (c, d) in zip(bounds, notch)]
            if any(hi-lo <= tolerance for lo, hi in overlap):
                continue
            removed = False
            for cut in piece:
                local = box(cut)
                translated = [[lo+number(piece, axis), hi+number(piece, axis)]
                              for (lo, hi), axis in zip(local, ("u", "v", "w"))]
                if all(clo <= lo+tolerance and chi >= hi-tolerance
                       for (clo, chi), (lo, hi) in zip(translated, overlap)):
                    removed = True
                    break
            if not removed:
                raise ValueError("Mother notch removes physical module material: " + piece.get("name", ""))


def inspect(doc, mother=False):
    detectors = doc.findall("./detectors/detector[@type='nODDShortStripBarrel']")
    if len(detectors) != 1:
        raise ValueError("Require exactly one unchanged short-strip barrel factory")
    detector = detectors[0]
    modules = list(detector.iter("module"))
    if not modules:
        raise ValueError("No barrel modules")
    first = modules[0]
    expected_recipe = recipe(first, FIELDS)
    template_name = first.get("name") + "_reuse_template"
    names = [piece.get("name") for piece in first]
    instances = []
    seen_ids = set()
    for layer in detector.findall("layer"):
        for stave in layer.findall("stave"):
            for module in stave.findall("module"):
                if set(module.attrib) != FIELDS or any(p.tag != "piece" or any(c.tag != "cut" or len(c) for c in p) for p in module):
                    raise ValueError("Unsupported module structure")
                if recipe(module, FIELDS) != expected_recipe:
                    raise ValueError("Strict module recipes differ")
                for piece in module:
                    if not piece.get("name") or piece.get("kind") not in ("box", "shoe", "tube", "sector", "torus"):
                        raise ValueError("Unsupported module piece")
                if mother:
                    verify_mother(module)
                ids = dict(system=int(detector.get("id")), layer=int(layer.get("id")),
                           stave=int(stave.get("id")), module=int(module.get("id")))
                key = tuple(ids.values())
                if key in seen_ids:
                    raise ValueError("Duplicate module IDs")
                seen_ids.add(key)
                instances.append(dict(ids=ids, module_name=module.get("name"),
                                      pieces=dict(zip(names, (p.get("name") for p in module)))))
    if len(instances) != len(modules):
        raise ValueError("Unsupported module nesting")
    return detector, dict(module_instances=len(instances), template_name=template_name,
                         strict_recipe_sha256=hashlib.sha256(repr(expected_recipe).encode()).hexdigest(),
                         template_pieces=names, instances=instances)


def prepare(source, output, mode):
    source, output = Path(source).resolve(), Path(output).resolve()
    if mode not in ("cache", "mother"):
        raise ValueError("Unknown comparison mode")
    doc = ET.parse(source).getroot()
    detector, manifest = inspect(doc, mode == "mother")
    detector.set("type", FACTORY)
    detector.set("reuse_mode", mode)
    if mode == "mother":
        # DD4hep's actual world/mother material is independently checked by
        # the factory, rather than assumed from this label at runtime.
        envelope = ET.SubElement(detector, "reuse_envelope", material="Air",
                                 **{k:f"{v:.17g}*mm" for k,v in ENVELOPE.items()})
        for attrs in NOTCHES:
            ET.SubElement(envelope, "cut", **{k:v if k == "kind" else f"{v:.17g}*mm"
                                             for k,v in attrs.items()})
    output.mkdir(parents=True, exist_ok=False)
    ET.indent(doc, space="  ")
    ET.ElementTree(doc).write(output / "tracker.xml", encoding="utf-8", xml_declaration=True)
    for name in ("materials.xml", "expected.json"):
        shutil.copyfile(source.parent / name, output / name)
    manifest.update(schema_version=1, status="PROTOTYPE", mode=mode,
                    source_sha256={name:sha(source.parent/name) for name in (source.name, "materials.xml", "expected.json")},
                    compact_sha256=sha(output / "tracker.xml"), producer_sha256=sha(Path(__file__)),
                    enclosing_material="Air" if mode == "mother" else None,
                    mother_envelope_mm=ENVELOPE if mode == "mother" else None,
                    mother_notches_mm=NOTCHES if mode == "mother" else [],
                    limitations=["Strict shared-module experiment; repeated XML retained.",
                                 "Local containment proof does not replace whole-tracker overlap, material, Geant4 or ACTS checks."])
    (output / "reuse-manifest.json").write_text(json.dumps(manifest, separators=(",", ":")) + "\n")
    print(json.dumps({k:manifest[k] for k in ("status", "mode", "module_instances", "strict_recipe_sha256")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("compact", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--mode", choices=("cache", "mother"), required=True)
    args = parser.parse_args()
    prepare(args.compact, args.output, args.mode)
