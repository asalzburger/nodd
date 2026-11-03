"""DES043 conserved effective shared services, with disjoint physical cells.

One common trunk includes upstream payload and the current fan's outer travel.
Power/HV packages, optical packages and Ti/CO2 pipes have independent counts.
"""
from collections import defaultdict
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]


def payload(c,s,power_mm=0.,fibre_mm=0.,leaf_tube_mm=0.,bulk_pair_mm=0.):
    gross=math.pi/4*c['power_cable_OD_mm']**2
    copper=2*c['lv_area_per_conductor_mm2']+2*s['service_power_HV_reservation_modules']*c['hv_area_per_conductor_mm2']+c['control_copper_mm2']+c['shield_copper_mm2']
    if copper>=gross:raise ValueError('Power conductors exceed finished cable envelope')
    noncu=gross-copper;solid=c['material']['new_power_non_copper_solid_fraction']
    fibre=math.pi/4*c['fibre_OD_mm']**2
    leaf_inner=c['leaf_pipe_OD_mm']-2*c['leaf_pipe_wall_mm']
    metal=math.pi/4*sum(od**2-di**2 for od,di in zip(c['trunk_pipe_OD_mm'],c['trunk_pipe_ID_mm']))
    fluid=math.pi/4*sum(di**2 for di in c['trunk_pipe_ID_mm'])
    result={'Copper':power_mm*copper,'Polyimide':power_mm*noncu*solid,
            'Air':power_mm*noncu*(1-solid),
            'Titanium':leaf_tube_mm*math.pi/4*(c['leaf_pipe_OD_mm']**2-leaf_inner**2)+bulk_pair_mm*metal,
            'CO2':leaf_tube_mm*math.pi/4*leaf_inner**2+bulk_pair_mm*fluid}
    for material,fraction in s['fibre_volume_fractions'].items():
        result[material]=result.get(material,0)+fibre_mm*fibre*fraction
    return {k:v for k,v in result.items() if v>0}


def add_payload(*items):
    result=defaultdict(float)
    for item in items:
        for material,value in item.items():result[material]+=value
    return dict(result)


