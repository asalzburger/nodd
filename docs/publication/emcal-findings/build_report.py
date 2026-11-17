#!/usr/bin/env python3
"""Build the eight-page, source-pinned EM calorimeter findings review. No simulation."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
from xml.sax.saxutils import escape

import reportlab
from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Flowable, Frame, Image, Paragraph, Spacer, Table, TableStyle
from pypdf import PdfReader
from response_comparison import drawing as comparison_drawing

ROOT=Path(__file__).resolve().parents[3]
BASE='79a967aa3fe78a525f15ede780c26be0cd73aeae'
HIST='3ebafd340b0e084c5e42e57123de115e3f489244'
DATE='2026-11-17'
SOURCES={
 'odd_assessment':(BASE,'docs/validation/ODD-realism-assessment.md'),
 'fixed_report':(BASE,'docs/validation/issue117/nodd-digitization-results.md'),
 'fixed_data':(BASE,'docs/validation/issue117/previews/nodd-digitized-response.json'),
 'siw_barrel':(BASE,'docs/design/DES-031-siw-barrel-prototype.md'),
 'siw_endcap':(BASE,'docs/design/DES-030-ecal-edge-sensors.md'),
 'continuous':(HIST,'docs/validation/ecal10k-untiled/README.md'),
 'staggered':(HIST,'docs/validation/ecal-staggering/README.md'),
 'highstat':(HIST,'docs/validation/ecal-highstat/README.md'),
 'lar_barrel':(BASE,'docs/design/DES-032-allegro-lar-barrel.md'),
 'lar_endcap':(BASE,'docs/design/DES-033-allegro-lar-endcaps.md'),
 'matched_report':(BASE,'docs/validation/lar10k/README.md'),
 'matched_data':(BASE,'docs/validation/lar10k/summary.json'),
 'matched_figure':(BASE,'docs/validation/lar10k/figures/angular-comparison.png'),
 'routing_proposal':(BASE,'docs/design/inputs/DES-032-side-rear-routing.md'),
 'routing_native':(BASE,'docs/validation/lar-routing-dd4hep/README.md'),
 'gap_report':(BASE,'docs/validation/lar-gap10k/README.md'),
 'gap_data':(BASE,'docs/validation/lar-gap10k/summary.json'),
 'gap_figure':(BASE,'docs/validation/lar-gap10k/figures/angular-widths.png'),
 'siw_placement':(BASE,'docs/validation/siw-real-wedge-default/README.md'),
 'lar_placement':(BASE,'docs/validation/lar-placement/README.md'),
}

def blob(key):
 rev,path=SOURCES[key]
 return subprocess.check_output(['git','show',rev+':'+path],cwd=ROOT)

def digest(data):return hashlib.sha256(data).hexdigest()
def link(key):
 rev,path=SOURCES[key]
 return 'https://github.com/asalzburger/nodd/blob/'+rev+'/'+path

FONTDIR=Path(reportlab.__file__).parent/'fonts'
for name,file in [('Body','Vera.ttf'),('Bold','VeraBd.ttf'),('Italic','VeraIt.ttf')]:
 pdfmetrics.registerFont(TTFont(name,str(FONTDIR/file)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Italic',boldItalic='Bold')
rl_config.useA85=False
INK=colors.HexColor('#172b3a');MUTED=colors.HexColor('#506373');GOLD=colors.HexColor('#cccc00')
PALE=colors.HexColor('#f7f7dd');LINE=colors.HexColor('#d8dfe3');BLUE=colors.HexColor('#2369a0');PURPLE=colors.HexColor('#7846a0')
W,H=A4;M=44;CW=W-2*M
styles={
 'body':ParagraphStyle('body',fontName='Body',fontSize=9.6,leading=14.0,textColor=INK,spaceAfter=8),
 'lead':ParagraphStyle('lead',fontName='Body',fontSize=11,leading=16,textColor=INK,spaceAfter=12),
 'h1':ParagraphStyle('h1',fontName='Bold',fontSize=22,leading=27,textColor=INK,spaceAfter=12),
 'h2':ParagraphStyle('h2',fontName='Bold',fontSize=12,leading=16,textColor=INK,spaceBefore=7,spaceAfter=6),
 'hero':ParagraphStyle('hero',fontName='Bold',fontSize=28,leading=33,textColor=INK,spaceAfter=13),
 'small':ParagraphStyle('small',fontName='Body',fontSize=8.1,leading=11.5,textColor=MUTED,spaceAfter=7),
 'cell':ParagraphStyle('cell',fontName='Body',fontSize=8.4,leading=11.4,textColor=INK),
 'head':ParagraphStyle('head',fontName='Bold',fontSize=8.4,leading=11.5,textColor=colors.white),
 'ref':ParagraphStyle('ref',fontName='Body',fontSize=8.3,leading=11.6,textColor=INK,spaceAfter=9),
}
def p(text,style='body'):return Paragraph(text,styles[style])
def h(text):return p(text,'h2')
def table(headers,rows,widths=None):
 data=[[p(escape(str(x)),'head') for x in headers]]+[[p(str(x),'cell') for x in row] for row in rows]
 t=Table(data,colWidths=widths or [CW/len(headers)]*len(headers),hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),INK),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f2f5f6')]),('LINEBELOW',(0,-1),(-1,-1),.5,LINE)]))
 return t

def box(text):
 t=Table([[p(text)]],colWidths=[CW]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('BOX',(0,0),(-1,-1),.6,GOLD),('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),3)]));return t

class AngularPlot(Flowable):
 """Render retained bin means/percentile endpoints as vector graphics, without refitting."""
 def __init__(self,series,axes,gap=False):
  super().__init__();self.width=CW;self.height=215;self.series=series;self.axes=axes;self.gap=gap
 def draw(self):
  c=self.canv;styles=[([],0),([4,2],1),([1,2],2)]
  def marker(x,y,kind):
   c.setFillColor(GOLD);c.setStrokeColor(INK);c.setLineWidth(.6)
   if kind==0:c.circle(x,y,2.1,fill=1,stroke=1)
   elif kind==1:c.rect(x-2,y-2,4,4,fill=1,stroke=1)
   else:
    path=c.beginPath();path.moveTo(x,y+2.5);path.lineTo(x-2.5,y-2);path.lineTo(x+2.5,y-2);path.close();c.drawPath(path,fill=1,stroke=1)
  for i,(label,model) in enumerate(self.series):
   x=10+i*(CW/len(self.series));c.setStrokeColor(GOLD);c.setLineWidth(1.2);c.setDash(styles[i][0]);c.line(x,202,x+17,202);c.setDash([]);marker(x+8,202,i);c.setFillColor(INK);c.setFont('Body',8.2);c.drawString(x+23,199,label)
  for panel,axis in enumerate(self.axes):
   left=35+panel*(CW/2+5);bottom=37;ww=CW/2-40;hh=140
   edges=self.series[0][1]['projections'][axis]['edges'];factor=180/math.pi if axis=='siw_folded_phi' else 1
   xmin,xmax=edges[0]*factor,edges[-1]*factor
   ymax=(50 if panel==0 else 100) if self.gap else (70 if panel==0 else 130)
   yticks=list(range(0,int(ymax)+1,10 if self.gap and panel==0 else 20 if panel==0 or self.gap else 40))
   X=lambda z:left+(z-xmin)/(xmax-xmin)*ww;Y=lambda z:bottom+z/ymax*hh
   c.setFont('Body',7.5)
   for y in yticks:
    c.setStrokeColor(LINE);c.setLineWidth(.35);c.line(left,Y(y),left+ww,Y(y));c.setFillColor(MUTED);c.drawRightString(left-5,Y(y)-2,str(y))
   c.setStrokeColor(MUTED);c.setLineWidth(.5);c.rect(left,bottom,ww,hh,fill=0,stroke=1)
   xticks=([0,1,2,3] if panel==0 else [1.1,1.3,1.5] if self.gap else [-10,0,10])
   for x in xticks:
    c.line(X(x),bottom,X(x),bottom-3);c.setFillColor(MUTED);c.drawCentredString(X(x),bottom-13,f'{x:g}')
   for i,(_,model) in enumerate(self.series):
    projection=model['projections'][axis];rows=projection['bins'];assert len(rows)==len(edges)-1
    coords=[]
    for a,b,row in zip(edges,edges[1:],rows):
     x=(a+b)/2*factor;y=100*row['fractional_width'];lo,hi=[100*z for z in row['fractional_width_bootstrap']['ci95']]
     assert 0<=lo<=hi<=ymax and 0<=y<=ymax
     xx=X(x);coords.append((xx,Y(y)));c.setDash([]);c.setStrokeColor(GOLD);c.setLineWidth(.55)
     c.line(xx,Y(lo),xx,Y(hi));c.line(xx-2,Y(lo),xx+2,Y(lo));c.line(xx-2,Y(hi),xx+2,Y(hi))
    c.setStrokeColor(GOLD);c.setLineWidth(1.15);c.setDash(styles[i][0]);path=c.beginPath();path.moveTo(*coords[0])
    for pair in coords[1:]:path.lineTo(*pair)
    c.drawPath(path);c.setDash([])
    for xx,yy in coords:marker(xx,yy,i)
   c.setFont('Body',8);c.setFillColor(INK);c.drawCentredString(left+ww/2,11,'|eta|' if panel==0 else 'fine |eta|' if self.gap else 'sector-folded phi [deg]')
   c.saveState();c.translate(left-25,bottom+hh/2);c.rotate(90);c.drawCentredString(0,0,'SD(R) / mean(R) [%]');c.restoreState()

class Routing(Flowable):
 """Schematic from declared envelope/centreline seeds; no clearance/volume claim."""
 def __init__(self):super().__init__();self.width=CW;self.height=294
 def draw(self):
  c=self.canv
  for i,(title,front,back,start,color) in enumerate([
    ('Previous layout: front-gap offset, 800 mm warm gap',4.9,5.86,4.17,BLUE),
    ('Merged working layout: side neck, 400 mm warm gap',4.5,5.46,3.30,PURPLE)]):
   ybase=178-i*154;xbase=27;ww=CW-43;hh=99
   X=lambda z:xbase+(z-2.9)/(6.55-2.9)*ww
   Y=lambda r:ybase+(r-2.3)/(4.95-2.3)*hh
   c.setFillColor(INK);c.setFont('Bold',9);c.drawString(0,ybase+109,title)
   def rect(z0,z1,r0,r1,fill):
    c.setFillColor(fill);c.setStrokeColor(MUTED);c.setLineWidth(.45);c.rect(X(z0),Y(r0),X(z1)-X(z0),Y(r1)-Y(r0),fill=1,stroke=1)
   rect(2.9,4.1,2.3,2.83,PALE);rect(front,back,2.3,2.949,PALE)
   rect(2.9,4.1,2.3,2.60,GOLD);rect(front+.11,back-.4,2.3,2.78,GOLD)
   rect(2.9,5.86,3.13,4.626,colors.HexColor('#cc6600'))
   rect(6.36,6.55,2.3,4.616,colors.HexColor('#cc6600'))
   c.setFillColor(INK);c.setFont('Body',8);c.drawString(X(3.04),Y(3.75),'HCAL barrel')
   c.drawString(X(3.0),Y(2.39),'LAr barrel');c.drawString(X(front+.14),Y(2.39),'LAr endcap')
   c.setStrokeColor(color);c.setLineWidth(2.5)
   path=c.beginPath();path.moveTo(X(start),Y(2.7353));end=start+.6194
   path.curveTo(X(start+.20),Y(2.7353),X(end-.20),Y(3.029),X(end),Y(3.029))
   path.lineTo(X(5.88),Y(3.029));path.curveTo(X(6.12),Y(3.029),X(6.28),Y(3.22),X(6.28),Y(3.429));path.lineTo(X(6.28),Y(4.8));c.drawPath(path)
   c.setFont('Body',7.7);c.setFillColor(color);c.drawString(X(4.8),Y(3.22),'outer bus + rear exit')
   c.setStrokeColor(MUTED);c.setLineWidth(.5);c.line(X(4.1),Y(2.21),X(front),Y(2.21));c.setFillColor(INK)
   c.drawCentredString((X(4.1)+X(front))/2,Y(2.21)-9,str(round((front-4.1)*1000))+' mm')
   c.drawCentredString((X(5.86)+X(6.36))/2,Y(4.8)+2,'500 mm exit')
   c.setFont('Body',7);c.drawString(X(2.9),Y(4.8),'R increases upward');c.drawRightString(CW,ybase-18,'|z| increases to the right')


def build(output):
 output.parent.mkdir(parents=True,exist_ok=True);assets=output.parent/'render-assets';assets.mkdir(exist_ok=True)
 matched=json.loads(blob('matched_data'));gap=json.loads(blob('gap_data'))
 def width(row):
  lo,hi=row['fractional_width_bootstrap']['ci95'];return f"{100*row['fractional_width']:.2f} [{100*lo:.2f}, {100*hi:.2f}]"
 rows=[]
 for k,label in [('siw_original','Si-W original'),('siw_staggered','Si-W staggered'),('lar','LAr, 800 mm reference')]:
  r=matched['models'][k]['global'];rows.append([label,f"{100*r['mean_response']:.3f}",width(r),str(r['zero_events']),str(r['below_half_mean_events'])])
 r=gap['views']['H']['models']['candidate']['global'];rows.append(['LAr, 400 mm working',f"{100*r['mean_response']:.3f}",width(r),str(r['zero_events']),str(r['own_global_tail_events'])])
 pages=[]
 pages.append([
  p('Electromagnetic<br/>calorimeter findings','hero'),
  p('From ODD to realistic Si-W and ALLEGRO-style LAr','lead'),
  p('Decision review | updated 17 November 2026 | PUB-EMCAL-2026-11-15','small'),
  box('<b>Selected nODD ECAL baseline.</b> ALLEGRO-style LAr with the 400 mm warm gap, following the human review direction of 17 November 2026. Retain realistic Si-W as a reference and alternative. Prioritize connected services, hermeticity and validated readout during integration.'),
  Spacer(1,12),
  p('The sequence of studies changes the picture: ODD provides a useful idealized sampling reference; explicit nODD Si-W hardware exposes inactive regions and passive-material effects; LAr gives a substantially smoother raw electron response in the matched broad-spectrum sample. The LAr barrel-endcap transition was its weakest region and improves strongly when the warm gap is reduced. [1-9]'),
  table(['Finding','Evidence and implication'],[
   ['Realism matters','At 20 GeV/c, detailed Si-W records only about 52-62% of the ODD mean silicon signal at the three illustrated directions. The full geometry/material changes are responsible collectively; the deficit is not a wafer-gap measurement.'],
   ['Staggering helps, cracks persist','Matched 10k raw SD/mean improves 43.09% to 39.27%. The independent 20k calibrated spline result is 30.21%, with strong residual seam losses.'],
   ['LAr is the stronger working option','Matched 10k raw SD/mean is 17.84% with the source-era gap and 13.56% with the reduced gap. In the fixed transition region it improves 44.18% to 21.00%.']],[117,CW-117]),
  Spacer(1,12),
  p('<b>Working-configuration status.</b> The PR145 reviewer records selection of LAr400 after discussion with Michael Duehrssen. This is a human working-baseline choice, without new engineering sign-off. The response study is ECAL-only; connected services and collar interfaces still need qualification. The existing combined exporter and full-layout drawings remain the validated 800 mm integration control.'),
  p('<b>Reading the numbers.</b> SD/mean includes zeros and tails. Broad-spectrum widths are not fixed-energy intrinsic resolution. Figure 1 labels ODD as an unmatched fixed-energy reference; the three 10k curves share their primaries. Sensitive sampling fractions alone do not rank performance.','small')
 ])
 pages.append([
  p('1  What changed from ODD','h1'),
  p('ODD is a simulation reference; the nODD Si-W model asks what happens when sensors, cassettes and local hardware occupy real space.','lead'),
  table(['Representation','ODD reference','Realistic nODD Si-W'],[
   ['Sampling','48 repetitions; 1.9 mm tungsten alloy and 0.5 mm sensitive silicon, with G10, HV/ground and PCB mixtures.','48 layers; 1.9 mm tungsten, 8 mm cassette body and 1 mm installation allowance: 10.9 mm pitch.'],
   ['Sensitive/readout geometry','5.1 mm virtual cells; no qualified detailed wafer/cassette/service inventory.','90 mm wafers, 88 mm active windows, 94 mm PCBs on 96 mm pitch; 5.5 mm virtual pads and passive guards.'],
   ['Hardware scope','Generic layered sampling and effective passive slices.','ASIC/thermal stacks, PCB/conductors, frames, cooling and reserved service bays; sixteen sectors.']],[96,196,CW-292]),
  p('The nODD copper cooling plates and other hardware change both material and active coverage. Virtual cell size must not be confused with physical sensor tiling. The ODD source stack has no matching 3 mm copper cooling plate. [1-3]'),
  h('A controlled illustration, separate from the 10k campaign'),
  p('Electrons at 20 GeV/c, origin, phi=0.123 rad; 200 events per geometry and direction. Both transports use B=0, FTFP_BERT, 0.7 mm range cuts and a 5 mm charged-step cap in active silicon. Fractions use persisted primary total energy. [2]','small'),
  table(['eta','Mean Si/E [%], ODD / nODD','Raw SD/mean [%], ODD / nODD'],[
   ['0','2.6460 / 1.6463','2.9257 / 4.7584'],['1','2.6978 / 1.5379','3.7422 / 4.8719'],['2','2.6475 / 1.3675','3.2242 / 7.7722']],[40,230,CW-270]),
  Spacer(1,8),
  p('Across the broader fixed-point electron/photon matrix the raw mean nODD/ODD ratio spans 0.488-0.629. Electronics-model changes are much smaller, about 0.5-1.2% in mean signal. This identifies a geometry/material effect, without isolating its individual causes. Lower silicon signal does not mean that the same fraction of total shower energy escaped.'),
  p('The geometry transports are independent. Raw and digitized stages are paired within a geometry; the shared ODD calibration preserves absolute response differences. One stochastic pair-only muon width gate failed, so complete original/native stochastic equivalence is not established. No LAr digitization comparison is inferred. [2]','small')
 ])
 pages.append([
  p('2  What Si-W improvements achieve','h1'),
  p('Inactive structure, rather than the virtual pad grid alone, sets the central limitation. Calibration can improve estimates, but it cannot recover information from an event with no measured signal.','lead'),
  h('Geometry diagnosis and physical mitigation'),
  p('<b>Original tiling.</b> Aligned board gaps, guard rims, service reservations and full-depth sector seams produce large angular tails. In the 10k scan the two seam-adjacent folded-phi bins have widths near 110%, versus 22.59-25.32% in interior bins. All 42 zero signals are retained. [4,7]'),
  p('<b>Continuous-silicon control.</b> Filling internal gaps reduces interior widths to 3.69-4.10% and seam widths to about 27%; 37 zeros remain. It adds 2475.64 kg silicon and removes 447.43 kg aluminium. This deliberately unbuildable, material-changing control diagnoses inactive regions; it is neither ODD nor a deployable solution. [4]'),
  p('<b>Physical staggering.</b> Four tangential/axial phases (0,0), (48,0), (0,48), (48,48) mm on the 96 mm pitch use actual narrow edge boards and changed packing. Raw inclusive width improves 43.09% to 39.27%, but 42 zeros and full-depth sector seams remain. A one-pitch slab shift alone does not stagger the internal board lattice. [4]'),
  h('Calibration: use the independent validation result'),
  table(['Same fresh 20k validation sample','Closed linear','Closed spline'],[
   ['Mean reconstructed / true energy','1.00287','1.00300'],['All-event SD/mean','31.322%','30.209%'],['Fractional-error RMS','31.412%','30.301%'],['Estimated energy below half truth','9.790%','9.380%']],[CW-182,91,91]),
  Spacer(1,8),
  p('PR137 used 100k training electrons and 20k fresh validation electrons, with models frozen before validation inspection. The spline gain is 1.112 percentage points against the linear comparator on that same 20k. Its full-refit approximate 95% width range is 29.596-30.817%. [5]'),
  p('Inclusive closure conceals local losses: spline sector-edge widths remain 73.23/75.06%, versus 11.01-12.65% inside sectors; all 84 zeros remain. The earlier 10k cross-fit gave 32.22% but mean energy was 8.09% low. That figure is not paired with the later 30.21% result. Neither calibrated sample is the raw LAr comparison. [4,5]','small'),
  p('Reusable solid mothers make these detailed models practical: Si-W volume-map build fell from 3953.8 s to 23.0 s; a separate LAr serial probe reached its first event in 67.4 s versus 522.3 s. These are different metrics and one-pair descriptive benchmarks, not a cross-technology speed ranking. [10]','small')
 ])
 pages.append([
  p('3  Selected LAr baseline','h1'),
  p('The ALLEGRO-style alternative replaces sensor-board sampling with inclined lead/steel absorbers, electrodes and liquid-argon gaps, while explicitly representing cryostats and local services.','lead'),
  p('The barrel uses 1536 inclined periods and eleven longitudinal electrode segments; each turbine endcap has three wheels with 384/720/1360 periods and a 450 mm sampling depth. Geometric readout totals 3,488,768 canonical cells across barrel and endcaps. These are virtual addresses, not a qualified electronics bill or charge-collection model. [6]'),
  table(['Matched origin electrons','Mean [%]','Raw width [%], 95% CI','Zeros','Low tails'],rows,[150,68,149,45,CW-412]),
  p('H is summed saved sensitive-hit energy. The table uses identical 10k primaries: uniform total E=10-80 GeV, eta=-3...3, full phi; ECAL-only, B=0, FTFP_BERT, 0.7 mm cuts and 5 mm active charged-step cap. Low tails use H/E below half each model\'s own global mean. [7,9]','small'),
  comparison_drawing(json.loads((Path(__file__).parent/'response-comparison.json').read_text()),CW),
  p('Figure 1. Requested sigma(E)/E raw-response proxy: SD(H/Etrue)/mean(H/Etrue) versus |eta|. Three matched curves use 0.05-wide bins (136-189 events each), all zeros, and 1000 shared whole-primary bootstrap resamples. Bars are pointwise 95% intervals. ODD retains its original detector scope: separate 20 GeV/c, phi=0.123, 200-event eta0/1/2 points with source 5000-resample intervals, not a fourth matched curve. No calibration or new transport. Standalone vector: response-comparison.svg. [2,7,9]','small'),
  p('The global staggered-Si-W minus LAr800 width difference is 21.43 percentage points [20.42, 22.48]. In the fixed 999-event transition it is only 3.03 points [-0.75, 7.05]; that interval does not establish a transition advantage for the old LAr gap. [7]')
 ])
 pages.append([
  p('4  Updated routing and its boundary','h1'),
  p('Move the outward service offset to barrel-side necks before the barrel end, run an axial bus outside the endcap, and turn radially outward in the rear service break. Endcap services also leave at the rear. [8]','lead'),
  Routing(),
  p('Figure 2. Schematic evolution to the merged working configuration; axes have different scales. Curves indicate connectivity, not installed bundle cross-sections or a clearance proof. The barrel is fixed, the ECAL endcap moves inward by 400 mm and HCAL stays fixed. ECAL is yellow; HCAL is orange. The unobstructed rear radial-exit window remains 500 mm. [8,9]','small'),
  table(['DD4hep routing representation','What is preserved or still required'],[
   ['Material-preserving bends','32 representative 20/18 mm OD/ID steel/N2 pipes; mitered chords approximate bends. Both routes retain 74.4014 kg steel and 0.809145 kg N2 in that illustrative inventory.'],
   ['Cable and jacket scope','100 mm jacket and cable lanes remain unmaterialized envelopes. Their material, real bundle packing and total circuit multiplicity are not supplied by the pipe model.'],
   ['Validation versus integration','Standalone old/new models pass material/navigation and 10 nm overlap checks. The unchanged-ECAL context diagnostic found existing-pipe and closed-wall contacts; a naive overlay is invalid.']],[143,CW-143]),
  Spacer(1,8),
  p('<b>Engineering work remaining.</b> Define sealed warm/cold ports, separate process circuits and headers; repack affected boards/supports; demonstrate thermal/hydraulic/structural margins and access. The rear turn and magnet/HCAL crossings require full three-dimensional bundle checks. The forward-collar and installation interfaces remain open. Merged working status does not resolve these checks. [8]','small')
 ])
 pages.append([
  p('5  Reduced-gap performance','h1'),
  p('The merged working choice is a 400 mm front warm gap, reduced from the source-era 800 mm. The numerical experiment moves each complete signed endcap 400 mm inward while keeping the barrel fixed.','lead'),
  table(['Complete accepted deposit A/E','800 mm reference','400 mm working'],[
   ['Global SD/mean, 10,000 events','17.84% [17.31, 18.40]','13.56% [13.44, 13.67]'],
   ['Fixed transition SD/mean, 999 events','44.18% [41.50, 46.88]','21.00% [20.40, 21.53]'],
   ['Common low-response count, all 10k','183','0'],
   ['Common low-response count, transition','183','0']],[CW-244,122,122]),
  p('Fixed transition: 1.2 &lt;= |eta| &lt; 1.5. Common cut: A/E &lt; 0.07966135709622409, frozen from half the original standard saved-hit global mean. Width intervals are pointwise 95%. Zero observed tails do not exclude a nonzero population rate. [9]','small'),
  AngularPlot([('800 mm reference',gap['views']['A']['models']['standard']),('400 mm working',gap['views']['A']['models']['candidate'])],('abs_eta','fine_transition'),gap=True),
  p('Figure 3. Complete-deposit width versus |eta|, including predeclared fine transition bins; bars are pointwise 95% intervals. Paired candidate-minus-reference differences are -4.29 points [-4.80, -3.78] globally and -23.19 points [-25.93, -20.60] in the fixed transition. [9]','small'),
  p('<b>What was preserved.</b> Internal shapes, material recipes, rotations, daughter-local placements, readout IDs and local services are unchanged. Active axial separation falls from 1100 to 700 mm. Native comparison covers 290,216 placements, with zero overlaps/extrusions at 10 nm. The external rerouting overlay and other detector systems are absent from the response run. [9]'),
  p('<b>Readout accounting.</b> Three/two midpoint cell-assignment failures leave 1.18839/0.148997 MeV unassigned across the old/new 10k. Independent A=S+U and exact float32 saved-cell checks close; saved hits replay exactly. H versus A changes the global width contrast by only 0.00000336 percentage points. The improvement is robust to these omissions, while canonical cell assignment still needs correction. [9]','small')
 ])
 pages.append([
  p('6  Recommendations and next gates','h1'),
  p('Develop the human-selected reduced-gap LAr baseline, using the results to prioritize integration while qualifying detector-wide performance separately.','lead'),
  table(['Priority','Recommended action','Evidence needed to close the gate'],[
   ['1  Connected service fit','Implement complete port/neck/bus/rear-exit ownership and displaced material in the combined model.','Full circuits and cable recipes; 3D swept clearances, board/support capacity, thermal/hydraulic/load margins, access and disconnection.'],
   ['2  Hermetic transition','Retain the 400 mm working gap, and resolve its forward/tracker/magnet/HCAL interfaces.','Signed eta/phi material and shower scans including external services, realistic upstream material, collar/FCAL and installation tolerances.'],
   ['3  Correct cell assignment','Resolve annular-midpoint failure cases without concealing energy or relaxing acceptance criteria.','Stable canonical IDs, per-cell references, complete deposited-energy accounting and boundary-focused regression checks.'],
   ['4  Response','Add LAr charge/electronics/noise response and a common reconstruction benchmark.','Independent fixed-energy e/gamma scans, local linearity/closure, tails, timing, radiation/occupancy and relevant systematics.'],
   ['5  Collider','Test jets, pileup and particle-flow consequences with the coupled detector.','HCAL/FCAL containment and service-crack effects; jet response, missing momentum, pileup robustness and calibration transfer.']],[66,190,CW-256]),
  Spacer(1,11),
  h('Retain Si-W as a reference and a design alternative'),
  p('Keep its physical staggering and frozen calibration evidence. Further progress needs interruption of full-depth sector/service cracks and a justified material/service budget, rather than relying on larger calibration gains. Require independent fresh test samples for any further tuning; the inspected 20k validation set is no longer untouched. [3-5]'),
  h('Treat readout coarsening as a separate optimization'),
  p('Selective coarser cells could reduce channel/electronics demand, but cell count alone does not determine cryostat walls, minimum bend radii or complete service volume. Quantify segmentation, occupancy, bandwidth, power, heat and particle-flow costs together before attributing a smaller gap to coarsening. The demonstrated gap benefit used unchanged segmentation. [6,8,9]'),
  box('<b>Decision boundary.</b> Current evidence supports smoother raw electron response for the represented LAr geometry and a strong benefit from its reduced gap. It does not yet measure realistic reconstructed resolution, particle-flow/jet performance, a fully fitted service installation or final engineering acceptance.')
 ])
 refs=[
  ('[1] ODD baseline and realism','odd_assessment','Static assessment uses c167363; the transported ODD comparison uses d70556f. Upstream ECAL XML at d70556f was read for this review (48 layers, 1.9 mm W alloy, 0.5 mm Si, 5.1 mm cells).'),
  ('[2] ODD versus realistic Si-W, fixed-point study','fixed_report','Frozen settings, response moments and retained stochastic-gate failure; compact data in issue117/previews/nodd-digitized-response.json.'),
  ('[3] Realistic Si-W geometry','siw_barrel','DES-031 barrel plus DES-030 endcaps: physical wafers, guards, cassettes, cooling and local services.'),
  ('[4] Inactive-region controls and physical staggering','staggered','Historical 3ebafd3: see also ecal10k-untiled/README.md. Material-changing diagnostic and actual staggered packing have different interpretations.'),
  ('[5] Independent high-statistics Si-W calibration','highstat','Historical 3ebafd3: 100k training plus 20k fresh validation; frozen model and full-refit uncertainty.'),
  ('[6] ALLEGRO-style LAr design/readout','lar_barrel','DES-032 barrel plus DES-033 turbine endcaps. Public k4geo e1ba7bc geometry is adapted explicitly; engineering and electronics qualifications remain separate.'),
  ('[7] Matched 10k Si-W and LAr comparison','matched_report','Raw saved-hit summary, angular populations, shared bootstrap and original source-era LAr gap.'),
  ('[8] Updated service topology and DD4hep routing','routing_native','See also DES-032-side-rear-routing.md. Component conservation/navigation and failed combined-fit diagnostic stay distinct.'),
  ('[9] Reduced-gap 10k response and energy audit','gap_report','Complete A/S/U/H accounting, exact retained replay, paired uncertainty and 84-variable covariance.'),
  ('[10] Reusable placements / startup','lar_placement','LAr matched first-event probe; separate Si-W volume-map metric in siw-real-wedge-default/README.md.'),
 ]
 last=[p('Sources and comparison contract','h1'),p('References link to immutable project evidence, not moving branch tips. Current evidence is pinned to 79a967aa; earlier calibration/control studies are pinned to 3ebafd34. The PDF and its source manifest preserve full hashes.','small')]
 for title,key,description in refs:
  last.append(p('<b>'+title+'</b> '+escape(description)+'<br/><link href="'+link(key)+'" color="#2369a0">Open source report</link> <font color="#506373">('+SOURCES[key][0][:8]+')</font>','ref'))
 last += [h('Statistical and status conventions'),p('Matched 10k intervals use 1000 shared whole-primary bootstrap replicates (seed 13001000); Figure 1 rebins the retained saved-hit ledgers to uniform 0.05-wide |eta| bins. ODD reference points keep their separate fixed-energy cohort and source intervals. The independent 20k calibration has distinct training/closure roles and 200 full-refit uncertainty. Cohorts and tail thresholds are not pooled; zeros are retained.','small'),p('The <link href="https://github.com/asalzburger/nodd/pull/145#issuecomment-6951330371" color="#2369a0">human review direction of 17 November 2026</link> explicitly selects LAr with the 400 mm warm gap as the nODD ECAL working baseline, following the earlier adoption convention. This does not qualify the connected services/collar or a new combined detector union, and grants no formal engineering acceptance.','small')]
 pages.append(last)
 assert len(pages)==8
 c=canvas.Canvas(str(output),pagesize=A4,pageCompression=1,invariant=1)
 c.setTitle('EM calorimeter findings: ODD, realistic Si-W and ALLEGRO-style LAr')
 c.setAuthor('nODD project');c.setSubject('Evidence review and recommendations; adopted reduced-gap working configuration')
 for i,story in enumerate(pages,1):
  c.setFillColor(INK);c.setFont('Bold',8);c.drawString(M,H-29,'nODD  /  ELECTROMAGNETIC CALORIMETRY')
  c.setFont('Body',7.5);c.setFillColor(MUTED);c.drawRightString(W-M,H-29,'FINDINGS REVIEW  |  '+DATE)
  c.setStrokeColor(GOLD);c.setLineWidth(2);c.line(M,H-39,W-M,H-39)
  c.setFont('Body',7.5);c.drawString(M,29,'PUB-EMCAL-2026-11-15  |  Working-design review')
  c.drawRightString(W-M,29,f'{i} / {len(pages)}')
  frame=Frame(M,52,CW,H-110,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
  remaining=list(story);frame.addFromList(remaining,c)
  if remaining:raise RuntimeError(f'Page{i} overflow: {len(remaining)} flowables, starts '+str(remaining[0])[:180])
  c.showPage()
 c.save()
 reader=PdfReader(output);assert len(reader.pages)==8 and len(reader.pages)<=10
 text='\n'.join(page.extract_text() for page in reader.pages)
 assert '\ufffd' not in text and '32.220' not in text
 assert all(f'{i} / 8' in reader.pages[i-1].extract_text() for i in range(1,9))
 provenance=dict(document_id='PUB-EMCAL-2026-11-15',date=DATE,pages=8,classification='Human-selected LAr400 ECAL working baseline; engineering qualification separate',source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),builder_sha256=digest(Path(__file__).read_bytes()),reportlab=reportlab.Version,pdf_sha256=digest(output.read_bytes()),sources={k:dict(revision=rev,path=path,sha256=digest(blob(k)),url=link(k)) for k,(rev,path) in SOURCES.items()},primary_odd=dict(revision='d70556f33b1c36abdf101a07ad8cf57eb56fbdf1',path='xml/detectors/CalorimeterECal.xml',github_blob='8ee81694badaf05d18000e6a818eb6b350c88a2c',access_date=DATE),no_new_simulation=True,review_update=dict(comment='https://github.com/asalzburger/nodd/pull/145#issuecomment-6951330371',comparison_data_sha256=digest((Path(__file__).parent/'response-comparison.json').read_bytes()),comparison_svg_sha256=digest((Path(__file__).parent/'response-comparison.svg').read_bytes()),comparison_producer_sha256=digest((Path(__file__).parent/'response_comparison.py').read_bytes()),new_transport=False,retained_ledgers_rebinned=True))
 output.with_suffix('.json').write_text(json.dumps(provenance,indent=2)+'\n')
 print(json.dumps(dict(pdf=str(output),pages=8,bytes=output.stat().st_size,sha256=provenance['pdf_sha256'])))

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'output/pdf/em-calorimeter-findings.pdf');args=parser.parse_args();build(args.output.resolve())
