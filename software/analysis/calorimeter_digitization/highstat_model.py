"""Training-only spline response maps and independently estimated scale closure."""
from dataclasses import dataclass
import numpy as np

SPLINE_LAMBDAS = (.0001, .01, 1.)
ORIGINAL_LAMBDAS = (.01, 1., 100.)
PAIRS = ((0, 3), (1, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 9), (0, 8))


def stages(n=100000):
    if n != 100000:
        raise ValueError('The frozen campaign requires100k training events')
    order = np.random.default_rng(13395200).permutation(n)
    role = np.empty(n, dtype=np.int8)
    role[order[:70000]] = 0
    role[order[70000:85000]] = 1
    role[order[85000:]] = 2
    return role


def quantile(x, weight, fractions):
    """Exact linear quantiles of integer bootstrap multiplicities, without repeats."""
    order = np.argsort(x, kind='stable'); x, weight = x[order], weight[order]
    if np.any(weight < 0) or np.any(weight != np.floor(weight)):
        raise ValueError('Quantile multiplicities must be nonnegative integers')
    keep = weight > 0; x, weight = x[keep], weight[keep]
    if not len(x):
        raise ValueError('Empty quantile training population')
    cumulative = np.cumsum(weight)
    location = np.asarray(fractions) * (cumulative[-1] - 1)
    low, high = np.floor(location), np.ceil(location)
    a = x[np.searchsorted(cumulative, low, side='right')]
    b = x[np.searchsorted(cumulative, high, side='right')]
    return a + (b - a) * (location - low)


def weighted_mean(x, w):
    return np.sum(x * w[:, None], axis=0) / w.sum() if x.ndim == 2 else float(w @ x / w.sum())


@dataclass
class Basis:
    kind: str
    low: np.ndarray
    high: np.ndarray
    centre: np.ndarray
    scale: np.ndarray
    knots: list
    column_centre: np.ndarray
    column_scale: np.ndarray

    def raw(self, feature):
        bounded = np.clip(feature, self.low, self.high)
        z = (bounded - self.centre) / self.scale
        columns = [z]
        for j, knots in enumerate(self.knots):
            if len(knots):
                columns.append(np.maximum(z[:, j, None] - np.asarray(knots)[None, :], 0))
        if self.kind == 'spline':
            columns.append(np.column_stack([z[:, a] * z[:, b] for a, b in PAIRS]))
        return np.column_stack(columns)

    def design(self, feature):
        return np.column_stack([np.ones(len(feature)),
                                (self.raw(feature) - self.column_centre) / self.column_scale])

    def record(self):
        return dict(kind=self.kind, low=self.low.tolist(), high=self.high.tolist(),
                    centre=self.centre.tolist(), scale=self.scale.tolist(), knots=self.knots,
                    column_centre=self.column_centre.tolist(), column_scale=self.column_scale.tolist())


def make_basis(feature, weight, kind, knot_count):
    if kind == 'spline':
        limits = np.array([quantile(feature[:, j], weight, [.001, .999]) for j in range(10)])
        low, high = limits.T
    else:
        low, high = np.full(10, -np.finfo(float).max), np.full(10, np.finfo(float).max)
    bounded = np.clip(feature, low, high)
    centre = weighted_mean(bounded, weight)
    scale = np.sqrt(np.maximum(weighted_mean((bounded - centre) ** 2, weight), 0))
    scale[scale < 1e-10] = 1.
    z = (bounded - centre) / scale
    knots = []
    for j in range(10):
        k = quantile(z[:, j], weight, np.arange(1, knot_count + 1) / (knot_count + 1)) if knot_count else []
        knots.append([float(v) for v in np.unique(k) if z[:, j].min() < v < z[:, j].max()])
    basis = Basis(kind, low, high, centre, scale, knots, np.zeros(1), np.ones(1))
    columns = basis.raw(feature)
    basis.column_centre = weighted_mean(columns, weight)
    basis.column_scale = np.sqrt(np.maximum(weighted_mean((columns - basis.column_centre) ** 2, weight), 0))
    basis.column_scale[basis.column_scale < 1e-10] = 1.
    return basis


@dataclass
class RegionModel:
    basis: Basis
    coefficient: np.ndarray
    response_scale: float
    regularization: float
    knot_count: int

    def normalized_response(self, feature):
        return self.basis.design(feature) @ self.coefficient

    def record(self):
        return dict(basis=self.basis.record(), coefficient=self.coefficient.tolist(),
                    response_scale=self.response_scale, regularization=self.regularization,
                    knot_count=self.knot_count)


