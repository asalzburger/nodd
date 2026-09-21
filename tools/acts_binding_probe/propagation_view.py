#!/usr/bin/env python3
"""PROTOTYPE: ACTS example propagation, written steps and a barrel x-y view."""
import argparse
import csv
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import shlex
import sys
from datetime import datetime, timezone

import acts
import acts.examples as ex
from acts.examples.simulation import (
    addParticleGun, ParticleConfig, EtaConfig, MomentumConfig,
)

from probe import construction, digest, dot

TRACKS = 48
SEED = 42
PT_GEV = 0.1
TOLERANCE_MM = 0.001  # OBJ writer exports six significant digits.


def read_steps(path):
    """Read the upstream writer's vertex blocks and verify their OBJ edges."""
    tracks, points, edges = [], [], []
    offset = 0

    def finish():
        assert len(points) > 2
        assert edges == [(offset+i, offset+i+1) for i in range(1, len(points))]
        tracks.append(points.copy())

    for line in path.read_text().splitlines():
        fields = line.split()
        if fields[0] == 'v':
            if edges:
                finish()
                offset += len(points)
                points, edges = [], []
            point = tuple(map(float, fields[1:]))
            assert len(point) == 3 and all(map(math.isfinite, point))
            points.append(point)
        else:
            assert fields[0] == 'l' and len(fields) == 3
            edges.append(tuple(map(int, fields[1:])))
    finish()
    return tracks


