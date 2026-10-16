#!/usr/bin/env python3
"""PROTOTYPE response to PR86: compact muon span and 500 GeV resolution.

Combine independent curvature variances at a common reference momentum. This
does not transport 500 GeV muons or model a full tracker--muon reconstruction.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import study

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/validation/MUON-001/compact-span'
TRACKER = OUT / 'idres/results.json'


def combine_independent(tracker, muon):
    """Local linear propagation of independent inverse-momentum errors."""
    return tracker * muon / math.hypot(tracker, muon)


def solve_fields(p, span, tracker, target=.10, material=1.3):
    at_one_tesla = study.spectrometer(p, 1., length=span, tms=material)
    coefficient = at_one_tesla['quadrature_fraction']
    standalone = coefficient / target
    # If the tracker alone meets the target, its curvature can be used without
    # a muon momentum measurement. This is not a claim of field-free muon ID.
    combined = (0. if tracker <= target else
                coefficient * math.sqrt(1 / target**2 - 1 / tracker**2))
    return dict(standalone_target_T=standalone,
                ideal_combined_target_T=combined,
                standalone_matches_tracker_T=coefficient/tracker)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plot', action='store_true')
    args = parser.parse_args()
    source = json.loads(TRACKER.read_text())
    nominal = next(r for r in source['runs'] if r['eta']==0 and r['material_scale']==1)
    sample = next(s for s in nominal['samples'] if s['p_GeV']==500)
    tracker = sample['fractional_pt_resolution']
    rows=[]
    for span in [5., 3.]:
        for field in [.2, .5, .8, 1., 1.4]:
            components=study.spectrometer(500., field, length=span)
            rows.append(dict(span_m=span, average_transverse_field_T=field,
                **components, ideal_combined_fraction=combine_independent(
                    tracker, components['quadrature_fraction'])))
    fields={str(span):solve_fields(500., span, tracker) for span in [5.,3.]}
    material_sensitivity=[dict(internal_x0=t, **solve_fields(500.,3.,tracker,material=t))
                          for t in [.5,1.3,5.,10.]]
    # Physical scaling controls at fixed total material and coordinate precision.
    a=study.spectrometer(500.,1.,length=3.)
    b=study.spectrometer(500.,1.,length=5.)
    assert math.isclose(a['measurement_fraction']/b['measurement_fraction'],25/9,rel_tol=1e-12)
    assert math.isclose(a['internal_scattering_fraction']/b['internal_scattering_fraction'],5/3,rel_tol=1e-12)
    for span in [3.,5.]:
        needed=fields[str(span)]['standalone_target_T']
        assert math.isclose(study.spectrometer(500,needed,length=span)['quadrature_fraction'],.10,rel_tol=1e-12)
    assert all(r['ideal_combined_fraction'] < tracker for r in rows)
    # Verify the positive-bound branch, rather than claiming that zero field
    # always meets a combined target with an arbitrary tracker precision.
    harder=solve_fields(500,3.,.15)
    rr=study.spectrometer(500,harder['ideal_combined_target_T'],length=3.)['quadrature_fraction']
    assert math.isclose(combine_independent(.15,rr),.10,rel_tol=1e-12)
    # High-p transport must not silently extrapolate the retained <=100 GeV data.
    tables=json.loads((OUT.parent/'pdg-tables.json').read_text())
    try:
        study.transport(500,tables)
    except ValueError:
        pass
    else:
        raise AssertionError('Unsupported high-energy transport was accepted')
    result=dict(status='DRAFT / PROTOTYPE; central covariance comparison, no full combined fit',
        comment_url='https://github.com/asalzburger/nodd/pull/86#issuecomment-6210895219',
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        spectrometer_script_sha256=hashlib.sha256(Path(study.__file__).read_bytes()).hexdigest(),
        tracker_source_sha256=hashlib.sha256(TRACKER.read_bytes()).hexdigest(),
        common_reference_p_GeV=500.,eta=0.,tracker_field_T=3.,
        tracker_fraction=tracker,
        tracker_independent_gls_fraction=sample['independent_sigma_inverse_pt_GeV_inverse']*sample['pt_GeV'],
        target_combined_fraction=.10,internal_material_x0=1.3,
        effective_station_sigma_um=study.STATION_SIGMA_M*1e6,
        fields_for_target=fields,
        field_preserving_5m_0p5T_measurement_at_3m_T=.5*(5/3)**2,
        material_sensitivity_3m=material_sensitivity,field_cases=rows,
        assumptions=['Independent Gaussian curvature information, linear propagation to fractional momentum error.',
            'Common500GeV reference; mean-loss correction and straggling are omitted, not extrapolated from100GeV stopping tables.',
            'Fixed total uniform1.3X0 within either station span; material density is not held fixed.',
            'Upstream calorimeter/solenoid106X0 is a matching covariance, not an internal standalone sagitta material term.',
            'Independent30um alignment per station; quoted35um fitted chamber coordinate already includes MDT tube information.',
            'Tracker material and effective layers remain the existing proxy; no efficiency, complete field or combined-fit validation.'],
        checks='PASS: span scaling, target roots, combination bounds, positive-field branch and high-energy transport guard')
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print('central500GeV tracker fraction',tracker)
    print('3m target fields',fields['3.0'])
    for row in rows: print(row)
    if args.plot:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
        grid=[.2+1.3*i/200 for i in range(201)]
        for span,color in [(3.,'#0072B2'),(5.,'#D55E00')]:
            mu=[study.spectrometer(500.,field,length=span)['quadrature_fraction'] for field in grid]
            axes[0].plot(grid,[100*r for r in mu],color=color,label=f'{span:g} m span')
            axes[1].plot(grid,[100*combine_independent(tracker,r) for r in mu],color=color,label=f'{span:g} m span')
        axes[0].set(xlabel='Average transverse bending field [T]',ylabel='Standalone resolution component sum [%]',
            title='PROTOTYPE: standalone at local 500 GeV\nATLAS precision; uniform internal 1.3 X₀',ylim=(0,45))
        axes[1].set(xlabel='Average transverse bending field [T]',ylabel='Ideal combined resolution [%]',
            title='Independent tracker + muon curvature proxy\nCommon 500 GeV reference; no loss straggling',ylim=(0,12))
        axes[0].axhline(10,color='#009E73',ls='--',label='10% standalone benchmark')
        axes[0].plot(fields['3.0']['standalone_target_T'],10,'o',color='#0072B2')
        axes[0].annotate('3 m: 0.86 T',xy=(.861,10),xytext=(.92,17),arrowprops=dict(arrowstyle='->'),fontsize=9)
        axes[1].axhline(tracker*100,color='grey',ls=':',label=f'3 T tracker alone: {100*tracker:.2f}%')
        axes[1].axhline(10,color='#009E73',ls='--',label='Requested 10% combined target')
        axes[1].text(.25,.6,'10% combined alone sets no positive field bound\n3 m + 1 T gives ≈5.31% in this ideal comparison',fontsize=9)
        for ax in axes:
            ax.set_xlim(.2,1.5)
            ax.grid(alpha=.2)
            ax.legend(fontsize=8,loc='upper right')
        fig.savefig(OUT/'compact-span.png',dpi=180)
        fig.savefig(OUT/'compact-span.svg')
        svg=OUT/'compact-span.svg'
        svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')


if __name__=='__main__': main()
