#!/usr/bin/env python3
"""PROTOTYPE mean-loss transport and three-station muon-spectrometer sizing.

This is a straight, ordinary barrel-ray estimate; no efficiency or full simulation.
PDG total stopping powers are interpolated in log kinetic energy. Highland's
log correction is applied once to the whole upstream material, never per step.
"""
import argparse
import bisect
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/validation/MUON-001'
MASS = 0.10565839
C = 0.299792458


def interpolate(rows, kinetic):
    xs = [r[0] for r in rows]
    i = max(0, min(len(rows)-2, bisect.bisect_right(xs, kinetic)-1))
    f = (math.log(max(kinetic, xs[0]))-math.log(xs[i])) / math.log(xs[i+1]/xs[i])
    return rows[i][1] + f*(rows[i+1][1]-rows[i][1])


def slabs():
    # FACT: ECAL constituent columns from DES031 native eta0 phi0.03 ray.
    # INFERENCE: material families homogenized within each calorimeter slab.
    # Low-column G10/electronics use Al stopping; organics use polystyrene.
    ecal = {'tungsten': 91.2410554/10*17.8,
            'copper': 150.9319143/10*8.96,
            'aluminum': 29.2131449/10*2.699 + 71.7923041/10*1.7,
            'silicon': 24.0108041/10*2.33,
            'polystyrene': 2.4010804/10*(1.2+1.42)}
    hcal = {'iron': 1080.4861823/10*7.85,
            'copper': 108.6188748/10*8.96,
            'aluminum': 36.3663636/10*2.7 + 37.2467598/10*1.7 + 1.5006753/10*2.0889,
            'polystyrene': (94.6425860/10*1.06 + 6.2027910/10*1.4 +
                             4.3769695/10*1.42 + .0500225/10*1.2 + .2000900/10*2.21)}
    # About 69.8 X0 for HCAL; mass-X0 approximation for minor materials.
    hx0 = (hcal['iron']/13.84 + hcal['copper']/12.86 +
           36.3663636/10*2.7/24.01 + 37.2467598/10*1.7/33 +
           1.5006753/10*2.0889/24.01 + hcal['polystyrene']/43.79)
    return [dict(name='solenoid', front_m=1.24, back_m=1.56, x0=1.40211,
                 column_g_cm2={'aluminum': 1.40211*24.01}),
            dict(name='ECAL', front_m=1.7, back_m=2.2332, x0=34.777095,
                 column_g_cm2=ecal),
            dict(name='HCAL', front_m=2.6, back_m=4.158, x0=hx0,
                 column_g_cm2=hcal)]


def transport(pin, tables, scale=1., steps=400, first_station=5.):
    kinetic = math.hypot(pin, MASS)-MASS
    initial = kinetic
    angular_var = position_var = 0.
    budgets = slabs()
    total_x0 = sum(s['x0'] for s in budgets)*scale
    factor = (1+.038*math.log(total_x0))**2
    losses = {}
    for slab in budgets:
        start = kinetic
        for i in range(steps):
            loss = sum(col*interpolate(tables[m]['kinetic_GeV_and_stopping_GeV_cm2_g'], kinetic)
                       for m, col in slab['column_g_cm2'].items())*scale/steps
            mid = kinetic-loss/2
            if mid < .01:
                return dict(p_in_GeV=pin, stopped=True)
            energy = mid+MASS
            p2 = energy*energy-MASS*MASS
            beta2 = p2/(energy*energy)
            dv = .0136**2 * slab['x0']*scale/steps/(p2*beta2)*factor
            r = slab['front_m']+(slab['back_m']-slab['front_m'])*(i+.5)/steps
            angular_var += dv
            position_var += dv*(first_station-r)**2
            kinetic -= loss
        losses[slab['name']] = start-kinetic
    pout = math.sqrt(kinetic*(kinetic+2*MASS))
    return dict(p_in_GeV=pin, p_out_GeV=pout, stopped=False,
                mean_energy_loss_GeV=initial-kinetic, loss_by_system_GeV=losses,
                projected_theta_rms_mrad=1000*math.sqrt(angular_var),
                projected_position_rms_at_5m_mm=1000*math.sqrt(position_var),
                upstream_scatter_over_2p5Tm_bend=math.sqrt(angular_var)*pout/(C*2.5))


