#!/usr/bin/env python3
"""Publish the user-selected names without rewriting historical numerical evidence."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'docs/design/DES-006-reviewed-layouts.json'
OUTPUT = ROOT / 'docs/design/DES-006-named-layouts.json'
NAMES = {'A': ('cobe', 'classical barrel endcap'),
         'C1': ('pint', 'progressive inclined transition')}


def named_catalogue(source):
    if {c['id'] for c in source['candidates']} != set(NAMES):
        raise ValueError('Expected exactly the two reviewed A/C1 candidates')
    result = copy.deepcopy(source)
    result['active_options'] = [NAMES[k][0] for k in source['active_options']]
    for candidate in result['candidates']:
        old = candidate['id']
        candidate['legacy_id'] = old
        candidate['id'], candidate['name'] = NAMES[old]
    result['definition'] = ('User-selected names, 2026-09-25: A -> cobe; C1 -> pint. '
                            'Layer IDs and all physical values are unchanged. '
                            'Historical evidence keeps its original A/C1 keys.')
    return result


def main():
    source = json.loads(SOURCE.read_text())
    result = named_catalogue(source)
    result['naming_provenance'] = {
        'classification': 'NODD DESIGN CHOICE',
        'authority': 'Explicit user naming instruction, 2026-09-25; not design sign-off',
        'source': str(SOURCE.relative_to(ROOT)),
        'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'record': 'logs/codex/SESSION-2026-09-25-pr13-rebase.md'}
    OUTPUT.write_text(json.dumps(result, indent=2)+'\n')
    for old, (new, full_name) in NAMES.items():
        p = ROOT / f'docs/design/DES-006-reviewed-{old}.md'
        text = p.read_text()
        # These are exact labels, not replacements of the English article A.
        text = text.replace(f'# DES-006 {old}:', f'# DES-006 {new}:')
        text = text.replace('DRAFT / PROTOTYPE, 2026-09-24. Only A and C1 remain active.',
                            f'DRAFT / PROTOTYPE, 2026-09-25. {new}: {full_name} (formerly {old}). Only cobe and pint remain active.')
        for before, after in [('Reviewed A layout', 'cobe layout'),
                              ('Reviewed C1 layout', 'pint layout'),
                              ('reviewed-A-rz.png', 'reviewed-cobe-rz.png'),
                              ('reviewed-C1-rz.png', 'reviewed-pint-rz.png'),
                              ('DES-006-reviewed-layouts.json', 'DES-006-named-layouts.json'),
                              ('# A:', '# cobe:'), ('# C1:', '# pint:'),
                              ('relative to original A.', 'relative to original A (cobe control).'),
                              ('relative to original C1.', 'relative to original C1 (pint control).'),
                              ('A remains', 'cobe remains'), ('C1 tested', 'pint tested'),
                              ('run on A only', 'run on cobe only'),
                              ('revisit C1 row', 'revisit pint row')]:
            text = text.replace(before, after)
        (p.parent / f'DES-006-reviewed-{new}.md').write_text(text)
    print('Generated cobe/pint catalogue and brief sources; historical artifacts preserved')


if __name__ == '__main__':
    main()
