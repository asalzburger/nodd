"""DES040 finite warm support prototype, with actual hollow material walls.

Geometry/contact connectivity and self-mass are distinct from structural
qualification. No case walls, coil masses or altered magnetic sources appear.
"""
from __future__ import annotations
import copy
import json
import math
from pathlib import Path
import numpy as np
from . import geometry as geo


def _cross2(a,b):
    return a[0]*b[1]-a[1]*b[0]


def _proposal(config):
    if 'frame' in config and 'barrel_interfaces' in config:
        return config
    if isinstance(config,str) or isinstance(config,Path):
        return _proposal(json.loads(Path(config).read_text()))
    p=Path(config['support_input'])
    if not p.is_absolute(): p=Path(__file__).resolve().parents[2]/p
    return json.loads(p.read_text())


def _basis(phi):
    a=math.radians(phi)
    return np.array([math.cos(a),math.sin(a),0.]),np.array([-math.sin(a),math.cos(a),0.])


def _beam(identifier,start,end,width,height,axis0,wall,material,density,category,**extra):
    a,b=np.asarray(start,float),np.asarray(end,float);n=(b-a)/np.linalg.norm(b-a)
    u=np.asarray(axis0,float);u=u-n*np.dot(u,n);u/=np.linalg.norm(u);v=np.cross(n,u)
    out=geo.prism(identifier,'support',(a+b)/2,np.column_stack((u,v,n)),
                  [[-width/2,-height/2],[width/2,-height/2],[width/2,height/2],[-width/2,height/2]],
                  np.linalg.norm(b-a),shape='rhs' if wall else 'solid',wall_m=wall,
                  material=material,density_kg_m3=density,category=category,
                  endpoints_m=[a.tolist(),b.tolist()],section_m=[width,height],**extra)
    return out


