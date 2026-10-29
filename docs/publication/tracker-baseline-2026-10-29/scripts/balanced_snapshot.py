#!/usr/bin/env python3
"""Extract/check the selected balanced TDR; never executes native simulation.

Extraction uses maintained pixel expected.json plus compact XML. The imported
historical data supply invariant local frames/technology, checked against every
current barrel/endcap module centre. --check needs only the standard library.
"""
import argparse
import copy
import hashlib
import gzip
import json
import math
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]
REPO = REPORT.parents[2]
DATA = REPORT / 'data'
PRESERVE = ['chapters/short-strip-detector.tex', 'chapters/long-strip-detector.tex',
            'chapters/strip-references.tex', 'generated/strip-disc-rows.tex'] + [
    'figures/' + name + '.pdf' for name in ('short-strip-barrel', 'short-strip-stave',
    'short-strip-endcap', 'long-strip-barrel', 'long-strip-anchors', 'long-strip-endcap')]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    p=Path(path)
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def value(s):
    # This compact deliberately uses simple literal*mm/rad unit expressions.
    number, unit = s.split('*')
    if unit not in ('mm', 'rad'):
        raise ValueError(f'Unsupported dimensional expression: {s}')
    return float(number)


def close(a, b, label):
    if len(a) != len(b) or any(abs(x-y) > 2e-9 for x, y in zip(a, b)):
        raise ValueError('Local structure changed: ' + label)


