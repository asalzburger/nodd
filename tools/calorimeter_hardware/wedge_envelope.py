"""Navigation-only Si-W wedge envelopes derived from the existing frame solids."""

import math
import xml.etree.ElementTree as ET

from assembly import wedge
from model import I


# Keep the mother boundary away from physical hardware and adjacent wedges.
ENVELOPE_PADDING_MM = 0.25


def add_wedge_envelope(detector, frame_region, frame_parts, sectors):
    """Append the mother solid in the local frame of a sector replica."""
    if not frame_parts or any(part["shape_kind"] != "xtru" or part["frame"] != I
                              or part["center_mm"][:2] != [0, 0] for part in frame_parts):
        raise ValueError("Si-W wedge envelope requires axial prism frame pieces")
    padding = ENVELOPE_PADDING_MM
    vertices = [vertex for part in frame_parts for vertex in part["vertices_mm"]]
    tangent = math.tan(math.pi / sectors)
    inset = min(x * tangent - abs(y) for x, y in vertices) - padding
    if inset <= 0:
        raise ValueError("Si-W wedge envelope would touch the sector boundary")
    inner = min(x for x, _ in vertices) - padding
    outer = max(x for x, _ in vertices) + padding
    z_min = min(p["center_mm"][2] - p["depth_mm"] / 2 for p in frame_parts) - padding
    z_max = max(p["center_mm"][2] + p["depth_mm"] / 2 for p in frame_parts) + padding
    envelope = ET.SubElement(detector, "wedge_envelope", kind="xtru", frame_region=frame_region,
                             depth=f"{z_max - z_min:.17g}*mm", center_z=f"{(z_max + z_min) / 2:.17g}*mm")
    for x, y in wedge(inner, outer, tangent, inset):
        ET.SubElement(envelope, "vertex", x=f"{x:.17g}*mm", y=f"{y:.17g}*mm")
