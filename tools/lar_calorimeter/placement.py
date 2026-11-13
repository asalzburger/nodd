"""Opt-in PROTOTYPE real period envelopes for the unchanged LAr leaves.

The container follows the two existing outer absorber faces and the existing
annular/axial boundary. It is completely partitioned by the existing material
leaves, within the numerical volume tolerances already used by DES032/033.
The native factory supplies the actual enclosing material; the container is
not another material layer, electrode, sensitive gap or physical component.
"""
from copy import deepcopy
import math

from barrel_geometry import annular_area, dot, face_point, polygon_between_faces, rotate

POLICY = "real-periods-v1"


def _finite(values):
    if not all(math.isfinite(x) for x in values):
        raise ValueError("Nonfinite period envelope input")


def _same(actual, expected, tolerance=1e-10):
    _finite(list(actual)+list(expected))
    if len(actual) != len(expected) or any(abs(a-b) > tolerance for a, b in zip(actual, expected)):
        raise ValueError("Period envelope boundary differs from the existing partition")


def _proof(envelope, leaves, copies, tolerance):
    total = math.fsum(p["volume_mm3"] for p in leaves)
    capacity = envelope["volume_mm3"]
    _finite([total, capacity])
    if total <= 0 or capacity <= 0:
        raise ValueError("Nonpositive period envelope volume")
    residual = (capacity-total)/capacity
    if abs(residual) > tolerance:
        raise ValueError("Period leaves do not fill the proposed mother")
    return dict(policy=POLICY, mother_material="actual enclosing native mother material",
                logical_mothers=1, physical_mothers=copies,
                material_leaf_count=len(leaves), mother_capacity_mm3=capacity,
                leaf_volume_sum_mm3=total, unfilled_relative_residual=residual,
                volume_relative_tolerance=tolerance,
                physical_leaf_shapes_materials_poses_ids="unchanged",
                interpretation="Numerical partition residual, not an added material allowance")


def _chain(leaves, names, fields):
    for a, b in zip(names, names[1:]):
        upper, lower = leaves[a]["upper_face"], leaves[b]["lower_face"]
        _same(fields(upper), fields(lower))


def barrel_envelope(report):
    """One exact, full-depth inclined period shared by all barrel replicas."""
    leaves = report["pieces"]
    by_name = {p["name"]: p for p in leaves}
    names = {f"{stem}_{layer}" for layer in range(11)
             for stem in ("core", "glue_-1", "glue_1", "steel_-1", "steel_1", "pcb", "gap_0", "gap_1")}
    if len(leaves) != 88 or set(by_name) != names:
        raise ValueError("Unsupported barrel material partition")
    lower = deepcopy(by_name["steel_-1_0"]["lower_face"])
    upper = deepcopy(by_name["gap_1_0"]["upper_face"])
    depth = leaves[0]["depth_mm"]
    radii = report["sampling"]["radii_mm"]
    if len(radii) != 12 or any(a >= b for a, b in zip(radii, radii[1:])):
        raise ValueError("Invalid barrel annular compartments")
    period = 2*math.pi/len(report["replicas"])
    _same(rotate(lower[0], period), upper[0])
    _same([lower[1]], [upper[1]])
    for layer in range(11):
        a, b = by_name[f"steel_-1_{layer}"]["lower_face"], by_name[f"gap_1_{layer}"]["upper_face"]
        _same(a[0]+[a[1]], lower[0]+[lower[1]])
        _same(b[0]+[b[1]], upper[0]+[upper[1]])
        _chain(by_name, [f"{stem}_{layer}" for stem in
                        ("steel_-1", "glue_-1", "core", "glue_1", "steel_1", "gap_0", "pcb", "gap_1")],
               lambda face: face[0]+[face[1]])
    outward = [lower[0][1], -lower[0][0]]
    polygon = polygon_between_faces(lower, upper, (radii[0], radii[-1]), outward)
    for leaf in leaves:
        if leaf["depth_mm"] != depth or leaf["center_mm"] != [0, 0, 0] or leaf["frame"] != [[1, 0, 0], [0, 1, 0], [0, 0, 1]]:
            raise ValueError("Unsupported barrel leaf transform/depth")
        layer = leaf["layer"]
        _same([leaf["clip_annulus_mm"]["rmin"], leaf["clip_annulus_mm"]["rmax"]], radii[layer:layer+2])
        # Existing faces are straight and annular clipping uses the positive
        # radial branch. Check both faces over endpoint/interior radii.
        for radius in (radii[layer], (radii[layer]+radii[layer+1])/2, radii[layer+1]):
            for normal, bound in (leaf["lower_face"], leaf["upper_face"]):
                point = face_point(normal, bound, radius, [normal[1], -normal[0]])
                if dot(lower[0], point) < lower[1]-1e-7 or dot(upper[0], point) > upper[1]+1e-7:
                    raise ValueError("Barrel leaf face lies outside proposed mother")
    envelope = dict(shape_kind="xtru", vertices_mm=polygon, depth_mm=depth,
                    clip_annulus_mm=dict(rmin=radii[0], rmax=radii[-1]),
                    volume_mm3=annular_area(polygon, radii[0], radii[-1])*depth,
                    lower_face=lower, upper_face=upper)
    return envelope, _proof(envelope, leaves, len(report["replicas"]), 2e-8)