def build_supports(config):
    """Return finite outer envelopes, material-wall rules and declared ports.

    The graph is *declared* until validate_supports derives actual material
    contacts. config may be DES040 design.json or the retained support proposal.
    """
    p=_proposal(config);f=p['frame'];N=int(f['folds']);delta=math.pi/N
    a=f['outer_polygon_apothem_m'];R=a/math.cos(delta)
    densities={k:v['density_kg_m3'] for k,v in p['materials'].items()}
    members=[];ports=[];ground=[]
    def beam(identifier,start,end,w,h,u,wall,mat,category,**kw):
        body=_beam(identifier,start,end,w,h,u,wall,mat,densities[mat],category,**kw)
        members.append(body);return body
    def ring(prefix,z,apothem,w,h,t,mat,category):
        # Exact mitered polygon sectors: all seams touch, none overlap in volume.
        for k in range(N):
            er,ep=_basis(k*360/N);lo,hi=apothem-w/2,apothem+w/2
            body=geo.prism(f'{prefix}/E{k:02d}','support',[0,0,z],np.column_stack((er,ep,[0,0,1])),
                [[lo,-lo*math.tan(delta)],[hi,-hi*math.tan(delta)],
                 [hi,hi*math.tan(delta)],[lo,lo*math.tan(delta)]],h,
                shape='ring_rhs',wall_m=t,material=mat,density_kg_m3=densities[mat],
                category=category,ring_apothem_m=apothem,ring_radial_m=w,
                ring_half_sector_rad=delta,ring_z_m=z)
            members.append(body)
    sec=f['outer_portal_section']
    for i,z in enumerate(f['main_portal_z_m']):
        ring(f'PORTAL{i}',z,a,sec['radial_m'],sec['axial_m'],sec['wall_m'],sec['material'],'outer_portal')
    for i,z in enumerate(f['carrier_portal_z_m']):
        ring(f'CARRIER{i}',z,a,sec['radial_m'],sec['axial_m'],sec['wall_m'],sec['material'],'outer_carrier')
    st=f['longitudinal_girders']
    for k in range(N):
        er,_=_basis(15+k*360/N)
        beam(f'GIRDER{k:02d}',R*er+[0,0,st['z_min_m']],R*er+[0,0,st['z_max_m']],
             st['radial_m'],st['tangent_m'],er,st['wall_m'],st['material'],'longitudinal_girder')
    br=f['diagonals']
    for i,(za,zb) in enumerate(br['intervals_z_m']):
        hand=1 if i%2==0 else -1
        for k in range(N):
            phi=15+k*360/N;er0,_=_basis(phi);er1,_=_basis(phi+hand*360/N);roll,_=_basis(phi+hand*180/N)
            beam(f'BRACE{i}-{k:02d}',R*er0+[0,0,za],R*er1+[0,0,zb],*br['section_outside_m'],roll,
                 br['wall_m'],br['material'],'diagonal_brace')
    e=p['endcap_interfaces'];inner=e['inner_carrier_ring'];sp=e['radial_spokes']
    for side,label in [(-1,'M'),(1,'P')]:
        for face in ['front','rear']:
            z=side*e[face]['abs_carrier_z_m'];prefix=f'ECT{label}-{face}'
            ring(prefix+'/INNER',z,inner['apothem_m'],inner['radial_m'],inner['axial_m'],
                 inner['wall_m'],inner['material'],'inner_carrier')
            for k in range(N):
                er,ep=_basis(15+k*360/N)
                beam(f'{prefix}/SPOKE{k:02d}',sp['r_min_m']*er+[0,0,z],sp['r_max_m']*er+[0,0,z],
                     sp['tangent_m'],sp['axial_m'],ep,sp['wall_m'],sp['material'],'carrier_spoke')
                case=e['case_ids']['plus' if side>0 else 'minus'][k]
                for j,r in enumerate(e['port_radii_m']):
                    skin=side*e[face]['abs_case_skin_z_m']
                    extent=sorted(side*x for x in e[face]['abs_lug_extent_z_m'])
                    end=min(extent) if face=='front' and side>0 else max(extent)
                    # Select the endpoint opposite the specified case skin.
                    end=extent[0] if abs(extent[-1]-skin)<1e-10 else extent[-1]
                    point=r*er+[0,0,skin];tip=r*er+[0,0,end]
                    ident=f'{prefix}/LUG{k:02d}-{j}'
                    body=beam(ident,point,tip,*e['lug_cross_section_radial_tangent_m'],er,0.,'Al_proxy','case_lug',case_id=case)
                    ports.append(dict(id=ident+'/PORT',case_id=case,member_id=ident,
                        group='endcap_plus' if side>0 else 'endcap_minus',coil_index=k,
                        point_m=point.tolist(),outward_normal=((tip-point)/np.linalg.norm(tip-point)).tolist(),
                        patch_axes=np.asarray(body['basis'])[:,:2].tolist(),section_m=body['section_m']))
    b=p['barrel_interfaces']
    for k,case in enumerate(b['case_ids']):
        er,ep=_basis(k*360/N)
        for j,z in enumerate(b['z_ports_m']):
            point=b['case_contact_r_m']*er+[0,0,z];tip=b['portal_contact_r_m']*er+[0,0,z]
            ident=f'BT-LUG{k:02d}-{j}'
            body=beam(ident,point,tip,b['lug_tangent_m'],b['lug_axial_m'],ep,0.,b['material'],'case_lug',case_id=case)
            ports.append(dict(id=ident+'/PORT',case_id=case,member_id=ident,group='barrel',coil_index=k,
                point_m=point.tolist(),outward_normal=er.tolist(),patch_axes=np.asarray(body['basis'])[:,:2].tolist(),section_m=body['section_m']))
    feet=p['feet']
    for ix,x in enumerate(feet['x_centres_m']):
        for iz,z in enumerate(feet['z_centres_m']):
            prefix=f'FOOT{ix}-{iz}'
            for name in ['Al_shoe','SS_cap','SS_column','SS_baseplate']:
                q=feet[name];low,high=q['y_extent_m']
                if name=='SS_column':w,h=q['outside_xz_m'];wall=q['wall_m']
                else:w,_,h=q['size_xyz_m'];wall=0.
                beam(prefix+'/'+name,[x,low,z],[x,high,z],w,h,[1,0,0],wall,q['material'],'foot_'+name)
            ground.append(dict(id=prefix+'/GROUND',member_id=prefix+'/SS_baseplate',floor_y_m=feet['floor_plane_y_m']))
    case_ids=b['case_ids']+e['case_ids']['plus']+e['case_ids']['minus']
    return dict(members=members,ports=ports,ground=ground,case_ids=case_ids,
                connections=[[x['case_id'],x['member_id']] for x in ports],
                graph=dict(validated=False,nodes=case_ids+[x['id'] for x in members]+[x['id'] for x in ground]),
                choices=p,limits=p['unresolved'],status='PROTOTYPE: declared contacts require material-wall validation')


