#!/usr/bin/env python3
"""PROTOTYPE: record a fixed DD4hep compact with native material physics.

Use one fresh process per case; geometry/materials/regions/cuts/physics/actions
must stay immutable. The optional persistent handle retains native per-event
ACTS seeds and stepping, with one Geant4 event per ACTS event.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
START = time.perf_counter()


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--compact',type=Path,required=True)
    p.add_argument('--factory-dir',type=Path,required=True)
    p.add_argument('--native-module-dir',type=Path,required=True)
    p.add_argument('--run-mode',choices=('standard','persistent'),default='persistent')
    p.add_argument('--events',type=int,default=1000)
    p.add_argument('--tracks',type=int,default=100)
    p.add_argument('--seed',type=int,default=228)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if min(a.events,a.tracks)<=0 or a.seed<0:p.error('Require positive events/tracks and nonnegative seed')
    a.output=a.output.resolve()
    if a.output.exists():p.error('Output exists; select a fresh directory')
    a.output.mkdir(parents=True)
    settings=dict(events=a.events,tracks_per_event=a.tracks,seed=a.seed,
        eta=[-4,4],eta_uniform=True,phi_degrees=[0,360],vertex_mm=[0,0,0,0],
        threads=1,charge=0,pdg=0,momentum_GeV=[1,10],recordElementFractions=False,
        prePostStep=True,recalculateTotals=True,excludeMaterials=['Air','Vacuum'])
    metrics=dict(pid=os.getpid(),settings=settings,phases=[],events=[],run_mode=a.run_mode,
        compact=str(a.compact.resolve()),compact_sha256=sha(a.compact),
        materials_sha256=sha(a.compact.with_name('materials.xml')),
        steering_sha256=sha(__file__),source_revision=subprocess.check_output(
            ['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),
        preloaded_libraries=os.environ.get('DYLD_INSERT_LIBRARIES','').split(os.pathsep))
    def save():
        (a.output/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    previous=(START,time.process_time())
    def stamp(name):
        nonlocal previous
        now=(time.perf_counter(),time.process_time())
        metrics['phases'].append(dict(name=name,wall_s=now[0]-previous[0],cpu_s=now[1]-previous[1]))
        previous=now;save()
    import acts
    import acts.examples
    import acts.examples.geant4
    import acts.examples.hepmc3
    from acts.examples.nodd import DD4hepNoddDetector
    from acts.examples.root import RootMaterialTrackWriter
    import dd4hep
    import ROOT as root
    sys.path.insert(0,str(a.native_module_dir.resolve()))
    import nodd_material_recording_native as native
    metrics['native_module']=dict(path=native.__file__,sha256=sha(native.__file__),
        source_sha256=sha(ROOT/'software/source/ActsExamples/MaterialRecording/PersistentMaterial.cpp'))
    stamp('imports')
    factories=[]
    for name in ['nODDPixelBarrel','nODDBeamPipe','nODDShortStripBarrel','nODDShortStripEndcap','nODDLongStrip']:
        library=(a.factory_dir/('lib'+name+'.dylib')).resolve()
        if root.gSystem.Load(str(library))<0:raise RuntimeError('Factory load failed: '+str(library))
        factories.append(dict(path=str(library),sha256=sha(library)))
    metrics['factories']=factories
    detector=DD4hepNoddDetector(DD4hepNoddDetector.Config(
        xmlFileNames=[str(a.compact.resolve())],gen3=False,
        logLevel=acts.logging.WARNING,dd4hepLogLevel=acts.logging.WARNING))
    stamp('factories_and_dd4hep')
    level=acts.logging.INFO;u=acts.UnitConstants
    rnd=acts.examples.RandomNumbers(seed=a.seed)
    seq=acts.examples.Sequencer(events=a.events,numThreads=1,outputDir=str(a.output))
    generator=acts.examples.EventGenerator(level=level,generators=[acts.examples.EventGenerator.Generator(
        multiplicity=acts.examples.FixedMultiplicityGenerator(n=1),
        vertex=acts.examples.GaussianVertexGenerator(mean=acts.Vector4(0,0,0,0),stddev=acts.Vector4(0,0,0,0)),
        particles=acts.examples.ParametricParticleGenerator(pdg=acts.PdgParticle.eInvalid,
            charge=0,randomizeCharge=False,mass=0,p=(1*u.GeV,10*u.GeV),
            eta=(-4.,4.),phi=(0.,360*u.degree),numParticles=a.tracks,etaUniform=True))],randomNumbers=rnd)
    seq.addReader(generator)
    converter=acts.examples.hepmc3.HepMC3InputConverter(level=level,
        inputEvent=generator.config.outputEvent,outputParticles='particles_initial',
        outputVertices='vertices_initial',mergePrimaries=False)
    seq.addAlgorithm(converter)
    handle=native.persistent_handle(a.events) if a.run_mode=='persistent' else None
    kwargs=dict(level=level,detector=detector,randomNumbers=rnd,
        inputParticles=converter.config.outputParticles,outputMaterialTracks='material_tracks',
        recordElementFractions=False,excludeMaterials=['Air','Vacuum'])
    if handle is not None:kwargs['geant4Handle']=handle
    recorder=acts.examples.geant4.Geant4MaterialRecording(**kwargs)
    starts={}
    class Marker(acts.examples.IAlgorithm):
        def __init__(self,before):
            super().__init__('BeforeGeant4' if before else 'AfterGeant4',level);self.before=before
        def execute(self,ctx):
            now=(time.perf_counter(),time.process_time())
            if self.before:starts[ctx.eventNumber]=now
            else:
                begin=starts.pop(ctx.eventNumber)
                metrics['events'].append(dict(event=ctx.eventNumber,wall_s=now[0]-begin[0],cpu_s=now[1]-begin[1]))
                save()
            return acts.examples.ProcessCode.SUCCESS
    seq.addAlgorithm(Marker(True));seq.addAlgorithm(recorder);seq.addAlgorithm(Marker(False))
    seq.addWriter(RootMaterialTrackWriter(level=level,prePostStep=True,recalculateTotals=True,
        inputMaterialTracks='material_tracks',treeName='material_tracks',filePath=str(a.output/'tracks.root')))
    stamp('pipeline_construction')
    try:
        seq.run()
    except BaseException:
        if handle is not None:native.finish(handle,False)
        raise
    if handle is not None:
        native.finish(handle)
        metrics['lifecycle']=dict(native.report(handle))
        first_report=dict(native.report(handle));native.finish(handle)
        metrics['finish_idempotent']=first_report==dict(native.report(handle))
    stamp('sequencer_run')
    metrics.update(total_wall_s=time.perf_counter()-START,total_cpu_s=time.process_time(),
        peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,completed=True)
    save()
    assert sha(a.compact)==metrics['compact_sha256']
    assert sha(a.compact.with_name('materials.xml'))==metrics['materials_sha256']
    assert all(sha(row['path'])==row['sha256'] for row in factories)
    print(json.dumps(dict(completed=True,events=len(metrics['events']),mode=a.run_mode,
        wall_s=metrics['total_wall_s'],lifecycle=metrics.get('lifecycle'))),flush=True)


if __name__=='__main__':main()
