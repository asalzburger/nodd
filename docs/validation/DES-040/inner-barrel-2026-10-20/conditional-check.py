#!/usr/bin/env python3
"""Pinned, scratch-only B1 feasibility calculation; no active geometry export."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time

import numpy as np

REV = '56f12ef5b2a9bd410cb77e95ac3140557d92f1b2'
BASE_PATH = 'docs/validation/DES-040/barrel-overlap-2026-10-20/candidate/geometry.json'
SOURCES = {
 'docs/design/DES-040-muon-chambers-frame.md':'a068f493811a562e147d09b32a6095bb52ab70b2a18265249f9e4eefe95bc452',
 BASE_PATH:'f4aebc7d5e1476d6f40f331d2aef0673fa6840ee1883015570089be6e79ad328',
 'tools/muon_layout/barrel_overlap.py':'e57597636d2634bd93f8cd38e00a1ca63500d7ebaff85751288e9a86471899ac',
 'tools/muon_layout/layout.py':'137fe25dcfd4eb7ebde8c966a903dddb88e0976e339934edadb0d622aacf4b17',
 'tools/muon_layout/geometry.py':'162aeafae3775d0483d770556286485be9333523227b6160af0265d74f5cc230',
 'tools/muon_layout/support.py':'14f294c0250166239caca055436ffe9c3f664b246f7d14baabd7eab62c75d7af',
 'tools/toroid_prototype/geometry.py':'e831bbc59054713f23dca5367df51f70360d80e52614ac1fe0b0e8d8943f049f',
 'tools/muon_layout/wheels.py':'8172819c34b7ceb991b1371ae7aa5d22edff340db4c2c5b12ce0a37a1fea0ed6',
}


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def identity(body):
    return {k: body[k] for k in ('id', 'kind', 'origin_m', 'basis', 'vertices_m', 'depth_m', 'station', 'compartment', 'face')}


def b1_candidates(chambers, config, dimensions):
    radius, zmax, phase = (chambers['barrel_apothems_m'][0], chambers['barrel_half_z_m'][0], chambers['barrel_phase_deg'][0])
    for facet in range(24):
        odd = facet % 2 == 1
        rr = dimensions['odd_apothem_m'] if odd else radius
        ww = dimensions['odd_half_width_m'] if odd else dimensions['even_half_width_m']
        for iz, (lo, hi) in enumerate(layout.tiles(-zmax, zmax, config['max_barrel_length_m'], chambers['gap_m'])):
            yield layout._barrel(f'B1/F{facet:02d}/Z{iz:02d}', 1, phase+facet*15., rr, lo, hi, -ww, ww, chambers)


def crossing(panels, rays, border=0., full_depth=True):
    found = np.zeros((len(rays), 3), bool)
    for body in panels:
        found[:, body['station']-1] |= np.isfinite(g.midplane_hits(body, rays, border, full_depth))
    return found


def coverage(before, after, noframe, full_z_templates):
    # Bounded fresh iid bank; no native transport or magnetic propagation.
    n, seed = 65536, 40087
    rng = np.random.default_rng(seed)
    mu = rng.uniform(-1., 1., n)
    phi = rng.uniform(0., 2*math.pi, n)
    rays = np.column_stack((np.sqrt(1-mu*mu)*np.cos(phi), np.sqrt(1-mu*mu)*np.sin(phi), mu))
    result = dict(samples=n, seed=seed, distribution='iid uniform cos(theta) and phi over full4pi',
                  scope='Straight IP rays; distinct stations; finite full-depth same-cassette proxy; no response/transport/reconstruction claim')
    # Fixed stations need evaluating only once per border definition.
    fixed = [p for p in before if not (p['kind']=='barrel' and p['station']==1)]
    b1old = [p for p in before if p['kind']=='barrel' and p['station']==1]
    b1new = [p for p in after if p['kind']=='barrel' and p['station']==1]
    for border in (0., .03):
        common = crossing(fixed, rays, border)
        oldbar = crossing(b1old, rays, border)[:, 0]
        newbar = crossing(b1new, rays, border)[:, 0]
        new_without_frame = crossing(noframe, rays, border)[:, 0]
        new_full_z = crossing(full_z_templates, rays, border)[:, 0]
        old, new = common.copy(), common.copy()
        old[:, 0] |= oldbar
        new[:, 0] |= newbar
        rec = {}
        for label, prior, trial in [('B1barrel', oldbar, newbar), ('station1', old[:, 0], new[:, 0]), ('three_station', old.all(axis=1), new.all(axis=1))]:
            delta = trial.astype(int)-prior.astype(int)
            rec[label] = dict(before_count=int(prior.sum()), after_count=int(trial.sum()),
                before_fraction=float(prior.mean()), after_fraction=float(trial.mean()),
                delta_percentage_points=float(delta.mean()*100), paired_sampling_standard_error_pp=float(delta.std(ddof=1)/math.sqrt(n)*100),
                gains=int(np.sum(delta==1)), losses=int(np.sum(delta==-1)),
                quarter_deltas_pp=[float(a.mean()*100) for a in np.array_split(delta, 4)])
        rec['loss_ids'] = np.flatnonzero(oldbar & ~newbar).tolist()
        rec['gain_ids'] = np.flatnonzero(newbar & ~oldbar).tolist()
        rec['loss_localization'] = {}
        for metric, loss in [('B1barrel', oldbar & ~newbar), ('three_station', old.all(axis=1) & ~new.all(axis=1))]:
            categories = dict(frame_packing_loss=loss & new_without_frame,
                longitudinal_seed_seam_loss=loss & ~new_without_frame & new_full_z,
                finite_barrel_end_loss=loss & ~new_full_z)
            localized = {}
            for name, mask in categories.items():
                inds = np.flatnonzero(mask)
                loc = dict(count=len(inds), sample_ids=inds[:5].tolist())
                if len(inds):
                    etas = np.arctanh(mu[inds])
                    loc.update(abs_eta_range=[float(abs(etas).min()), float(abs(etas).max())],
                        witnesses=[dict(direction_id=int(i),eta=float(np.arctanh(mu[i])),phi_deg=float(np.degrees(phi[i])),
                            before_panels=[p['id'] for p in b1old if np.isfinite(g.midplane_hits(p,rays[i:i+1],border,True)[0])],
                            after_panels=[p['id'] for p in b1new if np.isfinite(g.midplane_hits(p,rays[i:i+1],border,True)[0])]) for i in inds[:3]])
                localized[name] = loc
            assert sum(v['count'] for v in localized.values()) == int(loss.sum())
            rec['loss_localization'][metric] = localized
        result[str(border)] = rec
    # Angular template derivations are separate: actual eta=0 lies in the
    # retained common20mm z seam, so no central coverage claim is made here.
    return result


def calculate(base, args, source_records):
    start = time.monotonic()
    baseline = json.loads(base.read_text())
    original = copy.deepcopy(baseline)
    c = copy.deepcopy(baseline['configuration']['chambers'])
    cfg = copy.deepcopy(baseline['barrel_overlap_revision'])
    h, border, even_r, odd_r = c['depth_m']/2, c['active_border_m'], 5.2, 5.75
    even_b = (even_r-h)*math.tan(math.pi/24)-c['gap_m']/2
    even_a = math.atan((even_b-border)/(even_r+h))
    odd_a = math.radians(15.+.1)-even_a
    odd_b = (odd_r+h)*math.tan(odd_a)+border
    dim = dict(even_apothem_m=even_r, odd_apothem_m=odd_r, even_half_width_m=even_b, odd_half_width_m=odd_b,
        even_full_depth_border_half_angle_deg=math.degrees(even_a), odd_full_depth_border_half_angle_deg=math.degrees(odd_a),
        full_depth_border_overlap_deg=math.degrees(even_a+odd_a)-15., odd_outer_corner_radius_m=math.hypot(odd_r+h, odd_b),
        neighbor_separating_plane_gap_m=odd_r-h-((even_r+h)*math.cos(math.pi/12)+even_b*math.sin(math.pi/12)),
        minimum_stagger_for_20mm_neighbor_plane_gap_m=h+((even_r+h)*math.cos(math.pi/12)+even_b*math.sin(math.pi/12))+.02-even_r,
        B2_conservative_radial_gap_m=6.7-h-math.hypot(odd_r+h, odd_b),
        formula='bodd=(Rodd+h)*tan(15deg+0.1deg-atan((beven-border)/(Reven+h)))+border')
    # Reuse exact pinned packing kernel with an explicitly B1-only template source.
    # No existing coil certificate enters this call, and no fixed panel is repacked.
    old_candidates = bo.candidates
    bo.candidates = b1_candidates
    try:
        panels, noframe, stats, refstats, cache = bo.pack_barrels(baseline, c, cfg, dim)
    finally:
        bo.candidates = old_candidates
    assert baseline == original, 'packing mutated immutable baseline'
    fixed = copy.deepcopy([p for p in baseline['panels'] if not (p['kind']=='barrel' and p['station']==1)])
    trial = panels+fixed
    assert fixed == [p for p in original['panels'] if not (p['kind']=='barrel' and p['station']==1)]
    # Fresh actual orientations; this tests cache use but uses the same exact kernel.
    audits = [dict(id=p['id'], **g.certify_coil_clear(p, baseline['magnetic_configuration'], .05, .02, max_cells=50000)) for p in panels]
    assert all(p['clear'] for p in audits), [p for p in audits if not p['clear']]
    conflicts = wheels.all_panel_conflicts(trial)
    assert not conflicts, conflicts[:10]
    tplcfg = dict(cfg, max_barrel_length_m=2*c['barrel_half_z_m'][0])
    templates = list(b1_candidates(c, tplcfg, dim))
    adjacent = [[templates[i]['id'], templates[(i+1)%24]['id']] for i in range(24) if g.intersects(templates[i], templates[(i+1)%24], .02)]
    assert not adjacent
    assert dim['neighbor_separating_plane_gap_m'] >= .02
    assert all(p['support_certificate']['clear'] for p in panels)
    assert len(set(p['id'] for p in trial)) == len(trial)
    assert all(g.polygon_area(p['vertices_m']) >= .25-1e-10 and np.ptp(np.asarray(p['vertices_m'])[:, 1]) >= .5-1e-10 for p in panels)
    # Adverse controls detect occupancy, duplicate solids and width without stagger.
    bt = baseline['magnetic_configuration']['coil_groups']['barrel']
    occupied = g.prism('NEGATIVE/BT-interior', 'test', [bt['center_r_m']-bt['half_r_m'],0.,0.], np.eye(3), [[-.01,-.01],[.01,-.01],[.01,.01],[-.01,.01]], .02)
    negcoil = g.certify_coil_clear(occupied, baseline['magnetic_configuration'], .05, .005)
    support_bounds = np.asarray([g.aabb(m) for m in baseline['supports']['members']])
    negsupport = wheels.support_certificate(baseline['supports']['members'][0], baseline['supports']['members'], support_bounds, .05)
    negpair = wheels.all_panel_conflicts([panels[0], dict(panels[0], id='NEGATIVE/duplicate')])
    negwide = layout._barrel('NEGATIVE/wide-without-stagger', 1, 15., even_r, -1., 1., -odd_b, odd_b, c)
    negeven = layout._barrel('NEGATIVE/even', 1, 0., even_r, -1., 1., -even_b, even_b, c)
    negative = dict(occupied_coil=negcoil, occupied_support=negsupport, duplicate_pair=negpair,
        widened_without_stagger_conflicts=g.intersects(negeven, negwide),
        changed_radius_cache_collision=bo.coil_cache_key(negwide, baseline['magnetic_configuration'], c)==bo.coil_cache_key(dict(negwide,origin_m=np.asarray(negwide['origin_m'])*(odd_r/even_r)),baseline['magnetic_configuration'],c))
    assert not negcoil['clear'] and not negsupport['clear'] and negpair and negative['widened_without_stagger_conflicts'] and not negative['changed_radius_cache_collision']
    oldb1 = [p for p in baseline['panels'] if p['kind']=='barrel' and p['station']==1]
    oldids, newids = {p['id']:p for p in oldb1}, {p['id']:p for p in panels}
    retained = [k for k in oldids.keys() & newids.keys() if identity(oldids[k]) == identity(newids[k])]
    # All actual B1 prism points have radial distance >=apothem-halfdepth.
    hcalgaps = [float(np.linalg.norm(p['origin_m'][:2]))-h-baseline['magnetic_configuration']['hcal']['barrel_corner_radius_m'] for p in panels]
    result = dict(assignment='IB-M1', input_revision=REV, status='UNSELECTED conditional scratch outline option; no active candidate adoption or engineering acceptance',
        baseline_sha256=hashlib.sha256(base.read_bytes()).hexdigest(), derivation=dim,
        sources=source_records, command=[sys.executable]+sys.argv,
        checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        undercoil=dict(BT_inner_straight_center_m=bt['center_r_m']-bt['half_r_m'], BT_warm_inner_face_m=bt['center_r_m']-bt['half_r_m']-.25,
            required_coilplane_apothem_at_most_m=bt['center_r_m']-bt['half_r_m']-.25-.05-h,
            conservative_HCAL_apothem_at_least_m=baseline['magnetic_configuration']['hcal']['barrel_corner_radius_m']+.05+h,
            conservative_bound_deficit_m=baseline['magnetic_configuration']['hcal']['barrel_corner_radius_m']+.05+h-(bt['center_r_m']-bt['half_r_m']-.25-.05-h),
            limitation='Conservative corner bound is not literal HCAL material. ActualHCAL physical blocker is assessed separately by SysArch against pinned expanded HCAL source.'),
        packing=stats, without_support_packing=refstats, fresh_cache=cache,
        dimensions_before=bo.size_report(baseline['panels'])['1'], dimensions_after=bo.size_report(trial)['1'],
        counts=dict(total_before=len(baseline['panels']), total_conditional=len(trial), B1_before=len(oldb1), B1_conditional=len(panels),
                    fixed_panel_count=len(fixed), retained_geometry_B1_count=len(retained), retained_geometry_B1_ids=sorted(retained)),
        checks=dict(baseline_unmutated=baseline==original, fixed_panels_value_equal=True, support_count=len(baseline['supports']['members']),
            all_panel_pair_count=len(trial)*(len(trial)-1)//2, all_panel_conflicts=conflicts, adjacent_full_z_template_pairs=24, neighbor_20mm_conflicts=adjacent,
            actual_orientation_uncached_coil_audits=audits, audit_cells=sum(a['cells'] for a in audits),
            all_support_certificates_fresh=True, HCAL_corner_bound_minimum_gap_m=min(hcalgaps), unresolved_cells_accepted=0, negative_controls=negative),
        coverage=coverage(baseline['panels'], trial, noframe, templates),
        limits=['No native ACTS/DD4hep/Geant4 execution, no new dependencies, no field/map modifications.',
                'No tubes, material, readout, services, timing, backgrounds, response, sag or construction qualification.',
                'Same adaptive coil kernel for packing and uncached audits; not independent coil mathematics.',
                'Straight IP-ray angular overlap and full-depth same-cassette crossings are geometric proxies only.'],
        runtime=dict(python=platform.python_version(), numpy=np.__version__, elapsed_seconds=time.monotonic()-start))
    save(args.output, result)
    save(args.outlines_output, dict(status=result['status'],input_revision=REV,panels=panels))
    print(json.dumps({k:result[k] for k in ['status','derivation','counts','dimensions_after','runtime']},indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True, help='Checkout containing the pinned revision Git objects; read-only.')
    parser.add_argument('--revision', default=REV, help='Exact input revision; this bounded checker rejects any other revision.')
    parser.add_argument('--output', type=Path, required=True, help='Result JSON path; its parent must exist.')
    parser.add_argument('--outlines-output', type=Path, help='Conditional B1-only JSON path; default derives from --output.')
    args = parser.parse_args()
    if args.revision != REV:
        parser.error('This bounded IB-M1 assignment is pinned to '+REV)
    if args.outlines_output is None:
        args.outlines_output = args.output.with_name(args.output.stem+'-unselected-B1-outlines.json')
    if args.output.resolve() == args.outlines_output.resolve():
        parser.error('--output and --outlines-output must differ')
    # Imports are deliberately delayed until every execution source is freshly
    # extracted and hash-verified. No dirty checkout module or historical proof
    # cache can supply execution code. The temporary tree is removed on exit.
    with tempfile.TemporaryDirectory(prefix='pr90-IB-M1-src-') as temporary:
        source_root = Path(temporary)
        records = []
        for path, expected in SOURCES.items():
            command = ['git', '-C', str(args.repo), 'show', args.revision+':'+path]
            blob = subprocess.check_output(command)
            actual = hashlib.sha256(blob).hexdigest()
            if actual != expected:
                raise ValueError('Pinned source hash mismatch: '+path)
            target = source_root/path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob)
            records.append(dict(locator=args.revision+':'+path, sha256=actual, bytes=len(blob), command=command))
        sys.path.insert(0, str(source_root))
        global g, layout, wheels, bo
        from tools.muon_layout import geometry as g, layout, wheels, barrel_overlap as bo
        calculate(source_root/BASE_PATH, args, records)


if __name__ == '__main__':
    main()
