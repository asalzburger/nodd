"""PROTOTYPE vacuum magnetostatics from closed polygonal current loops, SI.

Each straight segment is integrated exactly, for both B and the Coulomb-gauge
vector potential A. Curved windings and finite current-density packs are
discretized explicitly; convergence in both discretizations remains the caller's
responsibility. There is no iron model and no artificial wire-radius softening.
Points on a source filament are returned as NaN. A finite pack is represented by
quadrature filaments and must not be interpreted as resolving conductor interiors.

The optional local C++ backend is built from the checked-in source with the system
C++ compiler into the repository's ignored build/ directory. NumPy is the only
Python dependency; backend='numpy' never invokes a compiler.
"""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
import hashlib
import math
import os
from pathlib import Path
import shutil
import subprocess
import warnings

import numpy as np

MU0 = 4.0e-7 * math.pi
K = MU0 / (4.0 * math.pi)


@dataclass(frozen=True)
class SegmentSources:
    """Directed endpoints, signed ampere-turns and named source-group indices."""

    a: np.ndarray
    b: np.ndarray
    current_Aturn: np.ndarray
    group: np.ndarray
    group_names: tuple[str, ...] = ("coil",)

    def __post_init__(self):
        a = np.ascontiguousarray(self.a, dtype=np.float64)
        b = np.ascontiguousarray(self.b, dtype=np.float64)
        current = np.ascontiguousarray(self.current_Aturn, dtype=np.float64)
        group = np.ascontiguousarray(self.group, dtype=np.int32)
        if a.ndim != 2 or a.shape[1:] != (3,) or b.shape != a.shape:
            raise ValueError("segment endpoints must both have shape (N, 3)")
        if current.shape != (len(a),) or group.shape != (len(a),):
            raise ValueError("current and group arrays must have shape (N,)")
        if not all(np.isfinite(x).all() for x in (a, b, current)):
            raise ValueError("source coordinates and currents must be finite")
        if np.any(np.linalg.norm(b - a, axis=1) == 0):
            raise ValueError("zero-length current segment")
        if not self.group_names or len(set(self.group_names)) != len(self.group_names):
            raise ValueError("source group names must be nonempty and unique")
        if len(group) and (group.min() < 0 or group.max() >= len(self.group_names)):
            raise ValueError("source group index outside group_names")
        for key, value in (("a", a), ("b", b), ("current_Aturn", current), ("group", group)):
            object.__setattr__(self, key, value)
        object.__setattr__(self, "group_names", tuple(self.group_names))

    def scaled(self, factor: float) -> "SegmentSources":
        return SegmentSources(self.a, self.b, self.current_Aturn * factor,
                              self.group, self.group_names)

    def transformed(self, rotation=None, translation=None) -> "SegmentSources":
        """Return rigidly transformed endpoints; rotation acts on column vectors."""
        matrix = np.eye(3) if rotation is None else np.asarray(rotation, dtype=float)
        shift = np.zeros(3) if translation is None else np.asarray(translation, dtype=float)
        if matrix.shape != (3, 3) or shift.shape != (3,):
            raise ValueError("rotation is 3 x 3 and translation has three components")
        if not np.allclose(matrix.T @ matrix, np.eye(3), atol=1e-12, rtol=0):
            raise ValueError("rotation must be orthogonal")
        if np.linalg.det(matrix) < 0:
            raise ValueError("rotation must preserve orientation")
        return SegmentSources(self.a @ matrix.T + shift, self.b @ matrix.T + shift,
                              self.current_Aturn, self.group, self.group_names)


def concatenate_sources(sources) -> SegmentSources:
    """Merge sources and coalesce identical group names in first-occurrence order."""
    sources = list(sources)
    if not sources:
        raise ValueError("at least one source is required")
    names = tuple(dict.fromkeys(name for source in sources for name in source.group_names))
    groups = []
    for source in sources:
        remap = np.array([names.index(name) for name in source.group_names], dtype=np.int32)
        groups.append(remap[source.group])
    return SegmentSources(np.concatenate([s.a for s in sources]),
                          np.concatenate([s.b for s in sources]),
                          np.concatenate([s.current_Aturn for s in sources]),
                          np.concatenate(groups), names)


def polyline_sources(vertices, current_Aturn, group="coil", closed=True) -> SegmentSources:
    """Create directed segments; an explicitly repeated closing point is accepted."""
    vertices = np.asarray(vertices, dtype=float)
    if vertices.ndim != 2 or vertices.shape[1:] != (3,) or len(vertices) < 2:
        raise ValueError("vertices must have shape (N >= 2, 3)")
    if closed and not np.array_equal(vertices[0], vertices[-1]):
        vertices = np.vstack((vertices, vertices[0]))
    n = len(vertices) - 1
    return SegmentSources(vertices[:-1], vertices[1:], np.full(n, current_Aturn),
                          np.zeros(n, dtype=np.int32), (group,))


