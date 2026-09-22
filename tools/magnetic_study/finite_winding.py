"""PROTOTYPE homogeneous azimuthal winding-pack current in vacuum.

SI units: m, T, A/m^2; J is averaged over the winding pack, not the strand.
Integrates Biot-Savart in radius, z and azimuth. No iron or structural model.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np
from solenoid import MU0, Solenoid, sha


class FiniteWinding:
    def __init__(self, r_min, r_max, half_length, central_field=3.,
                 nr=8, nz=96, nphi=128, guard=.12):
        if not all(math.isfinite(v) for v in (r_min, r_max, half_length, central_field, guard)):
            raise ValueError('parameters must be finite')
        if not 0 < r_min < r_max or half_length <= 0 or guard < 0:
            raise ValueError('invalid winding dimensions or guard')
        if any(isinstance(n, bool) or not isinstance(n, int) for n in (nr, nz, nphi)):
            raise ValueError('quadrature orders must be integers')
        if nr < 2 or nz < 2 or nphi < 4:
            raise ValueError('invalid quadrature order')
        self.a, self.b, self.h = r_min, r_max, half_length
        self.b0, self.guard = central_field, guard
        self.j = central_field / (MU0 * half_length *
                 (math.asinh(r_max/half_length)-math.asinh(r_min/half_length)))
        self.ni = self.j * 2 * half_length * (r_max-r_min)
        nodes, weights = np.polynomial.legendre.leggauss(nr)
        radii = (r_min+r_max)/2 + (r_max-r_min)/2*nodes
        weights = (r_max-r_min)/2*weights
        # A slice dr carries d(NI) = J * (2h) * dr, independent of radius.
        # Solenoid is a quadrature kernel, not a separately normalized physical coil.
        self.slices = [Solenoid(float(r), half_length,
                       MU0*self.j*half_length*float(w)/math.hypot(r, half_length),
                       nz, nphi, guard=0.) for r, w in zip(radii, weights)]

    def axis(self, z):
        """Closed-form radial AND axial integral, independent of quadrature."""
        if not math.isfinite(z):
            raise ValueError('z must be finite')
        def end(u):
            if u == 0:
                return 0.
            return u * (math.asinh(self.b/abs(u))-math.asinh(self.a/abs(u)))
        return MU0*self.j/2 * (end(z+self.h)-end(z-self.h))

    def field(self, r, z):
        if not math.isfinite(r) or not math.isfinite(z) or r < 0:
            raise ValueError('r,z must be finite and r nonnegative')
        distance = math.hypot(max(self.a-r, r-self.b, 0.), max(abs(z)-self.h, 0.))
        if distance <= self.guard:
            raise ValueError('point inside or too near winding pack for this quadrature')
        return sum((s.field(r, z) for s in self.slices), np.zeros(2))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', default='tools/magnetic_study/windings.json')
    p.add_argument('--output', default='docs/validation/DES-004-finite-winding-benchmark.json')
    p.add_argument('--figures', default='docs/design/figures')
    args = p.parse_args()
    config = json.loads(Path(args.config).read_text())
    old_path = Path('tools/magnetic_study/candidates.json')
    old = {c['id']: c for c in json.loads(old_path.read_text())['vacuum_controls']}
    quadrature = {'coarse': [4,48,64], 'nominal': [8,96,128], 'fine': [16,192,256]}
    rows = []
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['svg.hashsalt'] = 'nodd-finite-winding'
    fig, axes = plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for ax, c in zip(axes, config['windings']):
        models = {key: FiniteWinding(c['r_min_m'], c['r_max_m'], c['half_length_m'],
                  c['central_field_T'], *order) for key, order in quadrature.items()}
        model = models['nominal']
        sheet = old[c['id']]
        historical = Solenoid(sheet['radius_m'], sheet['half_length_m'], sheet['central_field_T'],192,256)
        checks = []
        for r,z in [(0.,0.),(0.,3.15),(.5,1.),(1.14,3.15),(3.,4.),(6.,8.)]:
            value, fine = model.field(r,z), models['fine'].field(r,z)
            tolerance = float(1e-6+1e-5*np.linalg.norm(fine))
            error = float(np.linalg.norm(value-fine))
            axis_error = abs(float(value[1])-model.axis(z)) if r == 0 else None
            checks.append({'r_m':r, 'z_m':z, 'Br_T':float(value[0]), 'Bz_T':float(value[1]),
                'coarse_to_nominal_T':float(np.linalg.norm(models['coarse'].field(r,z)-value)),
                'nominal_to_fine_T':error, 'screening_tolerance_T':tolerance,
                'axis_error_T':axis_error,
                'delta_from_historical_sheet_T':(value-historical.field(r,z)).tolist(),
                'passed':error < tolerance and (axis_error is None or axis_error < 1e-10)})
        z_values = np.linspace(-14,14,281)  # display samples, not a map or an acceptance test
        ax.plot(z_values,[model.axis(float(z)) for z in z_values],label='Finite winding, uniform J')
        ax.plot(z_values,historical.axis(z_values),'--',label='Historical thin sheet')
        ax.set(title=c['id']+' vacuum control',xlabel='z [m]',ylabel='Bz(0,z) [T]',ylim=(-.05,3.15))
        ax.grid(alpha=.25); ax.legend(fontsize=8)
        rows.append({'winding':c, 'J_A_per_mm2':model.j/1e6, 'NI_A_turn':model.ni,
                     'checks':checks, 'passed':all(check['passed'] for check in checks)})
    fig.suptitle('PROTOTYPE: finite homogeneous winding packs; no iron or engineering validation')
    out = Path(args.figures); out.mkdir(parents=True, exist_ok=True)
    for ext in ('png','svg'):
        path=out/('DES-004-finite-winding-axis.'+ext)
        fig.savefig(path,dpi=140,metadata={'Date':None} if ext=='svg' else None)
        if ext=='svg': path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    plt.close(fig)
    report = {'status':'PROTOTYPE; homogeneous finite windings in vacuum; no physical field ranking',
        'command':sys.argv, 'commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'working_tree_dirty':bool(subprocess.check_output(['git','status','--porcelain'],text=True).strip()),
        'input_sha256':{str(path):sha(path) for path in (Path(args.config),old_path,Path(__file__),Path(__file__).with_name('solenoid.py'))},
        'versions':{'python':sys.version,'numpy':np.__version__,'matplotlib':matplotlib.__version__},
        'random_seed':None, 'randomness':'none', 'quadrature_r_z_phi':quadrature,
        'tolerances':{'point_convergence':'1e-6 T + 1e-5 norm(B_fine)','axis_absolute_T':1e-10},
        'excluded_domain':'Within winding pack or <=0.12 m from its rectangular r-z cross-section; numerical guard, not physical clearance.',
        'limitations':['J is a homogeneous winding-pack average, not strand current density.',
            'Different constant J per control enforces +3 T at the origin in vacuum only.',
            'No iron, toroid field, turn discreteness, leads, structural or quench calculation.',
            'Sampled checks and analytic axis curves do not establish a validated transport map.'],
        'results':rows}
    Path(args.output).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps([{key:row[key] for key in ('J_A_per_mm2','NI_A_turn','passed')} for row in rows]))
    return 0 if all(row['passed'] for row in rows) else 1


if __name__ == '__main__':
    raise SystemExit(main())
