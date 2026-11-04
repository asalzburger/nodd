#!/usr/bin/env python3
"""Prepare a review extract from the exact published TDR and the PR overlay.

Does not checkout, commit, fetch, or publish the TDR. Compile the resulting
issue38-review.tex with the repository-pinned pdfLaTeX environment.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[2]
BASE = "7625cf6054f5761228be6d8d2de24d43f155bd19"
OVERLAY = ROOT / "docs/publication/issue38-mechanics"


def prepare(tdr: Path, output: Path) -> None:
    if output.exists():
        raise ValueError("Choose a new output directory; retained evidence is never overwritten")
    blob = subprocess.check_output(["git", "-C", str(tdr), "archive", BASE])
    with tarfile.open(fileobj=io.BytesIO(blob)) as archive:
        # Only ordinary files and directories are needed by the TeX manuscript.
        if any(not (m.isfile() or m.isdir()) for m in archive.getmembers()):
            raise ValueError("Unexpected non-file member in TDR source archive")
        for member in archive.getmembers():
            if Path(member.name).is_absolute() or ".." in Path(member.name).parts:
                raise ValueError("Unsafe archive path")
        output.mkdir(parents=True)
        archive.extractall(output, filter="data")
    shutil.copyfile(OVERLAY / "pixel-detector.tex", output / "chapters/pixel-detector.tex")
    shutil.copyfile(OVERLAY / "strip-mounting.tex", output / "issue38-strip-mounting.tex")
    shutil.copyfile(OVERLAY / "figures/mechanics.pdf", output / "figures/mechanics.pdf")
    source = (output / "pixel-detector.tex").read_text()
    source = source.replace("\\ODDdate{2026-10-09}", "\\ODDdate{2026-10-15}")
    source = source.replace("\\input{chapters/pixel-detector}",
                            "\\input{chapters/pixel-detector}\n\\clearpage\n\\markboth{Tracker}{Tracker}\n\\input{issue38-strip-mounting}")
    (output / "issue38-review.tex").write_text(source)
    paths = [OVERLAY / "pixel-detector.tex", OVERLAY / "strip-mounting.tex",
             OVERLAY / "figures/mechanics.pdf"]
    (output / "issue38-inputs.json").write_text(json.dumps({
        "base_tdr_revision": BASE,
        "overlay_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in paths},
        "compiler_image": "ghcr.io/xu-cheng/texlive-alpine@sha256:c06416ebbc69c8e90e07d1f1a6f7a3f9b334e773daa3543ce879ea533317c3a7",
        "scope": "Editorial review extract; no TDR publication or detector design approval",
    }, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tdr", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    prepare(args.tdr.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
