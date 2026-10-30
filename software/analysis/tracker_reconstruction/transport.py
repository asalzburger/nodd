"""Frozen Fatras/Geant4 scheduling for the isolated DES041 species benchmark.

``schedule`` returns JSON-compatible effective settings and an idempotent,
zero-argument cleanup callback. The caller must protect every operation after
scheduling, including further algorithm construction, with ``try/finally``.
Geant4 cases run in separate processes: finishing a persistent event loop does
not make native Geant4 safe to reconstruct concurrently or repeatedly.
"""
import hashlib
import importlib
import os
from pathlib import Path
import shutil
import subprocess


_DATASETS = (
    "G4NEUTRONHPDATA", "G4LEDATA", "G4LEVELGAMMADATA", "G4RADIOACTIVEDATA",
    "G4PARTICLEXSDATA", "G4PIIDATA", "G4REALSURFACEDATA", "G4SAIDXSDATA",
    "G4ABLADATA", "G4INCLDATA", "G4ENSDFSTATEDATA", "G4CHANNELINGDATA",
)


def _module_identity(module):
    filename = getattr(module, "__file__", None)
    if filename is None:
        return {"path": None, "sha256": None}
    path = Path(filename).resolve()
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def _geant4_environment():
    """Record only allowlisted dataset locations and the activated CLI version.

    Path existence is not dataset content verification. CLI identity does not
    by itself prove the version of a loaded library; runner hashes pin those.
    No toolkit setup, downloads or shared state mutation occurs here.
    """
    program = shutil.which("geant4-config")
    version = None
    if program is not None:
        try:
            result = subprocess.run([program, "--version"], capture_output=True,
                                    text=True, timeout=2, check=False)
            if result.returncode == 0:
                version = result.stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            pass
    return {"geant4_config": program, "geant4_config_version": version,
            "datasets": {name: {"path": os.environ.get(name),
                "directory_exists": Path(os.environ[name]).is_dir() if os.environ.get(name) else None}
                for name in _DATASETS},
            "dataset_check": "Environment locations/existence only; contents not verified"}


def schedule(seq, acts, detector, geometry, field, rnd, observer, config, events, level):
    """Schedule transport without any truth or topology selection.

    The only supported backends are ``config['simulation'] == 'fatras'`` or
    ``'geant4'``. This benchmark intentionally exposes no transport-cut override.
    Geant4 uses the existing native persistent lifecycle observer, not a new run
    manager implementation. A scheduling exception also invokes cleanup.
    """
    if not isinstance(config, dict) or config.get("simulation") not in ("fatras", "geant4"):
        raise ValueError("Require simulation 'fatras' or 'geant4'")
    if isinstance(events, bool) or not isinstance(events, int) or events <= 0:
        raise ValueError("Require a positive integer transport event count")
    if "transport" in config and config["transport"] != {}:
        raise ValueError("Transport overrides are unsupported in the frozen benchmark")
    backend = config["simulation"]
    if backend == "geant4" and config.get("geant4_run_mode", "persistent") != "persistent":
        raise ValueError("Geant4 reconstruction requires persistent lifecycle mode")
    simulation = importlib.import_module("acts.examples.simulation")
    common = {"inputParticles": "particles_generated", "outputParticles": "particles_simulated",
              "outputSimHits": "simhits", "rnd": rnd, "logLevel": level}
    settings = {"simulation": backend, "inputParticles": common["inputParticles"],
                "outputParticles": common["outputParticles"], "outputSimHits": common["outputSimHits"],
                "truth_selection": None, "simulation_helper": _module_identity(simulation)}
    if backend == "fatras":
        # 0.5 GeV is the unchanged native FatrasSimulation::Config default.
        simulation.addFatras(seq, geometry, field, **common,
                             enableInteractions=True, pMin=0.5 * acts.UnitConstants.GeV)
        settings.update(pMin_GeV=0.5, enableInteractions=True,
            generateHitsOnSensitive=True,
            interactions=["emScattering", "emEnergyLossIonisation", "emEnergyLossRadiation", "emPhotonConversion"],
            lifecycle="Native Fatras sequencer lifecycle; no persistent handle")
        return settings, lambda: None

    # Import registers the Geant4Handle Python type used by the observer binding.
    geant4 = importlib.import_module("acts.examples.geant4")
    if not hasattr(simulation, "__geant4Handle"):
        raise RuntimeError("Pinned ACTS addGeant4 persistent-handle interface unavailable")
    if simulation.__geant4Handle is not None:
        raise RuntimeError("A Geant4 helper handle already exists; use a fresh process")
    if not callable(getattr(observer, "persistent_handle", None)) or not callable(getattr(observer, "finish_persistent", None)):
        raise RuntimeError("Native persistent Geant4 lifecycle observer unavailable")
    settings.update(physicsList="FTFP_BERT", keepParticlesWithoutHits=True,
        recordHitsOfSecondaries=True, recordHitsOfCharged=True,
        recordHitsOfNeutrals=False, recordHitsOfPrimaries=True,
        killSecondaries=False, materialMappings=["Silicon", "pixel_Silicon"],
        volumeMappings=[], killVolume="trackingGeometry.highestTrackingVolume", killAfterTime_ns=25.,
        geant4_binding=_module_identity(geant4), lifecycle_observer=_module_identity(observer),
        environment=_geant4_environment(),
        lifecycle={"mode": "persistent", "expected_events": events,
            "event_contract": "One independent Geant4 event per ACTS event",
            "cleanup": "finish_persistent, clear helper reference and release adapter reference",
            "one_case_per_process": True})
    handle = observer.persistent_handle(events)
    simulation.__geant4Handle = handle

    def cleanup():
        nonlocal handle
        if handle is None:
            return
        active, handle = handle, None
        try:
            observer.finish_persistent(active)
        finally:
            # Do not overwrite another caller's handle if the invariant was
            # violated elsewhere. Native sequence/algorithm owners outlive this
            # callback until the caller releases the sequence or exits.
            if simulation.__geant4Handle is active:
                simulation.__geant4Handle = None

    try:
        simulation.addGeant4(seq, detector, geometry, field, **common,
            killVolume=geometry.highestTrackingVolume, killAfterTime=25 * acts.UnitConstants.ns,
            keepParticlesWithoutHits=True, recordHitsOfSecondaries=True,
            materialMappings=["Silicon", "pixel_Silicon"], volumeMappings=[],
            killSecondaries=False, physicsList="FTFP_BERT")
    except BaseException as error:
        try:
            cleanup()
        except BaseException as cleanup_error:
            error.add_note("Persistent Geant4 cleanup also failed: "
                           f"{type(cleanup_error).__name__}: {cleanup_error}")
        raise
    return settings, cleanup