def gauss_rule(width_m: float, order: int):
    """Offsets and weights normalized to one for a uniform full-width interval."""
    if not np.isfinite(width_m) or width_m < 0 or int(order) != order or order < 1:
        raise ValueError("quadrature width must be nonnegative and order a positive integer")
    if width_m == 0:
        return np.array([0.0]), np.array([1.0])
    nodes, weights = np.polynomial.legendre.leggauss(int(order))
    return nodes * width_m / 2, weights / 2


def rounded_racetrack_vertices(center_r_m, center_z_m, half_r_m, half_z_m,
                               corner_radius_m, phi_rad=0.0, normal_offset_m=0.0,
                               tangent_offset_m=0.0, corner_segments=8):
    """Closed racetrack in a meridional plane, including parallel-pack offsets.

    Positive current gives +e_phi field inside its window. The full current-pack
    width normal to the path changes both half-extents and the corner radius;
    the tangential coordinate is a translation along e_phi. Arc segmentation is
    polygonal, whereas straight sides are exact. Return vertices without a
    duplicate endpoint so polyline_sources can close the loop.
    """
    hr, hz, cr = (half_r_m + normal_offset_m, half_z_m + normal_offset_m,
                  corner_radius_m + normal_offset_m)
    if (not np.isfinite([center_r_m, center_z_m, hr, hz, cr, phi_rad,
                         tangent_offset_m]).all() or hr <= 0 or hz <= 0
            or cr <= 0 or cr > min(hr, hz) or center_r_m <= hr):
        raise ValueError("racetrack requires positive radius, extents and fitting corners")
    if int(corner_segments) != corner_segments or corner_segments < 1:
        raise ValueError("corner_segments must be a positive integer")
    corners = ((hr-cr, hz-cr, 0), (-hr+cr, hz-cr, math.pi/2),
               (-hr+cr, -hz+cr, math.pi), (hr-cr, -hz+cr, 3*math.pi/2))
    rz = []
    for r, z, angle in corners:
        theta = np.linspace(angle, angle+math.pi/2, int(corner_segments)+1)
        rz.extend(zip(center_r_m+r+cr*np.cos(theta), center_z_m+z+cr*np.sin(theta)))
    # Arc joins coincide only if a straight side has exactly zero length.
    clean = [rz[0]]
    for point in rz[1:]:
        if np.linalg.norm(np.subtract(point, clean[-1])) > 1e-14:
            clean.append(point)
    if np.linalg.norm(np.subtract(clean[0], clean[-1])) <= 1e-14:
        clean.pop()
    rz = np.asarray(clean[::-1])  # +e_phi normal, rather than -e_phi.
    cosine, sine = math.cos(phi_rad), math.sin(phi_rad)
    return np.column_stack((rz[:, 0]*cosine-tangent_offset_m*sine,
                            rz[:, 0]*sine+tangent_offset_m*cosine, rz[:, 1]))


def rounded_racetrack_sources(center_r_m, center_z_m, half_r_m, half_z_m,
                              corner_radius_m, phi_rad, current_Aturn,
                              pack_normal_m=0.0, pack_tangent_m=0.0,
                              quadrature_order=2, corner_segments=8,
                              group="coil") -> SegmentSources:
    """Uniform finite rectangular winding pack approximated by product quadrature.

    current_Aturn is the total signed ampere-turns, not a per-filament current.
    quadrature_order is an integer or (normal, tangent) pair. Use disjoint
    quadratures for Neumann self-energy evaluation, e.g. source=2 and target=3;
    identical source/target filaments have singular line self-integrals.
    """
    order = ((quadrature_order, quadrature_order) if np.isscalar(quadrature_order)
             else tuple(quadrature_order))
    if len(order) != 2:
        raise ValueError("quadrature_order is an integer or two integers")
    normals, wn = gauss_rule(pack_normal_m, order[0])
    tangents, wt = gauss_rule(pack_tangent_m, order[1])
    loops = []
    for normal, weight_n in zip(normals, wn):
        for tangent, weight_t in zip(tangents, wt):
            vertices = rounded_racetrack_vertices(
                center_r_m, center_z_m, half_r_m, half_z_m, corner_radius_m,
                phi_rad, normal, tangent, corner_segments)
            loops.append(polyline_sources(vertices, current_Aturn*weight_n*weight_t, group))
    return concatenate_sources(loops)


