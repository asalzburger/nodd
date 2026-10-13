"""DES031 compact standard sensor boards in independently serviced barrel slabs.

All dimensions in mm; standard library only; production geometry is untouched.
"""
import bisect
from collections import Counter
import json
import math
from pathlib import Path

from assembly import inventory
from edge_layout import rectangle
from model import ROOT, sha


def panel_layout(c,phase,board,pitch):
    panels=[];n=c['full_panels']//2;L=c['full_panel_length_mm'];gap=c['panel_gap_mm'];S=c['short_panel_length_mm']
    for i in range(-n,n+1):panels.append(dict(center_mm=i*(L+gap)+phase,length_mm=L,kind='full'))
    end=n*(L+gap)+L/2+gap+S/2
    panels.extend([dict(center_mm=-end+phase/2,length_mm=S+phase,kind='short'),dict(center_mm=end+phase/2,length_mm=S-phase,kind='short')])
    panels.sort(key=lambda q:q['center_mm']);rows=[]
    for i,p in enumerate(panels):
        p['index']=i;p['bay_sign']=-1 if p['center_mm']<0 else 1
        p['board_rows']=math.floor((p['length_mm']-2*c['panel_end_frame_mm']-c['service_bay_mm']+c['board_gap_mm'])/pitch)
        if p['board_rows']<1:raise ValueError('panel too short')
        p['row_centers_mm']=[p['center_mm']+(j-(p['board_rows']-1)/2)*pitch-(p['bay_sign']*c['short_panel_board_shift_mm'] if p['kind']=='short' else 0) for j in range(p['board_rows'])]
        p['bay_center_mm']=p['center_mm']+p['bay_sign']*(p['length_mm']/2-c['panel_end_frame_mm']-c['service_bay_mm']/2)
        if any(abs(z-p['center_mm'])+board/2>p['length_mm']/2-c['panel_end_frame_mm']+1e-8 or abs(z-p['bay_center_mm'])<(board+c['service_bay_mm'])/2+c['board_gap_mm']-1e-8 for z in p['row_centers_mm']):raise ValueError('board/bay separation')
        p['first_row']=len(rows);rows.extend(p['row_centers_mm'])
    return panels,rows,end+S/2


