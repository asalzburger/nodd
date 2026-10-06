#!/usr/bin/env python3
"""DES016 radial PROTOTYPE: oriented assemblies with explicit active seams."""
import argparse
from collections import Counter
import datetime
import gzip
import json
import math
from pathlib import Path
import platform
import subprocess

import numpy as np
import shapely
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
from shapely.strtree import STRtree

from study import ROOT, rectangle, metrics, coverage_certificate, baseline, digest


def load_config():
    return json.loads(Path(__file__).with_name('radial-inputs.json').read_text())


def check_datums(cfg, datums):
    """Pair reflected source datums despite harmless binary-float subtraction."""
    expected = cfg['positive_disc_datums_mm']; counts = Counter()
    if len(datums) != 2*len(expected):
        raise ValueError('Expected all 18 disc datums')
    for datum in datums:
        i = min(range(len(expected)), key=lambda k:abs(abs(datum)-expected[k]))
        if abs(abs(datum)-expected[i]) > cfg['datum_match_tolerance_mm']:
            raise ValueError('Disc datum differs from the independent positioning baseline')
        counts[i] += 1
    if any(counts[i] != 2 for i in range(len(expected))):
        raise ValueError('Missing or duplicated reflected disc datum')


def dimensions(cfg, family):
    f = cfg['families'][family]
    au, av = cfg['active_mm']; gap = cfg['interchip_gap_mm']
    return (f['columns'] * au + (f['columns'] - 1) * gap,
            f['rows'] * av + (f['rows'] - 1) * gap)


def family_at(policy, row):
    if row == 0 or policy == 'single':
        return 'single'
    if policy.startswith('single-') and row < 4:
        return 'single'
    if policy == 'single-double-quad':
        return 'double' if row < 6 else 'quad'
    return policy.removeprefix('single-')


def candidates(cfg, margin, phi_margin, policy='single'):
    """Concentric rectangular envelopes; seams are screened afterwards.

    For half angular spacing alpha, the envelope covers a circular band from
    (radius-half_v)/cos(alpha) to min(radius+half_v,half_u/sin(alpha)).
    This only proposes rings: actual matrices and finite-z coverage decide.
    """
    result = []; rings = []
    start = cfg['annulus_mm'][0]; row = 0
    while start < cfg['annulus_mm'][1]:
        family = family_at(policy, row)
        width, height = dimensions(cfg, family); hu, hv = width / 2, height / 2
        if row == 0:
            n, radius = cfg['inner_phi_modules'], cfg['inner_ring_radius_mm']
        else:
            for n in range(3, cfg['maximum_phi_population'] + 1):
                radius = start * math.cos(math.pi / n) + hv - margin
                if (radius + hv) * math.sin(math.pi / n) <= hu - phi_margin:
                    break
            else:
                raise ValueError('No bounded ring solution')
        phase = .5 * (row % 2)
        rings.append(dict(row=row, family=family, modules=n, radius_mm=radius,
                          phase_cells=phase))
        for k in range(n):
            phi = 2 * math.pi * (k + phase) / n
            i = len(result)
            result.append(dict(kind='polar', row=row, col=k, family=family,
                               module_id=200000+i, sensor_id=200000+i,
                               center_mm=[radius*math.cos(phi), radius*math.sin(phi), 0.],
                               u=[-math.sin(phi), math.cos(phi), 0.],
                               v=[math.cos(phi), math.sin(phi), 0.]))
        start = radius + hv
        # No duplicated margin on the transition from the preserved inner ring.
        row += 1
    return result, rings


def body_polygon(module, cfg):
    f = cfg['families'][module['family']]
    center = np.asarray(module['center_mm']) + f['periphery_offset_mm'] * np.asarray(module['v'])
    return rectangle(center, module['u'], module['v'], f['body_mm'][0]/2, f['body_mm'][1]/2)


def intersecting_pairs(shapes, tolerance):
    tree = STRtree(shapes)
    for i, shape in enumerate(shapes):
        for j in tree.query(shape, predicate='intersects'):
            j = int(j)
            if j < i and shape.intersection(shapes[j]).area > tolerance:
                yield i, j


