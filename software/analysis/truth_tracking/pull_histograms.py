"""Truth-minus-fit pulls and loss-accounted common-bin distributions."""

import numpy as np

from metrics import wrap_phi


BOUND = ("d0", "z0", "phi", "theta", "q_over_p", "time")


def bound_pulls(fitted, truth, covariance):
    fitted, truth, covariance = map(lambda a: np.asarray(a, dtype=float), (fitted, truth, covariance))
    if (fitted.ndim != 2 or fitted.shape[1] != 6 or truth.shape != fitted.shape
            or covariance.shape != (len(fitted), 6, 6)):
        raise ValueError("Require aligned six-parameter fit/truth/covariance")
    if not np.all(np.isfinite(truth)):
        raise ValueError("Nonfinite generated truth")
    diagonal = np.diagonal(covariance, axis1=1, axis2=2)
    valid = np.all(np.isfinite(covariance), axis=(1, 2)) & np.all(diagonal > 0, axis=1)
    valid &= np.all(np.isclose(covariance, covariance.transpose(0, 2, 1),
                               rtol=1e-5, atol=1e-14), axis=(1, 2))
    indices = np.flatnonzero(valid)
    if len(indices):
        sigma = np.sqrt(diagonal[indices])
        correlation = covariance[indices] / (sigma[:, :, None] * sigma[:, None, :])
        valid[indices] &= np.all(np.linalg.eigvalsh(
            (correlation + correlation.transpose(0, 2, 1)) / 2) > 0, axis=1)
    residual = truth - fitted
    residual[:, 2] = wrap_phi(residual[:, 2])
    with np.errstate(invalid="ignore", divide="ignore"):
        pulls = residual / np.sqrt(diagonal)
    finite = np.all(np.isfinite(fitted), axis=1)
    pulls[~valid | ~finite] = np.nan
    return pulls, {"valid_covariance": valid, "finite_parameters": finite}


def common_edges(arrays, core_limit, core_bin_width, tail_bins_per_decade):
    if core_limit <= 0 or core_bin_width <= 0 or tail_bins_per_decade < 1:
        raise ValueError("Invalid histogram binning")
    bins = round(2 * core_limit / core_bin_width)
    if bins < 1 or not np.isclose(bins * core_bin_width, 2 * core_limit):
        raise ValueError("Core width must exactly partition the core interval")
    finite = [np.asarray(a)[np.isfinite(a)] for a in arrays]
    maximum = max([core_limit] + [float(np.max(np.abs(a))) for a in finite if len(a)])
    core = np.linspace(-core_limit, core_limit, bins + 1)
    if maximum <= core_limit:
        return core
    limit = np.nextafter(maximum, np.inf)
    if not np.isfinite(limit):
        limit = maximum
    tail_bins = max(1, int(np.ceil(np.log10(limit / core_limit) * tail_bins_per_decade)))
    tail = np.geomspace(core_limit, limit, tail_bins + 1)
    return np.concatenate([-tail[:0:-1], core, tail[1:]])


def histogram(values, edges, core_limit):
    values, edges = np.asarray(values), np.asarray(edges)
    if len(edges) < 2 or not np.all(np.isfinite(edges)) or np.any(np.diff(edges) <= 0):
        raise ValueError("Histogram edges must be finite and strictly increasing")
    finite = values[np.isfinite(values)]
    counts = np.histogram(finite, bins=edges)[0]
    under, over = int(np.sum(finite < edges[0])), int(np.sum(finite > edges[-1]))
    if int(counts.sum()) + under + over != len(finite):
        raise ValueError("Histogram count closure failed")
    n = len(finite)
    return {
        "counts": counts.tolist(), "entries": n, "nonfinite": len(values) - n,
        "underflow": under, "overflow": over,
        "outside_core": int(np.sum(np.abs(finite) > core_limit)),
        "abs_gt3": int(np.sum(np.abs(finite) > 3)),
        "mean": float(np.mean(finite)) if n else None,
        "std": float(np.std(finite, ddof=1)) if n > 1 else None,
        "minimum": float(np.min(finite)) if n else None,
        "maximum": float(np.max(finite)) if n else None,
        "width68": float(np.diff(np.quantile(finite,
            [(1 - .6826894921370859) / 2, (1 + .6826894921370859) / 2]))[0] / 2) if n else None,
    }
