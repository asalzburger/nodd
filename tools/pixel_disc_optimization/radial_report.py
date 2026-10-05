#!/usr/bin/env python3
"""Retain revised radial evidence without overwriting the Cartesian control."""
import argparse
import gzip
import json
import math
from pathlib import Path
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon as Patch
import numpy as np

import radial
from study import ROOT, rectangle, digest


def drawings(cfg, out, layout, report):
    source = json.loads(gzip.decompress((ROOT/cfg['baseline']).read_bytes()))
    old = [rectangle(b['center_mm'], b['u'], b['v'], 20.6, 19.8) for b in source['bodies'] if b['layer_id']=='A-pixel-P1']
    new = radial.project(layout['modules'], cfg, cfg['disc_datum_mm'], guard=cfg['sensor_guard_mm'])
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.4), layout='constrained')
    counts = report['selected']
    titles = ['Before: 112 quad modules / 448 chips', f"Revised radial rings: {counts['modules']} modules / {counts['chips']} chips"]
    for ax, polys, title in zip(axes, [old, new], titles):
        for p in polys:
            ax.add_patch(Patch(np.asarray(p.exterior.coords), facecolor='#1583aa', edgecolor='#064560', linewidth=.45, alpha=.28))
        for r in cfg['annulus_mm']:
            ax.add_patch(Circle((0, 0), r, fill=False, edgecolor='#c52e36', linestyle='--', linewidth=1.4))
        ax.set(xlim=(-218, 218), ylim=(-218, 218), aspect='equal', xlabel='x [mm]', ylabel='y [mm]', title=title)
        ax.grid(alpha=.15)
    for m in layout['modules']:
        if m['col']==0 and m['row'] in [0, 4, 8]:
            x, y = m['center_mm'][:2]
            for axis, color in [('u', '#d46a10'), ('v', '#24733d')]:
                dx, dy = np.asarray(m[axis][:2])*8
                axes[1].annotate('', xy=(x+dx, y+dy), xytext=(x, y), arrowprops=dict(arrowstyle='->', color=color, lw=1.3))
    axes[1].text(.03, .03, 'orange: tangential u · green: radial v', transform=axes[1].transAxes, fontsize=9,
                 bbox=dict(facecolor='white', alpha=.85, edgecolor='none'))
    fig.suptitle('DES016 radial revision — projected physical sensor silicon; dashed circles: unchanged active annulus\nDRAFT prototype: 15% preferred / 20% maximum; supports and services remain unqualified', fontsize=11)
    fig.savefig(out/'disc-comparison.png', dpi=160); fig.savefig(out/'disc-comparison.svg'); plt.close(fig)

    phi = np.linspace(0, 2*math.pi, 361); pitch = cfg['rectangular_pixel_control_um']
    cart = [math.sqrt(radial.covariance(pitch, angle+math.pi/2)[0][0]) for angle in phi]
    fig, ax = plt.subplots(figsize=(9, 3.8), layout='constrained')
    ax.plot(np.degrees(phi), cart, label='Global x/y axes: tangential uncertainty', color='#b33d33')
    ax.axhline(pitch[0]/math.sqrt(12), label='Radial rings: tangential at module centres', color='#1583aa', lw=2)
    ax.axhline(pitch[1]/math.sqrt(12), label='Radial rings: radial at module centres', color='#24733d', linestyle='--')
    ax.set(xlabel='Module azimuth [degrees]', ylabel='Binary pitch-only sigma [µm]', xlim=(0, 360),
           title=f'Hypothetical {pitch[0]:g} × {pitch[1]:g} µm pixels: orientation control, not track-fit resolution')
    ax.legend(fontsize=9); ax.grid(alpha=.2)
    fig.savefig(out/'axis-covariance.png', dpi=160); fig.savefig(out/'axis-covariance.svg'); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 3.7), layout='constrained')
    for m in layout['modules']:
        radius = np.linalg.norm(m['center_mm'][:2]); width = radial.dimensions(cfg, m['family'])[1]
        ax.plot([radius-width/2, radius+width/2], [m['local_z_mm']]*2, alpha=.45, lw=2,
                color=plt.get_cmap('tab10')(m['level']))
    ax.axhspan(-3.15, 3.15, color='gray', alpha=.25, label='Inherited 6.3 mm plate thickness only')
    ax.set(xlabel='Module radius [mm]; radial extent schematic', ylabel='Local outward z [mm]',
           title=f"{counts['body']['levels']} axial levels keep ≥0.2 mm occupied-body separation")
    ax.legend(fontsize=9); ax.grid(alpha=.2); fig.savefig(out/'module-levels.svg'); plt.close(fig)
    for p in out.glob('*.svg'):
        p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', type=Path, required=True); p.add_argument('--audit', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); a = p.parse_args(); a.output.mkdir(parents=True, exist_ok=True)
    cfg = radial.load_config(); r = json.loads((a.run/'screening.json').read_text()); native = json.loads((a.audit/'acts-summary.json').read_text())
    if not r['selected'] or not r['all_18_straight_coverage_pass'] or not r['all_18_overlap_body_pass'] or not r['orientation']['passed'] or not all(native[n]['passed'] and not native[n]['tracks_missing_target_disc'] for n in ['candidate', 'baseline', 'exhaustive']):
        raise ValueError('Failed retained radial evidence')
    s = r['selected']; sensor = s['sensor']; body = s['body']; svc = r['services']; orient = r['orientation']
    drawings(cfg, a.output, json.loads((a.run/'layout.json').read_text()), r)
    for source, destination in [(a.run/'screening.json', 'screening.json'), (a.audit/'acts-summary.json', 'acts.json'), (Path(radial.__file__).with_name('radial-inputs.json'), 'inputs.json')]:
        shutil.copyfile(source, a.output/destination)
    ring_rows = [f"| {x['row']+1} | {x['family']} | {x['modules']} | {x['radius_mm']:.6f} |" for x in s['rings']]
    controls = []
    for policy in cfg['policies']:
        if policy=='single': continue
        row = min((x for x in r['scan'] if x['policy']==policy), key=lambda x:max(v['gap_mm2'] for v in x['vertices']))
        controls.append(f"| {policy} | {row['modules']} / {row['chips']} | {row['sensor']['overlap_over_union_percent']:.3f}% | {row['sensor']['annular_overlap_over_union_percent']:.3f}% | {max(v['gap_mm2'] for v in row['vertices']):.3f} | REJECTED |")
    scenarios = []
    for scenario in svc['scenarios']:
        positive = next(x for x in scenario['end_trunks'] if x['side']=='positive')
        scenarios.append(f"| {scenario['scenario']} | {scenario['cables_mm2']:.1f} | {scenario['feed_return_pipe_mm2']:.1f} | {positive['after_disc_8_demand_mm2']:.1f} | {positive['capacity_mm2']:.1f} | {positive['utilization']:.2f} × / {positive['status']} |")
    far_overlap = max(max(d['sensor']['overlap_over_union_percent'], d['sensor']['annular_overlap_over_union_percent']) for d in r['per_disc_screens'])
    guard = r['guard_control_0p5mm']
    text = f'''# DES016 — radial module revision

Status: **DRAFT / isolated PROTOTYPE. Coverage/body/orientation screens pass; inherited service packing remains unqualified.**

The user rejected global x/y-aligned modules and authorized 15–20% overlap for hermeticity. [DES016](../../../design/DES-016-pixel-disc-module-optimization.md) now prefers 15% and caps both whole projected silicon and annulus-only overlap at 20%. The earlier [Cartesian result](../results.md) is retained as superseded evidence. This revises PR41 independently of PR40 positioning and does not replace the production compact.

![Quad baseline and revised radial single-module rings](disc-comparison.png)

## Selected layout and bounded search

The selected arrangement has **{s['modules']} single-RD53i modules/chips per disc in {len(s['rings'])} concentric rings**, preserving the 18-module inner ring at template radius 41.15 mm. Every module has tangential `u` and outward radial `v` at its centre. Adjacent rings alternate half-cell phase. Active matrices remain 20 × 19.2 mm, with the existing 50 × 50 µm chip-cell fixture and nominal annulus r32.3..181.4550267061104 mm. Centres are compensated for axial staggering; the radii below are template radii before that compensation.

| Ring | Family | Modules | Template radius [mm] |
| --- | --- | ---: | ---: |
'''+ '\n'.join(ring_rows)+f'''

First-disc margins are {s['radial_margin_mm']} mm radial and {s['phi_margin_mm']} mm tangential in the ring-envelope proposal. These are search controls; actual active polygons decide coverage. The finite scan considers {len(r['scan'])} specified candidates, with single, tangential-double, radial-double, quad and mixed-family policies. It ranks fully passing candidates first by the preferred overlap tier, then chip count, module count and worst overlap. No scanned arrangement satisfied the preferred 15% limit for both overlap metrics with certified coverage; the selected candidate uses the authorized 20% tier. This is a bounded search, not a proof of a global optimum.

| Per disc | Original quad coplanar control | Revised first-disc nominal IP projection |
| --- | ---: | ---: |
| Modules / chips | 112 / 448 | {s['modules']} / {s['chips']} |
| Silicon repeated area / projected union | {r['baseline']['sensor']['overlap_over_union_percent']:.3f}% | **{sensor['overlap_over_union_percent']:.3f}%** |
| Annulus-only repeated area / union | {r['baseline']['sensor']['annular_overlap_over_union_percent']:.3f}% | **{sensor['annular_overlap_over_union_percent']:.3f}%** |
| Repeated area / summed installed area | {r['baseline']['sensor']['overlap_over_installed_percent']:.3f}% | {sensor['overlap_over_installed_percent']:.3f}% |
| Installed silicon outside annulus [mm²] | {r['baseline']['sensor']['installed_outside_annulus_mm2']:.1f} | {sensor['installed_outside_annulus_mm2']:.1f} |

Repeated area means `(sum of physical sensor-outline areas − union area) / union area`; triple coverage counts twice. Outlines include guard silicon. A double/quad has one shared outline, while coverage uses its individual active matrices with the inherited **0.2 mm inactive interchip gap**. The annulus is unchanged and outlines are never cropped to improve the overlap metric.

## Larger-module controls and seams

These representative rows minimize the worst endpoint coverage hole within each scanned family policy. Full controls and rejected certificates are retained in [screening.json](screening.json); lower silicon overlap alone is not sufficient to select a proposal.

| Policy | Modules / chips | Whole overlap | Annular overlap | Worst active hole at tested vertex [mm²] | Result |
| --- | ---: | ---: | ---: | ---: | --- |
'''+ '\n'.join(controls)+f'''

The tested larger/mixed rings leave active seam gaps and/or exceed the overlap ceiling. They are retained as rejected variants; this does not establish that every possible mixed-family design is infeasible. Shared-sensor seam response cannot be assumed or stretched. The body screen colours entire assemblies, keeping all chips on their parent's plane.

## Pixel axes and resolution scope

![Anisotropic pitch covariance control](axis-covariance.png)

For a hypothetical **25 × 100 µm** binary-pitch control, local pixel covariance is `diag(p_u²,p_v²)/12`, rotated into tangential/radial coordinates. Global x/y alignment makes tangential sigma vary from **{orient['global_xy_control_tangential_sigma_um'][0]:.3f} to {orient['global_xy_control_tangential_sigma_um'][1]:.3f} µm** with azimuth. The revised axes give constant **{orient['polar_center_tangential_radial_sigma_um'][0]:.3f} µm tangential** and **{orient['polar_center_tangential_radial_sigma_um'][1]:.3f} µm radial** values at module centres. The square-pixel control is rotation-invariant, as expected. This rectangular pitch is a test hypothesis; it does not change the RD53i hardware fixture.

Flat rectangles cannot align with the radial/tangential basis at every pixel. Maximum corner departure is **{orient['maximum_corner_axis_departure_degrees']:.3f}°**, dominated by the retained inner ring, and its nonzero rotated covariance is recorded. These are local geometric measurement controls, not fitted transverse/longitudinal track resolutions, digitization, charge sharing or irradiation qualification. Longitudinal track resolution also depends on polar angle, lever arms and reconstruction.

## Coverage, bodies and native ACTS

All nine positive disc datums pass conservative polygon-containment certificates for **every on-axis straight-ray vertex z in [−150,+150] mm**; geometric reflection supplies the negative end. The first disc uses {len(r['coverage_certificates'][0]['intervals'])} certified intervals. Individual active-matrix endpoint intersections contain a conservative annulus superset on each interval. No raster or guard silicon substitutes for active coverage. Numerical area threshold remains 1e−6 mm²; the circular superset error bound is {sensor['polygon_circle_area_error_bound_mm2']:.6f} mm².

All 18 overlap/body screens pass; worst overlap across distances is **{far_overlap:.3f}%**. {body['levels']} axial levels at 1.2 mm spacing retain ≥0.2 mm occupied-body separation. First-disc body envelope is r≤{body['maximum_radius_mm']:.3f} mm, with minimum beam radius {body['minimum_beam_radius_mm']:.3f} mm. Maximum body radius across all distances is {max(d['body']['maximum_radius_mm'] for d in r['per_disc_screens']):.3f} mm. The positive-side periphery remains outward under negative reflection. Existing original DES015 disc datums, including ±615.2 mm, are unchanged in this independent study.

Native **acts-nodd** constructs **{native['input_provenance']['all_disc_patches']} candidate sensitive planes** and compares {native['candidate']['tracks_requested']} matched tracks against the actual staggered quad baseline, using all 18 discs, 0/2 T, pT1 GeV, both charges and on-axis vertices −150/0/+150 mm. Six exhaustive first-disc controls bypass the shared broad-phase filter. All finite-plane intersections/IDs agree with the independent analytic oracle; no track misses its intended target disc. [acts.json](acts.json) retains exact binaries, source state and summary hashes. This is an actual finite supporting-plane transport audit, not global navigation, continuous-helix hermeticity, fitted resolution or material validation.

## Engineering boundary and service estimates

Sensor guard remains the unqualified **0.1 mm** choice, with the single-body 20.4 × 21.4 mm envelope. Doubles and quads retain explicitly defined shared-outline/body choices; the quad occupied envelope is inherited 43.2 × 44.2 mm. A **0.5 mm guard control gives {guard['overlap_over_union_percent']:.3f}% whole and {guard['annular_overlap_over_union_percent']:.3f}% annular overlap**, showing the effect of realistic edge allowances without hiding the control.

Conditional heat is **{svc['nominal_W']:.3f} W/disc**, {100*(1-s['chips']/448):.3f}% below 448 chips. Homogeneous half-ring groups produce **{svc['power_chains']} power chains** under both ≤16-module and ≤32-chip limits, and **{svc['local_circuits']} independently fed cooling circuits** under the inherited 300 W grouping ceiling. Both feed/return legs are counted. Circumferential tube length is {svc['half_ring_tube_length_without_feeds_mm']:.1f} mm/disc, giving {svc['local_tube_volume_envelope_mm3']/1000:.3f} cm³ of OD2.8 mm tube envelope before transport legs, bends and manifolds. These are spatial estimates, not routed or hydraulic-qualified assemblies.

The trial shared trunk occupies r{svc['trunk_inner_mm']}..{svc['trunk_outer_mm']} mm after reserving 2 mm beyond the largest occupied body. The inherited barrel traffic, eight joined discs and ninth-disc conditional bypass are retained.

| Scenario | Cable [mm²/disc] | Feed+return [mm²/disc] | Positive demand after 8 discs [mm²] | Available packed area [mm²] | Utilization / result |
| --- | ---: | ---: | ---: | ---: | --- |
'''+ '\n'.join(scenarios)+'''

The support envelope and all failing shared-trunk scenarios require engineering revision before adoption. No thermal failure is declared resolved by the geometric screen. No design sign-off or production integration is implied.

## Reproduction and provenance

[Inputs](inputs.json), [screening](screening.json), [ACTS](acts.json) and [artifact hashes](artifacts.json) pin the full scan, policies, preserved baseline, source/code state and runtime. Follow the [tool README](../../../../tools/pixel_disc_optimization/README.md). Matrix/pitch/material and service inputs are inherited evidence; new placement/body/guard/family controls are unqualified NODD DESIGN CHOICES; areas, certificates, covariance and services are INFERENCES. All plots are generated from the retained numerical proposal. Original Cartesian reports and scientific inputs remain intact.
'''
    (a.output/'results.md').write_text(text)
    summary = dict(producer_hashes={str(p.relative_to(ROOT)):digest(p) for p in sorted((ROOT/'tools/pixel_disc_optimization').glob('*.py'))},
                   files={p.name:digest(p) for p in sorted(a.output.iterdir()) if p.is_file() and p.name!='artifacts.json'})
    (a.output/'artifacts.json').write_text(json.dumps(summary, indent=2)+'\n')


if __name__ == '__main__':
    main()
