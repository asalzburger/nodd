"""Twelvefold DES-039 vacuum prototype; SI, no detector material response."""
from pathlib import Path
import json
import math
import numpy as np
from .field import (concatenate_sources, rounded_racetrack_sources,
                    circular_loop_sources, evaluate, gauss_rule)

HERE = Path(__file__).resolve().parent
C_LIGHT = .299792458

def load_design(path=None):
    return json.loads(Path(path or HERE/'design.json').read_text())

def solenoid_parameters():
    return json.loads((HERE/'solenoid-input.json').read_text())['sources'][1]['content']['result']

def coil_source(config, name, index=0, current_Aturn=None, order=4, corners=16):
    c=config['coil_groups'][name]
    current = c['ampere_turns_per_coil'] if current_Aturn is None else current_Aturn
    if current is None:
        raise ValueError('current has not been normalized')
    return rounded_racetrack_sources(
        c['center_r_m'],c['center_z_m'],c['half_r_m'],c['half_z_m'],
        c['corner_radius_m'],math.radians(c['phi_offset_deg']+index*360/config['folds']),
        current,config['pack']['normal_m'],config['pack']['tangent_m'],order,corners,name)

def toroid_sources(config, currents=None, order=4, corners=16):
    return concatenate_sources(coil_source(config,name,k,
        None if currents is None else currents[name],order,corners)
        for name in config['coil_groups'] for k in range(config['folds']))

def solenoid_sources(radial_order=3,z_order=96,segments=192):
    """Uniform J in the pinned annular winding; polygon correction fixes B(0)=3 T.

    Total current of quadrature loops equals J times the pack cross section.
    The tiny polygon normalization is reported separately, not absorbed into the
    pinned design's physical ampere-turns or stored-energy number.
    """
    c=solenoid_parameters()
    ri,ro=c['cold_inner_radius_m'],c['winding_outer_radius_m']
    rr,wr=gauss_rule(ro-ri,radial_order); rr += (ri+ro)/2
    zz,wz=gauss_rule(c['cold_mass_length_m'],z_order)
    raw=concatenate_sources(circular_loop_sources(r,z,c['ampere_turns']*a*b,segments)
       for r,a in zip(rr,wr) for z,b in zip(zz,wz))
    factor=3.0/evaluate([[0,0,0]],raw)[0,2]
    return raw.scaled(factor),factor

def ray(eta,phi_deg):
    theta=2*math.atan(math.exp(-eta)); phi=math.radians(phi_deg)
    return np.array([math.sin(theta)*math.cos(phi),math.sin(theta)*math.sin(phi),math.cos(theta)])

def station_distances(eta,phi_deg,config):
    """Actual finite-surface crossings; seams/apertures cannot invent missing hits."""
    from .geometry import station_intersections
    hits=station_intersections(eta,phi_deg,config,check_path=False)
    if not hits['three_hits']:
        raise ValueError('ray does not intersect all three finite station envelopes')
    return np.linalg.norm(np.asarray(hits['points_m']),axis=1)

def response_points(eta,phi_deg,config,order=48):
    """Unequal-spacing interpolation sagitta, signed MDT precision bending.

    Middle displacement relative to straight interpolation between outer hits:
    s1<s2<s3, weight w(s)=(s-s1)(s3-s2)/(s3-s1) before s2,
    (s3-s)(s2-s1)/(s3-s1) after s2. Signal = .299792458*q/p ∫w Bphi ds.
    This is half the conventional min(s,L-s) kernel for equal spacing.
    """
    stations=station_distances(eta,phi_deg,config)
    a,b,c=stations; nodes,weights=np.polynomial.legendre.leggauss(order)
    ss=[]; ww=[]
    for lo,hi in [(a,b),(b,c)]:
        s=(hi+lo)/2+(hi-lo)*nodes/2
        w=np.where(s<=b,(s-a)*(c-b)/(c-a),(c-s)*(b-a)/(c-a))
        ss.extend(s); ww.extend(weights*(hi-lo)/2*w)
    phi=math.radians(phi_deg)
    return np.asarray(ss)[:,None]*ray(eta,phi_deg),np.array(ww),np.array([-math.sin(phi),math.cos(phi),0.]),stations

def signed_response(eta,phi_deg,config,sources,order=48):
    p,w,ephi,s=response_points(eta,phi_deg,config,order)
    b=evaluate(p,sources)
    integral=float(np.sum(w*(b@ephi)))
    # Uniform field yields integral = B*(s2-s1)*(s3-s2)/2.
    return {'integral_T_m2':integral,'B_sag_T':2*integral/((s[1]-s[0])*(s[2]-s[1])),
            'stations_s_m':s.tolist(),'span_m':float(s[-1]-s[0])}

def normalize_currents(config,order=4,corners=16):
    """Solve two signed MDT responses with symmetric +/- endcap currents."""
    src=toroid_sources(config,{name:1e6 for name in config['coil_groups']},order,corners)
    rows=[]
    for target in config['field_target'].values():
        p,w,ephi,s=response_points(target['eta'],target['phi_deg'],config)
        b=evaluate(p,src,by_group=True)
        response=np.einsum('n,ngj,j->g',w,b,ephi)*2/((s[1]-s[0])*(s[2]-s[1]))
        rows.append([response[0],sum(response[1:])])
    matrix=np.array(rows); desired=[t['sagitta_equivalent_B_T'] for t in config['field_target'].values()]
    currents=np.linalg.solve(matrix,desired)*1e6
    if min(currents)<=0:
        raise ValueError('target requires a reversed coil family')
    out={'barrel':float(currents[0]),'endcap_plus':float(currents[1]),'endcap_minus':float(currents[1])}
    for name,current in out.items(): config['coil_groups'][name]['ampere_turns_per_coil']=current
    return {'response_T_per_MAturn':matrix.tolist(),'target_B_sag_T':desired,'currents_Aturn':out,
            'pack_current_density_A_mm2':{name:i/(config['pack']['normal_m']*config['pack']['tangent_m']*1e6) for name,i in out.items()}}
