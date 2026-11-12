"""One ROOT pass for complete native hit audit and reconstructed-only features.

The output directory contains an angular_analyze-compatible audit ledger plus a
features/ directory with the original feature NPZ schema. Campaign event IDs in
NPZ are globally unique; EventHeader/local IDs remain explicit in the ledger.
"""
import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
import time

import numpy as np

from angular_sample import ROOT, save, sha
from highstat_sample import FROZEN_HASHES, GEOMETRY_LIBRARY_SHA256, AUDIT_LIBRARY_SHA256, RUNNER_SHA256
from staggered_features import FEATURE_NAMES, NATIVE as MASK_NATIVE, masks_from_xml

NATIVE = r'''
#include <edm4hep/SimCalorimeterHitCollection.h>
#include <edm4hep/MCParticleCollection.h>
#include <vector>
#include <unordered_set>
#include <cmath>
#include <cstdint>
#include <stdexcept>
namespace nodd_highstat {
std::vector<double> primary(const edm4hep::MCParticleCollection& particles) {
  std::vector<double> out;int n=0;
  for(const auto& p:particles) if(p.getGeneratorStatus()==1) {
    ++n;const auto v=p.getVertex();const auto m=p.getMomentum();
    if(p.getPDG()!=11||v.x!=0||v.y!=0||v.z!=0)throw std::runtime_error("Invalid electron primary/vertex");
    out={double(m.x),double(m.y),double(m.z),p.getEnergy()};
  }
  if(n!=1)throw std::runtime_error("Require exactly one generator primary");
  for(double x:out)if(!std::isfinite(x))throw std::runtime_error("Nonfinite primary");
  return out;
}
std::vector<double> cells(const edm4hep::SimCalorimeterHitCollection& hits,int system) {
  // Same moments/layer sums as staggered_features.cells. Energy uses compensated
  // summation to preserve the original math.fsum audit within roundoff.
  std::vector<double> out(59,0.);std::unordered_set<uint64_t> seen;
  double sum=0.,correction=0.;
  for(const auto& h:hits) {
    const uint64_t id=h.getCellID();const double e=h.getEnergy();const auto p=h.getPosition();
    const int layer=(id>>14)&63;
    if(!seen.insert(id).second||(id&255)!=uint64_t(system)||layer>=48||
       !(std::isfinite(e)&&e>0&&std::isfinite(p.x)&&std::isfinite(p.y)&&std::isfinite(p.z)))
      throw std::runtime_error("Invalid/repeated persisted ECAL cell");
    const double next=sum+e;
    correction+=(std::abs(sum)>=std::abs(e))?(sum-next)+e:(e-next)+sum;sum=next;
    out[1]+=e*p.x;out[2]+=e*p.y;out[3]+=e*p.z;
    out[4]+=e*p.x*p.x;out[5]+=e*p.y*p.y;out[6]+=e*p.z*p.z;
    out[7]+=e*p.x*p.y;out[8]+=e*p.x*p.z;out[9]+=e*p.y*p.z;
    out[10+layer]+=e;out[58]+=1.;
  }
  out[0]=sum+correction;
  for(double x:out)if(!std::isfinite(x))throw std::runtime_error("Nonfinite accumulated cell moment");
  return out;
}
}
'''


def validate_workers(run, receipt):
    workers = [json.loads(p.read_text()) for p in sorted((run / "audit").glob("worker-*.json"))]
    tids = {w["thread_id"] for w in workers}
    if receipt["threads"] > 1 and tids != set(range(receipt["threads"])):
        raise ValueError("Worker set differs")
    if len(workers) != receipt["threads"] or sum(w["events"] for w in workers) != receipt["events"]:
        raise ValueError("Worker event totals differ")
    for w in workers:
        if w["status"] != "complete" or w["maximum_abs_magnetic_field_tesla"] != 0 or set(w["sensitive_si"]) != {"BARREL", "EDGE"}:
            raise ValueError("Incomplete worker native audit")
        if not any(r["mm"] == [.7] * 4 for r in w["region_cuts"]):
            raise ValueError("Worker cuts differ")
        if any(r["max_step_mm"] != 5 or r["Birks_mm_per_MeV"] != 0 for r in w["sensitive_si"].values()):
            raise ValueError("Worker ECAL response/step policy differs")
    return workers


