#!/usr/bin/env python3
"""Render exactly two A4 pages from each DES-006 Markdown brief.

Supported source syntax: headings, paragraphs and one image per line. Page
breaks are explicit. Layout overflow is an error, never silently truncated.
Requires the existing reference-reading PyMuPDF environment.
"""
from pathlib import Path
import re
import pymupdf

ROOT = Path(__file__).resolve().parents[2]


def render(path):
    pages = path.read_text().split('<!-- PAGE -->')
    if len(pages) != 2:
        raise ValueError('Exactly two source pages required')
    doc = pymupdf.open()
    for number, content in enumerate(pages, 1):
        page = doc.new_page(width=595, height=842)
        y = 36
        for block in re.split(r'\n\s*\n', content.strip()):
            block = block.strip()
            if block.startswith('!['):
                image = re.fullmatch(r'!\[.*?\]\((.*?)\)', block)
                if not image:
                    raise ValueError('Invalid image markup')
                page.insert_image(pymupdf.Rect(36, y, 559, y + 190), filename=str(path.parent / image[1]))
                y += 198
                continue
            heading = block.startswith('#')
            size = 15 if block.startswith('# ') else 11 if heading else 10
            font = 'hebo' if heading else 'helv'
            text = re.sub(r'^#+ ', '', block).replace('\n', ' ')
            text = text.replace('**', '').replace('`', '')
            lines, line = [], ''
            for word in text.split():
                proposed = (line + ' ' + word).strip()
                if pymupdf.get_text_length(proposed, fontname=font, fontsize=size) > 520:
                    lines.append(line)
                    line = word
                else:
                    line = proposed
            if line:
                lines.append(line)
            height = (len(lines) + .5) * size * 1.25
            if y + height > 792:
                raise ValueError(f'{path.name}: page {number} exceeds content boundary')
            spare = page.insert_textbox(pymupdf.Rect(36,y,559,y+height), '\n'.join(lines), fontsize=size,
                                        fontname=font, lineheight=1.25, color=(.12,.16,.21))
            if spare < 0:
                raise ValueError(f'Overfull text block: {block[:50]}')
            y += height + 7
        page.insert_text((36,815),f'DES-006 | PROTOTYPE | 2026-09-18 | page {number}/2',fontsize=8,color=(.4,.4,.4))
    doc.set_metadata({'title':path.stem,'author':'nODD: SysArch, TrackTech, PhysVal, SoftEng (AI-assisted)'})
    out = path.with_suffix('.pdf')
    doc.save(out, garbage=4, deflate=True)
    print(f'{out.relative_to(ROOT)}: {len(doc)} pages')


if __name__ == '__main__':
    for cid in ['A','B']:
        render(ROOT / f'docs/design/DES-006-proposal-{cid}.md')
