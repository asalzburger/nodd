"""DES032 independently derived inclined plates, active gaps and readout.

All dimensional arithmetic is in mm. Straight faces are intersected with named
annular layers exactly; no imported detector factory or uniform active shell.
"""
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/pixel_barrel_dd4hep'))
from materials import Materials, ELEMENTS
I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
ID_FIELDS = [('system', 8), ('plane', 11), ('layer', 4), ('gap', 1), ('theta', -12)]
ID_DESCRIPTOR = ','.join(f'{k}:{n}' for k, n in ID_FIELDS)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def cross(a, b):
    return a[0]*b[1]-a[1]*b[0]


def rotate(p, angle):
    c, s = math.cos(angle), math.sin(angle)
    return [c*p[0]-s*p[1], s*p[0]+c*p[1]]


def rotation(angle):
    c, s = math.cos(angle), math.sin(angle)
    # Columns of a right-handed rotation, matching existing piece protocols.
    return [[c, s, 0], [-s, c, 0], [0, 0, 1]]


def clip(poly, normal, bound):
    """Clip a convex polygon to dot(normal,p) <= bound."""
    out = []
    for a, b in zip(poly, poly[1:]+poly[:1]):
        fa, fb = dot(normal, a)-bound, dot(normal, b)-bound
        if fa <= 0:
            out.append(a)
        if (fa < 0 < fb) or (fb < 0 < fa):
            t = fa/(fa-fb)
            out.append([a[k]+t*(b[k]-a[k]) for k in range(2)])
    return out


def disk_polygon_area(poly, radius):
    """Green's-theorem integral for polygon intersected with a centred disk.

Each edge is split at circle crossings. Interior pieces contribute triangle
area; exterior pieces contribute the circular sector between their endpoints.
"""
    result = 0.0
    for a, b in zip(poly, poly[1:]+poly[:1]):
        delta = [b[k]-a[k] for k in range(2)]
        aa, bb, cc = dot(delta, delta), 2*dot(a, delta), dot(a, a)-radius**2
        ts = [0., 1.]
        discriminant = bb*bb-4*aa*cc
        if aa > 0 and discriminant > 0:
            root = math.sqrt(discriminant)
            ts += [t for t in ((-bb-root)/(2*aa), (-bb+root)/(2*aa)) if 0 < t < 1]
        ts.sort()
        for lo, hi in zip(ts, ts[1:]):
            u = [a[k]+lo*delta[k] for k in range(2)]
            v = [a[k]+hi*delta[k] for k in range(2)]
            m = [a[k]+(lo+hi)/2*delta[k] for k in range(2)]
            result += cross(u, v)/2 if dot(m, m) <= radius**2 else radius**2*math.atan2(cross(u, v), dot(u, v))/2
    return abs(result)


def annular_area(poly, inner, outer):
    return disk_polygon_area(poly, outer)-disk_polygon_area(poly, inner)


def face_point(normal, bound, radius, outward):
    """Positive-branch intersection of a line face with a centred circle."""
    if abs(bound) >= radius:
        raise ValueError('Face does not intersect sampling circle')
    base = [normal[k]*bound for k in range(2)]
    t = math.sqrt(radius*radius-bound*bound)
    return [base[k]+outward[k]*t for k in range(2)]


def polygon_between_faces(lower, upper, radii, outward):
    """Bounded exact face wedge. Annular CSG performs physical end clipping.

The enclosing planes have a 10 mm numerical construction margin. They lie
outside the circle/face intersection and add no physical material.
"""
    nl, bl = lower
    nu, bu = upper
    intersections = [face_point(n, b, r, [n[1], -n[0]])
                     for n, b in (lower, upper) for r in radii]
    lo = min(dot(outward, p) for p in intersections)-10
    hi = max(dot(outward, p) for p in intersections)+10
    extent = 2*radii[1]
    p = [[-extent, -extent], [extent, -extent], [extent, extent], [-extent, extent]]
    for n, b in (([-x for x in nl], -bl), (nu, bu), ([-x for x in outward], -lo), (outward, hi)):
        p = clip(p, n, b)
    if len(p) < 3 or annular_area(p, *radii) <= 0:
        raise ValueError('Nonpositive face gap or material prism')
    return p


