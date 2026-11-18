"""Draw the opt-in gap prototype with empty route reservations and collar conflict."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def capture(model):
    d=copy.deepcopy(json.loads((ROOT/'docs/layouts/LAYOUT-002-restored.json').read_text()))
    source=d['source']
    source['baseline_context']={key:source.pop(key) for key in ('exporter_sha256','compact_sha256','materials_sha256','selection')}
    source['baseline_context']['named_input_sha256']=sha(ROOT/'docs/layouts/LAYOUT-002-restored.json')
    source['baseline_context']['tracker_visual_component_sha256']=source['component_sha256'].pop('tracker')
    for path,want in d['tracker']['matched_source_sha256'].items():
        if sha(ROOT/path)!=want:raise ValueError('Changed tracker context: '+path)
    b=json.loads((model/'barrel/expected.json').read_text());e=json.loads((model/'endcaps/expected.json').read_text());s=b['services']['config']
    for folder,r in [('barrel',b),('endcaps',e)]:
        for name,want in r['artifact_sha256'].items():
            if sha(model/folder/name)!=want:raise ValueError('Changed prototype artifact')
    if b['execution']['variant']!='LAR-GAP400-SIDE-EGRESS-2026-11-18':raise ValueError('Wrong gap variant')
    d.update(prototype_variant=b['execution']['variant'],status='Conditional400mm-gap PROTOTYPE; unconstructed external route reservations',
        scope='Actual isolated ECAL envelopes; tracker/magnet/HCAL are display context only. No constructed external routes; prospective collar conflict retained.',
        barrel=dict(**b['envelopes'],sampling_inner_radius_mm=b['config']['sampling_inner_radius_mm'],sampling_outer_radius_mm=b['config']['sampling_outer_radius_mm'],planes=b['config']['planes']),
        endcaps=dict(**e['envelopes'],wheels_mm=[[w['inner_radius_mm'],w['outer_radius_mm']] for w in e['wheels']]),
        route_reservation=b['services']['external_route_reservation'],
        services=dict(front_gap_mm=s['front_service_gap_mm'],rear_gap_mm=s['rear_service_gap_mm'],route_radius_mm=s['external_route_radius_mm']))
    if (d['hcal']['half_z_mm'],d['hcal']['endcap_front_mm'])!=(s['hcal_barrel_half_z_mm'],s['hcal_endcap_front_z_mm']):raise ValueError('HCAL context moved')
    d['source'].update(prototype_generator_sha256=sha(__file__),layout_generator_sha256=sha(ROOT/'tools/calorimeter_baselines/layout.py'),
        combined_scope='ECAL-only; retained tracker is visual context',combined_compact_sha256=sha(model/'combined/combined.xml'),combined_materials_sha256=sha(model/'combined/materials.xml'),
        selection=dict(selected_working_baseline=False,variant=b['execution']['variant'],variant_spec_sha256=sha(ROOT/'tools/lar_calorimeter/gap400-prototype.json')),
        geometry_execution={n:r['execution'] for n,r in [('barrel',b),('endcaps',e)]},
        geometry_source_sha256={n:r['source_sha256'] for n,r in [('barrel',b),('endcaps',e)]})
    for n,folder,file in [('lar-barrel','barrel','barrel.xml'),('lar-endcaps','endcaps','endcaps.xml')]:
        d['source']['component_sha256'][n]=dict(compact=sha(model/folder/file),materials=sha(model/folder/'materials.xml'))
    return d


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--model',type=Path);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.model:a.input.write_text(json.dumps(capture(a.model),indent=2)+'\n')
    path=ROOT/'tools/calorimeter_baselines/layout.py';spec=importlib.util.spec_from_file_location('baseline_layout',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(module.draw(json.loads(a.input.read_text())))
