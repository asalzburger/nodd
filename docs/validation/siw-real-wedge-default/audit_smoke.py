"""Audit the three persisted electrons in the maintained tracker-plus-ECAL compact."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path

import edm4hep  # Load the generated ROOT classes before opening podio frames.
from podio import root_io


def run(directory, sensors):
    native = json.loads((directory / "native-transport-audit.json").read_text())
    if (native["maximum_abs_magnetic_field_tesla"] != 0
            or native["matched_ECAL_sensitive_step_mm"] != 5
            or set(native["audited_ECAL_roles"]) != {"barrel", "endcap"}):
        raise ValueError("Unexpected initialized transport")
    with sensors.open() as stream:
        volume_ids = {int(line.split("\t", 1)[0]) for line in stream}
    cases = [("barrel", .5, .123, 8, 0), ("positive", 2., .123, 9, 1), ("negative", -2., -.123, 9, 2)]
    result = []
    for run_number, (label, eta, phi, expected_system, expected_side) in enumerate(cases):
        reader = root_io.Reader(str(directory / f"{label}.root"))
        events = iter(reader.get("events"))
        event = next(events)
        if next(events, None) is not None:
            raise ValueError(f"Multiple smoke events in {label}")
        header, = event.get("EventHeader")
        primary, = (p for p in event.get("MCParticles") if p.getGeneratorStatus() == 1)
        momentum = primary.getMomentum()
        vertex = primary.getVertex()
        pt = math.hypot(momentum.x, momentum.y)
        effective = float(format(50*math.cosh(eta), ".6g"))
        if ((header.getRunNumber(), header.getEventNumber()) != (run_number, 0) or primary.getPDG() != 11
                or (vertex.x, vertex.y, vertex.z) != (0, 0, 0)
                or abs(math.hypot(momentum.x, momentum.y, momentum.z)-effective) > 1e-9
                or abs(math.asinh(momentum.z/pt)-eta) > 1e-12
                or abs(math.atan2(momentum.y, momentum.x)-phi) > 1e-12):
            raise ValueError(f"Unexpected primary in {label}")
        counts, energies = Counter(), Counter()
        for collection, system in (("BARRELHits", 8), ("EDGEHits", 9)):
            seen = set()
            for hit in event.get(collection):
                cell, energy = int(hit.getCellID()), float(hit.getEnergy())
                if ((cell & 255) != system or cell in seen or not math.isfinite(energy) or energy <= 0
                        or cell & ((1 << 30)-1) not in volume_ids):
                    raise ValueError(f"Invalid {collection} hit in {label}")
                seen.add(cell)
                key = system, (cell >> 8) & 3
                if system == 9 and hit.getPosition().z * (1 if key[1] == 1 else -1) <= 0:
                    raise ValueError(f"Endcap hit side differs from position in {label}")
                counts[key] += 1
                energies[key] += energy
        target = expected_system, expected_side
        if not counts[target] or any(energy > energies[target] for energy in energies.values()):
            raise ValueError(f"Dominant ECAL signal is outside aimed region in {label}")
        result.append(dict(case=label, eta=eta, phi_rad=phi, transverse_momentum_GeV=pt,
                           hits_by_system_side={f"{k[0]}:{k[1]}": count for k, count in counts.items()}))
    (directory / "readback.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("sensors", type=Path)
    args = parser.parse_args()
    run(args.directory, args.sensors)
