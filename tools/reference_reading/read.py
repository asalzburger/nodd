#!/usr/bin/env python3
"""Content-addressed local PDF extraction, literal search and selected rendering."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import tempfile
import time
import unicodedata

import pymupdf

ROOT = Path(__file__).resolve().parents[2]
SETTINGS = {'schema_version': 1, 'text_sort': True, 'ocr': False, 'page_numbers': 'one-based'}


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def source(root, source_id):
    entries = json.loads((root / 'reference/manifest.yaml').read_text())['sources']
    item = next((s for s in entries if s['id'] == source_id), None)
    if not item:
        raise ValueError('Unknown source ID')
    path = (root / item['local_file']).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Source path escapes repository')
    actual = sha(path)
    if actual != item['sha256']:
        raise ValueError('Source hash differs from catalogue; review before updating')
    return path, actual


def identity(source_id, digest):
    return {'source_id': source_id, 'source_sha256': digest,
            'extractor_sha256': sha(Path(__file__)), 'python': platform.python_version(),
            'pymupdf': pymupdf.VersionBind, 'mupdf': pymupdf.VersionFitz,
            'settings': SETTINGS}


def cache_path(root, provenance):
    key = hashlib.sha256(json.dumps(provenance, sort_keys=True).encode()).hexdigest()
    return root / 'reference/cache' / provenance['source_id'] / key


def verify_cache(directory, provenance):
    metadata = json.loads((directory / 'metadata.json').read_text())
    if metadata['provenance'] != provenance:
        raise ValueError('Cache provenance mismatch')
    for name, digest in metadata['artifacts'].items():
        path = (directory / name).resolve()
        if not path.is_relative_to(directory.resolve()) or sha(path) != digest:
            raise ValueError('Corrupt extraction artifact: ' + name)
    return metadata


def extract(root, source_id):
    started = time.perf_counter()
    pdf, digest = source(root, source_id)
    provenance = identity(source_id, digest)
    destination = cache_path(root, provenance)
    if destination.exists():
        metadata = verify_cache(destination, provenance)
        return destination, metadata, True, time.perf_counter() - started
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix='.extract-', dir=destination.parent))
    try:
        pages = []
        with pymupdf.open(pdf) as doc:
            if doc.needs_pass:
                raise ValueError('Encrypted PDF needs a password')
            write_json(temporary / 'outline.json', doc.get_toc())
            for page in doc:
                number = page.number + 1
                text = page.get_text('text', sort=SETTINGS['text_sort'])
                text_file = f'page-{number:04d}.txt'
                (temporary / text_file).write_text(text)
                blocks_file = f'page-{number:04d}-blocks.json'
                blocks = [list(b) for b in page.get_text('blocks', sort=SETTINGS['text_sort']) if b[6] == 0]
                write_json(temporary / blocks_file, blocks)
                pages.append({'pdf_page': number, 'embedded_label': page.get_label() or None,
                              'text_file': text_file, 'blocks_file': blocks_file,
                              'characters': len(text), 'replacement_characters': text.count('\ufffd'),
                              'empty_text': not text.strip(), 'raster_image_references': len(page.get_images()),
                              'width_points': page.rect.width, 'height_points': page.rect.height})
            write_json(temporary / 'pages.json', pages)
            metadata = {'provenance': provenance, 'created_at': datetime.now(timezone.utc).isoformat(),
                        'page_count': len(doc), 'outline_entries': len(doc.get_toc()),
                        'embedded_label_rules': doc.get_page_labels(),
                        'empty_text_pages': [p['pdf_page'] for p in pages if p['empty_text']],
                        'replacement_character_pages': [p['pdf_page'] for p in pages if p['replacement_characters']],
                        'artifacts': {p.name: sha(p) for p in sorted(temporary.iterdir())}}
        metadata['extraction_seconds'] = time.perf_counter() - started
        write_json(temporary / 'metadata.json', metadata)
        # Rename publishes only a complete cache; no overwrite/repair option.
        os.rename(temporary, destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return destination, metadata, False, time.perf_counter() - started


def load_cache(root, source_id):
    pdf, digest = source(root, source_id)
    provenance = identity(source_id, digest)
    directory = cache_path(root, provenance)
    if not directory.exists():
        raise ValueError('No cache for these bytes/tool versions; run extract first')
    return pdf, directory, verify_cache(directory, provenance)


def search(directory, query, limit):
    if not query.strip() or limit < 1:
        raise ValueError('Nonempty query and positive limit required')
    results = []
    for page in json.loads((directory / 'pages.json').read_text()):
        text = (directory / page['text_file']).read_text()
        # Whitespace normalization makes line-wrapped phrases retrievable.
        normalized = ' '.join(unicodedata.normalize('NFKC', text).split())
        needle = ' '.join(unicodedata.normalize('NFKC', query).split()).lower()
        index = normalized.lower().find(needle)
        if index >= 0:
            results.append({'pdf_page': page['pdf_page'], 'embedded_label': page['embedded_label'],
                            'excerpt': normalized[max(0, index-80):index+220]})
            if len(results) == limit:
                break
    return results


def render(pdf, directory, page_numbers):
    outputs = []
    with pymupdf.open(pdf) as doc:
        if any(p < 1 or p > len(doc) for p in page_numbers):
            raise ValueError('PDF page number out of range')
        output = directory / 'renders'
        output.mkdir(exist_ok=True)
        for number in page_numbers:
            path = output / f'page-{number:04d}-120dpi.png'
            doc[number-1].get_pixmap(dpi=120).save(path)
            outputs.append({'pdf_page': number, 'path': str(path), 'sha256': sha(path)})
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('extract', 'search', 'render'):
        p = sub.add_parser(command)
        p.add_argument('source_id')
        if command == 'search':
            p.add_argument('query')
            p.add_argument('--limit', type=int, default=10)
        elif command == 'render':
            p.add_argument('pages', type=int, nargs='+')
    args = parser.parse_args()
    root = args.repo.resolve()
    try:
        if args.command == 'extract':
            directory, meta, hit, elapsed = extract(root, args.source_id)
            print(json.dumps({'cache': str(directory.relative_to(root)), 'cache_hit': hit,
                              'elapsed_seconds': elapsed, 'metadata': meta}, indent=2))
        else:
            pdf, directory, _ = load_cache(root, args.source_id)
            result = search(directory, args.query, args.limit) if args.command == 'search' else render(pdf, directory, args.pages)
            print(json.dumps(result, indent=2))
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'error: {error}\n')


if __name__ == '__main__':
    main()
