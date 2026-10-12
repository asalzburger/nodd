"""PROTOTYPE incremental solenoid material along straight IP rays; SI units.

Explicit annular cold body, aluminium vessel and thermal shield; no production
solids or DD4hep material map. Scenario assumptions are not an engineered BOM.
"""
import gzip
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess

ROOT=Path(__file__).resolve().parents[2]


def ray_length(eta, part, stop=math.inf):
    """Exact finite annulus/axial-slab intersection length along a straight ray.

    Ray r=s/cosh(eta), z=s*tanh(eta), s>=0. Annular caps and cylindrical walls
    use the same primitive; intersect radial, axial and forward-path intervals.
    """
    if not math.isfinite(eta) or abs(eta)>10:
        raise ValueError('finite |eta| <=10 required')
    r0,r1,z0,z1=(part[k] for k in ('r_min_m','r_max_m','z_min_m','z_max_m'))
    if not all(math.isfinite(v) for v in (r0,r1,z0,z1)) or not 0<=r0<r1 or not z0<z1 or math.isnan(stop) or stop<=0:
        raise ValueError('invalid annular solid or ray extent')
    sr=1/math.cosh(eta); sz=math.tanh(eta)
    lo,hi=r0/sr,r1/sr
    if sz==0:
        if not z0<=0<=z1:return 0.
    else:
        a,b=sorted((z0/sz,z1/sz));lo=max(lo,a);hi=min(hi,b)
    return max(0.,min(hi,stop)-max(0.,lo))


def part(name,component,r0,r1,z0,z1,x0):
    return dict(name=name,component=component,r_min_m=r0,r_max_m=r1,
                z_min_m=z0,z_max_m=z1,X0_m=x0)


def enclosure(name,component,r0,r1,h,wall,end,x0):
    # Caps occupy end axial intervals. Barrel walls terminate at cap inner faces
    # so joints have no positive-volume overlap or double-counted material.
    if min(wall,end,x0)<=0 or r0+wall>=r1-wall or end>=h:
        raise ValueError('enclosure wall does not fit')
    return [part(name+'_inner',component,r0,r0+wall,-h+end,h-end,x0),
            part(name+'_outer',component,r1-wall,r1,-h+end,h-end,x0),
            part(name+'_end_positive',component,r0,r1,h-end,h,x0),
            part(name+'_end_negative',component,r0,r1,-h,-h+end,x0)]


def solids(sizing,assumptions,scenario):
    values=[assumptions[k] for k in ('aluminum_X0_m','atlas_cold_thickness_m','atlas_cold_t_over_X0',
        'shield_inner_radius_m','shield_outer_radius_m','shield_half_length_m')]
    values += [scenario[k] for k in ('cold_material_multiplier','vessel_barrel_wall_m','vessel_end_wall_m','shield_wall_m')]
    if not all(type(v) in (int,float) and math.isfinite(v) and v>0 for v in values):
        raise ValueError('positive finite material assumptions required')
    al=assumptions['aluminum_X0_m']
    proxy=scenario['cold_proxy']
    if proxy=='pure_aluminum':x0=al
    elif proxy=='atlas_equivalent':
        x0=assumptions['atlas_cold_thickness_m']/assumptions['atlas_cold_t_over_X0']
    else:raise ValueError('unknown cold material proxy')
    x0/=scenario['cold_material_multiplier']
    r=sizing
    cold=part('cold_mass','cold_mass',r['cold_inner_radius_m'],r['cold_outer_radius_m'],
              -r['cold_mass_length_m']/2,r['cold_mass_length_m']/2,x0)
    warm=enclosure('vessel','vessel',r['vessel_inner_radius_m'],r['vessel_outer_radius_m'],
                   r['vessel_length_m']/2,scenario['vessel_barrel_wall_m'],scenario['vessel_end_wall_m'],al)
    shield=enclosure('shield','shield',assumptions['shield_inner_radius_m'],
                     assumptions['shield_outer_radius_m'],assumptions['shield_half_length_m'],
                     scenario['shield_wall_m'],scenario['shield_wall_m'],al)
    result=[cold,*warm,*shield]
    for p in result:
        if not (r['vessel_inner_radius_m']<=p['r_min_m']<p['r_max_m']<=r['vessel_outer_radius_m']
                and -r['vessel_length_m']/2<=p['z_min_m']<p['z_max_m']<=r['vessel_length_m']/2):
            raise ValueError('material escapes vessel allocation')
        if p['X0_m']<=0:raise ValueError('nonpositive radiation length')
    for i,a in enumerate(result):
        for b in result[i+1:]:
            if min(a['r_max_m'],b['r_max_m'])>max(a['r_min_m'],b['r_min_m'])+1e-12 and min(a['z_max_m'],b['z_max_m'])>max(a['z_min_m'],b['z_min_m'])+1e-12:
                raise ValueError('overlapping material parts '+a['name']+' / '+b['name'])
    return result


