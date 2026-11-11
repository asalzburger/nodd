"""Retain matched fresh-process phase observations, without summing nested phases."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import statistics


def summarize(runs):
    observations = []
    groups = defaultdict(list)
    for label, directory in runs:
        timing = json.loads((directory / 'timing.json').read_text())
        provenance = json.loads((directory / 'provenance.json').read_text())
        inventory = json.loads((directory / 'inventory.json').read_text())
        if timing['exit_code'] or timing['sensitive_paths'] != 46682:
            raise ValueError('Unsuccessful or wrong-detector observation')
        phases = defaultdict(list)
        for phase in map(json.loads, (directory / 'native-phases.jsonl').read_text().splitlines()):
            phases[phase['name']].append(phase['wall_s'])
        required = ['xerces_dom_parse_path', 'g4_initialize', 'g4_close_geometry_voxelization',
                    'g4_update_couple_table', 'g4_event_transport_and_recording']
        if any(not phases[k] for k in required):
            raise ValueError('Missing native phase')
        item = dict(variant=label, directory=str(directory), timing=timing,
                    phase_wall_seconds=dict(phases), tgeo=inventory['tgeo'],
                    geant4=inventory['geant4'], provenance=provenance,
                    artifact_sha256={name:hashlib.sha256((directory / name).read_bytes()).hexdigest()
                        for name in ['timing.json', 'native-phases.jsonl', 'inventory.json',
                                     'provenance.json', 'probe.log']})
        observations.append(item)
        metrics = {k:timing[k] for k in ['mapping_seconds','wall_including_inventory_seconds','peak_child_rss_bytes']}
        # Only a single invocation is compared for these phases. Keep every
        # interval in observations; fail rather than choose one of several.
        for key in ['g4_initialize', 'g4_close_geometry_voxelization', 'g4_update_couple_table']:
            if len(phases[key]) != 1:
                raise ValueError('Ambiguous repeated initialization phase: ' + key)
            metrics[key + '_seconds'] = phases[key][0]
        groups[label].append(metrics)
    summary = {}
    for label, rows in groups.items():
        summary[label] = dict(runs=len(rows), metrics={key:dict(
            minimum=min(r[key] for r in rows), maximum=max(r[key] for r in rows),
            median=statistics.median(r[key] for r in rows)) for key in rows[0]})
    return dict(scope='Isolated short-strip barrel cache/real-mother PROTOTYPE, full tracker startup',
                observations=observations, summary=summary,
                limitations=['Phase intervals can nest; do not add them.',
                             'Observed ranges are not confidence intervals.',
                             'Timing does not establish material, response or reconstruction equivalence.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='append', required=True, help='VARIANT=RUN_DIRECTORY')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = summarize([(s.split('=',1)[0],Path(s.split('=',1)[1])) for s in args.run])
    args.output.write_text(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__':
    main()
