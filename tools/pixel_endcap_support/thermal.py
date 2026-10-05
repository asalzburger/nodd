"""Orthotropic pickup-sheet screening; no irradiated-sensor thermal-runaway model."""
import math
import numpy as np


def sheet_resistance(width,height,contact_u,contact_v,contact_v_offset,k,thickness,grid,
                     periphery_fraction=0.,periphery_width=1.8,tolerance=1e-10):
    """Cell-centred finite-volume sheet, adiabatic edges, isothermal contact.

    Return K/W under 1 W. Contact cells are pinned; their source bypasses sheet
    resistance. Matrix-free CG solves the remaining symmetric positive system.
    Dimensions in mm; conductivity W/(m K). No guessed interface resistance here.
    """
    nx,ny=math.ceil(width/grid),math.ceil(height/grid)
    dx,dy=width/nx,height/ny
    u=(np.arange(nx)+.5)*dx-width/2
    v=(np.arange(ny)+.5)*dy-height/2
    uu,vv=np.meshgrid(u,v,indexing='ij')
    sink=(abs(uu)<=contact_u/2)&(abs(vv-contact_v_offset)<=contact_v/2)
    if not np.any(sink) or np.all(sink):raise ValueError('Grid must resolve contact and heated sheet')
    # Source = uniform plus chip-periphery-like bands at the two tangential edges.
    # Orientation is conservative design sensitivity, not an RD53 pad-map assertion.
    edge=(abs(uu)>width/2-periphery_width)
    source=np.full((nx,ny),(1-periphery_fraction)/(nx*ny))
    if periphery_fraction:
        source+=edge*(periphery_fraction/edge.sum())
    gx=k*thickness/1000*dy/dx;gy=k*thickness/1000*dx/dy
    def operator(a):
        out=np.zeros_like(a)
        delta=gx*(a[1:,:]-a[:-1,:]);out[1:,:]+=delta;out[:-1,:]-=delta
        delta=gy*(a[:,1:]-a[:,:-1]);out[:,1:]+=delta;out[:,:-1]-=delta
        out[sink]=0.;return out
    rhs=source.copy();rhs[sink]=0.
    x=np.zeros_like(rhs);r=rhs.copy();p=r.copy();rr=float((r*r).sum());initial=rr
    iterations=0
    for iterations in range(1,10001):
        ap=operator(p);den=float((p*ap).sum())
        if den<=0:raise ValueError('Non-positive heat matrix / CG breakdown')
        alpha=rr/den;x+=alpha*p;r-=alpha*ap;new=float((r*r).sum())
        if new<=initial*tolerance*tolerance:break
        p=r+(new/rr)*p;rr=new
    else:raise ValueError('Thermal solve did not converge')
    # Face heat delivered from free cells into the pinned footprint, plus direct source.
    into=0.
    for axis,g in [(0,gx),(1,gy)]:
        left=[slice(None),slice(None)];right=left.copy();left[axis]=slice(None,-1);right[axis]=slice(1,None)
        l,rrr=tuple(left),tuple(right)
        mask=sink[l]!=sink[rrr]
        into+=float((g*abs(x[l]-x[rrr])*mask).sum())
    into+=float(source[sink].sum())
    return dict(max_K_W=float(x.max()),mean_K_W=float(x.mean()),sink_power_W=into,
                cells=[nx,ny],contact_cells=int(sink.sum()),iterations=iterations,
                relative_residual=float(math.sqrt(new/initial)))


