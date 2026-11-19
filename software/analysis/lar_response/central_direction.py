"""Geometry-only central-electron direction check on the frozen staggered SiW XML.

No shower results, native runtime or detector modifications are used.  The exact
compact contains axis-aligned rectangular sensitive prisms in sector zero;
their corners are transformed using the same matrix convention as the factory.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


COMPACT_SHA256 = 'd78ecea5c5aa5173af54a4ce392994491eede936a7f4edb87d55bc72e69a0c2b'
PROTOCOL_REVISION = 'a20ae153d7cf70c9b593df16f390edbfd7a11760'
SOURCE_HASHES = {
    'tools/calorimeter_hardware/barrel_export.py': 'fb79ae53fd58fefccc7edf4c88f856ba8f186b5681190b24f51db44499ab3c99',
    'tools/calorimeter_hardware/assembly_export.py': 'fc43c52b9170f5d510c0dc5256c080b5b6cad1bfec6b5027de2497351da75d94',
    'prototypes/calorimeter/BarrelCalorimeter.cpp': '8871c4d614a9c0b5cc2d91b8df7bfd2580690267085055b645c217c860a9aa6d',
}
ROOT = Path(__file__).resolve().parents[3]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def number(value):
    """Only the frozen export's numeric millimetres/dimensionless attributes."""
    return float(value.removesuffix('*mm'))


def transform(node, point):
    return tuple(number(node.get(axis)) + sum(float(node.get(f'a{i}{j}')) * point[j]
                 for j in range(3)) for i, axis in enumerate(('x', 'y', 'z')))


def load_geometry(compact):
    if sha(compact) != COMPACT_SHA256:
        raise ValueError('Compact differs from the frozen staggered Si-W sample')
    detector = ET.parse(compact).find("detectors/detector[@name='BARREL']")
    if detector is None:
        raise ValueError('Missing frozen barrel')
    templates = {b.get('name'): b for b in detector.findall('board')}
    layers = []
    for region in detector.findall('region'):
        boards = region.findall('board_instance')
        if not boards:
            continue
        replica = detector.find(f"replica[@sector='0'][@region='{region.get('name')}']")
        if replica is None:
            raise ValueError('Missing sector-zero replica')
        prisms = []
        for board in boards:
            sensitive, = templates[board.get('template')].findall("piece[@role='sensitive']")
            vertices = [(number(v.get('x')), number(v.get('y'))) for v in sensitive.findall('vertex')]
            half_depth = number(sensitive.get('depth')) / 2
            corners = [transform(replica, transform(board, transform(sensitive, (x, y, z))))
                       for x, y in vertices for z in (-half_depth, half_depth)]
            bounds = [(min(p[i] for p in corners), max(p[i] for p in corners)) for i in range(3)]
            # A bounding box is exact only when every transformed corner lies on
            # its axis-aligned faces; fail rather than approximate another model.
            if len(vertices) != 4 or any(not any(abs(p[i] - edge) < 1e-9 for edge in bounds[i])
                                         for p in corners for i in range(3)):
                raise ValueError('Frozen sensitive prism is not an axis-aligned rectangle')
            if abs(bounds[0][1] - bounds[0][0] - .5) > 1e-9:
                raise ValueError('Unexpected radial sensitive thickness')
            prisms.append({'module': int(board.get('module')), 'bounds_mm': bounds})
        layers.append({'layer': int(region.get('name').removeprefix('barrel_layer')), 'prisms': prisms})
    if sorted(layer['layer'] for layer in layers) != list(range(48)):
        raise ValueError('Need all 48 frozen barrel layers')
    return sorted(layers, key=lambda layer: layer['layer'])


def ray_box(direction, bounds):
    low, high = 0., math.inf
    for slope, (left, right) in zip(direction, bounds):
        if abs(slope) < 1e-15:
            if not left <= 0 <= right:
                return None
        else:
            a, b = sorted((left / slope, right / slope))
            low, high = max(low, a), min(high, b)
    return (low, high) if high > low else None


