#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Prepare exact upstream energy methods for the isolated GPL executable.

No network access, dependency installation, source rewriting or linked MPL code.
"""
import argparse
import hashlib
from pathlib import Path

PIN = "255967eb855ebbc8f75ebaac190b268b63332e8b"
HASHES = {
    "CaloDigi/Realistic/src/RealisticCaloDigiSilicon.cc":
        "5d6f745c8f2fc0ea61add7c75d2bb53dafa80a2929f022d5dd7ea2634f08f84e",
    "CaloDigi/Realistic/src/RealisticCaloDigi.cc":
        "c0f33f5bd38224c3418236399c87121fa743ed77244cd4145949ed7a0e80c8cb",
    "LICENCE": "8ceb4b9ee5adedde47b31e975c1d90c73ad27b6b165a1dcd80c7c545eb65b903",
}


def prepare(source, output):
    contents = {}
    for name, expected in HASHES.items():
        data = (source / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"Upstream hash mismatch: {name}; require {PIN}")
        contents[name] = data
    # Extract one whole, unchanged method using the upstream method separators.
    # The complete original silicon translation unit is copied byte for byte.
    base = contents["CaloDigi/Realistic/src/RealisticCaloDigi.cc"]
    start = base.index(b"float RealisticCaloDigi::EnergyDigi(")
    end = base.index(b"\n//------------------------------------------------------------------------------", start)
    output.mkdir(parents=True, exist_ok=True)
    (output / "RealisticCaloDigiSilicon.cc").write_bytes(
        contents["CaloDigi/Realistic/src/RealisticCaloDigiSilicon.cc"])
    (output / "OriginalEnergyDigi.cc").write_bytes(
        b'// GPL-3.0 upstream method; full source pin and license alongside.\n'
        b'#include "RealisticCaloDigiSilicon.h"\n'
        b'#include <algorithm>\n#include "CLHEP/Random/RandGauss.h"\n'
        b'#include "CLHEP/Random/RandFlat.h"\n' + base[start:end] + b'\n')
    (output / "LICENCE").write_bytes(contents["LICENCE"])
    (output / "upstream.txt").write_text(
        "iLCSoft/MarlinReco@" + PIN + "\n" +
        "\n".join(f"{digest}  {name}" for name, digest in HASHES.items()) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.source, args.output)
