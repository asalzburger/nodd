#!/usr/bin/env python3
"""PROTOTYPE ring-mounted candidate A: nominal geometry and material, not FEA."""
import argparse
import copy
import json
import math
from pathlib import Path
import subprocess
import sys

from outward import ROOT, corners, envelopes, load_layout, section, sha, _obb_overlap, stave_span
from services_geometry import body_envelope, _intersects


def make_mounts(layout, config, settings):
    """Six annular rings/layer and bounding boxes for discrete bearing feet."""
    assembly = section(layout, config, settings)
    bodies = assembly[0]
    boxes = envelopes(bodies, config)
    zplanes = settings['bearing_z_mm']
    if zplanes != sorted(set(zplanes)) or len(zplanes) < 2:
        raise ValueError('Ring stations must be ordered and distinct')
    if settings['axial_locator_z_mm'] not in zplanes:
        raise ValueError('Axial locator must be a ring station')
    if settings['section_z_mm'] not in zplanes:
        raise ValueError('Mounted drawing must cut a ring station')
    if settings['ring_to_stave_separation_mm'] <= 0 or settings['foot_tangential_width_mm'] <= 0:
        raise ValueError('Positive separation and foot width required')
    # Every selected ring must sit within each continuous stave's occupied length.
    for b in bodies:
        column = [m for m in layout['bodies'] if m['layer_id'] == b['layer_id'] and m['col'] == b['col']]
        lo, hi = stave_span(column, config)
        if zplanes[0]-config['rib_axial_mm']/2 < lo or zplanes[-1]+config['rib_axial_mm']/2 > hi:
            raise ValueError('Ring width extends past the continuous stave length')
        tangential_offset = sum(b['center_mm'][i]*b['u'][i] for i in range(2))
        if abs(tangential_offset)+settings['foot_tangential_width_mm']/2 > config['families'][b['family']]['spine_mm']/2:
            raise ValueError('Foot must fit on the narrow spine back face')
    rings, feet, layers = [], [], []
    for lid in sorted({b['layer_id'] for b in bodies}):
        bs = [b for b in bodies if b['layer_id'] == lid]
        support = [b for b in boxes if b['layer_id'] == lid]
        rmax = max(math.hypot(*p) for b in bs+support for p in corners(b))
        ri = rmax+settings['ring_to_stave_separation_mm']
        ro = ri+config['rib_radial_mm']
        density = config['density_g_cm3']['CFRP'] / 1000  # g/mm^3
        ring_mass = math.pi*(ro*ro-ri*ri)*config['rib_axial_mm']*density
        layer_feet = []
        for b in bs:
            spine = next(p for p in support if p['module_id'] == b['module_id'] and p['kind'] == 'spine')
            back = sum(spine['center_mm'][i]*spine['n'][i] for i in range(2))+spine['half_w_mm']
            half = settings['foot_tangential_width_mm']/2
            if math.hypot(back, half) >= ri:
                raise ValueError('Foot has no radial space below its ring')
            # Actual curved outer face ends at the inner ring cylinder; this box
            # encloses it for conservative conflict checks against other solids.
            foot = copy.deepcopy(b)
            foot.update(kind='foot', back_normal_mm=back, ring_inner_mm=ri,
                        half_u_mm=half, half_w_mm=(ri-back)/2,
                        half_v_mm=config['rib_axial_mm']/2)
            foot['center_mm'] = [((back+ri)/2)*n for n in b['n']]
            # Integral of sqrt(ri^2-u^2)-back, from -half to +half.
            area = half*math.sqrt(ri*ri-half*half)+ri*ri*math.asin(half/ri)-2*half*back
            foot['mass_g'] = area*config['rib_axial_mm']*density
            layer_feet.append(foot)
        for z in zplanes:
            rings.append(dict(id=f'{lid}-ring-z{z:g}', layer_id=lid,
                              r_min_mm=ri, r_max_mm=ro,
                              z_min_mm=z-config['rib_axial_mm']/2, z_max_mm=z+config['rib_axial_mm']/2,
                              z_mm=z, role='end mounting' if z in [zplanes[0], zplanes[-1]] else 'intermediate stiffening',
                              axial_locator=z == settings['axial_locator_z_mm'], mass_g=ring_mass))
            for foot in layer_feet:
                f = copy.deepcopy(foot)
                f['center_mm'][2] = z
                feet.append(f)
        layers.append(dict(layer=lid, staves=len(bs), nominal_radius_mm=next(l['r_m']*1000 for l in layout['layers'] if l['id'] == lid),
                           stave_outer_radius_mm=rmax, ring_inner_radius_mm=ri, ring_outer_radius_mm=ro,
                           rings=len(zplanes), feet=len(bs)*len(zplanes), ring_mass_g=ring_mass*len(zplanes),
                           foot_envelope_mass_g=sum(f['mass_g'] for f in layer_feet)*len(zplanes),
                           foot_height_range_mm=[min(ri-f['back_normal_mm'] for f in layer_feet),
                                                 max(ri-f['back_normal_mm'] for f in layer_feet)]))
    return assembly, boxes, rings, feet, layers


