#!/usr/bin/env python3
"""DES043 isolated explicit endcap module/cold-petal compact, all lengths mm.

The unchanged DES021 generic factory constructs these new XML solids. Default
is the first mirrored pair (792 sensors); --full includes all twelve discs.
No shared trunk, collector or full-tracker integration is instantiated here.
"""
import argparse
from collections import Counter
import importlib.util
import json
import math
from pathlib import Path
import sys
import subprocess
import xml.etree.ElementTree as ET

from model import ROOT, HERE, load, geometry, sha
from diagnostics import cooling_pieces, sample_piece, coverage

INPUT_REVISION = "c8bd0096264beea529696affb88cf31c907fffd4"
WINDOW_CLEARANCE_MM = .05


def module_xy(radius, theta, u=0., v=0.):
    return [radius * math.cos(theta) - u * math.sin(theta) - v * math.cos(theta),
            radius * math.sin(theta) + u * math.cos(theta) - v * math.sin(theta)]


def module_phi(module):
    if 'phi_rad' in module: return module['phi_rad']
    return math.atan2(module['side'] * module['center_mm'][1], module['center_mm'][0]) % (2 * math.pi)


def lands(c):
    offset = c['thermal']['endcap_pad_u_mm']
    return [0.] if offset == 0 else [-offset, offset]


def transformed(point, side, z, phi):
    x, y, w = point
    return [x * math.cos(phi) - y * math.sin(phi),
            side * (x * math.sin(phi) + y * math.cos(phi)), side * (z + w)]


def plumbing(c):
    result = []
    for loop, rings, ports in (("inner", c['ring_centres_mm'][:3], c['cooling_ports_deg'][:2]),
                               ("outer", c['ring_centres_mm'][3:], c['cooling_ports_deg'][2:])):
        for source in cooling_pieces(rings, ports, c['cooling_port_radius_mm'],
                bend=c['cooling_hairpin_radius_mm'], angles=c['cooling_leg_angles_deg'], stadium=True):
            p = dict(source, label=loop + '_' + source['label'], loop=loop)
            if p['kind'] == 'arc':
                p.update(native_kind='torus', center3=[*p['center'], -4.05], rotation=[0., 0., 0.],
                         dimensions=dict(major=p['radius'], start=p['start'], angle=p['angle']))
            else:
                angle = math.atan2(p['b'][1] - p['a'][1], p['b'][0] - p['a'][0])
                p.update(native_kind='tube', center3=[(a + b) / 2 for a, b in zip(p['a'], p['b'])] + [-4.05],
                         rotation=[0., math.pi / 2, angle], dimensions=dict(length=math.dist(p['a'], p['b'])))
            result.append(p)
    return result


def contact_screen(c, modules, pipes):
    """Conservative .5 mm centreline samples: missing contact is explicit."""
    samples = [xy for p in pipes for xy in sample_piece(p)]
    rows = []
    for m in modules:
        if m['layer'] != 0 or m['petal'] != 0:
            continue
        r, theta = m['radius_mm'], module_phi(m)
        distances = []
        for offset in lands(c):
            centre = module_xy(r, theta, offset)
            best = math.inf
            for x, y in samples:
                dx, dy = x - centre[0], y - centre[1]
                u = -math.sin(theta) * dx + math.cos(theta) * dy
                v = -math.cos(theta) * dx - math.sin(theta) * dy
                best = min(best, math.hypot(max(0., abs(u) - c['thermal']['endcap_pad_mm'][0] / 2),
                                          max(0., abs(v) - c['thermal']['endcap_pad_mm'][1] / 2)))
            distances.append(best)
        rows.append(dict(ring=m['ring'], phi_deg=math.degrees(theta),
            sampled_pipe_to_land_distance_mm=distances,
            definite_missing_contacts=sum(d - .25 > c['leaf_pipe_OD_mm'] / 2 for d in distances)))
    return dict(sample_step_mm=.5, sampling_distance_error_bound_mm=.25, rows=rows,
        definite_missing_contacts=sum(r['definite_missing_contacts'] for r in rows),
        scope='Planar footprint screen only. Reaching pipe-centre w is not proof of thermal contact; no thermal qualification.')


