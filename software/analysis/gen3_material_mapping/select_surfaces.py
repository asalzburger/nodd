#!/usr/bin/env python3
"""Select one native portal per sensitive layer plus configured gap/shell carriers."""
import argparse
import copy
import hashlib
import json
from pathlib import Path


def positive_bins(value, name):
    if type(value) is not int or value < 1:
        raise ValueError(f'{name} must be a positive integer')
    return value


def select(geometry, config):
    if config['schema_version'] != 1:
        raise ValueError('Unsupported configuration version')
    phi = positive_bins(config['phi_bins'], 'phi_bins')
    bins = {name: positive_bins(v,name) for name,v in config['bins'].items()}
    if config['layer_policy'] != {'pixel_barrel':'after','otherwise':'before'}:
        raise ValueError('This trial requires pixel barrel after; all others before')
    if config['shared_portal_binning'] not in ('maximum_requested','error'):
        raise ValueError('Unsupported shared-portal binning policy')
    portals = {p['surface_id']: p for p in geometry['portals']}
    if len(portals) != len(geometry['portals']):
        raise ValueError('Duplicate portal surface ID')
    if len({p['geometry_id'] for p in portals.values()}) != len(portals):
        raise ValueError('Duplicate portal geometry ID')
    volumes = {v['name']: v for v in geometry['volumes']}
    selected = {}
    conflicts = []

    def face(volume, kind, value):
        candidates=[]
        for sid in volume['portal_surface_ids']:
            p=portals[sid]
            if p['type']!=kind: continue
            coordinate=p['radius_mm'] if kind=='cylinder' else p['z_mm']
            if abs(coordinate-value)<1e-6:candidates.append(p)
        if len(candidates)!=1:
            raise ValueError(f"Expected one {kind} face at {value} on {volume['name']}; got {len(candidates)}")
        return candidates[0]

    def add(portal, role, family):
        axis='z' if portal['type']=='cylinder' else 'r'
        requested={'phi':phi,axis:bins[family]}
        role={**role,'binning_family':family,'requested_bins':requested}
        gid=portal['geometry_id']
        if gid not in selected:
            selected[gid]={'geometry_id':gid,'surface_id':portal['surface_id'],
                'material_key':f'nodd-gen3-portal-{gid}','type':portal['type'],
                'rz_segment_mm':portal['rz_segment_mm'],'bins':copy.deepcopy(requested),
                'roles':[],'owners':portal['owners']}
        item=selected[gid]
        if item['bins']!=requested:
            if config['shared_portal_binning']=='error':
                raise ValueError(f'Conflicting bins on shared portal {gid}')
            conflicts.append({'geometry_id':gid,'existing_bins':copy.deepcopy(item['bins']),
                              'new_request':requested,'resolution':'maximum_requested'})
            item['bins'][axis]=max(item['bins'][axis],requested[axis])
        item['roles'].append(role)

    layer_pairs=set()
    for group in sorted(geometry['sensor_groups'],key=lambda g:(g['system'],g['layer'])):
        sy,layer=group['system'],group['layer'];pair=(sy,layer)
        if pair in layer_pairs:raise ValueError(f'Duplicate sensitive layer {pair}')
        layer_pairs.add(pair)
        v=volumes[f'System{sy}Layer{layer}']
        detector='pixel' if sy<=3 else 'short_strip' if sy<=5 else 'long_strip'
        barrel=sy in (1,4,6)
        after=sy==1
        if barrel:
            p=face(v,'cylinder',v['r_max_mm'] if after else v['r_min_mm'])
        else:
            zmin,zmax=v['z_min_mm'],v['z_max_mm']
            if zmin*zmax<=0:raise ValueError('Endcap volume crosses the origin')
            p=face(v,'disc',zmin if zmin>0 else zmax)
        add(p,{'kind':'sensitive_layer','system':sy,'layer':layer,
               'detector':detector,'side':'after' if after else 'before'},
            detector+('_barrel' if barrel else '_endcap'))

    extras=config['extras']
    if extras['beam_pipe']:
        v=volumes['BeamPipe'];add(face(v,'cylinder',v['r_max_mm']),{'kind':'beam_pipe'},'beam_pipe')
    for name in extras['gap_volumes']:
        v=volumes[name]
        for side in ('inner','outer'):
            p=face(v,'cylinder',v['r_min_mm'] if side=='inner' else v['r_max_mm'])
            add(p,{'kind':'gap_cylinder','volume':name,'side':side},'gap_cylinder')
    if extras['barrel_endcap_separators']:
        for sy,detector in ((1,'pixel'),(4,'short_strip'),(6,'long_strip')):
            v=next(volumes[f'System{system}Layer{layer}'] for system,layer in sorted(layer_pairs) if system==sy)
            for side in ('negative','positive'):
                add(face(v,'disc',v['z_min_mm'] if side=='negative' else v['z_max_mm']),
                    {'kind':'barrel_endcap_separator','system':sy,'detector':detector,'side':side},detector+'_separator')
    if extras['outer_shell_volume']:
        v=volumes[extras['outer_shell_volume']]
        add(face(v,'cylinder',v['r_max_mm']),{'kind':'outer_shell','volume':v['name'],'side':'outer'},'outer_shell_cylinder')
        for side in ('negative','positive'):
            add(face(v,'disc',v['z_min_mm'] if side=='negative' else v['z_max_mm']),
                {'kind':'outer_shell','volume':v['name'],'side':side},'outer_shell_disc')
    for gid, override in config['surface_overrides'].items():
        gid=int(gid)
        if gid not in selected:raise ValueError(f'Override targets unselected portal {gid}')
        item=selected[gid];axis='z' if item['type']=='cylinder' else 'r'
        if set(override)!={'phi',axis}:raise ValueError('Override axes mismatch')
        item['bins']={k:positive_bins(v,k) for k,v in override.items()}
        item['explicit_binning_override']=True
    surfaces=sorted(selected.values(),key=lambda p:p['geometry_id'])
    roles=[r for p in surfaces for r in p['roles']]
    counts={'sensitive_layers':len(layer_pairs),'logical_roles':len(roles),
            'unique_surfaces':len(surfaces),'cylinders':sum(p['type']=='cylinder' for p in surfaces),
            'discs':sum(p['type']=='disc' for p in surfaces),
            'shared_physical_portals':sum(len(p['roles'])>1 for p in surfaces),
            'material_bins':sum(p['bins']['phi']*p['bins'].get('z',p['bins'].get('r')) for p in surfaces)}
    return {'schema_version':1,'status':'PROTOTYPE configurable full-inventory portal mapping',
            'material_inventory':'all recorded material; clear native sensor and pipe slabs first',
            'assignment':'ACTS nearest finite intersection; side selects portal relative to sensitive layer',
            'counts':counts,'binning_conflicts':conflicts,'surfaces':surfaces,'configuration':config}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--geometry',type=Path,required=True)
    ap.add_argument('--config',type=Path,default=Path(__file__).with_name('mapping_config.json'))
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();manifest=select(json.loads(args.geometry.read_text()),json.loads(args.config.read_text()))
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    manifest['provenance']={'geometry_sha256':digest(args.geometry),'config_sha256':digest(args.config),
        'selector_sha256':digest(Path(__file__)),'native_geometry_provenance':json.loads(args.geometry.read_text())['provenance']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n')
    print(json.dumps(manifest['counts'],indent=2))
    print('Shared portal binning:',manifest['binning_conflicts'])


if __name__=='__main__':main()
