"""DES029 deterministic plate/frame ownership and rectangular cassette packing."""
from collections import defaultdict
import json,math
from model import ROOT,I,build,sha
BARREL_FRAME=[[0,1,0],[0,0,1],[1,0,0]]
ENDCAP_FRAME=[[0,-1,0],[1,0,0],[0,0,1]]

def area(vertices):
    return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(vertices,vertices[1:]+vertices[:1])))/2

def wedge(r0,r1,tangent,inset):
    return [[r0,-r0*tangent+inset],[r1,-r1*tangent+inset],[r1,r1*tangent-inset],[r0,r0*tangent-inset]]

def part(name,role,material,vertices,z,depth,materials):
    v=area(vertices)*depth
    if v<=0:raise ValueError('degenerate structural part')
    return dict(name=name,role=role,material=material,shape_kind='xtru',vertices_mm=vertices,depth_mm=depth,center_mm=[0,0,z],frame=I,volume_mm3=v,mass_g=v*materials[material]['density_g_cm3']/1000)

def frame_rotation(phi,negative=False):
    co,si=math.cos(phi),math.sin(phi)
    # Columns of Rz(phi), optionally multiplied by Rx(pi); determinant +1.
    return [[co,si,0],[si if negative else -si,-co if negative else co,0],[0,0,-1 if negative else 1]]

def region(u,c,front,outer,kind,materials):
    tangent=math.tan(math.pi/c['sectors']);seam=c['seam_half_gap_mm'];rail=c['edge_rail_mm'];rim=c['endcap_rim_mm']
    layers=c[u['name']+'_layers'];pitch=u['absorber_mm']+u['body_depth_mm']+c['installation_gap_mm'];depth=layers*pitch
    r0,r1=(front,outer) if kind=='barrel' else (c['endcap_inner_apothem_mm'],outer)
    parts=[];placements=[];coverage=[]
    if kind=='barrel':
        zbase=0;structure_depth=2*c['barrel_half_z_mm'];row_min=-c['barrel_half_z_mm']+c['end_allocation_mm'];row_max=-row_min
    else:
        zbase=front+depth/2;structure_depth=depth;row_min=r0+rim+c['end_allocation_mm'];row_max=r1-rim-c['end_allocation_mm']
    left=[[r0,-r0*tangent+seam],[r1,-r1*tangent+seam],[r1,-r1*tangent+seam+rail],[r0,-r0*tangent+seam+rail]]
    right=[[a,-b] for a,b in reversed(left)]
    for tag,vertices in (('left',left),('right',right)):
        parts.append(part(u['name']+'_'+kind+'_'+tag,'edge_frame','Aluminium',vertices,zbase,structure_depth,materials))
    if kind=='barrel':
        for sign in (-1,1):
            parts.append(part(u['name']+'_barrel_flange'+str(sign),'end_frame','Aluminium',wedge(r0,r1+c['back_cover_mm'],tangent,seam),sign*(c['barrel_half_z_mm']+c['end_flange_mm']/2),c['end_flange_mm'],materials))
        parts.append(part(u['name']+'_barrel_back','back_cover','Aluminium',wedge(r1,r1+c['back_cover_mm'],tangent,seam),0,structure_depth,materials))
    else:
        for tag,a,b in (('inner',r0,r0+rim),('outer',r1-rim,r1)):
            parts.append(part(u['name']+'_endcap_'+tag,'rim_frame','Aluminium',wedge(a,b,tangent,seam+rail),zbase,depth,materials))
        parts.append(part(u['name']+'_endcap_back','back_cover','Aluminium',wedge(r0,r1,tangent,seam),front+depth+c['back_cover_mm']/2,c['back_cover_mm'],materials))
    h=u['height_mm'];w=u['width_mm'];step=h+c['cassette_gap_mm'];nrows=math.floor((row_max-row_min+c['cassette_gap_mm'])/step)
    for layer in range(layers):
        layer_front=front+layer*pitch;body_front=layer_front+u['absorber_mm']
        if kind=='barrel':
            vertices=wedge(layer_front,body_front,tangent,seam+rail);plate_depth=structure_depth;plate_z=0
            row_start=-(nrows*step-c['cassette_gap_mm'])/2+h/2
        else:
            vertices=wedge(r0+rim,r1-rim,tangent,seam+rail);plate_depth=u['absorber_mm'];plate_z=layer_front+u['absorber_mm']/2
            row_start=row_min+h/2
        material='TungstenDens24' if u['name']=='ecal' else 'Steel235'
        parts.append(part(u['name']+'_'+kind+'_absorber'+str(layer),'absorber',material,vertices,plate_z,plate_depth,materials))
        cassette=0
        for row in range(nrows):
            axial_or_radial=row_start+row*step
            narrow_radius=body_front if kind=='barrel' else axial_or_radial-h/2
            span=2*(narrow_radius*tangent-seam-c['edge_allocation_mm']);ncols=math.floor((span+c['cassette_gap_mm'])/(w+c['cassette_gap_mm']))
            if ncols<0:raise ValueError('negative packing span')
            start=-(ncols*(w+c['cassette_gap_mm'])-c['cassette_gap_mm'])/2+w/2
            for col in range(ncols):
                tangent_pos=start+col*(w+c['cassette_gap_mm'])
                center=[body_front,tangent_pos,axial_or_radial] if kind=='barrel' else [axial_or_radial,-tangent_pos,body_front]
                placements.append(dict(center_mm=center,frame=BARREL_FRAME if kind=='barrel' else ENDCAP_FRAME,layer=layer,cassette=cassette));cassette+=1
        if cassette>=4096 or layer>=64:raise ValueError('identifier capacity')
        face_area=(2*(body_front*tangent-seam-rail)*structure_depth if kind=='barrel' else area(vertices))
        active_area=sum(p['dimensions_mm']['sx']*p['dimensions_mm']['sy'] for p in u['parts'] if p['role']=='sensitive')
        coverage.append(dict(layer=layer,cassettes=cassette,plate_face_mm2=face_area,occupied_fraction=cassette*w*h/face_area,active_fraction=cassette*active_area/face_area))
    return dict(name=u['name']+'_'+kind,kind=kind,unit=u['name'],parts=parts,placements=placements,coverage=coverage,front_mm=front,outer_apothem_mm=outer,stack_depth_mm=depth,pitch_mm=pitch)

