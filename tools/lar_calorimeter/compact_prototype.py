"""Opt-in isolated compact LAr ECAL; maintained layout defaults remain unchanged."""
import argparse
import json
from pathlib import Path
import subprocess
import shutil

from barrel_geometry import ROOT, build as barrel_build, sha
import barrel_export
import barrel_services
from endcap_geometry import build as endcap_build
import endcap_export
import endcap_services

SPEC = Path(__file__).with_name('compact-prototype.json')


def configs():
    spec = json.loads(SPEC.read_text())
    barrel = json.loads((ROOT/'tools/lar_calorimeter/barrel.json').read_text())
    endcap = json.loads((ROOT/'tools/lar_calorimeter/endcaps.json').read_text())
    services = json.loads((ROOT/'tools/lar_calorimeter/services.json').read_text())
    front = spec['warm_bore_mm'] + sum(barrel[k] for k in
        ('front_warm_mm', 'front_vacuum_mm', 'front_cold_mm', 'front_bath_mm'))
    scale = front/barrel['sampling_inner_radius_mm']
    back = barrel['sampling_outer_radius_mm']*scale
    barrel.update(warm_inner_radius_mm=spec['warm_bore_mm'], sampling_inner_radius_mm=front,
        sampling_outer_radius_mm=back, segments_mm=[v*scale for v in barrel['segments_mm']],
        planes=spec['barrel_planes'], lead_mm=spec['barrel_lead_mm'], rear_bath_mm=spec['barrel_rear_bath_mm'])
    shift = spec['front_service_gap_mm']-services['front_service_gap_mm']
    extra = spec['endcap_sampling_depth_mm']-endcap['sampling_depth_mm']
    for key in ('sampling_front_z_mm', 'warm_front_z_mm', 'cold_front_z_mm'):
        endcap[key] += shift
    for key in ('warm_back_z_mm', 'cold_back_z_mm'):
        endcap[key] += shift+extra
    endcap['sampling_depth_mm'] = spec['endcap_sampling_depth_mm']
    services.update(board_bank_inner_radii_mm=[back+v for v in spec['barrel_board_bank_offsets_mm']],
        barrel_board_columns=spec['barrel_board_columns'], barrel_ring_inner_radius_mm=back+5,
        nitrogen_pipe_radius_mm=back+spec['barrel_nitrogen_offset_mm'],
        actual_bend_radii_mm=spec['actual_bend_radii_mm'], front_service_gap_mm=spec['front_service_gap_mm'],
        hcal_barrel_half_z_mm=endcap['warm_back_z_mm'],
        hcal_endcap_front_z_mm=endcap['warm_back_z_mm']+services['rear_service_gap_mm'])
    return spec, barrel, endcap, services


def export(out):
    out.mkdir(parents=True, exist_ok=False)
    spec, barrel, endcap, services = configs()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True))
    reports = {}
    for name, config, build, exporter, service in (
        ('barrel', barrel, barrel_build, barrel_export, barrel_services),
        ('endcaps', endcap, endcap_build, endcap_export, endcap_services)):
        folder=out/name;folder.mkdir();report, materials=build(config)
        service.augment(report, materials, services)
        report['materials']=materials.recipes;exporter.totals(report)
        exporter.write(folder/'materials.xml', materials.root)
        exporter.compact(report, folder, real_periods=True)
        source_files=[Path(__file__),SPEC,Path(exporter.__file__),Path(service.__file__),
            ROOT/'tools/lar_calorimeter/placement.py',ROOT/'tools/lar_calorimeter/services.py',
            ROOT/'tools/lar_calorimeter/services.json',ROOT/'prototypes/calorimeter/LArBarrel.cpp',
            ROOT/'prototypes/calorimeter/LArEndcap.cpp']
        report['source_sha256'].update({str(p.relative_to(ROOT)):sha(p) for p in source_files})
        report['execution']=dict(commit=revision,dirty=dirty,variant=spec['id'])
        compact=folder/('barrel.xml' if name=='barrel' else 'endcaps.xml')
        report['artifact_sha256']={p.name:sha(p) for p in (compact,folder/'materials.xml')}
        (folder/'expected.json').write_text(json.dumps(report,indent=2)+'\n')
        reports[name]=report
    from combined_native import build as combine
    combined=out/'combined'
    record=combine(out/'barrel/barrel.xml',out/'barrel/expected.json',
                   out/'endcaps/endcaps.xml',out/'endcaps/expected.json',combined)
    # The ECAL-only composer retains unprefixed world Vacuum/Air definitions;
    # the tracker+ECAL baseline composer assumes a tracker provides these.
    shutil.copyfile(combined/'combined.xml',combined/'detector.xml')
    metadata=combined/'baseline.json'
    value=dict(layout='LAYOUT-002',status='isolated PROTOTYPE, not maintained layout',
        compact_sha256=sha(combined/'detector.xml'),materials_sha256=sha(combined/'materials.xml'),
        variant=spec['id'],constructed=['isolated compact LAr barrel','isolated deepened LAr endcaps'],
        variant_spec_sha256=sha(SPEC),source_revision=revision,
        components=record['components'],raw_sensitive_ids=sum(r['physical_sensitive_elements'] for r in reports.values()))
    metadata.write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(dict(variant=spec['id'],raw_sensitive_ids=value['raw_sensitive_ids'],
        barrel=reports['barrel']['envelopes'],endcaps=reports['endcaps']['envelopes'],
        logical_channels=sum(r['logical_channels'] for r in reports.values()))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    export(p.parse_args().output)