def stagger(raw, cfg, datum):
    """Colour whole physical modules; keep all chips on their common plane."""
    bodies = [body_polygon(m, cfg).buffer(cfg['colour_padding_mm'], join_style=2) for m in raw]
    adjacency = [set() for _ in raw]
    for i, j in intersecting_pairs(bodies, cfg['area_tolerance_mm2']):
        adjacency[i].add(j); adjacency[j].add(i)
    colors = {}
    while len(colors) < len(raw):
        available = [i for i in range(len(raw)) if i not in colors]
        i = max(available, key=lambda i: (len({colors[j] for j in adjacency[i] if j in colors}), len(adjacency[i]), -i))
        used = {colors[j] for j in adjacency[i] if j in colors}
        colors[i] = next(k for k in range(len(raw)) if k not in used)
    output = []
    half = cfg['luminous_half_z_mm']; anchor = (datum*datum-half*half)/datum
    for i, m in enumerate(raw):
        dz = cfg['plate_to_module_mm'] + colors[i]*cfg['level_spacing_mm']
        c = np.asarray(m['center_mm']).copy()
        c[:2] *= 1+dz/anchor; c[2] = datum+dz
        output.append(dict(m, center_mm=c.tolist(), level=colors[i], local_z_mm=dz))
    return output


def active_patches(modules, cfg):
    au, av = cfg['active_mm']; gap = cfg['interchip_gap_mm']; output = []
    for m in modules:
        f = cfg['families'][m['family']]
        for col in range(f['columns']):
            for row in range(f['rows']):
                du = (col-(f['columns']-1)/2)*(au+gap)
                dv = (row-(f['rows']-1)/2)*(av+gap)
                center = np.asarray(m['center_mm'])+du*np.asarray(m['u'])+dv*np.asarray(m['v'])
                patch = col*f['rows']+row
                output.append(dict(m, id=300000+4*(m['module_id']-200000)+patch,
                                   center_mm=center.tolist(), half_u_mm=au/2, half_v_mm=av/2,
                                   patch=patch, layer_id='DES016-radial-template',
                                   subsystem='pixel', region='endcap'))
    return output


def project(modules, cfg, datum, vertex=0., guard=None):
    """One silicon outline per assembly, or each active chip island separately."""
    shapes = []
    items = active_patches(modules, cfg) if guard is None else modules
    for m in items:
        if guard is None:
            hu, hv = np.asarray(cfg['active_mm'])/2
        else:
            width, height = dimensions(cfg, m['family']); hu, hv = width/2+guard, height/2+guard
        scale = (datum-vertex)/(m['center_mm'][2]-vertex)
        poly = rectangle(m['center_mm'], m['u'], m['v'], hu, hv)
        shapes.append(Polygon([(x*scale, y*scale) for x, y in poly.exterior.coords]))
    return shapes


def body_screen(modules, cfg):
    shapes = [body_polygon(m, cfg) for m in modules]; bad = []; gaps = []
    for i, j in intersecting_pairs(shapes, cfg['area_tolerance_mm2']):
        gap = abs(modules[i]['center_mm'][2]-modules[j]['center_mm'][2])-cfg['body_thickness_mm']
        gaps.append(gap)
        if gap < cfg['required_gap_mm']-1e-8:
            bad.append([i, j, gap])
    return dict(overlaps_or_insufficient_gap=bad, minimum_z_gap_mm=min(gaps) if gaps else None,
                minimum_beam_radius_mm=min(p.distance(Point(0, 0)) for p in shapes),
                maximum_radius_mm=max(math.hypot(x, y) for p in shapes for x, y in p.exterior.coords),
                levels=max(m['level'] for m in modules)+1,
                occupied_local_z_mm=[min(m['local_z_mm'] for m in modules)-cfg['body_thickness_mm']/2,
                                     max(m['local_z_mm'] for m in modules)+cfg['body_thickness_mm']/2])


def covariance(pitch_um, angle):
    """Binary pitch/sqrt(12) control in local tangential/radial coordinates."""
    a, b = (np.asarray(pitch_um)**2/12).tolist()
    c, s = math.cos(angle), math.sin(angle)
    return [[a*c*c+b*s*s, (a-b)*c*s], [(a-b)*c*s, a*s*s+b*c*c]]


def orientation_screen(modules, cfg):
    center_errors = []; corner_errors = []
    for m in modules:
        phi = math.atan2(m['center_mm'][1], m['center_mm'][0])
        radial = np.array([math.cos(phi), math.sin(phi)])
        center_errors.append(abs(float(np.dot(m['u'][:2], radial))))
        for x, y in rectangle(m['center_mm'], m['u'], m['v'], *np.asarray(dimensions(cfg, m['family']))/2).exterior.coords:
            corner_errors.append(abs(math.atan2(x*m['u'][0]+y*m['u'][1], x*m['v'][0]+y*m['v'][1])))
    pitch = cfg['rectangular_pixel_control_um']
    controls = [covariance(pitch, x) for x in np.linspace(0, 2*math.pi, 361)]
    square = [covariance([50., 50.], x) for x in np.linspace(0, 2*math.pi, 361)]
    return dict(passed=max(center_errors)<1e-12,
                maximum_module_center_axis_error_sine=max(center_errors),
                maximum_corner_axis_departure_degrees=math.degrees(max(corner_errors)),
                rectangular_pixel_control_um=pitch,
                polar_center_tangential_radial_sigma_um=(np.asarray(pitch)/math.sqrt(12)).tolist(),
                global_xy_control_tangential_sigma_um=[math.sqrt(min(x[0][0] for x in controls)), math.sqrt(max(x[0][0] for x in controls))],
                square_pixel_control_variance_span_um2=max(x[0][0] for x in square)-min(x[0][0] for x in square),
                worst_corner_covariance_um2=covariance(pitch, max(corner_errors)),
                scope='Geometric binary-pitch covariance control. Rectangular pitch is a test hypothesis; no fitted-track, charge-sharing or longitudinal-resolution qualification.')


