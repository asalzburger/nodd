"""Prepare independent high-statistics batches for the frozen staggered prototype.

Local DDSim EventHeader IDs restart in each batch; campaign IDs are the explicit
batch offset plus the local ID. Raw inputs and outputs are never overwritten.
"""
import argparse
import copy
import json
import math
from pathlib import Path
import random
import shutil
import subprocess

import angular_sample as original
from angular_sample import ELECTRON_MASS_GEV, ROOT, save, sha

INPUT_REVISION = "e9aabc83d3c8aa4127d1bcd824db0a134e69e7b0"
FROZEN_HASHES = {
    "detector.xml": "d78ecea5c5aa5173af54a4ce392994491eede936a7f4edb87d55bc72e69a0c2b",
    "materials.xml": "5091f0cbc2444b6ef481c2293ec99375e5eada82a84ab03be7a50f3b8375cee1",
}
GEOMETRY_LIBRARY_SHA256 = "c0098ae4b5e7a453f46d8d118a82ac6a9c6a57a219f2af641e1c4e653b1e1dab"
AUDIT_LIBRARY_SHA256 = "4185d1bab353fc1c6a46920b63aeb9c3daa1f1bd0548887e7b02bdc295bb56e4"
RUNNER_SHA256 = "8befa2030bbf538d727a3e33588fb40539b2ee3c03ecc6d9430a7cedc4a30f81"
STEERING_SHA256 = "67b8ccfd7822dc75052047d44013de3fbe3013824ba0e2874b72284fb31d2562"
SOURCE_MANIFEST_SHA256 = "45ea2e25b53d15fdccafd29f6a07a21902c3896659c1896718e9620d1ea5798e"
DEFAULT_BYTES_PER_EVENT = 1270000.0  # Rounded above the retained12.613GB/10k measurement.


def seed_pair(index, primary_seed, transport_seed):
    return primary_seed + 1009 * index, transport_seed + 104729 * index


def primary_records(events, seed, offset):
    rng = random.Random(seed)
    for event in range(events):
        energy, eta, phi = rng.uniform(10., 80.), rng.uniform(-3., 3.), rng.uniform(-math.pi, math.pi)
        p = math.sqrt(energy * energy - ELECTRON_MASS_GEV ** 2)
        momentum = [p * math.cos(phi) / math.cosh(eta), p * math.sin(phi) / math.cosh(eta), p * math.tanh(eta)]
        yield dict(event=event, campaign_event=offset + event, energy_GeV=energy,
                   eta=eta, phi=phi, momentum_GeV=momentum)


def verify_source(source):
    if sha(source / "sample.json") != SOURCE_MANIFEST_SHA256:
        raise ValueError("Require the retained frozen staggered production sample manifest")
    manifest = json.loads((source / "sample.json").read_text())
    for name, digest in FROZEN_HASHES.items():
        if manifest["hashes"].get(name) != digest or sha(source / name) != digest:
            raise ValueError("Changed frozen staggered geometry")
    for name, key in (("particles.HEPEvt", "input_sha256"), ("truth-input.jsonl", "truth_sha256")):
        if sha(source / name) != manifest[key]:
            raise ValueError("Changed retained source primary records")
    return manifest