def material_parts(member):
    """Partition each hollow member into four nonoverlapping solid-wall prisms."""
    body=member;t=float(body.get('wall_m',0));base={k:v for k,v in body.items() if k not in ['id','kind','origin_m','basis','vertices_m','depth_m']}
    if t==0:return [dict(body,parent_id=body['id'])]
    if t<=0:raise ValueError('positive wall thickness required')
    out=[]
    def add(i,vertices,depth=None,shift=0):
        q=np.asarray(body['basis']);o=np.asarray(body['origin_m'])+shift*q[:,2]
        out.append(geo.prism(body['id']+f'/W{i}',body['kind'],o,q,vertices,
                            body['depth_m'] if depth is None else depth,
                            **dict(base,shape='solid',wall_m=0,parent_id=body['id'])))
    if body['shape']=='ring_rhs':
        a=body['ring_apothem_m'];w=body['ring_radial_m'];lo,hi=a-w/2,a+w/2;d=body['ring_half_sector_rad'];H=body['depth_m']
        if 2*t>=min(w,H):raise ValueError('wall fills hollow ring section')
        def quad(a,b):return [[a,-a*math.tan(d)],[b,-b*math.tan(d)],[b,b*math.tan(d)],[a,a*math.tan(d)]]
        add(0,quad(lo,hi),t,-H/2+t/2);add(1,quad(lo,hi),t,H/2-t/2)
        add(2,quad(lo,lo+t),H-2*t);add(3,quad(hi-t,hi),H-2*t)
    else:
        p=np.asarray(body['vertices_m']);lo=p.min(axis=0);hi=p.max(axis=0)
        if np.any(hi-lo<=2*t):raise ValueError('wall fills hollow beam section')
        def rect(x0,x1,y0,y1):return [[x0,y0],[x1,y0],[x1,y1],[x0,y1]]
        add(0,rect(lo[0],lo[0]+t,lo[1],hi[1]));add(1,rect(hi[0]-t,hi[0],lo[1],hi[1]))
        add(2,rect(lo[0]+t,hi[0]-t,lo[1],lo[1]+t));add(3,rect(lo[0]+t,hi[0]-t,hi[1]-t,hi[1]))
    return out


def _sample_prism(body,n,rng):
    p=np.asarray(body['vertices_m']);a=np.array([abs(_cross2(p[1]-p[0],p[2]-p[0])),abs(_cross2(p[2]-p[0],p[3]-p[0]))])
    tri=rng.choice(2,n,p=a/a.sum());u=rng.random(n);v=rng.random(n);take=u+v>1;u[take]=1-u[take];v[take]=1-v[take]
    v1=np.where(tri[:,None]==0,p[1],p[2]);v2=np.where(tri[:,None]==0,p[2],p[3])
    xy=p[0]+u[:,None]*(v1-p[0])+v[:,None]*(v2-p[0])
    local=np.column_stack((xy,rng.uniform(-body['depth_m']/2,body['depth_m']/2,n)))
    return local@np.asarray(body['basis']).T+body['origin_m']


def _multiplicity(parts,points):
    order=np.argsort(points[:,0]);p=points[order];count=np.zeros(len(p),np.uint16)
    for body in parts:
        lo,hi=geo.aabb(body);i,j=np.searchsorted(p[:,0],[lo[0]-1e-10,hi[0]+1e-10]);sub=p[i:j]
        mask=((sub[:,1:]>=lo[1:]-1e-10)&(sub[:,1:]<=hi[1:]+1e-10)).all(axis=1)
        ids=np.flatnonzero(mask)
        if len(ids):count[i+ids]+=geo.contains(body,sub[ids])
    result=np.empty_like(count);result[order]=count;return result


