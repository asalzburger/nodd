"""PROTOTYPE review-directed solenoid sizing; SI; vacuum stored energy.

U = 1/2 integral(J.A dV) = integral(B^2/(2 mu0) dV) over ALL space.
Integrate axial separation analytically in the Neumann loop-pair integral.
No finite map truncation, near-wire point evaluation, iron or toroid model.
"""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import numpy as np
from solenoid import MU0

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT/'tools/magnetic_study/sizing-policy.json'
POLICY = json.loads(POLICY_PATH.read_text())


def check_field(value):
    if not math.isfinite(value) or abs(value) > POLICY['central_field_max_T']:
        raise ValueError('central field must be finite and |B(0)| <= 5 T')


def pack_current(a, b, length, b0):
    check_field(b0)
    if not all(math.isfinite(v) for v in (a,b,length)) or not 0<a<b or length<=0:
        raise ValueError('invalid winding bounds')
    h=length/2
    return b0/(MU0*h*(math.asinh(b/h)-math.asinh(a/h)))


def stored_energy(a, b, length, b0, nr=48, nphi=192):
    """All-space vacuum energy, not a uniform-bore energy proxy.

    d^2=(r-r')^2+4rr'sin(phi/2)^2; G=L asinh(L/d)-hypot(L,d)+d.
    U=mu0 J^2 integral dr dr' rr' integral_0^pi cos(phi) G(d) dphi.
    Log singularity is integrable; endpoint-free quadrature, refine explicitly.
    """
    j=pack_current(a,b,length,b0)
    if any(isinstance(n,bool) or not isinstance(n,int) or n<2 for n in (nr,nphi)):
        raise ValueError('quadrature orders must be integers >=2')
    x,w=np.polynomial.legendre.leggauss(nr)
    r=(a+b)/2+(b-a)/2*x;w=w*(b-a)/2
    x,v=np.polynomial.legendre.leggauss(nphi)
    phi=(x+1)*math.pi/2;v=v*math.pi/2
    rr=r[:,None]*r[None,:]
    d=np.sqrt((r[:,None,None]-r[None,:,None])**2+4*rr[:,:,None]*np.sin(phi/2)**2)
    g=length*np.arcsinh(length/d)-np.hypot(length,d)+d
    angular=np.sum(g*(v*np.cos(phi))[None,None,:],axis=2)
    return float(MU0*j*j*np.sum(w[:,None]*w[None,:]*rr*angular))


def solve(family, nr=48, nphi=192):
    rv=family['vessel_inner_radius_m'];length=family['cold_mass_length_m'];b0=family['central_field_T']
    if rv<=0 or length<=0 or family['axial_gap_per_end_m']<=0 or b0==0:
        raise ValueError('positive physical dimensions and energized winding required')
    check_field(b0)
    a=rv*POLICY['inner_radius_scale']+POLICY['inner_radius_offset_m']
    fraction=POLICY['winding_radial_fraction_of_cold_mass'];density=POLICY['energy_per_cold_volume_J_m3']
    def evaluate(t):
        u=stored_energy(a,a+fraction*t,length,b0,nr,nphi)
        volume=math.pi*((a+t)**2-a*a)*length
        return u,volume
    lo,hi=1e-4,a
    while evaluate(hi)[0] > density*evaluate(hi)[1]:
        hi*=2
        if hi>100*a:raise ValueError('could not bracket energy/volume root')
    for _ in range(42):
        t=(lo+hi)/2;u,v=evaluate(t)
        if u>density*v:lo=t
        else:hi=t
    t=(lo+hi)/2;u,v=evaluate(t);b=a+fraction*t
    return dict(id=family['id'],candidates=family['candidates'],vessel_inner_radius_m=rv,
        cold_inner_radius_m=a,cold_outer_radius_m=a+t,winding_outer_radius_m=b,
        cold_mass_length_m=length,vessel_length_m=length+2*family['axial_gap_per_end_m'],
        axial_gap_per_end_m=family['axial_gap_per_end_m'],
        vessel_outer_radius_m=a+t+POLICY['outer_gap_scale']*(a-rv),
        central_field_T=b0,J_A_mm2=pack_current(a,b,length,b0)/1e6,
        stored_energy_J=u,cold_volume_m3=v,energy_density_J_m3=u/v,
        energy_density_relative_residual=abs(u/v/density-1))


