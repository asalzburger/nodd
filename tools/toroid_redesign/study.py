"""Issue105 separated toroids: isolated vacuum and schematic coverage PROTOTYPE.

Run: python3 -B -m tools.toroid_redesign.study
No historical map, energy matrix, chamber inventory or production input is changed.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess

import numpy as np

from tools.toroid_prototype import geometry as geo
from tools.toroid_prototype.field import evaluate
from tools.toroid_prototype.system import (coil_source, solenoid_parameters,
                                         solenoid_sources, toroid_sources)
from tools.toroid_prototype.energy import magnetic_energy

ROOT = Path(__file__).resolve().parents[2]
INPUT = Path(__file__).with_name('design.json')
OUTPUT = ROOT/'docs/validation/DES-039/issue105'


def load():
    return json.loads(INPUT.read_text())


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def axial_bounds(config, name, width='warm'):
    g = config['coil_groups'][name]
    h = config[width]['normal_m']/2
    return [g['center_z_m']-g['half_z_m']-h,
            g['center_z_m']+g['half_z_m']+h]


def validate(config):
    """Fail closed on interleaved finite warm envelopes and invalid host inputs."""
    policy = json.loads((ROOT/'tools/magnetic_study/sizing-policy.json').read_text())
    if config['redesign']['winding_field_limit_T'] > policy['toroid_winding_field_limit_T']:
        raise ValueError('winding limit exceeds review policy')
    for width in ('pack', 'cold', 'warm'):
        if not all(math.isfinite(v) and v > 0 for v in config[width].values()):
            raise ValueError('invalid sweep dimensions')
    for axis in ('normal_m', 'tangent_m'):
        if not config['pack'][axis] <= config['cold'][axis] <= config['warm'][axis]:
            raise ValueError('pack/cold/warm containment')
    bounds = {n: axial_bounds(config, n) for n in config['coil_groups']}
    gap = min(bounds['endcap_plus'][0]-bounds['barrel'][1],
              bounds['barrel'][0]-bounds['endcap_minus'][1])
    if gap < config['redesign']['warm_family_gap_min_m']-1e-12:
        raise ValueError('barrel/endcap warm envelopes interleave or lack required gap')
    st = config['stations']
    arrays = [st[k] for k in ('barrel_radii_m', 'disk_abs_z_m', 'disk_outer_radii_m')]
    if any(len(a) != 3 or not np.isfinite(a).all() or min(a) <= 0 for a in arrays):
        raise ValueError('three finite positive station dimensions required')
    return {'warm_axial_bounds_m': bounds, 'minimum_family_gap_m': gap,
            'barrel_centerline_full_length_m': 2*config['coil_groups']['barrel']['half_z_m'],
            'endcap_centerline_full_length_m': 2*config['coil_groups']['endcap_plus']['half_z_m']}


def exterior_probes(config, arc_steps=16):
    """Outside each representative pack, including straight legs, corners and ends.

    C12 rotation covers identical copies. This deliberately does not sample the
    singular quadrature filaments inside the pack or certify a conductor peak.
    """
    points = []
    for name, g in config['coil_groups'].items():
        phi = math.radians(g['phi_offset_deg'])
        path = geo.loop_polyline(g, g['phi_offset_deg'], arc_steps)
        tangent = np.diff(path, axis=0)
        tangent /= np.linalg.norm(tangent, axis=1)[:, None]
        ephi = np.array([-math.sin(phi), math.cos(phi), 0.])
        normal = np.cross(np.broadcast_to(ephi, tangent.shape), tangent)
        center = (path[:-1]+path[1:])/2
        a = config['pack']['normal_m']/2+.002
        b = config['pack']['tangent_m']/2+.002
        for u, v in [(s*a, t*b) for s in (-1, 1) for t in (-1, 0, 1)]+[(0, -b), (0, b)]:
            points.extend(center+u*normal+v*ephi)
    return np.asarray(points)


def normalize(config):
    """Set ordinary intercoil point targets, then reduce currents by exterior screen.

    No momentum/sagitta target drives the current; the 3 T solenoid is fixed.
    The engineering requirement remains max|B|<=4 T throughout the windings.
    """
    c = copy.deepcopy(config)
    source = toroid_sources(c, {n: 1e6 for n in c['coil_groups']})
    targets = list(c['field_target'].values())
    p = np.array([t['point_m'] for t in targets])
    ephi = np.column_stack((-p[:, 1], p[:, 0], np.zeros(len(p))))
    ephi /= np.linalg.norm(ephi, axis=1)[:, None]
    grouped = evaluate(p, source, by_group=True)
    response = np.einsum('ngj,nj->ng', grouped, ephi)
    matrix = np.column_stack((response[:, 0], response[:, 1:].sum(axis=1)))
    currents = np.linalg.solve(matrix, [t['Bphi_T'] for t in targets])*1e6
    if min(currents) <= 0:
        raise ValueError('point targets require reversed family')
    initial = dict(zip(c['coil_groups'], [currents[0], currents[1], currents[1]]))
    probes = exterior_probes(c)
    sol, factor = solenoid_sources()
    bs = evaluate(probes, sol)
    bt = evaluate(probes, toroid_sources(c, initial, order=6, corners=32))
    coarse_bt = evaluate(probes, toroid_sources(c, initial))
    # Bisection on total field, preserving both current ratios and solenoid.
    limit = c['redesign']['sampled_exterior_target_T']
    scale = 1.
    if np.linalg.norm(bt+bs, axis=1).max() > limit:
        lo, hi = 0., 1.
        if np.linalg.norm(bs, axis=1).max() > limit:
            raise ValueError('fixed solenoid already exceeds exterior target')
        for _ in range(45):
            mid = (lo+hi)/2
            if np.linalg.norm(mid*bt+bs, axis=1).max() <= limit:
                lo = mid
            else:
                hi = mid
        scale = lo
    actual = {n: v*scale for n, v in initial.items()}
    for n, v in actual.items():
        c['coil_groups'][n]['ampere_turns_per_coil'] = v
    fine = toroid_sources(c, order=6, corners=32)
    fine_b = evaluate(probes, fine)+bs
    coarse_b = scale*coarse_bt+bs
    maximum = int(np.argmax(np.linalg.norm(fine_b, axis=1)))
    if np.linalg.norm(fine_b, axis=1).max() > c['redesign']['winding_field_limit_T']:
        raise ValueError('refined exterior field exceeds winding limit; revise currents')
    samples = evaluate(p, fine)
    return c, {
        'response_T_per_MAturn': matrix.tolist(), 'initial_currents_Aturn': initial,
        'current_scale_after_exterior_screen': scale, 'currents_Aturn': actual,
        'uniform_pack_J_A_mm2': {n: v/(c['pack']['normal_m']*c['pack']['tangent_m']*1e6) for n, v in actual.items()},
        'point_Bphi_T': np.einsum('nj,nj->n', samples, ephi).tolist(),
        'probe_count': len(probes), 'probe_max_total_norm_T': float(np.linalg.norm(fine_b, axis=1).max()),
        'probe_max_at_m': probes[maximum].tolist(),
        'probe_max_refinement_delta_T': float(np.linalg.norm(fine_b-coarse_b, axis=1).max()),
        'solenoid_polygon_normalization': factor,
        'engineering_winding_limit_T': c['redesign']['winding_field_limit_T'],
        'conductor_peak_certified': False,
        'scope': 'Joint vacuum exterior-of-pack screen, 2 mm offsets; same probe set at pack4/corner16 and pack6/corner32. No interior peak bound, critical surface, temperature or load-line qualification.'}, sol


def crossings(eta, phi_deg, config, clipped=True):
    """Full-depth straight-ray shell intersections, at most one hit per station.

    Centre points are accepted only if the ray traverses both depth faces and
    the entire local normal extrusion clears the warm sweeps by 50 mm. Curved
    tracks, finite panel ends, seams, frames and response remain subsequent work.
    """
    eta, phi_deg = np.broadcast_arrays(np.asarray(eta, float), np.asarray(phi_deg, float))
    shape = eta.shape
    e, phi = eta.ravel(), np.radians(phi_deg.ravel())
    sh = np.sinh(abs(e)); side = np.where(e < 0, -1., 1.)
    st = config['stations']; h = st['outline_thickness_m']/2
    points = np.zeros((len(e), 3, 3)); available = np.zeros((len(e), 3), bool)
    kind = np.zeros((len(e), 3), int)
    def retained(p, geometric, surface, max_half_chord):
        ok = geometric.copy()
        if not clipped:
            return ok
        if ok.any():
            ok[ok] &= ~geo.chamber_depth_mask(p[ok], config, surface,
                config['redesign']['chamber_clearance_m'])
        subset = np.flatnonzero(ok)
        if len(subset):
            distance = np.linalg.norm(p[subset], axis=1)
            half_chord = (h*np.cosh(e[subset]) if surface == 'barrel' else
                h/np.maximum(abs(np.tanh(e[subset])), 1e-15))
            unit = p[subset]/distance[:, None]
            # Fixed station-wide bound makes results independent of how callers
            # batch the rays or which alternative surfaces have already survived.
            n = max(1, math.ceil(2*max_half_chord/.05))
            blocked = np.zeros(len(subset), bool)
            for f in np.linspace(-1, 1, n+1):
                todo = ~blocked
                blocked[todo] = geo.coil_mask(p[subset[todo]]+f*half_chord[todo, None]*unit[todo],
                    config, clearance=config['redesign']['chamber_clearance_m']+.025)
            ok[subset] &= ~blocked
        return ok
    for i, (r, z, outer) in enumerate(zip(st['barrel_radii_m'], st['disk_abs_z_m'], st['disk_outer_radii_m'])):
        end = st['barrel_half_lengths_m'][i]
        barrel = (r+h)*sh <= end
        # All of the axial depth must lie inside the annular face.
        disk = ((z-h) >= st['disk_inner_radius_m']*sh) & ((z+h) <= outer*sh) & (sh > 0)
        rd = np.divide(z, sh, out=np.zeros_like(sh), where=sh > 0)
        bp = np.column_stack((r*np.cos(phi), r*np.sin(phi), side*r*sh))
        dp = np.column_stack((rd*np.cos(phi), rd*np.sin(phi), side*z))
        barrel_ok = retained(bp, barrel, 'barrel', h*math.hypot(1, end/(r+h)))
        # OR within each station: a coil-clipped barrel must not hide a usable
        # wheel of the same station. Prefer the retained barrel crossing when
        # both survive, otherwise use the retained wheel for path/bending.
        disk_ok = retained(dp, disk & ~barrel_ok, 'disk', h*math.hypot(1, outer/(z+h)))
        choose_barrel = barrel_ok | (~disk_ok & barrel)
        points[:, i] = np.where(choose_barrel[:, None], bp, dp)
        available[:, i] = barrel_ok | disk_ok
        kind[:, i] = np.where(choose_barrel, 1, 2)
    return available.reshape(shape+(3,)), points.reshape(shape+(3, 3)), kind.reshape(shape+(3,))


def coverage(config, eta_step=.025, phi_step=.5, path_step=.10):
    maximum = config['redesign']['eta_max']
    ne, np_ = round(maximum/eta_step), round(30/phi_step)
    edges = np.linspace(0, maximum, ne+1)
    eta = (edges[:-1]+edges[1:])/2
    phi = (np.arange(np_)+.5)*30/np_
    ee, pp = np.meshgrid(eta, phi, indexing='ij')
    active, points, _ = crossings(ee, pp, config)
    count = active.sum(axis=-1)
    geometric = crossings(ee, pp, config, False)[0].sum(axis=-1)
    good = count == 3
    clear = good.copy()
    # Separate conservative magnet-free path metric; a magnet is material, not
    # an automatic muon veto. Sample intervals are guarded by half an interval.
    if good.any():
        triplets = points[good]
        start, end = triplets[:, 0], triplets[:, -1]
        length = np.linalg.norm(end-start, axis=1)
        n = math.ceil(float(length.max())/path_step)
        blocked = np.zeros(len(start), bool)
        for t in np.linspace(0, 1, n+1):
            todo = ~blocked
            blocked[todo] = geo.coil_mask(start[todo]+t*(end[todo]-start[todo]), config,
                clearance=path_step/2)
        clear[good] = ~blocked
    # Exact solid-angle weights integrated across each eta cell, two hemispheres
    # and full phi. Dividing by tanh(max) makes the conditional denominator clear.
    weights = np.broadcast_to(np.diff(np.tanh(edges))[:, None], count.shape)
    def fraction(mask):
        return {'flat_eta_phi_fraction': float(mask.mean()),
                'conditional_solid_angle_fraction': float(weights[mask].sum()/weights.sum()),
                'full_sphere_solid_angle_fraction': float(weights[mask].sum()/np_)}
    in3 = ee < 3
    def eta3fraction(mask):
        return {'flat_eta_phi_fraction': float(mask[in3].mean()),
                'conditional_solid_angle_fraction': float(weights[mask & in3].sum()/weights[in3].sum()),
                'full_sphere_solid_angle_fraction': float(weights[mask & in3].sum()/np_)}
    bands = []
    for lo, hi in [(0, 1), (1, 1.5), (1.5, 2.5), (2.5, 3), (3, 3.5)]:
        select = (eta >= lo) & (eta < hi)
        bands.append({'abs_eta_range': [lo, hi],
                      'three_station_phi_fraction': float(good[select].mean()),
                      'three_station_magnet_free_fraction': float(clear[select].mean())})
    return {'eta_step': maximum/ne, 'phi_step_deg': 30/np_, 'path_step_m': path_step,
            'sample_count': int(count.size), 'geometric_three': fraction(geometric == 3),
            'at_least_one': fraction(count >= 1), 'at_least_two': fraction(count >= 2),
            'three_station': fraction(good), 'three_station_magnet_free': fraction(clear),
            'within_abs_eta3': {'at_least_one': eta3fraction(count >= 1),
                'at_least_two': eta3fraction(count >= 2), 'three_station': eta3fraction(good),
                'three_station_magnet_free': eta3fraction(clear)},
            'eta_bands': bands, 'eta_centers': eta.tolist(), 'phi_centers_deg': phi.tolist(),
            'station_count_eta_phi': count.tolist(),
            'denominator': 'Cell-centred positive eta0..3.5, one30degree C12 sector; mirrored hemispheres. Conditional solid-angle integrates sech(eta)^2 exactly; full-sphere fraction includes the uncovered outside domain.',
            'scope': 'Schematic local shell availability ceiling, full depth and coil cutouts; no panel tiling, support/service exclusions, efficiency, transport or momentum resolution.'}


def energy(config, rows=((3, 4, 16, 4), (4, 5, 24, 8))):
    result = []
    currents = {n: g['ampere_turns_per_coil'] for n, g in config['coil_groups'].items()}
    for source_order, target_order, corners, line in rows:
        row = magnetic_energy(toroid_sources(config, order=source_order, corners=corners),
            {n: coil_source(config, n, order=target_order, corners=corners) for n in config['coil_groups']},
            symmetry_multiplicity=config['folds'], line_order=line, reference_currents_Aturn=currents)
        row['orders'] = [source_order, target_order, corners, line]
        result.append(row)
        print('energy orders', row['orders'], 'MJ', row['total_energy_J']/1e6, flush=True)
    pack = geo.analytic_sweep_union_volumes(config, width='pack', order=256)
    target = result[-1]['total_energy_J']/30e6
    # Same provisional aspect-ratio closure as DES039, but never permit cold
    # dimensions below the current pack. Explicitly reject an impossible fit.
    aspect = .24/.35
    lo = max(config['pack']['normal_m']**2/aspect,
             config['pack']['tangent_m']**2*aspect)
    hi = min(config['warm']['normal_m']**2/aspect,
             config['warm']['tangent_m']**2*aspect, .133)
    def set_cold(area):
        config['cold'] = {'normal_m': math.sqrt(area*aspect),
                          'tangent_m': math.sqrt(area/aspect)}
        return geo.analytic_sweep_union_volumes(config, width='cold', order=256)['sum_group_union_volume_m3']
    if not set_cold(lo) <= target <= set_cold(hi):
        raise ValueError('energy-sized cold mass cannot contain pack within warm reservation')
    for _ in range(45):
        mid = (lo+hi)/2
        if set_cold(mid) < target:
            lo = mid
        else:
            hi = mid
    set_cold((lo+hi)/2)
    cold = geo.analytic_sweep_union_volumes(config, width='cold', order=256)
    total = result[-1]['total_energy_J']+solenoid_parameters()['stored_energy_MJ']*1e6
    volume = cold['sum_group_union_volume_m3']+solenoid_parameters()['cold_volume_m3']
    return {'studies': result, 'relative_refinement_change': result[-1]['total_energy_J']/result[-2]['total_energy_J']-1,
            'toroid_cold_union_volume_m3': cold['sum_group_union_volume_m3'],
            'toroid_pack_union_volume_m3': pack['sum_group_union_volume_m3'],
            'complete_vacuum_energy_J': total,
            'solenoid_toroid_mutual_energy_J': 0.,
            'mutual_basis': 'Paired meridional pack offsets and axisymmetric solenoid imply zero net linked flux; toroid family mutuals are fully recomputed.',
            'complete_cold_volume_m3': volume, 'energy_density_MJ_m3': total/volume/1e6,
            'policy_target_toroid_cold_volume_m3': target,
            'vacuum_global_policy_closed': abs(total/volume/30e6-1) < 1e-8,
            'installed_policy_closed': False,
            'scope': 'Recomputed complete finite-pack vacuum self/mutual energy, no old matrix reuse. Cold size contains the fixed pack and closes global30MJ/m3 vacuum rule with provisional aspect0.24/0.35. Installed nonlinear HCAL energy, per-magnet allocation and engineering sizing remain open.'}


def bending(config, toroid, solenoid):
    """Signed unequal-spacing sagitta integral on selected retained shell rays.

    No resolution is inferred. Queries within pack+0.10m are rejected, rather
    than assigning a field to an unresolved winding interior.
    """
    rows = []
    nodes, weights = np.polynomial.legendre.leggauss(24)
    for eta in (0., .6, .9, 1.1, 1.3, 1.6, 2., 2.5, 2.9, 3.0, 3.4):
        for phi_deg in (0., 7.5, 15., 22.5):
            hits, xyz, kinds = crossings(np.array([eta]), np.array([phi_deg]), config)
            row = {'eta': eta, 'phi_deg': phi_deg, 'three_stations': bool(hits.all())}
            if not hits.all():
                rows.append(row); continue
            distances = np.linalg.norm(xyz[0], axis=1)
            a, b, c = distances
            points, ww = [], []
            for lo, hi in ((a, b), (b, c)):
                ss = (hi+lo)/2+(hi-lo)*nodes/2
                kernel = np.where(ss <= b, (ss-a)*(c-b)/(c-a), (c-ss)*(b-a)/(c-a))
                points.extend(ss[:, None]*xyz[0, 0]/a)
                ww.extend(weights*(hi-lo)/2*kernel)
            points = np.asarray(points)
            row.update(station_distances_m=distances.tolist(),
                       hit_types=''.join('B' if k == 1 else 'D' for k in kinds[0]))
            if geo.coil_mask(points, config, 'pack', clearance=.10).any():
                row['field_status'] = 'excluded: quadrature point within pack+0.10m'
            else:
                phi = math.radians(phi_deg); ep = np.array([-math.sin(phi), math.cos(phi), 0.])
                field = evaluate(points, toroid)+evaluate(points, solenoid)
                integral = float(np.array(ww)@(field@ep))
                row.update(field_status='evaluated in vacuum outside pack guard',
                    signed_sagitta_integral_T_m2=integral,
                    signed_B_sag_T=2*integral/((b-a)*(c-b)),
                    span_m=float(c-a))
            rows.append(row)
    return {'rows': rows, 'scope': 'Selected straight-ray signed Bphi bending at actual retained shell crossings; midpoint interpolation kernel. No reconstructed momentum, material or precision assumptions. Pack-guard samples remain excluded, not zero.'}


def run(output=OUTPUT):
    output.mkdir(parents=True, exist_ok=True)
    c = load(); dimensions = validate(c)
    c, field, sol = normalize(c)
    save(output/'configuration.json', c)
    print('currents and field', field, flush=True)
    comparisons = {}
    for name in ('short_barrel_chambers', 'nested_transition_chambers'):
        trial = copy.deepcopy(c)
        if name == 'short_barrel_chambers':
            trial['stations']['barrel_half_lengths_m'] = [5.7]*3
        comparisons[name] = coverage(trial)
        print(name, comparisons[name]['three_station'], flush=True)
    fine = coverage(c, .0125, .25, .05)
    # Coil-free control must expose every station for this nested shell scheme.
    ee, pp = np.meshgrid(np.array(fine['eta_centers']), np.array(fine['phi_centers_deg']), indexing='ij')
    if not crossings(ee[ee < 3], pp[ee < 3], c, False)[0].all():
        raise ValueError('selected nested shell control has a geometric gap below eta3')
    en = energy(c)
    validate(c)
    save(output/'configuration.json', c)
    source = toroid_sources(c, order=6, corners=32)
    origin = evaluate([[0, 0, 0]], source)+evaluate([[0, 0, 0]], sol)
    if np.linalg.norm(origin) > 5:
        raise ValueError('joint central field exceeds policy')
    probes = []
    # Actual toroidal field at clear representative intercoil locations.
    for z, radii, phi in [(0, [5.2, 6.7, 8.2], 15), (10.3, [1.5, 2., 4., 6.], 0)]:
        for r in radii:
            a = math.radians(phi); p = [r*math.cos(a), r*math.sin(a), z]
            b = evaluate([p], source)[0]+evaluate([p], sol)[0]
            probes.append({'point_m': p, 'B_cart_T': b.tolist(), 'norm_T': float(np.linalg.norm(b)),
                           'Bphi_T': float(b@np.array([-math.sin(a), math.cos(a), 0]))})
    report = {'status': 'DRAFT / isolated schematic PROTOTYPE; human approval pending',
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'source_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()),
        'input_sha256': hashlib.sha256(INPUT.read_bytes()).hexdigest(),
        'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [Path(__file__), ROOT/'tools/toroid_prototype/field.py', ROOT/'tools/toroid_prototype/field_backend.cpp',
             ROOT/'tools/toroid_prototype/geometry.py', ROOT/'tools/toroid_prototype/system.py', ROOT/'tools/toroid_prototype/energy.py', ROOT/'tools/toroid_prototype/solenoid-input.json', ROOT/'tools/magnetic_study/sizing-policy.json']},
        'software': {'python': platform.python_version(), 'numpy': np.__version__},
        'dimensions': dimensions, 'normalization': field, 'B_origin_T': origin[0].tolist(),
        'field_probes': probes, 'energy': en, 'coverage_comparisons': comparisons,
        'signed_bending': bending(c, source, sol),
        'coverage_refined': fine,
        'coverage_refinement_delta': fine['three_station']['flat_eta_phi_fraction']-comparisons['nested_transition_chambers']['three_station']['flat_eta_phi_fraction']}
    save(output/'results.json', report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    run(parser.parse_args().output)
