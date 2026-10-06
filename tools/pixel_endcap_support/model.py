"""DES014 design-only geometry: no production compact or active layout is written."""
from __future__ import annotations
import copy
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/module_layout'))
from geometry import _obb_overlap


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_inputs(path=None):
    path = Path(path) if path else Path(__file__).with_name('inputs.json')
    cfg = json.loads(path.read_text())
    positions = cfg['placement'].get('disc_abs_z_mm')
    if positions is not None:
        if (len(positions) != 9 or any(type(z) is not int or z <= 0 for z in positions)
                or any(a >= b for a, b in zip(positions, positions[1:]))):
            raise ValueError('Disc datums must be nine increasing positive integer millimetres')
    src = ROOT / cfg['baseline']
    if digest(src) != cfg['baseline_sha256']:
        raise ValueError('Baseline SHA changed: review module and interface provenance first')
    for item,expected in cfg['input_sha256'].items():
        if digest(ROOT/item)!=expected:raise ValueError('Dependent input SHA changed: '+item)
    layout = json.loads(gzip.decompress(src.read_bytes()))
    endcap=[b for b in layout['bodies'] if b['subsystem']=='pixel' and b['region']=='endcap']
    if any(b['family']!='quad' or abs(2*b['half_w_mm']-cfg['module_body_thickness_mm'])>1e-10 for b in endcap):
        raise ValueError('Review module family/thickness before using this support hypothesis')
    inherited = json.loads((ROOT / cfg['inherited_materials']).read_text())
    if any(v <= 0 for v in cfg['pickup'].values()):
        raise ValueError('Pickup layers must be positive')
    cool = cfg['cooling']
    if not 0 < cool['tube_wall_mm'] < cool['tube_OD_mm']/2:
        raise ValueError('Invalid tube wall')
    return cfg, layout, inherited


def polygon(b):
    return [[b['center_mm'][j]+s*b['half_u_mm']*b['u'][j]+t*b['half_v_mm']*b['v'][j]
             for j in range(2)] for s,t in [(-1,-1),(1,-1),(1,1),(-1,1)]]


def segment_distance(p,a,b):
    d=[b[i]-a[i] for i in range(2)]
    t=max(0.,min(1.,sum((p[i]-a[i])*d[i] for i in range(2))/sum(v*v for v in d)))
    return math.hypot(*(p[i]-a[i]-t*d[i] for i in range(2)))


def xy_gap(a,b):
    pa,pb=polygon(a),polygon(b)
    separated=False
    for axis in (a['u'][:2],a['v'][:2],b['u'][:2],b['v'][:2]):
        aa=[sum(x*y for x,y in zip(p,axis)) for p in pa]
        bb=[sum(x*y for x,y in zip(p,axis)) for p in pb]
        separated |= max(aa)<min(bb) or max(bb)<min(aa)
    if not separated:return 0.
    return min(segment_distance(p,pp[i],pp[(i+1)%4])
               for ps,pp in [(pa,pb),(pb,pa)] for p in ps for i in range(4))


def distance(a,b):
    dz=max(0.,abs(a['center_mm'][2]-b['center_mm'][2])-a['half_w_mm']-b['half_w_mm'])
    return math.hypot(dz,xy_gap(a,b))


def comparisons(aa,bb,tol,same=False):
    conflicts=[]; minimum=math.inf; pair=None
    for i,a in enumerate(aa):
        for j,b in enumerate(bb):
            if a['module_id']==b['module_id'] or (same and j<=i):continue
            # Cheap lower bound; retain exact shortest distance for nearby pairs.
            if math.dist(a['center_mm'][:2],b['center_mm'][:2])>100:continue
            if _obb_overlap(a,b,tolerance=tol):
                conflicts.append([a['module_id'],b['module_id']])
            d=distance(a,b)
            if d<minimum:minimum=d;pair=[a['module_id'],b['module_id']]
    return dict(overlaps=len(conflicts), examples=conflicts[:8], minimum_gap_mm=minimum,
                closest_module_pair=pair)


def template(layout):
    return [copy.deepcopy(b) for b in layout['bodies'] if b['layer_id']=='A-pixel-P1']


def dimensions(cfg):
    thick=2*cfg['plate']['skin_mm']+cfg['plate']['core_mm']
    pickup=sum(cfg['pickup'].values())
    return thick,pickup,cfg['module_body_thickness_mm']+pickup+cfg['placement']['gap_mm']


