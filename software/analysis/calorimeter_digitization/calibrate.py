#!/usr/bin/env python3
"""Freeze a binned MIP calibration using the first half of central muon events."""
import argparse
import json
from pathlib import Path

from podio import root_io

from generate import sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    reader = root_io.Reader(str(args.input))
    events = list(reader.get("events"))
    split = len(events) // 2
    if split < 100:
        parser.error("At least 200 muon events required")
    # Analysis binning selected before reading the observed peak: 2.5 keV bins.
    width = 2.5e-6
    counts = [0] * 200
    overflow = 0
    for frame in events[:split]:
        for hit in frame.get("ECalBarrelCollection"):
            energy = float(hit.getEnergy())
            if energy < 0:
                raise ValueError("Negative simulated deposit")
            index = int(energy / width)
            if index < len(counts):
                counts[index] += 1
            else:
                overflow += 1
    index = max(range(len(counts)), key=counts.__getitem__)
    if index in (0, len(counts) - 1) or counts[index] == 0:
        raise ValueError("MIP peak outside calibration range")
    result = dict(status="PROTOTYPE empirical calibration",
                  input_sha256=sha256(args.input), calibration_events=[0, split],
                  validation_events=[split, len(events)], collection="ECalBarrelCollection",
                  convention="Centre of highest-count silicon cell-energy bin; 2.5 keV bin width. No Landau fit or systematic-error claim.",
                  mip_energy_GeV=(index + 0.5) * width,
                  bin_quantization_half_width_GeV=width / 2,
                  edges_GeV=[i * width for i in range(len(counts) + 1)],
                  counts=counts, overflow=overflow, normalization="cell counts in calibration events",
                  limitations=["This is an empirical ODD muon peak, not transferred CALICE or nODD calibration.",
                                "MIP validation uses only the disjoint second half of these events.",
                                "Angular/path-length and Landau-fit systematics remain unquantified."])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"MIP scale: {result['mip_energy_GeV']:.8g} GeV; {split} calibration events")


if __name__ == "__main__":
    main()