def circular_loop_sources(radius_m, z_m, current_Aturn, segments=128,
                          group="solenoid") -> SegmentSources:
    """Polygon approximation to an xy circular loop; positive current gives +Bz."""
    if not np.isfinite([radius_m, z_m, current_Aturn]).all() or radius_m <= 0:
        raise ValueError("loop radius must be positive and inputs finite")
    if int(segments) != segments or segments < 4:
        raise ValueError("a circular polygon requires at least four segments")
    phi = 2*math.pi*np.arange(int(segments))/segments
    return polyline_sources(np.column_stack((radius_m*np.cos(phi), radius_m*np.sin(phi),
                                             np.full(int(segments), z_m))),
                            current_Aturn, group)


def _numpy_evaluate(points, sources, want_b, want_a, by_group, point_chunk, segment_chunk):
    groups = len(sources.group_names) if by_group else 1
    b_out = np.zeros((len(points), groups, 3)) if want_b else None
    a_out = np.zeros((len(points), groups, 3)) if want_a else None
    direction = sources.b - sources.a
    lengths = np.linalg.norm(direction, axis=1)
    unit = direction / lengths[:, None]
    with np.errstate(divide="ignore", invalid="ignore"):
        for start in range(0, len(points), point_chunk):
            stop = min(start + point_chunk, len(points))
            for first in range(0, len(sources.a), segment_chunk):
                last = min(first + segment_chunk, len(sources.a))
                w = points[start:stop, None, :] - sources.a[None, first:last]
                u = unit[first:last]
                length = lengths[first:last]
                axial = np.einsum("psj,sj->ps", w, u)
                radial = w - axial[:, :, None]*u
                rho2 = np.einsum("psj,psj->ps", radial, radial)
                ra = np.sqrt(rho2 + axial*axial)
                tail = axial-length
                rb = np.sqrt(rho2 + tail*tail)
                # Round-off tolerance only, not a physical wire radius.
                tolerance = 32*np.finfo(float).eps*np.maximum(1, length)
                on_axis = rho2 <= tolerance*tolerance
                singular = on_axis & (axial >= -tolerance) & (tail <= tolerance)
                current = K*sources.current_Aturn[first:last]
                active = sources.current_Aturn[first:last] != 0
                singular &= active[None, :]
                if want_b:
                    coefficient = np.divide(axial/ra-tail/rb, rho2,
                                            out=np.zeros_like(rho2), where=~on_axis)
                    values_b = np.cross(u[None, :, :], radial)*coefficient[:, :, None]
                    values_b *= current[None, :, None]
                    values_b[singular] = np.nan
                if want_a:
                    # log1p(2 L / (ra+rb-L)), with its small denominator
                    # rationalized so near-filament subtraction stays stable.
                    denominator = (rho2/(ra+np.abs(axial)) + rho2/(rb+np.abs(tail))
                                   + 2*np.maximum(-axial, 0) + 2*np.maximum(tail, 0))
                    integral = np.log1p(2*length/denominator)
                    outside = on_axis & ~singular
                    # Exact on-line exterior integral; avoids infinity-infinity.
                    integral[outside] = np.abs(np.log(ra[outside]/rb[outside]))
                    values_a = u[None, :, :]*integral[:, :, None]*current[None, :, None]
                    values_a[:, ~active, :] = 0
                    values_a[singular] = np.nan
                if by_group:
                    for group in np.unique(sources.group[first:last]):
                        selected = sources.group[first:last] == group
                        if want_b:
                            b_out[start:stop, group] += values_b[:, selected].sum(axis=1)
                        if want_a:
                            a_out[start:stop, group] += values_a[:, selected].sum(axis=1)
                else:
                    if want_b:
                        b_out[start:stop, 0] += values_b.sum(axis=1)
                    if want_a:
                        a_out[start:stop, 0] += values_a.sum(axis=1)
    return b_out, a_out


_CPP_LIBRARY = None