def proposal(template_bodies,cfg):
    thick,pickup,pitch=dimensions(cfg)
    bodies=[];tiles=[];feet=[]
    for original in template_bodies:
        b=copy.deepcopy(original)
        side=1 if b['row']%2 else -1
        levels=cfg['placement']['inner_phi_levels'] if b['row']==0 else cfg['placement']['other_phi_levels']
        h=(b['col']%levels)*pitch
        b['center_mm'][2]=side*(thick/2+pickup+b['half_w_mm']+h)
        b.update(kind='module',mount_face=side,foot_height_mm=h)
        tile=copy.deepcopy(b)
        tile.update(kind='pickup',half_w_mm=pickup/2)
        tile['center_mm'][2]=b['center_mm'][2]-side*(b['half_w_mm']+pickup/2)
        if h>0:
            foot=copy.deepcopy(b)
            foot.update(kind='foot',half_u_mm=cfg['foot']['envelope_u_mm']/2,
                        half_v_mm=cfg['foot']['envelope_v_mm']/2,half_w_mm=h/2)
            foot['center_mm']=[b['center_mm'][j]-cfg['foot']['radial_offset_mm']*b['v'][j] for j in range(2)]
            foot['center_mm'].append(side*(thick/2+h/2))
            feet.append(foot)
        bodies.append(b);tiles.append(tile)
    return bodies,tiles,feet


def retained(template_bodies,cfg,width):
    # A baseline P template only, w measured from nominal positive disc.
    bb=copy.deepcopy(template_bodies);posts=[]
    datum=bb[0]['center_mm'][2]-bb[0]['normal_offset_mm']
    for b in bb:
        b['center_mm'][2]-=datum
        bottom=b['center_mm'][2]+b['half_w_mm'];top=cfg['retained_case']['plate_front_mm']
        p=copy.deepcopy(b);p.update(kind='post',half_u_mm=width/2,half_v_mm=width/2,half_w_mm=(top-bottom)/2)
        p['center_mm'][2]=(top+bottom)/2;posts.append(p)
    return bb,posts


def disc_records(layout,cfg):
    thick,pickup,pitch=dimensions(cfg)
    result=[]
    for l in layout['layers']:
        if l['subsystem']!='pixel' or l['kind']!='disc':continue
        bs=[b for b in layout['bodies'] if b['layer_id']==l['id']]
        # Nominal is independent of placement's signed offset convention.
        old=bs[0]['center_mm'][2]-bs[0]['normal_offset_mm'];sgn=1 if old>0 else -1
        shift=cfg['placement']['first_disc_shift_mm'] if l['id'].endswith(('P1','N1')) else 0.
        positions=cfg['placement'].get('disc_abs_z_mm')
        datum=(positions[int(l['id'].rsplit('-',1)[1][1:])-1]
               if positions is not None else abs(old)+shift)
        shift=datum-abs(old)
        template_new=proposal(bs,cfg)[0]
        deltas=[sgn*datum+sgn*b['center_mm'][2]-a['center_mm'][2] for a,b in zip(bs,template_new)]
        collector=next((r for r in layout['metadata']['services']['routes']
                        if r['role']=='disc_collector' and l['id'] in r['layer_ids']),None)
        # Last discs use the existing bypass, documented separately.
        result.append(dict(layer=l['id'],side=sgn,old_z_mm=old,proposed_z_mm=sgn*datum,
                           modules=len(bs),chips=sum(p['layer_id']==l['id'] for p in layout['modules']),
                           body_abs_z_min_mm=datum+min(b['center_mm'][2]-b['half_w_mm'] for b in template_new),
                           body_abs_z_max_mm=datum+max(b['center_mm'][2]+b['half_w_mm'] for b in template_new),
                           collector_id=collector['id'] if collector else 'existing last-disc bypass',
                           collector_shift_mm=shift,minimum_module_z_change_mm=min(deltas),maximum_module_z_change_mm=max(deltas)))
    return result


