"""PROTOTYPE complete vacuum magnetic energy from finite-pack J dot A.

For closed steady currents in vacuum, U = (1/2) integral J dot A dV equals
the all-space integral of B squared/(2 mu0). Here A includes every source
segment, including the same physical coil as the target. No same-coil term,
filament term, near interaction or mutual interaction is removed or cut off.

A finite uniform current pack is represented by source and target cross-section
quadratures with *different nodes*. This avoids evaluating singular line
self-potentials; it does not remove the physical self-energy. The weakly
singular volume integral is approximated by a staggered double quadrature and
requires an explicit order-convergence study. Longitudinal target integration
is Gauss-Legendre on every exact straight polygon segment. Curved conductors
also require polygon-segmentation convergence.

The C_n reduction is exact only when the caller supplies an exactly repeated
source and one correspondingly weighted representative target coil per family.
An inductance normalized by ampere-turns is not the electrical terminal
inductance unless the actual turn count and circuit connection are supplied.
"""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy

import numpy as np

try:
    from .field import SegmentSources, evaluate
except ImportError:
    from field import SegmentSources, evaluate


def _longitudinal_quadrature(target: SegmentSources, line_order: int):
    if int(line_order) != line_order or line_order < 1:
        raise ValueError("line_order must be a positive integer")
    nodes, weights = np.polynomial.legendre.leggauss(int(line_order))
    direction = target.b-target.a
    points = target.a[:, None, :] + (nodes[None, :, None]+1)*direction[:, None, :]/2
    current_dl = (target.current_Aturn[:, None, None]*direction[:, None, :]
                  * weights[None, :, None]/2)
    return points.reshape(-1, 3), current_dl.reshape(-1, 3)


def integrate_current_dot_potential(target: SegmentSources, source: SegmentSources,
                                    line_order=4, backend="auto", threads=None,
                                    by_group=True):
    """Return integral I dl dot A, in joules, without a half or multiplicity.

    by_group=True returns one contribution per *source* group, in source order;
    otherwise returns a scalar. The target already contains its physical pack
    quadrature currents. Its own group labels do not alter this integral.
    Any coincident active source/target filament yields an explicit error.
    """
    points, current_dl = _longitudinal_quadrature(target, line_order)
    potential = evaluate(points, source, quantity="A", backend=backend,
                         by_group=by_group, threads=threads)
    if not np.isfinite(potential).all():
        raise ValueError("singular source/target filaments: use disjoint finite-pack quadratures")
    if by_group:
        return np.einsum("pgj,pj->g", potential, current_dl)
    return float(np.einsum("pj,pj->", potential, current_dl))


