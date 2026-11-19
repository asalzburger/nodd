"""Prepare new fixed-direction primaries on byte-identical audited ECAL models."""
import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
MASS = 0.00051099895


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')


def primaries(output, events, energy, eta, phi):
    if events <= 0 or not all(math.isfinite(x) for x in (energy, eta, phi)) or energy <= MASS:
        raise ValueError('Invalid fixed primary specification')
    p = math.sqrt(energy * energy - MASS * MASS)
    momentum = [p * math.cos(phi) / math.cosh(eta), p * math.sin(phi) / math.cosh(eta), p * math.tanh(eta)]
    line = '1\n1 11 0 0 ' + ' '.join(f'{x:.17g}' for x in momentum + [MASS]) + '\n'
    with (output / 'particles.HEPEvt').open('w') as hepevt, (output / 'truth-input.jsonl').open('w') as truth:
        for i in range(events):
            hepevt.write(line)
            truth.write(json.dumps(dict(event=i, energy_GeV=energy, eta=eta, phi=phi, momentum_GeV=momentum), separators=(',', ':')) + '\n')


def prepare(protocol_path, sources, output):
    protocol = json.loads(protocol_path.read_text())
    point = protocol['point']
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    output.mkdir(parents=True, exist_ok=False)
    for model, source in sources.items():
        previous = json.loads((source / 'sample.json').read_text())
        for name in ('detector.xml', 'materials.xml'):
            if sha(source / name) != protocol['models'][model]['hashes'][name]:
                raise ValueError('Geometry differs from the frozen model: ' + model + ':' + name)
        for population, spec in {'pilot': protocol['pilot'], **protocol['populations']}.items():
            out = output / population / model
            out.mkdir(parents=True)
            for name in ('detector.xml', 'materials.xml'):
                shutil.copyfile(source / name, out / name)
            primaries(out, spec['events'], point['energy_GeV'], point['eta'], point['phi_rad'])
            manifest = deepcopy(previous)
            for key in ('source_primary_manifest_sha256', 'control'):
                manifest.pop(key, None)
            manifest.update(events=spec['events'], source_revision=revision,
                source_primary_revision=revision, input_seed=None,
                distributions={'total_energy_GeV': [point['energy_GeV']] * 2,
                               'eta': [point['eta']] * 2, 'phi_rad': [point['phi_rad']] * 2,
                               'independent_uniform': False, 'type': 'fixed single-electron direction'},
                electron_mass_GeV=MASS, input_sha256=sha(out / 'particles.HEPEvt'),
                truth_sha256=sha(out / 'truth-input.jsonl'),
                hashes={name: sha(out / name) for name in ('detector.xml', 'materials.xml', 'particles.HEPEvt', 'truth-input.jsonl')},
                geometry_source_manifest_sha256=sha(source / 'sample.json'),
                geometry_source_revision=previous['source_revision'],
                study_protocol_sha256=sha(protocol_path), producer_sha256=sha(__file__),
                validation_point={**point, 'population': population, 'events': spec['events'],
                                  'transport_seed': spec['transport_seeds'][model],
                                  'identity': '(detector, population, transport_seed, event)'})
            write(out / 'sample.json', manifest)
    write(output / 'preparation.json', {'protocol_sha256': sha(protocol_path), 'source_revision': revision,
          'producer_sha256': sha(__file__), 'primary_policy': 'New deterministic repeated four-vectors; populations/detectors use separate transport seeds',
          'manifests': {str(path.relative_to(output)): sha(path) for path in sorted(output.glob('*/*/sample.json'))}})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--lar-source', type=Path, required=True)
    parser.add_argument('--siw-source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    prepare(args.protocol, {'lar': args.lar_source, 'siw': args.siw_source}, args.output)


if __name__ == '__main__':
    main()
