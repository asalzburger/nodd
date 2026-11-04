import gzip,json,hashlib,sys
from pathlib import Path
import argparse
parser=argparse.ArgumentParser(description='Refresh the report snapshot from the pinned nODD checkout; no network or detector runtime.')
parser.add_argument('--source-root',required=True,type=Path)
root=parser.parse_args().source_root.resolve(); out=Path(__file__).resolve().parents[1]
import subprocess
revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
if revision!='db74bec126646fe225a4ec6c0f6cc57c75eb3140':
 raise SystemExit('Use the documented PR37 checkout; updating provenance requires editorial review.')
sources=['docs/validation/DES-013-pixel-z/data/packed-200um/layout.json.gz','detector/config/pixel-barrel.json','detector/config/pixel-barrel-support.json','tools/pixel_endcap_support/inputs.json','tools/pixel_support/mounting.json','tools/pixel_support/services.json','docs/validation/DES-012/PR34/engineering/mounting.json','docs/validation/DES-015/summary.json','docs/design/DES-002-pixel-barrel-support-cooling.md','docs/design/DES-010-tracker-service-corridors.md','docs/design/DES-011-service-constrained-tracker-optimization.md','docs/design/DES-012-dd4hep-pixel-barrels.md','docs/design/DES-013-pixel-barrel-z-coverage.md','docs/design/DES-014-pixel-endcap-support.md','docs/design/DES-015-preliminary-pixel-detector.md','docs/design/inputs/DES-014-literature.md','reference/manifest.yaml','tools/pixel_barrel_dd4hep/export.py','tools/pixel_barrel_dd4hep/module_geometry.py','tools/pixel_detector_dd4hep/endcap_services.py','detector/config/pixel-detector.json','docs/validation/DES-012/PR34/engineering/routing.json.gz','docs/validation/DES-012/PR34/engineering/screening.json','docs/validation/DES-015/service-accounting.json','tools/module_layout/services_budget_inputs.json','tools/module_layout/review_models.json']
l=json.loads(gzip.decompress((root/sources[0]).read_bytes()))
bb=[b for b in l['bodies'] if b['subsystem']=='pixel' and b['region']=='barrel']
ee=[b for b in l['bodies'] if b['layer_id']=='A-pixel-P1']; ids={b['module_id'] for b in ee}
barrels=[]
for ly in l['layers']:
 if ly['subsystem']!='pixel' or ly['kind']!='cylinder':continue
 bs=[b for b in bb if b['layer_id']==ly['id']]; patches=[p for p in l['modules'] if p['layer_id']==ly['id']]
 barrels.append(dict(layer=ly,columns=[b for b in bs if b['row']==0],rows=[b for b in bs if b['col']==0],shape=l['metadata']['pixel_z_study']['shapes'][ly['id']],modules=len(bs),patches=len(patches),family=bs[0]['family']))
endcap=json.loads((root/'tools/pixel_endcap_support/inputs.json').read_text())
plate_half=(2*endcap['plate']['skin_mm']+endcap['plate']['core_mm'])/2
pickup=sum(endcap['pickup'].values()); body_t=endcap['module_body_thickness_mm']
step=body_t+pickup+endcap['placement']['gap_mm']
for b in ee:
 face=1 if b['row']%2 else -1
 levels=endcap['placement']['inner_phi_levels'] if b['row']==0 else endcap['placement']['other_phi_levels']
 h=(b['col']%levels)*step
 b.update(mount_face=face,foot_height_mm=h,local_z_mm=face*(plate_half+pickup+body_t/2+h))
