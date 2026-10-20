"""Prepare two pinned systems with identical upstream seeds and expanded domains."""
from __future__ import annotations
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.muon_layout.acts.prepare import (
    sha, save, export_geometry, export_map, directions as original_directions,
    entrance, write_tracks)
from tools.toroid_prototype.map import FieldMap

CONFIG = Path(__file__).with_name('config.json')


def configuration(system):
    base = json.loads(CONFIG.read_text())
    selected = base.pop('systems')[system]
    base.update(selected, system=system, study_configuration_sha256=sha(CONFIG))
    for key in ('geometry', 'map'):
        base[key+'_sha256'] = sha(ROOT/base[key])
    return base


def primaries(c):
    data = original_directions(c)
    # Preserve the entire original display/sphere bank, then add disjoint iid
    # cap precision samples. Never fold their weight into the sphere estimate.
    n = c['endcap_cap_directions_per_side']
    mu0 = np.tanh(c['endcap_abs_eta_min'])
    rng = np.random.default_rng(c['endcap_seed'])
    mu = np.r_[rng.uniform(mu0, 1., n), rng.uniform(-1., -mu0, n)]
    phi = rng.uniform(0., 360., 2*n)
    transverse = np.sqrt(1-mu*mu)
    direction = np.column_stack((transverse*np.cos(np.radians(phi)),
                                 transverse*np.sin(np.radians(phi)), mu))
    surface, start, kind = entrance(direction, c['entrance'])
    cap = dict(direction=direction, entrance_position_m=surface, start_m=start,
               entrance_kind=kind, eta_pos=np.arctanh(mu), phi_pos_deg=phi,
               eta_bin=np.full(2*n, -1), phi_bin=np.full(2*n, -1),
               sample=np.repeat([2, 3], n).astype('i1'),
               solid_angle_weight_sr=np.full(2*n, 2*np.pi*(1-mu0)/n))
    keys = list(cap)
    for key in keys:
        data[key] = np.concatenate((data[key], cap[key]), axis=0)
    size = len(data['direction'])
    cases = [(p, q) for p in c['momentum_GeV'] for q in c['charge_e']]
    result = {key: np.concatenate([data[key] for _ in cases]) for key in keys}
    result.update(direction_id=np.tile(np.arange(size), len(cases)),
                  track_id=np.arange(size*len(cases)),
                  momentum_GeV=np.repeat([p for p, _ in cases], size),
                  charge=np.repeat([q for _, q in cases], size),
                  eta_edges=data['eta_edges'], phi_edges_deg=data['phi_edges_deg'])
    return result


def queries(c, work):
    field = FieldMap(ROOT/c['map'])
    with np.load(ROOT/c['map'], allow_pickle=False) as f:
        radius, half_z = float(f['r_m'][-1]), float(f['z_m'][-1])
    rng = np.random.default_rng(90400)
    r, z, phi = rng.uniform(0, radius, 4096), rng.uniform(-half_z, half_z, 4096), rng.uniform(-4*np.pi, 4*np.pi, 4096)
    points = np.column_stack((r*np.cos(phi), r*np.sin(phi), z))
    points = np.vstack((points, [[0, 0, 0], [4.35, 0, 0], [radius, 0, 0],
                                [0, 0, half_z], [0, 0, -half_z],
                                [radius+.001, 0, 0], [0, 0, half_z+.001],
                                [1.4, 0, 0], [4.6, 0, 0]],
                        [[4.35*np.cos(a), 4.35*np.sin(a), 13.3]
                         for a in np.radians([-.000001, 0, .000001, 29.999999, 30., 30.000001, 359.999999, 360.])]))
    expected = np.full_like(points, np.nan)
    status = []
    for i, point in enumerate(points):
        try:
            expected[i] = field.field(point[None, :])[0]
            status.append('ok')
        except ValueError as error:
            status.append('outside_map' if 'outside' in str(error) else 'field_masked')
    with (work/'query-points.dat').open('w') as stream:
        stream.write(str(len(points))+'\n')
        np.savetxt(stream, points, fmt='%.17g')
    np.savez_compressed(work/'query-reference.npz', position_m=points,
                        field_T=expected, status=np.asarray(status))


def prepare(system, work):
    c = configuration(system)
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    panels = export_geometry(c, work/'geometry.dat')
    export_map(c, work/'map.bin')
    data = primaries(c)
    np.savez_compressed(work/'primaries.npz', **data)
    write_tracks(work/'tracks.dat', data)
    size = len(data['track_id'])//(len(c['momentum_GeV'])*len(c['charge_e']))
    controls = np.concatenate([k*size+np.linspace(0, size-1, 80, dtype=int)
                               for k in range(len(c['momentum_GeV'])*len(c['charge_e']))])
    write_tracks(work/'control-tracks.dat', data, controls)
    queries(c, work)
    save(work/'inputs.json', dict(configuration=c, panels=len(panels), tracks=len(data['track_id']),
                                  files={p.name: sha(p) for p in work.iterdir() if p.suffix in ('.dat', '.bin', '.npz')}))
    print(json.dumps(dict(system=system, panels=len(panels), tracks=len(data['track_id']),
                          directions_per_case=size, geometry_sha256=c['geometry_sha256'], map_sha256=c['map_sha256']), indent=2))
    return c, data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--system', choices=['before', 'after'], required=True)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    prepare(args.system, args.work)
