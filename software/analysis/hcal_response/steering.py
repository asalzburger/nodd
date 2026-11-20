"""HCAL raw-deposit response PROTOTYPE with serial maps and worker audit."""
from DDSim.DD4hepSimulation import DD4hepSimulation
import os
import ROOT

# macOS plugin discovery does not reliably scan task-local .components files.
# Load the exact hash-bound geometry and observer libraries before compact parsing.
for variable in ("NODD_HCAL_GEOMETRY_LIBRARY", "NODD_HCAL_AUDIT_LIBRARY"):
    if ROOT.gSystem.Load(os.environ[variable]) < 0:
        raise RuntimeError("Cannot load bound library: " + variable)


def configure(kernel):
    import os
    import ROOT
    library = os.environ["NODD_HCAL_AUDIT_LIBRARY"]
    if ROOT.gSystem.Load(library) < 0:
        raise RuntimeError("Cannot load the bound HCAL audit library")
    if not ROOT.gInterpreter.Declare("void initializeHCALResponseMaps(const std::string&, unsigned long);"):
        raise RuntimeError("Cannot declare serial HCAL map initializer")

    def initialize():
        ROOT.initializeHCALResponseMaps(os.environ["NODD_HCAL_AUDIT"], int(os.environ["NODD_HCAL_EXPECTED_RAW_IDS"]))

    ROOT._hcal_response_initialize = initialize
    kernel.get().register_initialize(initialize)


SIM = DD4hepSimulation()
SIM.physics.setupUserPhysics(configure)
SIM.action.run = "nODDHCALResponseAudit/HCALResponseAudit"
SIM.random.enableEventSeed = True

SIM.action.event = "nODDHCALObserver/HCALObserver"
SIM.action.step = "nODDHCALStepObserver/HCALStepObserver"
