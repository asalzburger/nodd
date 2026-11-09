#!/usr/bin/env python3
"""Run native Si-W diagnostics and retain only compact digitized-response evidence.

All event diagnostics, raw ROOT inputs and logs stay under the ignored work path.
The frozen protocol defines unsigned study settings, selections and uncertainty.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[3]
COLLECTIONS = ["ECalBarrelCollection", "ECalEndcapCollection"]
STAGES = ["raw", "off", "on"]
MODES = [dict(name="off", pair_energy_eV=0., noise_MIP=0.),
         dict(name="on", pair_energy_eV=3.6, noise_MIP=.13)]


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def histogram(values, edges, unit):
    values = np.asarray(values)
    if not np.isfinite(values).all():
        raise ValueError("Nonfinite histogram input")
    counts, _ = np.histogram(values, bins=edges)
    # numpy includes the uppermost edge; use a half-open convention everywhere.
    counts[-1] -= int(np.sum(values == edges[-1]))
    return dict(edges=np.asarray(edges).tolist(), counts=counts.tolist(),
                underflow=int(np.sum(values < edges[0])),
                overflow=int(np.sum(values >= edges[-1])), unit=unit,
                entries=int(values.size), normalization="counts; explicit under/overflow")


def basic(values):
    x = np.asarray(values, dtype=float)
    mean = float(x.mean())
    sd = float(x.std(ddof=1))
    return dict(n=len(x), mean=mean, mean_SE=sd / math.sqrt(len(x)),
                SD=sd, RMS_over_mean=sd / mean if mean else None,
                zero_count=int(np.sum(x == 0)), sums_powers=[float(np.sum(x ** k)) for k in range(1, 5)])


def bootstrap_sample(x, rng):
    index = rng.integers(0, len(x), (5000, len(x)))
    bs = x[index]
    means = bs.mean(axis=1)
    widths = np.full_like(means,np.nan)
    np.divide(bs.std(axis=1,ddof=1),means,out=widths,where=means!=0)
    return means, widths, bs


def uncertainty(values):
    if not np.isfinite(values).all():
        return dict(SE=None,CI95=None,undefined_replicates=int(np.sum(~np.isfinite(values))))
    return dict(SE=float(values.std(ddof=1)),CI95=np.quantile(values,[.025,.975]).tolist(),undefined_replicates=0)


def covariance(values):
    # Preserve undefined width rows/columns; never drop events or silently
    # condition width errors on the bootstrap samples that happened to be nonzero.
    valid=np.isfinite(values).all(axis=0)
    return [[float(np.cov(values[:,i],values[:,j],ddof=1)[0,1]) if valid[i] and valid[j] else None
             for j in range(values.shape[1])] for i in range(values.shape[1])]


def run_samples(args):
    args.work.mkdir(parents=True, exist_ok=True)
    calibration = json.loads(args.mip_calibration.read_text())
    rows = []
    for kind, path in [("showers", args.samples), ("calibration", args.calibration_samples),
                       ("muons", args.muon_samples)]:
        manifest = json.loads(path.read_text())
        if manifest["odd_revision"] != "d70556f33b1c36abdf101a07ad8cf57eb56fbdf1":
            raise ValueError("Unexpected ODD source")
        for sample in manifest["samples"]:
            if sample["exit_code"] or sha(sample["path"]) != sample["sha256"]:
                raise ValueError("Changed/failed source sample")
            rows.append(dict(kind=kind, sample=sample, manifest_sha256=sha(path)))
    def execute(index_row):
        index, row = index_row
        tag = row["kind"] + "-" + Path(row["sample"]["path"]).parent.name
        directory = args.work / tag
        directory.mkdir(exist_ok=True)
        config = dict(mip_energy_GeV=calibration["mip_energy_GeV"], threshold_MIP=.6,
                      dynamic_range_MIP=2500., seed=119117 + index * 100,
                      collections=COLLECTIONS, modes=MODES, save_cells=row["kind"] == "muons")
        config_path = directory / "config.json"
        data_path = directory / "diagnostics.jsonl"
        receipt_path = directory / "execution.json"
        identity = dict(input_sha256=sha(row["sample"]["path"]), binary_sha256=sha(args.binary),
                        backend_sha256=sha(args.backend), configuration=config)
        if receipt_path.exists():
            receipt = json.loads(receipt_path.read_text())
            if receipt["identity"] != identity or receipt["exit_code"] or sha(data_path) != receipt["output_sha256"]:
                raise ValueError("Existing execution is failed or has changed; use a fresh work path")
        else:
            if data_path.exists():
                raise ValueError("Unreceipted diagnostics; use a fresh work path")
            write(config_path, config)
            command = [str(args.binary.resolve()), row["sample"]["path"], str(config_path.resolve()),
                       str(data_path.resolve()), str(args.backend.resolve())]
            started = time.monotonic()
            with (directory / "native.log").open("w") as log:
                proc = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
            receipt = dict(identity=identity, command=command, exit_code=proc.returncode,
                           elapsed_seconds=time.monotonic() - started,
                           output_sha256=sha(data_path) if data_path.exists() else None,
                           config_sha256=sha(config_path), log_sha256=sha(directory / "native.log"))
            write(receipt_path, receipt)
            if proc.returncode:
                raise RuntimeError(f"Native validation failed: {directory}")
        result = dict(row, tag=tag, receipt=receipt, diagnostics=str(data_path.resolve()))
        print(tag, "exit", receipt["exit_code"], flush=True)
        return result
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        executed = list(pool.map(execute, enumerate(rows)))
    write(args.work / "runs.json", executed)


def read_events(row):
    path = Path(row["diagnostics"])
    if sha(path) != row["receipt"]["output_sha256"]:
        raise ValueError("Diagnostics changed")
    events = [json.loads(line) for line in path.read_text().splitlines()]
    if len(events) != row["sample"]["requested_events"]:
        raise ValueError("Event denominator mismatch")
    if [e["index"] for e in events]!=list(range(len(events))):
        raise ValueError("Diagnostic event order changed")
    identities = [tuple(e["identity"]) for e in events]
    if len(set(identities)) != len(events):
        raise ValueError("Duplicate event identities")
    return events


def verify_run(row,args):
    data_path=Path(row["diagnostics"])
    receipt_path=data_path.parent/"execution.json"
    receipt=json.loads(receipt_path.read_text())
    if receipt!=row["receipt"] or receipt["exit_code"]!=0:
        raise ValueError("Execution receipt changed or failed")
    identity=receipt["identity"]
    if identity["input_sha256"]!=row["sample"]["sha256"] or sha(row["sample"]["path"])!=identity["input_sha256"]:
        raise ValueError("Executed raw input changed")
    if sha(args.binary)!=identity["binary_sha256"] or sha(args.backend)!=identity["backend_sha256"]:
        raise ValueError("Executed binary/backend differs from analysis arguments")
    config_path=data_path.parent/"config.json"
    if sha(config_path)!=receipt["config_sha256"] or json.loads(config_path.read_text())!=identity["configuration"]:
        raise ValueError("Executed configuration changed")
    if sha(data_path.parent/"native.log")!=receipt["log_sha256"] or sha(data_path)!=receipt["output_sha256"]:
        raise ValueError("Executed native log/output changed")
    return dict(receipt_sha256=sha(receipt_path),input_size_bytes=Path(row["sample"]["path"]).stat().st_size,
                output_size_bytes=data_path.stat().st_size)


def truth_summary(row):
    from podio import root_io
    expected_pdg={"e-":11,"gamma":22,"mu-":13}[row["sample"]["particle"]]
    energies=[]
    momenta=[]
    for frame in root_io.Reader(row["sample"]["path"]).get("events"):
        primaries=[p for p in frame.get("MCParticles") if p.getGeneratorStatus()==1]
        if len(primaries)!=1 or primaries[0].getPDG()!=expected_pdg:
            raise ValueError("Wrong generated species/multiplicity")
        primary=primaries[0]
        p=primary.getMomentum()
        momentum=math.sqrt(p.x*p.x+p.y*p.y+p.z*p.z)
        eta=math.asinh(p.z/math.hypot(p.x,p.y))
        phi=math.atan2(p.y,p.x)
        if abs(momentum-row["sample"]["energy_GeV"])>1e-7 or abs(eta-row["sample"]["eta"])>1e-7 or abs(phi-row["sample"]["phi_rad"])>1e-7:
            raise ValueError("Generated momentum/direction mismatch")
        energies.append(float(primary.getEnergy()))
        momenta.append(momentum)
    if len(energies)!=row["sample"]["requested_events"] or max(energies)-min(energies)>1e-7:
        raise ValueError("Incomplete or non-monoenergetic truth")
    return dict(events=len(energies),PDG=expected_pdg,total_energy_GeV=float(np.mean(energies)),
                total_energy_range_GeV=[min(energies),max(energies)],
                momentum_GeV=float(np.mean(momenta)),
                convention="DDSim gun.energy in this configuration sets momentum magnitude; denominators use persisted MC total energy")


def array_events(events):
    return np.array([[e["raw_GeV"], e["modes"]["off"]["energy_GeV"],
                      e["modes"]["on"]["energy_GeV"]] for e in events])


def shower_summary(rows,args):
    calibration = {}
    rng = np.random.Generator(np.random.PCG64(119404))
    for row in rows:
        if row["kind"] != "calibration":
            continue
        x = array_events(read_events(row))
        off = x[:, 1]
        if not np.isfinite(off).all() or off.mean()<=0:
            raise ValueError("Independent calibration has no finite positive mean")
        # One independent noise-off electron calibration per direction, common to
        # species, test energy and raw/off/on. No per-point rescaling.
        truth=row["truth"]
        factor = truth["total_energy_GeV"] / float(off.mean())
        reference_means=off[rng.integers(0,len(off),(5000,len(off)))].mean(axis=1)
        if np.any(reference_means<=0):
            raise ValueError("Undefined resampled independent calibration; no events discarded")
        rep = truth["total_energy_GeV"] / reference_means
        calibration[row["sample"]["eta"]] = (factor, rep, dict(
            n=len(off), energy_GeV=row["sample"]["energy_GeV"], factor=factor,
            factor_SE=float(rep.std(ddof=1)), off=basic(off), input_sha256=row["sample"]["sha256"]))
    frozen={str(k):v[2] for k,v in calibration.items()}
    freeze_path=args.work/"frozen-shower-calibration.json"
    if freeze_path.exists():
        if json.loads(freeze_path.read_text())!=frozen:
            raise ValueError("Frozen calibration changed")
    else:
        write(freeze_path,frozen)
    results, boot_vectors, boot_labels, boot_tails = [], [], [], []
    for n, row in enumerate(rows):
        if row["kind"] != "showers":
            continue
        sample = row["sample"]
        events = read_events(row)
        x = array_events(events)
        factor, factor_bs, _ = calibration[sample["eta"]]
        beam = row["truth"]["total_energy_GeV"]
        means, widths, bs = bootstrap_sample(x, rng)
        corrected = means * factor_bs[:,None] / beam
        tails=(bs * factor_bs[:,None,None] / beam < .8).mean(axis=1)
        item = dict(particle=sample["particle"], beam_energy_GeV=beam, nominal_momentum_GeV=sample["energy_GeV"], eta=sample["eta"],
                    n=len(x), phi_rad=sample["phi_rad"], stages={},
                    stage_order=STAGES, paired_energy_covariance_GeV2=np.cov(x.T,ddof=1).tolist(),
                    response_bootstrap_covariance=np.cov(corrected.T,ddof=1).tolist(),
                    width_bootstrap_covariance=covariance(widths))
        from muon_response import wilson
        for j, stage in enumerate(STAGES):
            values=x[:,j]
            tail_count=int(np.sum(values*factor/beam<.8))
            tail_low,tail_high=wilson(tail_count,len(values))
            width_unc=uncertainty(widths[:,j])
            item["stages"][stage]=dict(basic(values),
                calibrated_response=float(values.mean()*factor/beam),
                calibrated_response_SE=float(corrected[:,j].std(ddof=1)),
                RMS_over_mean_SE=width_unc["SE"],
                RMS_over_mean_CI95=width_unc["CI95"],
                RMS_over_mean_undefined_bootstrap_replicates=width_unc["undefined_replicates"],
                calibrated_response_CI95=np.quantile(corrected[:,j],[.025,.975]).tolist(),
                calibrated_energy=histogram(values*factor,np.linspace(0,2.5*beam,201),"GeV"),
                low_response_tail=dict(cut_calibrated_response=.8,count=tail_count,denominator=len(values),
                    fraction=tail_count/len(values),conditional_Wilson95=[float(tail_low),float(tail_high)],
                    joint_reference_event_bootstrap_SE=float(tails[:,j].std(ddof=1)),
                    joint_reference_event_bootstrap_CI95=np.quantile(tails[:,j],[.025,.975]).tolist()),
                deposited_fraction=histogram(values/beam,np.linspace(0,.1,201),"1"))
            boot_vectors.append(corrected[:,j]); boot_labels.append(f"{sample['particle']}:eta{sample['eta']:g}:E{beam:g}:{stage}")
            boot_tails.append(tails[:,j])
        item["paired_on_minus_raw_GeV"] = basic(x[:,2]-x[:,0])
        item["paired_on_minus_off_GeV"] = basic(x[:,2]-x[:,1])
        a=item["stages"]["on"]["RMS_over_mean"];b=item["stages"]["off"]["RMS_over_mean"]
        item["paired_width_changes"]=dict(on_minus_off_value=a-b if a is not None and b is not None else None,
            on_minus_off_uncertainty=uncertainty(widths[:,2]-widths[:,1]),
            on_minus_raw_uncertainty=uncertainty(widths[:,2]-widths[:,0]))
        results.append(item)
    return dict(calibrations=frozen, calibration_freeze_sha256=sha(freeze_path), samples=results,
                response_covariance_labels=boot_labels,
                response_bootstrap_covariance=np.cov(np.asarray(boot_vectors),ddof=1).tolist(),
                low_response_tail_joint_bootstrap_covariance=np.cov(np.asarray(boot_tails),ddof=1).tolist(),
                uncertainty="5000 PCG64 whole-event paired bootstrap replications; seed119404, references then samples in manifest order; independent reference resampled once per direction and jointly across energies/species/stages")


def pedestal(args, mip):
    directory=args.work/"pedestal"
    directory.mkdir(exist_ok=True)
    request=dict(schema=1,event=0,seed=119402,mipGeV=mip,pairEnergyEv=0.,
                 noiseMip=.13,dynamicRangeMip=2500.,energiesGeV=[0.]*200000)
    input_path=directory/"input.json"; output_path=directory/"output.json"
    receipt_path=directory/"execution.json"
    identity=dict(backend_sha256=sha(args.backend),configuration=request)
    if not input_path.exists():
        write(input_path,request)
    elif json.loads(input_path.read_text())!=request:
        raise ValueError("Pedestal request changed")
    if output_path.exists():
        if not receipt_path.exists():
            raise ValueError("Unreceipted pedestal output")
        receipt=json.loads(receipt_path.read_text())
        if receipt["identity"]!=identity or sha(output_path)!=receipt["output_sha256"]:
            raise ValueError("Pedestal execution identity changed")
    else:
        subprocess.run([str(args.backend.resolve()),str(input_path.resolve()),str(output_path.resolve())],check=True)
        write(receipt_path,dict(identity=identity,output_sha256=sha(output_path),exit_code=0))
    response=json.loads(output_path.read_text())
    if response["upstream"]!="iLCSoft/MarlinReco@255967eb855ebbc8f75ebaac190b268b63332e8b":
        raise ValueError("Wrong pedestal backend")
    values=np.asarray(response["mip"])
    if len(values)!=200000 or not np.isfinite(values).all():
        raise ValueError("Invalid pedestal denominator/values")
    expected_probability=.5*math.erfc(2/math.sqrt(2))
    measured=basic(values)
    mean_z=measured["mean"]/(.13/math.sqrt(len(values)))
    RMS_z=(measured["SD"]-.13)/(.13/math.sqrt(2*(len(values)-1)))
    tail=int(np.sum(values>np.float32(.26)))
    tail_z=(tail-len(values)*expected_probability)/math.sqrt(len(values)*expected_probability*(1-expected_probability))
    return dict(basic(values), signed=histogram(values,np.linspace(-.65,.65,131),"MIP"),
                thresholds_MIP=[.26,.6], accepted_counts=[int(np.sum(values>np.float32(t))) for t in [.26,.6]],
                input_sha256=sha(input_path),output_sha256=sha(output_path),
                execution_receipt_sha256=sha(receipt_path),
                gaussian_control=dict(mean_z=mean_z,RMS_z=RMS_z,tail_2sigma_z=tail_z,
                                      passed=all(abs(z)<=5 for z in [mean_z,RMS_z,tail_z]),
                                      criterion="each analytic Gaussian deviation <=5 standard errors; configured sigma0.13MIP"),
                scope="explicit empty-channel extension bypasses undefined zero-energy pair statistics; not original sparse-processor equivalence or detector-wide occupancy")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage",choices=["run","analyze","geometry"])
    parser.add_argument("--samples",type=Path,required=True)
    parser.add_argument("--calibration-samples",type=Path,required=True)
    parser.add_argument("--muon-samples",type=Path,required=True)
    parser.add_argument("--mip-calibration",type=Path,required=True)
    parser.add_argument("--binary",type=Path,required=True)
    parser.add_argument("--backend",type=Path,required=True)
    parser.add_argument("--work",type=Path,required=True)
    parser.add_argument("--output",type=Path)
    parser.add_argument("--jobs",type=int,default=4)
    parser.add_argument("--fit-workers",type=int,default=8)
    parser.add_argument("--odd-source",type=Path)
    parser.add_argument("--odd-library",type=Path)
    args=parser.parse_args()
    if args.fit_workers<1:
        parser.error("Fit workers must be positive")
    from muon_response import geometry,muon_summary
    if args.stage=="geometry":
        if not args.odd_source or not args.odd_library:
            parser.error("Geometry requires ODD source/library")
        geometry(args)
        return
    if args.stage=="run":
        run_samples(args)
        return
    if not args.output or args.output.exists():
        parser.error("A fresh output path is required")
    rows=json.loads((args.work/"runs.json").read_text())
    for index,row in enumerate(rows):
        row["verified_execution"]=verify_run(row,args)
        expected=dict(mip_energy_GeV=json.loads(args.mip_calibration.read_text())["mip_energy_GeV"],threshold_MIP=.6,
                      dynamic_range_MIP=2500.,seed=119117+100*index,collections=COLLECTIONS,
                      modes=MODES,save_cells=row["kind"]=="muons")
        if row["receipt"]["identity"]["configuration"]!=expected:
            raise ValueError("Executed configuration differs from frozen study")
        row["truth"]=truth_summary(row)
    result=dict(status="PROTOTYPE digitized response characterization; no detector acceptance",
                settings=dict(mip_energy_GeV=json.loads(args.mip_calibration.read_text())["mip_energy_GeV"],
                              threshold_MIP=.6,dynamic_range_MIP=2500.,modes=MODES),
                showers=shower_summary(rows,args))
    result["pedestal"]=pedestal(args,result["settings"]["mip_energy_GeV"])
    result["muons"]=muon_summary(rows,args,result["pedestal"])
    import ROOT
    result["provenance"]=dict(python=platform.python_version(),numpy=np.__version__,ROOT=ROOT.gROOT.GetVersion(),
        source_sha256={str(p.relative_to(ROOT_DIR)):sha(p) for p in [Path(__file__),Path(__file__).with_name("muon_response.py"),ROOT_DIR/"software/source/ActsExamples/Calorimeter/EDM4hep/SiliconValidation.cpp",ROOT_DIR/"docs/validation/issue117/digitization-protocol.md"]},
        mip_calibration_sha256=sha(args.mip_calibration),native_binary_sha256=sha(args.binary),backend_sha256=sha(args.backend),
        runs=[dict(kind=r["kind"],particle=r["sample"]["particle"],energy_GeV=r["sample"]["energy_GeV"],eta=r["sample"]["eta"],
                   n=r["sample"]["requested_events"],input_sha256=r["sample"]["sha256"],manifest_sha256=r["manifest_sha256"],
                   truth=r["truth"],
                   verified_execution=r["verified_execution"],
                   executed_binary_sha256=r["receipt"]["identity"]["binary_sha256"],
                   executed_backend_sha256=r["receipt"]["identity"]["backend_sha256"],
                   simulation_seed=r["sample"]["seed"],configuration=r["receipt"]["identity"]["configuration"],
                   output_sha256=r["receipt"]["output_sha256"],exit_code=r["receipt"]["exit_code"],
                   native_log_sha256=r["receipt"]["log_sha256"],configuration_sha256=r["receipt"]["config_sha256"],
                   elapsed_seconds=r["receipt"]["elapsed_seconds"]) for r in rows])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    write(args.output,result)
    print(args.output,sha(args.output))


if __name__=="__main__":
    main()