def extract(expected_path, compact_path, materials_path, native_path=None, tracker_path=None):
    expected = read(expected_path)
    p = copy.deepcopy(read(DATA / 'pixel-layout.json'))
    s = copy.deepcopy(read(DATA / 'pixel-endcap-baseline.json'))
    editorial = copy.deepcopy(read(DATA / 'pixel-editorial-routing.json'))
    cfg = expected['provenance']['combined_config']
    placement = expected['provenance']['placement']
    if placement['id'] != 'balanced' or placement['pixel_barrel_radii_mm'] != [31.5, 57, 96, 182]:
        raise ValueError('Not the selected balanced geometry')
    if expected['counts']['module'] != 5666 or expected['counts']['sensitive'] != 12410:
        raise ValueError('Unexpected maintained pixel inventory')
    xml = ET.parse(compact_path).getroot()
    barrel = xml.find('detectors')[0]
    modules = {(q['ids']['system'], q['ids']['layer'], q['ids']['module']): q
               for q in expected['entities'] if q['role'] == 'module'}
    original_radii=[b['layer']['r_m']*1000 for b in p['barrels']]
    barrel_module_checks = 0
    for i, b in enumerate(p['barrels'], 1):
        nominal = placement['pixel_barrel_radii_mm'][i-1]
        delta = nominal - b['layer']['r_m'] * 1000
        b['layer']['r_m'] = nominal / 1000
        for key in ('columns', 'rows'):
            for q in b[key]:
                old = q['center_mm']
                target = modules[(1, i, q['module_id'])]['center_mm']
                close([old[j] + delta*q['n'][j] for j in range(3)], target, f'barrel {q["module_id"]}')
                q['center_mm'] = target
                barrel_module_checks += 1
        ring = p['rings']['layers'][i-1]
        element = barrel.find(f"layer[@id='{i}']/ring")
        ring['nominal_radius_mm'] = nominal
        ring['ring_inner_radius_mm'] = value(element.attrib['rmin'])
        ring['ring_outer_radius_mm'] = value(element.attrib['rmax'])
        ring['stave_outer_radius_mm'] += delta
        ring['ring_mass_g'] = sum(q['mass_g'] for q in expected['entities'] if q['role']=='ring' and q['name'].startswith(f'layer{i}_'))
        ring.pop('foot_envelope_mass_g',None)
    frozen_path='docs/validation/DES-013-pixel-z/data/packed-200um/layout.json.gz'
    frozen=read(REPO/frozen_path)
    full_barrel_checks=0
    for q in frozen['bodies']:
        if q['subsystem']!='pixel' or q['region']!='barrel': continue
        layer=int(q['layer_id'].rsplit('B',1)[1])
        original_radius=original_radii[layer-1]
        delta=placement['pixel_barrel_radii_mm'][layer-1]-original_radius
        target=modules[(1,layer,q['module_id'])]['center_mm']
        close([q['center_mm'][j]+delta*q['n'][j] for j in range(3)],target,f'full barrel {q["module_id"]}')
        full_barrel_checks+=1
    if full_barrel_checks!=3050: raise ValueError('Incomplete barrel module validation')
    services = {q.attrib['name']: q.attrib for q in barrel.findall('service')}
    for rows in (p['routing']['longitudinal'], editorial['column_zero_positive'], editorial['terminal_positive']):
        for q in rows:
            a = services['cable_' + q['id']]
            q['r_min_mm'] = value(a['rmin']); q['r_max_mm'] = value(a['rmax'])
            q['phi_width_rad'] = value(a['phi_width']); q['phi_center_rad'] = value(a['phi'])
    templates = {d['index']: d for d in s['discs']}
    discs = []
    for service in expected['service_accounting']['endcap']['discs']:
        if service['side'] != 1:
            continue
        donor = service['donor_layer']; d = copy.deepcopy(templates[donor])
        delta = service['datum_mm'] - d['z_mm']
        d.update(index=service['disc'], donor_layer=donor, z_mm=service['datum_mm'],
                 modules=service['modules'], chips=service['chips'], cooling=service['cooling'])
        current = [q for q in expected['entities'] if q['role'] == 'module' and
                   q['ids']['system'] == 3 and q['ids']['layer'] == d['index']]
        lookup = {q['template_module_id']: q for q in current}
        if len(lookup) != d['modules'] or len(d['bodies']) != d['modules']:
            raise ValueError('Disc body inventory mismatch')
        for m in d['bodies']:
            target = lookup[m['module_id']]
            close([m['center_mm'][0], m['center_mm'][1], m['center_mm'][2]+delta],
                  target['center_mm'], f'disc {d["index"]} template {m["module_id"]}')
            m['center_mm'] = target['center_mm']; m['source_module_id'] = target['source_module_id']
        discs.append(d)
    s['discs'] = sorted(discs, key=lambda d: d['z_mm'])
    if [d['index'] for d in s['discs']] != [1, 2, 10, 3, 4, 5, 6, 7, 8, 9]:
        raise ValueError('Unexpected physical station order')
    s['transport_P'] = expected['service_accounting']['endcap']['transport_P']
    s['counts'] = dict(barrel_modules=3050, barrel_chips=6794,
                      endcap_modules=2*sum(d['modules'] for d in discs),
                      endcap_chips=2*sum(d['chips'] for d in discs),
                      combined_modules=expected['counts']['module'],
                      combined_chips=expected['counts']['sensitive'],
                      endcap_circuits=2*sum(d['cooling']['number_circuits'] for d in discs))
    total_mass = sum(v['mass_g'] for v in expected['material_totals'].values())
    transport_mass = sum(q['mass_g'] for q in expected['entities'] if q['role'] == 'transport_services')
    s['mass_g'] = dict(combined=total_mass, downstream_transport=transport_mass)
    s['native_evidence'] = None
    s['parent_revision'] = expected['provenance']['source_revision']
    s['status'] = 'Human-selected balanced working simulation baseline; engineering qualification remains open'
    p['discs'] = s['discs']
    p={k:p[k] for k in ('barrels','module','support','endcap','mounting','rings','routing','service_summary','discs')}
    s['config']=cfg
    # Keep only fields used by current rendering; historical snapshots stay separate.
    data = dict(schema_version=1, id='balanced', pixel=p, endcap=s, editorial=editorial,
                counts=s['counts'], barrel_representative_centre_checks=barrel_module_checks,
                barrel_complete_centre_checks=full_barrel_checks,
                signed_logical_pixel_layers=24, tracker_discs_per_end=22,
                classification='NODD DESIGN CHOICE; exact maintained-export extraction',
                material_scope=expected['provenance']['service_scope'])
    if tracker_path:
        tracker=read(tracker_path)
        sensitive=[q for q in tracker['entities'] if q['role']=='sensitive']
        if len(sensitive)!=46250: raise ValueError('Unexpected full-tracker sensitive inventory')
        systems={}
        for q in sensitive:
            system=q['ids']['system']; systems[str(system)]=systems.get(str(system),0)+1
        if systems!={'1':6794,'2':2808,'3':2808,'4':8064,'5':4320,'6':13968,'7':7488}:
            raise ValueError('Unexpected per-system full-tracker inventory')
        groups={(q['ids']['system'],q['ids']['layer']) for q in sensitive}
        if len(groups)!=54: raise ValueError('Unexpected signed logical layer inventory')
        data['tracker_sensitive_inventory']=dict(total=len(sensitive), by_system=systems, signed_logical_groups=len(groups))
    write(DATA / 'balanced-baseline.json', data)
    inputs = [expected_path, compact_path, materials_path] + ([tracker_path] if tracker_path else [])
    source_hashes = {}
    for key in ('input_sha256', 'source_sha256', 'combined_source_sha256', 'endcap_factory_sha256'):
        source_hashes.update(expected['provenance'].get(key, {}))
    source_hashes['docs/design/inputs/DES-040-balanced-selection.json']=sha(REPO/'docs/design/inputs/DES-040-balanced-selection.json')
    revision=expected['provenance']['source_revision']
    uncommitted=[]
    for path, digest in source_hashes.items():
        original=subprocess.run(['git','show',revision+':'+path],cwd=REPO,capture_output=True)
        if original.returncode or hashlib.sha256(original.stdout).hexdigest()!=digest: uncommitted.append(path)
    provenance = dict(schema_version=1, source_revision=revision,
        source_dirty=bool(uncommitted), source_paths_differing_from_revision=sorted(uncommitted),
        source_revision_scope='Exporter-reported revision plus exact source fingerprints; dirty paths remain explicit, never substituted for native execution identity.',
        import_tdr_revision=read(REPORT/'source-import.json')['source_tdr_revision'],
        snapshot_sha256=sha(DATA/'balanced-baseline.json'),
        input_files=[dict(name=Path(p).name, sha256=sha(p)) for p in inputs],
        source_sha256=source_hashes, native_evidence=None,
        boundary='Pure extraction and rendering. Source/native execution identities remain distinct. Historical snapshots and extraction recipes remain as imported controls; figure recipes add an explicit balanced mode. They are not current balanced inventories.')
    if native_path:
        native=read(native_path)
        provenance['native_evidence'] = dict(name=Path(native_path).name, sha256=sha(native_path), result=native.get('result',native.get('status')), boundary='Retained native report identity; see original report for full execution provenance.')
    write(DATA/'balanced-provenance.json', provenance)
    print(json.dumps({'counts': s['counts'], 'mass_g': s['mass_g'], 'source_revision': provenance['source_revision']}))


