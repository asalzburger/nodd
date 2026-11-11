"""12-thread-capable PR133 ECAL transport with a per-worker native audit."""
from DDSim.DD4hepSimulation import DD4hepSimulation

SIM = DD4hepSimulation()
SIM.action.run = "nODDAngularAudit/AngularAudit"
SIM.random.enableEventSeed = True
