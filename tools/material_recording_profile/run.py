#!/usr/bin/env python3
"""Matched native material recording; use one fresh process per compact."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import time

START = time.perf_counter()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runtime', type=Path, required=True)
    p.add_argument('--compact', type=Path, required=True)
    p.add_argument('--factory', type=Path, action='append', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--events', type=int, default=100)
    p.add_argument('--tracks', type=int, default=100)
    p.add_argument('--seed', type=int, default=228)
    p.add_argument('--inventory', action='store_true', help='Collect native hierarchy after timing')
    p.add_argument('--inventory-only', action='store_true', help='Construct without processing events')
    p.add_argument('--guard-check', action='store_true', help='Run post-transport cache adverse controls')
    p.add_argument('--step-timing', action='store_true', help='Instrument each material stepping callback')
    a = p.parse_args()
    if min(a.events, a.tracks) <= 0 or a.seed < 0:
        p.error('events/tracks must be positive and seed nonnegative')
    if (a.guard_check or a.step_timing) and not os.environ.get('NATIVE_TIMING_LIBRARY'):
        p.error('guard/step diagnostics require NATIVE_TIMING_LIBRARY')
    if a.inventory_only and (a.guard_check or a.step_timing):
        p.error('guard/step diagnostics require transported events')
    if (a.output/'metrics.json').exists() or (a.output/'tracks.root').exists():
        p.error('output already contains evidence; choose a fresh output directory')
    a.output.mkdir(parents=True, exist_ok=True)
    metrics = {'pid': os.getpid(), 'phases': [], 'events': [], 'settings': {
        'events': a.events, 'tracks_per_event': a.tracks, 'seed': a.seed,
        'eta': [-4, 4], 'eta_uniform': True, 'phi_degrees': [0, 360],
        'vertex_mm': [0, 0, 0, 0], 'threads': 1, 'charge': 0, 'pdg': 0,
        'momentum_GeV': [1, 10], 'recordElementFractions': False,
        'prePostStep': True, 'recalculateTotals': True},
        'compact': str(a.compact.resolve()), 'factories': [],
        'steering_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'runtime_pipeline_sha256':hashlib.sha256((a.runtime/'software/running/nodd_material_recording.py').read_bytes()).hexdigest()}

    def save():
        (a.output / 'metrics.json').write_text(json.dumps(metrics, indent=2)+'\n')

    def stamp(label, before):
        now = (time.perf_counter(), time.process_time())
        metrics['phases'].append({'name': label, 'start_s': before[0]-START,
            'wall_s': now[0]-before[0], 'cpu_s': now[1]-before[1],
            'peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        save()
        print('MATPROFILE', label, metrics['phases'][-1], flush=True)
        return now

    t = (START, time.process_time())
    import acts
    import acts.examples
    import acts.examples.geant4
    import acts.examples.hepmc3
    from acts.examples.nodd import DD4hepNoddDetector
    from acts.examples.root import RootMaterialTrackWriter
    import dd4hep
    import ROOT
    t = stamp('imports', t)
    for lib in a.factory:
        lib = lib.resolve()
        if ROOT.gSystem.Load(str(lib)) < 0:
            raise RuntimeError(f'Factory failed to load: {lib}')
        metrics['factories'].append({'path': str(lib),
            'sha256': hashlib.sha256(lib.read_bytes()).hexdigest()})
        os.environ['DD4HEP_LIBRARY_PATH'] = str(lib.parent)+os.pathsep+os.environ.get('DD4HEP_LIBRARY_PATH','')
    t = stamp('factory_loading', t)
    cfg = DD4hepNoddDetector.Config(xmlFileNames=[str(a.compact.resolve())],
        gen3=False, logLevel=acts.logging.INFO, dd4hepLogLevel=acts.logging.WARNING)
    detector = DD4hepNoddDetector(cfg)
    t = stamp('dd4hep_from_compact_and_volume_manager', t)
    source = a.runtime / 'software/running/nodd_material_recording.py'
    spec = importlib.util.spec_from_file_location('recording_pipeline', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Retain the exact generator/converter/writer pipeline of the existing job.
    # Mark algorithm construction separately from execution using a sequencer proxy.
    seq = acts.examples.Sequencer(events=a.events, numThreads=1,
                                  outputDir=str(a.output))
    event_starts = {}

    class Marker(acts.examples.IAlgorithm):
        def __init__(self, name, before):
            super().__init__(name, acts.logging.INFO)
            self.before = before

        def execute(self, ctx):
            n = ctx.eventNumber
            now = (time.perf_counter(), time.process_time())
            if self.before:
                event_starts[n] = now
            else:
                start = event_starts.pop(n)
                metrics['events'].append({'event': n, 'wall_s': now[0]-start[0],
                    'cpu_s': now[1]-start[1], 'start_s': start[0]-START})
                save()
            return acts.examples.ProcessCode.SUCCESS

    class Proxy:
        def addReader(self, value):
            seq.addReader(value)

        def addAlgorithm(self, value):
            if 'Geant4' in type(value).__name__:
                seq.addAlgorithm(Marker('BeforeGeant4', True))
                seq.addAlgorithm(value)
                seq.addAlgorithm(Marker('AfterGeant4', False))
            else:
                seq.addAlgorithm(value)

        def addWriter(self, value):
            seq.addWriter(value)

    module.runMaterialRecording(detector=detector, s=Proxy(),
        tracksPerEvent=a.tracks, seed=a.seed, outputFileBase=a.output/'tracks')
    t = stamp('pipeline_construction_including_g4_conversion_initialize', t)
    if a.step_timing:
        import ctypes
        ctypes.CDLL(os.environ['NATIVE_TIMING_LIBRARY']).materialProfileInstallSteppingTimer()
    if not a.inventory_only:
        seq.run()
    t = stamp('sequencer_run', t)
    metrics['total_wall_s'] = time.perf_counter()-START
    metrics['total_cpu_s'] = time.process_time()
    metrics['peak_rss_bytes'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    save()
    # Audit after the measured work; hashing libraries must not enter its timings.
    import ctypes
    dyld = ctypes.CDLL(None)
    dyld._dyld_get_image_name.restype = ctypes.c_char_p
    loaded = []
    for i in range(dyld._dyld_image_count()):
        raw = dyld._dyld_get_image_name(i)
        path = Path(raw.decode()) if raw else None
        if path and path.is_file() and any(token in path.name for token in
                ('Acts', 'G4', 'DDCore', 'DDG4', 'nODD', 'OpenDataDetector', 'libpython', 'libCore.', 'NativeTiming')):
            loaded.append({'path':str(path.resolve()),
                'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    (a.output/'loaded-libraries.json').write_text(json.dumps(loaded,indent=2)+'\n')
    if a.guard_check:
        shim=ctypes.CDLL(os.environ['NATIVE_TIMING_LIBRARY'])
        shim.materialProfileGuardChecks.restype=ctypes.c_char_p
        checks=json.loads(shim.materialProfileGuardChecks())
        (a.output/'guard-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
        assert all(checks.values()), checks
    if a.inventory or a.inventory_only:
        view = Path('/Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view')
        ROOT.gInterpreter.AddIncludePath(str(view/'include'))
        ROOT.gInterpreter.AddIncludePath(str(view/'include/Geant4'))
        ROOT.gInterpreter.Declare(Path(__file__).with_name('inventory.hpp').read_text())
        (a.output/'inventory.json').write_text(str(ROOT.materialProfileInventory())+'\n')


if __name__ == '__main__':
    main()
