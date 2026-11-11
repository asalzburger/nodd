"""Count strict repeated local module recipes; this is not a cache implementation.

Only names and factory-specific outer placement/instance fields are excluded.
All descendant IDs, dimensions, material, sensitivity and local transforms stay
in the key. Numeric strings are deliberately not rounded or evaluated.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import xml.etree.ElementTree as ET


OUTER_FIELDS = {
    "nODDPixelBarrel": {"name", "id", "z"},
    "nODDPixelEndcap": {"name", "id", "col", "x", "y", "z", "ux", "uy", "vx", "vy", "nz"},
    "nODDShortStripBarrel": {"name", "id", "z", "lift"},
}


def recipe(node, outer_fields=frozenset()):
    excluded = {"name"} | outer_fields
    return (node.tag, tuple(sorted((k, v) for k, v in node.attrib.items() if k not in excluded)),
            tuple(recipe(child) for child in node))


def counts(compact):
    rows = []
    for detector in ET.parse(compact).findall("./detectors/detector"):
        kind = detector.get("type")
        if kind not in OUTER_FIELDS:
            continue
        modules = list(detector.iter("module"))
        groups = Counter(recipe(module, OUTER_FIELDS[kind]) for module in modules)
        rows.append(dict(system=int(detector.get("id")), factory=kind, instances=len(modules),
                         strict_local_recipe_classes=len(groups),
                         multiplicity_histogram=dict(sorted(Counter(groups.values()).items())),
                         instance_fields_excluded=sorted(OUTER_FIELDS[kind]),
                         descendant_ids_retained=True))
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("compact", type=Path)
    args = parser.parse_args()
    print(json.dumps(counts(args.compact), indent=2))
