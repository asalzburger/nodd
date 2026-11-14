"""Independent observer wrapper around the unchanged LAr response steering."""
import os
from pathlib import Path
import sys

repository=Path(os.environ['NODD_LAR_REPOSITORY']).resolve(strict=True)
if not (repository/'software/analysis/lar_response/steering.py').is_file():
    raise RuntimeError('Bound observer repository is unavailable')
sys.path.insert(0,str(repository))
from DDSim.DD4hepSimulation import DD4hepSimulation


def configure(kernel):
    import os
    import ROOT
    from software.analysis.lar_response.steering import configure as original_configure
    original_configure(kernel)
    if ROOT.gSystem.Load(os.environ['NODD_LAR_OBSERVER_LIBRARY'])<0:
        raise RuntimeError('Cannot load bound independent observer library')


SIM=DD4hepSimulation()
SIM.physics.setupUserPhysics(configure)
SIM.action.run='nODDLArResponseAudit/LArResponseAudit'
SIM.random.enableEventSeed=True
SIM.action.step='nODDLArObservedStep/ObservedSteps'
SIM.action.event='nODDLArObservedEvent/ObservedEvents'
