#!/usr/bin/env python3
"""Editable orthographic SVG cutaway of the existing DES-039 LAYOUT-001 model.

This is an explanatory vector illustration, not an additional detector geometry.
Physical envelopes and positions come from inputs.json/model.py. The removed
quadrant, sparse enlarged fibres, colours and camera are display choices only.
"""
import argparse
import html
import json
import math

from model import ROOT, HERE, build, fibre_endpoint, sha

OUTPUT = ROOT / 'docs/design/figures/DES-039/LAYOUT-001-FCAL-3d.svg'
NAVY = '#172d45'
MUTED = '#536b7e'
LONG = '#008e9f'
SHORT = '#456bd4'
SCALE = .72
# Orthonormal screen basis: an orthographic camera, with a true axial scale.
VIEW = (.71, .25, -math.sqrt(1-.71**2-.25**2))
NORM = math.hypot(VIEW[0], VIEW[2])
RIGHT = (-VIEW[2]/NORM, 0., VIEW[0]/NORM)
UP = (-RIGHT[2]*VIEW[1], NORM, RIGHT[0]*VIEW[1])


def project(p):
    return (300+SCALE*sum(a*b for a,b in zip(RIGHT,p)),
            675-SCALE*sum(a*b for a,b in zip(UP,p)))


def depth(p):
    return sum(a*b for a,b in zip(VIEW,p))


def xyz(radius, angle, z):
    a=math.radians(angle)
    return (radius*math.cos(a), radius*math.sin(a), z)


def points(pts):
    return ' '.join(f'{x:.3f},{y:.3f}' for x,y in pts)


def colour(rgb, brightness):
    return '#'+''.join(f'{max(0,min(255,round(v*brightness))):02x}' for v in rgb)


def text(x,y,label,size=18,fill=NAVY,weight=400,anchor='start',extra=''):
    return (f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}" {extra}>{html.escape(label)}</text>')


class Scene:
    def __init__(self):
        self.items=[]

    def polygon(self, pts, fill, stroke='#536477', width=.35, opacity=1):
        markup=(f'<polygon points="{points([project(p) for p in pts])}" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="{width}" opacity="{opacity}" stroke-linejoin="round"/>')
        self.items.append((sum(depth(p) for p in pts)/len(pts),markup))

    def line(self, pts, stroke, width=1, opacity=1, dash=''):
        markup=(f'<polyline points="{points([project(p) for p in pts])}" fill="none" '
                f'stroke="{stroke}" stroke-width="{width}" opacity="{opacity}" '
                f'stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="{dash}"/>')
        self.items.append((sum(depth(p) for p in pts)/len(pts),markup))

    def annulus(self, ri,ro,za,zb,rgb,cut=True):
        angles=list(range(90 if cut else 0,361,3))
        for a,b in zip(angles,angles[1:]):
            mid=math.radians((a+b)/2)
            light=.76+.22*max(-1,min(1,.45*math.cos(mid)+.85*math.sin(mid)))
            for radius,inner in [(ro,False),(ri,True)]:
                pts=[xyz(radius,a,za),xyz(radius,b,za),xyz(radius,b,zb),xyz(radius,a,zb)]
                self.polygon(pts,colour(rgb,light*(.82 if inner else 1)),stroke='none')
            for z,shade in [(za,1.12),(zb,.9)]:
                self.polygon([xyz(ri,a,z),xyz(ro,a,z),xyz(ro,b,z),xyz(ri,b,z)],
                             colour(rgb,shade),stroke='none')
        if cut:
            for angle,shade in [(0,1.08),(90,1.2)]:
                self.polygon([xyz(ri,angle,za),xyz(ro,angle,za),xyz(ro,angle,zb),xyz(ri,angle,zb)],
                             colour(rgb,shade),stroke=colour(rgb,.7),width=.6)
        for z in (za,zb):
            for r in (ri,ro):
                self.line([xyz(r,a,z) for a in angles],colour(rgb,.6),.5)

    def wire_enclosure(self,ri,ro,za,zb,stroke):
        for z in (za,zb):
            self.line([xyz(ro,a,z) for a in range(0,361,4)],stroke,.85,.5,'4 5')
        for a in (0,90,180,270):
            self.line([xyz(ro,a,za),xyz(ro,a,zb)],stroke,.85,.45,'4 5')

    def render(self):
        return '\n'.join(markup for _,markup in sorted(self.items,key=lambda item:item[0]))