def support_mass(members,samples=262144,seed=40036):
    """Gross stock and unique material union via unbiased multiplicity sampling.

    Sample the volume-weighted mixture of actual solid wall parts. At a sampled
    point, 1/k removes k-fold welded overlaps. Errors are Monte Carlo standard
    errors, not density/geometry/engineering uncertainties.
    """
    if samples<2:raise ValueError('at least two samples per material required')
    parts=[p for m in members for p in material_parts(m)];rng=np.random.default_rng(seed);result={}
    for mat in sorted({x['material'] for x in parts}):
        pp=[x for x in parts if x['material']==mat];vol=np.array([geo.volume(x) for x in pp]);gross=float(vol.sum())
        ids=rng.choice(len(pp),samples,p=vol/gross);points=np.empty((samples,3))
        for i,body in enumerate(pp):
            take=np.flatnonzero(ids==i)
            if len(take):points[take]=_sample_prism(body,len(take),rng)
        k=_multiplicity(pp,points)
        if np.any(k==0):raise AssertionError('sample escaped material part')
        values=1./k;union=gross*float(values.mean());err=gross*float(values.std(ddof=1))/math.sqrt(samples)
        rho=float(pp[0]['density_kg_m3'])
        if any(x['density_kg_m3']!=rho for x in pp):raise ValueError('one density required per material ID')
        result[mat]=dict(gross_stock_volume_m3=gross,unique_union_volume_m3=union,
                        union_volume_standard_error_m3=err,gross_stock_mass_kg=gross*rho,
                        unique_mass_kg=union*rho,mass_standard_error_kg=err*rho,
                        density_kg_m3=rho,maximum_sampled_multiplicity=int(k.max()))
    return dict(method='importance sample actual wall volumes; unique volume = gross * mean(1/multiplicity)',
                samples_per_material=samples,seed=seed,materials=result,
                gross_stock_mass_kg=sum(x['gross_stock_mass_kg'] for x in result.values()),
                unique_mass_kg=sum(x['unique_mass_kg'] for x in result.values()),
                combined_statistical_standard_error_kg=math.sqrt(sum(x['mass_standard_error_kg']**2 for x in result.values())),
                scope='frame/feet stock only; no case, cold magnet or chamber mass; no strength qualification')


def _clip_polygon(subject,clip,tolerance=1e-10):
    out=[np.asarray(x,float) for x in subject]
    for a,b in zip(clip,np.roll(clip,-1,axis=0)):
        edge=b-a;old=out;out=[]
        if not old:break
        def side(p):return float(_cross2(edge,p-a))
        previous=old[-1];dp=side(previous)
        for current in old:
            dc=side(current)
            if (dp>=-tolerance)!=(dc>=-tolerance):out.append(previous+(current-previous)*dp/(dp-dc))
            if dc>=-tolerance:out.append(current)
            previous,dp=current,dc
    return np.asarray(out)


def _face_contact_area(a,b,tolerance=1e-8):
    va,vb=geo.vertices3(a),geo.vertices3(b);faces=[[0,3,2,1],[4,5,6,7]]+[[i,(i+1)%4,(i+1)%4+4,i+4] for i in range(4)]
    best=0.
    for ia in faces:
        aa=va[ia];u=aa[1]-aa[0];u/=np.linalg.norm(u);normal=np.cross(u,aa[2]-aa[0]);normal/=np.linalg.norm(normal);v=np.cross(normal,u)
        clip=np.column_stack(((aa-aa[0])@u,(aa-aa[0])@v))
        if geo.polygon_area(clip)<0:clip=clip[::-1]
        for ib in faces:
            bb=vb[ib]
            if np.max(np.abs((bb-aa[0])@normal))>tolerance:continue
            sub=np.column_stack(((bb-aa[0])@u,(bb-aa[0])@v))
            if geo.polygon_area(sub)<0:sub=sub[::-1]
            poly=_clip_polygon(sub,clip)
            if len(poly)>=3:best=max(best,abs(geo.polygon_area(poly)))
    return best


