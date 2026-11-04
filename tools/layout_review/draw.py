"""Compact reviewer R-Z views on common equal-scale axes; envelope illustration."""
import hashlib,html,json,math
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'docs/layouts/review'
def drawing(data):
    lar=data['layout_id']=='LAYOUT-002'
    scale,left,base=48,135,345
    x=lambda z:left+(z+8.3)*scale
    y=lambda r:base-r*scale
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="430" viewBox="0 0 1100 430">',
        '<rect width="1100" height="430" fill="white"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#24344a;font-size:20px}.label{font-size:21px}.small{font-size:18px}</style>',
        '<text x="135" y="32" font-weight="bold">'+html.escape(data['layout_id']+' | '+('ALLEGRO LAr' if lar else 'Si-W'))+'</text>']
    def text(z,r,label,rotate=False):
        tx,ty=x(z),y(r);tr=f' transform="rotate(-90 {tx:.3f} {ty:.3f})"' if rotate else ''
        out.append(f'<text x="{tx:.3f}" y="{ty:.3f}" text-anchor="middle" dominant-baseline="middle"{tr}>{html.escape(label)}</text>')
    def box(a,b,r0,r1,fill,stroke='#64748b',dash=None):
        if a>=b or r0>=r1:raise ValueError('Nonpositive envelope')
        ds=f' stroke-dasharray="{dash}"' if dash else ''
        out.append(f'<rect x="{x(a):.3f}" y="{y(r1):.3f}" width="{(b-a)*scale:.3f}" height="{(r1-r0)*scale:.3f}" fill="{fill}" stroke="{stroke}" stroke-width="1.4"{ds}/>')
    for z in range(-8,9,2):
        out.append(f'<path d="M{x(z):.3f},{y(5):.3f} V{base}" stroke="#e2e8f0"/>');text(z,-.5,str(z))
    for r in range(6):
        out.append(f'<path d="M{left},{y(r):.3f} H{x(8.3):.3f}" stroke="#e2e8f0"/><text x="{left-23}" y="{y(r)+7:.3f}" text-anchor="end">{r}</text>')
    out.append('<text x="58" y="225" text-anchor="middle" transform="rotate(-90 58 225)">r [m]</text>')
    text(0,-1.10,'z [m] | equal scale; same axes for both candidates')
    h=data['hcal'];e=data['ecal'];t=data['tracker'];m=data['solenoid']
    box(-h['barrel_half_length_m'],h['barrel_half_length_m'],h['barrel_front_apothem_m'],h['barrel_outer_apothem_m'],'#edf1f6',dash='7 5')
    text(0,(h['barrel_front_apothem_m']+h['barrel_outer_apothem_m'])/2,'HCAL outline')
    for side in (-1,1):
        a,b=h['endcap_front_abs_z_m'],h['endcap_back_abs_z_m']
        box(a if side>0 else -b,b if side>0 else -a,h['endcap_inner_apothem_m'],h['endcap_outer_apothem_m'],'#edf1f6',dash='7 5')
        text(side*(a+b)/2,2.2,'HCAL',True)
    if lar:
        half=e['barrel_half_length_m'];r0=e['barrel_inner_radius_m'];r1=e['barrel_outer_radius_m']
        box(-half,half,r1,h['barrel_front_apothem_m'],'#d3edf2')
        for side in (-1,1):
            a,b=e['endcap_front_abs_z_m'],e['endcap_back_abs_z_m']
            box(a if side>0 else -b,b if side>0 else -a,e['endcap_outer_radius_m'],h['barrel_front_apothem_m'],'#d3edf2')
            for lo,hi,top in [(half,a,h['barrel_front_apothem_m']),(b,h['endcap_front_abs_z_m'],h['barrel_outer_apothem_m'])]:
                box(lo if side>0 else -hi,hi if side>0 else -lo,.30,top,'#e8f5f7')
    else:
        half=e['barrel_flange_half_length_m'];r0=e['barrel_front_apothem_m'];r1=e['barrel_outer_apothem_m']
        s=data['services']
        box(-h['barrel_half_length_m'],h['barrel_half_length_m'],s['inner_radius_m'],s['outer_radius_m'],'#d3edf2')
        for side in (-1,1):
            lo,hi=e['endcap_back_abs_z_m'],h['endcap_front_abs_z_m']
            box(lo if side>0 else -hi,hi if side>0 else -lo,.30,s['egress_radius_m'],'#e8f5f7')
    box(-half,half,r0,r1,'#f6d78e','#aa7c26');text(0,(r0+r1)/2,('LAr' if lar else 'Si-W')+' barrel')
    for side in (-1,1):
        a,b=e['endcap_front_abs_z_m'],e['endcap_back_abs_z_m']
        ri=e['endcap_inner_radius_m'] if lar else e['endcap_inner_apothem_m']
        ro=e['endcap_outer_radius_m'] if lar else e['endcap_outer_apothem_m']
        box(a if side>0 else -b,b if side>0 else -a,ri,ro,'#f6d78e','#aa7c26')
        text(side*(a+b)/2,1.15,'ECAL',True)
    box(-m['vessel_half_length_m'],m['vessel_half_length_m'],m['vessel_inner_radius_m'],m['vessel_outer_radius_m'],'#c2aedb','#9478ad')
    for g in t['sensitive_groups']:
        box(g['z_min_m'],g['z_max_m'],g['r_min_m'],g['r_max_m'],'#319778','#319778')
    out.append(f'<path d="M{x(-4):.3f},{y(data['beam_pipe']['display_radius_m']):.3f} H{x(4):.3f}" stroke="#46566f"/>')
    if data.get('forward_reservations'):
        for f in data['forward_reservations']:
            for side in (-1,1):
                a,b=f['z_min_abs_m'],f['z_max_abs_m']
                box(a if side>0 else -b,b if side>0 else -a,f['r_min_m'],f['r_max_m'],'#fff5f5','#bf4257','4 3')
    out.append('<text x="135" y="59" class="small">Gold: ECAL | Purple: 3 T magnet | Green: tracker | Dashed gray: HCAL</text>')
    out.append('<text x="135" y="85" class="small">Cyan: service space | Red: empty forward reservations</text>')
    out.append('<metadata>'+html.escape(json.dumps(dict(layout_id=data['layout_id'],generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='Envelope illustration; circular LAr radii / sector-centre SiW and HCAL apothems.')) )+'</metadata>')
    out.append('</svg>');return '\n'.join(out)+'\n'
if __name__=='__main__':
    for name in ('layout001','layout002'):
        d=json.loads((BASE/(name+'.json')).read_text())
        svg=BASE/'figures'/(name+'-rz.svg');svg.write_text(drawing(d))
        subprocess.run(['rsvg-convert','-w','3300','-o',str(svg.with_suffix('.png')),str(svg)],check=True)
        print('Wrote',svg)
