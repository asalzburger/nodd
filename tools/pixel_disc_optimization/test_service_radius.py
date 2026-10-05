"""Independent radial bounds, preserved transforms, acceptance loss and capacity controls."""
import math
import unittest

import radial
import service_radius as service
from study import metrics


class ServiceRadiusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg,cls.limits,cls.prior=service.load_config()
        cls.removed,cls.rings=service.choose_rows(cls.cfg,cls.limits,cls.prior)

    def test_whole_outer_ring_removal_preserves_inner_and_all_surviving_transforms(self):
        self.assertEqual(self.removed,[8])
        for datum in [615.2,3070.]:
            before,_=service.source_modules(self.cfg,self.prior,datum)
            after=service.placed_modules(self.cfg,self.prior,datum,self.removed)
            self.assertEqual(len(before)-len(after),63)
            self.assertEqual(len(after),296)
            self.assertEqual(after,[m for m in before if m['row']<8])
            self.assertEqual(sum(m['row']==0 for m in after),18)

    def test_body_land_and_tube_reservations_fit_while_inherited_quad_land_fails(self):
        for datum in [615.2,3070.]:
            modules=service.placed_modules(self.cfg,self.prior,datum,self.removed)
            screen=service.interface_screen(modules,self.cfg,self.limits)
            self.assertTrue(screen['passed'])
            self.assertLess(screen['maximum_reserved_radius_mm'],188.5)
            self.assertGreater(screen['collector_clearance_mm'],2.)
            self.assertEqual(screen['pickup_land_offset_mm'],[7.6])
            self.assertFalse(screen['inherited_land_control_pass'])
        original,_=service.source_modules(self.cfg,self.prior,615.2)
        self.assertFalse(service.interface_screen(original,self.cfg,self.limits)['passed'])

    def test_original_annulus_loss_is_detected_without_changing_target(self):
        modules=service.placed_modules(self.cfg,self.prior,615.2,self.removed)
        self.assertEqual(self.cfg['annulus_mm'],[32.3,181.4550267061104])
        for vertex in [-150.,0.,150.]:
            active=metrics(radial.project(modules,self.cfg,615.2,vertex=vertex),self.cfg)
            self.assertGreater(active['uncovered_annulus_superset_mm2'],2000.)
            self.assertLess(active['covered_fraction'],.98)

    def test_service_capacity_keeps_fixed_trunk_and_flange_neck(self):
        modules=service.placed_modules(self.cfg,self.prior,615.2,self.removed)
        rings=[r for r in self.rings if r['row'] not in self.removed]
        svc=service.fixed_services(modules,rings,self.cfg,self.limits)
        self.assertEqual((svc['trunk_inner_mm'],svc['trunk_outer_mm']), (192.,231.7))
        self.assertEqual(svc['flange_neck_outer_mm'],222.)
        self.assertEqual(svc['local_feed_return_radial_legs'],2*svc['local_circuits'])
        for scenario in svc['scenarios']:
            for side in scenario['end_trunks']:
                self.assertLess(side['flange_neck_capacity_mm2'],side['capacity_mm2'])
                self.assertAlmostEqual(side['flange_neck_capacity_mm2']/side['capacity_mm2'],(222**2-192**2)/(231.7**2-192**2))
                self.assertEqual(side['status'],'PASS' if side['after_disc_8_demand_mm2']<=side['capacity_mm2'] else 'FAIL')


if __name__=='__main__':unittest.main()
