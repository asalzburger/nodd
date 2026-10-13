import unittest
from endcap_geometry import build
from endcap_export import totals
from endcap_services import augment
class EndcapServiceTests(unittest.TestCase):
    def test_board_inventory_and_displaced_mass(self):
        r,m=build();augment(r,m);totals(r)
        s=r['services']['physical_endcaps']
        self.assertEqual(s['board_slots_each'],1584);self.assertEqual(s['capacity_channels_each'],811008)
        self.assertEqual(s['cooling_branches_each'],48)
        self.assertGreater(s['capacity_power_kW_scenarios_each'][-1],40)
        roots={p['name']:p for p in r['passive']}
        for name in ('rear_bath_1','rear_bath_2'):
            p=roots[name];children=[x for x in r['passive'] if x.get('parent_name')==name]
            self.assertAlmostEqual(p['volume_mm3'],p['exclusive_volume_mm3']+sum(x['volume_mm3'] for x in children))
        self.assertAlmostEqual(sum(x['mass_g'] for x in r['material_totals'].values()),r['mass_g'])
if __name__=='__main__':unittest.main()
