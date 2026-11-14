"""Independent observer wrapper around the unchanged LAr response steering."""
import os
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from DDSim.DD4hepSimulation import DD4hepSimulation
from software.analysis.lar_response.steering import configure as original_configure


def configure(kernel):
    import ROOT
    original_configure(kernel)
    if ROOT.gSystem.Load(os.environ['NODD_LAR_OBSERVER_LIBRARY'])<0:
        raise RuntimeError('Cannot load bound independent observer library')


SIM=DD4hepSimulation()
SIM.physics.setupUserPhysics(configure)
SIM.action.run='nODDLArResponseAudit/LArResponseAudit'
SIM.random.enableEventSeed=True
SIM.action.step='nODDLArObservedStep/ObservedSteps'
SIM.action.event='nODDLArObservedEvent/ObservedEvents'
