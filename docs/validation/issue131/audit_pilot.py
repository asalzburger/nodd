"""Audit persisted truth and measure the timings of the four DDSim populations."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import subprocess

import edm4hep
import ROOT
from podio import root_io


def validate_file(path, index, sample):
    reader = root_io.Reader(str(path))
    cells = Counter()
    zero_events = 0
    errors = Counter()
    count = 0
    # The native /gun/momentumAmp command quantized each pilot value to six significant figures.
    effective_p = float(format(sample["p_GeV"], ".6g"))
    for count, frame in enumerate(reader.get("events"), start=1):
        header, = frame.get("EventHeader")
        assert (header.getRunNumber(), header.getEventNumber()) == (index, count - 1)
        primary, = [p for p in frame.get("MCParticles") if p.getGeneratorStatus() == 1]
        assert primary.getPDG() == 11
        p = primary.getMomentum()
        v = primary.getVertex()
        pt = math.hypot(p.x, p.y)
        eta = math.asinh(p.z / pt)
        phi = math.atan2(p.y, p.x)
        assert (v.x, v.y, v.z) == (0., 0., 0.)
        momentum = math.hypot(p.x, p.y, p.z)
        assert abs(momentum - effective_p) < 1e-9
        assert abs(primary.getEnergy() - math.hypot(effective_p, primary.getMass())) < 1e-9
        assert abs(eta - sample["eta"]) < 1e-12 and abs(phi - sample["phi"]) < 1e-12
        for key, got, expected in (
            ("pt_GeV", pt, 50.),
            ("eta", eta, sample["eta"]),
            ("phi_rad", phi, sample["phi"]),
            ("energy_GeV", primary.getEnergy(), math.hypot(sample["p_GeV"], primary.getMass())),
        ):
            error = abs(got - expected)
            errors[key] = max(errors[key], error)
        count_hits = 0
        for name, system in (("BARRELHits", 8), ("EDGEHits", 9)):
            hits = frame.get(name)
            ids = [int(hit.getCellID()) for hit in hits]
            assert len(ids) == len(set(ids))
            assert all(cell_id & 255 == system for cell_id in ids)
            assert all(math.isfinite(hit.getEnergy()) and hit.getEnergy() > 0 for hit in hits)
            cells[name] += len(ids)
            count_hits += len(ids)
        zero_events += count_hits == 0
    assert count == sample["events"]
    root = ROOT.TFile.Open(str(path), "READ")
    assert root and not root.IsZombie()
    tree = root.Get("events")
    assert tree and tree.InheritsFrom("TTree") and tree.GetEntries() == count
    compression = dict(algorithm=int(root.GetCompressionAlgorithm()), level=int(root.GetCompressionLevel()))
    collection_types = {name: str(type(frame.get(name)).__cpp_name__)
                        for name in ("MCParticles", "BARRELHits", "EDGEHits")}
    root.Close()
    with path.open("rb") as stream:
        root_sha256 = hashlib.file_digest(stream, "sha256").hexdigest()
    return dict(root_sha256=root_sha256, format="podio EDM4hep ROOT TTree", compression=compression,
                collection_types=collection_types, bytes_per_event=path.stat().st_size / count,
                events=count, cells_by_collection=dict(cells), zero_events=zero_events,
                bytes=path.stat().st_size, effective_p_GeV=effective_p, maximum_nominal_truth_error=dict(errors))


def main(directory):
    timing = json.loads((directory / "timing.json").read_text())
    for name in ("detector.xml", "materials.xml", "pilot.mac", "transport.log"):
        with (directory / name).open("rb") as stream:
            assert hashlib.file_digest(stream, "sha256").hexdigest() == timing["sha256"][name]
    native = json.loads((directory / "native-transport-audit.json").read_text())
    assert native["maximum_abs_magnetic_field_tesla"] == 0.
    assert native["matched_ECAL_sensitive_step_mm"] == 5.
    assert set(native["audited_ECAL_roles"]) == {"barrel", "endcap"}
    assert any(region["production_cuts_mm"] == [0.7] * 4 for region in native["regions"])
    begins = {}
    finishes = {}
    for line in (directory / "transport.log").read_text().splitlines():
        stamp = re.match(r"^\[\s*([0-9.]+)\]", line)
        if stamp is None:
            continue
        if match := re.search(r"Initializing event \d+\. Within run:(\d+) event 1\.", line):
            begins[int(match[1])] = float(stamp[1])
        if match := re.search(r"Finished run (\d+) after 25 events", line):
            finishes[int(match[1])] = float(stamp[1])
    assert timing["exit_code"] == 0 and not timing["macro_errors"]
    markers = timing["markers"]
    results = []
    for index, sample in enumerate(timing["samples"]):
        row = validate_file(directory / (sample["name"] + ".root"), index, sample)
        begin, end = (markers[f"ECAL_TIMING_{key}_{index}"] for key in ("BEGIN", "END"))
        assert begin <= begins[index] < finishes[index] <= end
        state_path = directory / f"random-state-{index}.json"
        row["native_rng"] = json.loads(state_path.read_text())
        row["native_rng_state_sha256"] = hashlib.sha256(Path(str(state_path) + ".state").read_bytes()).hexdigest()
        row.update(sample, run_seconds=end - begin, event_seconds=finishes[index] - begins[index],
                   begin_to_first_event_seconds=begins[index] - begin)
        row["seconds_per_event"] = row["event_seconds"] / row["events"]
        results.append(row)
    total_events = sum(row["events"] for row in results)
    total_bytes = sum(row["bytes"] for row in results)
    total_event_seconds = sum(row["event_seconds"] for row in results)
    assert total_events == 100
    report = dict(
        source_revision=timing["environment"]["source_revision"],
        started_at=timing["started_at"], ended_at=timing["ended_at"],
        environment=timing["environment"],
        geant4_datasets_after_run=subprocess.check_output(["geant4-config", "--check-datasets"], text=True).strip(),
        sha256=timing["sha256"],
        audit_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        native_transport_audit=native,
        seconds_per_event=total_event_seconds / total_events,
        event_loop_seconds=total_event_seconds,
        output_bytes=total_bytes, output_bytes_per_event=total_bytes / total_events,
        launch_to_first_beam_on_seconds=markers["ECAL_TIMING_BEGIN_0"],
        initialization_definition="DDSim child launch to first event-initialization message, includes Python, geometry, native audit compilation/execution and first-run physics setup; excludes export/build/Spack activation",
        event_loop_definition="Sum of first-event initialization to Finished-run message intervals / 100; includes transport and in-loop output; excludes run setup and final process teardown",
        output_definition="Sum of the four closed compressed ROOT file sizes / 100 persisted primaries; includes truth, hits, contributions and file metadata; no digitization or reconstruction",
        events=sum(row["events"] for row in results), groups=results,
        initialization_seconds=begins[0],
        wall_seconds=timing["elapsed_seconds"],
        cpu_seconds=timing["cpu_user_seconds"] + timing["cpu_system_seconds"],
        peak_rss_bytes=timing["peak_rss_bytes"],
        magnetic_field_tesla=native["maximum_abs_magnetic_field_tesla"],
    )
    (directory / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    if not __debug__:
        raise SystemExit("Run without Python optimization; event assertions are mandatory")
    main(Path(sys.argv[1]).resolve())