def tables():
    d=read(DATA/'balanced-baseline.json'); p=d['pixel']; s=d['endcap']
    barrels=[]
    for b in p['barrels']:
        barrels.append(f"{b['layer']['id'][-2:]} & {b['layer']['r_m']*1000:g} & {abs(b['columns'][0]['normal_offset_mm']):.3f} & {len(b['columns'])} & {len(b['rows'])} & {b['modules']} " + r'\\')
    discs=[]
    for disc in s['discs']:
        singles=', '.join(str(i+1) for i in disc['retained_rows'] if i<4)
        discs.append(f"{disc['index']} & {disc['z_mm']:.0f} & {singles} & {disc['families']['single']} & 50 & {disc['chips']} & {disc['cooling']['number_circuits']} " + r'\\')
    return {'generated/pixel-barrel-rows.tex': '\n'.join(barrels)+'\n',
            'generated/pixel-disc-rows.tex': '\n'.join(discs)+'\n'}


def check():
    manifest=read(DATA/'balanced-render-manifest.json'); provenance=read(DATA/'balanced-provenance.json')
    if sha(DATA/'balanced-baseline.json') != provenance['snapshot_sha256']:
        raise ValueError('Balanced snapshot fingerprint mismatch')
    for path, digest in manifest['files_sha256'].items():
        if sha(REPORT/path) != digest:
            raise ValueError('Stale current manuscript/render: '+path)
    for path, content in tables().items():
        if (REPORT/path).read_text() != content:
            raise ValueError('Current generated table mismatch: '+path)
    original=read(REPORT/'source-import.json')['imported_file_sha256']
    pixel_text=(REPORT/'chapters/pixel-detector.tex').read_text()
    overview_text=(REPORT/'chapters/tracker-overview.tex').read_text()
    for token in (r'\num{5666}',r'\num{12410}',r'\qtylist{31.5;57;96;182}',r'\num{2616}',r'\num{5616}',r'\num{280}'):
        if token not in pixel_text: raise ValueError('Missing current pixel claim: '+token)
    for token in (r'\num{5362}',r'\num{11806}',r'\num{2312}',r'\num{5012}',r'\num{248}',r'\qtylist{34;60;106;182}'):
        if token in pixel_text: raise ValueError('Stale pixel claim: '+token)
    if r'\num{46250}' not in overview_text or '22 disc assemblies per end' not in overview_text:
        raise ValueError('Missing current integrated tracker inventory')
    current=read(DATA/'balanced-baseline.json')
    for mass in current['endcap']['mass_g'].values():
        if ('\\qty{'+f'{mass/1000:.3f}'+'}{\\kilogram}') not in pixel_text:
            raise ValueError('Missing current generated model mass')
    for path in PRESERVE:
        if sha(REPORT/path) != original[path]:
            raise ValueError('Unchanged strip control modified: '+path)
    for key in ('source_sha256',):
        for path, digest in provenance[key].items():
            if sha(REPO/path) != digest:
                raise ValueError('Source producer changed; refresh extraction: '+path)
    print(f"PASS: {len(manifest['files_sha256'])} current source/assets, {len(PRESERVE)} strip controls, exact tables and snapshot/source identities")


