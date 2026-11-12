"""Exploratory learning curve of the frozen 10-feature cross-fit calibration."""
import argparse
import json
from pathlib import Path
import time
import numpy as np
from angular_sample import save, sha
from staggered_calibration import CrossFit
from staggered_results import load_features, moments, interval
from angular_analyze import ETA_EDGES, PHI_EDGES, bin_index, folded_phi

SIZES = (1000, 2000, 4000, 8000)


def subsets(model):
    output = {}
    for repeat in range(3):
        for outer in range(5):
            ids = np.flatnonzero(model.outer != outer)
            order = np.random.default_rng(13395000 + 10 * repeat + outer).permutation(ids)
            for size in SIZES:
                mask = np.zeros(len(ids) + 2000)
                mask[order[:size]] = 1
                output[repeat, outer, size] = mask
    return output


def predictions(model, selected, counts):
    output = np.empty((3, len(SIZES), len(counts)))
    clipped = np.zeros_like(output)
    for repeat in range(3):
        for j, size in enumerate(SIZES):
            for outer in range(5):
                p = model.predict(selected[repeat, outer, size] * counts)
                test = model.outer == outer
                output[repeat, j, test] = p['response'][test]
                clipped[repeat, j, test] = p['clipped'][test]
    return output, clipped


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--features', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--predictions-output', type=Path, required=True)
    p.add_argument('--bootstrap', type=int, default=200)
    a = p.parse_args()
    data, receipt = load_features(a.features)
    model = CrossFit(data); selected = subsets(model)
    point, clipped = predictions(model, selected, np.ones(10000))
    categories = [np.zeros(10000, dtype=int), bin_index(abs(data['eta']), ETA_EDGES),
                  bin_index(folded_phi(data['phi']), PHI_EDGES)]
    def statistics(values, counts):
        return np.array([[np.concatenate([moments(v, c, counts, 1 if i == 0 else 10)[k]
                                         for i, c in enumerate(categories)])
                          for k in (0, 1)] for v in values.reshape(-1, 10000)]).reshape(3, 4, 2, 21)
    central = statistics(point, np.ones(10000))
    boot = np.zeros((a.bootstrap, 4, 2, 21))
    rng = np.random.default_rng(13395100); start = time.monotonic()
    for b in range(a.bootstrap):
        counts = np.bincount(rng.integers(10000, size=10000), minlength=10000)
        values, _ = predictions(model, selected, counts)
        boot[b] = statistics(values, counts).mean(axis=0)
        if (b + 1) % 20 == 0:
            print(f'Full learning-curve refits {b+1}/{a.bootstrap}: {time.monotonic()-start:.1f}s', flush=True)
    rows = []
    for j, size in enumerate(SIZES):
        rows.append(dict(training_events_per_outer_fit=size, held_out_events=10000,
            seed_global_means=central[:, j, 0, 0].tolist(), seed_global_widths=central[:, j, 1, 0].tolist(),
            seed_gain_clipped_fractions=clipped[:, j].mean(axis=1).tolist(),
            mean=float(central[:, j, 0, 0].mean()), fractional_width=float(central[:, j, 1, 0].mean()),
            mean_uncertainty=interval(boot[:, j, 0, 0]), width_uncertainty=interval(boot[:, j, 1, 0]),
            angular_mean=central[:, j, 0, 1:].mean(axis=0).tolist(),
            angular_width=central[:, j, 1, 1:].mean(axis=0).tolist()))
    a.output.mkdir(parents=True, exist_ok=False)
    save(a.output / 'learning-curve.json', dict(status='PROTOTYPE exploratory',
        interpretation='Frozen original architecture; old10k already informed design. Nested subsets, same5outer held-out IDfolds,3subset permutations; inclusive mean of3seed metrics.',
        uncertainty='200 common whole-event bootstrap replicas refitting nested preprocessing/selection/models; folds and subset memberships fixed',
        bootstrap_replicates=a.bootstrap, bootstrap_seed=13395100, subset_seed_base=13395000,
        feature_receipt=receipt, producer_sha256=sha(__file__), core_sha256=sha(Path(__file__).with_name('staggered_calibration.py')),
        zero_events=int(np.count_nonzero(data['signal'] == 0)), rows=rows,
        angular_order=[f'{axis}:{i}' for axis in ('abs_eta','folded_phi') for i in range(10)]))
    np.savez_compressed(a.predictions_output, response=point, clipped=clipped)
    print(json.dumps(rows, indent=2), flush=True)


if __name__ == '__main__':
    main()
