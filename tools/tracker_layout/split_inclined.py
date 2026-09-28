#!/usr/bin/env python3
"""DES-006 PROTOTYPE: isolate short-strip tilt (C1) from all-strip tilt (C2).

Reuses the validated C solver and preserves the original A/B/C inputs and evidence.
No layer-position optimization, detector integration or fitted performance claim.
"""
import copy
import json
from pathlib import Path
import platform
import subprocess
import sys

from inclined_study import crossings, summarize, area_ledger, sha

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'docs/design/DES-006-layouts.json'
OLD_C = ROOT/'docs/design/DES-006-inclined-layouts.json'
CONFIG = ROOT/'docs/design/DES-006-inclined-split-layouts.json'
REPORT = ROOT/'docs/validation/DES-006-inclined-split-screen.json'


def renamed(layer, cid):
    result = copy.deepcopy(layer)
    result['id'] = cid + layer['id'][1:]
    result['station_group'] = cid + layer.get('station_group', layer['id'])[1:]
    return result


def variants(a, c):
    c1 = dict(id='C1', name='Inclined short strips; cylindrical long strips', layers=[])
    c2 = dict(id='C2', name='Inclined short and long strips (original C)', layers=[])
    for layer in c['layers']:
        c2['layers'].append(renamed(layer, 'C2'))
        if layer['subsystem'] != 'long_strip':
            c1['layers'].append(renamed(layer, 'C1'))
    c1['layers'].extend(renamed(l, 'C1') for l in a['layers'] if l['subsystem']=='long_strip')
    return [a, c1, c2]


def run(baseline, original_c):
    candidates = variants(baseline['candidates'][0], original_c['candidate'])
    scan = baseline['scan']
    step = scan['eta_step']
    etas = [round(scan['eta_min']+i*step, 10)
            for i in range(round((scan['eta_max']-scan['eta_min'])/step)+1)]
    summaries, profiles, landmarks = [], [], []
    keys = ['stations', 'module_crossings', 'silicon_face_crossings',
            'long_strip_scalar_faces', 'local_material_percent', 'radial_span_m']
    for field in scan['field_T']:
        for pt in scan['pt_GeV']:
            for zv in scan['vertex_z_m']:
                rows = {c['id']: [summarize(crossings(c,e,zv,pt,field)) for e in etas] for c in candidates}
                for cid in ('C1','C2'):
                    ratios = [r['local_material_percent']/a['local_material_percent']
                              for r,a in zip(rows[cid],rows['A'])]
                    summaries.append(dict(candidate=cid,field_T=field,pt_GeV=pt,vertex_z_m=zv,
                        min_stations=min(r['stations'] for r in rows[cid]),
                        lost_station_etas=[e for e,r,a in zip(etas,rows[cid],rows['A']) if r['stations']<a['stations']],
                        min_material_ratio_to_A=min(ratios),max_material_ratio_to_A=max(ratios),
                        min_ratio_eta=etas[ratios.index(min(ratios))],max_ratio_eta=etas[ratios.index(max(ratios))]))
                if field==3 and pt in (1,100):
                    for cid, values in rows.items():
                        profiles.append(dict(candidate=cid,field_T=field,pt_GeV=pt,vertex_z_m=zv,
                                             **{k:[r[k] for r in values[::5]] for k in keys}))
                if field==3 and pt==100:
                    for cid, values in rows.items():
                        landmarks.extend(dict(candidate=cid,eta=e,vertex_z_m=zv,**r)
                                         for e,r in zip(etas,values) if e in [0.,.5,.8,1.,1.2,1.5,2.,2.5,3.,4.])
    # Finer vertex/transition check, at zero field as in the retained independent audit.
    dense = []
    for zv in scan['vertex_z_m']:
        for c in candidates[1:]:
            loss=[]
            for i in range(8001):
                eta=round(-4+i*.001,10)
                a=summarize(crossings(candidates[0],eta,zv,100,0))
                b=summarize(crossings(c,eta,zv,100,0))
                if b['stations']<a['stations']: loss.append(eta)
            dense.append(dict(candidate=c['id'],vertex_z_m=zv,lost_station_etas=loss))
    config=dict(schema_version=1,status='DRAFT / PROTOTYPE',units=baseline['units'],
        host=baseline['host'],classification='NODD DESIGN CHOICE DES-006-C08; unsigned, no approving humans',
        recipe=original_c['recipe'],
        definition={'C1':'Original C for short strips; A for every long-strip layer',
                    'C2':'Original C geometry and material, renamed; both strip types inclined',
                    'common':'A pixels/disks; original radii and row centres; no position optimization'},
        candidates=candidates)
    report=dict(status='PROTOTYPE comparison, no layout selection or performance acceptance',
        areas={c['id']:area_ledger(c) for c in candidates},
        geometry_inventory={c['id']:dict(inclined_rows=sum(l['kind']=='inclined_ring' for l in c['layers']),
            inclined_long_strip_rows=sum(l['kind']=='inclined_ring' and l['subsystem']=='long_strip' for l in c['layers']))
            for c in candidates},scan=scan,probes_per_candidate=len(etas)*len(scan['field_T'])*len(scan['pt_GeV'])*len(scan['vertex_z_m']),
        summaries=summaries,eta_grid=etas[::5],profiles=profiles,landmarks=landmarks,
        dense_zero_field_scan=dict(eta_step=.001,points_per_vertex=8001,rows=dense),
        limitations=['Conical envelopes of planar rows; no module tiling/phi gaps or engineering clearance',
                     'Both long-strip faces counted; pair material once; every overlap contributes material',
                     'Parent station count is a coverage proxy, not complete measurement information or efficiency',
                     'No position optimization, complete service budget, C1/C2 IdRes or scattering fit'])
    return config,report


def main():
    baseline=json.loads(BASE.read_text()); original_c=json.loads(OLD_C.read_text())
    config,report=run(baseline,original_c)
    CONFIG.write_text(json.dumps(config,indent=2)+'\n')
    report['provenance']=dict(command=' '.join(sys.orig_argv),python=platform.python_version(),seed=None,
        project_revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        working_tree_dirty=bool(subprocess.check_output(['git','status','--porcelain'])),
        hashes={str(p.relative_to(ROOT)):sha(p) for p in
                [BASE,OLD_C,CONFIG,Path(__file__),ROOT/'tools/tracker_layout/inclined_study.py',ROOT/'tools/tracker_layout/study.py']})
    REPORT.write_text(json.dumps(report,indent=2)+'\n')
    print('Wrote C1/C2 split and A comparison, including dense vertex coverage checks.')


if __name__=='__main__': main()
