import json,math,tempfile,unittest
from pathlib import Path
from model import load,build,point,axes
class Controls(unittest.TestCase):
 def test_pin(self):
  c=load();c['input_sha256']['docs/validation/DES-022/inventory.json.gz']='0'*64
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'c.json';p.write_text(json.dumps(c))
   with self.assertRaisesRegex(ValueError,'Pinned'):load(p)
 def test_bounds(self):
  c=load();c['core_inner_mm']=782
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'c.json';p.write_text(json.dumps(c))
   with self.assertRaisesRegex(ValueError,'bounds'):load(p)
 def test_both_faces_proper_frames(self):
  l=build(load());seen=set()
  for m in l['modules']:
   key=m['layer'],m['module_id'],m['face'];self.assertNotIn(key,seen);seen.add(key)
   u,v=m['u'],m['v'];cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
   self.assertLess(math.dist(cross,m['n']),1e-12)
  for a,b in zip(l['modules'][::2],l['modules'][1::2]):
   self.assertEqual(a['module_id'],b['module_id']);self.assertAlmostEqual(sum(x*y for x,y in zip(a['u'],b['u'])),math.cos(.04))
 def test_row_local_ids_and_groups(self):
  l=build(load());pairs=[p for p in l['pairs'] if p['layer']==0 and p['petal']==0]
  self.assertEqual(len(pairs),26);self.assertEqual([p['local_id'] for p in pairs],list(range(26)))
  self.assertEqual(len(l['pairs']),3744)
 def test_loop_containment(self):
  c=load();start=c['seam_rad'];stop=2*math.pi/12-start
  # Test both straight endpoints and dense half-torus centre lines including OD.
  for uc in c['circuit_centers_u_mm']:
   for k in range(181):
    a=math.pi*k/180;u=uc+10*math.cos(a);v=-805+10*math.sin(a);x,y,z=point([0,0,0],axes(math.pi/12,side=1),[u,v,0]);r=math.hypot(x,y);angle=math.atan2(y,x)
    self.assertGreater(r-1.25,784);self.assertLess(r+1.25,1130);self.assertGreater(angle-math.asin(1.25/r),start);self.assertLess(angle+math.asin(1.25/r),stop)
 def test_web_collector_clearance(self):
  c=load()
  for u in c['web_u_mm']:
   v=math.sqrt(c['web_outer_radius_mm']**2-(abs(u)+c['web_width_mm']/2)**2)
   self.assertAlmostEqual(math.hypot(abs(u)+c['web_width_mm']/2,v),1114)
   self.assertLess(math.hypot(abs(u)+c['web_width_mm']/2,v),1115)
 def test_pair_circuit_assignment(self):
  from export import routes
  c=load();l=build(c);rr,_=routes(c,l)
  for r in rr:
   self.assertEqual(len(r['circuits']),6)
   self.assertTrue(all(0<len(a)<=12 for a in r['circuits']))
   self.assertEqual(sorted(m for a in r['circuits'] for m in a),r['pairs'])
 def test_group_overfill_rejection(self):
  from export import routes
  c=load();c['circuit_centers_u_mm']=[0]
  with self.assertRaisesRegex(ValueError,'Group cap'):routes(c,build(c))
 def test_collector_rejection(self):
  c=load();c['disc_z_mm'][0]=1403.65
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'c.json';p.write_text(json.dumps(c))
   with self.assertRaisesRegex(ValueError,'collector'):load(p)
if __name__=='__main__':unittest.main()
