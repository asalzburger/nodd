"""Capture restored baseline envelopes and draw a reproducible equal-scale R-Z view."""
import argparse
import hashlib
import html
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
COLOURS={'pixel':'#0066cc','short_strip':'#ff9933','long_strip':'#009999',
         'ecal':'#cccc00','hcal':'#cc6600','magnets':'#999999','beampipe':'#ffcc66'}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def capture(baseline):
    record=json.loads((baseline/'baseline.json').read_text())
    if record['ecal_selection']['variant']!='LAR-RESTORED-SAMPLING-2026-11-18':
        raise ValueError('Need the selected restored LAr baseline')
    for file,key in [('detector.xml','compact_sha256'),('materials.xml','materials_sha256')]:
        if sha(baseline/file)!=record[key]:raise ValueError('Changed composed artifact: '+file)
    folder=baseline/'components/restored-lar'
    b=json.loads((folder/'barrel/expected.json').read_text())
    e=json.loads((folder/'endcaps/expected.json').read_text())
    for c in record['components']:
        if sha(c['compact'])!=c['compact_sha256'] or sha(Path(c['compact']).parent/'materials.xml')!=c['materials_sha256']:
            raise ValueError('Changed component export')
    tracker_path=ROOT/'docs/layouts/tracker-baseline-des043.json'
    tracker=json.loads(tracker_path.read_text())['tracker']
    for path,want in tracker['matched_source_sha256'].items():
        if sha(ROOT/path)!=want:raise ValueError('Changed tracker overlay source: '+path)
    context_path=ROOT/'docs/layouts/LAYOUT-002.json'
    context=json.loads(context_path.read_text());s=b['services']['config']
    return dict(schema_version=1,layout='LAYOUT-002',date='2026-11-18',
        status='User-selected restored LAr EM working baseline; engineering approval open',
        units='mm; tracker and conditional magnet context retained in metres',
        source=dict(exporter_sha256=record['exporter_sha256'],layout_generator_sha256=sha(__file__),
            selection=record['ecal_selection'],compact_sha256=record['compact_sha256'],materials_sha256=record['materials_sha256'],
            component_sha256={c['component']:dict(compact=c['compact_sha256'],materials=c['materials_sha256']) for c in record['components']},
            tracker_context_sha256=sha(tracker_path),magnet_context_sha256=sha(context_path),
            geometry_execution={name:r['execution'] for name,r in [('barrel',b),('endcaps',e)]},
            geometry_source_sha256={name:r['source_sha256'] for name,r in [('barrel',b),('endcaps',e)]}),
        barrel=dict(**b['envelopes'],sampling_inner_radius_mm=b['config']['sampling_inner_radius_mm'],
            sampling_outer_radius_mm=b['config']['sampling_outer_radius_mm'],planes=b['config']['planes']),
        endcaps=dict(**e['envelopes'],wheels_mm=[[w['inner_radius_mm'],w['outer_radius_mm']] for w in e['wheels']]),
        services=dict(front_gap_mm=s['front_service_gap_mm'],rear_gap_mm=s['rear_service_gap_mm'],route_radius_mm=s['external_route_radius_mm']),
        hcal=dict(front_mm=s['hcal_barrel_front_apothem_mm'],outer_mm=s['hcal_barrel_front_apothem_mm']+s['hcal_total_depth_mm'],
            half_z_mm=s['hcal_barrel_half_z_mm'],endcap_front_mm=s['hcal_endcap_front_z_mm'],
            endcap_back_mm=s['hcal_endcap_front_z_mm']+s['hcal_total_depth_mm'],
            endcap_inner_mm=s['hcal_endcap_inner_radius_mm'],endcap_outer_mm=s['hcal_endcap_outer_apothem_mm']),
        tracker=tracker,solenoid=context['solenoid'],beam_pipe=context['beam_pipe'],
        scope='Tracker sensitive overlay and actual ECAL envelopes; conditional magnet/HCAL context only. FCAL omitted pending updated integration. No field, full-detector response or engineering acceptance.')


