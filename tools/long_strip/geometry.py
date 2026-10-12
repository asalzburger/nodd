"""Convex geometry from DES-007 / PR21, revision 17d84a4c92916a49929db3c5e75684e51bf613b7.
Copied locally so this PROTOTYPE does not depend on an unmerged branch.
"""
import math
import numpy as np

def area(poly):
    p = np.asarray(poly)
    return abs(np.dot(p[:, 0], np.roll(p[:, 1], -1)) -
               np.dot(p[:, 1], np.roll(p[:, 0], -1))) / 2


def inside(poly, x, y):
    """Inclusive convex CCW containment; boundary epsilon is numerical only."""
    out = np.ones(np.broadcast_shapes(np.shape(x), np.shape(y)), dtype=bool)
    for a, b in zip(poly, np.roll(poly, -1, axis=0)):
        out &= ((b[0]-a[0])*(y-a[1]) - (b[1]-a[1])*(x-a[0])) >= -1e-9
    return out


def intersects(a, b):
    """Strict interior overlap using SAT; touching is not an interior overlap."""
    for p in (a, b):
        for d in np.roll(p, -1, axis=0) - p:
            n = np.array([-d[1], d[0]])
            ap, bp = a @ n, b @ n
            if ap.max() <= bp.min()+1e-9 or bp.max() <= ap.min()+1e-9:
                return False
    return True


def rectangle(x0, x1, width):
    return np.array([[x0, -width/2], [x1, -width/2],
                     [x1, width/2], [x0, width/2]])


def rotate(p, phi):
    c, s = math.cos(phi), math.sin(phi)
    return p @ np.array([[c, s], [-s, c]])


def radial_extent(poly):
    nearest = math.inf
    for a, b in zip(poly, np.roll(poly, -1, axis=0)):
        d = b-a
        t = np.clip(-np.dot(a, d)/np.dot(d, d), 0, 1)
        nearest = min(nearest, float(np.linalg.norm(a+t*d)))
    return nearest, float(np.linalg.norm(poly, axis=1).max())
