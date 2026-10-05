#!/usr/bin/env python3
"""PROTOTYPE: compare Python-native modules with the historical JSON control."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import shlex
import subprocess
import sys

import acts

from probe import construction, digest, fixture_digest, navigation, package_version
from propagation_view import run


def git(*args, cwd=None):
    return subprocess.check_output(['git', *args], cwd=cwd, text=True).strip()


def check_layout(work, stagger_mm):
    cases = {}
    for backend in ('python', 'json'):
        for policy in ('try_all', 'array'):
            directory = work / backend / policy
            directory.mkdir(parents=True, exist_ok=True)
            geo, ctx, surfaces, definitions, root, nodes = construction(
                directory, policy, backend, stagger_mm, json_schema='type')
            result = navigation(geo, ctx, surfaces, definitions, directory/'navigation.csv')
            result.update(sensitive_modules=len(surfaces), unique_ids=len({s.geometryId.value for s in surfaces}),
                          fixture_sha256=fixture_digest(definitions),
                          ids=[s.geometryId.value for s in surfaces])
            if backend == 'python':
                assert not list(directory.glob('*.json')), 'Native construction must not use JSON files'
            cases[f'{backend}/{policy}'] = result
    for policy in ('try_all', 'array'):
        # Exact diagnostic output, identifiers and analytic checks must agree.
        assert cases[f'python/{policy}'] == cases[f'json/{policy}']
    for backend in ('python', 'json'):
        assert (cases[f'{backend}/try_all']['module_intersections'] ==
                cases[f'{backend}/array']['module_intersections'])
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--acts-source', type=Path, required=True)
    args = parser.parse_args()
    source = args.acts_source.resolve()
    if not hasattr(acts.Surface, 'assignIsSensitive'):
        raise RuntimeError('Run with the ACTS source build containing the sensitivity binding.')
    # Fresh work directories prevent stale JSON files from masking the boundary.
    args.work.mkdir(parents=True, exist_ok=False)
    layouts = {name: check_layout(args.work/name, stagger)
               for name, stagger in [('baseline', 0.), ('alternating_barrel_z_2mm', 2.)]}
    propagation = {}
    for backend in ('python', 'json'):
        propagation[backend] = [run(args.work/'propagation'/backend/f'{field:g}T', field, backend, json_schema='type')[0]
                                for field in (0., 2.)]
    assert propagation['python'] == propagation['json']
    assert (layouts['baseline']['python/array']['fixture_sha256'] !=
            layouts['alternating_barrel_z_2mm']['python/array']['fixture_sha256'])
    code = Path(__file__).parent
    report = dict(
        status='PROTOTYPE software capability; no detector design or acceptance',
        recorded_at=datetime.now(timezone.utc).isoformat(),
        command=shlex.join([sys.executable, '-B', *sys.argv]),
        python=platform.python_version(), platform=platform.platform(),
        pyacts_distribution=package_version('pyacts'),
        project_revision=git('rev-parse', 'HEAD'),
        project_code_uncommitted=bool(git('status', '--porcelain', '--', str(code))),
        code_sha256={p.name: digest(p) for p in [Path(__file__), code/'probe.py', code/'propagation_view.py']},
        acts_source_revision=git('rev-parse', 'HEAD', cwd=source),
        acts_source_changes=git('status', '--porcelain', cwd=source).splitlines(),
        acts_surface_binding_sha256=digest(source/'Python/Core/src/Surfaces.cpp'),
        acts_extension_sha256=digest(Path(acts.ActsPythonBindings.__file__)),
        tolerances=dict(center_mm=1e-9, normal=1e-12, propagation_mm=.001, intersection_mm=.002),
        configuration=dict(modules=32, barrel_layers=2, disc_layers=2, rays_per_case=200,
                           seed=42, tracks_per_field=48, fields_T=[0., 2.], pt_GeV=.1, eta=0.,
                           material=False, stagger_mm=[0., 2.], json_control_schema='type/PlaneSurface'),
        layouts=layouts, propagation=propagation,
        limitations=[
            'Source build includes an uncommitted mirror of the draft sensitivity-binding patch; hashes identify it.',
            'JSON is an explicit compatibility control only; Python module construction performs no JSON I/O.',
            'Alternating z positions exercise placement edits, not arbitrary topology or production hermeticity.',
            'Pseudo-navigation rays use the origin and fixed seed; magnetic propagations cover the central barrel slice.',
            'No material, response, reconstruction, physical field map, DD4hep or Geant4 transport validation.',
        ])
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'layouts': {k: {c: v['module_intersections'] for c,v in cases.items()}
                                 for k,cases in layouts.items()}, 'propagation': propagation}, indent=2))


if __name__ == '__main__':
    main()
