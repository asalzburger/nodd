#!/usr/bin/env python3
"""PROTOTYPE independent DES-006 inclined-row geometry and area audit.

The dense straight-ray calculation imports no shared geometry routine. The
endpoint-normal Newton solver is compared with the shared bisection solver.
Controls and numerical tolerances are audit fixtures, not detector requirements.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'docs/design/DES-006-layouts.json'
CONFIG = ROOT / 'docs/design/DES-006-inclined-layouts.json'
OUTPUT = ROOT / 'docs/validation/DES-006-inclined-independent.json'


def independent_rows(baseline, recipe, margin):
    rows = []
    start, end, step = (recipe[k] for k in ('start_z_m', 'end_z_m', 'band_step_m'))
    for layer in baseline['layers']:
        if layer['kind'] != 'cylinder' or layer['subsystem'] == 'pixel':
            continue
        radius = layer['r_m']
        for side in (-1, 1):
            for index in range(round((end - start) / step)):
                center = start + (index + 0.5) * step
                alpha = min(math.atan(center / radius), math.radians(recipe['max_tilt_deg']))
                cosine, sine = math.cos(alpha), math.sin(alpha)
                tangent = sine / cosine
                points = []
                for boundary, direction in ((center-step/2, -1), (center+step/2, 1)):
                    r = (radius + tangent*center) / (1 + tangent*boundary/radius)
                    z = boundary*r/radius
                    u = (z-center)/cosine + direction*margin
                    points.append((radius-sine*u, side*(center+cosine*u)))
                rows.append(dict(parent=layer['id'], subsystem=layer['subsystem'],
                                 points=points, x0_percent=layer['x0_percent']))
    return rows


def straight_hit(points, eta, vertex, material):
    (r1, z1), (r2, z2) = points
    length = math.hypot(r2-r1, z2-z1)
    nr, nz = (z2-z1)/length, -(r2-r1)/length
    sh = math.sinh(eta)
    denominator = nr+nz*sh
    if abs(denominator) < 1e-14:
        return None
    r = (nr*r1+nz*(z1-vertex))/denominator
    z = vertex+r*sh
    fraction = ((r-r1)*(r2-r1)+(z-z1)*(z2-z1))/length**2
    if r <= 0 or not -1e-12 <= fraction <= 1+1e-12:
        return None
    return r, material*math.cosh(eta)/abs(denominator)


def straight_sample(baseline, recipe, eta, vertex, rows=None):
    hits = []
    for layer in baseline['layers']:
        if layer['kind'] == 'cylinder':
            low, high = layer['z_min_m'], layer['z_max_m']
            if rows is not None and layer['subsystem'] != 'pixel':
                low, high = -recipe['start_z_m'], recipe['start_z_m']
            points = [(layer['r_m'], low), (layer['r_m'], high)]
        elif layer['kind'] == 'disc':
            points = [(layer['r_min_m'], layer['z_m']), (layer['r_max_m'], layer['z_m'])]
        else:
            raise ValueError('Independent baseline audit only supports cylinders/disks')
        hit = straight_hit(points, eta, vertex, layer['x0_percent'])
        if hit:
            hits.append((layer['id'], *hit))
    for row in rows or []:
        hit = straight_hit(row['points'], eta, vertex, row['x0_percent'])
        if hit:
            hits.append((row['parent'], *hit))
    return dict(stations=len({hit[0] for hit in hits}), physical_module_crossings=len(hits),
                material_percent=sum(hit[2] for hit in hits))


def reference_area(baseline, recipe, rows=None):
    area = dict(pixel=0., short_strip=0., long_strip=0.)
    for layer in baseline['layers']:
        if layer['kind'] == 'cylinder':
            length = layer['z_max_m']-layer['z_min_m']
            if rows is not None and layer['subsystem'] != 'pixel':
                length = 2*recipe['start_z_m']
            value = 2*math.pi*layer['r_m']*length
        else:
            value = math.pi*(layer['r_max_m']**2-layer['r_min_m']**2)
        area[layer['subsystem']] += value
    for row in rows or []:
        (r1, z1), (r2, z2) = row['points']
        area[row['subsystem']] += math.pi*(r1+r2)*math.hypot(r2-r1, z2-z1)
    return dict(reference_area_m2=area, silicon_face_area_m2=dict(area, long_strip=2*area['long_strip']))


def margin_scan(baseline, recipe):
    result = []
    for margin in (0., 0.005, 0.010):
        rows = independent_rows(baseline, recipe, margin)
        probes = []
        for vertex in (-0.15, 0., 0.15):
            losses = []
            min_a = min_c = math.inf
            max_delta, min_delta = -math.inf, math.inf
            overlaps = max_loss = max_gain = 0
            for index in range(-4000, 4001):
                eta = index*0.001
                a = straight_sample(baseline, recipe, eta, vertex)
                c = straight_sample(baseline, recipe, eta, vertex, rows)
                min_a, min_c = min(min_a, a['stations']), min(min_c, c['stations'])
                delta = c['material_percent']-a['material_percent']
                max_delta, min_delta = max(max_delta, delta), min(min_delta, delta)
                overlaps += int(c['physical_module_crossings'] > c['stations'])
                max_loss = max(max_loss, a['stations']-c['stations'])
                max_gain = max(max_gain, c['stations']-a['stations'])
                if c['stations'] < a['stations']:
                    losses.append(eta)
            probes.append(dict(vertex_z_m=vertex, min_A_stations=min_a, min_C_stations=min_c,
                loss_bins=len(losses), max_station_loss=max_loss, max_station_gain=max_gain,
                station_loss_etas=losses, max_delta_x0_percentage_points=max_delta,
                min_delta_x0_percentage_points=min_delta, overlap_bins=overlaps))
        landmarks = [dict(eta=eta, vertex_z_m=vertex,
                    A=straight_sample(baseline, recipe, eta, vertex),
                    C=straight_sample(baseline, recipe, eta, vertex, rows))
                    for vertex in (0., 0.15) for eta in (0., 1., 1.5, 2., 2.5, 4.)]
        result.append(dict(tangent_extension_m=margin, areas=reference_area(baseline, recipe, rows),
                           vertex_scans=probes, landmarks=landmarks))
    return result


def newton_hit(layer, eta, vertex, pt, field):
    """Derive normal from endpoints and solve independently of stored normal."""
    r1, z1, r2, z2 = (layer[k] for k in ('r1_m', 'z1_m', 'r2_m', 'z2_m'))
    length = math.hypot(r2-r1, z2-z1)
    nr, nz = (z2-z1)/length, -(r2-r1)/length
    if nr < 0:
        nr, nz = -nr, -nz
    sh, ch = math.sinh(eta), math.cosh(eta)
    rho = pt/(0.299792458*abs(field)) if field else math.inf
    constant = nr*r1+nz*(z1-vertex)
    # Reject rays that cannot reach this endcap before attempting Newton steps.
    if (sh >= 0 and max(z1, z2) < vertex) or (sh <= 0 and min(z1, z2) > vertex):
        return None
    if nr+nz*sh <= 0:
        raise ValueError('Independent audit domain requires a positive initial derivative')
    # For this same-facing audit domain the surface residual is monotonic.
    # A target beyond the first radial turning point has no allowed root.
    if field and constant >= nr*2*rho+nz*sh*math.pi*rho:
        return None
    arc = constant/(nr+nz*sh)
    if arc <= 0:
        return None
    for _ in range(15):
        r = arc if field == 0 else 2*rho*math.sin(arc/(2*rho))
        derivative = 1. if field == 0 else math.cos(arc/(2*rho))
        correction = (nr*r+nz*sh*arc-constant)/(nr*derivative+nz*sh)
        arc -= correction
        if abs(correction) < 1e-14:
            break
    else:
        raise ValueError('Independent Newton audit failed to converge')
    if not 0 < arc < math.pi*rho:
        return None
    r = arc if field == 0 else 2*rho*math.sin(arc/(2*rho))
    z = vertex+arc*sh
    fraction = ((r-r1)*(r2-r1)+(z-z1)*(z2-z1))/length**2
    if not -1e-11 <= fraction <= 1+1e-11:
        return None
    if abs(nr*r+nz*sh*arc-constant) > 1e-11:
        raise ValueError('Independent Newton point is not on the surface')
    cosine = abs(nr*(1. if field == 0 else math.cos(arc/(2*rho)))+nz*sh)/ch
    return r, z, arc*ch, layer['x0_percent']/cosine


def solver_audit(candidate):
    # The shared function is the comparison target only; never used by own solver.
    from inclined_study import ring_intersection
    rings = [layer for layer in candidate['layers'] if layer['kind'] == 'inclined_ring']
    queries = hits = 0
    differences = [0., 0., 0., 0.]
    for field in (0., 2., 3., 4.):
        for pt in (1., 10., 100.):
            for vertex in (-0.15, 0., 0.15):
                for index in range(-40, 41):
                    for layer in rings:
                        eta = index/10
                        actual = newton_hit(layer, eta, vertex, pt, field)
                        shared = ring_intersection(layer, eta, vertex, pt, field)
                        queries += 1
                        if (actual is None) != (shared is None):
                            raise AssertionError((layer['id'], eta, vertex, pt, field, actual, shared))
                        if actual is not None:
                            hits += 1
                            differences = [max(old, abs(a-b)) for old, a, b in zip(differences, actual, shared)]
    if max(differences) > 1e-10:
        raise AssertionError('Numerical audit tolerance exceeded')
    return dict(queries=queries, finite_crossings=hits, crossing_presence_disagreements=0,
                max_abs_difference=dict(zip(('r_m', 'z_m', 'path_m', 'material_percentage_points'), differences)),
                numerical_comparison_tolerance=1e-10,
                sampling=dict(eta_min=-4, eta_max=4, eta_step=0.1, vertex_z_m=[-0.15, 0., 0.15],
                              pt_GeV=[1., 10., 100.], field_T=[0., 2., 3., 4.]))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    baseline = json.loads(BASE.read_text())['candidates'][0]
    config = json.loads(CONFIG.read_text())
    report = dict(status='PROTOTYPE numerical cross-check, no detector acceptance',
        units=dict(length='m', area='m^2', momentum='GeV', field='T', material='percent X0'),
        baseline_areas=reference_area(baseline, config['recipe']),
        straight_ray_controls=margin_scan(baseline, config['recipe']),
        straight_ray_sampling=dict(eta_min=-4, eta_max=4, eta_step=0.001, points_per_vertex=8001,
                                   vertex_z_m=[-0.15, 0., 0.15], field_T=0),
        finite_field_solver_audit=solver_audit(config['candidate']),
        provenance=dict(command=' '.join(sys.orig_argv), python=platform.python_version(), seed=None,
            project_revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            working_tree_dirty=bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT)),
            baseline_sha256=digest(BASE), configuration_sha256=digest(CONFIG), code_sha256=digest(Path(__file__)),
            comparison_code_sha256=digest(ROOT/'tools/tracker_layout/inclined_study.py')),
        limitations=['Axisymmetric ideal surfaces; no module masks or phi gaps',
                     'Vertex and extension controls are numerical fixtures, not acceptance requirements',
                     'Sampled grids do not prove continuous coverage',
                     'No scattering, covariance, full simulation or reconstructed efficiency'])
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print('Wrote independent dense margin scan and 209952-query solver audit:', args.output)


if __name__ == '__main__':
    main()
