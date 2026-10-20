"""Native ACTS exports and actual XY sections for the inward B1 stagger and rotated B2 chambers.

Run after freezing the refinement source. Uses the retained, fingerprinted ACTS
engine and writer; no shared installation, magnetic source or old artifact changes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess

import numpy as np

from . import export_obj as obj
from . import wheels_artifacts as assets
from . import wheels_xy as xy
from .acts.prepare import export_geometry
from .geometry import vertices3, volume

ROOT = Path(__file__).resolve().parents[2]
SCOPE = ROOT / 'docs/validation/DES-040/sketched-stagger-2026-10-20'
BASELINE = ROOT / 'docs/validation/DES-040/barrel-overlap-2026-10-20/candidate/geometry.json'
SOURCE_PATHS = (
    'tools/muon_layout/sketched_artifacts.py',
    'tools/muon_layout/sketched_views.py',
    'tools/muon_layout/sketched_stagger.py',
    'tools/muon_layout/barrel_overlap.py',
    'tools/muon_layout/sketched-stagger-config.json',
    'tools/muon_layout/refined_wheels.py',
    'tools/muon_layout/refined-wheels-config.json',
    'tools/muon_layout/wheels_artifacts.py',
    'tools/muon_layout/wheels_xy.py',
    'tools/muon_layout/export_obj.py',
    'tools/muon_layout/wheel_inventory.py',
    'tools/muon_layout/acts/prepare.py',
    'tools/muon_layout/acts/propagate.cpp',
    'tools/muon_layout/wheels_acts/variant.py',
    'tools/muon_layout/obj_writer/writer.cpp',
    'tools/muon_layout/geometry.py',
    'tools/muon_layout/draw.py',
    'tools/muon_layout/support.py',
    'tools/toroid_prototype/geometry.py',
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')


def frozen_sources():
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    hashes = {}
    for name in SOURCE_PATHS:
        actual = (ROOT / name).read_bytes()
        pinned = subprocess.check_output(['git', 'show', revision + ':' + name], cwd=ROOT)
        if actual != pinned:
            raise ValueError('Freeze executed source before acquisition: ' + name)
        hashes[name] = hashlib.sha256(actual).hexdigest()
    return revision, hashes


def produce(args):
    revision, sources = frozen_sources()
    for path, expected in (
        (args.propagator, assets.EXPECTED_PROPAGATOR),
        (args.writer, assets.EXPECTED_WRITER),
        (args.acts_library, assets.EXPECTED_CORE),
    ):
        if sha(path) != expected:
            raise ValueError('Native dependency fingerprint changed: ' + str(path))
    geometry_hash, baseline_hash = sha(args.geometry), sha(BASELINE)
    geometry = json.loads(args.geometry.read_text())
    out = args.output / 'obj'
    work = out / 'native-inspection'
    work.mkdir(parents=True, exist_ok=True)
    panels = export_geometry({'geometry': str(args.geometry.resolve().relative_to(ROOT))}, work / 'geometry.dat')
    vertices = np.concatenate([vertices3(p) for p in panels])
    if not ((np.hypot(vertices[:, 0], vertices[:, 1]) < 9.1).all() and (abs(vertices[:, 2]) < 13.3).all()):
        raise ValueError('Changed geometry exceeds the retained native world')
    command = [str(args.propagator.resolve()), '--geometry', str(work / 'geometry.dat'),
               '--field', 'zero', '--inspect-only', '--output-dir', str(work),
               '--world-radius-m', '9.1', '--world-half-z-m', '13.3',
               '--entrance-radius-m', '4.35', '--entrance-half-z-m', '6.4684']
    with (work / 'inspection.log').open('w') as stream:
        subprocess.run(command, check=True, stdout=stream, stderr=subprocess.STDOUT)
    chambers, native_error = obj.chambers(work, panels)
    coils = obj.coils(geometry['magnetic_configuration'])
    frame = assets.prism_objects(geometry['supports']['members'])
    volumes = {o[0]: volume(p) for o, p in zip(chambers, panels)}
    volumes.update({o[0]: volume(p) for o, p in zip(frame, geometry['supports']['members'])})
    bundles = {
        'chambers-and-coils': (chambers + coils, 'Inward B1 and rotated B2 chambers and fixed toroid envelopes', False),
        'barrel-chambers': ([o for o, p in zip(chambers, panels) if p['kind'] == 'barrel'], 'Inward B1 and rotated B2 barrel chambers', False),
        'positive-endcap-chambers': ([o for o, p in zip(chambers, panels) if p['kind'] == 'endcap' and p['side'] > 0], 'Unchanged refined positive-endcap chambers', False),
        'toroids-and-frame': (coils + frame, 'Unchanged toroids and frame outer reservations', True),
    }
    checks, artifacts, component_members = {}, {}, []
    for name, (objects, label, has_frame) in bundles.items():
        object_input, target = work / (name + '-objects.txt'), out / (name + '.obj')
        obj.write_input(object_input, objects)
        result = subprocess.run([str(args.writer.resolve()), str(object_input), str(target)],
                                check=True, capture_output=True, text=True)
        original_material = assets.material_cleanup(target.with_suffix('.mtl'), {o[1] for o in objects})
        # ACTS writes trailing blanks in MTL. Preserve every material token
        # while making this new export conform to repository whitespace rules.
        material = target.with_suffix('.mtl')
        raw = material.read_text()
        cleaned = '\n'.join(line.rstrip() for line in raw.splitlines()).rstrip() + '\n'
        assert cleaned.split() == raw.split()
        material.write_text(cleaned)
        checks[name] = assets.verify_obj(target, objects, volumes)
        checks[name].update(assets.preview(out / (name + '.png'), objects, label, has_frame),
                            raw_native_material_sha256=original_material,
                            native_writer_stdout=result.stdout.strip())
        artifacts[name] = {p.name: sha(p) for p in (target, target.with_suffix('.mtl'), out / (name + '.png'))}
        if name != 'chambers-and-coils':
            component_members.extend((target, target.with_suffix('.mtl')))
    zip_checks = {
        'chambers-and-coils.zip': assets.bundle_zip(out / 'chambers-and-coils.zip',
            [out / 'chambers-and-coils.obj', out / 'chambers-and-coils.mtl']),
        'components.zip': assets.bundle_zip(out / 'components.zip', component_members),
    }
    inventory_dir = args.output / 'inventory'
    inventory_dir.mkdir(exist_ok=True)
    change = assets.inventories(BASELINE, args.geometry, inventory_dir)
    from . import wheel_inventory as inventory
    import matplotlib
    barrel_reports = {}
    before_geometry = json.loads(BASELINE.read_text())
    barrel_dims = [inventory.dimensions(p) for model in (before_geometry, geometry) for p in model['panels'] if p['kind']=='barrel']
    barrel_scale = (max(d['tangential_width_m'] for d in barrel_dims), max(d['longitudinal_length_m'] for d in barrel_dims))
    for name, source, label in [('before-barrel', BASELINE, 'Previous 888-chamber candidate'), ('after-barrel', args.geometry, 'Inward B1 and rotated B2')]:
        with matplotlib.rc_context({'savefig.bbox': 'tight', 'savefig.pad_inches': .2}):
            barrel_reports[name] = inventory.write(source, inventory_dir, 'barrel', label, prefix=name, common_limits=barrel_scale)
    change['shape_families'].update({name: report['shape_families'] for name, report in barrel_reports.items()})
    from . import sketched_views
    drawing_dir = args.output / 'views'
    xy_checks = sketched_views.produce(BASELINE, args.geometry, drawing_dir)
    import matplotlib
    report = dict(status='DRAFT isolated PROTOTYPE; no internals, response or engineering acceptance',
        execution_revision=revision, executed_sources_match_revision=True, source_sha256=sources,
        geometry=str(args.geometry.resolve().relative_to(ROOT)), geometry_sha256=geometry_hash,
        baseline_geometry=str(BASELINE.relative_to(ROOT)), baseline_geometry_sha256=baseline_hash,
        unchanged_magnetic_configuration=geometry['magnetic_configuration'] == json.loads(BASELINE.read_text())['magnetic_configuration'],
        unchanged_supports=geometry['supports'] == json.loads(BASELINE.read_text())['supports'],
        unchanged_endcaps=[p for p in geometry['panels'] if p['kind']=='endcap'] == [p for p in json.loads(BASELINE.read_text())['panels'] if p['kind']=='endcap'],
        native_binary_sha256=sha(args.propagator), native_writer_sha256=sha(args.writer), acts_core_sha256=sha(args.acts_library),
        native_inspection_command=[str(Path(x).resolve().relative_to(ROOT)) if x.startswith(str(ROOT)) else x for x in command],
        native_metadata=json.loads((work / 'metadata.json').read_text()),
        native_corner_sha256=sha(work / 'geometry-corners.csv'), native_face_sha256=sha(work / 'geometry.csv'),
        maximum_native_corner_residual_m=native_error, counts=dict(chambers=len(chambers), coils=len(coils), frame=len(frame)),
        checks=checks, zip_checks=zip_checks, obj_artifacts=artifacts,
        inventory_counts=change['counts'], inventory_families=change['shape_families'], xy_checks=xy_checks,
        material_processing='Deduplicate identical ACTS blocks and normalize trailing/EOF whitespace; all material tokens preserved.',
        barrel_view_artifacts={p.name: sha(p) for p in sorted(drawing_dir.iterdir()) if p.suffix in ('.png', '.svg', '.json')},
        runtime=dict(python=platform.python_version(), numpy=np.__version__, matplotlib=matplotlib.__version__),
        limits=[assets.FRAME_SCOPE, 'Blue outlines are native finite chamber volumes; gray coils are warm-envelope sweeps.',
                'No new magnetic, material, detector-response or momentum-resolution calculation is implied.'])
    assert report['unchanged_magnetic_configuration'] and report['unchanged_supports'] and report['unchanged_endcaps']
    assert sha(args.geometry) == geometry_hash and sha(BASELINE) == baseline_hash
    assert all(sha(ROOT / p) == h for p, h in sources.items())
    save(args.output / 'artifacts.json', report)
    print(json.dumps(dict(counts=report['counts'], native_corner_error_m=native_error,
                         inventory=report['inventory_families'], xy=xy_checks), indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry', type=Path, default=SCOPE / 'candidate/geometry.json')
    parser.add_argument('--output', type=Path, default=SCOPE)
    parser.add_argument('--propagator', type=Path, default=ROOT / 'reference/cache/pr90-wheels/build/nodd-muon-wheels-propagate')
    parser.add_argument('--writer', type=Path, default=ROOT / 'reference/cache/pr90-obj/build/nodd-muon-obj')
    parser.add_argument('--acts-library', type=Path, default=Path('/Users/salzburg/Documents/work/installed/acts-nodd/lib/libActsCore.dylib'))
    produce(parser.parse_args())


if __name__ == '__main__':
    main()