def run(work, field_tesla):
    work.mkdir(parents=True, exist_ok=True)
    geo, ctx, surfaces, definitions, root, nodes = construction(work, 'array')
    seq = ex.Sequencer(events=1, numThreads=1, logLevel=acts.logging.WARNING,
                       outputDir=str(work))
    addParticleGun(
        seq, ParticleConfig(num=TRACKS, pdg=acts.PdgParticle.eMuon,
                            randomizeCharge=False),
        EtaConfig(0., 0.), MomentumConfig(PT_GEV * acts.UnitConstants.GeV,
                                        PT_GEV * acts.UnitConstants.GeV, transverse=True),
        rnd=ex.RandomNumbers(seed=SEED), outputDirCsv=work,
        logLevel=acts.logging.WARNING,
    )
    seq.addAlgorithm(ex.ParticleTrackParamExtractor(
        level=acts.logging.WARNING, inputParticles='particles_generated',
        outputTrackParameters='params'))
    navigator = acts.Navigator(trackingGeometry=geo, resolveSensitive=True,
                               resolveMaterial=False, resolvePassive=False)
    stepper = acts.EigenStepper(acts.ConstantBField(
        acts.Vector3(0., 0., field_tesla * acts.UnitConstants.T)))
    propagator = ex.ConcretePropagator(acts.Propagator(stepper, navigator))
    seq.addAlgorithm(ex.PropagationAlgorithm(
        propagatorImpl=propagator, level=acts.logging.WARNING,
        sterileLogger=False, inputTrackParameters='params',
        outputSummaryCollection='summary', energyLoss=False,
        multipleScattering=False, recordMaterialInteractions=False,
        maxStepSize=2 * acts.UnitConstants.mm,
    ))
    seq.addWriter(ex.ObjPropagationStepsWriter(
        level=acts.logging.WARNING, collection='summary',
        outputDir=str(work), outputScalor=1.,
    ))
    seq.run()
    obj = work / 'event000000000-propagation-steps.obj'
    particles_path = work / 'event000000000-particles.csv'
    tracks = read_steps(obj)
    with particles_path.open() as handle:
        particles = list(csv.DictReader(handle))
    # The algorithm can skip failed propagations, and the OBJ writer omits short
    # tracks. Account for the full generated denominator before trusting order.
    assert len(tracks) == len(particles) == TRACKS
    crossings, max_residual = [], 0.
    barrel = [(i, d) for i, d in enumerate(definitions)
              if d['transform']['translation'][2] == 0.]
    for track_id, (points, particle) in enumerate(zip(tracks, particles)):
        px, py, q = (float(particle[k]) for k in ('px', 'py', 'q'))
        pt = math.hypot(px, py)
        assert abs(pt-PT_GEV) < 1e-8 and q == -1.
        assert math.dist(points[0], (0., 0., 0.)) < TOLERANCE_MM
        assert all(abs(p[2]) < TOLERANCE_MM for p in points)
        assert 106. < math.hypot(*points[-1][:2]) < 108.
        direction = (px/pt, py/pt)
        # Signed transverse curvature: GeV, T -> mm^-1.
        curvature = -q * 0.299792458 * field_tesla / (1000 * pt)
        phi = math.atan2(py, px)
        if curvature:
            center = (-math.sin(phi)/curvature, math.cos(phi)/curvature)
            radius = abs(1/curvature)

            def arc(point):
                angle = math.atan2(curvature*(point[0]-center[0]),
                                   -curvature*(point[1]-center[1]))
                return ((angle-phi) % math.tau) / curvature

            end = arc(points[-1])
            residuals = [abs(math.dist(p[:2], center)-radius) for p in points]
        else:
            end = dot(points[-1][:2], direction)
            residuals = [abs(p[0]*direction[1]-p[1]*direction[0]) for p in points]
        assert max(residuals) < TOLERANCE_MM
        max_residual = max(max_residual, max(residuals))
        expected, observed = set(), set()
        for index, definition in barrel:
            c = definition['transform']['translation']
            rot = definition['transform']['rotation']
            u, normal = ([rot[i*3+j] for i in range(3)] for j in (0, 2))
            if curvature:
                relative = [c[i]-center[i] for i in range(2)]
                b = dot(relative, u[:2])
                discriminant = b*b - dot(relative, relative) + radius*radius
                candidates = [] if discriminant < 0 else [
                    [c[i]+t*u[i] for i in range(2)]
                    for t in (-b-math.sqrt(discriminant), -b+math.sqrt(discriminant))
                    if abs(t) <= 10.]
                predicted = [p for p in candidates if 0 < arc(p) < end]
            else:
                denominator = dot(direction, normal[:2])
                distance = dot(c[:2], normal[:2])/denominator if abs(denominator) > 1e-12 else -1.
                p = [distance*d for d in direction]
                predicted = [p] if 0 < distance < end and abs(dot([p[i]-c[i] for i in range(2)], u[:2])) <= 10. else []
            assert len(predicted) <= 1  # This fixture exits before curling revisits.
            if predicted:
                expected.add(index)
            on_plane = []
            for point in points:
                relative = [point[i]-c[i] for i in range(3)]
                residual = abs(dot(relative, normal))
                if residual < TOLERANCE_MM and abs(dot(relative, u)) <= 10. and abs(relative[2]) <= 20.:
                    on_plane.append((residual, point))
            if on_plane:
                observed.add(index)
                best = min(on_plane)[1]
                assert predicted and math.dist(best[:2], predicted[0]) < 2*TOLERANCE_MM
                crossings.append(dict(track=track_id, module=index,
                                      geometry_id=surfaces[index].geometryId.value,
                                      x_mm=best[0], y_mm=best[1], z_mm=best[2]))
        assert observed == expected, (track_id, observed, expected)
    assert crossings
    result = dict(field_tesla=field_tesla, generated_tracks=TRACKS,
                  written_tracks=len(tracks), written_steps=sum(map(len, tracks)),
                  module_intersections=len(crossings),
                  distinct_modules_crossed=len({c['module'] for c in crossings}),
                  analytic_tracks_matched=TRACKS,
                  max_trajectory_residual_mm=max_residual,
                  obj_sha256=digest(obj), particles_sha256=digest(particles_path),
                  module_input_sha256=digest(work/'test-modules-array.json'))
    return result, tracks, crossings, barrel


