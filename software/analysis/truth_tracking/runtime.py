"""Portable campaign guards and native ROOT output inventory."""
import gzip
import json
import math
from pathlib import Path


def load_campaign(path):
    config = json.loads(Path(path).read_text())
    if config.get("schema_version") != 1 or config.get("status") != "PROTOTYPE":
        raise ValueError("Expected prototype campaign schema1")
    if config.get("particles_per_event") != 1 or config.get("vertex_mm") != [0., 0., 0.]:
        raise ValueError("Baseline requires exactly one origin particle per event")
    if not math.isfinite(config["field_Bz_T"]) or config["field_Bz_T"] == 0:
        raise ValueError("A finite nonzero constant Bz is required")
    for axis in ("eta_range", "phi_range_rad"):
        bounds = config[axis]
        if len(bounds) != 2 or not all(math.isfinite(x) for x in bounds) or bounds[0] >= bounds[1]:
            raise ValueError("Invalid sampling bounds")
    if config.get("randomize_charge") is not True:
        raise ValueError("Baseline requires randomized muon charge")
    digi = config["digitization"]
    if digi.get("long_strip_measured_coordinates") != 1:
        raise ValueError("Long strips require one measured coordinate per native face")
    if digi.get("digital") is not True or digi.get("threshold") != 0:
        raise ValueError("This baseline implements explicit ideal digital readout with zero threshold")
    if digi.get("component_digital") is not True or digi.get("drift") is not False or digi.get("diffusion") is not False:
        raise ValueError("Unsupported native geometric response settings")
    if config["truth_tracking"].get("particle_hypothesis") != "muon":
        raise ValueError("Baseline requires native muon particle hypothesis")
    training=config.get("error_training")
    if training and (training.get("simulation")!="fatras" or training.get("log_uniform_pt") is not True
            or len(training["pt_range_GeV"])!=2
            or not 0<training["pt_range_GeV"][0]<training["pt_range_GeV"][1]
            or training["seed"]==config["seed"]):
        raise ValueError("Error training requires independent Fatras seed and finite loguniform pT bounds")
    return config


def material_map(source, output):
    source, output = Path(source), Path(output)
    with gzip.open(source, "rb") as stream:
        payload = stream.read()
    # Invalid maps fail before native geometry construction.
    json.loads(payload)
    output.write_bytes(payload)
    return output


def root_inventory(ROOT, path):
    source = ROOT.TFile.Open(str(path))
    if not source or source.IsZombie():
        raise RuntimeError(f"Invalid ROOT output: {path}")
    result, cycles = {}, {}
    for key in source.GetListOfKeys():
        name, cycle = key.GetName(), int(key.GetCycle())
        if cycle <= cycles.get(name, -1):
            continue
        obj = key.ReadObj()
        if obj.InheritsFrom("TTree"):
            cycles[name] = cycle
            result[obj.GetName()] = {"entries": int(obj.GetEntries()),
                "branches": {b.GetName(): (b.GetClassName() or b.GetTitle())
                             for b in obj.GetListOfBranches()}}
    source.Close()
    return result