def prepare(args):
    source, out = args.source.resolve(), args.output.resolve()
    prior = verify_source(source)
    if args.batch_events < 12 or args.batch_events > 10000 or min(args.training_events, args.validation_events) <= 0:
        raise ValueError("Require positive train/validation counts and12..10000 events per batch")
    if args.training_events % args.batch_events or args.validation_events % args.batch_events:
        raise ValueError("Train and validation sizes must be multiples of batch size")
    total = args.training_events + args.validation_events
    if not math.isfinite(args.bytes_per_event) or args.bytes_per_event <= 0 or not math.isfinite(args.reserve_gib) or args.reserve_gib < 0:
        raise ValueError("Invalid disk guard")
    free = shutil.disk_usage(out.parent if out.parent.exists() else source).free
    required = 2 * total * args.bytes_per_event + args.reserve_gib * 1024 ** 3
    if free < required:
        raise ValueError(f"Insufficient campaign disk budget: need{required:.0f}, free{free}; no batches created")
    old = {tuple(json.loads(line)["momentum_GeV"]) for line in (source / "truth-input.jsonl").read_text().splitlines()}
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    seeds, entries = set(), []
    n_batches = total // args.batch_events
    for index in range(n_batches):
        a, b = seed_pair(index, args.primary_seed, args.transport_seed)
        if a == b or a in seeds or b in seeds or a <= 0 or b <= 0 or max(a, b) >= 2 ** 31 or a == prior["input_seed"] or b == 133812341:
            raise ValueError("Primary/transport seeds must be fresh, positive, distinct and signed31bit")
        seeds.update((a, b))
    out.mkdir(parents=True, exist_ok=False)
    seen = set(old)
    for index in range(n_batches):
        split = "train" if index < args.training_events // args.batch_events else "validation"
        split_index = index if split == "train" else index - args.training_events // args.batch_events
        name = f"{split}-{split_index:03d}"
        target = out / "batches" / name / "input"
        target.mkdir(parents=True)
        for filename in FROZEN_HASHES:
            shutil.copyfile(source / filename, target / filename)
        primary_seed, transport_seed = seed_pair(index, args.primary_seed, args.transport_seed)
        offset = index * args.batch_events
        with (target / "particles.HEPEvt").open("w") as hep, (target / "truth-input.jsonl").open("w") as truth:
            for record in primary_records(args.batch_events, primary_seed, offset):
                key = tuple(record["momentum_GeV"])
                if key in seen:
                    raise ValueError("Repeated exact primary across retained source or campaign; partial evidence retained")
                seen.add(key)
                hep.write("1\n1 11 0 0 " + " ".join(f"{x:.17g}" for x in [*key, ELECTRON_MASS_GEV]) + "\n")
                truth.write(json.dumps(record, separators=(",", ":")) + "\n")
        manifest = copy.deepcopy(prior)
        manifest.update(source_revision=revision, events=args.batch_events, input_seed=primary_seed,
                        producer_sha256=sha(__file__), input_sha256=sha(target / "particles.HEPEvt"),
                        truth_sha256=sha(target / "truth-input.jsonl"), disk_free_bytes=shutil.disk_usage(out).free)
        manifest["campaign"] = dict(batch=name, batch_index=index, split=split, event_offset=offset,
             events=args.batch_events, global_event_range=[offset, offset + args.batch_events - 1],
             transport_seed=transport_seed, geometry_manifest_sha256=SOURCE_MANIFEST_SHA256,
             geometry_source_revision=prior["source_revision"], input_revision=INPUT_REVISION,
             local_identity="DDSim IDs restart at0; campaign_event=event_offset+local EventHeader ID",
             original_source_events_reused=False)
        save(target / "sample.json", manifest)
        entries.append(dict(batch=name, split=split, input=str(target.relative_to(out)),
                            events=args.batch_events, event_offset=offset, primary_seed=primary_seed,
                            transport_seed=transport_seed, sample_sha256=sha(target / "sample.json"),
                            input_sha256=manifest["input_sha256"], truth_sha256=manifest["truth_sha256"]))
        print(f"Prepared{name}: {args.batch_events} fresh primaries, campaign IDs{offset}..{offset+args.batch_events-1}", flush=True)
    campaign = dict(status="PROTOTYPE", source_revision=revision, input_revision=INPUT_REVISION,
        producer_sha256=sha(__file__), geometry_manifest_sha256=SOURCE_MANIFEST_SHA256,
        geometry_hashes=FROZEN_HASHES, geometry_library_sha256=GEOMETRY_LIBRARY_SHA256,
        audit_library_sha256=AUDIT_LIBRARY_SHA256, angular_runner_sha256=RUNNER_SHA256,
        angular_steering_sha256=STEERING_SHA256,
        training_events=args.training_events, validation_events=args.validation_events,
        events=total, batch_events=args.batch_events, threads=12, batches=entries,
        primary_seed_base=args.primary_seed, transport_seed_base=args.transport_seed,
        disk_plan=dict(free_bytes_before=free, bytes_per_event=args.bytes_per_event,
                       retention_multiplier=2, reserve_gib=args.reserve_gib, required_bytes=required),
        original_source_overlap_check="Exact momentum tuples disjoint from retained10k and all new batches; no old event reuse")
    save(out / "campaign.json", campaign)
    print(f"Prepared{total} events; campaign manifest {out / 'campaign.json'}", flush=True)


