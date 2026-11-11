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
    common_hashes = common_command = None
    compact_hashes = {}
    for label, directory in runs:
        timing = json.loads((directory / 'timing.json').read_text())
        provenance = json.loads((directory / 'provenance.json').read_text())
        inventory = json.loads((directory / 'inventory.json').read_text())
        hashes = {Path(p).name:h for p,h in provenance['sha256'].items() if Path(p).name != 'tracker.xml'}
        command = provenance['command'][:]
        for flag in ['--compactFile','--macroFile','--outputFile']:
            command[command.index(flag)+1] = '<run-specific>'
        if common_hashes is None:
            common_hashes,common_command = hashes,command
        elif common_hashes != hashes or common_command != command:
            raise ValueError('Unmatched runtime binaries, materials, instrumentation or simulation command')
        digest = next(h for p,h in provenance['sha256'].items() if Path(p).name == 'tracker.xml')
        if label in compact_hashes and compact_hashes[label] != digest:
            raise ValueError('Variant compact changed between observations')
        compact_hashes[label] = digest
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
                                     'provenance.json', 'probe.log', 'geant4-sensors.json']})
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
    if set(groups) != {'baseline','cache','mother'} or any(len(rows)<2 for rows in groups.values()):
        raise ValueError('Require at least two complete observations for each of the three variants')
    if len(set(compact_hashes.values())) != 3:
        raise ValueError('Expected three distinct variant compacts')
    return dict(scope='Isolated short-strip barrel cache/real-mother PROTOTYPE, full tracker startup',
                matched_identity=dict(common_sha256=common_hashes,common_command=common_command,
                                      variant_compact_sha256=compact_hashes),
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