def _contact(parts_a,parts_b):
    for a in parts_a:
        for b in parts_b:
            if not geo.intersects(a,b):continue
            # Strictly shrink one prism to distinguish shared stock from a face.
            if geo.intersects(a,b,clearance=-1e-7):
                return dict(kind='overlapping_material',parts=[a['id'],b['id']])
            area=_face_contact_area(a,b)
            if area>1e-10:return dict(kind='material_face_contact',area_m2=area,parts=[a['id'],b['id']])
    return None


def _port_check(port,body,magnetic):
    from tools.toroid_prototype.geometry import coil_mask,group_mask
    c=np.asarray(port['point_m']);axes=np.asarray(port['patch_axes']);n=np.asarray(port['outward_normal']);w,h=port['section_m']
    points=np.array([c+x*w/2*axes[:,0]+y*h/2*axes[:,1] for x in [-1,0,1] for y in [-1,0,1]])
    group=copy.deepcopy(magnetic['coil_groups'][port['group']]);group['phi_offset_deg']+=port['coil_index']*360/magnetic['folds']
    warm=magnetic['warm'];on=group_mask(points,group,1,warm['normal_m'],warm['tangent_m'])
    inward=group_mask(points-1e-6*n,group,1,warm['normal_m'],warm['tangent_m'])
    outward=group_mask(points+1e-6*n,group,1,warm['normal_m'],warm['tangent_m'])
    endface=geo.contains(body,points)
    return dict(valid=bool(on.all() and inward.all() and not outward.any() and endface.all()),
                skin_samples=9,on_skin=bool(on.all()),inward_occupied=bool(inward.all()),
                outward_clear=bool(not outward.any()),actual_lug_face=bool(endface.all()),
                scope='declared warm-skin interface; no invented case wall or pressure-boundary qualification')


def _lug_warm_certificate(body,port,magnetic):
    """Prove a lug lies outside its entire assembly's supporting skin plane.

    A centre/face sample alone would not prove the rest of a finite lug clear.
    The selected assembly is bounded analytically in the outward normal, and
    every remaining assembly uses the ordinary full-volume distance proof.
    """
    n=np.asarray(port['outward_normal']);point=np.asarray(port['point_m'])
    group=magnetic['coil_groups'][port['group']];a=magnetic['warm']['normal_m']/2;b=magnetic['warm']['tangent_m']/2
    upper=[]
    for k in range(magnetic['folds']):
        er,ep=_basis(group['phi_offset_deg']+k*360/magnetic['folds'])
        radial=float(n@er);tangent=float(n@ep)
        r=(group['center_r_m']+group['half_r_m']+a if radial>=0 else group['center_r_m']-group['half_r_m']-a)
        upper.append(radial*r+abs(tangent)*b+n[2]*group['center_z_m']+abs(n[2])*(group['half_z_m']+a))
    plane=float(n@point);support=max(upper)
    own=(abs(support-plane)<1e-8 and np.min(geo.vertices3(body)@n)>=plane-1e-10)
    other=copy.deepcopy(magnetic);other['coil_groups']={k:v for k,v in magnetic['coil_groups'].items() if k!=port['group']}
    proof=(geo.certify_coil_clear(body,other,clearance=0.,resolution=.01,width='warm')
           if other['coil_groups'] else dict(clear=True,reason='no other assemblies'))
    return dict(clear=bool(own and proof['clear']),reason='analytic assembly supporting-plane and other-assembly volume proof',
                assembly_support_plane_m=support,port_plane_m=plane,entire_lug_outward=bool(own),other_groups=proof)