def check_mounts(layout, config, settings, mounts):
    assembly, boxes, rings, feet, layers = mounts
    # Exact body radial/z extrema; a disjoint projection proves no intersection.
    all_body_bounds = [(b, body_envelope(b)) for b in layout['bodies']]
    ring_body = [(r['id'], b['module_id']) for r in rings for b, e in all_body_bounds if _intersects(r, e)]
    ring_routes = [(r['id'], q['id']) for r in rings for q in layout['metadata']['services']['routes'] if _intersects(r, q)]
    ring_reservations = [(r['id'], q['layer_id']) for r in rings for q in layout['metadata']['services']['supports'] if _intersects(r, q)]
    # Stave columns are uniform: reuse one transverse section for support/foot
    # checks at all stations, with identical arbitrary extrusion about z=0.
    cut_feet = [copy.deepcopy(f) for f in feet if f['center_mm'][2] == settings['section_z_mm']]
    for f in cut_feet:
        f['center_mm'][2] = 0.
        f['half_v_mm'] = 1.
    tol = settings['overlap_tolerance_mm']  # numerical, not engineering clearance
    foot_bounds = [(f, body_envelope(f)) for f in feet]
    foot_body = [(f['layer_id'], f['col'], f['center_mm'][2], b['module_id'])
                 for f, bounds in foot_bounds for b, e in all_body_bounds
                 if _intersects(bounds, e) and _obb_overlap(f, b, tolerance=tol)]
    foot_support = [(f['layer_id'], f['col'], b['layer_id'], b['col']) for f in cut_feet for b in boxes if _obb_overlap(f, b, tolerance=tol)]
    foot_foot = [(a['layer_id'], a['col'], b['layer_id'], b['col']) for i, a in enumerate(cut_feet) for b in cut_feet[i+1:] if _obb_overlap(a, b, tolerance=tol)]
    # Projection is conservative for narrow feet too; report potential conflicts.
    foot_routes = [(f['layer_id'], f['col'], f['center_mm'][2], q['id']) for f, e in foot_bounds
                   for q in layout['metadata']['services']['routes'] if _intersects(e, q)]
    foot_reservations = [(f['layer_id'], f['col'], f['center_mm'][2], q['layer_id']) for f, e in foot_bounds
                        for q in layout['metadata']['services']['supports'] if _intersects(e, q)]
    ring_ring = [(a['id'], b['id']) for i, a in enumerate(rings) for b in rings[i+1:] if _intersects(a, b)]
    foot_other_ring = [(f['layer_id'], f['col'], f['center_mm'][2], r['id']) for f, e in foot_bounds for r in rings
                       if (f['layer_id'], f['center_mm'][2]) != (r['layer_id'], r['z_mm']) and _intersects(e, r)]
    ring_support = [(r['id'], p['layer_id'], p['col']) for r in rings if r['z_mm'] == settings['section_z_mm']
                    for p in boxes if _intersects(dict(r, z_min_mm=-1, z_max_mm=1), body_envelope(p))]
    pixel_start = min(abs(q['z_min_mm']) for q in layout['metadata']['services']['routes']
                      if q['subsystem'] == 'pixel' and q['role'] == 'barrel_turn' and q['side'] == 'positive')
    result = dict(status='PROTOTYPE ring and foot envelopes; no cage stiffness or mounting qualification',
                  layers=layers, ring_count=len(rings), foot_count=len(feet),
                  bearing_z_mm=settings['bearing_z_mm'], axial_locator_z_mm=settings['axial_locator_z_mm'],
                  maximum_station_pitch_mm=max(b-a for a, b in zip(settings['bearing_z_mm'], settings['bearing_z_mm'][1:])),
                  ring_axial_mm=config['rib_axial_mm'], ring_radial_mm=config['rib_radial_mm'],
                  radial_separation_mm=settings['ring_to_stave_separation_mm'],
                  overlap_tolerance_mm=tol,
                  barrel_service_start_abs_z_mm=pixel_start,
                  end_ring_to_service_axial_gap_mm=pixel_start-max(r['z_max_mm'] for r in rings),
                  ring_mass_g=sum(r['mass_g'] for r in rings), foot_envelope_mass_g=sum(f['mass_g'] for f in feet),
                  local_radial_ring_X0_percent=100*config['rib_radial_mm']/config['radiation_length_mm']['CFRP'],
                  nominal_conflicts=dict(ring_body=ring_body, ring_routes=ring_routes, ring_reservations=ring_reservations,
                                         ring_support=ring_support, foot_body=foot_body, foot_support=foot_support,
                                         foot_foot=foot_foot, foot_routes=foot_routes,
                                         foot_reservations=foot_reservations, ring_ring=ring_ring,
                                         foot_other_ring=foot_other_ring),
                  limitations=['Six ring stations are proposed, not an optimized or proven minimum.',
                               'Intermediate rings stiffen the cage; they are not grounded 220 mm beam supports.',
                               'Mass includes solid CFRP ring/foot envelopes only; joints, inserts, adhesive, global mounts and tolerances omitted.',
                               'No module or active surface moved; no production integration or new tracking/FEA result.'])
    return result


