"""Independent IP ray interval intersection with physical tilted faces/circles."""
import math
def interval(lo,hi,origin,direction,normal,bound):
    slope=sum(a*b for a,b in zip(normal,direction))
    delta=bound-sum(a*b for a,b in zip(normal,origin))
    if abs(slope)<1e-15:return (lo,hi) if delta<=1e-10 else (1,0)
    if slope>0:lo=max(lo,delta/slope)
    else:hi=min(hi,delta/slope)
    return lo,hi

def intersections(model,direction,limit=9000):
    active=0.;crossings=0;support=0.
    transverse=math.hypot(*direction[:2])
    if transverse<=0:return dict(active_mm=0.,gap_crossings=0,support_mm=0.)
    wheels={w['wheel']:w for w in model['wheels']}
    for rep in model['replicas']:
        origin=[-sum(a*b for a,b in zip(col,rep['center_mm'])) for col in rep['frame']]
        vector=[sum(a*b for a,b in zip(col,direction)) for col in rep['frame']]
        if abs(origin[0])+abs(origin[1])>1e-8:raise ValueError('Reference requires coaxial IP replicas')
        for p in wheels[rep['wheel']]['pieces']:
            if p['role']!='sensitive':continue
            circle=p['clip_annulus_mm'];lo=max(0,circle['rmin']/transverse);hi=min(limit,circle['rmax']/transverse)
            bounds=[([0,0,1],-p['half_z_mm']),([0,0,-1],-p['half_z_mm']),
                ([1,0,0],min(v[0] for v in p['vertices_mm'])),([-1,0,0],-max(v[0] for v in p['vertices_mm'])),
                (p['lower_face']['normal'],p['lower_face']['bound']),
                ([-v for v in p['upper_face']['normal']],-p['upper_face']['bound'])]
            for normal,bound in bounds:lo,hi=interval(lo,hi,origin,vector,normal,bound)
            if hi>lo+1e-8:active+=hi-lo;crossings+=1
    for p in model['passive']:
        if p['role']!='wheel_support':continue
        d=p['dimensions_mm'];lo=max(0,d['rmin']/transverse);hi=min(limit,d['rmax']/transverse)
        origin=[-sum(a*b for a,b in zip(col,p['center_mm'])) for col in p['frame']]
        vector=[sum(a*b for a,b in zip(col,direction)) for col in p['frame']]
        for n,b in [([0,0,1],-d['length']/2),([0,0,-1],-d['length']/2)]:lo,hi=interval(lo,hi,origin,vector,n,b)
        support+=max(0,hi-lo)
    return dict(active_mm=active,gap_crossings=crossings,support_mm=support)
