"""Finite-panel and frame views for the isolated DES040 PROTOTYPE.

``draw(geometry, coverage, output)`` writes four review figures. Coordinates
and prism transforms come from generated data; no layout dimensions are chosen
here. Planar cuts intersect complete convex prisms, not their projections.
Coils use the fixed DES039 exact sweep membership at raster cell centres;
only the 3D display tessellates rounded curves. Hollow support members are
rendered through ``support.material_parts`` so cavities stay empty.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .geometry import vertices3
from tools.toroid_prototype.geometry import coil_mask, loop_polyline

STATION_COLORS = {1: '#007f82', 2: '#4169b1', 3: '#8c50a0'}
WARM_COLOR = '#dfa652'
AL_COLOR = '#7a8793'
SS_COLOR = '#384752'
EDGE_INDICES = ((0, 1), (1, 2), (2, 3), (3, 0),
                (4, 5), (5, 6), (6, 7), (7, 4),
                (0, 4), (1, 5), (2, 6), (3, 7))
FACE_INDICES = ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
                (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))


def section_polygon(body, normal, offset, horizontal, vertical, tolerance=1e-9):
    """Convex prism/plane intersection in declared orthonormal plot axes.

    Coincident face cuts retain that face. A point/edge tangent has zero area
    and is omitted. No body outside the plane appears as a projection.
    """
    v = vertices3(body)
    n, u, w = (np.asarray(x, float) for x in (normal, horizontal, vertical))
    distance = v @ n - offset
    if distance.min() > tolerance or distance.max() < -tolerance:
        return None
    points = []
    for i, j in EDGE_INDICES:
        a, b = distance[i], distance[j]
        if abs(a) <= tolerance:
            points.append(v[i])
        if abs(b) <= tolerance:
            points.append(v[j])
        if a*b < 0:
            points.append(v[i] + a/(a-b)*(v[j]-v[i]))
    if len(points) < 3:
        return None
    xy = np.column_stack((np.asarray(points) @ u, np.asarray(points) @ w))
    xy = np.unique(np.round(xy, 10), axis=0)
    if len(xy) < 3:
        return None
    center = xy.mean(axis=0)
    order = np.argsort(np.arctan2(xy[:, 1]-center[1], xy[:, 0]-center[0]))
    xy = xy[order]
    area = abs(np.sum(xy[:, 0]*np.roll(xy[:, 1], -1) -
                      xy[:, 1]*np.roll(xy[:, 0], -1)))/2
    return xy if area > tolerance**2 else None


def _support_parts(geometry):
    # Import lazily: this renderer is also usable with panel-only fixtures.
    members = geometry.get('supports', {}).get('members', [])
    if not members:
        return []
    from .support import material_parts
    parts = []
    for member in members:
        for part in material_parts(member):
            item = dict(part)
            item.setdefault('material', member.get('material', 'Al_proxy'))
            item.setdefault('component', member.get('component', member.get('category', member.get('kind', 'frame'))))
            parts.append(item)
    return parts


def _floor_y(geometry):
    ground = geometry.get('supports', {}).get('ground', [])
    values = [float(x['floor_y_m']) for x in ground if 'floor_y_m' in x]
    if not values:
        feet = [x for x in geometry.get('supports', {}).get('members', [])
                if str(x.get('category', '')).startswith('foot')]
        values = [float(vertices3(x)[:, 1].min()) for x in feet]
    return min(values) if values else None


def _legend_handles():
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    return [Line2D([], [], color=STATION_COLORS[i], lw=1.5,
                   label=f'Station {i}: empty chamber prism') for i in (1, 2, 3)] + [
        Patch(facecolor=WARM_COLOR, edgecolor='#af7835', label='Fixed warm coil union'),
        Patch(facecolor=AL_COLOR, label='Al support stock; hollow cavities empty'),
        Patch(facecolor=SS_COLOR, label='SS foot stock'),
        Line2D([], [], color='#7b647e', ls='-.', label='Pinned solenoid vessel envelope'),
        Line2D([], [], color='#747a80', ls='--', label='Pinned HCAL outer bounds')]


def _context(ax, config, plane, value):
    """Pinned envelope context only; no invented filled absorber or vessel."""
    from matplotlib.patches import Circle, Rectangle
    from tools.toroid_prototype.system import solenoid_parameters
    sol = solenoid_parameters()
    # The source helper returns the pinned legacy parameter names.
    inner = sol.get('vessel_inner_m', sol.get('vessel_inner_radius_m'))
    outer = sol.get('vessel_outer_m', sol.get('vessel_outer_radius_m'))
    length = sol.get('vessel_length_m')
    if inner is None or outer is None or length is None:
        raise ValueError('pinned solenoid vessel parameters unavailable')
    hcal = config.get('hcal', {})
    br = hcal.get('barrel_corner_radius_m', hcal.get('barrel_outer_corner_m'))
    bz = hcal.get('barrel_half_z_m')
    ef = hcal.get('endcap_front_abs_z_m', hcal.get('endcap_front_z_m'))
    eb = hcal.get('endcap_back_abs_z_m', hcal.get('endcap_back_z_m'))
    er = hcal.get('endcap_outer_corner_radius_m', hcal.get('endcap_outer_radius_m'))
    if plane == 'xy':
        if abs(value) <= length/2:
            for r in (inner, outer):
                ax.add_patch(Circle((0, 0), r, fill=False, color='#7b647e', ls='-.', lw=.8))
        if br is not None and bz is not None and abs(value) <= bz:
            ax.add_patch(Circle((0, 0), br, fill=False, color='#747a80', ls='--', lw=.8))
        if None not in (ef, eb, er) and ef <= abs(value) <= eb:
            ax.add_patch(Circle((0, 0), er, fill=False, color='#747a80', ls='--', lw=.8))
    else:
        ax.add_patch(Rectangle((-length/2, inner), length, outer-inner,
                               fill=False, color='#7b647e', ls='-.', lw=.8))
        if br is not None and bz is not None:
            ax.plot([-bz, -bz, bz, bz], [0, br, br, 0], '--', color='#747a80', lw=.8)
        if None not in (ef, eb, er):
            for side in (-1, 1):
                lo, hi = sorted((side*ef, side*eb))
                ax.plot([lo, lo, hi, hi], [0, er, er, 0], '--', color='#747a80', lw=.8)


def _coil_section(ax, config, plane, value, limits, step=.04):
    """Exact warm-sweep membership on a bounded display raster (metres)."""
    from matplotlib.colors import ListedColormap
    xlo, xhi, ylo, yhi = limits
    xe = np.linspace(xlo, xhi, int(np.ceil((xhi-xlo)/step))+1)
    ye = np.linspace(ylo, yhi, int(np.ceil((yhi-ylo)/step))+1)
    xx, yy = np.meshgrid((xe[1:]+xe[:-1])/2, (ye[1:]+ye[:-1])/2)
    if plane == 'xy':
        points = np.column_stack((xx.ravel(), yy.ravel(), np.full(xx.size, value)))
    else:
        angle = np.deg2rad(value)
        points = np.column_stack((yy.ravel()*np.cos(angle), yy.ravel()*np.sin(angle), xx.ravel()))
    hit = coil_mask(points, config, 'warm').reshape(xx.shape)
    mask = np.ma.masked_where(~hit, np.ones(hit.shape))
    ax.pcolormesh(xe, ye, mask, cmap=ListedColormap([WARM_COLOR]),
                  vmin=0, vmax=1, rasterized=True, zorder=1)


def _sections(ax, panels, supports, normal, offset, horizontal, vertical):
    from matplotlib.collections import PolyCollection
    for station in (1, 2, 3):
        polygons = [p for body in panels if int(body['station']) == station
                    if (p := section_polygon(body, normal, offset, horizontal, vertical)) is not None]
        if polygons:
            ax.add_collection(PolyCollection(polygons, facecolors='none',
                edgecolors=STATION_COLORS[station], linewidths=.7, zorder=4))
    for material in ('Al', 'SS'):
        polygons = [p for body in supports
                    if ('SS' if str(body.get('material', '')).startswith('SS') else 'Al') == material
                    if (p := section_polygon(body, normal, offset, horizontal, vertical)) is not None]
        if polygons:
            ax.add_collection(PolyCollection(polygons,
                facecolors=SS_COLOR if material == 'SS' else AL_COLOR,
                edgecolors='#42515d', linewidths=.2, zorder=3))


def _style_section(ax, limits):
    ax.set_xlim(limits[:2]); ax.set_ylim(limits[2:]); ax.set_aspect('equal')
    ax.grid(color='#e0e5e9', lw=.4); ax.set_axisbelow(True)
    ax.tick_params(labelsize=8)


def _xy(geometry, supports, output):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 3, figsize=(15.8, 11.2))
    config = geometry['magnetic_configuration']; panels = geometry['panels']
    limits = (-11.9, 11.9, -11.9, 11.)
    for ax, z in zip(axes.ravel(), (0., .5, 6.3, 8., 9.5, 11.)):
        _coil_section(ax, config, 'xy', z, limits)
        _sections(ax, panels, supports, [0, 0, 1], z, [1, 0, 0], [0, 1, 0])
        _context(ax, config, 'xy', z)
        floor_y = _floor_y(geometry)
        if floor_y is not None:
            ax.axhline(floor_y, color='#3d4144', lw=.8)
        _style_section(ax, limits)
        ax.set_title(f'z = {z:g} m', fontsize=11)
        ax.set_xlabel('x [m]', fontsize=9); ax.set_ylabel('y [m]', fontsize=9)
    fig.suptitle('DES040  |  True XY cuts through finite chambers, coils and frame',
                 fontsize=15, x=.5, y=.986)
    fig.legend(handles=_legend_handles(), loc='lower center', ncol=4, fontsize=8,
               frameon=False, bbox_to_anchor=(.5, .025))
    fig.text(.5, .012, 'PROTOTYPE · chamber outlines only · warm membership raster ≤40 mm; prism cuts exact · floor from generated ground contacts',
             ha='center', fontsize=8, color='#46515b')
    fig.subplots_adjust(left=.05, right=.99, top=.95, bottom=.13, hspace=.22, wspace=.22)
    fig.savefig(output/'xy-sections.png', dpi=170, facecolor='white'); plt.close(fig)


def _rz(geometry, supports, output):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(16, 10.5))
    config = geometry['magnetic_configuration']; panels = geometry['panels']
    limits = (-12.9, 12.9, 0., 11.9)
    for ax, phi in zip(axes.ravel(), (0., 7.5, 15., 270.)):
        ph = np.deg2rad(phi); radial = [np.cos(ph), np.sin(ph), 0]
        normal = [-np.sin(ph), np.cos(ph), 0]
        _coil_section(ax, config, 'rz', phi, limits)
        _sections(ax, panels, supports, normal, 0., [0, 0, 1], radial)
        _context(ax, config, 'rz', phi)
        _style_section(ax, limits)
        label = 'φ = 270° · +R down; foot rows lie off this plane' if phi == 270 else ('φ = 7.5° · aligned facet boundary gap' if phi == 7.5 else f'φ = {phi:g}°')
        ax.set_title(label, fontsize=11)
        ax.set_xlabel('z [m]', fontsize=9); ax.set_ylabel('R along stated φ [m]', fontsize=9)
        if supports and phi in (0., 15.):
            # Contact details use the same actual slice and material-wall parts.
            # Bounds magnify the declared BT/ECT port interfaces, not projections.
            family = 'barrel' if phi == 0 else 'endcap_plus'
            ports = [p for p in geometry['supports'].get('ports', [])
                     if p['group'] == family and p['coil_index'] == 0]
            if not ports:
                continue
            port = min(ports, key=lambda p: abs(p['point_m'][2]))
            x, y, z = port['point_m']; r = np.hypot(x, y)
            zoom = (z-.28, z+.28, r-.20, r+.50) if phi == 0 else (z-.45, z+.30, r-.30, r+.33)
            inset = ax.inset_axes([.035, .58, .25, .36])
            _coil_section(inset, config, 'rz', phi, zoom, step=.006)
            _sections(inset, panels, supports, normal, 0., [0, 0, 1], radial)
            _style_section(inset, zoom)
            inset.tick_params(labelsize=6)
            inset.set_title('BT case → lug → portal' if phi == 0 else
                            'ECT case → lug → spoke', fontsize=7, pad=2)
        if supports and phi == 270.:
            feet = [p for p in supports if str(p.get('component', '')).startswith('foot')]
            if feet:
                foot_x = min(p['origin_m'][0] for p in feet)
                floor = _floor_y(geometry)
                z = min((p['origin_m'][2] for p in feet), key=abs)
                zoom = (z-.70, z+.70, floor-.12, floor+2.45)
                inset = ax.inset_axes([.04, .15, .18, .65])
                _sections(inset, [], supports, [1, 0, 0], foot_x, [0, 0, 1], [0, 1, 0])
                _style_section(inset, zoom)
                inset.axhline(floor, color='#3d4144', lw=.7)
                inset.tick_params(labelsize=6)
                inset.set_title(f'YZ foot cut\nx={foot_x:.3f} m', fontsize=7, pad=2)
                inset.set_xlabel('z [m]', fontsize=6)
                inset.set_ylabel('y [m]', fontsize=6)
    fig.suptitle('DES040  |  True R–Z half-plane cuts at fixed azimuth', fontsize=15, y=.985)
    fig.legend(handles=_legend_handles(), loc='lower center', ncol=4, fontsize=8,
               frameon=False, bbox_to_anchor=(.5, .025))
    fig.text(.5, .012, 'PROTOTYPE · R≥0 in each stated azimuth; both z ends · no projection or rotational replication of feet',
             ha='center', fontsize=8, color='#46515b')
    fig.subplots_adjust(left=.055, right=.99, top=.93, bottom=.14, hspace=.25, wspace=.18)
    fig.savefig(output/'rz-sections.png', dpi=170, facecolor='white'); plt.close(fig)


def _coil_faces(config, cutaway=False, arc_steps=20):
    """Display tessellation of finite rectangular-section rounded sweeps."""
    a = config['warm']['normal_m']/2; b = config['warm']['tangent_m']/2
    faces = []
    for group in config['coil_groups'].values():
        # phi=0 gives the meridional (R,z) centreline, including closing point.
        centerline = loop_polyline(group, 0., arc_steps)[:, [0, 2]]
        half = np.array([group['half_r_m'], group['half_z_m']])
        center = np.array([group['center_r_m'], group['center_z_m']])
        rho = group['corner_radius_m']
        relative = centerline-center
        corner = np.clip(relative, -(half-rho), half-rho)
        normal = (relative-corner)/rho
        for k in range(config['folds']):
            phi = np.deg2rad(group['phi_offset_deg'] + k*360/config['folds'])
            er = np.array([np.cos(phi), np.sin(phi), 0.])
            et = np.array([-np.sin(phi), np.cos(phi), 0.])
            if cutaway and center[0]*er[0] < -1e-9:
                continue
            path = []
            for sn, st in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                rz = centerline+sn*a*normal
                path.append(rz[:, :1]*er + rz[:, 1:]*[0, 0, 1] + st*b*et)
            path = np.asarray(path)
            for j in range(len(centerline)-1):
                if np.linalg.norm(centerline[j+1]-centerline[j]) < 1e-10:
                    continue
                for side in range(4):
                    nxt = (side+1) % 4
                    faces.append(np.array([path[side, j], path[nxt, j],
                                           path[nxt, j+1], path[side, j+1]]))
    return faces


def _plot3d(geometry, supports, output):
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection
    fig = plt.figure(figsize=(17, 9.6))
    for index, cutaway in enumerate((False, True), 1):
        ax = fig.add_subplot(1, 2, index, projection='3d')
        # Display axes (z,x,y) put the beam horizontal and gravity vertical.
        transform = lambda p: np.asarray(p)[..., [2, 0, 1]]
        coil = [transform(p) for p in _coil_faces(geometry['magnetic_configuration'], cutaway)]
        ax.add_collection3d(Poly3DCollection(coil, facecolors=WARM_COLOR,
                                             edgecolors='none', alpha=.22, zsort='average'))
        for material in ('Al', 'SS'):
            faces = []
            for body in supports:
                is_ss = str(body.get('material', '')).startswith('SS')
                if is_ss != (material == 'SS'):
                    continue
                if cutaway and vertices3(body).mean(axis=0)[0] < -1e-9 and 'foot' not in str(body.get('component', '')):
                    continue
                v = vertices3(body)
                faces.extend(transform(v[list(face)]) for face in FACE_INDICES)
            if faces:
                ax.add_collection3d(Poly3DCollection(faces,
                    facecolors=SS_COLOR if material == 'SS' else AL_COLOR,
                    edgecolors='#56616a', linewidths=.12, alpha=.72, zsort='average'))
        for station in (1, 2, 3):
            lines = []
            for body in geometry['panels']:
                if int(body['station']) != station or (cutaway and vertices3(body).mean(axis=0)[0] < -1e-9):
                    continue
                v = vertices3(body)
                lines.extend(transform(v[[a, b]]) for a, b in EDGE_INDICES)
            if lines:
                ax.add_collection3d(Line3DCollection(lines, colors=STATION_COLORS[station],
                                                     linewidths=.27, alpha=.58))
        floor = np.array([[-12.8, -10.2, -11.5], [12.8, -10.2, -11.5],
                          [12.8, 10.2, -11.5], [-12.8, 10.2, -11.5], [-12.8, -10.2, -11.5]])
        # floor already follows the display-axis ordering.
        floor_y = _floor_y(geometry)
        if floor_y is not None:
            floor[:, 2] = floor_y
            ax.plot(*floor.T, color='#657079', lw=.6, alpha=.7)
        ax.set(xlim=(-13, 13), ylim=(-10.8, 10.8), zlim=(-11.7, 10.8))
        ax.set_box_aspect((26, 21.6, 22.5)); ax.view_init(elev=18, azim=-57)
        ax.set_xlabel('z [m]', labelpad=1); ax.set_ylabel('x [m]', labelpad=1); ax.set_zlabel('y [m]', labelpad=1)
        ax.tick_params(labelsize=7, pad=0)
        for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
            axis.pane.set_facecolor((.97, .98, .99, 1))
            axis._axinfo['grid']['color'] = (.83, .86, .89, .45)
        ax.set_title('Complete generated geometry' if not cutaway else
                     'Display cutaway: near half at x<0 omitted; feet retained', fontsize=11, pad=2)
    handles = _legend_handles()[:6]
    handles.append(Line2D([], [], color='#657079', label='Declared floor plane'))
    fig.legend(handles=handles, loc='lower center', ncol=4, fontsize=9,
               frameon=False, bbox_to_anchor=(.5, .055))
    fig.suptitle('DES040  |  Modular rectangular / trapezoidal chamber outlines and connected warm frame',
                 fontsize=15, y=.97)
    fig.text(.5, .035, 'PROTOTYPE · empty chamber prisms; finite support stock and warm coil allocation · cutaway is plotting only',
             ha='center', fontsize=9, color='#46515b')
    fig.subplots_adjust(left=.01, right=.98, bottom=.14, top=.9, wspace=-.02)
    fig.savefig(output/'layout-3d.png', dpi=170, facecolor='white'); plt.close(fig)


def _edges(centers, lower, upper):
    p = np.asarray(centers, float)
    if p.ndim != 1 or len(p) < 2 or not np.all(np.diff(p) > 0):
        raise ValueError('coverage axes must contain ordered unique cell centres')
    edges = np.r_[lower, (p[:-1]+p[1:])/2, upper]
    if not np.all(np.diff(edges) > 0) or not (p[0] > lower and p[-1] < upper):
        raise ValueError('coverage must span full sphere with cell-centred axes')
    return edges


def _coverage_array(coverage, key, shape):
    data = np.asarray(coverage[key])
    if data.shape == shape:
        return data
    if shape[0] != shape[1] and data.shape == shape[::-1]:
        return data.T
    raise ValueError(f'{key} has shape {data.shape}; expected mu,phi={shape}')


def _coverage(coverage, output):
    import matplotlib.pyplot as plt
    from matplotlib.colors import BoundaryNorm, ListedColormap
    mu = np.asarray(coverage['mu']); phi = np.asarray(coverage['phi_deg'])
    me, pe = _edges(mu, -1., 1.), _edges(phi, 0., 360.)
    shape = (len(mu), len(phi))
    fig, axes = plt.subplots(3, 3, figsize=(17, 11.6), sharex=True, sharey=True)
    countmap = ListedColormap(['#eef0f2', '#eacb8f', '#80b8cd', '#176d76'])
    norm = BoundaryNorm([-.5, .5, 1.5, 2.5, 3.5], countmap.N)
    boolmap = ListedColormap(['#f0f2f4', '#ad5f49'])
    titles = [('outer_count', 'Outer-envelope measurement-plane stations'),
              ('active_count', 'Border-inset measurement-plane stations'),
              ('depth_count', 'Border-inset complete-depth station traversals'),
              ('support_upstream', 'Support stock: IP → first retained plane'),
              ('support_between', 'Support stock: first → last retained plane'),
              ('support_any', 'Support stock: full outward ray'),
              ('coil_upstream', 'Warm coil: IP → first retained plane'),
              ('coil_between', 'Warm coil: first → last retained plane'),
              ('coil_any', 'Warm coil: full outward ray')]
    weights = np.diff(me)[:, None]*np.diff(pe)[None, :]/720
    count_artist = bool_artist = None
    for i, (ax, (key, title)) in enumerate(zip(axes.ravel(), titles)):
        values = _coverage_array(coverage, key, shape)
        if i < 3:
            if np.any(~np.isfinite(values)) or np.any((values < 0) | (values > 3)):
                raise ValueError('station counts must be finite in 0..3')
            count_artist = ax.pcolormesh(pe, me, values, cmap=countmap, norm=norm, rasterized=True)
            frac = float(np.sum(weights*(values == 3)))
            note = f'grid estimate, 3 stations: {100*frac:.2f}% of 4π'
        else:
            bool_artist = ax.pcolormesh(pe, me, values.astype(bool), cmap=boolmap,
                                        vmin=0, vmax=1, rasterized=True)
            frac = float(np.sum(weights*values.astype(bool)))
            note = f'grid estimate, tagged: {100*frac:.2f}% of 4π'
        ax.set_title(title, fontsize=10, pad=7)
        ax.text(.02, .035, note, transform=ax.transAxes, fontsize=8,
                bbox=dict(facecolor='white', alpha=.9, edgecolor='none', pad=2))
        ax.set_xlim(0, 360); ax.set_ylim(-1, 1)
        ax.set_xticks([0, 90, 180, 270, 360]); ax.set_yticks([-1, -.5, 0, .5, 1])
        ax.tick_params(labelsize=8)
        if i >= 6:
            ax.set_xlabel('φ [degrees]', fontsize=9)
        if i % 3 == 0:
            ax.set_ylabel('μ = cos θ', fontsize=9)
    cbax = fig.add_axes([.925, .68, .012, .19])
    fig.colorbar(count_artist, cax=cbax, ticks=[0, 1, 2, 3]).set_label('Distinct stations', fontsize=9)
    cbax = fig.add_axes([.925, .21, .012, .31])
    fig.colorbar(bool_artist, cax=cbax, ticks=[0, 1]).ax.set_yticklabels(['clear', 'tagged'])
    fig.suptitle('DES040  |  Full-sphere straight-ray geometry: panel availability and material tags',
                 fontsize=15, y=.975)
    fig.text(.5, .055, 'Display grid estimates; uniform μ and full φ, both ends. Use the independent random-ray estimator in results.json for headline fractions.',
             ha='center', fontsize=9, color='#46515b')
    fig.text(.5, .032, 'Material tags do not veto station counts and do not predict detector or reconstruction efficiency. “Any” includes material beyond the last station.',
             ha='center', fontsize=9, color='#46515b')
    fig.subplots_adjust(left=.055, right=.90, bottom=.12, top=.91, hspace=.29, wspace=.15)
    fig.savefig(output/'coverage.png', dpi=170, facecolor='white'); plt.close(fig)


def draw(geometry, coverage, output):
    """Write four parameterized PROTOTYPE figures; return output metadata.

    geometry keys: configuration, magnetic_configuration, panels, supports.
    coverage keys: mu, phi_deg, outer_count/active_count/depth_count, and six
    support_/coil_ upstream/between/any boolean arrays with shape (mu,phi).
    No numerical map or physical geometry input is modified or regenerated.
    """
    import matplotlib
    matplotlib.use('Agg')
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    if not geometry.get('magnetic_configuration'):
        raise ValueError('normalized fixed magnetic_configuration required')
    supports = _support_parts(geometry)
    with matplotlib.rc_context({'font.family': 'DejaVu Sans', 'font.size': 9,
                                 'savefig.facecolor': 'white'}):
        _plot3d(geometry, supports, output)
        _xy(geometry, supports, output)
        _rz(geometry, supports, output)
        _coverage(coverage, output)
    names = ('layout-3d.png', 'xy-sections.png', 'rz-sections.png', 'coverage.png')
    return {'status': 'PROTOTYPE review render; no engineering acceptance',
            'outputs': [str(output/name) for name in names],
            'coil_slice_display_max_step_m': .04,
            'chamber_sections': 'exact convex-prism/plane intersections',
            'support_sections': 'material stock parts only; cavities empty',
            'coverage_domain': 'full sphere, cell-centred mu and phi'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry', type=Path, required=True)
    parser.add_argument('--coverage', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    geometry = json.loads(args.geometry.read_text())
    if args.coverage.suffix == '.npz':
        with np.load(args.coverage, allow_pickle=False) as data:
            coverage = dict(data)
    else:
        coverage = json.loads(args.coverage.read_text())
    print(json.dumps(draw(geometry, coverage, args.output), indent=2))


if __name__ == '__main__':
    main()
