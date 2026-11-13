"""LAr raw-deposit response PROTOTYPE with serial maps and worker audit."""
from DDSim.DD4hepSimulation import DD4hepSimulation


def configure(kernel):
    import os
    import ROOT
    library = os.environ["NODD_LAR_AUDIT_LIBRARY"]
    if ROOT.gSystem.Load(library) < 0:
        raise RuntimeError("Cannot load the bound LAr audit library")
    if not ROOT.gInterpreter.Declare("void initializeLArResponseMaps(const std::string&);"):
        raise RuntimeError("Cannot declare serial LAr map initializer")

    def initialize():
        ROOT.initializeLArResponseMaps(os.environ["NODD_LAR_AUDIT"])

    ROOT._lar_response_initialize = initialize
    kernel.get().register_initialize(initialize)


SIM = DD4hepSimulation()
SIM.physics.setupUserPhysics(configure)
SIM.action.run = "nODDLArResponseAudit/LArResponseAudit"
SIM.random.enableEventSeed = True
