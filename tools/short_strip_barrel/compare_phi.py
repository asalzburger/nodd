#!/usr/bin/env python3
"""DES-020 discrete stave symmetry and angular-overlap comparison (not acceptance)."""
import argparse
import json
import math
from pathlib import Path
from model import ROOT,load,build,frame,sha


def metrics(c):
    layout=build(c);rows=[];maximum=0
    for layer in layout['layers']:
        staves=[s for s in layout['staves'] if s['layer']==layer['layer']]
        n=len(staves);step=2*math.pi/n;modules=[m for m in layout['modules'] if m['layer']==layer['layer']]
        residual=0
        for m in modules:
            other=modules[((m['stave']+1)%n)*c['rows']+m['row']]
            for key in ('center_mm','u','n'):
                x,y,z=m[key];rot=[math.cos(step)*x-math.sin(step)*y,math.sin(step)*x+math.cos(step)*y,z]
                residual=max(residual,math.dist(rot,other[key]))
        spans=[];radial=[]
        for s in staves:
            for lift in (0,c['row_lift_mm']):
                ends=[frame(0,s['radius_mm'],[u,0,lift],s.get('tilt_rad',0)) for u in (-24,24)]
                span=math.atan2(ends[1][1],ends[1][0])-math.atan2(ends[0][1],ends[0][0])
                spans.append(span)
                for u in (-26.35,26.35):
                    for w in (-7.15,1.6):radial.append(math.hypot(*frame(0,s['radius_mm'],[u,0,w],s.get('tilt_rad',0))[:2]))
        rows.append(dict(layer=layer['layer'],staves=n,anchor_radii_mm=sorted({s['radius_mm'] for s in staves}),
            rotational_residual_mm_or_axis=residual,angular_pitch_deg=math.degrees(step),
            active_span_deg=[math.degrees(min(spans)),math.degrees(max(spans))],
            projected_overlap_fraction=[1-step/min(spans),1-step/max(spans)],
            conservative_cold_stack_radial_bounds_mm=[min(radial),max(radial)]))
        maximum=max(maximum,residual)
    return dict(layers=rows,modules=len(layout['modules']),staves=len(layout['staves']),
        maximum_one_stave_rotation_residual_mm_or_axis=maximum,
        scope='Local stave/sensor rotation only; ring continuous, twelve sectors and mixed layer pitches excluded. Angular overlap is a radial point-origin projection, not curved-track coverage.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    base=Path(__file__).with_name('inputs.json');alt=base.with_name('inputs-phi-tilted.json')
    result=dict(control=metrics(load(base)),phi_tilted=metrics(load(alt)),
        sources=dict(control_input=sha(base),alternative_input=sha(alt),model=sha(Path(__file__).with_name('model.py'))),producer_sha256=sha(__file__),
        limitations=['Same-handed tilts are not reflection symmetric.','N-fold local geometry is not continuous detector/sector symmetry or a resolution claim.','Projected overlap ignores luminous extent, field and inactive sensor guards; use independent finite-plane coverage.','Radial bounds enclose cold assembly only; mounting feet, rings and inactive end boards are separate.'])
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['phi_tilted'],indent=2))
