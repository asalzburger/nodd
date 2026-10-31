#!/usr/bin/env python3
"""Compose the frozen DES041 ROOT persistence audit for DES042 flat cases.

Usage: root_audit.py --native NATIVE_PARENT --data RETAINED --output AUDIT.json
Repeat with --verify for an exact re-audit. --pilot requires four pitches of
one population/momentum, two generated events each, and optional ROOT writers.
Only temporary views and the explicitly requested new JSON output are written.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile
from types import ModuleType


ROOT = Path(__file__).resolve().parents[3]
INPUT_REVISION = "8c45136098d1e4d407c4d2f96e3590bb78eb6b75"
SOURCES = {
    "software/analysis/tracker_reconstruction/audit_root.py": "f846edf1127a186565fa4bfd42797138aa5e3dfc652a3b55354d85395fbd4439",
    "software/analysis/strixel_reconstruction/analyze.py": "52378dab3da4e1838b499a9add3fd09c9f251e1d9412539e83880e5b8c073df5",
    "software/analysis/strixel_reconstruction/runtime.py": "346e0fe6631e777f271642b5aaa25af7dc7bd271c8bd7961ac9e309d3d7c7ce7",
    "software/analysis/strixel_reconstruction/campaign.py": "5b167712c0a171849e60c42b0f9626e1bead0ac12c7a5ea134509dc119d1d319",
}
ROOT_FILES = {"hits.root", "measurements.root", "tracksummary_ckf.root", "tracksummary_ambi.root"}
VALIDATOR = "software/analysis/strixel_reconstruction/analyze.py"


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def read_gzip(path):
    return json.loads(gzip.decompress(Path(path).read_bytes()))


def source_gate():
    actual = {name: (hashlib.sha256(pinned_validator_bytes()).hexdigest() if name == VALIDATOR else
                     digest(ROOT / name)) for name in SOURCES}
    if actual != SOURCES:
        raise ValueError("Pinned ROOT audit/analyzer/runtime/campaign source changed")
    return {**actual, "software/analysis/strixel_reconstruction/root_audit.py": digest(__file__)}


def pinned_validator_bytes():
    body = subprocess.check_output(["git", "show", INPUT_REVISION + ":" + VALIDATOR], cwd=ROOT)
    if hashlib.sha256(body).hexdigest() != SOURCES[VALIDATOR]:
        raise ValueError("Pinned analyzer validator Git object differs from assignment")
    return body


def validator_module():
    # Offline analysis may receive separately authorized fixes while native
    # source HEAD stays fixed. Execute only this exact matrix/config/array gate.
    module = ModuleType("des042_pinned_analysis_for_root")
    module.__file__ = str(ROOT / VALIDATOR)
    exec(compile(pinned_validator_bytes(), module.__file__, "exec"), module.__dict__)
    return module


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inside(base, relative):
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()) or not path.is_file():
        raise ValueError("Unsafe or missing audit input: " + str(relative))
    return path


def reference_binding(data, item, native_case, report, analyzer):
    """Bind exact raw native report bytes to the portable retained inventory."""
    name = analyzer.case_name(analyzer.case_identity(report))
    if item["case"] != name or report.get("case_id") != name or native_case.name != name:
        raise ValueError("Native/retained case identity binding differs")
    if (report.get("simulation") != report["campaign"]["simulation"] or
            report.get("particle") != report["campaign"]["particle"]):
        raise ValueError("Native top-level population differs from campaign")
    report_hash = digest(native_case / "run-report.json")
    if item["run_report_sha256"] != report_hash or item["report"] != analyzer.sanitize(report):
        raise ValueError("Native report differs from retained reference binding")
    if report.get("outcome") != "completed" or not re.fullmatch(r"[0-9a-f]{40}", report.get("source_revision", "")):
        raise ValueError("Require completed native case with a full source revision")
    if report.get("input_revision") != analyzer.INPUT_REVISION:
        raise ValueError("Native scientific input revision differs")
    expected_paths = {"events_file": f"cases/{name}/events.npz",
                      "summary_file": f"cases/{name}/summary.json.gz",
                      "configuration_file": f"cases/{name}/configuration.json.gz"}
    if any(item.get(key) != value for key, value in expected_paths.items()):
        raise ValueError("Retained case reference points outside its canonical case")
    if set(item["files"]) != set(expected_paths.values()):
        raise ValueError("Retained file hash coverage differs from the three case artifacts")
    for relative, expected in item["files"].items():
        if digest(inside(data, relative)) != expected:
            raise ValueError("Retained artifact hash differs: " + relative)
    summary = read_gzip(data / item["summary_file"])
    if (summary["events"] != report["events"] or summary["pt_GeV"] != report["pt_GeV"] or
            summary["seed"] != report["seed"] or summary["profile"] != report["profile"] or
            summary["native_source_revision"] != report["source_revision"] or
            summary["run_report_sha256"] != report_hash or
            summary["events_sha256"] != report["output_sha256"]["events.jsonl.gz"]):
        raise ValueError("Retained summary differs from native case reference")
    if hashlib.sha256(canonical(summary)).hexdigest() != item["native_summary_sha256"]:
        raise ValueError("Retained summary differs from independently reduced native summary")
    configuration = read_gzip(data / item["configuration_file"])
    for filename in ("error-table.json", "digitization.json", "gbts/config.json"):
        native_path = inside(native_case, filename)
        expected = report["prepared_input_sha256"].get(filename)
        if expected is None or digest(native_path) != expected:
            raise ValueError("Prepared ROOT audit configuration hash differs: " + filename)
        if configuration[filename] != json.loads(native_path.read_text()):
            raise ValueError("Retained/native configuration reference differs: " + filename)
    return name, summary, configuration


def declared_source_binding(reports):
    revisions = {report.get("source_revision") for report in reports}
    if len(revisions) != 1 or not re.fullmatch(r"[0-9a-f]{40}", next(iter(revisions)) or ""):
        raise ValueError("Native matrix must share one full declared source revision")
    revision = next(iter(revisions))
    for relative in ("software/analysis/strixel_reconstruction/runtime.py",
                     "software/analysis/strixel_reconstruction/campaign.py"):
        try:
            body = subprocess.check_output(["git", "show", revision + ":" + relative], cwd=ROOT,
                                           stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as error:
            raise ValueError("Declared native source commit is unavailable for audit: " + revision) from error
        expected = hashlib.sha256(body).hexdigest()
        if expected != SOURCES[relative]:
            raise ValueError("Declared executing native source differs from the pinned scientific implementation")
        for report in reports:
            observed = [value for name, value in report["source_sha256"].items()
                        if name.endswith("/" + relative)]
            if observed != [expected]:
                raise ValueError("Executing native source hash differs from its declared commit: " + relative)
    return revision


def root_coverage(native_case, report):
    """Every actual ROOT file must be declared, present and content-identical."""
    expected = {name: value for name, value in report["output_sha256"].items() if name.endswith(".root")}
    actual = {path.name for path in native_case.glob("*.root") if path.is_file()}
    if not ROOT_FILES.issubset(expected) or set(expected) != actual:
        raise ValueError("Incomplete or undeclared ROOT output coverage; require --write-root native cases")
    for name, value in expected.items():
        if digest(inside(native_case, name)) != value:
            raise ValueError("Actual ROOT output differs from native report: " + name)
    return expected


def prepare_bindings(native, data, inventory, analyzer, pilot=False):
    """Run the pinned new analyzer's matrix/engine/config/array gates first."""
    import numpy as np
    items = inventory["reports"]
    names = [item["case"] for item in items]
    if len(names) != len(set(names)):
        raise ValueError("Repeated retained case reference")
    reports = [item["report"] for item in items]
    analyzer.validate_matrix(reports, pilot)
    if pilot and any(report["events"] != 2 for report in reports):
        raise ValueError("ROOT audit pilot requires exactly two generated events/case")
    if (not re.fullmatch(r"[0-9a-f]{64}", inventory.get("retention_source_sha256", "")) or
            inventory.get("input_revision") != analyzer.INPUT_REVISION or
            inventory.get("native_analyzer_sha256") != analyzer.NATIVE_ANALYZER_SHA256 or
            inventory.get("frozen_contract") != analyzer.frozen_contract()):
        raise ValueError("Retained analyzer/frozen-contract provenance differs from the pinned source")
    paths = sorted(native.glob("*/run-report.json"))
    native_reports = [json.loads(path.read_text()) for path in paths]
    analyzer.validate_matrix(native_reports, pilot)
    declared_source_binding(native_reports)
    if {path.parent.name for path in paths} != set(names):
        raise ValueError("Native and retained exact case coverage differs")
    if {path.name for path in native.iterdir() if path.is_dir()} != set(names):
        raise ValueError("Native case-directory coverage differs from inventory")
    if {path.name for path in (data / "cases").iterdir() if path.is_dir()} != set(names):
        raise ValueError("Retained case-directory coverage differs from inventory")
    by_name = {item["case"]: item for item in items}
    bindings = {}
    for path, report in zip(paths, native_reports):
        native_case = path.parent.resolve()
        if not native_case.is_relative_to(native):
            raise ValueError("Native case escapes declared parent")
        analyzer.validate_engine(report, inventory["frozen_contract"])
        name, summary, config = reference_binding(data, by_name[path.parent.name], native_case, report, analyzer)
        with np.load(data / by_name[name]["events_file"], allow_pickle=False) as source:
            arrays = {key: source[key] for key in source.files}
        analyzer.verify_arrays(arrays, summary)
        roots = root_coverage(native_case, report)
        bindings[name] = {"native_case": native_case, "item": by_name[name], "summary": summary,
            "roots": roots, "run_report_sha256": digest(path),
            "native_configuration_sha256": {filename: report["prepared_input_sha256"][filename]
                for filename in ("error-table.json", "digitization.json", "gbts/config.json")}}
    identities = {analyzer.case_identity(item["report"])[:3] for item in items}
    for identity in sorted(identities):
        selected = sorted((item for item in items if analyzer.case_identity(item["report"])[:3] == identity),
                          key=lambda item: item["report"]["pitch_mm"])
        analyzer.validate_configurations(selected, [read_gzip(data / item["configuration_file"]) for item in selected])
    return bindings


