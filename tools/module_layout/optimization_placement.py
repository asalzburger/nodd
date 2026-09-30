"""DES-011 PROTOTYPE: refill complete modules within physical disc annuli.

The annuli constrain occupied module bodies, not sensitive boundaries. Module
shapes, the reviewed staggering policy, and barrel placements remain unchanged.
This helper does not qualify supports or run the expensive all-body SAT check;
the optimization driver must validate the complete candidate afterwards.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math

try:
    from . import geometry
except ImportError:
    import geometry


_TOLERANCE_MM = 1e-7


def _radial_limits(center, shape, parity_shift):
    """Envelope over the two column-parity radial shifts of a flat disc row."""
    half_u, half_v = shape["body_u"]/2, shape["body_v"]/2
    return (center-half_v-parity_shift,
            math.hypot(center+half_v+parity_shift, half_u))


def _same_parity_clear(lo, hi, count, shape, shift, clearance):
    # Rows two apart reuse normal levels. Their complete radial projections
    # must clear even when different phi counts prevent column alignment.
    if count < 3:
        return True
    step = (hi-lo)/(count-1)
    return all(_radial_limits(lo+i*step, shape, shift)[1]+clearance <=
               _radial_limits(lo+(i+2)*step, shape, shift)[0]+_TOLERANCE_MM
               for i in range(count-2))


def refill_candidate(candidate, models, annuli_mm, *, layouts_path=None):
    """Return ``layout``, effective ``candidate``, ``models`` and ``diagnostics``.

    ``candidate`` is a layer-catalogue candidate dictionary. ``annuli_mm`` maps
    each disc subsystem to [minimum, maximum] *occupied-body* radius in mm.
    Models are copied; only the long-strip endcap row-count control is derived.
    IDs are regenerated and local to the returned candidate.

    Row density follows the inherited active-height minus overlap pitch. The
    generator's ceil rule supplies complete edge-covering rows; long-strip's
    formerly fixed six rows now use that same rule, reducing the count only if
    rows reusing a normal level would violate conservative radial clearance.
    This is a bounded filling policy, not globally optimal rectangle packing.
    """
    if not isinstance(candidate, dict) or not isinstance(candidate.get("layers"), list):
        raise ValueError("refill_candidate requires a candidate dictionary with layers")
    effective = copy.deepcopy(candidate)
    derived = copy.deepcopy(models)
    geometry.validate_models(derived)
    geometry._review_policy(derived, "review_default")
    required = {layer["subsystem"] for layer in effective["layers"]
                if layer["kind"] == "disc"}
    if required-set(annuli_mm):
        raise ValueError("missing occupied-body annulus for a disc subsystem")
    specifications = {}
    placement = derived["placement"]
    for sub in sorted(required):
        bounds = annuli_mm[sub]
        if (not isinstance(bounds, (tuple, list)) or len(bounds) != 2 or
                any(not isinstance(x, (int, float)) or not math.isfinite(x) for x in bounds)
                or not 0 <= bounds[0] < bounds[1]):
            raise ValueError("annuli must be finite increasing nonnegative radii in mm")
        inner, outer = map(float, bounds)
        family = "quad" if sub == "pixel" else sub
        shape = geometry._shape(family, derived)
        if shape["body_v_offset"] != 0:
            raise ValueError("disc refilling requires the reviewed centred body outline")
        overlap = placement[sub+"_overlap_v_mm"]
        pitch = shape["height"]-overlap
        if pitch <= 0:
            raise ValueError("active radial pitch must be positive")
        shift = overlap/4
        half_u, half_v = shape["body_u"]/2, shape["body_v"]/2
        if outer <= half_u:
            raise ValueError("annulus cannot contain the module's tangential body span")
        first = inner+half_v+shift
        last = math.sqrt(outer*outer-half_u*half_u)-half_v-shift
        span = last-first
        if span < -_TOLERANCE_MM:
            raise ValueError(f"{sub} annulus cannot contain a complete module row")
        last = max(first, last)
        margin = (derived["long_strip"]["endcap_radial_margin_mm"]
                  if sub == "long_strip" else placement["end_margin_mm"])
        nominal = [first+margin-shape["height"]/2,
                   last-margin+shape["height"]/2]
        # Use the same arithmetic order as _linear_centres so rounding at an
        # exact pitch does not silently disagree with the existing generator.
        interval = (nominal[1]+margin)-(nominal[0]-margin)
        count = (1 if interval <= shape["height"] else
                 math.ceil((interval-shape["height"])/pitch)+1)
        requested_count = count
        if sub == "long_strip":
            while count >= 3 and not _same_parity_clear(
                    first, last, count, shape, shift, placement["body_clearance_mm"]):
                count -= 1
            if count < 2:
                raise ValueError("long-strip generator requires space for at least two rows")
            derived["long_strip"]["endcap_rings"] = count
        elif not _same_parity_clear(first, last, count, shape, shift,
                                    placement["body_clearance_mm"]):
            raise ValueError(f"{sub} inherited row policy violates same-parity clearance")
        specifications[sub] = dict(
            requested_body_annulus_mm=[inner, outer],
            nominal_active_annulus_mm=nominal,
            row_center_limits_mm=[first, last],
            inherited_active_pitch_mm=pitch, requested_rows=requested_count,
            rows=count, actual_center_pitch_mm=(last-first)/(count-1) if count > 1 else None,
            column_parity_radial_shift_mm=shift,
            same_parity_radial_clearance_mm=placement["body_clearance_mm"])
    for layer in effective["layers"]:
        if layer["kind"] == "disc":
            low, high = specifications[layer["subsystem"]]["nominal_active_annulus_mm"]
            layer["r_min_m"], layer["r_max_m"] = low/1000, high/1000
    layout = geometry.generate_layout(effective, "review_default", "mixed", models=derived,
                                      layouts_path=layouts_path)
    layers = layout["metadata"]["host_diagnostics"]["layers"]
    actual = {}
    for layer in effective["layers"]:
        if layer["kind"] != "disc":
            continue
        record = layers[layer["id"]]
        bounds = specifications[layer["subsystem"]]["requested_body_annulus_mm"]
        if (record["r_min_mm"] < bounds[0]-_TOLERANCE_MM or
                record["r_max_mm"] > bounds[1]+_TOLERANCE_MM):
            raise ValueError("generated body exceeds requested physical annulus")
        actual[layer["id"]] = dict(body_annulus_mm=[record["r_min_mm"], record["r_max_mm"]],
                                    modules=record["modules"])
    diagnostics = dict(
        status="PROTOTYPE; full SAT, support, service and host checks required by caller",
        policy="Inherited active pitch, finite-body edge fit, bounded row count",
        radial_tolerance_mm=_TOLERANCE_MM, subsystems=specifications, layers=actual,
        effective_candidate_sha256=hashlib.sha256(json.dumps(
            effective, sort_keys=True, separators=(",", ":")).encode()).hexdigest())
    layout["metadata"]["optimization_refill"] = copy.deepcopy(diagnostics)
    return dict(layout=layout, candidate=effective, models=derived, diagnostics=diagnostics)