def validate_sized_winding(w):
    check_field(w['central_field_T'])
    s=w['sizing'];a=s['cold_inner_radius_m'];b=s['cold_outer_radius_m'];rv=s['vessel_inner_radius_m']
    def close(x,y):return math.isclose(x,y,rel_tol=2e-8,abs_tol=1e-9)
    if not close(a,rv*POLICY['inner_radius_scale']+POLICY['inner_radius_offset_m']):raise ValueError('inner gap scaling violated')
    if not close(s['vessel_outer_radius_m'],b+POLICY['outer_gap_scale']*(a-rv)):raise ValueError('outer gap scaling violated')
    if not rv<a<b<s['vessel_outer_radius_m']:raise ValueError('invalid cold/vessel order')
    if not close(w['r_min_m'],a) or not close(w['r_max_m'],a+POLICY['winding_radial_fraction_of_cold_mass']*(b-a)):raise ValueError('winding/cold allocation mismatch')
    if not close(2*w['half_length_m'],s['cold_mass_length_m']):raise ValueError('winding/cold axial mismatch')
    if not close(s['vessel_length_m'],s['cold_mass_length_m']+2*s['axial_gap_per_end_m']):raise ValueError('axial allocation mismatch')
    # Recompute from geometry; never trust the retained energy field alone.
    u=stored_energy(w['r_min_m'],w['r_max_m'],2*w['half_length_m'],w['central_field_T'])
    volume=math.pi*(b*b-a*a)*s['cold_mass_length_m']
    if abs(u/(POLICY['energy_per_cold_volume_J_m3']*volume)-1)>5e-4:raise ValueError('energy/cold-volume scaling violated')
    return u


def main():
    rows=[];windings=[]
    for f in POLICY['families']:
        row=solve(f)
        energies=[stored_energy(row['cold_inner_radius_m'],row['winding_outer_radius_m'],row['cold_mass_length_m'],row['central_field_T'],n,4*n) for n in (24,48,96)]
        row['refinement_orders_r_phi']=[[24,96],[48,192],[96,384]]
        row['refinement_energy_J']=energies
        row['relative_refinement']=abs(energies[2]/energies[1]-1)
        if row['relative_refinement']>5e-4:raise ValueError('energy quadrature not converged')
        rows.append(row)
        w=dict(id=f['id'],applies_to_main_solenoid=f['candidates'],r_min_m=row['cold_inner_radius_m'],r_max_m=row['winding_outer_radius_m'],half_length_m=f['cold_mass_length_m']/2,central_field_T=f['central_field_T'],sizing=row,rationale='Review-directed energy/volume and vessel scaling; vacuum-only conditional closure; axial end allowances provisional.')
        validate_sized_winding(w);windings.append(w)
    out=ROOT/'tools/magnetic_study/windings.json'
    out.write_text(json.dumps(dict(status='PROTOTYPE; homogeneous finite windings; review-directed scaling in vacuum',basis='docs/design/inputs/DES-004-magnet-sizing-review.md',windings=windings),indent=2)+'\n')
    paths=[POLICY_PATH,Path(__file__),Path(__file__).with_name('solenoid.py'),out]
    report=dict(status='PROTOTYPE; vacuum all-space energy, conditional engineering sizing',results=rows,command=sys.argv,commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],text=True).strip()),versions=dict(python=sys.version,numpy=np.__version__),random_seed=None,hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},tolerances=dict(energy_relative_refinement=5e-4,energy_volume_root=1e-8),limitations=['RCM interpreted as RCMi; confirmation pending.','Cold-mass axial length equals winding length; end allowances are unengineered hypotheses.','Energy includes the complete field of the vacuum winding; no nonlinear steel, toroids or coupling.','MAG-02/04/05 reuse conditional main-coil sizing, not complete-system energy certification.','5 T central cap does not certify peak conductor field/current margin.'])
    (ROOT/'docs/validation/DES-004-magnet-sizing.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(rows,indent=2))


if __name__=='__main__':main()
