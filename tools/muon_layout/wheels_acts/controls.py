"""Execute inherited native gates on each new system and domain-specific fixtures."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.muon_layout.acts.controls import (
    Controls as OriginalControls, repository_paths, audit_run, read_primaries,
    analytic_ray_events, compare_runs, write_fixture, _fixture_panel)
from tools.muon_layout.acts.prepare import sha, save, write_tracks, entrance
from tools.muon_layout.wheels_acts.prepare import CONFIG


def prepared(work):
    work = Path(work)
    inputs = json.loads((work/'inputs.json').read_text())
    c = inputs['configuration']
    if sha(CONFIG) != c['study_configuration_sha256']:
        raise ValueError('Study configuration changed since preparation')
    for key in ('geometry', 'map'):
        if sha(ROOT/c[key]) != c[key+'_sha256']:
            raise ValueError('Prepared physical input changed: '+key)
    for name, digest in inputs['files'].items():
        if sha(work/name) != digest:
            raise ValueError('Prepared runtime input changed: '+name)
    return inputs


def dimension_args(c):
    return ['--world-radius-m', str(c['world']['radius_m']),
            '--world-half-z-m', str(c['world']['half_z_m']),
            '--entrance-radius-m', str(c['entrance']['radius_m']),
            '--entrance-half-z-m', str(c['entrance']['half_z_m'])]


class Controls(OriginalControls):
    def __init__(self, work, executable, output):
        self.work, self.executable, self.output = map(lambda p: Path(p).resolve(), (work, executable, output))
        inputs = prepared(self.work)
        self.config = inputs['configuration']
        self.panels = json.loads((ROOT/self.config['geometry']).read_text())['panels']
        self.runs = self.work/'native-controls'/sha(self.executable)[:12]
        self.runs.mkdir(parents=True, exist_ok=True)
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.selection = self.prepare_control_tracks()
        sources = [Path(__file__), CONFIG, Path(__file__).with_name('prepare.py'),
                   Path(__file__).with_name('variant.py'), Path(__file__).with_name('CMakeLists.txt'),
                   ROOT/'tools/muon_layout/acts/propagate.cpp', ROOT/'tools/muon_layout/acts/controls.py',
                   ROOT/'tools/muon_layout/acts/analyze.py', ROOT/'tools/muon_layout/geometry.py']
        self.report = dict(passed=False, system=self.config['system'],
                           source_revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                           executable_sha256=sha(self.executable), configuration_sha256=sha(CONFIG),
                           preparation_sha256=sha(self.work/'inputs.json'),
                           physical_inputs={k: self.config[k] for k in ['geometry', 'map', 'geometry_sha256', 'map_sha256']},
                           source_sha256={str(p.relative_to(ROOT)): sha(p) for p in sources},
                           direction_selection=self.selection, checks=[],
                           scope='Inherited unchanged native-root/finite-owner/helix/refinement gates with configured expanded world and common launch; additional wheel/domain controls.')
        self.flush()

    def native(self, name, tracks=None, geometry=None, field='map', bz=0., step=.05,
               tolerance=1e-8, policy='indexed', mode='surface-audit', query=False,
               inspect=False, rk_tolerance=None):
        directory = self.runs/name
        directory.mkdir(parents=True, exist_ok=True)
        command = [str(self.executable), '--output-dir', str(directory),
                   '--map', str(self.work/'map.bin'), '--field', field, '--mode', mode,
                   '--policy', policy, '--bz', str(bz), '--max-step-m', str(step),
                   '--tolerance-m', str(tolerance), '--rk-tolerance-m',
                   str(self.config['rk_tolerance_m'] if rk_tolerance is None else rk_tolerance),
                   '--max-steps', str(self.config['max_steps']),
                   '--path-limit-m', str(self.config['path_limit_m']), *dimension_args(self.config)]
        if query:
            command += ['--query-field', str(self.work/'query-points.dat')]
        else:
            command += ['--geometry', str(geometry or self.work/'geometry.dat')]
            command += ['--inspect-only'] if inspect else ['--tracks', str(tracks)]
        start = time.perf_counter()
        result = subprocess.run(command, capture_output=True, text=True, cwd=ROOT)
        record = dict(argv=command, returncode=result.returncode,
                      elapsed_seconds=time.perf_counter()-start,
                      stdout=result.stdout, stderr=result.stderr,
                      output_sha256={p.name: sha(p) for p in directory.iterdir() if p.is_file()})
        if (directory/'metadata.json').exists():
            record['native_metadata'] = json.loads((directory/'metadata.json').read_text())
        self.current_commands.append(record)
        return directory, record

    def unbounded_negative(self):
        # Same original seed directions / p,q as the historical witnesses,
        # remapped because the separate cap bank changes rows per case.
        with np.load(self.work/'primaries.npz', allow_pickle=False) as source:
            data = dict(source)
        selected = np.flatnonzero((data['momentum_GeV'] == 2.65) & (data['charge'] == 1) &
                                  np.isin(data['direction_id'], [5958, 13902]))
        assert len(selected) == 2
        tracks = self.runs/'unbounded-witness-tracks.dat'
        write_tracks(tracks, data, selected)
        audits, commands = [], []
        for policy in ('indexed', 'unbounded'):
            directory, command = self.native('witness-'+policy, tracks=tracks, policy=policy)
            commands.append(command)
            if command['returncode']:
                return False, dict(negative_control=True, error='Witness process failed'), commands
            audits.append(audit_run(directory, self.panels, self.config['active_border_m']))
        matches, differences = compare_runs(*audits)
        return True, dict(negative_control=True, primary_algorithm=False,
                          direction_ids=[5958, 13902], track_ids=selected.tolist(),
                          expected_negative_observed=not matches, matches_bounded_primary=matches,
                          scope='Historical seed directions remapped into the new bank/domain; changed-system adverse outcome need not equal the old one.',
                          differences=differences), commands

    def domains(self):
        h, r = self.config['entrance']['half_z_m'], self.config['entrance']['radius_m']
        primaries = {0: dict(p=1000., q=1., start=np.array([0., 0., h+1e-5]), direction=np.array([0., 0., 1.])),
                     1: dict(p=1000., q=1., start=np.array([0., 0., h+1e-5]), direction=np.array([0., 0., -1.])),
                     2: dict(p=1000., q=1., start=np.array([r+1e-5, 0., 0.]), direction=np.array([1., 0., 0.]))}
        geometry, tracks = write_fixture(self.runs/'domain-fixture', [_fixture_panel('test-only-domain')], primaries)
        directory, command = self.native('expanded-world-and-common-entry', tracks=tracks, geometry=geometry, field='zero')
        if command['returncode']:
            return False, {}, [command]
        audit = audit_run(directory, [_fixture_panel('test-only-domain')])
        expected = {0: ('completed', np.array([0., 0., self.config['world']['half_z_m']])),
                    1: ('returned_to_entrance', np.array([0., 0., h])),
                    2: ('completed', np.array([self.config['world']['radius_m'], 0., 0.]))}
        errors = []
        for ident, (status, point) in expected.items():
            row = audit['tracks'][ident]
            got = np.array([float(row[k+'_m']) for k in ('x', 'y', 'z')])
            errors.append(float(np.linalg.norm(got-point)))
            assert row['status'] == status
        meta = command['native_metadata']
        assert meta['world_half_z_m'] == self.config['world']['half_z_m']
        assert meta['entrance_half_z_m'] == h
        return max(errors) < 1e-6, dict(tracks=3, maximum_position_error_m=max(errors),
                                       tolerance_m=1e-6, native_metadata=meta), [command]

    def wheel_edges(self):
        panels = []
        for side in (-1, 1):
            for station in (1, 3):
                panels.append(next(p for p in self.panels if p['kind'] == 'endcap' and p['side'] == side and p['station'] == station))
        primaries = {}
        for panel in panels:
            vertices = np.asarray(panel['vertices_m'])
            center = vertices.mean(axis=0)
            points = [center]
            # Inside/outside perturbations of each side midpoint, plus bore and
            # outer corners. Exact clips determine which full prism is crossed.
            for a, b in zip(vertices, np.roll(vertices, -1, axis=0)):
                mid = (a+b)/2
                toward = (center-mid)/np.linalg.norm(center-mid)
                points += [mid+1e-4*toward, mid-1e-4*toward]
            for xy in points:
                point = np.asarray(panel['origin_m'])+np.asarray(panel['basis'])@np.r_[xy, 0.]
                direction = point/np.linalg.norm(point)
                _, start, _ = entrance(direction[None, :], self.config['entrance'])
                primaries[len(primaries)] = dict(p=1000., q=1., start=start[0], direction=direction)
        geometry, tracks = write_fixture(self.runs/'wheel-edge-input', panels, primaries)
        directory, command = self.native('wheel-bore-sector-edge-exact', tracks=tracks, geometry=geometry, field='zero')
        if command['returncode']:
            return False, {}, [command]
        audit = audit_run(directory, panels)
        maximum, mismatches = 0., []
        for ident, primary in primaries.items():
            expected = analytic_ray_events(primary, panels, audit['catalog'])
            actual = audit['events'][ident]
            if [(e[1], e[2]) for e in expected] != [(int(e['panel_index']), int(e['face_index'])) for e in actual]:
                mismatches.append(ident)
                continue
            for oracle, event in zip(expected, actual):
                point = np.array([event[k+'_m'] for k in ('x', 'y', 'z')])
                maximum = max(maximum, float(np.linalg.norm(point-oracle[4])))
        return not mismatches and maximum < 1e-6, dict(tracks=len(primaries),
                    event_sequence_mismatches=mismatches, maximum_position_error_m=maximum,
                    tolerance_m=1e-6, scope='Actual first/last wheel prisms at both ends; near-sector edges and radial bases.'), [command]

    def run(self):
        super().run()
        self.check('expanded_world_and_common_launch', self.domains)
        self.check('actual_wheel_edges_bore_and_sector_gaps', self.wheel_edges)
        self.report['passed'] = (sha(self.executable) == self.report['executable_sha256'] and
                                 all(c['passed'] for c in self.report['checks']))
        self.flush()
        return self.report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = Controls(args.work, args.executable, args.output).run()
    raise SystemExit(0 if result['passed'] else 1)
