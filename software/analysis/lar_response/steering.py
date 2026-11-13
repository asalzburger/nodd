"""LAr raw-deposit response PROTOTYPE with explicit worker policy audit."""
from DDSim.DD4hepSimulation import DD4hepSimulation

SIM = DD4hepSimulation()
SIM.action.run = "nODDLArResponseAudit/LArResponseAudit"
SIM.random.enableEventSeed = True
