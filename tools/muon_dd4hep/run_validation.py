#!/usr/bin/env python3
"""Run the issue92/93 envelope gate and requested DDSim transport smoke test.

Activate DD4hep/Geant4 first. Reports distinguish source/native geometry checks
from Air-envelope transport; they cannot establish detector response.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def event_count(path):
    import ROOT as pyroot
    f = pyroot.TFile.Open(str(path))
    if not f or f.IsZombie():
        raise RuntimeError('DDSim output is not a readable ROOT file')
    keys = [str(k.GetName()) for k in f.GetListOfKeys()]
    counts = {}
    for key in ('events', 'EVENT', 'Events'):
        obj = f.Get(key)
        if obj and hasattr(obj, 'GetEntries'):
            counts[key] = int(obj.GetEntries())
    f.Close()
    if len(counts) != 1:
        raise RuntimeError(f'Expected one recognized event tree, found {counts}; keys={keys}')
    return dict(tree=next(iter(counts)), events=next(iter(counts.values())), keys=keys)


def execute(command, log, records, env):
    with log.open('w') as stream:
        result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, env=env, cwd=ROOT)
    records.append(dict(command=command, exit_code=result.returncode, log=log.name, log_sha256=digest(log)))
    return result.returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('compact', 'expected', 'library', 'output-dir'):
        parser.add_argument('--' + key, type=Path, required=True)
    parser.add_argument('--events', type=int, default=1000)
    parser.add_argument('--seed', type=int, default=92393)
    parser.add_argument('--overlap-tolerance-mm', type=float, default=1e-5)
    args = parser.parse_args(argv)
    if args.events < 1 or not 0 < args.overlap_tolerance_mm:
        parser.error('events and numerical overlap tolerance must be positive')
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    report_path = output / 'run.json'
    # Refuse to reuse stale successful evidence after a failed attempt.
    if report_path.exists() or (output / 'test_muon_system.root').exists():
        parser.error('use a fresh output directory for each run')
    report = dict(status='FAIL', recorded_at=datetime.now(timezone.utc).isoformat(),
                  source_revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  source_dirty=bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()),
                  python_version=platform.python_version(), commands=[], errors=[], artifacts={},
                  overlap_tolerance_mm=args.overlap_tolerance_mm, requested_events=args.events, seed=args.seed,
                  physics_list='FTFP_BERT', empty_event_action='nODDMuonEmptyEvent', output_plugin='DD4HEP ROOT', user_particle_handler='', particle='gamma', energy='20*GeV', distribution='uniform',
                  limitations=['Air-filled chamber and warm-reservation envelopes; no material/response validation.',
                               'No Geant4 magnetic field, HCAL or484 support bodies in this bounded compact.',
                               'No drift tubes or sensitive response in the initial envelope stage.',
                               'Default tracker-region particle handler disabled because this compact has no tracker or sim-hits.',
                               'An empty Geant4 hit container enables MC-truth persistence; it creates no hit collections.'])
    try:
        for key in ('compact', 'expected', 'library'):
            path = getattr(args, key).resolve()
            report['artifacts'][key] = dict(name=path.name, sha256=digest(path))
        report['artifacts']['runner'] = dict(name=Path(__file__).name, sha256=digest(__file__))
        for filename in ('tools/muon_dd4hep/run_with_factory.py', 'prototypes/muon/MuonEvent.cpp'):
            report['artifacts'][filename] = dict(name=filename, sha256=digest(ROOT / filename))
        import dd4hep
        import ROOT as pyroot
        report['native_length_per_mm'] = float(dd4hep.mm)
        report['root_version'] = pyroot.gROOT.GetVersion()
        env = os.environ.copy()
        libdir = str(args.library.resolve().parent)
        for name in ('DD4HEP_LIBRARY_PATH', 'LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH'):
            env[name] = libdir + os.pathsep + env.get(name, '')
        stock = shutil.which('checkOverlaps')
        ddsim = shutil.which('ddsim')
        if not stock or not ddsim:
            raise RuntimeError('Activated installation must provide checkOverlaps and ddsim')
        report['artifacts']['installed_checkOverlaps'] = dict(name='checkOverlaps', sha256=digest(stock))
        # checkOverlaps passes tolerance directly to ROOT, despite its mm help.
        # Convert physical mm to this installation's native ROOT units explicitly.
        native_tolerance = args.overlap_tolerance_mm * float(dd4hep.mm)
        report['stock_tolerance_native'] = native_tolerance
        load_and_run = str(ROOT / 'tools/muon_dd4hep/run_with_factory.py')
        stock_command = [sys.executable, load_and_run, str(args.library.resolve()), stock,
                         '-c', str(args.compact.resolve()), '-t', str(native_tolerance)]
        if execute(stock_command, output / 'checkOverlaps.log', report['commands'], env):
            raise RuntimeError('DD4hep checkOverlaps execution failed')
        validator_output = output / 'geometry-validation.json'
        validator_command = [sys.executable, '-B', str(ROOT / 'tools/muon_dd4hep/validate.py'),
                             '--compact', str(args.compact.resolve()), '--expected', str(args.expected.resolve()),
                             '--library', str(args.library.resolve()), '--output', str(validator_output),
                             '--overlap-tolerance-mm', str(args.overlap_tolerance_mm)]
        rc = execute(validator_command, output / 'geometry-validation.log', report['commands'], env)
        if not validator_output.exists():
            raise RuntimeError('Native validator produced no structured geometry report')
        geometry = json.loads(validator_output.read_text())
        report['artifacts']['geometry_validation'] = dict(name=validator_output.name, sha256=digest(validator_output))
        if rc or geometry.get('status') != 'PASS':
            raise RuntimeError('Native geometry gate failed; DDSim was not started')
        root_output = output / 'test_muon_system.root'
        simulation_command = [sys.executable, load_and_run, str(args.library.resolve()), ddsim,
                              '--enableGun', '--numberOfEvents', str(args.events), '--gun.energy', '20*GeV',
                              '--gun.particle', 'gamma', '--gun.distribution', 'uniform',
                              '--compactFile', str(args.compact.resolve()), '--outputFile', str(root_output),
                              '--random.seed', str(args.seed), '--physics.list', 'FTFP_BERT',
                              '--part.userParticleHandler', '', '--outputConfig.forceDD4HEP',
                              '--action.event', 'nODDMuonEmptyEvent/EmptyHitContainer']
        if execute(simulation_command, output / 'ddsim.log', report['commands'], env):
            raise RuntimeError('DDSim transport failed')
        report['transport_output'] = event_count(root_output)
        if report['transport_output']['events'] != args.events:
            raise RuntimeError('DDSim output event count differs from request')
        report['artifacts']['simulation_root'] = dict(name=root_output.name, sha256=digest(root_output),
                                                     size_bytes=root_output.stat().st_size)
        report['status'] = 'PASS'
    except Exception as exc:
        report['errors'].append(f'{type(exc).__name__}: {exc}')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], errors=report['errors'], report=str(report_path))))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
