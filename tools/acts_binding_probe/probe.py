#!/usr/bin/env python3
"""PROTOTYPE: wheel-only Gen-3 construction with synthetic module fixtures."""
import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import shlex
import subprocess
import sys

import acts
import acts.json


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def specs():
    """All lengths are synthetic test values in ACTS mm, not nODD dimensions."""
    groups = []
    for name, radius, z, barrel in [
        ('TEST-negative-disc', 70., -100., False),
        ('TEST-barrel-inner', 50., 0., True),
        ('TEST-barrel-outer', 100., 0., True),
        ('TEST-positive-disc', 70., 100., False),
    ]:
        modules = []
        for i in range(8):
            phi = i * math.tau / 8
            c, s = math.cos(phi), math.sin(phi)
            # Local u tangential; v longitudinal (barrel) or inward radial (disc).
            rotation = [-s, 0., c, c, 0., s, 0., 1., 0.] if barrel else [-s, -c, 0., c, -s, 0., 0., 0., 1.]
            modules.append(dict(kind='PlaneRectangle', sensitive=True,
                                transform=dict(translation=[radius*c, radius*s, z], rotation=rotation),
                                bounds=dict(type='RectangleBounds', values=[-10., -20., 10., 20.])))
        groups.append(dict(name=name, barrel=barrel, modules=modules))
    return groups


def construction(work, policy):
    ctx = acts.GeometryContext.dangerouslyDefaultConstruct()
    groups = specs()
    path = work / f'test-modules-{policy}.json'
    definitions = [m for g in groups for m in g['modules']]
    path.write_text(json.dumps(definitions, indent=2) + '\n')
    reader = acts.json.SurfaceJsonOptions()
    reader.inputFile = str(path)
    reader.jsonEntryPath = []
    surfaces = acts.json.readSurfaceVectorFromJson(reader)
    assert len(surfaces) == 32 and all(s.isSensitive for s in surfaces)
    root = acts.Blueprint(envelope=acts.ExtentEnvelope(r=[5., 5.], z=[5., 5.]))
    detector = root.addCylinderContainer('TEST-detector', acts.AxisDirection.AxisZ)
    barrel = None
    nodes = []
    for j, group in enumerate(groups):
        if group['barrel']:
            if barrel is None:
                barrel = detector.addCylinderContainer('TEST-barrel', acts.AxisDirection.AxisR)
                barrel.addStaticVolume(acts.Transform3.Identity(), acts.CylinderVolumeBounds(0.,40.,21.), 'TEST-beam-void')
            parent = barrel
        else:
            parent = detector.addCylinderContainer(group['name']+'-container', acts.AxisDirection.AxisR)
            z = group['modules'][0]['transform']['translation'][2]
            parent.addStaticVolume(acts.Transform3(acts.Vector3(0.,0.,z)),
                                   acts.CylinderVolumeBounds(0.,40.,1.), group['name']+'-void')
        node = parent.addLayer(group['name'])
        nodes.append(node)  # Keep handles: children getter is broken in this wheel.
        node.layerType = (acts.LayerBlueprintNode.LayerType.Cylinder if group['barrel']
                          else acts.LayerBlueprintNode.LayerType.Disc)
        node.surfaces = surfaces[j*8:(j+1)*8]
        node.envelope = acts.ExtentEnvelope(r=[1.,1.], z=[1.,1.])
        if policy == 'array':
            cfg = acts.SurfaceArrayNavigationPolicy.Config()
            cfg.layerType = (acts.SurfaceArrayNavigationPolicy.LayerType.Cylinder if group['barrel']
                             else acts.SurfaceArrayNavigationPolicy.LayerType.Disc)
            cfg.bins = (8, 1) if group['barrel'] else (1, 8)
            portals = acts.TryAllNavigationPolicy.Config()
            portals.sensitives = False
            node.navigationPolicyFactory = (acts.NavigationPolicyFactory.make()
                .add(acts.TryAllNavigationPolicy, portals).add(acts.SurfaceArrayNavigationPolicy, cfg))
    options = acts.BlueprintOptions()
    options.defaultNavigationPolicyFactory = acts.NavigationPolicyFactory.make().add(acts.TryAllNavigationPolicy)
    geo = root.construct(options, ctx, acts.logging.WARNING)
    seen = []
    geo.visitSurfaces(lambda s: seen.append(s))
    assert len(seen) == 32 and all(s.isSensitive for s in seen)
    assert len({s.geometryId.value for s in seen}) == 32
    assert all(geo.findVolumeByName(g['name']) is not None for g in groups)
    for sf, definition in zip(surfaces, definitions):
        center = sf.center(ctx)
        assert max(abs(center[i]-definition['transform']['translation'][i]) for i in range(3)) < 1e-9
        normal = sf.normal(ctx, center, acts.Vector3(1,0,0))
        rotation = definition['transform']['rotation']
        assert max(abs(normal[i]-rotation[i*3+2]) for i in range(3)) < 1e-12
    acts.Navigator(trackingGeometry=geo, resolveSensitive=True, resolveMaterial=True, resolvePassive=True)
    return geo, ctx, surfaces, definitions, root, nodes


