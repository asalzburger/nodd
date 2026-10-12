#!/usr/bin/env python3
"""Render retained DES-013 comparisons and vector module mockups."""
import argparse
import gzip
import json
from pathlib import Path
import sys
from layout import ROOT, load
from geometry import _shape


def read_report(path):
    if path.exists():return json.loads(path.read_text())
    return json.loads(gzip.decompress(path.with_suffix(path.suffix+'.gz').read_bytes()))


def available(path):
    return path.exists() or path.with_suffix(path.suffix+'.gz').exists()


def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,r))+' |' for r in rows])


def mockup(config,path):
    baseline=load(config);models=baseline['metadata']['models']
    from layout import shape
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="670" viewBox="0 0 1120 670">',
         '<rect width="1120" height="670" fill="white"/>',
         '<g font-family="sans-serif" fill="#16283a">',
         '<text x="24" y="28" font-size="21">DES-013 PROTOTYPE: bond / flex allowance moves into phi</text>',
         '<text x="24" y="54" font-size="14">Sensor face: z horizontal, tangential u vertical. Dimensions in mm. No qualified bond-loop or guard design.</text>']
    for row,family in enumerate(('single','quad')):
        old=_shape(family,models);case=next(c for c in config['cases'] if c['id']=='packed-200um');new=shape(family,models,case)
        for col,which in enumerate(('baseline','packed-200um')):
            cx=280+col*550;cy=210+row*280;scale=4.5
            if col==0:
                bz,bp=old['body_v'],old['body_u'];sz,sp=old['sensor_v'],old['sensor_u']
                dz,dp=old['body_v_offset'],0;patches=old['patches']
            else:
                bz,bp=new['body_z'],new['body_phi'];sz,sp=new['sensor_z'],new['sensor_phi']
                dz,dp=0,new['offset_phi'];patches=new['patches']
            def rect(z,p,w,h,fill,stroke):
                svg.append(f'<rect x="{cx+(z-w/2)*scale:.2f}" y="{cy-(p+h/2)*scale:.2f}" width="{w*scale:.2f}" height="{h*scale:.2f}" fill="{fill}" stroke="{stroke}"/>')
            rect(dz,dp,bz,bp,'#ffdeb0','#9d5705');rect(0,0,sz,sp,'#d3d7dc','#667788')
            for u,v,hu,hv in patches:rect(v,u,2*hv,2*hu,'#73c8c0','#197b76')
            svg.append(f'<text x="{cx-235}" y="{cy-116}" font-size="17">{family}: {which}</text>')
            svg.append(f'<text x="{cx-235}" y="{cy+120}" font-size="14">body z × phi = {bz:.1f} × {bp:.1f}; sensor = {sz:.1f} × {sp:.1f}</text>')
    svg+=['<text x="24" y="646" font-size="14">Teal: unchanged active ASIC matrices. Grey: inactive silicon. Orange: die/service occupied envelope. Quad 0.2 mm chip seams remain.</text>','</g></svg>']
    path.write_text('\n'.join(svg)+'\n')