def load_batch(campaign_dir, name):
    campaign = json.loads((campaign_dir / "campaign.json").read_text())
    entry, = [e for e in campaign["batches"] if e["batch"] == name]
    sample = (campaign_dir / entry["input"]).resolve()
    if sha(sample / "sample.json") != entry["sample_sha256"]:
        raise ValueError("Changed batch sample manifest")
    manifest = json.loads((sample / "sample.json").read_text())
    if manifest["hashes"] != FROZEN_HASHES or manifest["campaign"]["transport_seed"] != entry["transport_seed"]:
        raise ValueError("Changed batch geometry/seed contract")
    for name, digest in FROZEN_HASHES.items():
        if sha(sample / name) != digest:
            raise ValueError("Changed batch geometry")
    for filename, key in (("particles.HEPEvt", "input_sha256"), ("truth-input.jsonl", "truth_sha256")):
        if sha(sample / filename) != manifest[key] or manifest[key] != entry[key]:
            raise ValueError("Changed batch primary records")
    return campaign, entry, sample


def run_batch(args):
    campaign_dir = args.campaign.resolve()
    campaign, entry, sample = load_batch(campaign_dir, args.batch)
    for path, digest in ((args.geometry_library, GEOMETRY_LIBRARY_SHA256), (args.audit_library, AUDIT_LIBRARY_SHA256),
                         (Path(original.__file__), RUNNER_SHA256),
                         (Path(original.__file__).with_name("angular_transport.py"), STEERING_SHA256)):
        if sha(path) != digest:
            raise ValueError(f"Changed frozen transport artifact: {path}")
    free = shutil.disk_usage(sample).free
    disk = campaign["disk_plan"]
    if free < 2 * entry["events"] * disk["bytes_per_event"] + disk["reserve_gib"] * 1024 ** 3:
        raise ValueError("Insufficient disk for complete batch; retained all earlier batches")
    original.run(argparse.Namespace(sample=sample, output=sample.parent / "run", events=entry["events"],
        skip=0, threads=12, seed=entry["transport_seed"], reserve_gib=disk["reserve_gib"],
        bytes_per_event=disk["bytes_per_event"], geometry_library=args.geometry_library,
        audit_library=args.audit_library))
    receipt = json.loads((sample.parent / "run" / "receipt.json").read_text())
    if receipt["events"] != entry["events"]:
        raise ValueError("Incomplete batch; do not treat partial campaign as complete")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="stage", required=True)
    a = sub.add_parser("prepare")
    a.add_argument("--source", type=Path, required=True); a.add_argument("--output", type=Path, required=True)
    a.add_argument("--training-events", type=int, default=100000); a.add_argument("--validation-events", type=int, default=20000)
    a.add_argument("--batch-events", type=int, default=10000)
    a.add_argument("--primary-seed", type=int, default=14410000); a.add_argument("--transport-seed", type=int, default=144812341)
    a.add_argument("--reserve-gib", type=float, default=30.); a.add_argument("--bytes-per-event", type=float, default=DEFAULT_BYTES_PER_EVENT)
    a = sub.add_parser("run-batch")
    a.add_argument("--campaign", type=Path, required=True); a.add_argument("--batch", required=True)
    a.add_argument("--geometry-library", type=Path, required=True); a.add_argument("--audit-library", type=Path, required=True)
    args = p.parse_args()
    (prepare if args.stage == "prepare" else run_batch)(args)


if __name__ == "__main__":
    main()
