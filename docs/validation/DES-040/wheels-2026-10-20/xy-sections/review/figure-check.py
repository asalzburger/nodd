"""Portable exact-revision artifact assessment for PR90 three-wheel XY sections.

Reads all evidence and independent math from Git objects at --revision.
Only --output is retained on disk; temporary evidence copies are discarded.
Requires NumPy. PNG visual assessment remains the recorded human-readable
review of the artifact hashes listed in the result, not a programmatic check.
"""
import argparse,ast,hashlib,itertools,json,math,pathlib,subprocess,tempfile,types,xml.etree.ElementTree as ET
import numpy as np
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo',type=pathlib.Path,required=True)
parser.add_argument('--revision',required=True)
parser.add_argument('--output',type=pathlib.Path,required=True)
args=parser.parse_args()
REPO=args.repo.resolve()
REV=subprocess.check_output(['git','-C',str(REPO),'rev-parse','--verify',args.revision+'^{commit}'],text=True).strip()
OLD='99bb67a6d3a65d4ef6de30ff2def8698b3ed053d'
def git(path,rev=REV):return subprocess.check_output(['git','-C',str(REPO),'show',rev+':'+path])
TEMP=tempfile.TemporaryDirectory(prefix='nodd-xy-artifact-review-')
BASE=pathlib.Path(TEMP.name)
PREFIX='docs/validation/DES-040/wheels-2026-10-20/xy-sections'
for name in ['sections.json','provenance.json','unchanged-inputs.json','review/input-check.py','endcap-wheels-xy.png','endcap-wheels-xy.svg']+[f'wheel-{station}-xy.{ext}' for station in [1,2,3] for ext in ['png','svg']]:
 destination=BASE/name;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(git(PREFIX+'/'+name))
def sha(b):return hashlib.sha256(b).hexdigest()
gpath='docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json';geometry=git(gpath);assert geometry==git(gpath,OLD);g=json.loads(geometry)
# Load only the previously authored independent analytic functions; do not rerun query banks.
mod=ast.parse((BASE/'review/input-check.py').read_text());ns={'np':np,'itertools':itertools,'math':math}
fns=[x for x in mod.body if isinstance(x,ast.FunctionDef) and x.name in {'cut','prism','slice_filled','intervals'}];exec(compile(ast.Module(body=fns,type_ignores=[]),'independent XY-P1 functions','exec'),ns)
cut,intervals=ns['cut'],ns['intervals']
mod=ast.parse(git('tools/muon_layout/support.py').decode());f=next(x for x in mod.body if isinstance(x,ast.FunctionDef) and x.name=='material_parts');ns['geo']=types.SimpleNamespace(prism=ns['prism']);exec(compile(ast.Module(body=[f],type_ignores=[]),'pinned material_parts','exec'),ns)
parts={p['id']:(m['id'],p) for m in g['supports']['members'] for p in ns['material_parts'](m)}
sections=json.loads((BASE/'sections.json').read_text());assert sections['common_xy_limits_m']==[-10.,10.]
worst=0.;checks=[]
def check(expected,actual):
 global worst
 expected=np.asarray(expected);actual=np.asarray(actual);assert expected.shape==actual.shape
 d=np.linalg.norm(expected[:,None,:]-actual[None,:,:],axis=2);err=max(float(d.min(axis=0).max()),float(d.min(axis=1).max()));worst=max(worst,err);assert err<2e-9
