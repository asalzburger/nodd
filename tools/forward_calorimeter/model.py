"""DES039 isolated FCAL solids, exact fibre inventory and straight-ray screening.

All lengths are mm. This is a design model, not an optical or shower simulation.
"""
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def load_config(path=None):
    return json.loads(Path(path or HERE / 'inputs.json').read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def zones(config):
    result = {}
    z = 0.
    for item in config['module']['zones']:
        if item['length_mm'] <= 0 or item['name'] in result:
            raise ValueError('Invalid or duplicate axial zone')
        result[item['name']] = (z, z + item['length_mm'])
        z += item['length_mm']
    if abs(z - config['module']['length_mm']) > 1e-8:
        raise ValueError('Axial zones do not close package length')
    return result


def slot_vertices(config, radius, phi):
    half = config['readout']['cartridge_side_mm'] / 2
    c, s = math.cos(phi), math.sin(phi)
    return [((radius + dr)*c - dt*s, (radius + dr)*s + dt*c)
            for dr in (-half, half) for dt in (-half, half)]


def validate_config(c):
    m, f, r, t = (c[k] for k in ('module', 'fibres', 'readout', 'thermal'))
    z = zones(c)
    if not 0 < m['bore_radius_mm'] < m['sampling_inner_radius_mm'] < m['sampling_outer_radius_mm'] < m['outer_radius_mm']:
        raise ValueError('Invalid radial nesting')
    if not 0 < f['core_radius_mm'] < f['buffer_outer_radius_mm'] < f['hole_radius_mm'] < f['pitch_mm']/2:
        raise ValueError('Fibre, buffer, insertion gap and pitch are inconsistent')
    if not 0 < f['short_start_mm'] < z['sampling'][1]-z['sampling'][0]:
        raise ValueError('Short fibre starts outside sample')
    if r['radial_edges_mm'][0] != m['sampling_inner_radius_mm'] or r['radial_edges_mm'][-1] != m['sampling_outer_radius_mm']:
        raise ValueError('Readout bands must close sampling annulus')
    if any(a >= b for a,b in zip(r['radial_edges_mm'], r['radial_edges_mm'][1:])):
        raise ValueError('Non-monotonic readout bands')
    if len(r['cartridge_radius_rows_mm']) != 2*(len(r['radial_edges_mm'])-1):
        raise ValueError('One sensor cartridge per ring and population required')
    if t['pipe_radius_mm'] + t['pipe_outer_diameter_mm']/2 >= m['rear_shell_inner_mm']:
        raise ValueError('Rear cooling pipe intersects housing')
    if t['pipe_radius_mm'] - t['pipe_outer_diameter_mm']/2 <= m['rear_cover_outer_mm']:
        raise ValueError('Rear cooling pipe intersects rear closure')
    dphi = 2*math.pi/r['sectors']
    for radius in r['cartridge_radius_rows_mm']:
        vertices=slot_vertices(c,radius,0.)
        if max(math.hypot(x,y) for x,y in vertices) >= m['rear_shell_inner_mm']:
            raise ValueError('Sensor cartridge outside rear housing')
        if min(x for x,y in vertices) <= m['bore_radius_mm']:
            raise ValueError('Sensor cartridge intersects bore')
        if max(abs(math.atan2(y,x)) for x,y in vertices) >= dphi/2:
            raise ValueError('Sensor cartridge intersects adjacent sector')
    rows = r['cartridge_radius_rows_mm']
    if min(b-a for a,b in zip(rows, rows[1:])) <= r['cartridge_side_mm']:
        raise ValueError('Sensor cartridges overlap radially')
    if r['ferrule_grid_per_side']*r['ferrule_pitch_mm'] > r['pixel_side_mm']:
        raise ValueError('Fibre ferrule does not fit pixel')
    if not 0 < m['half_seam_half_angle_deg'] < 1:
        raise ValueError('Clamshell seam must be finite and small')
    return z


def in_half(x,y,radius,margin,half_gap):
    """Require finite circular bore inside a clamshell azimuthal boundary."""
    phi = math.atan2(y,x)
    a = math.asin(min(1., margin/radius))
    right = -math.pi/2+half_gap+a < phi < math.pi/2-half_gap-a
    left = phi > math.pi/2+half_gap+a or phi < -math.pi/2-half_gap-a
    return 0 if right else (1 if left else None)


def build(config=None):
    c = deepcopy(config or load_config())
    z = validate_config(c)
    m,f,r = (c[k] for k in ('module','fibres','readout'))
    pitch, hole = f['pitch_mm'], f['hole_radius_mm']
    n = math.ceil(m['sampling_outer_radius_mm']/pitch)
    fibres = []
    counts = Counter()
    gap = math.radians(m['half_seam_half_angle_deg'])
    for i in range(-n,n):
        for j in range(-n,n):
            x,y=(i+.5)*pitch,(j+.5)*pitch
            rad=math.hypot(x,y)
            if rad-hole <= m['sampling_inner_radius_mm'] or rad+hole >= m['sampling_outer_radius_mm']:
                continue
            half = in_half(x,y,rad,hole,gap)
            if half is None:
                continue
            phi=math.atan2(y,x)%(2*math.pi)
            sector=int(phi/(2*math.pi)*r['sectors'])
            ring=next(k for k,(lo,hi) in enumerate(zip(r['radial_edges_mm'],r['radial_edges_mm'][1:])) if lo <= rad < hi)
            population=(i+j)%2
            channel=(sector*(len(r['radial_edges_mm'])-1)+ring)*2+population
            ordinal=counts[channel]
            counts[channel]+=1
            front=z['sampling'][0]+(f['short_start_mm'] if population else 0.)
            fibres.append({'index':len(fibres),'i':i,'j':j,'x_mm':x,'y_mm':y,
                           'half':half,'sector':sector,'ring':ring,'population':population,
                           'channel':channel,'ordinal':ordinal,'pixel':ordinal%16,
                           'pixel_fibre':ordinal//16,'z0_mm':front,'z1_mm':z['sampling'][1]})
    channels=[]
    for sector in range(r['sectors']):
        phi=(sector+.5)*2*math.pi/r['sectors']
        for ring in range(len(r['radial_edges_mm'])-1):
            for pop in (0,1):
                channel=(sector*(len(r['radial_edges_mm'])-1)+ring)*2+pop
                rad=r['cartridge_radius_rows_mm'][ring*2+pop]
                channels.append({'channel':channel,'sector':sector,'ring':ring,'population':pop,
                                 'phi_rad':phi,'radius_mm':rad,'x_mm':rad*math.cos(phi),'y_mm':rad*math.sin(phi),
                                 'fibre_count':counts[channel], 'pixels':16,
                                 'vertices_mm':slot_vertices(c,rad,phi)})
    if any(v['fibre_count']==0 for v in channels):
        raise ValueError('Empty channel')
    if max(math.ceil(v/16) for v in counts.values()) > r['ferrule_grid_per_side']**2:
        raise ValueError('Actual fibre inventory exceeds physical pixel ferrule capacity')
    return {'config':c,'zones_mm':z,'fibres':fibres,'channels':channels}


def fibre_endpoint(model, fibre):
    """End each buffered fibre inside its actual 6mm SiPM pixel, no lens."""
    r=model['config']['readout']; ch=model['channels'][fibre['channel']]
    pix=fibre['pixel']; gx=pix%4; gy=pix//4
    slot=fibre['pixel_fibre']; nx=r['ferrule_grid_per_side']
    dr=(gx-1.5)*r['pixel_pitch_mm']+(slot%nx-(nx-1)/2)*r['ferrule_pitch_mm']
    dt=(gy-1.5)*r['pixel_pitch_mm']+(slot//nx-(nx-1)/2)*r['ferrule_pitch_mm']
    a=ch['phi_rad']; co,si=math.cos(a),math.sin(a)
    return (ch['x_mm']+dr*co-dt*si,ch['y_mm']+dr*si+dt*co)


def routing(model):
    """Smooth endpoint routing bounds; individual-fibre crossings are unqualified."""
    c=model['config']; length=model['zones_mm']['fanout'][1]-model['zones_mm']['fanout'][0]
    max_d=0.; minimum=math.inf; extra=0.
    q=c['fibres']['routing_samples']
    for f in model['fibres']:
        x,y=fibre_endpoint(model,f)
        d=math.hypot(x-f['x_mm'],y-f['y_mm']);max_d=max(d,max_d)
        if d:
            # Cosine S curve: zero endpoint slope; explicit curvature at endpoints.
            for k in range(q):
                t=k/(q-1); v=d*math.pi/(2*length)*math.sin(math.pi*t)
                a=d*math.pi**2/(2*length*length)*math.cos(math.pi*t)
                if a:minimum=min(minimum,(1+v*v)**1.5/abs(a))
            segments=[]
            prev=0.
            for k in range(1,q):
                t=k/(q-1); h=(1-math.cos(math.pi*t))/2
                segments.append(math.hypot(length/(q-1),d*(h-prev)));prev=h
            extra+=sum(segments)-length
    if minimum < c['fibres']['minimum_bend_radius_mm']:
        raise ValueError('Optical fanout violates minimum bend radius')
    return {'maximum_endpoint_displacement_mm':max_d,'sampled_minimum_bend_radius_mm':minimum,
            'required_minimum_bend_radius_mm':c['fibres']['minimum_bend_radius_mm'],
            'total_fibre_length_mm':len(model['fibres'])*length+extra,
            'claim':'Endpoint, pixel occupancy and sampled single-fibre bend screen; no complete 3D fibre-fibre collision, optical attenuation or connector qualification.'}


def inventory(model):
    c=model['config'];m,f=c['module'],c['fibres'];z=model['zones_mm']
    length=z['sampling'][1]-z['sampling'][0]
    area=math.pi*(m['sampling_outer_radius_mm']**2-m['sampling_inner_radius_mm']**2)*(1-4*m['half_seam_half_angle_deg']/360)
    fibre_length=sum(x['z1_mm']-x['z0_mm'] for x in model['fibres'])
    hole_v=math.pi*f['hole_radius_mm']**2*fibre_length
    quartz_v=math.pi*f['core_radius_mm']**2*fibre_length
    buffer_v=math.pi*(f['buffer_outer_radius_mm']**2-f['core_radius_mm']**2)*fibre_length
    volumes={'tungsten':area*length-hole_v,'fused_silica':quartz_v,'buffer_proxy':buffer_v,'air_insertion_gap':hole_v-quartz_v-buffer_v}
    annulus=lambda a,b,l:math.pi*(b*b-a*a)*l
    # Disjoint enclosure shells / closure plates. Auxiliary electronics are a partial bill.
    al=annulus(m['bore_radius_mm'],m['inner_shell_outer_mm'],m['length_mm'])
    al+=annulus(m['sampling_shell_inner_mm'],m['outer_radius_mm'],z['sampling'][1])
    al+=annulus(m['rear_shell_inner_mm'],m['outer_radius_mm'],m['length_mm']-z['sampling'][1])
    al+=annulus(m['inner_shell_outer_mm'],m['sampling_shell_inner_mm'],m['cover_thickness_mm'])
    al+=annulus(m['inner_shell_outer_mm'],m['rear_cover_outer_mm'],m['cover_thickness_mm'])
    # Rear load ring outside optical exit; four longitudinal block cradle ribs.
    al+=annulus(m['sampling_outer_radius_mm'],m['sampling_shell_inner_mm'],18.)
    al+=4*(m['sampling_shell_inner_mm']-m['sampling_outer_radius_mm']-.2)*6.*length
    volumes['aluminium']=al
    masses={k:v*c['materials'][k]['density_g_cm3']/1000 for k,v in volumes.items() if k in c['materials']}
    nuc=sum(volumes[k]/area/c['materials'][k]['lambda_nuclear_mm'] for k in ('tungsten','fused_silica','buffer_proxy'))
    x0=sum(volumes[k]/area/c['materials'][k]['x0_mm'] for k in ('tungsten','fused_silica','buffer_proxy'))
    # W-only normalized front depth conservatively ignores additional core/buffer X0.
    long_n=sum(v['population']==0 for v in model['fibres'])
    wfront=1-long_n*math.pi*f['hole_radius_mm']**2/area
    return {'fibres_per_end':len(model['fibres']),'population_counts':dict(Counter('S' if x['population'] else 'L' for x in model['fibres'])),
            'optical_channels_per_end':len(model['channels']),'physical_sipm_pixels_per_end':16*len(model['channels']),
            'channel_fibre_count_min_max':[min(x['fibre_count'] for x in model['channels']),max(x['fibre_count'] for x in model['channels'])],
            'sampling_envelope_volume_mm3':area*length,'volumes_mm3':volumes,'partial_masses_g':masses,
            'partial_mass_per_end_kg':sum(masses.values())/1000,
            'averaged_sample_nuclear_lambda':nuc,'averaged_sample_x0':x0,
            'w_only_x0_before_short_start':f['short_start_mm']*wfront/c['materials']['tungsten']['x0_mm'],
            'claim':'Exclusive material volumes, including actual finite hole counts/lengths and clamshell seams. Transverse area average is not a directional path, pion interaction length or shower-containment measurement. Fanout/electronics/external routes and detailed mounts omitted from this partial mass.'}


def intervals(z0,z1,inner,outer,eta):
    sh=math.sinh(abs(eta));a=max(z0,inner*sh);b=min(z1,outer*sh)
    return (a,b) if b>a else None


def ray_sample(model, eta, phi, sample_front, side=1):
    """Exact finite cylinder intersections for IP straight rays; lengths along ray."""
    c=model['config'];m,f=c['module'],c['fibres']
    length=model['zones_mm']['sampling'][1]-model['zones_mm']['sampling'][0]
    base=intervals(sample_front,sample_front+length,m['sampling_inner_radius_mm'],m['sampling_outer_radius_mm'],eta)
    out={'tungsten':0.,'fused_silica':0.,'buffer_proxy':0.,'air_insertion_gap':0.,'seam_air':0.}
    if not base:return {'paths_mm':out,'nuclear_lambda':0.,'x0':0.,'fibre_core_crossings':0}
    # Negative side is a proper Rx(pi): local y and z change signs.
    local_phi=phi if side>0 else -phi
    co,si=math.cos(local_phi),math.sin(local_phi);sh=math.sinh(abs(eta));norm=math.cosh(eta)/sh
    axial=base[1]-base[0]
    ph=math.atan2(si,co)
    if in_half(co,si,1.,0.,math.radians(m['half_seam_half_angle_deg'])) is None:
        out['seam_air']=axial*norm
        return {'paths_mm':out,'nuclear_lambda':0.,'x0':0.,'fibre_core_crossings':0}
    out['tungsten']=axial*norm
    crossings=0
    for fibre in model['fibres']:
        cross=-fibre['x_mm']*si+fibre['y_mm']*co
        if abs(cross)>=f['hole_radius_mm']:continue
        proj=fibre['x_mm']*co+fibre['y_mm']*si
        if proj<=0:continue
        lo=max(base[0],sample_front+fibre['z0_mm']-model['zones_mm']['sampling'][0]);hi=base[1]
        amounts=[]
        for rad in (f['hole_radius_mm'],f['buffer_outer_radius_mm'],f['core_radius_mm']):
            if abs(cross)>=rad:amounts.append(0.);continue
            dz=math.sqrt(rad*rad-cross*cross)*sh
            amounts.append(max(0.,min(hi,proj*sh+dz)-max(lo,proj*sh-dz))*norm)
        hole,buffer,core=amounts
        out['tungsten']-=hole;out['fused_silica']+=core
        out['buffer_proxy']+=buffer-core;out['air_insertion_gap']+=hole-buffer
        crossings+=bool(core)
    nuc=sum(out[k]/c['materials'][k]['lambda_nuclear_mm'] for k in ('tungsten','fused_silica','buffer_proxy'))
    x0=sum(out[k]/c['materials'][k]['x0_mm'] for k in ('tungsten','fused_silica','buffer_proxy'))
    return {'paths_mm':out,'nuclear_lambda':nuc,'x0':x0,'fibre_core_crossings':crossings}


def hcal_path(context,eta,phi):
    """16-gon envelope interval only; no sampling/material asserted here."""
    h=context['hcal'];dphi=2*math.pi/16
    off=(phi+dphi/2)%dphi-dphi/2
    inner=1000*h['endcap_inner_apothem_m']/math.cos(off)
    outer=1000*h['endcap_outer_apothem_m']/math.cos(off)
    interval=intervals(1000*h['endcap_front_abs_z_m'],1000*h['endcap_back_abs_z_m'],inner,outer,eta)
    return 0. if interval is None else (interval[1]-interval[0])*math.cosh(eta)/math.sinh(abs(eta))


def layout_report(model, name, context):
    c=model['config'];m=c['module'];p=c['layouts'][name];z=model['zones_mm']
    front=p['package_front_abs_z_mm'];end=front+m['length_mm'];sf=front+z['sampling'][0];sb=front+z['sampling'][1]
    if end>p['original_back_abs_z_mm']:
        raise ValueError('Package exceeds allocated rear bound')
    h=context['hcal'];ec=context['ecal'];pipe=context['beam_pipe']
    bore_ec=ec.get('endcap_inner_radius_m',ec.get('endcap_inner_apothem_m'))
    if front<1000*ec['endcap_back_abs_z_m'] and end>1000*ec['endcap_front_abs_z_m'] and m['outer_radius_mm']>=1000*bore_ec:
        raise ValueError('FCAL clashes with ECAL package')
    if front<1000*h['endcap_back_abs_z_m'] and end>1000*h['endcap_front_abs_z_m'] and m['outer_radius_mm']>=1000*h['endcap_inner_apothem_m']:
        raise ValueError('FCAL clashes with HCAL inner apothem')
    # Exact slot/piping spatial facts are separate from envelope navigation.
    original_entry=p['original_bore_radius_mm']*math.sinh(5.)
    scans=[]
    nphi=c['validation']['phi_samples']
    for eta in c['validation']['etas']:
        rays=[]
        for side in (-1,1):
            for i in range(nphi):
                phi=2*math.pi*(i+.5)/nphi
                ray=ray_sample(model,eta,phi,sf,side)
                rays.append(ray)
        vals=[r['nuclear_lambda'] for r in rays]
        cores=[r['fibre_core_crossings'] for r in rays]
        hp=[hcal_path(context,eta,2*math.pi*(i+.5)/nphi) for i in range(nphi)]
        scans.append({'abs_eta':eta,'rays':len(rays),'fcal_nuclear_lambda_min':min(vals),'fcal_nuclear_lambda_mean':sum(vals)/len(vals),'fcal_nuclear_lambda_max':max(vals),
                      'fibre_core_crossings_min':min(cores),'fibre_core_crossings_max':max(cores),'fraction_without_core_crossing':sum(v==0 for v in cores)/len(cores),
                      'hcal_envelope_path_mm_min':min(hp),'hcal_envelope_path_mm_max':max(hp)})
    return {'layout_id':name,'context_source_revision':context['source_revision'],'package_abs_z_mm':[front,end],'sampling_abs_z_mm':[sf,sb],
            'original_bore_radius_mm':p['original_bore_radius_mm'],'proposed_bore_radius_mm':m['bore_radius_mm'],
            'radial_amendment_mm':p['original_bore_radius_mm']-m['bore_radius_mm'],
            'remaining_rear_allocation_mm':p['original_back_abs_z_mm']-end,
            'clearances_mm':{'hcal':1000*h['endcap_inner_apothem_m']-m['outer_radius_mm'],'ecal_radial_where_axial_overlap':1000*bore_ec-m['outer_radius_mm'] if front<1000*ec['endcap_back_abs_z_m'] and end>1000*ec['endcap_front_abs_z_m'] else None,
                             'hypothetical_straight_pipe':m['bore_radius_mm']-1000*pipe['outer_radius_m']},
            'full_sampling_envelope_eta':[math.asinh(sb/m['sampling_outer_radius_mm']),math.asinh(sf/m['sampling_inner_radius_mm'])],
            'eta5_front_inner_margin_mm':sf/math.sinh(5)-m['sampling_inner_radius_mm'],
            'eta5_path_retained_R80_sampling_mm':max(0.,sb-max(sf,original_entry))*math.cosh(5)/math.sinh(5),
            'proper_negative_rotation':{'axis':'x','angle_deg':180.,'determinant':1},
            'service_route':{'axial_radius_interval_mm':[281.,287.],'begins_after_sensor_cassette_abs_z_mm':front+z['electronics_cooling'][0]+6.,
                             'radial_handoff_abs_z_mm':[1000*h['endcap_back_abs_z_m']+p['external_handoff_clearance_mm'],1000*h['endcap_back_abs_z_m']+p['external_handoff_clearance_mm']+p['external_handoff_length_mm']],
                             'handoff_radius_mm':p['handoff_radius_mm'],'status':'NEW empty service/load interface beyond HCAL; pipes and cable connector allocations explicit, complete radial manifold and engineering pending.'},
            'directional_sampling':scans,'claim':'FCAL finite-solid material paths; HCAL envelope lengths only. Phase sample excludes deliberately aligned seams, whose zero-material control is separately retained. No jets, efficiency or containment claim.'}


def thermal(model):
    c=model['config'];t=c['thermal'];pixels=16*len(model['channels'])
    out={'physical_sipm_pixels_per_end':pixels,'beam_deposition_heat_w':None}
    for tag in ('nominal','stress'):
        heat=pixels*(t[tag+'_pixel_current_a']*t['nominal_bias_v']+t[tag+'_fe_per_pixel_w'])+t[tag+'_control_per_end_w']
        detector_heat=heat
        heat/=t.get('conversion_efficiency',1.)
        out[tag]={'detector_subtotal_w':detector_heat,'conversion_efficiency':t.get('conversion_efficiency',1.),'pixel_bias_heat_w':pixels*t[tag+'_pixel_current_a']*t['nominal_bias_v'],
                  'front_end_heat_w':pixels*t[tag+'_fe_per_pixel_w'],'local_heat_per_end_w':heat,'both_ends_heat_w':2*heat,
                  'ideal_water_flow_per_end_kg_s':heat/(t['coolant_cp_j_per_kg_k']*t['coolant_rise_k'])}
    out['claim']='Planning current/power stresses, not measured device or EOL heat. Includes declared local conversion loss; excludes beam heat and external cooling plant; no hydraulic qualification.'
    return out


def collar_config(config):
    c=deepcopy(config);a=c.pop('collar')
    for key in ('module','fibres','readout','thermal'):
        c[key].update(a.get(key,{}))
    name=a['layout_id'];p=c['layouts'][name]
    c['layouts']={name:dict(p,package_front_abs_z_mm=a['package_front_abs_z_mm'],original_back_abs_z_mm=a['collector_abs_z_mm'][0])}
    c['component']='collar'
    return c


def report(model, contexts):
    rout=routing(model)
    return {'schema_version':1,'design_id':'DES-039','status':'DRAFT / PROTOTYPE','input_sha256':sha(HERE/'inputs.json'),'context_sha256':sha(HERE/'layout-contexts.json'),
            'model_sha256':sha(__file__),'inventory':inventory(model),'routing':rout,'thermal':thermal(model),
            'layouts':{name:layout_report(model,name,contexts[name]) for name in model['config']['layouts']},
            'controls':{'aligned_clamshell_seam_eta4':ray_sample(model,4.,math.pi/2,4553.2),
                        'note':'Exact phi=90/270 degree clamshell seams have zero matrix sampling. Report them separately, never hide them with azimuth averages.'},
            'not_run':['DD4hep/Geant4 full detector construction','Geant4 optical response and attenuation','Shower response / leakage / energy calibration','Complete 3D fanout fibre collision check','Radiation EOL / thermal hydraulic / mechanical and machine qualification']}
