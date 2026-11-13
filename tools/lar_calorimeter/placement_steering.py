"""Initialize both volume-ID maps serially, then audit the placed LAr model."""
from DDSim.DD4hepSimulation import DD4hepSimulation


def configure(kernel):
    import os
    from pathlib import Path
    import subprocess
    import ROOT
    prefix = Path(subprocess.check_output(["geant4-config", "--prefix"], text=True).strip())
    ROOT.gInterpreter.AddIncludePath(str(prefix / "include/Geant4"))
    header = Path(os.environ["LAR_PLACE_AUDIT_HEADER"])
    if not ROOT.gInterpreter.Declare(header.read_text()):
        raise RuntimeError("Cannot compile placement audit")
    def audit():
        ROOT.auditLArPlacement(os.environ["LAR_PLACE_DIRECTORY"])
    ROOT._lar_placement_callback = audit
    kernel.get().register_initialize(audit)


SIM = DD4hepSimulation()
SIM.physics.setupUserPhysics(configure)