def validate_inputs(run, sample):
    receipt = json.loads((run / "receipt.json").read_text())
    manifest = json.loads((sample / "sample.json").read_text())
    if receipt["exit_code"] or receipt["disk_abort"] or receipt["sample_sha256"] != sha(sample / "sample.json"):
        raise ValueError("Incomplete or changed transport")
    if receipt["geometry_library_sha256"] != GEOMETRY_LIBRARY_SHA256 or receipt["audit_library_sha256"] != AUDIT_LIBRARY_SHA256:
        raise ValueError("Transport used different native libraries")
    if receipt["runner_sha256"] != RUNNER_SHA256:
        raise ValueError("Transport used a different runner")
    for name, digest in FROZEN_HASHES.items():
        if manifest["hashes"].get(name) != digest or sha(sample / name) != digest:
            raise ValueError("Changed frozen geometry input")
    for name, key in (("particles.HEPEvt", "input_sha256"), ("truth-input.jsonl", "truth_sha256")):
        if sha(sample / name) != manifest[key]:
            raise ValueError("Changed input primary records")
    expected = [json.loads(line) for line in (sample / "truth-input.jsonl").read_text().splitlines()]
    if len(expected) != manifest["events"] or [r["event"] for r in expected] != list(range(len(expected))):
        raise ValueError("Invalid local input identity ledger")
    if receipt["skip"] < 0 or receipt["events"] <= 0 or receipt["skip"] + receipt["events"] > len(expected):
        raise ValueError("Invalid transported event range")
    if "campaign" in manifest:
        c = manifest["campaign"]
        if receipt["skip"] != 0 or receipt["events"] != manifest["events"] or receipt["seed"] != c["transport_seed"] or receipt["threads"] != 12:
            raise ValueError("Changed or incomplete campaign batch configuration")
        if [r.get("campaign_event") for r in expected] != list(range(c["event_offset"], c["event_offset"] + len(expected))):
            raise ValueError("Invalid campaign identity ledger")
    return receipt, manifest, expected, validate_workers(run, receipt)


def verify_primary(values, ref):
    px, py, pz, energy = map(float, values)
    pt = math.hypot(px, py)
    if not pt > 0:
        raise ValueError("Primary has undefined direction")
    eta, phi = math.asinh(pz / pt), math.atan2(py, px)
    errors = dict(momentum_GeV=max(abs(a - b) for a, b in zip((px, py, pz), ref["momentum_GeV"])),
                  energy_GeV=abs(energy - ref["energy_GeV"]), eta=abs(eta - ref["eta"]),
                  phi=abs((phi - ref["phi"] + math.pi) % (2 * math.pi) - math.pi))
    if any(errors[k] > tolerance for k, tolerance in (("momentum_GeV", 1e-7), ("energy_GeV", 1e-7), ("eta", 1e-9), ("phi", 1e-9))):
        raise ValueError(f"Saved primary differs from input: {errors}")
    if not 10 <= energy <= 80 or not -3 <= eta <= 3:
        raise ValueError("Saved primary outside requested phase space")
    return energy, eta, phi, errors


def reconstructed(barrel, edge, native):
    total = barrel + edge
    feature = np.zeros(len(FEATURE_NAMES))
    result = dict(feature=feature, valid=False, eta=0., phi=0., region=0)
    if total[0] <= 0:
        return result
    centre = total[1:4] / total[0]
    radius, norm = math.hypot(centre[0], centre[1]), np.linalg.norm(centre)
    if radius <= 1e-8 or norm <= 1e-8:
        return result
    eta, phi = math.asinh(centre[2] / radius), math.atan2(centre[1], centre[0])
    fraction = barrel[0] / total[0]
    exposure = list(native.probe(eta, phi, fraction))
    direction = centre / norm
    moment = np.array([[total[4], total[7], total[8]], [total[7], total[5], total[9]],
                       [total[8], total[9], total[6]]]) / total[0]
    lateral = math.sqrt(max(0., np.trace(moment) - direction @ moment @ direction))
    period = math.pi / 8
    delta = (phi + period / 2) % period - period / 2
    seam_distance = radius * math.sin(period / 2 - abs(delta))
    feature[:] = [abs(eta), *exposure, math.exp(-.5 * (seam_distance / 22) ** 2),
                  total[10:26].sum() / total[0], total[42:58].sum() / total[0],
                  min(fraction, 1 - fraction), lateral / 22]
    result.update(valid=True, eta=eta, phi=phi, region=int(fraction < .5))
    return result


