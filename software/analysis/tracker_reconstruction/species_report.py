"""Reproduce the DES041 five-sample transport/species report from retained arrays."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np
from analyze import rate

ROOT = Path(__file__).resolve().parents[3]
PTS = (1, 5, 10, 100)
MATRIX = (("fatras", "muon"), ("fatras", "electron"),
          ("geant4", "muon"), ("geant4", "electron"), ("geant4", "pion"))
PARAMETERS = ("d0", "z0", "phi", "theta", "q/p", "t0")
OUTCOMES = {0: "Alive", 1: "KilledInteraction", 2: "KilledVolumeExit",
            3: "KilledTime", 4: "KilledSecondaryParticle", -1: "MissingPrimaryRecord"}
OLD_REFERENCE = ROOT / "docs/validation/tracker-reconstruction/validation/selected"


def label(simulation, particle):
    return f"{'Geant4' if simulation == 'geant4' else 'Fatras'} single {particle}s"


def case_directory(data, simulation, particle, muon_reference=OLD_REFERENCE):
    return Path(muon_reference) if (simulation, particle) == ("fatras", "muon") else Path(data) / simulation / particle


def read_summary(directory):
    path = Path(directory) / "summary.json"
    if path.exists():
        return json.loads(path.read_text()), path
    path = path.with_suffix(".json.gz")
    return json.loads(gzip.decompress(path.read_bytes())), path


def distribution(values, thresholds=(), display_window=None):
    """Describe every finite value; a display range is never a selection."""
    values = np.asarray(values)
    finite = values[np.isfinite(values)]
    result = {"entries": int(values.size), "finite_entries": int(finite.size),
              "nonfinite_entries": int(values.size - finite.size),
              "mean_bias": None, "median_bias": None, "population_sd": None,
              "central68_halfwidth": None, "min": None, "max": None,
              "quantile_probabilities": [.001, .01, .16, .5, .84, .99, .999], "quantiles": None,
              "absolute_tail_counts": {str(t): int(np.sum(np.abs(finite) > t)) for t in thresholds}}
    if finite.size:
        quantiles = np.quantile(finite, result["quantile_probabilities"])
        result.update(mean_bias=float(np.mean(finite)), median_bias=float(np.median(finite)),
            population_sd=float(np.std(finite)), central68_halfwidth=float((quantiles[4] - quantiles[2]) / 2),
            min=float(np.min(finite)), max=float(np.max(finite)), quantiles=quantiles.tolist())
    if display_window is not None:
        lo, hi = display_window
        result["display_window"] = [lo, hi]
        result["display_underflow"] = int(np.sum(finite < lo))
        result["display_overflow"] = int(np.sum(finite > hi))
    return result


def primary_outcomes(arrays, mask):
    if "primary_outcome" not in arrays:
        return {"available": False, "reason": "Not retained in immutable original Fatras muon reference"}
    outcomes = arrays["primary_outcome"]
    n = int(np.sum(mask))
    codes = sorted(set(OUTCOMES) | set(int(c) for c in np.unique(outcomes)))
    killed = mask & (outcomes == 3)
    result = {"available": True, "events": n,
        "codes": {str(code): {"name": OUTCOMES.get(code, "UnknownOutcome"),
            "rate_all_generated": rate(int(np.sum(mask & (outcomes == code))), n)} for code in codes},
        "killed_time": {"incidence_all_generated": rate(int(np.sum(killed)), n),
            "reconstructed_given_killed_time": rate(int(np.sum(killed & arrays["ambi_matched"].astype(bool))), int(np.sum(killed)))}}
    time_key = "primary_final_ct_mm" if "primary_final_ct_mm" in arrays else "final_ct_mm"
    position_key = "primary_final_position_mm" if "primary_final_position_mm" in arrays else "final_position_mm"
    if time_key not in arrays or position_key not in arrays:
        raise ValueError("Outcome records require final ct and final position arrays")
    position = arrays[position_key][killed]
    result["killed_time"].update(
        final_time_ns=distribution(arrays[time_key][killed] / 299.792458),
        final_radius_mm=distribution(np.hypot(position[:, 0], position[:, 1])),
        final_z_mm=distribution(position[:, 2]))
    return result


def sample_report(summary, arrays):
    n = len(arrays["eta"])
    if n != summary["events"]:
        raise ValueError("Array/event-summary denominator mismatch")
    matched = arrays["ambi_matched"].astype(bool)
    counts = summary["stages"]["ambi"]["counts"]
    for key in ("matched", "accepted", "fake", "secondary", "duplicates", "wrong_charge"):
        if int(np.sum(arrays["ambi_" + key])) != counts[key]:
            raise ValueError("Array/summary candidate count mismatch: " + key)
    reco = arrays["ambi_reco"]
    with np.errstate(divide="ignore", invalid="ignore"):
        relative_pt = (arrays["pt"] - np.abs(np.sin(reco[:, 3]) / reco[:, 4])) / arrays["pt"]

    def resolution(mask):
        subset = mask & matched
        return {"matched": int(np.sum(subset)),
            "d0_um": distribution(arrays["ambi_residual"][subset, 0] * 1000, (100., 1000.)),
            "z0_um": distribution(arrays["ambi_residual"][subset, 1] * 1000, (100., 1000.)),
            "relative_pt_truth_minus_reco": distribution(relative_pt[subset], (.1, .5, 1.))}

    def coverage(mask):
        return rate(int(np.sum(mask & matched & (arrays["ambi_inliers"] >= 10))), int(np.sum(mask)))

    all_events = np.ones(n, dtype=bool)
    stage = summary["stages"]["ambi"]
    result = {"events": n, "efficiency": stage["efficiency"],
        "conditional_efficiency": stage["conditional"], "conditional4_efficiency": stage["conditional4"],
        "counts": counts, "fake_event_incidence": stage["fake_event"],
        "duplicate_event_incidence": stage["duplicate_event"], "wrong_charge": stage["wrong_charge"],
        "candidate_fractions": {key: stage[key + "_candidate_fraction"] for key in ("fake", "secondary", "duplicates")},
        "duplicates_before_ambiguity": summary["stages"]["ckf"]["counts"]["duplicates"],
        "ge10_inliers_all_generated": coverage(all_events),
        "all_eta_resolution": resolution(all_events),
        "central_abs_eta_lt0p5": resolution(np.abs(arrays["eta"]) < .5),
        "pulls_all_eta": {name: distribution(arrays["ambi_pull"][matched, i], (3., 5.), (-6., 6.))
                          for i, name in enumerate(PARAMETERS)},
        "primary_outcomes": primary_outcomes(arrays, all_events), "eta_bins": [],
        "provenance": {key: summary.get(key) for key in ("seed", "profile", "native_source_revision", "source_sha256",
            "run_report_sha256", "events_sha256", "sample_sha256", "particle_configuration", "simulation", "species_audit")}}
    for bin_summary in summary["eta_bins"]:
        lo, hi = bin_summary["eta"]
        mask = (arrays["eta"] >= lo) & ((arrays["eta"] < hi) | ((hi == summary["eta_edges"][-1]) & (arrays["eta"] == hi)))
        if int(np.sum(mask)) != bin_summary["events"]:
            raise ValueError("Eta-bin summary/array denominator mismatch")
        result["eta_bins"].append({"eta": [lo, hi], "events": int(np.sum(mask)),
            "efficiency": bin_summary["stages"]["ambi"]["efficiency"],
            "conditional_efficiency": bin_summary["stages"]["ambi"]["conditional"],
            "wrong_charge": bin_summary["stages"]["ambi"]["wrong_charge"],
            "ge10_inliers_all_generated": coverage(mask), "resolution": resolution(mask),
            "primary_outcomes": primary_outcomes(arrays, mask)})
    return result


def _percent(value):
    return "unavailable" if value is None else f"{100 * value:.2f}%"


def _rate(record, interval=True):
    if record["value"] is None:
        return f"— ({record['numerator']}/{record['denominator']})"
    bounds = record.get("wilson95")
    return (_percent(record["value"]) + (f" [{100*bounds[0]:.2f}, {100*bounds[1]:.2f}]" if interval and bounds else ""))


def _number(value):
    return "—" if value is None else f"{value:.3g}"


def markdown(payload):
    lines = ["# Single-particle tracker reconstruction across transport models", "",
        "DES041 DRAFT / isolated PROTOTYPE. Human expert review and acceptance remain pending.", "",
        "The frozen `pt4-nominal-triplet` GBTS configuration reconstructs single muons, electrons and charged pions at pT 1/5/10/100 GeV on the maintained balanced PR104 geometry, at constant 3 T and uniform signed η∈[−4,4]. Frozen Gaussian digitization remains 2D for pixels/short strips and 1D for long strips. No species validation result enters seeder tuning.", "",
        "The Fatras muon sample is the immutable original reference. Every table uses each sample's own generated-event denominator; species and transport populations are compared without statistical pooling or an assumption of paired events.", "",
        "## Efficiencies and candidate categories", "",
        "Efficiencies show 95% Wilson intervals. Conditional efficiency requires ≥6 unique sensitive sensors and ≥3 physical pixel groups; the nested four-group result is retained in JSON. Quality/matching are frozen at ≥7 unique inliers, valid reference/covariance, purity ≥0.5 and completeness ≥0.5. Every generated primary remains in the headline denominator.", "",
        "| Sample | pT [GeV] | Efficiency [95% Wilson] | Conditional efficiency | Unmatched / accepted | Secondary matches | Duplicates after ambiguity | Wrong charge / matched |",
        "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for key, case in payload["samples"].items():
        for pt, row in case["pt_GeV"].items():
            c = row["counts"]
            lines.append(f"| {case['label']} | {pt} | {_rate(row['efficiency'])} | {_rate(row['conditional_efficiency'], False)} | {c['fake']}/{c['accepted']} | {c['secondary']} | {c['duplicates']} | {c['wrong_charge']}/{c['matched']} |")
    lines += ["", "Unmatched candidates are defined by the frozen double-matching rule and can include incomplete primary segments. Simulated-secondary matches remain separate from unmatched candidates; additional matches to a particle are duplicates. For interacting or decaying pions, primary efficiency refers to the original charged-pion identity and its own associated measurements. Daughter-only tracks do not count as a reconstructed primary. Mixed candidates can satisfy the frozen ≥50% primary-purity rule; daughter measurements are not reassigned to the primary identity. The analysis does not relabel a matched primary segment as a complete pre-interaction pion trajectory.", "",
        "Candidate fractions retain event-block bootstrap intervals in [performance.json](performance.json); fake-event rates include exact one-sided 95% limits for zero observations. Single-particle fake rates do not establish dense-event or pile-up performance.", "",
        "![All five population efficiencies](figures/efficiency-comparison.png)", "",
        "## Resolutions, bias and full distributions", "",
        "One deterministic matched-primary representative supplies all six bound parameters. Residuals are truth−reconstruction, with wrapped φ. Central 68% means (q84−q16)/2; these descriptive widths have no claimed confidence interval. Bias and tail statistics retain every finite matched entry, including wrong-charge tracks. Nonfinite entries are separately counted. Relative momentum residual is (pT,true−pT,reco)/pT,true.", "",
        "| Sample | pT [GeV] | Central d0 width / mean bias [µm] | Central z0 width / mean bias [µm] | Central relative pT width / mean bias | ≥10 inliers / all generated |",
        "|---|---:|---:|---:|---:|---:|"]
    for case in payload["samples"].values():
        for pt, row in case["pt_GeV"].items():
            central = row["central_abs_eta_lt0p5"]
            values = [f"{_number(central[p]['central68_halfwidth'])} / {_number(central[p]['mean_bias'])}" for p in ("d0_um", "z0_um")]
            momentum = central["relative_pt_truth_minus_reco"]
            values += [f"{_percent(momentum['central68_halfwidth'])} / {_percent(momentum['mean_bias'])}", _rate(row["ge10_inliers_all_generated"], False)]
            lines.append(f"| {case['label']} | {pt} | " + " | ".join(values) + " |")
    pion100 = payload["samples"]["geant4/pion"]["pt_GeV"]["100"]
    pion_qop = pion100["pulls_all_eta"]["q/p"]
    pion_momentum = pion100["all_eta_resolution"]["relative_pt_truth_minus_reco"]
    electron100 = payload["samples"]["fatras/electron"]["pt_GeV"]["100"]
    lines += ["", "The central table uses |η|<0.5. Full signed-η and all-acceptance distributions, mean/median biases, extrema, quantiles, d0/z0 tails beyond 100/1000 µm and relative-pT tails beyond 10/50/100% are retained in JSON. These thresholds describe tails and never select tracks.", "",
        f"Efficiency alone does not establish momentum or charge accuracy. At 100 GeV, Geant4 pions have {pion100['counts']['wrong_charge']}/{pion100['counts']['matched']} wrong-charge representatives, {pion_momentum['absolute_tail_counts']['0.5']} relative-pT errors beyond 50%, and {pion_qop['absolute_tail_counts']['5.0']} q/p pulls beyond 5σ (maximum absolute pull {_number(max(abs(pion_qop['min']), abs(pion_qop['max'])))}). These failures remain in every distribution; they are not confined to the far-forward acceptance.", "",
        f"The electron fit also needs further work: 100 GeV Fatras electrons have {electron100['counts']['wrong_charge']}/{electron100['counts']['matched']} wrong-charge representatives and {electron100['all_eta_resolution']['relative_pt_truth_minus_reco']['absolute_tail_counts']['0.5']} relative-pT errors beyond 50%. Their central |η|<0.5 relative-pT central68 width is {_percent(electron100['central_abs_eta_lt0p5']['relative_pt_truth_minus_reco']['central68_halfwidth'])}. Narrow electron pull cores coexist with these momentum failures; fitted uncertainties are not established as calibrated. This campaign benchmarks the frozen muon-selected reconstruction across species, without species-specific retuning.", "",
        "Each pull panel overlays 1/5/10/100 GeV and integrates over the full η acceptance. The displayed range is −6…6; density uses the full finite-entry denominator, so overflow is not renormalized away. Arrays retain all tails; JSON records underflow/overflow, extrema and |pull|>3/5. Bound time is native ct[mm], converted to ns with 299.792458 mm/ns; without timing measurements its pull is prior dominated.", ""]
    for simulation, particle in MATRIX[1:]:
        folder = f"figures/{simulation}/{particle}"
        lines += [f"### {label(simulation, particle)}", "", f"![Full integrated pulls]({folder}/pulls.png)", "",
            f"[Efficiency]({folder}/efficiency.pdf), [resolution versus η]({folder}/resolution-eta.pdf), [resolution versus pT]({folder}/resolution-pt.pdf), [pull width versus η]({folder}/pull-width-eta.pdf), [pull width versus pT]({folder}/pull-width-pt.pdf), [momentum/hits/fake bounds]({folder}/momentum-hits-fakes.pdf), [full pull-tail statistics]({folder}/pull-tails.json).", ""]
    lines += ["## Primary transport outcomes and time limits", "",
        "Native outcome codes are retained without removing events: Alive, KilledInteraction, KilledVolumeExit, KilledTime and KilledSecondaryParticle. `KilledInteraction` is the native outcome label and does not identify a particular hadronic interaction or decay process. Fatras can stop at its momentum threshold while retaining `Alive`; that label does not establish passage through the outer tracker. Missing primary records remain explicit. In the 5 GeV Fatras electron sample, events 3047 and 4270 reached the maximum propagation steps and lack final primary records; these are transport failures, not physical absorption, and both remain in the 5,000-event denominator. The immutable original Fatras muon sample lacks these extra outcome arrays; its outcomes are unavailable.", "",
        "| Sample | pT [GeV] | Recorded primary / generated | KilledInteraction | KilledVolumeExit | KilledTime [95% Wilson] | Reconstructed given KilledTime | KilledTime final t range [ns] |",
        "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for case in payload["samples"].values():
        for pt, row in case["pt_GeV"].items():
            outcome = row["primary_outcomes"]
            if not outcome["available"]:
                continue
            kt = outcome["killed_time"]
            missing = outcome["codes"]["-1"]["rate_all_generated"]["numerator"]
            timerange = kt["final_time_ns"]
            lines.append(f"| {case['label']} | {pt} | {row['events']-missing}/{row['events']} | {_rate(outcome['codes']['1']['rate_all_generated'], False)} | {_rate(outcome['codes']['2']['rate_all_generated'], False)} | {_rate(kt['incidence_all_generated'])} | {_rate(kt['reconstructed_given_killed_time'], False)} | {_number(timerange['min'])}…{_number(timerange['max'])} |")
    lines += ["", "Per-pT and signed-η outcome rates and KilledTime final ct, radius and z distributions are retained in JSON. The configured Geant4 simulation limit is 25 ns and the kill boundary is the highest tracking volume. These limits remain part of the benchmark. Their causal contribution to inefficiency has not been measured with an uncut control, and the time limit is not established as unbiased for electrons.", "",
        "## Model and validation boundaries", "",
        "Geant4 uses FTFP_BERT and the detailed maintained DD4hep tracker, including charged secondary hits and particles without hits. Fatras and reconstruction use the retained role-transported effective ACTS material map, including the homogeneous added-disc approximation. Differences therefore include the existing material representations; this campaign does not establish a fresh Geant4 material map.", "",
        "Fatras keeps its unchanged 0.5 GeV absolute-momentum cutoff and electromagnetic interactions. Its Bethe–Bloch ionization approximation is explicitly limited for electrons, and this electron sample is not precision electromagnetic-shower validation. Native electron hypotheses select the existing multicomponent bremsstrahlung-recovery CKF in one-way mode; muons and pions use ordinary two-way CKF. One-way electron processing avoids a demonstrated native reverse-state Jacobian FPE, without masking FPE checks. No separate GaussianSumFitter refit is scheduled.", "",
        "Task-owned SafeFatras preserves the native Bethe–Heitler sampling and updates while avoiding demonstrated libm underflow traps: the loss expression exp(−u)−1 returns its binary64 rounded result +0 for 0≤u<2⁻⁵⁴ and −1 for u>40. Other exponents use the original expression. Sampling draws, parent/photon updates, numerical build flags and FPE checks are preserved. All 15,000 native event audits and all nine ROOT tree contents at 1/5/10 GeV are bitwise identical to the original same-seed runs that failed the final FPE gate. Those failed attempts and independent numerical/replay checks remain in [diagnostics](diagnostics/); the validated sample uses the passing guard implementation.", "",
        "Gaussian response is species independent and unmerged. Electron showers and secondary-rich pion events do not include charge sharing or merging between nearby hits; comparisons therefore do not validate realistic shower digitization or dense-event reconstruction.", "",
        "All new samples use the native uint32 maximum ambiguity iteration budget, with the original shared-hit threshold and minimum hit count. Independent replay requires every native survivor to have fewer than three shared measurements. The immutable muon Fatras reference used 1,000 iterations; its independent 20,000-event replay finds zero shared measurements among survivors and at most two initial candidates, so that cap was not limiting. A separate electron shower smoke exhausted the old limit, motivating this pre-validation computation-budget correction. GBTS settings and physics cuts are unchanged.", "",
        "Source/config/runtime/input identities and actual native outcomes are retained in the run evidence. The historical field loaded_Geant4_version contains the observer header version; actual library hashes and CLI version identify the installed runtime. No claim is made that Geant4-internal floating-point exceptions are checked by ACTS event-algorithm FPE monitoring. Software checks and numerical results grant no human design approval.", ""]
    return "\n".join(lines)


def report(data, output, *, muon_reference=OLD_REFERENCE):
    data, output = Path(data), Path(output)
    samples = {}
    for simulation, particle in MATRIX:
        directory = case_directory(data, simulation, particle, muon_reference)
        case = {"label": label(simulation, particle), "simulation": simulation,
                "particle": particle, "pt_GeV": {}}
        for pt in PTS:
            sample_dir = directory / f"pt{pt}"
            summary, summary_path = read_summary(sample_dir)
            if (simulation, particle) != ("fatras", "muon"):
                if summary.get("simulation") != simulation or summary.get("particle_configuration", {}).get("name") != particle:
                    raise ValueError("Retained sample identity differs from directory: " + str(sample_dir))
            arrays_path = sample_dir / "events.npz"
            with np.load(arrays_path, allow_pickle=False) as arrays:
                row = sample_report(summary, arrays)
            row["input_sha256"] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in (summary_path, arrays_path)}
            case["pt_GeV"][str(pt)] = row
        samples[simulation + "/" + particle] = case
    payload = {"schema_version": 1, "status": "PROTOTYPE", "design": "DES-041 DRAFT; no human approval inferred",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "samples": samples,
        "uncertainty": "Per-sample Wilson intervals and retained event-block candidate bootstrap; no pooling across species, transports or momenta; resolution widths descriptive without confidence intervals",
        "tail_policy": "All finite matched entries; nonfinite counts explicit; no residual/pull/charge cuts",
        "parameter_order": list(PARAMETERS)}
    output.mkdir(parents=True, exist_ok=True)
    (output / "performance.json").write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    (output / "results.md").write_text(markdown(payload))
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="Directory for performance.json and results.md")
    parser.add_argument("--muon-reference", type=Path, default=OLD_REFERENCE)
    args = parser.parse_args()
    report(args.data, args.output, muon_reference=args.muon_reference)
