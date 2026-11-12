"""Small nested cross-fit response calibration with whole-procedure refitting."""
from dataclasses import dataclass
import numpy as np

LAMBDAS = (.01, 1., 100.)
OUTER_SEED, INNER_SEED = 1337000, 1337001
LOW_RESPONSE, HIGH_RESPONSE = 1 / 3, 2.


def folds(events, count, seed):
    """Immutable ID assignments; bootstrap multiplicities never change them."""
    events = np.asarray(events)
    if not np.array_equal(np.sort(events), np.arange(len(events))):
        raise ValueError("Require complete, unique IDs starting at zero")
    assignment = np.empty(len(events), dtype=np.int64)
    assignment[np.random.default_rng(seed).permutation(len(events))] = np.arange(len(events)) % count
    return assignment[events]


@dataclass
class Model:
    response_scale: float
    coefficient: np.ndarray
    regularization: float
    training_weight: float
    centre: np.ndarray
    scale: np.ndarray

    def record(self):
        return dict(response_scale=self.response_scale, coefficient=self.coefficient.tolist(),
                    regularization=self.regularization, training_weight=self.training_weight,
                    feature_centre=self.centre.tolist(), feature_scale=self.scale.tolist())

    def infer(self, features, signal):
        """Actual energy inference API: measured signal/features only."""
        design = np.column_stack([np.ones(len(features)), features])
        prediction = design @ self.coefficient
        bounded = np.clip(prediction, LOW_RESPONSE, HIGH_RESPONSE)
        gain = 1 / bounded
        return (np.asarray(signal) / self.response_scale * gain, gain,
                (prediction < LOW_RESPONSE) | (prediction > HIGH_RESPONSE))


def solve_model(gram, response_moment, regularization):
    """Fit with training-only weighted centring/scaling from sufficient moments."""
    weight = gram[0, 0]
    if weight <= 0:
        raise ValueError("Empty training region")
    response_scale = response_moment[0] / weight
    if response_scale <= 0:
        raise ValueError("Training mean response is not positive")
    mean = gram[0, 1:] / weight
    variance = np.diag(gram)[1:] / weight - mean ** 2
    scale = np.sqrt(np.maximum(variance, 0))
    scale[scale < 1e-10] = 1.
    transform = np.eye(len(mean) + 1)
    transform[0, 1:] = -mean / scale
    transform[np.arange(1, len(mean) + 1), np.arange(1, len(mean) + 1)] = 1 / scale
    covariance = transform.T @ gram @ transform / weight
    rhs = transform.T @ response_moment / weight / response_scale
    penalty = np.eye(len(mean) + 1) * regularization
    penalty[0, 0] = 0.
    coefficient = transform @ np.linalg.solve(covariance + penalty, rhs)
    return Model(float(response_scale), coefficient, float(regularization), float(weight), mean, scale)


def validation_error(model, gram, moment, square):
    """Weighted prediction SSE in dimensionless response, before gain clipping."""
    coefficient, scale = model.coefficient, model.response_scale
    return max(0., float(coefficient @ gram @ coefficient
                         - 2 * coefficient @ moment / scale + square / scale ** 2))


