"""Build the identical four-page ECAL reviewer content as Markdown and PDF.

Markdown and source-provenance checks use standard Python. PDF generation and
parity checks use existing reportlab/pypdf; no detector runtime is required.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'docs/layouts/review'
SOURCE=BASE/'brief.json'
MARKDOWN=BASE/'ecal-layout-review.md'
PDF=BASE/'ecal-layout-review.pdf'
BRANCH='codex/ecal-layout-review-entry'
RAW='https://raw.githubusercontent.com/asalzburger/nodd/'+BRANCH+'/'
PDF_URL='https://github.com/asalzburger/nodd/blob/'+BRANCH+'/docs/layouts/review/ecal-layout-review.pdf'
LINK=re.compile(r'\[([^\]]+)\]\((https?://[^\s)]+)\)')

def load():
    d=json.loads(SOURCE.read_text())
    if len(d['pages'])!=4:raise ValueError('Exactly four pages required')
    for page in d['pages']:
        if not page['title'] or not page['blocks']:raise ValueError('Empty page')
        for b in page['blocks']:
            if b['type'] not in ('paragraph','heading','table','figure'):raise ValueError('Unsupported content block')
            for value in ([b.get('text',''),b.get('caption','')]+b.get('headers',[])+[cell for row in b.get('rows',[]) for cell in row]):
                for match in re.finditer(r'\[[^\]]+\]\(([^)]+)\)',str(value)):
                    if not match[1].startswith('https://'):raise ValueError('Use absolute public hyperlinks for identical PDF/PR content')
                if any(char in str(value) for char in ('‑','–','—')):raise ValueError('Use ASCII hyphens')
            if b['type']=='table':
                if not b['headers'] or any(len(row)!=len(b['headers']) for row in b['rows']):raise ValueError('Ragged table')
            if b['type']=='figure':
                p=ROOT/b['path']
                if not p.is_file() or not p.resolve().is_relative_to(BASE):raise ValueError('Figure missing or outside review snapshot')
    return d

def check_sources():
    sources=json.loads((BASE/'sources.json').read_text())['sources']
    for key,source in sources.items():
        data=subprocess.check_output(['git','show',source['revision']+':'+source['path']],cwd=ROOT)
        if hashlib.sha256(data).hexdigest()!=source['sha256']:
            raise ValueError('Pinned source hash differs: '+key)
        if key in ('layout001','layout002') and (BASE/(key+'.json')).read_bytes()!=data:
            raise ValueError('Layout snapshot differs from pinned source: '+key)
    return dict(status='PASS',pinned_source_hashes_checked=len(sources),layout_snapshots_checked=2)

def markdown(d):
    out=['# '+d['title'],'',d['subtitle'],'','Snapshot: '+d['date']+'. [Four-page PDF]('+PDF_URL+').','']
    for page in d['pages']:
        out+=['## '+page['title'],'']
        for b in page['blocks']:
            if b['type']=='paragraph':out += [b['text'],'']
            elif b['type']=='heading':out += ['### '+b['text'],'']
            elif b['type']=='figure':out += ['!['+b['alt']+']('+RAW+b['path']+')','',b['caption'],'']
            else:
                out += ['| '+' | '.join(x.replace('|','&#124;') for x in b['headers'])+' |',
                        '| '+' | '.join('---' for _ in b['headers'])+' |']
                out += ['| '+' | '.join(str(x).replace('|','&#124;') for x in row)+' |' for row in b['rows']]
                out += ['']
    return '\n'.join(out).rstrip()+'\n'

def rich(text):
    text=html.escape(str(text))
    text=LINK.sub(lambda m:'<a href="'+m[2]+'" color="#24588a">'+m[1]+'</a>',text)
    text=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',text)
    return text.replace(chr(96),'')

def body_strings(d):
    result=[d['title'],d['subtitle'],'Snapshot: '+d['date']+'. Four-page PDF.']
    links={PDF_URL}
    for page in d['pages']:
        result.append(page['title'])
        for b in page['blocks']:
            if b['type']=='figure':strings=[b['caption']]
            elif b['type']=='table':strings=b['headers']+[x for row in b['rows'] for x in row]
            else:strings=[b['text']]
            for s in strings:
                s=str(s);links.update(m[2] for m in LINK.finditer(s))
                result.append(LINK.sub(lambda m:m[1],s).replace('**','').replace(chr(96),''))
    return result,links

def check_pdf(d,path=PDF):
    from pypdf import PdfReader
    reader=PdfReader(path)
    if len(reader.pages)!=4:raise ValueError('PDF must have exactly four pages')
    actual=' '.join(p.extract_text() or '' for p in reader.pages)
    normalize=lambda s:re.sub(r'\s+','',s)
    expected,links=body_strings(d)
    missing=[s for s in expected if normalize(s) not in normalize(actual)]
    if missing:raise ValueError('PDF omitted source text: '+str(missing[:3]))
    actual_links=set()
    for page in reader.pages:
        for ref in page.get('/Annots',[]):
            action=ref.get_object().get('/A',{})
            if action.get('/URI'):actual_links.add(str(action['/URI']))
    if links-actual_links:raise ValueError('PDF omitted hyperlinks: '+str(links-actual_links))
    return dict(status='PASS',pages=4,text_blocks_checked=len(expected),hyperlinks_checked=len(links),
        content_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        image_sha256={b['path']:hashlib.sha256((ROOT/b['path']).read_bytes()).hexdigest() for p in d['pages'] for b in p['blocks'] if b['type']=='figure'},
        markdown_sha256=hashlib.sha256(MARKDOWN.read_bytes()).hexdigest(),
        pdf_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        interpretation='Same source prose, tables, captions, drawings and clickable citations in Markdown and PDF. Pagination is presentation.',
        renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())

def pdf(d,font_dir=None):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak
    normal,bold='Helvetica','Helvetica-Bold'
    if font_dir:
        for name,file in [('ReviewSans','LiberationSans-Regular.ttf'),('ReviewSansBold','LiberationSans-Bold.ttf')]:
            pdfmetrics.registerFont(TTFont(name,str(font_dir/file)))
        pdfmetrics.registerFontFamily('ReviewSans',normal='ReviewSans',bold='ReviewSansBold',italic='ReviewSans',boldItalic='ReviewSansBold')
        normal,bold='ReviewSans','ReviewSansBold'
    w,h=A4; margin=40; width=w-2*margin
    styles={
      'body':ParagraphStyle('body',fontName=normal,fontSize=10.3,leading=14,spaceAfter=7,textColor=colors.HexColor('#233247')),
      'table':ParagraphStyle('table',fontName=normal,fontSize=9.6,leading=12.6,spaceAfter=0),
      'caption':ParagraphStyle('caption',fontName=normal,fontSize=9,leading=12,spaceAfter=8,textColor=colors.HexColor('#46556b')),
      'section':ParagraphStyle('section',fontName=bold,fontSize=16,leading=20,spaceAfter=10,textColor=colors.HexColor('#233247')),
      'heading':ParagraphStyle('heading',fontName=bold,fontSize=11.3,leading=15,spaceBefore=4,spaceAfter=5),
      'title':ParagraphStyle('title',fontName=bold,fontSize=21,leading=25,spaceAfter=7,textColor=colors.HexColor('#233247'))}
    story=[]
    for index,page in enumerate(d['pages']):
        if index==0:
            story += [Paragraph(rich(d['title']),styles['title']),Paragraph(rich(d['subtitle']),styles['caption']),
                Paragraph('Snapshot: '+d['date']+'. <a href="'+PDF_URL+'" color="#24588a">Four-page PDF</a>.',styles['caption'])]
        story.append(Paragraph(rich(page['title']),styles['section']))
        for b in page['blocks']:
            if b['type'] in ('paragraph','heading'):story.append(Paragraph(rich(b['text']),styles['body' if b['type']=='paragraph' else 'heading']))
            elif b['type']=='figure':
                from PIL import Image as PILImage
                with PILImage.open(ROOT/b['path']) as im:iw,ih=im.size
                story += [Image(str(ROOT/b['path']),width=width,height=width*ih/iw),Paragraph(rich(b['caption']),styles['caption'])]
            else:
                rows=[[Paragraph('<b>'+rich(x)+'</b>',styles['table']) for x in b['headers']]]
                rows += [[Paragraph(rich(x),styles['table']) for x in row] for row in b['rows']]
                if len(b['headers'])==2:col=[width*.32,width*.68]
                elif len(b['headers'])==3:col=[width*.30,width*.35,width*.35]
                else:col=[width/len(b['headers'])]*len(b['headers'])
                table=Table(rows,colWidths=col,hAlign='LEFT',repeatRows=1)
                table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eef4')),
                    ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f7f9fb')]),
                    ('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#9bafc4')),
                    ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
                    ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
                story += [table,Spacer(1,8)]
        if index!=3:story.append(PageBreak())
    def footer(canvas,doc):
        canvas.setFont(normal,9);canvas.setFillColor(colors.HexColor('#6b7c90'))
        canvas.drawRightString(w-margin,24,str(doc.page)+' / 4')
    doc=SimpleDocTemplate(str(PDF),pagesize=A4,rightMargin=margin,leftMargin=margin,topMargin=36,bottomMargin=42,
        title=d['title'],author='nODD',subject=d['subtitle'],pageCompression=1,invariant=1)
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return check_pdf(d)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--markdown-only',action='store_true');p.add_argument('--check',action='store_true');p.add_argument('--font-dir',type=Path);p.add_argument('--check-sources',action='store_true',help='Verify pinned Git source objects (fetch component PR refs first)');a=p.parse_args()
    if a.check_sources:
        print(json.dumps(check_sources(),indent=2))
        if not a.check:raise SystemExit(0)
    d=load();md=markdown(d)
    if a.check:
        if not MARKDOWN.is_file() or MARKDOWN.read_text()!=md:raise SystemExit('Markdown differs from canonical content')
        report=check_pdf(d)
        print(json.dumps(report,indent=2))
    else:
        MARKDOWN.write_text(md)
        if not a.markdown_only:
            report=pdf(d,a.font_dir);(BASE/'content-check.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps(report,indent=2))
        else:print('Wrote identical-content PR description source')
