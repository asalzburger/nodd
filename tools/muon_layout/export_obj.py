"""Export current native ACTS chamber faces and fixed toroid warm envelopes.

Visualization only. No chamber, coil, field or propagation result is changed.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.muon_layout.acts.prepare import configuration, export_geometry
from tools.muon_layout.geometry import vertices3, volume
from tools.toroid_prototype.geometry import loop_polyline

BLUE = (0, 96, 255)
GREY = (160, 160, 160)
NAME = 'chambers-and-coils'
ARC_STEPS = 64


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def chambers(native, panels):
    """Use actual native finite-face vertices, rather than a plotting outline."""
    faces = defaultdict(list)
    with (native/'geometry-corners.csv').open(newline='') as stream:
        for row in csv.DictReader(stream):
            key = int(row['panel_index']), int(row['face_index'])
            assert int(row['vertex_index']) == len(faces[key])
            faces[key].append([float(row[k+'_m']) for k in ('x', 'y', 'z')])
    assert len(faces) == 6*len(panels)
    objects = []
    maximum = 0.
    for i, body in enumerate(panels):
        expected = vertices3(body)
        center = expected.mean(axis=0)
        polygons = []
        for f in range(6):
            polygon = np.array(faces[i, f])
            assert polygon.shape == (4, 3)
            residual = np.linalg.norm(polygon[:, None, :]-expected[None, :, :], axis=2).min(axis=1)
            maximum = max(maximum, float(residual.max()))
            assert residual.max() < 1e-10
            normal = np.cross(polygon[1]-polygon[0], polygon[2]-polygon[0])
            if np.dot(normal, polygon.mean(axis=0)-center) < 0:
                polygon = polygon[::-1]
            polygons.append(polygon)
        name = 'chamber_'+re.sub(r'[^A-Za-z0-9_.-]', '_', body['id'])
        objects.append((name, BLUE, polygons))
    return objects, maximum


def coils(config):
    """Closed rectangular-section sweeps; shared warm reservations stay separate."""
    a, b = config['warm']['normal_m']/2, config['warm']['tangent_m']/2
    objects = []
    for family, group in config['coil_groups'].items():
        rz = loop_polyline(group, 0., ARC_STEPS)[:-1, [0, 2]]
        center = np.array([group['center_r_m'], group['center_z_m']])
        half = np.array([group['half_r_m'], group['half_z_m']])
        rho = group['corner_radius_m']
        relative = rz-center
        normal = (relative-np.clip(relative, -(half-rho), half-rho))/rho
        assert np.allclose(np.linalg.norm(normal, axis=1), 1., atol=1e-12)
        for k in range(config['folds']):
            phi = np.radians(group['phi_offset_deg']+k*360/config['folds'])
            er = np.array([np.cos(phi), np.sin(phi), 0.])
            et = np.array([-np.sin(phi), np.cos(phi), 0.])
            rings = []
            for sn, st in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                offset = rz+sn*a*normal
                rings.append(offset[:, :1]*er+offset[:, 1:]*[0, 0, 1]+st*b*et)
            rings = np.array(rings)
            polygons = []
            for j in range(len(rz)):
                nxt = (j+1) % len(rz)
                for side in range(4):
                    other = (side+1) % 4
                    polygons.append(rings[[side, other, other, side], [j, j, nxt, nxt]])
            objects.append((f'coil_{family}_{k:02d}', GREY, polygons))
    return objects


def write_input(path, objects):
    assert len({o[0] for o in objects}) == len(objects)
    with path.open('w') as stream:
        stream.write(f'{len(objects)}\n')
        for name, color, faces in objects:
            stream.write(f'{name} {color[0]} {color[1]} {color[2]} {len(faces)}\n')
            for face in faces:
                stream.write(str(len(face))+' '+' '.join(format(float(v), '.17g') for v in np.asarray(face).ravel())+'\n')


def deduplicate_materials(path):
    """Installed ACTS emits repeated identical blocks; retain their first copy."""
    raw = path.read_bytes()
    blocks = re.split(r'(?=^newmtl )', raw.decode(), flags=re.M)
    unique = {}
    for block in blocks:
        if not block.strip():
            continue
        name = block.splitlines()[0].split()[1]
        assert name not in unique or unique[name] == block
        unique[name] = block
    assert len(unique) == 2
    path.write_text(''.join(unique.values()))
    return hashlib.sha256(raw).hexdigest()


def read_obj(path):
    vertices, objects = [], {}
    name = material = None
    for line in path.read_text().splitlines():
        item = line.split()
        if not item:
            continue
        if item[0] == 'mtllib':
            assert item[1:] == [path.with_suffix('.mtl').name]
        elif item[0] == 'o':
            assert len(item) == 2 and item[1] not in objects
            name = item[1]
            objects[name] = []
        elif item[0] == 'usemtl':
            material = item[1]
        elif item[0] == 'v':
            assert len(item) == 4
            vertices.append(list(map(float, item[1:])))
        elif item[0] == 'f':
            ids = [int(i)-1 for i in item[1:]]
            assert len(ids) == 4 and min(ids) >= 0 and max(ids) < len(vertices)
            objects[name].append((material, np.array([vertices[i] for i in ids])))
        elif not line.startswith('#'):
            raise ValueError('unexpected OBJ record: '+line)
    assert np.isfinite(vertices).all()
    return objects, len(vertices)


def verify(path, expected, panels):
    objects, count = read_obj(path)
    assert list(objects) == [o[0] for o in expected]
    maximum, minimum_volume = 0., float('inf')
    chamber_volume_error = 0.
    for index, (name, color, polygons) in enumerate(expected):
        actual = objects[name]
        assert len(actual) == len(polygons)
        edges = Counter()
        directed = Counter()
        signed_volume = 0.
        for (material, face), wanted in zip(actual, polygons):
            assert material == 'material_'+'_'.join(map(str, color))
            error = np.abs(face-wanted).max()
            maximum = max(maximum, float(error))
            assert error < 1e-12
            ids = [tuple(np.round(v, 9)) for v in face]
            assert len(set(ids)) == 4
            for a, b in zip(ids, ids[1:]+ids[:1]):
                edges[tuple(sorted((a, b)))] += 1
                directed[a, b] += 1
            for j in (1, 2):
                signed_volume += np.dot(face[0], np.cross(face[j], face[j+1]))/6
        assert all(v == 2 for v in edges.values())
        assert all(directed[b, a] == n for (a, b), n in directed.items())
        assert signed_volume > 0
        minimum_volume = min(minimum_volume, signed_volume)
        if index < len(panels):
            chamber_volume_error = max(chamber_volume_error, abs(signed_volume-volume(panels[index])))
    assert chamber_volume_error < 1e-10
    material = path.with_suffix('.mtl').read_text()
    assert material.count('newmtl ') == 2
    for color in (BLUE, GREY):
        block = material.split('newmtl material_'+'_'.join(map(str, color))+'\n')[1].split('newmtl ')[0]
        kd = next(line.split()[1:] for line in block.splitlines() if line.startswith('Kd '))
        assert np.allclose(list(map(float, kd)), np.array(color)/256, atol=5.1e-7, rtol=0)
    return dict(objects=len(objects), chamber_objects=len(panels), coil_objects=len(objects)-len(panels),
                raw_obj_vertices=count, quad_faces=sum(len(o[2]) for o in expected),
                all_objects_closed_and_consistently_oriented=True,
                maximum_obj_roundtrip_coordinate_error_m=maximum,
                maximum_chamber_volume_error_m3=chamber_volume_error,
                minimum_positive_object_volume_m3=minimum_volume,
                materials=2, coordinates='metres; right-handed xyz; beam along z')


def preview(path, objects):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    for color, alpha in ((GREY, 1.), (BLUE, .24)):
        faces = [face for _, col, fs in objects if col == color for face in fs]
        ax.add_collection3d(Poly3DCollection(faces, facecolors=np.array(color)/256,
                                            edgecolors='none', alpha=alpha, rasterized=True))
    ax.set(xlim=(-10, 10), ylim=(-10, 10), zlim=(-13, 13), xlabel='x [m]', ylabel='y [m]', zlabel='z [m]')
    ax.set_box_aspect((20, 20, 26))
    ax.view_init(elev=17, azim=-48)
    ax.legend(handles=[Patch(color=np.array(BLUE)/256, label='1,560 chamber envelopes'),
                       Patch(color=np.array(GREY)/256, label='36 toroid warm envelopes')], loc='upper left')
    ax.set_title('PR90 current geometry · chambers and coils\nPROTOTYPE · chamber transparency in this preview only')
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--propagator', type=Path, required=True)
    parser.add_argument('--writer', type=Path, required=True)
    parser.add_argument('--acts-library', type=Path, required=True)
    parser.add_argument('--work', type=Path, default=ROOT/'reference/cache/pr90-obj')
    parser.add_argument('--output', type=Path, default=ROOT/'docs/validation/DES-040/obj')
    args = parser.parse_args()
    args.work.mkdir(parents=True, exist_ok=True)
    args.output.mkdir(parents=True, exist_ok=True)
    config = configuration()
    geometry_path = ROOT/config['geometry']
    geometry = json.loads(geometry_path.read_text())
    panels = export_geometry(config, args.work/'geometry.txt')
    command = [str(args.propagator.resolve()), '--geometry', str(args.work/'geometry.txt'),
               '--field', 'zero', '--inspect-only', '--output-dir', str(args.work/'native')]
    subprocess.run(command, check=True)
    chamber_objects, native_error = chambers(args.work/'native', panels)
    objects = chamber_objects+coils(geometry['magnetic_configuration'])
    write_input(args.work/'objects.txt', objects)
    obj = args.output/(NAME+'.obj')
    subprocess.run([str(args.writer.resolve()), str(args.work/'objects.txt'), str(obj)], check=True)
    raw_mtl = deduplicate_materials(obj.with_suffix('.mtl'))
    checks = verify(obj, objects, panels)
    checks['maximum_native_corner_to_source_corner_error_m'] = native_error
    preview(args.output/(NAME+'.png'), objects)
    revision = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    source_files = ['tools/muon_layout/export_obj.py', 'tools/muon_layout/obj_writer/writer.cpp',
                    'tools/muon_layout/obj_writer/CMakeLists.txt', 'tools/muon_layout/acts/propagate.cpp',
                    'tools/muon_layout/acts/prepare.py', 'tools/muon_layout/geometry.py',
                    'tools/toroid_prototype/geometry.py']
    fingerprints = {p: sha(ROOT/p) for p in source_files}
    clean = all(hashlib.sha256(subprocess.check_output(['git', '-C', str(ROOT), 'show', revision+':'+p])).hexdigest() == digest
                for p, digest in fingerprints.items())
    assert clean, 'commit the export sources before capturing final provenance'
    report = dict(status='PROTOTYPE; current geometry visualization only', source_revision=revision,
                  source_files_match_revision=clean, source_sha256=fingerprints,
                  geometry_sha256=sha(geometry_path), unchanged_field_map_sha256=sha(ROOT/config['map']),
                  native_propagator_sha256=sha(args.propagator), obj_writer_sha256=sha(args.writer),
                  acts_library_sha256=sha(args.acts_library),
                  native_inspection_command=command, native_metadata=json.loads((args.work/'native/metadata.json').read_text()),
                  native_face_corners_sha256=sha(args.work/'native/geometry-corners.csv'),
                  native_faces_sha256=sha(args.work/'native/geometry.csv'),
                  raw_acts_material_sha256=raw_mtl,
                  material_processing='Deduplicate byte-identical ACTS material blocks; relative sibling mtllib; no color/coordinate changes.',
                  coil_representation='36 fixed toroid warm-envelope sweeps; overlapping sleeves remain separate allocations, not a Boolean union. No solenoid, frame, world, entrance or track objects.',
                  colors_rgb_8bit=dict(chambers=BLUE, coils=GREY), acts_material_rgb_divisor=256,
                  arc_segments_per_quadrant=ARC_STEPS,
                  maximum_coil_chord_sagitta_m=max((g['corner_radius_m']+geometry['magnetic_configuration']['warm']['normal_m']/2)*(1-np.cos(np.pi/(4*ARC_STEPS))) for g in geometry['magnetic_configuration']['coil_groups'].values()),
                  checks=checks, artifacts={p.name: sha(p) for p in (obj, obj.with_suffix('.mtl'), args.output/(NAME+'.png'))})
    (args.output/'export.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    with zipfile.ZipFile(args.output/(NAME+'.zip'), 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in (obj, obj.with_suffix('.mtl')):
            entry = zipfile.ZipInfo(path.name, date_time=(2026, 10, 19, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, path.read_bytes())
    print(json.dumps(checks, indent=2))


if __name__ == '__main__':
    main()
