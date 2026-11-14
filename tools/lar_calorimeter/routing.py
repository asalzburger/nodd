"""Export isolated, constituent-volume-preserving old/new service-route models."""
import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from barrel_geometry import material_model

ROOT = Path(__file__).resolve().parents[2]
CONFIG = Path(__file__).with_name('routing_config.json')


def sha(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def dot(a, b): return math.fsum(x*y for x, y in zip(a, b))
def add(a, b): return [x+y for x, y in zip(a, b)]
def scale(a, k): return [x*k for x in a]
def sub(a, b): return [x-y for x, y in zip(a, b)]
def cross(a, b): return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]


def unit(vector):
    length = math.sqrt(dot(vector, vector))
    if not math.isfinite(length) or length < 1e-9: raise ValueError('Degenerate/reversing route segment or join')
    return scale(vector, 1/length)


def segments(vertices, phi):
    tangents = [unit(sub(b, a)) for a, b in zip(vertices, vertices[1:])]
    result = []
    transverse = [-math.sin(phi), math.cos(phi), 0.]
    for i, (a, b, tangent) in enumerate(zip(vertices, vertices[1:], tangents)):
        bottom = scale(unit(add(tangents[i-1], tangent)), -1) if i else scale(tangent, -1)
        top = unit(add(tangent, tangents[i+1])) if i+1 < len(tangents) else tangent
        frame = [transverse, unit(cross(tangent, transverse)), tangent]
        low, high = [[dot(axis, normal) for axis in frame] for normal in (bottom, top)]
        if low[2] >= -1e-6 or high[2] <= 1e-6: raise ValueError('Degenerate miter plane')
        result.append(dict(index=i, center_mm=scale(add(a, b), .5), frame=frame,
                           length_mm=math.sqrt(dot(sub(b, a), sub(b, a))),
                           low_normal_local=low, high_normal_local=high,
                           low_normal_global=bottom, high_normal_global=top))
    return result


def validate(c, services):
    if set(c) != set(json.loads(CONFIG.read_text())): raise ValueError('Unsupported routing configuration keys')
    numeric = [v for v in c.values() if isinstance(v, (int, float))]
    if any(not math.isfinite(v) or v <= 0 for v in numeric): raise ValueError('Positive finite routing parameter required')
    if not 0 < c['arc_step_deg'] <= 30: raise ValueError('Arc step must be in (0,30] degrees')
    if not isinstance(c['stations_each_side'], int) or c['stations_each_side'] < 1 or c['stations_each_side'] > 64:
        raise ValueError('Invalid representative route multiplicity')
    if c['sides'] != [-1, 1]: raise ValueError('Both proper signed ends are required')
    if set(c['s_bend_start_abs_z_mm']) != {'old', 'new'}: raise ValueError('Old and new starts required')
    if c['prototype_system_id'] != 240: raise ValueError('Isolated routing system ID is fixed at240')
    for key, reference in [('cold_radius_mm', 'nitrogen_pipe_radius_mm'), ('external_radius_mm', 'external_route_radius_mm')]:
        if c[key] != services[reference]: raise ValueError('Routing reference changed: '+key)
    if (services['nitrogen_pipe_id_mm'], services['nitrogen_pipe_od_mm'], services['nitrogen_effective_density_g_cm3']) != (18, 20, .02):
        raise ValueError('Selected existing pipe construction changed')
    delta = c['external_radius_mm']-c['cold_radius_mm']
    if not 0 < delta < 2*c['bend_radius_mm']: raise ValueError('Invalid two-arc outward offset')
    theta = math.acos(1-delta/(2*c['bend_radius_mm']))
    advance = 2*c['bend_radius_mm']*math.sin(theta)
    for start in c['s_bend_start_abs_z_mm'].values():
        if not math.isfinite(start) or not c['upstream_abs_z_mm'] < start < c['rear_turn_start_abs_z_mm']-advance:
            raise ValueError('Nonpositive upstream/downstream route straight')
    if c['handoff_radius_mm'] <= c['external_radius_mm']+c['bend_radius_mm']:
        raise ValueError('Nonpositive rear radial handoff')


