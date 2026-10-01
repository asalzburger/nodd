#!/usr/bin/env python3
"""Export coloured ROOT geometry and verify it in a separate ROOT-only process."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
PALETTE = ROOT_DIR / "detector/config/display.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def style_name(material):
    if material.endswith("_Core"):
        return "Foam"
    if material.startswith("CableMix_"):
        return "Cable"
    if material.startswith("end_"):
        return "Service"
    return "Copper" if material == "PatternedCopper" else material


def snapshot(manager, ROOT):
    palette = json.loads(PALETTE.read_text())["styles"]
    result = {}
    # Inspect placed geometry, excluding DD4hep's unplaced default Air volumes.
    pending = [manager.GetTopVolume()]
    seen = set()
    while pending:
        volume = pending.pop()
        name = str(volume.GetName())
        if name in seen:
            continue
        seen.add(name)
        pending.extend(
            volume.GetNode(i).GetVolume() for i in range(volume.GetNdaughters())
        )
        if volume.IsAssembly() or name == str(manager.GetTopVolume().GetName()):
            continue
        name = str(volume.GetName())
        material = str(volume.GetMaterial().GetName())
        style = style_name(material)
        reference = palette[style]
        colour_id = int(volume.GetLineColor())
        colour = ROOT.gROOT.GetColor(colour_id)
        if not colour:
            raise ValueError(f"{name}: ROOT colour {colour_id} is undefined")
        rgb = [
            float(colour.GetRed()),
            float(colour.GetGreen()),
            float(colour.GetBlue()),
        ]
        # ROOT uses its explicit index; config rgb is an independent display
        # choice for RGB-based consumers. Preserve actual ROOT RGB in the
        # snapshot so the fresh-process round trip still checks persistence.
        if colour_id != reference["root_color"]:
            raise ValueError(f"{name}: persisted colour index differs from palette")
        raw_transparency = volume.GetTransparency()
        transparency = (
            ord(raw_transparency)
            if isinstance(raw_transparency, str)
            else int(raw_transparency)
        )
        # Record effective ROOT transparency without enforcing a config alpha
        # conversion; ROOT/DD4hep or interactive settings may differ.
        if name in result:
            raise ValueError("Duplicate volume name: " + name)
        result[name] = dict(
            material=material,
            style=style,
            colour=colour_id,
            rgb=rgb,
            transparency=transparency,
            fill_colour=int(volume.GetFillColor()),
            visible=bool(volume.IsVisible()),
            daughters_visible=bool(volume.IsVisDaughters()),
        )
    return result


def run_phase(args):
    import ROOT

    ROOT.gROOT.SetBatch(True)
    before_path = args.output.with_suffix(".display-before.json")
    if args.phase == "write":
        import dd4hep

        if ROOT.gSystem.Load(str(args.library.resolve())) < 0:
            raise RuntimeError("Cannot load detector library")
        detector = dd4hep.Detector.getInstance()
        try:
            detector.fromXML(str(args.compact.resolve()))
            manager = detector.manager()
            before = snapshot(manager, ROOT)
            manager.Export(str(args.output.resolve()))
            before_path.write_text(json.dumps(before, sort_keys=True) + "\n")
        finally:
            dd4hep.Detector.destroyInstance()
            if ROOT.gGeoManager:
                ROOT.gGeoManager.Delete()
    else:
        # Deliberately no dd4hep import, factory load, or palette creation here.
        manager = ROOT.TGeoManager.Import(str(args.output.resolve()))
        if not manager:
            raise RuntimeError("Could not reopen exported geometry")
        try:
            after = snapshot(manager, ROOT)
            if after != json.loads(before_path.read_text()):
                raise ValueError("ROOT export changed display attributes")
            styles = {}
            counts = Counter(item["style"] for item in after.values())
            for item in after.values():
                styles[item["style"]] = dict(
                    rgb=item["rgb"],
                    colour=item["colour"],
                    transparency=item["transparency"],
                    volumes=counts[item["style"]],
                )
            report = dict(
                status="PASS",
                scope="Display attributes only; fresh ROOT process after geometry export",
                root_version=str(ROOT.gROOT.GetVersion()),
                volumes_checked=len(after),
                styles=styles,
                compact_sha256=sha(args.compact),
                library_sha256=sha(args.library),
                palette_sha256=sha(PALETTE),
                root_file_sha256=sha(args.output),
                script_sha256=sha(__file__),
                command=sys.argv,
                comparison="Every non-assembly detector volume: colour index, RGB, transparency, fill colour, visibility and daughter visibility",
                interactive_rendering_tested=False,
            )
            args.output.with_suffix(".display.json").write_text(
                json.dumps(report, indent=2) + "\n"
            )
            print(f"PASS: {len(after)} volume styles preserved in {args.output}")
        finally:
            manager.Delete()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compact", type=Path, required=True)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", choices=["write", "read"], help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.output.suffix != ".root":
        parser.error("--output must end in .root")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.phase:
        run_phase(args)
    else:
        for phase in ("write", "read"):
            subprocess.run(
                [
                    sys.executable,
                    "-B",
                    __file__,
                    "--compact",
                    str(args.compact),
                    "--library",
                    str(args.library),
                    "--output",
                    str(args.output),
                    "--phase",
                    phase,
                ],
                check=True,
            )


if __name__ == "__main__":
    main()
