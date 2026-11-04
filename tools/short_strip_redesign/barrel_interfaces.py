#!/usr/bin/env python3
"""DES-043 source-only barrel pickup interface screen; no native geometry claim.

Default: compact JSON on stdout. ``--output [PATH]`` additionally saves it
(default PATH: build/short-strip-redesign/barrel-interfaces.json).
Baseline construction constants are guarded by exact Git-source SHA-256 values;
proposed stack, lands and rail dimensions come from the selected central input.
"""

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCE_REVISION = "476826f6b369a34d9fef08e56cfae5dfcdcda32e"
BASELINE_HASHES = {
    "tools/short_strip_barrel/model.py": "39b85f4f50ab28caa785cf9ac3248598446ae3926be0bbf617bec16ffadf6d3e",
    "tools/short_strip_barrel/inputs-phi-tilted.json": "8cf2e44ae392bf727e1671ec728452a5ef3de741729e4c8118be2ba81c55c52b",
    "tools/short_strip_barrel/export.py": "3675efeada968dba0bb1d22c5901a66cfaf46bee5b9415b51b3c1d4bb334a8af",
}
TOLERANCE_MM = 1e-9
# Proposed barrel window convention: .05 mm clearance on each planar edge.
# This is a source-screen assumption, not an instantiated barrel CSG solid.
WINDOW_CLEARANCE_MM = .05


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


@dataclass(frozen=True)
class Box:
    xy: tuple
    u: tuple
    w: tuple
    hu: float
    hw: float
    zlo: float
    zhi: float
    role: str


def box(radius, phi, tilt, u, z, w, width, length, thickness, role):
    angle = phi + tilt
    eu = (-math.sin(angle), math.cos(angle))
    ew = (math.cos(angle), math.sin(angle))
    xy = (radius * math.cos(phi) + u * eu[0] + w * ew[0],
          radius * math.sin(phi) + u * eu[1] + w * ew[1])
    return Box(xy, eu, ew, width / 2, thickness / 2,
               z - length / 2, z + length / 2, role)


def separating_bound(a, b):
    """Exact box SAT sign; positive value is a lower bound on distance.

    All barrel boxes share the global z axis. The complete 3-D SAT therefore
    consists of z and the four planar rectangle edge normals (unit vectors).
    """
    delta = (b.xy[0] - a.xy[0], b.xy[1] - a.xy[1])
    gaps = [max(b.zlo - a.zhi, a.zlo - b.zhi)]
    for axis in (a.u, a.w, b.u, b.w):
        support = (a.hu * abs(dot(a.u, axis)) + a.hw * abs(dot(a.w, axis))
                   + b.hu * abs(dot(b.u, axis)) + b.hw * abs(dot(b.w, axis)))
        gaps.append(abs(dot(delta, axis)) - support)
    return max(gaps)