def guard_clearance(c, modules):
    """Exact finite rectangle distance to other modules' guards at overlapping w."""
    modules = [m for m in modules if m['layer'] == 0]
    def polygon(m, u, v, width, length):
        angle = module_phi(m)
        return [module_xy(m['radius_mm'], angle, u + su * width / 2, v + sv * length / 2)
                for su, sv in ((-1,-1), (1,-1), (1,1), (-1,1))]
    def distance(first, second):
        separated = False
        for polygon in (first, second):
            for p, q in zip(polygon, polygon[1:] + polygon[:1]):
                axis = [p[1]-q[1], q[0]-p[0]]
                a = [sum(x*y for x,y in zip(point,axis)) for point in first]
                b = [sum(x*y for x,y in zip(point,axis)) for point in second]
                if max(a) < min(b) or max(b) < min(a): separated = True
        if not separated: return 0.
        best = math.inf
        for own, other in ((first, second), (second, first)):
            for p in own:
                for a, b in zip(other, other[1:] + other[:1]):
                    d = [b[i]-a[i] for i in (0,1)]
                    t = max(0.,min(1.,sum((p[i]-a[i])*d[i] for i in (0,1))/sum(x*x for x in d)))
                    best = min(best,math.hypot(*(p[i]-a[i]-t*d[i] for i in (0,1))))
        return best
    minimum = math.inf; overlaps = 0; pairs = 0
    for m in modules:
        top = m['lift_mm'] - .825
        for other in modules:
            if other is m or other['lift_mm'] - .1 >= top: continue
            if math.dist(m['center_mm'][:2],other['center_mm'][:2]) > 100: continue
            for offset in lands(c):
                land = polygon(m,offset,0,*c['thermal']['endcap_pad_mm'])
                for u,v,w,h in ((-24.25,0,.5,97),(24.25,0,.5,97),(0,-48.25,48,.5),(0,48.25,48,.5)):
                    value = distance(land,polygon(other,u,v,w,h)); pairs += 1
                    minimum = min(minimum,value); overlaps += value == 0
    return dict(minimum_other_guard_clearance_mm=minimum, intersecting_rectangle_pairs=overlaps, checked_pairs=pairs,
        scope='Exact finite planar rectangle clearance when the pickup and other guard axial intervals overlap; representative complete disc including petal seams. Native ROOT independently checks every solid.')