def run_geometry(layout,cfg):
    source=template(layout); bodies,tiles,feet=proposal(source,cfg);tol=cfg['numerical_overlap_tolerance_mm']
    def xy_signature(bs):
        return sorted((b['row'],b['col'],b['family'],*(round(v,8) for v in b['center_mm'][:2]),
                       b['half_u_mm'],b['half_v_mm'],b['half_w_mm'],*b['u'],*b['v']) for b in bs)
    sig=xy_signature(source)
    discs=disc_records(layout,cfg)
    common=all(xy_signature([b for b in layout['bodies'] if b['layer_id']==d['layer']])==sig for d in discs)
    endcap_ids={d['layer'] for d in discs}
    active=[p for p in layout['modules'] if p['layer_id'] in endcap_ids]
    body=[b for b in layout['bodies'] if b['layer_id'] in endcap_ids]
    baseline_digest=hashlib.sha256(json.dumps(dict(bodies=body,patches=active),sort_keys=True,separators=(',',':')).encode()).hexdigest()
    checks={name:comparisons(aa,bb,tol,same) for name,aa,bb,same in
            [('body_body',bodies,bodies,True),('pickup_body',tiles,bodies,False),
             ('foot_body',feet,bodies,False),('foot_pickup',feet,tiles,False),
             ('pickup_pickup',tiles,tiles,True),('foot_foot',feet,feet,True)]}
    probe={}
    for width in [cfg['retained_case']['central_post_mm'],cfg['retained_case']['wider_post_probe_mm']]:
        bb,pp=retained(source,cfg,width);probe[str(width)]=comparisons(pp,bb,tol)
    cool=cfg['cooling'];p=cfg['plate'];half=dimensions(cfg)[0]/2
    rmax=max(math.hypot(*v) for b in bodies+tiles+feet for v in polygon(b))
    radii=[sum(math.hypot(*b['center_mm'][:2]) for b in bodies if b['row']==r)/sum(b['row']==r for b in bodies)+cfg['foot']['radial_offset_mm'] for r in range(5)]
    # Check against every non-pixel baseline body potentially sharing a proposed disc z range.
    min_other=math.inf
    for d in discs:
        for b in layout['bodies']:
            if b['subsystem']=='pixel':continue
            # All existing strip endcap n along z, barrel n transverse. Full corner z range.
            ext=sum(abs(axis[2])*b[key] for axis,key in zip([b['u'],b['v'],b['n']],['half_u_mm','half_v_mm','half_w_mm']))
            if abs(b['center_mm'][2]-d['proposed_z_mm'])>half+ext:continue
            # A corner bound is not an inner radius; nearest point to axis via projection.
            c=b['center_mm'];axes=[b['u'],b['v'],b['n']];hw=[b['half_u_mm'],b['half_v_mm'],b['half_w_mm']]
            # Project the two nonzero transverse axes: all current untilted strips.
            transverse=[(a,h) for a,h in zip(axes,hw) if math.hypot(*a[:2])>1e-10]
            if len(transverse)!=2:raise ValueError('Need an exact projected polygon for tilted strip')
            poly=[[c[j]+s*transverse[0][0][j]*transverse[0][1]+t*transverse[1][0][j]*transverse[1][1]
                   for j in range(2)] for s,t in [(-1,-1),(1,-1),(1,1),(-1,1)]]
            radial=min(segment_distance([0.,0.],poly[i],poly[(i+1)%4]) for i in range(4))
            min_other=min(min_other,radial-cfg['mounting']['tab_end_r_mm'])
    return dict(common_xy_template=common,discs=discs,rows=[dict(row=r,modules=sum(b['row']==r for b in bodies),cooling_radius_mm=radii[r]) for r in range(5)],
                frozen_endcap_digest=baseline_digest,baseline_module_count=len(body),baseline_chip_count=len(active),
                comparisons=checks,retained_backplate_post_probes=probe,
                sensitive_baseline_file_unmodified=True,maximum_module_radius_mm=rmax,
                tube_plane_gap_mm=abs(cool['routing_planes_mm'][1]-cool['routing_planes_mm'][0])-cool['tube_OD_mm'],
                tube_to_skin_clearance_mm=p['core_mm']/2-max(abs(z) for z in cool['routing_planes_mm'])-cool['tube_OD_mm']/2,
                outer_tube_to_plate_edge_mm=p['r_max_mm']-max(radii)-cool['tube_OD_mm']/2,
                tab_to_other_subsystem_radial_lower_bound_mm=min_other,
                first_disc_barrel_turn_clearance_mm=min(d['body_abs_z_min_mm'] for d in discs)-max(r['z_max_mm'] for r in layout['metadata']['services']['routes'] if r['subsystem']=='pixel' and r['role']=='barrel_turn' and r['side']=='positive'),
                body_to_trunk_radial_clearance_mm=190.-rmax,
                limitations=['Exact OBB screens cover module/pickup/foot envelopes; intentional own-module contacts excluded.',
                             'Common x/y pattern checked on all 18 discs; local screens repeat under z reflection.',
                             'Tube arc-to-radial transitions, weld lands, clips, flex artwork and mounting pockets are envelope concepts, not checked swept solids.',
                             'Two tube routing planes separate crossing envelopes, not a complete collision-free pipe design.'])
