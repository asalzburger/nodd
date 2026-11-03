"""DES043 adapter for the unchanged DES020 barrel factory (all lengths mm).

The historical exporter supplies placements, supports, pipes and flex wraps.
Only this adapter replaces the module stack/lands and cuts actual cold windows.
"""
from collections import Counter
import math
import xml.etree.ElementTree as ET


def number(node, key):
    return float(node.get(key).removesuffix('*mm').removesuffix('*rad'))


def volume(kind, dims):
    if kind in ('box', 'shoe'):
        return dims['sx'] * dims['sy'] * dims['sz']
    if kind in ('tube', 'sector'):
        return dims.get('angle', 2*math.pi)/2 * (dims['rmax']**2-dims['rmin']**2)*dims['length']
    if kind == 'torus':
        return dims['angle']*math.pi*dims['major']*(dims['rmax']**2-dims['rmin']**2)
    raise ValueError('Unsupported native primitive '+kind)


def budget(entity, node, recipes):
    """Primitive volumes are exact; intersecting/outside CSG cuts are bounded."""
    dims = {k: number(node, k) for k in ('sx','sy','sz','rmin','rmax','length','start','angle','major') if node.get(k) is not None}
    gross = volume(node.get('kind'), dims)
    cuts = len(node.findall('cut'))
    entity.update(kind=node.get('kind'), dimensions_mm=dims, cuts=cuts)
    density = recipes[entity['material']]['density_g_cm3']
    if cuts:
        entity.pop('volume_mm3', None); entity.pop('mass_g', None)
        entity.update(volume_bounds_mm3=[0., gross], mass_bounds_g=[0., gross*density/1000],
                      mass_policy='Bounded CSG; no sum-of-full-cuts or stochastic Capacity exactness claim')
    else:
        entity.update(volume_mm3=gross, mass_g=gross*density/1000)


