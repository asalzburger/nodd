"""DES030 physical boundary masks, pad topology and deterministic ECAL layouts.

Standard library only. All units are mm. No production detector inputs change.
"""
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from assembly import inventory
from model import ROOT, sha

EPS = 1e-8


def signed_area(p):
    return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))/2


def area(p):
    return abs(signed_area(p)) if len(p)>2 else 0.


def clean(p):
    q=[]
    for a in p:
        if not q or math.dist(a,q[-1])>EPS:q.append(a)
    if len(q)>1 and math.dist(q[0],q[-1])<EPS:q.pop()
    changed=True
    while changed and len(q)>2:
        changed=False
        for i in range(len(q)):
            a,b,c=q[i-1],q[i],q[(i+1)%len(q)]
            if abs((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]))<EPS:
                q.pop(i);changed=True;break
    if signed_area(q)<0:q.reverse()
    return q if area(q)>EPS else []


def clip(p,a,b,c):
    """Clip to a*x+b*y <= c; retain convex polygons counterclockwise."""
    if not p:return []
    out=[]
    for u,v in zip(p,p[1:]+p[:1]):
        du,dv=a*u[0]+b*u[1]-c,a*v[0]+b*v[1]-c
        if du<=EPS:out.append(u)
        if (du>EPS)!=(dv>EPS):
            t=du/(du-dv);out.append([u[0]+t*(v[0]-u[0]),u[1]+t*(v[1]-u[1])])
    return clean(out)


def rectangle(x,y,w,h):return [[x,y],[x+w,y],[x+w,y+h],[x,y+h]]


def planes(p):
    for u,v in zip(p,p[1:]+p[:1]):
        a,b=v[1]-u[1],u[0]-v[0];yield a,b,a*u[0]+b*u[1]


def intersect(p,q):
    for a,b,c in planes(q):p=clip(p,a,b,c)
    return p


def inset(p,d):
    q=p
    for a,b,c in planes(p):q=clip(q,a,b,c-d*math.hypot(a,b))
    return q


def contains(p,x,y,tol=EPS):
    return bool(p) and all(a*x+b*y<=c+tol*math.hypot(a,b) for a,b,c in planes(p))


def centroid(p):
    cross=[a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])];den=3*sum(cross)
    return [sum((a[k]+b[k])*v for a,b,v in zip(p,p[1:]+p[:1],cross))/den for k in (0,1)]


def min_width(p):
    return min((max(a*x+b*y for x,y in p)-min(a*x+b*y for x,y in p))/math.hypot(a,b) for a,b,_ in planes(p))


def regular(apothem,n=16):
    r=apothem/math.cos(math.pi/n)
    return [[r*math.cos((2*k+1)*math.pi/n),r*math.sin((2*k+1)*math.pi/n)] for k in range(n)]


def quarter(p,side):return clip(clip(p,-1,0,-side),0,-1,-side)


def circle_intersection_area(p,r):
    """Exact polygon/disc intersection by directed triangle/sector integration."""
    total=0.
    for a,b in zip(p,p[1:]+p[:1]):
        dx,dy=b[0]-a[0],b[1]-a[1];A=dx*dx+dy*dy;B=2*(a[0]*dx+a[1]*dy);C=a[0]**2+a[1]**2-r*r
        ts=[0.,1.];disc=B*B-4*A*C
        if disc>0 and A>0:
            for t in ((-B-math.sqrt(disc))/(2*A),(-B+math.sqrt(disc))/(2*A)):
                if 0<t<1:ts.append(t)
        ts.sort()
        for t,u in zip(ts,ts[1:]):
            x,y=[a[0]+t*dx,a[1]+t*dy],[a[0]+u*dx,a[1]+u*dy];mid=(t+u)/2
            cross=x[0]*y[1]-x[1]*y[0]
            if (a[0]+mid*dx)**2+(a[1]+mid*dy)**2<=r*r+EPS:total+=cross/2
            else:total+=r*r*math.atan2(cross,x[0]*y[0]+x[1]*y[1])/2
    return abs(total)


