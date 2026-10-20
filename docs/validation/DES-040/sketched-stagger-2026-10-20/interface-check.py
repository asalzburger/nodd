#!/usr/bin/env python3
"""SS-A1 pinned physical-interface check; scratch outputs only, no native runtime."""
import argparse, collections, hashlib, importlib, json, math, pathlib, platform, subprocess, sys, tempfile, time
import numpy as np
REV='a12efbb5f169e5e02cd1f36aee48c1e748b6ce6f'
HCAL='0e8530d56d171f38c9d53d3c60c8b48803680bbd'
PATHS=['docs/design/DES-040-muon-chambers-frame.md','docs/validation/DES-040/barrel-overlap-2026-10-20/candidate/geometry.json','tools/muon_layout/barrel_overlap.py','tools/muon_layout/layout.py','tools/muon_layout/geometry.py','tools/muon_layout/support.py','tools/toroid_prototype/geometry.py','docs/validation/DES-040/inner-barrel-2026-10-20/interface-check.json','docs/validation/DES-040/inner-barrel-2026-10-20/conditional-report.md','docs/validation/MUON-001/hcal-material.json','docs/validation/DES-039/sources.json','docs/design/DES-039-twelvefold-toroid.md','tools/muon_layout/acts/prepare.py','tools/muon_layout/wheels_acts/config.json']
HPATHS=['tools/hcal_barrel/design.py','tools/hcal_barrel/config.json','docs/validation/DES-037/summary.json','tools/siw_services/inputs.json','tools/siw_services/study.py','docs/design/DES-034-siw-service-envelopes.md']
EXPECTED=['7854245d0a5b00bf6c74bc71b5f949a6c097c736a19a8d70f558cb423048d018','f4aebc7d5e1476d6f40f331d2aef0673fa6840ee1883015570089be6e79ad328','e57597636d2634bd93f8cd38e00a1ca63500d7ebaff85751288e9a86471899ac','137fe25dcfd4eb7ebde8c966a903dddb88e0976e339934edadb0d622aacf4b17','162aeafae3775d0483d770556286485be9333523227b6160af0265d74f5cc230','14f294c0250166239caca055436ffe9c3f664b246f7d14baabd7eab62c75d7af','e831bbc59054713f23dca5367df51f70360d80e52614ac1fe0b0e8d8943f049f','7bcc4bb19cda9adfe6606dbbc75f4f1004258e53cc15a922d71d4777bd75d656','d465fd6734edd3cd875a975ef4aa7b29934c7401d725b00c4dd275232b699583']
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,v):pathlib.Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def extract(repo,rev,path,root,manifest):
 b=subprocess.check_output(['git','-C',str(repo),'show',rev+':'+path]);oid=subprocess.check_output(['git','-C',str(repo),'rev-parse',rev+':'+path],text=True).strip();q=root/path;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b);manifest[rev+':'+path]={'blob_oid':oid,'sha256':sha(b),'bytes':len(b),'show_command':['git','-C',str(repo),'show',rev+':'+path]};return b

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=pathlib.Path,required=True);p.add_argument('--revision',required=True);p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--candidate',type=pathlib.Path);a=p.parse_args()
 if a.revision!=REV:raise ValueError('checker is pinned to '+REV)
 if not str(a.output).startswith('/private/tmp/pr90-SS-A1-'):raise ValueError('scratch output path must use /private/tmp/pr90-SS-A1-*')
 started=time.monotonic();manifest={}
 with tempfile.TemporaryDirectory(prefix='pr90-SS-A1-src-',dir='/private/tmp') as td:
  root=pathlib.Path(td)
  for i,path in enumerate(PATHS):
   b=extract(a.repo,REV,path,root,manifest)
   if i<len(EXPECTED) and sha(b)!=EXPECTED[i]:raise ValueError('dispatch input hash mismatch '+path)
  hroot=root/'hcal-source'
  for path in HPATHS:extract(a.repo,HCAL,path,hroot,manifest)
  material=json.loads((root/PATHS[9]).read_text());assert material['repo_head']==HCAL
  for path in HPATHS[:3]:assert manifest[HCAL+':'+path]['sha256']==material['source_sha256'][path]
  # Import only modules extracted with git show, never working-tree source.
  sys.path.insert(0,str(root));g=importlib.import_module('tools.muon_layout.geometry');layout=importlib.import_module('tools.muon_layout.layout');support=importlib.import_module('tools.muon_layout.support')
  j=json.loads((root/PATHS[1]).read_text());c=j['configuration']['chambers'];mag=j['magnetic_configuration'];members=j['supports']['members'];assert len(members)==484
  hc=json.loads((hroot/'tools/hcal_barrel/config.json').read_text());hs=json.loads((hroot/'docs/validation/DES-037/summary.json').read_text());services=json.loads((hroot/'tools/siw_services/inputs.json').read_text());sc=services['choices'];sf=services['source_facts']
  h=.25;pitch=math.pi/12;b=(5.2-h)*math.tan(math.pi/24)-.01;ae=math.atan((b-.03)/(5.2+h));ao=math.radians(15.1)-ae;t=math.tan(ao);R=4.63;w=(R+h)*t+.03
  cos,sin=math.cos(pitch),math.sin(pitch)
  upper=(5.2-h-.02-h*cos-(h*t+.03)*sin)/(cos+t*sin)
  jacket=(hc['egress_radius_mm']+hc['egress_jacket_radius_mm'])/1000
  lower=jacket+.05+h
  plane_gap=5.2-h-((R+h)*cos+w*sin)
  slab_gap=(R-h)*sin-w*cos-mag['warm']['tangent_m']/2
  coil_sufficient_min=(mag['warm']['tangent_m']/2+.05+h*sin+(h*t+.03)*cos)/(sin-t*cos)
  def facet(k,station=1,radius=R,width=w,zmax=6.4456,phase=0):
   return layout._barrel(f'B{station}/F{k:02d}/FULLZ',station,phase+k*15,radius,-zmax,zmax,-width,width,c)
  b1=[facet(k,radius=5.2 if k%2==0 else R,width=b if k%2==0 else w) for k in range(24)]
  b2w=(6.7-h)*math.tan(math.pi/24)-.01
  b2=[facet(k,station=2,radius=6.7,width=b2w,zmax=9.2,phase=7.5) for k in range(24)]
  neighbor=[(b1[k]['id'],b1[(k+1)%24]['id']) for k in range(24) if g.intersects(b1[k],b1[(k+1)%24],.02)]
  b1coils=[dict(id=v['id'],**g.certify_coil_clear(v,mag,.05,.02,max_cells=300000)) for v in b1]
  b1support=[dict(id=v['id'],conflicts=[m['id'] for m in members if g.intersects(v,m,.05)]) for v in b1]
  # Full-z B2 templates intentionally expose fixed-frame and ECT cuts.
  b2coils=[dict(id=v['id'],**g.certify_coil_clear(v,mag,.05,.02,max_cells=300000)) for v in b2]
  b2support=[dict(id=v['id'],conflicts=[m['id'] for m in members if g.intersects(v,m,.05)]) for v in b2]
  # Actual HCAL finite steel and rear covers, constructed exactly from pinned design.py formulas.
  hcalbodies=[];tan=math.tan(math.pi/hc['sectors']);outer=hc['proposed_outer_apothem_mm']/1000;usable=(hc['half_length_mm']-hc['end_flange_mm'])/1000
  def band(name,k,lo,hi,inset):
   ph=k*2*math.pi/hc['sectors'];basis=np.array([[math.cos(ph),-math.sin(ph),0],[math.sin(ph),math.cos(ph),0],[0,0,1.]])
   return g.prism(name,'HCAL',[0,0,0],basis,[[lo,-lo*tan+inset],[hi,-hi*tan+inset],[hi,hi*tan-inset],[lo,lo*tan-inset]],2*usable)
  for k in range(16):
   for layer in hs['layers']:
    lo=layer['steel_front_mm']/1000;hcalbodies.append(band(f'HCAL/S{k:02d}/Steel{layer["layer"]:02d}',k,lo,lo+.03,.021))
   hcalbodies.append(band(f'HCAL/S{k:02d}/RearCover',k,outer-.010,outer,.001))
  actual_corner=max(np.linalg.norm(g.vertices3(v)[:,:2],axis=1).max() for v in hcalbodies)
  actual_conflicts=[dict(panel=v['id'],hcal=m['id']) for v in b1 for m in hcalbodies if g.intersects(v,m,.05)]
  # The detailed regional HCAL assembly lives inside its corner envelope; endcap bound is separately retained.
  hcal_sufficient_gap=R-h-max(mag['hcal']['barrel_corner_radius_m'],mag['hcal']['endcap_outer_corner_radius_m'])
  # Reproduce the known DES034 tube backbone; no installed service material is asserted.
  bend=sc['bend_radius_OD']*sc['water_jacket_mm']/1000;rear=sf['ecal_endcap_back_abs_z_mm']/1000;turn=rear+sc['rear_axial_gap_mm']/2000-bend
  route=[(sc['lane_centre_radius_mm']/1000,z/1000) for z in (0,sf['ecal_barrel_flange_half_length_mm'],sf['ecal_endcap_back_abs_z_mm'])]+[(sc['lane_centre_radius_mm']/1000,turn)]
  route += [(sc['lane_centre_radius_mm']/1000+bend*(1-math.cos(q)),turn+bend*math.sin(q)) for q in np.linspace(0,math.pi/2,65)]
  route += [(sc['egress_radius_mm']/1000,rear+sc['rear_axial_gap_mm']/2000)]
  jacket_bound=max(x for x,z in route)+sc['water_jacket_mm']/2000;assert abs(jacket_bound-jacket)<1e-12
  # Actual support symmetry, without assigning magnetic C12 to the feet.
  def signature(v,angle=0):
   vv=g.vertices3(v);co,si=math.cos(angle),math.sin(angle);rot=np.array([[co,-si,0],[si,co,0],[0,0,1.]])
   coords=tuple(sorted(tuple(round(float(x),8) for x in row) for row in vv@rot.T));return (v['category'],v['material'],v.get('wall_m'),coords)
  original=collections.Counter(signature(v) for v in members);rotated=collections.Counter(signature(v,pitch*2) for v in members)
  missing=list((rotated-original).elements());asymmetric=[v['id'] for v in members if signature(v,pitch*2) not in original]
  # Entrance closed cylinder sufficient bounds and actual inside-start diagnostic.
  er=np.array([math.cos(pitch),math.sin(pitch),0.]);d=4.35*er+np.array([0,0,1.]);d/=np.linalg.norm(d);offset=1e-5;surface=d*(4.35/np.linalg.norm(d[:2]));start=surface+offset*d
  diag=layout._barrel('NEGATIVE/R4.60-B1/F01/Z02',1,15,4.6,.01,3.2178,-((4.6+h)*t+.03),((4.6+h)*t+.03),c)
  final=layout._barrel('B1/F01/Z02',1,15,R,.01,3.2178,-w,w,c)
  entrance=dict(radius_m=4.35,half_z_m=6.4684,forward_offset_m=offset,
   sufficient_radius_open_interval_m=[jacket,R-h-offset],sufficient_half_z_open_interval_m=[mag['hcal']['endcap_back_abs_z_m'],c['disk_abs_z_m'][0]-h-offset],
   radius_gap_to_known_service_m=4.35-jacket,minimum_B1_radial_start_reserve_m=R-h-4.35-offset,
   cap_start_reserve_to_first_endcap_m=c['disk_abs_z_m'][0]-h-6.4684-offset,
   all_chambers_before_start_proof='Every barrel point has r>=4.38m; every endcap point has|z|>=6.4956m. A unit-direction10um offset raises radius or|z| by at most10um. Thus the entire closed entrance plus offset is before every finite chamber; B1 maximum|z|6.4456 does not invalidate the radial proof.',
   negative_R4_60=dict(surface_m=surface.tolist(),direction=d.tolist(),start_m=start.tolist(),inside_diagnostic_panel=bool(g.contains(diag,[start])[0]),inside_final_R4_63_panel=bool(g.contains(final,[start])[0]),scope='The oldR4.35 entrance starts inside diagnosticR4.60, but does not start inside selectedR4.63.'))
  assert entrance['negative_R4_60']['inside_diagnostic_panel'] and not entrance['negative_R4_60']['inside_final_R4_63_panel']
  result=dict(assignment='SS-A1',role='SysArch explicitly supplied fallback mandate',input_revision=REV,hcal_source_revision=HCAL,status='DRAFT isolated outline interface assessment; no engineering sign-off',sources=manifest,
   analytic_dimensions=dict(R_even_m=5.2,R_odd_m=R,depth_m=.5,even_full_width_m=2*b,odd_full_width_m=2*w,even_border_half_angle_deg=math.degrees(ae),odd_border_half_angle_deg=math.degrees(ao),full_depth_overlap_deg=.1,odd_outer_corner_radius_m=math.hypot(R+h,w),neighbor20mm_upper_R_m=upper,known_water_jacket50mm_lower_R_m=lower,sufficient_feasible_interval_m=[lower,upper],neighbor_separating_plane_gap_m=plane_gap,coil_tangent_slab_gap_m=slab_gap,coil50mm_sufficient_lower_R_m=coil_sufficient_min,ECT_nearest_axial_gap_to_B1_m=7.05-6.4456,scope='Whole-prism sufficient analytic inequalities;50mm and20mm exact contact should retain strict numerical guards.'),
   b1_full_z_template_checks=dict(adjacent_pairs=24,neighbor20mm_conflicts=neighbor,actual_orientation_uncached_coil_checks=b1coils,all484_support_checks=b1support,actual_HCAL_steel_and_cover_count=len(hcalbodies),actual_HCAL_steel_cover_max_corner_m=float(actual_corner),actual_HCAL50mm_conflicts=actual_conflicts,complete_HCAL_corner_bound_gap_m=hcal_sufficient_gap,known_water_jacket_gap_m=R-h-jacket),
   b2_full_z_templates=dict(phase_deg=7.5,depth_m=.5,full_width_m=2*b2w,actual_orientation_uncached_coil_checks=b2coils,all484_support_checks=b2support,scope='Full-z templates expose hardware corridors; packing must retain finite split cuts and freshly certify all leaves. No blind rotation accepted.'),
   symmetry=dict(magnetic_folds=mag['folds'],magnetic_groups={k:v['phi_offset_deg'] for k,v in mag['coil_groups'].items()},support_total=484,support_30deg_rotation_unmatched_count=len(missing),unmatched_rotated_member_ids=asymmetric,HCAL_sector_count=hc['sectors'],scope='C12 coil symmetry is actual source property. Frame feet are asymmetric; HCAL is16-fold, so magnetic symmetry cannot be reused for their clearance tests.'),
   services=dict(source_classification=services['status'],water_route_vertices_rz_m=route,known_jacket_outer_radius_m=jacket_bound,known_jacket_abs_z_upper_m=max(z for r,z in route)+.025,minimum_selected_B1_gap_m=R-h-jacket_bound,source_hcal_services=hs['services']['implementation'],excluded=hs['excluded'],scope='DES034 ECAL water egress through HCAL rearbreak is an empty design reservation. It is not installedHCALmaterial or a certified envelope for allHCALcollectors/cables/plant; those external routes remain unimplemented. Source cable-lane/collector qualification remains open.'),entrance=entrance,changed_repository_files=[],actual_native_execution=False,
   interface_register=[dict(owners=['MuonTech','SysArch magnets'],frame='Cartesian m, radial apothem and actual prism basis',boundary='B1 innerleg and B2 BT/ECT crossings',clearance_m=.05,validation='actual-orientation full-volume coil-distance certificate'),dict(owners=['MuonTech','SysArch common mechanics'],frame='Cartesian m, all484 finite fixed envelopes',boundary='B2 frontcarriers/spokes/lugs at|z|~6.3 to7.05m',clearance_m=.05,validation='all484 support SAT at every actual orientation'),dict(owners=['MuonTech','CalorimeterTech and SysArch common services'],frame='Cartesian m; HCAL16-fold, ECAL egress route RZ',boundary='inwardB1 vs finiteHCAL and known service jacket',clearance_m=.05,validation='finite steel/cover SAT plus conservative full-HCAL and service radial bound; unknownexternalHCALroutes remainunqualified'),dict(owners=['MuonTech','SoftEng'],frame='closed cylindrical native entrance with10um forwardoffset',boundary='first finite B1/endcap depthface',validation='analytic entire-surface bound and inside-start negative witness; no native transport claim')])
  if a.candidate:
   candidate=json.loads(a.candidate.read_text());panels=candidate.get('panels',candidate.get('B1_panels'))
   if panels is None:raise ValueError('candidate requires panels array')
   changed=[v for v in panels if v['kind']=='barrel' and v['station'] in(1,2)];proofs=[];conflicts=[]
   for v in changed:
    proofs.append(dict(id=v['id'],**g.certify_coil_clear(v,mag,.05,.02,max_cells=300000)))
    conflicts +=[dict(panel=v['id'],support=m['id']) for m in members if g.intersects(v,m,.05)]
   result['candidate_audit']=dict(path=str(a.candidate),sha256=sha(a.candidate.read_bytes()),changed_barrel_count=len(changed),fresh_actual_orientation_coil=proofs,all484_support_conflicts=conflicts,
    retained_magnetic_equal=candidate.get('magnetic_configuration')==mag,retained_support_equal=candidate.get('supports')==j['supports'],retained_B3_equal=[v for v in panels if v['kind']=='barrel' and v['station']==3]==[v for v in j['panels'] if v['kind']=='barrel' and v['station']==3],retained_endcap_equal=[v for v in panels if v['kind']=='endcap']==[v for v in j['panels'] if v['kind']=='endcap'])
   assert all(x['clear'] for x in proofs) and not conflicts
  assert not neighbor and all(v['clear'] for v in b1coils) and not any(v['conflicts'] for v in b1support) and not actual_conflicts and lower<R<upper
  result['passed_bounded_checks']=True;result['runtime']=dict(python=platform.python_version(),numpy=np.__version__,seconds=time.monotonic()-started);result['checker_sha256']=sha(pathlib.Path(__file__).read_bytes());save(a.output,result)
  print(json.dumps(dict(passed_bounded_checks=True,source_count=len(manifest),fullz_B1=24,fullz_B2=24,seconds=result['runtime']['seconds'],output=str(a.output))))
if __name__=='__main__':main()
