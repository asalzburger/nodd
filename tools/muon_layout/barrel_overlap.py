"""DES040 isolated outer-barrel stagger and longer-cassette PROTOTYPE.

Only finite quadrilateral chamber outlines change. Magnetic sources, the complete
frame and refined endcaps are immutable inputs. Angular overlap is a straight-IP,
full-depth geometric proxy, not chamber response or construction qualification.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import platform
import time

import numpy as np

from . import geometry as g
from . import layout
from . import wheels

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / 'tools/muon_layout/barrel-overlap-config.json'
DEFAULT_OUTPUT = ROOT / 'docs/validation/DES-040/barrel-overlap-2026-10-20/candidate'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def fixed_interfaces(baseline):
    return dict(magnetic_configuration=fingerprint(baseline['magnetic_configuration']),
                supports=fingerprint(baseline['supports']),
                endcaps=fingerprint([p for p in baseline['panels'] if p['kind'] == 'endcap']))


def stagger_dimensions(chambers, config):
    """Derive width from the limiting far depth face of the retained even facet.

    At phi offset beta, a straight IP ray has tangent coordinate (R+d/2)tan(beta)
    on its limiting outer face. Inset both lateral edges by the active border.
    Odd and adjacent even angular half widths sum to15deg plus the chosen overlap.
    """
    half_depth = chambers['depth_m']/2
    radius = chambers['barrel_apothems_m'][2]
    even_half = (radius-half_depth)*math.tan(math.pi/chambers['barrel_facets'])-chambers['gap_m']/2
    border = chambers['active_border_m']
    even_angle = math.atan((even_half-border)/(radius+half_depth))
    odd_angle = math.radians(360/chambers['barrel_facets']+config['target_overlap_deg'])-even_angle
    odd_radius = config['outer_odd_apothem_m']
    odd_half = (odd_radius+half_depth)*math.tan(odd_angle)+border
    corner = math.hypot(odd_radius+half_depth, odd_half)
    return dict(even_apothem_m=radius, odd_apothem_m=odd_radius,
        radial_stagger_m=odd_radius-radius, even_half_width_m=even_half,
        odd_half_width_m=odd_half, even_full_depth_border_half_angle_deg=math.degrees(even_angle),
        odd_full_depth_border_half_angle_deg=math.degrees(odd_angle),
        target_overlap_deg=config['target_overlap_deg'],
        derived_full_depth_border_overlap_deg=math.degrees(even_angle+odd_angle)-360/chambers['barrel_facets'],
        odd_outer_corner_radius_m=corner,
        derivation='b_odd=(R_odd+d/2)*tan(15deg+overlap-atan((b_even-border)/(R_even+d/2)))+border',
        scope='Full-width templates only; finite packed z seams and hardware cuts remain separately visible.')


def candidates(chambers, config, dimensions):
    for station, (radius, zmax, phase) in enumerate(zip(chambers['barrel_apothems_m'],
            chambers['barrel_half_z_m'], chambers['barrel_phase_deg']), 1):
        half = (radius-chambers['depth_m']/2)*math.tan(math.pi/chambers['barrel_facets'])-chambers['gap_m']/2
        for facet in range(chambers['barrel_facets']):
            moved = station == 3 and facet % 2 == 1
            rr = dimensions['odd_apothem_m'] if moved else radius
            ww = dimensions['odd_half_width_m'] if moved else half
            for iz, (lo, hi) in enumerate(layout.tiles(-zmax, zmax,
                    config['max_barrel_length_m'], chambers['gap_m'])):
                yield layout._barrel(f'B{station}/F{facet:02d}/Z{iz:02d}', station,
                    phase+facet*360/chambers['barrel_facets'], rr, lo, hi, -ww, ww, chambers)


def coil_cache_key(body, magnetic, chambers, source_key=None):
    """C12 canonical orientation plus actual radius, solid and proof inputs.

    A station/ID key alone is unsafe when odd facets move. No historical proof is
    loaded. Source fingerprint also prevents reuse after changing coil geometry.
    """
    if source_key is None:
        source_key = (fingerprint(magnetic), fingerprint(chambers))
    return (source_key, body['station'],
            round(body['compartment']['phi_deg'] % 30, 9),
            round(float(np.linalg.norm(np.asarray(body['origin_m'])[:2])), 12),
            float(body['origin_m'][2]), tuple(np.asarray(body['vertices_m']).ravel()), body['depth_m'])


def pack_barrels(baseline, chambers, config, dimensions):
    magnetic = baseline['magnetic_configuration']
    members = baseline['supports']['members']
    bounds = np.asarray([g.aabb(m) for m in members])
    cache, cells = {}, 0
    # Fingerprints are fixed for this call; avoid serializing large inputs per leaf.
    source_key = (fingerprint(magnetic), fingerprint(chambers))
    def coil(body):
        nonlocal cells
        key = coil_cache_key(body, magnetic, chambers, source_key)
        if key not in cache:
            proof = g.certify_coil_clear(body, magnetic, chambers['coil_clearance_m']+config['rotation_roundoff_guard_m'],
                chambers['coil_certificate_resolution_m'], max_cells=config['max_certificate_cells'])
            cells += proof['cells']
            cache[key] = (body['id'], proof)
        source, proof = cache[key]
        return dict(proof, symmetry_source_id=source, symmetry='fresh C12 source proof with actual radius/solid/config key',
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
        source_fingerprint=source_key[0], chamber_config_fingerprint=source_key[1],
        key_fields=['magnetic/config fingerprints', 'station', 'phi modulo30deg', 'actual apothem',
                    'origin z', 'all local vertices', 'depth'], historical_certificates_loaded=0)


def size_report(panels):
    result = {}
    for station in (1, 2, 3):
        chosen = [p for p in panels if p['kind'] == 'barrel' and p['station'] == station]
        spans = np.array([np.ptp(p['vertices_m'], axis=0) for p in chosen])
        sizes = {}
        for span in spans:
            key = tuple(round(float(v), 12) for v in span)
            sizes[key] = sizes.get(key, 0)+1
        result[str(station)] = dict(count=len(chosen), tangent_width_range_m=spans[:, 0][[np.argmin(spans[:, 0]), np.argmax(spans[:, 0])]].tolist(),
            z_length_range_m=spans[:, 1][[np.argmin(spans[:, 1]), np.argmax(spans[:, 1])]].tolist(),
            dimensions=[dict(tangent_width_m=k[0], z_length_m=k[1], count=n) for k, n in sorted(sizes.items())],
            dimension_family_count=len(sizes),
            tangent_width_below_half_m_count=int(np.sum(spans[:, 0] < .5-1e-10)),
            minimum_area_m2=min(g.polygon_area(p['vertices_m']) for p in chosen))
    return result


def stagger_checks(chambers, config, dimensions):
    """All24 adjacent full-z template pairs, independent of packing exclusions."""
    template_config = dict(config, max_barrel_length_m=2*chambers['barrel_half_z_m'][2])
    templates = [p for p in candidates(chambers, template_config, dimensions) if p['station'] == 3]
    if len(templates) != 24:
        raise ValueError('expected24 unsplit outer templates')
    conflicts = []
    for i, body in enumerate(templates):
        other = templates[(i+1) % len(templates)]
        if g.intersects(body, other, config['neighbor_clearance_m']):
            conflicts.append([body['id'], other['id']])
    # This separating plane belongs to the odd prism's radial inner face. Its
    # gap is a rigorous lower bound on Euclidean distance for entire templates.
    angle = math.radians(360/chambers['barrel_facets'])
    even_support = ((dimensions['even_apothem_m']+chambers['depth_m']/2)*math.cos(angle)
                    +dimensions['even_half_width_m']*math.sin(angle))
    gap = dimensions['odd_apothem_m']-chambers['depth_m']/2-even_support
    if conflicts or gap < config['neighbor_clearance_m']:
        raise ValueError('staggered neighboring volumes fail20mm clearance')
    return dict(passed=True, checked_adjacent_template_pairs=24, conflicts=conflicts,
        required_clearance_m=config['neighbor_clearance_m'], separating_plane_gap_m=gap,
        method='Full-depth/full-z convex-prism SAT with conservative face-offset expansion; independent odd radial supporting-plane distance bound',
        scope='All accepted packed panels are subsets of these separated templates.')


def independent_controls(barrels, baseline, chambers, config, dimensions):
    """Uncached actual orientations and occupied/collision negative controls."""
    probes = []
    for body in barrels:
        proof = g.certify_coil_clear(body, baseline['magnetic_configuration'], chambers['coil_clearance_m'],
            chambers['coil_certificate_resolution_m'], max_cells=config['max_certificate_cells'])
        probes.append(dict(id=body['id'], **proof))
    magnetic = baseline['magnetic_configuration']
    bt = magnetic['coil_groups']['barrel']
    # Occupied interior far from any boundary ensures rejection has a witness.
    occupied = g.prism('NEGATIVE/BT-interior', 'test', [bt['center_r_m']-bt['half_r_m'], 0., 0.],
        np.eye(3), [[-.01, -.01], [.01, -.01], [.01, .01], [-.01, .01]], .02)
    coil_negative = g.certify_coil_clear(occupied, magnetic, chambers['coil_clearance_m'], .005)
    members = baseline['supports']['members']
    bounds = np.asarray([g.aabb(m) for m in members])
    support_negative = wheels.support_certificate(members[0], members, bounds, chambers['support_clearance_m'])
    pair_negative = wheels.all_panel_conflicts([barrels[0], dict(barrels[0], id='NEGATIVE/duplicate')])
    width = dimensions['odd_half_width_m']
    even = layout._barrel('NEGATIVE/even', 3, 0., dimensions['even_apothem_m'], -1., 1.,
        -dimensions['even_half_width_m'], dimensions['even_half_width_m'], chambers)
    no_stagger = layout._barrel('NEGATIVE/widened-without-stagger', 3, 15., dimensions['even_apothem_m'], -1., 1., -width, width, chambers)
    unshifted_conflict = g.intersects(even, no_stagger)
    stale_key = coil_cache_key(no_stagger, magnetic, chambers) == coil_cache_key(
        layout._barrel('NEGATIVE/same-id-at-new-radius', 3, 15., dimensions['odd_apothem_m'], -1., 1., -width, width, chambers), magnetic, chambers)
    if (not all(p['clear'] for p in probes) or coil_negative['clear'] or support_negative['clear']
            or not pair_negative or not unshifted_conflict or stale_key):
        raise ValueError('independent positive/adverse barrel controls failed')
    return dict(passed=True, actual_orientation_uncached_coil_audits=probes,
        adaptive_audit_count=len(probes), adaptive_cells=sum(p['cells'] for p in probes),
        occupied_coil_fixture=coil_negative, occupied_support_fixture=support_negative,
        duplicate_panel_conflict=pair_negative, widened_without_stagger_conflict=bool(unshifted_conflict),
        changed_radius_cache_key_collision=bool(stale_key),
        scope='Independent of symmetry reuse; adaptive method is the same full-volume kernel, not an independent mathematical coil model. SAT fixtures are independently located occupied solids.')


def validate_contract(baseline, config):
    chambers = baseline['configuration']['chambers']
    if config['coil_clearance_m'] != .05 or config['support_clearance_m'] != .05:
        raise ValueError('fixed50mm coil/support clearances required')
    if config['neighbor_clearance_m'] != .02 or config['gap_m'] != .02:
        raise ValueError('fixed20mm seams/stagger clearance required')
    if (chambers['barrel_apothems_m'] != [5.2, 6.7, 8.2] or chambers['barrel_half_z_m'] != [6.4456, 9.2, 12.5]
            or chambers['barrel_phase_deg'] != [0., 0., 0.] or chambers['barrel_facets'] != 24
            or chambers['depth_m'] != .5 or chambers['active_border_m'] != .03):
        raise ValueError('fixed barrel station/facet/depth/border contract changed')
    if (chambers['coil_clearance_m'] != .05 or chambers['support_clearance_m'] != .05
            or chambers['gap_m'] != .02 or chambers['min_span_m'] != .5 or chambers['min_area_m2'] != .25
            or chambers['max_subdivision_depth'] != 6):
        raise ValueError('existing clearance/useful-size/subdivision policy changed')
    if len(baseline['supports']['members']) != 484:
        raise ValueError('expected all484 fixed support members')
    if sum(p['kind'] == 'endcap' for p in baseline['panels']) != 192:
        raise ValueError('expected192 unchanged refined endcaps')
    if fixed_interfaces(baseline) != config['fixed_interface_sha256']:
        raise ValueError('fixed magnetic/support/endcap geometry fingerprint changed')
    if config['outer_odd_apothem_m'] != 8.75 or config['target_overlap_deg'] != .1:
        raise ValueError('fixed initial8.75m/0.1deg prototype choices changed')
    if config['maximum_corner_radius_m'] != 9.4 or baseline['magnetic_configuration']['map']['r_max_m'] != 9.5:
        raise ValueError('fixed9.4m corner cap within9.5m map domain required')
    if not 0 < config['rotation_roundoff_guard_m'] <= 1e-7 or config['max_barrel_length_m'] not in (3., 4., 6.):
        raise ValueError('declared3/4/6m seeds and at most0.1um rotation guard required')


def build(baseline, config):
    """Return (geometry, controls); no filesystem writes or baseline mutations."""
    validate_contract(baseline, config)
    chambers = copy.deepcopy(baseline['configuration']['chambers'])
    chambers['max_barrel_length_m'] = config['max_barrel_length_m']
    dimensions = stagger_dimensions(chambers, config)
    if dimensions['odd_outer_corner_radius_m'] >= config['maximum_corner_radius_m']:
        raise ValueError('candidate exceeds strict9.4m corner cap')
    neighbor = stagger_checks(chambers, config, dimensions)
    barrels, reference, stats, refstats, cache = pack_barrels(baseline, chambers, config, dimensions)
    endcaps = copy.deepcopy([p for p in baseline['panels'] if p['kind'] == 'endcap'])
    panels = barrels+endcaps
    conflicts = wheels.all_panel_conflicts(panels)
    if conflicts:
        raise ValueError('finite panel volume conflict: '+str(conflicts[:10]))
    ids = [p['id'] for p in panels]
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate chamber identifier')
    if len(barrels) >= sum(p['kind'] == 'barrel' for p in baseline['panels']):
        raise ValueError('longer-cassette candidate did not reduce barrel count')
    hcal = []
    for p in barrels:
        radial = float(np.linalg.norm(np.asarray(p['origin_m'])[:2]))-p['depth_m']/2
        if radial-baseline['magnetic_configuration']['hcal']['barrel_corner_radius_m'] < .05:
            hcal.append(p['id'])
        if g.polygon_area(p['vertices_m']) < chambers['min_area_m2']-1e-10:
            raise ValueError('existing minimum area violated')
        if np.ptp(np.asarray(p['vertices_m'])[:, 1]) < chambers['min_span_m']-1e-10:
            raise ValueError('existing minimum z-span violated')
    if hcal:
        raise ValueError('HCAL bound conflict: '+str(hcal[:10]))
    independent = independent_controls(barrels, baseline, chambers, config, dimensions)
    geometry = copy.deepcopy(baseline)
    geometry['panels'] = panels
    geometry['without_support_panels'] = reference+copy.deepcopy(endcaps)
    geometry['packing'], geometry['without_support_packing'] = stats, refstats
    geometry['configuration']['chambers'] = chambers
    geometry['configuration']['status'] = config['status']
    geometry['configuration']['barrel_overlap_configuration'] = 'tools/muon_layout/barrel-overlap-config.json'
    geometry['configuration']['barrel_apothem_scope'] = 'B3 odd facets use barrel_overlap_dimensions.odd_apothem_m; actual origin/basis define every solid'
    geometry['barrel_overlap_revision'] = copy.deepcopy(config)
    geometry['barrel_overlap_dimensions'] = dimensions
    maximum = max(float(np.linalg.norm(g.vertices3(p)[:, :2], axis=1).max()) for p in panels)
    previous = max(float(np.linalg.norm(g.vertices3(p)[:, :2], axis=1).max()) for p in baseline['panels'])
    if maximum >= config['maximum_corner_radius_m']:
        raise ValueError('actual packed corner violates strict9.4m cap')
    geometry['validation'] = dict(panel_panel_conflicts=[], fresh_barrel_coil_certificates=len(barrels),
        fresh_barrel_support_certificates=len(barrels), accepted_coil_certificates=len(panels),
        accepted_support_certificates=len(panels), coil_clearance_m=.05, panel_support_clearance_m=.05,
        coil_certificate_cells=cache['cells'], unresolved_cells_accepted=0, hcal_bound_conflicts=[],
        retained_endcap_count=len(endcaps), scope='All barrel coil/support proofs fresh;192 endcaps retain unchanged historical certificates; every panel pair freshly checked.')
    before, after = size_report(baseline['panels']), size_report(panels)
    controls = dict(passed=True, status=config['status'], input_revision=config['input_revision'],
        counts={kind: {str(j): sum(p['kind'] == kind and p['station'] == j for p in panels) for j in (1, 2, 3)} for kind in ('barrel', 'endcap')},
        total_panels=len(panels), barrel_count_before=sum(v['count'] for v in before.values()),
        barrel_count_after=len(barrels), barrel_count_reduction=sum(v['count'] for v in before.values())-len(barrels),
        dimensions_before=before, dimensions_after=after, stagger=dimensions,
        stagger_volume_checks=neighbor, packing=stats, without_support_packing=refstats,
        coil_certificate_cache=cache, independent_controls=independent,
        all_panel_pair_count=len(panels)*(len(panels)-1)//2, panel_panel_conflicts=conflicts,
        all_support_members_checked_per_barrel=len(baseline['supports']['members']),
        fixed_interfaces_retained=fixed_interfaces(geometry) == fixed_interfaces(baseline),
        endcaps_retained_value_equal=endcaps == [p for p in baseline['panels'] if p['kind'] == 'endcap'],
        supports_retained_value_equal=geometry['supports'] == baseline['supports'],
        magnetic_configuration_retained_exact=geometry['magnetic_configuration'] == baseline['magnetic_configuration'],
        envelope=dict(maximum_corner_radius_before_m=previous, maximum_corner_radius_after_m=maximum,
            maximum_corner_radius_growth_m=maximum-previous, strict_corner_radius_cap_m=config['maximum_corner_radius_m'],
            joint_map_maximum_radius_m=9.5, minimum_radial_map_margin_m=9.5-maximum,
            barrel_half_z_m=chambers['barrel_half_z_m'],
            actual_barrel_abs_z_max_m={str(j): max(float(abs(g.vertices3(p)[:, 2]).max()) for p in barrels if p['station'] == j) for j in (1, 2, 3)}),
        useful_size_policy='Retained layout._children policy: z-splits require each child≥0.5m; all splits require area≥0.25m². Tangential widths have no universal0.5m floor (baseline already contains narrower B2 fragments).',
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
        before=controls['dimensions_before'][str(j)]['count'], after=controls['counts']['barrel'][str(j)]) for j in (1, 2, 3)]
    save(args.output/'shape-change-mapping.json', mapping)
    sources = [source, args.config, Path(__file__), ROOT/'tools/muon_layout/geometry.py',
        ROOT/'tools/muon_layout/layout.py', ROOT/'tools/muon_layout/wheels.py',
        ROOT/'tools/toroid_prototype/geometry.py', ROOT/'docs/design/DES-040-muon-chambers-frame.md']
    controls.update(sources={wheels.relative(p): digest(p) for p in sources},
        command=['python3', '-B', '-m', 'tools.muon_layout.barrel_overlap', '--geometry', wheels.relative(source),
                 '--config', wheels.relative(args.config), '--output', wheels.relative(args.output)],
        runtime=dict(python=platform.python_version(), numpy=np.__version__, seconds=time.monotonic()-started),
        outputs={p.name: digest(p) for p in args.output.iterdir() if p.is_file() and p.name != 'geometry-controls.json'})
    save(args.output/'geometry-controls.json', controls)
    print(json.dumps(dict(passed=controls['passed'], counts=controls['counts'], seconds=controls['runtime']['seconds']), indent=2))


if __name__ == '__main__':
    main()
