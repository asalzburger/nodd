"""Collect a native hierarchy inventory after DDG4 initialization."""
from DDSim.DD4hepSimulation import DD4hepSimulation


def configure(kernel):
    import json
    import os
    from pathlib import Path
    import subprocess
    import ROOT
    repo = Path(os.environ["TRACKER_PROBE_REPO"])
    prefix = Path(subprocess.check_output(["geant4-config", "--prefix"], text=True).strip())
    ROOT.gInterpreter.AddIncludePath(str(prefix / "include/Geant4"))
    if not ROOT.gInterpreter.Declare((repo / "tools/material_recording_profile/inventory.hpp").read_text()):
        raise RuntimeError("Cannot compile the existing native inventory helper")

    def inventory():
        value = json.loads(str(ROOT.materialProfileInventory()))
        path = Path(os.environ["TRACKER_PROBE_OUTPUT"]) / "inventory.json"
        path.write_text(json.dumps(value, indent=2) + "\n")
        print("TRACKER_NATIVE_INVENTORY_DONE", flush=True)

    ROOT._tracker_inventory_callback = inventory
    kernel.get().register_initialize(inventory)


SIM = DD4hepSimulation()
SIM.physics.setupUserPhysics(configure)