def centreline(c, variant):
    if variant not in ('old', 'new'): raise ValueError('Unknown route variant')
    radius = c['bend_radius_mm']; r0 = c['cold_radius_mm']; r1 = c['external_radius_mm']
    start = c['s_bend_start_abs_z_mm'][variant]
    theta = math.acos(1-(r1-r0)/(2*radius))
    n = math.ceil(math.degrees(theta)/c['arc_step_deg']); rear_n = math.ceil(90/c['arc_step_deg'])
    if max(n, rear_n) > 10000: raise ValueError('Arc resolution exceeds bounded prototype capacity')
    points = [[c['upstream_abs_z_mm'], r0], [start, r0]]
    for i in range(1, n+1):
        t = theta*i/n
        points.append([start+radius*math.sin(t), r0+radius*(1-math.cos(t))])
    middle = points[-1]
    for i in range(1, n+1):
        u = theta*i/n
        points.append([middle[0]+radius*(math.sin(theta)-math.sin(theta-u)),
                       middle[1]+radius*(math.cos(theta-u)-math.cos(theta))])
    points[-1] = [start+2*radius*math.sin(theta), r1]
    points.append([c['rear_turn_start_abs_z_mm'], r1])
    for i in range(1, rear_n+1):
        t = math.pi/2*i/rear_n
        points.append([c['rear_turn_start_abs_z_mm']+radius*math.sin(t), r1+radius*(1-math.cos(t))])
    points.append([c['rear_turn_start_abs_z_mm']+radius, c['handoff_radius_mm']])
    analytic = ((start-c['upstream_abs_z_mm'])+2*radius*theta+
                (c['rear_turn_start_abs_z_mm']-start-2*radius*math.sin(theta))+
                math.pi/2*radius+(c['handoff_radius_mm']-r1-radius))
    poly = math.fsum(math.dist(a, b) for a, b in zip(points, points[1:]))
    sagitta = radius*(1-math.cos(max(theta/n, math.pi/2/rear_n)/2))
    return points, analytic, poly, sagitta


def build(variant, config=None, services=None):
    c = deepcopy(config or json.loads(CONFIG.read_text()))
    services = deepcopy(services or json.loads((Path(__file__).with_name('services.json')).read_text()))
    validate(c, services)
    rz, analytic, poly, sagitta = centreline(c, variant)
    radius_scale = math.sqrt(analytic/poly)
    nominal = dict(inner=services['nitrogen_pipe_id_mm']/2, outer=services['nitrogen_pipe_od_mm']/2)
    adjusted = {key: value*radius_scale for key, value in nominal.items()}
    paths = []; probes = []
    for side in c['sides']:
        for station in range(c['stations_each_side']):
            phi = 2*math.pi*station/c['stations_each_side']
            vertices = [[r*math.cos(phi), r*math.sin(phi), side*z] for z, r in rz]
            pieces = segments(vertices, phi)
            for piece in pieces:
                low, high = piece['low_normal_local'], piece['high_normal_local']
                slope = math.hypot(low[0]/low[2]-high[0]/high[2], low[1]/low[2]-high[1]/high[2])
                piece['minimum_full_disk_thickness_mm'] = piece['length_mm']-adjusted['outer']*slope
                if piece['minimum_full_disk_thickness_mm'] <= 0: raise ValueError('Miter end planes cross within full pipe disk')
            path = dict(name=f'route_{"m" if side < 0 else "p"}_{station}', side=side, station=station,
                        phi_rad=phi, vertices_mm=vertices, segments=pieces)
            paths.append(path)
            transverse = [-math.sin(phi), math.cos(phi), 0.]
            for i in range(len(pieces)-1):
                normal = pieces[i]['high_normal_global']; point = vertices[i+1]
                for material, radial in [('PrototypeNitrogenTwoPhase', 0.), ('lArCaloSteel', (adjusted['inner']+adjusted['outer'])/2)]:
                    for sign in (-1, 1):
                        p = add(add(point, scale(transverse, radial)), scale(normal, sign*c['joint_probe_distance_mm']))
                        probes.append(dict(path=path['name'], joint=i, sign=sign, point_mm=p, material=material,
                                           crossing_normal=normal, expected_boundary_distance_mm=c['joint_probe_distance_mm']))
    m = material_model(); m.add('PrototypeNitrogenTwoPhase', .02, {'N': 1.})
    route_count = len(paths)
    targets = {'lArCaloSteel': math.pi*(nominal['outer']**2-nominal['inner']**2)*analytic,
               'PrototypeNitrogenTwoPhase': math.pi*nominal['inner']**2*analytic}
    totals = {name: dict(volume_mm3_per_route=volume, volume_mm3=route_count*volume,
                        mass_g=route_count*volume*m.recipes[name]['density_g_cm3']/1000) for name, volume in targets.items()}
    return dict(status='PROTOTYPE', variant=variant, config=c, route_count=route_count,
                multiplicity='One representative pipe per declared azimuth/end; not an engineered circuit/station bill',
                paths=paths, joint_probes=probes, analytic_length_mm=analytic, polyline_length_mm=poly,
                radius_scale=radius_scale, nominal_radii_mm=nominal, adjusted_radii_mm=adjusted,
                max_sagitta_mm=sagitta, material_totals=totals,
                physical_segments=route_count*(len(rz)-1), physical_material_pieces=2*route_count*(len(rz)-1),
                materials={name:m.recipes[name] for name in ('lArCaloSteel', 'PrototypeNitrogenTwoPhase')},
                empty_envelopes=dict(materialised=False, excluded_from_material_inventory=True,
                    reference_only='Existing cable/jacket reservations; actual individual routes and walls undefined',
                    station_bundle=services['station_bundle'],
                    nitrogen_external_jacket_od_mm=services['nitrogen_external_jacket_od_mm'],
                    lar_utility_external_od_mm=services['lar_utility_external_od_mm'],
                    ordinary_lane_mm=services['ordinary_lane_mm'], utility_lane_mm=services['utility_lane_mm']),
                limitations=['Standalone component only; baseline solids are not cut, moved or replaced.',
                    'Mitered circular chords with adjusted radii preserve constituent volume; bends are not manufactured elbows.',
                    'Nitrogen density is the existing provisional mass hypothesis, not a fluid-state or flow result.',
                    'Pressure/vacuum interfaces, complete circuits and collision-free integration remain unresolved.']), m