def plot(cases, target, cache):
    cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault('MPLCONFIGDIR', str(cache.resolve()))
    os.environ.setdefault('XDG_CACHE_HOME', str(cache.resolve()))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    fig, axes = plt.subplots(1, 2, figsize=(11, 6), layout='constrained')
    fig.get_layout_engine().set(h_pad=.12, w_pad=.08)
    for ax, (result, tracks, crossings, modules) in zip(axes, cases):
        for points in tracks:
            ax.plot([p[0] for p in points], [p[1] for p in points],
                    color='#4286ae', linewidth=.65, alpha=.5)
        for _, module in modules:
            c, rot = module['transform']['translation'], module['transform']['rotation']
            ax.plot([c[0]-10*rot[0], c[0]+10*rot[0]],
                    [c[1]-10*rot[3], c[1]+10*rot[3]], color='#182b39', linewidth=3)
        ax.scatter([c['x_mm'] for c in crossings], [c['y_mm'] for c in crossings],
                   s=17, color='#df7423', edgecolors='white', linewidths=.35, zorder=4)
        ax.scatter([0], [0], color='#182b39', marker='+', s=55, zorder=5)
        ax.set(xlabel='x [mm]', ylabel='y [mm]', xlim=(-115, 115), ylim=(-115, 115),
               aspect='equal', title=f"Bz = {result['field_tesla']:g} T | {result['module_intersections']} module intersections")
        ax.grid(alpha=.17)
        ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('Gen-3 module geometry: recorded ACTS propagation steps\n'
                 'PROTOTYPE · 48 muons per panel · pT = 0.1 GeV · eta = 0 · seed 42', fontsize=13)
    fig.legend(handles=[Line2D([], [], color='#182b39', lw=3, label='Finite barrel module surface'),
                        Line2D([], [], color='#4286ae', lw=1, label='Written propagation path'),
                        Line2D([], [], color='#df7423', marker='o', lw=0, label='Recorded step on a module')],
               loc='outside lower center', ncols=3, frameon=False)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=180, metadata={'Software': 'nODD pyacts propagation prototype'})
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--figure', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    cases = [run(args.work/f'field-{field:g}T', field) for field in (0., 2.)]
    assert cases[0][0]['particles_sha256'] == cases[1][0]['particles_sha256']
    plot(cases, args.figure, args.work/'mpl-cache')
    report = dict(status='PROTOTYPE; central-slice propagation smoke test only',
                  recorded_at=datetime.now(timezone.utc).isoformat(),
                  command=shlex.join(['reference/cache/pyacts-bindings-venv/bin/python', '-B', *sys.argv]),
                  pyacts=importlib.metadata.version('pyacts'),
                  matplotlib=importlib.metadata.version('matplotlib'),
                  python=platform.python_version(), platform=platform.platform(),
                  project_revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  code_uncommitted_at_run=bool(subprocess.check_output(
                      ['git', 'status', '--porcelain', '--', str(Path(__file__)),
                       str(Path(__file__).with_name('probe.py'))], text=True).strip()),
                  code_sha256=digest(Path(__file__)), geometry_code_sha256=digest(Path(__file__).with_name('probe.py')),
                  seed=SEED, pt_GeV=PT_GEV, eta=0., charge=-1,
                  max_step_mm=2., trajectory_and_plane_tolerance_mm=TOLERANCE_MM,
                  intersection_position_tolerance_mm=2*TOLERANCE_MM,
                  writer='ObjPropagationStepsWriter', sterileLogger=False,
                  field_cases=[c[0] for c in cases],
                  intersections=[c[2] for c in cases],
                  figure=str(args.figure), figure_sha256=digest(args.figure),
                  limitations=['ROOT writer absent from tested wheel; used existing OBJ step writer.',
                               'OBJ has positions and connectivity, no surface IDs; intersections are geometrically associated recorded steps.',
                               'Synthetic central barrel slice only; endcaps remain in geometry but are not crossed or projected.',
                               'No material, response, reconstruction, beamspot or coverage validation.'])
    args.report.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report['field_cases'], indent=2))


if __name__ == '__main__':
    main()
