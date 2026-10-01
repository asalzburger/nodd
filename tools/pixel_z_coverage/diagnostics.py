#!/usr/bin/env python3
"""Matched paired regressions and fine luminous-z seam scan from retained layouts."""
import argparse
import gzip
import json
import math
from pathlib import Path

from layout import barrel
from sampling import directions, tracks_for
from intersections import SurfaceIndex


def read(path):return json.loads(gzip.decompress(path.read_bytes()))


def run(root,config):
    baseline=read(root/'baseline/track-results.json.gz')
    samples=directions(config['sampling'])
    paired={};scan={}
    for case in config['cases']:
        name=case['id'];raw=read(root/name/'track-results.json.gz');paired[name]={}
        for mode in baseline:
            b=baseline[mode]['per_subdetector_region']['pixel_barrel'];c=raw[mode]['per_subdetector_region']['pixel_barrel']
            # Unchanged detector regions must yield identical counts for every ray.
            for region,columns in baseline[mode]['per_subdetector_region'].items():
                if region!='pixel_barrel' and columns!=raw[mode]['per_subdetector_region'][region]:
                    raise AssertionError('Unchanged region changed: '+name+'/'+mode+'/'+region)
            if b['ideal_stations']!=c['ideal_stations']:raise AssertionError('Denominator changed')
            strata={}
            selections={'off_grid':[i for i,s in enumerate(samples) if s['cohort']=='off_grid']}
            for j in range(8):
                lo,hi=-4+j,-3+j
                selections[f'eta[{lo},{hi})']=[i for i,s in enumerate(samples) if s['cohort']=='off_grid' and lo<=s['eta']<hi]
            for lo,hi in [(-150,-50),(-50,50),(50,150)]:
                selections[f'z[{lo},{hi})']=[i for i,s in enumerate(samples) if s['cohort']=='off_grid' and lo<=s['origin_mm'][2]<hi]
            for label,indices in selections.items():
                delta=[c['missing_stations'][i]-b['missing_stations'][i] for i in indices]
                denom=sum(b['ideal_stations'][i] for i in indices)
                strata[label]=dict(tracks=len(indices),ideal_opportunities=denom,
                    gained_tracks=sum(d<0 for d in delta),lost_tracks=sum(d>0 for d in delta),
                    unchanged_tracks=sum(d==0 for d in delta),net_missing_change=sum(delta),
                    baseline_missing=sum(b['missing_stations'][i] for i in indices),
                    case_missing=sum(c['missing_stations'][i] for i in indices))
            paired[name][mode]=strata
        layout=read(root/name/'layout.json.gz');layout['modules']=[p for p in layout['modules'] if barrel(p)]
        layout['layers']=[l for l in layout['layers'] if l['subsystem']=='pixel' and l['kind']=='cylinder']
        index=SurfaceIndex(layout);rows=[]
        for z in range(-150,151):
            hit_counts=[]
            for j in range(16):
                track=dict(origin_mm=[.5,.5,z],eta=0.,phi=2*math.pi*(j+.3819660112501051)/16,charge=1,field_T=0.,pt_GeV=1.)
                hits=index.hits(track)
                stations={layout['modules'][i]['layer_id'] for i,_ in hits}
                hit_counts.append(len(stations))
            rows.append(dict(z_mm=z,mean_barrel_stations=sum(hit_counts)/16,min_barrel_stations=min(hit_counts)))
        scan[name]=rows
        print(name,'paired invariance PASS; z scan complete',flush=True)
    (root/'paired-comparison.json').write_text(json.dumps(paired,indent=2)+'\n')
    (root/'z-seam-scan.json').write_text(json.dumps(dict(definition='Straight eta=0, 16 phase-offset phi values, x=y=0.5 mm, z in 1 mm steps; finite sampling, not proof of hermeticity',cases=scan),indent=2)+'\n')
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="640" viewBox="0 0 1120 640"><rect width="1120" height="640" fill="white"/><g font-family="sans-serif" font-size="13">',
         '<text x="24" y="24" font-size="20">Pixel barrel seam scan: mean stations versus luminous z (eta=0)</text>',
         '<text x="24" y="48">16 fixed off-axis azimuths; straight rays; 1 mm z steps can miss narrower holes. No longitudinal stave staggering.</text>']
    colours=['#951e35','#be7424','#70784a','#885ab7','#147d78','#205ca6']
    for k,(name,rows) in enumerate(scan.items()):
        y0=90+k*82;x0=205
        svg.append(f'<text x="10" y="{y0+15}">{name}</text>')
        for level in (0,2,4):
            yy=y0+50-level*12
            svg.append(f'<path d="M{x0} {yy}h880" stroke="#ccd2da"/><text x="185" y="{yy+4}">{level}</text>')
        points=' '.join(f"{x0+(r['z_mm']+150)*880/300:.2f},{y0+50-r['mean_barrel_stations']*12:.2f}" for r in rows)
        svg.append(f'<polyline points="{points}" fill="none" stroke="{colours[k]}" stroke-width="1.2"/>')
    svg+=['<text x="200" y="618">−150 mm</text><text x="638" y="618">0</text><text x="1024" y="618">+150 mm</text></g></svg>']
    (root.parent/'z-seams.svg').write_text('\n'.join(svg)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);a=p.parse_args()
    run(a.run,json.loads(Path(__file__).with_name('config.json').read_text()))
