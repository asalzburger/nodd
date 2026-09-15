#!/usr/bin/env python3
"""Download user-supplied CERNBox PDF shares without overwriting existing PDFs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
NAMES = {
    'ATLAS-TDR-025': 'ATLAS-ITk-Strip-TDR.pdf',
    'ATLAS-TDR-030': 'ATLAS-ITk-Pixel-TDR.pdf',
    'ATLAS-TDR-031': 'ATLAS-HGTD-TDR.pdf',
    'CMS-TDR-014': 'CMS-Phase2-Tracker-TDR.pdf',
    'CMS-TDR-020': 'CMS-MTD-TDR.pdf',
}


def sources(path):
    entries = re.findall(r'^\|\s*([A-Z0-9-]+)\s*\|\s*https://cernbox\.cern\.ch/s/([A-Za-z0-9]+)\s*\|',
                         path.read_text(), re.MULTILINE)
    if not entries or len({label for label, _ in entries}) != len(entries):
        raise ValueError('Expected nonempty, uniquely labelled CERNBox table entries')
    return entries


def inspect_pdf(path):
    digest = hashlib.sha256()
    size = 0
    with path.open('rb') as stream:
        if stream.read(5) != b'%PDF-':
            raise ValueError('Response is not a PDF (missing PDF header)')
        stream.seek(0)
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            size += len(chunk)
            digest.update(chunk)
    return {'size_bytes': size, 'sha256': digest.hexdigest()}


def download(url, destination):
    if destination.exists():
        return {'acquisition': 'existing-local-file', **inspect_pdf(destination)}
    temporary = None
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            # Preserve partial downloads only until the request completes.
            with tempfile.NamedTemporaryFile(dir=destination.parent, suffix='.part', delete=False) as stream:
                temporary = Path(stream.name)
                for chunk in iter(lambda: response.read(1024 * 1024), b''):
                    stream.write(chunk)
            details = inspect_pdf(temporary)
            expected = response.headers.get('Content-Length')
            if expected is not None and int(expected) != details['size_bytes']:
                raise ValueError('Content length mismatch')
            # A hard link publishes atomically and fails if a concurrent writer won.
            os.link(temporary, destination)
        return {'acquisition': 'downloaded', **details}
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', nargs='+', help='Select report labels from sources.md')
    parser.add_argument('--receipt', type=Path, required=True, help='New JSON receipt; never overwrite')
    args = parser.parse_args()
    instructions = ROOT / 'reference/pdfs/sources.md'
    entries = sources(instructions)
    if args.only:
        unknown = set(args.only) - {label for label, _ in entries}
        if unknown:
            parser.error('Unknown labels: ' + ', '.join(sorted(unknown)))
        entries = [(label, token) for label, token in entries if label in args.only]
    receipt = {'schema_version': 1, 'instructions': 'reference/pdfs/sources.md',
               'instructions_sha256': hashlib.sha256(instructions.read_bytes()).hexdigest(),
               'verification': 'PDF header, byte count and SHA-256 only; bibliographic identity and PDF structure not verified.',
               'files': []}
    # Reserve the receipt before network I/O; refuse to overwrite prior evidence.
    with args.receipt.open('x') as output:
        for label, token in entries:
            filename = NAMES.get(label, label + '.pdf')
            destination = ROOT / 'reference/pdfs' / filename
            row = {'label': label, 'local_file': destination.relative_to(ROOT).as_posix()}
            try:
                row.update(download('https://cernbox.cern.ch/remote.php/dav/public-files/' + token, destination))
                row['status'] = 'available'
            except (OSError, ValueError, urllib.error.URLError) as error:
                row['status'] = 'failed'
                # Do not copy bearer share URLs or response bodies into public records.
                row['error'] = f'HTTP {error.code}' if isinstance(error, urllib.error.HTTPError) else type(error).__name__
            row['checked_at'] = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
            receipt['files'].append(row)
            output.seek(0)
            json.dump(receipt, output, indent=2)
            output.write('\n')
            output.truncate()
            output.flush()
            print(f"{label}: {row['status']}" + (f" ({row['size_bytes']} bytes)" if 'size_bytes' in row else ''), flush=True)
    return int(any(row['status'] == 'failed' for row in receipt['files']))


if __name__ == '__main__':
    raise SystemExit(main())
