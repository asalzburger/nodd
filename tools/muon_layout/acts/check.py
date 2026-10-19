"""Verify captured evidence without claiming a native ACTS rerun."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from tools.muon_layout.acts.prepare import configuration,sha,save

OUTPUT=ROOT/'docs/validation/DES-040/acts-propagation'


def check(capture=False):
    c=configuration()
    summary=json.loads((OUTPUT/'summary.json').read_text())
    controls=json.loads((OUTPUT/'controls.json').read_text())
    if summary['configuration']!=c or controls['passed'] is not True:
        raise ValueError('configuration differs or native controls did not pass')
    if summary['native_metadata']['executable_sha256']!=controls['executable_sha256']:
        raise ValueError('native scan executable differs from executed controls')
    used=summary['native_metadata']['controls_sha256']
    if used not in {sha(p) for p in (OUTPUT/'controls.json',OUTPUT/'controls-acquisition.json') if p.exists()}:
        raise ValueError('native acquisition control record is not retained')
    if summary['audit']['orphan_transitions'] or summary['audit']['navigation_unqualified_tracks']:
        raise ValueError('unresolved chamber boundary navigation')
    expected=(c['map_grid']['eta_bins']*c['map_grid']['phi_bins']+c['full_sphere_directions'])*len(c['momentum_GeV'])*len(c['charge_e'])
    with np.load(OUTPUT/'tracks.npz',allow_pickle=False) as tracks:
        if len(tracks['track_id'])!=expected or not np.array_equal(tracks['track_id'],np.arange(expected)):
            raise ValueError('generated track denominator lost')
        if np.any(tracks['status']=='missing'):
            raise ValueError('missing native status')
        for case in summary['cases']:
            mask=(tracks['momentum_GeV']==case['momentum_GeV'])&(tracks['charge']==case['charge'])
            sphere=mask&(tracks['sample']==1)
            if sphere.sum()!=c['full_sphere_directions'] or not np.isclose(tracks['solid_angle_weight_sr'][sphere].sum(),4*np.pi):
                raise ValueError('full-sphere denominator changed')
            grid=mask&(tracks['sample']==0)
            cells=tracks['eta_bin'][grid]*c['map_grid']['phi_bins']+tracks['phi_bin'][grid]
            if not np.array_equal(np.sort(cells),np.arange(c['map_grid']['eta_bins']*c['map_grid']['phi_bins'])):
                raise ValueError('display grid lost or duplicated a generated ray')
    with np.load(OUTPUT/'hits.npz',allow_pickle=False) as hits:
        if hits['geometry_id'].dtype!=np.dtype('uint64'):
            raise ValueError('native geometry IDs lost precision')
        xyz=np.column_stack([hits[k+'_m'] for k in ('x','y','z')])
        if not np.isfinite(xyz).all() or len(xyz)!=summary['audit']['raw_boundary_hits']:
            raise ValueError('invalid or missing native positions')
        if np.any((hits['panel_index']<0)|(hits['panel_index']>=1560)):
            raise ValueError('unknown chamber owner')
    for name,digest in summary['artifacts'].items():
        if sha(OUTPUT/name)!=digest:
            raise ValueError('analysis artifact changed: '+name)
    manifest=OUTPUT/'artifact-manifest.json'
    if capture:
        names=['summary.json','tracks.npz','hits.npz','controls.json','controls-initial.json',
               'controls-acquisition.json','controls-refinement-failure.json',
               'rebuild.md','rebuild.json','provenance.json','results.md','figures.json',
               'review-code-85b.md','review-code-85b.json','independent-code-checks.py','independent-code-checks.json',
               'hit-positions.png','entrance-segments.png','entrance-paired-stations.png','momentum-coverage.png']
        files=[OUTPUT/name for name in names]+sorted(Path(__file__).parent.glob('*.py'))
        files += [Path(__file__).parent/name for name in ['config.json','CMakeLists.txt','propagate.cpp','README.md','README-engine.md']]
        save(manifest,dict(scope='Captured artifact/source integrity; native ACTS propagation is not rerun by CI.',
                           files={str(p.relative_to(ROOT)):sha(p) for p in files}))
    for path,digest in json.loads(manifest.read_text())['files'].items():
        if sha(ROOT/path)!=digest:
            raise ValueError('frozen evidence changed: '+path)
    print(f'Captured ACTS evidence: {expected} tracks, native control gate and artifact hashes passed; no native rerun.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--capture',action='store_true');a=p.parse_args();check(a.capture)
