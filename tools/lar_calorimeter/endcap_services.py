"""Physical DES033 rear support, cold-board slots and radial cooling branches."""
from collections import defaultdict
import math
from pathlib import Path
from barrel_geometry import I, rotation, ROOT, sha
from services import budget

def augment(report,m):
    b=budget();c=b['config'];ps=report['passive']
    for key,value in dict(board_face_mm=[350,75],board_radial_depth_mm=35,
        board_grid_pitch_mm=[500,80],board_gap_mm=10,nitrogen_pipe_id_mm=18,
        nitrogen_pipe_od_mm=20,endcap_stations_each=16).items():
        if c[key]!=value:raise ValueError('Unsupported endcap packing amendment: '+key)
    m.add('Copper',8.96,{'Cu':1.});m.add('Silicon',2.329,{'Si':1.})
    m.add('PrototypeNitrogenTwoPhase',c['nitrogen_effective_density_g_cm3'],{'N':1.})
    m.recipes['PrototypeNitrogenTwoPhase']['note']='NODD effective density0.02g/cm3 choice, no EOS/hydraulic qualification.'
    def add(name,material,kind,dims,center,frame=I,parent=None,role='service'):
        v=math.prod(dims.values()) if kind=='box' else math.pi*(dims['rmax']**2-dims['rmin']**2)*dims['length']
        p=dict(name=name,material=material,shape_kind=kind,dimensions_mm=dims,center_mm=center,frame=frame,
            role=role,volume_mm3=v,mass_g=v*m.recipes[material]['density_g_cm3']/1000)
        if parent:p['parent_name']=parent
        ps.append(p);return p
    board_count=0
    for side in (1,2):
        parent='rear_bath_'+str(side)
        add('rear_support_'+str(side),'Aluminium','tube',dict(rmin=400,rmax=2800,length=30),[0,0,-100],parent=parent,role='rear_support')
        for plane,z in enumerate((-67.5,-22.5,22.5)):
            for sector in range(16):
                phi=sector*2*math.pi/16;fr=rotation(phi)
                for row,n in enumerate((1,3,5,6,8,10)):
                    radius=585+355*row
                    for col in range(n):
                        u=(col-(n-1)/2)*80
                        name=f'ECFEB_{side}_{plane}_{sector}_{row}_{col}'
                        add(name,'LAr','box',dict(sx=350,sy=75,sz=35),
                            [radius*math.cos(phi)-u*math.sin(phi),radius*math.sin(phi)+u*math.cos(phi),z],fr,parent,'cold_board_envelope')
                        add(name+'_pcb','PCB','box',dict(sx=348,sy=73,sz=1.6),[0,0,-16.7],parent=name,role='cold_board')
                        add(name+'_cu','Copper','box',dict(sx=348,sy=73,sz=.105),[0,0,-15.8475],parent=name,role='cold_board')
                        add(name+'_spreader','Aluminium','box',dict(sx=348,sy=73,sz=5),[0,0,14],parent=name,role='cold_board')
                        for chip in range(8):
                            add(name+f'_chip{chip}','Silicon','box',dict(sx=20,sy=20,sz=1),[-140+40*chip,0,-14.5],parent=name,role='cold_board')
                        board_count+=1
        for i in range(48):
            phi=2*math.pi*i/48;cs,sn=math.cos(phi),math.sin(phi)
            # Proper rotation: tube local-z follows outward radial vector.
            fr=[[0,0,-1],[-sn,cs,0],[cs,sn,0]]
            center=[1597.5*cs,1597.5*sn,56]
            add(f'ECN2wall_{side}_{i}','lArCaloSteel','tube',dict(rmin=9,rmax=10,length=2355),center,fr,parent,'cooling_wall')
            add(f'ECN2fluid_{side}_{i}','PrototypeNitrogenTwoPhase','tube',dict(rmin=0,rmax=9,length=2355),center,fr,parent,'cooling_fluid')
    children=defaultdict(float)
    for p in ps:
        if 'parent_name' in p:children[p['parent_name']]+=p['volume_mm3']
    for p in ps:
        if p['name'] in children:
            p['displaced_volume_mm3']=children[p['name']]
            p['exclusive_volume_mm3']=p['volume_mm3']-children[p['name']]
            if p['exclusive_volume_mm3']<=0:raise ValueError('Overfull cold-board/bath mother')
    capacity=board_count//2*c['channels_per_board']
    if capacity<c['endcap_channel_budget_each']:raise ValueError('Insufficient endcap board capacity')
    b['physical_endcaps']=dict(board_slots_each=board_count//2,capacity_channels_each=capacity,
        actual_logical_channels_each=report['logical_cells_per_side'],cold_board_planes=3,cooling_branches_each=48,
        capacity_power_kW_scenarios_each=[capacity*p/1e6 for p in c['electronics_power_mW_per_channel_scenarios']],
        limitation='Slots and full-material board proxies include spare capacity. Cable/power budget uses650k planning channels. Full-population adverse power can exceed40kW cooling allowance; no thermal acceptance.')
    report['services']=b;report['source_sha256'].update(b['source_sha256'])
    report['source_sha256'][str(Path(__file__).relative_to(ROOT))]=sha(__file__)
    return report