def leader(anchor, elbow, end, number, title, detail, label_x,label_y):
    p=project(anchor)
    return (f'<polyline points="{points([p,elbow,end])}" fill="none" stroke="#8ca1b2" stroke-width="1.2"/>'
            f'<circle cx="{p[0]:.2f}" cy="{p[1]:.2f}" r="4" fill="white" stroke="#536b7e" stroke-width="1.4"/>'
            f'<circle cx="{label_x+12}" cy="{label_y-6}" r="12" fill="{NAVY}"/>'
            +text(label_x+12,label_y-1,str(number),12,'white',700,'middle')
            +text(label_x+34,label_y,title,19,NAVY,650)
            +text(label_x+34,label_y+25,detail,15,MUTED))


def make_svg():
    model=build()
    c=model['config']; m=c['module']; z=model['zones_mm']; f=c['fibres']; readout=c['readout']
    scene=Scene()
    # All volumes retain their design coordinates; only their display cut changes.
    scene.annulus(m['sampling_inner_radius_mm'],m['sampling_outer_radius_mm'],*z['sampling'],(100,112,126))
    scene.annulus(m['bore_radius_mm'],m['inner_shell_outer_mm'],0,m['length_mm'],(167,184,198))
    scene.annulus(m['sampling_shell_inner_mm'],m['outer_radius_mm'],0,z['sampling'][1],(186,200,212))
    # The rear enclosure is shown as a wire envelope to expose optical/readout allocations.
    scene.wire_enclosure(m['rear_shell_inner_mm'],m['outer_radius_mm'],z['sampling'][1],m['length_mm'],'#627b90')
    scene.annulus(m['sampling_outer_radius_mm'],m['sampling_shell_inner_mm'],z['sampling'][1],z['sampling'][1]+18,(177,190,202))
    scene.annulus(m['inner_shell_outer_mm'],m['sampling_shell_inner_mm'],0,m['cover_thickness_mm'],(190,202,213))
    scene.annulus(m['inner_shell_outer_mm'],m['rear_cover_outer_mm'],m['length_mm']-m['cover_thickness_mm'],m['length_mm'],(172,189,204))
    scene.annulus(m['inner_shell_outer_mm'],m['rear_shell_inner_mm']-1,z['electronics_cooling'][0],z['electronics_cooling'][0]+6,(83,163,170))
    # Selected real finite-lattice sites in the removed quadrant. The displayed
    # line thickness is deliberately enlarged, not a new fibre diameter.
    subset=[q for q in model['fibres'] if q['x_mm']>9 and q['y_mm']>9 and q['i']%9==0 and q['j']%8==0]
    for q in subset:
        tone=LONG if q['population']==0 else SHORT
        scene.line([(q['x_mm'],q['y_mm'],q['z0_mm']),
                    (q['x_mm'],q['y_mm'],q['z1_mm'])],tone,1.15,.83)
        xe,ye=fibre_endpoint(model,q)
        tail=[]
        for k in range(25):
            t=k/24; blend=(1-math.cos(math.pi*t))/2
            tail.append((q['x_mm']+(xe-q['x_mm'])*blend,
                         q['y_mm']+(ye-q['y_mm'])*blend,
                         z['fanout'][0]+(z['fanout'][1]-z['fanout'][0])*t))
        scene.line(tail,tone,.9,.6)
    # Package and pixel footprints, following the existing model/native placement.
    for ch in model['channels']:
        scene.polygon([(x,y,z['sensors'][0]+.01) for x,y in ch['vertices_mm']],
                      '#224766' if ch['population']==0 else '#4b568b',stroke='white',width=.4)
    for phi in c['thermal']['pipe_phi_deg']:
        r=c['thermal']['pipe_radius_mm']; a=math.radians(phi)
        xy=(r*math.cos(a),r*math.sin(a))
        scene.line([(*xy,z['electronics_cooling'][0]+6),(*xy,m['length_mm'])], '#168f9b',3.1)
    # Axial dashed line is a reference axis, not a downstream beam-pipe model.
    axis=([project((0,0,-190)),project((0,0,m['length_mm']+130))])
    meta={
        'design':'DES-039','layout':'LAYOUT-001','status':'DRAFT / PROTOTYPE',
        'input':'tools/forward_calorimeter/inputs.json','input_sha256':sha(HERE/'inputs.json'),
        'model_sha256':sha(HERE/'model.py'),'generator_sha256':sha(__file__),
        'units':'mm','body_length_mm':m['length_mm'],
        'body_radii_mm':[m['bore_radius_mm'],m['outer_radius_mm']],
        'sampling_radii_mm':[m['sampling_inner_radius_mm'],m['sampling_outer_radius_mm']],
        'axial_zones_mm':z,'fibre_count_per_end':len(model['fibres']),
        'sensor_cartridges_per_end':len(model['channels']),
        'shown_fibre_count':len(subset),
        'display_only':'Orthographic projection; upper quadrant removed; sparse fibres enlarged; rear enclosure wireframe; tiny clamshell joints and support ribs omitted; electronics/service zones are allocations, not detailed hardware; no downstream beam pipe is represented.'}
    parts=['<?xml version="1.0" encoding="UTF-8"?>',
           '<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1240" viewBox="0 0 1800 1240" role="img" aria-labelledby="title desc">',
           '<title id="title">LAYOUT-001 tungsten–quartz forward calorimeter: 3D cutaway</title>',
           '<desc id="desc">Orthographic cutaway of one 1800 mm annular FCAL, with 50 mm bore radius, 290 mm outer radius, a 1200 mm tungsten sampling block, selected long and short quartz fibres, 300 mm rear optical fan-out and SiPM readout. An inset shows all 96 sensor cartridges. Both detector ends are placed at absolute z 4533.2 to 6333.2 mm. Prototype, with representative enlarged fibres and removed material for visibility.</desc>',
           '<metadata id="design-provenance">'+html.escape(json.dumps(meta,sort_keys=True))+'</metadata>',
           '<defs><linearGradient id="background" x2="0" y2="1"><stop stop-color="#ffffff"/><stop offset="1" stop-color="#f1f5f8"/></linearGradient></defs>',
           '<rect width="1800" height="1240" fill="url(#background)"/>',
           '<g font-family="Arial, Helvetica, sans-serif">',
           '<rect x="64" y="48" width="6" height="61" rx="3" fill="#008e9f"/>',
           text(88,76,'Forward calorimeter',34,NAVY,700),
           text(88,107,'LAYOUT-001  /  Tungsten absorber + quartz Cherenkov fibres',19,MUTED),
           '<rect x="1457" y="54" width="279" height="37" rx="18" fill="#e7edf2"/>',
           text(1596.5,78,'DES-039  ·  DRAFT / PROTOTYPE',14,MUTED,700,'middle')]
    for x,value,label in [(88,'1.80 m','complete package / end'),(478,'580 mm','outer diameter · 100 mm bore'),(868,f'{len(model["fibres"]):,}','quartz fibres / end')]:
        parts += [text(x,170,value,31,NAVY,700),text(x,198,label,15,MUTED)]
    parts += ['<line x1="88" y1="223" x2="1736" y2="223" stroke="#d8e2e9"/>',
              '<ellipse cx="804" cy="866" rx="595" ry="45" fill="#172d45" opacity=".045"/>',
              f'<polyline points="{points(axis)}" fill="none" stroke="#8195a5" stroke-width="1.2" stroke-dasharray="7 6"/>',
              scene.render()]
    # Length dimension displaced below the complete model.
    pa=project((0,-m['outer_radius_mm']-90,0)); pb=project((0,-m['outer_radius_mm']-90,m['length_mm']))
    parts.append(f'<line x1="{pa[0]}" y1="{pa[1]}" x2="{pb[0]}" y2="{pb[1]}" stroke="#8195a5" stroke-width="1"/>')
    for p in (pa,pb):
        parts.append(f'<line x1="{p[0]-4}" y1="{p[1]-10}" x2="{p[0]+4}" y2="{p[1]+10}" stroke="#8195a5"/>')
    angle=math.degrees(math.atan2(pb[1]-pa[1],pb[0]-pa[0])); mx=(pa[0]+pb[0])/2; my=(pa[1]+pb[1])/2
    parts.append(text(mx,my-10,'1800 mm · complete envelope',16,MUTED,500,'middle',f'transform="rotate({angle:.3f} {mx:.3f} {my-10:.3f})"'))
    parts += [leader((155,0,650),(640,320),(308,320),1,'Dense tungsten matrix','1200 mm sampling length',88,291),
              leader((110,150,890),(955,320),(900,320),2,'Long + short quartz fibres','Short population starts 100 mm deeper',754,266),
              leader((150,140,1390),(1340,322),(1420,322),3,'Rear optical fan-out','300 mm routing allocation',1390,277),
              leader((model['channels'][5]['x_mm'],model['channels'][5]['y_mm'],z['sensors'][0]),(1370,741),(1420,741),4,'SiPM readout','Cooled sensors + rear services',1390,785),
              leader((0,0,15),(143,861),(88,861),5,'Central beam aperture','Physical bore radius 50 mm',88,915)]
    # Full rear-view footprint inset, at a true common transverse scale.
    cx,cy,sc=1580,502,.47
    parts += ['<rect x="1418" y="366" width="324" height="351" rx="15" fill="#ffffff" stroke="#d8e2e9"/>',
              text(1440,396,'REAR SENSOR FACE',13,MUTED,700),
              f'<circle cx="{cx}" cy="{cy+31}" r="{m["outer_radius_mm"]*sc}" fill="#edf3f7" stroke="#99acbc"/>']
    cy+=31
    for ch in model['channels']:
        pts=[(cx+x*sc,cy-y*sc) for x,y in ch['vertices_mm']]
        parts.append(f'<polygon points="{points(pts)}" fill="{LONG if ch["population"]==0 else SHORT}" stroke="white" stroke-width=".5"/>')
    parts += [f'<circle cx="{cx}" cy="{cy}" r="{m["bore_radius_mm"]*sc}" fill="white" stroke="#99acbc"/>',
              text(1440,687,'96 cartridges · 16 pixels each',15,NAVY,600)]
    # Readable axial allocations, in exact common mm-to-pixel proportion.
    parts += [text(88,1002,'AXIAL ALLOCATION',13,MUTED,700)]
    colours={'front':'#b4c1cc','sampling':'#718093','fanout':'#b6e0df','sensors':'#5976b9','electronics_cooling':'#59a6ac','service_interface':'#bed0d5','rear':'#b4c1cc'}
    barx,bary,barscale=88,1020,.71
    for name,(lo,hi) in z.items():
        parts.append(f'<rect x="{barx+lo*barscale:.3f}" y="{bary}" width="{(hi-lo)*barscale:.3f}" height="31" fill="{colours[name]}" stroke="white"/>')
    parts += [text(88,1077,'20 front   /   1200 sampling   /   300 fan-out   /   90 sensors   /   100 FE + cooling   /   70 services   /   20 rear  [mm]',15,MUTED),
              text(88,1122,'INSTALLED ON BOTH SIDES',13,MUTED,700),
              text(88,1150,'|z| = 4533.2–6333.2 mm  ·  active annulus R55–270 mm  ·  16 sectors × 3 radial bands × 2 fibre populations',17,NAVY,550),
              '<line x1="88" y1="1180" x2="1736" y2="1180" stroke="#d8e2e9"/>',
              text(88,1209,'Orthographic cutaway · upper quadrant removed · selected fibres enlarged · rear housing in wireframe',14,MUTED),
              text(1736,1209,'nODD / 2026-10-20',14,MUTED,500,'end'),
              # Key is beside the main image rather than over its geometry.
              '<line x1="1115" y1="919" x2="1152" y2="919" stroke="#008e9f" stroke-width="3"/>',
              text(1161,925,'L · full depth',15,MUTED),
              '<line x1="1320" y1="919" x2="1357" y2="919" stroke="#456bd4" stroke-width="3"/>',
              text(1366,925,'S · delayed start',15,MUTED),
              text(1115,953,'Two overlapping depth weightings',15,MUTED),
              '</g></svg>']
    return '\n'.join(parts)+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Check retained SVG without writing')
    args=parser.parse_args()
    content=make_svg()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text()!=content:
            raise SystemExit('Retained 3D SVG differs; regenerate with draw_3d.py')
        print('3D SVG matches named design inputs and generator')
    else:
        OUTPUT.parent.mkdir(parents=True,exist_ok=True)
        OUTPUT.write_text(content)
        print(OUTPUT.relative_to(ROOT))


if __name__=='__main__':
    main()