def build(c, full=False):
    bc, ec, lc, bl, old, ll, selected = geometry(c)
    required = dict(sensor_mm=[48., 96., .2], body_mm=[49., 103.], insert_bottom_w_mm=-4.05,
                    pipe_centre_w_mm=-4.05, pipe_OD_mm=2.5)
    for key, value in required.items():
        if c['native_module'][key] != value:
            raise ValueError('Native module interface requires new review: ' + key)
    if c['ring_centres_mm'] != [289.5, 381.25, 473., 564.75, 656.5] or c['target_annulus_mm'] != [243.5, 703.]:
        raise ValueError('Require the authorized full-phi 703 mm input, not the earlier sketch')
    spec = importlib.util.spec_from_file_location('_des043_materials', ROOT / 'tools/pixel_barrel_dd4hep/materials.py')
    materials = importlib.util.module_from_spec(spec); spec.loader.exec_module(materials)
    mat = materials.Materials(dict(coolant_density_g_cm3=1., cfrp_carbon_mass_fraction=.7,
        module=dict(flex_copper_coverage=.5)), dict(density_g_cm3=dict(titanium=4.51, graphite=2.21,
        insulation=1.42, glue=2., CFRP=1.73, foam=.20)))
    mat.add('CarbonFoam', .20, {'C': 1.})
    mat.effective('BumpFixture', {'Copper': .15}, 1.)
    mat.effective('SignalFlex', {'Copper': .085, 'Polyimide': .915}, 1.)
    mat.effective('ElectronicsFixture', {'Silicon': .04, 'Copper': .01, 'Polyimide': .10}, 1.)
    mat.add('InsulatingTIM', c['material']['TIM_density_upper_g_cm3'], {'Epoxy': 1.})
    doc = ET.Element('lccdd')
    ET.SubElement(doc, 'info', name='ShortStripRedesign', title='DES043 explicit module and cold petal PROTOTYPE', author='nODD', version='0.1', status='prototype')
    ET.SubElement(ET.SubElement(doc, 'includes'), 'gdmlFile', ref='materials.xml')
    defs = ET.SubElement(doc, 'define')
    for axis, value in zip('xyz', (1000, 1000, 3700)):
        ET.SubElement(defs, 'constant', name='world_' + axis, value=f'{value}*mm')
    for key, value in [('rmax', 800), ('zmax', 3300)]:
        ET.SubElement(defs, 'constant', name='tracker_region_' + key, value=f'{value}*mm')
    readout = ET.SubElement(ET.SubElement(doc, 'readouts'), 'readout', name='ShortStripRedesignHits')
    ET.SubElement(readout, 'segmentation', type='CartesianGridXY', grid_size_x='.075*mm', grid_size_y='2*mm', offset_x='.0375*mm', offset_y='1*mm')
    ET.SubElement(readout, 'id').text = 'system:5,layer:4,petal:4,ring:3,module:4,sensor:1,x:-11,y:-10'
    detector = ET.SubElement(ET.SubElement(doc, 'detectors'), 'detector', name='ShortStripRedesign', id='4', type='nODDShortStripEndcap', readout='ShortStripRedesignHits')
    ET.SubElement(detector, 'sensitive', type='tracker')
    entities, probes = [], []
    pipes = plumbing(c)
    sampled_pipes = [(p, sample_piece(p)) for p in pipes]
    witness_cache = {}
    cutting_cache = {}

    def nearby_pipes(radius, theta, offset):
        key = (radius, round(theta, 10), offset)
        if key not in cutting_cache:
            centre = module_xy(radius, theta, offset); nearby = []
            for segment, samples in sampled_pipes:
                for x, y in samples:
                    dx, dy = x - centre[0], y - centre[1]
                    u = -math.sin(theta) * dx + math.cos(theta) * dy
                    v = -math.cos(theta) * dx - math.sin(theta) * dy
                    distance = math.hypot(max(0., abs(u) - c['thermal']['endcap_pad_mm'][0] / 2),
                                          max(0., abs(v) - c['thermal']['endcap_pad_mm'][1] / 2))
                    # <=.5 mm arc-length samples have <=.25 mm nearest-point
                    # error. Excluding larger distances cannot remove a cut
                    # which intersects this finite rectangular land.
                    if distance <= 1.500001: nearby.append(segment); break
            cutting_cache[key] = nearby
        return cutting_cache[key]

    def contact_witness(radius, theta, offset):
        key = (radius, round(theta, 10), offset)
        if key not in witness_cache:
            centre = module_xy(radius, theta, offset)
            found = None
            for segment, samples in sampled_pipes:
                for x, y in samples[2:-2]:
                    dx, dy = x - centre[0], y - centre[1]
                    u = -math.sin(theta) * dx + math.cos(theta) * dy
                    v = -math.cos(theta) * dx - math.sin(theta) * dy
                    if abs(u) < c['thermal']['endcap_pad_mm'][0] / 2 - .02 and abs(v) < c['thermal']['endcap_pad_mm'][1] / 2 - .02:
                        found = (segment, [x, y], [u, v]); break
                if found: break
            if found is None: raise ValueError('No finite pipe-centreline contact inside the specified land')
            witness_cache[key] = found
        return witness_cache[key]

    def attributes(centre, dims, rotation=(0., 0., 0.)):
        a = {k: format(float(v), '.17g') + '*mm' for k, v in zip(('u', 'v', 'w'), centre)}
        a.update({k: format(float(v), '.17g') + ('*rad' if k in ('start', 'angle') else '*mm') for k, v in dims.items()})
        a.update({k: format(float(v), '.17g') + '*rad' for k, v in zip(('rx', 'ry', 'rz'), rotation)})
        return a

    def piece(parent, name, role, material, kind, centre, dims, transform=lambda p: p, rotation=(0., 0., 0.)):
        node = ET.SubElement(parent, 'piece', name=name, kind=kind, material=material, **attributes(centre, dims, rotation))
        entity = dict(name=name, role=role, center_mm=transform(centre), kind=kind, dimensions_mm=dims,
                      material=material, cuts=0)
        entities.append(entity)
        return node, entity

    def cut(node, entity, kind, centre, dims, rotation=(0., 0., 0.)):
        ET.SubElement(node, 'cut', kind=kind, **attributes(centre, dims, rotation)); entity['cuts'] += 1

    discs = selected['discs'] if full else [d for d in selected['discs'] if d['station'] == 0]
    for disc in discs:
        layer, side, z = disc['layer'], disc['side'], abs(disc['z_mm'])
        dn = f'D{layer}'
        disk = ET.SubElement(detector, 'disc', name=dn, id=str(layer), z=f'{z}*mm', side=str(side))
        for index, (rin, rout) in enumerate(([236., 250.], c['outer_frame_mm'])):
            piece(disk, dn + f'_frame{index}', 'frame', 'CFRP', 'sector', [0, 0, -12],
                  dict(rmin=rin, rmax=rout, length=3., start=0., angle=2 * math.pi),
                  lambda p, s=side, zz=z: transformed(p, s, zz, 0.))
        for petal in range(12):
            phi = petal * math.pi / 6; pn = dn + f'_P{petal}'
            p = ET.SubElement(disk, 'petal', name=pn, id=str(petal), phi=f'{phi}*rad')
            transform = lambda q, s=side, zz=z, ph=phi: transformed(q, s, zz, ph)
            def box(label, role, material, centre, size, rotation=0.):
                return piece(p, pn + '_' + label, role, material, 'box', centre,
                             dict(zip(('sx', 'sy', 'sz'), size)), transform, (0., 0., rotation))
            def polar(radius, angle, w):
                return [radius * math.cos(angle), radius * math.sin(angle), w]
            start = ec['petal_gap_mm'] / 236 / 2
            sector = dict(rmin=236., rmax=c['petal_outer_plate_mm'], start=start, angle=math.pi / 6 - 2 * start)
            supports = []
            for label, low, high, material in [('front_skin', -1.45, -1.3, 'CFRP'),
                    ('front_glue', -1.55, -1.45, 'Epoxy'), ('core', -6.55, -1.55, 'CarbonFoam'),
                    ('back_glue', -6.65, -6.55, 'Epoxy'), ('back_skin', -6.8, -6.65, 'CFRP')]:
                node, entity = piece(p, pn + '_' + label, 'core' if label == 'core' else 'support', material,
                    'sector', [0, 0, (low + high) / 2], dict(sector, length=high - low), transform)
                if label in ('front_skin', 'front_glue', 'core'):
                    supports.append((node, entity, (low + high) / 2, low, high))
                    probes.append(dict(name=entity['name'], point_mm=[709.5*math.cos(math.pi/12),709.5*math.sin(math.pi/12),0.],
                        inside=True, reason='Cold support retained outside all module windows'))
                if label == 'core':
                    for segment in pipes:
                        cut(node, entity, segment['native_kind'], [segment['center3'][0], segment['center3'][1], 0.],
                            dict(segment['dimensions'], rmin=0., rmax=1.25), segment['rotation'])
            for segment in pipes:
                for role, material, rmin, rmax in [('cooling_tube', 'Titanium', 1.11, 1.25), ('coolant', 'CO2', 0., 1.11)]:
                    piece(p, pn + '_' + segment['label'] + '_' + role, role, material, segment['native_kind'],
                        segment['center3'], dict(segment['dimensions'], rmin=rmin, rmax=rmax), transform, segment['rotation'])
            members = [m for m in selected['modules'] if m['layer'] == layer and m['petal'] == petal]
            counters = Counter(); flex_volume = 0.
            for m in members:
                ring = m['ring']; module = counters[ring]; counters[ring] += 1
                theta = module_phi(m) - phi; r, lift = m['radius_mm'], m['lift_mm']; mn = pn + f'_R{ring}_M{module}'
                mod = ET.SubElement(p, 'module', name=mn, id=str(module), ring=str(ring), radius=f'{r}*mm', phi=f'{theta}*rad', lift=f'{lift}*mm')
                def local_transform(q):
                    return transform([*module_xy(r, theta, q[0], q[1]), q[2] + lift])
                def module_box(label, role, material, centre, size):
                    return piece(mod, mn + '_' + label, role, material, 'box', centre,
                                 dict(zip(('sx', 'sy', 'sz'), size)), local_transform)
                node, e = module_box('active', 'sensitive', 'Silicon', [0, 0, 0], [48, 96, .2])
                node.set('sensitive', 'true'); e.update(ids=dict(system=4, layer=layer, petal=petal, ring=ring, module=module, sensor=0),
                    size_mm=[48, 96, .2], u=m['u'], v=m['v'], normal=m['n'])
                for sign in (-1, 1):
                    module_box('guardU' + str(sign), 'guard', 'Silicon', [sign * 24.25, 0, 0], [.5, 97, .2])
                    module_box('guardV' + str(sign), 'guard', 'Silicon', [0, sign * 48.25, 0], [48, .5, .2])
                    module_box('flex' + str(sign), 'module_flex', 'SignalFlex', [0, sign * 50, -.5], [49, 3, .1])
                for label, role, material, width in [('bumps', 'interconnect', 'BumpFixture', [48, 96]),
                        ('redistribution', 'redistribution', 'SignalFlex', [48, 96]),
                        ('spreader', 'spreader', 'Graphite', [48, 96]), ('TIM', 'TIM', 'InsulatingTIM', [48, 96]),
                        ('backing', 'backing', 'CFRP', [48, 96])]:
                    low, high = c['native_module'][label + '_w_mm']
                    n, ent = module_box(label, role, material, [0, 0, (low + high) / 2], [*width, high - low])
                    if label == 'backing':
                        probes.append(dict(name=ent['name'], point_mm=[20.,40.,0.], inside=True, reason='Finite backing retained outside window'))
                        for offset in lands(c):
                            cut(n, ent, 'box', [offset, 0, 0], dict(sx=c['thermal']['endcap_pad_mm'][0] + .1,
                                sy=c['thermal']['endcap_pad_mm'][1] + .1, sz=.4))
                            probes.append(dict(name=ent['name'], point_mm=[offset, 0, 0], inside=False, reason='Backing window'))
                for index, (u, v) in enumerate(c['thermal']['ASIC_centres_uv_mm']):
                    for label, role, material, interval in [('ASIC', 'readout', 'Silicon', 'ASIC_w_mm'),
                                                           ('ASIC_glue', 'ASIC_glue', 'Epoxy', 'ASIC_glue_w_mm')]:
                        low, high = c['native_module'][interval]
                        module_box(label + str(index), role, material, [u, v, (low + high) / 2], [23.4, 23.4, high - low])
                for land_index, offset in enumerate(lands(c)):
                    xy = module_xy(r, theta, offset)
                    bottom, top = -4.05, lift - .825
                    height = top - bottom
                    if height > c['thermal']['maximum_pickup_height_mm']:
                        raise ValueError('Native pickup exceeds the thermal path requirement')
                    n, ent = module_box('pickup' + str(land_index), 'thermal_pickup', 'Graphite',
                        [offset, 0, (bottom + top) / 2 - lift], [*c['thermal']['endcap_pad_mm'], height])
                    ent['height_mm'] = height
                    for segment in nearby_pipes(r, theta, offset):
                        cx, cy, cw = segment['center3']; dx, dy = cx - xy[0], cy - xy[1]
                        centre = [-math.sin(theta) * dx + math.cos(theta) * dy,
                                  -math.cos(theta) * dx - math.sin(theta) * dy, cw - (bottom + top) / 2]
                        rotation = list(segment['rotation']); rotation[2] -= theta + math.pi / 2
                        cut(n, ent, segment['native_kind'], centre,
                            dict(segment['dimensions'], rmin=0., rmax=1.25), rotation)
                    # Actual native CSG probes bracket the common tube/graphite
                    # surface by .01 mm, at a centreline inside the finite land.
                    segment, qxy, quv = contact_witness(r, theta, offset)
                    for distance, graphite_inside in ((1.24, False), (1.26, True)):
                        probes.append(dict(name=ent['name'], point_mm=[*quv, -4.05 + distance - (bottom + top) / 2],
                            inside=graphite_inside, reason='Finite pipe saddle contact'))
                        dx, dy = qxy[0] - segment['center3'][0], qxy[1] - segment['center3'][1]
                        if segment['native_kind'] == 'torus': point = [dx, dy, distance]
                        else:
                            a = segment['rotation'][2]
                            point = [-distance, -math.sin(a) * dx + math.cos(a) * dy, math.cos(a) * dx + math.sin(a) * dy]
                        probes.append(dict(name=pn + '_' + segment['label'] + '_cooling_tube', point_mm=point,
                            inside=not graphite_inside, reason='Finite titanium contact surface'))
                    for support, se, w, low, high in supports:
                        window_low = max(bottom - WINDOW_CLEARANCE_MM, low - .1)
                        window_high = high + .1
                        cut(support, se, 'box', [*xy, (window_low + window_high) / 2 - w],
                            dict(sx=c['thermal']['endcap_pad_mm'][0] + .1, sy=c['thermal']['endcap_pad_mm'][1] + .1,
                                 sz=window_high - window_low), (0., 0., theta + math.pi / 2))
                        probes.append(dict(name=se['name'], point_mm=[*xy, max(bottom + .1, low + .01) - w], inside=False, reason='Direct insert cold window'))
                flex_volume += .6 * (max(0., 705 - (r + 50)) + abs(theta - math.pi / 12) * (r + 50))
            # Three 4 mm/polarity islands retain the specified total copper width.
            bus_phi = math.pi / 12; length = c['endcap_bus_entry_mm'] - 250.; middle = (250 + c['endcap_bus_entry_mm']) / 2
            for island, u in enumerate((-10., 0., 10.)):
                def buspoint(radius, offset, w):
                    return module_xy(radius, bus_phi, offset, 0) + [w]
                box(f'railPI{island}', 'rail_insulation', 'Polyimide', buspoint(middle, u, -6.875), [8.5, length, .15], bus_phi + math.pi / 2)
                for sign in (-1, 1):
                    box(f'rail{island}_{sign}', 'power_bus', 'Copper', buspoint(middle, u + sign * 2.25, -6.95 - .17 / 2), [4, length, .17], bus_phi + math.pi / 2)
                box(f'protection{island}', 'protection_allocation', 'ElectronicsFixture', buspoint(702, u, -7.62), [4, 6, 1.], bus_phi + math.pi / 2)
            box('signal_HV', 'signal_bus', 'SignalFlex', polar(middle, math.radians(22), -6.85), [8, length, .1], math.radians(22) + math.pi / 2)
            capacity = sector['angle'] / 2 * (710 ** 2 - 236 ** 2) * .5
            recipe = {'Copper': flex_volume * .085, 'Polyimide': flex_volume * .915}
            mix = mat.effective(pn + '_fanout_material', recipe, capacity)
            _, ent = piece(p, pn + '_fanout', 'local_fanout', mix, 'sector', [0, 0, 9.25], dict(sector, length=.5), transform)
            ent['constituent_volumes_mm3'] = recipe
            for index, (radius, angle_deg) in enumerate(((243., 10.), (705., 10.), (705., 26.))):
                angle = math.radians(angle_deg)
                box('plate_lug' + str(index), 'plate_mount', 'CFRP', polar(radius, angle, -8.65),
                    [8., 6., 3.7], angle + math.pi / 2)
            box('board', 'end_board', 'ElectronicsFixture', polar(c['board_radius_mm'], bus_phi, c['board_z_offset_mm']), [52, 20, 8], bus_phi + math.pi / 2)
            for sign in (-1, 1):
                # Peripheral stems clear plate710 and body708.424; arms touch
                # fanout top9.5 and board bottom10 without overlapping either.
                xy = module_xy(712.5, bus_phi, sign * 15)
                box('stem' + str(sign), 'board_mount', 'CFRP', [*xy, -.25], [4, 4, 20.5], bus_phi + math.pi / 2)
                xy = module_xy(707.25, bus_phi, sign * 15)
                box('cantilever' + str(sign), 'board_mount', 'CFRP', [*xy, 9.75], [4, 14.5, .5], bus_phi + math.pi / 2)
    expected = dict(status='PROTOTYPE', initial_contract_revision=INPUT_REVISION, full=full,
        disc_layers=[d['layer'] for d in discs], counts=dict(Counter(e['role'] for e in entities)), entities=entities,
        probes=probes, cell_mm=c['pitch_mm'], materials=mat.recipes,
        source_coverage=coverage(c, selected), thermal_contact_screen=contact_screen(c, selected['modules'], pipes),
        guard_clearance=guard_clearance(c, selected['modules']),
        module_stack=c['native_module'], actual_core_penetration_mm=2.5, reserved_extra_core_mm=c['thermal']['extra_core_insert_mm'],
        shared_services_instantiated=False,
        limitations=['No production integration, ACTS/Geant4 transport, engineering qualification or whole-tracker material claim.',
            'Intersecting/outside CSG cuts are intentional; no exact composite capacity or mass is obtained by subtracting full cut capacities.',
            'TIM is an epoxy density proxy; interposer/signal/protection/board materials are explicit effective allocations, not qualified hardware.',
            'Only endcap module/petal/local services are constructed. Barrel20x64 lands remain an unchanged source-model interface.',
            'Thermal-contact misses are blockers: pipe-plane reach alone does not establish a conductive pipe contact.'])
    return doc, mat.root, expected


