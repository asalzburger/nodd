#!/usr/bin/env python3
"""Verify retained provenance, complete grids, duplicate formats and SVG XML."""
import csv
import gzip
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

from prepare import ROOT, OUT, digest, read
from run import eta_grid


def verify(data=OUT):
    config, report = read(data/"geometries.json"), read(data/"provenance.json")
    assert digest(data/"geometries.json") == report["configuration_sha256"]
    for path, sha in config["source_sha256"].items():
        assert digest(ROOT/path) == sha, path
    for path, sha in report["producer_sha256"].items():
        assert digest(ROOT/path) == sha, path
    for run in report["runs"]:
        assert run["expected_rows"] == run["result_rows"] == run["hit_rows"]
        assert run["exit_code"] == 0
        for path, info in run["files"].items():
            p = data/path
            assert digest(p) == info["sha256"], path
            import hashlib
            raw = gzip.decompress(p.read_bytes()) if p.suffix == ".gz" else p.read_bytes()
            assert hashlib.sha256(raw).hexdigest() == info["uncompressed_sha256"], path
    profiles, resolutions = read(data/"profiles.json.gz"), read(data/"resolutions.json.gz")
    for stem, rows in (("profiles", profiles), ("resolutions", resolutions)):
        with gzip.open(data/(stem+".csv.gz"), "rt") as handle:
            csvrows = list(csv.DictReader(handle))
        assert len(csvrows) == len(rows)
        for a,b in zip(rows,csvrows):
            for k,v in a.items():
                if isinstance(v, list):
                    assert v == json.loads(b[k])
                elif isinstance(v, bool):
                    assert str(v) == b[k]
                elif isinstance(v, (float,int)):
                    assert math.isfinite(float(b[k])) and v == float(b[k])
                else:
                    assert v == b[k]
    scan = config["scan"]
    expected = {(c["id"], b,z,pt,eta) for c in config["candidates"] for b in scan["field_T"]
                for z in scan["vertex_z_m"] for pt in scan["pt_GeV"] for eta in eta_grid(scan)}
    actual = [(r["geometry"],r["field_T"],r["vertex_z_m"],r["pt_GeV"],r["eta"]) for r in resolutions]
    assert len(actual) == len(expected) and set(actual) == expected
    controls = read(data/"controls.json")
    assert len(controls) == 54 and all(r["within_half_printed_unit"] for r in controls)
    full = {(r["field_T"],r["vertex_z_m"],r["pt_GeV"],r["eta"]): r for r in resolutions if r["geometry"] == "extended"}
    for r in resolutions:
        if r["geometry"] == "aperture":
            reference = full[r["field_T"],r["vertex_z_m"],r["pt_GeV"],r["eta"]]
            assert all(v == reference[k] for k,v in r.items() if k != "geometry")
    if report["build_log_sha256"]:
        assert digest(data/"build.log") == report["build_log_sha256"]
    figs = data/"figures"
    manifest = read(figs/"manifest.json")
    assert digest(ROOT/"tools/odd_idres/plot.py") == manifest["producer_sha256"]
    for p,sha in manifest["inputs"].items():
        assert digest(data/p) == sha
    for p,sha in manifest["files"].items():
        assert digest(figs/p) == sha
        assert ET.parse(figs/p).getroot().tag.endswith("svg")
    print(f"PASS: {len(report['runs'])} runs; {len(resolutions)} fit rows; {len(profiles)} profiles; 54 controls; {len(manifest['files'])} SVGs; all hashes and CSV/JSON values agree")


if __name__ == "__main__":
    verify()
