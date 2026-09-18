#!/usr/bin/env python3
"""DES-006 PROTOTYPE: inclined ring envelopes, explicit face and station accounting.

C is an axisymmetric envelope of module rows, not a tiled detector or IdRes input.
A/B retained inputs and evidence are never overwritten by this study.
"""
import copy
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

from study import intersection, area, validate, KAPPA

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'docs/design/DES-006-layouts.json'
CONFIG = ROOT / 'docs/design/DES-006-inclined-layouts.json'
REPORT = ROOT / 'docs/validation/DES-006-inclined-screen.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def candidate_c(baseline, recipe):
    """Replace each strip barrel's end bands by finite, mirrored inclined rows."""
    result = {'id': 'C', 'name': 'Inclined strip barrel ends', 'layers': []}
    start, end, step = (recipe[k] for k in ('start_z_m', 'end_z_m', 'band_step_m'))
    margin = recipe['tangent_margin_m']
    for original in baseline['layers']:
        layer = copy.deepcopy(original)
        layer['id'] = 'C' + layer['id'][1:]
        layer['station_group'] = layer['id']
        if layer['kind'] != 'cylinder' or layer['subsystem'] == 'pixel':
            result['layers'].append(layer)
            continue
        radius = layer['r_m']
        layer['z_min_m'], layer['z_max_m'] = -start, start
        result['layers'].append(layer)
        for side in (-1, 1):
            for index in range(round((end - start) / step)):
                lo, hi = start + index * step, start + (index + 1) * step
                zc = (lo + hi) / 2
                alpha = min(math.atan2(zc, radius), math.radians(recipe['max_tilt_deg']))
                nr, nz = math.cos(alpha), math.sin(alpha)
                d = nr * radius + nz * zc
                endpoints = []
                for zb, extension in ((lo, -margin), (hi, margin)):
                    slope = zb / radius
                    r = d / (nr + nz * slope)
                    z = slope * r
                    endpoints.append((r - nz * extension, side * (z + nr * extension)))
                row = {k: v for k, v in layer.items() if k not in ('r_m', 'z_min_m', 'z_max_m')}
                row.update(id=f"{layer['id']}-{'P' if side > 0 else 'N'}{index+1}",
                           kind='inclined_ring', r0_m=radius, z0_m=side * zc,
                           normal_r=nr, normal_z=side*nz,
                           r1_m=endpoints[0][0], z1_m=endpoints[0][1],
                           r2_m=endpoints[1][0], z2_m=endpoints[1][1],
                           provenance='DES-006-C07')
                result['layers'].append(row)
    return result