def declare_native(R):
    if not hasattr(R, "nodd_staggering") and not R.gInterpreter.Declare(MASK_NATIVE):
        raise RuntimeError("Native mask compilation failed")
    if not hasattr(R, "nodd_highstat") and not R.gInterpreter.Declare(NATIVE):
        raise RuntimeError("Native audit compilation failed")


def build_masks(R, sample):
    geometry = masks_from_xml(sample / "detector.xml")
    native = R.nodd_staggering.Masks()
    for section, layers in enumerate(geometry):
        for layer, entry in enumerate(layers):
            native.plane(section, layer, entry["plane_mm"])
            for p in entry["polygons"]:
                native.add(section, layer, R.std.vector("double")([v[0] for v in p]), R.std.vector("double")([v[1] for v in p]))
    return geometry, native


def extract(args):
    import ROOT as R
    import edm4hep
    from podio import root_io
    start = time.monotonic()
    run, sample, output = args.run.resolve(), args.sample.resolve(), args.output.resolve()
    receipt, manifest, expected, workers = validate_inputs(run, sample)
    if output.exists():
        raise ValueError("Refusing analysis overwrite")
    declare_native(R)
    geometry, masks = build_masks(R, sample)
    ids = set(range(receipt["skip"], receipt["skip"] + receipt["events"]))
    n, offset = receipt["events"], receipt["skip"]
    feature = np.zeros((n, len(FEATURE_NAMES)))
    signal, response, energy, eta, phi, rec_eta, rec_phi = [np.zeros(n) for _ in range(7)]
    region, valid = np.zeros(n, dtype=np.int64), np.zeros(n, dtype=bool)
    layers = np.zeros((n, 48))
    seen, cells = set(), dict(BARRELHits=0, EDGEHits=0)
    errors = dict(momentum_GeV=0., energy_GeV=0., eta=0., phi=0.)
    root = run / "events.root"
    before = root.stat()
    f = R.TFile.Open(str(root), "READ")
    if not f or f.IsZombie() or not f.Get("events") or f.Get("events").GetEntries() != n:
        raise ValueError("ROOT event count mismatch")
    compression = dict(algorithm=int(f.GetCompressionAlgorithm()), level=int(f.GetCompressionLevel()))
    f.Close()
    output.mkdir(parents=True, exist_ok=False)
    features_dir = output / "features"
    features_dir.mkdir()
    with (output / "event-summary.jsonl").open("w") as stream:
        for frame in root_io.Reader(str(root)).get("events"):
            header, = frame.get("EventHeader")
            event = int(header.getEventNumber())
            if int(header.getRunNumber()) != 0 or event not in ids or event in seen:
                raise ValueError("Unexpected/repeated event identity")
            seen.add(event)
            i = event - offset
            e, et, ph, er = verify_primary(R.nodd_highstat.primary(frame.get("MCParticles")), expected[event])
            for key, value in er.items():
                errors[key] = max(errors[key], value)
            b = np.asarray(list(R.nodd_highstat.cells(frame.get("BARRELHits"), 8)))
            d = np.asarray(list(R.nodd_highstat.cells(frame.get("EDGEHits"), 9)))
            total = b + d
            energies = dict(BARRELHits=float(b[0]), EDGEHits=float(d[0]))
            counts = dict(BARRELHits=int(b[58]), EDGEHits=int(d[58]))
            s = math.fsum(energies.values())
            signal[i], response[i], energy[i], eta[i], phi[i] = s, s / e, e, et, ph
            layers[i] = total[10:58]
            for key, value in counts.items():
                cells[key] += value
            r = reconstructed(b, d, masks)
            feature[i], valid[i], region[i], rec_eta[i], rec_phi[i] = r["feature"], r["valid"], r["region"], r["eta"], r["phi"]
            row = dict(event=event, energy_GeV=e, eta=et, phi=ph, signal_GeV=s,
                       response=s / e, energies_GeV=energies, counts=counts)
            if "campaign_event" in expected[event]:
                row["campaign_event"] = expected[event]["campaign_event"]
            stream.write(json.dumps(row, separators=(",", ":"), allow_nan=False) + "\n")
            if len(seen) % 1000 == 0:
                print(f"Native audited/reconstructed{len(seen)}/{n} events in{time.monotonic()-start:.1f}s", flush=True)
    if seen != ids or not all(np.all(np.isfinite(a)) for a in (feature, signal, response, energy, eta, phi, layers, rec_eta, rec_phi)):
        raise ValueError("Incomplete/nonfinite persisted event/features")
    root_digest = sha(root)
    after = root.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError("ROOT file changed during audit")
    shutil.copyfile(run / "receipt.json", output / "receipt.json")
    proof = dict(status="PASS", events=n, event_ids=dict(min=min(ids), max=max(ids)),
        identity_order="verified by local event ID; physical output order unrestricted", cells_by_collection=cells,
        maximum_input_errors=errors, compression=compression, root_sha256=root_digest,
        event_summary_sha256=sha(output / "event-summary.jsonl"), receipt_sha256=sha(output / "receipt.json"),
        audit_sha256=sha(__file__), sample=manifest, worker_events={str(w["thread_id"]): w["events"] for w in workers}, workers=workers,
        native_checks="Cell ID uniqueness within each event/collection; system; finite positive deposit; finite position; layer0..47; exactly one origin electron; exact primary/ID/worker/input checks",
        source_revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip())
    save(output / "readback.json", proof)
    event_ids = np.array([expected[i].get("campaign_event", i) for i in range(offset, offset + n)], dtype=np.int64)
    np.savez_compressed(features_dir / "features.npz", features=feature, signal=signal, response=response, energy=energy,
        eta=eta, phi=phi, region=region, valid_axis=valid, reconstructed_eta=rec_eta, reconstructed_phi=rec_phi,
        layer_signal=layers, event=event_ids)
    save(features_dir / "masks.json", geometry)
    save(features_dir / "receipt.json", dict(status="PASS", events=n, cell_hits=sum(cells.values()), valid_axes=int(valid.sum()),
        zero_signals=int(np.count_nonzero(signal == 0)), feature_names=FEATURE_NAMES,
        inference_inputs="Persisted cell energies/positions/IDs and fixed physical masks only; no truth energy/direction",
        mask_probe="Gaussian transverse widths5.5/11/22mm,5x5 samples; fixed longitudinal Gaussian centre16,width8layers; analysis probes only",
        feature_sha256=sha(features_dir / "features.npz"), masks_sha256=sha(features_dir / "masks.json"), producer_sha256=sha(__file__),
        feature_recipe_sha256=sha(Path(__file__).with_name("staggered_features.py")),
        geometry_helper_sha256=sha(Path(__file__).with_name("untiled_geometry.py")), source_revision=proof["source_revision"],
        readback_sha256=sha(output / "readback.json"), root_sha256=root_digest, sample_sha256=sha(sample / "sample.json"),
        compact_sha256=sha(sample / "detector.xml"), event_identity="Campaign-global IDs when campaign present; otherwise original local IDs",
        campaign=manifest.get("campaign"), wall_seconds=time.monotonic() - start))
    print(f"PASS: {n} events, {sum(cells.values())} cells, {valid.sum()} axes; {time.monotonic()-start:.1f}s", flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", type=Path, required=True); p.add_argument("--sample", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    extract(p.parse_args())


if __name__ == "__main__":
    main()
