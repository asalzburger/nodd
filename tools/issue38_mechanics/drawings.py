#!/usr/bin/env python3
"""Issue #38 review schematics; topology, not fabrication drawings or FEA.

Parent evidence: 5b4e5d9e563505aea17e9b792458708c3175ec4a (DES012/014/019-023).
TDR evidence: 7625cf6054f5761228be6d8d2de24d43f155bd19 (current chapters).
Only the named PDF and PNG are written. Requires reportlab, pypdfium2 and Pillow.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen.canvas import Canvas

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs/publication/issue38-mechanics/figures"
W, H = 900, 650
INK = "#243647"
CARBON = "#546979"
FOAM = "#eadcc1"
GRAPHITE = "#94a3a8"
GLUE = "#c77742"
SI = "#b9d5c3"
COOL = "#188dc2"
FLEX = "#d5a936"
OPEN = "#8c5783"


class Drawing:
    def __init__(self, canvas):
        self.c = canvas

    def box(self, x, y, w, h, fill=None, stroke=INK, dash=False, radius=0):
        c = self.c
        c.setStrokeColor(HexColor(stroke))
        c.setFillColor(HexColor(fill) if fill else white)
        c.setLineWidth(0.8)
        c.setDash([4, 3] if dash else [])
        c.roundRect(x, H-y-h, w, h, radius, stroke=1, fill=bool(fill))
        c.setDash([])

    def line(self, points, ink=INK, width=1, dash=False):
        c = self.c
        c.setStrokeColor(HexColor(ink)); c.setLineWidth(width)
        c.setDash([4, 3] if dash else [])
        p = c.beginPath(); p.moveTo(points[0][0], H-points[0][1])
        for x, y in points[1:]:
            p.lineTo(x, H-y)
        c.drawPath(p); c.setDash([])

    def arrow(self, x, y, x2, y2, ink=INK, dash=False):
        self.line([(x, y), (x2, y2)], ink, 1.4, dash)
        a = math.atan2(y2-y, x2-x)
        self.line([(x2-7*math.cos(a-.4), y2-7*math.sin(a-.4)),
                   (x2, y2), (x2-7*math.cos(a+.4), y2-7*math.sin(a+.4))], ink, 1.4)

    def text(self, x, y, text, size=10, bold=False, ink=INK, width=None, leading=None):
        c = self.c
        font = "Helvetica-Bold" if bold else "Helvetica"
        c.setFont(font, size); c.setFillColor(HexColor(ink))
        lines = []
        for line in text.split("\n"):
            lines.extend(simpleSplit(line, font, size, width) if width else [line])
        for i, line in enumerate(lines):
            c.drawString(x, H-y-i*(leading or size*1.35), line)

    def circle(self, x, y, r, fill=None, ink=INK, dash=False):
        c = self.c
        c.setFillColor(HexColor(fill) if fill else white)
        c.setStrokeColor(HexColor(ink)); c.setLineWidth(1)
        c.setDash([4, 3] if dash else [])
        c.circle(x, H-y, r, fill=bool(fill), stroke=1); c.setDash([])

    def page(self, n, title, subtitle, locator):
        self.box(0, 0, W, H, "#ffffff", "#ffffff")
        self.box(0, 0, W, 68, "#edf2f5", "#edf2f5")
        self.text(30, 29, title, 20, True)
        self.text(30, 51, subtitle, 10)
        self.text(30, 614, "PROTOTYPE / REVIEW: dimensions label the model; joints and stiffness remain unqualified.", 9, True, OPEN)
        self.text(30, 632, locator, 8)
        self.text(850, 632, f"{n} / 4", 8)

    def card(self, x, y, w, h, title):
        self.box(x, y, w, h, "#fafbfc", "#d2dce3", radius=5)
        self.text(x+13, y+23, title, 12, True)

    def flow(self, x, y, labels, width=780, fill=CARBON):
        item = (width-(len(labels)-1)*20)/len(labels)
        for i, label in enumerate(labels):
            xx = x+i*(item+20)
            self.box(xx, y, item, 43, "#edf2f5", fill, radius=3)
            self.text(xx+7, y+17, label, 9, width=item-12)
            if i+1 < len(labels):
                self.arrow(xx+item+2, y+21, xx+item+18, y+21, fill)


def barrel(d):
    d.page(1, "Pixel barrel: material and mounting", "Module normal points outward toward the stave. Views use independent display scales.",
           "DES012 PB-C03-05; DES002 PS-C01-10/I04; tools/pixel_support/mounting.py make_mounts/check_mounts.")
    d.card(30, 86, 420, 300, "A. Through the module and cooled stave")
    layers = [
        ("Sensor silicon", "0.150", SI, 14), ("Bump standoff (unfilled)", "0.020", "#ffffff", 9),
        ("ASIC silicon", "0.150", SI, 14), ("Graphite contact shim", "0.255", GRAPHITE, 18),
        ("Epoxy support interface", "0.100", GLUE, 13), ("Electrical insulation", "0.025", FLEX, 9),
        ("Graphite spreader", "0.200", GRAPHITE, 15), ("CFRP upper skin", "0.150", CARBON, 12),
        ("Bored foam core", "4.100", FOAM, 43), ("CFRP lower skin", "0.150", CARBON, 12),
    ]
    yy = 126
    for label, value, fill, height in layers:
        d.box(48, yy, 100, height, fill)
        d.text(163, yy+height/2+3, f"{label}: {value} mm", 9)
        if label == "Bored foam core":
            for x in [78, 118]:
                d.circle(x, yy+height/2, 12, CARBON)
                d.circle(x, yy+height/2, 10, COOL)
        yy += height
    d.text(47, 330, "Support beyond body-back plane: 4.725 mm total.", 9, True)
    d.text(47, 347, "0.080 mm-equivalent core glue retains specified foam mass.\nFlex-side epoxy (0.025 mm) is on the opposite sensor face.\nUnknown graphite/ASIC and mount bondlines remain open.", 9)
    d.card(466, 86, 404, 300, "B. At one bearing station (radial section)")
    d.box(495, 132, 145, 20, SI); d.text(655, 145, "Module", 10)
    d.box(493, 152, 149, 8, GLUE); d.text(655, 160, "Epoxy + insulation", 9)
    d.box(491, 160, 153, 12, GRAPHITE)
    d.box(491, 172, 153, 6, CARBON)
    d.box(526, 178, 83, 48, FOAM)
    d.box(526, 226, 83, 6, CARBON)
    d.box(555, 232, 25, 41, CARBON)
    d.box(486, 273, 165, 12, CARBON)
    d.text(659, 191, "Narrow spine", 10)
    d.text(659, 213, "10 / 24 mm", 9)
    d.text(659, 246, "CFRP foot", 10)
    d.text(659, 266, "4 mm wide, 8 mm in z", 9)
    d.text(659, 286, "Ring outside stave", 10)
    d.arrow(565, 297, 565, 325, OPEN, True)
    d.box(492, 329, 151, 22, None, OPEN, True)
    d.text(502, 344, "Cage / end support", 10, ink=OPEN)
    d.text(489, 370, "Dashed: joint/cage topology; thickness and stiffness unspecified.", 8.5, ink=OPEN)
    d.card(30, 403, 840, 185, "C. Axial load path and station schedule")
    x0, x1 = 90, 806
    d.box(x0, 459, x1-x0, 18, FOAM)
    for z in [-546, -330, -110, 110, 330, 546]:
        x = x0+(z+552.8)/1105.6*(x1-x0)
        d.box(x-4, 448, 8, 47, CARBON)
        d.text(x-16, 438, str(z), 9)
        d.line([(x, 495), (x, 520)], OPEN, 1.4, True)
    d.text(42, 470, "Stave", 9)
    d.line([(x0, 520), (x1, 520)], OPEN, 2, True)
    d.arrow(x0, 520, x0-27, 520, OPEN, True); d.arrow(x1, 520, x1+27, 520, OPEN, True)
    d.text(75, 543, "Cage and end restraints: conceptual. Rings are coupled parts of one support, not six ground reactions.", 10, ink=OPEN)
    d.text(75, 564, "z = -546 mm sets axial reference; the other contacts propose longitudinal sliding/compliance.", 10)


def endcap(d):
    d.page(2, "Pixel endcap: graphite feet and tongues", "Local per-chip thermal contact and global support are different interfaces.",
           "DES019 PM-C04-06; DES014 EC-C07/10/13-16; TDR current chapter support ledger. Exact input SHAs in README.")
    d.card(30, 86, 405, 340, "A. Local graphite foot (separate illustrative cuts)")
    for x, lift, title in [(68, 0, "Low"), (235, 33, "Raised")]:
        d.text(x+13, 127, title, 11, True)
        y = 233-lift
        d.box(x, y, 112, 24, SI); d.text(x+9, y+16, "Module body", 9)
        # From module toward plate: bond, TIM, insulation, graphite, cradle.
        # trimmed_export.py builds the reverse order from the plate outward.
        for h, fill in [(5, GLUE), (5, GLUE), (5, FLEX), (14, GRAPHITE), (9, CARBON)]:
            d.box(x, y+24, 112, h, fill); y += h
        if lift:
            d.box(x+41, y+24, 30, lift, GRAPHITE)
        d.box(x-6, 295, 124, 7, CARBON)
        d.box(x-6, 302, 124, 54, FOAM)
        d.box(x-6, 356, 124, 7, CARBON)
        d.box(x+41, 296, 30, 46, None, GRAPHITE, True)
        d.circle(x+56, 327, 12, CARBON); d.circle(x+56, 327, 10, COOL)
    d.text(48, 382, "Pickup = 0.30 graphite + 0.075 CFRP cradle + 0.025 each\ninsulation, TIM and adhesive = 0.45 mm. Raised stem: 6 x 8 x 1.65 mm.\nDashed insert: effective core inventory; tube saddle/contact needs CAD.", 9)
    d.card(451, 86, 419, 340, "B. Three tongues in disc plan")
    cx, cy = 654, 246
    d.circle(cx, cy, 94, FOAM)
    d.circle(cx, cy, 14, "#fafbfc")
    d.circle(cx, cy, 116, None, CARBON)
    for a, label in [(90, "Cone"), (210, "Slot"), (330, "Plane")]:
        t = math.radians(a)
        x0, y0 = cx+92*math.cos(t), cy-92*math.sin(t)
        x1, y1 = cx+114*math.cos(t), cy-114*math.sin(t)
        d.line([(x0,y0), (x1,y1)], CARBON, 8)
        d.circle(x1,y1,5,None,OPEN,True)
        d.text(x1+(10 if a != 210 else -46), y1+3, label, 10, ink=OPEN)
    d.text(475, 124, "Standalone DES019 plate r = 27..188.5 mm", 10)
    d.text(475, 385, "Tongues: 10 mm wide, r = 186..228 mm; angles 90/210/330 deg.\nRails: 8 x 8 mm boxes, wall 0.4 mm, on closed CFRP shell.\nCone/slot/plane is a proposed 6-constraint kinematic coupling.", 9)
    d.card(30, 444, 840, 144, "C. Load transfer beyond the disc")
    d.flow(48, 485, ["Module cradle /\ngraphite foot", "Common disc\nsandwich", "Three radial\ntongues", "Three box rails\n+ closed shell", "End flanges /\nexternal support"], 804)
    d.text(49, 549, "Rail-to-shell bond, coupling preload, cold motion and end reactions require analysis and coupon/assembly tests.", 10)
    d.text(49, 569, "Whole-endcap axial installation is assumed; shell split/access and independent half-disc extraction remain open.", 9)


def pigtails(d):
    d.page(3, "Pixel services: proposed pigtail handoffs", "Solid blocks locate material/envelopes; dashed paths and open connectors are conceptual interfaces.",
           "DES014 EC-C11/14; DES019 PM-C06; DES012 PB-C06-08; TDR7625cf... module termination and service sections.")
    d.card(30, 86, 840, 220, "A. Barrel module to cumulative longitudinal bundle (local side view)")
    d.box(67, 161, 165, 40, SI); d.text(80, 185, "Sensor / ASIC / shim", 10)
    d.box(67, 148, 165, 9, FLEX); d.text(80, 137, "Backside module flex", 10)
    d.box(67, 205, 165, 15, GLUE)
    d.box(67, 220, 165, 27, FOAM)
    d.box(270, 222, 22, 43, CARBON); d.text(254, 274, "Ring / foot", 9)
    d.box(348, 150, 244, 27, FLEX); d.text(359, 168, "Bundle outside bearing rings", 10)
    d.line([(232,152),(252,140),(274,140),(300,163),(348,163)], OPEN, 2, True)
    d.box(300, 155, 14, 16, None, OPEN, True)
    d.text(252, 120, "Exposed flex pad -> pigtail / strain relief -> insulated bundle", 10, ink=OPEN)
    d.arrow(595,164,648,164,FLEX,True)
    d.box(652,144,182,62,"#f5ead1",FLEX)
    d.text(664,163,"Half-stave end -> sector\ncollector -> axial trunk",10)
    d.text(348,211,"Crossing route, bend radius, connector head and insulation\nclearance need detailed design. No route through a foot is assumed.",9,ink=OPEN)
    d.text(67,283,"Termination and wire bonds are an electrical concept; detailed connector/bond material is not supplied by cable fill.",9)
    d.card(30, 323, 840, 265, "B. Endcap: remain on the module's own plate face")
    d.box(64, 426, 430, 65, FOAM)
    d.box(64, 420, 430, 6, CARBON); d.box(64,491,430,6,CARBON)
    d.box(89,365,129,25,SI);d.text(99,382,"Module",10)
    d.box(126,390,52,30,GRAPHITE);d.text(76,448,"Disc sandwich",10)
    d.box(261,403,152,10,FLEX); d.text(266,387,"Same-face ring bus",10)
    d.line([(216,371),(234,379),(234,408),(261,408)],OPEN,2,True)
    d.box(228,395,12,15,None,OPEN,True)
    d.text(68,534,"Side-slot drop beside the foot; no passage through an opposite-face module.",9,ink=OPEN)
    d.line([(414,408),(473,408),(522,392),(548,365),(586,365)],OPEN,2,True)
    d.box(587,346,247,57,"#f5ead1",FLEX)
    d.text(598,365,"Radial fan -> rim turn -> collector\n-> axial trunk / last-disc bypass",10)
    d.text(535,431,"Front/back fan material is effective in the model.\nSlots, connectors, rim bends and access remain open.",9,ink=OPEN)
    d.text(68,564,"Electrical chains and hydraulic circuits are separate networks; a graphite foot is not a coolant feed or connector.",10)


def strips(d):
    d.page(4, "Strip mounting: local load to external frame", "One cooled structural sandwich per stave/petal; the long-strip pair uses both faces of that same carrier.",
           "DES020 SB-C04/07/15; DES021 SE-C04/06; DES022 LS-C02-04; DES023 LE-C02/03/07; current TDR bearing schedule.")
    panels = [(30,86,"A. Short-strip barrel"),(456,86,"B. Long-strip barrel"),
              (30,347,"C. Short-strip petal"),(456,347,"D. Long-strip petal")]
    for x,y,title in panels:
        d.card(x,y,414,241,title)
    # Short barrel: one-face pickup, mounting land on the back.
    d.box(55,140,159,18,SI);d.box(84,158,25,18,GRAPHITE);d.box(160,158,25,18,GRAPHITE)
    d.box(55,176,159,6,CARBON);d.box(55,182,159,26,FOAM);d.box(55,208,159,6,CARBON)
    d.box(179,214,10,31,CARBON);d.box(55,245,159,10,CARBON)
    d.arrow(44,225,44,144,CARBON);d.text(51,131,"Radially outward",8)
    d.text(230,153,"Module -> pickups ->\nsandwich -> bare skin land\n-> 2 mm beveled web\n-> inner bearing ring",10)
    d.text(49,280,"9 stations. Centre fixes z; others slide/comply.\nRing/cage reaction and web joint need qualification.",10)
    # Long barrel sandwich with both faces.
    d.box(479,139,161,12,SI);d.box(516,151,39,13,GRAPHITE)
    d.box(479,164,161,6,CARBON);d.box(479,170,161,27,FOAM);d.box(479,197,161,6,CARBON)
    d.box(516,203,39,13,GRAPHITE);d.box(479,216,161,12,SI)
    d.circle(631,181,6,GLUE);d.line([(631,181),(653,181),(653,243)],CARBON,8)
    d.box(479,243,183,10,CARBON)
    d.text(675,150,"Both sensors -> same\nsandwich -> potted lands\n-> keyed web / shoe\n-> inner bearing ring",10)
    d.text(475,280,"17 stations, 163.75 mm pitch. Centre fixes z.\nOther contacts reserve +/-0.3 mm longitudinal travel.",10)
    # Petals: same schematic silhouette, different contact assignments.
    for x,y,long in [(30,347,False),(456,347,True)]:
        cx,cy=x+103,y+124
        d.line([(cx-61,cy+43),(cx-38,cy-62),(cx+38,cy-62),(cx+61,cy+43),(cx-61,cy+43)],CARBON,2)
        points = [(cx,cy-62),(cx-53,cy+25),(cx+53,cy+25)]
        for px,py in points:
            d.circle(px,py,6,CARBON)
            d.line([(px,py),(px,py+17)],OPEN,1.4,True)
        d.text(x+186,y+64,"Both faces -> common petal" if long else "Module pickups -> petal",10,True)
        desc = ("Two outer contacts + inner key.\nOne outer fixes in plane; other\nslides tangentially; inner slides\nradially. +/-0.3 mm reserve." if long else
                "Three back lugs to inner/outer\nCFRP frames. Inner datum; two\nouter constrained/sliding seats.\nFrame-to-cage joint remains open.")
        d.text(x+186,y+88,desc,10)
        d.text(x+20,y+209,"Horizontal handling fails screen; temporary frame required." if long else
               "Lug preload, cold adhesive stress and cage stiffness are open.",9,ink=OPEN)


def build():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / "mechanics.pdf"
    c = Canvas(str(path), pagesize=(W,H), invariant=1, pageCompression=1)
    c.setTitle("Issue 38 mechanics and services review schematics")
    c.setAuthor("nODD documentation prototype")
    d = Drawing(c)
    for draw in [barrel, endcap, pigtails, strips]:
        draw(d); c.showPage()
    c.save()
    import pypdfium2 as pdfium
    from PIL import Image, ImageOps
    pdf = pdfium.PdfDocument(str(path))
    assert len(pdf) == 4
    pages = [page.render(scale=1.5).to_pil().convert("RGB") for page in pdf]
    preview = Image.new("RGB", (pages[0].width*2, pages[0].height*2), "#d7dfe5")
    for i, page in enumerate(pages):
        preview.paste(ImageOps.expand(page,border=2,fill="#d7dfe5").resize(page.size),
                      ((i%2)*page.width, (i//2)*page.height))
    preview.save(OUTPUT / "mechanics.png")
    print(f"Wrote {path} (4 pages), mechanics.png ({preview.width} x {preview.height}).")


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    build()
