#!/usr/bin/env python3
"""Actual native nODD/zero-field-ODD diagnostics and common-scale comparisons.

ROOT inputs and cell/event diagnostics stay local. Public output contains only
population moments, histograms, event-bootstrap intervals and covariance.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time
import xml.etree.ElementTree as ET

import numpy as np

from digitized_response import basic, histogram, covariance, uncertainty, read_events
from nodd_generate import ROOT, PROTOCOL, referenced_files, sha, save, verify

MIP = .00014875
STAGES = ["raw", "off", "on"]
MODES = [dict(name="off", pair_energy_eV=0., noise_MIP=0.),
         dict(name="on", pair_energy_eV=3.6, noise_MIP=.13)]
LOADED_SOURCE = Path(__file__).read_bytes()
ANALYSIS_NOTES = ROOT / 'docs/validation/issue117/nodd-digitization-analysis-notes.md'


def expected_configuration(index, sample, manifest):
    return dict(mip_energy_GeV=MIP, threshold_MIP=.6, dynamic_range_MIP=2500.,
                seed=125500+100*index, collections=manifest['geometries'][sample['geometry']]['collections'],
                modes=MODES, save_cells=True)


def bind_configuration(receipt, config, expected, input_sha256):
    if (config != expected or receipt['identity']['configuration'] != expected
            or receipt['identity']['input_sha256'] != input_sha256):
        raise ValueError('Native configuration/input differs from the frozen execution identity')


def ordered_samples(args):
    manifest = verify(args.transport_manifest.parent)
    registration = args.transport_manifest.parent / 'plugin-registration-audit.json'
    proof = json.loads(registration.read_text())
    for name, digest in proof['immutable'].items():
        if sha(name) != digest:
            raise ValueError('Executed plugin registration changed')
    data = json.loads(args.samples.read_text())
    if data["manifest_sha256"] != sha(args.transport_manifest):
        raise ValueError("Generation manifest identity changed")
    executed = {}
    for artifact in data["receipts"]:
        path = Path(artifact["path"])
        if sha(path) != artifact["sha256"]:
            raise ValueError("Closed transport receipt changed")
        receipt = json.loads(path.read_text())
        if receipt["exit_code"] or not receipt.get("all_inputs_verified"):
            raise ValueError("Incomplete/failed transport group")
        for name, key in (("commands.mac", "macro_sha256"), ("producer.py", "producer_sha256"),
                          ("steering.py", "steering_sha256"), ("transport.log", "log_sha256"),
                          ("native-transport-audit.json", "native_transport_audit_sha256")):
            if sha(path.parent / name) != receipt[key]:
                raise ValueError("Closed transport evidence changed")
        executed.update({(r["geometry"], r["id"]): r for r in receipt["samples"]})
        for sample in receipt['samples']:
            if (sha(sample['rng_audit_path']) != sample['rng_audit_sha256']
                    or sha(sample['rng_audit_path']+'.state') != sample['rng_state_sha256']):
                raise ValueError("Actual transport RNG audit changed")
    indexed = {(r["geometry"], r["id"]): r for r in data["samples"]}
    if indexed != executed:
        raise ValueError("Indexed samples differ from their executed receipts")
    samples = [indexed[(r["geometry"], r["id"])] for r in manifest["samples"]]
    if len(samples) != len(indexed):
        raise ValueError("Unexpected population inventory")
    for sample in samples:
        expected = next(r for r in manifest["samples"] if (r["geometry"], r["id"]) == (sample["geometry"], sample["id"]))
        if any(sample[key] != value for key, value in expected.items()):
            raise ValueError("Executed sample differs from the frozen population")
        if sample["exit_code"] or sha(sample["path"]) != sample["sha256"]:
            raise ValueError("Changed/failed raw input")
    return manifest, samples


def run(args):
    manifest, samples = ordered_samples(args)
    args.work.mkdir(parents=True, exist_ok=True)
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    def execute(item):
        index, sample = item
        directory = args.work / (sample["geometry"] + "-" + sample["id"])
        directory.mkdir(exist_ok=True)
        output = directory / "diagnostics.jsonl"
        receipt_path = directory / "execution.json"
        config = expected_configuration(index, sample, manifest)
        identity = dict(input_sha256=sample["sha256"], binary_sha256=sha(args.binary),
                        backend_sha256=sha(args.backend), configuration=config)
        if receipt_path.exists():
            receipt = json.loads(receipt_path.read_text())
            if receipt["identity"] != identity or receipt["exit_code"] or sha(output) != receipt["output_sha256"]:
                raise ValueError("Existing native execution is changed/failed")
        else:
            if output.exists():
                raise ValueError("Unreceipted diagnostics; choose a fresh work directory")
            save(directory / "config.json", config)
            (directory / "producer.py").write_bytes(LOADED_SOURCE)
            command = [str(args.binary.resolve()), sample["path"], str((directory / "config.json").resolve()),
                       str(output.resolve()), str(args.backend.resolve())]
            started = time.monotonic()
            with (directory / "native.log").open("w") as log:
                result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            receipt = dict(identity=identity, command=command, exit_code=result.returncode,
                           source_commit=revision, producer_sha256=hashlib.sha256(LOADED_SOURCE).hexdigest(),
                           protocol_sha256=sha(PROTOCOL), elapsed_seconds=time.monotonic()-started,
                           analysis_notes_sha256=sha(ANALYSIS_NOTES),
                           config_sha256=sha(directory / "config.json"), log_sha256=sha(directory / "native.log"),
                           output_sha256=sha(output) if output.exists() else None)
            save(receipt_path, receipt)
            if result.returncode:
                raise RuntimeError("Native diagnostics failed: " + str(directory))
        print(sample["geometry"], sample["id"], "native exit0", flush=True)
        return dict(kind=sample["kind"], geometry=sample["geometry"], sample=sample,
                    diagnostics=str(output.resolve()), directory=str(directory.resolve()), receipt=receipt)
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        executed = list(pool.map(execute, enumerate(samples)))
    save(args.work / "runs.json", executed)


def verify_runs(args):
    manifest, samples = ordered_samples(args)
    runs = json.loads((args.work / "runs.json").read_text())
    if [r["sample"] for r in runs] != samples:
        raise ValueError("Native population identity/order changed")
    for index, row in enumerate(runs):
        if any(row[key] != row["sample"][key] for key in ("geometry", "kind")):
            raise ValueError("Native geometry/population labels differ from the bound sample")
        directory = Path(row["directory"])
        receipt = json.loads((directory / "execution.json").read_text())
        if receipt != row["receipt"] or receipt["exit_code"]:
            raise ValueError("Native receipt changed")
        config = json.loads((directory/'config.json').read_text())
        bind_configuration(receipt, config, expected_configuration(index,row['sample'],manifest),row['sample']['sha256'])
        if receipt['analysis_notes_sha256'] != sha(ANALYSIS_NOTES):
            raise ValueError('Pre-analysis clarification changed after execution')
        for name, key in (("config.json", "config_sha256"), ("native.log", "log_sha256"), ("producer.py", "producer_sha256")):
            if sha(directory / name) != receipt[key]:
                raise ValueError("Native execution evidence changed")
        if sha(args.backend) != receipt["identity"]["backend_sha256"] or sha(args.binary) != receipt["identity"]["binary_sha256"]:
            raise ValueError("Executed native binary identity changed")
        historical = subprocess.check_output(["git", "show", receipt["source_commit"]+":software/analysis/calorimeter_digitization/nodd_response.py"], cwd=ROOT)
        if hashlib.sha256(historical).hexdigest() != receipt["producer_sha256"]:
            raise ValueError("Native producer does not match its executed source commit")
        if receipt["protocol_sha256"] != sha(PROTOCOL):
            raise ValueError("Executed scientific protocol changed")
        read_events(row)
    return manifest, runs


def array_events(events):
    x = np.array([[e["raw_GeV"], e["modes"]["off"]["energy_GeV"],
                   e["modes"]["on"]["energy_GeV"]] for e in events], dtype=float)
    if not np.isfinite(x).all() or np.any(x < 0):
        raise ValueError("Nonfinite/negative summed response")
    return x


def ratio(a, b):
    result = np.full_like(np.asarray(a, dtype=float), np.nan)
    return np.divide(a, b, out=result, where=np.asarray(b) != 0)


def descriptors(compact, names):
    result = {}
    for path in referenced_files(compact):
        for readout in ET.parse(path).getroot().findall('.//readout'):
            if readout.get('name') not in names:
                continue
            offset = 0
            fields = {}
            for field in readout.findtext('id').strip().split(','):
                pieces = field.split(':')
                if len(pieces) == 3:
                    offset = int(pieces[1])
                width = int(pieces[-1])
                fields[pieces[0]] = (offset, width)
                offset += abs(width)
            result[readout.get('name')] = fields
    if set(result) != set(names):
        raise ValueError("Missing actual readout descriptor")
    return result


def decode(cid, fields, name):
    offset, width = fields[name]
    value = (cid >> offset) & ((1 << abs(width))-1)
    return value-(1 << abs(width)) if width < 0 and value & (1 << (abs(width)-1)) else value


def longitudinal(row, events, geom):
    from podio import root_io
    fields = descriptors(geom["compact"], geom["collections"])
    per_event = []
    for frame, event in zip(root_io.Reader(row["sample"]["path"]).get("events"), events, strict=True):
        values = {}
        for name in geom["collections"]:
            def key(cid):
                side = decode(cid, fields[name], "side" if "side" in fields[name] else "barrel")
                return f"{name}:side{side}:layer{decode(cid,fields[name],'layer')}"
            for hit in frame.get(name):
                target = values.setdefault(key(int(hit.getCellID())), np.zeros(3))
                target[0] += float(hit.getEnergy())
            for stage_index, mode in enumerate(("off", "on"), 1):
                for cid, amplitude in event["modes"][mode]["cells"][name]:
                    if amplitude > float(np.float32(.6)):
                        target = values.setdefault(key(cid), np.zeros(3))
                        target[stage_index] += amplitude*MIP
        if not np.allclose(np.sum(list(values.values()), axis=0) if values else np.zeros(3),
                           [event["raw_GeV"], event["modes"]["off"]["energy_GeV"], event["modes"]["on"]["energy_GeV"]], rtol=1e-11, atol=1e-13):
            raise ValueError("Per-layer native/raw energy closure failed")
        per_event.append(values)
    labels = sorted({name for values in per_event for name in values})
    data = np.array([[values.get(name, np.zeros(3)) for name in labels] for values in per_event]).reshape(len(events), len(labels), 3)
    return dict(axes=labels, unit="GeV per generated event", events=len(events),
                stages={stage: dict(mean=data[:, :, i].mean(axis=0).tolist(),
                                     SEM=(data[:, :, i].std(axis=0, ddof=1)/math.sqrt(len(events))).tolist())
                        for i, stage in enumerate(STAGES)},
                scope="Observed region/side/layer ID axes, zeros retained per event; absent axes are not a full constructed-layer inventory; errors are marginal event SEM")


def shower_summary(runs, manifest, args):
    rng = np.random.Generator(np.random.PCG64(126300))
    calibration = {}
    factors = {}
    for row in runs:
        if row["kind"] != "calibration":
            continue
        x = array_events(read_events(row))[:, 1]
        energy = row["sample"]["truth"]["generated_total_energy_GeV"]
        eta = str(row["sample"]["eta"])
        means = x[rng.integers(0, len(x), (5000, len(x)))].mean(axis=1)
        if np.any(means <= 0) or x.mean() <= 0:
            raise ValueError("Nonpositive independent calibration")
        factors[eta] = energy/means
        calibration[eta] = dict(factor=energy/float(x.mean()), factor_bootstrap=uncertainty(factors[eta]),
                                n=len(x), input_sha256=row["sample"]["sha256"],
                                D_GeV=basic(x), primary_total_energy_GeV=energy)
    if set(calibration) != {"0", "1", "2", "-2"}:
        raise ValueError("Four independent ODD reference directions required")
    calibration_path = args.work / "common-calibration.json"
    if calibration_path.exists() and json.loads(calibration_path.read_text()) != calibration:
        raise ValueError("Previously frozen common calibration changed")
    save(calibration_path, calibration)
    output = []
    boot_response = []
    boot_width = []
    boot_tail = []
    axes = []
    populations = {}
    for row in runs:
        if row["kind"] != "showers":
            continue
        sample = row["sample"]
        events = read_events(row)
        x = array_events(events)
        energy = sample["truth"]["generated_total_energy_GeV"]
        eta = str(sample["eta"])
        factor = calibration[eta]["factor"]
        index = rng.integers(0, len(x), (5000, len(x)))
        replicas = x[index]
        means = replicas.mean(axis=1)
        widths = ratio(replicas.std(axis=1, ddof=1), means)
        responses = means*factors[eta][:, None]/energy
        tails = (replicas*factors[eta][:, None, None]/energy < .8).mean(axis=1)
        stages = {}
        for i, stage in enumerate(STAGES):
            response = x[:, i]*factor/energy
            tail_count = int(np.sum(response < .8))
            from muon_response import wilson
            low, high = wilson(tail_count, len(x))
            stages[stage] = dict(energy_GeV=basic(x[:, i]), visible_fraction=basic(x[:, i]/energy),
                                 mean_response=float(response.mean()), response_bootstrap=uncertainty(responses[:, i]),
                                 SD_over_mean_bootstrap=uncertainty(widths[:, i]),
                                 visible_fraction_histogram=histogram(x[:, i]/energy, np.linspace(0, .1, 251), "Si GeV / generated GeV"),
                                 response_histogram=histogram(response, np.linspace(0, 2.4, 121), "common-scale response"),
                                 low_response_tail=dict(count=tail_count, denominator=len(x), fraction=tail_count/len(x),
                                                        Wilson95=[float(low), float(high)], bootstrap=uncertainty(tails[:, i])))
            axes.append(f"{row['geometry']}:{sample['particle']}:p{sample['energy_GeV']}:eta{sample['eta']}:{stage}")
        changes = {}
        for label, left, right in (("D_minus_raw", 1, 0), ("PN_minus_D", 2, 1), ("PN_minus_raw", 2, 0)):
            changes[label] = dict(energy_GeV=basic(x[:, left]-x[:, right]),
                                  visible_fraction_bootstrap=uncertainty((means[:, left]-means[:, right])/energy),
                                  mean_response_change=float((x[:, left]-x[:, right]).mean()*factor/energy),
                                  relative_mean_change_to_raw=float((x[:, left]-x[:, right]).mean()/x[:,0].mean()) if x[:,0].mean() else None,
                                  relative_change_bootstrap=uncertainty(ratio(means[:,left]-means[:,right],means[:,0])),
                                  response_change_bootstrap=uncertainty(responses[:, left]-responses[:, right]),
                                  width_change_bootstrap=uncertainty(widths[:, left]-widths[:, right]))
        output.append(dict(geometry=row["geometry"], particle=sample["particle"], momentum_GeV=sample["energy_GeV"],
                           eta=sample["eta"], n=len(x), mirror_control=sample["eta"] == -2,
                           primary_total_energy_GeV=energy, stages=stages, paired_changes=changes,
                           longitudinal=longitudinal(row, events, manifest["geometries"][row["geometry"]]),
                           input_sha256=sample["sha256"], native_output_sha256=row["receipt"]["output_sha256"]))
        boot_response.append(responses)
        boot_width.append(widths)
        boot_tail.append(tails)
        populations[(row["geometry"], sample["particle"], sample["energy_GeV"], sample["eta"])] = (x, means, widths, energy)
        print("Characterized", row["geometry"], sample["id"], flush=True)
    comparisons = []
    for geometry, particle, momentum, eta in populations:
        if geometry != "nodd":
            continue
        n, nb, nw, ne = populations[("nodd", particle, momentum, eta)]
        o, ob, ow, oe = populations[("odd-zero", particle, momentum, eta)]
        comparisons.append(dict(particle=particle, momentum_GeV=momentum, eta=eta,
                                stages={stage: dict(mean_ratio_nodd_over_ODD=float((n[:, i].mean()/ne)/(o[:, i].mean()/oe)) if o[:, i].mean() else None,
                                                    mean_ratio_bootstrap=uncertainty(ratio(nb[:, i]/ne, ob[:, i]/oe)),
                                                    width_difference_bootstrap=uncertainty(nw[:, i]-ow[:, i]))
                                        for i, stage in enumerate(STAGES)},
                                sampling="Independent transports; event bootstrap independent across geometries, paired only across stages within geometry"))
    return dict(calibration=calibration, populations=output, geometry_comparisons=comparisons,
                covariance_axes=axes, response_bootstrap_covariance=covariance(np.concatenate(boot_response, axis=1)),
                width_bootstrap_covariance=covariance(np.concatenate(boot_width, axis=1)),
                tail_bootstrap_covariance=covariance(np.concatenate(boot_tail, axis=1)),
                bootstrap=dict(seed=126300, replicates=5000, unit="whole event", independent_geometry_samples=True,
                               shared_ODD_calibration_across_geometries_species_energies_stages=True))


def pedestal(args):
    """Reuse the measured signed fixture only after exact backend/payload checks."""
    directory = ROOT / "build/issue117/nov9/digitized-response/pedestal"
    receipt_path = directory / "execution.json"
    receipt = json.loads(receipt_path.read_text())
    previous_path = ROOT / "docs/validation/issue117/previews/digitized-response.json"
    previous = json.loads(previous_path.read_text())["pedestal"]
    request = json.loads((directory / "input.json").read_text())
    if (receipt["exit_code"] or receipt["identity"]["backend_sha256"] != sha(args.backend)
            or receipt["identity"]["configuration"] != request
            or request["mipGeV"] != MIP or request["pairEnergyEv"] != 0 or request["noiseMip"] != .13
            or len(request["energiesGeV"]) != 200000 or any(request["energiesGeV"])):
        raise ValueError("Previous signed pedestal backend/configuration mismatch")
    for path, key in ((directory / "input.json", "input_sha256"), (directory / "output.json", "output_sha256"),
                      (receipt_path, "execution_receipt_sha256")):
        if sha(path) != previous[key]:
            raise ValueError("Previous measured pedestal evidence changed")
    if not previous["gaussian_control"]["passed"]:
        raise ValueError("Signed model pedestal gate failed")
    return dict(previous, reused_fixture=dict(summary_sha256=sha(previous_path), backend_sha256=sha(args.backend),
                                              same_backend_and_response_configuration=True,
                                              scope="Independent prior signed electronics-only fixture, not new hardware data"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["run", "showers", "geometry", "analyze"])
    parser.add_argument("--transport-manifest", type=Path, required=True)
    parser.add_argument("--samples", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--binary", type=Path, default=Path('/private/tmp/nodd-digitization117-build/EDM4hep/nodd_silicon_validation'))
    parser.add_argument("--backend", type=Path, default=Path('/private/tmp/nodd-digitization117-build/nodd_marlin_silicon_backend'))
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--fit-workers", type=int, default=8)
    parser.add_argument("--geometry", choices=["nodd", "odd-zero"])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.stage == "run":
        run(args)
        return
    if args.stage == "geometry":
        from nodd_muon_response import geometry
        geometry(args)
        return
    manifest, runs = verify_runs(args)
    result = dict(status="PROTOTYPE nODD/ODD baseline-stage response characterization",
                  settings=dict(mip_energy_GeV=MIP, threshold_MIP=.6, dynamic_range_MIP=2500., modes=MODES),
                  showers=shower_summary(runs, manifest, args),
                  provenance=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                                  analysis_sha256=hashlib.sha256(LOADED_SOURCE).hexdigest(), protocol_sha256=sha(PROTOCOL),
                                  analysis_notes_sha256=sha(ANALYSIS_NOTES),
                                  plugin_registration_audit_sha256=sha(args.transport_manifest.parent/'plugin-registration-audit.json'),
                                  transport_manifest_sha256=sha(args.transport_manifest), samples_sha256=sha(args.samples),
                                  native_runs_sha256=sha(args.work / 'runs.json')))
    if args.stage == "analyze":
        checkpoint = json.loads(json.dumps(result, allow_nan=False).replace(str(ROOT), '${NODD_REPO}').replace(str(Path.home()), '${USER_HOME}'))
        save(args.work / 'shower-summary-checkpoint.json', checkpoint)
        from nodd_muon_response import muon_summary
        result["pedestal"] = pedestal(args)
        result["muons"] = muon_summary(runs, args, result["pedestal"])
    result = json.loads(json.dumps(result).replace(str(ROOT), '${NODD_REPO}').replace(str(Path.home()), '${USER_HOME}'))
    save(args.output or args.work / 'summary.json', result)


if __name__ == "__main__":
    main()
