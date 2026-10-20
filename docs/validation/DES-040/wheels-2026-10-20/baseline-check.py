#!/usr/bin/env python3
"""Read-only baseline inventories/domain/region accounting for W-P1 planning."""
import argparse,collections,hashlib,io,json,subprocess
from pathlib import Path
import numpy as np
REV='5674a7688319d6dd5179c04cd381cb59f48d36bb'
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--revision',default=REV);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 def get(path):return subprocess.check_output(['git','-C',str(a.root),'show',a.revision+':'+path])
 geo_raw=get('docs/validation/DES-040/geometry.json');geo=json.loads(geo_raw);c=geo['configuration']['chambers'];mag=geo['magnetic_configuration'];rows=[]
 for family in ['barrel','endcap']:
  for station in [1,2,3]:
   for side in ([0] if family=='barrel' else [-1,1]):
    panels=[p for p in geo['panels'] if p['kind']==family and p['station']==station and (family=='barrel' or p['side']==side)]
    areas=[];aabbs=[];spans=[]
    for b in panels:
     xy=np.array(b['vertices_m']);areas.append(abs((xy[:,0]*np.roll(xy[:,1],-1)-xy[:,1]*np.roll(xy[:,0],-1)).sum())/2)
     h=b['depth_m']/2;xyz=np.vstack([np.c_[xy,np.full(4,w)] for w in [-h,h]])@np.array(b['basis']).T+b['origin_m'];aabbs.append([xyz.min(0),xyz.max(0)])
     spans.append((xy.max(0)-xy.min(0)).tolist())
    bb=np.array(aabbs);rows.append(dict(kind=family,station=station,side=side,count=len(panels),shape=panels[0]['face'],face_area_m2_sum=float(sum(areas)),face_area_m2_range=[float(min(areas)),float(max(areas))],aabb_min_m=bb[:,0].min(0).tolist(),aabb_max_m=bb[:,1].max(0).tolist(),local_face_span_m_range=[np.array(spans).min(0).tolist(),np.array(spans).max(0).tolist()]))
 cfg=json.loads(get('tools/muon_layout/acts/config.json'));raw=get('docs/validation/DES-040/acts-propagation/tracks.npz')
 with np.load(io.BytesIO(raw),allow_pickle=False) as f:t={k:f[k] for k in ['momentum_GeV','charge','sample','eta_pos','entrance_kind','incomplete','outer_unique_faces','active_paired_stations']}
 split=float(np.arcsinh(cfg['entrance']['half_z_m']/cfg['entrance']['radius_m']));cases=[]
 for mom in cfg['momentum_GeV']:
  for q in cfg['charge_e']:
   whole=(t['momentum_GeV']==mom)&(t['charge']==q)&(t['sample']==1);end=whole&(abs(t['eta_pos'])>=split);assert np.array_equal(end,whole&(t['entrance_kind']!=0))
   fields={}
   for label,mask in [('endcap_both',end),('endcap_plus',end&(t['eta_pos']>0)),('endcap_minus',end&(t['eta_pos']<0))]:
    bad=t['incomplete'][mask];passed=t['outer_unique_faces'][mask]>=6
    fields[label]=dict(N=int(mask.sum()),incomplete=int(bad.sum()),proven_six_global_faces=int(passed.sum()),possible_six_global_faces=int((passed|bad).sum()))
   cases.append(dict(local_momentum_GeV=mom,charge=q,regions=fields))
 warm_a=mag['warm']['normal_m']/2;ect=mag['coil_groups']['endcap_plus'];front=ect['center_z_m']-ect['half_z_m']-warm_a;rear=ect['center_z_m']+ect['half_z_m']+warm_a;h=c['depth_m']/2;clear=c['coil_clearance_m'];hcal=mag['hcal']['endcap_back_abs_z_m'];inner_max=front-clear-h;outer_min=rear+clear+h
 result=dict(assignment='W-P1',revision=a.revision,status='Planning controls, not a proposed physical layout or ACTS rerun',geometry_sha256=hashlib.sha256(geo_raw).hexdigest(),tracks_sha256=hashlib.sha256(raw).hexdigest(),inventory=rows,
  region=dict(definition='Original closed-entrance-cap angular region; |eta_position|>=asinh(6.5/4.35), frozen for comparisons',abs_eta_boundary=split,full_sphere_fraction=float(1-np.tanh(split)),source='Original prepared direction labels; no selection by observed hits or candidate layout',baseline_cases=cases),
  domain=dict(ECT_warm_front_abs_z_m=front,ECT_warm_rear_abs_z_m=rear,chamber_depth_m=c['depth_m'],coil_clearance_m=clear,inner_before_ECT_max_center_abs_z_m=inner_max,inner_before_ECT_max_front_abs_z_m=inner_max-h,existing_entrance_half_z_m=cfg['entrance']['half_z_m'],outer_after_ECT_min_center_abs_z_m=outer_min,outer_after_ECT_min_back_abs_z_m=outer_min+h,current_world_half_z_m=11.5,current_map_half_z_m=12.5,old_world_minus_chamber_back_m=.25,old_map_minus_world_m=1.,example_paired_world_half_z_m=outer_min+h+.25,example_paired_map_half_z_m=outer_min+h+.25+1.,fixed_full_radius_HCAL_ECT_gap_m=front-hcal,clearance_depth_deficit_m=c['depth_m']+2*clear-(front-hcal)),
  limits=['Original endcap-region numbers are global all-family face counters, not endcap-only station counters.','Actual candidate dimensions depend on the physical-interface decision.','The synthetic common entrance must precede every candidate chamber face; the original cap can omit an inward-moved wheel.','No native propagation, geometry amendment or efficiency validation executed.'])
 a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({k:result[k] for k in ['inventory','domain']},indent=2));print('Region',split,'N/side',cases[0]['regions'])
if __name__=='__main__':main()
