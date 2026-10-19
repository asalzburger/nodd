"""Controls for finite support material, real contacts and grounded identities."""
import copy
import json
import math
from pathlib import Path
import unittest
import numpy as np
from tools.muon_layout import geometry as geo
from tools.muon_layout import support as s


class SupportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.design=json.loads(Path('tools/muon_layout/design.json').read_text())
        cls.model=s.build_supports(cls.design)
        cls.mag=json.loads(Path('docs/validation/DES-039/results.json').read_text())['configuration']
        cls.validation=s.validate_supports(cls.model,cls.mag)

    def test_fixed_members_ports_and_material_ground_connectivity(self):
        r=self.validation
        self.assertTrue(r['valid'],r['failed_coil_checks'])
        self.assertEqual(r['member_count'],484);self.assertEqual(r['material_part_count'],1378)
        self.assertEqual(r['case_count'],36);self.assertEqual(r['port_count'],156);self.assertEqual(r['ground_count'],10)
        self.assertEqual(len(r['components']),1)
        self.assertEqual(r['ungrounded_cases'],[]);self.assertEqual(r['ungrounded_members'],[])
        self.assertEqual(r['cross_material_penetrations'],[])
        self.assertTrue(all(x['valid'] for x in r['port_checks']))
        self.assertTrue(all(x['contact_area_m2']>1 for x in r['ground_checks']))
        self.assertTrue(any(x['kind']=='material_face_contact' for x in r['contacts']))
        self.assertTrue(any(x['kind']=='overlapping_material' for x in r['contacts']))

    def test_hollow_material_excludes_cavity_and_has_exact_section_volume(self):
        b=s._beam('TEST-TUBE',[0,0,-1],[0,0,1],.4,.3,[1,0,0],.02,'TEST',1.,'test')
        parts=s.material_parts(b)
        expected=2*(.4*.3-.36*.26)
        self.assertAlmostEqual(sum(geo.volume(x) for x in parts),expected,places=12)
        self.assertTrue(geo.contains(b,[[0,0,0]])[0])
        self.assertFalse(any(geo.contains(x,[[0,0,0]])[0] for x in parts))
        floating=s._beam('TEST-IN-CAVITY',[0,0,-.2],[0,0,.2],.1,.1,[1,0,0],0,'TEST',1.,'test')
        self.assertTrue(geo.intersects(b,floating))
        self.assertIsNone(s._contact(parts,s.material_parts(floating)))

    def test_declared_roll_and_case_skin_patches(self):
        byid={x['id']:x for x in self.model['members']}
        # The radial BT lug's transverse dimensions are tangential and axial,
        # rather than a helper-axis roll inferred independently for each beam.
        b=byid['BT-LUG00-2'];v=geo.vertices3(b)
        np.testing.assert_allclose(v.min(axis=0),[9.05,-.15,-.15],atol=1e-12)
        np.testing.assert_allclose(v.max(axis=0),[9.15,.15,.15],atol=1e-12)
        for x in self.validation['port_checks']:
            self.assertTrue(x['on_skin'] and x['outward_clear'] and x['inward_occupied'] and x['actual_lug_face'])
        self.assertTrue(all(x['pack']['clear'] and x['cold']['clear'] and x['warm']['clear'] for x in self.validation['coil_checks']))

    def test_mitered_ring_stock_volume_matches_analytic_hollow_ring(self):
        ring=[x for x in self.model['members'] if x['id'].startswith('PORTAL0/')]
        volume=sum(geo.volume(w) for x in ring for w in s.material_parts(x))
        perimeter=24*9.3*math.tan(math.pi/12)
        self.assertAlmostEqual(volume,perimeter*(.30*.40-.26*.36),places=11)
        # Adjacent sectors meet through material on a miter face, not a centre
        # floating in their cross-section cavities.
        contact=s._contact(s.material_parts(ring[0]),s.material_parts(ring[1]))
        self.assertEqual(contact['kind'],'material_face_contact')
        self.assertGreater(contact['area_m2'],0)

    def test_importance_union_matches_known_overlap_and_disjoint_controls(self):
        a=s._beam('TEST-A',[0,0,-.5],[0,0,.5],1.,1.,[1,0,0],0,'TEST',1.,'test')
        b=copy.deepcopy(a);b['id']='TEST-B';b['origin_m'][0]=.5
        r=s.support_mass([a,b],samples=131072,seed=85)['materials']['TEST']
        self.assertAlmostEqual(r['gross_stock_volume_m3'],2.)
        self.assertLess(abs(r['unique_union_volume_m3']-1.5),5*r['union_volume_standard_error_m3'])
        b['origin_m'][0]=2.
        d=s.support_mass([a,b],samples=1000,seed=86)['materials']['TEST']
        self.assertEqual(d['unique_union_volume_m3'],2.);self.assertEqual(d['union_volume_standard_error_m3'],0.)

    def test_stock_reproduces_proposal_and_union_reduces_only_shared_stock(self):
        r=s.support_mass(self.model['members'],samples=65536,seed=40036)
        self.assertAlmostEqual(r['gross_stock_mass_kg'],131193.12131951563,places=6)
        self.assertLess(r['unique_mass_kg'],r['gross_stock_mass_kg'])
        self.assertGreater(r['unique_mass_kg'],.97*r['gross_stock_mass_kg'])
        self.assertEqual(r['materials']['SS_proxy']['maximum_sampled_multiplicity'],1)
        self.assertEqual(r['materials']['SS_proxy']['union_volume_standard_error_m3'],0.)
        self.assertGreater(r['materials']['Al_proxy']['union_volume_standard_error_m3'],0.)

    def test_touching_faces_have_area_but_point_contact_does_not_connect(self):
        a=s._beam('TEST-A',[0,0,-.5],[0,0,.5],1.,1.,[1,0,0],0,'TEST',1.,'test')
        b=copy.deepcopy(a);b['id']='TEST-B';b['origin_m'][0]=1.
        r=s._contact([a],[b]);self.assertEqual(r['kind'],'material_face_contact');self.assertAlmostEqual(r['area_m2'],1.)
        b['origin_m']=[1.,1.,1.]
        self.assertIsNone(s._contact([a],[b]))

    def test_missing_port_is_not_hidden_by_other_case_attachments(self):
        m=copy.deepcopy(self.model);m['ports']=m['ports'][1:]
        r=s.validate_supports(m,self.mag,check_coils=False)
        self.assertFalse(r['valid']);self.assertFalse(r['count_checks']['expected_port_counts'])

    def test_case_face_contact_does_not_exempt_an_inward_lug(self):
        port=next(x for x in self.model['ports'] if x['member_id']=='BT-LUG00-2')
        body=copy.deepcopy(next(x for x in self.model['members'] if x['id']==port['member_id']))
        self.assertTrue(s._lug_warm_certificate(body,port,self.mag)['clear'])
        body['origin_m'][0]-=.10
        proof=s._lug_warm_certificate(body,port,self.mag)
        self.assertFalse(proof['entire_lug_outward']);self.assertFalse(proof['clear'])

    def test_feet_are_asymmetric_and_actual_material_ray_misses_cavities(self):
        feet=[x for x in self.model['members'] if x['category'].startswith('foot_')]
        self.assertTrue(all(geo.aabb(x)[1][1]<0 for x in feet))
        self.assertEqual(len([x for x in feet if x['category']=='foot_SS_baseplate']),10)
        # Side ray hits the outer envelope but can pass through an open tube's
        # normal end; material intervals remain a separate physical quantity.
        tube=s._beam('TEST-ZTUBE',[0,0,2],[0,0,4],.4,.4,[1,0,0],.02,'TEST',1.,'test')
        lo,hi=geo.ray_intervals(tube,[[0,0,1]])
        self.assertTrue(np.isfinite(lo[0]))
        self.assertTrue(all(not np.isfinite(geo.ray_intervals(x,[[0,0,1]])[0][0]) for x in s.material_parts(tube)))


if __name__=='__main__':unittest.main()
