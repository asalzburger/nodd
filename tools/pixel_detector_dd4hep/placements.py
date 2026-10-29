"""Maintained DES040 placement contract, independent of analysis prototypes.

The frozen inputs describe local units. These controls rigidly place those units;
they never recompute module packing, luminous compensation or readout identities.
"""

import copy
import json
import math
from pathlib import Path


def load(config, root):
    if "placement" in config:
        return copy.deepcopy(config["placement"])
    path = config.get("placement_config")
    return json.loads((Path(root) / path).read_text())["placement"] if path else None


def barrel_offsets(placement, layers):
    if placement is None:
        return {}
    radii = placement["pixel_barrel_radii_mm"]
    counts = placement["pixel_barrel_staves"]
    if len(radii) != len(layers) or len(counts) != len(layers):
        raise ValueError("Placement must describe every existing pixel barrel layer")
    if any(type(r) not in (int, float) or not math.isfinite(r) or r <= 0 for r in radii):
        raise ValueError("Invalid pixel barrel placement radius")
    if any(a >= b for a, b in zip(radii, radii[1:])):
        raise ValueError("Pixel barrel radii must be ordered")
    if counts != [layer["staves"] for layer in layers]:
        raise ValueError("This maintained baseline preserves the reference stave counts")
    return {layer["layer"]: r - layer["nominal_radius_mm"]
            for layer, r in zip(layers, radii)}


def disc_plan(config, source_discs, reference_datums):
    """Return logical-ID order, carrying an explicit original donor identity."""
    if len(reference_datums) != len(source_discs):
        raise ValueError("Reference disc schedule does not match frozen local inputs")
    placement = config.get("placement")
    datums = ({str(i): z for i, z in enumerate(reference_datums, 1)}
              if placement is None else placement["pixel_disks_abs_z_mm"])
    if set(datums) != {str(i) for i in range(1, len(source_discs) + 1)}:
        raise ValueError("Every existing disc logical ID requires one placement")
    controls = [(i, i, datums[str(i)]) for i in range(1, len(source_discs) + 1)]
    extra = None if placement is None else placement.get("additional_pixel_disk")
    if extra:
        if set(extra) != {"abs_z_mm", "donor_layer", "layer_id"}:
            raise ValueError("Unsupported added-disc controls")
        donor, identity = extra["donor_layer"], extra["layer_id"]
        if type(identity) is not int or not len(source_discs) < identity < 16:
            raise ValueError("Added disc must have a new four-bit logical ID")
        if type(donor) is not int or not 1 <= donor <= len(source_discs):
            raise ValueError("Added disc donor does not exist")
        controls.append((identity, donor, extra["abs_z_mm"]))
    zvalues = [z for _, _, z in controls]
    if any(type(z) not in (int, float) or not math.isfinite(z)
           or not min(reference_datums) <= z <= max(reference_datums) for z in zvalues):
        raise ValueError("Disc placement exceeds the fixed reference allocation")
    if placement and any(b - a < 77.636 for a, b in zip(sorted(zvalues), sorted(zvalues)[1:])):
        raise ValueError("Disc/collector separation is below 77.636 mm")
    result = []
    for identity, donor, datum in controls:
        record = copy.deepcopy(source_discs[donor - 1])
        record.update(logical_id=identity, donor_layer=donor, datum_mm=datum,
                      source_datum_mm=source_discs[donor - 1]["datum_mm"],
                      reference_datum_mm=reference_datums[donor - 1])
        result.append(record)
    return result
