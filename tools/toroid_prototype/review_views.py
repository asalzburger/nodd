"""PR87 scientific slice and straight-ray coverage views, PROTOTYPE only.

Run with the plotting Python described in tools/toroid_prototype/README.md:
  python -m tools.toroid_prototype.review_views --results RESULTS --field-map MAP

Coil membership uses the exact rounded-rectangle distance/slab masks, rather
than projecting every coil into one plane. Chambers are finite empty envelopes
whose complete radial (barrel) or axial (disk) depth must clear both coil
families. A shared cold/warm sweep union is a reservation, not an engineered
cryostat. Coverage describes straight IP rays and geometric reservations only;
it is not detection or reconstruction efficiency.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np

from .geometry import chamber_depth_mask, coil_mask
from .map import FieldMap
from .system import solenoid_parameters

ROOT = Path(__file__).resolve().parents[2]
INPUT_REVISION = "71406b09fa2d3fbfa119dba61e436f8fad1d11ac"
DEFAULT_RESULTS = ROOT/"docs/validation/DES-039/results.json"
DEFAULT_OUTPUT = ROOT/"docs/validation/DES-039/review-coverage"
STATUS = {
    0: "fewer than three geometric station crossings",
    1: "three crossings; at least one chamber envelope excluded",
    2: "three retained chamber hits; interstation warm reservation blocked",
    3: "three retained chamber hits and clear interstation path",
}
COLORS = {"warm": "#e9b875", "cold": "#7194bb", "pack": "#183854",
          "retained": "#86c6b3", "excluded": "#edb0aa"}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def configuration_hash(config):
    return hashlib.sha256(json.dumps(config, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_inputs(results_path=DEFAULT_RESULTS, map_path=None):
    """Load the executed configuration, including its actual energy-sized cold width."""
    path = Path(results_path)
    results = json.loads(path.read_text())
    if "configuration" not in results:
        raise ValueError("results must contain the normalized executed configuration")
    config = results["configuration"]
    for name in ("pack", "cold", "warm"):
        if any(config[name][axis] <= 0 for axis in ("normal_m", "tangent_m")):
            raise ValueError("executed coil widths must be positive")
    candidate = Path(map_path) if map_path is not None else path.parent/"joint-field.npz"
    field = FieldMap(candidate) if candidate.exists() else None
    if map_path is not None and field is None:
        raise FileNotFoundError(candidate)
    expected = results.get("map", {}).get("sha256")
    if field is not None and expected is not None and sha256(candidate) != expected:
        raise ValueError("field map does not match the executed results SHA-256")
    return results, config, field, candidate if field is not None else None


def slice_masks(points, config, clearance_m=.05, cell_bound_m=0.):
    """Exact coil slice masks and full-depth-clipped chamber volume membership.

    A raster point inside a chamber's empty volume is mapped back to that
    chamber's centre surface; its *whole* normal extrusion is then checked.
    cell_bound_m additionally encloses a displayed raster cell. No coil
    projection or fictitious radial disk-depth inflation is performed.
    """
    p = np.asarray(points, dtype=float)
    if p.ndim != 2 or p.shape[1] != 3 or not np.isfinite(p).all():
        raise ValueError("points must be finite Nx3 Cartesian coordinates")
    out = {name: coil_mask(p, config, width=name) for name in ("pack", "cold", "warm")}
    nominal = np.zeros(len(p), dtype=bool)
    retained = np.zeros(len(p), dtype=bool)
    excluded = np.zeros(len(p), dtype=bool)
    r = np.hypot(p[:, 0], p[:, 1])
    st = config["stations"]
    h = st["outline_thickness_m"]/2
    for radius, disk_z in zip(st["barrel_radii_m"], st["disk_abs_z_m"]):
        selections = [("B", (np.abs(r-radius) <= h) &
                        (np.abs(p[:, 2]) <= disk_z-st["barrel_end_shortening_m"]), 0)]
        for side in (-1, 1):
            selections.append(("D", (np.abs(p[:, 2]-side*disk_z) <= h) &
                               (r >= st["disk_inner_radius_m"]) & (r <= radius+h), side))
        for kind, select, side in selections:
            if not np.any(select):
                continue
            center = p[select].copy()
            if kind == "B":
                center[:, :2] *= radius/r[select, None]
                # Mapping a raster cell to the barrel's outer depth face can
                # enlarge its azimuthal extent. Bound that projection as well.
                bound = cell_bound_m*(radius+h)/(radius-h)
            else:
                center[:, 2] = side*disk_z
                bound = cell_bound_m
            blocked = chamber_depth_mask(center, config, kind, clearance=clearance_m,
                                          cell_bound_m=bound)
            nominal[select] = True
            retained[select] |= ~blocked
            excluded[select] |= blocked
    out.update(chamber_nominal=nominal, chamber_retained=retained,
               chamber_excluded=excluded)
    return out


def ray_station_points(eta, phi_deg, config):
    """Vectorized counterpart of geometry.station_intersections, retaining missing stations."""
    eta, phi_deg = np.broadcast_arrays(np.asarray(eta, float), np.asarray(phi_deg, float))
    if not np.isfinite(eta).all() or not np.isfinite(phi_deg).all():
        raise ValueError("eta and phi must be finite")
    eta, phi = eta.ravel(), np.radians(phi_deg.ravel())
    sh = np.sinh(np.abs(eta))
    sign = np.where(eta < 0, -1., 1.)
    st = config["stations"]
    h = st["outline_thickness_m"]/2
    points = np.full((len(eta), 3, 3), np.nan)
    kinds = np.full((len(eta), 3), "-", dtype="U1")
    for k, (radius, z) in enumerate(zip(st["barrel_radii_m"], st["disk_abs_z_m"] )):
        barrel = radius*sh <= z-st["barrel_end_shortening_m"]
        rd = np.divide(z, sh, out=np.full_like(sh, np.inf), where=sh > 0)
        disk = ~barrel & (rd >= st["disk_inner_radius_m"]) & (rd <= radius+h)
        r = np.where(barrel, radius, rd)
        zz = sign*np.where(barrel, radius*sh, z)
        exists = barrel | disk
        points[exists, k] = np.column_stack((r[exists]*np.cos(phi[exists]),
                                            r[exists]*np.sin(phi[exists]), zz[exists]))
        kinds[barrel, k] = "B"
        kinds[disk, k] = "D"
    return points, kinds


def interstation_blocked(start, end, config, clearance_m=.05, step_m=.01,
                         batch_rays=128):
    """Conservative sampled path test with a half-step mask guard.

    All segments are sampled at spacing <=step_m. Inflating the exact slab
    and distance masks by step_m/2 covers every point between samples, since
    both distance coordinates are 1-Lipschitz. The guard can reject an extra
    <=step_m/2 near a reservation; it cannot open a narrow sampled gap.
    """
    a, b = np.asarray(start, float), np.asarray(end, float)
    if a.shape != b.shape or a.ndim != 2 or a.shape[1] != 3 or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("path endpoints must be equally shaped finite Nx3 arrays")
    if step_m <= 0 or batch_rays < 1:
        raise ValueError("positive path sample step and batch size required")
    out = np.zeros(len(a), dtype=bool)
    lengths = np.linalg.norm(b-a, axis=1)
    for first in range(0, len(a), batch_rays):
        last = min(len(a), first+batch_rays)
        n = np.maximum(1, np.ceil(lengths[first:last]/step_m).astype(int))
        j = np.arange(n.max()+1)
        active = j[None, :] <= n[:, None]
        t = np.minimum(j[None, :]/n[:, None], 1.)
        p = a[first:last, None, :] + t[:, :, None]*(b[first:last]-a[first:last])[:, None, :]
        hit = np.zeros(active.shape, bool)
        hit[active] = coil_mask(p[active], config, width="warm",
                                clearance=clearance_m+step_m/2)
        out[first:last] = hit.any(axis=1)
    return out


def classify_rays(eta, phi_deg, config, clearance_m=.05, path_step_m=.01):
    """Separate reference crossings, retained chamber envelopes and intervening reservations."""
    points, kinds = ray_station_points(eta, phi_deg, config)
    exists = kinds != "-"
    hit_blocked = np.zeros(kinds.shape, dtype=bool)
    for station in range(3):
        for kind in ("B", "D"):
            take = kinds[:, station] == kind
            if take.any():
                hit_blocked[take, station] = chamber_depth_mask(
                    points[take, station], config, kind, clearance=clearance_m)
    nominal_count = exists.sum(axis=1)
    retained_count = (exists & ~hit_blocked).sum(axis=1)
    has_three = nominal_count == 3
    path_blocked = np.zeros(len(points), bool)
    # Check every nominal three-hit ray independently of chamber exclusions,
    # so diagnostics do not conflate the two distinct obstructions.
    if has_three.any():
        path_blocked[has_three] = interstation_blocked(
            points[has_three, 0], points[has_three, 2], config,
            clearance_m=clearance_m, step_m=path_step_m)
    status = np.zeros(len(points), dtype=np.uint8)
    status[has_three] = 1
    three_retained = retained_count == 3
    status[three_retained & path_blocked] = 2
    status[three_retained & ~path_blocked] = 3
    retained = exists & ~hit_blocked
    upstream_checked = retained.any(axis=1)
    upstream_blocked = np.zeros(len(points), bool)
    if upstream_checked.any():
        first = np.argmax(retained[upstream_checked], axis=1)
        end = points[upstream_checked, first]
        upstream_blocked[upstream_checked] = interstation_blocked(
            np.zeros_like(end), end, config, clearance_m=clearance_m, step_m=path_step_m)
    return {"points_m": points, "kinds": kinds, "surface_count": nominal_count,
            "retained_count": retained_count, "hit_blocked": hit_blocked,
            "path_blocked": path_blocked, "status": status,
            "upstream_checked": upstream_checked, "upstream_blocked": upstream_blocked}


def interpolate_field_partial(field, points):
    """Return Cartesian B, leaving invalid/outside interpolation stencils as NaN."""
    p = np.asarray(points, float)
    coordinates = (np.hypot(p[:, 0], p[:, 1]), p[:, 2],
                   np.degrees(np.arctan2(p[:, 1], p[:, 0])) % 30)
    axes = (field.r, field.z, field.phi)
    inside = np.ones(len(p), bool)
    indices = []
    for q, axis in zip(coordinates, axes):
        inside &= (q >= axis[0]) & (q <= axis[-1])
        indices.append(np.clip(np.searchsorted(axis, q, side="right")-1, 0, len(axis)-2))
    valid = inside.copy()
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                cell = tuple(i+k for i, k in zip(indices, (a, b, c)))
                valid &= field.valid[cell] & np.isfinite(field.b[cell]).all(axis=1)
    out = np.full((len(p), 3), np.nan)
    if valid.any():
        out[valid] = field.field(p[valid])
    return out


def _edges(start, stop, step):
    if step <= 0 or stop <= start:
        raise ValueError("positive step and ordered domain required")
    return np.linspace(start, stop, math.ceil((stop-start)/step)+1)


def coverage_scan(config, eta_step=.025, phi_step_deg=.5, path_step_m=.01,
                   clearance_m=.05):
    """Cell-centre rays spanning eta 0..3 and one complete 30-degree sector."""
    ee, pe = _edges(0, 3, eta_step), _edges(0, 30, phi_step_deg)
    ec, pc = (ee[:-1]+ee[1:])/2, (pe[:-1]+pe[1:])/2
    eta, phi = np.meshgrid(ec, pc, indexing="ij")
    arrays = classify_rays(eta.ravel(), phi.ravel(), config,
                           clearance_m=clearance_m, path_step_m=path_step_m)
    weights = np.diff(np.tanh(ee))[:, None]*np.radians(np.diff(pe))[None, :]
    shape = eta.shape
    def summary(select):
        status = arrays["status"].reshape(shape)[select]
        w = weights[select]
        surface = arrays["surface_count"].reshape(shape)[select] == 3
        retained = arrays["retained_count"].reshape(shape)[select] == 3
        upstream = arrays["upstream_blocked"].reshape(shape)[select]
        checked = arrays["upstream_checked"].reshape(shape)[select]
        total = float(w.sum())
        return {"ray_count": int(status.size), "solid_angle_sr": total,
                "status_counts": {str(code): int((status == code).sum()) for code in STATUS},
                "three_surface_count": int(surface.sum()),
                "three_retained_count": int(retained.sum()),
                "three_clear_path_count": int((status == 3).sum()),
                "upstream_checked_count": int(checked.sum()),
                "upstream_shadow_count": int(upstream.sum()),
                "three_clear_path_with_upstream_shadow_count": int(((status == 3) & upstream).sum()),
                "solid_angle_weighted_three_surface_fraction": float(w[surface].sum()/total),
                "solid_angle_weighted_three_retained_fraction": float(w[retained].sum()/total),
                "solid_angle_weighted_three_clear_path_fraction": float(w[status == 3].sum()/total),
                "solid_angle_weighted_upstream_shadow_fraction": float(w[upstream].sum()/total),
                "solid_angle_weighted_three_clear_path_and_upstream_clear_fraction":
                    float(w[(status == 3) & ~upstream].sum()/total)}
    bands = []
    for lo, hi in zip((0, .8, 1.2, 1.6, 2., 2.5), (.8, 1.2, 1.6, 2., 2.5, 3.)):
        # Default grid aligns with these boundaries. Report the actual covered
        # cell edges for other CLI step choices rather than inventing subcells.
        take = (ec >= lo) & (ec < hi)
        if take.any():
            value = summary(take)
            value.update(eta_min=float(ee[np.flatnonzero(take)[0]]),
                         eta_max=float(ee[np.flatnonzero(take)[-1]+1]))
            bands.append(value)
    report = {"status": "PROTOTYPE / geometric straight-ray diagnostic; not reconstruction efficiency",
              "status_codes": {str(k): v for k, v in STATUS.items()},
              "eta_edges": ee.tolist(), "phi_edges_deg": pe.tolist(),
              "sample_convention": "one ray per eta-phi cell centre; no duplicate periodic endpoint",
              "grid_shape_eta_phi": list(shape), "clearance_to_warm_m": clearance_m,
              "chamber_depth_sample_max_step_m": .025,
              "path_sample_max_step_m": path_step_m,
              "path_half_step_guard_m": path_step_m/2,
              "solid_angle_weight": "dOmega=dphi*(tanh(eta_high)-tanh(eta_low)); conditional on eta0..3",
              "summary": summary(np.ones(len(ec), bool)), "eta_bands": bands,
              "arrays": {key: arrays[key].reshape(shape).tolist() for key in
                         ("surface_count", "retained_count", "path_blocked", "status",
                          "upstream_checked", "upstream_blocked")},
              "scope": ["Straight IP rays and empty station envelopes only.",
                        "All nine nominal chamber envelopes; no chamber internals or detector response.",
                        "The path criterion concerns only first-to-last station, not material before the first station.",
                        "Upstream toroid-coil shadow is separately tested from the IP to the first retained station; it does not alter the three-hit status.",
                        "Warm coil-following sweeps are reservations; the shared endcap pressure vessel remains unengineered.",
                        "Numerical ray and raster sampling are diagnostics, not continuum acceptance bounds."]}
    rows = []
    for index, (e, p) in enumerate(zip(eta.ravel(), phi.ravel())):
        rows.append({"eta": float(e), "phi_deg": float(p),
                     "station_types": "".join(arrays["kinds"][index]),
                     "surface_count": int(arrays["surface_count"][index]),
                     "retained_count": int(arrays["retained_count"][index]),
                     "path_blocked": bool(arrays["path_blocked"][index]),
                     "upstream_checked": bool(arrays["upstream_checked"][index]),
                     "upstream_blocked": bool(arrays["upstream_blocked"][index]),
                     "status": int(arrays["status"][index])})
    return report, rows


def _draw_slice(ax, u, v, points, config, field, pixel_bound_m):
    masks = slice_masks(points, config, cell_bound_m=pixel_bound_m)
    shape = (len(v), len(u))
    if field is not None:
        b = interpolate_field_partial(field, points)
        magnitude = np.linalg.norm(b, axis=1)
        magnitude[masks["warm"]] = np.nan
        grid = magnitude.reshape(shape)
        finite = grid[np.isfinite(grid)]
        levels = [x for x in (.25, .5, 1., 1.5, 2., 3., 4.)
                  if len(finite) and finite.min() < x < finite.max()]
        if levels:
            contours = ax.contour(u, v, grid, levels=levels, colors="#526173", linewidths=.55, alpha=.65)
            ax.clabel(contours, fmt="%g T", fontsize=6, inline_spacing=2)
    for key in ("chamber_excluded", "chamber_retained", "warm", "cold", "pack"):
        mask = masks[key].reshape(shape)
        if mask.any():
            color = COLORS[key.removeprefix("chamber_")]
            ax.contourf(u, v, mask.astype(int), levels=[.5, 1.5], colors=[color], alpha=.92)
            if (~mask).any():
                ax.contour(u, v, mask.astype(int), levels=[.5], colors=[color], linewidths=.45)
    ax.set_aspect("equal")
    ax.grid(color="#d9dfe5", linewidth=.35, alpha=.7)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=8)


def _legend(figure, field_present):
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    handles = [Patch(facecolor=COLORS["pack"], label="Finite winding pack"),
               Patch(facecolor=COLORS["cold"], label="Energy-sized cold allocation"),
               Patch(facecolor=COLORS["warm"], label="Warm coil / case reservation"),
               Patch(facecolor=COLORS["retained"], label="Retained whole-depth chamber envelope"),
               Patch(facecolor=COLORS["excluded"], label="Excluded nominal chamber footprint")]
    if field_present:
        handles.append(Line2D([0], [0], color="#526173", linewidth=.7,
                              label="Joint vacuum |B| contours (masked)"))
    handles.extend([Line2D([0], [0], color="#815588", linestyle="-.", linewidth=1.,
                           label="Pinned solenoid vessel envelope"),
                    Line2D([0], [0], color="#7a7c81", linestyle="--", linewidth=.9,
                           label="HCAL outer bounds only")])
    figure.legend(handles=handles, loc="lower center", ncol=3, fontsize=9,
                  frameon=False, bbox_to_anchor=(.5, .035))


def _draw_context(ax, config, solenoid, kind, coordinate):
    """Unfilled pinned vessel and HCAL bounding outlines; no magnetic-steel claim."""
    from matplotlib.patches import Circle, Rectangle
    hcal = config.get("hcal", {})
    if kind == "XY":
        if abs(coordinate) <= solenoid["vessel_length_m"]/2:
            for radius in (solenoid["vessel_inner_radius_m"], solenoid["vessel_outer_radius_m"]):
                ax.add_patch(Circle((0, 0), radius, fill=False, color="#815588", linestyle="-.", linewidth=1.))
        radius = None
        if hcal and abs(coordinate) <= hcal["barrel_half_z_m"]:
            radius = hcal["barrel_corner_radius_m"]
        if hcal and hcal["endcap_front_abs_z_m"] <= abs(coordinate) <= hcal["endcap_back_abs_z_m"]:
            radius = hcal["endcap_outer_corner_radius_m"]
        if radius is not None:
            ax.add_patch(Circle((0, 0), radius, fill=False, color="#7a7c81", linestyle="--", linewidth=.9))
    elif kind == "RZ":
        ax.add_patch(Rectangle((-solenoid["vessel_length_m"]/2, solenoid["vessel_inner_radius_m"]),
                               solenoid["vessel_length_m"],
                               solenoid["vessel_outer_radius_m"]-solenoid["vessel_inner_radius_m"],
                               fill=False, color="#815588", linestyle="-.", linewidth=1.))
        if hcal:
            def outer_bound(lo, hi, radius):
                # Open at R=0: this is the outer bound, not an invented inner
                # aperture or a filled calorimeter/magnetic material model.
                ax.plot([lo, lo, hi, hi], [0, radius, radius, 0], color="#7a7c81",
                         linestyle="--", linewidth=.9)
            outer_bound(-hcal["barrel_half_z_m"], hcal["barrel_half_z_m"], hcal["barrel_corner_radius_m"])
            for side in (-1, 1):
                front, back = sorted((side*hcal["endcap_front_abs_z_m"], side*hcal["endcap_back_abs_z_m"]))
                outer_bound(front, back, hcal["endcap_outer_corner_radius_m"])
    else:
        raise ValueError("context kind must be XY or RZ")


def plot_slices(config, field, output, step_m=.025, solenoid=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    solenoid = solenoid_parameters() if solenoid is None else solenoid
    maximum_r = float(config["map"]["r_max_m"])
    maximum_z = max(abs(config["map"]["z_min_m"]), abs(config["map"]["z_max_m"]))
    q = _edges(-maximum_r, maximum_r, step_m)
    xx, yy = np.meshgrid(q, q)
    slices = [0.] + [-float(z) for z in config["stations"]["disk_abs_z_m"]]
    slices += [float(z) for z in config["stations"]["disk_abs_z_m"]]
    figure, axes = plt.subplots(2, 4, figsize=(20, 11))
    for ax, z in zip(axes.ravel(), slices):
        p = np.column_stack((xx.ravel(), yy.ravel(), np.full(xx.size, z)))
        _draw_slice(ax, q, q, p, config, field, step_m/math.sqrt(2))
        _draw_context(ax, config, solenoid, "XY", z)
        ax.set_title(f"z = {z:g} m — actual XY slice", fontsize=11)
        ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]")
    for ax in axes.ravel()[len(slices):]:
        ax.axis("off")
        ax.text(.03, .9, f"FINITE ENVELOPES\n\nCurrent pack, cold allocation and\nwarm reservation are distinct.\n\n{config['stations']['outline_thickness_m']*1000:g} mm chambers are empty outlines.\nEntire normal depth plus 50 mm\nclearance must avoid warm sweeps.\n\nShared endcap vessel, supports and\nmaterial response remain unresolved.",
                transform=ax.transAxes, va="top", fontsize=11, linespacing=1.5)
    figure.suptitle("DES-039 · Twelvefold toroid and chamber reservations\nSlices through the finite geometry; no all-azimuth coil projection", fontsize=16, y=.98)
    _legend(figure, field is not None)
    figure.text(.07, .018, "Shared cold/warm sleeve union is a geometric allocation; a common endcap vessel is unengineered. Chambers have no internals.", fontsize=9)
    figure.subplots_adjust(left=.05, right=.985, top=.91, bottom=.16, wspace=.25, hspace=.25)
    figure.savefig(output/"xy-envelope.png", dpi=160)
    plt.close(figure)
    r = _edges(0, maximum_r, step_m)
    z = _edges(-maximum_z, maximum_z, step_m)
    zz, rr = np.meshgrid(z, r)
    figure, axes = plt.subplots(3, 1, figsize=(15, 15))
    for ax, phi_deg in zip(axes, (0, 7.5, 15)):
        phi = math.radians(phi_deg)
        p = np.column_stack((rr.ravel()*math.cos(phi), rr.ravel()*math.sin(phi), zz.ravel()))
        _draw_slice(ax, z, r, p, config, field, step_m/math.sqrt(2))
        _draw_context(ax, config, solenoid, "RZ", phi_deg)
        ax.set_title(f"φ = {phi_deg:g}° — actual meridional slice", fontsize=12)
        ax.set_xlabel("z [m]"); ax.set_ylabel("R [m]")
    figure.suptitle("DES-039 · R–Z slices of finite coil and chamber envelopes\nBoth endcaps shown; coil sweeps outside each azimuthal plane are absent", fontsize=16, y=.985)
    _legend(figure, field is not None)
    figure.text(.07, .018, "Shared cold/warm sleeve union is a reservation; a common endcap vessel is unengineered. Chambers have no internals.", fontsize=9)
    figure.subplots_adjust(left=.07, right=.98, top=.93, bottom=.13, hspace=.3)
    figure.savefig(output/"rz-envelope.png", dpi=160)
    plt.close(figure)


def plot_coverage(report, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap, BoundaryNorm
    status = np.asarray(report["arrays"]["status"])
    retained = np.asarray(report["arrays"]["retained_count"])
    surface = np.asarray(report["arrays"]["surface_count"])
    ee, pe = np.array(report["eta_edges"]), np.array(report["phi_edges_deg"])
    figure, axes = plt.subplots(4, 1, figsize=(14, 14), gridspec_kw={"height_ratios": [1, 1, 1, .85]})
    colors = ["#e0e5ea", "#d78e84", "#e2bd70", "#468c77"]
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(np.arange(-.5, 4), 4)
    image = axes[0].pcolormesh(ee, pe, status.T, cmap=cmap, norm=norm, shading="flat", rasterized=True)
    bar = figure.colorbar(image, ax=axes[0], ticks=range(4), pad=.015, fraction=.025)
    bar.ax.set_yticklabels(["<3 surfaces", "chamber cutout", "path blocked", "3 hits + clear path"], fontsize=9)
    axes[0].set_title("Three geometric surfaces, whole-depth chamber cutouts and interstation clearance are separate tests", fontsize=11)
    image = axes[1].pcolormesh(ee, pe, retained.T, cmap=ListedColormap(["#e0e5ea", "#c7d5df", "#83acba", "#357c86"]),
                               norm=norm, shading="flat", rasterized=True)
    figure.colorbar(image, ax=axes[1], ticks=range(4), pad=.015, fraction=.025,
                    label="Retained chamber outlines crossed")
    axes[1].set_title("Retained station envelopes crossed, before requiring a clear path between stations", fontsize=11)
    ec = (ee[:-1]+ee[1:])/2
    checked = np.asarray(report["arrays"]["upstream_checked"])
    upstream = np.asarray(report["arrays"]["upstream_blocked"])
    upstream_status = np.where(checked, np.where(upstream, 2, 1), 0)
    image = axes[2].pcolormesh(ee, pe, upstream_status.T,
                              cmap=ListedColormap(["#e0e5ea", "#c5d9d2", "#d78e84"]),
                              norm=BoundaryNorm(np.arange(-.5, 3), 3), shading="flat", rasterized=True)
    bar = figure.colorbar(image, ax=axes[2], ticks=range(3), pad=.015, fraction=.025)
    bar.ax.set_yticklabels(["no retained hit", "no coil shadow", "upstream shadow"], fontsize=9)
    axes[2].set_title("Separate upstream toroid-reservation shadow: IP to first retained hit; does not veto the three-hit status above", fontsize=10)
    axes[3].plot(ec, (surface == 3).mean(axis=1), color="#566775", label="3 reference surfaces")
    axes[3].plot(ec, (retained == 3).mean(axis=1), color="#357c86", label="3 retained chamber envelopes")
    axes[3].plot(ec, (status == 3).mean(axis=1), color="#468c77", label="3 retained hits + clear path")
    if "comparison" in report:
        before = report["comparison"]["before"]
        old = np.array(before["arrays"]["status"])
        old_eta = np.array(before["eta_edges"])
        axes[3].plot((old_eta[:-1]+old_eta[1:])/2, (old == 3).mean(axis=1),
                     color="#8a626b", linestyle="--", label="PR87 input: 3 hits + clear path")
    axes[3].set_ylim(0, 1.05); axes[3].set_xlim(0, 3)
    axes[3].set_ylabel("Fraction of sampled φ cells")
    axes[3].legend(loc="lower left", frameon=False, fontsize=9, ncol=2)
    for ax in axes[:3]:
        ax.set_ylabel("φ [degrees]"); ax.set_ylim(0, 30)
    for ax in axes:
        ax.set_xlabel("η"); ax.grid(alpha=.2, linewidth=.5)
    summary = report["summary"]
    figure.suptitle("DES-039 · Geometric chamber and coil-reservation coverage\nStraight IP rays over η = 0…3 and one complete 30° sector", fontsize=16, y=.98)
    figure.text(.07, .035,
                "Solid-angle weighted within η0…3: "
                f"3 surfaces {summary['solid_angle_weighted_three_surface_fraction']:.1%}; "
                f"3 retained envelopes {summary['solid_angle_weighted_three_retained_fraction']:.1%}; "
                f"3 hits + clear path {summary['solid_angle_weighted_three_clear_path_fraction']:.1%}.\n"
                "Geometry diagnostic only: no efficiency, scattering, chamber internals or engineered common endcap vessel.",
                fontsize=10, linespacing=1.5)
    figure.subplots_adjust(left=.07, right=.86, bottom=.13, top=.9, hspace=.4)
    figure.savefig(output/"coverage.png", dpi=170)
    plt.close(figure)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--field-map", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--slice-step-m", type=float, default=.025)
    parser.add_argument("--eta-step", type=float, default=.025)
    parser.add_argument("--phi-step-deg", type=float, default=.5)
    parser.add_argument("--path-step-m", type=float, default=.01)
    comparison = parser.add_mutually_exclusive_group()
    comparison.add_argument("--baseline-results", type=Path)
    comparison.add_argument("--baseline-revision")
    args = parser.parse_args()
    start = time.perf_counter()
    results, config, field, map_path = load_inputs(args.results, args.field_map)
    args.output.mkdir(parents=True, exist_ok=True)
    report, rows = coverage_scan(config, args.eta_step, args.phi_step_deg, args.path_step_m)
    coarse, _ = coverage_scan(config, 2*args.eta_step, 2*args.phi_step_deg, args.path_step_m)
    report["sampling_sensitivity"] = {
        "scope": "Identical geometry/path test; compare cell-centre angular sampling. Differences are not rigorous continuum bounds.",
        "fine_requested_steps": {"eta": args.eta_step, "phi_deg": args.phi_step_deg},
        "coarse_requested_steps": {"eta": 2*args.eta_step, "phi_deg": 2*args.phi_step_deg},
        "after_fine": report["summary"], "after_coarse": coarse["summary"]}
    if args.baseline_results is not None or args.baseline_revision is not None:
        if args.baseline_results is not None:
            content = args.baseline_results.read_bytes()
            baseline_locator = str(args.baseline_results)
        else:
            baseline_locator = args.baseline_revision+":docs/validation/DES-039/results.json"
            content = subprocess.check_output(["git", "show", baseline_locator], cwd=ROOT)
        baseline = json.loads(content)
        before_config = baseline.get("configuration", baseline)
        before, _ = coverage_scan(before_config, args.eta_step, args.phi_step_deg, args.path_step_m)
        before_coarse, _ = coverage_scan(before_config, 2*args.eta_step, 2*args.phi_step_deg, args.path_step_m)
        report["sampling_sensitivity"].update(before_fine=before["summary"], before_coarse=before_coarse["summary"])
        report["comparison"] = {"before": before, "before_configuration": before_config,
                                 "before_configuration_sha256": configuration_hash(before_config),
                                 "before_source": baseline_locator,
                                 "before_source_sha256": hashlib.sha256(content).hexdigest(),
                                 "scope": "Same cell-centre rays, warm clearance and full-depth masks; geometry only, independent of current or field map."}
    pinned_solenoid = results.get("solenoid_pinned_parameters", solenoid_parameters())
    plot_slices(config, field, args.output, args.slice_step_m, pinned_solenoid)
    plot_coverage(report, args.output)
    import matplotlib
    report["provenance"] = {"assignment_input_revision": INPUT_REVISION,
                            "source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                            "configuration": config, "configuration_sha256": configuration_hash(config),
                            "results_path": str(args.results), "results_sha256": sha256(args.results),
                            "field_map_path": str(map_path) if map_path is not None else None,
                            "field_map_sha256": sha256(map_path) if map_path is not None else None,
                            "source_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in
                                              (Path(__file__), Path(__file__).with_name("geometry.py"),
                                               Path(__file__).with_name("map.py"),
                                               Path(__file__).with_name("system.py"),
                                               Path(__file__).with_name("solenoid-input.json"))},
                            "python": platform.python_version(), "python_executable": sys.executable,
                            "numpy": np.__version__, "matplotlib": matplotlib.__version__,
                            "slice_raster_step_m": args.slice_step_m,
                            "slice_cell_bound_m": args.slice_step_m/math.sqrt(2),
                            "slice_barrel_cell_bound": "base cell bound multiplied by (R+h)/(R-h) to cover outer-depth-face projection",
                            "pinned_solenoid_vessel_parameters": pinned_solenoid,
                            "HCAL_context": "unfilled outer bounds only; no invented inner aperture and no magnetic-steel solution",
                            "field_contours": "joint vacuum magnitude; invalid interpolation stencils and warm reservations masked",
                            "elapsed_seconds": time.perf_counter()-start,
                            "command": "python -m tools.toroid_prototype.review_views " + " ".join(sys.argv[1:])}
    with (args.output/"coverage.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    (args.output/"coverage.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