def inside_polygon(poly, p, tolerance=1e-8):
    signs = [cross([b[k]-a[k] for k in range(2)], [p[k]-a[k] for k in range(2)]) for a, b in zip(poly, poly[1:]+poly[:1])]
    return min(signs) >= -tolerance or max(signs) <= tolerance


def point_on_gap(piece, radius):
    a = face_point(*piece['lower_face'], radius, [piece['lower_face'][0][1], -piece['lower_face'][0][0]])
    b = face_point(*piece['upper_face'], radius, [piece['upper_face'][0][1], -piece['upper_face'][0][0]])
    phi = math.atan2(a[1], a[0])+math.atan2(cross(a, b), dot(a, b))/2
    return [radius*math.cos(phi), radius*math.sin(phi)]


def theta_index(theta, layer, readout):
    fine = math.floor((theta-readout['theta_offset_rad'])/readout['theta_fine_pitch_rad']+.5)
    merge = readout['theta_merging'][layer]
    return merge*math.floor(fine/merge)


def theta_bounds(index, layer, readout):
    h, o, m = readout['theta_fine_pitch_rad'], readout['theta_offset_rad'], readout['theta_merging'][layer]
    return o+(index-.5)*h, o+(index+m-.5)*h


def canonical_reference(piece, index, readout):
    """Interior point for a clipped theta group in canonical plane0/gap0."""
    r0, r1, hz = piece['clip_annulus_mm']['rmin'], piece['clip_annulus_mm']['rmax'], piece['depth_mm']/2
    minimum = math.atan2(r0, hz)
    lo, hi = theta_bounds(index, piece['layer'], readout)
    lo, hi = max(lo, minimum), min(hi, math.pi-minimum)
    if not lo < hi:
        raise ValueError('Ghost theta group outside physical layer')
    theta = (lo+hi)/2
    bound = hz*math.tan(min(theta, math.pi-theta)) if abs(theta-math.pi/2) > 1e-12 else float('inf')
    # Choose away from both annular and axial boundaries, including end groups.
    radius = min((r0+r1)/2, (r0+min(r1, bound))/2)
    point = point_on_gap(piece, radius)+[radius/math.tan(theta)]
    if not r0 < radius < r1 or abs(point[2]) >= hz or not inside_polygon(piece['vertices_mm'], point[:2]):
        raise ValueError('Reference outside canonical active gap')
    if theta_index(math.atan2(radius, point[2]), piece['layer'], readout) != index:
        raise ValueError('Theta reference roundtrip')
    return point


def encode(fields):
    value, offset = 0, 0
    for key, signed_bits in ID_FIELDS:
        bits = abs(signed_bits)
        v = fields.get(key, 0)
        lo, hi = (-(1 << (bits-1)), (1 << (bits-1))-1) if signed_bits < 0 else (0, (1 << bits)-1)
        if not lo <= v <= hi:
            raise ValueError('ID field out of range: '+key)
        value |= (v & ((1 << bits)-1)) << offset
        offset += bits
    return value


def decode(value):
    fields, offset = {}, 0
    for key, signed_bits in ID_FIELDS:
        bits = abs(signed_bits)
        v = (value >> offset) & ((1 << bits)-1)
        if signed_bits < 0 and v >= 1 << (bits-1):
            v -= 1 << bits
        fields[key] = v
        offset += bits
    return fields


def logical_id(fields, theta, readout):
    if not 0 <= fields['plane'] < readout['planes'] or fields['gap'] not in (0, 1):
        raise ValueError('Invalid raw electrode/gap')
    out = dict(fields)
    out['plane'] = fields['plane']//readout['phi_merge']*readout['phi_merge']
    out['gap'] = 0
    out['theta'] = theta_index(theta, out['layer'], readout)
    return encode(out)


