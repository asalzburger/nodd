#!/usr/bin/env python3
"""Retain native report fingerprints and portable metadata without local paths."""
import argparse
import gzip
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from analyze import sha256


def portable(value,root):
    if isinstance(value,dict):return {k:portable(v,root) for k,v in value.items() if k!="path"}
    if isinstance(value,list):return [portable(v,root) for v in value]
    if isinstance(value,str):
        if value.startswith(str(root)):return "<repository>"+value[len(str(root)):]
        if value.startswith("/"):return "<local path omitted>/"+Path(value).name
    return value


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--case",action="append",required=True,help="LABEL=directory")
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args();root=Path(__file__).resolve().parents[3];reports=[]
    for spec in args.case:
        label,directory=spec.split("=",1);path=Path(directory)/"run-report.json"
        source=json.loads(path.read_text());clean=portable(source,root)
        if "/Users/" in json.dumps(clean):raise ValueError("Unreviewed local path remains")
        reports.append({"case":label,"source_report_sha256":sha256(path),"report":clean})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(gzip.compress((json.dumps({"schema_version":1,"status":"PROTOTYPE",
        "method":"Original report fingerprints retained; local absolute paths replaced by named placeholders; numeric data and source/binary/output hashes unchanged.",
        "reports":reports},indent=2)+"\n").encode(),mtime=0))


if __name__=="__main__":main()
