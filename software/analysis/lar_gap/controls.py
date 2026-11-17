"""Exact saved-cell serial/MT control for the conditional LAr gap experiment."""
import argparse
import json
import math
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "software/analysis/lar_response"))
import transport as response_transport

COLLECTIONS = tuple(response_transport.COLLECTIONS)
sha = response_transport.sha


def compare_events(serial, parallel):
    if set(serial) != set(range(24)) or set(parallel) != set(range(24)):
        raise ValueError("Need exactly the same 24 unique saved event IDs")
    cells = dict.fromkeys(COLLECTIONS, 0)
    for event in range(24):
        if serial[event] != parallel[event]:
            raise ValueError(f"Serial/MT primary, cell, energy or position mismatch: event {event}")
        for name in COLLECTIONS:
            cells[name] += len(serial[event]["cells"][name])
    return cells


def read_events(path):
    import edm4hep  # noqa: F401; registers dictionaries
    from podio import root_io
    result = {}
    for frame in root_io.Reader(str(path)).get("events"):
        header, = frame.get("EventHeader")
        event = int(header.getEventNumber())
        if header.getRunNumber() != 0 or event in result:
            raise ValueError("Repeated event ID or unexpected run")
        primary, = [p for p in frame.get("MCParticles") if p.getGeneratorStatus() == 1]
        momentum = primary.getMomentum()
        vertex = primary.getVertex()
        observed = (int(primary.getPDG()), float(primary.getEnergy()),
                    *map(float, (momentum.x, momentum.y, momentum.z)),
                    *map(float, (vertex.x, vertex.y, vertex.z)))
        if observed[0] != 11 or observed[-3:] != (0., 0., 0.):
            raise ValueError("Not one origin electron")
        cells = {}
        for name in COLLECTIONS:
            rows = []
            for hit in frame.get(name):
                p = hit.getPosition()
                row = (int(hit.getCellID()), float(hit.getEnergy()),
                       float(p.x), float(p.y), float(p.z))
                if row[1] <= 0 or not all(map(math.isfinite, row[1:])):
                    raise ValueError("Invalid saved hit")
                rows.append(row)
            rows.sort()
            if len({r[0] for r in rows}) != len(rows):
                raise ValueError("Duplicate saved canonical cell")
            cells[name] = rows
        result[event] = dict(primary=observed, cells=cells)
    return result


def check_policy(receipt, threads):
    for key, expected in dict(events=24, skip=0, threads=threads,
                              seed=133812341, max_step_mm=5.).items():
        if receipt.get(key) != expected:
            raise ValueError("Unexpected serial/MT control policy: " + key)
    if receipt.get("exit_code") != 0 or receipt.get("disk_abort"):
        raise ValueError("Unsuccessful control transport")


def compare(sample, serial, parallel, output):
    if output.exists():
        raise ValueError("Refusing control-proof overwrite")
    manifest = json.loads((sample / "sample.json").read_text())
    response_transport.verify_hashes(sample, manifest["hashes"])
    bindings = {}
    for name, run, threads in (("serial", serial, 1), ("mt", parallel, 12)):
        receipt = json.loads((run / "receipt.json").read_text())
        proof = json.loads((run / "readback.json").read_text())
        check_policy(receipt, threads)
        if (receipt["sample_sha256"] != sha(sample / "sample.json") or
                proof.get("status") != "PASS" or proof.get("events") != 24 or
                proof["receipt_sha256"] != sha(run / "receipt.json") or
                proof["root_sha256"] != sha(run / "events.root") or
                proof["event_summary_sha256"] != sha(run / "event-summary.jsonl") or
                proof["sample"] != manifest):
            raise ValueError("Unbound serial/MT saved-data proof")
        response_transport.check_workers(proof["workers"], receipt)
        for file, expected in proof["worker_audit_sha256"].items():
            if Path(file).name != file or sha(run / "audit" / file) != expected:
                raise ValueError("Changed control worker evidence")
        bindings[name] = {key: sha(run / key) for key in
                          ("receipt.json", "readback.json", "events.root", "event-summary.jsonl")}
    cells = compare_events(read_events(serial / "events.root"),
                           read_events(parallel / "events.root"))
    result = dict(status="PASS", events=24, cells_by_collection=cells,
                  comparison="Exact saved primary and canonical cell IDs, per-cell energies and positions by event ID; ROOT output order unrestricted",
                  sample_sha256=sha(sample / "sample.json"),
                  comparator_sha256=sha(__file__), bindings=bindings)
    output.parent.mkdir(parents=True, exist_ok=True)
    response_transport.save(output, result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("sample", "serial", "mt", "output"):
        parser.add_argument("--" + key, type=Path, required=True)
    args = parser.parse_args()
    proof = compare(args.sample, args.serial, args.mt, args.output)
    print(json.dumps({key: proof[key] for key in ("status", "events", "cells_by_collection")}))
