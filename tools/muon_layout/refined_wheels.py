"""Isolated DES040 refined quadrilateral chamber-outline PROTOTYPE.

Historical geometry is immutable input. Every new cassette gets a volume proof;
all frame members, magnets and barrel panels are copied byte-for-byte in JSON
value terms. The nominal eta aperture, polygon losses and unavoidable coil
reservations are reported separately. No engineering or response acceptance.
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
from . import wheels
from .wheel_inventory import dimensions

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / 'tools/muon_layout/refined-wheels-config.json'
DEFAULT_OUTPUT = ROOT / 'docs/validation/DES-040/refined-wheels-2026-10-20/candidate'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def aperture_radius(spec, config):
    """Circumscribed hole apothem at the depth face nearest the IP."""
    return (spec['abs_z_m'] - config['depth_m']/2) / math.sinh(config['eta_limit'])


def radial_quad(u0, u1, w0, w1):
    if not 0 < u0 < u1 or min(w0, w1) <= 0:
        raise ValueError('positive nondegenerate radial trapezoid required')
    return [[u0, -w0], [u1, -w1], [u1, w1], [u0, w0]]


def outer_apothem(radius, slope, intercept):
    """Positive root of u²+(slope*u+intercept)²=radius²."""
    aa = 1 + slope*slope
    return (-slope*intercept + math.sqrt(aa*radius*radius-intercept*intercept))/aa


def trapezoid(u0, u1, alpha, half_seam):
    return radial_quad(u0, u1, u0*math.tan(alpha)-half_seam/math.cos(alpha),
                       u1*math.tan(alpha)-half_seam/math.cos(alpha))


def make_family(spec, station, family, vertices, sectors, phase, config):
    bodies = []
    v = np.asarray(vertices)
    for side, label in ((-1, 'M'), (1, 'P')):
        for sector in range(sectors):
            phi = phase + 360*sector/sectors
            a = math.radians(phi)
            q = np.array([[math.cos(a), -math.sin(a), 0.],
                          [math.sin(a), math.cos(a), 0.], [0., 0., 1.]])
            body = g.prism(f'E{label}{station}/REFINED/{family}/S{sector:02d}',
                'endcap', [0., 0., side*spec['abs_z_m']], q, vertices,
                config['depth_m'], station=station, side=side, face='trapezoid',
                wheel=spec['name'], family=family, whole_sector=True,
                ordinary_radial_module_cap_exempt=True,
                cassette_size_exception=config['cassette_size_exemptions'],
                compartment=dict(phi_deg=[phi-180/sectors, phi+180/sectors],
                                 radial_m=[float(v[:, 0].min()), spec['outer_radius_m']]))
            body['dimensions'] = dimensions(body)
            bodies.append(body)
    return bodies


def inner_wheel(magnetic, config):
    spec = config['stations']['1']
    old_spec = dict(station=1, abs_z_m=spec['abs_z_m'],
        inner_radius_m=aperture_radius(spec, config), outer_radius_m=spec['outer_radius_m'],
        sectors=spec['sectors'], phase_deg=spec['phase_deg'],
        seam_half_width_at_bore_m=config['inner_core_bore_half_gap_m'],
        extra_BT_box_margin_m=config['certification_guard_m'])
    d = wheels.wheel_dimensions(old_spec, magnetic, config['coil_clearance_m'])
    core = radial_quad(d['u0_m'], d['u1_m'], d['inner_base_m']/2, d['outer_base_m']/2)
    panels = make_family(spec, 1, 'CORE', core, 12, spec['phase_deg'], config)
    slope, intercept = d['seam_slope'], d['seam_intercept_m']
    # The core edge already exists: a full20mm normal offset is needed
    # between that edge and the filler, not a second10mm half-gap.
    inset = config['seam_width_m'] * math.sqrt(1+slope*slope)
    bt = magnetic['coil_groups']['barrel']
    radius = bt['center_r_m']-bt['half_r_m']
    a = magnetic['warm']['normal_m']/2+config['coil_clearance_m']
    guard = config['certification_guard_m']
    slot_lo, slot_hi = radius-a, radius+a
    alpha = math.pi/12
    xend = d['u1_m']*math.cos(alpha)+d['outer_base_m']/2*math.sin(alpha)
    ranges = {'PRE_SLOT': (aperture_radius(spec, config), slot_lo-guard),
              'POST_SLOT': (slot_hi+guard, xend)}
    for name, (lo, hi) in ranges.items():
        vertices = radial_quad(lo, hi, slope*lo+intercept-inset, slope*hi+intercept-inset)
        panels += make_family(spec, 1, name, vertices, 12, bt['phi_offset_deg'], config)
    required_half = magnetic['warm']['tangent_m']/2+config['coil_clearance_m']
    # This is an area accounting statement, not a claim that the guard is material.
    conservative_slot_area = 2*((slope*(slot_hi**2-slot_lo**2)/2 +
                                intercept*(slot_hi-slot_lo)) - required_half*(slot_hi-slot_lo))
    return panels, dict(core=d, filler_u_ranges_m={k: list(v) for k, v in ranges.items()},
        filler_to_core_normal_seam_m=inset/math.sqrt(1+slope*slope),
        BT_clearance_box_local_xy_m=[slot_lo, slot_hi, -required_half, required_half],
        residual_affine_guard_area_beyond_BT_clearance_boxes_one_end_m2=12*conservative_slot_area,
        retained_guard_scope='Only the localized BT slot band; large radial fan regions receive new fillers.')


def middle_wheel(magnetic, config):
    """Three families at fixed z; local ECT-driven aperture loss is explicit."""
    if config['middle_aperture_strategy'] != 'fixed-z-three-families-explicit-ECT-loss':
        raise ValueError('unrecognized middle aperture strategy')
    spec = config['stations']['2']
    alpha = math.pi/spec['sectors']
    half_seam = config['seam_width_m']/2
    guard = config['certification_guard_m']
    c = config['coil_clearance_m']
    a, b = magnetic['warm']['normal_m']/2+c, magnetic['warm']['tangent_m']/2+c
    ect = magnetic['coil_groups']['endcap_plus']
    ect_inner_outer = ect['center_r_m']-ect['half_r_m']+a
    # Adjacent +/-15degree ECT inner-leg boxes project into BT-centred sectors.
    delta = math.radians(ect['phi_offset_deg']-magnetic['coil_groups']['barrel']['phi_offset_deg'])
    projected_ect = ect_inner_outer*math.cos(delta)+b*abs(math.sin(delta))
    nominal = aperture_radius(spec, config)
    full_start = max(nominal, ect_inner_outer+guard)
    split_start = max(nominal, projected_ect+guard)
    outer = outer_apothem(spec['outer_radius_m'], math.tan(alpha), -half_seam/math.cos(alpha))
    bt = magnetic['coil_groups']['barrel']
    bt_radius = bt['center_r_m']-bt['half_r_m']
    low_end, high_start = bt_radius-a-guard, bt_radius+a+guard
    recipes = {'FULL': (full_start, outer, ect['phi_offset_deg']),
               'BT_LOW': (split_start, low_end, bt['phi_offset_deg']),
               'BT_HIGH': (high_start, outer, bt['phi_offset_deg'])}
    panels = []
    for name, (lo, hi, phase) in recipes.items():
        panels += make_family(spec, 2, name, trapezoid(lo, hi, alpha, half_seam), 12, phase, config)
    return panels, dict(recipes={k: dict(u0_m=v[0], u1_m=v[1], phase_deg=v[2]) for k, v in recipes.items()},
        nominal_eta3_apothem_m=nominal, ECT_inner_leg_clearance_outer_u_m=ect_inner_outer,
        adjacent_ECT_projected_max_u_m=projected_ect,
        local_aperture_excess_m={'FULL': full_start-nominal, 'BT_LOW': split_start-nominal},
        sector_centre_nearest_face_eta={'FULL': math.asinh((spec['abs_z_m']-config['depth_m']/2)/full_start),
                                     'BT_LOW': math.asinh((spec['abs_z_m']-config['depth_m']/2)/split_start)},
        limitation='Exactly3 radial-trapezoid families impose additional aperture loss beyond local ECT box shadows; eta3 all-phi coverage is not achieved at fixed z.')


def outer_wheel(config):
    spec = config['stations']['3']
    alpha, half_seam = math.pi/spec['sectors'], config['seam_width_m']/2
    lo = aperture_radius(spec, config)
    hi = outer_apothem(spec['outer_radius_m'], math.tan(alpha), -half_seam/math.cos(alpha))
    return make_family(spec, 3, 'FULL', trapezoid(lo, hi, alpha, half_seam),
                       spec['sectors'], spec['phase_deg'], config), dict(u0_m=lo, u1_m=hi)


def middle_certificate(body, magnetic, config):
    """Full slab lies in straight legs; all coil legs become exact finite boxes."""
    vv = g.vertices3(body)
    zlo, zhi = vv[:, 2].min(), vv[:, 2].max()
    clear, conflicts, checked = True, [], 0
    c = config['coil_clearance_m']
    a, b = magnetic['warm']['normal_m']/2+c, magnetic['warm']['tangent_m']/2+c
    for name, group in magnetic['coil_groups'].items():
        # Every rounded return is outside this straight-leg slab. Other end is
        # separated by the complete warm axial supporting plane.
        center = group['center_z_m']
        extent = group['half_z_m']+a
        if zhi < center-extent or zlo > center+extent:
            continue
        straight = group['half_z_m']-group['corner_radius_m']-a
        if max(abs(zlo-center), abs(zhi-center)) >= straight:
            clear = False
            conflicts.append(name+'/unproved-return-region')
            continue
        for sector in range(magnetic['folds']):
            phi = math.radians(group['phi_offset_deg']+360*sector/magnetic['folds'])
            q = np.array([[math.cos(phi), -math.sin(phi), 0.],
                          [math.sin(phi), math.cos(phi), 0.], [0., 0., 1.]])
            for leg in (-1, 1):
                radial = group['center_r_m']+leg*group['half_r_m']
                box = g.prism(f'{name}/{sector}/{leg}', 'proof',
                    [radial*math.cos(phi), radial*math.sin(phi), center], q,
                    [[-a, -b], [a, -b], [a, b], [-a, b]], 2*extent)
                checked += 1
                if g.intersects(body, box):
                    conflicts.append(box['id'])
    return dict(clear=bool(clear and not conflicts), cells=0, boxes_checked=checked,
        required_clearance_m=c, conflicts=conflicts,
        method='Full-volume straight-leg axial bounds and exact SAT against every rotated coil leg box, enlarged componentwise for Euclidean clearance.')


def certificate(body, magnetic, config):
    if body['station'] == 2:
        return middle_certificate(body, magnetic, config)
    return wheels.wheel_certificate(body, config, magnetic)


def independent_controls(changed, baseline, config):
    """Audit every changed orientation with the independent distance-bound kernel.

    Inner ECT separation uses its analytic supporting planes, because the
    adaptive kernel otherwise spends its cell budget resolving the4.4mm excess
    over the required axial margin. Its BT checks still cover the entire prism.
    """
    magnetic = baseline['magnetic_configuration']
    only_bt = copy.deepcopy(magnetic)
    only_bt['coil_groups'] = {'barrel': magnetic['coil_groups']['barrel']}
    probes = []
    for body in changed:
        source = only_bt if body['station'] == 1 else magnetic
        proof = g.certify_coil_clear(body, source, config['coil_clearance_m'],
            config['numerics']['adaptive_resolution_m'],
            max_cells=config['numerics']['max_certificate_cells'])
        probes.append(dict(id=body['id'], groups=list(source['coil_groups']), **proof))
    bt = magnetic['coil_groups']['barrel']
    occupied = g.prism('NEGATIVE/BT-interior', 'test',
        [bt['center_r_m']-bt['half_r_m'], 0., config['stations']['1']['abs_z_m']],
        np.eye(3), [[-.01, -.01], [.01, -.01], [.01, .01], [-.01, .01]], .02)
    occupied_proof = g.certify_coil_clear(occupied, magnetic,
        config['coil_clearance_m'], config['numerics']['adaptive_resolution_m'])
    # At a15degree sector centre, the rotated BT box begins before u4.30.
    # Treating the coil radial coordinate as sector u must fail.
    spec = config['stations']['1']
    naive = make_family(spec, 1, 'NEGATIVE_NAIVE_ROTATION',
        trapezoid(aperture_radius(spec, config), 4.29, math.pi/12, config['seam_width_m']/2),
        12, spec['phase_deg'], config)[0]
    naive_proof = certificate(naive, magnetic, config)
    # Nominal eta aperture at the ECT-centred middle sector meets its inner leg.
    middle = config['stations']['2']
    naive_ect = make_family(middle, 2, 'NEGATIVE_ETA_WITHOUT_ECT',
        trapezoid(aperture_radius(middle, config), 3., math.pi/24,
                  config['seam_width_m']/2), 12,
        magnetic['coil_groups']['endcap_plus']['phi_offset_deg'], config)[0]
    ect_proof = certificate(naive_ect, magnetic, config)
    members = baseline['supports']['members']
    bounds = np.asarray([g.aabb(m) for m in members])
    support_proof = wheels.support_certificate(members[0], members, bounds,
                                               config['support_clearance_m'])
    pair_control = wheels.all_panel_conflicts([changed[0], dict(changed[0], id='NEGATIVE/DUPLICATE')])
    passed = (all(p['clear'] for p in probes) and not occupied_proof['clear']
              and not naive_proof['clear'] and not ect_proof['clear']
              and not support_proof['clear'] and bool(pair_control))
    if not passed:
        raise ValueError('independent positive/negative geometric controls failed')
    return dict(passed=True, adaptive_probes=probes,
        adaptive_audit_count=len(probes), adaptive_cells=sum(p['cells'] for p in probes),
        occupied_coil_fixture=occupied_proof, incorrect_rotated_bound_fixture=naive_proof,
        nominal_eta_without_ECT_clearance_fixture=ect_proof,
        occupied_support_fixture=support_proof, duplicate_panel_conflict=pair_control,
        scope='Every changed prism audited; inner BT adaptive proof plus separate whole-volume ECT axial planes. Adverse fixtures must be rejected.')


def aperture_report(panels, config):
    out = {}
    for station in (1, 2, 3):
        spec = config['stations'][str(station)]
        aperture_families = {1: {'CORE', 'PRE_SLOT'}, 2: {'FULL', 'BT_LOW'}, 3: {'FULL'}}
        chosen = [p for p in panels if p['station'] == station and p['side'] == 1
                  and p['family'] in aperture_families[station]]
        nearest = spec['abs_z_m']-config['depth_m']/2
        radii = [np.linalg.norm(np.asarray(p['vertices_m'])[[0, 3]], axis=1) for p in chosen]
        out[str(station)] = dict(nearest_face_abs_z_m=nearest,
            nominal_eta3_radius_m=aperture_radius(spec, config),
            minimum_base_apothem_m=min(min(v[0] for v in p['vertices_m']) for p in chosen),
            inner_base_corner_radius_extrema_m=[float(np.min(radii)), float(np.max(radii))],
            inner_corner_nearest_face_eta_extrema=[float(math.asinh(nearest/np.max(radii))),
                                                   float(math.asinh(nearest/np.min(radii)))],
            whole_depth_same_cassette_eta_above_limit_possible=False,
            side_entry_or_midplane_only_hits_can_extend_beyond_limit=True,
            scope='Circumscribed nominal polygon hole; corner/seam and local coil-driven loss are not all-phi acceptance.')
    return out


def build(baseline, config):
    """Return (geometry, controls), with no filesystem writes."""
    if config['eta_limit'] != 3 or config['depth_m'] != .5:
        raise ValueError('fixed eta3/500mm outline contract required')
    if config['coil_clearance_m'] != .05 or config['support_clearance_m'] != .05:
        raise ValueError('fixed50mm coil/support clearance cannot be weakened or changed')
    if config['seam_width_m'] != .02:
        raise ValueError('fixed20mm cassette seams required')
    if len(baseline['supports']['members']) != 484:
        raise ValueError('expected every one of484 fixed support members')
    if any(config['stations'][str(j)]['abs_z_m'] != z for j, z in ((1, 6.7456), (2, 9.5), (3, 12.8))):
        raise ValueError('fixed station centres changed')
    if any(config['stations'][str(j)]['outer_radius_m'] != r for j, r in ((1, 5.45), (2, 6.95), (3, 8.45))):
        raise ValueError('fixed outer radius bounds changed')
    magnetic = baseline['magnetic_configuration']
    if magnetic['folds'] != 12 or magnetic['warm'] != {'normal_m': .5, 'tangent_m': .6}:
        raise ValueError('fixed C12 warm coil reservation required')
    inner, inner_d = inner_wheel(magnetic, config)
    middle, middle_d = middle_wheel(magnetic, config)
    outer, outer_d = outer_wheel(config)
    changed = inner+middle+outer
    members = baseline['supports']['members']
    bounds = np.asarray([g.aabb(m) for m in members])
    hcal_back = magnetic['hcal']['endcap_back_abs_z_m']
    hcal_separation = {}
    for body in changed:
        separation = abs(body['origin_m'][2])-body['depth_m']/2-hcal_back
        if separation < config['support_clearance_m']-config['numerics']['comparison_tolerance_m']:
            raise ValueError('HCAL axial bound clearance failed: '+body['id'])
        hcal_separation[body['id']] = separation
        proof = certificate(body, magnetic, config)
        if not proof['clear']:
            raise ValueError('coil volume conflict: '+body['id']+' '+str(proof))
        body['coil_certificate'] = proof
        support = wheels.support_certificate(body, members, bounds, config['support_clearance_m'])
        if not support['clear']:
            raise ValueError('support volume conflict: '+body['id']+' '+str(support))
        body['support_certificate'] = support
        r = float(np.linalg.norm(g.vertices3(body)[:, :2], axis=1).max())
        if r > config['stations'][str(body['station'])]['outer_radius_m']+config['numerics']['comparison_tolerance_m']:
            raise ValueError('outer corner bound exceeded: '+body['id'])
    barrels = copy.deepcopy([p for p in baseline['panels'] if p['kind'] == 'barrel'])
    panels = barrels+changed
    conflicts = wheels.all_panel_conflicts(panels)
    if conflicts:
        raise ValueError('panel volume conflict: '+str(conflicts[:10]))
    independent = independent_controls(changed, baseline, config)
    ids = [p['id'] for p in panels]
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate chamber identifier')
    geometry = copy.deepcopy(baseline)
    geometry['panels'] = panels
    # Replacing diagnostic support-free packing by copied old endcaps would mix
    # old/new geometry. Preserve its barrel subset and use the changed endcaps.
    geometry['without_support_panels'] = copy.deepcopy([p for p in baseline['without_support_panels'] if p['kind'] == 'barrel'])+copy.deepcopy(changed)
    geometry['refined_wheel_revision'] = copy.deepcopy(config)
    geometry['refined_wheel_dimensions'] = dict(inner_wheel=inner_d, middle_wheel=middle_d, outer_wheel=outer_d)
    geometry['configuration']['status'] = config['status']
    geometry['configuration']['refined_wheel_configuration'] = 'tools/muon_layout/refined-wheels-config.json'
    geometry['configuration']['ordinary_endcap_segmentation_scope'] = 'superseded by refined_wheel_revision for all three endcap stations'
    geometry['configuration']['chambers']['disk_inner_r_m'] = None
    geometry['configuration']['chambers']['disk_aperture_scope'] = 'station-dependent eta3 nominal polygon holes and explicit coil exclusions; see refined_wheel_revision'
    counts = {str(j): sum(p['station'] == j for p in changed) for j in (1, 2, 3)}
    family_counts = {str(j): len({tuple(round(v, 9) for v in dimensions(p).values()) for p in changed if p['station'] == j}) for j in (1, 2, 3)}
    if counts != {'1': 72, '2': 72, '3': 48} or family_counts != {'1': 3, '2': 3, '3': 1}:
        raise ValueError('unexpected refined counts/families')
    geometry['validation'] = dict(panel_panel_conflicts=[], accepted_coil_certificates=len(panels),
        fresh_endcap_coil_certificates=len(changed), fresh_endcap_support_certificates=len(changed),
        retained_barrel_count=len(barrels), coil_clearance_m=config['coil_clearance_m'],
        panel_support_clearance_m=config['support_clearance_m'], unresolved_cells_accepted=0,
        hcal_bound_conflicts=[],
        scope='Changed endcaps freshly certified; retained barrel/source certificates remain historical. All chamber pairs retested.')
    controls = dict(passed=True, status=config['status'], input_revision=config['input_revision'],
        counts_both_ends=counts, dimension_families=family_counts, total_panels=len(panels),
        barrel_panels_retained_exact=len(barrels), supports_retained_exact=len(members),
        magnetic_configuration_retained_exact=geometry['magnetic_configuration'] == baseline['magnetic_configuration'],
        supports_retained_value_equal=geometry['supports'] == baseline['supports'],
        endcap_fresh_coil_certificates=len(changed), endcap_fresh_support_certificates=len(changed),
        all_support_members_checked_per_endcap=len(members), all_panel_pair_count=len(panels)*(len(panels)-1)//2,
        panel_panel_conflicts=conflicts, independent_controls=independent,
        hcal_endcap_axial_bound_minimum_clearance_m=min(hcal_separation.values()),
        aperture=aperture_report(changed, config),
        dimensions=geometry['refined_wheel_dimensions'], limits=config['limits'])
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
    mapping['replacements'] = [dict(station=j, side='both',
        old_count=sum(p['kind'] == 'endcap' and p['station'] == j for p in baseline['panels']),
        new_count=controls['counts_both_ends'][str(j)],
        new_dimension_families=controls['dimension_families'][str(j)]) for j in (1, 2, 3)]
    save(args.output/'shape-change-mapping.json', mapping)
    sources = [source, args.config, Path(__file__), ROOT/'tools/muon_layout/geometry.py',
               ROOT/'tools/muon_layout/wheels.py', ROOT/'tools/muon_layout/wheel_inventory.py',
               ROOT/'tools/toroid_prototype/geometry.py', ROOT/'docs/design/DES-040-muon-chambers-frame.md']
    controls.update(sources={wheels.relative(p): digest(p) for p in sources},
        command=['python3', '-B', '-m', 'tools.muon_layout.refined_wheels', '--geometry', wheels.relative(source),
                 '--config', wheels.relative(args.config), '--output', wheels.relative(args.output)],
        runtime=dict(python=platform.python_version(), numpy=np.__version__, seconds=time.monotonic()-started),
        outputs={p.name: digest(p) for p in args.output.iterdir() if p.is_file() and p.name != 'geometry-controls.json'})
    save(args.output/'geometry-controls.json', controls)
    print(json.dumps(dict(passed=controls['passed'], counts=controls['counts_both_ends'],
                         families=controls['dimension_families'], seconds=controls['runtime']['seconds']), indent=2))


if __name__ == '__main__':
    main()