def render():
    for path, content in tables().items():
        (REPORT/path).write_text(content)
    for script in ('pixel_figures.py', 'tracker_figures.py'):
        subprocess.run([sys.executable, '-B', str(REPORT/'scripts'/script), '--balanced'], check=True)
    files={str(p.relative_to(REPORT)):sha(p) for p in sorted(REPORT.rglob('*')) if p.is_file() and
           p.suffix in ('.tex','.sty','.pdf','.svg','.py','.json') and
           p.name not in ('balanced-render-manifest.json','balanced-checks.json') and
           '__pycache__' not in p.parts and not (p.parent==REPORT and p.suffix=='.pdf')}
    write(DATA/'balanced-render-manifest.json', dict(schema_version=1, generator='scripts/balanced_snapshot.py',
          files_sha256=files, classifications=dict(geometry='maintained balanced export',
          strips='byte-preserved imported full-tracker sources/assets',
          historical='Old pixel/tracker snapshots and recipes are retained controls; current pixel recipes use --balanced.')))
    check()
    write(DATA/'balanced-checks.json', dict(schema_version=1, result='PASS',
        snapshot_sha256=sha(DATA/'balanced-baseline.json'),
        render_manifest_sha256=sha(DATA/'balanced-render-manifest.json'),
        source_import_sha256=sha(REPORT/'source-import.json'),
        table_check='exact regenerated content', preserved_strip_controls=PRESERVE,
        geometry_check='Exact canonical complete barrel and positive-endcap module centres and local donor geometry; canonical module/sensitive inventory.',
        native_execution='Not run by publication producer; use separately retained integration evidence.',
        pdf_compilation='Coordinator-owned; not asserted by this source/asset check.'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected', type=Path); parser.add_argument('--compact', type=Path)
    parser.add_argument('--materials', type=Path); parser.add_argument('--native', type=Path)
    parser.add_argument('--tracker-expected', type=Path)
    parser.add_argument('--render', action='store_true'); parser.add_argument('--check', action='store_true')
    args=parser.parse_args()
    if args.expected:
        if not args.compact or not args.materials: parser.error('--compact and --materials required with --expected')
        extract(args.expected,args.compact,args.materials,args.native,args.tracker_expected)
    if args.render: render()
    if args.check: check()
    if not (args.expected or args.render or args.check): parser.error('Choose --expected, --render or --check')

if __name__ == '__main__':
    main()
