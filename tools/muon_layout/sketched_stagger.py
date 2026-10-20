"""DES040 isolated sketched B1 stagger and B2 half-pitch PROTOTYPE.

B1 coil-plane facets stay at5.20m and inter-coil facets move inward to4.63m.
B2 is freshly packed at+7.5degrees. Fixed B3, endcaps, magnets and supports are
retained exactly. Full-volume checks qualify outlines, not construction,
backgrounds, timing response, reconstructed efficiency or momentum resolution.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path
import platform
import time

import numpy as np

from . import barrel_overlap as previous
from . import geometry as g
from . import layout
from . import wheels

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / 'tools/muon_layout/sketched-stagger-config.json'
DEFAULT_OUTPUT = ROOT / 'docs/validation/DES-040/sketched-stagger-2026-10-20/candidate'
digest, fingerprint, save = previous.digest, previous.fingerprint, previous.save
size_report = previous.size_report


def fixed_interfaces(baseline):
    return dict(previous.fixed_interfaces(baseline),
        B3=fingerprint([p for p in baseline['panels'] if p['kind'] == 'barrel' and p['station'] == 3]))


def stagger_dimensions(chambers, config):
    """Same-cassette full-depth angular overlap with30mm edge border.

    Both facing depth planes must lie in a single finite rectangle. Its far
    radial plane therefore limits the angular interval. Odd inner facets use
    that same constraint; moving inward does not make their near plane limiting.
    """
    h = chambers['depth_m']/2
    radius = chambers['barrel_apothems_m'][0]
    even_half = (radius-h)*math.tan(math.pi/chambers['barrel_facets'])-chambers['gap_m']/2
    border = chambers['active_border_m']
    even_angle = math.atan((even_half-border)/(radius+h))
    pitch = 360/chambers['barrel_facets']
    odd_angle = math.radians(pitch+config['target_overlap_deg'])-even_angle
    odd_radius = config['inner_odd_apothem_m']
    odd_half = (odd_radius+h)*math.tan(odd_angle)+border
    return dict(even_apothem_m=radius, odd_apothem_m=odd_radius,
        radial_stagger_m=odd_radius-radius, even_half_width_m=even_half,
        odd_half_width_m=odd_half, even_full_depth_border_half_angle_deg=math.degrees(even_angle),
        odd_full_depth_border_half_angle_deg=math.degrees(odd_angle),
        target_overlap_deg=config['target_overlap_deg'],
        derived_full_depth_border_overlap_deg=math.degrees(even_angle+odd_angle)-pitch,
        odd_outer_corner_radius_m=math.hypot(odd_radius+h, odd_half),
        derivation='b_odd=(R_odd+d/2)*tan(15deg+overlap-atan((b_even-border)/(R_even+d/2)))+border',
        scope='Full-width templates only; packed finite seams and hardware cuts remain explicit.')


def candidates(chambers, config, dimensions):
    """Fresh B1/B2 seeds only; B3 and endcap solids are never regenerated."""
    for station in (1, 2):
        radius = chambers['barrel_apothems_m'][station-1]
        zmax = chambers['barrel_half_z_m'][station-1]
        phase = chambers['barrel_phase_deg'][station-1]
        half = (radius-chambers['depth_m']/2)*math.tan(math.pi/chambers['barrel_facets'])-chambers['gap_m']/2
        for facet in range(chambers['barrel_facets']):
            moved = station == 1 and facet % 2 == 1
            rr = dimensions['odd_apothem_m'] if moved else radius
            ww = dimensions['odd_half_width_m'] if moved else half
            for iz, (lo, hi) in enumerate(layout.tiles(-zmax, zmax,
                    config['max_barrel_length_m'], chambers['gap_m'])):
                yield layout._barrel(f'B{station}/F{facet:02d}/Z{iz:02d}', station,
                    phase+facet*360/chambers['barrel_facets'], rr, lo, hi, -ww, ww, chambers)


def coil_cache_key(body, magnetic, chambers, source_key=None):
    """Actual transform, solid, radius, phase and all proof inputs; no IDs.

    Even C12-related orientations have different keys. Cache reuse only avoids
    repeating identical trial solids in no-frame/frame packing and seam merging.
    """
    if source_key is None:
        source_key = (fingerprint(magnetic), fingerprint(chambers))
    return (source_key, body['station'],
        round(body['compartment']['phi_deg'] % 360, 9),
        round(float(np.linalg.norm(np.asarray(body['origin_m'])[:2])), 12),
        tuple(np.asarray(body['origin_m']).ravel()), tuple(np.asarray(body['basis']).ravel()),
        tuple(np.asarray(body['vertices_m']).ravel()), body['depth_m'])


def pack_barrels(baseline, chambers, config, dimensions):
    magnetic = baseline['magnetic_configuration']
    members = baseline['supports']['members']
    bounds = np.asarray([g.aabb(m) for m in members])
    cache, cells = {}, 0
    # Fingerprints are fixed for this call; avoid serializing large inputs per leaf.
    source_key = (fingerprint(magnetic), fingerprint(chambers), fingerprint(config))
    def coil(body):
        nonlocal cells
        key = coil_cache_key(body, magnetic, chambers, source_key)
        if key not in cache:
            proof = g.certify_coil_clear(body, magnetic, chambers['coil_clearance_m']+config['rotation_roundoff_guard_m'],
                chambers['coil_certificate_resolution_m'], max_cells=config['max_certificate_cells'])
            cells += proof['cells']
            cache[key] = (body['id'], proof)
        source, proof = cache[key]
        return dict(proof, symmetry_source_id=source, symmetry='fresh actual-orientation source proof; no historical or rotated proof reuse',
                    rotation_roundoff_guard_m=config['rotation_roundoff_guard_m'], source_fingerprint=source_key[0])
    initial = list(candidates(chambers, config, dimensions))
    def pack(with_support):
        accepted, rejected, splits = [], [], 0
        def visit(body, depth):
            nonlocal splits
            proof = coil(body)
            sproof = wheels.support_certificate(body, members, bounds, chambers['support_clearance_m']) if proof['clear'] and with_support else None
            if proof['clear'] and (sproof is None or sproof['clear']):
                record = dict(body, coil_certificate=proof)
                if sproof is not None:
                    record['support_certificate'] = sproof
                accepted.append(record)
                return
            children = layout._children(body, chambers, depth) if depth < chambers['max_subdivision_depth'] else []
            if children:
                splits += 1
                for child in children:
                    visit(child, depth+1)
            else:
                rejected.append(dict(id=body['id'], reason=proof['reason'] if not proof['clear'] else 'support clearance',
                    coil_certificate=proof, support_ids=sproof['conflicts'] if sproof else []))
        for body in initial:
            visit(body, 0)
        # Only adjacent rectangles in the identical tangent lane may remove an
        # existing z seam. Certify the complete union, including the filled seam,
        # before accepting it. No rejected hardware corridor is bridged.
        before_merge = len(accepted)
        groups = {}
        for body in accepted:
            lane = (body['station'], body['compartment']['phi_deg'],
                    tuple(body['compartment']['tangent_m']))
            groups.setdefault(lane, []).append(body)
        merged, attempts, rejected_merges = [], 0, 0
        for lane in sorted(groups):
            ordered = sorted(groups[lane], key=lambda p: p['compartment']['z_m'][0])
            current = ordered[0]
            for following in ordered[1:]:
                lo, hi = current['compartment']['z_m']
                next_lo, next_hi = following['compartment']['z_m']
                if (abs(next_lo-hi-chambers['gap_m']) > 1e-10
                        or next_hi-lo > config['max_barrel_length_m']+1e-10):
                    merged.append(current)
                    current = following
                    continue
                attempts += 1
                radius = float(np.linalg.norm(np.asarray(current['origin_m'])[:2]))
                candidate = layout._barrel(current['id']+'/MERGED', current['station'],
                    current['compartment']['phi_deg'], radius, lo, next_hi,
                    *current['compartment']['tangent_m'], chambers)
                proof = coil(candidate)
                sproof = wheels.support_certificate(candidate, members, bounds,
                    chambers['support_clearance_m']) if proof['clear'] and with_support else None
                if proof['clear'] and (sproof is None or sproof['clear']):
                    current = dict(candidate, coil_certificate=proof,
                        merged_from=current.get('merged_from', [current['id']])+following.get('merged_from', [following['id']]))
                    if sproof is not None:
                        current['support_certificate'] = sproof
                else:
                    rejected_merges += 1
                    merged.append(current)
                    current = following
            merged.append(current)
        accepted = merged
        return accepted, dict(initial_compartments=len(initial), subdivisions=splits,
            accepted=len(accepted), rejected_leaves=rejected,
            z_seam_merging=dict(before=before_merge, after=len(accepted), attempted=attempts,
                accepted=before_merge-len(accepted), rejected=rejected_merges,
                scope='Identical tangent lanes; only adjacent20mm seams; each complete union freshly coil/support certified; maximum seed length retained.'))
    reference, refstats = pack(False)
    accepted, stats = pack(True)
    return accepted, reference, stats, refstats, dict(cells=cells, unique_certificates=len(cache),
        source_fingerprint=source_key[0], chamber_config_fingerprint=source_key[1], prototype_config_fingerprint=source_key[2],
        key_fields=['magnetic/config fingerprints', 'station', 'actual phi modulo360deg', 'actual apothem',
                    'full orientation basis', 'origin z', 'all local vertices', 'depth', 'prototype config fingerprint'], historical_certificates_loaded=0)

def stagger_checks(chambers, config, dimensions):
    """All24 full-z neighboring B1 template pairs, before hardware cuts."""
    template_config = dict(config, max_barrel_length_m=2*max(chambers['barrel_half_z_m']))
    templates = [p for p in candidates(chambers, template_config, dimensions) if p['station'] == 1]
    if len(templates) != 24:
        raise ValueError('expected24 unsplit B1 templates')
    conflicts = [[body['id'], templates[(i+1) % 24]['id']]
        for i, body in enumerate(templates)
        if g.intersects(body, templates[(i+1) % 24], config['neighbor_clearance_m'])]
    angle = math.radians(360/chambers['barrel_facets'])
    odd_support = ((dimensions['odd_apothem_m']+chambers['depth_m']/2)*math.cos(angle)
                   +dimensions['odd_half_width_m']*math.sin(angle))
    gap = dimensions['even_apothem_m']-chambers['depth_m']/2-odd_support
    if conflicts or gap < config['neighbor_clearance_m']:
        raise ValueError('inward stagger fails20mm neighboring volume clearance')
    return dict(passed=True, checked_adjacent_template_pairs=24, conflicts=conflicts,
        required_clearance_m=config['neighbor_clearance_m'], separating_plane_gap_m=gap,
        method='Full-depth/full-z convex-prism SAT with conservative face-offset expansion; independent even radial supporting-plane distance bound',
        scope='Accepted packed B1 panels are subsets of these separated templates.')


def hcal_checks(barrels, config):
    """Sufficient whole-volume bounds above HCAL and the known service reservation."""
    records = []
    for body in barrels:
        lower = float(np.linalg.norm(np.asarray(body['origin_m'])[:2]))-body['depth_m']/2
        margin = lower-config['known_service_jacket_outer_radius_m']
        hcal_margin = lower-config['installed_hcal_corner_radius_m']
        records.append(dict(id=body['id'], radial_lower_bound_m=lower,
                            known_service_clearance_lower_bound_m=margin,
                            installed_hcal_clearance_lower_bound_m=hcal_margin,
                            clear=min(margin, hcal_margin) >= config['hcal_clearance_m']-1e-12))
    conflicts = [r['id'] for r in records if not r['clear']]
    return dict(passed=not conflicts, conflicts=conflicts,
        required_clearance_m=config['hcal_clearance_m'],
        known_service_reservation_outer_radius_m=config['known_service_jacket_outer_radius_m'],
        installed_hcal_corner_bound_m=config['installed_hcal_corner_radius_m'],
        minimum_known_service_clearance_lower_bound_m=min(r['known_service_clearance_lower_bound_m'] for r in records),
        minimum_installed_hcal_clearance_lower_bound_m=min(r['installed_hcal_clearance_lower_bound_m'] for r in records),
        records=records,
        scope='Conservative full-z radial bounds separately enclose installed HCAL and the known DES034 ECAL external-water egress jacket reservation. Cylinders are bounds, not occupied material. Unimplemented external HCAL collectors/cable routing are unqualified; actual-source assessment remains separate.')


def independent_controls(barrels, baseline, chambers, config, dimensions):
    """Uncached actual-orientation proofs plus physically occupied controls."""
    probes = [dict(id=body['id'], **g.certify_coil_clear(body,
        baseline['magnetic_configuration'], chambers['coil_clearance_m'],
        chambers['coil_certificate_resolution_m'], max_cells=config['max_certificate_cells']))
        for body in barrels]
    magnetic = baseline['magnetic_configuration']
    bt = magnetic['coil_groups']['barrel']
    occupied = g.prism('NEGATIVE/BT-interior', 'test',
        [bt['center_r_m']-bt['half_r_m'], 0., 0.], np.eye(3),
        [[-.01, -.01], [.01, -.01], [.01, .01], [-.01, .01]], .02)
    coil_negative = g.certify_coil_clear(occupied, magnetic, chambers['coil_clearance_m'], .005)
    members = baseline['supports']['members']
    bounds = np.asarray([g.aabb(m) for m in members])
    support_negative = wheels.support_certificate(members[0], members, bounds,
                                                   chambers['support_clearance_m'])
    pair_negative = wheels.all_panel_conflicts([barrels[0], dict(barrels[0], id='NEGATIVE/duplicate')])
    even = layout._barrel('NEGATIVE/even', 1, 0., dimensions['even_apothem_m'], -1., 1.,
        -dimensions['even_half_width_m'], dimensions['even_half_width_m'], chambers)
    no_stagger = layout._barrel('NEGATIVE/widened-without-stagger', 1, 15.,
        dimensions['even_apothem_m'], -1., 1.,
        -dimensions['odd_half_width_m'], dimensions['odd_half_width_m'], chambers)
    changed_radius = layout._barrel('NEGATIVE/new-radius', 1, 15.,
        dimensions['odd_apothem_m'], -1., 1.,
        -dimensions['odd_half_width_m'], dimensions['odd_half_width_m'], chambers)
    changed_phase = layout._barrel('NEGATIVE/new-phase', 1, 22.5,
        dimensions['even_apothem_m'], -1., 1.,
        -dimensions['odd_half_width_m'], dimensions['odd_half_width_m'], chambers)
    unshifted_conflict = g.intersects(even, no_stagger)
    radius_collision = coil_cache_key(no_stagger, magnetic, chambers) == coil_cache_key(changed_radius, magnetic, chambers)
    phase_collision = coil_cache_key(no_stagger, magnetic, chambers) == coil_cache_key(changed_phase, magnetic, chambers)
    below_services = layout._barrel('NEGATIVE/R4.60-service-clearance', 1, 15., 4.60,
        -1., 1., -dimensions['odd_half_width_m'], dimensions['odd_half_width_m'], chambers)
    hcal_negative = hcal_checks([below_services], config)
    if (not all(p['clear'] for p in probes) or coil_negative['clear'] or support_negative['clear']
            or not pair_negative or not unshifted_conflict or radius_collision or phase_collision
            or hcal_negative['passed']):
        raise ValueError('independent positive/adverse sketched-stagger controls failed')
    return dict(passed=True, actual_orientation_uncached_coil_audits=probes,
        adaptive_audit_count=len(probes), adaptive_cells=sum(p['cells'] for p in probes),
        occupied_coil_fixture=coil_negative, occupied_support_fixture=support_negative,
        duplicate_panel_conflict=pair_negative, widened_without_stagger_conflict=bool(unshifted_conflict),
        changed_radius_cache_key_collision=radius_collision, changed_phase_cache_key_collision=phase_collision,
        R4_60_service_clearance_diagnostic=hcal_negative,
        scope='Same full-volume coil kernel without cache reuse, not independent coil mathematics; occupied SAT/coil fixtures and insufficient service margin are negative controls.')


def validate_contract(baseline, config):
    chambers = baseline['configuration']['chambers']
    if any(config[k] != .05 for k in ('coil_clearance_m', 'support_clearance_m', 'hcal_clearance_m')):
        raise ValueError('fixed50mm coil/support/HCAL clearances required')
    if config['neighbor_clearance_m'] != .02 or config['gap_m'] != .02:
        raise ValueError('fixed20mm seams/stagger clearance required')
    if (chambers['barrel_apothems_m'] != [5.2, 6.7, 8.2]
            or chambers['barrel_half_z_m'] != [6.4456, 9.2, 12.5]
            or chambers['barrel_phase_deg'] != [0., 0., 0.]
            or chambers['depth_m'] != .5 or chambers['active_border_m'] != .03):
        raise ValueError('fixed baseline barrel station/depth/border contract changed')
    if fingerprint(chambers) != config['fixed_chamber_configuration_sha256']:
        raise ValueError('fixed chamber policy fingerprint changed')
    if len(baseline['panels']) != 888 or len(baseline['supports']['members']) != 484:
        raise ValueError('expected888 baseline panels and all484 supports')
    if (sum(p['kind'] == 'endcap' for p in baseline['panels']) != 192
            or sum(p['kind'] == 'barrel' and p['station'] == 3 for p in baseline['panels']) != 432):
        raise ValueError('expected fixed432 B3 and192 endcaps')
    if fixed_interfaces(baseline) != config['fixed_interface_sha256']:
        raise ValueError('fixed magnetic/support/B3/endcap geometry fingerprint changed')
    if (config['inner_odd_apothem_m'] != 4.63 or config['middle_barrel_phase_deg'] != 7.5
            or config['target_overlap_deg'] != .1 or config['max_barrel_length_m'] != 4.):
        raise ValueError('declared R4.63/+7.5deg/0.1deg/4m prototype choices changed')
    if (config['maximum_corner_radius_m'] != 9.4
            or baseline['magnetic_configuration']['map']['r_max_m'] != 9.5
            or config['known_service_jacket_outer_radius_m'] != 4.325
            or config['installed_hcal_corner_radius_m'] != 4.23946):
        raise ValueError('fixed map/corner/service-envelope bounds changed')
    if not 0 < config['rotation_roundoff_guard_m'] <= 1e-7:
        raise ValueError('at most0.1um rotation guard required')


def build(baseline, config):
    """Return deterministic geometry,controls without writes or input mutation."""
    validate_contract(baseline, config)
    chambers = copy.deepcopy(baseline['configuration']['chambers'])
    chambers['max_barrel_length_m'] = config['max_barrel_length_m']
    chambers['barrel_phase_deg'][1] = config['middle_barrel_phase_deg']
    dimensions = stagger_dimensions(chambers, config)
    neighbor = stagger_checks(chambers, config, dimensions)
    changed, reference, stats, refstats, cache = pack_barrels(baseline, chambers, config, dimensions)
    fixed = copy.deepcopy([p for p in baseline['panels']
        if p['kind'] == 'endcap' or p['station'] == 3])
    panels = changed+fixed
    conflicts = wheels.all_panel_conflicts(panels)
    if conflicts:
        raise ValueError('finite panel volume conflict: '+str(conflicts[:10]))
    if len({p['id'] for p in panels}) != len(panels):
        raise ValueError('duplicate chamber identifier')
    hcal = hcal_checks(changed, config)
    if not hcal['passed']:
        raise ValueError('50mm HCAL/service-envelope conflict: '+str(hcal['conflicts'][:10]))
    for body in changed:
        if g.polygon_area(body['vertices_m']) < chambers['min_area_m2']-1e-10:
            raise ValueError('existing minimum area violated')
        zspan = np.ptp(np.asarray(body['vertices_m'])[:, 1])
        if zspan < chambers['min_span_m']-1e-10 or zspan > config['max_barrel_length_m']+1e-10:
            raise ValueError('existing z-size policy violated')
        if abs(g.vertices3(body)[:, 2]).max() > chambers['barrel_half_z_m'][body['station']-1]+1e-10:
            raise ValueError('barrel z endpoint changed')
    independent = independent_controls(changed, baseline, chambers, config, dimensions)
    geometry = copy.deepcopy(baseline)
    geometry['panels'] = panels
    fixed_reference = copy.deepcopy([p for p in baseline['without_support_panels']
        if p['kind'] == 'endcap' or p['station'] == 3])
    geometry['without_support_panels'] = reference+fixed_reference
    geometry['packing'], geometry['without_support_packing'] = stats, refstats
    geometry['configuration']['chambers'] = chambers
    geometry['configuration']['status'] = config['status']
    geometry['configuration']['sketched_stagger_configuration'] = 'tools/muon_layout/sketched-stagger-config.json'
    geometry['configuration']['barrel_apothem_scope'] = ('B1 odd facets use sketched_stagger_dimensions.odd_apothem_m; '
        'B3 odd facets retain barrel_overlap_dimensions.odd_apothem_m; actual origin/basis define every solid')
    geometry['sketched_stagger_revision'] = copy.deepcopy(config)
    geometry['sketched_stagger_dimensions'] = dimensions
    maximum = max(float(np.linalg.norm(g.vertices3(p)[:, :2], axis=1).max()) for p in panels)
    previous_max = max(float(np.linalg.norm(g.vertices3(p)[:, :2], axis=1).max()) for p in baseline['panels'])
    if maximum >= config['maximum_corner_radius_m']:
        raise ValueError('actual packed corner violates strict9.4m cap')
    geometry['validation'] = dict(panel_panel_conflicts=[],
        fresh_changed_barrel_coil_certificates=len(changed),
        fresh_changed_barrel_support_certificates=len(changed),
        accepted_coil_certificates=len(panels), accepted_support_certificates=len(panels),
        coil_clearance_m=.05, panel_support_clearance_m=.05, hcal_clearance_m=.05,
        coil_certificate_cells=cache['cells'], unresolved_cells_accepted=0,
        hcal_bound_conflicts=hcal['conflicts'], retained_B3_count=432, retained_endcap_count=192,
        scope='Only B1/B2 coil/support proofs are freshly constructed; fixed432 B3 and192 endcaps retain value-equal historical certificates. All panel pairs are freshly checked.')
    before, after = size_report(baseline['panels']), size_report(panels)
    controls = dict(passed=True, status=config['status'], input_revision=config['input_revision'],
        counts={kind: {str(j): sum(p['kind'] == kind and p['station'] == j for p in panels)
            for j in (1, 2, 3)} for kind in ('barrel', 'endcap')},
        total_panels=len(panels), fresh_changed_panel_count=len(changed),
        barrel_count_before=sum(v['count'] for v in before.values()),
        barrel_count_after=sum(v['count'] for v in after.values()),
        barrel_count_change=sum(v['count'] for v in after.values())-sum(v['count'] for v in before.values()),
        count_reduction_required=False, dimensions_before=before, dimensions_after=after,
        stagger=dimensions, middle_barrel_phase_deg=config['middle_barrel_phase_deg'],
        stagger_volume_checks=neighbor, packing=stats, without_support_packing=refstats,
        coil_certificate_cache=cache, independent_controls=independent,
        hcal_and_known_service_bounds=hcal,
        all_panel_pair_count=len(panels)*(len(panels)-1)//2, panel_panel_conflicts=conflicts,
        all_support_members_checked_per_changed_barrel=len(baseline['supports']['members']),
        fixed_interfaces_retained=fixed_interfaces(geometry) == fixed_interfaces(baseline),
        fixed_panels_retained_value_equal=fixed == [p for p in baseline['panels']
            if p['kind'] == 'endcap' or p['station'] == 3],
        endcaps_retained_value_equal=[p for p in panels if p['kind'] == 'endcap'] ==
            [p for p in baseline['panels'] if p['kind'] == 'endcap'],
        B3_retained_value_equal=[p for p in panels if p['kind'] == 'barrel' and p['station'] == 3] ==
            [p for p in baseline['panels'] if p['kind'] == 'barrel' and p['station'] == 3],
        supports_retained_value_equal=geometry['supports'] == baseline['supports'],
        magnetic_configuration_retained_exact=geometry['magnetic_configuration'] == baseline['magnetic_configuration'],
        envelope=dict(maximum_corner_radius_before_m=previous_max, maximum_corner_radius_after_m=maximum,
            maximum_corner_radius_growth_m=maximum-previous_max,
            strict_corner_radius_cap_m=config['maximum_corner_radius_m'],
            joint_map_maximum_radius_m=9.5, minimum_radial_map_margin_m=9.5-maximum,
            barrel_half_z_m=chambers['barrel_half_z_m'],
            actual_barrel_abs_z_max_m={str(j): max(float(abs(g.vertices3(p)[:, 2]).max())
                for p in panels if p['kind'] == 'barrel' and p['station'] == j) for j in (1, 2, 3)}),
        useful_size_policy='Retained layout._children z subdivision>=0.5m and area>=0.25m2; no universal0.5m tangential-width floor.',
        max_z_seam_merging=stats['z_seam_merging'], limits=config['limits'])
    return geometry, controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry', type=Path)
    parser.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    started = time.monotonic()
    config = json.loads(args.config.read_text())
    source = args.geometry or ROOT/config['base_geometry']
    if digest(source) != config['base_geometry_sha256']:
        raise ValueError('pinned baseline geometry bytes changed')
    baseline = json.loads(source.read_text())
    geometry, controls = build(baseline, config)
    args.output.mkdir(parents=True, exist_ok=True)
    save(args.output/'geometry.json', geometry)
    mapping = wheels.shape_mapping(baseline['panels'], geometry['panels'])
    mapping['replacements'] = [dict(station=j, kind='barrel',
        before=controls['dimensions_before'][str(j)]['count'],
        after=controls['counts']['barrel'][str(j)]) for j in (1, 2)]
    save(args.output/'shape-change-mapping.json', mapping)
    sources = [source, args.config, Path(__file__), ROOT/'tools/muon_layout/geometry.py',
        ROOT/'tools/muon_layout/layout.py', ROOT/'tools/muon_layout/wheels.py',
        ROOT/'tools/muon_layout/barrel_overlap.py', ROOT/'tools/toroid_prototype/geometry.py',
        ROOT/'docs/design/DES-040-muon-chambers-frame.md']
    controls.update(sources={wheels.relative(p): digest(p) for p in sources},
        command=['python3', '-B', '-m', 'tools.muon_layout.sketched_stagger',
            '--geometry', wheels.relative(source), '--config', wheels.relative(args.config),
            '--output', wheels.relative(args.output)],
        runtime=dict(python=platform.python_version(), numpy=np.__version__, seconds=time.monotonic()-started),
        outputs={p.name: digest(p) for p in args.output.iterdir()
            if p.is_file() and p.name != 'geometry-controls.json'})
    save(args.output/'geometry-controls.json', controls)
    print(json.dumps(dict(passed=controls['passed'], counts=controls['counts'],
        seconds=controls['runtime']['seconds']), indent=2))


if __name__ == '__main__':
    main()
