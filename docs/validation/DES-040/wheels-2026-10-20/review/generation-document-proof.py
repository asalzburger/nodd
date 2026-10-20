from pathlib import Path
import hashlib,json,subprocess,difflib
root=Path.cwd();path='docs/design/DES-040-muon-chambers-frame.md';revision='22a3f8c113a276b1321adeb9b994107594eb3c7d'
def read(path):return subprocess.check_output(['git','show',revision+':'+path])
def sha(raw):return hashlib.sha256(raw).hexdigest()
raw=read(path);frozen=raw.decode();target='78590c60800e60d55d986b9f94cbe012dc470d4d0b83d7c46b50eec681b95678'
block='The recorded affine corridor has10 mm half-seam at the0.70 m bore base and\n360 mm half-corridor at the BT clearance-box inner edge R4.30 m; its extra10 mm\nbeyond the required350 mm is a prototype certification margin. Exact inner\nwheel base-distance4.666416782 m and base widths0.354423346/1.901652879 m follow\nfrom mirrored straight sides and the5.45 m outer-vertex bound. Outer-wheel\nbase-distance7.679008474 m and widths0.164140917/2.186062207 m follow from the\n8.45 m outer-vertex bound and20 mm seams. Source inputs/configuration retain\nfull-precision values; no arbitrary shaped coil holes or radial fragments.\n'
assert frozen.count(block)==1;generated=frozen.replace(block,'');assert sha(generated.encode())==target
out=Path(__file__).resolve().parent
(out/'DES040-generation.md').write_text(generated);(out/'DES040-freeze.md').write_bytes(raw)
diff=''.join(difflib.unified_diff(generated.splitlines(keepends=True),frozen.splitlines(keepends=True),fromfile='DES040-generation-78590c60',tofile='DES040-freeze-22a3f8c-0af3c991'))
(out/'delta.patch').write_text(diff)
controls=json.loads(read('docs/validation/DES-040/wheels-2026-10-20/candidate/geometry-controls.json'));geometry=json.loads(read('docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json'));config=json.loads(read('tools/muon_layout/wheels-config.json'))
checks=[]
for p,h in controls['sources'].items():
 now=sha(read(p));checks.append(dict(path=p,generation_sha256=h,freeze_sha256=now,match=h==now))
assert [q['path'] for q in checks if not q['match']]==[path]
assert geometry['wheel_revision']==config
magsha=sha(read('docs/validation/DES-040/wheels-2026-10-20/magnetic/configuration.json'));assert magsha==controls['magnetic_configuration_sha256']
numeric=[dict(parameter='inner bore half-seam',config_value_m=config['inner_wheel']['seam_half_width_at_bore_m'],later_document_value_m=.010),dict(parameter='extra margin',config_value_m=config['inner_wheel']['extra_BT_box_margin_m'],later_document_value_m=.010)]
for name in ['inner_wheel','outer_wheel']:
 d=geometry['wheel_dimensions'][name]
 for key in ['radial_base_distance_m','inner_base_m','outer_base_m']:
  numeric.append(dict(parameter=name+'.'+key,generation_value_m=d[key],later_document_value_m=round(d[key],9)))
start=frozen[:frozen.index(block)].count('\n')+1
proof=dict(proven=True,assignment='W-G1 read-only provenance closeout',path=path,generation_sha256=target,freeze_commit=revision,freeze_sha256=sha(raw),freeze_added_lines=[start,start+len(block.splitlines())-1],operation='remove exactly the8-line affine corridor/base-dimension paragraph from frozen document; remaining bytes hash exactly to generation DES040 fingerprint',added_block=block,source_locator=revision+':'+path,all_generation_source_checks=checks,matching_source_entries=sum(c['match'] for c in checks),total_source_entries=len(checks),top_level_magnetic_configuration_check=dict(generation_sha256=controls['magnetic_configuration_sha256'],freeze_sha256=magsha,match=True),config_already_embedded_exactly=True,configuration_source_sha256=controls['sources']['tools/muon_layout/wheels-config.json'],dimension_restatement=numeric,scope='later design-document numerical restatement; no changed source configuration, magnet/chamber/frame parameters or geometry in this delta',important_distinction='geometry-controls records generation-time document bytes, not a promise that all source paths match a later documentation freeze',geometry_sha256=sha(read('docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json')))
(out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
print(diff);print(json.dumps({k:v for k,v in proof.items() if k not in ['all_generation_source_checks','dimension_restatement','added_block']},indent=2));print('proof_sha256',sha((out/'proof.json').read_bytes()))
