#!/usr/bin/env python3
"""DES016: trim complete radial rings within the inherited service envelope.

Keep surviving transforms and the original acceptance target. A successful
interface screen does not turn the explicit coverage loss into hermeticity.
"""
import argparse
import datetime
import json
import math
from pathlib import Path
import platform
import shutil
import subprocess

import numpy as np
import shapely
from shapely.geometry import Point

import radial
from study import ROOT, digest, metrics, rectangle


INPUTS = Path(__file__).with_name('service-radius-inputs.json')


def load_config():
    limits = json.loads(INPUTS.read_text())
    for path, expected in limits['input_sha256'].items():
        if digest(ROOT/path) != expected:
            raise ValueError(f'Stale service-radius input: {path}')
    cfg = json.loads((ROOT/limits['radial_inputs']).read_text())
    prior = json.loads((ROOT/limits['radial_screening']).read_text())['selected']
    support = json.loads((ROOT/limits['support_inputs']).read_text())
    transport = json.loads((ROOT/limits['transport_inputs']).read_text())['transport']
    limits.update(plate_outer_mm=support['plate']['r_max_mm'],
                  collector_outer_mm=transport['collector_r_mm'][1],
                  trunk_r_mm=transport['trunk_r_mm'],
                  inherited_land_mm=[support['foot']['envelope_u_mm'], support['foot']['envelope_v_mm']],
                  inherited_land_offset_mm=support['foot']['radial_offset_mm'])
    if digest(ROOT/cfg['baseline']) != cfg['baseline_sha256']:
        raise ValueError('Stale original detector layout')
    return cfg, limits, prior


def source_modules(cfg, prior, datum):
    raw, rings = radial.candidates(cfg, prior['radial_margin_mm'], prior['phi_margin_mm'], prior['policy'])
    return radial.stagger(raw, cfg, datum), rings


def radius_of(polygon):
    return max(math.hypot(x, y) for x, y in polygon.exterior.coords)


def choose_rows(cfg, limits, prior):
    """Remove contiguous outer rings if any body exceeds the fixed local plate."""
    removed = set()
    for datum in cfg['positive_disc_datums_mm']:
        modules, rings = source_modules(cfg, prior, datum)
        for m in modules:
            if radius_of(radial.body_polygon(m, cfg)) > limits['plate_outer_mm']:
                removed.add(m['row'])
    if not removed:
        return [], rings
    removed = list(range(min(removed), max(r['row'] for r in rings)+1))
    if 0 in removed:
        raise ValueError('Inherited service bound cannot retain the inner ring')
    return removed, rings


def placed_modules(cfg, prior, datum, removed):
    modules, _ = source_modules(cfg, prior, datum)
    # Do not recolour or compensate surviving modules a second time.
    return [m for m in modules if m['row'] not in removed]


def interface_screen(modules, cfg, limits):
    bodies = radial.body_screen(modules, cfg)
    lands = []; old_lands = []
    width, height = limits['inherited_land_mm']; offsets = []
    for m in modules:
        family = cfg['families'][m['family']]
        offset = family['periphery_offset_mm'] + family['body_mm'][1]/2 - height/2
        offsets.append(offset)
        c = np.asarray(m['center_mm']); v = np.asarray(m['v'])
        land = rectangle(c+offset*v, m['u'], m['v'], width/2, height/2)
        if not radial.body_polygon(m, cfg).buffer(1e-9).covers(land):
            raise ValueError('Reserved pickup land is outside the occupied body')
        lands.append(land)
        old_lands.append(rectangle(c+limits['inherited_land_offset_mm']*v, m['u'], m['v'], width/2, height/2))
    tube = max(np.linalg.norm(m['center_mm'][:2]) for m in modules)+cfg['local_tube_OD_mm']/2
    maximum = max(bodies['maximum_radius_mm'], tube, max(map(radius_of, lands)))
    passed = (maximum <= limits['plate_outer_mm'] and
              maximum+cfg['collector_radial_gap_mm'] <= limits['collector_outer_mm'] and
              not bodies['overlaps_or_insufficient_gap'] and
              bodies['minimum_beam_radius_mm'] >= cfg['beam_clearance_radius_mm'] and
              min(p.distance(Point(0, 0)) for p in lands) >= cfg['beam_clearance_radius_mm'])
    return dict(passed=passed, body=bodies, maximum_reserved_radius_mm=maximum,
                plate_outer_mm=limits['plate_outer_mm'], plate_clearance_mm=limits['plate_outer_mm']-maximum,
                collector_boundary_mm=limits['collector_outer_mm'], collector_clearance_mm=limits['collector_outer_mm']-maximum,
                effective_trunk_inner_mm=limits['trunk_r_mm'][0], trunk_clearance_mm=limits['trunk_r_mm'][0]-maximum,
                local_tube_outer_radius_mm=tube, pickup_land_outer_radius_mm=max(map(radius_of, lands)),
                pickup_land_offset_mm=sorted(set(offsets)), inherited_land_control_outer_radius_mm=max(map(radius_of, old_lands)),
                inherited_land_control_pass=max(map(radius_of, old_lands)) <= limits['plate_outer_mm'],
                scope='Body/land/tube bounding envelopes only; pickup contacts, flex routing and swept bends are not engineering-qualified.')


