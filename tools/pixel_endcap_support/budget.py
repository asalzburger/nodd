"""Disjoint mass inventory, service-space arithmetic and stiffness brackets."""
import json
import math
from model import ROOT, dimensions


def inventory(cfg,base,rows,bodies):
    p,f,m,c=cfg['plate'],cfg['foot'],cfg['mounting'],cfg['cooling']
    ann=math.pi*(p['r_max_mm']**2-p['r_min_mm']**2);thick=dimensions(cfg)[0]
    # Tangential rectangular tongues start at r186, but only their external part
    # is charged here. Conservative full-width extension beyond the circular rim.
    y=m['tab_width_mm']/2;R=p['r_max_mm']
    tabs=3*(m['tab_width_mm']*m['tab_end_r_mm']-(y*math.sqrt(R*R-y*y)+R*R*math.asin(y/R)))
    face_area=ann+tabs
    arc_length=2*sum(math.pi*r['cooling_radius_mm'] for r in rows)
    # Every half-loop has inlet AND outlet radial leg, plus bend allowance.
    radial_length=4*sum(p['r_max_mm']-r['cooling_radius_mm']+c['radial_leg_extra_mm'] for r in rows)
    length=arc_length+radial_length
    ro=c['tube_OD_mm']/2;ri=ro-c['tube_wall_mm']
    tube_outer=math.pi*ro*ro*length;ti=math.pi*(ro*ro-ri*ri)*length;liquid=math.pi*ri*ri*length
    afoot=f['graphite_u_mm']*f['envelope_v_mm'];height=sum(b['foot_height_mm'] for b in bodies)
    insert_depth=thick/2+abs(min(c['routing_planes_mm']))-ro
    insert_depths=[thick/2-b['mount_face']*min(c['routing_planes_mm']) for b in bodies]
    # 180-degree machined Ti saddle: block reaches tube centre, half-cylinder removed.
    insert_volumes=[afoot*d-.5*math.pi*ro*ro*f['graphite_u_mm'] for d in insert_depths]
    inserts=sum(insert_volumes)
    feet=afoot*height
    bodyA=4*bodies[0]['half_u_mm']*bodies[0]['half_v_mm']
    totalA=len(bodies)*bodyA
    # Remove through-skin land windows and foam displaced by tubes and inserts.
    # Machined inserts cradle 180 degrees of the local evaporator; transitions remain unrouted.
    # This additive deduction assumes the later radial routing avoids the inserts.
    skin_volume=2*face_area*p['skin_mm']-len(bodies)*afoot*p['skin_mm']
    tube_in_core=math.pi*ro*ro*(length-4*len(rows)*c['radial_leg_extra_mm'])
    core_volume=face_area*p['core_mm']-tube_in_core-(inserts-len(bodies)*afoot*p['skin_mm'])
    if core_volume<=0:raise ValueError('Invalid occupied foam volume')
    components=[]
    def add(label,mat,volume,scope='disc',extra_mass=0.):
        density=base['density_g_cm3'][mat]
        X0=base['radiation_length_mm'].get(mat)
        if mat=='liquid_CO2':X0=base['co2_X0_g_cm2']/density*10
        components.append(dict(component=label,material=mat,scope=scope,volume_mm3=volume,
                               mass_g=volume*density/1000+extra_mass,
                               annulus_normalized_X0_percent=100*volume/(ann*X0) if X0 and scope=='disc' else None))
    add('facesheets and tongues, thermal windows deducted','CFRP',skin_volume)
    add('foam core, tubes and inserts deducted','foam',core_volume)
    add('graphite feet and through-core thermal inserts','graphite',feet+inserts)
    pick=cfg['pickup']
    add('module pickup graphite','graphite',totalA*pick['graphite_mm'])
    add('module cradles, land windows deducted','CFRP',(totalA-len(bodies)*afoot)*pick['cradle_mm'])
    add('module isolation','insulation',totalA*pick['insulation_mm'])
    add('TIM and module bond films','glue',totalA*(pick['TIM_mm']+pick['bond_mm']))
    add('skin/core bond films, foam displaced','glue',face_area*p['glue_equivalent_mm'])
    # Glue replaces foam; do not add mass without displacing the allocated core.
    components[1]['volume_mm3']-=face_area*p['glue_equivalent_mm']
    components[1]['mass_g']=components[1]['volume_mm3']*base['density_g_cm3']['foam']/1000
    components[1]['annulus_normalized_X0_percent']=100*components[1]['volume_mm3']/(ann*base['radiation_length_mm']['foam'])
    add('local evaporators and radial legs','titanium',ti)
    add('local tubing: full-liquid mass bound','liquid_CO2',liquid)
    # End closeouts: thin CFRP skins around annular free edges; explicit extra, outside foam.
    closeout=math.pi*(p['r_max_mm']**2-(p['r_max_mm']-p['skin_mm'])**2+(p['r_min_mm']+p['skin_mm'])**2-p['r_min_mm']**2)*p['core_mm']
    add('inner/outer edge closeouts inside foam','CFRP',closeout)
    components[1]['volume_mm3']-=closeout
    components[1]['mass_g']=components[1]['volume_mm3']*base['density_g_cm3']['foam']/1000
    components[1]['annulus_normalized_X0_percent']=100*components[1]['volume_mm3']/(ann*base['radiation_length_mm']['foam'])
    add('module clip allowance','CFRP',len(bodies)*m['module_clip_allowance_g']*1000/base['density_g_cm3']['CFRP'])
    add('mounting hardware mass allowance (Ti equivalent)','titanium',m['hardware_allowance_g_per_disc']*1000/base['density_g_cm3']['titanium'])
    flex=cfg['flex'];bus=arc_length*flex['bus_width_mm']*flex['bus_envelope_mm']
    fans=2*flex['radial_fans']*(p['r_max_mm']-p['r_min_mm'])*flex['bus_width_mm']*flex['bus_envelope_mm']
    tails=sum(b['foot_height_mm']+flex['tail_extra_length_mm'] for b in bodies)*flex['tail_width_mm']*flex['tail_envelope_mm']
    flexvolume=bus+fans+tails
    add('local flex polyimide, provisional 40% envelope fill','insulation',flexvolume*flex['polyimide_volume_fraction'])
    vcu=flexvolume*flex['copper_volume_fraction']
    components.append(dict(component='local flex copper, provisional 10% envelope fill',material='copper',scope='disc',volume_mm3=vcu,
                           mass_g=vcu*flex['copper_density_g_cm3']/1000,
                           annulus_normalized_X0_percent=100*vcu/(ann*flex['copper_X0_mm'])))
    L=m['carrier_z_mm'][1]-m['carrier_z_mm'][0];r=m['shell_outer_r_mm'];t=m['shell_mm']
    add('closed carrier shell','CFRP',math.pi*(r*r-(r-t)**2)*L,'one_end')
    box=m['rail_width_mm']*m['rail_depth_mm']-(m['rail_width_mm']-2*m['rail_wall_mm'])*(m['rail_depth_mm']-2*m['rail_wall_mm'])
    add('three longitudinal box rails','CFRP',3*box*L,'one_end')
    add('two carrier end flanges','CFRP',2*math.pi*(r*r-(r-m['flange_radial_mm'])**2)*m['flange_axial_mm'],'one_end')
    disc=sum(a['mass_g'] for a in components if a['scope']=='disc');shared=sum(a['mass_g'] for a in components if a['scope']=='one_end')
    # Rectangular equivalent full-diameter plate beam: deliberately limited screen.
    plate_I=(p['r_max_mm']*2)*2*p['skin_mm']*(thick/2-p['skin_mm']/2)**2
    shell_I=math.pi/4*(r**4-(r-t)**4)
    disc_payload=disc+112*m['module_mass_g']
    end_mass=9*disc_payload+shared+1000*m['service_mass_allowance_kg_per_end']
    elastic=[]
    for E in cfg['mechanical_screen']['E_GPa']:
        g=cfg['mechanical_screen']['gravity_m_s2'];span=2*p['r_max_mm']
        F=disc_payload/1000*g;distributed=5*F*span**3/(384*E*1000*plate_I)
        concentrated=F*span**3/(48*E*1000*plate_I)
        global_sag=5*(end_mass/1000*g)*L**3/(384*E*1000*shell_I)
        # An unsupported 8x8 rail alone, one-third end weight, illustrates load path.
        rail_I=(m['rail_width_mm']*m['rail_depth_mm']**3-(m['rail_width_mm']-2*m['rail_wall_mm'])*(m['rail_depth_mm']-2*m['rail_wall_mm'])**3)/12
        free_rail=5*(end_mass/3000*g)*L**3/(384*E*1000*rail_I)
        elastic.append(dict(E_GPa=E,disc_beam_distributed_mm=distributed,disc_beam_central_load_mm=concentrated,
                            closed_shell_sag_mm=global_sag,unsupported_one_rail_sag_mm=free_rail))
    return dict(components=components,annulus_area_mm2=ann,local_tube_length_mm=length,arc_length_mm=arc_length,
                radial_leg_length_with_allowance_mm=radial_length,disc_passive_mass_g=disc,
                disc_equivalent_normal_X0_percent=sum(a['annulus_normalized_X0_percent'] or 0 for a in components),
                shared_support_per_end_g=shared,all_18_discs_passive_plus_two_carriers_kg=(18*disc+2*shared)/1000,
                disc_payload_with_modules_g=disc_payload,one_end_mechanical_mass_with_service_allowance_kg=end_mass/1000,
                elastic_screens=elastic,
                limitations=['Annulus-normalized volume/X0 includes external tongue/hardware inventory; not an actual spatial material average or eta/phi scan.',
                             'Mass includes full-liquid local tubes; no vapour fraction mass reduction is claimed.',
                             'Disc hardware/clip allowances are not a released bill of materials; external harness/transport/manifold material is separate.',
                             'Tube/flex length allowances do not replace routed CAD; additive volume deductions assume radial legs avoid graphite inserts; exact solid union pending.',
                             'Beam brackets omit annular opening, three-point support, skin anisotropy, core shear, cutout weakening, joints, torsion and ovalization.',
                             'Carrier sag presumes closed structural shell and supported end flanges; no buckling, eigenmode or thermal-cycle qualification.'])


