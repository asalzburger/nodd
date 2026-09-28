"""PROTOTYPE: vacuum current-sheet diagnostics; no detector/iron field model.

Coordinates and lengths: metres; field: tesla; NI: ampere-turns.
Positive azimuthal current gives positive Bz at the origin.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import numpy as np

MU0 = 4e-7 * math.pi  # diagnostic classical approximation; uncertainty immaterial here

class Solenoid:
    def __init__(self, radius, half_length, central_field=3., nz=96, nphi=128, guard=.12):
        if not all(math.isfinite(v) for v in (radius, half_length, central_field, guard)):
            raise ValueError('parameters must be finite')
        if radius <= 0 or half_length <= 0 or guard < 0 or nz < 2 or nphi < 4:
            raise ValueError('invalid dimensions, guard or quadrature')
        self.radius, self.half_length, self.b0 = radius, half_length, central_field
        self.guard, self.nz, self.nphi = guard, nz, nphi
        self.ni = 2 * central_field * math.hypot(radius, half_length) / MU0
        nodes, weights = np.polynomial.legendre.leggauss(nz)
        self.zs = half_length * nodes[:, None]
        self.weights = weights[:, None] * half_length
        self.cos = np.cos(2 * np.pi * np.arange(nphi)[None, :] / nphi)

    def axis(self, z):
        z = np.asarray(z, dtype=float)
        a, h = self.radius, self.half_length
        return MU0 * self.ni / (4*h) * ((z+h)/np.hypot(a,z+h)-(z-h)/np.hypot(a,z-h))

    def field(self, r, z):
        """Return Br,Bz using independent z-Gauss / azimuthal periodic quadrature.

        Raise outside mathematical domain or within guard of ideal sheet/edge;
        no extrapolation, saturation correction or hidden clipping.
        """
        if not math.isfinite(r) or not math.isfinite(z) or r < 0:
            raise ValueError('r,z must be finite and r nonnegative')
        if math.hypot(r-self.radius, max(abs(z)-self.half_length, 0)) <= self.guard:
            raise ValueError('point excluded near ideal current sheet')
        a, h = self.radius, self.half_length
        dz = z - self.zs
        d2 = r*r + a*a - 2*r*a*self.cos + dz*dz
        weight = self.weights / d2**1.5
        scale = MU0*self.ni / (4*np.pi*2*h) * (2*np.pi/self.nphi)
        return np.array([scale*np.sum(weight*a*self.cos*dz),
                         scale*np.sum(weight*(a*a-a*r*self.cos))])


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', default='tools/magnetic_study/candidates.json')
    p.add_argument('--output', default='docs/validation/DES-004-solenoid-benchmark.json')
    p.add_argument('--figures', default='docs/design/figures')
    args=p.parse_args()
    config=json.loads(Path(args.config).read_text())
    results=[]
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    for c in config['vacuum_controls']:
        coarse=Solenoid(c['radius_m'],c['half_length_m'],c['central_field_T'],48,64)
        model=Solenoid(c['radius_m'],c['half_length_m'],c['central_field_T'])
        fine=Solenoid(c['radius_m'],c['half_length_m'],c['central_field_T'],192,256)
        points=[(0.,0.),(0.,3.15),(.5,1.),(1.14,3.15),(3.,4.),(6.,8.)]
        checks=[]
        for r,z in points:
            val=model.field(r,z); ref=fine.field(r,z)
            checks.append({'r_m':r,'z_m':z,'Br_T':float(val[0]),'Bz_T':float(val[1]),
                'coarse_to_nominal_T':float(np.linalg.norm(coarse.field(r,z)-val)),
                'nominal_to_fine_T':float(np.linalg.norm(val-ref)),
                'screening_tolerance_T':float(1e-6+1e-5*np.linalg.norm(ref)),
                'axis_error_T':float(abs(val[1]-model.axis(z))) if r==0 else None})
        # Test fixtures, not a physical field accuracy requirement.
        passed=all(v['nominal_to_fine_T'] < v['screening_tolerance_T'] and
                   (v['axis_error_T'] is None or v['axis_error_T'] < 1e-10) for v in checks)
        rs=np.linspace(0,8,65); zs=np.linspace(-14,14,113)
        br=np.full((len(rs),len(zs)),np.nan); bz=br.copy()
        for i,r in enumerate(rs):
            for j,z in enumerate(zs):
                try: br[i,j],bz[i,j]=model.field(float(r),float(z))
                except ValueError: pass
        # Atlas grid is more demanding near the sheet: independently check each
        # unmasked grid point at doubled resolution and retain a visible mask.
        max_delta=0.; masked=0
        for i,r in enumerate(rs):
            for j,z in enumerate(zs):
                if np.isnan(br[i,j]): continue
                reference=fine.field(float(r),float(z))
                delta=float(np.linalg.norm(np.array([br[i,j],bz[i,j]])-reference))
                max_delta=max(max_delta,delta)
                if delta > 1e-6 + 1e-5*np.linalg.norm(reference):
                    br[i,j]=bz[i,j]=np.nan; masked+=1
        fig,axes=plt.subplots(2,1,figsize=(11,7),sharex=True,layout='constrained')
        for ax,field,label in zip(axes,[bz,br],['Bz [T]','Br [T]']):
            im=ax.pcolormesh(zs,rs,field,vmin=-3,vmax=3,cmap='RdBu_r',shading='auto')
            ax.plot([-model.half_length,model.half_length],[model.radius]*2,'k-',lw=2,label='ideal current sheet')
            ax.plot([-3.15,-3.15,3.15,3.15],[0,1.14,1.14,0],'k--',lw=1,label='tracker host')
            ax.set_ylabel('r [m]'); fig.colorbar(im,ax=ax,label=label,extend='both')
        axes[0].legend(loc='upper right'); axes[-1].set_xlabel('z [m]')
        fig.suptitle(c['id']+' vacuum control — PROTOTYPE\n3 T normalization; no iron, material or performance model')
        out=Path(args.figures); out.mkdir(parents=True,exist_ok=True)
        for ext in ('png','svg'): fig.savefig(out/('DES-004-'+c['id'].lower()+'-field.'+ext),dpi=140)
        plt.close(fig)
        results.append({'candidate':c,'NI_A_turn':model.ni,'checks':checks,'passed':passed,
            'atlas':{'r_range_m':[0,8],'z_range_m':[-14,14],'grid':[65,113],
                     'near_sheet_guard_m':model.guard,'additional_convergence_mask_count':masked,
                     'maximum_unmasked_before_convergence_cut_delta_T':max_delta,
                     'convergence_cut':'1e-6 T + 1e-5 * norm(B_fine)'}})
    report={'status':'PROTOTYPE numerical benchmark; no physical architecture ranking',
        'command':sys.argv,'commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'working_tree_dirty':bool(subprocess.check_output(['git','status','--porcelain'],text=True).strip()),
        'config_sha256':sha(args.config),'script_sha256':sha(__file__),
        'versions':{'python':sys.version,'numpy':np.__version__,'matplotlib':matplotlib.__version__},
        'seed':None,'randomness':'none','quadrature':{'coarse':[48,64],'nominal':[96,128],'fine':[192,256]},
        'tolerances':{'point_convergence':'1e-6 T + 1e-5 * norm(B_fine)','axis_absolute_T':1e-10},'results':results}
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':all(r['passed'] for r in results),'candidates':[r['candidate']['id'] for r in results]}))
    return 0 if all(r['passed'] for r in results) else 1

if __name__=='__main__': raise SystemExit(main())
