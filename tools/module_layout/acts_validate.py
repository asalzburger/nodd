#!/usr/bin/env python3
"""PROTOTYPE native ACTS propagation audit of finite active sensor patches.

All patches are retained in one Gen-3 leaf with TryAllNavigationPolicy. This
retains every active patch without overlapping layer volumes. The full native
Navigator control exposes curved-track candidate loss in that single leaf.
The main audit therefore uses actual ACTS trajectory states, supporting-plane
target propagations and finite native bounds, with explicit scope limits.
"""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np

CODE_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def _git(*args, cwd=None):
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def runtime_provenance(acts_source=None):
    import acts
    import ROOT
    result = dict(python=platform.python_version(), executable=sys.executable,
                  platform=platform.platform(), acts_python=str(Path(acts.__file__).resolve()),
                  acts_extension_sha256=digest(acts.ActsPythonBindings.__file__),
                  root_version=ROOT.gROOT.GetVersion(), numpy=np.__version__,
                  project_revision=_git("rev-parse", "HEAD"),
                  code_sha256=CODE_SHA256,
                  code_uncommitted=bool(_git("status", "--porcelain", "--", __file__)))
    if acts_source is not None:
        source = Path(acts_source)
        result.update(acts_source_revision=_git("rev-parse", "HEAD", cwd=source),
                      acts_source_changes=_git("status", "--porcelain", cwd=source).splitlines(),
                      acts_source_diff_sha256=hashlib.sha256(subprocess.check_output(
                          ["git", "diff", "HEAD"], cwd=source)).hexdigest(),
                      acts_sensitivity_binding_sha256=digest(source / "Python/Core/src/Surfaces.cpp"))
    return result


def construct(layout, host_radius_mm=1140., host_half_z_mm=3150.):
    """Return geometry, patch-ID map, and retained Python lifetime owners."""
    import acts
    if not hasattr(acts.Surface, "assignIsSensitive"):
        raise RuntimeError("ACTS Surface.assignIsSensitive is required (ACTS PR #6176)")
    ctx = acts.GeometryContext.dangerouslyDefaultConstruct()
    surfaces = []
    modules = layout["modules"]
    if not modules or len({m["id"] for m in modules}) != len(modules):
        raise ValueError("A nonempty layout with unique active-patch IDs is required")
    max_radius = 0.
    max_z = 0.
    low, high = np.full(3, np.inf), np.full(3, -np.inf)
    for module in modules:
        u, v = np.asarray(module["u"]), np.asarray(module["v"])
        n = np.cross(u, v)
        rotation = acts.RotationMatrix3(acts.Vector3(*u), acts.Vector3(*v), acts.Vector3(*n))
        center = np.asarray(module["center_mm"])
        transform = acts.Transform3(acts.Vector3(*center), rotation)
        surface = acts.Surface.createPlane(transform, acts.RectangleBounds(
            float(module["half_u_mm"]), float(module["half_v_mm"])))
        surface.assignIsSensitive(True)
        if max(abs(surface.center(ctx)[j] - center[j]) for j in range(3)) > 1e-9:
            raise AssertionError("ACTS transform changed a patch center")
        for su in (-1, 1):
            for sv in (-1, 1):
                corner = center + su * module["half_u_mm"] * u + sv * module["half_v_mm"] * v
                max_radius = max(max_radius, math.hypot(*corner[:2]))
                max_z = max(max_z, abs(corner[2]))
                low, high = np.minimum(low, corner), np.maximum(high, corner)
        surfaces.append(surface)
    # Leaves are navigation envelopes, not physical support or material.
    # A cuboid keeps every arbitrary plane without requiring concentrically
    # aligned volumes. Counted steps are clipped to the cylindrical study host.
    # Padding covers the full host even in sparse test fixtures. Keep the box
    # tight so pT=1 GeV central tracks exit before their first half-turn.
    root = acts.Blueprint(envelope=acts.ExtentEnvelope(x=[1., 1.], y=[1., 1.], z=[1., 1.]))
    leaf = root.addLayer("PROTOTYPE-all-active-patches")
    leaf.layerType = acts.LayerBlueprintNode.LayerType.Plane
    leaf.surfaces = surfaces
    half_extent, midpoint = (high - low) / 2., (high + low) / 2.
    padding = np.maximum(0., np.array([host_radius_mm, host_radius_mm, host_half_z_mm])
                         + abs(midpoint) - half_extent) + 1.
    leaf.envelope = acts.ExtentEnvelope(x=[float(padding[0])] * 2,
                                       y=[float(padding[1])] * 2,
                                       z=[float(padding[2])] * 2)
    options = acts.BlueprintOptions()
    options.defaultNavigationPolicyFactory = acts.NavigationPolicyFactory.make().add(acts.TryAllNavigationPolicy)
    geometry = root.construct(options, ctx, acts.logging.WARNING)
    visited = []
    geometry.visitSurfaces(lambda surface: visited.append(surface))
    identifiers = {(int(surface.geometryId.volume), int(surface.geometryId.sensitive)): module["id"]
                   for surface, module in zip(surfaces, modules)}
    if len(visited) != len(modules) or len(identifiers) != len(modules) or not all(s.isSensitive for s in visited):
        raise AssertionError("ACTS did not retain all uniquely sensitive active patches")
    return geometry, identifiers, (ctx, root, leaf, surfaces)


