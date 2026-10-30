"""Retain and verify the frozen species/transport extension, without raw states."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
CASES=(("fatras","electron"),("geant4","muon"),("geant4","electron"),("geant4","pion"))
PTS=(1,5,10,100)


def digest(data):return hashlib.sha256(data).hexdigest()


def read(path):
    path=Path(path)
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix==".gz" else raw)


def retain(native,analysis,destination):
    native,analysis,destination=map(Path,(native,analysis,destination))
    reports={}
    for simulation,particle in CASES:
        for pt in PTS:
            relative=Path(simulation)/particle/f"pt{pt}"
            source=analysis/relative;target=destination/relative;target.mkdir(parents=True,exist_ok=True)
            report=read(native/relative/"run-report.json")
            if report["outcome"]!="completed":raise ValueError("Cannot retain failed case: "+str(relative))
            reports[str(relative)]=report
            (target/"summary.json.gz").write_bytes(gzip.compress((source/"summary.json").read_bytes(),mtime=0))
            shutil.copyfile(source/"events.npz",target/"events.npz")
            if simulation=="geant4":
                raw=(native/relative/"geant4-mapping.json").read_bytes()
                (target/"geant4-mapping.json.gz").write_bytes(gzip.compress(raw,mtime=0))
    destination.mkdir(parents=True,exist_ok=True)
    (destination/"native-reports.json.gz").write_bytes(gzip.compress(json.dumps(reports,separators=(",",":")).encode(),mtime=0))


def manifest(destination):
    destination=Path(destination)
    report={"schema_version":1,"status":"PROTOTYPE",
        "files_sha256":{str(p.relative_to(destination)):digest(p.read_bytes()) for p in sorted(destination.rglob("*")) if p.is_file() and p.name!="manifest.json"},
        "scope":"16 new5000event samples; immutable muonFatras reference is linked, never pooled as independent extra trials",
        "summary_encoding":"gzip preserves original summary/mapping bytes and source hashes",
        "raw_policy":"Native state/ROOT outputs remain ignored; full input/source/runtime/output hashes are retained"}
    (destination/"manifest.json").write_text(json.dumps(report,indent=2)+"\n")


def root_audit(native,analysis,destination):
    """Check actual persisted ROOT content and require the entire declared matrix."""
    from audit_root import audit
    import audit_root
    native,analysis,destination=map(Path,(native,analysis,destination));cases={}
    destination.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        for backend in ("fatras","geant4"):
            output=Path(temporary)/(backend+".json")
            audit(native/backend,analysis/backend,output)
            cases.update({backend+"/"+k:v for k,v in read(output)["cases"].items()})
    expected={f"{sim}/{particle}/pt{pt}" for sim,particle in CASES for pt in PTS}
    if set(cases)!=expected:raise ValueError("ROOT audit does not cover the complete species matrix")
    payload={"schema_version":1,"status":"PASS","source_revision":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        "source_sha256":digest(Path(audit_root.__file__).read_bytes()),"producer_sha256":digest(Path(__file__).read_bytes()),"cases":cases}
    (destination/"root-audit.json").write_text(json.dumps(payload,indent=2)+"\n")


def verify(data):
    data=Path(data);reports=read(data/"native-reports.json.gz");cache={};runtime={};sources=set();n=0
    for name,expected in read(data/"manifest.json")["files_sha256"].items():
        if digest((data/name).read_bytes())!=expected:raise ValueError("Artifact changed: "+name)
    frozen=read(ROOT/"docs/validation/tracker-reconstruction/frozen/validation-campaign.json")
    effective_gbts=read(ROOT/"docs/validation/tracker-reconstruction/native-validation-reports.json.gz")["selected/pt1"]["gbts_statistics"]["effective_configuration"]
    expected_cases={f"{sim}/{particle}/pt{pt}" for sim,particle in CASES for pt in PTS}
    if set(reports)!=expected_cases:raise ValueError("Incomplete declared species matrix")
    persistence=read(data/"root-audit.json")
    if persistence["status"]!="PASS" or set(persistence["cases"])!=expected_cases:raise ValueError("Incomplete ROOT persistence verification")
    for key,path in (("source_sha256","software/analysis/tracker_reconstruction/audit_root.py"),("producer_sha256","software/analysis/tracker_reconstruction/species_evidence.py")):
        if persistence[key]!=digest(subprocess.check_output(["git","show",persistence["source_revision"]+":"+path],cwd=ROOT)):raise ValueError("ROOT audit source identity changed")
    binaries={}
    for case,r in reports.items():
        simulation,particle,pt=case.split("/");directory=data/case
        s=read(directory/"summary.json.gz");a=np.load(directory/"events.npz",allow_pickle=False)
        momentum=float(pt.removeprefix("pt"))
        if r["pt_GeV"]!=momentum or s["pt_GeV"]!=momentum or not np.allclose(a["pt"],momentum,rtol=1e-12,atol=0):raise ValueError("Mislabeled momentum sample")
        if r["outcome"]!="completed" or r["events"]!=5000 or s["events"]!=5000:raise ValueError("Incomplete native sample")
        if r["phase"]!="validation" or s["seed"]!=r["seed"] or r["seed"]!=(133042 if simulation=="fatras" else 143042):raise ValueError("Wrong frozen validation split")
        if r["profile"]!="pt4-nominal-triplet" or s["profile"]!=r["profile"]:raise ValueError("Selected GBTS profile changed")
        c=r["campaign"]
        if c["particle"]!=particle or c["simulation"]!=simulation or s["simulation"]!=simulation:raise ValueError("Sample mislabeled")
        expected_campaign=read(data/"frozen"/("electron_campaign.json" if simulation=="fatras" else "geant4_campaign.json"))
        expected_campaign.update(particle=particle,simulation=simulation)
        if c!=expected_campaign:raise ValueError("Executed campaign differs from retained frozen protocol")
        for key in ("profiles","ckf","quality","matching","parameter_estimation","field_Bz_T","eta_range","phi_range_rad"):
            if c[key]!=frozen[key]:raise ValueError("Frozen benchmark changed: "+key)
        if c["ambiguity"]!={**frozen["ambiguity"],"maximum_iterations":4294967295}:raise ValueError("Ambiguity convergence budget changed")
        if (not s["ambiguity_audit"]["all_native_survivors_converged"] or
            np.any(a["ambiguity_max_shared_measurements"]>=c["ambiguity"]["maximum_shared_hits"])):raise ValueError("Truncated ambiguity resolution")
        g=r["gbts_statistics"];identity=g["particle_configuration"]
        if g["effective_configuration"]!=effective_gbts:raise ValueError("Actual native GBTS settings changed")
        if identity!=s["particle_configuration"] or identity["name"]!=particle or not s["species_audit"]["all_native_hypotheses_verified"]:raise ValueError("Unverified actual species")
        pdg={"muon":13,"electron":11,"pion":211}[particle]
        if identity["absolute_pdg"]!=pdg or set(map(int,s["species_audit"]["generated_pdgs"]))!={-pdg,pdg}:raise ValueError("Wrong generated species/charge coverage")
        if sum(s["species_audit"]["generated_pdgs"].values())!=5000:raise ValueError("Lost generated species entries")
        if g["effective_two_way"]!=(particle!="electron"):raise ValueError("Wrong species-dependent fit policy")
        if g["events"]!=5000 or g["retained_seeds"]!=s["stage_counts"]["seeds"]:raise ValueError("GBTS event/seed accounting mismatch")
        if digest(json.dumps(r,indent=2,allow_nan=False).encode()+b"\n")!=s["run_report_sha256"]:raise ValueError("Run report bytes changed")
        revision=r["source_revision"];sources.add(revision)
        def source_hash(relative):
            key=(revision,relative)
            if key not in cache:cache[key]=digest(subprocess.check_output(["git","show",revision+":"+relative],cwd=ROOT))
            return cache[key]
        for path,expected in r["source_sha256"].items():
            relative=path.split("/nodd-gen3-material-mapping/",1)[1]
            if relative.startswith("build/"):
                binaries.setdefault(relative,set()).add(expected)
            elif source_hash(relative)!=expected:raise ValueError("Executed source differs from launch revision: "+relative)
        if s["source_sha256"]!=source_hash("software/analysis/tracker_reconstruction/analyze.py"):raise ValueError("Reduction source differs from launch pin")
        if s["species_analysis_sha256"]!=source_hash("software/analysis/tracker_reconstruction/species.py"):raise ValueError("Species audit source differs from launch pin")
        for path,expected in r["runtime_sha256"].items():
            if path in runtime and runtime[path]!=expected:raise ValueError("Native runtime changed across cases")
            runtime[path]=expected
        for key in ("material-map.json","error-table.json","digitization.json"):
            if not r["preparation"]["baseline_semantic_equivalence"][key]:raise ValueError("Baseline material/response changed")
        if set(s["measurement_audit"]["systems"])!={str(i) for i in range(1,8)} or not s["measurement_audit"]["frozen_native_double_variances"]:raise ValueError("Incomplete detector/response audit")
        if len(a["event"])!=5000 or len(np.unique(a["event"]))!=5000:raise ValueError("Lost/duplicated generated events")
        persisted=persistence["cases"][case]
        if persisted["measurement_rows"]!=s["stage_counts"]["measurements"] or not persisted["exact_float32_variance_match"]:raise ValueError("ROOT measurements differ from event audit")
        expected_root={k:v for k,v in r["output_sha256"].items() if k.endswith(".root")}
        if len(expected_root)!=3 or persisted["root_sha256"]!=expected_root:raise ValueError("ROOT persistence evidence belongs to different native outputs")
        for stage in ("ckf","ambi"):
            counts=s["stages"][stage]["counts"]
            ps=persisted["stages"][stage]
            if ps["events"]!=5000 or ps["candidates"]!=counts["raw"] or ps["matched_parameter_marginals"]!=6*counts["matched"] or not ps["exact_float32_perigee_and_sigma_match"]:raise ValueError("ROOT perigee/covariance audit incomplete")
            for key in ("matched","accepted","fake","secondary","duplicates","wrong_charge"):
                if int(a[stage+"_"+key].sum())!=counts[key]:raise ValueError("Array/count mismatch: "+key)
            if s["stages"][stage]["efficiency"]["value"]!=counts["matched"]/5000:raise ValueError("Generated denominator changed")
            expected=a["truth"]-a[stage+"_reco"];expected[:,2]=(expected[:,2]+np.pi)%(2*np.pi)-np.pi
            if not np.array_equal(expected,a[stage+"_residual"],equal_nan=True):raise ValueError("Residual sign/wrapping changed")
            if not np.array_equal(expected/np.sqrt(a[stage+"_variance"]),a[stage+"_pull"],equal_nan=True):raise ValueError("Pull definition changed")
            for label,key in (("conditional","reconstructable"),("conditional4","reconstructable4")):
                mask=a[key].astype(bool);metric=s["stages"][stage][label]
                if (metric["numerator"],metric["denominator"])!=(int((mask&a[stage+"_matched"].astype(bool)).sum()),int(mask.sum())):raise ValueError("Conditional denominator changed")
        outcome_counts={str(k):int(np.sum(a["primary_outcome"]==k)) for k in range(5)}
        if any(v!=s["species_audit"]["primary_outcomes"].get(k,0) for k,v in outcome_counts.items()):raise ValueError("Primary outcome accounting changed")
        if simulation=="fatras":
            transport=g["transport_configuration"]
            if transport["upstream_source_revision"]!="355ea68493b326956756c9386d2fd9eaf9328568" or not c["species_extension"]["fatras_numerical_guard"]:raise ValueError("Unverified numerical repair")
            if transport["pMin_GeV"]!=.5 or not all(transport[k] for k in ("emScattering","emEnergyLossIonisation","emEnergyLossRadiation","emPhotonConversion")):raise ValueError("Fatras physics/cuts changed")
            if transport["numerical_sidecar"]["sha256"] not in r["source_sha256"].values():raise ValueError("SafeFatras binary not fingerprinted")
        if simulation=="geant4":
            mapping=read(directory/"geant4-mapping.json.gz")
            if digest(gzip.decompress((directory/"geant4-mapping.json.gz").read_bytes()))!=r["output_sha256"]["geant4-mapping.json"]:raise ValueError("Mapping source bytes changed")
            ids=mapping["mapped_geometry_ids"]
            if len(set(ids))!=46250 or set(ids)!=set(mapping["expected_geometry_ids"]) or mapping["duplicate_geometry_ids"] or not mapping["all_sensitive_surfaces_mapped"]:raise ValueError("Missing/duplicate Geant4 active mapping")
            if sum(mapping["mapped_by_system"].values())!=46250 or set(mapping["mapped_by_system"])!={str(i) for i in range(1,8)}:raise ValueError("Geant4 mapping system inventory changed")
            transport=g["transport_configuration"]
            if transport["native_geant4_events"]!=5000 or transport["physicsList"]!="FTFP_BERT" or not transport["production_cuts"]:raise ValueError("Unverified Geant4 runtime/event contract")
            if transport["materialMappings"] or transport["volumeMappings"]!=["nodd_active::"] or transport["killSecondaries"] or not transport["keepParticlesWithoutHits"]:raise ValueError("Geant4 sensitivity/secondary policy changed")
            environment=transport["environment"]
            installed=environment["installed_datasets"]
            if environment["check_datasets_returncode"]!=0 or len(installed)!=12 or any(not d["directory_exists"] or d["cli_status"]!="INSTALLED" for d in installed.values()):raise ValueError("Unverified installed Geant4 datasets")
        n+=5000
    if any(len(values)!=1 for values in binaries.values()):raise ValueError("Observation/seeding module changed during final matrix")
    print(f"PASS:16 species/transport cases, {n} generated events; frozen GBTS, actual hypotheses, full tails, native identities, Geant4 mapping/events and baseline response. Sources={sorted(sources)}")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("mode",choices=("retain","root-audit","manifest","verify"));p.add_argument("--data",type=Path,required=True);p.add_argument("--native",type=Path);p.add_argument("--analysis",type=Path);a=p.parse_args()
    if a.mode in ("retain","root-audit"):
        if a.native is None or a.analysis is None:p.error("Retention requires native and analysis directories")
        (retain if a.mode=="retain" else root_audit)(a.native,a.analysis,a.data)
    elif a.mode=="manifest":manifest(a.data)
    else:verify(a.data)