def service_estimate(modules, rings, cfg, outer_radius):
    inp = json.loads((ROOT/cfg['services_input']).read_text()); barrel = json.loads((ROOT/cfg['barrel_services']).read_text()); p = inp['pixel']
    groups = {}
    for m in modules:
        groups.setdefault((m['row'], m['family'], m['col'] >= next(r['modules'] for r in rings if r['row']==m['row'])/2), []).append(m)
    chains = circuits = 0
    for (_, family, _), group in groups.items():
        f = cfg['families'][family]; chips = f['columns']*f['rows']
        chains += math.ceil(len(group)/min(p['max_chain_modules'], p['max_chain_chips']//chips))
        circuits += math.ceil(len(group)*chips*p['power_per_chip_W']/p['cooling_power_per_circuit_W'])
    nmodules = len(modules); nchips = len(active_patches(modules, cfg))
    # Each complete ring is split into two independently served half-rings.
    length = sum(2*math.pi*max(np.linalg.norm(m['center_mm'][:2]) for m in modules if m['row']==r['row']) for r in rings)
    pipes = circuits*math.pi*((p['feed_outer_diameter_mm']/2)**2+(p['return_outer_diameter_mm']/2)**2)
    inner = math.ceil(outer_radius+cfg['collector_radial_gap_mm']); outer = cfg['carrier_shell_inner_mm']
    section = math.pi*max(0., outer*outer-inner*inner); scenarios = []
    for name, s in inp['scenarios'].items():
        links = nmodules*(s['pixel_uplinks_per_module']+s['pixel_commands_per_module'])+nchips*s['pixel_uplinks_per_chip']
        cable = chains*p['ancillary_chain_area_mm2']+links*p['differential_link_area_mm2']; sides = []
        for side in ['positive', 'negative']:
            braw = sum(sum(x['scenarios'][name]['terminal_cable_footprint_mm2'].values())+x['scenarios'][name]['terminal_pipe_footprint_mm2'] for x in barrel['sectors'] if x['side']==side)
            demand = (braw+8*(cable+pipes))*s['demand_multiplier']; cap = section*s['available_phi_fraction']*s['packing_fraction']
            sides.append(dict(side=side, after_disc_8_demand_mm2=demand, capacity_mm2=cap,
                              utilization=demand/cap if cap else None, status='PASS' if demand<=cap else 'FAIL'))
        scenarios.append(dict(scenario=name, uplink_command_links=links, cables_mm2=cable, feed_return_pipe_mm2=pipes, end_trunks=sides))
    return dict(modules_per_disc=nmodules, chips_per_disc=nchips, families=dict(Counter(m['family'] for m in modules)),
                nominal_W=nchips*p['power_per_chip_W'], power_chains=chains, local_circuits=circuits,
                half_ring_tube_length_without_feeds_mm=length, local_tube_OD_mm=cfg['local_tube_OD_mm'],
                local_tube_volume_envelope_mm3=length*math.pi*(cfg['local_tube_OD_mm']/2)**2,
                trunk_inner_mm=inner, trunk_outer_mm=outer, scenarios=scenarios,
                limitations=['Half-rings are independently served; homogeneous family chains obey both module and chip limits.',
                             'Tube length is a circumferential estimate without feeds, returns, bends or manifold routing.',
                             'Existing support, thermal interfaces and shared trunk engineering are not qualified.'])


def screen(raw, cfg, datum):
    placed = stagger(raw, cfg, datum); sensor = metrics(project(placed, cfg, datum, guard=cfg['sensor_guard_mm']), cfg)
    body = body_screen(placed, cfg)
    vertices = [dict(vertex_z_mm=v, gap_mm2=metrics(project(placed, cfg, datum, vertex=v), cfg)['uncovered_annulus_superset_mm2']) for v in cfg['vertices_z_mm']]
    passing = (max(sensor['overlap_over_union_percent'], sensor['annular_overlap_over_union_percent']) <= cfg['overlap_limit_percent'] and
               all(v['gap_mm2']<=cfg['area_tolerance_mm2'] for v in vertices) and
               not body['overlaps_or_insufficient_gap'] and body['minimum_beam_radius_mm']>=cfg['beam_clearance_radius_mm'])
    return placed, dict(modules=len(raw), chips=len(active_patches(raw, cfg)), sensor=sensor, body=body,
                        vertices=vertices, endpoint_body_overlap_pass=passing)


def run(cfg, out):
    out.mkdir(parents=True, exist_ok=True)
    source = json.loads(gzip.decompress((ROOT/cfg['baseline']).read_bytes()))
    if digest(ROOT/cfg['baseline']) != cfg['baseline_sha256']:
        raise ValueError('Stale baseline pin')
    rows = []; options = []
    for policy in cfg['policies']:
        controls = cfg['single_scan'] if policy == 'single' else cfg['family_controls']
        for margin, phi_margin in controls:
            raw, rings = candidates(cfg, margin, phi_margin, policy)
            placed, row = screen(raw, cfg, cfg['disc_datum_mm'])
            row.update(policy=policy, radial_margin_mm=margin, phi_margin_mm=phi_margin, rings=rings)
            rows.append(row)
            print(json.dumps(dict(policy=policy, margin=margin, phi_margin=phi_margin, chips=row['chips'], overlap=row['sensor']['overlap_over_union_percent'], annular_overlap=row['sensor']['annular_overlap_over_union_percent'], max_gap=max(v['gap_mm2'] for v in row['vertices']), passes=row['endpoint_body_overlap_pass'])), flush=True)
            if row['endpoint_body_overlap_pass']:
                preferred = max(row['sensor']['overlap_over_union_percent'], row['sensor']['annular_overlap_over_union_percent']) <= cfg['preferred_overlap_percent']
                options.append(((not preferred, row['chips'], row['modules'], max(row['sensor']['overlap_over_union_percent'], row['sensor']['annular_overlap_over_union_percent'])), raw, rings, row))
    datums = cfg['positive_disc_datums_mm']; selected = None; failures = []
    for _, raw, rings, row in sorted(options, key=lambda x: x[0]):
        discs = []; certificates = []
        for z in datums:
            placed, check = screen(raw, cfg, z)
            cert = coverage_certificate(active_patches(placed, cfg), cfg, z)
            discs.append(dict(datum_mm=z, **check)); certificates.append(cert)
            if not check['endpoint_body_overlap_pass'] or not cert['passed']:
                break
        if len(discs)==len(datums) and all(c['passed'] for c in certificates) and all(d['endpoint_body_overlap_pass'] for d in discs):
            selected = raw, rings, row, discs, certificates; break
        failures.append(dict(policy=row['policy'], radial_margin_mm=row['radial_margin_mm'], phi_margin_mm=row['phi_margin_mm'], tested_discs=discs, certificates=certificates))
    report = dict(status='DRAFT / isolated radial PROTOTYPE', baseline=baseline(cfg, source), scan=rows,
                  preferred_overlap_percent=cfg['preferred_overlap_percent'], overlap_limit_percent=cfg['overlap_limit_percent'],
                  selected=None, rejected_certificates=failures,
                  provenance=dict(revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                                  dirty=bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True)),
                                  generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), python=platform.python_version(), numpy=np.__version__, shapely=shapely.__version__,
                                  hashes={str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__), Path(__file__).with_name('radial-inputs.json'), ROOT/cfg['baseline'], ROOT/cfg['services_input'], ROOT/cfg['barrel_services']]}))
    if selected:
        raw, rings, row, discs, certificates = selected
        placed = stagger(raw, cfg, cfg['disc_datum_mm'])
        report.update(selected=row, per_disc_screens=discs, coverage_certificates=certificates,
                      all_18_overlap_body_pass=True, all_18_straight_coverage_pass=True,
                      orientation=orientation_screen(placed, cfg),
                      guard_control_0p5mm=metrics(project(placed, cfg, cfg['disc_datum_mm'], guard=.5), cfg),
                      services=service_estimate(placed, rings, cfg, max(d['body']['maximum_radius_mm'] for d in discs)),
                      negative_side_scope='Reflect complete assemblies and active patches through z=0, reversing u to retain plane-frame parity and outward radial periphery v. Positive proofs supply equivalent negative coverage and body screens.')
        (out/'layout.json').write_text(json.dumps(dict(status=report['status'], modules=placed, active_patches=active_patches(placed, cfg), rings=rings), indent=2)+'\n')
    (out/'screening.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    if not selected:
        raise ValueError('No radial candidate passed all required screens')
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); run(load_config(), a.output)


if __name__ == '__main__':
    main()