def magnetic_energy(source: SegmentSources, target_representatives,
                    symmetry_multiplicity=12, line_order=4,
                    reference_currents_Aturn=None, backend="auto", threads=None):
    """Compute the complete ordered source-family energy matrix.

    source contains all physical coils. target_representatives is a mapping
    {source_group_name: representative finite-pack coil}, or a sequence whose
    length and order match source.group_names. A scalar symmetry_multiplicity
    applies to every family; a mapping allows explicit family multiplicities.

    coupling_integral_J[g][h] = n_g integral_rep_g I_g dl dot A_h.
    energy_matrix_J is one half of this matrix, and total_energy_J is its sum.
    Thus each diagonal contains the entire same-family energy; the two ordered
    off-diagonal entries together contain one complete family mutual energy.
    Matrices are returned unsymmetrized so the reciprocity residual remains
    visible. reference_currents_Aturn optionally gives per-family controlling
    currents and produces coupling/(I_g I_h) in henries per ampere-turn basis.
    """
    names = source.group_names
    if isinstance(target_representatives, Mapping):
        if set(target_representatives) != set(names):
            raise ValueError("representative target keys must exactly match source groups")
        targets = [target_representatives[name] for name in names]
    else:
        targets = list(target_representatives)
        if len(targets) != len(names):
            raise ValueError("one representative target is required per source group")
    if isinstance(symmetry_multiplicity, Mapping):
        if set(symmetry_multiplicity) != set(names):
            raise ValueError("multiplicity keys must exactly match source groups")
        multiplicities = np.asarray([symmetry_multiplicity[name] for name in names], dtype=float)
    else:
        multiplicities = np.full(len(names), symmetry_multiplicity, dtype=float)
    if (not np.isfinite(multiplicities).all() or (multiplicities < 1).any()
            or (multiplicities != np.floor(multiplicities)).any()):
        raise ValueError("symmetry multiplicities must be positive integers")
    coupling = np.array([multiplicities[index]*integrate_current_dot_potential(
        target, source, line_order=line_order, backend=backend, threads=threads,
        by_group=True) for index, target in enumerate(targets)])
    antisymmetric = coupling-coupling.T
    normalization = max(float(np.max(np.abs(coupling))), np.finfo(float).tiny)
    result = {
        "group_names": list(names),
        "symmetry_multiplicity": multiplicities.astype(int).tolist(),
        "line_quadrature_order": int(line_order),
        "coupling_integral_J": coupling.tolist(),
        "energy_matrix_J": (coupling/2).tolist(),
        "total_energy_J": float(coupling.sum()/2),
        "reciprocity_max_absolute_J": float(np.max(np.abs(antisymmetric))),
        "reciprocity_max_relative": float(np.max(np.abs(antisymmetric))/normalization),
        "method": "all-source Coulomb-gauge A; staggered finite-pack J dot A; no self/mutual omission",
    }
    if reference_currents_Aturn is not None:
        if isinstance(reference_currents_Aturn, Mapping):
            if set(reference_currents_Aturn) != set(names):
                raise ValueError("reference current keys must exactly match source groups")
            currents = np.array([reference_currents_Aturn[name] for name in names], dtype=float)
        else:
            currents = np.asarray(reference_currents_Aturn, dtype=float)
        if currents.shape != (len(names),) or not np.isfinite(currents).all() or (currents == 0).any():
            raise ValueError("reference currents must be finite, nonzero and one per group")
        result["reference_currents_Aturn"] = currents.tolist()
        result["inductance_matrix_H_per_Aturn_basis"] = (coupling/np.outer(currents, currents)).tolist()
    return result


def rescale_energy(result, currents_Aturn):
    """Exactly rescale an energy result to new currents in the same vacuum geometry.

    result is a row returned by magnetic_energy with reference_currents_Aturn.
    Every matrix entry scales as I_g I_h; no field-volume approximation enters.
    The stored ampere-turn inductance matrix is kept unsymmetrized, preserving
    the original numerical reciprocity diagnostic. Zero and reversed new
    currents are valid. Geometry, pack-current profile and material response
    must remain the same for this linear-superposition operation to apply.
    """
    names = tuple(result["group_names"])
    if isinstance(currents_Aturn, Mapping):
        if set(currents_Aturn) != set(names):
            raise ValueError("new current keys must exactly match source groups")
        currents = np.array([currents_Aturn[name] for name in names], dtype=float)
    else:
        currents = np.asarray(currents_Aturn, dtype=float)
    if currents.shape != (len(names),) or not np.isfinite(currents).all():
        raise ValueError("new currents must be finite and one per source group")
    old_currents = np.asarray(result["reference_currents_Aturn"], dtype=float)
    if "inductance_matrix_H_per_Aturn_basis" in result:
        inductance = np.asarray(result["inductance_matrix_H_per_Aturn_basis"], dtype=float)
    else:
        if (old_currents == 0).any():
            raise ValueError("nonzero reference currents or an inductance matrix are required")
        inductance = np.asarray(result["coupling_integral_J"], dtype=float)/np.outer(old_currents, old_currents)
    if inductance.shape != (len(names), len(names)) or not np.isfinite(inductance).all():
        raise ValueError("inductance matrix must be finite and square in source groups")
    coupling = inductance*np.outer(currents, currents)
    normalization = max(float(np.max(np.abs(coupling))), np.finfo(float).tiny)
    out = deepcopy(result)
    out.update(reference_currents_Aturn=currents.tolist(),
               rescaled_from_currents_Aturn=old_currents.tolist(),
               coupling_integral_J=coupling.tolist(), energy_matrix_J=(coupling/2).tolist(),
               total_energy_J=float(coupling.sum()/2),
               reciprocity_max_absolute_J=float(np.max(np.abs(coupling-coupling.T))),
               reciprocity_max_relative=float(np.max(np.abs(coupling-coupling.T))/normalization),
               inductance_matrix_H_per_Aturn_basis=inductance.tolist(),
               rescaling_method="exact I_g I_h rescaling of every vacuum self and mutual term at fixed geometry")
    return out
