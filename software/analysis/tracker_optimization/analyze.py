#!/usr/bin/env python3
"""Loss-accounted reduction of isolated Fatras optimisation experiments.

Uses the PR101 numerical observables but validates each new run's own identities.
No residual, pull, fit-quality or tail selection is applied.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import awkward as ak
import numpy as np
import uproot

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "software/analysis/truth_tracking"))
from export_profiles import (BARCODE, PARAMETERS, event_indices, flat,
                             audit_measurement_errors)
from metrics import classify_primary_barcodes, perigee_observables, statistics
from pull_histograms import BOUND, bound_pulls, common_edges, histogram


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def wilson(successes, trials):
    """Pointwise 95% Wilson interval, not a simultaneous search guarantee."""
    if not 0 <= successes <= trials:
        raise ValueError("Invalid binomial counts")
    if not trials:
        return {"value": None, "low": None, "high": None}
    p, z = successes / trials, 1.959963984540054
    den = 1 + z*z/trials
    c = (p + z*z/(2*trials))/den
    r = z*np.sqrt(p*(1-p)/trials + z*z/(4*trials*trials))/den
    return {"value": p, "low": float(max(0, c-r)), "high": float(min(1, c+r))}


def table(directory, name, tree):
    with uproot.open(directory / name) as stream:
        return stream[tree].arrays(library="ak")


def read_case(directory):
    """Join generated, primary proto, created and fitted rows by exact event ID."""
    directory = Path(directory)
    report = json.loads((directory / "run-report.json").read_text())
    if report["outcome"] != "completed" or report["simulation"] != "fatras":
        raise ValueError("Require a complete native Fatras experiment")
    # New study reports expose a file inventory; historical reference reports
    # expose provenance.files. Require an unambiguous hash for each ROOT input.
    files = report.get("provenance", {}).get("files", [])
    declared = report.get("output_sha256", {})
    used = ("particles.root", "particles_selected.root", "audit.root",
            "tracksummary_kf.root", "measurements.root")
    for name in used:
        expected = declared.get(name)
        if expected is None:
            matches = [x["sha256"] for x in files if x["name"] == name]
            if len(matches) != 1:
                raise ValueError("Missing/ambiguous input fingerprint: " + name)
            expected = matches[0]
        if sha256(directory / name) != expected:
            raise ValueError("Native output fingerprint mismatch: " + name)
    g = table(directory, "particles.root", "particles")
    a = table(directory, "audit.root", "audit")
    t = table(directory, "tracksummary_kf.root", "tracksummary")
    s = table(directory, "particles_selected.root", "particles")
    n = report["events"]
    ids = ak.to_numpy(g.event_id)
    if len(g) != n or not np.all(ak.to_numpy(ak.num(g.pt)) == 1):
        raise ValueError("Generated denominator is not one primary per event")
    ao = event_indices(ak.to_numpy(a.event_nr), ids)
    a = a[ao]
    if len(a) != n or not np.all(ak.to_numpy(a.generated) == 1):
        raise ValueError("Audit changed generated denominator")
    eta, phi, pt, charge = (flat(g, k) for k in ("eta", "phi", "pt", "q"))
    if (not np.all(np.isfinite(np.column_stack([eta, phi, pt, charge])))
            or not np.allclose(pt, report["pt_GeV"], rtol=2e-6, atol=1e-7)
            or not np.all(np.abs(charge) == 1)
            or not np.all(np.abs(flat(g, "particle_type")) == 13)
            or np.any(np.abs(eta) > 4)):
        raise ValueError("Generated particles differ from declared origin-muon gun")
    if any(np.any(flat(g, k) != 0) for k in ("vx", "vy", "vz")):
        raise ValueError("Non-origin truth needs perigee extrapolation")
    audit = {k: ak.to_numpy(a[k]).astype(np.int64) for k in
             ("generated", "simhits", "measurements", "selected", "fit_attempts",
              "fit_tracks", "invalid_covariance", "primary_measurements",
              "corrected_proto_measurements", "primary_measurement_associations_raw")}
    if any(np.any(x < 0) for x in audit.values()):
        raise ValueError("Negative stage count")
    for k in ("selected", "fit_attempts", "fit_tracks"):
        if np.any(audit[k] > 1):
            raise ValueError("More than one primary-derived candidate")
    if (np.any(audit["fit_tracks"] > audit["fit_attempts"])
            or np.any(audit["fit_attempts"] > audit["selected"])):
        raise ValueError("Candidate stages do not partition events")
    unique = np.array([len(set(row)) for row in ak.to_list(a.measurement_geometry_id)])
    lengths = ak.to_numpy(ak.num(a.measurement_geometry_id))
    if (not np.array_equal(unique, lengths)
            or not np.array_equal(unique, audit["primary_measurements"])
            or not np.array_equal(unique, audit["measurements"])):
        raise ValueError("Created measurements are not unique primary sensor IDs")
    if np.any(audit["corrected_proto_measurements"] != unique * audit["selected"]):
        raise ValueError("Corrected proto inputs lost or repeated primary measurements")
    si = event_indices(ids, ak.to_numpy(s.event_id))
    if len(s) != n or not np.array_equal(ak.to_numpy(ak.num(s.particle)), audit["selected"][si]):
        raise ValueError("Selected particles differ from audited selection")
    se = ak.to_numpy(ak.flatten(ak.broadcast_arrays(s.event_id, s.particle)[0]))
    gi = event_indices(ids, se)
    for k in BARCODE:
        if not np.array_equal(flat(s, k), flat(g, k)[gi]):
            raise ValueError("Selected particle differs from unique primary")
    te = ak.to_numpy(ak.flatten(ak.broadcast_arrays(t.event_nr, t.track_nr)[0]))
    ti = event_indices(ids, te)
    tc = np.bincount(ti, minlength=n)
    if (np.any(tc > 1) or not np.array_equal(tc, audit["fit_tracks"])
            or np.any(flat(t, "track_nr") != 0)
            or np.any(audit["selected"][ti] != 1)
            or np.any(audit["fit_attempts"][ti] != 1)):
        raise ValueError("Fitted output lacks unique primary-derived input")
    match = classify_primary_barcodes(
        np.column_stack([flat(t, "majorityParticleId_"+k) for k in BARCODE]),
        np.column_stack([flat(g, k)[ti] for k in BARCODE]))
    classification = flat(t, "trackClassification")
    if np.any(classification[match] != 1) or np.any(classification[~match] != 3):
        raise ValueError("Unexpected matched/zero-barcode Fake classification")
    np.testing.assert_allclose(flat(t, "t_eta")[match], eta[ti][match], rtol=2e-6, atol=2e-6)
    par = (*PARAMETERS, "eT")
    fitted = np.column_stack([flat(t, k+"_fit") for k in par])
    cov = np.stack([flat(t, "cov_"+p+"_"+q) for p in par for q in par], axis=1).reshape(-1, 6, 6)
    truth = np.column_stack([np.zeros(n), np.zeros(n), flat(g, "phi"),
                             flat(g, "theta"), flat(g, "q_over_p"), flat(g, "vt")])
    values, flags = perigee_observables(fitted[:, :5], truth[ti, :5], cov[:, :5, :5])
    pulls, flags6 = bound_pulls(fitted, truth[ti], cov)
    # Signed curvature remains well behaved when reconstructed q/p approaches0.
    theta, qop = fitted[:, 3], fitted[:, 4]
    true_curv = truth[ti, 4] / np.sin(truth[ti, 3])
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        curv = qop / np.sin(theta)
        dt, dq = -qop*np.cos(theta)/np.sin(theta)**2, 1/np.sin(theta)
        cv = dt*dt*cov[:, 3, 3]+dq*dq*cov[:, 4, 4]+2*dt*dq*cov[:, 3, 4]
        values["q_over_pt_relative"] = {"residual": (curv-true_curv)/np.abs(true_curv),
            "pull": (curv-true_curv)/np.sqrt(cv)}
    has = flat(t, "hasFittedParams").astype(bool)
    values["q_over_pt_relative"]["pull"][~flags6["valid_covariance"] | ~(cv > 0)] = np.nan
    aligned = {}
    for k, pair in values.items():
        aligned[k] = {}
        for observable, data in pair.items():
            full = np.full(n, np.nan)
            full[ti] = np.where(has, data, np.nan)
            aligned[k][observable] = full
    all_pulls = {}
    for j, k in enumerate(BOUND):
        full = np.full(n, np.nan)
        full[ti] = np.where(has, pulls[:, j], np.nan)
        all_pulls[k] = full
    all_pulls["pt_relative"] = -aligned["pt_relative"]["pull"]
    used_hits = np.zeros(n, dtype=int)
    used_hits[ti] = flat(t, "nMeasurements").astype(int)
    if np.any(used_hits > unique):
        raise ValueError("Fit used more measurements than primary created")
    wrong = np.zeros(n, dtype=bool)
    wrong[ti] = flags["wrong_charge"] & has
    valid = np.zeros(n, dtype=bool)
    valid[ti] = flags6["valid_covariance"] & has & flags6["finite_parameters"]
    table_path = directory / "error-table.json"
    error_audit = audit_measurement_errors(directory / "measurements.root", json.loads(table_path.read_text())) if table_path.exists() else None
    metadata = {"run_report_sha256": sha256(directory/"run-report.json"),
        "events": n, "pt_GeV": report["pt_GeV"],
        "native_unmatched_event_ids": te[~match].astype(int).tolist(),
        "measurement_error_audit": error_audit,
        "counts": {k: int(x.sum()) for k, x in audit.items()},
        "source_files": {k: sha256(directory/k) for k in used}}
    return {"metadata": metadata, "event_id": ids, "eta": eta, "phi": phi,
            "pt": pt, "charge": charge, "created": unique, "used": used_hits,
            "incident_records": audit["simhits"], "proto": audit["corrected_proto_measurements"],
            "fitted": tc.astype(bool), "valid_covariance": valid, "wrong_charge": wrong,
            "values": aligned, "pulls": all_pulls}


def summarize(case, mask, rng, bootstrap):
    n = int(mask.sum())
    result = {"generated": n, "fit_tracks": int(case["fitted"][mask].sum()),
              "wrong_charge": int(case["wrong_charge"][mask].sum()),
              "invalid_covariance": int(np.sum(mask & case["fitted"] & ~case["valid_covariance"])),
              "stages": {}, "quantities": {}}
    for stage in ("incident_records", "created", "proto", "used"):
        hits = case[stage][mask]
        result["stages"][stage] = {"sum": int(hits.sum()),
            "ge10": wilson(int(np.sum(hits >= 10)), n),
            "hit_counts": {str(int(v)): int(c) for v,c in zip(*np.unique(hits, return_counts=True))}}
    for k, pair in case["values"].items():
        result["quantities"][k] = {name: statistics(data[mask & case["fitted"]],
            bootstrap_replicates=bootstrap, rng=rng) for name, data in pair.items()}
    return result


def reduce(case, bootstrap=100):
    rng = np.random.default_rng(74042)
    result = {**case["metadata"], "global": summarize(case, np.ones(len(case["eta"]), dtype=bool), rng, bootstrap)}
    for name, data, edges in (("eta", case["eta"], np.linspace(-4,4,33)),
                              ("abs_eta", np.abs(case["eta"]), np.arange(0,4.1,.5)),
                              ("phi", case["phi"], np.linspace(-np.pi,np.pi,17))):
        result[name] = []
        for j,(lo,hi) in enumerate(zip(edges[:-1],edges[1:])):
            mask = (data >= lo) & ((data <= hi) if j == len(edges)-2 else (data < hi))
            row = summarize(case, mask, rng, bootstrap)
            row.update(low=float(lo), high=float(hi))
            result[name].append(row)
        if sum(x["generated"] for x in result[name]) != len(case["eta"]):
            raise ValueError("Bins do not partition generated denominator")
    return result


def paired_comparison(base, candidate, bootstrap=400):
    """Paired bootstrap only after checking exact generated event and gun values."""
    for key in ("event_id", "eta", "phi", "pt", "charge"):
        if not np.array_equal(base[key], candidate[key]):
            raise ValueError("Paired comparison requires identical generated "+key)
    rows, rng = [], np.random.default_rng(174042)
    edges = np.arange(0,4.1,.5)
    for low,high in [(0.,4.), *zip(edges[:-1],edges[1:])]:
        mask = (np.abs(base["eta"]) >= low) & (np.abs(base["eta"]) < high)
        ix = np.flatnonzero(mask)
        row = {"low":float(low), "high":float(high), "generated":len(ix), "quantities":{}}
        if not len(ix):
            rows.append(row); continue
        change = (candidate["created"][ix] >=10).astype(float)-(base["created"][ix] >=10)
        row["coverage_change"] = float(change.mean())
        row["coverage_change_se"] = float(change.std(ddof=1)/np.sqrt(len(change))) if len(change)>1 else None
        for q in ("d0","z0","pt_relative","q_over_pt_relative"):
            x,y = base["values"][q]["residual"][ix], candidate["values"][q]["residual"][ix]
            common=np.isfinite(x)&np.isfinite(y)
            def width(a):
                a=a[np.isfinite(a)]
                return float(np.diff(np.quantile(a,[.15865525393145707,.8413447460685429]))[0]/2) if len(a)>=30 else np.nan
            w0,w1=width(x),width(y)
            ratios=[]
            for _ in range(bootstrap):
                j=rng.integers(len(ix),size=len(ix)); a,b=width(x[j]),width(y[j])
                ratios.append(b/a)
            finite=np.array(ratios)[np.isfinite(ratios)]
            row["quantities"][q]={"baseline_width68":float(w0) if np.isfinite(w0) else None,
                "candidate_width68":float(w1) if np.isfinite(w1) else None,
                "ratio":float(w1/w0) if np.isfinite(w1/w0) else None,
                "ratio_bootstrap95":np.quantile(finite,[.025,.975]).tolist() if len(finite) else None,
                "common_survivors":int(common.sum()),
                "common_survivor_width68":[width(x[common]),width(y[common])] if common.sum()>=30 else [None,None]}
        rows.append(row)
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--case", action="append", required=True, help="LABEL=directory")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--bootstrap", type=int, default=100)
    args=p.parse_args()
    cases={}
    for spec in args.case:
        label,path=spec.split("=",1)
        if label in cases: raise ValueError("Duplicate case label")
        cases[label]=read_case(Path(path))
    edges={q:common_edges([c["pulls"][q] for c in cases.values()],5.,.1,16) for q in (*BOUND,"pt_relative")}
    output={"schema_version":1,"status":"PROTOTYPE", "samples":{}, "pull_edges":{q:x.tolist() for q,x in edges.items()},
        "source_revision":subprocess.check_output(["git","-C",str(ROOT),"rev-parse","HEAD"],text=True).strip(),
        "source_sha256":sha256(__file__),"bootstrap_replicates":args.bootstrap,
        "notes":["Coverage uses all generated events; physical sensor IDs counted once.",
                 "Resolution conditional on fitted tracks; no tail/quality cuts.",
                 "Pull sign truth-minus-fit, wrapped phi, full fitted covariance; time is a prior diagnostic.",
                 "Pointwise95% Wilson coverage and event-bootstrap resolution errors."]}
    for label,case in cases.items():
        row=reduce(case,args.bootstrap)
        row["pulls"]={q:histogram(x,edges[q],5.) for q,x in case["pulls"].items()}
        output["samples"][label]=row
        print(label,row["global"]["stages"]["created"]["ge10"]["value"],flush=True)
    output["paired_comparisons"]={}
    for label,case in cases.items():
        prefix,sep,pt=label.rpartition("-pt")
        baseline=cases.get("baseline-pt"+pt)
        if sep and prefix!="baseline" and baseline is not None:
            output["paired_comparisons"][label]=paired_comparison(baseline,case,args.bootstrap)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(gzip.compress((json.dumps(output,allow_nan=False,separators=(",",":"))+"\n").encode(),mtime=0))


if __name__=="__main__": main()