def thermal_screen(cfg,base,rows,bodies):
    t=cfg['thermal'];foot=cfg['foot'];pick=cfg['pickup'];cool=cfg['cooling']
    width=2*bodies[0]['half_u_mm'];height=2*bodies[0]['half_v_mm'];A=foot['graphite_u_mm']*foot['envelope_v_mm']*1e-6
    # Includes longest foot and a graphite insert through plate down to the far tube plane.
    max_h=max(b['foot_height_mm'] for b in bodies)
    pipe_reach=(2*cfg['plate']['skin_mm']+cfg['plate']['core_mm'])/2+abs(min(cool['routing_planes_mm']))-cool['tube_OD_mm']/2
    path_lengths=[b['foot_height_mm']+(2*cfg['plate']['skin_mm']+cfg['plate']['core_mm'])/2-b['mount_face']*min(cool['routing_planes_mm']) for b in bodies]
    foot_R=max(path_lengths)/1000/(foot['k_axial_W_m_K']*A)
    # Two thin bonded interfaces at narrow contact; insulating TIM on full module.
    bond_R=2*pick['bond_mm']/1000/(t['bond_k_W_m_K']*A)
    normal_R=pick['graphite_mm']/1000/(t['graphite_k_normal_W_m_K']*A)
    fullA=width*height*1e-6
    module_interface_R=(pick['TIM_mm']/1000/t['TIM_k_W_m_K']+
                        pick['insulation_mm']/1000/base['conductivity_W_m_K']['insulation'])/fullA
    wet_area=math.pi*(cool['tube_OD_mm']-2*cool['tube_wall_mm'])*foot['graphite_u_mm']*1e-6
    # Full circumference wet area optimistic; half-contact sensitivity represented by htc/2.
    # Ti wall conduction through 180deg saddle, titanium k=16 W/mK comparator assumption.
    ti_R=math.log((cool['tube_OD_mm']/2)/(cool['tube_OD_mm']/2-cool['tube_wall_mm']))/(math.pi*cool['titanium_k_W_m_K']*foot['graphite_u_mm']/1000)
    fixed=dict(foot_and_core_insert_K_W=foot_R,bonds_K_W=bond_R,graphite_through_plane_K_W=normal_R,
               module_interface_K_W=module_interface_R,titanium_wall_K_W=ti_R)
    variants=[];convergence=[]
    nominal=4*base['power_per_chip_W'];stress=nominal*base['stress_factor']
    for k in t['k_sensitivity_W_m_K']:
        for fraction in [0.,t['periphery_fraction']]:
            sheet=sheet_resistance(width,height,foot['graphite_u_mm'],foot['envelope_v_mm'],
                                   -foot['radial_offset_mm'],k,pick['graphite_mm'],t['grid_mm'],
                                   fraction,t['periphery_width_mm'],t['cg_relative_tolerance'])
            if k==t['graphite_k_inplane_W_m_K']:
                coarse=sheet_resistance(width,height,foot['graphite_u_mm'],foot['envelope_v_mm'],
                                       -foot['radial_offset_mm'],k,pick['graphite_mm'],t['coarse_grid_mm'],fraction,
                                       t['periphery_width_mm'],t['cg_relative_tolerance'])
                convergence.append(dict(periphery_fraction=fraction,fine_K_W=sheet['max_K_W'],coarse_K_W=coarse['max_K_W'],
                                        relative_change=abs(coarse['max_K_W']/sheet['max_K_W']-1)))
            for htc in cool['htc_sensitivity_W_m2_K']:
                R=sheet['max_K_W']+sum(fixed.values())+1/(htc*wet_area)
                variants.append(dict(k_inplane_W_m_K=k,periphery_fraction=fraction,htc_W_m2_K=htc,
                                     sheet=sheet,R_total_K_W=R,nominal_C=cool['coolant_C']+nominal*R,
                                     stress_C=cool['coolant_C']+stress*R,
                                     stress_at_minus35_C=-35+stress*R,
                                     stress_target_pass=cool['coolant_C']+stress*R<=cool['sensor_target_C']))
    circuits=[]
    for r in rows:
        n=r['modules']//2;power=n*nominal;flow=cool['flow_per_half_ring_g_s'][r['row']]
        circuits.append(dict(row=r['row'],circuits_per_disc=2,modules_per_circuit=n,
                             nominal_W=power,stress_W=power*base['stress_factor'],flow_g_s=flow,
                             nominal_exit_quality=cool['inlet_quality']+power/(flow*base['latent_heat_J_g']),
                             stress_exit_quality=cool['inlet_quality']+power*base['stress_factor']/(flow*base['latent_heat_J_g']),
                             evaporator_arc_length_mm=math.pi*r['cooling_radius_mm']))
    # A deliberately favourable lower bound for the rejected tall central post:
    # no pickup spreading, graphite c-axis penalty or boiling resistance added.
    A4=cfg['retained_case']['central_post_mm']**2*1e-6
    longest=cfg['retained_case']['plate_front_mm']-(-4.2+.5)
    lower=longest/1000/(foot['k_axial_W_m_K']*A4)+2*pick['bond_mm']/1000/(t['bond_k_W_m_K']*A4)
    return dict(module_nominal_W=nominal,module_stress_W=stress,disc_nominal_W=112*nominal,
                all_endcaps_nominal_W=18*112*nominal,disc_flow_g_s=2*sum(cool['flow_per_half_ring_g_s']),
                all_endcaps_flow_g_s=36*sum(cool['flow_per_half_ring_g_s']),
                required_total_R_K_W=(cool['sensor_target_C']-cool['coolant_C'])/stress,
                fixed_resistances=fixed,variants=variants,grid_convergence=convergence,circuits=circuits,
                retained_A_optimistic_R_lower_bound_K_W=lower,
                retained_A_optimistic_stress_C=cool['coolant_C']+stress*lower,
                limitations=['Uniform and edge-biased heat maps are sensitivity models, not RD53 electrothermal FEA.',
                             'No temperature-dependent leakage, dose/fluence requirement, hot-spot map or runaway margin.',
                             'Anisotropic pickup, oriented graphite foot and contact windows are essential; no heat is forced through CFRP c-axis.',
                             'Boiling htc and wet area are unmeasured. Pressure drop, capillary sizing and dry-out are NOT validated.',
                             'Sink is represented by a rectangular isothermal land; lumped insert/saddle path needs 3D validation.'])