def draw(d):
    b,e,h=d['barrel'],d['endcaps'],d['hcal'];scale=86.;left=100.;base=730.
    prototype=d.get('prototype_variant')=='LAR-GAP400-SIDE-EGRESS-2026-11-18'
    x=lambda z:left+(z+9)*scale
    y=lambda r:base-r*scale
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1030" viewBox="0 0 1800 1030">',
         '<title>LAr conditional400mm-gap prototype, R-Z envelopes</title>' if prototype else '<title>Restored LAr EM working baseline, R-Z envelopes</title>',
         '<desc>Equal axial and radial scales. Current tracker sensitive bounds, restored LAr cryostat and sampling. Magnet and HCAL are conditional context. FCAL integration pending.</desc>',
         '<rect width="1800" height="1030" fill="white"/>']
    def text(X,Y,t,size=20,anchor='start',weight='normal'):
        out.append(f'<text x="{X:.3f}" y="{Y:.3f}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" fill="#25312e" text-anchor="{anchor}" font-weight="{weight}">{html.escape(t)}</text>')
    def box(z0,z1,r0,r1,fill,stroke='#667066',dash=None):
        out.append(f'<rect x="{x(z0):.3f}" y="{y(r1):.3f}" width="{(z1-z0)*scale:.3f}" height="{(r1-r0)*scale:.3f}" fill="{fill}" stroke="{stroke}" stroke-width="1"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
    text(65,52,'LAr 400 mm gap — conditional side-egress prototype' if prototype else 'Restored LAr — selected EM calorimeter working baseline',31,weight='bold')
    text(65,89,'1.8 mm Pb • 1248 inclined barrel periods • 650 mm turbine-endcap sampling • prototype 2026-11-18' if prototype else '1.8 mm Pb • 1248 inclined barrel periods • 650 mm turbine-endcap sampling • selection 2026-11-18',21)
    text(65,124,'Equal R–Z scale; physical ECAL envelopes from the selected export. Conditional magnet and HCAL context are outlined.',19)
    text(65,166,'Tracker: 46,682 sensitive planes. Light ECAL shade: warm package; solid ECAL shade: sampling envelope.',19)
    for z in range(-9,10):
        out.append(f'<path d="M{x(z):.3f},{y(5):.3f} V{base}" stroke="#e3e7e2"/>');text(x(z),base+29,str(z),17,'middle')
    for r in range(6):
        out.append(f'<path d="M{x(-9):.3f},{y(r):.3f} H{x(9):.3f}" stroke="#e3e7e2"/>');text(left-15,y(r)+6,str(r),17,'end')
    box(-h['half_z_mm']/1000,h['half_z_mm']/1000,h['front_mm']/1000,h['outer_mm']/1000,'#f2dbc5',COLOURS['hcal'],'7 4')
    box(-b['warm_half_z_mm']/1000,b['warm_half_z_mm']/1000,b['inner_radius_mm']/1000,b['outer_radius_mm']/1000,'#f2f2c5',COLOURS['ecal'])
    box(-b['active_half_z_mm']/1000,b['active_half_z_mm']/1000,b['sampling_inner_radius_mm']/1000,b['sampling_outer_radius_mm']/1000,COLOURS['ecal'])
    for side in (-1,1):
        def pair(z0,z1,r0,r1,fill,stroke='#667066',dash=None):
            box(z0 if side>0 else -z1,z1 if side>0 else -z0,r0,r1,fill,stroke,dash)
        pair(e['warm_front_z_mm']/1000,e['warm_back_z_mm']/1000,e['warm_inner_radius_mm']/1000,e['warm_outer_radius_mm']/1000,'#f2f2c5',COLOURS['ecal'])
        for lo,hi in e['wheels_mm']:
            pair(e['sampling_front_z_mm']/1000,e['sampling_back_z_mm']/1000,lo/1000,hi/1000,COLOURS['ecal'])
        pair(h['endcap_front_mm']/1000,h['endcap_back_mm']/1000,h['endcap_inner_mm']/1000,h['endcap_outer_mm']/1000,'#f2dbc5',COLOURS['hcal'],'7 4')
        text(x(side*7.5),y(3.6),'HCAL',19,'middle');text(x(side*7.5),y(3.3),'context',17,'middle')
        out.append(f'<text transform="translate({x(side*(e["warm_front_z_mm"]+e["warm_back_z_mm"])/2000):.3f} {y(1.9):.3f}) rotate(-90)" font-family="Arial,Helvetica,sans-serif" font-size="17" text-anchor="middle" fill="#25312e">LAr endcap</text>')
    if prototype:
        out.append('<defs><pattern id="reserved" width="7" height="7" patternUnits="userSpaceOnUse"><path d="M0,0 L7,7" stroke="#919100" stroke-width="1"/></pattern></defs>')
        r=d['route_reservation'];a,z=r['side_neck_band_abs_z_mm'];lo,hi=r['radial_single_jacket_bounds_mm'];lane=r['lanes']['utility']
        for side in (-1,1):
            box(a/1000 if side>0 else -z/1000,z/1000 if side>0 else -a/1000,lo/1000,hi/1000,'url(#reserved)','#919100','4 3')
            box(z/1000 if side>0 else -h['half_z_mm']/1000,h['half_z_mm']/1000 if side>0 else -z/1000,lane['inner_radius_mm']/1000,lane['outer_radius_mm']/1000,'url(#reserved)','#919100','4 3')
            box(4.5 if side>0 else -4.85,4.85 if side>0 else -4.5,.301,.450,'none','#b33e32','3 2')
        text(65,204,'Hatched neck/bus: unconstructed reservations; ports, board/ring clearance and connected bundles remain open.',18)
    m=d['solenoid'];box(-m['vessel_half_length_m'],m['vessel_half_length_m'],m['vessel_inner_radius_m'],m['vessel_outer_radius_m'],'#dddddd',COLOURS['magnets'],'5 3')
    for g in d['tracker']['sensitive_groups']:
        key='pixel' if g['component']=='pixel' else ('short_strip' if g['component'].startswith('short') else 'long_strip')
        box(g['z_min_m'],g['z_max_m'],g['r_min_m'],g['r_max_m'],COLOURS[key],COLOURS[key])
    pipe=d['beam_pipe'];out.append(f'<path d="M{x(-pipe["half_length_m"]):.3f},{y(pipe["display_radius_m"]):.3f} H{x(pipe["half_length_m"]):.3f}" stroke="{COLOURS["beampipe"]}" stroke-width="3"/>')
    text(x(0),y(3.75),'HCAL barrel context',23,'middle');text(x(0),y(2.12),'LAr sampling',22,'middle')
    text(x(0),base+64,'z [m] — both signs; r [m] — positive radius',21,'middle')
    for i,(key,label) in enumerate([('pixel','Pixels'),('short_strip','Short strips'),('long_strip','Long strips'),('ecal','ECAL'),('hcal','HCAL context'),('magnets','Magnet context'),('beampipe','Beampipe')]):
        xx=65+i*244;out.append(f'<rect x="{xx}" y="832" width="23" height="15" fill="{COLOURS[key]}"/>');text(xx+31,846,label,18)
    text(65,890,'Warm gap 0.400 m • endcap package |z| 4.500–5.660 m • sampling depth and barrel geometry retained' if prototype else 'Barrel sampling R 1.7728–2.3500 m • warm outer R 2.6417 m • endcap package |z| 5.100–6.260 m',20)
    text(65,925,'Endcap-to-HCAL interval 1.100 m; retained radial exit window 0.500 m. HCAL context is fixed.' if prototype else 'Front / rear service reservations: 1.000 / 0.500 m. HCAL endcap context: |z| 6.760–8.2559 m.',19)
    text(65,960,'Red outline: prospective collar conflict R301–450 mm, |z|4500–4850 mm. Forward integration remains open.' if prototype else 'FCAL/collar omitted: previous routing and clearance results require reassessment for the shifted HCAL context.',19)
    text(65,995,'Tracker passives omitted in this view. No installed solenoid field, combined response or engineering qualification is implied.',18)
    out.append('</svg>');return '\n'.join(out)+'\n'


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--baseline',type=Path);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.baseline:a.input.write_text(json.dumps(capture(a.baseline),indent=2)+'\n')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(draw(json.loads(a.input.read_text())))