def export(c, output, full=False):
    doc, materials, expected = build(c, full)
    output.mkdir(parents=True, exist_ok=True)
    for filename, node in [('short-strip-redesign.xml', doc), ('materials.xml', materials)]:
        ET.indent(node, space='  '); ET.ElementTree(node).write(output / filename, encoding='utf-8', xml_declaration=True)
    expected['provenance'] = {str(p.relative_to(ROOT)): sha(p) for p in [HERE / 'inputs.json', HERE / 'model.py',
        HERE / 'diagnostics.py', Path(__file__), ROOT / 'prototypes/short_strip_endcap/ShortStripEndcap.cpp',
        ROOT / 'tools/pixel_barrel_dd4hep/materials.py', HERE / 'validate_native.py',
        ROOT / 'prototypes/short_strip_redesign/CMakeLists.txt']}
    expected['generation_source_revision'] = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    expected['compact_sha256'] = sha(output / 'short-strip-redesign.xml')
    expected['generated_artifact_sha256'] = {name:sha(output/name) for name in ('short-strip-redesign.xml','materials.xml')}
    (output / 'expected.json').write_text(json.dumps(expected, separators=(',', ':'), allow_nan=False) + '\n')
    print(json.dumps(dict(counts=expected['counts'], missing_thermal_contacts=expected['thermal_contact_screen']['definite_missing_contacts'])))
    return expected


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'build/short-strip-redesign/native/compact')
    parser.add_argument('--full', action='store_true')
    args = parser.parse_args(); export(load(), args.output, args.full)
