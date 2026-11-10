"""Register the probe audit against the initialized Geant4 touchables."""
from DDSim.DD4hepSimulation import DD4hepSimulation


def configure(kernel):
    import os
    from pathlib import Path
    import ROOT
    import subprocess
    prefix = Path(subprocess.check_output(["geant4-config", "--prefix"], text=True).strip())
    ROOT.gInterpreter.AddIncludePath(str(prefix / "include/Geant4"))
    if not ROOT.gInterpreter.Declare(Path(os.environ["WEDGE_AUDIT_HEADER"]).read_text()):
        raise RuntimeError("Could not compile Geant4 touchable audit")

    def audit():
        ROOT.auditCombinedWedges(os.environ["WEDGE_AUDIT_DIRECTORY"])
        print("ECAL Geant4 touchable audit complete", flush=True)

    ROOT._wedge_audit_callback = audit
    kernel.get().register_initialize(audit)


SIM = DD4hepSimulation()
SIM.physics.setupUserPhysics(configure)
