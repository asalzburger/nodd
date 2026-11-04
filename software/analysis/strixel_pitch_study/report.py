#!/usr/bin/env python3
"""Replay the human-readable DES042 numerical report from retained evidence."""
import argparse
import gzip
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]


def ratio(stats):
    value=stats['ratio_to_baseline'];error=stats['ratio_se']
    return 'undefined' if value is None else f'{value:.3f} ± {error:.3f}'


def render(data,services,control=None):
    matrix=[(g['pt_GeV'],c['pitch_v_mm']) for g in data['groups'] for c in g['cases']]
    expected={(pt,p) for pt in (1.,10.,100.) for p in (.5,1.,1.5,2.)}
    if len(matrix)!=12 or set(matrix)!=expected or any(c['events']!=20000 for g in data['groups'] for c in g['cases']):
        raise ValueError('Full numerical report requires twelve20000-event cases')
    power=lambda p,n,f:next(x for x in services['cases'] if x['pitch_v_mm']==p and
                            x['power_normalization']==n and x['channel_dependent_fraction']==f)
    lines=['# DES-042 — Strixel pitch, truth tracking and service savings','',
      '**PROTOTYPE.** The baseline detector is unchanged. This study varies local-v',
      'segmentation from 0.5 to 1/1.5/2 mm at fixed 75 µm fine pitch in both strixel',
      'systems: barrel z and endcap radial direction. EC counts include both ends.','',
      'Per the 2026-10-31 publication instruction, event arrays and compressed/CSV',
      'datasets stay local and ignored. The PR contains plots, compact reports,',
      'provenance and rerun code. See [local artifact inventory](local-artifacts.json).','',
      '## Channel count and single-cell estimate','',
      '| Local-v pitch | Binary σv | Barrel channels | EC channels | Total channels | Reduction |',
      '|---|---:|---:|---:|---:|---:|']
    for p in (.5,1,1.5,2):
        c=power(p,'CMS_PS_comparator',1)
        lines.append(f"| {p:g} mm | {c['sigma_v_um']:.1f} µm | {c['channels']['barrel']:,} | {c['channels']['endcap']:,} | {sum(c['channels'].values()):,} | {100*(1-c['channel_fraction']):.1f}% |")
    lines+=['','Fine single-cell σu stays 21.65 µm. These pitch/√12 numbers are analytical',
      'controls. The native geometric digitizer clusters multiple cells, so its',
      'actual centroid response and covariance need not have single-cell widths.','',
      '## Native tracking sample and controls','',
      'PR104 balanced DD4hep → ACTS geometry, unchanged role-transported effective',
      'material map, constant 3 T field, one origin muon/event, random charge,',
      'uniform eta [-4,4], full phi, pT 1/10/100 GeV. Each pitch/momentum case has',
      '20,000 generated events: **240,000 events across twelve cases**. This is',
      'Fatras plus native geometric digitization and a truth-associated Kalman fit.',
      'It uses pitch-derived clustered covariance with no old 0.5 mm calibration.',
      'Truth association/seeds exclude pattern-recognition and occupancy tests.','',
      'All four variants at each momentum have identical generated truth and exact',
      'all/primary simulated-hit payload hashes. Balanced sensitive inventory is',
      '6,794 pixel barrel, 2,808 per pixel endcap, 8,064 strixel barrel, 4,320',
      'strixel endcap, 13,968 long-strip barrel faces and 7,488 endcap faces.',
      'Geometry/material comparisons pass for every native case.','',
      '| pT [GeV] | Pitch [mm] | Finite fits / generated | Native matched / generated | Finite fits failing 5×5 covariance checks | Wrong charge / finite fits |',
      '|---:|---:|---:|---:|---:|---:|']
    for group in data['groups']:
        for case in group['cases']:
            c=case['global']['counts']
            lines.append(f"| {group['pt_GeV']:g} | {case['pitch_v_mm']:g} | {c['finite_fit']:,}/{c['generated']:,} | {c['native_matched']:,}/{c['generated']:,} | {c['finite_fit']-c['valid_covariance']} | {c['wrong_charge']:,}/{c['finite_fit']:,} |")
    lines+=['','The covariance column counts finite fits lacking a valid covariance; native',
      'audit counters and all failure flags remain in the retained event data.','',
      '## Measured track-resolution ratios','',
      'Central 68.27% half-width relative to the newly run 0.5 mm control;',
      '1 means unchanged. Values below are conditional on finite fits in each',
      'variant, with paired generated-event bootstrap standard errors (400 draws).',
      'No residual/tail cuts are applied. Full SD/RMS, bias and pull diagnostics',
      'remain in the CSV/JSON. The separately plotted common-success ratios test',
      'survivor effects. Errors are statistical only.','',
      '| pT [GeV] | Absolute eta region | Pitch [mm] | z0 ratio | theta ratio | Relative-pT ratio |',
      '|---:|---|---:|---:|---:|---:|']
    for group in data['groups']:
        for case in group['cases'][1:]:
            for region in case['summary_regions']:
                q=region['quantities']
                label=f"{region['low']:g}–{region['high']:g}"
                lines.append(f"| {group['pt_GeV']:g} | {label} | {case['pitch_v_mm']:g} | {ratio(q['z0']['residual'])} | {ratio(q['theta']['residual'])} | {ratio(q['pt_relative']['residual'])} |")
    high=next(g for g in data['groups'] if g['pt_GeV']==100)
    central=[next(r for r in c['summary_regions'] if r['low']==0 and r['high']==1) for c in high['cases']]
    fit_statement=('Every generated event in this region fits at every pitch, so survivor changes do not explain it.'
                   if all(r['counts']['finite_fit']==r['counts']['generated'] for r in central)
                   else 'Consult the common-success comparison and all-generated fractions for survivor effects.')
    lines+=['','### High-momentum response diagnostic','',
      'At 100 GeV and |eta|<1, the native digital z0/theta core becomes narrower',
      'with coarser cells. '+fit_statement, 'The',
      'uncut standard deviation changes less than the central width, and pull',
      'standard deviations are well below one. This is an uncalibrated response',
      'and fit-weighting sensitivity, not evidence that larger physical cells',
      'improve a detector. The causal response assumption remains unqualified.','',
      'With the configured digital flag and merging enabled, the native merge',
      'stage recomputes path-weighted cell centroids and both coordinate variances.',
      'Both variances contain the same two-dimensional cell-weight concentration',
      'factor. Coarsening local-v therefore also changes the reported fine-u',
      'covariance. Source inspection and a small measurement-writing pilot verify',
      'this coupling; they do not isolate the entire high-pT mechanism. See',
      '[response-diagnostic.json](response-diagnostic.json) for source hashes.','',
      '| Pitch [mm] | z0 width68 [µm] | z0 uncut SD [µm] | z0 pull SD | theta width68 [µrad] | theta uncut SD [µrad] | theta pull SD |',
      '|---:|---:|---:|---:|---:|---:|---:|']
    for case in high['cases']:
        region=next(r for r in case['summary_regions'] if r['low']==0 and r['high']==1)
        z,t=[region['quantities'][q] for q in ('z0','theta')]
        lines.append(f"| {case['pitch_v_mm']:g} | {z['residual']['width68']*1000:.3f} | {z['residual']['std']*1000:.3f} | {z['pull']['std']:.3f} | {t['residual']['width68']*1e6:.2f} | {t['residual']['std']*1e6:.2f} | {t['pull']['std']:.3f} |")
    lines+=['','At 1/10 GeV, longitudinal summary widths are close to the control.',
      'Momentum-resolution summary changes stay at the percent scale in this',
      'sample. This fixed-material truth-associated scan does not measure any',
      'performance benefit from a hypothetical reduction of service material.','',
      'All six perigee/derived quantities and every signed-eta bin are available in',
      'local, ignored `summary.csv` and `profiles.json.gz`.',
      'Figures: [fit fractions](figures/fit-fractions.png),',
      '[1 GeV ratios](figures/ratio-pt1.png), [10 GeV ratios](figures/ratio-pt10.png),',
      '[100 GeV ratios](figures/ratio-pt100.png). Absolute widths and',
      '`common_ratio-pt*.png` controls are in the same figure directory.','']
    if control is not None:
        if control.get('response_model')!='gaussian_pitch_over_sqrt12_no_merge' or control.get('events_per_case')!=5000:
            raise ValueError('Separate Gaussian-control identity/count differs')
        if len(control['groups'])!=1 or control['groups'][0]['pt_GeV']!=100:
            raise ValueError('Separate control requires only100GeV')
        cases=control['groups'][0]['cases']
        if len(cases)!=4 or {c['pitch_v_mm'] for c in cases}!={.5,1.,1.5,2.} or any(c['events']!=5000 for c in cases):
            raise ValueError('Separate control requires four5000-event pitches')
        if [c['pitch_v_mm'] for c in cases]!=[a['pitch_v_mm'] for a in control['control_audit']]:
            raise ValueError('Control case and native audit pairing differ')
        attempts=', '.join(str(x) for x in sorted({a['native_digitization']['maximum_draw_attempts'] for a in control['control_audit']}))
        lines+=['## Separate Gaussian-response diagnostic','',
          'Four additional 5,000-event cases at 100 GeV use independent input',
          'Gaussian widths equal to nominal pitch/√12 in every measured coordinate,',
          'with merging disabled and one-coordinate long strips. Only the strixel-v',
          'width changes within this control. The generated/transport samples are',
          'paired across pitches. This adds 20,000 processed case-events, distinct',
          'from the 240,000-event native geometric scan.','',
          'All-coordinate response replacement tests the overall model dependence;',
          'it does not identify one causal mechanism or calibrate a physical sensor.',
          f'Native draws near sensor edges are bounded/retried, with at most {attempts}',
          'draw attempts. Retry counts are not exposed; zero lost measurements would not',
          'prove zero retries. Exact stored variance checks and standardized local',
          'residual diagnostics are retained in the control native reports.','',
          '| Pitch [mm] | Finite fits / generated | Native matched / generated | Wrong charge / finite fits | Simulated hits / measurements | Hits without measurement |',
          '|---:|---:|---:|---:|---:|---:|']
        for case,audit in zip(control['groups'][0]['cases'],control['control_audit']):
            c=case['global']['counts']
            lines.append(f"| {case['pitch_v_mm']:g} | {c['finite_fit']:,}/{c['generated']:,} | {c['native_matched']:,}/{c['generated']:,} | {c['wrong_charge']:,}/{c['finite_fit']:,} | {audit['simhits']:,}/{audit['measurements']:,} | {audit['simhits_without_measurement']} |")
        lines+=['','Central |eta|<1 absolute widths and pull checks:','',
          '| Pitch [mm] | z0 width68 [µm] | theta width68 [µrad] | z0 pull SD | theta pull SD | Relative-pT pull SD |',
          '|---:|---:|---:|---:|---:|---:|']
        for case in cases:
            q=next(r for r in case['summary_regions'] if r['low']==0 and r['high']==1)['quantities']
            lines.append(f"| {case['pitch_v_mm']:g} | {q['z0']['residual']['width68']*1000:.3f} | {q['theta']['residual']['width68']*1e6:.2f} | {q['z0']['pull']['std']:.3f} | {q['theta']['pull']['std']:.3f} | {q['pt_relative']['pull']['std']:.3f} |")
        lines+=['','The central longitudinal pulls are much closer to unit width in this',
          'control, while momentum pulls retain substantial tails/nonclosure.',
          'This is a response-model sensitivity, not global fit calibration.']
        lines+=['','| Absolute eta region | Pitch [mm] | z0 ratio | theta ratio | Relative-pT ratio |',
          '|---|---:|---:|---:|---:|']
        for case in control['groups'][0]['cases'][1:]:
            for region in case['summary_regions']:
                q=region['quantities'];label=f"{region['low']:g}–{region['high']:g}"
                lines.append(f"| {label} | {case['pitch_v_mm']:g} | {ratio(q['z0']['residual'])} | {ratio(q['theta']['residual'])} | {ratio(q['pt_relative']['residual'])} |")
        lines+=['','Errors use the same paired-event bootstrap prescription, 400 draws.',
          '[Gaussian ratios](gaussian-control/figures/gaussian-ratio-pt100.png),',
          '[absolute widths](gaussian-control/figures/gaussian-absolute-pt100.png),',
          'The local, ignored `gaussian-control/profiles.json.gz` and',
          '`gaussian-control/summary.csv` retain all six quantities and eta bins.','']
    lines+=[
      '## Conditional power estimate','',
      'The existing DES020/021 proxies are 7.8 W/module and',
      '7.8 × 122,880/30,208 = 31.7288 W/module. The first is a complete CMS PS',
      'service-load comparator; the second is its deliberately crude channel-density',
      'scaling. **They are sensitivity normalizations, not physical bounds or',
      'measurements of a compatible strixel ASIC.** Longer cells change capacitance',
      'and do not guarantee equal power/channel.','',
      'Let f be the channel-dependent fraction of that load. The study assumes',
      '`P(p)=P(0.5)[(1-f)+f×0.5/p]`. It keeps 2 W/module HV leakage (24.768 kW)',
      'and 5 W/network boards (3.600 kW) fixed, and recomputes local 12 V rail I²R',
      'loss. HV leakage is not added to LV current. External cable/converter losses',
      'are unknown. The two baseline heat-load proxies are 125.354 and 427.772 kW.','',
      '| Pitch | Electronics saving, f=1 [kW] | Heat saving including local rail loss, f=1 [kW] | Heat saving, f=0.5 [kW] |',
      '|---|---:|---:|---:|']
    for p in (1,1.5,2):
        lo,hi=[power(p,n,1) for n in ('CMS_PS_comparator','channel_density_proxy')]
        half=[power(p,n,.5)['saved_heat_kW'] for n in ('CMS_PS_comparator','channel_density_proxy')]
        lines.append(f"| {p:g} mm | {lo['saved_electronics_kW']:.1f}–{hi['saved_electronics_kW']:.1f} | {lo['saved_heat_kW']:.1f}–{hi['saved_heat_kW']:.1f} | {half[0]:.1f}–{half[1]:.1f} |")
    lines+=['','If f=0, the modeled power saving is zero. These spans compare assumptions;',
      'they are not confidence intervals. Reduced heat does not establish smaller',
      'cooling pipes or a qualified thermal/hydraulic operating point.','',
      '## Conditional cable-space estimate','',
      'The existing 13.4 mm power + 3.6 mm fibre benchmark gives 1,584 sets across',
      'both ends: 516.155 L gross power envelope and 37.254 L fibre envelope in',
      'collectors/fans and downstream transport. Local buses/module flexes are',
      'excluded from these volumes. Keeping the hardware unchanged recovers',
      '**zero installed cable, cooling, tray or electronics-footprint space**.','',
      'A separate redesigned-harness hypothesis keeps the 13.4 mm benchmark OD',
      'but assigns capacity equal to twelve baseline module loads, rounds within',
      'each half-stave/petal including its 5 W board, and keeps fibres and cooling',
      'fixed. Source cables have twelve independent LV and twelve HV circuits:',
      '**the assumed reaggregation requires new conductors, fanouts, connectors and',
      'HV/control topology. Aggregate power arithmetic does not qualify that cable.**','',
      '| Pitch | Power bundles, B / EC per network (f=1) | Gross power envelope removed, both ends | Effective Cu / PI / internal void removed | Worst-sector area-equivalent radial saving |',
      '|---|---:|---:|---:|---:|']
    for p in (1,1.5,2):
        c=power(p,'CMS_PS_comparator',1);m=c['saved_effective_material_L']
        lines.append(f"| {p:g} mm | {c['power_harnesses']['barrel']//576} / {c['power_harnesses']['endcap']//144} | {c['saved_power_envelope_L']:.1f} L | {m['Copper']:.1f} / {m['Polyimide']:.1f} / {m['internal_void_air']:.1f} L | {c['saved_worst_sector_equivalent_width_mm']:.1f} mm |")
    lines+=['','The Cu/PI/air entries use the existing effective 20%/30%/50% recipe, not',
      'qualified electrical gauges. With f=0.5 all alternatives remove 242.7 L under',
      'this same redesign hypothesis; with f=0 none do. The 1.5 and 2 mm f=1 cases',
      'have equal cable-space benefit because bundle counts are discrete.','',
      'The fixed 56 pipe pairs/end and fibres give worst-sector area-equivalent',
      'widths 75.590 mm baseline, 46.717 mm for 1/2 bundles per B/EC network,',
      'and 41.000 mm for 1/1. These exact annular inversions use r=710 mm, 75%',
      'azimuth and 50% packing, excluding walls/bends/connectors. They are routing',
      'capacity screens, not proven narrower envelopes. Baseline native worst-sector',
      'demand already exceeds the inherited 73 mm corridor packing budget.','',
      'Relative to the actual 73 mm allocation, the redesigned area-only demands',
      'leave approximately 26.3 or 32.0 mm before wall/bend/connector reserves;',
      'the larger equivalent savings in the table are relative to the baseline',
      '75.590 mm demand, including its existing overcommitment.','',
      'If bundle outer diameters stay fixed, an alternative conductor-only scaling',
      'could remove material but recovers zero external space; fixed HV/control',
      'copper is unknown. Do not scale fibre traffic with channel count at fixed',
      'particle flux. [Service tradeoff figure](figures/services-tradeoff.png).','',
      '## Reproduction, provenance and review','',
      'Commands and dependency/build arguments are in the',
      '[repeatable workflow](../../../software/analysis/strixel_pitch_study/README.md).',
      'Offline replay uses compact all-event NPZ arrays, native reports and exact',
      'configuration/content hashes. Raw ROOT and full covariance remain in ignored',
      'native output directories. Every stored residual/pull/flag was recomputed',
      'from full truth/fitted/covariance arrays before compact retention.','',
      'Production ran the corrected source at',
      '`8b7c147b3b0da4bd40dcd9ad06c98abcb2de58f9`. Native report preparation omitted',
      'the imported metrics.py fingerprint; a separate launch/completion blob/hash',
      'check and exact observable replay close this stated provenance gap. Initial',
      'v1/v2 pilots had incorrect residual-sign metadata; v3 production and all',
      'retained observables use fitted−truth consistently.','',
      'Scientific assumptions and service arithmetic received separate PhysVal and',
      'SysArch assessments. Exact reviewed revisions, subsequent corrections,',
      'executed checks and final evidence assessment are recorded in the',
      '[session journal](../../../logs/codex/SESSION-2026-10-31-strixel-pitch-study.md).',
      'No design sign-off or preferred pitch is inferred from these calculations.','']
    return '\n'.join(lines)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data',type=Path,default=ROOT/'docs/validation/DES-042/profiles.json.gz')
    parser.add_argument('--services',type=Path,default=ROOT/'docs/validation/DES-042/services.json')
    parser.add_argument('--control',type=Path,default=ROOT/'docs/validation/DES-042/gaussian-control/profiles.json.gz')
    parser.add_argument('--output',type=Path,default=ROOT/'docs/validation/DES-042/results.md')
    parser.add_argument('--check',action='store_true',help='Check the retained report without overwriting it')
    args=parser.parse_args()
    data=json.loads(gzip.decompress(args.data.read_bytes()))
    services=json.loads(args.services.read_text())
    control=json.loads(gzip.decompress(args.control.read_bytes())) if args.control.exists() else None
    rendered=render(data,services,control)
    if args.check:
        if args.output.read_text()!=rendered:raise ValueError('Retained report differs from deterministic rendering')
        print('PASS: numerical report replay');return
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(rendered)
    print(args.output)


if __name__=='__main__':main()
