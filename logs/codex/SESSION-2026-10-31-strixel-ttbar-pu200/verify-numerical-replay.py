"""One-time DES042 numerical regression gate, before campaign resume."""
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "software/analysis/strixel_ttbar"))
import campaign


def read(path):
    return json.loads(Path(path).read_text())


def eligible(state):
    x, y, z = state["direction"]
    transverse = math.hypot(x, y)
    eta = math.asinh(z / transverse) if transverse else math.copysign(math.inf, z)
    position = state["position4"]
    return (state["charge"] != 0 and state["p_GeV"] * transverse >= 1
            and abs(eta) <= 3 and math.hypot(*position[:2]) <= 24
            and abs(position[2]) <= 1000)


def main():
    journal = Path(__file__).resolve().parent
    directory = ROOT / "build/strixel-ttbar-production-v2"
    expected = read(directory / "campaign-plan.json")
    assert expected["source_revision"] == "250a211ff71be2ce7339cc043766f0d839470411"
    assert expected["source_sha256"] == campaign.source_identity()
    sample = directory / "sample"
    report = campaign.report_check(sample, expected)
    assert report["events"] == 100 and report["seed"] == 153042
    assert all(report["postrun_immutability"].values())
    assert not (sample / "native-fpe-diagnostic.json").exists()
    for field in ("all_events_retained", "all_201_interactions_verified",
                  "all_201_full_unfiltered_generated_origins_verified"):
        assert report["sample_audit"][field], field

    reference = read(journal / "failed-sample-inventory.json")
    failed = ROOT / "build/strixel-ttbar-production/sample"
    attempt = read(journal / "production-attempt-01.json")
    assert campaign.sha256(failed / "run-report.json") == attempt["run_report_sha256"]
    assert read(failed / "run-report.json")["outcome"] == "failed"
    manifest = read(sample / "sample-manifest.json")
    assert [r["event"] for r in manifest["event_rows"]] == list(range(100))
    assert [r["event"] for r in reference["event_rows"]] == list(range(100))
    rows = []
    for old, current in zip(reference["event_rows"], manifest["event_rows"]):
        event = old["event"]
        name = f"sample/event{event:06d}.json.gz"
        observed = campaign.sha256(sample / name)
        assert campaign.sha256(failed / name) == old["sha256"], event
        assert observed == old["sha256"] == current["file_sha256"], event
        assert current["counts"] == old["counts"], event
        rows.append({"event": event, "sha256": observed,
                     "byte_identical_to_preserved_attempt": True})

    audit = read(sample / "transport-failures.json")
    assert [r["event"] for r in audit["events"]] == list(range(100))
    losses = []
    checked_events = []
    for item in audit["events"]:
        if not item["failures"]:
            continue
        event = item["event"]
        with gzip.open(sample / f"sample/event{event:06d}.json.gz", "rt") as stream:
            payload = json.load(stream)
        generated = {tuple(p["initial"]["id"]): p["initial"] for p in payload["generated"]}
        origins = {tuple(p["id"]): p for p in payload["labels"]}
        simulated = {tuple(p["initial"]["id"]) for p in payload["simulated"]}
        missing = [list(pid) for pid, state in generated.items() if eligible(state) and pid not in simulated]
        assert not missing, (event, missing)
        checked_events.append(event)
        for failure in item["failures"]:
            state = failure["initial_state"]
            pid = tuple(state["id"])
            is_generated = pid in generated
            if is_generated:
                for key in ("id", "pdg", "charge", "mass_GeV", "position4", "direction", "p_GeV"):
                    assert state[key] == generated[pid][key], (event, pid, key)
            assert pid not in simulated
            assert not any(tuple(hit["particle_id"]) == pid for hit in payload["hits"])
            loss = {"event": event, "initial_state": state,
                    "initial_pt_GeV": state["p_GeV"] * math.hypot(*state["direction"][:2]),
                    "is_generated": is_generated,
                    "headline_eligible_generated": is_generated and eligible(generated[pid]),
                    "origin": origins.get(pid), "error_value": failure["error_value"],
                    "error_message": failure["error_message"]}
            losses.append(loss)
    assert len(losses) == 6
    assert not any(loss["headline_eligible_generated"] for loss in losses)
    result = {"status": "PASS", "source_revision": expected["source_revision"],
              "verifier_sha256": campaign.sha256(__file__), "events": 100,
              "all_native_payloads_byte_identical": True,
              "active_fatras_sequencer_completed": True,
              "original_failed_attempt_remains_invalid": True,
              "sample_report_sha256": campaign.sha256(sample / "run-report.json"),
              "failed_report_sha256": attempt["run_report_sha256"],
              "reference_inventory_sha256": campaign.sha256(journal / "failed-sample-inventory.json"),
              "native_module_sha256": report["isolated_fatras_provenance"]["module_sha256"],
              "counts": reference["counts"], "event_payloads": rows,
              "failure_audit_sha256": campaign.sha256(sample / "transport-failures.json"),
              "failure_audit_event_coverage": 100, "transport_failed_particles": losses,
              "affected_event_missing_eligible_generated_check": checked_events,
              "qualification": "Six particle transport losses retained; missing background hits can affect occupancy and fake rates. No event, cut or propagation-limit changes."}
    output = ROOT / "docs/validation/DES-042/ttbar-pu200/numerical-replay.json"
    with output.open("x") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    with (output.parent / "transport-failures.json").open("xb") as stream:
        stream.write((sample / "transport-failures.json").read_bytes())
    print(json.dumps({"status": "PASS", "events": 100, "byte_identical": 100,
                      "transport_losses": len(losses), "headline_eligible_losses": 0}))


if __name__ == "__main__":
    main()
