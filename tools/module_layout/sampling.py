"""Deterministic PROTOTYPE sampling; fractions use this measure, not event rates."""
import itertools
import math

import numpy as np


def directions(config):
    """Central grid, all twelve luminous corners/faces, and uniform off-grid rays."""
    maximum = float(config["eta_max"])
    samples = []
    for eta, j, z in itertools.product(
        np.linspace(-maximum, maximum, config["eta_points"]),
        range(config["phi_points"]), config["z_vertices_mm"]
    ):
        samples.append(dict(origin_mm=[*config["xy_center_mm"], z], eta=float(eta),
                            phi=2*math.pi*j/config["phi_points"], cohort="central_grid"))
    for eta, j, x, y, z in itertools.product(
        np.linspace(-maximum, maximum, config["stress_eta_points"]),
        range(config["stress_phi_points"]), config["xy_corner_values_mm"],
        config["xy_corner_values_mm"], config["z_vertices_mm"]
    ):
        # Irrational phase prevents the two angular grids sharing every seam.
        samples.append(dict(origin_mm=[x, y, z], eta=float(eta),
                            phi=2*math.pi*(j+0.3819660112501051)/config["stress_phi_points"],
                            cohort="luminous_boundary_grid"))
    rng = np.random.default_rng(config["seed"])
    for _ in range(config["random_tracks"]):
        xy = rng.uniform(min(config["xy_corner_values_mm"]), max(config["xy_corner_values_mm"]), 2)
        z = rng.uniform(min(config["z_vertices_mm"]), max(config["z_vertices_mm"]))
        samples.append(dict(origin_mm=[*map(float, xy), float(z)],
                            eta=float(rng.uniform(-maximum, maximum)),
                            phi=float(rng.uniform(0, 2*math.pi)), cohort="off_grid"))
    return samples


def tracks_for(samples, mode, config):
    if mode not in ("straight", "positive", "negative"):
        raise ValueError("unknown trajectory mode")
    convention = config["momentum_convention"]
    if convention not in ("pt", "p"):
        raise ValueError("momentum_convention must be pt or p")
    return [dict(sample, charge=-1 if mode == "negative" else 1,
                 field_T=0. if mode == "straight" else config["field_T"],
                 pt_GeV=config["momentum_GeV"]/(math.cosh(sample["eta"]) if convention == "p" else 1.))
            for sample in samples]


def control_sample(samples, count, seed):
    """Deterministic random subset shared by all controls and their mixed baseline."""
    rng = np.random.default_rng(seed)
    indices = sorted(rng.choice(len(samples), min(count, len(samples)), replace=False))
    return [samples[i] for i in indices]


def native_sample(tracks_by_mode, count, seed, worst_indices=None):
    """Broad seeded sample plus oracle worst cases, retaining both charge signs."""
    rng = np.random.default_rng(seed)
    chosen = []
    per_mode = max(1, count//len(tracks_by_mode))
    for mode, tracks in tracks_by_mode.items():
        indices = set(map(int, rng.choice(len(tracks), min(per_mode, len(tracks)), replace=False)))
        indices.update((worst_indices or {}).get(mode, [])[:4])
        chosen.extend(dict(tracks[i], mode=mode, original_index=i) for i in sorted(indices))
    return chosen
