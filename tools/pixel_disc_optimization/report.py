#!/usr/bin/env python3
"""Retain a compact, sourced DES016 review package from the executable study."""
import argparse
import json
from pathlib import Path
import shutil
from study import ROOT,digest
from plots import render


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--audit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    c=json.loads((ROOT/'tools/pixel_disc_optimization/inputs.json').read_text());r=json.loads((a.run/'screening.json').read_text());audit=json.loads((a.audit/'acts-summary.json').read_text());selected=r['selected'];svc=r['services']
    if not selected or not r['all_18_straight_coverage_pass'] or not r['all_18_overlap_body_pass'] or not all(x['passed'] for x in audit.values()):raise ValueError('Failed retained evidence')
    render(c,a.output,json.loads((a.run/'layout.json').read_text()))
    shutil.copyfile(a.run/'screening.json',a.output/'screening.json');shutil.copyfile(a.audit/'acts-summary.json',a.output/'acts.json')
    # Layout is reproducible from inputs + code; do not duplicate 18 scenes.
    summary={'producer_hashes':{str(p.relative_to(ROOT)):digest(p) for p in sorted((ROOT/'tools/pixel_disc_optimization').glob('*.py'))},'files':{p.name:digest(p) for p in a.output.iterdir() if p.is_file()}}
    sensor=selected['sensor'];body=selected['body'];rows=[]
    for s in svc['scenarios']:
        positive=next(x for x in s['end_trunks'] if x['side']=='positive');rows.append(f"| {s['scenario']} | {s['cables_mm2']:.1f} | {s['feed_return_pipe_mm2']:.1f} | {positive['after_disc_8_demand_mm2']:.1f} | {positive['capacity_mm2']:.1f} | {positive['utilization']:.2f} × / {positive['status']} |")
    text=f'''# DES016 — preliminary disc silicon optimization

Status: **DRAFT / isolated PROTOTYPE. Geometric target passes; inherited service packing FAILS.**

[Issue #38](https://github.com/asalzburger/nodd/issues/38#issuecomment-5981583892) requests less silicon overlap with unchanged coverage. The user fixed the limit at 10%. [DES016](../../design/DES-016-pixel-disc-module-optimization.md) defines metric, dimensions and approval boundary. The separate positioning PR retains ownership of changed disc datums.

![Existing and proposed projected silicon](disc-comparison.png)

The selected mixed Cartesian/inner-ring tiling has **328 single-RD53i modules/disc**, retaining the 20 × 19.2 mm active matrix, 50 µm pitch, 0.15 mm sensor, nine discs per end and nominal active annulus **r32.3..181.4550267061104 mm**. Eighteen singles form the inner polar ring; 310 form the Cartesian interior/boundary. The first-disc lattice pitch is 19.55 × 18.75 mm; its0.45 mm pitch reduction scales as615.2/abs(z) on farther discs while retaining the same328 module indices. Five outward z levels with 1.2 mm spacing retain the 1 mm occupied body and ≥0.2 mm z gap wherever physical bodies overlap in x/y. All proposed numbers remain unqualified choices.

| Quantity, per disc | Existing coplanar x/y quad control | Proposed at first-disc nominal IP projection |
| --- | ---: | ---: |
| Modules / chips | 112 / 448 | 328 / 328 |
| Gross silicon Σarea [mm²] | {r['baseline']['sensor']['summed_mm2']:.1f} | {sensor['summed_mm2']:.1f} |
| Repeated area / projected union | {r['baseline']['sensor']['overlap_over_union_percent']:.3f}% | **{sensor['overlap_over_union_percent']:.3f}%** |
| Repeated area / summed installed area | {r['baseline']['sensor']['overlap_over_installed_percent']:.3f}% | {sensor['overlap_over_installed_percent']:.3f}% |
| Annulus-only repeated area / union | {r['baseline']['sensor']['annular_overlap_over_union_percent']:.3f}% | **{sensor['annular_overlap_over_union_percent']:.3f}%** |
| Installed silicon outside nominal annulus [mm²] | {r['baseline']['sensor']['installed_outside_annulus_mm2']:.1f} | {sensor['installed_outside_annulus_mm2']:.1f} |

Overlap is `(Σ individual polygon area − area of union) / area of union`, so triple-covered silicon is counted twice as redundancy. Physical guard silicon counts in the overlap metric; only active matrices count toward active coverage. Nothing is clipped to improve a selection metric. The retained baseline table is a coplanar x/y control; ACTS compares the actual DES014/015 z stagger separately. Baseline active coverage has {r['baseline']['active']['uncovered_annulus_superset_mm2']:.1f} mm² of holes in that control, despite gross sensor-outline coverage.

## Continuous straight coverage and native audit

All nine positive disc datums passed polygon containment certificates for **every on-axis luminous z vertex in [−150,+150] mm**; reflection supplies the negative end. Per-interval intersections of endpoint footprints are contained in every intermediate footprint because each rectangle projects by a monotone homothety. Their union contains a conservative polygon superset of the true circular annulus. First-disc proof uses {len(r['coverage_certificates'][0]['intervals'])} intervals; each retained gap upper bound is zero with a 1e−6 mm² numerical area threshold. Circle discretization gives a 0.0153 mm² conservative area bound, not a weakened coverage target. Transverse displaced vertices and continuous helical coverage are outside this proof.

The placement centre correction uses `D=(z²−150²)/z`, `xy_physical=xy_template×(1+local_z/D)` to balance the two vertex extremes without changing any active matrix dimension. The same chip count/tiling policy is repeated; x/y datums and lattice pitches differ slightly with disc distance. All 18 per-disc sensor and body screens pass; largest envelope radius across the nine distances is {max(d['body']['maximum_radius_mm'] for d in r['per_disc_screens']):.3f} mm. Disc positions retain the original DES015 list including ±615.2 mm first datums; they are not the independent whole-mm amendment.

Native **acts-nodd** constructed all {audit['candidate']['active_patches']} proposed finite sensitive planes and {audit['baseline']['active_patches']} baseline planes, and audited **324 matched tracks each**, using 0/2 T, pT=1 GeV, both charges, all 18 discs and vertices −150/0/+150 mm. Actual ACTS supporting-plane transport, finite RectangleBounds and returned IDs agree with the independently tested analytic oracle: zero mismatches. Candidate missing intended target-disc crossings: **{len(audit['candidate']['tracks_missing_target_disc'])}**; baseline: **{len(audit['baseline']['tracks_missing_target_disc'])}**. Six first-disc control tracks test all 328 planes without the shared voxel broad phase. [Native evidence](acts.json) includes actual binary/source hashes, existing ACTS working-tree changes, residuals and limitations. This is a finite intersection audit; it does not establish global navigation, reconstruction, material response or continuous helix hermeticity.

## Physical envelope and guard sensitivity

First-disc body envelope: **r≤{body['maximum_radius_mm']:.3f} mm**, minimum beam radius {body['minimum_beam_radius_mm']:.3f} mm, local occupied z {body['occupied_local_z_mm'][0]:.1f}..{body['occupied_local_z_mm'][1]:.1f} mm, five levels. The original r188.5 mm support and local service bands cannot be reused. The enlarged radial envelope is a cost of the Cartesian edge overhang; it is explicitly reported rather than hidden in the overlap ratio.

Sensor guard is **0.1 mm per edge**, occupied body **20.4 × 21.4 mm**, with inherited 1.8 mm ASIC periphery directed outward. These slim-edge/assembly choices require detector/module review and prototype evidence. Keeping the inherited **0.5 mm guard gives {r['guard_control_0p5mm']['overlap_over_union_percent']:.3f}% overlap**, failing 10%. The optimized concentric single-chip control has {r['polar_control']['chips']} chips and {r['polar_control']['sensor']['overlap_over_union_percent']:.3f}% overlap, also failing. No fabricated sensor/ASIC qualification or sign-off is asserted.

![Module axial levels](module-levels.svg)

## Cable and cooling envelope estimates

Use the unchanged DES010 scenario inputs and complete module count. New nominal heat is **{svc['nominal_W']:.3f} W/disc**, compared with 1204.224 W for 448 chips (−26.786%). Installed sensor-envelope volume is328×20.2×19.4×0.15={328*(c['active_mm'][0]+2*c['sensor_guard_mm'])*(c['active_mm'][1]+2*c['sensor_guard_mm'])*0.15/1000:.3f} cm³/disc, compared with 27.410 cm³ for the 112 quad outlines. Projected areas in the table differ from physical installed areas because of finite z. Across 18 discs: {18*svc['nominal_W']/1000:.3f} kW. Local row/ring grouping produces **{svc['power_chains']} power chains** (≤16 singles and≤32 chips each), compared with16 old quad chains. The conservative local routing concept has **{svc['local_circuits']} independently fed circuits** (one per row/ring, subdivided above 300 W), versus10 old half-ring loops. The heat-only lower bound is {svc['absolute_heat_only_circuit_lower_bound']} circuits; merging spatial loops is not hydraulic validation.

Local evaporator OD2.8 mm and combined row/ring centreline length **{svc['row_ring_tube_length_without_feeds_mm']:.1f} mm** imply **{svc['local_tube_volume_envelope_mm3']/1000:.3f} cm³/disc** of bounding tube envelope before feeds, returns and bends. The 20 loops have both4 mm OD transport legs, occupying **{svc['scenarios'][0]['feed_return_pipe_mm2']:.1f} mm²** bare feed/return cross-section. Counts and lengths are explicit estimates, not routed or thermal-qualified supports.

Place the trial trunk at **r{svc['trunk_inner_mm']}..{svc['trunk_outer_mm']} mm** after reserving2 mm beyond the enlarged module envelope, within the inherited carrier shell. The area scenarios include the current barrel inventory and eight joined discs; the ninth retains its conditional bypass. Demand multipliers and packing/available-phi factors are applied separately.

| Scenario | Cable [mm²/disc] | Feed+return [mm²/disc] | Positive trunk after8 discs [mm²] | Available packed area [mm²] | Utilization / result |
| --- | ---: | ---: | ---: | ---: | ---: |
'''+'\n'.join(rows)+'''

All inherited trunk scenarios fail. Splitting quads reduces chips and heat but increases physical modules, command/uplink bundles, chain count and boundary overhang. A revised readout aggregation, cooling grouping, collector/last-disc route and carrier/support architecture is required before baseline adoption. The study therefore **does not replace the preliminary DD4hep compact**. Existing thermal failures are not resolved by this geometric result.

## Reproduction and evidence

[Screening](screening.json) retains rejected candidates, guard control, full certificates, counts and source/code hashes. [ACTS](acts.json) retains exact runtime provenance and matched audit summaries. Install `requirements.txt` in an isolated local target or venv; keep that target prepended to the activated ACTS PYTHONPATH, preserving existing runtime paths. See the [tool README](../../../tools/pixel_disc_optimization/README.md). Figures are original nODD drawings generated from the same polygons. No baseline files or historical reports are overwritten; human design approval is still pending.
'''
    (a.output/'results.md').write_text(text)
    summary['files']['results.md']=digest(a.output/'results.md');(a.output/'artifacts.json').write_text(json.dumps(summary,indent=2)+'\n')

if __name__=='__main__':main()