def validate_supports(model,magnetic_config,check_coils=True):
    """Material-contact graph, positive-area skin ports, ground and coil checks."""
    members=model['members'];byid={x['id']:x for x in members};parts={x['id']:material_parts(x) for x in members}
    expected=model['choices'];bt=expected['barrel_interfaces'];ec=expected['endcap_interfaces']
    expected_cases=bt['case_ids']+ec['case_ids']['plus']+ec['case_ids']['minus']
    port_counts={case:sum(x['case_id']==case for x in model['ports']) for case in expected_cases}
    count_checks=dict(unique_member_ids=len(byid)==len(members),
                      unique_port_ids=len({x['id'] for x in model['ports']})==len(model['ports']),
                      exact_case_ids=sorted(model['case_ids'])==sorted(expected_cases),
                      exact_ground_count=len(model['ground'])==expected['feet']['count'],
                      expected_port_counts=all(port_counts[x]==(bt['ports_per_case'] if x in bt['case_ids'] else ec['ports_per_case']) for x in expected_cases))
    bounds=np.array([geo.aabb(x) for x in members]);contacts=[];edges=[];cross_material=[]
    for i,a in enumerate(members):
        mask=((bounds[i+1:,0]<=bounds[i,1]+1e-9)&(bounds[i+1:,1]>=bounds[i,0]-1e-9)).all(axis=1)
        for j in np.flatnonzero(mask)+i+1:
            b=members[j];contact=_contact(parts[a['id']],parts[b['id']])
            if contact:
                record=dict(members=[a['id'],b['id']],**contact);contacts.append(record);edges.append(record['members'])
                if a['material']!=b['material'] and contact['kind']=='overlapping_material':cross_material.append(record)
    port_checks=[]
    for port in model['ports']:
        check=_port_check(port,byid[port['member_id']],magnetic_config);port_checks.append(dict(id=port['id'],**check))
        if check['valid']:edges.append([port['case_id'],port['member_id']])
    ground_checks=[]
    for gr in model['ground']:
        body=byid[gr['member_id']];vv=geo.vertices3(body);floor=gr['floor_y_m']
        bottom=vv[np.isclose(vv[:,1],floor,atol=1e-9)];area=0.
        if len(bottom)==4:
            xz=bottom[:,[0,2]];order=np.argsort(np.arctan2(xz[:,1]-xz[:,1].mean(),xz[:,0]-xz[:,0].mean()));area=abs(geo.polygon_area(xz[order]))
        valid=area>1e-10 and vv[:,1].min()>=floor-1e-9
        ground_checks.append(dict(id=gr['id'],valid=bool(valid),contact_area_m2=area))
        if valid:edges.append([gr['id'],gr['member_id']])
    components=geo.connected_components(edges);groundids={x['id'] for x in model['ground']}
    supported=set()
    for comp in components:
        if groundids.intersection(comp):supported.update(comp)
    ungrounded_cases=sorted(set(model['case_ids'])-supported);ungrounded_members=sorted(set(byid)-supported)
    coil_checks=[]
    if check_coils:
        ports_by_member={x['member_id']:x for x in model['ports']}
        for body in members:
            record=dict(id=body['id'])
            for width in ['pack','cold']:
                # The shared root certificate accepts a chosen source width.
                record[width]=geo.certify_coil_clear(body,magnetic_config,clearance=0.,resolution=.01,width=width)
            if 'case_id' not in body:
                record['warm']=geo.certify_coil_clear(body,magnetic_config,clearance=0.,resolution=.01,width='warm')
            else:record['warm']=_lug_warm_certificate(body,ports_by_member[body['id']],magnetic_config)
            coil_checks.append(record)
    failed_coils=[x['id'] for x in coil_checks if not all(x[w]['clear'] for w in ['pack','cold','warm'])]
    valid=(all(count_checks.values()) and not ungrounded_cases and not ungrounded_members and not cross_material and
           all(x['valid'] for x in port_checks+ground_checks) and not failed_coils)
    result=dict(valid=valid,member_count=len(members),material_part_count=sum(map(len,parts.values())),
                case_count=len(model['case_ids']),port_count=len(model['ports']),ground_count=len(model['ground']),
                contact_count=len(contacts),contacts=contacts,port_checks=port_checks,ground_checks=ground_checks,
                count_checks=count_checks,ports_per_case=port_counts,
                graph_edges=edges,components=components,ungrounded_cases=ungrounded_cases,
                ungrounded_members=ungrounded_members,cross_material_penetrations=cross_material,
                coil_checks=coil_checks,failed_coil_checks=failed_coils,
                scope='actual material connectivity and finite-volume separation only; no force/stiffness/pressure qualification')
    model['connections']=edges;model['graph']=dict(validated=valid,edges=edges,components=components)
    return result
