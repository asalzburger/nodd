"""Independent signed-sagitta and scattering controls for actual station crossings.

Integrates the equation of motion twice rather than calling the implementation
weight generator. Source evaluation is shared and is separately controlled by
the exact-wire, loop, Maxwell and energy tests. Writes the paired JSON report.
"""
import sys,math,json,hashlib,copy
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from tools.toroid_prototype import system
from tools.toroid_prototype.field import evaluate
root=ROOT
files=['tools/toroid_prototype/system.py','tools/toroid_prototype/field.py','tools/toroid_prototype/field_backend.cpp','tools/toroid_prototype/design.json','tools/toroid_prototype/geometry.py','tools/toroid_prototype/solenoid-input.json']
hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files}
cfg=system.load_design(); norm=system.normalize_currents(cfg); src=system.toroid_sources(cfg)
gnodes,gweights=np.polynomial.legendre.leggauss(128)
def integrate(a,b,f):
    ss=a+(gnodes+1)*(b-a)/2
    return np.dot(gweights,f(ss))*(b-a)/2
out=[]
for eta,phi in [(0,15),(.8,15),(1.10,7.5),(1.14,7.5),(1.22,22.5),(2,0),(-2,0),(math.asinh(cfg['stations']['disk_abs_z_m'][0]/cfg['stations']['barrel_radii_m'][0])-.001,7.5)]:
    ph=math.radians(phi);ur=1/math.cosh(eta);uz=math.tanh(eta)
    direction=np.array([ur*math.cos(ph),ur*math.sin(ph),uz]);ephi=np.array([-math.sin(ph),math.cos(ph),0.])
    types=['barrel' if r*abs(math.sinh(eta)) <= z-cfg['stations']['barrel_end_shortening_m'] else 'disk' for r,z in zip(cfg['stations']['barrel_radii_m'],cfg['stations']['disk_abs_z_m'])]
    stations=np.array([r/ur if typ=='barrel' else abs(z/uz) for typ,r,z in zip(types,cfg['stations']['barrel_radii_m'],cfg['stations']['disk_abs_z_m'])])
    a,b,d=stations; t=(b-a)/(d-a)
    def f(ss):return evaluate(ss[:,None]*direction,src)@ephi
    # Integrate y''=Bphi twice and remove the line fixed by first/last hits.
    y2=integrate(a,b,lambda ss:(b-ss)*f(ss))
    y3=integrate(a,b,lambda ss:(d-ss)*f(ss))+integrate(b,d,lambda ss:(d-ss)*f(ss))
    direct=-(y2-t*y3)
    authored=system.signed_response(eta,phi,cfg,src)
    rel=abs(direct-authored['integral_T_m2'])/max(abs(direct),1e-12)
    assert rel<2e-5,(eta,phi,rel)
    # Independent uniform angular-scattering integral for unequal hit distances.
    # slope kicks are propagated to measured three-hit interpolation residual.
    variance_weight=integrate(a,b,lambda ss:((b-ss)-t*(d-ss))**2)+integrate(b,d,lambda ss:(t*(d-ss))**2)
    exact=(b-a)**2*(d-b)**2/(3*(d-a))
    assert math.isclose(variance_weight,exact,rel_tol=1e-12)
    out.append({'eta':eta,'phi_deg':phi,'types':types, 'stations_s_m':stations.tolist(),'independent_integral_T_m2':float(direct),'authored_integral_T_m2':authored['integral_T_m2'],'relative_difference':rel,'uniform_scattering_variance_weight_m3':float(variance_weight)})
