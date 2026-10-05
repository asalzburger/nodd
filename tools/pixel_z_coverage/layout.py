"""DES-013 isolated barrel replacement. Existing compact defaults are untouched."""
import copy
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/module_layout'))
from geometry import _shape, _obb_overlap


def barrel(item):
    return item['subsystem'] == 'pixel' and item.get('region') == 'barrel'


def load(config):
    raw = (ROOT / config['baseline']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != config['baseline_sha256']:
        raise ValueError('Baseline fingerprint changed; review before regenerating')
    return json.loads(gzip.decompress(raw))


def shape(family, models, case):
    """Rotate (old u,old v) -> (-old v,old u), keeping a right-handed frame."""
    old = _shape(family, models)
    g = models['pixel']['guard_mm'] if case['mode'] == 'rotate' else case['guard_z_mm']
    if g <= 0 or (case['mode'] == 'packed' and case['gap_mm'] <= 0):
        raise ValueError('Positive sensor edge and mechanical clearance required')
    sensor_phi = old['sensor_v']
    sensor_z = old['width'] + 2*g
    # Approximate inherited die width is retained; it must fit the proposed sensor.
    nx = models['pixel']['families'][family][0]
    die_z = nx*models['pixel']['approximate_die_u_mm'] + (nx-1)*models['pixel']['interchip_gap_mm']
    return dict(active_phi=old['height'], active_z=old['width'],
                sensor_phi=sensor_phi, sensor_z=sensor_z,
                body_phi=old['body_v'], body_z=old['body_u'] if case['mode']=='rotate' else max(sensor_z, die_z),
                offset_phi=-old.get('body_v_offset', 0.),
                patches=[(-v,u,hv,hu) for u,v,hu,hv in old['patches']],
                guard_z=g)


def row_centres(low, high, spec, case):
    pitch = spec['body_z'] + case['gap_mm']
    if case['phase'] == 'symmetric':
        count = math.floor((high-low+case['gap_mm'])/pitch)
        return [(i-(count-1)/2)*pitch+(low+high)/2 for i in range(count)]
    if case['phase'] != 'chip':
        raise ValueError('Unknown row phase')
    # Put one actual chip centre at the origin, not the centre of a quad dead seam.
    offset = -spec['patches'][0][1]
    first = math.ceil((low+spec['body_z']/2-offset)/pitch)
    last = math.floor((high-spec['body_z']/2-offset)/pitch)
    return [i*pitch+offset for i in range(first,last+1)]


def build(baseline, case):
    if case['mode'] == 'baseline':
        return copy.deepcopy(baseline)
    if case['mode'] not in ('rotate','packed'):
        raise ValueError('Unknown construction mode')
    result = copy.deepcopy(baseline)
    result['bodies'] = [b for b in result['bodies'] if not barrel(b)]
    result['modules'] = [m for m in result['modules'] if not barrel(m)]
    mid = max(b['module_id'] for b in baseline['bodies'])
    pid = max(m['id'] for m in baseline['modules'])
    sid = max(m['sensor_id'] for m in baseline['modules'])
    models = baseline['metadata']['models']
    specs = {}
    old_patches = {}
    for p in baseline['modules']:
        if barrel(p):
            old_patches.setdefault(p['module_id'], []).append(p)
    for layer in baseline['layers']:
        original = [b for b in baseline['bodies'] if barrel(b) and b['layer_id'] == layer['id']]
        if not original:
            continue
        spec = shape(original[0]['family'], models, case)
        specs[layer['id']] = spec
        templates = {b['col']: b for b in reversed(original)}
        for col, template in sorted(templates.items()):
            old = sorted([b for b in original if b['col']==col], key=lambda b:b['center_mm'][2])
            # Existing body centre includes +0.9 mm peripheral offset for singles.
            if case['mode'] == 'rotate':
                centres = [sum(m['center_mm'][2] for m in old_patches[b['module_id']])/len(old_patches[b['module_id']]) for b in old]
            else:
                centres = row_centres(layer['z_min_m']*1000,layer['z_max_m']*1000,spec,case)
            sample = old_patches[template['module_id']][0]
            for row, z in enumerate(centres):
                mid += 1; sid += 1
                origin = [*template['center_mm'][:2], z]
                body = copy.deepcopy(template)
                body.update(module_id=mid,row=row,half_u_mm=spec['body_phi']/2,half_v_mm=spec['body_z']/2,
                            center_mm=[origin[d]+spec['offset_phi']*body['u'][d] for d in range(3)])
                result['bodies'].append(body)
                for k,(u,v,hu,hv) in enumerate(spec['patches']):
                    pid += 1
                    patch = copy.deepcopy(sample)
                    patch.update(id=pid,sensor_id=sid,module_id=mid,row=row,col=col,patch=k,
                                 half_u_mm=hu,half_v_mm=hv,active_area_mm2=4*hu*hv,
                                 sensor_area_mm2=spec['sensor_phi']*spec['sensor_z'],
                                 center_mm=[origin[d]+u*patch['u'][d]+v*patch['v'][d] for d in range(3)])
                    result['modules'].append(patch)
    result['status'] = 'DES-013 PROTOTYPE; pending approval; inherited service metadata is not a recalculation'
    result['metadata']['pixel_z_study'] = dict(case=case,shapes=specs)
    return result


def transverse_support_screen(layout, tolerance):
    """Project full repeated stave columns, even when a z cut happens to hit a seam."""
    sys.path.insert(0, str(ROOT/'tools/pixel_support'))
    import outward
    config=json.loads((ROOT/'tools/pixel_support/inputs.json').read_text())
    representatives={}
    for body in layout['bodies']:
        if barrel(body):
            b=copy.deepcopy(body); b['center_mm'][2]=0.; b['half_v_mm']=1.
            representatives[(b['layer_id'],b['col'])]=b
    bodies=list(representatives.values())
    boxes=outward.envelopes(bodies,config)
    conflicts=[]
    for i,a in enumerate(boxes):
        others=[b for b in bodies if b['module_id']!=a['module_id']]
        others += [b for b in boxes[i+1:] if b['module_id']!=a['module_id']]
        for b in others:
            if _obb_overlap(a,b,tolerance):
                conflicts.append([a['layer_id'],a['col'],a['kind'],b['layer_id'],b['col'],b.get('kind','module')])
    maximum=max(math.hypot(*p) for b in boxes+bodies for p in outward.corners(b))
    trunk=next(r for r in layout['metadata']['services']['routes'] if r['id']=='pixel-trunk-P')
    return dict(conflicts=conflicts,staves=len(bodies),radial_headroom_mm=trunk['r_min_mm']-maximum,
                scope='Extruded transverse candidate-A plates/spines and occupied module boxes; excludes new flex, bonds, rings and connectors')