def export(args):
    config = json.loads(args.config.read_text())
    if args.arc_step_deg is not None: config['arc_step_deg'] = args.arc_step_deg
    report, materials = build(args.variant, config)
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=False)
    materials_path = output/'materials.xml'; ET.indent(materials.root)
    ET.ElementTree(materials.root).write(materials_path, encoding='utf-8', xml_declaration=True)
    root = ET.Element('lccdd'); ET.SubElement(root, 'info', name='IsolatedLArRouting', title='Material-preserving routing prototype', author='nODD', version='0.1', status='prototype')
    ET.SubElement(ET.SubElement(root, 'includes'), 'gdmlFile', ref='materials.xml')
    define = ET.SubElement(root, 'define')
    for key, value in [('world_x', 6000), ('world_y', 6000), ('world_z', 7500)]: ET.SubElement(define, 'constant', name=key, value=f'{value}*mm')
    detector = ET.SubElement(ET.SubElement(root, 'detectors'), 'detector', name='LArRouting'+args.variant.title(), id=str(config['prototype_system_id']), type='nODDLArRoutingPrototype')
    for path in report['paths']:
        node = ET.SubElement(detector, 'route', name=path['name'], side=str(path['side']), station=str(path['station']))
        for segment in path['segments']:
            attrs = dict(name=path['name']+f'_s{segment["index"]}', length=f'{segment["length_mm"]:.17g}*mm',
                         rinner=f'{report["adjusted_radii_mm"]["inner"]:.17g}*mm', router=f'{report["adjusted_radii_mm"]["outer"]:.17g}*mm',
                         wall_material='lArCaloSteel', core_material='PrototypeNitrogenTwoPhase')
            for axis, value in zip('xyz', segment['center_mm']): attrs[axis] = f'{value:.17g}*mm'
            for row in range(3):
                for col in range(3): attrs[f'a{row}{col}'] = format(segment['frame'][col][row], '.17g')
            for prefix, normal in [('lo', segment['low_normal_local']), ('hi', segment['high_normal_local'])]:
                for axis, value in zip('xyz', normal): attrs[prefix+axis] = format(value, '.17g')
            ET.SubElement(node, 'segment', **attrs)
    ET.indent(root); ET.ElementTree(root).write(output/'routing.xml', encoding='utf-8', xml_declaration=True)
    sources = [Path(__file__), args.config, Path(__file__).with_name('services.json'), Path(__file__).with_name('barrel_geometry.py'), ROOT/'prototypes/lar_routing/LArRouting.cpp', ROOT/'prototypes/lar_routing/CMakeLists.txt']
    report['source_sha256'] = {str(p.resolve().relative_to(ROOT)):sha(p) for p in sources}
    report['artifact_sha256'] = {name:sha(output/name) for name in ('routing.xml', 'materials.xml')}
    report['execution'] = dict(commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), dirty=bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True)))
    save(output/'expected.json', report)
    print(json.dumps({key:report[key] for key in ('variant', 'route_count', 'physical_segments', 'analytic_length_mm', 'polyline_length_mm', 'radius_scale', 'max_sagitta_mm', 'material_totals')}, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--variant', choices=['old', 'new'], required=True)
    p.add_argument('--config', type=Path, default=CONFIG); p.add_argument('--arc-step-deg', type=float)
    p.add_argument('--output', type=Path, required=True); export(p.parse_args())
