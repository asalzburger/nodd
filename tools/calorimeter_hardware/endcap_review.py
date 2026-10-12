"""DES029 packing diagnosis and illustrative counterfactuals; run from repo root."""
import json,math,copy,sys,subprocess
from pathlib import Path
root=Path.cwd();sys.path.insert(0,str(root/'tools/calorimeter_hardware'))
from assembly import inventory
from model import sha
from test_assemblies import check_containment
r,_=inventory();units={u['name']:u for u in r['units']};result=dict(method_sha256=sha(__file__),status='DRAFT analytical diagnosis; no geometry change or native validation of alternatives',execution=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=r['source_sha256']),baseline=[],packing_counterfactuals=[])
for region in r['regions']:
 if region['kind']!='endcap':continue
 u=units[region['unit']];placements=[p for p in region['placements'] if p['layer']==0];parts=[p for p in u['parts'] if p['role']=='sensitive'];rows={}
 for p in placements:rows.setdefault(str(p['center_mm'][0]),0);rows[str(p['center_mm'][0])]+=1
 active=sum(p['dimensions_mm']['sx']*p['dimensions_mm']['sy'] for p in parts)
 first=min(p['center_mm'][0]+q['center_mm'][1]-q['dimensions_mm']['sy']/2 for p in placements for q in parts)
 result['baseline'].append(dict(subsystem=u['name'],coverage=region['coverage'][0],cassette_size_mm=[u['width_mm'],u['height_mm']],cassette_sensitive_area_mm2=active,cassette_active_fill=active/(u['width_mm']*u['height_mm']),row_centres_and_counts=rows,inner_sensitive_radius_mm=first,first_front_eta_estimate=math.asinh(region['front_mm']/first),illustrative_eta3_radius_at_front_mm=region['front_mm']/math.sinh(3),minimum_cassette_inner_fit_radius_mm=(u['width_mm']/2+r['config']['seam_half_gap_mm']+r['config']['edge_allocation_mm'])/math.tan(math.pi/r['config']['sectors'])))
for sectors,edge in ((16,40),(16,20),(12,40),(8,40),(8,20)):
 c=copy.deepcopy(r['config']);c['sectors']=sectors;c['edge_allocation_mm']=edge;x,_=inventory(c);check_containment(x)
 result['packing_counterfactuals'].append(dict(sectors=sectors,edge_allocation_mm=edge,logical_corner_check='PASS',endcaps=[dict(subsystem=z['unit'],coverage=z['coverage'][0]) for z in x['regions'] if z['kind']=='endcap']))
p=Path('docs/validation/DES-029/endcap-coverage-review.json');p.write_text(json.dumps(result,indent=2)+'\n')
print([(b['subsystem'],b['coverage']['occupied_fraction'],b['cassette_active_fill'],b['inner_sensitive_radius_mm']) for b in result['baseline']])
