"""Conservation and failure controls for the additive service prototype."""
import copy
import json
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import services


class ServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=json.loads((services.HERE/'inputs.json').read_text())
        cls.mount=json.loads((services.HERE/'mounting.json').read_text())
        cls.settings=json.loads((services.HERE/'services.json').read_text())
        cls.inputs=json.loads((services.ROOT/'tools/module_layout/services_budget_inputs.json').read_text())
        cls.layout=services.load_layout(cls.config)
        before=copy.deepcopy(cls.layout)
        cls.result,cls.export,cls.mounts=services.build(cls.layout,cls.config,cls.mount,cls.inputs,cls.settings)
        assert cls.layout==before, 'Service proposal mutated the baseline'

    def test_ownership_and_terminal_budget(self):
        groups=self.export['groups']
        ids=[mid for g in groups for mid in g['module_ids']]
        expected={b['module_id'] for b in self.layout['bodies'] if b['subsystem']=='pixel' and b['region']=='barrel'}
        self.assertEqual(set(ids),expected);self.assertEqual(len(ids),len(expected))
        self.assertEqual(len(groups),164)
        inherited=[g for g in services.budget._groups(self.layout,self.inputs) if g['subsystem']=='pixel' and g['region']=='barrel']
        terminal=services.budget._inventory(inherited,self.inputs)
        for scenario in self.inputs['scenarios']:
            self.assertAlmostEqual(sum(sum(g['scenarios'][scenario]['terminal_footprint_mm2'].values()) for g in groups),terminal['scenarios'][scenario]['cables_mm2'])
        inner=[g for g in groups if g['layer_id']=='A-pixel-B1' and g['col']==0]
        self.assertEqual(sorted(g['modules'] for g in inner),[23,24])
        self.assertEqual(self.result['totals']['chains'],328)

    def test_link_volume_independent_path_sum_and_monotonicity(self):
        bodies={b['module_id']:b for b in self.layout['bodies']}
        for g in self.export['groups']:
            # A reference module contributes two links all the way from pickup
            # to the bay. This independent per-source sum checks step integration.
            expected=sum(2*(555-abs(bodies[mid]['center_mm'][2])) for mid in g['module_ids'])
            self.assertAlmostEqual(g['scenarios']['reference']['footprint_volume_mm3']['links'],expected,places=6)
            steps=[s for s in self.export['longitudinal'] if s['group_id']==g['id'] and s['scenario']=='reference']
            self.assertEqual([s['r_max_mm'] for s in steps],sorted(s['r_max_mm'] for s in steps))
            for s in steps:
                area=.5*s['phi_width_rad']*(s['r_max_mm']**2-s['r_min_mm']**2)
                self.assertAlmostEqual(area,s['envelope_area_mm2'],places=8)
                self.assertLessEqual(s['counts']['chains'],g['chains'])
        targets={s['id'] for s in self.export['longitudinal']}|{s['id'] for s in self.export['radial']}
        self.assertTrue(all(s['connects_to'] in targets for s in self.export['longitudinal']))

    def test_counterflow_and_uneven_sectors(self):
        circuits=self.export['circuits'];self.assertEqual(len(circuits),164)
        self.assertAlmostEqual(sum(c['flow_g_s'] for c in circuits),328.4)
        for s in self.result['sectors']:
            inlet=[c for c in circuits if c['sector']==s['sector'] and c['inlet_side']==s['side']]
            exhaust=[c for c in circuits if c['sector']==s['sector'] and c['exhaust_side']==s['side']]
            self.assertEqual(len(inlet),s['staves']);self.assertEqual(len(exhaust),s['staves'])
            self.assertAlmostEqual(sum(c['flow_g_s'] for c in inlet),s['feed_g_s'])
            self.assertAlmostEqual(sum(c['nominal_heat_W'] for c in exhaust),s['nominal_exhaust_heat_W'])
            self.assertAlmostEqual(s['pair_OD_mm']**2,16*s['staves'])
        self.assertEqual({s['staves'] for s in self.result['sectors']},{6,7})
        self.assertEqual(services.sector_index(-1e-8,12),0)
        self.assertEqual(services.sector_index(2*math.pi-1e-8,12),0)

    def test_failures_are_retained_not_relabeled(self):
        r=self.result['scenarios']
        self.assertTrue(r['reference']['barrel_envelope_pass'])
        self.assertLess(r['reference']['radial_peak_utilization'],1)
        self.assertLess(r['reference']['axial_peak_utilization'],1)
        for name in ['conservative','stress']:
            self.assertFalse(r[name]['barrel_envelope_pass'])
            self.assertGreater(r[name]['radial_peak_utilization'],1)
            self.assertGreater(r[name]['axial_peak_utilization'],1)
        self.assertIsNone(r['reference']['cable_mass_g'])
        # Each radial interval preserves the exact sum of incoming cable area.
        groups={g['id']:g for g in self.export['groups']}
        for route in self.export['radial']:
            gs=[g for g in groups.values() if g['side']==route['side'] and g['sector']==route['sector']]
            for seg in route['segments']:
                incoming=[g for g in gs if g['inner_radius_mm']<=seg['r_min_mm']]
                self.assertEqual(seg['staves'],len(incoming))
                for kind in ['ancillary','links']:
                    self.assertAlmostEqual(seg['footprint_mm2'][kind],sum(g['scenarios'][route['scenario']]['terminal_footprint_mm2'][kind] for g in incoming))

    def test_finite_extraction_and_displaced_control(self):
        self.assertEqual(self.result['reference_extraction_body_conflicts'],[])
        moved=copy.deepcopy(self.export)
        route=next(r for r in moved['radial'] if r['scenario']=='reference' and r['side']=='positive')
        route['segments'][0]['abs_z_center_mm']=540  # named collision fixture
        self.assertTrue(services.extraction_body_conflicts(self.layout,moved))
        for r in self.export['radial']:
            self.assertLess(r['axial']['r_min_mm'],self.settings['handoff_radius_mm'])
            self.assertGreater(r['axial']['r_max_mm'],self.settings['handoff_radius_mm'])

    def test_invalid_interfaces_and_no_invented_composition(self):
        for key,value in [('handoff_radius_mm',240),('sectors',0),('transport_wall_mm',2),('cable_composition_volume_fractions',{'Cu':1})]:
            settings=dict(self.settings);settings[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                services.build(self.layout,self.config,self.mount,self.inputs,settings)


if __name__=='__main__':unittest.main()
