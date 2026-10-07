import copy,json,math,tempfile,unittest
from pathlib import Path
from model import load,build,deflection,point,axes
from components import Export
class Controls(unittest.TestCase):
 def test_continuous_beam_limit(self):
  from mechanics import solve
  c=load();c['half_length_mm']=100;payload=dict(continuous_g=10,point_loads=[])
  screen=dict(anchors_z_mm=[-100,100],EI_N_mm2=1e7,shear_rigidity_N=1e4,load_factor=1)
  a=solve(c,payload,screen,10);q=.01*9.80665/200
  reference=5*q*200**4/(384*1e7)+q*200**2/(8*1e4)
  self.assertAlmostEqual(a['maximum_deflection_mm'],reference,delta=reference*.005)
  self.assertLess(a['maximum_support_residual_mm'],1e-12)
 def test_source_pin(self):
  c=load();c['input_sha256']['detector/config/elements.json']='0'*64
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'bad.json';p.write_text(json.dumps(c))
   with self.assertRaisesRegex(ValueError,'Pinned source'):load(p)
 def test_true_pair_and_stereo(self):
  c=load();l=build(c);a,b=l['modules'][:2]
  self.assertEqual(a['module_id'],b['module_id']);self.assertNotEqual(a['sensor_id'],b['sensor_id'])
  self.assertAlmostEqual(sum(x*y for x,y in zip(a['u'],b['u'])),math.cos(.04))
  self.assertAlmostEqual(math.dist(a['center_mm'],b['center_mm']),6.7)
 def test_shear_not_omitted(self):
  c=load();p=dict(continuous_g=1000,point_loads=[])
  a=deflection(c,p,17,G=5);b=deflection(c,p,17,G=10)
  self.assertGreater(a['core_shear_mm'],a['bending_mm']);self.assertAlmostEqual(a['core_shear_mm'],2*b['core_shear_mm'])
 def test_uniform_load_analytic(self):
  c=load();p=dict(continuous_g=1000,point_loads=[]);r=deflection(c,p,2,factor=1);L=r['span_mm'];q=9.80665/(2*c['half_length_mm'])
  self.assertAlmostEqual(r['bending_mm'],5*q*L**4/(384*r['EI_N_mm2']))
 def test_point_load_monotonic(self):
  c=load();p=dict(continuous_g=100,point_loads=[[0,200]])
  self.assertGreater(deflection(c,p,2)['total_mm'],deflection(c,p,3)['total_mm'])
 def test_pipe_rejected(self):
  c=load();c['tube_OD_mm']=6
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'bad.json';p.write_text(json.dumps(c))
   with self.assertRaisesRegex(ValueError,'Pipe'):load(p)
 def test_overfilled_service_rejected(self):
  x=Export(load(),'LongStripBarrel')
  with self.assertRaisesRegex(ValueError,'exceeds'):x.materials.effective('bad',{'Copper':2},1)
if __name__=='__main__':unittest.main()
