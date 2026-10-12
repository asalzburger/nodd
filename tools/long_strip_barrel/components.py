"""Primitive XML and analytical constituent inventory shared by DES-022/023."""
from pathlib import Path
from collections import Counter,defaultdict
import math,sys,json,xml.etree.ElementTree as ET
from model import ROOT,sha,point
sys.path.insert(0,str(ROOT/'tools/pixel_barrel_dd4hep'))
from materials import Materials
I=[[1,0,0],[0,1,0],[0,0,1]]
TUBE=[[1,0,0],[0,0,1],[0,-1,0]] # cylinder axis local v

def volume(kind,d):
 if kind in ('box','shoe'):return d['sx']*d['sy']*d['sz']
 if kind in ('tube','sector'):return d.get('angle',2*math.pi)/2*(d['rmax']**2-d['rmin']**2)*d['length']
 if kind=='torus':return d['angle']*math.pi*d['major']*(d['rmax']**2-d['rmin']**2)
 raise ValueError(kind)
def compose(a,b):return [[sum(a[k][i]*b[j][k] for k in range(3)) for i in range(3)] for j in range(3)]
def attrs(center,frame):
 a={k:f'{v:.17g}*mm' for k,v in zip(('x','y','z'),center)}
 for i in range(3):
  for j in range(3):a[f'a{i}{j}']=format(frame[j][i],'.17g')
 return a
class Export:
 def __init__(self,c,name):
  self.c=c;self.name=name;self.entities=[];self.totals=defaultdict(lambda:dict(volume_mm3=0.,mass_g=0.))
  self.materials=Materials(dict(coolant_density_g_cm3=1,cfrp_carbon_mass_fraction=.7,module=dict(flex_copper_coverage=.5)),dict(density_g_cm3=dict(titanium=4.51,graphite=2.21,insulation=1.42,glue=2,CFRP=1.73,foam=.2)))
  self.materials.add('CarbonFoam',.2,{'C':1});self.materials.add('Aluminium',2.7,{'Al':1});self.materials.add('Silica',2.2,{'Si':1,'O':2},atoms=True)
  self.materials.effective('Electronics',{'Silicon':.04,'Copper':.01,'Polyimide':.10},1)
  self.doc=ET.Element('lccdd');ET.SubElement(self.doc,'info',name=name,title='isolated long-strip prototype',author='nODD',version='0.1',status='prototype')
  ET.SubElement(ET.SubElement(self.doc,'includes'),'gdmlFile',ref='materials.xml');defs=ET.SubElement(self.doc,'define')
  for k,v in dict(world_x=4000,world_y=4000,world_z=4000,tracker_region_rmax=1140,tracker_region_zmax=3300).items():ET.SubElement(defs,'constant',name=k,value=f'{v}*mm')
  ro=ET.SubElement(ET.SubElement(self.doc,'readouts'),'readout',name=name+'Hits')
  ET.SubElement(ro,'segmentation',type='CartesianStripX',strip_size_x=f"{c['pitch_mm']}*mm",offset_x=f"{c['pitch_mm']/2}*mm")
  ET.SubElement(ro,'id').text='system:5,layer:4,stave:8,module:6,sensor:1,strip:-12'
  self.det=ET.SubElement(ET.SubElement(self.doc,'detectors'),'detector',name=name,id=str(c['system_id']),type='nODDLongStrip',readout=name+'Hits');ET.SubElement(self.det,'sensitive',type='tracker')
 def add(self,name,role,mat,center,frame,kind,dims,ids=None):
  node=ET.SubElement(self.det,'piece',group='_'.join(name.split('_')[:2]) if name.startswith('L') else 'services' if role in ('routed_services','service_tray') else 'assembly_'+name,name=name,role=role,material=mat,kind=kind,**attrs(center,frame))
  for k,v in dims.items():node.set(k,f'{v:.17g}'+('*rad' if k in ('angle','start') else '' if k=='slope' else '*mm'))
  e=dict(shape_kind=kind,dimensions_mm=dims,name=name,role=role,center_mm=center,frame=frame,volume_mm3=volume(kind,dims),material=mat)
  if ids:
   node.set('sensitive','true')
   for k,v in ids.items():
    if k!='system':node.set(k,str(v))
   e.update(ids=ids,normal=frame[2],u=frame[0],v=frame[1],size_mm=[dims['sx'],dims['sy'],dims['sz']])
  e['mass_g']=e['volume_mm3']*self.materials.recipes[mat]['density_g_cm3']/1000
  self.entities.append(e);return node,e
 def box(self,name,role,mat,origin,frame,local,size,ids=None,rot=None):return self.add(name,role,mat,point(origin,frame,local),compose(frame,rot) if rot else frame,'box',dict(zip(('sx','sy','sz'),size)),ids)
 def cut(self,node,e,kind,center,frame,dims):
  cut=ET.SubElement(node,'cut',kind=kind,**attrs(center,frame))
  for k,v in dims.items():cut.set(k,f'{v:.17g}'+('*rad' if k in ('angle','start') else '' if k=='slope' else '*mm'))
  e['volume_mm3']-=volume(kind,dims)
  if e['volume_mm3']<=0:raise ValueError('Cut removes whole solid')
  e['mass_g']=e['volume_mm3']*self.materials.recipes[e['material']]['density_g_cm3']/1000
 def save(self,out,layout,engineering,input_path):
  from model import execution
  out.mkdir(parents=True,exist_ok=True)
  for e in self.entities:
   for key in ('volume_mm3','mass_g'):self.totals[e['material']][key]+=e[key]
  result=dict(name=self.name,system_id=self.c['system_id'],layers=len({m['layer'] for m in layout['modules']}),entities=self.entities,counts=dict(Counter(e['role'] for e in self.entities)),material_totals=dict(self.totals),material_recipes=self.materials.recipes,engineering=engineering,layout=layout,cell_mm=[self.c['pitch_mm']],provenance=dict(execution=execution(),input_sha256=sha(input_path),pinned_sources=self.c['input_sha256'],producer_sha256=sha(__file__),source_hashes={str(p.relative_to(ROOT)):sha(p) for p in (Path(__file__),Path(__file__).with_name('model.py'),Path(__file__).with_name('mechanics.py'),Path(__file__).with_name('export.py'),ROOT/'prototypes/long_strip_barrel/LongStrip.cpp',ROOT/'tools/pixel_barrel_dd4hep/materials.py')}))
  for p,n in ((out/'materials.xml',self.materials.root),(out/'long-strip.xml',self.doc)):
   ET.indent(n,space='  ');ET.ElementTree(n).write(p,encoding='utf-8',xml_declaration=True)
  (out/'expected.json').write_text(json.dumps(result,indent=2)+'\n');return result
