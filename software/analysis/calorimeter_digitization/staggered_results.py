"""Four-way ECAL comparison with nested calibration refit in paired bootstraps."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import time

import numpy as np

from angular_analyze import ETA_EDGES, PHI_EDGES, bin_index, folded_phi
from angular_sample import ROOT, save, sha
from staggered_calibration import CrossFit, INNER_SEED, OUTER_SEED, LAMBDAS

ENERGY_EDGES = np.linspace(10, 80, 15)
SERIES = ("baseline_raw", "baseline_calibrated", "staggered_raw", "staggered_calibrated")
CONTRASTS = ((0, 2, "raw_layout_reduction"), (0, 1, "baseline_calibration_reduction"),
             (2, 3, "staggered_calibration_reduction"), (1, 3, "calibrated_layout_reduction"))


def load_features(directory):
    receipt = json.loads((directory / "receipt.json").read_text())
    if receipt["status"] != "PASS" or sha(directory / "features.npz") != receipt["feature_sha256"]:
        raise ValueError("Changed/unsuccessful reconstructed features")
    with np.load(directory / "features.npz", allow_pickle=False) as source:
        data = {key: source[key].copy() for key in source.files}
    if not np.array_equal(data["event"], np.arange(10000)):
        raise ValueError("Expected all 10k feature IDs in identity order")
    return data, receipt


def moments(values, category, multiplicity, bins):
    count = np.bincount(category, weights=multiplicity, minlength=bins)
    total = np.bincount(category, weights=multiplicity * values, minlength=bins)
    square = np.bincount(category, weights=multiplicity * values ** 2, minlength=bins)
    mean = np.divide(total, count, out=np.full(bins, np.nan), where=count > 0)
    variance = np.divide(square - total * mean, count - 1,
                         out=np.full(bins, np.nan), where=count > 1)
    width = np.divide(np.sqrt(np.maximum(variance, 0)), mean,
                      out=np.full(bins, np.nan), where=mean > 0)
    return mean, width


def interval(values):
    undefined = int(np.count_nonzero(~np.isfinite(values)))
    return dict(ci95=np.quantile(values, [.025, .975]).tolist() if undefined == 0 else None,
                bootstrap_undefined=undefined)


def population(values, tail_values, selected, data, prediction=None):
    v = values[selected]
    quantile = np.quantile(v, [.16, .5, .84]) if len(v) else [np.nan] * 3
    mean = float(v.mean()) if len(v) else None
    sd = float(v.std(ddof=1)) if len(v) > 1 else None
    result = dict(events=int(selected.sum()), mean=mean, sample_sd=sd,
        fractional_width=sd / mean if sd is not None and mean > 0 else None,
        q16=float(quantile[0]) if len(v) else None,
        median=float(quantile[1]) if len(v) else None, q84=float(quantile[2]) if len(v) else None,
        central_quantile_fraction=float((quantile[2] - quantile[0]) / 2 / quantile[1]) if quantile[1] > 0 else None,
        zero_events=int(np.count_nonzero(v == 0)),
        tail_below_half=int(np.count_nonzero(tail_values[selected] < .5)),
        tail_fraction=float(np.mean(tail_values[selected] < .5)) if len(v) else None,
        invalid_axis_events=int(np.count_nonzero(~data["valid_axis"][selected])),
        energy_mean_GeV=float(data["energy"][selected].mean()) if len(v) else None)
    if prediction is not None:
        result["gain_clipped_events"] = int(prediction["clipped"][selected].sum())
        result["gain_clipped_fraction"] = float(prediction["clipped"][selected].mean()) if len(v) else None
    return result


def fit_only(args):
    data, receipt = load_features(args.features)
    model = CrossFit(data)
    prediction = model.predict(record=True)
    prior = model.predict(prior="inverse_energy", record=True)
    args.output.mkdir(parents=True, exist_ok=False)
    np.savez_compressed(args.output / "predictions.npz", **{key: value for key, value in prediction.items() if key != "records"})
    save(args.output / "fit.json", dict(feature_receipt=receipt, primary_models=prediction["records"],
        secondary_prior_models=prior["records"], primary_global=population(prediction["response"], prediction["response"],
        np.ones(10000, dtype=bool), data, prediction), source_sha256=sha(__file__),
        core_sha256=sha(Path(__file__).with_name("staggered_calibration.py"))))
    print(json.dumps(dict(events=10000, calibrated_width=float(prediction["response"].std(ddof=1) / prediction["response"].mean()),
                          mean=float(prediction["response"].mean()), clipped=int(prediction["clipped"].sum())), indent=2))


def compare(args):
    loaded = [load_features(args.baseline), load_features(args.staggered)]
    data = [x[0] for x in loaded]
    for key in ("event", "energy", "eta", "phi"):
        if not np.array_equal(data[0][key], data[1][key]):
            raise ValueError(f"Geometry primary pairing differs: {key}")
    models = [CrossFit(d) for d in data]
    predictions = [m.predict(record=True) for m in models]
    priors = [m.predict(prior="inverse_energy", record=True) for m in models]
    values = np.array([data[0]["response"], predictions[0]["response"], data[1]["response"], predictions[1]["response"]])
    tails = np.array([predictions[0]["scale_only"], predictions[0]["response"], predictions[1]["scale_only"], predictions[1]["response"]])
    categories = [bin_index(abs(data[0]["eta"]), ETA_EDGES), bin_index(folded_phi(data[0]["phi"]), PHI_EDGES)]
    energy_category = bin_index(data[0]["energy"], ENERGY_EDGES)
    reference = json.loads(args.reference.read_text())
    for axis,name in enumerate(("abs_eta","folded_phi")):
        for i,original in enumerate(reference["projections"][name]["bins"]):
            v=data[0]["response"][categories[axis]==i]
            if len(v)!=original["events"] or int((v==0).sum())!=original["zero_events"]:
                raise ValueError("Original baseline population changed")
            for value,key in ((v.mean(),"mean_response"),(v.std(ddof=1),"sample_sd"),
                              (v.std(ddof=1)/v.mean(),"fractional_width")):
                if not math.isclose(float(value),original[key],rel_tol=1e-12,abs_tol=1e-15):
                    raise ValueError("Original baseline moment changed")
    width_boot = np.full((args.bootstrap, 4, 20), np.nan)
    mean_boot = np.full_like(width_boot, np.nan)
    tail_boot = np.full_like(width_boot, np.nan)
    energy_mean_boot = np.full((args.bootstrap, 4, 14), np.nan)
    global_boot = np.full((args.bootstrap,4,3),np.nan)
    rng = np.random.default_rng(args.seed)
    start = time.monotonic()
    for replicate in range(args.bootstrap):
        indices = rng.integers(10000, size=10000)
        counts = np.bincount(indices, minlength=10000)
        predicted = [m.predict(counts) for m in models]
        vv = [data[0]["response"], predicted[0]["response"], data[1]["response"], predicted[1]["response"]]
        tt = [predicted[0]["scale_only"], predicted[0]["response"], predicted[1]["scale_only"], predicted[1]["response"]]
        for series in range(4):
            for axis in range(2):
                sl = slice(axis * 10, (axis + 1) * 10)
                mean_boot[replicate, series, sl], width_boot[replicate, series, sl] = moments(vv[series], categories[axis], counts, 10)
                tail_boot[replicate, series, sl] = moments((tt[series] < .5).astype(float), categories[axis], counts, 10)[0]
            energy_mean_boot[replicate, series] = moments(vv[series], energy_category, counts, 14)[0]
            gm,gw=moments(vv[series],np.zeros(10000,dtype=int),counts,1)
            global_boot[replicate,series]=[gm[0],gw[0],float(counts@(tt[series]<.5)/10000)]
        if (replicate + 1) % 50 == 0:
            print(f"Refitted paired bootstrap {replicate+1}/{args.bootstrap}: {time.monotonic()-start:.1f}s", flush=True)
    projections = {}
    histogram_edges={"raw_response_percent":np.linspace(0,max(.5,math.ceil(values[[0,2]].max()*200)/2),61),
                     "calibrated_energy_ratio":np.linspace(0,max(.5,math.ceil(values[[1,3]].max()*2)/2),61)}
    for axis, (name, edges) in enumerate((("abs_eta", ETA_EDGES), ("folded_phi", PHI_EDGES))):
        bins = []
        for i in range(10):
            selected = categories[axis] == i
            entry = dict(low=float(edges[i]), high=float(edges[i+1]), series={}, contrasts={})
            for series, label in enumerate(SERIES):
                geometry = series // 2
                point = population(values[series], tails[series], selected, data[geometry], predictions[geometry] if series % 2 else None)
                histogram_key="calibrated_energy_ratio" if series%2 else "raw_response_percent"
                displayed=values[series,selected]*(1 if series%2 else 100)
                histogram,_=np.histogram(displayed,bins=histogram_edges[histogram_key])
                if histogram.sum()!=selected.sum():raise ValueError("Histogram dropped a generated event")
                point["histogram_counts"]=histogram.tolist()
                for key, samples in (("fractional_width",width_boot),("mean",mean_boot),("tail_fraction",tail_boot)):
                    point[key+"_uncertainty"] = interval(samples[:,series,axis*10+i])
                entry["series"][label] = point
            for left, right, label in CONTRASTS:
                left_value=entry["series"][SERIES[left]]["fractional_width"]
                right_value=entry["series"][SERIES[right]]["fractional_width"]
                entry["contrasts"][label] = dict(value=left_value-right_value if left_value is not None and right_value is not None else None,
                    **interval(width_boot[:,left,axis*10+i] - width_boot[:,right,axis*10+i]))
            bins.append(entry)
        projections[name] = dict(edges=edges.tolist(),unit="rad" if axis else "dimensionless",bins=bins)
    energy = []
    for i in range(14):
        selected = energy_category == i
        point = dict(low=float(ENERGY_EDGES[i]),high=float(ENERGY_EDGES[i+1]),series={},prior_sensitivity={})
        for series,label in enumerate(SERIES):
            point["series"][label] = population(values[series],tails[series],selected,data[series//2],predictions[series//2] if series%2 else None)
            point["series"][label]["mean_uncertainty"] = interval(energy_mean_boot[:,series,i])
        for geometry,label in enumerate(("baseline","staggered")):
            point["prior_sensitivity"][label] = population(priors[geometry]["response"],priors[geometry]["response"],selected,data[geometry],priors[geometry])
        energy.append(point)
    controls = {}
    for name,category in (("signed_eta",bin_index(data[0]["eta"],np.linspace(-3,3,21))),
                          ("eta_sign",(data[0]["eta"]>=0).astype(int)),
                          ("sector",np.floor((data[0]["phi"]+math.pi/16)%(2*math.pi)/(math.pi/8)).astype(int))):
        controls[name] = {str(i): {label:population(values[k],tails[k],category==i,data[k//2],predictions[k//2] if k%2 else None)
                                  for k,label in enumerate(SERIES)} for i in sorted(set(category))}
    flat = width_boot.reshape(args.bootstrap,80)
    contrast_samples = np.concatenate([width_boot[:,a]-width_boot[:,b] for a,b,_ in CONTRASTS],axis=1)
    finite_widths=bool(np.isfinite(flat).all())
    finite_contrasts=bool(np.isfinite(contrast_samples).all())
    global_stats={}
    for k,label in enumerate(SERIES):
        entry=population(values[k],tails[k],np.ones(10000,dtype=bool),data[k//2],predictions[k//2] if k%2 else None)
        for j,key in enumerate(("mean","fractional_width","tail_fraction")):
            entry[key+"_uncertainty"]=interval(global_boot[:,k,j])
        global_stats[label]=entry
    result = dict(status="PROTOTYPE", events=10000,
        definition="Raw width=sample SD(S/Etrue)/mean; calibrated width=sample SD(Ecal/Etrue)/mean; all generated events retained",
        tail_definition="Pr(Ecal/Etrue<0.5); raw comparator uses training-only cross-fit scale S/R0; not unscaled silicon fraction",
        crossfit=dict(outer_folds=5,inner_folds=3,outer_seed=OUTER_SEED,inner_seed=INNER_SEED,ridge_lambdas=list(LAMBDAS),
            relative_gain_bounds=[.5,3],primary_prior="uniform",secondary_prior="inverse true energy in training only",energy_proxy_input=False),
        bootstrap=dict(replicates=args.bootstrap,seed=args.seed,method="joint whole-event multiplicities with fixed IDfolds; full preprocessing/innerselection/outermodel refit",
                       interval="approximate pointwise95% percentile; includes training uncertainty",wall_seconds=time.monotonic()-start),
        source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        producer_sha256=sha(__file__),calibration_core_sha256=sha(Path(__file__).with_name('staggered_calibration.py')),
        baseline_reference_sha256=sha(args.reference),
        feature_receipts={name:x[1] for name,x in zip(('baseline','staggered'),loaded)},
        models={name:p['records'] for name,p in zip(('baseline','staggered'),predictions)},
        secondary_models={name:p['records'] for name,p in zip(('baseline','staggered'),priors)},
        projections=projections,energy_slices=energy,controls=controls,global_statistics=global_stats,
        histogram_edges={k:v.tolist() for k,v in histogram_edges.items()},
        width_covariance_order=[f'{label}:{projection}:{i}' for label in SERIES for projection in projections for i in range(10)],
        width_covariance=np.cov(flat,rowvar=False).tolist() if finite_widths else None,
        contrast_covariance_order=[f'{label}:{projection}:{i}' for _,_,label in CONTRASTS for projection in projections for i in range(10)],
        contrast_covariance=np.cov(contrast_samples,rowvar=False).tolist() if finite_contrasts else None)
    args.output.mkdir(parents=True,exist_ok=False)
    save(args.output/'summary.json',result)
    np.savez_compressed(args.predictions_output, event=np.arange(10000),values=values,tails=tails,
                        baseline_gain=predictions[0]['gain'],staggered_gain=predictions[1]['gain'],
                        baseline_clipped=predictions[0]['clipped'],staggered_clipped=predictions[1]['clipped'])
    print('Completed matched four-way comparison and full refitting bootstrap',flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='stage',required=True)
    a=s.add_parser('fit');a.add_argument('--features',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    a=s.add_parser('compare');a.add_argument('--baseline',type=Path,required=True);a.add_argument('--staggered',type=Path,required=True)
    a.add_argument('--output',type=Path,required=True);a.add_argument('--predictions-output',type=Path,required=True)
    a.add_argument('--reference',type=Path,default=ROOT/'docs/validation/ecal10k/summary.json')
    a.add_argument('--bootstrap',type=int,default=1000);a.add_argument('--seed',type=int,default=1338000)
    args=p.parse_args();globals()['fit_only' if args.stage=='fit' else 'compare'](args)


if __name__=='__main__':main()
