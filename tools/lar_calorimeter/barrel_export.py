"""Export the isolated DES032 barrel; never wired into production CMake."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from collections import defaultdict
from barrel_geometry import ROOT, build, sha


def write(path, node):
    ET.indent(node, space='  ')
    ET.ElementTree(node).write(path, encoding='utf-8', xml_declaration=True)


def pose(node, piece):
    for key, value in zip(('x', 'y', 'z'), piece['center_mm']):
        node.set(key, f'{value:.17g}*mm')
    for i in range(3):
        for j in range(3):
            node.set(f'a{i}{j}', format(piece['frame'][j][i], '.17g'))


def shape(node, piece):
    node.set('kind', piece['shape_kind'])
    for key, value in piece.get('dimensions_mm', {}).items():
        node.set(key, f'{value:.17g}*mm')
    if piece['shape_kind'] == 'xtru':
        node.set('depth', f"{piece['depth_mm']:.17g}*mm")
        for x, y in piece['vertices_mm']:
            ET.SubElement(node, 'vertex', x=f'{x:.17g}*mm', y=f'{y:.17g}*mm')
    if 'clip_annulus_mm' in piece:
        a = piece['clip_annulus_mm']
        ET.SubElement(node, 'annulus', rmin=f"{a['rmin']:.17g}*mm", rmax=f"{a['rmax']:.17g}*mm", length=f"{piece['depth_mm']:.17g}*mm")
    for cut in piece.get('cuts', []):
        element = ET.SubElement(node, 'cut')
        shape(element, cut)
        pose(element, cut)


def append_piece(parent, piece):
    element = ET.SubElement(parent, 'piece', name=piece['name'], role=piece['role'], material=piece['material'])
    if 'parent_name' in piece:
        element.set('parent_name', piece['parent_name'])
    shape(element, piece)
    pose(element, piece)
    if piece['role'] == 'sensitive':
        element.set('layer', str(piece['layer']))
        element.set('gap', str(piece['gap']))
    return element


def totals(report):
    parents = {p['name']:p for p in report['passive']}
    if len(parents) != len(report['passive']):
        raise ValueError('Duplicate passive name')
    daughters = defaultdict(float)
    for piece in report['passive']:
        parent = piece.get('parent_name')
        seen = {piece['name']}
        while parent:
            if parent not in parents or parent in seen:
                raise ValueError('Unknown parent or cyclic passive hierarchy')
            seen.add(parent)
            parent = parents[parent].get('parent_name')
        if 'parent_name' in piece:
            daughters[piece['parent_name']] += piece['volume_mm3']
    for name, displaced in daughters.items():
        piece = parents[name]
        exclusive = piece.get('exclusive_volume_mm3', piece['volume_mm3'])
        if abs(piece['volume_mm3']-exclusive-displaced) > max(1e-5, piece['volume_mm3']*1e-10):
            raise ValueError('Mother daughter displacement does not conserve exclusive volume: '+name)
        if 'displaced_volume_mm3' in piece and abs(piece['displaced_volume_mm3']-displaced) > max(1e-5, displaced*1e-10):
            raise ValueError('Declared bath displacement differs from daughters')
    result = defaultdict(lambda: dict(volume_mm3=0., mass_g=0.))
    for part, count in [(x, len(report['replicas'])) for x in report['pieces']]+[(x, 1) for x in report['passive']]:
        if part['volume_mm3'] <= 0 or part['mass_g'] <= 0:
            raise ValueError('Nonpositive exclusive volume or mass')
        exclusive = part.get('exclusive_volume_mm3', part['volume_mm3'])
        if not 0 < exclusive <= part['volume_mm3']*(1+1e-12):
            raise ValueError('Invalid exclusive mother volume')
        density = report['materials'][part['material']]['density_g_cm3']
        part['mass_g'] = exclusive*density/1000
        result[part['material']]['volume_mm3'] += count*exclusive
        result[part['material']]['mass_g'] += count*part['mass_g']
    report['material_totals'] = dict(result)
    report['mass_g'] = sum(x['mass_g'] for x in result.values())
    report['physical_material_parts'] = len(report['pieces'])*len(report['replicas'])+len(report['passive'])


def compact(report, output):
    doc = ET.Element('lccdd')
    ET.SubElement(doc, 'info', name='LAYOUT002LArBarrelPrototype', title='DES032 isolated inclined LAr barrel', author='nODD', version='0.1', status='prototype')
    ET.SubElement(ET.SubElement(doc, 'includes'), 'gdmlFile', ref='materials.xml')
    define = ET.SubElement(doc, 'define')
    extent = max(report['envelopes']['outer_radius_mm']+1000, 6000)
    for key, value in dict(world_x=extent, world_y=extent, world_z=report['envelopes']['warm_half_z_mm']+2000).items():
        ET.SubElement(define, 'constant', name=key, value=f'{value:.17g}*mm')
    ro = report['readout']
    readout = ET.SubElement(ET.SubElement(doc, 'readouts'), 'readout', name=ro['name'])
    table = [v for layer in ro['layers'] for p in layer['reference_points'] for v in [layer['layer'], p['theta_index'], *p['position_mm']]]
    ET.SubElement(readout, 'segmentation', type='nODDLArBarrelMerged', theta_fine_pitch_rad=format(ro['theta_fine_pitch_rad'], '.17g'), theta_offset_rad=format(ro['theta_offset_rad'], '.17g'), theta_merging=' '.join(map(str, ro['theta_merging'])), planes=str(ro['planes']), phi_merge=str(ro['phi_merge']), reference_table_mm=' '.join(format(x, '.17g') for x in table))
    ET.SubElement(readout, 'id').text = ro['descriptor']
    detector = ET.SubElement(ET.SubElement(doc, 'detectors'), 'detector', name='LArBarrel', id=str(ro['system_id']), type='nODDLArBarrelPrototype', readout=ro['name'])
    ET.SubElement(detector, 'sensitive', type='calorimeter')
    period = ET.SubElement(detector, 'period', name='LArInclinedPeriod')
    for piece in report['pieces']:
        append_piece(period, piece)
    for replica in report['replicas']:
        element = ET.SubElement(detector, 'replica', plane=str(replica['plane']))
        pose(element, replica)
    for piece in report['passive']:
        append_piece(detector, piece)
    write(output/'barrel.xml', doc)


def export(output, services=None):
    output.mkdir(parents=True, exist_ok=True)
    report, m = build()
    if services:
        specification = importlib.util.spec_from_file_location('lar_barrel_services', services)
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
        result = module.augment(report, m)
        if result is not None:
            report = result
        report['source_sha256'][str(services.resolve().relative_to(ROOT))] = sha(services)
    report['materials'] = m.recipes
    totals(report)
    write(output/'materials.xml', m.root)
    compact(report, output)
    report['source_sha256'].update({str(p.relative_to(ROOT)):sha(p) for p in (Path(__file__), ROOT/'prototypes/calorimeter/LArBarrel.cpp')})
    report['execution'] = dict(commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), dirty=bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True)))
    report['artifact_sha256'] = {p.name:sha(p) for p in (output/'barrel.xml', output/'materials.xml')}
    (output/'expected.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Exported', report['physical_sensitive_elements'], 'raw sensitive volumes;', report['logical_channels'], 'merged logical cells;', report['mass_g']/1e6, 't')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--services', type=Path, help='Optional project-owned module with augment(report,materials)')
    args = parser.parse_args()
    export(args.output, args.services)