def check_direction(layers, eta, phi_deg):
    if not math.isfinite(eta) or not math.isfinite(phi_deg) or abs(phi_deg) >= 11.25:
        raise ValueError('Require finite eta and a direction inside sector zero (|phi| < 11.25 degrees)')
    phi = math.radians(phi_deg)
    direction = (math.cos(phi)/math.cosh(eta), math.sin(phi)/math.cosh(eta), math.tanh(eta))
    records = []
    for layer in layers:
        crossings = []
        nearest = None
        for prism in layer['prisms']:
            bounds = prism['bounds_mm']
            mid_x = sum(bounds[0])/2
            mid_y, mid_z = mid_x*math.tan(phi), mid_x*math.sinh(eta)/math.cos(phi)
            cu = min(mid_y-bounds[1][0], bounds[1][1]-mid_y)
            cv = min(mid_z-bounds[2][0], bounds[2][1]-mid_z)
            candidate = {'module': prism['module'], 'tangential_midplane_clearance_mm': cu,
                         'axial_midplane_clearance_mm': cv, 'signed_midplane_clearance_mm': min(cu, cv)}
            if nearest is None or candidate['signed_midplane_clearance_mm'] > nearest['signed_midplane_clearance_mm']:
                nearest = candidate
            interval = ray_box(direction, bounds)
            if interval is None:
                continue
            entry, exit = interval
            clearance = [min(t*direction[i]-bounds[i][0], bounds[i][1]-t*direction[i])
                         for i in (1, 2) for t in interval]
            radial_span = (exit-entry)*direction[0]
            crossings.append({'module': prism['module'], 'entry_mm': entry, 'exit_mm': exit,
                              'path_mm': exit-entry, 'radial_span_mm': radial_span,
                              'full_thickness': math.isclose(radial_span, .5, rel_tol=0, abs_tol=1e-9),
                              'tangential_clearance_mm': min(clearance[:2]),
                              'axial_clearance_mm': min(clearance[2:])})
        records.append({'layer': layer['layer'], 'crossings': crossings, 'nearest_midplane_window': nearest})
    crossed = [crossing for row in records for crossing in row['crossings']]
    if not crossed:
        raise ValueError('No active sensitive crossings')
    first_radius = min(sum(p['bounds_mm'][0])/2 for p in layers[0]['prisms'])
    return {'point': {'eta': eta, 'phi_deg': phi_deg, 'phi_rad': phi, 'origin_mm': [0, 0, 0]},
            'active_layers': sum(bool(row['crossings']) for row in records), 'total_layers': len(records),
            'missed_layers': [row['layer'] for row in records if not row['crossings']],
            'all_crossings_full_thickness': all(c['full_thickness'] for c in crossed),
            'active_sensor_path_mm': math.fsum(c['path_mm'] for c in crossed),
            'minimum_tangential_clearance_mm': min(c['tangential_clearance_mm'] for c in crossed),
            'minimum_crossed_window_clearance_mm': min(min(c['tangential_clearance_mm'], c['axial_clearance_mm']) for c in crossed),
            'nearest_sector_boundary_separation_deg': 11.25-abs(phi_deg),
            'tangential_sector_boundary_distance_first_plane_mm': first_radius*(math.tan(math.radians(11.25))-abs(math.tan(phi))),
            'layers': records}


def scan(layers, step_deg):
    """Repeat the predeclared geometry-only 0..8 degree clearance scan."""
    if not math.isfinite(step_deg) or not 0 < step_deg <= 8:
        raise ValueError('Invalid scan spacing')
    windows = []
    for layer in layers:
        windows.append(sorted({(sum(p['bounds_mm'][0])/2, sum(p['bounds_mm'][1])/2,
                                (p['bounds_mm'][1][1]-p['bounds_mm'][1][0])/2)
                               for p in layer['prisms']}))
    best_phi, best_score = None, -math.inf
    for index in range(int(round(8/step_deg))+1):
        phi_deg = index*step_deg
        if phi_deg > 8+1e-12:
            break
        tangent = math.tan(math.radians(phi_deg))
        score = math.inf
        for layer in windows:
            score = min(score, max(half-abs(radius*tangent-centre) for radius, centre, half in layer))
            if score < best_score:
                break
        if score > best_score:
            best_phi, best_score = phi_deg, score
    return {'range_deg': [0, 8], 'step_deg': step_deg,
            'criterion': 'maximum of minimum tangential midplane active-window clearance over all layers',
            'best_phi_deg': best_phi, 'best_phi_rad': math.radians(best_phi),
            'minimum_tangential_midplane_clearance_mm': best_score,
            'limitation': 'Finite geometry-only scan, not a shower-response optimum'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compact', required=True, type=Path)
    parser.add_argument('--eta', type=float, default=.1)
    parser.add_argument('--phi-deg', type=float, default=.7)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--scan', action='store_true')
    parser.add_argument('--scan-step-deg', type=float, default=.0001)
    args = parser.parse_args()
    for path, digest in SOURCE_HASHES.items():
        if sha(ROOT/path) != digest:
            raise ValueError('Geometry source differs from recorded direction check: '+path)
    layers = load_geometry(args.compact)
    result = {'status': 'PROTOTYPE / analytical geometry check', 'compact_sha256': sha(args.compact),
              'script_sha256': sha(__file__), 'source_sha256': SOURCE_HASHES,
              'source_revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
              'prospective_protocol_revision': PROTOCOL_REVISION,
              'method': 'Exact XML transform of rectangular sensitive prisms; normalized origin-ray clipping through finite 0.5mm radial thickness',
              'limitation': 'No native navigator or shower check; favourable interior direction, not completely gap-free or a global response optimum',
              **check_direction(layers, args.eta, args.phi_deg)}
    if args.scan:
        result['geometry_scan'] = scan(layers, args.scan_step_deg)
    text = json.dumps(result, indent=2, allow_nan=False)+'\n'
    if args.output:
        if args.output.exists():
            raise FileExistsError('Refusing to overwrite existing direction evidence')
        args.output.write_text(text)
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