def material_model():
    m = Materials.__new__(Materials)
    m.root, m.recipes, m.cache = ET.Element('materials'), {}, {}
    for item in ELEMENTS:
        e = ET.SubElement(m.root, 'element', name=item['name'], formula=item['name'], Z=str(item['Z']))
        ET.SubElement(e, 'atom', type='A', value=str(item['A']), unit='g/mol')
    m.add('Air', .0012, {'N': .754, 'O': .234, 'Ar': .012})
    m.add('Vacuum', 1e-12, {'H': 1.})
    m.add('LAr', 1.396, {'Ar': 1.})
    m.add('Aluminium', 2.699, {'Al': 1.})
    m.add('Lead', 11.35, {'Pb': 1.})
    m.add('lArCaloSteel', 7.84, {'Fe': .7175, 'Cr': .19, 'Ni': .0925})
    m.add('lArCaloGlue', 1.69, {'C': 5, 'H': 8, 'O': 4, 'Si': 1}, atoms=True)
    source = {'Si': .180774, 'O': .405633, 'C': .278042, 'H': .0684428, 'Br': .0671091}
    norm = sum(source.values())
    m.add('PCB', 1.7, {k: v/norm for k, v in source.items()})
    m.recipes['PCB']['source_mass_fractions'] = source
    m.recipes['PCB']['normalization'] = norm
    return m


def validate_config(c):
    for key, value in c.items():
        if isinstance(value, (int, float)) and (not math.isfinite(value) or value <= 0):
            raise ValueError('Positive finite parameter required: '+key)
    if c['planes'] < 8 or c['planes'] > 2048 or c['planes'] % c['phi_merge']:
        raise ValueError('Plane count / phi merging / ID capacity')
    if not math.isclose(c['theta_pitch_rad'], 4*c['theta_fine_pitch_rad'], rel_tol=1e-12):
        raise ValueError('Fine/regular theta pitch mismatch')
    if c['phi_merge'] != 2 or c['theta_merging'] != [4, 1]+[4]*9:
        raise ValueError('DES032 grouped readout contract')
    if len(c['segments_mm']) != 11 or any(x <= 0 or not math.isfinite(x) for x in c['segments_mm']):
        raise ValueError('Eleven positive finite compartments required')
    if not 0 < c['inclination_deg'] < 90 or c['sampling_inner_radius_mm'] >= c['sampling_outer_radius_mm']:
        raise ValueError('Sampling circle/inclination')
    if c['warm_half_z_mm'] <= sum(c[k] for k in ('end_warm_mm', 'end_vacuum_mm', 'end_cold_mm'))+c.get('end_bath_mm', 0):
        raise ValueError('Sampling half length')
    entrance = c['warm_inner_radius_mm']+sum(c[k] for k in ('front_warm_mm', 'front_vacuum_mm', 'front_cold_mm', 'front_bath_mm'))
    if abs(entrance-c['sampling_inner_radius_mm']) > 1e-8:
        raise ValueError('Front cryostat/bath closure')


