#!/usr/bin/env python3
"""Independent native dimensions, mass, vacuum and directional wall checks."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / 'tools/pixel_barrel_dd4hep'))
from validate import trace_ray, ray_direction


def main():
    p = argparse.ArgumentParser()
    for key in ('compact', 'expected', 'library', 'output'):
        p.add_argument('--'+key, type=Path, required=True)
    args = p.parse_args()
    import ROOT
    import dd4hep
    ROOT.gROOT.SetBatch(True)
    if ROOT.gSystem.Load(str(args.library.resolve())) < 0:
        raise RuntimeError('Factory load failed')
    d = dd4hep.Detector.getInstance()
    d.fromXML(str(args.compact.resolve()))
    expected = json.loads(args.expected.read_text())
    c = expected['config']
    de = d.detector('BeamPipe')
    volume = de.volume()
    shape = volume.solid().ptr()
    material = volume.material().ptr().GetMaterial()
    unit = float(dd4hep.mm)
    errors = []
    dimensions = [float(shape.GetRmin())/unit, float(shape.GetRmax())/unit, float(shape.GetDz())/unit]
    target = [c['inner_radius_mm'], expected['outer_radius_mm'], c['half_length_mm']]
    if math.dist(dimensions, target) > 1e-9:
        errors.append('Pipe dimensions differ from config')
    capacity = float(shape.Capacity()) / unit**3
    mass = capacity * float(material.GetDensity()) / 1000
    if not math.isclose(mass, expected['wall_mass_g'], rel_tol=1e-12):
        errors.append('Wall mass differs from analytic shell')
    if not math.isclose(float(material.GetZ()), 4) or not math.isclose(float(material.GetDensity()), c['density_g_cm3'], rel_tol=1e-12):
        errors.append('Be composition/density mismatch')
    ROOT.gInterpreter.Declare('#include <DD4hep/DetType.h>\nbool nodd_is_beampipe(dd4hep::DetElement e) {return dd4hep::DetType(e.typeFlag()).is(dd4hep::DetType::BEAMPIPE);}')
    if not ROOT.nodd_is_beampipe(de) or volume.isSensitive():
        errors.append('Passive BEAMPIPE flag invalid')
    manager = d.manager()
    manager.CheckOverlaps(1e-5*unit)
    overlaps = [dict(title=str(o.GetTitle()), distance_mm=float(o.GetOverlap())/unit) for o in manager.GetListOfOverlaps()]
    if overlaps:
        errors.append('Geometry overlaps')
    origin_node = manager.FindNode(0,0,0)
    if str(origin_node.GetVolume().GetMaterial().GetName()) != 'Vacuum':
        errors.append('Bore is not vacuum')
    rays = []
    for eta in (-4, -2, 0, 2, 4):
        for phi in (0, .37, 1.11):
            r = trace_ray(manager, dd4hep, [0.,0.,0.], ray_direction(eta, phi), {}, 4100)
            target_path = c['wall_mm']*math.cosh(eta)
            observed = r['material_path_mm'].get('Beryllium',0)
            if not math.isclose(observed, target_path, abs_tol=1e-7):
                errors.append(f'Wall path mismatch eta={eta} phi={phi}')
            r.update(eta=eta,phi=phi,expected_wall_path_mm=target_path)
            rays.append(r)
    report = dict(status='PASS' if not errors else 'FAIL', errors=errors, dimensions_mm=dimensions,
                  wall_volume_mm3=capacity, wall_mass_g=mass, radiation_length_mm=float(material.GetRadLen())/unit,
                  interaction_length_mm=float(material.GetIntLen())/unit, elemental_Z=float(material.GetZ()),
                  overlaps=overlaps, overlap_tolerance_mm=1e-5, navigation=rays, sensitive_count=0,
                  git_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT_DIR,text=True).strip(),
                  git_dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT_DIR,text=True).strip()),
                  root_version=ROOT.gROOT.GetVersion(), python_version=platform.python_version(),
                  file_sha256={k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in dict(compact=args.compact,expected=args.expected,library=args.library,validator=Path(__file__),factory=ROOT_DIR/'detector/src/BeamPipe.cpp').items()},
                  limitations=['Straight-ray checks, no beam/vacuum engineering qualification; Geant4 transport and tracker integration checked separately.'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    dd4hep.Detector.destroyInstance()
    if ROOT.gGeoManager:
        ROOT.gGeoManager.Delete()
    return bool(errors)

if __name__ == '__main__':
    sys.exit(main())
