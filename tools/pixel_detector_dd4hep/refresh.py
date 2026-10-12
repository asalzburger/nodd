#!/usr/bin/env python3
"""Build, validate and display the preliminary pixels in an activated DD4hep shell."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, default=ROOT / "build/dd4hep")
    parser.add_argument(
        "--nodehammer", type=Path, default=ROOT / "build/nodehammer/native/nodehammer"
    )
    parser.add_argument(
        "--display-output", type=Path, default=ROOT / "build/nodehammer/pixel-detector"
    )
    parser.add_argument("--without-display", action="store_true")
    parser.add_argument(
        "--geant4-init",
        action="store_true",
        help="Initialize DDSim and Geant4, without transporting events",
    )
    args = parser.parse_args()
    build = args.build.resolve()
    build.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    plugin = build / "detector"
    for key in ("DD4HEP_LIBRARY_PATH", "DYLD_LIBRARY_PATH", "LD_LIBRARY_PATH"):
        env[key] = str(plugin) + os.pathsep + env.get(key, "")
    record = dict(
        status="RUNNING",
        revision=subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        recorded_at=datetime.now(timezone.utc).isoformat(),
        commands=[],
        geant4_events=0 if args.geant4_init else None,
    )

    def run(label, command):
        log = build / (label + ".log")
        print(label, flush=True)
        with log.open("w") as out:
            result = subprocess.run(
                list(map(str, command)),
                cwd=ROOT,
                env=env,
                stdout=out,
                stderr=subprocess.STDOUT,
            )
        record["commands"].append(
            dict(
                command=list(map(str, command)),
                exit_code=result.returncode,
                log=str(log),
                sha256=hashlib.sha256(log.read_bytes()).hexdigest(),
            )
        )
        if result.returncode:
            raise RuntimeError(f"{label} failed; see {log}")

    try:
        run(
            "configure",
            [
                "cmake",
                "-S",
                ROOT,
                "-B",
                build,
                "-G",
                "Ninja",
                "-DCMAKE_BUILD_TYPE=RelWithDebInfo",
            ],
        )
        run("build", ["cmake", "--build", build, "--parallel", "4"])
        run("ctest", ["ctest", "--test-dir", build, "--output-on-failure"])
        compact = plugin / "pixel-detector/pixel-detector.xml"
        if not args.without_display:
            run(
                "nodehammer",
                [
                    sys.executable,
                    "-B",
                    ROOT / "tools/nodehammer/prepare.py",
                    "--compact",
                    compact,
                    "--nodehammer",
                    args.nodehammer.resolve(),
                    "--output",
                    args.display_output.resolve(),
                ],
            )
        if args.geant4_init:
            ddsim = shutil.which("ddsim")
            if not ddsim:
                raise RuntimeError(
                    "Activate DD4hep/DDG4 and Geant4 before --geant4-init"
                )
            macro = build / "initialize.mac"
            macro.write_text(
                "# Initialization smoke only; no beamOn command.\n/run/verbose 0\n"
            )
            # Explicit Python bypasses macOS /usr/bin/env DYLD stripping.
            run(
                "geant4-initialize",
                [
                    sys.executable,
                    ddsim,
                    "--compactFile",
                    compact,
                    "--runType",
                    "run",
                    "--macroFile",
                    macro,
                    "--outputFile",
                    build / "initialize.root",
                    "--physics.list",
                    "FTFP_BERT",
                    "--random.seed",
                    "42",
                ],
            )
            text = (build / "geant4-initialize.log").read_text()
            expected = json.loads(compact.with_name("expected.json").read_text())[
                "counts"
            ]["sensitive"]
            if (
                f"{expected} sensitive path entries" not in text
                or "Successfully converted geometry to Geant4" not in text
            ):
                raise RuntimeError(
                    "Geant4 initialization did not confirm expected sensitive paths"
                )
            version = re.search(r"Geant4 version Name:\s*(.+)", text)
            record["geant4_initialization"] = dict(
                sensitive_paths=expected,
                events=0,
                geometry_conversion=True,
                physics_list="FTFP_BERT",
                seed=42,
                version=version.group(1).strip() if version else None,
            )
        record["status"] = "PASS"
    except Exception as error:
        record.update(status="FAIL", error=str(error))
        raise
    finally:
        (build / "pixel-workflow.json").write_text(json.dumps(record, indent=2) + "\n")
    print(build / "pixel-workflow.json")


if __name__ == "__main__":
    main()