def pad_mask(active,pitch,minimum):
    lo=[min(v[k] for v in active) for k in (0,1)];hi=[max(v[k] for v in active) for k in (0,1)];raw={}
    for ix in range(math.floor(lo[0]/pitch),math.ceil(hi[0]/pitch)):
        for iy in range(math.floor(lo[1]/pitch),math.ceil(hi[1]/pitch)):
            p=intersect(rectangle(ix*pitch,iy*pitch,pitch,pitch),active)
            if area(p)>EPS:raw[(ix,iy)]=dict(key=[ix,iy],polygons=[p],area_mm2=area(p),members=[[ix,iy]])
    groups={k:v for k,v in raw.items()};membership={k:k for k in raw}
    # Only grid-adjacent electrodes merge: the union remains connected.
    while True:
        small=sorted((k for k,g in groups.items() if g['area_mm2']<minimum-EPS),key=lambda k:(groups[k]['area_mm2'],k))
        if not small:break
        k=small[0];g=groups[k];neighbours=set()
        for ix,iy in g['members']:
            for q in ((ix-1,iy),(ix+1,iy),(ix,iy-1),(ix,iy+1)):
                if q in membership and membership[q]!=k:neighbours.add(membership[q])
        if not neighbours:raise ValueError('isolated tiny pad')
        dest=max(neighbours,key=lambda q:(groups[q]['area_mm2'],-q[0],-q[1]));h=groups[dest]
        for q in g['members']:membership[tuple(q)]=dest
        h['polygons']+=g['polygons'];h['members']+=g['members'];h['area_mm2']+=g['area_mm2'];del groups[k]
    result=[]
    for k,g in sorted(groups.items()):
        p=[sum(centroid(q)[i]*area(q) for q in g['polygons'])/g['area_mm2'] for i in (0,1)]
        raw_key=(math.floor(p[0]/pitch),math.floor(p[1]/pitch))
        # A concave merged electrode may have its centroid outside the union.
        # Its interior reference point then comes from the largest constituent.
        if membership.get(raw_key)!=k:p=centroid(max(g['polygons'],key=area))
        assert membership[(math.floor(p[0]/pitch),math.floor(p[1]/pitch))]==k
        g['reference_mm']=p;g['reference_is_area_centroid']=math.dist(p,[sum(centroid(q)[i]*area(q) for q in g['polygons'])/g['area_mm2'] for i in (0,1)])<EPS
        g['bbox_mm']=[max(v[i] for q in g['polygons'] for v in q)-min(v[i] for q in g['polygons'] for v in q) for i in (0,1)]
        result.append(g)
    assert math.isclose(sum(g['area_mm2'] for g in result),area(active),rel_tol=1e-10)
    return result


def asic_slots(board,count,c,e):
    w,h=e['asic_package_xy_mm'];gap=c['asic_clearance_mm'];step=c['asic_search_step_mm']
    lo=[min(p[i] for p in board) for i in (0,1)];hi=[max(p[i] for p in board) for i in (0,1)]
    preferred=[[-22,-22],[-22,22],[22,-22],[22,22]];candidates=preferred+[[lo[0]+w/2+gap+i*step,lo[1]+h/2+gap+j*step] for i in range(max(0,math.floor((hi[0]-lo[0]-w-2*gap)/step)+1)) for j in range(max(0,math.floor((hi[1]-lo[1]-h-2*gap)/step)+1))]
    slots=[]
    for x,y in candidates:
        if not all(contains(board,u,v) for u,v in rectangle(x-w/2-gap/2,y-h/2-gap/2,w+gap,h+gap)):continue
        if any(abs(x-u)<w+gap-EPS and abs(y-v)<h+gap-EPS for u,v in slots):continue
        slots.append([x,y])
        if len(slots)==count:return slots
    return None