def navigation(geo, ctx, surfaces, definitions, path):
    # Diagnostic uses hardcoded seed42, origin starts, and straight rays.
    acts.pseudoNavigation(geo, ctx, path, 200, 1, (-3., 3.), acts.logging.WARNING)
    with path.open() as handle:
        reader = csv.reader(handle)
        header = next(reader)
        rows = list(reader)
    assert header == ['x','y','z','volume','boundary','sensitive','material']
    assert all(len(r) == 8 and all(math.isfinite(float(v)) for v in r) for r in rows)
    by_run = {}
    for row in rows:
        by_run.setdefault(int(row[0]), []).append(row)
    assert set(by_run) == set(range(200))
    catalog = {(sf.geometryId.volume, sf.geometryId.sensitive): definition
               for sf, definition in zip(surfaces, definitions)}
    crossed = set()
    hit_rows = 0
    by_region = dict(barrel=0, negative_disc=0, positive_disc=0)
    for run_rows in by_run.values():
        # Every straight-ray sample gives its direction from the known origin.
        point = next([float(v) for v in r[1:4]] for r in run_rows
                     if sum(float(v)**2 for v in r[1:4]) > 1e-8)
        norm = math.sqrt(dot(point, point))
        direction = [v/norm for v in point]
        expected = set()
        for identifier, definition in catalog.items():
            center = definition['transform']['translation']
            matrix = definition['transform']['rotation']
            u, v, normal = ([matrix[i*3+j] for i in range(3)] for j in range(3))
            denominator = dot(normal, direction)
            if abs(denominator) < 1e-12:
                continue
            distance = dot(normal, center) / denominator
            if distance <= 0:
                continue
            relative = [distance*d-c for d,c in zip(direction, center)]
            # CSV coordinates have limited precision; no sampled ray is near an edge.
            if abs(dot(relative,u)) <= 10. and abs(dot(relative,v)) <= 20.:
                expected.add(identifier)
        actual = {(int(r[4]),int(r[6])) for r in run_rows if int(r[6]) > 0}
        assert actual == expected, (actual, expected)
        assert sum(int(r[6]) > 0 for r in run_rows) == len(actual)
        for identifier in actual:
            z = catalog[identifier]['transform']['translation'][2]
            by_region['barrel' if z == 0 else 'negative_disc' if z < 0 else 'positive_disc'] += 1
        hit_rows += sum(int(r[6]) > 0 for r in run_rows)
        crossed.update(actual)
    assert hit_rows > 0
    assert all(value > 0 for value in by_region.values())
    return dict(rays=200, seed=42, rows=len(rows), module_intersections=hit_rows,
                distinct_modules_crossed=len(crossed), analytic_ray_comparisons=200,
                mismatched_rays=0, csv_sha256=digest(path),
                module_intersections_by_region=by_region,
                csv_header_missing_leading_run=True)


def limitations():
    ctx = acts.GeometryContext.dangerouslyDefaultConstruct()
    translation = acts.Vector3(50.,0.,0.)
    rotation = acts.RotationMatrix3(acts.Vector3(0,1,0),acts.Vector3(0,0,1),acts.Vector3(1,0,0))
    broken = acts.Transform3(translation,rotation)
    finite = all(math.isfinite(broken.translation[i]) for i in range(3))
    safe = (acts.Transform3(translation) * acts.AngleAxis3(math.pi/2,acts.Vector3(0,0,1))
            * acts.AngleAxis3(math.pi/2,acts.Vector3(1,0,0)))
    direct = acts.Surface.createPlane(safe,acts.RectangleBounds(10.,20.))
    direct.assignGeometryId(acts.GeometryIdentifier(sensitive=1))
    assert all(math.isfinite(direct.center(ctx)[i]) for i in range(3))
    assert not direct.isSensitive
    children_error = None
    try:
        acts.Blueprint().children
    except RuntimeError as error:
        children_error = str(error)
    return dict(two_argument_transform_is_finite=finite,
                composed_transform_is_finite=True,
                direct_surface_sensitive_after_id_assignment=direct.isSensitive,
                assignIsSensitive_bound=hasattr(acts.Surface,'assignIsSensitive'),
                layer_setProtoLayer_bound=hasattr(acts.LayerBlueprintNode,'setProtoLayer'),
                tracking_volume_addSurface_bound=hasattr(acts.TrackingVolume,'addSurface'),
                children_getter_error=children_error)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True)
    args = parser.parse_args()
    args.work.mkdir(parents=True,exist_ok=True)
    report = dict(status='PROTOTYPE software capability only; no detector acceptance',
        checked_date='2026-09-21', pyacts=importlib.metadata.version('pyacts'),
        python=platform.python_version(),platform=platform.platform(),
        command=shlex.join(['python','-B',*sys.argv]),
        project_revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        code_sha256=digest(Path(__file__)), limitations=limitations(), fixtures={})
    for policy in ['try_all','array']:
        geo,ctx,surfaces,definitions,root,nodes = construction(args.work,policy)
        result = navigation(geo,ctx,surfaces,definitions,args.work/f'test-navigation-{policy}.csv')
        result.update(sensitive_modules=32, cylinder_layers=2, disc_layers=2,
                      unique_module_ids=32, center_tolerance_mm=1e-9,normal_tolerance=1e-12,
                      module_input_sha256=digest(args.work/f'test-modules-{policy}.json'))
        report['fixtures'][policy] = result
    assert report['fixtures']['try_all']['module_intersections'] == report['fixtures']['array']['module_intersections']
    receipt=Path('reference/cache/pyacts-bindings-install.json')
    if receipt.exists():
        install=json.loads(receipt.read_text())['install'][0]
        report['wheel']=dict(url=install['download_info']['url'],sha256=install['download_info']['archive_info']['hashes']['sha256'])
    args.report.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(report['fixtures'],indent=2))


if __name__ == '__main__':
    main()
