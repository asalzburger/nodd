"""Physical prototype supports/CFEB proxies/cooling inside LAr bath mothers.

All choices are documented in DES032. Bath mass excludes daughter displacement.
External service lanes are empty reservations, not material-filled geometry.
"""
from collections import defaultdict
import math
from pathlib import Path
from barrel_geometry import I, rotation, sha, ROOT
from services import budget


def augment(report, m):
    b = budget(); c = b['config']
    m.add('PrototypeNitrogenTwoPhase', c['nitrogen_effective_density_g_cm3'], {'N':1.})
    m.recipes['PrototypeNitrogenTwoPhase']['note']='NODD effective density hypothesis 0.02g/cm3; source flow scenario does not determine density. No EOS/transport claim.'
    m.add('Copper',8.96,{'Cu':1.})
    m.add('Silicon',2.329,{'Si':1.})
    passive = report['passive']
    def part(name, material, kind, dims, center, frame=I, parent='rear_bath', role='service'):
        volume = math.prod(dims.values()) if kind=='box' else math.pi*(dims['rmax']**2-dims['rmin']**2)*dims['length']
        p=dict(name=name,role=role,material=material,shape_kind=kind,dimensions_mm=dims,
            center_mm=center,frame=frame,parent_name=parent,volume_mm3=volume,
            mass_g=volume*m.recipes[material]['density_g_cm3']/1000)
        passive.append(p);return p
    r0=c['barrel_ring_inner_radius_mm']; r1=r0+c['barrel_ring_height_mm']; f=c['barrel_ring_flange_mm']
    for i in range(16):
        z=-3750+500*i
        for name,lo,hi,length in (('inner',r0,r0+f,100),('outer',r1-f,r1,100),('web',r0+f,r1-f,20)):
            part(f'Hring_{i}_{name}','Aluminium','tube',dict(rmin=lo,rmax=hi,length=length),[0,0,z],role='support')
    boards = []
    def board(name, inner, tangent, z, phi, end=False, parent='rear_bath'):
        sy,sz=(350,75) if end else (75,350)
        fr=rotation(phi);radius=inner+17.5
        center=[radius*math.cos(phi)-tangent*math.sin(phi),radius*math.sin(phi)+tangent*math.cos(phi),z]
        mother=part(name,'LAr','box',dict(sx=35,sy=sy,sz=sz),center,fr,parent,'cold_board_envelope')
        # Wet board envelope: explicit G10/Cu board, eight silicon package proxies,
        # aluminium heat-spreader. Remaining space retains LAr, not an air void.
        part(name+'_pcb','PCB','box',dict(sx=1.6,sy=sy-2,sz=sz-2),[-16.7,0,0],parent=name,role='cold_board')
        part(name+'_copper','Copper','box',dict(sx=.105,sy=sy-2,sz=sz-2),[-15.8475,0,0],parent=name,role='cold_board')
        part(name+'_spreader','Aluminium','box',dict(sx=5,sy=sy-2,sz=sz-2),[14,0,0],parent=name,role='cold_board')
        for chip in range(8):
            long=-140+40*chip
            center=[-14.5,long,0] if end else [-14.5,0,long]
            part(name+f'_chip{chip}','Silicon','box',dict(sx=1,sy=20,sz=20),center,parent=name,role='cold_board')
        boards.append(mother)
    for sector in range(16):
        phi=sector*2*math.pi/16
        for bank,inner in enumerate(c['board_bank_inner_radii_mm']):
            for col in range(12):
                for row in range(15):
                    board(f'CFEB_{sector}_{bank}_{col}_{row}',inner,-440+80*col,-3500+500*row,phi)
            for side in (-1,1):
                for col,tangent in enumerate((-190,190)):
                    board(f'CFEBend_{sector}_{bank}_{side}_{col}',inner,tangent,0,phi,True,f'end_bath_{side}')
    for side in (-1,1):
        for i in range(48):
            phi=2*math.pi*i/48;r=c['nitrogen_pipe_radius_mm']
            center=[r*math.cos(phi),r*math.sin(phi),side*1955]
            part(f'N2wall_{side}_{i}','lArCaloSteel','tube',dict(rmin=9,rmax=10,length=3900),center,role='cooling_wall')
            part(f'N2fluid_{side}_{i}','PrototypeNitrogenTwoPhase','tube',dict(rmin=0,rmax=9,length=3900),center,role='cooling_fluid')
    # Local child coordinates; full native containment/overlap gates validate the
    # physical geometry independently. Exclusive inventory conserves mother mass.
    children=defaultdict(float)
    for p in passive:
        if 'parent_name' in p:children[p['parent_name']]+=p['volume_mm3']
    for p in passive:
        if p['name'] in children:
            p['displaced_volume_mm3']=children[p['name']]
            p['exclusive_volume_mm3']=p['volume_mm3']-children[p['name']]
            if p['exclusive_volume_mm3']<=0:raise ValueError('Overfull service mother')
    capacity=len(boards)*c['channels_per_board']
    if capacity<c['barrel_channel_budget']:raise ValueError('CFEB slots fail reserved channel capacity')
    b['physical_barrel']=dict(board_envelopes=len(boards),capacity_channels=capacity,
        actual_logical_channels=report['logical_channels'],H_rings=16,cooling_half_branches=96,
        hottest_installed_capacity_kW_scenarios=[capacity*p/1e6 for p in c['electronics_power_mW_per_channel_scenarios']],
        approximation='Homogeneous electrode PCB plus separate CFEB copper/package/spreader proxies; no selected ASIC, connectors, seals, header or thermal contact qualification.')
    report['services']=b
    report['source_sha256'].update(b['source_sha256'])
    report['source_sha256'][str(Path(__file__).relative_to(ROOT))]=sha(__file__)
    return report