def inventory(config=None):
    c=config or json.loads((ROOT/'tools/calorimeter_hardware/assemblies.json').read_text());units,m=build()
    if c['sectors']<3 or c['sectors']>32:raise ValueError('sector identifier range')
    if any(not math.isfinite(v) or v<=0 for k,v in c.items() if isinstance(v,(int,float))):raise ValueError('positive finite assembly parameter')
    if c['edge_allocation_mm']<c['edge_rail_mm']:raise ValueError('edge allocation')
    e,h=units['units'];ep=e['absorber_mm']+e['body_depth_mm']+c['installation_gap_mm'];hp=h['absorber_mm']+h['body_depth_mm']+c['installation_gap_mm']
    ef=c['ecal_front_apothem_mm'];eo=ef+c['ecal_layers']*ep;hf=eo+c['back_cover_mm']+c['interface_gap_mm'];ho=hf+c['hcal_layers']*hp
    ez=c['ecal_endcap_front_mm'];hz=ez+c['ecal_layers']*ep+c['back_cover_mm']+c['interface_gap_mm']
    if c['barrel_half_z_mm']+c['end_flange_mm']>=ez:raise ValueError('barrel/endcap clearance')
    regions=[];replicas=[]
    for u,f,o,z in ((e,ef,eo,ez),(h,hf,ho,hz)):
        for kind,front in (('barrel',f),('endcap',z)):
            r=region(u,c,front,o,kind,m.recipes);regions.append(r)
            for side in (0,) if kind=='barrel' else (1,2):
                for sector in range(c['sectors']):replicas.append(dict(region=r['name'],unit=u['name'],side=side,sector=sector,center_mm=[0,0,0],frame=frame_rotation(sector*2*math.pi/c['sectors'],side==2)))
    totals=defaultdict(lambda:dict(mass_g=0.,volume_mm3=0.));summary=[]
    for r in regions:
        u=next(u for u in units['units'] if u['name']==r['unit']);mult=sum(x['region']==r['name'] for x in replicas);n=len(r['placements']);sm=sum(p['mass_g'] for p in r['parts']);cm=u['cassette_mass_g']
        for p in r['parts']:
            for key in ('mass_g','volume_mm3'):totals[p['material']][key]+=mult*p[key]
        for p in u['parts']:
            if p['owner']=='cassette':
                for key in ('mass_g','volume_mm3'):totals[p['material']][key]+=mult*n*p[key]
        summary.append(dict(region=r['name'],replicas=mult,cassettes=mult*n,sensitive_elements=mult*n*u['sensitive_count'],channels=mult*n*u['channels'],mass_g=mult*(sm+n*cm),sector_structure_mass_g=sm,sector_cassette_mass_g=n*cm,
                            continuous_heat_W=mult*n*u['power']['total_heat_W'],water_g_s=mult*n*u['power']['water_g_s'],min_active_fraction=min(x['active_fraction'] for x in r['coverage']),max_active_fraction=max(x['active_fraction'] for x in r['coverage'])))
    return dict(status='DRAFT / PROTOTYPE',config=c,units=units['units'],materials=units['materials'],regions=regions,replicas=replicas,summary=summary,material_totals=dict(totals),mass_g=sum(x['mass_g'] for x in totals.values()),
                envelopes=dict(ecal_barrel_front_mm=ef,ecal_barrel_outer_mm=eo,hcal_barrel_front_mm=hf,hcal_barrel_outer_mm=ho,ecal_endcap_front_mm=ez,hcal_endcap_front_mm=hz,hcal_endcap_back_mm=hz+c['hcal_layers']*hp+c['back_cover_mm'],barrel_corner_radius_mm=(ho+c['back_cover_mm'])/math.cos(math.pi/c['sectors'])),source_sha256={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'tools/calorimeter_hardware/assemblies.json',ROOT/'tools/calorimeter_hardware/assembly.py',ROOT/'tools/calorimeter_hardware/model.py',ROOT/'tools/calorimeter_hardware/cassettes.json')}),m