def fixed_services(modules, rings, cfg, limits):
    svc = radial.service_estimate(modules, rings, cfg, radial.body_screen(modules, cfg)['maximum_radius_mm'])
    inner, outer = limits['trunk_r_mm']; neck = limits['flange_neck_outer_mm']
    if inner < svc['trunk_inner_mm']:
        raise ValueError('Inherited service trunk intersects the reserved collector gap')
    inputs = json.loads((ROOT/cfg['services_input']).read_text())
    for scenario in svc['scenarios']:
        settings = inputs['scenarios'][scenario['scenario']]
        for side in scenario['end_trunks']:
            cap = math.pi*(outer**2-inner**2)*settings['available_phi_fraction']*settings['packing_fraction']
            neck_cap = math.pi*(neck**2-inner**2)*settings['available_phi_fraction']*settings['packing_fraction']
            demand = side['after_disc_8_demand_mm2']
            side.update(capacity_mm2=cap, utilization=demand/cap, status='PASS' if demand<=cap else 'FAIL',
                        flange_neck_capacity_mm2=neck_cap, flange_neck_utilization=demand/neck_cap,
                        flange_neck_status='PASS' if demand<=neck_cap else 'FAIL')
    svc.update(trunk_inner_mm=inner, trunk_outer_mm=outer, flange_neck_outer_mm=neck,
               pickup_land_scope='18x8 mm bounding reservations within the single body, offset7.6 mm; inherited16 mm quad offset fails.',
               local_feed_return_radial_legs=2*svc['local_circuits'])
    svc['limitations'].append('Fixed DES015 r192..231.7 trunk and r222 flange neck; neither reservation is expanded to improve packing.')
    return svc


