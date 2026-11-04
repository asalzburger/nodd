#!/usr/bin/env python3
"""Check completed matched ROOT output and summarize observed timing evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics


def statistics_for(values):
    return {'n': len(values), 'sum': sum(values), 'mean': statistics.mean(values),
            'median': statistics.median(values), 'min': min(values), 'max': max(values),
            'stdev': statistics.stdev(values) if len(values)>1 else 0.0}


def inspect(directory):
    import awkward as ak
    import numpy as np
    import uproot
    metrics = json.loads((directory/'metrics.json').read_text())
    settings = metrics['settings']
    assert len(metrics['events']) == settings['events'], 'incomplete event metrics'
    root = directory/'tracks.root'
    tree = uproot.open(root)['material_tracks']
    fields = ['event_id', 'v_x', 'v_y', 'v_z', 'v_px', 'v_py', 'v_pz', 'v_phi', 'v_eta']
    data = tree.arrays(fields+['t_X0', 't_L0', 'mat_step_length', 'mat_X0', 'mat_L0'], library='ak')
    assert tree.num_entries == settings['events']*settings['tracks_per_event']
    ids, counts = np.unique(ak.to_numpy(data.event_id), return_counts=True)
    assert np.array_equal(ids, np.arange(settings['events']))
    assert np.all(counts == settings['tracks_per_event'])
    for field in ('t_X0', 't_L0'):
        assert np.all(np.isfinite(ak.to_numpy(data[field])))
        assert np.all(ak.to_numpy(data[field]) > 0)
    for field in ('v_x', 'v_y', 'v_z'):
        assert np.all(ak.to_numpy(data[field]) == 0)
    for total, length in (('t_X0','mat_X0'), ('t_L0','mat_L0')):
        calculated = ak.to_numpy(ak.sum(data.mat_step_length/data[length],axis=1))
        assert np.allclose(ak.to_numpy(data[total]), calculated, rtol=2e-6, atol=2e-6)
    bank = np.column_stack([ak.to_numpy(data[field]) for field in fields])
    bank = bank[np.lexsort(tuple(bank[:,i] for i in reversed(range(bank.shape[1]))))]
    steady = metrics['events'][1:]
    steps = ak.to_numpy(ak.num(data.mat_step_length))
    result = {'settings': settings, 'phases': metrics['phases'],
        'total_wall_s': metrics['total_wall_s'], 'total_cpu_s': metrics['total_cpu_s'],
        'peak_rss_bytes': metrics['peak_rss_bytes'], 'first_event': metrics['events'][0],
        'steady_wall_s': statistics_for([e['wall_s'] for e in steady]),
        'steady_cpu_s': statistics_for([e['cpu_s'] for e in steady]),
        'integrity': {'entries': tree.num_entries, 'events':len(ids),
            'tracks_per_event':settings['tracks_per_event'], 'finite_positive_totals':True,
            'totals_recomputed_from_steps':True, 'origin_vertices':True,
            'generated_bank_sha256':hashlib.sha256(bank.tobytes()).hexdigest(),
            'root_sha256':hashlib.sha256(root.read_bytes()).hexdigest(),
            'root_bytes':root.stat().st_size,
            'recorded_steps':int(steps.sum()),
            'steps_per_track':statistics_for(steps.tolist()),
            'mean_t_X0':float(ak.mean(data.t_X0)), 'mean_t_L0':float(ak.mean(data.t_L0))}}
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('odd',type=Path)
    parser.add_argument('nodd',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    results={name:inspect(path) for name,path in (('odd',args.odd),('nodd',args.nodd))}
    assert results['odd']['settings'] == results['nodd']['settings'], 'unmatched settings'
    assert results['odd']['integrity']['generated_bank_sha256'] == results['nodd']['integrity']['generated_bank_sha256'], 'unmatched generated probes'
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(results,indent=2)+'\n')
    print(args.output)


if __name__=='__main__':
    main()
