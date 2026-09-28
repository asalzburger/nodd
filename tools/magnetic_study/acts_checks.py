#!/usr/bin/env python3
"""PROTOTYPE: pyacts propagation fixtures, not nODD performance validation."""
import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys
import acts
import acts.examples as ex
from acts.examples.simulation import addParticleGun, MomentumConfig, EtaConfig, PhiConfig, ParticleConfig


def run_case(root, name, field_t, charge, straight=False, step_mm=10.):
    out = root / name
    out.mkdir(parents=True, exist_ok=True)
    level = acts.logging.WARNING
    detector = ex.GenericDetector(logLevel=level)
    navigator = acts.Navigator(trackingGeometry=detector.trackingGeometry(), resolveSensitive=True)
    stepper = acts.StraightLineStepper() if straight else acts.EigenStepper(
        acts.ConstantBField(acts.Vector3(0, 0, field_t * acts.UnitConstants.T)))
    propagator = ex.ConcretePropagator(acts.Propagator(stepper, navigator, level))
    sequence = ex.Sequencer(events=1, numThreads=1, logLevel=level,
                            outputDir=str(out), trackFpes=False)
    pdg = acts.PdgParticle.eAntiMuon if charge > 0 else acts.PdgParticle.eMuon
    addParticleGun(sequence, momentumConfig=MomentumConfig(10., 10., False),
                   etaConfig=EtaConfig(.5, .5), phiConfig=PhiConfig(0., 0.),
                   particleConfig=ParticleConfig(1, pdg, False),
                   rnd=ex.RandomNumbers(seed=228), logLevel=level,
                   outputDirCsv=out)
    sequence.addAlgorithm(ex.ParticleTrackParamExtractor(
        inputParticles='particles_generated', outputTrackParameters='params', level=level))
    sequence.addAlgorithm(ex.PropagationAlgorithm(
        propagatorImpl=propagator, inputTrackParameters='params',
        outputSummaryCollection='summary', multipleScattering=False,
        energyLoss=False, recordMaterialInteractions=False,
        maxStepSize=step_mm, level=level))
    sequence.addWriter(ex.ObjPropagationStepsWriter(
        collection='summary', outputDir=str(out), outputPrecision=16, level=level))
    sequence.run()
    with (out / 'event000000000-particles.csv').open() as stream:
        particle = next(csv.DictReader(stream))
    if float(particle['q']) != charge:
        raise AssertionError('Generated particle charge differs from requested fixture')
    obj = out / 'event000000000-propagation-steps.obj'
    points = [tuple(map(float, line.split()[1:])) for line in obj.read_text().splitlines() if line.startswith('v ')]
    if len(points) < 3:
        raise AssertionError('Propagation produced too few recorded points')
    if not all(math.isfinite(value) for point in points for value in point):
        raise AssertionError('Propagation produced nonfinite coordinates')
    p_t = 10. / math.cosh(.5)
    residuals = []
    for x, y, z in points:
        if field_t == 0 or straight:
            residuals.append(max(abs(y), abs(z - x * math.sinh(.5))))
        else:
            radius = 1000 * p_t / (0.299792458 * abs(field_t))
            sign = charge * (1 if field_t > 0 else -1)
            radial = abs(math.hypot(x, y + sign * radius) - radius)
            angle = math.atan2(x / radius, 1 + sign * y / radius)
            residuals.append(max(radial, abs(z - radius * angle * math.sinh(.5))))
    # OBJ uses limited decimal precision despite requested outputPrecision=16.
    # 0.02 mm is a serialization-aware synthetic-fixture check, not detector tolerance.
    tolerance = .02
    result = {'case': name, 'field_T': field_t, 'charge_e': charge,
              'stepper': type(stepper).__name__, 'maximum_step_mm': step_mm,
              'points': len(points), 'max_analytic_residual_mm': max(residuals),
              'fixture_tolerance_mm': tolerance,
              'passed': all(math.isfinite(r) and r < tolerance for r in residuals),
              'last_position_mm': points[-1], 'obj_sha256': hashlib.sha256(obj.read_bytes()).hexdigest()}
    if not result['passed']:
        raise AssertionError(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='Ignored directory for raw OBJ/CSV')
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    cases = [run_case(args.output, 'straight', 0., -1, True),
             run_case(args.output, 'eigen_zero', 0., -1),
             run_case(args.output, 'helix', 3., -1),
             run_case(args.output, 'field_reversed', -3., -1),
             run_case(args.output, 'charge_reversed', 3., 1),
             run_case(args.output, 'helix_half_step', 3., -1, step_mm=5.),
             run_case(args.output, 'charge_and_field_reversed', -3., 1)]
    radius, length = 1415., 6600.  # Explicit benchmark values in mm, not winding design.
    field = acts.SolenoidBField(radius=radius, length=length, nCoils=1000,
                               bMagCenter=3*acts.UnitConstants.T)
    cache = field.makeCache(acts.MagneticFieldContext())
    def axis_shape(z):
        return ((z+length/2)/math.hypot(radius,z+length/2)
                -(z-length/2)/math.hypot(radius,z-length/2))
    solenoid = []
    for z in (0., 2400., 3150., 5000., -3150.):
        measured = field.getField(acts.Vector3(0,0,z),cache)[2]/acts.UnitConstants.T
        expected = 3*axis_shape(z)/axis_shape(0.)
        if not all(math.isfinite(value) for value in (measured, expected)):
            raise AssertionError('Nonfinite solenoid axis field')
        error = abs(measured-expected)
        solenoid.append({'z_mm':z,'acts_Bz_T':measured,'finite_sheet_Bz_T':expected,
                         'absolute_difference_T':error})
        if not math.isfinite(error) or error > 1e-5:
            raise AssertionError(solenoid[-1])
    first = cases[2]['last_position_mm']
    reversal_residual = max(abs(first[0]-c['last_position_mm'][0]) +
                            abs(first[1]+c['last_position_mm'][1]) +
                            abs(first[2]-c['last_position_mm'][2]) for c in cases[3:5])
    # The generic geometry is not assumed mirror symmetric: compare curves against
    # the analytic solution above, not endpoints selected by different boundaries.
    result = {'status': 'PROTOTYPE fixture checks passed; no nODD geometry/response validation',
              'pyacts': importlib.metadata.version('pyacts'), 'acts': str(acts.__version__),
              'python': platform.python_version(), 'platform': platform.platform(),
              'project_revision': subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
              'project_worktree_dirty':bool(subprocess.check_output(['git','status','--porcelain'],text=True).strip()),
              'command':shlex.join([os.path.relpath(sys.executable),*sys.argv]),
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'solenoid_axis_comparison': {'radius_mm':radius,'length_mm':length,
                 'central_field_T':3.,'acts_nCoils':1000,'fixture_tolerance_T':1e-5,
                 'samples':solenoid,'scope':'Finite discrete ACTS coils versus continuous thin sheet; no ferromagnetic material'},
              'configuration': {'p_GeV':10., 'eta':.5, 'phi':0., 'vertex_mm':[0,0,0],
                                'seed':228, 'material_effects':False, 'geometry':'ACTS GenericDetector fixture'},
              'cases':cases, 'endpoint_reversal_difference_mm_descriptive':reversal_residual,
              'limitations':['No nODD active geometry, material, field map or performance checked.',
                             'OBJ serialization limits precision; tolerance applies only to fixtures.',
                             'Half-step run is an analytic cross-check, not a full adaptive-tolerance convergence study.']}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2)+'\n')
    print(f'{len(cases)} ACTS propagation fixture checks passed; report {args.report}')


if __name__ == '__main__':
    main()
