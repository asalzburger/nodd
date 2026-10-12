"""Source-derived sensor and die geometry for legacy and transverse-periphery modules."""
import math


def describe(body, patches, models, layout):
    local=[tuple(sum((p['center_mm'][j]-body['center_mm'][j])*body[axis][j] for j in range(3))
                 for axis in ('u','v')) for p in patches]
    uc,vc=(sum(p[i] for p in local)/len(local) for i in range(2))
    active=[max(x[i]+p['half_'+axis+'_mm'] for x,p in zip(local,patches))-
            min(x[i]-p['half_'+axis+'_mm'] for x,p in zip(local,patches)) for i,axis in enumerate(('u','v'))]
    study=layout['metadata'].get('pixel_z_study')
    rotated=study is not None
    if rotated:
        spec=study['shapes'][body['layer_id']]
        su,sv=spec['sensor_phi'],spec['sensor_z']
        if any(abs(active[i]-spec[key])>1e-8 for i,key in enumerate(('active_phi','active_z'))):
            raise ValueError('Selected finite patches disagree with the source module shape')
    else:
        su,sv=(x+2*models['guard_mm'] for x in active)
    if any(not math.isclose(p['sensor_area_mm2'],su*sv,rel_tol=1e-10) for p in patches):
        raise ValueError('Physical sensor area disagrees with source layout')
    if abs(uc)+su/2>body['half_u_mm']+1e-9 or abs(vc)+sv/2>body['half_v_mm']+1e-9:
        raise ValueError('Sensor substrate exceeds its source occupied body')
    periphery=models['approximate_die_v_mm']-models['chip_active_v_mm']
    dies=[]
    for u,v in local:
        if rotated:
            sign=-1 if len(patches)==1 or u<uc else 1
            dies.append(dict(u=u+sign*periphery/2,v=v,width=models['approximate_die_v_mm'],length=models['approximate_die_u_mm']))
        else:
            sign=1 if len(patches)==1 or v>vc else -1
            dies.append(dict(u=u,v=v+sign*periphery/2,width=models['approximate_die_u_mm'],length=models['approximate_die_v_mm']))
    return dict(local=local,u=uc,v=vc,width=su,length=sv,dies=dies,periphery_axis='u' if rotated else 'v')


def stave_frame(body):
    """Orientation is independent of the tangentially translated origin."""
    phi=math.atan2(body['n'][1],body['n'][0])
    radius=sum(body['center_mm'][i]*body['n'][i] for i in range(2))
    offset=sum(body['center_mm'][i]*body['u'][i] for i in range(2))
    return phi,radius,offset
