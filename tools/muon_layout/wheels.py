"""Selected DES040 whole-wheel outline PROTOTYPE; no chamber internals.

Run from the repository root with ``python -m tools.muon_layout.wheels``.
Historical inputs are read and fingerprinted, never rewritten. Magnetic source
and cold sizing are supplied by the separate DES039 calculation. This module
constructs finite chamber/support prisms and proves their geometric interfaces;
it does not qualify MDT manufacturing, forces, vessels or detector response.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import platform
import time
import numpy as np
from . import geometry as g
from . import layout
from . import support

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / 'tools/muon_layout/wheels-config.json'
DEFAULT_MAGNETIC = ROOT / 'docs/validation/DES-040/wheels-2026-10-20/magnetic/configuration.json'
DEFAULT_OUTPUT = ROOT / 'docs/validation/DES-040/wheels-2026-10-20/candidate'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def relative(path):
    path = Path(path).resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def checked_input(config, key):
    path = ROOT / config[key]
    if digest(path) != config[key + '_sha256']:
        raise ValueError('historical input changed: ' + config[key])
    return json.loads(path.read_text())


def wheel_dimensions(spec, magnetic, clearance):
    """Derive whole trapezoids, with exact outer-corner radius and bore base.

    u is along the sector centre. x/y are along/across the lower sector seam.
    Both affine sides are straight; no Boolean cutting or radial tiling occurs.
    """
    alpha = math.pi / spec['sectors']
    u0 = spec['inner_radius_m']
    if 'extra_BT_box_margin_m' in spec:
        bt = magnetic['coil_groups']['barrel']
        delta = spec['seam_half_width_at_bore_m']
        x0 = u0 / math.cos(alpha) - delta * math.tan(alpha)
        xguard = bt['center_r_m'] - bt['half_r_m'] - magnetic['warm']['normal_m']/2 - clearance
        yguard = magnetic['warm']['tangent_m']/2 + clearance + spec['extra_BT_box_margin_m']
        slope = (yguard - delta) / (xguard - x0)
        intercept = delta - slope*x0
        rule = dict(seam_slope=slope, seam_intercept_m=intercept,
                    inner_vertex_seam_xy_m=[x0, delta],
                    inflated_BT_box_start_x_m=xguard,
                    side_at_box_start_y_m=yguard,
                    extra_margin_m=spec['extra_BT_box_margin_m'])
    else:
        delta = spec['seam_normal_width_m']/2
        slope, intercept = 0., delta
        rule = dict(seam_slope=0., seam_intercept_m=delta,
                    normal_seam_width_m=2*delta)
    A = (math.sin(alpha)-slope*math.cos(alpha))/(math.cos(alpha)+slope*math.sin(alpha))
    B = -intercept/(math.cos(alpha)+slope*math.sin(alpha))
    R = spec['outer_radius_m']
    u1 = (-A*B + math.sqrt((A*B)**2-(1+A*A)*(B*B-R*R)))/(1+A*A)
    w0, w1 = A*u0+B, A*u1+B
    if not (0 < w0 < w1 and u1 > u0):
        raise ValueError('selected corridor has no whole positive-bore trapezoid')
    return dict(u0_m=u0, u1_m=u1, inner_base_m=2*w0, outer_base_m=2*w1,
                radial_base_distance_m=u1-u0, outer_corner_radius_m=math.hypot(u1,w1),
                half_width_slope=A, half_width_intercept_m=B,
                area_m2=(u1-u0)*(w0+w1), **rule)


def whole_wheels(config, magnetic):
    bodies = []
    dimensions = {}
    for name in ['inner_wheel', 'outer_wheel']:
        spec = config[name]
        d = wheel_dimensions(spec, magnetic, config['coil_clearance_m'])
        dimensions[name] = d
        u0,u1,w0,w1 = d['u0_m'],d['u1_m'],d['inner_base_m']/2,d['outer_base_m']/2
        for side, label in [(-1,'M'),(1,'P')]:
            for k in range(spec['sectors']):
                angle = spec['phase_deg'] + k*360/spec['sectors']
                a = math.radians(angle)
                er,ep = [math.cos(a),math.sin(a),0.],[-math.sin(a),math.cos(a),0.]
                bodies.append(g.prism(f'E{label}{spec["station"]}/WHEEL/S{k:02d}', 'endcap',
                    [0,0,side*spec['abs_z_m']], np.column_stack((er,ep,[0,0,1])),
                    [[u0,-w0],[u1,-w1],[u1,w1],[u0,w0]], config['depth_m'],
                    station=spec['station'], side=side, face='trapezoid', wheel=name,
                    whole_sector=True, ordinary_radial_module_cap_exempt=True,
                    compartment=dict(phi_deg=[angle-180/spec['sectors'],angle+180/spec['sectors']],
                                     radial_m=[spec['inner_radius_m'],spec['outer_radius_m']]),
                    dimensions=d))
    return bodies, dimensions


def wheel_certificate(body, config, magnetic):
    """Analytic whole-volume proof for the two longitudinally exterior wheels.

    Endcap groups are separated by supporting z planes. At the inner wheel the
    entire BT loop is enclosed by its straight-leg boxes plus return regions
    beyond |z|=half_z-corner. The wheel lies before those regions. Each box is
    enlarged in both r and tangent by the requested clearance; SAT against that
    box is conservative for the Euclidean clearance. This is a volume proof,
    independent of corner/centre sampling and of adaptive-cell convergence.
    """
    vv = g.vertices3(body)
    zlo,zhi = np.min(abs(vv[:,2])),np.max(abs(vv[:,2]))
    c = config['coil_clearance_m']
    half = magnetic['warm']['normal_m']/2
    ect_front = min(abs(x['center_z_m'])-x['half_z_m']-half
                    for n,x in magnetic['coil_groups'].items() if n.startswith('endcap'))
    ect_back = max(abs(x['center_z_m'])+x['half_z_m']+half
                   for n,x in magnetic['coil_groups'].items() if n.startswith('endcap'))
    bt = magnetic['coil_groups']['barrel']
    if body['station'] == 3:
        back = max(ect_back, abs(bt['center_z_m'])+bt['half_z_m']+half)
        clear = zlo > back+c
        return dict(clear=bool(clear), reason='whole-volume axial supporting-plane separation',
                    minimum_axial_separation_m=float(zlo-back), required_clearance_m=c,
                    cells=0, boundary=back)
    radial_max = float(np.linalg.norm(vv[:,:2],axis=1).max())
    return_start = bt['half_z_m']-bt['corner_radius_m']-half
    outer_leg_start = bt['center_r_m']+bt['half_r_m']-half
    bounds_ok = (zhi+c < ect_front and zhi+c < return_start and radial_max+c < outer_leg_start)
    clashes = []
    btboxes = []
    for k in range(magnetic['folds']):
        angle = math.radians(bt['phi_offset_deg']+k*360/magnetic['folds'])
        er,ep = np.array([math.cos(angle),math.sin(angle),0.]),np.array([-math.sin(angle),math.cos(angle),0.])
        radius = bt['center_r_m']-bt['half_r_m']
        aa,bb = half+c,magnetic['warm']['tangent_m']/2+c
        box = g.prism(f'BT-INFLATED/{k}', 'proof', radius*er,
            np.column_stack((er,ep,[0,0,1])), [[-aa,-bb],[aa,-bb],[aa,bb],[-aa,bb]],
            2*(bt['half_z_m']+half+c))
        btboxes.append(box)
        if g.intersects(body,box): clashes.append(k)
    return dict(clear=bool(bounds_ok and not clashes),
        reason='axial endcap/return planes, outer-leg radius and exact SAT against all inflated BT inner-leg boxes',
        cells=0, required_clearance_m=c, inflated_BT_box_conflicts=clashes,
        ect_axial_separation_m=float(ect_front-zhi),
        BT_return_axial_bound_separation_m=float(return_start-zhi),
        BT_outer_leg_radial_bound_separation_m=float(outer_leg_start-radial_max),
        supporting_plane_checks=bool(bounds_ok), boxes_checked=len(btboxes))


def independent_wheel_controls(wheels,config,magnetic):
    """Cross-check the analytic proofs with the independent adaptive kernel.

    For the closely spaced inner wheel, the exact ECT supporting-plane proof
    remains primary; the adaptive cross-check independently audits every BT
    exclusion. Rear-wheel adaptive checks include all assemblies. Occupied
    negative fixtures must be rejected, rather than merely proving empty space.
    """
    probes=[]
    only_bt=copy.deepcopy(magnetic)
    only_bt['coil_groups']={'barrel':magnetic['coil_groups']['barrel']}
    for body in wheels:
        source=only_bt if body['station']==1 else magnetic
        proof=g.certify_coil_clear(body,source,config['coil_clearance_m'],
            config['numerics']['independent_wheel_probe_resolution_m'],
            max_cells=config['numerics']['max_certificate_cells'])
        probes.append(dict(id=body['id'],groups=list(source['coil_groups']),**proof))
    a=magnetic['coil_groups']['barrel']
    occupied=g.prism('negative/BT-leg','test',[a['center_r_m']-a['half_r_m'],0,6.7456],
                     np.eye(3),[[-.01,-.01],[.01,-.01],[.01,.01],[-.01,.01]],.02)
    negative=g.certify_coil_clear(occupied,magnetic,config['coil_clearance_m'],.005)
    near_seam=g.prism('negative/overlapping-panel','test',[4.6,0,6.7456],np.eye(3),
                     [[-.2,-.2],[.2,-.2],[.2,.2],[-.2,.2]],.5)
    overlap_detection=g.intersects(near_seam,occupied)
    passed=all(p['clear'] for p in probes) and not negative['clear'] and overlap_detection
    if not passed:raise ValueError('independent wheel controls failed')
    return dict(passed=passed,adaptive_probes=probes,negative_occupied_fixture=negative,
                overlapping_prism_fixture_detected=bool(overlap_detection),
                scope='analytic supporting planes remain the full ECT proof for the inner wheel; adaptive BT/full-source probes are independent cross-checks')


def support_certificate(body, members, bounds, clearance):
    lo,hi = g.aabb(body)
    # Rotated face-offset expansion is enclosed by this conservative AABB pad.
    pad = 2*clearance
    near = np.flatnonzero(((bounds[:,1]+pad>=lo)&(bounds[:,0]-pad<=hi)).all(axis=1))
    clashes=[members[i]['id'] for i in near if g.intersects(body,members[i],clearance)]
    return dict(clear=not clashes,required_clearance_m=clearance,
                method='all support outer envelopes; conservative AABB broad phase then exact convex-prism SAT with face-offset member expansion',
                total_members=len(members),broad_phase_pad_m=pad,
                exact_tested_member_ids=[members[i]['id'] for i in near],conflicts=clashes)


def support_clashes(body, members, bounds, clearance):
    return support_certificate(body,members,bounds,clearance)['conflicts']


def pack_barrels(chamber_config, magnetic, supports):
    """Fresh old whole-module packing, against the changed magnets and lugs."""
    c = chamber_config['chambers']
    members = supports['members']
    bounds = np.asarray([g.aabb(x) for x in members])
    cache = {}
    cells = 0
    def check(body):
        nonlocal cells
        # Source geometry has exact C12 symmetry; local vertices remain exact.
        # Additional0.1um in the first certificate bounds rotation roundoff.
        key = (body['station'], round(body['compartment']['phi_deg'] % 30,9),
               tuple(np.asarray(body['vertices_m']).ravel()),body['depth_m'])
        if key not in cache:
            proof = g.certify_coil_clear(body, magnetic, c['coil_clearance_m']+1e-7,
                                         c['coil_certificate_resolution_m'])
            cells += proof['cells']
            cache[key] = (body['id'], proof)
        ident, proof = cache[key]
        return dict(proof, symmetry_source_id=ident, symmetry='C12 exact source;0.1um rotation-roundoff guard')
    initial = [p for p in layout.candidates(chamber_config) if p['kind']=='barrel']
    def pack(with_support):
        accepted,rejected,splits = [],[],0
        def visit(body, depth):
            nonlocal splits
            proof = check(body)
            sproof = support_certificate(body,members,bounds,c['support_clearance_m']) if proof['clear'] and with_support else None
            clashes = sproof['conflicts'] if sproof else []
            if proof['clear'] and not clashes:
                record=dict(body,coil_certificate=proof)
                if sproof:record['support_certificate']=sproof
                accepted.append(record);return
            children = layout._children(body,c,depth) if depth<c['max_subdivision_depth'] else []
            if children:
                splits += 1
                for child in children: visit(child,depth+1)
            else:
                rejected.append(dict(id=body['id'],reason=proof['reason'] if not proof['clear'] else 'support clearance',
                                     coil_certificate=proof,support_ids=clashes))
        for body in initial:visit(body,0)
        return accepted,dict(initial_compartments=len(initial),subdivisions=splits,
                             accepted=len(accepted),rejected_leaves=rejected)
    reference,refstats = pack(False)
    accepted,stats = pack(True)
    return accepted,reference,stats,refstats,cells


def all_panel_conflicts(panels):
    bounds = np.asarray([g.aabb(x) for x in panels])
    conflicts = []
    for i,body in enumerate(panels):
        near = np.flatnonzero(((bounds[i,1]>=bounds[i+1:,0])&(bounds[i,0]<=bounds[i+1:,1])).all(axis=1))+i+1
        for j in near:
            if g.intersects(body,panels[j]):conflicts.append([body['id'],panels[j]['id']])
    return conflicts


def shape_mapping(before, after):
    old,new = {p['id']:p for p in before},{p['id']:p for p in after}
    records = []
    for ident in sorted(set(old)|set(new)):
        if ident not in new:change='removed'
        elif ident not in old:change='new'
        else:
            a,b=old[ident],new[ident]
            same=all(np.array_equal(np.asarray(a[k]),np.asarray(b[k])) for k in ['origin_m','basis','vertices_m','depth_m'])
            change='retained-exact' if same else 'changed-placement-or-shape'
        records.append(dict(id=ident,change=change))
    return dict(scope='semantic ID mapping; native numeric IDs may change when geometry order changes',
                counts={key:sum(r['change']==key for r in records) for key in
                        ['removed','new','retained-exact','changed-placement-or-shape']},records=records,
                replacements=[dict(old_station=1,side='both',old_kind='radially packed endcap modules',new_kind='12 whole-sector trapezoids per side'),
                              dict(old_station=3,side='both',old_kind='radially packed endcap modules',new_kind='24 whole-sector trapezoids per side')])


def wheel_gap_diagnostic(geometry,config):
    """Isolated whole-depth wheels vs ideal annuli, on straight IP rays.

    The primary result is analytic solid angle, avoiding aliasing of20mm seams
    on an angular grid. For every footprint face n.t<=b and depth face zf,
    slopes t=(x/z,y/z) obey n.t<=min(b/(z-h),b/(z+h)). The resulting convex
    quadrilateral's solid angle is the sum of its two exact triangle angles.
    The midpoint grid remains an explicitly labelled sampling cross-check.
    """
    from .coverage import sphere_grid
    def omega(body,border=0):
        n,b=g.polygon_planes(body['vertices_m']);b=b-border
        z=abs(body['origin_m'][2]);h=body['depth_m']/2
        bb=np.minimum(b/(z-h),b/(z+h))
        p=np.array([np.linalg.solve(np.stack((n[i-1],n[i])),[bb[i-1],bb[i]]) for i in range(4)])
        v=np.column_stack((p,np.ones(4)));answer=0.
        for ids in [[0,1,2],[0,2,3]]:
            a,b,c=v[ids];la,lb,lc=np.linalg.norm(v[ids],axis=1)
            denominator=la*lb*lc+(a@b)*lc+(a@c)*lb+(b@c)*la
            answer+=2*math.atan2(abs(float(np.linalg.det(np.stack((a,b,c))))),float(denominator))
        return answer
    mu,phi,d = sphere_grid(config['numerics']['diagnostic_mu_bins'],config['numerics']['diagnostic_phi_bins'])
    result = {}
    for name in ['inner_wheel','outer_wheel']:
        s = config[name];z=s['abs_z_m'];half=config['depth_m']/2
        mid = z/np.maximum(abs(d[:,2]),1e-30)
        radial = np.linalg.norm(d[:,:2],axis=1)
        ideal = ((mid*(1-half/z)*radial>=s['inner_radius_m']) &
                 (mid*(1+half/z)*radial<=s['outer_radius_m']))
        hit=np.zeros(len(d),bool)
        active=np.zeros(len(d),bool)
        for body in geometry['panels']:
            if body.get('wheel')!=name:continue
            positive=d[:,2]*body['side']>0
            ix=np.flatnonzero(ideal&positive)
            hit[ix]|=np.isfinite(g.midplane_hits(body,d[ix],0,True))
            active[ix]|=np.isfinite(g.midplane_hits(body,d[ix],geometry['configuration']['chambers']['active_border_m'],True))
        theta_inner=math.atan(s['inner_radius_m']/(z-half));theta_outer=math.atan(s['outer_radius_m']/(z+half))
        ideal_omega=4*math.pi*(math.cos(theta_inner)-math.cos(theta_outer))
        selected=[p for p in geometry['panels'] if p.get('wheel')==name]
        outline_omega=sum(omega(p) for p in selected)
        border_omega=sum(omega(p,geometry['configuration']['chambers']['active_border_m']) for p in selected)
        exact_loss=1-outline_omega/ideal_omega
        grid_loss=float(np.mean(~hit[ideal]))
        result[name]=dict(method='analytic whole-depth slope-halfspaces and exact spherical-triangle solid angles',
             envelope_gap_fraction_within_ideal_annulus=exact_loss,
             border_inset_loss_fraction_within_ideal_annulus=1-border_omega/ideal_omega,
             ideal_annulus_fraction_4pi=ideal_omega/(4*math.pi),
             solid_angle_sr=dict(ideal_annulus_both_ends=ideal_omega,whole_envelopes_both_ends=outline_omega,border_inset_both_ends=border_omega),
             midpoint_grid_cross_check=dict(ideal_annulus_rays=int(ideal.sum()),whole_envelope_rays=int((ideal&hit).sum()),
                  border_inset_rays=int((ideal&active).sum()),envelope_gap_fraction=grid_loss,
                  grid_minus_analytic_loss=grid_loss-exact_loss,
                  scope='sampling check only; thin seams can alias the finite phi grid'),
             scope='both ends, straight IP rays; full0.5m depth; includes affine/normal seam and outer/inner polygon boundary losses; no coils, supports or field transport veto')
    return dict(grid=[len(mu),len(phi)],sampling='analytic primary; equal-solid-angle midpoint grid cross-check; geometric diagnostic only',wheels=result)


def draw_views(geometry,path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon
    fig,ax=plt.subplots(1,3,figsize=(16,6))
    for j,name in enumerate(['inner_wheel','outer_wheel']):
        panels=[p for p in geometry['panels'] if p.get('wheel')==name and p['side']==1]
        for p in panels:ax[j].add_patch(Polygon(g.vertices3(p)[:4,:2],facecolor='#2684ce',edgecolor='#13476c',lw=.6))
        spec=geometry['wheel_revision'][name]
        ax[j].add_patch(plt.Circle((0,0),spec['inner_radius_m'],fill=False,color='#555555',ls='--'))
        ax[j].set_title(f'{len(panels)} whole trapezoids, +z={spec["abs_z_m"]:g}m')
        ax[j].set_aspect('equal');ax[j].set_xlim(-9,9);ax[j].set_ylim(-9,9)
        ax[j].set_xlabel('x [m]');ax[j].set_ylabel('y [m]');ax[j].grid(alpha=.2)
    # Actual BT warm boxes in the inner-wheel XY plane. ECT and front frame
    # lie outside this axial plane; a filled annular cryostat is not invented.
    bt=geometry['magnetic_configuration']['coil_groups']['barrel']
    for k in range(12):
        a=math.radians(bt['phi_offset_deg']+30*k);er=np.array([math.cos(a),math.sin(a)]);ep=np.array([-math.sin(a),math.cos(a)])
        r=bt['center_r_m']-bt['half_r_m'];aa=.25;bb=.30
        v=np.array([r*er+x*aa*er+y*bb*ep for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]])
        ax[0].add_patch(Polygon(v,facecolor='#777777',edgecolor='#333333',lw=.5))
    for p in geometry['panels']:
        if p['kind']=='barrel' and abs(p['compartment']['phi_deg'])<1e-8:
            v=g.vertices3(p);ax[2].add_patch(Polygon([[v[:,2].min(),v[:,0].min()],[v[:,2].max(),v[:,0].min()],
                [v[:,2].max(),v[:,0].max()],[v[:,2].min(),v[:,0].max()]],facecolor='#2684ce',edgecolor='#13476c',lw=.4))
    for name in ['inner_wheel','outer_wheel']:
        s=geometry['wheel_revision'][name]
        for sign in [-1,1]:
            x=sign*s['abs_z_m'];h=geometry['wheel_revision']['depth_m']/2
            ax[2].add_patch(Polygon([[x-h,s['inner_radius_m']],[x+h,s['inner_radius_m']],
                [x+h,s['outer_radius_m']],[x-h,s['outer_radius_m']]],facecolor='#2684ce',alpha=.6))
    ax[2].set_xlim(-13.5,13.5);ax[2].set_ylim(0,9.5);ax[2].set_xlabel('z [m]');ax[2].set_ylabel('R [m]')
    ax[2].set_title('Chamber R–Z projection; barrel facet at phi=0°');ax[2].grid(alpha=.2)
    fig.suptitle('DES040 selected whole-wheel PROTOTYPE; no chamber internals / engineering acceptance')
    fig.tight_layout();fig.savefig(path,dpi=170);plt.close(fig)


def build(config,magnetic,baseline):
    warm=magnetic['warm']
    if magnetic['folds']!=12 or warm!={'normal_m':.5,'tangent_m':.6}:
        raise ValueError('selected contract requires C12 and unchanged0.50x0.60m warm reservation')
    for name in ['endcap_plus','endcap_minus']:
        s=magnetic['coil_groups'][name]
        if abs(abs(s['center_z_m'])-9.5)>1e-12 or abs(s['half_z_m']-2.2)>1e-12:
            raise ValueError('selected ECT shortening not supplied')
    if any(magnetic[w][k]>warm[k] for w in ['pack','cold'] for k in warm):
        raise ValueError('pack/cold allocation does not fit retained warm reservation')
    original=checked_input(config,'base_configuration')
    chamber_config=copy.deepcopy(original)
    ch=chamber_config['chambers']
    ch['barrel_half_z_m']=config['barrel_half_z_m']
    ch['disk_abs_z_m']=[config['inner_wheel']['abs_z_m'],9.5,config['outer_wheel']['abs_z_m']]
    chamber_config['status']=config['status']
    chamber_config['whole_wheel_configuration']='tools/muon_layout/wheels-config.json'
    chamber_config['ordinary_endcap_segmentation_scope']='station2 only; new station1/3 whole-wheel outlines use wheel_revision'
    chamber_config['support_revision']='same support input with front attachments amended by wheel_revision.front_attachment'
    # The magnetic map belongs to W-F1/root and is deliberately not guessed here.
    chamber_config['magnetic_results']='separate shortened-ECT magnetic configuration; see geometry-controls.json'
    chamber_config.pop('magnetic_results_sha256',None)
    chamber_config.pop('magnetic_map',None);chamber_config.pop('magnetic_map_sha256',None)
    proposal=checked_input(config,'support_input')
    proposal['endcap_interfaces']['front'].update(
        abs_case_skin_z_m=config['front_attachment']['abs_skin_z_m'],
        abs_lug_extent_z_m=config['front_attachment']['abs_lug_extent_z_m'],
        lug_axial_length_m=config['front_attachment']['lug_axial_length_m'])
    proposal['endcap_interfaces']['unavoidable_chamber_interface']=(
        'Retained front spokes at|z|6.30 and extended front lugs6.45-7.05m cross B2/B3 in localized phi corridors; '
        'all barrels freshly repacked. Rear carrier bound12.45m precedes outer-wheel front12.55m. '
        'Carrier ring lies radially beyond inner-wheel bound5.45m; individual prism checks enforce clearance.')
    supports=support.build_supports(proposal)
    # Preserve unchanged finite stock and ports bit-for-bit, rather than
    # reconstructing them with a potentially different NumPy trig/normalizer.
    old_members={p['id']:p for p in baseline['supports']['members']}
    old_ports={p['id']:p for p in baseline['supports']['ports']}
    supports['members']=[m if '-front/LUG' in m['id'] else copy.deepcopy(old_members[m['id']])
                         for m in supports['members']]
    supports['ports']=[p if '-front/LUG' in p['id'] else copy.deepcopy(old_ports[p['id']])
                       for p in supports['ports']]
    supports['ground']=copy.deepcopy(baseline['supports']['ground'])
    sv=support.validate_supports(supports,magnetic)
    if not sv['valid']:raise ValueError('new frame contact/material/coil validation failed: '+str(sv['failed_coil_checks']))
    supports['status']='PROTOTYPE: material-contact graph and geometric interfaces validated; no structural qualification'
    # Verify the broad phase encloses every actual face-offset expansion.
    pad=2*config['support_clearance_m']
    for m in supports['members']:
        lo,hi=g.aabb(m);elo,ehi=g.aabb(g.expanded(m,config['support_clearance_m']))
        if np.any(elo<lo-pad-1e-12) or np.any(ehi>hi+pad+1e-12):
            raise ValueError('support broad-phase pad does not enclose actual expansion: '+m['id'])
    print('Frame: all36case contact paths grounded; pack/cold/warm volume checks passed',flush=True)
    barrels,refbarrels,stats,refstats,cells=pack_barrels(chamber_config,magnetic,supports)
    print(f'Fresh barrel packing: {len(barrels)}accepted, {len(stats["rejected_leaves"])}rejected leaves',flush=True)
    wheels,dimensions=whole_wheels(config,magnetic)
    independent_controls=independent_wheel_controls(wheels,config,magnetic)
    bounds=np.asarray([g.aabb(x) for x in supports['members']])
    for body in wheels:
        proof=wheel_certificate(body,config,magnetic)
        sproof=support_certificate(body,supports['members'],bounds,config['support_clearance_m'])
        clashes=sproof['conflicts']
        if not proof['clear'] or clashes:raise ValueError(f'whole wheel cannot be clipped/rejected: {body["id"]}, {proof}, {clashes}')
        body['coil_certificate']=proof
        body['support_certificate']=sproof
    middle=[]
    for old in baseline['panels']:
        if old['kind']!='endcap' or old['station']!=2:continue
        body={k:copy.deepcopy(v) for k,v in old.items() if k!='coil_certificate'}
        proof=g.certify_coil_clear(body,magnetic,config['coil_clearance_m'],config['numerics']['middle_certificate_resolution_m'])
        sproof=support_certificate(body,supports['members'],bounds,config['support_clearance_m'])
        clashes=sproof['conflicts']
        if not proof['clear'] or clashes:raise ValueError(f'middle panel no longer clear: {body["id"]}, {proof}, {clashes}')
        body['coil_certificate']=proof;body['support_certificate']=sproof;middle.append(body)
    if len(middle)!=config['middle_wheel']['expected_count_both_sides']:raise ValueError('middle wheel count changed')
    panels=barrels+middle+wheels
    conflicts=all_panel_conflicts(panels)
    if conflicts:raise ValueError('panel volume conflict: '+str(conflicts[:10]))
    unchanged=[];changed=[]
    for m in supports['members']:
        (unchanged if m==old_members[m['id']] else changed).append(m['id'])
    expected_changed=[m['id'] for m in supports['members'] if '-front/LUG' in m['id']]
    if sorted(changed)!=sorted(expected_changed):raise ValueError('unexpected frame change')
    hcal=[]
    for body in panels:
        if body['kind']=='endcap':
            separation=abs(body['origin_m'][2])-body['depth_m']/2-config['hcal_endcap_back_abs_z_m']
        else:
            # Tangential extrusion cannot reduce radius below the face apothem.
            separation=float(np.linalg.norm(np.asarray(body['origin_m'])[:2])-body['depth_m']/2-config['hcal_barrel_corner_radius_m'])
        if separation<config['hcal_clearance_m']-1e-10:hcal.append(body['id'])
    if hcal:raise ValueError('HCAL-bound clearance failed: '+str(hcal[:10]))
    geometry=dict(configuration=chamber_config,magnetic_configuration=magnetic,supports=supports,
        panels=panels,without_support_panels=refbarrels+middle+wheels,
        packing=stats,without_support_packing=refstats,
        validation=dict(panel_panel_conflicts=conflicts,accepted_coil_certificates=len(panels),
            accepted_support_certificates=sum(bool(p.get('support_certificate',{}).get('clear')) for p in panels),
            coil_certificate_cells=cells+sum(p['coil_certificate']['cells'] for p in middle),
            panel_support_clearance_m=config['support_clearance_m'],coil_clearance_m=config['coil_clearance_m'],
            unresolved_cells_accepted=0,hcal_bound_conflicts=hcal),
        wheel_revision=config,wheel_dimensions=dimensions)
    tests=dict(passed=True,support_validation=sv,
        independent_wheel_controls=independent_controls,
        counts={kind:{str(j):sum(p['kind']==kind and p['station']==j for p in panels) for j in [1,2,3]} for kind in ['barrel','endcap']},
        full_wheel_checks=dict(inner_count_both_sides=sum(p.get('wheel')=='inner_wheel' for p in panels),
            outer_count_both_sides=sum(p.get('wheel')=='outer_wheel' for p in panels),
            all_unclipped_whole_sector=all(p['whole_sector'] for p in wheels),
            dimensions=dimensions,coil_certificates={p['id']:p['coil_certificate'] for p in wheels}),
        panel_validation=geometry['validation'],
        frame_changes=dict(changed_members=changed,unchanged_members=unchanged,
            extra_front_lug_stock_volume_m3=sum(g.volume(m)-g.volume(old_members[m['id']]) for m in supports['members'] if m['id'] in changed),
            scope='frame stock only; unique-union mass and structural qualification remain separate'),
        axial_interfaces=dict(inner_wheel_near_abs_z_m=config['inner_wheel']['abs_z_m']-config['depth_m']/2,
            inner_wheel_far_abs_z_m=config['inner_wheel']['abs_z_m']+config['depth_m']/2,
            HCAL_to_inner_wheel_m=config['inner_wheel']['abs_z_m']-config['depth_m']/2-config['hcal_endcap_back_abs_z_m'],
            B1_to_inner_wheel_m=config['inner_wheel']['abs_z_m']-config['depth_m']/2-config['barrel_half_z_m'][0],
            inner_wheel_to_ECT_warm_m=7.05-config['inner_wheel']['abs_z_m']-config['depth_m']/2,
            outer_wheel_near_abs_z_m=config['outer_wheel']['abs_z_m']-config['depth_m']/2,
            rear_carrier_to_outer_wheel_m=config['outer_wheel']['abs_z_m']-config['depth_m']/2-12.45),
        chamber_bounds=dict(maximum_corner_radius_m=max(float(np.linalg.norm(g.vertices3(p)[:,:2],axis=1).max()) for p in panels),
                            maximum_abs_z_m=max(float(abs(g.vertices3(p)[:,2]).max()) for p in panels)),
        limits=config['limits'])
    return geometry,tests


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,default=DEFAULT_CONFIG)
    p.add_argument('--magnetic-config',type=Path,default=DEFAULT_MAGNETIC)
    p.add_argument('--output',type=Path,default=DEFAULT_OUTPUT)
    p.add_argument('--skip-views',action='store_true')
    args=p.parse_args();start=time.monotonic()
    config=json.loads(args.config.read_text());baseline=checked_input(config,'base_geometry')
    magnetic_record=json.loads(args.magnetic_config.read_text())
    magnetic=magnetic_record.get('configuration',magnetic_record)
    args.output.mkdir(parents=True,exist_ok=True)
    geometry,controls=build(config,magnetic,baseline)
    save(args.output/'geometry.json',geometry)
    save(args.output/'shape-change-mapping.json',shape_mapping(baseline['panels'],geometry['panels']))
    controls['straight_wheel_gap_diagnostic']=wheel_gap_diagnostic(geometry,config)
    if not args.skip_views:draw_views(geometry,args.output/'geometry-views.png')
    sources=[args.config,Path(__file__),ROOT/'tools/muon_layout/geometry.py',ROOT/'tools/muon_layout/layout.py',
             ROOT/'tools/muon_layout/support.py',ROOT/'tools/toroid_prototype/geometry.py',
             ROOT/'docs/design/DES-039-twelvefold-toroid.md',ROOT/'docs/design/DES-040-muon-chambers-frame.md',
             ROOT/config['base_geometry'],ROOT/config['base_configuration'],ROOT/config['support_input'],args.magnetic_config]
    controls.update(input_revision=config['input_revision'],status=config['status'],
        sources={relative(path):digest(path) for path in sources},
        magnetic_configuration_sha256=digest(args.magnetic_config),
        command=['python','-m','tools.muon_layout.wheels','--config',relative(args.config),
                 '--magnetic-config',relative(args.magnetic_config),'--output',relative(args.output)]+(['--skip-views'] if args.skip_views else []),
        argv_paths='repository-relative; executed from repository root',
        runtime=dict(python=platform.python_version(),numpy=np.__version__,seconds=time.monotonic()-start),
        outputs={f.name:digest(f) for f in args.output.iterdir() if f.is_file() and f.name!='geometry-controls.json'})
    save(args.output/'geometry-controls.json',controls)
    print(json.dumps(dict(passed=controls['passed'],counts=controls['counts'],seconds=controls['runtime']['seconds']),indent=2),flush=True)


if __name__=='__main__':main()
