#!/usr/bin/env python3
"""Regenerate selected-baseline support/services inputs and technical drawings.

This explicit refresh never overwrites historical PR29/PR34 study evidence.
--update-config pins the generated inputs for the current DD4hep working default.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools/pixel_support'))
import mounting
import outward
import importlib.util
_spec=importlib.util.spec_from_file_location("pixel_support_services", ROOT/"tools/pixel_support/services.py")
services=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(services)


def read(path):return json.loads(path.read_text())
def write(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def refresh(output,draw=False,update_config=False):
    config=read(ROOT/'detector/config/pixel-barrel.json')
    support_path=ROOT/config['support_config']
    support=read(support_path);layout=outward.load_layout(support)
    mounts=read(ROOT/'tools/pixel_support/mounting.json')
    settings=read(ROOT/'tools/pixel_support/services.json')
    inputs=read(ROOT/'tools/module_layout/services_budget_inputs.json')
    summary,route,assembly=services.build(layout,support,mounts,inputs,settings)
    mounted=mounting.check_mounts(layout,support,mounts,assembly)
    if any(mounted['nominal_conflicts'].values()):
        raise RuntimeError('Mounting conflict: '+json.dumps(mounted['nominal_conflicts']))
    ref=summary['scenarios']['reference']
    if not ref['barrel_envelope_pass'] or ref['radial_peak_utilization']>1 or ref['axial_peak_utilization']>1 or summary['reference_extraction_body_conflicts']:
        raise RuntimeError('New reference service inventory does not fit inherited routing')
    section_settings=read(ROOT/'tools/pixel_support/outward.json')
    cross=outward.section(layout,support,section_settings)
    clearance=outward.screen(layout,support,section_settings,cross)
    if clearance['support_body_conflicts'] or clearance['support_support_conflicts']:
        raise RuntimeError('Outward support clearance conflict')
    layers=[]
    for layer in summary['layers']:
        lid=layer['layer_id'];bodies=[b for b in layout['bodies'] if b['layer_id']==lid]
        family=support['families'][bodies[0]['family']]
        power=layer['chips']*support['power_per_chip_W']
        heat=power/layer['staves']*support['stress_factor']*support['heat_fraction_max']
        quality=support['inlet_quality']+heat/(family['flow_g_s']*support['latent_heat_J_g'])
        layers.append(dict(layer=lid,nominal_power_W=power,stave_stress_W=power/layer['staves']*support['stress_factor'],
                           flow_per_circuit_g_s=family['flow_g_s'],exit_quality_stress_imbalanced=quality,
                           exit_quality_limit=support['maximum_quality'],heat_balance_pass=quality<=support['maximum_quality'],
                           minimum_heat_balance_flow_g_s=heat/((support['maximum_quality']-support['inlet_quality'])*support['latent_heat_J_g']),
                           passive_z_mm=outward.stave_span(bodies,support)))
    thermal=dict(status='PROTOTYPE heat balance only; configured flows unchanged; failed quality ceiling retained',layers=layers,
                 nominal_power_W=sum(l['nominal_power_W'] for l in layers),hydraulic_qualification=False)
    producers=[support_path,ROOT/'tools/pixel_support/mounting.json',ROOT/'tools/pixel_support/services.json',ROOT/'tools/module_layout/services_budget_inputs.json']
    producers += [ROOT/'tools/pixel_support'/n for n in ['outward.py','mounting.py','services.py']]
    producers += [ROOT/'tools/module_layout'/n for n in ['geometry.py','services_geometry.py','services_budget.py']]
    producers += [Path(__file__)]
    provenance=dict(baseline=support['baseline'],baseline_sha256=support['baseline_sha256'],
        source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=sys.argv,python=sys.version,producer_files_sha256={str(p.relative_to(ROOT)):sha(p) for p in producers})
    summary['provenance']=provenance;route['provenance']=provenance
    output.mkdir(parents=True,exist_ok=True)
    write(output/'screening.json',summary);write(output/'mounting.json',mounted);write(output/'outward.json',clearance);write(output/'thermal.json',thermal)
    (output/'routing.json.gz').write_bytes(gzip.compress(json.dumps(route,sort_keys=True,separators=(',',':')).encode(),mtime=0))
    if draw:
        for folder in ['outward','mounted','services']:(output/folder).mkdir(exist_ok=True)
        outward.draw(cross,clearance,output/'outward')
        mounting.draw(layout,support,mounts,assembly,mounted,output/'mounted')
        services.draw(summary,route,assembly,support,settings,layout,output/'services')
    if update_config:
        config.update(support_config=str(support_path.relative_to(ROOT)),routing=str((output/'routing.json.gz').relative_to(ROOT)),
                      service_summary=str((output/'screening.json').relative_to(ROOT)))
        pins=[support_path,ROOT/support['baseline'],ROOT/'tools/pixel_support/mounting.json',ROOT/'tools/pixel_support/services.json',ROOT/'tools/module_layout/review_models.json',ROOT/'tools/module_layout/services_budget_inputs.json',output/'routing.json.gz',output/'screening.json']
        config['input_sha256']={str(p.relative_to(ROOT)):sha(p) for p in pins}
        write(ROOT/'detector/config/pixel-barrel.json',config)
    print(json.dumps(dict(counts=summary['totals'],reference_services=ref,thermal=thermal),indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'docs/validation/DES-012/PR34/engineering');p.add_argument('--draw',action='store_true');p.add_argument('--update-config',action='store_true');a=p.parse_args();refresh(a.output.resolve(),a.draw,a.update_config)