def validate_ring(layer, host):
    for key in ('r0_m', 'z0_m', 'r1_m', 'z1_m', 'r2_m', 'z2_m',
                'normal_r', 'normal_z', 'x0_percent', 'sigma_rphi_m', 'sigma_second_m'):
        value = layer[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError('Nonfinite ring parameter')
    nr, nz = layer['normal_r'], layer['normal_z']
    if nr <= 0 or not math.isclose(nr*nr+nz*nz, 1., abs_tol=1e-12):
        raise ValueError('Ring normal must be a unit vector with positive radial component')
    if layer['x0_percent'] < 0 or min(layer['sigma_rphi_m'], layer['sigma_second_m']) <= 0:
        raise ValueError('Invalid material/response')
    if layer['z1_m'] == layer['z2_m']:
        raise ValueError('Empty or unsupported horizontal ring')
    for i in (1, 2):
        r, z = layer[f'r{i}_m'], layer[f'z{i}_m']
        if not host['r_min_m'] <= r <= host['r_max_m'] or abs(z) > host['abs_z_max_m']:
            raise ValueError('Inclined row outside host')
        if abs(nr*(r-layer['r0_m'])+nz*(z-layer['z0_m'])) > 1e-12:
            raise ValueError('Endpoint is not on ring envelope')


def ring_intersection(layer, eta, zv, pt, field):
    if pt <= 0:
        raise ValueError('pT must be positive')
    sh, ch = math.sinh(eta), math.cosh(eta)
    rho = math.inf if field == 0 else pt/(KAPPA*abs(field))
    nr, nz = layer['normal_r'], layer['normal_z']
    constant = nr*layer['r0_m'] + nz*layer['z0_m']
    if sh == 0:
        if not min(layer['z1_m'],layer['z2_m']) <= zv <= max(layer['z1_m'],layer['z2_m']):
            return None
        r = (constant-nz*zv)/nr
        if r <= 0 or r >= 2*rho:
            return None
        st = r if math.isinf(rho) else 2*rho*math.asin(r/(2*rho))
    else:
        low, high = sorted(( (layer['z1_m']-zv)/sh, (layer['z2_m']-zv)/sh ))
        low, high = max(0., low), min(math.pi*rho, high)
        if high <= low:
            return None
        def residual(st):
            r = st if math.isinf(rho) else 2*rho*math.sin(st/(2*rho))
            return nr*r + nz*(zv+st*sh) - constant
        # Current candidate and scan have nz*sinh(eta)>=0: residual is monotonic.
        # Unsupported opposite-facing cases fail explicitly, rather than miss roots.
        if nz*sh < 0:
            raise ValueError('Opposite-facing ring crossing requires a general root solver')
        flo, fhi = residual(low), residual(high)
        if flo > 1e-12 or fhi < -1e-12:
            return None
        for _ in range(45):
            middle = (low+high)/2
            if residual(middle) < 0:
                low = middle
            else:
                high = middle
        st = (low+high)/2
        r = st if math.isinf(rho) else 2*rho*math.sin(st/(2*rho))
    z = zv+st*sh
    cosine = abs(nr*math.cos(st/(2*rho)) + nz*sh)/ch
    if st <= 0 or st >= math.pi*rho or cosine < 1e-12:
        return None
    return r, z, st*ch, layer['x0_percent']/cosine


def crossings(candidate, eta, zv, pt, field):
    hits = []
    for layer in candidate['layers']:
        hit = (ring_intersection(layer, eta, zv, pt, field) if layer['kind']=='inclined_ring'
               else intersection(layer, eta, zv, pt, field))
        if hit:
            hits.append((layer, hit))
    return sorted(hits, key=lambda item: item[1][2])


def summarize(hits):
    # Count parent station groups conservatively; extra row crossings carry material
    # and faces. This grouping is not a claim about their full fit information.
    groups = {l.get('station_group', l['id']): l for l, _ in hits}
    long_pairs = sum(l['subsystem']=='long_strip' for l, _ in hits)
    return dict(stations=len(groups), module_crossings=len(hits),
                pixel_stations=sum(l['subsystem']=='pixel' for l in groups.values()),
                long_strip_pair_crossings=long_pairs, long_strip_scalar_faces=2*long_pairs,
                silicon_face_crossings=len(hits)+long_pairs,
                grouped_station_coordinates=2*len(groups),
                physical_scalar_coordinates=2*len(hits),
                local_material_percent=sum(h[3] for _, h in hits),
                radial_span_m=max((h[0] for _,h in hits),default=0)-min((h[0] for _,h in hits),default=0))


def area_ledger(candidate):
    totals = dict(pixel=0.,short_strip=0.,long_strip=0.)
    for layer in candidate['layers']:
        if layer['kind']=='inclined_ring':
            value=math.pi*(layer['r1_m']+layer['r2_m'])*math.hypot(
                layer['r2_m']-layer['r1_m'],layer['z2_m']-layer['z1_m'])
        else:
            value=area({'layers':[layer]})[layer['subsystem']]
        totals[layer['subsystem']]+=value
    return {'reference_area_m2':totals,
            'silicon_face_area_m2':dict(totals, long_strip=2*totals['long_strip']),
            'long_strip_material_ownership':'2% normal X0 per paired module, counted once per crossing; two silicon faces'}


def run(config, baseline):
    validate(baseline)
    a=baseline['candidates'][0]
    c=candidate_c(a,config['recipe'])
    for layer in c['layers']:
        if layer['kind']=='inclined_ring': validate_ring(layer,baseline['host'])
    candidates=[a,c]
    scan=baseline['scan']
    step=scan['eta_step']
    etas=[round(scan['eta_min']+i*step,10)
          for i in range(round((scan['eta_max']-scan['eta_min'])/step)+1)]
    profiles=[]
    worst=[]
    comparisons=[]
    for field in scan['field_T']:
        for pt in scan['pt_GeV']:
            for zv in scan['vertex_z_m']:
                rows={}
                for cand in candidates:
                    rows[cand['id']]=[summarize(crossings(cand,e,zv,pt,field)) for e in etas]
                    values=rows[cand['id']]
                    worst.append(dict(candidate=cand['id'],field_T=field,pt_GeV=pt,vertex_z_m=zv,
                                      min_stations=min(r['stations'] for r in values),
                                      max_material_percent=max(r['local_material_percent'] for r in values)))
                    if field==3 and pt in (1,100):
                        profiles.append(dict(candidate=cand['id'],field_T=field,pt_GeV=pt,vertex_z_m=zv,
                                             rows=[dict(eta=e,**r) for e,r in zip(etas[::5],values[::5])]))
                lost=[e for e,ra,rc in zip(etas,rows['A'],rows['C']) if rc['stations']<ra['stations']]
                ratios=[rc['local_material_percent']/ra['local_material_percent'] for ra,rc in zip(rows['A'],rows['C'])]
                comparisons.append(dict(field_T=field,pt_GeV=pt,vertex_z_m=zv,
                                         station_loss_etas=lost,min_C_over_A_material=min(ratios),
                                         max_C_over_A_material=max(ratios),
                                         material_increase_eta_points=sum(r>1+1e-10 for r in ratios)))
    landmarks=[]
    for cand in candidates:
        for eta in [0.,.5,.8,1.,1.2,1.5,2.,2.5,3.,4.]:
            for zv in scan['vertex_z_m']:
                hits=crossings(cand,eta,zv,100,3)
                landmarks.append(dict(candidate=cand['id'],eta=eta,vertex_z_m=zv,**summarize(hits)))
    config['candidate']=c
    return dict(status='PROTOTYPE: geometric/material comparison only',
                areas={cand['id']:area_ledger(cand) for cand in candidates},
                landmarks=landmarks,extrema=worst,comparisons=comparisons,profiles=profiles,
                scan=dict(scan,profile_step=5*step),
                limitations=['Axisymmetric conical row envelopes, no planar phi tiling or module masks',
                             'All overlaps charged material; repeated rows of a parent station counted once',
                             'No beam pipe/remote services, no scattering fit, no C IdRes prediction',
                             'Uniform fields, vertex stress probes, no efficiency or engineering acceptance'])


def main():
    config=json.loads(CONFIG.read_text())
    baseline=json.loads(BASE.read_text())
    report=run(config,baseline)
    CONFIG.write_text(json.dumps(config,indent=2)+'\n')
    report['provenance']=dict(project_revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
       working_tree_dirty=bool(subprocess.check_output(['git','status','--porcelain'])),
       input_sha256=sha(CONFIG),baseline_sha256=sha(BASE),code_sha256=sha(Path(__file__)),
       geometry_code_sha256=sha(ROOT/'tools/tracker_layout/study.py'),python=platform.python_version(),
       command=' '.join(sys.argv),seed=None)
    report['margin_controls'] = []
    for margin in (0., .005, .01):
        control = copy.deepcopy(config)
        control['recipe']['tangent_margin_m'] = margin
        result = report if margin == .01 else run(control,baseline)
        report['margin_controls'].append(dict(
            tangent_margin_m=margin, areas=result['areas']['C'],
            lost_station_probe_count=sum(len(r['station_loss_etas']) for r in result['comparisons']),
            min_C_over_A_material=min(r['min_C_over_A_material'] for r in result['comparisons']),
            max_C_over_A_material=max(r['max_C_over_A_material'] for r in result['comparisons'])))
    REPORT.write_text(json.dumps(report,indent=2)+'\n')
    print('Wrote C geometry and signed-eta 2/3/4 T, 1/10/100 GeV, three-vertex comparison.')


if __name__=='__main__': main()
