#!/usr/bin/env python3
"""Check the Tracker TDR overlay or assemble its pinned, self-contained edition."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='New directory for a complete report source tree')
    parser.add_argument('--tdr-root', type=Path, default=REPO / 'docs/tdr')
    args = parser.parse_args()
    manifest = json.loads((HERE / 'manifest.json').read_text())
    original = manifest['source_files_sha256']
    result = manifest['result_files_sha256']
    changed = set(manifest['overlay_files'])
    overlay = HERE / 'overlay'
    actual = {p.relative_to(overlay).as_posix() for p in overlay.rglob('*') if p.is_file()}
    if actual != changed:
        raise ValueError('Overlay file inventory differs')
    if {p for p in result if result[p] != original.get(p)} != changed:
        raise ValueError('Result manifest does not match the declared changes')
    for name in changed:
        if digest((overlay / name).read_bytes()) != result[name]:
            raise ValueError('Overlay fingerprint differs: ' + name)
    for name, expected in {**manifest['evidence_sha256'], **manifest['geometry_sources_sha256']}.items():
        if digest((REPO / name).read_bytes()) != expected:
            raise ValueError('Parent evidence/source fingerprint differs: ' + name)
    for item in manifest['imported_figures']:
        if digest((REPO / item['source']).read_bytes()) != item['sha256'] or result[item['target']] != item['sha256']:
            raise ValueError('Imported figure differs: ' + item['target'])
    if args.output:
        # Read committed base bytes, so unrelated dirty submodule edits are preserved.
        archive = subprocess.check_output(['git', '-C', str(args.tdr_root), 'archive', manifest['tdr_input_revision']])
        with tarfile.open(fileobj=io.BytesIO(archive)) as source:
            files = {p.name: source.extractfile(p).read() for p in source.getmembers() if p.isfile()}
        if set(files) != set(original) or any(digest(files[p]) != original[p] for p in files):
            raise ValueError('Pinned TDR base differs from its source manifest')
        args.output.mkdir(parents=True, exist_ok=False)
        for name in result:
            target = args.output / name
            target.parent.mkdir(parents=True, exist_ok=True)
            data = (overlay / name).read_bytes() if name in changed else files[name]
            if digest(data) != result[name]:
                raise ValueError('Assembled report fingerprint differs: ' + name)
            target.write_bytes(data)
        print('Assembled complete report source:', args.output)
    print('PASS: overlay, unchanged geometry sources, evidence and three imported plots')


if __name__ == '__main__':
    main()