def build(config=None):
    c=config or json.loads((ROOT/'tools/calorimeter_hardware/barrel.json').read_text())
    base,_=inventory();a=base['config'];e=json.loads((ROOT/'tools/calorimeter_hardware/cassettes.json').read_text())['ecal']
    for key,value in c.items():
        if isinstance(value,(int,float)) and (not math.isfinite(value) or value<=0):raise ValueError('positive finite '+key)
    if c['full_panels']%2!=1:raise ValueError('odd full-panel count preserves a central slab')
    if c['full_panels']!=7 or a['sectors']!=16 or a['ecal_layers']!=48:raise ValueError('DES031 retained topology')
    if c['cooling_plate_mm']!=3:raise ValueError('inherited 4.8-7.8mm cold-plate stack')
    size=e['sensor_outer_mm'];board=size+2*c['board_margin_mm'];pitch=board+c['board_gap_mm']
    phases=c['layer_panel_phases_mm']
    if not phases or any(not math.isfinite(q) or abs(q)>pitch for q in phases):raise ValueError('panel phase')
    panels,rows,bound=panel_layout(c,0,board,pitch)
    if bound>a['barrel_half_z_mm']-a['end_allocation_mm']+1e-8:raise ValueError('axial allocation exceeded')
    if len(rows)*c['module_row_stride']>1024:raise ValueError('module ID range')
    cells=round(e['sensor_active_mm']/e['pitch_mm']);channels=cells*cells;asics=math.ceil(channels/e['asic_channels'])
    baseconfig=json.loads((ROOT/'tools/calorimeter_hardware/cassettes.json').read_text())
    layers=[];tangent=math.tan(math.pi/a['sectors']);summary=Counter();heat=0
    for layer in range(a['ecal_layers']):
        phase=phases[layer%len(phases)];panels,rows,_=panel_layout(c,phase,board,pitch)
        front=a['ecal_front_apothem_mm']+layer*base['regions'][0]['pitch_mm'];r_pcb=front+e['absorber_mm']+e['pcb_front_mm']
        halfwidth=r_pcb*tangent-a['seam_half_gap_mm']-a['edge_allocation_mm']
        cols=math.floor((2*halfwidth+c['board_gap_mm'])/pitch)
        if not 0<cols<=c['module_row_stride']:raise ValueError('column/ID capacity')
        x=[(j-(cols-1)/2)*pitch for j in range(cols)];modules=[];interfaces=[]
        for p in panels:
            lanes_per_interface=c['interface_capacity_channels']//(p['board_rows']*channels)
            if lanes_per_interface<1:raise ValueError('one lane exceeds interface capacity')
            for k in range(0,cols,lanes_per_interface):
                lane_indices=list(range(k,min(k+lanes_per_interface,cols)))
                interfaces.append(dict(index=len(interfaces),panel=p['index'],lanes=lane_indices,channels=len(lane_indices)*p['board_rows']*channels))
            for row,z in enumerate(p['row_centers_mm'],p['first_row']):
                for col,u in enumerate(x):modules.append(dict(index=row*c['module_row_stride']+col,row=row,column=col,panel=p['index'],center_mm=[u,z]))
        count=len(modules);installed=asics*e['asic_channels']*count
        lv=(installed*e['asic_continuous_W_channel']+len(interfaces)*e['interface_W'])/baseconfig['converter_efficiency']
        bias=count*channels*e['bias_V']*e['leakage_A_channel'];power=lv+bias
        # Full sensitive-face denominator includes slab seams, bays and edge allocations.
        face=2*((front+e['absorber_mm']+e['sensor_center_z_mm'])*tangent-a['seam_half_gap_mm'])*2*a['barrel_half_z_mm']
        layers.append(dict(index=layer,phase_mm=phase,panels=panels,row_centers_mm=rows,front_mm=front,columns=cols,column_centers_mm=x,modules=modules,interfaces=interfaces,channels=count*channels,powered_channels=installed,heat_W=power,active_face_fraction=count*e['sensor_active_mm']**2/face,pcb_side_clearance_mm=halfwidth-(cols*board+(cols-1)*c['board_gap_mm'])/2))
        summary['sensors']+=count*a['sectors'];summary['channels']+=count*channels*a['sectors'];summary['asics']+=count*asics*a['sectors'];summary['interfaces']+=len(interfaces)*a['sectors'];heat+=power*a['sectors']
    baseconfig=json.loads((ROOT/'tools/calorimeter_hardware/cassettes.json').read_text())
    summary.update(continuous_heat_W=heat,ideal_water_kg_s=heat/baseconfig['coolant_heat_capacity_J_kg_K']/baseconfig['coolant_rise_K'],minimum_active_face_fraction=min(p['active_face_fraction'] for p in layers),maximum_active_face_fraction=max(p['active_face_fraction'] for p in layers),minimum_pcb_side_clearance_mm=min(p['pcb_side_clearance_mm'] for p in layers))
    active=rectangle(-e['sensor_active_mm']/2,-e['sensor_active_mm']/2,e['sensor_active_mm'],e['sensor_active_mm'])
    report=dict(status='DRAFT / PROTOTYPE',config=c,assembly_config=a,ecal=e,centered_control_panels=panel_layout(c,0,board,pitch)[0],layers=layers,summary=dict(summary),active_mask_mm=active,board_size_mm=board,board_pitch_mm=pitch,layer_pitch_mm=base['regions'][0]['pitch_mm'],envelopes=base['envelopes'],excluded=['external coolant headers/manifolds and rail/absorber ports','LV/bias/data collection cables and connectors','fasteners, handling and engineering qualification','calorimetric response and particle flow'],source_sha256={**base['source_sha256'],str(Path(__file__).relative_to(ROOT)):sha(__file__),'tools/calorimeter_hardware/barrel.json':sha(ROOT/'tools/calorimeter_hardware/barrel.json')})
    return report,base


def crossings(report,eta,phi):
    a=report['assembly_config'];e=report['ecal'];N=a['sectors'];period=2*math.pi/N;angle=(phi+period/2)%period-period/2;half=e['sensor_active_mm']/2;hits=[]
    for p in report['layers']:
        rows=p['row_centers_mm']
        r=p['front_mm']+e['absorber_mm']+e['sensor_center_z_mm'];u=r*math.tan(angle);z=r/math.cos(angle)*math.sinh(eta)
        row=bisect.bisect_left(rows,z)
        for i in (row-1,row):
            if not 0<=i<len(rows) or abs(rows[i]-z)>half+1e-8:continue
            j=round(u/report['board_pitch_mm']+(p['columns']-1)/2)
            if 0<=j<p['columns'] and abs(p['column_centers_mm'][j]-u)<=half+1e-8:hits.append(p['index']);break
    return hits


def coverage(report):
    result=[]
    for eta in (0,.25,.5,.75,1,1.25,1.5,1.6,1.65,1.7,1.75,1.8,2):
        counts=[len(crossings(report,eta,(i+.5)*2*math.pi/360)) for i in range(360)]
        result.append(dict(eta=eta,phi_samples=360,minimum_layers=min(counts),maximum_layers=max(counts),mean_layers=sum(counts)/360,phi_fraction_at_least_40_layers=sum(q>=40 for q in counts)/360,zero_hit_phi_fraction=sum(q==0 for q in counts)/360))
    return dict(scope='Geometric plane/active-mask intersections, not efficiency; finite-thickness near ties needs native rays.',eta_samples=result,sector_center_eta0_layers=len(crossings(report,0,0)))


if __name__=='__main__':
    r,_=build();print(json.dumps(dict(summary=r['summary'],example_layer_panels=r['layers'][0]['panels'],coverage=coverage(r)),indent=2))
