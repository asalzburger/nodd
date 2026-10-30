"""Retain byte-preserving compressed summaries and numerical event distributions."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil


def retain(native,analysis,destination,phase):
    native,analysis,destination=map(Path,(native,analysis,destination))
    reports={}
    for source in sorted(analysis.glob("*/*/summary.json")):
        relative=source.parent.relative_to(analysis);target=destination/phase/relative
        target.mkdir(parents=True,exist_ok=True)
        raw=source.read_bytes()
        (target/"summary.json.gz").write_bytes(gzip.compress(raw,mtime=0))
        # Preserve the original bytes (and their already-frozen input hash).
        if gzip.decompress((target/"summary.json.gz").read_bytes())!=raw:raise RuntimeError("Compression changed evidence")
        (target/"summary.json").unlink(missing_ok=True)
        shutil.copyfile(source.with_name("events.npz"),target/"events.npz")
        report=native/relative/"run-report.json"
        reports[str(relative)]=json.loads(report.read_text())
    # Preserve nested key order: indent=2 reserialization must reproduce each
    # original run-report byte hash retained by the independent reduction.
    (destination/("native-"+phase+"-reports.json.gz")).write_bytes(gzip.compress(json.dumps(reports,separators=(",",":")).encode(),mtime=0))


def manifest(destination):
    destination=Path(destination)
    files={str(p.relative_to(destination)):hashlib.sha256(p.read_bytes()).hexdigest()
           for p in sorted(destination.rglob("*")) if p.is_file() and p.name!="manifest.json"}
    report={"schema_version":1,"status":"PROTOTYPE","files_sha256":files,
            "summary_encoding":"summary.json.gz decompresses to exactly the original summary.json bytes; frozen selection input hashes address those decompressed bytes",
            "event_arrays":"One entry per generated muon; no-fit parameters are NaN sentinels, matched masks retained; all residual/pull tails uncut",
            "native_root_policy":"Raw native event JSONL and ROOT files remain ignored under build/tracker-reconstruction; their recorded hashes and exact run provenance are retained"}
    (destination/"manifest.json").write_text(json.dumps(report,indent=2)+"\n")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--native",type=Path);p.add_argument("--analysis",type=Path);p.add_argument("--destination",type=Path,required=True);p.add_argument("--phase",choices=("tuning","validation"));p.add_argument("--manifest",action="store_true")
    a=p.parse_args()
    if a.manifest:manifest(a.destination)
    else:
        if not a.native or not a.analysis or not a.phase:p.error("Native/analysis/phase required for retention")
        retain(a.native,a.analysis,a.destination,a.phase)