def fit_region(feature, response, weight, kind, knot_count, regularization):
    basis = make_basis(feature, weight, kind, knot_count)
    design = basis.design(feature); scale = weighted_mean(response, weight)
    gram = design.T @ (design * weight[:, None]) / weight.sum()
    rhs = design.T @ (response * weight) / weight.sum() / scale
    penalty = np.eye(design.shape[1]) * regularization; penalty[0, 0] = 0
    coefficient = np.linalg.solve(gram + penalty, rhs)
    return RegionModel(basis, coefficient, scale, regularization, knot_count)


@dataclass
class Calibration:
    kind: str
    models: list
    fallback_response: float
    closure: float
    selection: list

    def infer(self, feature, signal, region, valid_axis):
        """Measured inputs only; no truth energy/direction argument."""
        energy = np.asarray(signal) / self.fallback_response
        gains = np.ones(len(signal)); clipped = np.zeros(len(signal), dtype=bool)
        extrapolated = np.zeros(len(signal), dtype=bool)
        for r, model in enumerate(self.models):
            selected = valid_axis & (region == r)
            prediction = model.normalized_response(feature[selected])
            gains[selected] = 1 / np.clip(prediction, 1 / 3, 2)
            clipped[selected] = (prediction < 1 / 3) | (prediction > 2)
            extrapolated[selected] = np.any((feature[selected] < model.basis.low) |
                                            (feature[selected] > model.basis.high), axis=1)
            energy[selected] = signal[selected] / model.response_scale * gains[selected]
        return dict(pre_energy=energy, energy=energy * self.closure, gain=gains,
                    clipped=clipped, feature_extrapolated=extrapolated)

    def record(self):
        return dict(kind=self.kind, models=[m.record() for m in self.models],
                    fallback_response=self.fallback_response, closure=self.closure, selection=self.selection)


def fit(data, role, kind, multiplicity=None):
    count = np.ones(len(role)) if multiplicity is None else np.asarray(multiplicity, dtype=float)
    if set(np.unique(role)) != {0, 1, 2} or count.shape != role.shape or np.any(count < 0):
        raise ValueError('Invalid fit/tuning/closure roles or multiplicities')
    models, selection = [], []
    for region in range(2):
        valid = data['valid_axis'] & (data['region'] == region)
        train = valid & (role == 0) & (count > 0)
        tune = valid & (role == 1) & (count > 0)
        refit = valid & (role != 2) & (count > 0)
        trials = []
        for knots in ((0,) if kind == 'original' else (3, 7)):
            # Basis/design moments are shared by the three penalties.
            for lam in (ORIGINAL_LAMBDAS if kind == 'original' else SPLINE_LAMBDAS):
                model = fit_region(data['features'][train], data['response'][train], count[train], kind, knots, lam)
                error = model.normalized_response(data['features'][tune]) - data['response'][tune] / model.response_scale
                mse = weighted_mean(error ** 2, count[tune])
                trials.append(dict(knots=knots, regularization=lam, mse=mse))
        best = min(trials, key=lambda t: (t['mse'], t['knots'], -t['regularization']))
        selection.append(dict(region=region, candidates=trials, choice=best))
        models.append(fit_region(data['features'][refit], data['response'][refit], count[refit],
                                 kind, best['knots'], best['regularization']))
    fallback = weighted_mean(data['response'][role != 2], count[role != 2])
    result = Calibration(kind, models, fallback, 1., selection)
    closure = role == 2
    inferred = result.infer(data['features'][closure], data['signal'][closure],
                            data['region'][closure], data['valid_axis'][closure])
    result.closure = 1 / weighted_mean(inferred['pre_energy'] / data['energy'][closure], count[closure])
    if not np.isfinite(result.closure) or not .5 <= result.closure <= 2:
        raise ValueError('Closure factor outside predeclared sanity bounds0.5..2')
    return result


def restore(record):
    models = []
    for m in record['models']:
        b = m['basis']
        basis = Basis(b['kind'], *[np.array(b[k]) for k in ('low','high','centre','scale')],
                      b['knots'], np.array(b['column_centre']), np.array(b['column_scale']))
        models.append(RegionModel(basis, np.array(m['coefficient']), m['response_scale'],
                                   m['regularization'], m['knot_count']))
    return Calibration(record['kind'], models, record['fallback_response'], record['closure'], record['selection'])
