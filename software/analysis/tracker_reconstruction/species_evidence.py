"""Retain and verify the frozen species/transport extension, without raw states."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
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


def verify(data):
    data=Path(data);reports=read(data/"native-reports.json.gz");cache={};runtime={};sources=set();n=0
    for name,expected in read(data/"manifest.json")["files_sha256"].items():
        if digest((data/name).read_bytes())!=expected:raise ValueError("Artifact changed: "+name)
    frozen=read(ROOT/"docs/validation/tracker-reconstruction/frozen/validation-campaign.json")
    effective_gbts=read(ROOT/"docs/validation/tracker-reconstruction/native-validation-reports.json.gz")["selected/pt1"]["gbts_statistics"]["effective_configuration"]
    expected_cases={f"{sim}/{particle}/pt{pt}" for sim,particle in CASES for pt in PTS}
    if set(reports)!=expected_cases:raise ValueError("Incomplete declared species matrix")
    binaries={}
    for case,r in reports.items():
        simulation,particle,pt=case.split("/");directory=data/case
        s=read(directory/"summary.json.gz");a=np.load(directory/"events.npz",allow_pickle=False)
        if r["outcome"]!="completed" or r["events"]!=5000 or s["events"]!=5000:raise ValueError("Incomplete native sample")
        if r["phase"]!="validation" or s["seed"]!=r["seed"] or r["seed"]!=(133042 if simulation=="fatras" else 143042):raise ValueError("Wrong frozen validation split")
        if r["profile"]!="pt4-nominal-triplet" or s["profile"]!=r["profile"]:raise ValueError("Selected GBTS profile changed")
        c=r["campaign"]
        if c["particle"]!=particle or c["simulation"]!=simulation or s["simulation"]!=simulation:raise ValueError("Sample mislabeled")
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
        for stage in ("ckf","ambi"):
            counts=s["stages"][stage]["counts"]
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
        if simulation=="geant4":
            mapping=read(directory/"geant4-mapping.json.gz")
            if digest(gzip.decompress((directory/"geant4-mapping.json.gz").read_bytes()))!=r["output_sha256"]["geant4-mapping.json"]:raise ValueError("Mapping source bytes changed")
            ids=mapping["mapped_geometry_ids"]
            if len(set(ids))!=46250 or set(ids)!=set(mapping["expected_geometry_ids"]) or mapping["duplicate_geometry_ids"] or not mapping["all_sensitive_surfaces_mapped"]:raise ValueError("Missing/duplicate Geant4 active mapping")
            if sum(mapping["mapped_by_system"].values())!=46250 or set(mapping["mapped_by_system"])!={str(i) for i in range(1,8)}:raise ValueError("Geant4 mapping system inventory changed")
            transport=g["transport_configuration"]
            if transport["native_geant4_events"]!=5000 or transport["physicsList"]!="FTFP_BERT" or not transport["production_cuts"]:raise ValueError("Unverified Geant4 runtime/event contract")
            if transport["materialMappings"] or transport["volumeMappings"]!=["nodd_active::"] or transport["killSecondaries"] or not transport["keepParticlesWithoutHits"]:raise ValueError("Geant4 sensitivity/secondary policy changed")
        n+=5000
    if any(len(values)!=1 for values in binaries.values()):raise ValueError("Observation/seeding module changed during final matrix")
    print(f"PASS:16 species/transport cases, {n} generated events; frozen GBTS, actual hypotheses, full tails, native identities, Geant4 mapping/events and baseline response. Sources={sorted(sources)}")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("mode",choices=("retain","manifest","verify"));p.add_argument("--data",type=Path,required=True);p.add_argument("--native",type=Path);p.add_argument("--analysis",type=Path);a=p.parse_args()
    if a.mode=="retain":
        if a.native is None or a.analysis is None:p.error("Retention requires native and analysis directories")
        retain(a.native,a.analysis,a.data)
    elif a.mode=="manifest":manifest(a.data)
    else:verify(a.data)
