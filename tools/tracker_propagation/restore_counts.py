#!/usr/bin/env python3
"""Restore retained, compressed tracker counts for plotting without ACTS."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil


def restore(source, output):
    config = json.loads((source / "study.json").read_text())
    output.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source / "study.json", output / "study.json")
    for pt in config["pt_GeV"]:
        case = output / f"pt_{pt:g}GeV"
        case.mkdir(exist_ok=True)
        report = json.loads((source / f"pt-{pt:g}GeV-run.json").read_text())
        data = gzip.decompress((source / f"counts-pt-{pt:g}GeV.csv.gz").read_bytes())
        if report["status"] != "PASS" or hashlib.sha256(data).hexdigest() != report["artifact_sha256"]["counts.csv"]:
            raise ValueError("retained counts failed identity/accounting checks")
        (case / "counts.csv").write_bytes(data)
        (case / "run.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Restored validated counts: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    restore(args.source, args.output)
