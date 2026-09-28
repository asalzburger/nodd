#!/usr/bin/env python3
"""Build the reviewer brief from TeX and presentation crops of existing SVGs."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / 'docs/design'
OUTPUT = DESIGN / 'DES-001-review-summary.pdf'
# SVG display coordinates only; these crops carry no detector dimensions.
CROPS = (
    ('DES-001-compact-modules.svg', 'cross-section', (0, 450, 1280, 365)),
    ('DES-001-compact-modules.svg', 'compact-plan', (0, 80, 1280, 365)),
    ('DES-001-quad-modules.svg', 'quad-plan', (0, 85, 1200, 540)),
)


def main():
    for executable in ('rsvg-convert', 'pdflatex', 'pdfinfo'):
        if not shutil.which(executable):
            raise SystemExit(f'Required executable missing: {executable}')
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    with tempfile.TemporaryDirectory(prefix='nodd-module-summary-') as location:
        work = Path(location)
        for source, label, box in CROPS:
            tree = ET.parse(DESIGN / 'figures' / source)
            svg = tree.getroot()
            svg.set('viewBox', ' '.join(map(str, box)))
            svg.set('width', str(box[2]))
            svg.set('height', str(box[3]))
            cropped = work / f'{label}.svg'
            tree.write(cropped, encoding='utf-8', xml_declaration=True)
            subprocess.run(['rsvg-convert', '--format', 'pdf', '--output',
                            str(work / f'{label}.pdf'), str(cropped)], check=True)
        shutil.copy(DESIGN / 'DES-001-review-summary.tex', work / 'summary.tex')
        result = subprocess.run(['pdflatex', '-interaction=nonstopmode',
                                 '-halt-on-error', 'summary.tex'], cwd=work,
                                capture_output=True, text=True)
        if result.returncode:
            raise SystemExit(result.stdout[-6000:] + result.stderr)
        log = (work / 'summary.log').read_text()
        if 'Overfull' in log:
            raise SystemExit('Summary layout failure:\n' + '\n'.join(line for line in log.splitlines() if 'Overfull' in line))
        info = subprocess.check_output(['pdfinfo', str(work / 'summary.pdf')], text=True)
        match = re.search(r'^Pages:\s+(\d+)$', info, re.MULTILINE)
        if not match or int(match[1]) > 3:
            raise SystemExit('Reviewer summary exceeds the three-page limit.')
        shutil.copy(work / 'summary.pdf', OUTPUT)
        print(f'Built {OUTPUT.relative_to(ROOT)}: {match[1]} A4 pages; no overfull boxes.')


if __name__ == '__main__':
    main()