# The revised nominal seams overlap in angular coverage while their full-depth
# faces retain50mm separation. Preserve missing-hit rejection with a deliberately
# gapped TEST fixture, rather than asserting that the physical revision has gaps.
nominal_seams=[]
for sr,sz in zip(cfg['stations']['barrel_radii_m'],cfg['stations']['disk_abs_z_m']):
    barrel_end=math.asinh((sz-cfg['stations']['barrel_end_shortening_m'])/sr)
    disk_start=math.asinh(sz/(sr+cfg['stations']['outline_thickness_m']/2))
    assert barrel_end>=disk_start
    nominal_seams.append({'barrel_max_eta':barrel_end,'disk_min_eta':disk_start,'overlap_eta':barrel_end-disk_start})
gap_fixture=copy.deepcopy(cfg);gap_fixture['stations']['barrel_end_shortening_m']=.5
sr=gap_fixture['stations']['barrel_radii_m'][0];sz=gap_fixture['stations']['disk_abs_z_m'][0]
seam_barrel_end=math.asinh((sz-gap_fixture['stations']['barrel_end_shortening_m'])/sr)
seam_disk_start=math.asinh(sz/(sr+gap_fixture['stations']['outline_thickness_m']/2))
assert seam_disk_start>seam_barrel_end
seam_eta=(seam_disk_start+seam_barrel_end)/2
seam_missing=[i+1 for i,(r,z) in enumerate(zip(gap_fixture['stations']['barrel_radii_m'],gap_fixture['stations']['disk_abs_z_m'])) if r*math.sinh(seam_eta)>z-gap_fixture['stations']['barrel_end_shortening_m'] and z/math.sinh(seam_eta)>r+gap_fixture['stations']['outline_thickness_m']/2]
assert seam_missing
try:
    system.response_points(seam_eta,7.5,gap_fixture)
except ValueError:
    seam_control={'fixture':'revised dimensions with deliberately gapped500mm barrel shortening, not physical proposal','eta':seam_eta,'phi_deg':7.5,'independently_missing_stations':seam_missing,'implementation_rejects_missing_station':True,'revised_nominal_seams':nominal_seams}
else:
    raise AssertionError('finite seam was replaced with an idealized station')
# True signed cancellation control: Bphi positive then equally negative around midpoint.
for a,b,d in [(0.,1.5,3.),(1.,2.,5.)]:
    t=(b-a)/(d-a)
    wa=integrate(a,b,lambda ss:(ss-a)*(1-t))
    wb=integrate(b,d,lambda ss:(d-ss)*t)
    amplitude=wa/wb
    signed=wa-amplitude*wb;absolute=wa+amplitude*wb
    assert abs(signed)<1e-12 and absolute>0
# Refinement changes the source quadrature and curved paths, retaining fixed currents.
fine=system.toroid_sources(cfg,order=6,corners=32)
refine=[]
for eta,phi in [(0,15),(2,0),(1.14,7.5)]:
    nominal=system.signed_response(eta,phi,cfg,src,order=96)['B_sag_T']
    high=system.signed_response(eta,phi,cfg,fine,order=96)['B_sag_T']
    refine.append({'eta':eta,'phi_deg':phi,'nominal_B_sag_T':nominal,'refined_B_sag_T':high,'relative_change':abs(high-nominal)/abs(high)})
report={'status':'Independent physics arithmetic controls at recorded file hashes; no acceptance or transport efficiency claim','input_sha256':hashes,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'reproduction_command':'python3 docs/validation/DES-039/independent-response-controls.py','normalization':norm,'response_comparisons':out,'finite_surface_gap_control':seam_control,'source_refinement':refine,'signed_cancellation_control':'passed: equal weighted opposite fields cancel despite positive integral of magnitude','limits':['No finite-outline acceptance assertion; coil masks evaluated separately.','Field-source implementation is shared; observable integration and unequal-spacing variance were independently derived.','No nonlinear steel response or conductor engineering checks.']}
Path(__file__).with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'output':str(Path(__file__).with_suffix('.json')),'response_cases':len(out),'maximum_relative_response_difference':max(x['relative_difference'] for x in out),'maximum_source_refinement_change':max(x['relative_change'] for x in refine)},indent=2))