def replace(doc,matdoc,entities,recipes,s,c):
    if (c['trunk_mm']!=[717.,781.5,1310.,3500.] or c['collector_mm']!=[244.,781.5,1245.,1310.]
            or c['front_fan_mm']!=[690.,781.5,20.,100.]):
        raise ValueError('Unsupported shared service handoff; requires interface amendment')
    if not 0<s['shared_service_phi_fraction']<=1 or s['service_power_HV_reservation_modules']!=14:
        raise ValueError('Invalid service azimuth or HV reservation')
    if not math.isclose(sum(s['fibre_volume_fractions'].values()),1.) or any(v<0 for v in s['fibre_volume_fractions'].values()):
        raise ValueError('Invalid independent optical package fractions')
    if c['maximum_modules_per_power_feed']!=14 or c['endcap_loops_per_petal']!=2:
        raise ValueError('Power feed and cooling branch contract changed')
    removed=set()
    for detector in doc.findall('./detectors/detector'):
        for piece in list(detector.findall('piece')):
            name=piece.get('name')
            if name.startswith(('short_barrel_collector_','short_barrel_trunk_','short_endcap_fan_','short_endcap_trunk_','long_barrel_trunk_')):
                removed.add(name);detector.remove(piece)
    entities=[e for e in entities if e['name'] not in removed]
    owner=doc.find("./detectors/detector[@name='ShortStripBarrel']")
    endcap=doc.find("./detectors/detector[@name='ShortStripEndcap']")
    if owner is None or endcap is None:raise ValueError('Missing service endpoint detector')
    sectors=[[] for _ in range(12)]
    for layer in owner.findall('layer'):
        staves=layer.findall('stave')
        for stave in staves:
            i=min(11,int(int(stave.get('id'))*12/len(staves)))
            sectors[i].append(float(stave.get('radius').removesuffix('*mm')))
    if [len(x) for x in sectors]!=[25,25,22]*4:
        raise ValueError('Barrel half-stave route count changed')
    discs=sorted((abs(float(d.get('z').removesuffix('*mm'))),int(d.get('side'))) for d in endcap.findall('disc'))
    if len(discs)!=12:raise ValueError('Shared services require all twelve endcap discs')
    endcap_groups=defaultdict(int)
    for entity in entities:
        if entity.get('role')=='sensitive' and entity.get('component')=='short_endcap':
            endcap_groups[(entity['ids']['layer'],entity['ids']['petal'])]+=1
    if len(endcap_groups)!=144 or set(endcap_groups.values())!={33}:
        raise ValueError('Require 33 independently serviced modules in each full endcap petal')
    ec_power=math.ceil(33/c['maximum_modules_per_power_feed'])
    ec_optical=math.ceil(33/c['maximum_modules_per_optical_group'])
    ec_loops=c['endcap_loops_per_petal']
    packing=[]
    for sector,radii in enumerate(sectors):
        B=len(radii)
        power=B+6*ec_power;optical=2*B+6*ec_optical
        banks=math.ceil(B/c['maximum_loops_per_manifold'])+math.ceil(6*ec_loops/c['maximum_loops_per_manifold'])
        demand=power*math.pi/4*c['power_cable_OD_mm']**2+optical*math.pi/4*c['fibre_OD_mm']**2+banks*math.pi/4*sum(d*d for d in c['trunk_pipe_OD_mm'])
        for name,scenario in c['packing'].items():
            rin,rout,_,_=c['trunk_mm'];wall=c['tray_wall_mm']
            capacity=scenario['phi_fraction']*scenario['packing_fraction']*math.pi*((rout-wall)**2-(rin+wall)**2)/12
            fill=scenario['spare_factor']*demand/capacity
            if fill>1:raise ValueError('DES043 shared service packing fails '+name)
            packing.append(dict(sector=sector,scenario=name,fill_ratio=fill,power_feeds=power,optical_groups=optical,bulk_pipe_pairs=banks))
    new=[]; ledger=[];allocated=defaultdict(float);oracle=defaultdict(float);spine=defaultdict(float)
    angle=s['shared_service_phi_fraction']*2*math.pi/12;wall=c['tray_wall_mm']
    ri,ro,z0,z1=c['trunk_mm'];fr0,fr1,fw0,fw1=c['front_fan_mm']
    def piece(name,role,material,side,sector,a,b,r0,r1,constituents=None,**metadata):
        start=(sector+.5)*2*math.pi/12-angle/2
        capacity=angle/2*(r1*r1-r0*r0)*(b-a)
        if min(capacity,b-a,r1-r0)<=0:raise ValueError('Nonpositive service cell')
        ET.SubElement(owner,'piece',name=name,role=role,kind='sector',material=material,u='0*mm',v='0*mm',
            w=f'{side*(a+b)/2:.17g}*mm',rmin=f'{r0:.17g}*mm',rmax=f'{r1:.17g}*mm',
            length=f'{b-a:.17g}*mm',start=f'{start:.17g}*rad',angle=f'{angle:.17g}*rad')
        ent=dict(name=name,role=role,component='shared_short_services',material=material,
            center_mm=[0,0,side*(a+b)/2],volume_mm3=capacity,mass_g=capacity*recipes[material]['density_g_cm3']/1000,
            bounds_rz_mm=[r0,r1,a,b],side=side,sector=sector,**metadata)
        if constituents is not None:ent['constituent_volumes_mm3']=constituents
        new.append(ent)
        return ent
    def cell(label,side,sector,a,b,r0,r1,content,**metadata):
        cap=angle/2*(r1*r1-r0*r0)*(b-a)
        if sum(content.values())>cap*(1+1e-10):raise ValueError('DES043 service payload exceeds physical corridor')
        filled=dict(content);filled['Air']=filled.get('Air',0)+max(0.,cap-sum(content.values()))
        masses={k:v*recipes[k]['density_g_cm3'] for k,v in filled.items() if v>0}
        density=sum(masses.values())/cap
        material=label+'_material';node=ET.SubElement(matdoc,'material',name=material)
        ET.SubElement(node,'D',value=f'{density:.17g}',unit='g/cm3')
        fractions={k:v/sum(masses.values()) for k,v in masses.items()}
        for k,v in fractions.items():ET.SubElement(node,'fraction',n=f'{v:.17g}',ref=k)
        recipes[material]=dict(density_g_cm3=density,composition=fractions,basis='mass_fraction')
        for k,v in content.items():allocated[k]+=v
        return piece(label,'service_cell',material,side,sector,a,b,r0,r1,content,**metadata)
    for side in (-1,1):
        stations=sorted(z for z,signed in discs if signed==side)
        pockets=[(z+fw0,z+fw1) for z in stations]
        if any(a<z0 or b>z1 for a,b in pockets) or any(a[1]>=b[0] for a,b in zip(pockets,pockets[1:])):
            raise ValueError('Overlapping or out-of-trunk fan pockets')
        for sector,radii in enumerate(sectors):
            B=len(radii);prefix=f'DES043_S{side}_P{sector}'
            cr0,cr1,ca,cb=c['collector_mm']
            power_len=sum(cr1-r+math.pi*s['collector_power_bend_radius_mm'] for r in radii)
            pipe_len=2*sum(cr1-r+math.pi*s['collector_pipe_bend_radius_mm'] for r in radii)
            content=payload(c,s,power_len,2*power_len,pipe_len)
            cell(prefix+'_collector',side,sector,ca,cb,cr0+wall,cr1-wall,content,
                 power_feeds=B,optical_groups=2*B,leaf_loops=B)
            for j,r in enumerate((cr0,cr1-wall)):
                piece(prefix+f'_collector_wall{j}','tray','Aluminium',side,sector,ca,cb,r,r+wall)
            breaks=sorted({z0,z1,*[x for pocket in pockets for x in pocket]})
            for index,(a,b) in enumerate(zip(breaks,breaks[1:])):
                mid=(a+b)/2;joined=sum(hi<=a+1e-9 for lo,hi in pockets)
                active=next((j for j,(lo,hi) in enumerate(pockets) if lo<mid<hi),None)
                power=B+ec_power*joined;optical=2*B+ec_optical*joined
                banks=math.ceil(B/c['maximum_loops_per_manifold'])+math.ceil(joined*ec_loops/c['maximum_loops_per_manifold'])
                incoming=payload(c,s,power*(b-a),optical*(b-a),bulk_pair_mm=banks*(b-a))
                fan={}
                if active is not None:
                    fan_length=(ro-c['board_radius_mm'])+math.pi*s['fan_power_bend_radius_mm']
                    leaf_length=(ro-c['cooling_port_radius_mm'])+math.pi*s['fan_pipe_bend_radius_mm']
                    fullfan=payload(c,s,ec_power*fan_length,ec_optical*fan_length,2*ec_loops*leaf_length)
                    fraction=(ri+wall-c['board_radius_mm'])/(ro-c['board_radius_mm'])
                    fan={k:v*(1-fraction) for k,v in fullfan.items()}
                    inner={k:v*fraction for k,v in fullfan.items()}
                    cell(prefix+f'_fan{active}_inner',side,sector,a,b,fr0+wall,ri+wall,inner,
                         source_petal=sector if side>0 else 11-sector,local_power_feeds=3,local_optical_groups=3,leaf_loops=2)
                label=prefix+f'_trunk{index}'
                content=add_payload(incoming,fan)
                cell(label,side,sector,a,b,ri+wall,ro-wall,content,joined_stations=joined,
                    power_feeds=power,optical_groups=optical,bulk_pipe_pairs=banks,
                    current_fan_station=active,upstream_payload_mm3=incoming,current_fan_payload_mm3=fan)
                innerwall=fr0 if active is not None else ri
                piece(label+'_wall0','tray','Aluminium',side,sector,a,b,innerwall,innerwall+wall)
                piece(label+'_wall1','tray','Aluminium',side,sector,a,b,ro-wall,ro)
                ledger.append(dict(side=side,sector=sector,z_mm=[a,b],joined_stations=joined,
                    power_feeds=power,optical_groups=optical,bulk_pipe_pairs=banks,fan_station=active))
            # Independent source route integral, without reading generated cells.
            joins=[z+fw1 for z in stations]
            external=sum(z1-z for z in joins)
            bulk=math.ceil(B/c['maximum_loops_per_manifold'])*(z1-z0)
            bulk+=sum((math.ceil(n*ec_loops/c['maximum_loops_per_manifold'])-math.ceil((n-1)*ec_loops/c['maximum_loops_per_manifold']))*(z1-z)
                      for n,z in enumerate(joins,1))
            straight=payload(c,s,B*(z1-z0)+ec_power*external,2*B*(z1-z0)+ec_optical*external,bulk_pair_mm=bulk)
            collector=payload(c,s,power_len,2*power_len,pipe_len)
            fans=payload(c,s,len(stations)*ec_power*((ro-c['board_radius_mm'])+math.pi*s['fan_power_bend_radius_mm']),
                len(stations)*ec_optical*((ro-c['board_radius_mm'])+math.pi*s['fan_power_bend_radius_mm']),
                len(stations)*2*ec_loops*((ro-c['cooling_port_radius_mm'])+math.pi*s['fan_pipe_bend_radius_mm']))
            for k,v in straight.items():spine[k]+=v
            for k,v in add_payload(straight,collector,fans).items():oracle[k]+=v
    if set(allocated)!=set(oracle) or any(not math.isclose(v,oracle[k],rel_tol=1e-10,abs_tol=1e-5) for k,v in allocated.items()):
        raise ValueError('New service route constituent not conserved through partitioned cells')
    # Source endpoint and physical route counts are independent of cell partition.
    barrel_endpoints=2*sum(map(len,sectors));petals=len(endcap_groups)
    loops=barrel_endpoints+petals*ec_loops
    totals=dict(power_feeds=barrel_endpoints+petals*ec_power,optical_groups=2*barrel_endpoints+petals*ec_optical,
                leaf_loops=loops,physical_boards=barrel_endpoints+petals,
                bulk_pipe_pairs_at_both_end_handoffs=2*sum(math.ceil(len(r)/c['maximum_loops_per_manifold'])+math.ceil(6*ec_loops/c['maximum_loops_per_manifold']) for r in sectors),leaf_ports=2*loops)
    metadata=dict(action='DES043 replace legacy SS collector/fans/trunk; retain one shared tray and cumulative payload',
        design='DES-043',removed_names=sorted(removed),new_placements=len(new),route_totals=totals,
        ledger=ledger,allocated_payload_mm3=dict(allocated),new_route_payload_oracle_mm3=dict(oracle),
        spine_only_payload_mm3=dict(spine),packing=packing,power_HV_reservation_modules=14,
        air='Internal cable air plus unused physical cell air exactly once',
        fan_policy='Inner pocket replaces trunk wall; outer fan payload shares common trunk cell; station joins at datum+100 mm',
        scope=s['scope'])
    return entities+new,[metadata]
