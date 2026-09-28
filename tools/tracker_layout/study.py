#!/usr/bin/env python3
"""PROTOTYPE: ideal surfaces, first outward crossing, uniform axial field.

No module masks, detector construction, tracking efficiency or physical budget.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

KAPPA = 0.299792458  # pT [GeV] / (B[T] * radius[m])


def validate(data):
    if data['schema_version'] != 1 or data['units'] != {
        'length': 'm', 'momentum': 'GeV', 'field': 'T', 'x0': 'percent'
    }:
        raise ValueError('Unsupported units/schema')
    host = data['host']
    seen = set()
    candidates_seen = set()
    scan = data['scan']
    for key in ['eta_min', 'eta_max', 'eta_step']:
        if isinstance(scan[key], bool) or not math.isfinite(scan[key]):
            raise ValueError('Non-finite/non-numeric scan')
    if scan['eta_step'] <= 0 or scan['eta_min'] >= scan['eta_max']:
        raise ValueError('Invalid eta scan')
    for candidate in data['candidates']:
        if candidate['id'] in candidates_seen:
            raise ValueError('Duplicate candidate ID')
        candidates_seen.add(candidate['id'])
        for layer in candidate['layers']:
            if layer['id'] in seen:
                raise ValueError('Duplicate surface ID')
            seen.add(layer['id'])
            for key, val in layer.items():
                if key.endswith(('_m', '_percent')) and (
                    isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(val)
                ):
                    raise ValueError('Non-finite/non-numeric parameter')
            if layer['kind'] == 'cylinder':
                rlo = rhi = layer['r_m']
                zlo, zhi = layer['z_min_m'], layer['z_max_m']
                if zlo >= zhi:
                    raise ValueError('Empty cylinder')
            elif layer['kind'] == 'disc':
                rlo, rhi = layer['r_min_m'], layer['r_max_m']
                zlo = zhi = layer['z_m']
                if rlo >= rhi:
                    raise ValueError('Empty disc')
            else:
                raise ValueError('Unsupported surface')
            if not (host['r_min_m'] <= rlo <= rhi <= host['r_max_m'] and
                    -host['abs_z_max_m'] <= zlo <= zhi <= host['abs_z_max_m']):
                raise ValueError('Surface outside fixed host')
            if layer['x0_percent'] < 0 or min(layer['sigma_rphi_m'], layer['sigma_second_m']) <= 0:
                raise ValueError('Invalid material/response')


def intersection(layer, eta, vertex_z, pt, field):
    """Return (r,z,path,X/X0 percent); include exact active edges, no curling returns."""
    if pt <= 0:
        raise ValueError('pT must be positive')
    rho = math.inf if field == 0 else pt / (KAPPA * abs(field))
    sh, ch = math.sinh(eta), math.cosh(eta)
    if layer['kind'] == 'cylinder':
        r = layer['r_m']
        if r >= 2 * rho:
            return None  # tangent/turning point has no stable material crossing
        st = r if math.isinf(rho) else 2 * rho * math.asin(r / (2 * rho))
        z = vertex_z + st * sh
        if not layer['z_min_m'] <= z <= layer['z_max_m']:
            return None
        cosine = math.sqrt(1 - (r / (2 * rho)) ** 2) / ch
    else:
        if sh == 0:
            return None
        z = layer['z_m']
        st = (z - vertex_z) / sh
        if st <= 0 or st >= math.pi * rho:
            return None
        r = st if math.isinf(rho) else 2 * rho * math.sin(st / (2 * rho))
        if not layer['r_min_m'] <= r <= layer['r_max_m']:
            return None
        cosine = abs(math.tanh(eta))
    return r, z, st * ch, layer['x0_percent'] / cosine


def sample(candidate, eta, vertex_z, pt, field):
    hits = [(layer, intersection(layer, eta, vertex_z, pt, field)) for layer in candidate['layers']]
    hits = sorted([(layer, hit) for layer, hit in hits if hit is not None], key=lambda item: item[1][2])
    radii = [hit[0] for _, hit in hits]
    return {
        'stations': len(hits),
        'pixel_stations': sum(layer['subsystem'] == 'pixel' for layer, _ in hits),
        'short_strip_stations': sum(layer['subsystem'] == 'short_strip' for layer, _ in hits),
        'long_strip_pair_stations': sum(layer['subsystem'] == 'long_strip' for layer, _ in hits),
        'radial_span_m': max(radii) - min(radii) if radii else 0,
        'local_material_percent': sum(hit[3] for _, hit in hits),
        'surface_ids': [layer['id'] for layer, _ in hits],
    }


def area(candidate):
    result = dict(pixel=0., short_strip=0., long_strip=0.)
    for layer in candidate['layers']:
        value = (2 * math.pi * layer['r_m'] * (layer['z_max_m'] - layer['z_min_m'])
                 if layer['kind'] == 'cylinder' else
                 math.pi * (layer['r_max_m'] ** 2 - layer['r_min_m'] ** 2))
        result[layer['subsystem']] += value
    return result  # reference surface area, long-strip silicon area is twice this


def run(data):
    validate(data)
    scan = data['scan']
    n = round((scan['eta_max'] - scan['eta_min']) / scan['eta_step'])
    etas = [round(scan['eta_min'] + i * scan['eta_step'], 10) for i in range(n + 1)]
    output = {}
    for candidate in data['candidates']:
        profiles, extremes = [], []
        for b in scan['field_T']:
            for pt in scan['pt_GeV']:
                for zv in scan['vertex_z_m']:
                    rows = [sample(candidate, eta, zv, pt, b) for eta in etas]
                    low = min(row['stations'] for row in rows)
                    extremes.append(dict(field_T=b, pt_GeV=pt, vertex_z_m=zv,
                                         min_stations=low, min_pixel_stations=min(r['pixel_stations'] for r in rows),
                                         min_station_etas=[e for e, r in zip(etas, rows) if r['stations'] == low],
                                         max_local_material_percent=max(r['local_material_percent'] for r in rows)))
                    if b == scan['baseline_field_T'] and pt in [1., 100.]:
                        profiles.append(dict(field_T=b, pt_GeV=pt, vertex_z_m=zv,
                                             stations=[r['stations'] for r in rows[::5]],
                                             pixel_stations=[r['pixel_stations'] for r in rows[::5]],
                                             local_material_percent=[r['local_material_percent'] for r in rows[::5]],
                                             radial_span_m=[r['radial_span_m'] for r in rows[::5]]))
        landmarks = []
        for eta in [0., 1., 2., 2.5, 3., 3.5, 3.9, 4.]:
            for zv in scan['vertex_z_m']:
                landmarks.append(dict(eta=eta, vertex_z_m=zv, pt_GeV=10., field_T=3.,
                                      **sample(candidate, eta, zv, 10., 3.)))
        output[candidate['id']] = dict(reference_area_m2=area(candidate),
                                       effective_surface_count=len(candidate['layers']),
                                       extrema=extremes, profiles=profiles, landmarks=landmarks)
    return dict(eta_grid=etas[::5], profile_eta_step=scan['eta_step'] * 5,
                extrema_eta_step=scan['eta_step'], candidates=output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    report = run(data)
    report['metadata'] = {
        'status': 'PROTOTYPE characterization; no detector acceptance',
        'command': ' '.join(sys.argv), 'python': platform.python_version(),
        'project_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'working_tree_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'])),
        'input_sha256': hashlib.sha256(args.input.read_bytes()).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'seed': None, 'sampling': data['scan'],
        'limitations': ['Uniform-field first outward intersections of ideal surfaces, no azimuth gaps',
                        'Count each effective stereo pair once, not individual silicon faces',
                        'No beam pipe or remote services, no efficiency, occupancy, fit or timing',
                        'Exact active edges included; sampled grids do not prove hermeticity',
                        'Surface area is not installed sensor area, mass, cost or power'],
    }
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print('Wrote', args.output)


if __name__ == '__main__':
    main()
