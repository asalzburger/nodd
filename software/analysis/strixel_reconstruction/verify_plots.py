#!/usr/bin/env python3
"""Check published strixel figures without requiring local-only event data."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_family(directory, source, expected_figures):
    manifest = json.loads((directory / "manifest.json").read_text())
    files = manifest.get("figures_sha256", manifest.get("files_sha256"))
    if not isinstance(files, dict) or len(files) != 2 * expected_figures:
        raise ValueError("Figure inventory does not have the prescribed PNG/PDF pairs")
    for name, expected in files.items():
        if (not isinstance(name, str) or Path(name).name != name or "\\" in name
                or Path(name).suffix not in (".png", ".pdf")
                or not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected)):
            raise ValueError("Unsafe or invalid figure inventory entry")
    for name, expected in files.items():
        path = directory / name
        if path.is_symlink() or not path.is_file() or sha(path) != expected:
            raise ValueError(f"Missing or changed figure: {name}")
        partner = str(Path(name).with_suffix(".pdf" if name.endswith(".png") else ".png"))
        if partner not in files:
            raise ValueError(f"Missing paired export: {name}")
    actual = {p.name for p in directory.iterdir() if p.suffix in (".png", ".pdf")}
    if actual != set(files):
        raise ValueError("Unlisted figure export")
    source_hash = manifest.get("plot_source_sha256", manifest.get("plot_sha256"))
    if sha(source) != source_hash:
        raise ValueError("Plot source differs from the retained figure source")
    profiles = directory.parent / "profiles.json.gz"
    if profiles.exists() and sha(profiles) != manifest["profiles_sha256"]:
        raise ValueError("Local profile input differs from the figure manifest")
    return len(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        # Frozen export counts, not physics cuts: the original truth scan,
        # Gaussian control, five GBTS populations × four figure families,
        # and two ttbar selections × three figure families.
        families = (("", "strixel_pitch_study/plot.py", 11),
                    ("gaussian-control", "strixel_pitch_study/control_plot.py", 2),
                    ("gbts", "strixel_reconstruction/plot.py", 20),
                    ("ttbar-pu200", "strixel_ttbar/plot.py", 6))
        for name, source, expected in families:
            count = verify_family(root / "docs/validation/DES-042" / name / "figures",
                                  root / "software/analysis" / source, expected)
            print(f"PASS {name}: {count} published exports, paired formats and source hashes")
        print("Event/statistical replay requires the separately retained local dataset.")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