def screen_run(out):
    cfg, limits, prior = load_config(); removed, rings = choose_rows(cfg, limits, prior)
    surviving = [r for r in rings if r['row'] not in removed]; discs = []
    for datum in cfg['positive_disc_datums_mm']:
        modules = placed_modules(cfg, prior, datum, removed)
        interface = interface_screen(modules, cfg, limits)
        sensor = metrics(radial.project(modules, cfg, datum, guard=cfg['sensor_guard_mm']), cfg)
        active = [dict(vertex_z_mm=v, **metrics(radial.project(modules, cfg, datum, vertex=v), cfg)) for v in cfg['vertices_z_mm']]
        uncovered = any(x['uncovered_annulus_superset_mm2'] > cfg['area_tolerance_mm2'] for x in active)
        if uncovered:
            certificate = dict(passed=False, reason='Direct endpoint counterexamples disprove full-annulus coverage; no adaptive continuous certificate can pass.',
                               counterexamples=active, target_annulus_mm=cfg['annulus_mm'])
        else:
            certificate = radial.coverage_certificate(radial.active_patches(modules, cfg), cfg, datum)
        discs.append(dict(datum_mm=datum, interface=interface, sensor=sensor, active_vertices=active, coverage_certificate=certificate))
    modules = placed_modules(cfg, prior, cfg['disc_datum_mm'], removed)
    if not all(d['interface']['passed'] and max(d['sensor']['overlap_over_union_percent'], d['sensor']['annular_overlap_over_union_percent'])<=cfg['overlap_limit_percent'] for d in discs):
        raise ValueError('Trimmed layout fails radial interface/body/overlap bounds')
    report = dict(status='DRAFT / isolated service-radius PROTOTYPE; original-annulus hermeticity fails explicitly',
                  prior_modules=prior['modules'], modules=len(modules), chips=len(radial.active_patches(modules, cfg)),
                  removed_rows=removed, removed_modules=prior['modules']-len(modules), rings=surviving,
                  original_annulus_mm=cfg['annulus_mm'], per_disc_screens=discs,
                  all_18_interface_body_overlap_pass=True,
                  all_18_original_annulus_coverage_pass=all(d['coverage_certificate']['passed'] for d in discs),
                  orientation=radial.orientation_screen(modules, cfg),
                  guard_control_0p5mm=metrics(radial.project(modules, cfg, cfg['disc_datum_mm'], guard=.5), cfg),
                  services=fixed_services(modules, surviving, cfg, limits), limits=limits,
                  reflection_scope='Reflect through z=0, reversing u, preserving outward v/periphery; equivalent radial and straight projection bounds on negative discs.',
                  provenance=dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                                  dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),
                                  generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=platform.python_version(),numpy=np.__version__,shapely=shapely.__version__,
                                  hashes={str(p.relative_to(ROOT)):digest(p) for p in [INPUTS,Path(__file__),*map(lambda x:ROOT/x,limits['input_sha256']),ROOT/cfg['baseline'],ROOT/cfg['services_input'],ROOT/cfg['barrel_services']]}))
    out.mkdir(parents=True, exist_ok=True)
    (out/'screening.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    (out/'layout.json').write_text(json.dumps(dict(status=report['status'],modules=modules,rings=surviving,active_patches=radial.active_patches(modules,cfg)),indent=2)+'\n')
    print(json.dumps(dict(modules=report['modules'],removed_modules=report['removed_modules'],maximum_reserved_radius_mm=max(d['interface']['maximum_reserved_radius_mm'] for d in discs),original_annulus_coverage_pass=report['all_18_original_annulus_coverage_pass'])))
    return report


def native_audit(run, out, acts_source):
    import audit
    import radial_audit
    cfg, limits, prior = load_config(); report=json.loads((run/'screening.json').read_text())
    raw,_=radial.candidates(cfg,prior['radial_margin_mm'],prior['phi_margin_mm'],prior['policy'])
    new,old,discs=radial_audit.layouts(cfg,raw)
    new['modules']=[m for m in new['modules'] if m['row'] not in report['removed_rows']]
    tracks=audit.tracks(discs); original_count=len(tracks)
    for d in discs:
        for phi in limits['edge_control_phi_rad']:
            radius=limits['edge_control_radius_mm']
            tracks.append(dict(target_layer=d['layer'],target_radius_mm=radius,eta=math.asinh(d['proposed_z_mm']/radius),phi=phi,field_T=0.,pt_GeV=1.,charge=1.,origin_mm=[0.,0.,0.]))
    first=dict(modules=[m for m in new['modules'] if m['layer_id']==discs[0]['layer']]); summaries={}
    out.mkdir(parents=True,exist_ok=True)
    for name,layout,ts,exhaustive in [('candidate',new,tracks,False),('baseline',old,tracks,False),('exhaustive',first,tracks[:6],True)]:
        result=audit.acts_validate.validate(layout,ts,out/name,acts_source=acts_source,host_radius_mm=234.,host_half_z_mm=3150.,exhaustive=exhaustive)
        by_id={m['id']:m['layer_id'] for m in layout['modules']}
        misses=[dict(track=t['track'],input=t['input']) for t in result['per_track'] if not any(by_id[i]==t['input']['target_layer'] for i in t['observed_patch_hits'])]
        summaries[name]={k:v for k,v in result.items() if k!='per_track'}
        summaries[name].update(tracks_missing_target_disc=misses,per_track_sha256=digest(out/name/'native-target-audit.json'),
                               original_probe_count=min(original_count,len(ts)),edge_control_count=max(0,len(ts)-original_count))
        if not result['passed']:
            raise ValueError('Native finite-plane audit disagrees with the analytic oracle')
    summaries['input_provenance']=dict(screening_sha256=digest(run/'screening.json'),config_sha256=digest(INPUTS),audit_code_sha256=digest(__file__),
                                      patches_per_disc=len(first['modules']),all_disc_patches=len(new['modules']),
                                      scope='Finite supporting-plane/identifier audit; expected edge misses retained as coverage-loss evidence, not treated as transport mismatches.')
    (out/'acts-summary.json').write_text(json.dumps(summaries,indent=2,allow_nan=False)+'\n')
    print(json.dumps({n:dict(passed=r['passed'],tracks=r['tracks_requested'],hits=r['reached_native_targets'],missing_target_disc=len(r['tracks_missing_target_disc'])) for n,r in summaries.items() if n!='input_provenance'}))


def report_run(run, audit_dir, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Polygon as Patch
    cfg,limits,prior=load_config(); r=json.loads((run/'screening.json').read_text()); native=json.loads((audit_dir/'acts-summary.json').read_text())
    if not r['all_18_interface_body_overlap_pass'] or not r['orientation']['passed'] or not all(native[n]['passed'] for n in ['candidate','baseline','exhaustive']):
        raise ValueError('Failed retained interface/transport evidence')
    out.mkdir(parents=True,exist_ok=True)
    before,_=source_modules(cfg,prior,cfg['disc_datum_mm']); after=json.loads((run/'layout.json').read_text())['modules']
    fig,axes=plt.subplots(1,2,figsize=(12,6.4),layout='constrained')
    for ax,modules,title in zip(axes,[before,after],['Previous radial proposal: 359 modules / 9 rings',f"Within service bounds: {r['modules']} modules / {len(r['rings'])} rings"]):
        for p in radial.project(modules,cfg,cfg['disc_datum_mm'],guard=cfg['sensor_guard_mm']):
            ax.add_patch(Patch(np.asarray(p.exterior.coords),facecolor='#1583aa',edgecolor='#064560',linewidth=.4,alpha=.3))
        for rr in cfg['annulus_mm']:
            ax.add_patch(Circle((0,0),rr,fill=False,edgecolor='#c52e36',linestyle='--',linewidth=1.3))
        for rr,color,label in [(limits['plate_outer_mm'],'#987123','188.5 mm plate'),(limits['collector_outer_mm'],'#753996','190 mm service boundary')]:
            ax.add_patch(Circle((0,0),rr,fill=False,edgecolor=color,linewidth=1,label=label))
        ax.set(xlim=(-215,215),ylim=(-215,215),aspect='equal',xlabel='x [mm]',ylabel='y [mm]',title=title);ax.grid(alpha=.15)
    axes[1].legend(loc='lower left',fontsize=8)
    fig.suptitle('DES016 service-radius revision — outer 63-module ring removed; surviving transforms retained\nDashed red: original active target (outer-edge coverage is lost); fixed support/service bounds',fontsize=11)
    fig.savefig(out/'disc-comparison.png',dpi=160);fig.savefig(out/'disc-comparison.svg');plt.close(fig)
    p=out/'disc-comparison.svg';p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')
    for source,destination in [(run/'screening.json','screening.json'),(run/'layout.json','layout.json'),(audit_dir/'acts-summary.json','acts.json'),(INPUTS,'inputs.json')]:
        shutil.copyfile(source,out/destination)
    first=r['per_disc_screens'][0]; interface=first['interface']; worst=max(d['interface']['maximum_reserved_radius_mm'] for d in r['per_disc_screens'])
    overlap=max(max(d['sensor']['overlap_over_union_percent'],d['sensor']['annular_overlap_over_union_percent']) for d in r['per_disc_screens'])
    active=[x for d in r['per_disc_screens'] for x in d['active_vertices']]; svc=r['services']
    rings='\n'.join(f"| {x['row']+1} | {x['modules']} | {x['radius_mm']:.6f} |" for x in r['rings'])
    rows=[]
    for x in svc['scenarios']:
        side=x['end_trunks'][0]
        rows.append(f"| {x['scenario']} | {x['cables_mm2']:.1f} | {x['feed_return_pipe_mm2']:.1f} | {side['after_disc_8_demand_mm2']:.1f} | {side['capacity_mm2']:.1f} | {side['utilization']:.3f}× / {side['status']} | {side['flange_neck_capacity_mm2']:.1f} | {side['flange_neck_utilization']:.3f}× / {side['flange_neck_status']} |")
    text=f'''# DES016 — fixed service-radius revision

Status: **DRAFT / isolated PROTOTYPE. Radial interface/body/overlap screens pass; original-annulus hermeticity FAILS explicitly.**

The user required the radial layout to remain within cable/service bounds, removing the outermost row if needed. This supersedes the [nine-ring proposal](../radial-revision/results.md) while preserving its evidence and the [Cartesian control](../results.md). [DES016 DO-C08/09](../../../design/DES-016-pixel-disc-module-optimization.md) records the amendment before implementation.

## Fixed radial interfaces and surviving layout

Remove the complete outer **{r['removed_modules']}-module ring**: **{r['modules']} single modules/chips remain in {len(r['rings'])} rings**. Keep all surviving centres, axial levels, axes and stable identifiers at every disc distance; the 18-single inner ring remains unchanged. No matrices, silicon outlines, nominal annulus or disc positions are resized. The independent PR40 movement table and production compact are unchanged.

| Ring | Single modules | Template radius [mm] |
| --- | ---: | ---: |
{rings}

Maximum occupied/reserved radius across all distances is **{worst:.6f} mm**, inside the inherited **r{limits['plate_outer_mm']} mm plate**, with **{limits['plate_outer_mm']-worst:.6f} mm clearance**. It clears the unchanged **r190 mm collector/service boundary by {limits['collector_outer_mm']-worst:.6f} mm**, and effective **r192 mm trunk by {limits['trunk_r_mm'][0]-worst:.6f} mm**. The ≥2 mm radial collector gap is retained. Five inherited 1.2 mm axial levels keep ≥0.2 mm occupied-body separation; negative-side reflection preserves the outward periphery. The local OD2.8 mm circumferential tube bound reaches r{interface['local_tube_outer_radius_mm']:.6f} mm on the first disc.

The inherited quad-specific +16 mm pickup-land offset would reach **r{interface['inherited_land_control_outer_radius_mm']:.6f} mm**, beyond the plate, so it is a rejected reuse control. An **18×8 mm provisional land reservation at +7.6 mm** is contained within the slim single-body silhouette, ending at its outboard edge. This dimension follows 0.9+21.4/2−8/2 mm; it is a NODD DESIGN CHOICE for bounding geometry. It does not qualify a thermal contact, foot manufacture or swept pipe/flex artwork. Contact, heat-transfer, stiffness, flexes and bends still require engineering within these fixed bounds; none is moved into the service trunk.

## Coverage and overlap — retained loss

The original nominal **r32.3..181.4550267061104 mm** annulus stays the comparison target. Whole-ring removal leaves outer-edge holes. Across all nine distances and the three sampled on-axis vertices, uncovered area bounds range **{min(x['uncovered_annulus_superset_mm2'] for x in active):.3f}..{max(x['uncovered_annulus_superset_mm2'] for x in active):.3f} mm²**; covered area fractions range **{100*min(x['covered_fraction'] for x in active):.4f}..{100*max(x['covered_fraction'] for x in active):.4f}%**. Direct endpoint counterexamples disprove full-annulus hermeticity; no certificate is relabelled as passing and no reduced target is substituted. These are projected geometric areas, not tracking efficiency or momentum-resolution measurements.

First-disc silicon overlap is **{first['sensor']['overlap_over_union_percent']:.3f}% whole / {first['sensor']['annular_overlap_over_union_percent']:.3f}% annular**, with worst **{overlap:.3f}%** across all distances, under the authorized 20% maximum. Original guard/body assumptions remain unqualified; the 0.5 mm guard control is retained in the screening. Radial/tangential axes and the prior covariance scope are unchanged.

## Native ACTS and retained controls

Native acts-nodd constructs **{native['input_provenance']['all_disc_patches']} candidate sensitive planes** and compares **{native['candidate']['tracks_requested']} matched tracks per layout** with the actual staggered baseline. The original 324 probes span 18 discs, 0/2 T, pT 1 GeV, both charges and vertices −150/0/+150 mm; 54 added straight edge probes target r181 mm within the original annulus. Six exhaustive first-disc controls bypass the broad-phase filter. Native finite-plane IDs/intersections agree with the analytic oracle; candidate target-disc misses: **{len(native['candidate']['tracks_missing_target_disc'])}**, baseline misses: **{len(native['baseline']['tracks_missing_target_disc'])}**, explicitly retained in [acts.json](acts.json). Transport agreement is not hermeticity. No fitted resolution, global navigation, continuous helix or transverse-vertex certificate is asserted.

## Cable/cooling accounting with fixed service bounds

Conditional heat is **{svc['nominal_W']:.3f} W/disc**; **{svc['power_chains']} chains** obey ≤16 physical modules and ≤32 chips, and **{svc['local_circuits']} half-ring cooling circuits** count both feed and return: **{svc['local_feed_return_radial_legs']} radial legs**. Both OD4 mm transport legs consume {svc['scenarios'][0]['feed_return_pipe_mm2']:.1f} mm²/disc. Circumferential tube length is {svc['half_ring_tube_length_without_feeds_mm']:.1f} mm/disc before transport legs, bends and manifolds. These are spatial inventories, not routed/hydraulic qualification.

Use the existing **r192..231.7 mm trunk** and **r192..222 mm flange neck**, with inherited packing/phi fractions and barrel traffic. The smaller layout neither widens the outer service envelope nor moves its inner boundary inward.

| Scenario | Cables/disc [mm²] | Both pipe legs/disc [mm²] | Accumulated demand [mm²] | Trunk capacity [mm²] | Trunk utilization/status | Neck capacity [mm²] | Neck utilization/status |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
{chr(10).join(rows)}

Packing failures remain unresolved; clearance alone does not guarantee cable capacity or close inherited thermal/support failures. Guard qualification, engineering of the bounded single-module contact/routing, and any restoration of full-annulus acceptance require review. No design sign-off or production integration is recorded.

## Reproduction and provenance

[Inputs](inputs.json), [screening](screening.json), [retained surviving transforms](layout.json), [ACTS](acts.json) and [hashes](artifacts.json) pin the inherited interfaces, exact source control, code/runtime and acceptance-loss evidence. Follow the [README](../../../../tools/pixel_disc_optimization/README.md). Boundaries/envelopes are inherited NODD DESIGN CHOICES; whole-ring removal and land reservation follow the human-directed DO-C08/09 amendment; areas, clearances, counts and service arithmetic are INFERENCES. Edge-track values are numerical test controls. No new external technology or experimentally qualified performance claim is added.
'''
    (out/'results.md').write_text(text)
    hashes={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='artifacts.json'}
    (out/'artifacts.json').write_text(json.dumps(dict(artifacts=hashes,producer_hashes={str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__),INPUTS,Path(radial.__file__),Path(radial.__file__).with_name('radial_audit.py')]}),indent=2)+'\n')
    print(f'Retained {len(hashes)} service-radius artifacts; original coverage failure remains explicit.')


def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('screen');s.add_argument('--output',type=Path,required=True)
    s=sub.add_parser('audit');s.add_argument('--run',type=Path,required=True);s.add_argument('--output',type=Path,required=True);s.add_argument('--acts-source',type=Path,required=True)
    s=sub.add_parser('report');s.add_argument('--run',type=Path,required=True);s.add_argument('--audit',type=Path,required=True);s.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.command=='screen':screen_run(a.output)
    elif a.command=='audit':native_audit(a.run,a.output,a.acts_source)
    else:report_run(a.run,a.audit,a.output)


if __name__=='__main__':main()