discs=[dict(index=int(ly['id'].split('P')[-1]),z_mm=ly['z_m']*1000+(endcap['placement']['first_disc_shift_mm'] if ly['id'].endswith('P1') else 0)) for ly in l['layers'] if ly['subsystem']=='pixel' and ly['kind']=='disc' and '-P' in ly['id']]
data=dict(status='PRELIMINARY; selected PR36/PR37 layout, no engineering sign-off',barrels=barrels,endcap_bodies=ee,endcap_patches=[p for p in l['modules'] if p['module_id'] in ids],discs=discs,module=json.loads((root/'detector/config/pixel-barrel.json').read_text())['module'],support=json.loads((root/'detector/config/pixel-barrel-support.json').read_text()),endcap=endcap,mounting=json.loads((root/'tools/pixel_support/mounting.json').read_text()),rings=json.loads((root/'docs/validation/DES-012/PR34/engineering/mounting.json').read_text()),services=json.loads((root/'tools/pixel_support/services.json').read_text()))
routing=json.loads(gzip.decompress((root/'docs/validation/DES-012/PR34/engineering/routing.json.gz').read_bytes()))
chosen={g['id'] for g in routing['groups'] if g['col']==0 and g['layer_id'] in ['A-pixel-B1','A-pixel-B3']}
data['routing']={k:[x for x in routing[k] if (x.get('group_id',x.get('id')) in chosen) and x.get('scenario','reference')=='reference'] for k in ['groups','longitudinal']}
data['routing']['circuits']=[x for x in routing['circuits'] if x['col']==0 and x['layer_id'] in ['A-pixel-B1','A-pixel-B3']]
data['routing']['radial']=[x for x in routing['radial'] if x['side']=='positive' and x['sector']==0 and x['scenario']=='reference'] if all('side' in x for x in routing['radial']) else [x for x in routing['radial'] if x['id']=='radial-positive-s00-reference']
data['service_summary']=json.loads((root/'docs/validation/DES-012/PR34/engineering/screening.json').read_text())
data['combined_config']=json.loads((root/'detector/config/pixel-detector.json').read_text())
data['combined_services']=json.loads((root/'docs/validation/DES-015/service-accounting.json').read_text())
data['service_budget']=json.loads((root/'tools/module_layout/services_budget_inputs.json').read_text())
(out/'data/pixel-layout.json').write_text(json.dumps(data,indent=2)+'\n')
manifest=dict(date='2026-10-02',parent_revision='db74bec126646fe225a4ec6c0f6cc57c75eb3140',pr36_revision='6a07da7cd3096e6482bae4e96ccabe9b4facf0a3',pr37_revision='db74bec126646fe225a4ec6c0f6cc57c75eb3140',classification='Values are NODD DESIGN CHOICE or INFERENCE from the named design contracts. Public source facts are cited separately. No manufacturing tolerances or human sign-off implied.',snapshot='pixel-layout.json contains only pixel records required for report figures and tables; exact original barrel columns and rows plus the common positive endcap template. local_z_mm follows DES014 EC-C07/08; first datum +3.5 mm follows EC-C08. Negative endcap is z-reflected. Rounded table display does not alter snapshot.',sources=[dict(path=p,sha256=hashlib.sha256((root/p).read_bytes()).hexdigest()) for p in sources],snapshot_sha256=hashlib.sha256((out/'data/pixel-layout.json').read_bytes()).hexdigest(),des001='Exact DES001 and compact/quad input blobs inspected at 214747a3c83c140caa6c4ae9c3fb6486ac5cb825; hashes verified against review_models.json. Selected parameters interpreted with subsequent DES012/013 placement amendments.',figures={'pixel-overview.pdf':'Exact nominal barrel radii, selected disc datums; schematic envelope thickness and service paths.','pixel-modules.pdf':'Exact occupied barrel bounds and active patches; scale drawing in local module plane.','pixel-packing.pdf':'Exact selected barrel row body and active bounds, clipped to central window.','pixel-barrels.pdf':'Exact barrel stave module transverse rectangles, support stack and mounting-ring radii; z projection, not one common physical cut.','pixel-stave.pdf':'Scale cross-section of selected single/quad supports, simplified module as occupied envelope.','pixel-endcap.pdf':'Exact common module x/y rectangles and selected mounting faces; all z levels projected.','pixel-disc-section.pdf':'Scale axial/radial row envelope/pickup drawing at a representative azimuth; projected levels, not swept CAD.','pixel-carrier.pdf':'Dimensioned explanatory load-path schematic; not to scale.','pixel-services.pdf':'Dimensioned explanatory service topology schematic; not a routing CAD or acceptance plot.'})
models=json.loads((root/'tools/module_layout/review_models.json').read_text())
manifest['git_blobs']=[]
for entry in models['sources']:
 if 'DES-001' not in entry['path']: continue
 blob=subprocess.check_output(['git','show',entry['revision']+':'+entry['path']],cwd=root)
 digest=hashlib.sha256(blob).hexdigest()
 if digest!=entry['sha256']: raise SystemExit('Pinned DES001 blob hash mismatch: '+entry['path'])
 manifest['git_blobs'].append(dict(path=entry['path'],revision=entry['revision'],sha256=digest,url=entry['url']))
manifest['figures'].update({
'pixel-module-stack.pdf':'Selected physical stack in local w, with true relative thicknesses; bump volume unresolved, not drawn as manufactured bumps. Flex electrical links and heat arrows schematic.',
'pixel-sensor-detail.pdf':'Exact selected quad substrate, active patches, guards and seams; enlarged pixel grid explains readout pitch and is not implant artwork.',
'pixel-barrel-routing.pdf':'Exact B1 column0 selected reference stepped cable envelope and ring radial positions; module pickups and full-length counterflow are schematic connections, no bends qualified.',
'pixel-sector-handoff.pdf':'Selected twelve-sector barrel handoff with real stave populations and radial collection envelopes; grouped pipe centreline paths schematic.',
'pixel-endcap-routing.pdf':'Exact common module outline/face assignment and cooling radii; separate intended two-face bus and ten half-ring hydraulic topology. Radial legs and service fans illustrative, no swept-route claim.',
'pixel-service-interfaces.pdf':'Exact positive-endcap effective cell r-z bounds, first/last collectors, bypass, flange necks and rear turn; schematic connectivity arrows, not manufactured routing.'})
(out/'data/pixel-provenance.json').write_text(json.dumps(manifest,indent=2)+'\n')

cat=json.loads((root/'reference/manifest.yaml').read_text())
ids=['SRC-RD53-OVERVIEW-2023','SRC-ATLAS-ITK-PIXEL-COOLING-2024','SRC-CMS-TEPX-SYSTEM-2026','SRC-PLANAR-SLIM-2013','SRC-MINTEQ-GRAPHITE-2011','SRC-ATLAS-IBL-PRODUCTION-2018','SRC-NIST-CO2-SATURATION-DES002']
(out/'data/pixel-public-sources.json').write_text(json.dumps({'status':'Selected existing public catalogue entries; no new facts or sources added. Local-file fields describe original catalogue copies, not files redistributed in this report.','sources':[x for x in cat['sources'] if x['id'] in ids]},indent=2)+'\n')