def pack(c,e,outer,phase,edges,detail=True):
    size=e['sensor_outer_mm'];board_size=size+2*c['board_margin_mm'];step=board_size+c['board_gap_mm'];start=c['carrier_side_reserve_mm']+phase
    face=quarter(inset(outer,c['outer_service_band_mm']+c['inner_support_mm']),c['carrier_side_reserve_mm'])
    hole=c['inner_square_apothem_mm']+c['inner_support_mm'];modules=[];rejected=Counter();grid={}
    n=math.ceil(max(p[0] for p in outer)/step)
    for ix in range(n):
        for iy in range(n):
            x,y=start+ix*step,start+iy*step;blank=rectangle(x,y,board_size,board_size);board=intersect(blank,face)
            if not board:continue
            if x<hole-EPS and y<hole-EPS:rejected['inner_support_cell']+=1;continue
            full=math.isclose(area(board),board_size**2,rel_tol=1e-10)
            if not full and not edges:rejected['needs_edge_profile']+=1;continue
            sensor=inset(board,c['board_margin_mm'])
            if not sensor or area(sensor)<c['minimum_sensor_area_mm2'] or min_width(sensor)<c['minimum_sensor_width_mm']:
                rejected['small_or_narrow_profile']+=1;continue
            active=inset(sensor,(size-e['sensor_active_mm'])/2 if full else c['edge_guard_mm'])
            if not active:rejected['no_active_window']+=1;continue
            origin=[x+board_size/2,y+board_size/2]
            local=lambda p:[[a-origin[0],b-origin[1]] for a,b in p]
            # The grid address preserves existing square IDs when edge units are added.
            m=dict(index=ix*n+iy,grid=[ix,iy],center_mm=origin,board=local(board),sensor=local(sensor),active=local(active),full=full,sensitive_area_mm2=area(active),family='square' if full else {3:'triangle',4:'trapezoid',5:'chamfered',6:'double_chamfer'}.get(len(sensor),'polygon'))
            if detail:
                m['pads']=pad_mask(m['active'],e['pitch_mm'],c['minimum_pad_fraction']*e['pitch_mm']**2)
                m['asics']=asic_slots(m['board'],math.ceil(len(m['pads'])/e['asic_channels']),c,e)
                if m['asics'] is None:rejected['electronics_does_not_fit']+=1;continue
            modules.append(m);grid[(ix,iy)]=m
    if any(m['index']>=1024 for m in modules):raise ValueError('module ID field capacity')
    def hit(x,y):
        m=grid.get((math.floor((x-start)/step),math.floor((y-start)/step)))
        return bool(m and contains(m['active'],x-m['center_mm'][0],y-m['center_mm'][1]))
    return dict(modules=modules,phase_mm=phase,rejected=dict(rejected),active_area_mm2=sum(m['sensitive_area_mm2'] for m in modules),hit=hit)