def compose_audit(native, data, pilot=False):
    native, data = Path(native).resolve(), Path(data).resolve()
    sources = source_gate()
    analyzer = validator_module()
    auditor = load_module("des041_pinned_root_auditor", ROOT / "software/analysis/tracker_reconstruction/audit_root.py")
    inventory_path = data / "native-reports.json.gz"
    inventory_hash = digest(inventory_path)
    inventory = read_gzip(inventory_path)
    bindings = prepare_bindings(native, data, inventory, analyzer, pilot)
    with tempfile.TemporaryDirectory(prefix="des042-root-audit-") as temporary:
        view = Path(temporary)
        native_view, analysis_view = view / "native", view / "analysis"
        for name, binding in bindings.items():
            native_parent = native_view / name; native_parent.mkdir(parents=True)
            (native_parent / "run").symlink_to(binding["native_case"], target_is_directory=True)
            analysis_case = analysis_view / name / "run"; analysis_case.mkdir(parents=True)
            (analysis_case / "summary.json").write_bytes(canonical(binding["summary"]) + b"\n")
            (analysis_case / "events.npz").symlink_to(data / binding["item"]["events_file"])
        result_path = view / "frozen-audit.json"
        auditor.audit(native_view, analysis_view, result_path)
        original = json.loads(result_path.read_text())
    if (original.get("status") != "PASS" or original.get("source_sha256") != SOURCES[
            "software/analysis/tracker_reconstruction/audit_root.py"] or
            set(original["cases"]) != {name + "/run" for name in bindings}):
        raise ValueError("Frozen ROOT auditor returned incomplete case coverage or source identity")
    for name, binding in bindings.items():
        if original["cases"][name + "/run"]["root_sha256"] != binding["roots"]:
            raise ValueError("Frozen ROOT auditor did not cover exactly the bound native ROOT files")
        report = json.loads((binding["native_case"] / "run-report.json").read_text())
        if digest(binding["native_case"] / "run-report.json") != binding["run_report_sha256"]:
            raise ValueError("Native report changed during ROOT audit")
        root_coverage(binding["native_case"], report)
        for relative, expected in binding["native_configuration_sha256"].items():
            if digest(inside(binding["native_case"], relative)) != expected:
                raise ValueError("Native configuration changed during ROOT audit")
        for relative, expected in binding["item"]["files"].items():
            if digest(inside(data, relative)) != expected:
                raise ValueError("Retained artifact changed during ROOT audit")
    if digest(inventory_path) != inventory_hash or source_gate() != sources:
        raise ValueError("Inventory or audit source changed during ROOT audit")
    return {"schema_version": 1, "status": "PASS", "study_status": "PROTOTYPE", "pilot": pilot,
        "input_revision": INPUT_REVISION,
        "native_source_revisions": sorted({binding["item"]["report"]["source_revision"] for binding in bindings.values()}),
        "source_sha256": sources, "native_inventory_sha256": inventory_hash,
        "validator_source": {"revision": INPUT_REVISION, "path": VALIDATOR, "sha256": SOURCES[VALIDATOR],
                             "blob_oid": "887a9559f368519d88dece5917e3604aa2c41519",
                             "execution": "Pinned Git object bytes; current offline analysis file is not executed"},
        "frozen_audit_source": {"revision": INPUT_REVISION,
            "path": "software/analysis/tracker_reconstruction/audit_root.py",
            "blob_oid": "61e0e2e616cd8ab9b94d4b7536cc3792f722bbb8",
            "sha256": SOURCES["software/analysis/tracker_reconstruction/audit_root.py"]},
        "retention_source_sha256": inventory["retention_source_sha256"],
        "case_count": len(bindings), "events_per_case": 2 if pilot else 1000,
        "scope": "Independent persisted ROOT measurement counts/float32 variances, all generated track event IDs including zero-track events, raw candidate counts and complete representative perigee+sigma tuples in the same event",
        "case_bindings": {name: {"run_report_sha256": binding["run_report_sha256"],
            "retained_file_sha256": binding["item"]["files"], "root_sha256": binding["roots"]}
            for name, binding in sorted(bindings.items())},
        "frozen_audit": original,
        "immutability": {"native_reports": True, "root_files": True, "retained_files": True,
                         "native_configurations": True, "inventory": True, "audit_sources": True}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify and not args.output.is_file():
        parser.error("--verify requires an existing audit JSON")
    if not args.verify and args.output.exists():
        parser.error("Refusing to overwrite existing audit JSON; use --verify or a new output")
    result = compose_audit(args.native, args.data, args.pilot)
    if args.verify:
        if canonical(json.loads(args.output.read_text())) != canonical(result):
            raise ValueError("Exact ROOT re-audit differs from stored audit")
        print("Verified exact ROOT persistence audit replay")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
        print("Saved independent ROOT audit for", result["case_count"], "cases")


if __name__ == "__main__":
    main()