def radial_bounds(a):
    """Exact rectangle radial extrema, including closest points on edges."""
    points = [(a.xy[0] + su * a.hu * a.u[0] + sw * a.hw * a.w[0],
               a.xy[1] + su * a.hu * a.u[1] + sw * a.hw * a.w[1])
              for su, sw in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    maximum = max(math.hypot(*p) for p in points)
    minimum = maximum
    for p, q in zip(points, points[1:] + points[:1]):
        d = (q[0] - p[0], q[1] - p[1])
        t = max(0., min(1., -dot(p, d) / dot(d, d)))
        minimum = min(minimum, math.hypot(p[0] + t * d[0], p[1] + t * d[1]))
    return minimum, maximum


def self_controls():
    a = box(0, 0, 0, 0, 0, 0, 2, 2, 2, "control")
    values = {"overlap": separating_bound(a, box(0, 0, 0, 1.5, 0, 0, 2, 2, 2, "control")),
              "touch": separating_bound(a, box(0, 0, 0, 2, 0, 0, 2, 2, 2, "control")),
              "separate": separating_bound(a, box(0, 0, 0, 3, 0, 0, 2, 2, 2, "control")),
              "z_separate": separating_bound(a, box(0, 0, 0, 0, 3, 0, 2, 2, 2, "control"))}
    # Thin parallel boxes with overlapping axis-aligned bounds, separated along
    # their rotated normals. This exercises the OBB axes rather than only AABBs.
    p = box(0, 0, math.pi / 4, 0, 0, 0, 4, 2, .2, "control")
    q = box(0, 0, math.pi / 4, 0, 0, .3, 4, 2, .2, "control")
    values["rotated_separate"] = separating_bound(p, q)
    passed = all(abs(values[k] - expected) < 1e-12 for k, expected in
                 (("overlap", -.5), ("touch", 0.), ("separate", 1.), ("z_separate", 1.), ("rotated_separate", .1)))
    if not passed:
        raise ValueError("SAT self-control failed: " + repr(values))
    return {"passed": passed, "bounds_mm": values}


def module_parts(b, c, radius, phi, row, pitch, proposed):
    z = (row - (b['rows'] - 1) / 2) * pitch
    lift = (row % 2) * b['row_lift_mm']
    tilt = math.radians(b['phi_tilt_deg'])
    parts = []

    def add(role, u, v, dw, size):
        parts.append(box(radius, phi, tilt, u, z + v, lift + dw, *size, role))

    # Fixed baseline export.py:144-155; its source hash is mandatory above.
    add('active', 0, 0, 0, b['active_mm'])
    for side in (-1, 1):
        add('guard_u', side * 24.25, 0, 0, [.5, 97, .2])
        add('guard_v', 0, side * 48.25, 0, [48, .5, .2])
    if proposed:
        for role in ('bumps', 'redistribution', 'spreader', 'TIM', 'backing'):
            low, high = c['native_module'][role + '_w_mm']
            add(role, 0, 0, (low + high) / 2, [48, 96, high - low])
        for u, v in c['thermal']['ASIC_centres_uv_mm']:
            for role in ('ASIC', 'ASIC_glue'):
                low, high = c['native_module'][role + '_w_mm']
                add(role, u, v, (low + high) / 2,
                    [*c['thermal']['ASIC_tile_mm'][:2], high - low])
    else:
        add('bumps', 0, 0, -.1125, [48, 96, .025])
        for u in (-12, 12):
            for v in (-36, -12, 12, 36):
                add('ASIC', u, v, -.2, [23.4, 23.4, .15])
        for role, dw, thickness in (('ASIC_glue', -.325, .1), ('spreader', -.475, .2),
                                    ('isolation', -.5875, .025), ('backing_glue', -.65, .1),
                                    ('backing', -.8, .2)):
            add(role, 0, 0, dw, [48, 96, thickness])
    # Flex and host-frame wraps retain the baseline routing (export.py:156-166).
    for side in (-1, 1):
        add('flex', 0, side * 50, -.5, [49, 3, .1])
        bottom, top = -6.8, lift - .55
        parts.append(box(radius, phi, tilt, 26.3, z + side * 50,
                         (bottom + top) / 2, .1, 3, top - bottom, 'tail'))
        add('front_bridge', (24.5 + 26.35) / 2, side * 50, -.5, [1.85, 3, .1])
        parts.append(box(radius, phi, tilt, (24 + 26.35) / 2, z + side * 50,
                         -6.85, 2.35, 3, .1, 'back_bridge'))
    return parts


def pickups(b, c, radius, phi, row, pitch, proposed):
    lift = row % 2 * b['row_lift_mm']
    z = (row - (b['rows'] - 1) / 2) * pitch
    if proposed:
        bottom = c['native_module']['insert_bottom_w_mm']
        top = lift + c['native_module']['TIM_w_mm'][0]
        offset = c['thermal']['barrel_pad_u_mm']
        width, length = c['thermal']['barrel_pad_mm']
    else:
        bottom, top, offset = -1.3, lift - .9, 10.
        width, length = b['pickup_mm']
    if top <= bottom:
        raise ValueError('Nonpositive pickup height')
    return [box(radius, phi, math.radians(b['phi_tilt_deg']), side * offset, z,
                (bottom + top) / 2, width, length, top - bottom, 'pickup') for side in (-1, 1)]


def supports(b, c, model, radius, phi, proposed):
    tilt = math.radians(b['phi_tilt_deg'])
    result = []

    def add(role, u, z, w, width, length, thickness):
        result.append(box(radius, phi, tilt, u, z, w, width, length, thickness, role))

    for role, w, thickness in (('front_skin', -1.375, .15), ('front_glue', -1.5, .1),
                                ('core_envelope', -4.05, 5.), ('back_glue', -6.6, .1),
                                ('back_skin', -6.725, .15)):
        add(role, 0, 0, w, b['stave_width_mm'], 2420, thickness)
    add('rail_PI', 0, 0, -6.875, 26, 2420, .15)
    for side in (-1, 1):
        add('Cu_rail', side * 6.25, 0, -7.05,
            c['barrel_rail_width_mm'] if proposed else b['power_bus_width_mm'], 2420,
            c['rail_thickness_mm'] if proposed else b['power_bus_copper_mm'])
        if proposed:
            # Separate conservative benchmark, not a second installed rail.
            add('old_Cu_rail_benchmark', side * 6.25, 0, -7.05,
                b['power_bus_width_mm'], 2420, b['power_bus_copper_mm'])
    add('signal_bus', 20, 0, -6.85, 8, 2420, .1)
    shoe = model['foot_profile'](b, radius)
    bottom = shoe['center_w_mm'] - shoe['height_mm'] / 2 - abs(shoe['bottom_slope']) * b['foot_width_mm'] / 2
    for z in b['bearing_z_mm']:
        add('foot_enclosing_box', b['foot_u_mm'], z, (bottom - 6.8) / 2,
            b['foot_width_mm'], b['ring_axial_mm'], -6.8 - bottom)
    for side in (-1, 1):
        add('end_board', 0, side * 1230, 4, 52, 30, 8)
    return result


def screen(b, c, model, layout, proposed):
    minima, overlaps = {}, Counter()
    own_minima, own_overlaps = {}, Counter()
    own_comparisons = 0
    comparisons, layers = 0, []
    pitch, rows = layout['row_pitch_mm'], b['rows']

    def compare(a, other):
        nonlocal comparisons
        distance = separating_bound(a, other)
        comparisons += 1
        minima[other.role] = min(minima.get(other.role, math.inf), distance)
        if distance < -TOLERANCE_MM:
            overlaps[other.role] += 1
        return distance

    for layer in layout['layers']:
        radius, count = layer['nominal_radius_mm'], layer['staves']
        candidates = [pickups(b, c, radius, 0, row, pitch, proposed) for row in range(rows)]
        initial_count = comparisons
        layer_minimum = math.inf
        envelope = [item for row in range(rows) for item in
                    module_parts(b, c, radius, 0, row, pitch, proposed) + candidates[row]]
        envelope += supports(b, c, model, radius, 0, proposed)
        for row, pads in enumerate(candidates):
            for pad in pads:
                for other in module_parts(b, c, radius, 0, row, pitch, proposed):
                    if proposed and other.role == 'backing':
                        continue  # Declared same-module backing window.
                    distance = separating_bound(pad, other)
                    own_comparisons += 1
                    own_minima[other.role] = min(own_minima.get(other.role, math.inf), distance)
                    if distance < -TOLERANCE_MM:
                        own_overlaps[other.role] += 1
        for stave in range(count):
            phi = stave * 2 * math.pi / count
            others = [module_parts(b, c, radius, phi, row, pitch, proposed)
                      + pickups(b, c, radius, phi, row, pitch, proposed) for row in range(rows)]
            cold = supports(b, c, model, radius, phi, proposed)
            for row, pads in enumerate(candidates):
                for pad in pads:
                    # Same-module backing/support intersections require the
                    # declared CSG windows; exclude these intentional hosts.
                    for other_row in range(max(0, row - 1), min(rows, row + 2)):
                        if stave == 0 and other_row == row:
                            continue
                        for other in others[other_row]:
                            layer_minimum = min(layer_minimum, compare(pad, other))
                    if stave != 0:
                        for other in cold:
                            layer_minimum = min(layer_minimum, compare(pad, other))
        # Same-module pad pair has no intentional intersection.
        pair_min = min(separating_bound(*pads) for pads in candidates)
        pickup_radial = [radial_bounds(pad) for pads in candidates for pad in pads]
        bounds = [radial_bounds(item) for item in envelope]
        inner = min(min(x[0] for x in bounds), radius - b['ring_inset_mm'])
        outer = max(x[1] for x in bounds)
        ring_gap = min(x[0] for x in pickup_radial) - (radius - b['ring_inset_mm'] + b['ring_radial_mm'])
        layers.append(dict(layer=layer['layer'], nominal_radius_mm=radius, staves=count,
                           modules=layer['modules'], comparisons=comparisons - initial_count,
                           minimum_sat_separating_bound_mm=layer_minimum,
                           own_pickup_pair_bound_mm=pair_min,
                           pickup_radial_bounds_mm=[min(x[0] for x in pickup_radial), max(x[1] for x in pickup_radial)],
                           bearing_ring_radial_clearance_mm=ring_gap,
                           complete_checked_layer_radial_bounds_mm=[inner, outer]))
    gaps = [right['complete_checked_layer_radial_bounds_mm'][0] - left['complete_checked_layer_radial_bounds_mm'][1]
            for left, right in zip(layers, layers[1:])]
    # More distant rows are excluded exactly along z, independent of phi.
    pad_length = c['thermal']['barrel_pad_mm'][1] if proposed else b['pickup_mm'][1]
    z0 = -(rows - 1) / 2 * pitch
    radius = b['nominal_radii_mm'][0]
    reference_parts = module_parts(b, c, radius, 0, 0, pitch, proposed) + pickups(b, c, radius, 0, 0, pitch, proposed)
    other_half_z = max(max(abs(item.zlo - z0), abs(item.zhi - z0)) for item in reference_parts)
    far_row_gap = 2 * pitch - pad_length / 2 - other_half_z
    passed = (not overlaps and not own_overlaps and min(x['own_pickup_pair_bound_mm'] for x in layers) >= -TOLERANCE_MM
              and min(x['bearing_ring_radial_clearance_mm'] for x in layers) > 0
              and min(gaps) > 0 and far_row_gap > 0)
    return dict(passed=passed, comparisons=comparisons, positive_volume_intersections=sum(overlaps.values()),
                intersection_counts_by_role=dict(overlaps), minimum_sat_separating_bounds_mm=minima,
                own_module_comparisons=own_comparisons, own_module_positive_volume_intersections=sum(own_overlaps.values()),
                own_module_intersection_counts_by_role=dict(own_overlaps), own_module_minimum_sat_bounds_mm=own_minima,
                distant_rows_z_separation_lower_bound_mm=far_row_gap,
                adjacent_layer_radial_clearance_lower_bounds_mm=gaps, layers=layers)


def contact_and_windows(b, c, layout):
    t, stack = c['thermal'], c['native_module']
    width, length = t['barrel_pad_mm']
    offset, pitch = t['barrel_pad_u_mm'], layout['row_pitch_mm']
    heights = [lift + stack['TIM_w_mm'][0] - stack['insert_bottom_w_mm']
               for lift in (0., b['row_lift_mm'])]
    margins = dict(backing_edge_mm=24 - offset - width / 2 - WINDOW_CLEARANCE_MM,
                   stave_edge_mm=b['stave_width_mm'] / 2 - offset - width / 2 - WINDOW_CLEARANCE_MM,
                   stave_end_mm=b['stave_half_length_mm'] - (b['active_half_length_mm'] - 48 + length / 2 + WINDOW_CLEARANCE_MM),
                   adjacent_row_window_gap_mm=pitch - length - 2 * WINDOW_CLEARANCE_MM,
                   adjacent_row_flex_gap_mm=pitch - length / 2 - 51.5,
                   own_back_skin_normal_gap_mm=stack['insert_bottom_w_mm'] - (-6.65))
    lengths, brackets = [], 0
    pipe_r, inner_r = b['tube_OD_mm'] / 2, b['tube_OD_mm'] / 2 - b['tube_wall_mm']
    pipe_u_margin = width / 2 - abs(offset - b['tube_offset_u_mm']) - pipe_r
    for row in range(b['rows']):
        z = abs((row - (b['rows'] - 1) / 2) * pitch)
        lengths.append(max(0., min(z + length / 2, b['stave_half_length_mm']) - max(z - length / 2, b['loop_start_mm'])))
        top = row % 2 * b['row_lift_mm'] + stack['TIM_w_mm'][0]
        for _side in (-1, 1):
            # Analytic centre-of-land witness on the straight leg, not a native
            # Contains()/CSG probe or a measured thermal contact resistance.
            for distance, expected_graphite in ((pipe_r - .01, False), (pipe_r + .01, True)):
                inside_box = (width / 2 > abs(offset - b['tube_offset_u_mm'])
                              and stack['insert_bottom_w_mm'] < b['tube_w_mm'] + distance < top)
                graphite = inside_box and distance > pipe_r
                titanium = inner_r < distance < pipe_r
                if graphite != expected_graphite or titanium == expected_graphite:
                    raise ValueError('Analytic pipe-saddle bracket failed')
                brackets += 1
    overhang = [24 - offset - width / 2, 48 - length / 2]
    overhang_matches = all(abs(a - v) < TOLERANCE_MM for a, v in zip(overhang, t['leakage_corner_overhang_mm']['barrel']))
    witnesses_reach = all(abs((r - (b['rows'] - 1) / 2) * pitch) > b['loop_start_mm'] for r in range(b['rows']))
    passed = (min(margins.values()) > 0 and min(lengths) > 0 and pipe_u_margin > 0
              and max(heights) <= t['maximum_pickup_height_mm'] and overhang_matches and witnesses_reach)
    return dict(passed=passed, proposed_pad_mm=[width, length], proposed_pad_centres_u_mm=[-offset, offset],
                old_pad_centres_u_mm=[-10., 10.], proposed_height_mm=heights,
                old_height_mm=[.4, b['row_lift_mm'] + .4], window_edge_clearance_assumption_mm=WINDOW_CLEARANCE_MM,
                positive_window_clearances_mm=margins, leakage_corner_overhang_mm=overhang,
                overhang_matches_thermal_input=overhang_matches, pipe_cross_section_planar_margin_mm=pipe_u_margin,
                minimum_straight_pipe_contact_length_mm=min(lengths), maximum_straight_pipe_contact_length_mm=max(lengths),
                partial_straight_contact_rows_per_stave=sum(x < length - TOLERANCE_MM for x in lengths),
                analytic_saddle_bracket_points_per_stave=brackets,
                witness_reaches_straight_pipe=witnesses_reach)


def run(input_path, source_revision):
    revision = git('rev-parse', '--verify', source_revision + '^{commit}').decode().strip()
    sources = {path: git('show', revision + ':' + path) for path in BASELINE_HASHES}
    for path, expected in BASELINE_HASHES.items():
        if sha(sources[path]) != expected:
            raise ValueError('Baseline construction source changed; review screen constants: ' + path)
    data = input_path.read_bytes()
    c = json.loads(data)
    b = json.loads(sources['tools/short_strip_barrel/inputs-phi-tilted.json'])
    if c['schema_version'] != 1 or b['lane_step_mm'] != 0 or not b['phi_tilt_deg']:
        raise ValueError('Unsupported schema or non-symmetric barrel frame')
    if c['thermal']['barrel_pad_count'] != 2 or c['native_module']['sensor_mm'] != b['active_mm']:
        raise ValueError('Screen requires two lands and the baseline sensor footprint')
    t, stack = c['thermal'], c['native_module']
    if stack['body_mm'] != [49., 103.] or t['ASIC_tiles'] != len(t['ASIC_centres_uv_mm']):
        raise ValueError('Screen retains baseline body/flex routing and requires consistent ASIC count')
    positive = [*t['barrel_pad_mm'], t['barrel_pad_u_mm'], t['maximum_pickup_height_mm'],
                *t['ASIC_tile_mm'], c['barrel_rail_width_mm'], c['rail_thickness_mm']]
    if any(not math.isfinite(x) or x <= 0 for x in positive):
        raise ValueError('Nonpositive/nonfinite proposed dimensions')
    if len(t['leakage_corner_overhang_mm']['barrel']) != 2 or any(
            not math.isfinite(x) for centre in t['ASIC_centres_uv_mm'] for x in centre):
        raise ValueError('Invalid barrel overhang/ASIC centre parameters')
    previous_bottom = -.1  # Sensor underside; each following layer meets it.
    for role in ('bumps', 'redistribution', 'ASIC', 'ASIC_glue', 'spreader', 'TIM', 'backing'):
        low, high = stack[role + '_w_mm']
        if not all(math.isfinite(x) for x in (low, high)) or low >= high or abs(high - previous_bottom) > TOLERANCE_MM:
            raise ValueError('Noncontiguous or invalid module stack: ' + role)
        previous_bottom = low
    for role, thickness in (('ASIC', t['ASIC_tile_mm'][2]), ('spreader', t['spreader_mm']), ('TIM', t['insulating_TIM_total_mm'])):
        low, high = stack[role + '_w_mm']
        if abs(high - low - thickness) > TOLERANCE_MM:
            raise ValueError('Central thermal/physical thickness mismatch: ' + role)
    if not (c['native_module']['insert_bottom_w_mm'] == c['native_module']['pipe_centre_w_mm'] == b['tube_w_mm']
            and c['native_module']['pipe_OD_mm'] == b['tube_OD_mm']):
        raise ValueError('Screen requires a pipe-centre saddle at the original pipe position')
    for path in ('tools/short_strip_barrel/model.py', 'tools/short_strip_barrel/inputs-phi-tilted.json'):
        if c['baseline_source_sha256'][path] != sha(sources[path]):
            raise ValueError('Central baseline-source pin mismatch: ' + path)
    model = {'__name__': 'pinned_barrel_source', '__file__': str(ROOT / 'tools/short_strip_barrel/model.py')}
    exec(compile(sources['tools/short_strip_barrel/model.py'], revision + ':barrel/model.py', 'exec'), model)
    layout = model['build'](b)  # Pure source layout; no load(), export or native runtime.
    control = self_controls()
    old = screen(b, c, model, layout, False)
    proposed = screen(b, c, model, layout, True)
    contacts = contact_and_windows(b, c, layout)
    central_path = 'tools/short_strip_redesign/inputs.json'
    return dict(schema_version=1, status='PROTOTYPE SOURCE SCREEN', native_geometry_constructed=False,
                passed=old['passed'] and proposed['passed'] and contacts['passed'],
                provenance=dict(source_revision=revision,
                                input_path=str(input_path.resolve().relative_to(ROOT)), input_sha256=sha(data),
                                input_matches_source_revision=sha(data) == sha(git('show', revision + ':' + central_path)),
                                source_sha256={p: sha(d) for p, d in sources.items()},
                                producer_path=str(Path(__file__).resolve().relative_to(ROOT)), producer_sha256=sha(Path(__file__).read_bytes()),
                                python_version=sys.version.split()[0]),
                method=dict(name='finite common-z 3-D box SAT plus analytic pipe/window/radial checks',
                            tolerance_mm=TOLERANCE_MM, row_pitch_mm=layout['row_pitch_mm'],
                            staves=sum(x['staves'] for x in layout['layers']), modules=len(layout['modules']),
                            tested_representative_stave=0, other_staves='all same-layer staves',
                            other_rows='same and adjacent rows; farther rows excluded by exact z bound',
                            rotational_symmetry='Equal-radius staves and identical row staggering permit one source stave per layer.',
                            source_locators=['short_strip_barrel/model.py:75-144 (frame, foot and layout)',
                                             'short_strip_barrel/export.py:99-188 (support, old module, flex, pickup, board, foot and ring)',
                                             'short_strip_redesign/inputs.json:thermal,native_module,rail_thickness_mm,barrel_rail_width_mm']),
                self_controls=control, old_source_control=old, proposed_barrel=proposed, contact_and_windows=contacts,
                limitations=[
                    'Source-level geometric inference only; no DD4hep/ROOT construction, native CSG overlap, Geant4 transport or engineering acceptance.',
                    'Positive SAT values are conservative separating-axis distance bounds, not exact closest-point distances.',
                    'Same-module backing and own cold support intersections are intentional proposed windows; this script does not construct or validate their CSG.',
                    'Pipe contact is conditional on subtracting the actual pipe outer solid from the insert and cutting the declared backing/skin/glue/core windows.',
                    'Old and proposed pickups are compared to their corresponding module stack; this is not a whole-barrel overlap audit of every component pair.',
                    'Sloping feet use conservative enclosing boxes; core envelopes also bound their internal pipes. Cross-layer clearance uses conservative radial envelopes.',
                    'Proposed-land checks retain the old copper rail as an additional conservative benchmark; it is not a second installed conductor.',
                    'Straight-leg contact lengths exclude any beneficial U-bend contact; contact area, bond tolerances, thermal resistance and mechanical strength are unqualified.',
                    'Window edge allowance .05 mm is a proposed source-screen convention. Barrel native construction and contact probes remain required.',
                    'Comparison counts belong to this reproducible all-stave screen; they do not reconstruct earlier temporary inline-script counts.'
                ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=HERE / 'inputs.json')
    parser.add_argument('--source-revision', default=SOURCE_REVISION)
    parser.add_argument('--output', type=Path, nargs='?', const=ROOT / 'build/short-strip-redesign/barrel-interfaces.json')
    args = parser.parse_args()
    report = run(args.input, args.source_revision)
    encoded = json.dumps(report, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n'
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
        print(json.dumps(dict(passed=report['passed'], comparisons=sum(report[k]['comparisons']+report[k]['own_module_comparisons'] for k in ('old_source_control','proposed_barrel')), source_only=True)))
    else:
        print(encoded, end='')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