def load_cpp_backend():
    """Compile/load the checked-in kernel; raise if the local compiler fails."""
    global _CPP_LIBRARY
    if _CPP_LIBRARY is not None:
        return _CPP_LIBRARY
    source = Path(__file__).with_name("field_backend.cpp")
    compiler = os.environ.get("CXX", "c++")
    resolved = shutil.which(compiler)
    if not resolved:
        raise RuntimeError(f"C++ compiler unavailable: {compiler}")
    digest = hashlib.sha256(source.read_bytes()+resolved.encode()).hexdigest()[:16]
    build = Path(__file__).resolve().parents[2] / "build" / "toroid_field"
    build.mkdir(parents=True, exist_ok=True)
    library = build / f"field-{digest}.so"
    if not library.exists():
        temporary = build / f"field-{digest}-{os.getpid()}.so"
        result = subprocess.run([resolved, "-std=c++17", "-O3", "-DNDEBUG", "-shared",
                                 "-fPIC", "-pthread", str(source), "-o", str(temporary)],
                                capture_output=True, text=True, check=False)
        if result.returncode:
            raise RuntimeError(f"C++ field backend compile failed: {result.stderr.strip()}")
        temporary.replace(library)
    loaded = ctypes.CDLL(str(library))
    pointer = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")
    integers = np.ctypeslib.ndpointer(dtype=np.int32, flags="C_CONTIGUOUS")
    loaded.field_evaluate.argtypes = [ctypes.c_size_t, pointer, ctypes.c_size_t,
                                     pointer, pointer, pointer, integers,
                                     ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                     ctypes.c_int, ctypes.c_int, pointer, pointer]
    loaded.field_evaluate.restype = ctypes.c_int
    _CPP_LIBRARY = loaded
    return loaded


def evaluate(points, sources: SegmentSources, quantity="B", backend="auto",
             by_group=False, threads=None, point_chunk=256, segment_chunk=512):
    """Evaluate Cartesian B [T] and/or A [T m] at Cartesian SI positions.

    quantity='both' returns (B, A); otherwise returns the requested array.
    Shape is (N, 3), or (N, n_groups, 3) when by_group=True. Group order is
    sources.group_names. Input points always have shape (N, 3), including N=1.
    """
    points = np.ascontiguousarray(points, dtype=np.float64)
    if points.ndim != 2 or points.shape[1:] != (3,) or not np.isfinite(points).all():
        raise ValueError("points must be a finite array of shape (N, 3)")
    if quantity not in ("B", "A", "both") or backend not in ("auto", "numpy", "cpp"):
        raise ValueError("quantity is B/A/both and backend is auto/numpy/cpp")
    if int(point_chunk) != point_chunk or int(segment_chunk) != segment_chunk or min(point_chunk, segment_chunk) < 1:
        raise ValueError("chunk sizes must be positive integers")
    want_b, want_a = quantity != "A", quantity != "B"
    threads = min(8, os.cpu_count() or 1) if threads is None else threads
    if int(threads) != threads or threads < 1:
        raise ValueError("threads must be a positive integer")
    library = None
    if backend != "numpy":
        try:
            library = load_cpp_backend()
        except (OSError, RuntimeError) as error:
            if backend == "cpp":
                raise
            warnings.warn(f"{error}; using NumPy field backend", RuntimeWarning, stacklevel=2)
    if library is None:
        b, a = _numpy_evaluate(points, sources, want_b, want_a, by_group,
                               int(point_chunk), int(segment_chunk))
    else:
        groups = len(sources.group_names) if by_group else 1
        b = np.zeros((len(points), groups, 3)) if want_b else np.empty(0)
        a = np.zeros((len(points), groups, 3)) if want_a else np.empty(0)
        status = library.field_evaluate(len(points), points, len(sources.a),
                                       sources.a, sources.b, sources.current_Aturn,
                                       sources.group, groups, int(by_group),
                                       int(want_b), int(want_a), int(threads), b, a)
        if status:
            raise RuntimeError(f"C++ field backend failed with status {status}")
    if not by_group:
        if want_b:
            b = b[:, 0]
        if want_a:
            a = a[:, 0]
    return (b, a) if quantity == "both" else b if want_b else a


def filament_distance(points, sources: SegmentSources, point_chunk=256, segment_chunk=512):
    """Minimum distance to any nonzero-current segment, for explicit source masks."""
    points = np.ascontiguousarray(points, dtype=float)
    if points.ndim != 2 or points.shape[1:] != (3,) or not np.isfinite(points).all():
        raise ValueError("points must have shape (N, 3) and be finite")
    if min(point_chunk, segment_chunk) < 1:
        raise ValueError("chunk sizes must be positive")
    active = sources.current_Aturn != 0
    firsts, lasts = sources.a[active], sources.b[active]
    out = np.full(len(points), np.inf)
    for start in range(0, len(points), point_chunk):
        stop = min(start+point_chunk, len(points))
        for first in range(0, len(firsts), segment_chunk):
            a, b = firsts[first:first+segment_chunk], lasts[first:first+segment_chunk]
            direction = b-a
            w = points[start:stop, None, :]-a
            t = np.clip(np.einsum("psj,sj->ps", w, direction)
                        / np.einsum("sj,sj->s", direction, direction), 0, 1)
            distance = np.linalg.norm(w-t[:, :, None]*direction, axis=2)
            out[start:stop] = np.minimum(out[start:stop], distance.min(axis=1))
    return out
