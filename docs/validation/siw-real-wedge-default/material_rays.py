"""Compare native material navigation for stock and default LAYOUT-001 compacts."""
import argparse
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools/pixel_barrel_dd4hep"))
from validate import trace_ray


def trace(compact, output, libraries):
    import dd4hep
    import ROOT

    ROOT.gROOT.SetBatch(True)
    for library in libraries:
        if ROOT.gSystem.Load(str(library.resolve())) < 0:
            raise RuntimeError(f"Cannot load {library}")
    detector = dd4hep.Detector.getInstance()
    detector.fromXML(str(compact.resolve()))
    manager = detector.manager()
    world = manager.GetTopVolume().GetMaterial()
    unit = float(dd4hep.mm)
    world_name = str(world.GetName())
    rays = []
    for eta in (-4., -3.2, -2., -1.6, -1.45, -.5, .001, .5, 1.45, 1.6, 2., 3.2, 4.):
        for phi in (.03, .123, math.pi/16-.004, math.pi/16+.004, .7):
            direction = [math.cos(phi)/math.cosh(eta), math.sin(phi)/math.cosh(eta), math.tanh(eta)]
            ray = trace_ray(manager, dd4hep, [0, 0, 0], direction, {}, max_length_mm=7000.)
            # The ray helper already excludes the world. Exclude identical
            # ambient air attributed to the navigation mothers in the new tree.
            air = ray["material_path_mm"].pop(world_name, 0.)
            ray["x_over_x0"] -= air / (world.GetRadLen()/unit)
            ray["l_over_lambda"] -= air / (world.GetIntLen()/unit)
            rays.append(dict(eta=eta, phi=phi, x0=ray["x_over_x0"], nuclear=ray["l_over_lambda"],
                             materials=ray["material_path_mm"]))
    output.write_text(json.dumps(rays, indent=2) + "\n")
    dd4hep.Detector.destroyInstance()
    if ROOT.gGeoManager:
        ROOT.gGeoManager.Delete()


def compare(stock, wedge, output):
    old = json.loads(stock.read_text())
    new = json.loads(wedge.read_text())
    if len(old) != len(new) or len(old) != 65:
        raise ValueError("Unexpected ray inventory")
    length = x0 = nuclear = 0.
    for a, b in zip(old, new):
        if (a["eta"], a["phi"]) != (b["eta"], b["phi"]):
            raise ValueError("Ray direction mismatch")
        x0 = max(x0, abs(a["x0"]-b["x0"]))
        nuclear = max(nuclear, abs(a["nuclear"]-b["nuclear"]))
        left, right = a["materials"], b["materials"]
        for material in left.keys() | right.keys():
            length = max(length, abs(left.get(material, 0.)-right.get(material, 0.)))
    if length >= 1e-5 or x0 >= 1e-6 or nuclear >= 1e-6:
        raise ValueError(f"Material paths differ by {length} mm, {x0} X0, {nuclear} lambda")
    result = dict(rays=len(old), maximum_material_path_delta_mm=length,
                  maximum_radiation_length_delta=x0, maximum_interaction_length_delta=nuclear)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    sample = commands.add_parser("trace")
    sample.add_argument("compact", type=Path)
    sample.add_argument("output", type=Path)
    sample.add_argument("libraries", type=Path, nargs="+")
    check = commands.add_parser("compare")
    check.add_argument("stock", type=Path)
    check.add_argument("wedge", type=Path)
    check.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.action == "trace":
        trace(args.compact, args.output, args.libraries)
    else:
        compare(args.stock, args.wedge, args.output)