def generate(run,out,config):
    out.mkdir(parents=True,exist_ok=True)
    records={c['id']:read_report(run/c['id']/'summary.json') for c in config['cases']}
    lines=['# DES-013 — Pixel barrel z-coverage prototype results','',
           '**Pending human approval.** Existing detector defaults are unchanged. See [design contract](../../design/DES-013-pixel-barrel-z-coverage.md) and [reproduction commands](../../../tools/pixel_z_coverage/README.md).','',
           '## Matched off-grid comparison','',
           '4,096 directions uniform in eta ∈ [-4,4], phi ∈ [0,2π], x/y ∈ [0,1] mm and z ∈ [-150,150] mm. Same rays for every layout. Fractions describe this sampling measure. A missing opportunity means an active hit is absent on a reachable ideal barrel layer; extra hits elsewhere cannot cancel it.','']
    rows=[]
    for name,r in records.items():
        inv=r['inventory'];b=inv['silicon']['pixel/barrel'];s=r['coverage']['straight']['cohorts']['off_grid']['pixel_barrel'];p=r['coverage']['positive']['cohorts']['off_grid']['pixel_barrel'];n=r['coverage']['negative']['cohorts']['off_grid']['pixel_barrel']
        rows.append([name,b['modules'],b['patches'],f"{b['sensor_area_m2']:.4f}",f"{100*s['missing_ideal_station_fraction']:.2f}%",f"{100*p['missing_ideal_station_fraction']:.2f}%",f"{100*n['missing_ideal_station_fraction']:.2f}%",f"{100*s['fraction_all_ideal_stations_hit']:.2f}%",f"{s['stations']['mean']:.4f}"])
    lines += [table(['Case','Modules','Chips','Sensor m²','Miss straight','Miss q+','Miss q−','All reachable hit, straight','Mean barrel stations, straight'],rows),'',
              'Bent primary sample: pT=1 GeV, constant 3 T, both charge signs. Silicon area counts physical sensor substrates once (including guards and chip seams), not ASIC silicon. All cases retain 82 staves and the four radii.','',
              '## Full tracker and separate momentum sensitivity','']
    rows=[]
    for name,r in records.items():
        c=r['coverage']['straight'];t=c['cohorts']['off_grid']['total'];b=c['cohorts']['eta0_z0']['pixel_barrel']
        rows.append([name,f"{t['stations']['mean']:.4f}",f"{r['inventory']['silicon']['total']['sensor_area_m2']:.4f}",f"{b['stations']['mean']:.2f}"]+[f"{100*r['total_p_coverage'][q]['cohorts']['off_grid']['pixel_barrel']['missing_ideal_station_fraction']:.2f}%" for q in ('positive','negative')])
    lines += [table(['Case','Mean total stations, straight','Total sensor m²','Mean barrel stations at eta=z=0','Miss total-p=1 GeV q+','Miss total-p=1 GeV q−'],rows),'',
              'The eta=z=0 diagnostic includes central and luminous-boundary grid azimuths. It is a seam probe, not an event-weighted average. Total-p curves follow the existing first-host-exit or transverse-half-turn convention; low-pT curling is consequently truncated.','',
              '## Per-layer and subsystem results','',
              'Tables below use the full matched 7,312-track cohort per primary mode (angular grid + luminous boundaries + random sample). Machine-readable summaries also retain eta and phi profiles, subsystem/region counts, sensor hits, missing stations, distributions, and per-track arrays. Endcaps and strips are byte-for-byte unchanged.','']
    for mode in ('straight','positive','negative'):
        rows=[]
        for name,r in records.items():
            c=r['coverage'][mode]
            rows.append([name]+[f"{100*c['per_layer'][f'A-pixel-B{i}']['missing_ideal_fraction']:.2f}%" for i in range(1,5)]+[f"{c['per_subdetector'][s]['stations']['mean']:.4f}" for s in ('pixel','short_strip','long_strip')])
        lines += [f'### {mode}','',table(['Case','B1 miss','B2 miss','B3 miss','B4 miss','Pixel stations','Short-strip stations','Long-strip stations'],rows),'']
    lines += ['## Mechanical packing, services and cooling','']
    rows=[]
    for name,r in records.items():
        for lid,x in r['inventory']['layers'].items():
            rows.append([name,lid.rsplit('-',1)[-1],x['rows'],f"{x['pitch_z_mm']:.3f}",f"{x['gap_mm']:.3f}",f"[{x['occupied_z_min_mm']:.1f}, {x['occupied_z_max_mm']:.1f}]",f"{x['stress_power_per_stave_W']:.2f}",f"{x['exit_quality_stress_imbalanced']:.4f}"])
    lines += [table(['Case','Layer','Rows','Pitch mm','Body gap mm','Occupied z mm','Stress W/stave','Stress exit quality'],rows),'',
              'Cooling uses DES002 power, 1.5 stress factor, 2/3 maximum heat share in either of two circuits, inlet quality 0.1 and inherited 1.3/2.5 g/s per circuit. The selected exit-quality ceiling is 0.45. This is a heat-balance screen; no new pressure-drop/flow stability/FEA or bond qualification. More chips also require revised power and data cable counts; inherited service metadata in layout files is reference-only.','',
              'No material is removed from an approved detector by this study. The proposed z gap reserves no end clamp or connector: mounting must be behind or lateral to the sensor. Guard, dicing, glue squeeze-out, placement and thermal-motion tolerances need expert review. The quad internal chip seam is still inactive.','',
              '## Geometry and native ACTS checks','']
    rows=[]
    for name,r in records.items():
        audit=run/name/'acts/native-target-audit.json'
        a=read_report(audit) if available(audit) else None
        seam_path=run/name/'acts-seams/native-target-audit.json'
        seam=read_report(seam_path) if available(seam_path) else None
        rows.append([name,r['body_screen']['overlapping_body_pairs'],len(r['support_screen']['conflicts']),f"{r['support_screen']['radial_headroom_mm']:.3f}",a['tracks_requested'] if a else 'NOT RUN',a['passed'] if a else 'NOT RUN',seam['tracks_requested'] if seam else 'NOT RUN',seam['passed'] if seam else 'NOT RUN',f"{a['maximum_trajectory_residual_mm']:.3g}" if a else '—'])
    lines += [table(['Case','Body overlaps','Support conflicts','Trunk radial headroom mm','ACTS tracks','Audit passed','Edge/seam tracks','Edge/seam passed','Max residual mm'],rows),'',
              'ACTS constructs all finite sensitive planes and propagates selected positive/negative/straight tracks to supporting planes with EigenStepper; native bounds and hit IDs are checked against the analytic oracle. Central seam and worst-missing-hit tracks supplement the random sample, including total-p=1 GeV. This audit does not validate global navigation, material interactions, detector response or reconstruction. The conservative broad phase is shared with the oracle; exhaustive synthetic tests check that boundary. Runtime/source/extension hashes and tolerances are in each audit.','',
              'Dedicated edge controls test 1 µm inside/outside each barrel layer’s actual z bounds, plus common z=−11/0/+11 mm seam rays. Audit pass means agreement with expected geometry, including predicted holes; it does not mean every track hits all layers.', '', '![Module rotation and narrowed z edge](module-orientation.svg)','',
              'See [recommendation and remaining approvals](recommendation.md).']
    (out/'results.md').write_text('\n'.join(lines)+'\n')
    mockup(config,out/'module-orientation.svg')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();generate(a.run,a.output,json.loads(Path(__file__).with_name('config.json').read_text()))
