"""Per-track performance statistics, independent of the native ACTS fitter."""

import math
import numpy as np


QUANTITIES = ("d0", "z0", "phi", "theta", "q_over_p", "pt_relative")


def wrap_phi(angle):
    """Signed shortest angular difference in [-pi, pi)."""
    return (np.asarray(angle, dtype=float) + math.pi) % (2 * math.pi) - math.pi


def validate_covariance(covariance):
    """Require a finite symmetric positive-definite five-parameter covariance.

    Normalize to a correlation matrix before the eigenvalue check so different
    physical parameter units do not set the numerical conditioning.
    """
    covariance = np.asarray(covariance, dtype=float)
    if covariance.ndim != 3 or covariance.shape[1:] != (5, 5):
        raise ValueError("Expected an N x 5 x 5 perigee covariance")
    valid = np.all(np.isfinite(covariance), axis=(1, 2))
    diagonal = np.diagonal(covariance, axis1=1, axis2=2)
    valid &= np.all(diagonal > 0, axis=1)
    valid &= np.all(np.isclose(covariance, covariance.transpose(0, 2, 1),
                               rtol=1.e-5, atol=1.e-14), axis=(1, 2))
    indices = np.flatnonzero(valid)
    if indices.size:
        sigma = np.sqrt(diagonal[indices])
        correlation = covariance[indices] / (sigma[:, :, None] * sigma[:, None, :])
        eigenvalues = np.linalg.eigvalsh((correlation + correlation.transpose(0, 2, 1)) / 2)
        valid[indices] &= np.all(eigenvalues > 0, axis=1)
    return valid


def perigee_observables(fitted, truth, covariance):
    """Residuals and pulls for unit-charge muons at the same perigee.

    Columns are d0 [mm], z0 [mm], phi/theta [rad], q/p [e/GeV].
    Native fitted covariances, including theta--q/p, determine pT uncertainty.
    """
    fitted, truth, covariance = map(lambda x: np.asarray(x, dtype=float),
                                     (fitted, truth, covariance))
    if fitted.ndim != 2 or fitted.shape[1] != 5 or truth.shape != fitted.shape:
        raise ValueError("Expected aligned N x 5 fitted/truth parameters")
    if covariance.shape != (len(fitted), 5, 5):
        raise ValueError("Covariance and parameter counts differ")
    finite_fit = np.all(np.isfinite(fitted), axis=1)
    finite_truth = np.all(np.isfinite(truth), axis=1)
    if not np.all(finite_truth) or np.any(truth[:, 4] == 0):
        raise ValueError("Truth must be finite charged-muon parameters")
    residual = fitted - truth
    residual[:, 2] = wrap_phi(residual[:, 2])
    valid_covariance = validate_covariance(covariance) & finite_fit
    diagonal = np.diagonal(covariance, axis1=1, axis2=2)
    with np.errstate(invalid="ignore", divide="ignore", over="ignore"):
        pull = residual / np.sqrt(diagonal)
        pt_truth = np.sin(truth[:, 3]) / np.abs(truth[:, 4])
        pt_fit = np.sin(fitted[:, 3]) / np.abs(fitted[:, 4])
        derivative_theta = np.cos(fitted[:, 3]) / np.abs(fitted[:, 4])
        derivative_qop = (-np.sin(fitted[:, 3]) * np.sign(fitted[:, 4])
                          / fitted[:, 4] ** 2)
        pt_variance = (derivative_theta ** 2 * covariance[:, 3, 3]
                       + derivative_qop ** 2 * covariance[:, 4, 4]
                       + 2 * derivative_theta * derivative_qop * covariance[:, 3, 4])
        pt_residual = (pt_fit - pt_truth) / pt_truth
        pt_pull = (pt_fit - pt_truth) / np.sqrt(pt_variance)
    pull[~valid_covariance] = np.nan
    pt_pull[~valid_covariance | ~(pt_variance > 0)] = np.nan
    residual[~finite_fit] = np.nan
    pt_residual[~finite_fit | ~np.isfinite(pt_fit)] = np.nan
    values = {
        name: {"residual": residual[:, index], "pull": pull[:, index]}
        for index, name in enumerate(QUANTITIES[:5])
    }
    values["pt_relative"] = {"residual": pt_residual, "pull": pt_pull}
    return values, {
        "finite_fitted_parameters": finite_fit,
        "valid_covariance": valid_covariance,
        "valid_pt_variance": valid_covariance & np.isfinite(pt_variance) & (pt_variance > 0),
        "wrong_charge": np.sign(fitted[:, 4]) != np.sign(truth[:, 4]),
    }


def interval_mask(values, low, high, final=False, absolute=False):
    values = np.asarray(values)
    if absolute:
        values = np.abs(values)
    return (values >= low) & ((values <= high) if final else (values < high))


def statistics(values, probability=0.6826894921370859, minimum_entries=30,
               bootstrap_replicates=400, rng=None):
    """Unclipped empirical statistics and event-level bootstrap standard errors.

    A single selected track represents each independent generated event.
    Resample tracks within a displayed bin, not hits or track states.
    Missing/undersampled bins retain counts with null estimates.
    """
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not 0 < probability < 1:
        raise ValueError("Expected one-dimensional values and probability in (0,1)")
    if minimum_entries < 2 or bootstrap_replicates < 2:
        raise ValueError("At least two entries/replicates are required")
    finite = values[np.isfinite(values)]
    count = finite.size
    result = {"entries": int(count), "nonfinite": int(values.size - count),
              "status": "measured" if count >= minimum_entries else "undersampled"}
    names = ("mean", "mean_se", "median", "std", "rms", "width68",
             "median_se", "std_se", "rms_se", "width68_se")
    result.update({name: None for name in names})
    if count < minimum_entries:
        return result
    low, high = (1 - probability) / 2, (1 + probability) / 2
    quantiles = np.quantile(finite, [low, .5, high])
    result.update(mean=float(np.mean(finite)), median=float(quantiles[1]),
                  std=float(np.std(finite, ddof=1)),
                  rms=float(np.sqrt(np.mean(finite ** 2))),
                  width68=float((quantiles[2] - quantiles[0]) / 2))
    result["mean_se"] = result["std"] / math.sqrt(count)
    rng = rng if rng is not None else np.random.default_rng(74042)
    estimates = []
    # Limit scratch memory for wide eta slices and full-sample summaries.
    for start in range(0, bootstrap_replicates, 32):
        batch = min(32, bootstrap_replicates - start)
        sampled = finite[rng.integers(count, size=(batch, count))]
        quantiles = np.quantile(sampled, [low, .5, high], axis=1)
        estimates.append(np.column_stack([
            quantiles[1], np.std(sampled, ddof=1, axis=1),
            np.sqrt(np.mean(sampled ** 2, axis=1)),
            (quantiles[2] - quantiles[0]) / 2,
        ]))
    errors = np.std(np.concatenate(estimates), axis=0, ddof=1)
    for name, error in zip(("median", "std", "rms", "width68"), errors):
        result[name + "_se"] = float(error)
    return result


def binomial_interval(successes, trials):
    """Wilson one-standard-normal interval; null for an empty denominator."""
    if not 0 <= successes <= trials:
        raise ValueError("Invalid binomial counts")
    if trials == 0:
        return {"value": None, "low": None, "high": None}
    p = successes / trials
    denominator = 1 + 1 / trials
    centre = (p + 1 / (2 * trials)) / denominator
    radius = math.sqrt(p * (1 - p) / trials + 1 / (4 * trials ** 2)) / denominator
    return {"value": p, "low": max(0., centre - radius), "high": min(1., centre + radius)}