def foot_polygon(foot):
    half = foot['half_u_mm']
    back = foot['back_normal_mm']
    ri = foot['ring_inner_mm']
    local = [(-half, back), (half, back)]
    # Drawing approximation to the exact circular face used for the mass integral.
    local += [(u, math.sqrt(ri*ri-u*u)) for u in [half-2*half*i/16 for i in range(17)]]
    return [[u*foot['u'][i]+r*foot['n'][i] for i in range(2)] for u, r in local]


def draw(layout, config, settings, mounts, result, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Circle, Patch, Polygon, Rectangle, Wedge
    plt.rcParams.update({'font.size': 10, 'svg.fonttype': 'none', 'pdf.fonttype': 42,
                         'svg.hashsalt': 'DES002-mounted-A'})
    assembly, boxes, rings, feet, layers = mounts
    bodies, sensors, parts, tubes = assembly
    purple, foot_color = '#7043a1', '#94a8be'
    colors = dict(interface='#bc693e', insulation='#c9a629', graphite='#78919c', top_skin='#303c49', core='#ead5a3', bottom_skin='#303c49')
    cut_rings = [r for r in rings if r['z_mm'] == settings['section_z_mm']]
    cut_feet = [f for f in feet if f['center_mm'][2] == settings['section_z_mm']]

    def save(fig, name):
        for ext in ['png', 'pdf', 'svg']:
            target = output/f'{name}.{ext}'
            metadata = {'Date': None} if ext == 'svg' else ({'CreationDate': None, 'ModDate': None} if ext == 'pdf' else {})
            fig.savefig(target, dpi=190, metadata=metadata)
            if ext == 'svg':
                target.write_text('\n'.join(s.rstrip() for s in target.read_text().splitlines())+'\n')
        plt.close(fig)

    def paint(ax, lids, only=None):
        def use(p): return p['layer_id'] in lids and (only is None or p['module_id'] == only)
        for r in cut_rings:
            if r['layer_id'] in lids:
                ax.add_patch(Wedge((0, 0), r['r_max_mm'], 0, 360, width=r['r_max_mm']-r['r_min_mm'], fc=purple, ec='none'))
        for b in bodies:
            if use(b): ax.add_patch(Polygon(corners(b), fc='#dfebe3', ec='#819a88', lw=.35))
        for p in parts:
            if use(p): ax.add_patch(Polygon(corners(p), fc=colors[p['kind']], ec='none'))
        for f in cut_feet:
            if use(f): ax.add_patch(Polygon(foot_polygon(f), fc=foot_color, ec='#53697e', lw=.35))
        for t in tubes:
            if use(t):
                ax.add_patch(Circle(t['center_mm'], t['outer_radius_mm'], fc='#8399a5', ec='#38434d', lw=.35))
                ax.add_patch(Circle(t['center_mm'], t['inner_radius_mm'], fc='#267eb7' if t['flow_sign'] == -1 else '#ce6058', ec='none'))
        for m in sensors:
            if use(m):
                ends = [[m['center_mm'][j]+s*m['half_u_mm']*m['u'][j] for j in range(2)] for s in [-1, 1]]
                ax.plot([p[0] for p in ends], [p[1] for p in ends], c='#187943', lw=.9)
        ax.set_aspect('equal'); ax.grid(alpha=.15); ax.set_xlabel('x [mm]'); ax.set_ylabel('y [mm]')

    handles = [Line2D([], [], color='#187943', label='Active sensor plane (fixed)'), Patch(fc='#dfebe3', ec='#819a88', label='Module body envelope'),
               Patch(fc='#ead5a3', ec='#303c49', label='Foam + CFRP stave (outward)'), Patch(fc='#267eb7', label='Two Ti / CO₂ circuits per stave'),
               Patch(fc=purple, label=f"CFRP ring: {config['rib_radial_mm']:g} mm radial × {config['rib_axial_mm']:g} mm z"),
               Patch(fc=foot_color, label=f"Bearing-foot envelope ({settings['foot_tangential_width_mm']:g} mm wide)")]
    for layer in layers+[None]:
        chosen = [layer] if layer else layers; lids = {l['layer'] for l in chosen}
        tag = layer['layer'].split('-')[-1] if layer else 'all'
        fig = plt.figure(figsize=(13.2, 9.5)); ax = fig.add_axes([.07, .18, .59, .70])
        paint(ax, lids); limit=max(l['ring_outer_radius_mm'] for l in chosen)*1.10
        ax.set_xlim(-limit, limit); ax.set_ylim(-limit, limit); ax.plot(0, 0, '+', color='#59616b', ms=9)
        ax.annotate('beam axis', (0, 0), (6, -14), textcoords='offset points', fontsize=9)
        label = (f"{tag} | {layer['staves']} staves | {layer['rings']} ring stations" if layer
                 else f"All four barrels | {result['ring_count']} rings in total")
        fig.suptitle('Candidate A — outward staves with mounting rings\n'+label, fontsize=17, y=.97)
        fig.text(.075, .895, f"Actual x–y section at z = +{settings['section_z_mm']:g} mm, through an intermediate ring", fontsize=10)
        fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(.69, .89), frameon=False, fontsize=9)
        dl=layer or layers[0]; b=next(b for b in bodies if b['layer_id']==dl['layer'] and b['col']==0)
        detail=fig.add_axes([.74, .40, .22, .26]); paint(detail, {dl['layer']}, b['module_id'])
        detail.set_xlim(b['center_mm'][0]-2, dl['ring_outer_radius_mm']+1)
        detail.set_ylim(-b['half_u_mm']-2, b['half_u_mm']+2)
        detail.set_title(f"{dl['layer'].split('-')[-1]}: stave → foot → ring", fontsize=9)
        detail.tick_params(labelsize=7); detail.xaxis.label.set_size(8); detail.yaxis.label.set_size(8)
        fig.text(.715, .345, 'Sensor side ← beam       +r / ring →', fontsize=9)
        if layer:
            note=f"Ring radii: {layer['ring_inner_radius_mm']:.3f}–{layer['ring_outer_radius_mm']:.3f} mm\nFoot heights: {layer['foot_height_range_mm'][0]:.2f}–{layer['foot_height_range_mm'][1]:.2f} mm\n{layer['rings']} rings + {layer['feet']} foot envelopes"
        else:
            note='\n'.join(f"{l['layer'].split('-')[-1]} ring outer r: {l['ring_outer_radius_mm']:.3f} mm" for l in layers)
        fig.text(.715, .305, note, va='top', fontsize=9.5, linespacing=1.5)
        zlabel=', '.join(f'{z:+g}' for z in settings['bearing_z_mm'])
        fig.text(.715, .175, f"z stations [mm]: {zlabel}\n2 end mounts + {len(settings['bearing_z_mm'])-2} stiffening rings / layer\nRings are not independently grounded bearings.", fontsize=8.0, va='top')
        fig.text(.075, .055, 'PROTOTYPE · mm, true x–y aspect ratio; sensor line width symbolic. Module positions unchanged.\n'
                 'Feet follow the staggering. Pins, inserts, split joints and global end mounts remain unresolved.\n'
                 'This is a ring plane; the earlier z = 25 mm section remains the view between rings.', fontsize=9, color='#515964')
        save(fig, f'barrel-{tag}')

    fig=plt.figure(figsize=(14, 8.5)); ax=fig.add_axes([.065, .52, .90, .35])
    pixel_routes=[q for q in layout['metadata']['services']['routes'] if q['subsystem']=='pixel' and q['role'] in ['barrel_turn','subsystem_trunk']]
    def rz(a):
        for q in pixel_routes:
            a.add_patch(Rectangle((q['z_min_mm'], q['r_min_mm']), q['z_max_mm']-q['z_min_mm'], q['r_max_mm']-q['r_min_mm'], fc='#efd8b8', ec='none', alpha=.7))
        # One representative of each radial level; phi projection includes both.
        for l in layers:
            lid=l['layer']; selected=[b for b in layout['bodies'] if b['layer_id']==lid and b['col'] in [0,1]]
            for b in selected:
                e=body_envelope(b)
                a.add_patch(Rectangle((e['z_min_mm'], e['r_min_mm']), e['z_max_mm']-e['z_min_mm'], e['r_max_mm']-e['r_min_mm'], fc='#dfebe3', ec='#819a88', lw=.3))
            for col in [0,1]:
                bs=[b for b in selected if b['col']==col]; zmin,zmax=stave_span(bs,config)
                for p in boxes:
                    if p['layer_id']==lid and p['col']==col:
                        e=body_envelope(p)
                        a.add_patch(Rectangle((zmin, e['r_min_mm']), zmax-zmin, e['r_max_mm']-e['r_min_mm'], fc='#ead5a3', ec='#303c49', lw=.3, alpha=.7))
            for m in layout['modules']:
                if m['layer_id']==lid and m['col'] in [0,1]:
                    e=body_envelope(dict(m,half_w_mm=0.))
                    a.add_patch(Rectangle((e['z_min_mm'],e['r_min_mm']),e['z_max_mm']-e['z_min_mm'],e['r_max_mm']-e['r_min_mm'],fc='#187943',alpha=.65,ec='none'))
        for f in feet:
            if f['col'] in [0,1]:
                a.add_patch(Rectangle((f['center_mm'][2]-f['half_v_mm'],f['back_normal_mm']),2*f['half_v_mm'],f['ring_inner_mm']-f['back_normal_mm'],fc=foot_color,ec='none',alpha=.8))
        for r in rings:
            a.add_patch(Rectangle((r['z_min_mm'],r['r_min_mm']),r['z_max_mm']-r['z_min_mm'],r['r_max_mm']-r['r_min_mm'],fc=purple,ec=purple,lw=.4))
        a.set_xlabel('z [mm]');a.set_ylabel('|r| [mm]');a.grid(alpha=.15);a.set_aspect('equal')
    rz(ax);ax.set_xlim(-625,625);ax.set_ylim(0,240)
    for z in settings['bearing_z_mm']:
        ax.axvline(z,color=purple,ls=':',lw=.7,alpha=.45)
        ax.text(z,243,f'{z:+g}',ha='center',fontsize=8)
    for l in layers:ax.text(-618,l['nominal_radius_mm'],l['layer'].split('-')[-1],fontsize=8,va='center')
    fig.suptitle('Candidate A — pixel barrel |r|–z assembly\nSix ring stations per barrel, with end rings clear of the service bays',fontsize=16,y=.97)
    fig.text(.065,.90,'Projection over φ: both stagger levels shown; dotted vertical lines locate stations, not solid radial walls.',fontsize=10)
    detail=fig.add_axes([.075,.12,.34,.30]);rz(detail);detail.set_xlim(535,568);detail.set_ylim(175,198)
    detail.set_title(f"B4 positive end: {result['end_ring_to_service_axial_gap_mm']:g} mm axial ring-to-bay gap",fontsize=10)
    detail.annotate('',(550,195),(555,195),arrowprops=dict(arrowstyle='<->',color='black'))
    detail.text(552.5,195.5,'5 mm',ha='center',fontsize=8)
    fig.text(.48,.40,'Mounting and constraint proposal',fontsize=12,fontweight='bold')
    fig.text(.48,.36,'End rings at z = ±546 mm attach to global end supports (interface unresolved).\n'
             'Four internal rings hold barrel shape and share loads; maximum station pitch 220 mm.\n'
             'One axial locator at −546 mm; other feet slide/flex along z during cooldown.\n'
             'The global cage stiffness must be verified: short-span beam sag is not a cage result.\n\n'
             f"{result['ring_count']} CFRP rings: {result['ring_mass_g']:.1f} g; {result['foot_count']} solid foot envelopes: {result['foot_envelope_mass_g']:.1f} g.\n"
             'Additional pins, inserts, joints, adhesive, flex and global mounts are not counted.\n'
             f"B4 rings extend to r = {next(l['ring_outer_radius_mm'] for l in layers if l['layer']=='A-pixel-B4'):.3f} mm, only at the ring z bands.\n"
             'Their outer end is |z| = 550 mm; the reserved service bay begins at 555 mm.',
             fontsize=9.3,va='top',linespacing=1.5)
    fig.legend(handles=[handles[0],handles[2],handles[4],handles[5],Patch(fc='#efd8b8',label='Reserved service volumes')],loc='lower center',bbox_to_anchor=(.5,.015),ncol=3,frameon=False,fontsize=9)
    save(fig,'barrels-rz')
    return matplotlib.__version__


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'docs/validation/DES-002/outward-A-mounted')
    args=parser.parse_args()
    config=json.loads(Path(__file__).with_name('inputs.json').read_text())
    settings=json.loads(Path(__file__).with_name('mounting.json').read_text())
    layout=load_layout(config);mounts=make_mounts(layout,config,settings);result=check_mounts(layout,config,settings,mounts)
    args.output.mkdir(parents=True,exist_ok=True)
    version=draw(layout,config,settings,mounts,result,args.output)
    paths=['tools/pixel_support/mounting.py','tools/pixel_support/mounting.json','tools/pixel_support/inputs.json',
           'tools/pixel_support/outward.py','tools/module_layout/geometry.py','tools/module_layout/services_geometry.py']
    import numpy
    result['provenance']=dict(baseline=config['baseline'],baseline_sha256=config['baseline_sha256'],
                              producer_files_sha256={p:sha(ROOT/p) for p in paths},python=sys.version,matplotlib=version,
                              numpy=numpy.__version__,
                              source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                              command='python3 -B '+' '.join(sys.argv),random_seed=None)
    (args.output/'screening.json').write_text(json.dumps(result,indent=2)+'\n')
    files=sorted(args.output.glob('barrel*.*'))+[args.output/'screening.json']
    (args.output/'artifacts.json').write_text(json.dumps(dict(producer_files_sha256=result['provenance']['producer_files_sha256'],
                                                            artifacts_sha256={p.name:sha(p) for p in files}),indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='provenance'},indent=2))
    if any(result['nominal_conflicts'].values()):raise SystemExit('Potential nominal collision: review screen before accepting layout')


if __name__=='__main__':main()
