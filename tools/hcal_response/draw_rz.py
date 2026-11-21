"""Draw the selected tracker/LAr baseline with the DES045/046 HCAL proposal.

This is a composite envelope/sampling-stack schematic, not a common native
detector or an exact constant-phi material slice. No geometry is modified.
"""
import argparse
import copy
import hashlib
import html
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
COLOURS = {'pixel': '#0066cc', 'short_strip': '#ff9933',
           'long_strip': '#009999', 'ecal': '#cccc00',
           'hcal': '#cc6600', 'magnets': '#999999', 'beampipe': '#ffcc66'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def capture(gap_mm=400):
    context = ROOT/('docs/layouts/LAYOUT-002-gap400.json' if gap_mm == 400
                   else 'docs/layouts/LAYOUT-002-restored.json')
    d = json.loads(context.read_text())
    for path, wanted in d['tracker']['matched_source_sha256'].items():
        if sha(ROOT/path) != wanted:
            raise ValueError('Changed tracker snapshot source: '+path)
    receipt_path = ROOT/'docs/validation/hcal50-edge/geometry.json'
    receipt = json.loads(receipt_path.read_text())
    for path, wanted in receipt['source_sha256'].items():
        if sha(ROOT/path) != wanted:
            raise ValueError('Changed validated HCAL source: '+path)

    # Rebuild the current selected ECAL bounds, including local services. The
    # older snapshot's source hashes are historical, not current-source claims.
    sys.path.insert(0, str(ROOT/'tools/lar_calorimeter'))
    import compact_prototype as lar
    spec_path = ROOT/('tools/lar_calorimeter/gap400-prototype.json' if gap_mm == 400
                     else 'tools/lar_calorimeter/restored-sampling.json')
    spec, b, e, services = lar.configs(spec_path)
    selection = json.loads((ROOT/'detector/config/ecal-baseline.json').read_text())
    if (spec['id'] != d['source']['selection']['variant']
            or sha(spec_path) != d['source']['selection']['variant_spec_sha256']):
        raise ValueError('Retained ECAL variant specification changed')
    baseline_selection = (d['source']['baseline_context']['selection'] if gap_mm == 400
                          else d['source']['selection'])
    if selection['variant'] != baseline_selection['variant']:
        raise ValueError('Base ECAL selection changed')
    current = {}
    for name, config, build, augment in (
            ('barrel', b, lar.barrel_build, lar.barrel_services.augment),
            ('endcaps', e, lar.endcap_build, lar.endcap_services.augment)):
        report, materials = build(config)
        augment(report, materials, services)
        current[name] = report
        for key, value in report['envelopes'].items():
            if not math.isclose(d[name][key], value, abs_tol=1e-9):
                raise ValueError('Restored ECAL snapshot envelope changed: '+key)
        d[name].update(report['envelopes'])
    d['barrel'].update(sampling_inner_radius_mm=b['sampling_inner_radius_mm'],
                       sampling_outer_radius_mm=b['sampling_outer_radius_mm'], planes=b['planes'])
    d['endcaps']['wheels_mm'] = [[w['inner_radius_mm'], w['outer_radius_mm']]
                                for w in current['endcaps']['wheels']]
    c = json.loads((ROOT/'tools/hcal_response/config.json').read_text())
    carrier = json.loads((ROOT/'tools/hcal_readout/config.json').read_text())['carrier']['size_mm'][2]
    depth = c['layers']*(c['steel_mm']+carrier+c['installation_gap_mm'])+c['back_cover_mm']
    if (c['barrel']['outer_apothem_mm']-c['barrel']['front_apothem_mm'] != depth
            or c['endcap']['back_abs_z_mm']-c['endcap']['front_abs_z_mm'] != depth):
        raise ValueError('HCAL stack does not close')
    d['hcal'] = dict(front_mm=c['barrel']['front_apothem_mm'], outer_mm=c['barrel']['outer_apothem_mm'],
        half_z_mm=c['barrel']['half_z_mm'], endcap_front_mm=c['endcap']['front_abs_z_mm'],
        endcap_back_mm=c['endcap']['back_abs_z_mm'], endcap_inner_mm=c['endcap']['inner_apothem_mm'],
        endcap_outer_mm=c['endcap']['outer_apothem_mm'], layers=c['layers'], steel_mm=c['steel_mm'],
        carrier_mm=carrier, installation_gap_mm=c['installation_gap_mm'], back_cover_mm=c['back_cover_mm'],
        sectors=c['sectors'], edge_core_half_strip_mm=receipt['edge_coverage']['core_plane_inactive_half_strip_mm'],
        outer_corner_radius_mm=c['barrel']['outer_apothem_mm']/math.cos(math.pi/c['sectors']))
    d['date'] = '2026-11-20'
    d['status'] = ('Tracker and merged400mm-gap LAr variant plus isolated DES045/046 HCAL; DRAFT / PROTOTYPE'
                   if gap_mm == 400 else
                   'Selected tracker/LAr working baseline plus isolated DES045/046 HCAL; DRAFT / PROTOTYPE')
    d['ecal_gap_mm'] = gap_mm
    d['source'] = dict(input_revision=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        context_path=str(context.relative_to(ROOT)), context_sha256=sha(context),
        retained_context_provenance=d['source'],
        current_ecal_source_sha256={p:sha(ROOT/p) for p in sorted(set().union(
            *[set(v) for v in d['source']['geometry_source_sha256'].values()],
            {'detector/config/ecal-baseline.json',str(spec_path.relative_to(ROOT))}))},
        active_ecal_variant=spec['id'], active_ecal_spec_path=str(spec_path.relative_to(ROOT)),
        active_ecal_spec_sha256=sha(spec_path),
        hcal_receipt_path=str(receipt_path.relative_to(ROOT)), hcal_receipt_sha256=sha(receipt_path),
        hcal_source_revision=receipt['source_revision'], hcal_source_sha256=receipt['source_sha256'],
        renderer_sha256=sha(__file__))
    d['scope'] = ('Composite envelope/sampling-stack schematic. Tracker sensitive group bounds; '
                  + ('merged400mm-gap LAr ECAL variant warm and sampling bounds; ' if gap_mm == 400
                     else 'ECAL warm and sampling bounds; ')
                  +
                  'conditional solenoid allocations; isolated validated HCAL prototype. Polygon radii are face apothems. '
                  'Individual module/sector gaps and tracker passives are unresolved in this view. '
                  'No common native detector, installed field or engineering acceptance. FCAL and muons omitted.')
    return d


def capture_compact():
    """Display the screened 80mm-allowance proposal; no geometry adoption."""
    parent_path=ROOT/'docs/layouts/LAYOUT-002-DES046-gap400.json'
    screen_path=ROOT/'docs/validation/hcal-compact-screen/screen.json'
    screen=json.loads(screen_path.read_text())
    for path,wanted in screen['source_sha256'].items():
        if sha(ROOT/path)!=wanted:
            raise ValueError('Changed compaction screening input: '+path)
    if sha(ROOT/'tools/hcal_response/compact_screen.py')!=screen['generator_sha256']:
        raise ValueError('Changed compaction screening producer')
    candidate=next(c for c in screen['candidates'] if c['name']=='preserve_allowance80')
    if candidate['cassette_to_flange_mm']!=80 or candidate['overall_length_saved_mm']!=1040:
        raise ValueError('Unexpected compact proposal')
    d=json.loads(parent_path.read_text())
    old_hcal=copy.deepcopy(d['hcal'])
    d['hcal'].update(half_z_mm=candidate['barrel_half_z_mm'],
        endcap_front_mm=candidate['endcap_front_mm'],endcap_back_mm=candidate['endcap_back_mm'])
    if d['hcal']['endcap_back_mm']-d['hcal']['endcap_front_mm']!=candidate['depth_mm']:
        raise ValueError('Proposed stack depth changed')
    d.update(date='2026-11-21',status='Proposed compact HCAL envelope; not adopted or native-validated',
        proposal=dict(id='HCAL-AXIAL-COMPACT-ALLOW80',barrel_rows=candidate['barrel_rows'],
            cassette_to_flange_mm=80,overall_length_saved_mm=1040,previous_hcal=old_hcal,
            radial_handoff_mm=json.loads((ROOT/'tools/hcal_response/config.json').read_text())['radial_handoff_mm']),
        route_reservation=candidate['service_reservation'])
    d['source']=dict(input_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        parent_layout_path=str(parent_path.relative_to(ROOT)),parent_layout_sha256=sha(parent_path),
        parent_context_provenance=d['source'],screen_path=str(screen_path.relative_to(ROOT)),
        screen_sha256=sha(screen_path),screen_input_revision=screen['input_revision'],
        candidate='preserve_allowance80',renderer_sha256=sha(__file__))
    d['scope']=('Proposed compact HCAL envelope and sampling-stack schematic, not adopted or native-validated. '
        'Tracker/ECAL/solenoid unchanged from parent named layout. Dashed HCAL outlines show the previous envelope. '
        'Hatching between HCAL barrel and endcap marks an unconstructed ECAL-service exit reservation. '
        'Individual module/sector gaps and tracker passives unresolved; no installed solenoid field or engineering acceptance.')
    return d


def draw(d):
    b, e, h, m = (d[k] for k in ('barrel', 'endcaps', 'hcal', 'solenoid'))
    gap400 = d['services']['front_gap_mm'] == 400
    compact = d.get('proposal',{}).get('id') == 'HCAL-AXIAL-COMPACT-ALLOW80'
    scale, left, base = 84., 105., 730.
    x, y = lambda z:left+(z+10)*scale, lambda r:base-r*scale
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1900" height="1130" viewBox="0 0 1900 1130">',
           '<title>nODD proposed compact HCAL with tracker, solenoid and ECAL, R-Z</title>' if compact else
           '<title>nODD tracker, solenoid, restored LAr ECAL and DES046 HCAL, R-Z</title>',
           '<desc>'+html.escape(d['scope'])+'</desc><rect width="1900" height="1130" fill="white"/>',
           '<defs><pattern id="magnet" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="#eeeeee"/><path d="M0,0 L8,8" stroke="#999999" stroke-width="1"/></pattern></defs>']
    def text(a, v, s, size=20, anchor='start', weight='normal'):
        out.append(f'<text x="{a:.3f}" y="{v:.3f}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" fill="#25312e" text-anchor="{anchor}" font-weight="{weight}">{html.escape(s)}</text>')
    def box(z0, z1, r0, r1, fill, stroke='none', dash=None, width=1):
        if min(z1-z0, r1-r0) <= 0:
            raise ValueError('Nonpositive drawing box')
        out.append(f'<rect x="{x(z0):.3f}" y="{y(r1):.3f}" width="{(z1-z0)*scale:.3f}" height="{(r1-r0)*scale:.3f}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
    def pair(side, z0, z1, r0, r1, fill, stroke='none', dash=None):
        box(z0 if side>0 else -z1, z1 if side>0 else -z0, r0, r1, fill, stroke, dash)
    text(65,52,'nODD — proposed compact HCAL layout' if compact else 'nODD — tracker + solenoid + ECAL + HCAL',32,weight='bold')
    text(65,89,('DES043 tracker + solenoid allocation + 400 mm-gap LAr ECAL + 60-layer HCAL • 21 November 2026' if compact else
               'Merged 400 mm-gap LAr ECAL and DES043 tracker • 60-layer DES046 HCAL • 20 November 2026' if gap400 else
               'Current selected LAr ECAL and DES043 tracker • 60-layer HCAL with DES046 edge modules • 20 November 2026'),21)
    text(65,125,'Equal r–z scale • 1.04 m shorter overall • proposed envelope, not yet adopted' if compact else
         'Equal r–z scale • envelope and sampling-stack schematic • DRAFT / PROTOTYPE',20)
    for z in range(-10,11):
        out.append(f'<path d="M{x(z):.3f},{y(6.1):.3f} V{base:.3f}" stroke="#e4e8e4"/>')
        text(x(z),base+30,str(z),17,'middle')
    for r in range(7):
        out.append(f'<path d="M{x(-10):.3f},{y(r):.3f} H{x(10):.3f}" stroke="#e4e8e4"/>')
        text(left-17,y(r)+6,str(r),17,'end')
    text(left-40,y(6.1)-18,'r [m]',20)
    text(x(0),base+67,'z [m]',21,'middle')
    if compact:
        out.append('<defs><pattern id="exit" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M0,0 L8,8" stroke="#cccc00" stroke-width="1.5"/></pattern></defs>')
        for side in (-1,1):
            pair(side,h['half_z_mm']/1000,h['endcap_front_mm']/1000,
                 d['route_reservation']['lanes']['utility']['inner_radius_mm']/1000,
                 d['proposal']['radial_handoff_mm']/1000,'url(#exit)')
    box(-h['half_z_mm']/1000,h['half_z_mm']/1000,h['front_mm']/1000,h['outer_mm']/1000,'#f7e7d8')
    for side in (-1,1):
        pair(side,h['endcap_front_mm']/1000,h['endcap_back_mm']/1000,h['endcap_inner_mm']/1000,h['endcap_outer_mm']/1000,'#f7e7d8')
    # Radial barrel and axial endcap sampling periods. These depict the stack
    # organization, not uninterrupted sensitive planes or resolved module gaps.
    pitch = h['steel_mm']+h['carrier_mm']+h['installation_gap_mm']
    for layer in range(h['layers']):
        r=(h['front_mm']+layer*pitch)/1000
        box(-h['half_z_mm']/1000,h['half_z_mm']/1000,r,r+h['steel_mm']/1000,'#e6b88a')
        box(-h['half_z_mm']/1000,h['half_z_mm']/1000,r+h['steel_mm']/1000,r+(h['steel_mm']+h['carrier_mm'])/1000,COLOURS['hcal'])
        for side in (-1,1):
            z=(h['endcap_front_mm']+layer*pitch)/1000
            pair(side,z,z+h['steel_mm']/1000,h['endcap_inner_mm']/1000,h['endcap_outer_mm']/1000,'#e6b88a')
            pair(side,z+h['steel_mm']/1000,z+(h['steel_mm']+h['carrier_mm'])/1000,h['endcap_inner_mm']/1000,h['endcap_outer_mm']/1000,COLOURS['hcal'])
    box(-h['half_z_mm']/1000,h['half_z_mm']/1000,h['front_mm']/1000,h['outer_mm']/1000,'none',COLOURS['hcal'])
    for side in (-1,1):
        pair(side,h['endcap_front_mm']/1000,h['endcap_back_mm']/1000,h['endcap_inner_mm']/1000,h['endcap_outer_mm']/1000,'none',COLOURS['hcal'])
    if compact:
        old=d['proposal']['previous_hcal']
        box(-old['half_z_mm']/1000,old['half_z_mm']/1000,old['front_mm']/1000,old['outer_mm']/1000,'none',COLOURS['hcal'],'8 5',1.5)
        for side in (-1,1):
            pair(side,old['endcap_front_mm']/1000,old['endcap_back_mm']/1000,
                 old['endcap_inner_mm']/1000,old['endcap_outer_mm']/1000,'none',COLOURS['hcal'],'8 5')
    box(-b['warm_half_z_mm']/1000,b['warm_half_z_mm']/1000,b['inner_radius_mm']/1000,b['outer_radius_mm']/1000,'#f2f2c5',COLOURS['ecal'])
    box(-b['active_half_z_mm']/1000,b['active_half_z_mm']/1000,b['sampling_inner_radius_mm']/1000,b['sampling_outer_radius_mm']/1000,COLOURS['ecal'])
    for side in (-1,1):
        pair(side,e['warm_front_z_mm']/1000,e['warm_back_z_mm']/1000,e['warm_inner_radius_mm']/1000,e['warm_outer_radius_mm']/1000,'#f2f2c5',COLOURS['ecal'])
        for lo,hi in e['wheels_mm']:
            pair(side,e['sampling_front_z_mm']/1000,e['sampling_back_z_mm']/1000,lo/1000,hi/1000,COLOURS['ecal'])
        zz=side*(e['warm_front_z_mm']+e['warm_back_z_mm'])/2000
        out.append(f'<text transform="translate({x(zz):.3f} {y(1.7):.3f}) rotate(-90)" font-family="Arial,Helvetica,sans-serif" font-size="19" text-anchor="middle" fill="#25312e">LAr ECAL endcap</text>')
        zz=side*(h['endcap_front_mm']+h['endcap_back_mm'])/2000
        text(x(zz),y(4.6),'HCAL',23,'middle',weight='bold')
        text(x(zz),y(4.22),'endcap',20,'middle')
    if gap400:
        # The warm-envelope axial interval, not the sampling-edge interval.
        a,z=b['warm_half_z_mm']/1000,e['warm_front_z_mm']/1000
        yy=y(2.82)
        out.append(f'<path d="M{x(a):.3f},{yy:.3f} H{x(z):.3f} M{x(a):.3f},{yy-6:.3f} V{yy+6:.3f} M{x(z):.3f},{yy-6:.3f} V{yy+6:.3f}" stroke="#25312e" fill="none"/>')
        text(x((a+z)/2),yy-12,'400 mm',17,'middle')
    box(-m['vessel_half_length_m'],m['vessel_half_length_m'],m['vessel_inner_radius_m'],m['vessel_outer_radius_m'],'url(#magnet)',COLOURS['magnets'])
    box(-m['cold_half_length_m'],m['cold_half_length_m'],m['cold_inner_radius_m'],m['cold_outer_radius_m'],COLOURS['magnets'])
    box(-m['vessel_half_length_m'],m['vessel_half_length_m'],m['vessel_inner_radius_m'],m['assembly_outer_reservation_m'],'none',COLOURS['magnets'],'5 3')
    for g in d['tracker']['sensitive_groups']:
        key='pixel' if g['component']=='pixel' else ('short_strip' if g['component'].startswith('short') else 'long_strip')
        box(g['z_min_m'],g['z_max_m'],g['r_min_m'],g['r_max_m'],COLOURS[key])
    pipe=d['beam_pipe']
    out.append(f'<path d="M{x(-pipe["half_length_m"]):.3f},{y(pipe["display_radius_m"]):.3f} H{x(pipe["half_length_m"]):.3f}" stroke="{COLOURS["beampipe"]}" stroke-width="3"/>')
    text(x(0),y(4.7),'HCAL barrel · 60 sampling layers',24,'middle',weight='bold')
    text(x(0),y(4.28),'30 mm steel + 12 mm cassette + 1 mm allowance',20,'middle')
    text(x(0),y(2.1),'LAr ECAL barrel',23,'middle')
    text(x(0),y(1.47),'3 T solenoid allocation',18,'middle')
    for i,(key,label) in enumerate([('pixel','Pixels'),('short_strip','Short strips'),('long_strip','Long strips'),('ecal','ECAL'),('hcal','HCAL'),('magnets','Solenoid'),('beampipe','Beampipe')]):
        xx=65+i*254
        out.append(f'<rect x="{xx}" y="836" width="23" height="16" fill="{COLOURS[key]}"/>')
        text(xx+31,850,label,19)
    text(65,899,'Proposed HCAL barrel: |z| ≤ 5.740 m. Endcaps: |z| 6.240–8.830 m. Radial bounds and 60-layer depth retained.' if compact else
         'HCAL barrel: R 3.130–5.720 m, |z| ≤ 6.260 m. Endcaps: |z| 6.760–9.350 m, R 0.300–5.710 m.',20)
    text(65,936,'Polygon radii are face apothems; barrel corner reaches R 5.832 m. Steel: light orange; readout cassettes: dark orange.',19)
    text(65,973,'ECAL: pale yellow = warm package; yellow = sampling. Solenoid: hatched vessel, grey cold-mass allocation, dashed reservation.',19)
    text(65,1010,'Dashed orange: previous HCAL outline. Yellow hatching: relocated 500 mm service-exit reservation; no installed route.' if compact else
         'DES046 narrows the barrel edge modules to leave 7.05 mm per side at the core plane; the global r–z outline is unchanged.',19)
    text(65,1047,('ECAL warm gap 400 mm: |z| 4.100–4.500 m; endcaps |z| 4.500–5.660 m. External routes remain empty reservations.' if gap400 else
                 'Tracker: 46,682 sensitive planes; passive services and individual calorimeter module/sector gaps are unresolved here.'),19)
    text(65,1084,'43 barrel rows, retaining the 80 mm cassette/flange allowance. Native geometry, services and transition response await validation.' if compact else
         'Composite view, not a common native detector. Installed magnet, support/services qualification, FCAL and muon integration remain open.',18)
    out.append('</svg>')
    return '\n'.join(out)+'\n'


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--capture',action='store_true',help='Refresh named inputs from current source and validated HCAL receipt')
    p.add_argument('--ecal-gap-mm',type=int,choices=(400,1000),default=400,
                   help='ECAL warm-envelope gap for capture; default is the merged PR151 400mm variant')
    p.add_argument('--compact-hcal',action='store_true',help='Capture the screened, unadopted 80mm-allowance compact HCAL proposal')
    a=p.parse_args()
    if a.compact_hcal and not a.capture:
        p.error('--compact-hcal requires --capture; named proposal inputs replay without either flag')
    if a.compact_hcal and a.ecal_gap_mm!=400:
        p.error('The screened compact HCAL proposal uses the 400mm-gap ECAL')
    if a.capture:
        a.input.write_text(json.dumps(capture_compact() if a.compact_hcal else capture(a.ecal_gap_mm),indent=2)+'\n')
    d=json.loads(a.input.read_text())
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(draw(d))