def adapt(doc, expected, c, baseline, layout):
    by_name = {e['name']: e for e in expected['entities']}
    removed = set(); added = []; probes = []
    detector = doc.find('./detectors/detector')
    old_module_roles = {'interconnect','readout','module_passive'}
    native, thermal = c['native_module'], c['thermal']
    if (thermal['barrel_pad_mm'] != [20.,64.] or thermal['barrel_pad_u_mm'] != 12.
            or thermal['barrel_pad_count'] != 2 or baseline['tube_offset_u_mm'] != 12.):
        raise ValueError('Unsupported barrel saddle geometry; amend finite interface assessment')
    if thermal['ASIC_tiles'] != len(thermal['ASIC_centres_uv_mm']) or thermal['ASIC_tiles'] != 2:
        raise ValueError('Require two explicitly placed ASIC tiles')
    material = doc.find('./readouts/readout/segmentation')
    material.set('grid_size_y','2*mm'); material.set('offset_y','1*mm')
    expected['cell_mm'] = c['pitch_mm']
    recipes = expected['materials']
    recipes['InsulatingTIM'] = dict(density_g_cm3=c['material']['TIM_density_upper_g_cm3'],
        composition={'Epoxy':1.}, basis='mass_fraction')

    for layer in detector.findall('layer'):
        for stave in layer.findall('stave'):
            name=stave.get('name'); phi=number(stave,'phi'); radius=number(stave,'radius')
            tilt=number(stave,'tilt') if stave.get('tilt') else 0.
            angle=phi+tilt
            def transform(point):
                u,v,w=point
                return [radius*math.cos(phi)-u*math.sin(angle)+w*math.cos(angle),
                        radius*math.sin(phi)+u*math.cos(angle)+w*math.sin(angle),v]
            def piece(parent, label, role, mat, point, size, origin=(0.,0.,0.)):
                node=ET.SubElement(parent,'piece',name=label,kind='box',role=role,material=mat,
                    **{k:f'{x:.17g}*mm' for k,x in zip(('u','v','w'),point)},
                    **{k:f'{x:.17g}*mm' for k,x in zip(('sx','sy','sz'),size)})
                ent=dict(name=label,role=role,material=mat,
                         center_mm=transform([x+y for x,y in zip(point,origin)]))
                added.append(ent); by_name[label]=ent
                return node,ent
            def cut(node, point, size):
                ET.SubElement(node,'cut',kind='box',
                    **{k:f'{x:.17g}*mm' for k,x in zip(('u','v','w'),point)},
                    **{k:f'{x:.17g}*mm' for k,x in zip(('sx','sy','sz'),size)})
            supports=[]
            for node in list(stave.findall('piece')):
                ent=by_name[node.get('name')]
                if ent['role']=='thermal_pickup':
                    stave.remove(node);removed.add(ent['name'])
                if node.get('name').endswith(('front_skin','front_glue','core')):
                    supports.append(node)
                if ent['role']=='power_bus' and node.get('material')=='Copper':
                    node.set('sz',f"{c['rail_thickness_mm']}*mm")
                    node.set('sx',f"{c['barrel_rail_width_mm']}*mm")
            pipes=[node for node in stave.findall('piece') if node.get('role') in ('cooling_tube','cooling_bend')]
            for module in stave.findall('module'):
                mn=module.get('name'); z=number(module,'z');lift=number(module,'lift')
                origin=(0.,z,lift)
                for node in list(module.findall('piece')):
                    if by_name[node.get('name')]['role'] in old_module_roles:
                        removed.add(node.get('name')); module.remove(node)
                for label,role,mat in [('bumps','interconnect','BumpFixture'),('redistribution','redistribution','SignalFlex'),
                        ('spreader','spreader','Graphite'),('TIM','TIM','InsulatingTIM'),('backing','backing','CFRP')]:
                    low,high=native[label+'_w_mm']
                    node,ent=piece(module,mn+'_'+label,role,mat,[0,0,(low+high)/2],[48,96,high-low],origin)
                    if label=='backing':
                        for sign in (-1,1):
                            cut(node,[sign*thermal['barrel_pad_u_mm'],0,0],[20.1,64.1,.4])
                            probes.append(dict(name=ent['name'],point_mm=[sign*12,0,0],inside=False,reason='Barrel backing window'))
                        probes.append(dict(name=ent['name'],point_mm=[0,40,0],inside=True,reason='Barrel backing retained'))
                for index,(u,v) in enumerate(thermal['ASIC_centres_uv_mm']):
                    for label,role,mat in [('ASIC','readout','Silicon'),('ASIC_glue','ASIC_glue','Epoxy')]:
                        low,high=native[label+'_w_mm']
                        piece(module,mn+f'_{label}{index}',role,mat,[u,v,(low+high)/2],
                              [*thermal['ASIC_tile_mm'][:2],high-low],origin)
                for sign in (-1,1):
                    u=sign*thermal['barrel_pad_u_mm'];bottom=native['insert_bottom_w_mm'];top=lift+native['TIM_w_mm'][0]
                    if top-bottom>thermal['maximum_pickup_height_mm']:
                        raise ValueError('Barrel insert exceeds thermal path bound')
                    middle=(bottom+top)/2
                    node,ent=piece(stave,mn+f'_direct_pickup{sign}','thermal_pickup','Graphite',[u,z,middle],
                                   [*thermal['barrel_pad_mm'],top-bottom])
                    ent['height_mm']=top-bottom
                    # Only actual straight legs intersect these lands: torus is
                    # >=16 mm from origin; closest land starts12.8 mm, so include
                    # the finite bend as well whenever its envelope can touch.
                    for pipe in pipes:
                        pu,pv,pw=(number(pipe,k) for k in ('u','v','w'))
                        if pipe.get('kind')=='tube':
                            if abs(pu-u)>thermal['barrel_pad_mm'][0]/2+1.25:continue
                            if abs(pv-z)>number(pipe,'length')/2+32+1.25:continue
                        elif abs(pv-z)>number(pipe,'major')+32+1.25:continue
                        attrs={key:value for key,value in pipe.attrib.items() if key in ('kind','rmin','rmax','length','major','start','angle')}
                        attrs.update(rmin='0*mm',u=f'{pu-u:.17g}*mm',v=f'{pv-z:.17g}*mm',w=f'{pw-middle:.17g}*mm')
                        ET.SubElement(node,'cut',**attrs)
                    side=1 if z>0 else -1
                    pipe=next(p for p in pipes if p.get('kind')=='tube' and abs(number(p,'u')-u)<1e-9 and number(p,'v')*side>0)
                    if not baseline['loop_start_mm']<abs(z)<baseline['stave_half_length_mm']:
                        raise ValueError('Barrel centre-of-land witness misses finite straight pipe')
                    for distance,inside in ((1.24,False),(1.26,True)):
                        probes.append(dict(name=ent['name'],point_mm=[0,0,native['pipe_centre_w_mm']+distance-middle],inside=inside,reason='Barrel finite pipe saddle'))
                        # Tube's factory local rotation is Rx(pi/2).
                        probes.append(dict(name=pipe.get('name'),point_mm=[0,distance,-(z-number(pipe,'v'))],inside=not inside,reason='Barrel titanium surface'))
                    for support in supports:
                        w=number(support,'w');thick=number(support,'sz');low=w-thick/2;high=w+thick/2
                        lo=max(bottom-.05,low-.1);hi=high+.1
                        cut(support,[u,z,(lo+hi)/2-w],[20.1,64.1,hi-lo])
                        probes.append(dict(name=support.get('name'),point_mm=[u,z,max(bottom+.1,low+.01)-w],inside=False,reason='Barrel direct cold window'))
            for node in stave.findall('.//piece'):
                budget(by_name[node.get('name')],node,recipes)
    # Newly added names deliberately reuse old stack labels.
    expected['entities']=[e for e in expected['entities'] if e['name'] not in removed]+added
    expected['counts']=dict(Counter(e['role'] for e in expected['entities']))
    expected['shape_probes']=probes
    expected.pop('material_totals',None)
    expected['mass_policy']='Exact primitive budget; bounded intersecting CSG. No complete native mass claim.'
    return expected
