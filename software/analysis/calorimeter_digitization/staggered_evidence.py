"""Curate portable, aggregate geometry/run evidence; never copy event payloads."""
import argparse
import json
from pathlib import Path

from angular_sample import save, sha


def read(path):
    return json.loads(path.read_text())


def curate(root, output):
    geometry = read(root / 'production-input/geometry-audit.json')
    native = read(root / 'native-dev.json')
    run = read(root / 'production12/receipt.json')
    proof = read(root / 'production12/readback.json')
    pilot = read(root / 'pilot12/readback.json')
    if native['status'] != 'PASS' or proof['status'] != 'PASS' or pilot['status'] != 'PASS':
        raise ValueError('Unsuccessful validation')
    if run['exit_code'] != 0 or run['events'] != 10000 or run['threads'] != 12:
        raise ValueError('Incomplete transport')
    if geometry['output_compact_sha256'] != native['compact_sha256']:
        raise ValueError('Native geometry differs from transport geometry')
    result = {k: v for k, v in geometry.items() if k not in ('barrel', 'endcap')}
    result['barrel'] = {k: v for k, v in geometry['barrel'].items() if k != 'layers'}
    result['barrel']['layers'] = [
        {k: v for k, v in layer.items() if k != 'modules'}
        for layer in geometry['barrel']['layers']]
    result['endcap'] = {k: v for k, v in geometry['endcap'].items() if k != 'families'}
    result['endcap']['families'] = [
        dict({k: v for k, v in family.items() if k != 'modules'},
             module_count=len(family['modules']))
        for family in geometry['endcap']['families']]
    result['native_validation'] = native
    result['run_receipt'] = {k: v for k, v in run.items() if k != 'command'}
    result['sample'] = read(root / 'production-input/sample.json')
    result['readback'] = proof
    result['pilot_readback'] = pilot
    result['disk_plan'] = read(root / 'disk-budget.json')
    result['full_geometry_audit_sha256'] = sha(root / 'production-input/geometry-audit.json')
    result['curator_sha256'] = sha(__file__)
    result['scope'] = ('Isolated PROTOTYPE; physical modules and inherited sector seams. '
                       'Material changes explicit; no engineering or production acceptance.')
    if len(json.dumps(result)) > 500_000:
        raise ValueError('Unexpectedly large aggregate: inspect before publication')
    output.mkdir(parents=True, exist_ok=True)
    save(output / 'geometry-and-run.json', result)
    save(output / 'coverage-screen.json', read(root / 'screen-dev/screen.json'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    curate(args.local_root, args.output)
