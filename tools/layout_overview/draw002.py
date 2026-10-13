"""Deterministic LAYOUT-002 envelope SVG; isolated native ECAL evidence is separate."""
import argparse
import hashlib
import html
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
INPUT=ROOT/'docs/layouts/LAYOUT-002.json';OUTPUT=ROOT/'docs/layouts/figures/LAYOUT-002-rz.svg'
def draw(d):
    t=d['tracker'];v=d['view'];e=d['ecal'];h=d['hcal'];s=d['services']
    if sum(g['count'] for g in t['sensitive_groups'])!=45646:raise ValueError('Tracker snapshot count')
    if not math.isclose(e['endcap_front_abs_z_m']-e['barrel_half_length_m'],s['front_axial_gap_m'],abs_tol=1e-12):raise ValueError('Front gap mismatch')
    if not math.isclose(h['endcap_front_abs_z_m']-e['endcap_back_abs_z_m'],s['rear_axial_gap_m'],abs_tol=1e-12):raise ValueError('Rear gap mismatch')
    scale,left,base=100,110,730
    x=lambda z:left+(z-v['z_min_m'])*scale
    y=lambda r:base-r*scale
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="1900" height="980" viewBox="0 0 1900 980" role="img" aria-labelledby="title description">',
        '<title id="title">LAYOUT-002: tracker, conditional inner3T magnet, ALLEGRO-style LAr ECAL and enlarged HCAL outline</title>',
        '<desc id="description">Equal-scale envelope R-Z view, positive radius and both signs of z. Physical LAr cryostat and sampling envelopes; empty routing gaps and hatched unbuilt FCal/collar. Forward eta4 uncovered; no muon system.</desc>',
        '<metadata>'+html.escape(json.dumps(dict(input_sha256=hashlib.sha256(INPUT.read_bytes()).hexdigest(),generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_revisions=sorted({a['revision'] for a in d['sources'].values()})),sort_keys=True))+'</metadata>',
        '<defs><pattern id="missing" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M0,0 L8,8" stroke="#c94757" stroke-width="1"/></pattern></defs>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#24344a}.title{font-size:29px;font-weight:700}.sub{font-size:20px}.label{font-size:17px}.small{font-size:16px}.grid{stroke:#e5eaf0;stroke-width:1}</style>',
        '<rect width="1900" height="980" fill="white"/>',
        '<text x="80" y="49" class="title">LAYOUT-002 · Tracker + inner3T solenoid + ALLEGRO-style LAr ECAL</text>',
        '<text x="80" y="83" class="sub">Alternative DRAFT PROTOTYPE · larger HCAL/service envelopes · engineering and response sign-off pending</text>']
    def text(z,r,label,klass='label'):
        out.append(f'<text x="{x(z):.3f}" y="{y(r):.3f}" class="{klass}" text-anchor="middle">{html.escape(label)}</text>')
    def box(z0,z1,r0,r1,fill,stroke='#8191a7',dash=None):
        if z0>=z1 or r0>=r1:raise ValueError('Invalid envelope')
        ds=f' stroke-dasharray="{dash}"' if dash else ''
        out.append(f'<rect x="{x(z0):.3f}" y="{y(r1):.3f}" width="{(z1-z0)*scale:.3f}" height="{(r1-r0)*scale:.3f}" fill="{fill}" stroke="{stroke}" stroke-width="1.2"{ds}/>')
    for lx,fill,label in [(80,'#3b9b79','Tracker sensitive bounds'),(420,'#beaad8','Conditional3T magnet'),(780,'#f4cc78','LAr cryostat / sampling'),(1170,'#f0f3f7','HCAL outline'),(1450,'#d5eff3','Empty service space'),(1710,'url(#missing)','Unbuilt FCal')]:
        out.append(f'<rect x="{lx}" y="112" width="25" height="17" fill="{fill}" stroke="#718298"/><text x="{lx+33}" y="127" class="small">{label}</text>')
    for z in range(-8,9):
        out.append(f'<path d="M{x(z):.3f},{y(5):.3f} V{base}" class="grid"/>');text(z,-.27,str(z),'small')
    for r in range(6):
        out.append(f'<path d="M{left},{y(r):.3f} H{x(v['z_max_m']):.3f}" class="grid"/><text x="{left-18}" y="{y(r)+6:.3f}" class="small" text-anchor="end">{r}</text>')
    box(-h['barrel_half_length_m'],h['barrel_half_length_m'],h['barrel_front_apothem_m'],h['barrel_outer_apothem_m'],'#f0f3f7',dash='7 5')
    text(0,4.12,'HCAL barrel · enlarged outline','sub')
    box(-e['barrel_half_length_m'],e['barrel_half_length_m'],e['barrel_outer_radius_m'],h['barrel_front_apothem_m'],'#d5eff3')
    text(0,3.00,'300mm external routing corridor','small')
    box(-e['barrel_half_length_m'],e['barrel_half_length_m'],e['barrel_inner_radius_m'],e['barrel_outer_radius_m'],'#f9e8c3')
    box(-e['barrel_active_half_length_m'],e['barrel_active_half_length_m'],e['barrel_sampling_inner_radius_m'],e['barrel_sampling_outer_radius_m'],'#f4cc78')
    text(0,2.40,'LAr barrel ·1536 inclined periods','sub')
    for side in (-1,1):
        def mirrored(a,b,r0,r1,fill,stroke='#8191a7',dash=None):
            box(a if side>0 else -b,b if side>0 else -a,r0,r1,fill,stroke,dash)
        a,b=e['endcap_front_abs_z_m'],e['endcap_back_abs_z_m']
        mirrored(a,b,e['endcap_outer_radius_m'],h['barrel_front_apothem_m'],'#d5eff3')
        mirrored(e['barrel_half_length_m'],a,.30,h['barrel_front_apothem_m'],'#e7f4f6')
        mirrored(b,h['endcap_front_abs_z_m'],.30,h['barrel_outer_apothem_m'],'#e7f4f6')
        mirrored(a,b,e['endcap_inner_radius_m'],e['endcap_outer_radius_m'],'#f9e8c3')
        for r0,r1 in e['endcap_wheels_m']:
            mirrored(e['endcap_sampling_front_abs_z_m'],e['endcap_sampling_back_abs_z_m'],r0,r1,'#f4cc78','#b28135')
        mirrored(h['endcap_front_abs_z_m'],h['endcap_back_abs_z_m'],h['endcap_inner_apothem_m'],h['endcap_outer_apothem_m'],'#f0f3f7',dash='7 5')
        text(side*7.10,2.5,'HCAL endcap','sub');text(side*7.10,2.23,'outline only','small')
        text(side*5.35,3.60,'LAr turbine','small')
        for z,label in ((side*4.5,'800mm service gap'),(side*6.11,'500mm service gap')):
            out.append(f'<text x="{x(z):.3f}" y="{y(1.65):.3f}" class="small" text-anchor="middle" transform="rotate(-90 {x(z):.3f} {y(1.65):.3f})">{label}</text>')
        for f in d['forward_reservations']:
            mirrored(f['z_min_abs_m'],f['z_max_abs_m'],f['r_min_m'],f['r_max_m'],'url(#missing)','#c94757')
        # eta4 ray is a geometric reference, not claimed acceptance.
        a,b=0,8.05
        out.append(f'<path d="M{x(0):.3f},{y(0):.3f} L{x(side*b):.3f},{y(b/math.sinh(4)):.3f}" stroke="#be3a51" stroke-dasharray="4 4"/>')
    m=d['solenoid']
    box(-m['vessel_half_length_m'],m['vessel_half_length_m'],m['vessel_inner_radius_m'],m['vessel_outer_radius_m'],'#e8e0f2','#9876b4')
    box(-m['cold_half_length_m'],m['cold_half_length_m'],m['cold_inner_radius_m'],m['cold_outer_radius_m'],'#beaad8','#9876b4')
    text(0,1.54,'Conditional inner3T solenoid · PR64','small')
    reservation=t['planning_reservation'];box(-reservation['half_length_m'],reservation['half_length_m'],0,reservation['radius_m'],'none',dash='4 4')
    colours={'pixel':'#8754b4','short':'#247db1','long':'#33996b'}
    for g in t['sensitive_groups']:
        family='pixel' if g['component']=='pixel' else g['component'].split('_')[0]
        box(g['z_min_m'],g['z_max_m'],g['r_min_m'],g['r_max_m'],colours[family],colours[family])
    text(0,.90,'Tracker ·45,646 sensitive planes','sub')
    bp=d['beam_pipe'];out.append(f'<path d="M{x(-bp['half_length_m']):.3f},{y(bp['display_radius_m']):.3f} H{x(bp['half_length_m']):.3f}" stroke="#596879"/>')
    text(0,-.62,'z [m] · equal axial/radial scale','sub')
    out.append('<text x="38" y="480" class="sub" transform="rotate(-90 38 480)" text-anchor="middle">r [m]</text>')
    out += ['<text x="110" y="830" class="sub">Hatched collar/FCal are empty future reservations; the red |η|=4 rays have no active LAr coverage.</text>',
        '<text x="110" y="863" class="small">Circular LAr radii; HCAL sector-centre16-gon apothems (corners extend farther). Blocks include inactive walls/supports/baths.</text>',
        '<text x="110" y="893" class="small">Full-depth barrel/endcap transition unresolved. Adverse power exceeds cooling allowance. Ports, headers and machine interfaces remain open.</text>',
        '<text x="110" y="923" class="small">Tracker passives omitted; HCAL physical modules, FCal, muon system and muon-system magnets not included. No full-detector field/response claim.</text>',
        '<text x="110" y="955" class="small">Pinned inputs: docs/layouts/LAYOUT-002.json · DES032/PR73 barrel + DES033 turbine · native LAr ECAL evidence is separate from this illustration.</text>','</svg>']
    result='\n'.join(out)+'\n';ET.fromstring(result);return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();r=draw(json.loads(INPUT.read_text()))
    if a.check:
        if not OUTPUT.exists() or OUTPUT.read_text()!=r:raise SystemExit('Retained LAYOUT002 differs from inputs')
        print('PASS deterministic LAYOUT002 SVG')
    else:OUTPUT.write_text(r);print('Wrote',OUTPUT)