class CrossFit:
    def __init__(self, data):
        self.feature = np.asarray(data["features"], dtype=float)
        self.response = np.asarray(data["response"], dtype=float)
        self.valid = np.asarray(data["valid_axis"], dtype=bool)
        self.region = np.asarray(data["region"], dtype=np.int64)
        self.energy = np.asarray(data["energy"], dtype=float)
        self.signal = np.asarray(data["signal"], dtype=float)
        self.events = np.asarray(data["event"], dtype=np.int64)
        if len(self.feature) != len(self.response) or self.feature.shape[1] > 10:
            raise ValueError("Invalid feature dimensions")
        if not np.isfinite(self.feature).all() or not np.isfinite(self.response).all() or np.any(self.response < 0):
            raise ValueError("Invalid input features or response")
        if not np.isfinite(self.energy).all() or np.any(self.energy <= 0) or not np.isfinite(self.signal).all() or np.any(self.signal < 0):
            raise ValueError("Invalid energy labels or measured signal")
        self.outer = folds(self.events, 5, OUTER_SEED)
        self.inner = folds(self.events, 3, INNER_SEED)
        self.design = np.column_stack([np.ones(len(self.feature)), self.feature])
        # Precompute sufficient-statistic products. Bootstrap aggregation then
        # refits all preprocessing/models without repeatedly scanning ROOT data.
        self.dimension = self.design.shape[1]
        self.products = (self.design[:, :, None] * self.design[:, None, :]).reshape(len(self.feature), -1)
        self.moments = self.design * self.response[:, None]
        self.blocks = self.region * 15 + self.outer * 3 + self.inner
        self.test_indices = {(o, r): np.flatnonzero((self.outer == o) & (self.region == r) & self.valid)
                             for o in range(5) for r in range(2)}

    def aggregate(self, weight):
        blocks = self.blocks[self.valid]
        weights = weight[self.valid]
        def sums(values):
            values = values[self.valid]
            return np.column_stack([np.bincount(blocks, weights=weights * values[:, j], minlength=30)
                                    for j in range(values.shape[1])])
        gram = sums(self.products).reshape(2, 5, 3, self.dimension, self.dimension)
        moment = sums(self.moments).reshape(2, 5, 3, self.dimension)
        square = np.bincount(blocks, weights=weights * self.response[self.valid] ** 2,
                             minlength=30).reshape(2, 5, 3)
        return gram, moment, square

    def predict(self, multiplicity=None, prior="uniform", record=False):
        n = len(self.response)
        counts = np.ones(n) if multiplicity is None else np.asarray(multiplicity, dtype=float)
        if counts.shape != (n,) or np.any(counts < 0):
            raise ValueError("Invalid bootstrap multiplicities")
        if prior not in ("uniform", "inverse_energy"):
            raise ValueError("Unknown training prior")
        weight = counts * (1 / self.energy if prior == "inverse_energy" else 1.)
        gram, moment, square = self.aggregate(weight)
        corrected = np.zeros(n)
        inferred_energy = np.zeros(n)
        scale_only = np.zeros(n)
        gain = np.ones(n)
        clipped = np.zeros(n, dtype=bool)
        assigned = np.zeros(n, dtype=bool)
        records = []
        for outer in range(5):
            train = self.outer != outer
            global_weight = weight[train].sum()
            if global_weight <= 0:
                raise ValueError("Empty outer training fold")
            fallback = float(weight[train] @ self.response[train] / global_weight)
            test = self.outer == outer
            scale_only[test] = self.signal[test] / fallback / self.energy[test]
            corrected[test] = scale_only[test]
            inferred_energy[test] = self.signal[test] / fallback
            assigned[test & ~self.valid] = True
            for region in range(2):
                selected = np.arange(5) != outer
                g = gram[region, selected].sum(axis=0)
                h = moment[region, selected].sum(axis=0)
                q = square[region, selected].sum(axis=0)
                errors = []
                for regularization in LAMBDAS:
                    error, validation_weight = 0., 0.
                    for inner in range(3):
                        inner_train = np.arange(3) != inner
                        model = solve_model(g[inner_train].sum(axis=0), h[inner_train].sum(axis=0), regularization)
                        error += validation_error(model, g[inner], h[inner], q[inner])
                        validation_weight += g[inner, 0, 0]
                    errors.append(error / validation_weight)
                choice = min(range(len(LAMBDAS)), key=lambda i: (errors[i], -LAMBDAS[i]))
                model = solve_model(g.sum(axis=0), h.sum(axis=0), LAMBDAS[choice])
                indices = self.test_indices[(outer, region)]
                inferred_energy[indices], gain[indices], clipped[indices] = model.infer(self.feature[indices], self.signal[indices])
                scale_only[indices] = self.signal[indices] / model.response_scale / self.energy[indices]
                corrected[indices] = inferred_energy[indices] / self.energy[indices]
                assigned[indices] = True
                if record:
                    records.append(dict(outer_fold=outer, region=region, inner_errors=errors,
                                        model=model.record(), held_out_events=len(indices),
                                        fallback_global_response=fallback))
        if not assigned.all() or not np.isfinite(corrected).all() or not np.isfinite(scale_only).all():
            raise ValueError("Incomplete/nonfinite cross-fit predictions")
        if np.any(corrected[self.response == 0] != 0):
            raise AssertionError("Calibration changed a physical zero")
        return dict(response=corrected, inferred_energy=inferred_energy, scale_only=scale_only, gain=gain, clipped=clipped,
                    fallback=~self.valid, records=records)
