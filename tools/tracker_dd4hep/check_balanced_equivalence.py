"""Read-only XML dimensions/transforms/ID diagnostic, not native qualification.

Compare maintained source export with the audited DES040 study compact. Local
endcap child order is retained; barrel feet are matched by stable names because
the study writer regrouped them by stave. Angular parameters are modulo2pi.
Labels and material-reference names are excluded; material identity needs its
separate recipe/native audit. No XML is modified.
"""
import argparse,hashlib,json,math
from pathlib import Path
import xml.etree.ElementTree as E
p=argparse.ArgumentParser();p.add_argument('--reference',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
a=E.parse(args.reference).getroot();b=E.parse(args.candidate).getroot();issues=[];counts={'endcap':0,'barrel':0}
def number(x):return float(x.split('*')[0])
def compare(x,y,path,group):
 counts[group]+=1
 if x is None or y is None:issues.append([path,'missing']);return
 if x.tag!=y.tag:issues.append([path,'tag',x.tag,y.tag]);return
 for key in set(x.attrib)|set(y.attrib):
  if key in ('name','vis','material'):continue
  u,v=x.get(key,''),y.get(key,'')
  try:
   difference=number(u)-number(v)
   if key in ('phi','rx','ry','rz'):difference=math.remainder(difference,2*math.pi)
   equal=abs(difference)<1.e-9 and u.partition("*")[2]==v.partition("*")[2]
  except (ValueError,TypeError):equal=u==v
  if not equal:issues.append([path,key,u,v])
 if len(x)!=len(y):issues.append([path,'children',len(x),len(y)]);return
 for i,(q,r) in enumerate(zip(x,y)):compare(q,r,path+'/'+q.tag+str(i),group)
for system in (2,3):
 for layer in range(1,11):
  path=f'./detectors/detector[@id="{system}"]/disc[@id="{layer}"]'
  compare(a.find(path),b.find(path),f'{system}:{layer}','endcap')
for layer in range(1,5):
 path=f'./detectors/detector[@id="1"]/layer[@id="{layer}"]'
 before,after=a.find(path),b.find(path)
 for tag in ('stave','ring','foot'):
  aa=before.findall(tag);bb={q.get('name'):q for q in after.findall(tag)}
  if len(aa)!=len(bb):issues.append([f'1:{layer}/{tag}','count',len(aa),len(bb)])
  for q in aa:compare(q,bb.get(q.get('name')),f'1:{layer}/{tag}{q.get("name")}','barrel')
def fingerprint(path):return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
result={'status':'FAIL' if issues else 'PASS','reference':fingerprint(args.reference),'candidate':fingerprint(args.candidate),'tolerance_mm':1.e-9,'angular_comparison':'Modulo2pi,1e-9rad','barrel_correspondence':'Stable XML name within each existing logical layer; study XML reorders feet','endcap_correspondence':'Existing logical ID1..9, added logical ID10; identical donor local child order','excluded_attributes':['name','vis','material'],'scope':'Local repeated-unit parameters/transforms/readoutIDs only; excludes material-reference names, global service attachments and native construction','checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'nodes_compared':counts,'differences':issues}
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='differences'},indent=2));raise SystemExit(bool(issues))