def spectrometer(p, field, length=5., sigma=180e-6, tms=1.3):
    sigma_s = math.sqrt(1.5)*sigma
    meas = 8*sigma_s*p/(C*field*length**2)
    theta_p = .0136*math.sqrt(tms)*(1+.038*math.log(tms))
    # Uniform material over L. PDG sagitta RMS = L*theta0/(4 sqrt(3)).
    ms = 2*theta_p/(math.sqrt(3)*C*field*length)
    return dict(measurement_fraction=meas, internal_scattering_fraction=ms,
                quadrature_fraction=math.hypot(meas, ms))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plot', action='store_true')
    args = parser.parse_args()
    tables = json.loads((OUT/'pdg-tables.json').read_text())
    values = [3, 4, 5, 7, 10, 20, 50, 100]
    rows = [transport(p,tables) for p in values]
    lo, hi = 1., 5.
    for _ in range(35):
        mid = (lo+hi)/2
        if transport(mid,tables)['stopped']: lo = mid
        else: hi = mid
    # Meaningful controls: step convergence, field scaling, analytic constant-p limit.
    fine = transport(5,tables,steps=800)
    assert abs(fine['p_out_GeV']-rows[2]['p_out_GeV']) < .001
    assert abs(fine['projected_theta_rms_mrad']/rows[2]['projected_theta_rms_mrad']-1)<.001
    a,b = spectrometer(100,.5),spectrometer(100,1.)
    assert abs(a['measurement_fraction']/b['measurement_fraction']-2)<1e-12
    assert abs(a['internal_scattering_fraction']/b['internal_scattering_fraction']-2)<1e-12
    t = sum(s['x0'] for s in slabs())
    q = .0136*math.sqrt(t)*(1+.038*math.log(t))
    high = transport(100,tables)
    assert abs(high['projected_theta_rms_mrad']*100/1000/q-1)<.05
    result = dict(status='DRAFT / PROTOTYPE; mean transport, no efficiency prediction',
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  slabs=slabs(), total_upstream_x0=t, upstream_theta_p_GeV=q,
                  central_CSDA_exit_threshold_GeV=hi, barrel_transport=rows,
                  field_cases={str(p):{str(B):spectrometer(p,B) for B in [.2,.5,1.,2.]}
                               for p in [5,10,50,100,1000]},
                  crossover_local_p_GeV=spectrometer(1,1)['internal_scattering_fraction']/spectrometer(1,1)['measurement_fraction'],
                  field_for_5percent_upstream_kink_comparison_T=q/(C*5*.05),
                  checks='Step convergence <0.1%; both terms scale as 1/B; high-p Highland limit <5%: PASS')
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print('total X0',round(t,2),'theta*p',round(q,4),'CSDA exit p',round(hi,3))
    for row in rows: print(row)
    if args.plot:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,axes = plt.subplots(1,2,figsize=(11,4.3),layout='constrained')
        grid=[3+47*i/200 for i in range(201)]
        scan=[transport(p,tables,steps=100) for p in grid]
        axes[0].plot(grid,[r['projected_theta_rms_mrad'] for r in scan],lw=2,color='#0072B2')
        axes[0].set(xlabel='Momentum at IP [GeV]',ylabel='Projected calorimeter + coil scattering [mrad]',yscale='log',ylim=(2,150),title='LAYOUT-001 + HCAL: ordinary central path')
        axes[0].axvspan(3,5,color='#E69F00',alpha=.15)
        axes[0].axvline(10,color='#009E73',ls='--',alpha=.6)
        axes[0].text(11,80,'5 GeV practical starting point\n10 GeV more robust matching',fontsize=9)
        ps=[5*10**(3*i/200) for i in range(201)]
        for B,color in [(.5,'#0072B2'),(1.,'#D55E00')]:
            m=[spectrometer(p,B) for p in ps]
            axes[1].loglog(ps,[100*v['measurement_fraction'] for v in m],color=color,label=f'Measurement, B={B:g} T')
            axes[1].axhline(100*m[0]['internal_scattering_fraction'],color=color,ls='--',label=f'Internal MS, B={B:g} T')
        axes[1].set(xlabel='Local momentum in muon system [GeV]',ylabel='Momentum resolution component [%]',xlim=(5,1000),ylim=(.1,100),title='Three stations, 5 m span, 180 μm per station')
        axes[1].legend(fontsize=8,loc='upper left')
        axes[1].text(6,.14,'Internal material: illustrative uniform 1.3 X₀\nCrossover ≈51 GeV for either field',fontsize=8)
        for ax in axes: ax.grid(alpha=.18,which='both')
        fig.suptitle('PROTOTYPE estimates; material and chamber geometry remain assumptions',fontsize=11)
        fig.savefig(OUT/'muon-reach-field.png',dpi=180)
        fig.savefig(OUT/'muon-reach-field.svg')


if __name__ == '__main__': main()