def material_budget(eta,parts,sizing):
    # All proposed magnet parts are inside these proposed ECAL entrance bounds.
    # This is a convenient clipping envelope, not proof of an active face/acceptance.
    stop_r=sizing['proposed_ecal_inner_radius_m']*math.cosh(eta)
    sz=abs(math.tanh(eta))
    stop_z=sizing['proposed_ecal_endcap_front_m']/sz if sz else math.inf
    totals={k:0. for k in ('cold_mass','vessel','shield')}
    for p in parts:totals[p['component']]+=ray_length(eta,p,min(stop_r,stop_z))/p['X0_m']
    return dict(eta=eta,**totals,total=sum(totals.values()))


def evaluate():
    paths=['docs/validation/DES-026/sizing.json','tools/solenoid_baseline/material-assumptions.json',
           'tools/solenoid_baseline/material.py']
    sizing=json.loads((ROOT/paths[0]).read_text())['result']
    assumptions=json.loads((ROOT/paths[1]).read_text())
    n=round((assumptions['eta_max']-assumptions['eta_min'])/assumptions['eta_step'])
    etas=[assumptions['eta_min']+i*assumptions['eta_step'] for i in range(n+1)]
    scenarios=[]
    for scenario in assumptions['scenarios']:
        parts=solids(sizing,assumptions,scenario)
        rows=[material_budget(e,parts,sizing) for e in etas]
        scenarios.append(dict(id=scenario['id'],assumptions=scenario,solids=parts,profile=rows,
                              central=rows[0],peak=max(rows,key=lambda r:r['total'])))
    for rows in zip(*(s['profile'] for s in scenarios)):
        if not rows[0]['total']<=rows[1]['total']+1e-12<=rows[2]['total']+2e-12:
            raise ValueError('material scenario ordering violated')
    return dict(status='PROTOTYPE estimate; scenario spread, not a confidence interval or native material scan',
                python=platform.python_version(),
                execution_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                execution_dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),
                input_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
                ray_definition='Straight rays from IP; eta=-ln(tan(theta/2)); axial symmetry; both signs give same result. Incremental magnet material only.',
                exclusions=['existing tracker and beam pipe','calorimeter own material/cryostat','local supports/feet/chimney/penetrations/cables','real conductor BOM and exact material map','helix transport and shower/jet response'],
                assumptions=assumptions,scenarios=scenarios)

if __name__=='__main__':
    report=evaluate();out=ROOT/'docs/validation/DES-026/material.json'
    profiles={s['id']:s.pop('profile') for s in report['scenarios']}
    profile_path=out.with_name('material-profile.json.gz')
    profile_path.write_bytes(gzip.compress(json.dumps(profiles,separators=(',',':')).encode(),mtime=0))
    report['profile_file']=str(profile_path.relative_to(ROOT))
    report['profile_sha256']=hashlib.sha256(profile_path.read_bytes()).hexdigest()
    report['eta_sampling_step']=report['assumptions']['eta_step']
    out.write_text(json.dumps(report,indent=2)+'\n')
    for s in report['scenarios']:
        print(s['id'],'eta0=',round(s['central']['total'],6),'peak=',round(s['peak']['total'],6),'at eta=',s['peak']['eta'])
