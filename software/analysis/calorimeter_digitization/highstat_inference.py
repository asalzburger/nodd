"""Apply the recorded staggered ECAL calibration without fitting or truth inputs."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from highstat_model import restore

ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / 'docs/validation/ecal-highstat/frozen'
SEMANTIC_KEYS = ('feature_names', 'producer_sha256', 'feature_recipe_sha256',
                 'geometry_helper_sha256')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_record(artifact=ARTIFACT):
    """Check the versioned manifest, unchanged coefficients and inference source."""
    artifact = Path(artifact)
    manifest = json.loads((artifact / 'manifest.json').read_text())
    if manifest['schema_version'] != 1 or manifest['coefficients_file'] != 'models.json':
        raise ValueError('Unsupported calibration artifact schema')
    if sha(artifact / 'models.json') != manifest['coefficients_sha256']:
        raise ValueError('Calibration coefficient file changed')
    record = json.loads((artifact / 'models.json').read_text())
    if record['core_sha256'] != sha(Path(__file__).with_name('highstat_model.py')):
        raise ValueError('Frozen calibration inference source changed')
    if manifest['feature_semantics'] != record['feature_semantics']:
        raise ValueError('Manifest feature semantics differ from the frozen model')
    return manifest, record


def calibrate(features, signal_GeV, region, valid_axis, *, geometry_sha256,
              feature_semantics, kind='spline', artifact=ARTIFACT):
    """Return calibrated energies in GeV and flags; never use truth or refit."""
    manifest, record = load_record(artifact)
    if kind not in manifest['models']:
        raise ValueError('Unknown calibration model')
    if geometry_sha256 != manifest['geometry']['detector_xml_sha256']:
        raise ValueError('Calibration geometry mismatch')
    if feature_semantics != record['feature_semantics']:
        raise ValueError('Calibration feature semantics mismatch')
    features = np.asarray(features, dtype=float)
    signal = np.asarray(signal_GeV, dtype=float)
    region, valid_axis = np.asarray(region), np.asarray(valid_axis)
    n = len(signal) if signal.ndim == 1 else -1
    if (features.shape != (n, len(feature_semantics['feature_names']))
            or region.shape != (n,) or valid_axis.shape != (n,)):
        raise ValueError('Expected N signals, N x 10 features and N region/axis flags')
    if (not np.isfinite(features).all() or not np.isfinite(signal).all()
            or np.any(signal < 0)):
        raise ValueError('Features/signals must be finite and signals nonnegative')
    if (valid_axis.dtype != np.bool_ or not np.issubdtype(region.dtype, np.integer)
            or not np.isin(region, [0, 1]).all()):
        raise ValueError('Expected boolean axis flags and integer regions 0/1')
    result = restore(record['models'][kind]).infer(features, signal, region, valid_axis)
    if not all(np.isfinite(v).all() for v in result.values()):
        raise ValueError('Nonfinite calibrated output')
    result.update(zero_signal=signal == 0, fallback=~valid_axis)
    return result


def apply_file(features_dir, output, kind='spline', artifact=ARTIFACT):
    """Consume only measured feature columns from an audited feature directory."""
    features_dir, output = Path(features_dir), Path(output)
    receipt = json.loads((features_dir / 'receipt.json').read_text())
    source = features_dir / 'features.npz'
    if receipt['status'] != 'PASS' or receipt['feature_sha256'] != sha(source):
        raise ValueError('Changed or failed feature input')
    semantics = {k: receipt[k] for k in SEMANTIC_KEYS}
    # Validate compatibility before opening arrays, including unused truth columns.
    manifest, record = load_record(artifact)
    if (semantics != record['feature_semantics']
            or receipt['compact_sha256'] != manifest['geometry']['detector_xml_sha256']):
        raise ValueError('Feature input geometry/semantics mismatch')
    with np.load(source, allow_pickle=False) as data:
        result = calibrate(data['features'], data['signal'], data['region'], data['valid_axis'],
                           geometry_sha256=receipt['compact_sha256'],
                           feature_semantics=semantics, kind=kind, artifact=artifact)
        event = data['event'].copy()
    if (event.shape != result['energy'].shape or not np.issubdtype(event.dtype, np.integer)
            or len(np.unique(event)) != len(event) or receipt['events'] != len(event)):
        raise ValueError('Invalid feature event identities/count')
    output.mkdir(parents=True, exist_ok=False)
    np.savez_compressed(output / 'calibrated.npz', event=event, **result)
    proof = dict(status='PASS', model_id=manifest['models'][kind]['id'],
                 events=len(event), energy_unit='GeV',
                 coefficients_sha256=manifest['coefficients_sha256'],
                 manifest_sha256=sha(Path(artifact) / 'manifest.json'),
                 inference_sha256=sha(__file__), core_sha256=record['core_sha256'],
                 feature_sha256=sha(source), feature_receipt_sha256=sha(features_dir / 'receipt.json'),
                 output_sha256=sha(output / 'calibrated.npz'),
                 zero_signals=int(result['zero_signal'].sum()),
                 fallback_events=int(result['fallback'].sum()),
                 gain_clipped_events=int(result['clipped'].sum()),
                 feature_extrapolated_events=int(result['feature_extrapolated'].sum()),
                 truth_inputs_used=False, coefficients_refitted=False)
    (output / 'receipt.json').write_text(json.dumps(proof, indent=2) + '\n')
    return proof


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--features', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--kind', choices=('spline', 'original'), default='spline')
    parser.add_argument('--artifact', type=Path, default=ARTIFACT)
    args = parser.parse_args()
    print(json.dumps(apply_file(args.features, args.output, args.kind, args.artifact), indent=2))


if __name__ == '__main__':
    main()