def services(cfg,layout,rows):
    inp=json.loads((ROOT/cfg['service_inputs']).read_text())
    barrel=json.loads((ROOT/cfg['barrel_services']).read_text())
    chains=2*sum(math.ceil((r['modules']/2)/8) for r in rows)
    discs=[];stages=[];groups=[]
    template=[b for b in layout['bodies'] if b['layer_id']=='A-pixel-P1']
    for row in rows:
        members=sorted([b for b in template if b['row']==row['row']],key=lambda b:b['col'])
        if len(members)%2:raise ValueError('Half-ring grouping requires an even module count')
        for half in [0,1]:
            chunk=members[half*len(members)//2:(half+1)*len(members)//2]
            groups.append(dict(circuit=f'row-{row["row"]}-half-{half}',row=row['row'],half=half,
                               module_ids=[b['module_id'] for b in chunk],
                               power_chains=[[b['module_id'] for b in chunk[i:i+8]] for i in range(0,len(chunk),8)]))
    r0=190+inp['capacity']['boundary_allowance_mm']
    # Shell lies outside r232; no unused boundary allowance is double charged.
    r1=min(234-inp['capacity']['boundary_allowance_mm'],cfg['mounting']['shell_outer_r_mm']-cfg['mounting']['shell_mm'])
    section=math.pi*(r1*r1-r0*r0)
    for name,s in inp['scenarios'].items():
        links=112*s['pixel_uplinks_per_module']+448*s['pixel_uplinks_per_chip']+112*s['pixel_commands_per_module']
        cables=chains*inp['pixel']['ancillary_chain_area_mm2']+links*inp['pixel']['differential_link_area_mm2']
        pipes=10*2*math.pi*(cfg['cooling']['transport_OD_mm']/2)**2
        disc_raw=cables+pipes
        # With half-ring collection, inner neck carries only inner-row traffic.
        necks=[]
        cum_modules=cum_chains=cum_loops=0
        for row in rows:
            n=row['modules'];cum_modules+=n;cum_chains+=2*math.ceil((n/2)/8);cum_loops+=2
            nlinks=cum_modules*(s['pixel_uplinks_per_module']+4*s['pixel_uplinks_per_chip']+s['pixel_commands_per_module'])
            demand=(cum_chains*35+nlinks+cum_loops*2*math.pi*2**2)*s['demand_multiplier']
            radius=min(188.,row['cooling_radius_mm']+cfg['foot']['envelope_v_mm']/2)
            # 50 mm bay less 2 mm boundaries, all azimuth scenario allowance.
            capacity=2*math.pi*radius*(50-4)*s['available_phi_fraction']*s['packing_fraction']
            necks.append(dict(after_row=row['row'],radius_mm=radius,demand_mm2=demand,capacity_mm2=capacity,utilization=demand/capacity))
        discs.append(dict(scenario=name,chains=chains,links=links,cables_mm2=cables,pipes_mm2=pipes,
                          bare_total_mm2=disc_raw,radial_necks=necks))
        for side in ['positive','negative']:
            sectors=[x['scenarios'][name] for x in barrel['sectors'] if x['side']==side]
            barrel_raw=sum(sum(x['terminal_cable_footprint_mm2'].values())+x['terminal_pipe_footprint_mm2'] for x in sectors)
            for n in range(9): # P1..8 join; P9 retains bypass.
                demand=(barrel_raw+n*disc_raw)*s['demand_multiplier']
                cap=section*s['available_phi_fraction']*s['packing_fraction']
                stages.append(dict(side=side,scenario=name,endcap_discs_joined=n,barrel_bare_mm2=barrel_raw,
                                   demand_mm2=demand,capacity_mm2=cap,utilization=demand/cap,status='PASS' if demand<=cap else 'FAIL'))
    return dict(template_groups=groups,local_disc_scenarios=discs,accumulation=stages,barrel_source=cfg['barrel_services'],
                barrel_inventory=barrel['totals'],local_circuits_per_disc=10,power_chains_per_disc=chains,
                reserved_phi_for_mounts_and_ports_deg=90.,rail_sector_centres_deg=cfg['mounting']['angles_deg'],
                last_disc='Retain DES010 last-disc bypass and rear turn. A common rim interface needs a last-disc adapter; not routed/qualified here.',
                limitations=['Aggregate cross-section screening only: fixed-sector redistribution, exact bends, connectors, voltage drop and bandwidth are unqualified.',
                             '12 existing barrel sectors are retained for inventory; redistribution into endcap free sectors is NOT demonstrated.',
                             'The common shell and three rails occupy reserved interfaces; bracket and weld keep-outs still need a solid layout.',
                             'Local effective flex inventory and transport cable footprints describe different sections; packing void is not material.'])