def build(config=None):
    c = config or json.loads((ROOT/'tools/lar_calorimeter/barrel.json').read_text())
    validate_config(c)
    m = material_model()
    r0, r1 = c['sampling_inner_radius_mm'], c['sampling_outer_radius_mm']
    alpha, period = math.radians(c['inclination_deg']), 2*math.pi/c['planes']
    d, normal, p = [math.cos(alpha), math.sin(alpha)], [-math.sin(alpha), math.cos(alpha)], [r0, 0]
    path = -r0*math.cos(alpha)+math.sqrt(r1*r1-r0*r0*math.sin(alpha)**2)
    remainder = path-sum(c['segments_mm'])
    if abs(remainder) > 1e-3:
        raise ValueError('Tabulated path does not close sampling boundary')
    lengths = list(c['segments_mm']); lengths[-1] += remainder
    endpoints = [0.]
    for length in lengths:
        endpoints.append(endpoints[-1]+length)
    radii = [math.hypot(r0+t*d[0], t*d[1]) for t in endpoints]
    radii[-1] = r1
    cold_inner_half = c['warm_half_z_mm']-sum(c[k] for k in ('end_warm_mm', 'end_vacuum_mm', 'end_cold_mm'))
    hz = cold_inner_half-c.get('end_bath_mm', 0)
    absorber = c['lead_mm']+c['steel_total_mm']+c['glue_total_mm']
    def face(angle, shift):
        n, pp = rotate(normal, angle), rotate(p, angle)
        return [n, dot(n, pp)+shift]
    pieces = []
    def prism(name, role, material, lower, upper, layer, gap=None):
        poly = polygon_between_faces(lower, upper, radii[layer:layer+2], rotate(d, period/4))
        volume = annular_area(poly, *radii[layer:layer+2])*2*hz
        item = dict(name=name, role=role, material=material, shape_kind='xtru', vertices_mm=poly,
                    depth_mm=2*hz, clip_annulus_mm=dict(rmin=radii[layer], rmax=radii[layer+1]),
                    center_mm=[0, 0, 0], frame=I, layer=layer, volume_mm3=volume,
                    mass_g=volume*m.recipes[material]['density_g_cm3']/1000,
                    lower_face=lower, upper_face=upper)
        if gap is not None:
            item['gap'] = gap
        pieces.append(item)
    halflead, halfglue, halfsteel = c['lead_mm']/2, c['glue_total_mm']/2, c['steel_total_mm']/2
    for layer in range(11):
        prism(f'core_{layer}', 'absorber_core', 'LAr' if layer == 0 else 'Lead', face(0, -halflead), face(0, halflead), layer)
        for side in (-1, 1):
            lo, hi = sorted([side*halflead, side*(halflead+halfglue)])
            prism(f'glue_{side}_{layer}', 'absorber_glue', 'lArCaloGlue', face(0, lo), face(0, hi), layer)
            lo, hi = sorted([side*(halflead+halfglue), side*(halflead+halfglue+halfsteel)])
            prism(f'steel_{side}_{layer}', 'absorber_skin', 'lArCaloSteel', face(0, lo), face(0, hi), layer)
        prism(f'pcb_{layer}', 'electrode', 'PCB', face(period/2, -c['electrode_mm']/2), face(period/2, c['electrode_mm']/2), layer)
        prism(f'gap_0_{layer}', 'sensitive', 'LAr', face(0, absorber/2), face(period/2, -c['electrode_mm']/2), layer, 0)
        prism(f'gap_1_{layer}', 'sensitive', 'LAr', face(period/2, c['electrode_mm']/2), face(period, -absorber/2), layer, 1)
    # Explicit disjoint shell/end ownership. Bath voids may be displaced later by
    # root-owned service geometry; cutters must have a conserved exclusive ledger.
    passive = []
    def tube(name, role, material, a, b, half, z=0):
        volume = math.pi*(b*b-a*a)*2*half
        passive.append(dict(name=name, role=role, material=material, shape_kind='tube', dimensions_mm=dict(rmin=a, rmax=b, length=2*half), center_mm=[0, 0, z], frame=I, volume_mm3=volume, mass_g=volume*m.recipes[material]['density_g_cm3']/1000))
    front_warm = c['warm_inner_radius_mm']+c['front_warm_mm']
    front_vac = front_warm+c['front_vacuum_mm']
    rear_bath = r1+c['rear_bath_mm']; rear_cold = rear_bath+c['rear_cold_mm']
    rear_vac = rear_cold+c['rear_vacuum_mm']; outer = rear_vac+c['rear_warm_mm']
    warm_inner_half = c['warm_half_z_mm']-c['end_warm_mm']
    cold_outer_half = warm_inner_half-c['end_vacuum_mm']
    tube('front_warm', 'warm_wall', 'Aluminium', c['warm_inner_radius_mm'], front_warm, c['warm_half_z_mm'])
    tube('rear_warm', 'warm_wall', 'Aluminium', rear_vac, outer, c['warm_half_z_mm'])
    tube('front_vacuum', 'vacuum', 'Vacuum', front_warm, front_vac, cold_outer_half)
    tube('rear_vacuum', 'vacuum', 'Vacuum', rear_cold, rear_vac, cold_outer_half)
    tube('front_cold', 'cold_wall', 'Aluminium', front_vac, r0-c['front_bath_mm'], cold_inner_half)
    tube('rear_cold', 'cold_wall', 'Aluminium', rear_bath, rear_cold, cold_inner_half)
    tube('front_bath', 'bath', 'LAr', r0-c['front_bath_mm'], r0, hz)
    tube('rear_bath', 'bath', 'LAr', r1, rear_bath, hz)
    for side in (-1, 1):
        if c.get('end_bath_mm', 0):
            tube(f'end_bath_{side}', 'bath', 'LAr', r0-c['front_bath_mm'], rear_bath, c['end_bath_mm']/2, side*(hz+c['end_bath_mm']/2))
        tube(f'end_warm_{side}', 'warm_wall', 'Aluminium', front_warm, rear_vac, c['end_warm_mm']/2, side*(c['warm_half_z_mm']-c['end_warm_mm']/2))
        tube(f'end_vacuum_{side}', 'vacuum', 'Vacuum', front_warm, rear_vac, c['end_vacuum_mm']/2, side*(warm_inner_half-c['end_vacuum_mm']/2))
        tube(f'end_cold_{side}', 'cold_wall', 'Aluminium', front_vac, rear_cold, c['end_cold_mm']/2, side*(cold_outer_half-c['end_cold_mm']/2))
    replicas = [dict(plane=i, center_mm=[0, 0, 0], frame=rotation(i*period)) for i in range(c['planes'])]
    ro = dict(name='LArBarrelHits', system_id=c.get('system_id', 10), descriptor=ID_DESCRIPTOR, planes=c['planes'], phi_merge=c['phi_merge'], theta_fine_pitch_rad=c['theta_fine_pitch_rad'], theta_merging=c['theta_merging'], theta_offset_rad=c.get('theta_offset_rad', .5902785), half_z_mm=hz, radii_mm=radii, canonical_gap=0, semantics='Raw IDs distinguish plane/layer/gap. Logical cells canonicalize neighbouring electrode pairs and both active gaps. Position is local to canonical even-plane gap0; volumeID returns that raw volume.', layers=[])
    channels = 0
    for layer in range(11):
        minimum = math.atan2(radii[layer], hz)
        first = theta_index(math.nextafter(minimum, math.inf), layer, ro)
        last = theta_index(math.nextafter(math.pi-minimum, -math.inf), layer, ro)
        merge = ro['theta_merging'][layer]
        indices = list(range(first, last+1, merge))
        gap = next(p for p in pieces if p.get('gap') == 0 and p['layer'] == layer)
        references = [dict(theta_index=i, position_mm=canonical_reference(gap, i, ro)) for i in indices]
        count = len(indices)*(c['planes']//c['phi_merge'])
        channels += count
        ro['layers'].append(dict(layer=layer, theta_min_rad=minimum, theta_max_rad=math.pi-minimum, indices=indices, reference_points=references, channels=count))
    totals = defaultdict(lambda: dict(volume_mm3=0., mass_g=0.))
    for part, multiplicity in [(x, c['planes']) for x in pieces]+[(x, 1) for x in passive]:
        for key in ('volume_mm3', 'mass_g'):
            totals[part['material']][key] += multiplicity*part[key]
    sampling_volume = sum(p['volume_mm3'] for p in pieces)*c['planes']
    annulus_volume = math.pi*(r1*r1-r0*r0)*2*hz
    residual = sampling_volume/annulus_volume-1
    if abs(residual) > 2e-8:
        raise ValueError('Inclined period does not tessellate sampling annulus: '+str(residual))
    report = dict(status='DRAFT / PROTOTYPE', config=c, materials=m.recipes, pieces=pieces, replicas=replicas, passive=passive, readout=ro, logical_channels=channels, physical_sensitive_elements=2*11*c['planes'], physical_material_parts=len(pieces)*c['planes']+len(passive), material_totals=dict(totals), mass_g=sum(v['mass_g'] for v in totals.values()), sampling=dict(path_length_mm=path, tabulated_sum_mm=sum(c['segments_mm']), final_segment_remainder_mm=remainder, closed_segments_mm=lengths, radii_mm=radii, half_z_mm=hz, filled_volume_mm3=sampling_volume, annular_volume_mm3=annulus_volume, fill_relative_residual=residual), envelopes=dict(inner_radius_mm=c['warm_inner_radius_mm'], outer_radius_mm=outer, warm_half_z_mm=c['warm_half_z_mm'], cold_inner_half_z_mm=cold_inner_half, active_half_z_mm=hz), source_sha256={str(p.relative_to(ROOT)):sha(p) for p in (Path(__file__), ROOT/'tools/lar_calorimeter/barrel.json', ROOT/'tools/pixel_barrel_dd4hep/materials.py', ROOT/'detector/config/elements.json')})
    return report, m