def endcap_envelope(wheel, materials):
    """One clipped turbine period, shared between its two signed wheels."""
    from endcap_geometry import at_circle, primitive
    leaves = wheel["pieces"]
    by_name = {p["name"].split("_", 1)[1]: p for p in leaves}
    if len(leaves) != 8 or set(by_name) != {"lead", "glue_-1", "glue_1", "steel_-1", "steel_1", "pcb", "gap0", "gap1"}:
        raise ValueError("Unsupported turbine material partition")
    lower = deepcopy(by_name["steel_-1"]["lower_face"])
    upper = deepcopy(by_name["gap1"]["upper_face"])
    _chain(by_name, ["steel_-1", "glue_-1", "lead", "glue_1", "steel_1", "gap0", "pcb", "gap1"],
           lambda face: face["normal"]+[face["bound"]])
    period = 2*math.pi/wheel["periods"]
    _same(rotate(lower["normal"][:2], period)+lower["normal"][2:], upper["normal"])
    _same([lower["bound"]], [upper["bound"]])
    ri, ro = wheel["inner_radius_mm"], wheel["outer_radius_mm"]
    half = leaves[0]["half_z_mm"]
    if not 0 < ri < ro or half <= 0:
        raise ValueError("Invalid turbine envelope bounds")
    for leaf in leaves:
        if leaf["half_z_mm"] != half or leaf["center_mm"] != [0, 0, 0] or leaf["frame"] != [[1, 0, 0], [0, 1, 0], [0, 0, 1]]:
            raise ValueError("Unsupported turbine leaf transform/depth")
        _same([leaf["clip_annulus_mm"]["rmin"], leaf["clip_annulus_mm"]["rmax"]], [ri, ro])
        for radius in (ri, (ri+ro)/2, ro):
            for z in (-half, 0., half):
                for face in (leaf["lower_face"], leaf["upper_face"]):
                    point = at_circle(face, z, radius)+[z]
                    if dot(lower["normal"], point) < lower["bound"]-1e-7 or dot(upper["normal"], point) > upper["bound"]+1e-7:
                        raise ValueError("Turbine leaf face lies outside proposed mother")
    # primitive supplies the existing straight-face/Arb8/circular construction
    # and its independently converged axial capacity quadrature.
    envelope = primitive("period_envelope", "container", "Air", lower, upper, ri, ro, half, materials)
    proof = _proof(envelope, leaves, 2*wheel["periods"], 1e-7)
    proof["wheel"] = wheel["wheel"]
    return envelope, proof