def build():
    c=json.loads((ROOT/'tools/calorimeter_hardware/edge_sensors.json').read_text());base,_=inventory();e=base['units'][0];econfig=json.loads((ROOT/'tools/calorimeter_hardware/cassettes.json').read_text())['ecal']
    for key in ('target_abs_eta','inner_square_apothem_mm','inner_support_mm','carrier_side_reserve_mm','outer_service_band_mm','board_margin_mm','board_gap_mm','edge_guard_mm','minimum_sensor_area_mm2','minimum_sensor_width_mm','minimum_pad_fraction','cooling_plate_mm'):
        if not math.isfinite(c[key]) or c[key]<=0:raise ValueError('invalid '+key)
    if c['carriers']!=4:raise ValueError('this prototype has four quadrant carriers')
    front=base['envelopes']['ecal_endcap_front_mm'];radius=base['envelopes']['ecal_barrel_outer_mm'];outer=regular(radius);target_r=front/math.sinh(c['target_abs_eta'])
    if math.sqrt(2)*(c['inner_square_apothem_mm']+c['inner_support_mm'])>=target_r:raise ValueError('supported aperture blocks eta target')
    search=[]
    for phase in c['grid_phase_candidates_mm']:
        p=pack(c,econfig,outer,phase,False,False);coverage=sum(p['hit'](target_r*math.cos((i+.5)*math.pi/360),target_r*math.sin((i+.5)*math.pi/360)) for i in range(180))/180
        search.append(dict(phase_mm=phase,target_front_active_phi_fraction=coverage,quarter_active_area_mm2=p['active_area_mm2']))
    phase=max(search,key=lambda q:(q['target_front_active_phi_fraction'],q['quarter_active_area_mm2']))['phase_mm']
    layouts={name:pack(c,econfig,outer,phase,edges) for name,edges in (('squares',False),('edges',True))}
    face=area(outer)-4*c['inner_square_apothem_mm']**2;fiducial=area(outer)-math.pi*target_r**2;summary={}
    for name,p in layouts.items():
        modules=p['modules'];pads=sum(len(m['pads']) for m in modules);asics=sum(len(m['asics']) for m in modules);interfaces=math.ceil(pads/8192);powered=asics*econfig['asic_channels'];lv=(powered*econfig['asic_continuous_W_channel']+interfaces*econfig['interface_W'])/.9;bias=pads*econfig['bias_V']*econfig['leakage_A_channel']
        target_active=sum(area([[x+m['center_mm'][0],y+m['center_mm'][1]] for x,y in m['active']])-circle_intersection_area([[x+m['center_mm'][0],y+m['center_mm'][1]] for x,y in m['active']],target_r) for m in modules)*4
        summary[name]=dict(quarter_sensors=len(modules),quarter_edge_sensors=sum(not m['full'] for m in modules),quarter_channels=pads,quarter_asic_packages=asics,quarter_powered_asic_channels=powered,quarter_unused_asic_channels=powered-pads,quarter_interfaces=interfaces,active_face_fraction=4*p['active_area_mm2']/face,active_eta4_fiducial_face_fraction=target_active/fiducial,rejected=p['rejected'],families=dict(Counter(m['family'] for m in modules)),channels_both_endcaps=pads*4*2*48,continuous_heat_both_endcaps_W=(lv+bias)*4*2*48,minimum_pad_area_mm2=min(g['area_mm2'] for m in modules for g in m['pads']),merged_electrodes=sum(len(g['members'])>1 for m in modules for g in m['pads']))
    profiles={}
    for m in layouts['edges']['modules']:
        if m['full']:continue
        key=tuple(tuple(round(v,7) for v in p) for p in m['sensor']);profiles.setdefault(key,dict(family=m['family'],sensor_mm=m['sensor'],active_mm=m['active'],board_mm=m['board'],occurrences_per_quarter=0,pad_channels=len(m['pads']),asic_packages=len(m['asics'])))['occurrences_per_quarter']+=1
    for i,p in enumerate(profiles.values()):p['id']=f'E{i:03d}'
    report=dict(status='DRAFT / PROTOTYPE',config=c,front_mm=front,outer_apothem_mm=radius,outer_polygon_mm=outer,layer_pitch_mm=base['regions'][1]['pitch_mm'],layers=48,back_cover_mm=base['config']['back_cover_mm'],eta4_front_radius_mm=target_r,nominal_face_area_mm2=face,eta4_fiducial_face_area_mm2=fiducial,grid_phase_search=search,summary=summary,edge_profiles=list(profiles.values()),source_sha256={**base['source_sha256'],**{str(p.relative_to(ROOT)):sha(p) for p in (Path(__file__),ROOT/'tools/calorimeter_hardware/edge_sensors.json')}})
    return report,layouts,base


if __name__=='__main__':
    report,layouts,_=build();out=ROOT/'build/calorimeter/edges';out.mkdir(parents=True,exist_ok=True)
    (out/'layout.json').write_text(json.dumps(report,indent=2)+'\n');(out/'modules.json').write_text(json.dumps({k:{q:v for q,v in p.items() if q!='hit'} for k,p in layouts.items()},indent=2)+'\n')
    print(json.dumps(dict(eta4_radius_mm=report['eta4_front_radius_mm'],phase_search=report['grid_phase_search'],summary=report['summary'],custom_profile_count=len(report['edge_profiles'])),indent=2))