def write_particles(tracks, work):
    """Create explicit vertices and preserve the CSV reader's float32 inputs.

    Each track has a unique primary vertex: the extractor otherwise shares the
    first particle's origin across all particles with the same vertex barcode.
    ACTS' CSV ParticleData stores float, so the oracle receives the exact
    effective float32 origin/momentum, despite writing 17 significant digits.
    """
    keys = ["particle_id_pv", "particle_id_sv", "particle_id_part", "particle_id_gen",
            "particle_id_subpart", "particle_type", "process", "vx", "vy", "vz", "vt",
            "px", "py", "pz", "m", "q"]
    effective = []
    path = work / "event000000000-particles.csv"
    with path.open("w") as output:
        writer = csv.DictWriter(output, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        for i, track in enumerate(tracks):
            x, y, z = map(float, np.asarray(track.get("origin_mm", [0., 0., 0.]), dtype=np.float32))
            pt = float(track.get("pt_GeV", 1.))
            eta, phi = float(track["eta"]), float(track["phi"])
            px, py, pz = map(float, np.asarray([pt * math.cos(phi), pt * math.sin(phi),
                                               pt * math.sinh(eta)], dtype=np.float32))
            charge = float(track.get("charge", 1.))
            if charge not in (-1., 1.):
                raise ValueError("ACTS audit currently requires charge +1 or -1")
            row = dict.fromkeys(keys, 0)
            row.update(particle_id_pv=i + 1, particle_id_part=1,
                       particle_type=-13 if charge > 0 else 13, vx=x, vy=y, vz=z,
                       px=px, py=py, pz=pz, q=charge, m=.1056583755)
            writer.writerow(row)
            rounded_pt = math.hypot(px, py)
            effective.append(dict(track, origin_mm=[x, y, z], phi=math.atan2(py, px),
                                  eta=math.asinh(pz / rounded_pt), pt_GeV=rounded_pt,
                                  charge=charge))
    return effective, path


def propagate(geometry, identifiers, tracks, work, max_step_mm=10.):
    """Run EigenStepper and real Navigator, retaining ROOT surface IDs."""
    import acts
    import acts.examples as ex
    from acts.examples.root import RootPropagationStepsWriter
    import ROOT
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    fields = {float(t.get("field_T", 0.)) for t in tracks}
    if len(fields) != 1:
        raise ValueError("Each propagation batch must contain exactly one constant field")
    effective, csv_path = write_particles(tracks, work)
    field = fields.pop()
    root_path = work / "propagation-steps.root"
    seq = ex.Sequencer(events=1, numThreads=1, logLevel=acts.logging.WARNING)
    seq.addReader(ex.CsvParticleReader(inputDir=str(work), inputStem="particles",
                                      outputParticles="particles", level=acts.logging.WARNING))
    seq.addAlgorithm(ex.ParticleTrackParamExtractor(level=acts.logging.WARNING,
                     inputParticles="particles", outputTrackParameters="params"))
    nav = acts.Navigator(trackingGeometry=geometry, resolveSensitive=True,
                         resolveMaterial=False, resolvePassive=False)
    stepper = acts.EigenStepper(acts.ConstantBField(acts.Vector3(0., 0., field * acts.UnitConstants.T)))
    propagator = ex.ConcretePropagator(acts.Propagator(stepper, nav))
    seq.addAlgorithm(ex.PropagationAlgorithm(propagatorImpl=propagator, level=acts.logging.WARNING,
                     sterileLogger=False, inputTrackParameters="params", outputSummaryCollection="summary",
                     energyLoss=False, multipleScattering=False, recordMaterialInteractions=False,
                     maxStepSize=max_step_mm * acts.UnitConstants.mm, ptLoopers=0.))
    seq.addWriter(RootPropagationStepsWriter(level=acts.logging.WARNING, collection="summary",
                                             filePath=str(root_path)))
    seq.run()
    root_file = ROOT.TFile.Open(str(root_path))
    tree = root_file.Get("propagation_steps")
    if int(tree.GetEntries()) != len(tracks):
        raise AssertionError(f"ACTS wrote {tree.GetEntries()} of {len(tracks)} tracks; propagation denominator lost")
    observations = []
    for i, row in enumerate(tree):
        if int(row.track_nr) != i:
            raise AssertionError("ACTS ROOT track order changed")
        points = np.column_stack([list(row.g_x), list(row.g_y), list(row.g_z)])
        directions = np.column_stack([list(row.d_x), list(row.d_y), list(row.d_z)])
        if len(points) < 2 or not np.all(np.isfinite(points)):
            raise AssertionError("ACTS wrote an empty or nonfinite trajectory")
        if np.linalg.norm(points[0] - effective[i]["origin_mm"]) > 1e-4:
            raise AssertionError("ACTS changed the requested luminous origin")
        expected_direction = np.array([math.cos(effective[i]["phi"]), math.sin(effective[i]["phi"]),
                                       math.sinh(effective[i]["eta"])]) / math.cosh(effective[i]["eta"])
        if np.linalg.norm(directions[0] - expected_direction) > 1e-6:
            raise AssertionError("ACTS changed the requested initial direction")
        patch_hits, hit_positions = [], []
        for j, (volume, sensitive) in enumerate(zip(row.volume_id, row.sensitive_id)):
            if int(sensitive) > 0:
                key = int(volume), int(sensitive)
                if key not in identifiers:
                    raise AssertionError(f"Unknown native ACTS sensitive ID: {key}")
                patch_hits.append(identifiers[key])
                hit_positions.append(points[j].tolist())
        observations.append(dict(patch_hits=patch_hits, hit_positions_mm=hit_positions,
                                 points=points, written_steps=len(points)))
    root_file.Close()
    return observations, effective, dict(field_T=field, csv_sha256=digest(csv_path),
                                         root_sha256=digest(root_path))


def validate_full_navigation(layout, tracks, work, expected_patch_hits=None, *, host_radius_mm=1140.,
             host_half_z_mm=3150., max_step_mm=10., acts_source=None):
    """Audit all finite patches and every supplied track against the oracle.

    Returns disagreements explicitly. A caller must require ``passed``; neither
    propagation success nor a nonzero number of hits establishes coverage.
    Optional expected_patch_hits overrides the oracle for negative-control tests.
    """
    try:
        from .intersections import track_sensor_hits, positions, traversal_limit
    except ImportError:
        from intersections import track_sensor_hits, positions, traversal_limit
    start_time = time.monotonic()
    geometry, identifiers, owners = construct(layout, host_radius_mm, host_half_z_mm)
    work = Path(work)
    by_field = {}
    for i, track in enumerate(tracks):
        by_field.setdefault(float(track.get("field_T", 0.)), []).append((i, track))
    observations, effective = [None] * len(tracks), [None] * len(tracks)
    files = []
    for field, indexed in sorted(by_field.items()):
        observed, rounded, artifacts = propagate(geometry, identifiers, [t for _, t in indexed],
                                                 work / f"field-{field:g}T", max_step_mm)
        files.append(artifacts)
        for (i, _), observation, track in zip(indexed, observed, rounded):
            observations[i], effective[i] = observation, track
    expected = (expected_patch_hits if expected_patch_hits is not None else
                track_sensor_hits(layout, effective, return_patch_hits=True,
                                  host_radius_mm=host_radius_mm, host_half_z_mm=host_half_z_mm))
    by_id = {m["id"]: m for m in layout["modules"]}
    mismatches, per_track = [], []
    maximum_residual = 0.
    for i, (track, observation, prediction) in enumerate(zip(effective, observations, expected)):
        actual = observation["patch_hits"]
        wanted, got = set(prediction), set(actual)
        points = observation["points"]
        eta, phi = track["eta"], track["phi"]
        origin = np.asarray(track["origin_mm"])
        curvature = -.000299792458 * track["charge"] * track.get("field_T", 0.) / track["pt_GeV"]
        if abs(math.sinh(eta)) > 1e-8:
            arc = (points[:, 2] - origin[2]) / math.sinh(eta)
        elif curvature:
            angles = np.arctan2(math.sin(phi) + curvature * (points[:, 0] - origin[0]),
                               math.cos(phi) - curvature * (points[:, 1] - origin[1]))
            phase = (angles - phi + math.pi) % (2. * math.pi) - math.pi
            arc = np.unwrap(phase) / curvature
        else:
            arc = (points[:, 0] - origin[0]) * math.cos(phi) + (points[:, 1] - origin[1]) * math.sin(phi)
        residual = float(np.max(np.linalg.norm(points - positions(track, arc), axis=1)))
        maximum_residual = max(maximum_residual, residual)
        end = traversal_limit(track, host_radius_mm, host_half_z_mm)
        # Float32 ROOT positions and CSV inputs set the diagnostic tolerance.
        trajectory_tolerance_mm = .002
        endpoint_shortfall = max(0., end - float(arc[-1]))
        if wanted != got or residual > trajectory_tolerance_mm or endpoint_shortfall > trajectory_tolerance_mm:
            mismatches.append(dict(track=i, missing=sorted(wanted - got), extra=sorted(got - wanted),
                                   trajectory_residual_mm=residual, endpoint_shortfall_mm=endpoint_shortfall))
        sensors = {by_id[p].get("sensor_id", p) for p in got}
        per_track.append(dict(track=i, input=tracks[i], effective_input=track,
                              expected_patch_hits=sorted(wanted), observed_patch_hits=sorted(got),
                              observed_sensor_hits=sorted(sensors), written_steps=observation["written_steps"],
                              duplicate_sensitive_steps=len(actual) - len(got),
                              trajectory_residual_mm=residual, endpoint_shortfall_mm=endpoint_shortfall))
    return dict(status="PROTOTYPE; native ACTS navigation audit, not detector acceptance",
                passed=not mismatches, tracks_requested=len(tracks), tracks_written=len(observations),
                active_patches=len(identifiers), physical_sensors=len({m.get("sensor_id", m["id"]) for m in layout["modules"]}),
                geometry_sha256=json_digest(layout), tracks_sha256=json_digest(tracks),
                construction="Python finite sensitive planes in one Gen-3 leaf; TryAllNavigationPolicy",
                propagation="ACTS EigenStepper + Navigator; RootPropagationStepsWriter sensitive IDs",
                host_radius_mm=host_radius_mm, host_half_z_mm=host_half_z_mm, max_step_mm=max_step_mm,
                trajectory_tolerance_mm=.002, maximum_trajectory_residual_mm=maximum_residual,
                csv_float32_inputs=True, max_expected_hits_override=expected_patch_hits is not None,
                mismatches=mismatches, per_track=per_track, artifacts=files,
                runtime=runtime_provenance(acts_source), elapsed_seconds=time.monotonic() - start_time,
                limitations=["Finite audit sample; bulk coverage statistics use the independently audited analytic oracle.",
                             "Vacuum transport: no material, scattering, energy loss, response or reconstruction.",
                             "One navigation leaf is an exhaustive software control, not a production navigation hierarchy.",
                             "Rectangle active patches only; future surface shapes require an explicit matching adapter."])


def validate(layout, tracks, work, expected_patch_hits=None, *, host_radius_mm=1140.,
             host_half_z_mm=3150., max_step_mm=None, acts_source=None, exhaustive=False):
    """Audit native finite-plane target propagations, including negative trials.

    This does not validate the global Navigator. The exhaustive TryAll control
    above exposes its candidate loss in a large curved-track navigation leaf.
    With the step-size binding each conservative voxel candidate's supporting
    plane is targeted directly by ACTS' EigenStepper/VoidNavigator, followed by
    native finite-bounds membership. Older bindings use native guide-state
    reanchoring. No analytic hit prediction selects candidates.
    The shared broad phase is checked against exhaustive all-plane controls.
    """
    import acts
    try:
        from .intersections import SurfaceIndex, positions, traversal_limit
    except ImportError:
        from intersections import SurfaceIndex, positions, traversal_limit
    start_time = time.monotonic()
    geometry, identifiers, owners = construct(layout, host_radius_mm, host_half_z_mm)
    ctx, surfaces = owners[0], owners[-1]
    # The target aborter's finite-bound check can miss a plane while taking a
    # long curved step whose tangent initially falls outside the small patch.
    # Propagate to its unbounded supporting plane, then ask ACTS' actual finite
    # RectangleBounds to decide the hit. Geometry and sensitive IDs stay those
    # of the finite plane; this is an intersection audit, not a navigation claim.
    target_planes = []
    for surface, module in zip(surfaces, layout["modules"]):
        u, v = np.asarray(module["u"]), np.asarray(module["v"])
        rotation = acts.RotationMatrix3(acts.Vector3(*u), acts.Vector3(*v), acts.Vector3(*np.cross(u, v)))
        target = acts.Surface.createPlane(acts.Transform3(acts.Vector3(*module["center_mm"]), rotation), None)
        target.assignGeometryId(surface.geometryId)
        target_planes.append(target)
    index = SurfaceIndex(layout)
    by_id = {m["id"]: m for m in layout["modules"]}
    propagators = {}
    per_track, mismatches = [], []
    total_candidates, total_native_hits, total_target_calls, maximum_residual = 0, 0, 0, 0.
    step_size = 10. if max_step_mm is None else float(max_step_mm)
    if not math.isfinite(step_size) or step_size <= 0.:
        raise ValueError("max_step_mm must be positive and finite")
    direct_mode = hasattr(acts.PropagatorPlainOptions(ctx, acts.MagneticFieldContext()), "stepping")
    error_counts = {}
    for i, track in enumerate(tracks):
        field = float(track.get("field_T", 0.))
        if field not in propagators:
            propagators[field] = acts.EigenVoidPropagator(
                acts.EigenStepper(acts.ConstantBField(acts.Vector3(0., 0., field * acts.UnitConstants.T))),
                acts.VoidNavigator(), acts.logging.FATAL)
        propagator = propagators[field]
        origin = list(map(float, track.get("origin_mm", [0., 0., 0.])))
        eta, phi = float(track["eta"]), float(track["phi"])
        pt, charge = float(track.get("pt_GeV", 1.)), float(track.get("charge", 1.))
        if charge not in (-1., 1.):
            raise ValueError("Native audit requires charge +1 or -1")
        transverse_limit = traversal_limit(track, host_radius_mm, host_half_z_mm)
        options = acts.PropagatorPlainOptions(ctx, acts.MagneticFieldContext())
        options.pathLimit = transverse_limit * math.cosh(eta)
        options.maxSteps = 10000
        options.surfaceTolerance = 1e-6
        options.loopProtection = False
        if direct_mode:
            options.stepping.maxStepSize = step_size * acts.UnitConstants.mm
        start = acts.BoundTrackParameters.createCurvilinear(
            acts.Vector4(*origin, 0.), phi, 2. * math.atan(math.exp(-eta)),
            charge / (pt * math.cosh(eta)), None, acts.ParticleHypothesis.muon)
        candidates = (np.arange(len(surfaces)) if exhaustive else
                      index.candidates(track, transverse_limit))
        predicted = ([layout["modules"][j]["id"] for j, _ in index.hits(
            track, host_radius_mm=host_radius_mm, host_half_z_mm=host_half_z_mm,
            all_surfaces=exhaustive)] if expected_patch_hits is None else expected_patch_hits[i])
        wanted, actual, hit_positions = set(predicted), set(), []
        # The current binding cannot set target-propagation maxStepSize. Build
        # native double-precision guide states by propagating to cross-section
        # planes 10 mm ahead, normal to the current momentum. Such a plane is
        # approached from below in a constant field. Reanchor target trials at
        # the native state immediately before their supporting-plane crossing.
        guide_states, guide_points, guide_paths = [start], [np.asarray(origin)], [0.]
        path = 0.
        guide_step = step_size
        path_limit = options.pathLimit
        while not direct_mode and path < path_limit - 1e-6:
            state = guide_states[-1]
            pars = state.parameters
            direction = np.array([math.cos(pars[2]) * math.sin(pars[3]),
                                  math.sin(pars[2]) * math.sin(pars[3]), math.cos(pars[3])])
            distance = min(guide_step, path_limit - path)
            guide_center = guide_points[-1] + distance * direction
            reference = np.array([0., 0., 1.]) if abs(direction[2]) < .9 else np.array([1., 0., 0.])
            u = np.cross(reference, direction)
            u /= np.linalg.norm(u)
            v = np.cross(direction, u)
            rotation = acts.RotationMatrix3(acts.Vector3(*u), acts.Vector3(*v), acts.Vector3(*direction))
            guide = acts.Surface.createPlane(acts.Transform3(acts.Vector3(*guide_center), rotation), None)
            guide_options = acts.PropagatorPlainOptions(ctx, acts.MagneticFieldContext())
            guide_options.pathLimit = distance * 1.01 + 1e-6
            guide_options.surfaceTolerance = 1e-6
            guide_options.loopProtection = False
            state = propagator.propagateToSurface(state, guide, guide_options)
            bound = state.parameters
            point = guide_center + bound[0] * u + bound[1] * v
            if abs(math.sinh(eta)) > 1e-8:
                path = (point[2] - origin[2]) / math.tanh(eta)
            elif field:
                curvature = -.000299792458 * charge * field / pt
                phase = (bound[2] - phi + math.pi) % (2. * math.pi) - math.pi
                path = phase / curvature * math.cosh(eta)
            else:
                path = ((point[0] - origin[0]) * math.cos(phi)
                        + (point[1] - origin[1]) * math.sin(phi)) * math.cosh(eta)
            if path <= guide_paths[-1]:
                raise AssertionError("Native guide trajectory did not advance")
            guide_states.append(state)
            guide_points.append(point)
            guide_paths.append(path)
        guide_points = np.asarray(guide_points)
        native_errors, residual_max, target_calls, bounds_rejections = {}, 0., 0, 0
        for j in candidates:
            surface = surfaces[j]
            module = layout["modules"][j]
            signed = (guide_points - module["center_mm"]) @ np.cross(module["u"], module["v"])
            brackets = ([0] if direct_mode else np.flatnonzero((signed[:-1] * signed[1:] <= 0.)
                         | (abs(signed[:-1]) <= 1e-6) | (abs(signed[1:]) <= 1e-6)))
            end = None
            for segment in brackets:
                if direct_mode:
                    local_options = options
                else:
                    local_options = acts.PropagatorPlainOptions(ctx, acts.MagneticFieldContext())
                    local_options.pathLimit = max(1e-6, min(guide_paths[segment + 1], path_limit)
                                                   - guide_paths[segment] + 1e-6)
                    local_options.surfaceTolerance = 1e-6
                    local_options.loopProtection = False
                target_calls += 1
                try:
                    trial = propagator.propagateToSurface(start if direct_mode else guide_states[segment],
                                                         target_planes[j], local_options)
                except RuntimeError as exc:
                    error = str(exc)
                    native_errors[error] = native_errors.get(error, 0) + 1
                    error_counts[error] = error_counts.get(error, 0) + 1
                    continue
                bound = trial.parameters
                if surface.bounds.inside(acts.Vector2(bound[0], bound[1])):
                    end = trial
                    break
                bounds_rejections += 1
            if end is None:
                continue
            bound = end.parameters
            native_id = (int(end.referenceSurface.geometryId.volume),
                         int(end.referenceSurface.geometryId.sensitive))
            patch_id = identifiers[native_id]
            if patch_id != module["id"]:
                raise AssertionError("Native target propagation returned a different surface ID")
            point = (np.asarray(module["center_mm"]) + bound[0] * np.asarray(module["u"])
                     + bound[1] * np.asarray(module["v"]))
            curvature = -.000299792458 * charge * field / pt
            if abs(math.sinh(eta)) > 1e-8:
                arc = (point[2] - origin[2]) / math.sinh(eta)
            elif curvature:
                angle = math.atan2(math.sin(phi) + curvature * (point[0] - origin[0]),
                                   math.cos(phi) - curvature * (point[1] - origin[1]))
                phase = (angle - phi + math.pi) % (2. * math.pi) - math.pi
                arc = phase / curvature
            else:
                arc = ((point[0] - origin[0]) * math.cos(phi)
                       + (point[1] - origin[1]) * math.sin(phi))
            residual = float(np.linalg.norm(point - positions(track, arc)))
            residual_max = max(residual_max, residual)
            if not -1e-6 <= arc <= transverse_limit + .002:
                raise AssertionError("ACTS target propagation crossed the first host traversal limit")
            actual.add(patch_id)
            hit_positions.append(dict(patch_id=patch_id, position_mm=point.tolist(),
                                      transverse_path_mm=float(arc)))
        total_candidates += len(candidates)
        total_target_calls += target_calls
        total_native_hits += len(actual)
        maximum_residual = max(maximum_residual, residual_max)
        if wanted != actual or residual_max > .002:
            mismatches.append(dict(track=i, missing=sorted(wanted - actual), extra=sorted(actual - wanted),
                                   trajectory_residual_mm=residual_max))
        per_track.append(dict(track=i, input=track, tested_candidates=len(candidates),
                              expected_patch_hits=sorted(wanted), observed_patch_hits=sorted(actual),
                              observed_sensor_hits=sorted({by_id[p].get("sensor_id", p) for p in actual}),
                              native_propagation_errors=sum(native_errors.values()),
                              native_bounds_rejections=bounds_rejections,
                              native_target_calls=target_calls,
                              negative_candidate_targets=len(candidates) - len(actual),
                              native_guide_states=0 if direct_mode else len(guide_states),
                              native_error_counts=native_errors, hit_positions=hit_positions,
                              trajectory_residual_mm=residual_max))
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    report = dict(status="PROTOTYPE; native ACTS finite-surface propagation audit, not global navigation validation",
                  passed=not mismatches, tracks_requested=len(tracks), tracks_written=len(tracks),
                  active_patches=len(identifiers),
                  physical_sensors=len({m.get("sensor_id", m["id"]) for m in layout["modules"]}),
                  geometry_sha256=json_digest(layout), tracks_sha256=json_digest(tracks),
                  construction="Python finite sensitive planes retained in one Gen-3 cuboid leaf",
                  propagation=("ACTS EigenVoidPropagator direct supporting-plane targets with bounded maxStepSize; native finite RectangleBounds.inside and returned geometry IDs"
                               if direct_mode else "ACTS EigenVoidPropagator with native guide-state reanchoring to supporting planes; native finite RectangleBounds.inside and returned geometry IDs"),
                  candidate_selection="all planes" if exhaustive else "conservative voxel/helix-sagitta superset shared with oracle",
                  tested_candidate_targets=total_candidates, reached_native_targets=total_native_hits,
                  native_target_calls=total_target_calls,
                  negative_candidate_targets=total_candidates - total_native_hits,
                  native_target_error_counts=error_counts, exhaustive=exhaustive,
                  native_propagation_errors=sum(error_counts.values()),
                  native_bounds_rejections=sum(t["native_bounds_rejections"] for t in per_track),
                  host_radius_mm=host_radius_mm, host_half_z_mm=host_half_z_mm,
                  path_limit="Exact first host exit or transverse half-turn, per track, expressed in 3D path length",
                  max_steps=10000, surface_tolerance_mm=1e-6, trajectory_tolerance_mm=.002,
                  native_guide_step_mm=None if direct_mode else step_size,
                  max_step_mm=step_size if direct_mode else None,
                  native_max_step_size_binding=direct_mode,
                  maximum_trajectory_residual_mm=maximum_residual, csv_float32_inputs=False,
                  mismatches=mismatches, per_track=per_track,
                  runtime=runtime_provenance(acts_source), elapsed_seconds=time.monotonic() - start_time,
                  limitations=["Finite audit sample; bulk coverage uses the independently tested analytic oracle.",
                               "Per-target native transport validates finite intersections, not global ACTS navigation.",
                               "The large TryAll leaf loses curved-track candidates; its failed control is retained separately.",
                               "Broad-phase candidate code is shared; exhaustive small-fixture controls test that boundary.",
                               "No material, scattering, energy loss, response or reconstruction.",
                               "Rectangle active patches only; future shapes require matching native bounds adapters."]
                              + ([] if direct_mode else ["Native guide segments bracket supporting-plane crossings; unsampled tangencies or double crossings inside one guide segment remain a limitation."]))
    (work / "native-target-audit.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--layout", type=Path)
    source.add_argument("--candidate", choices=["cobe", "pint"])
    parser.add_argument("--variant", default="flat")
    parser.add_argument("--pixel-family", default="mixed")
    parser.add_argument("--tracks", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--acts-source", type=Path)
    parser.add_argument("--full-navigation", action="store_true",
                        help="Run the adverse single-leaf Navigator control instead of the target audit")
    args = parser.parse_args()
    if args.layout is not None:
        layout = json.loads(args.layout.read_text())
    else:
        from geometry import generate_layout
        layout = generate_layout(args.candidate, args.variant, args.pixel_family)
    tracks = json.loads(args.tracks.read_text())
    if isinstance(tracks, dict) and "per_track" in tracks:
        tracks = [entry["input"] for entry in tracks["per_track"]]
    runner = validate_full_navigation if args.full_navigation else validate
    result = runner(layout, tracks, args.work, acts_source=args.acts_source)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: result[k] for k in ("passed", "active_patches", "tracks_written", "mismatches", "elapsed_seconds")}))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
