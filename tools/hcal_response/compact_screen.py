"""Screen proposed axial HCAL coordinates without exporting or changing geometry.

Finite absorber calculations are for phi=10 degrees, away from sector/quarter
seams. They exclude sensitive tiles, service material and shower development.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
import model
sys.path.insert(0, str(ROOT/'tools/lar_calorimeter'))
import compact_prototype as lar
import services


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def steel_path(c, eta):
    """Actual plate intervals, phi10; analytically clipped away from all seams."""
    phi=math.radians(10);co=math.cos(phi);s=math.sinh(abs(eta));ch=math.cosh(eta)
    b,e=c['barrel'],c['endcap'];pitch=c['steel_mm']+12+c['installation_gap_mm']
    max_rho=(b['half_z_mm']-b['end_flange_mm'])/s
    barrel=sum(max(0,min((b['front_apothem_mm']+pitch*i+c['steel_mm'])/co,max_rho)
                    -(b['front_apothem_mm']+pitch*i)/co)*ch for i in range(c['layers']))
    zlo=(e['inner_apothem_mm']+e['inner_frame_mm'])/co*s
    zhi=(e['outer_apothem_mm']-e['outer_frame_mm'])/co*s
    endcap=sum(max(0,min(e['front_abs_z_mm']+pitch*i+c['steel_mm'],zhi)
                    -max(e['front_abs_z_mm']+pitch*i,zlo))*ch/s for i in range(c['layers']))
    return dict(barrel_mm=barrel,endcap_mm=endcap,total_mm=barrel+endcap)


def screen():
    c=json.loads(model.CONFIG.read_text())
    context_path=ROOT/'docs/layouts/LAYOUT-002-DES046-gap400.json'
    context=json.loads(context_path.read_text())
    receipt_path=ROOT/'docs/validation/hcal50-edge/geometry.json'
    receipt=json.loads(receipt_path.read_text())
    for path,wanted in receipt['source_sha256'].items():
        if sha(ROOT/path)!=wanted:
            raise ValueError('Changed validated HCAL source: '+path)
    spec,b,e,s=lar.configs(ROOT/'tools/lar_calorimeter/gap400-prototype.json')
    if e['warm_back_z_mm']!=context['endcaps']['warm_back_z_mm']:
        raise ValueError('Changed moved ECAL rear')
    current_layers=model.barrel_layout(c)
    old_rows=len(current_layers[0]['rows_mm'])
    old_barrel_tiles=(receipt['counts']['sensitive_tiles']
                      -receipt['counts']['endcap_carriers']*model.common()[0]['sensitive_count'])
    candidates=[]
    for name,half in [('current',c['barrel']['half_z_mm']),('exact_alignment',5660),
                      ('allowance20',5680),('preserve_allowance80',5740)]:
        q=copy.deepcopy(c);q['barrel']['half_z_mm']=half
        front=(c['endcap']['front_abs_z_mm'] if name=='current' else half+s['rear_service_gap_mm'])
        depth=model.validate_config(c)
        q['endcap'].update(front_abs_z_mm=front,back_abs_z_mm=front+depth)
        model.validate_config(q);layers=model.barrel_layout(q)
        rows=len(layers[0]['rows_mm']);height=model.common()[0]['fixture']['carrier_size_mm'][1]
        edge=max(abs(y+layer['axial_phase_mm'])+height/2 for layer in layers for y in layer['rows_mm'])
        carrier_count=q['sectors']*sum(layer['carriers_per_sector'] for layer in layers)
        route=copy.deepcopy(s);route.update(hcal_barrel_half_z_mm=half,hcal_endcap_front_z_mm=front)
        budget=services.budget(route)
        path_points={str(eta):steel_path(q,eta) for eta in (.8,.9,.94,1.,1.1,1.3)}
        minimum=min((steel_path(q,.8+i*.00001)['total_mm'],.8+i*.00001) for i in range(45001))
        candidates.append(dict(name=name,barrel_half_z_mm=half,endcap_front_mm=front,
            endcap_back_mm=front+depth,overall_length_saved_mm=2*(c['endcap']['back_abs_z_mm']-front-depth),
            barrel_rows=rows,barrel_carriers=carrier_count,
            barrel_tiles=old_barrel_tiles*rows//old_rows,
            cassette_to_flange_mm=half-q['barrel']['end_flange_mm']-edge,
            rear_ecal_interval_mm=front-e['warm_back_z_mm'],depth_mm=depth,
            service_reservation=budget['external_route_reservation'],
            largest_rear_bend_bound_mm=max(v['rear_two_face_bound_mm'] for v in budget['bends'].values()),
            coarse_full_depth_eta=[math.asinh(half/q['barrel']['outer_apothem_mm']),
                                   math.asinh((front+depth)/q['endcap']['outer_apothem_mm'])],
            phi10_steel_paths=path_points,
            phi10_minimum_steel_eta_08_to_125_step_1e5=dict(steel_mm=minimum[0],eta=minimum[1])))
    negative_checks=[]
    for name,half,front,window in [('exit400',5740,6140,400),('barrel_only_alignment',4100,4600,500)]:
        route=copy.deepcopy(s)
        route.update(hcal_barrel_half_z_mm=half,hcal_endcap_front_z_mm=front,rear_service_gap_mm=window)
        try:
            services.budget(route)
        except ValueError as error:
            negative_checks.append(dict(name=name,status='rejected as expected',reason=str(error)))
        else:
            raise AssertionError('Invalid service case unexpectedly passed: '+name)
    sources=set(receipt['source_sha256'])|set(context['source']['current_ecal_source_sha256'])|{
        str(context_path.relative_to(ROOT)),str(receipt_path.relative_to(ROOT)),
        'tools/lar_calorimeter/services.py','tools/lar_calorimeter/services.json',
        'tools/lar_calorimeter/compact_prototype.py'}
    return dict(status='DRAFT / proposal screen; no geometry adoption or native transport',
        python_version=sys.version.split()[0],
        input_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        generator_sha256=sha(__file__),source_sha256={p:sha(ROOT/p) for p in sorted(sources)},
        ecal_warm_back_mm=e['warm_back_z_mm'],candidates=candidates,
        negative_checks=negative_checks,
        rejected_barrel_only_alignment=dict(barrel_half_z_mm=4100,endcap_front_mm=4600,
            ecal_endcap_axial_envelope_overlap_mm=1060,
            reason='Full HCAL endcaps at4600mm intersect ECAL endcaps4500–5660mm at shared radii.'),
        limits=['Services are empty reservations; the490mm bend bound is not an installed route or engineering minimum.',
                'Exact5660mm alignment has zero cassette/flange clearance;20mm is an unsigned new allowance;80mm preserves the current model allowance.',
                'Phi10 steel paths use actual30mm plate intervals,20mm flange exclusion and310/5690mm endcap steel apothems; avoid seams; no active tiles or shower response.',
                'Eta extrema are sampled at1e-5; not all-phi acceptance bounds. Endcap bore and forward/muon interfaces still need full validation.',
                'Model checks/packing predictions do not replace native construction, material/ID/overlap/path checks or matched pion validation.'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=screen();a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print('Four in-memory candidates screened; no detector config or native artifacts modified.')