for row,counts in zip(sections['sections'],[(12,120,24),(108,96,48),(24,0,0)]):
 z=row['z_m'];ep={p['id']:c for p in g['panels'] if p['kind']=='endcap' if (c:=cut(p,z)) is not None}
 assert set(ep)=={p['id'] for p in row['chambers']}
 for p in row['chambers']:check(ep[p['id']],p['xy_m'])
 sp={k:(m,c) for k,(m,b) in parts.items() if (c:=cut(b,z)) is not None};assert set(sp)=={p['part_id'] for p in row['support_stock']}
 for p in row['support_stock']:
  mid,c=sp[p['part_id']];assert mid==p['member_id'];check(c,p['xy_m'])
 cp={}
 for name,group in g['magnetic_configuration']['coil_groups'].items():
  for k in range(12):
   ph=math.radians(group['phi_offset_deg']+30*k);c,s=math.cos(ph),math.sin(ph)
   for i,(lo,hi) in enumerate(intervals(group,z,.25)):
    cp[name,k,i]=[[u*c-v*s,u*s+v*c] for u,v in [(lo,-.3),(hi,-.3),(hi,.3),(lo,.3)]]
 assert set(cp)=={(p['group'],p['coil'],p['interval']) for p in row['warm_coils']}
 for p in row['warm_coils']:check(cp[p['group'],p['coil'],p['interval']],p['xy_m'])
 assert (len(ep),len(sp),len(cp))==counts
 vertices=np.vstack([p['xy_m'] for key in ['chambers','support_stock','warm_coils'] for p in row[key]])
 assert abs(vertices).max()<10
 checks.append(dict(z_m=z,chambers=len(ep),frame_material_parts=len(sp),coil_rectangles=len(cp),max_absolute_coordinate_m=float(abs(vertices).max())))
provenance=json.loads((BASE/'provenance.json').read_text());artifact_checks=[]
for name,entry in provenance['artifacts'].items():
 b=(BASE/name).read_bytes();assert len(b)==entry['bytes'] and sha(b)==entry['sha256'];artifact_checks.append(name)
for path,digest in provenance['source_sha256'].items():assert sha(git(path))==digest,path
svg=[]
for path in sorted(BASE.glob('*.svg')):
 root=ET.fromstring(path.read_bytes());tags=[x.tag.rsplit('}',1)[-1] for x in root.iter()];assert 'image' not in tags
 svg.append(dict(name=path.name,xml_parsed=True,raster_images=0,path_count=tags.count('path')))
unchanged=json.loads((BASE/'unchanged-inputs.json').read_text());unchanged_count=0
for path,digest in unchanged['unchanged_files'].items():
 # Object identity proves byte identity without redundantly loading large map blobs.
 oldoid=subprocess.check_output(['git','-C',str(REPO),'rev-parse',OLD+':'+path],text=True).strip();newoid=subprocess.check_output(['git','-C',str(REPO),'rev-parse',REV+':'+path],text=True).strip();assert oldoid==newoid;unchanged_count+=1
index=unchanged['index_exception'];assert git(index['path']).startswith(git(index['path'],OLD));assert sha(git(index['path']))==index['current_sha256'];assert sha(git(index['path'],OLD))==index['baseline_sha256']
# Source style has equal metric axes and the exact native material blue/grey values.
source=git('tools/muon_layout/wheels_xy.py').decode();assert "aspect='equal'" in source and "BLUE = (0., 96/256, 255/256)" in source and "COIL = (160/256,)*3" in source
result=dict(assignment='XY-P2',reviewed_revision=REV,input_geometry_revision=OLD,geometry_sha256=sha(geometry),passed=True,findings=[],checks=dict(displayed_polygon_ids_and_vertices_match_independent_cuts=True,total_chamber_polygons=144,total_frame_stock_polygons=216,total_coil_polygons=72,max_vertex_distance_m=worst,planes=checks,common_limits_m=[-10.,10.],source_equal_aspect=True,source_blue_grey_match_native_material_convention=True,artifact_hashes_and_sizes_verified=artifact_checks,source_hashes_verified=len(provenance['source_sha256']),svg_xml_and_raster_checks=svg,unchanged_declared_files_git_blob_identity=unchanged_count,evidence_index_old_bytes_prefix=True,visually_inspected=['endcap-wheels-xy.png','wheel-2-xy.png']),provenance_note='Source was uncommitted at recorded execution head; execution_source_matches_head records false for wheels_xy.py honestly. Exact executed SHA matches this reviewed frozen source. No claim that generation used a clean committed checkout.',limitations=['Display fidelity assessment only; no new physics or engineering acceptance.','Independent author supplied XY-P1 expected-cut checker, but did not implement the root plotting source.','No ACTS or broad scientific rerun; unchanged evidence established by exact Git blob identity.','SVG XML/path structure checked; visual inspection performed on PNG exports.'])
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'reviewed_revision':REV,'output':str(args.output),'passed':result['passed'],'max_vertex_distance_m':worst,'artifact_hashes_verified':len(artifact_checks),'svg_count':len(svg),'unchanged_files':unchanged_count},indent=2))
