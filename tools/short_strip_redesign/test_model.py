"""DES043 requirements/negative controls, independent of committed plot bytes."""
import copy
import math
import unittest
import model
from diagnostics import cooling_routes, sampled_interloop_clearance, cooling_pieces, pad_contacts


class DesignScreens(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=model.load();cls.parts=model.geometry(cls.c)

    def test_population_and_readout(self):
        *_,old,long,new=self.parts
        self.assertEqual(len(new['modules']),4752)
        counts=[sum(m['layer']==0 and m['ring']==i for m in new['modules']) for i in range(5)]
        self.assertEqual(counts,[48,60,84,96,108])
        self.assertEqual((8064+len(new['modules']))*30720,393707520)

    def test_finite_edge_minimum(self):
        sensor=dict(center_mm=[10,0,0],u=[0,1,0],v=[-1,0,0],half_u_mm=3,half_v_mm=2)
        minimum,maximum=model.radial_bounds(sensor)
        self.assertEqual(minimum,8)
        self.assertAlmostEqual(maximum,math.sqrt(153))
        self.assertLess(minimum,math.sqrt(8**2+3**2))

    def test_gap_and_finite_body(self):
        *_,old,long,new=self.parts
        outer=max(model.radial_bounds(x)[1] for x in new['modules'])
        inner=min(model.radial_bounds(x)[0] for x in long['modules'])
        self.assertAlmostEqual(inner-outer,82.33481340506682)
        self.assertLess(max(math.hypot(x['radius_mm']+51.5,24.5) for x in new['modules']),710.)
        self.assertGreater(783.5-self.c['trunk_mm'][1],1.99)

    def test_discrete_bus_known_two_taps(self):
        result=model.bus([0,500],1000,10,10,.02,1)
        self.assertAlmostEqual(result['return_drop_V'],.03)
        self.assertAlmostEqual(result['loss_W'],.1)

    def test_warm_rail_rejection_control(self):
        bl=self.parts[3]
        taps=[x['center_mm'][2] for x in bl['modules'] if x['layer']==0 and x['stave']==0 and x['center_mm'][2]>0]
        w=self.c['reference_electronics_W']*.625;rho=.0175*1.4
        self.assertLess(model.bus(taps,1210,w,11,rho,12*.17)['return_drop_V'],.2)
        self.assertGreater(model.bus(taps,1210,w,11,rho,12*.15)['return_drop_V'],.2)

    def test_connector_allowance_selects_ten_mm2(self):
        w=self.c['reference_electronics_W']*.625;current=(14*w+5)/11
        bus_drop=2*.185707390702345
        self.assertLess(2*.0175*1.4*3.5/10*current+bus_drop+.15,1.)
        self.assertGreater(2*.0175*1.4*3.5/8*current+bus_drop+.15,1.)

    def test_packing_throats_and_rejections(self):
        bl=self.parts[3];n=len(self.parts[-1]['modules']);p=model.packing(self.c,bl,n)
        self.assertTrue(all(x['passed'] and x['new_collector_join_fill']<1 for x in p))
        self.assertGreater(max(x['old_collector_join_fill'] for x in p),1)
        c=copy.deepcopy(self.c);c['trunk_mm'][:2]=[725,783]
        self.assertGreater(max(x['fill_ratio'] for x in model.packing(c,bl,n)),1)
        c['power_cable_OD_mm']=10;c['trunk_mm'][:2]=[710,783]
        self.assertGreater(max(x['fill_ratio'] for x in model.packing(c,bl,n)),1)

    def test_thermal_floor_and_no_scaling_rejection(self):
        t=model.thermal(self.c,'endcap')
        self.assertLess(-35+(self.c['reference_electronics_W']*.625+2)*t['R_K_W']+t['distributed_leakage_corner_K']+t['upstream_sensor_leakage_K'],-20)
        self.assertGreater(-35+(self.c['reference_electronics_W']+2)*t['R_K_W']+t['distributed_leakage_corner_K']+t['upstream_sensor_leakage_K'],-20)

    def test_pipe_ports_are_positive_and_disjoint(self):
        result=cooling_routes(self.c,self.parts[1])
        self.assertTrue(result['interloop_clearance']['passed'])
        self.assertGreater(result['new_total_length_mm'],result['old_total_length_mm'])
        # Natural ascending angle assignment crosses the outer entry fillet.
        a=cooling_pieces(self.c['ring_centres_mm'][:3],[27,27.5],712)
        b=cooling_pieces(self.c['ring_centres_mm'][3:],[28,28.5],712)
        self.assertFalse(sampled_interloop_clearance(a,b,2.5)['passed'])

    def test_explicit_upstream_and_ASIC_bond_heat_paths(self):
        t=model.thermal(self.c,'endcap')
        self.assertAlmostEqual(t['terms_K_W']['ASIC_bond'],.00005/(1.2*2*.0234**2))
        self.assertEqual(t['upstream_sensor_leakage_K'],1.)
        q=self.c['reference_electronics_W']*.625+2
        maximum=-35+q*t['R_K_W']+t['distributed_leakage_corner_K']+t['upstream_sensor_leakage_K']
        self.assertGreater(maximum,-20.34);self.assertLess(maximum,-20.32)

    def test_every_module_has_a_pipe_saddle(self):
        pipes=cooling_routes(self.c,self.parts[1]);contacts=pad_contacts(self.c,self.parts[-1],pipes)
        self.assertEqual(contacts['checked_modules'],33)
        self.assertEqual(contacts['failed_modules'],0)
        legacy={key:cooling_pieces(centres,[29,28],712) for key,centres in [('inner',self.c['ring_centres_mm'][:3]),('outer',self.c['ring_centres_mm'][3:])]}
        self.assertGreater(pad_contacts(self.c,self.parts[-1],legacy)['failed_modules'],0)

    def test_material_debits_and_no_void_mass(self):
        bc,ec,_,bl,old,_,new=self.parts;m=model.material(self.c,bc,ec,bl,old,new)
        self.assertEqual(m['power_feeds_both_ends'],dict(old=1584,new=1008))
        self.assertEqual(m['optical_groups_both_ends'],dict(old=1584,new=1584))
        by={x['component']:x for x in m['entries']}
        self.assertGreater(by['Direct graphite inserts and added pickups']['delta_kg'],8064*2*20*64*3.1*2.21/1e6)
        self.assertGreater(by['New TIM and module service reserve']['delta_kg'],80)
        self.assertGreater(by['Additional EC cooling pipe bank']['delta_kg'],0)
        self.assertLess(m['delta_kg'],0)
        self.assertLess(m['new_copper_mm2'],math.pi*8**2/4)
        self.assertAlmostEqual(m['delta_kg'],sum(x['delta_kg'] for x in m['entries']))


if __name__=='__main__':unittest.main()
