import copy
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import ROOT,load_inputs,template,proposal,run_geometry,comparisons,digest
from thermal import sheet_resistance,thermal_screen
from budget import inventory,services


class DesignControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg,cls.layout,cls.base=load_inputs()
        cls.before=json.dumps(cls.layout,sort_keys=True)
        cls.g=run_geometry(cls.layout,cls.cfg)
        cls.bodies,cls.tiles,cls.feet=proposal(template(cls.layout),cls.cfg)

    def test_frozen_input_and_complete_module_inventory(self):
        self.assertEqual(self.before,json.dumps(self.layout,sort_keys=True))
        self.assertEqual(digest(ROOT/self.cfg['baseline']),self.cfg['baseline_sha256'])
        self.assertTrue(self.g['common_xy_template'])
        self.assertEqual(len(self.g['discs']),18)
        self.assertEqual(self.g['baseline_module_count'],2016)
        self.assertEqual(self.g['baseline_chip_count'],8064)
        self.assertEqual([r['modules'] for r in self.g['rows']],[12,16,24,28,32])

    def test_every_local_component_screen_and_mirror(self):
        for v in self.g['comparisons'].values():self.assertEqual(v['overlaps'],0)
        self.assertGreaterEqual(self.g['comparisons']['pickup_body']['minimum_gap_mm'],.2-1e-12)
        aa,bb=copy.deepcopy(self.feet),copy.deepcopy(self.bodies)
        for b in aa+bb:b['center_mm'][2]*=-1
        mirror=comparisons(aa,bb,1e-7)
        self.assertEqual(mirror['overlaps'],0)
        self.assertAlmostEqual(mirror['minimum_gap_mm'],self.g['comparisons']['foot_body']['minimum_gap_mm'])
        self.assertGreater(self.g['first_disc_barrel_turn_clearance_mm'],2.)
        self.assertGreater(self.g['tab_to_other_subsystem_radial_lower_bound_mm'],0.)

    def test_two_inner_levels_are_detectably_insufficient(self):
        cfg=copy.deepcopy(self.cfg);cfg['placement']['inner_phi_levels']=2
        b,_,_=proposal(template(self.layout),cfg)
        self.assertGreater(comparisons(b,b,1e-7,same=True)['overlaps'],0)

    def test_fat_retained_posts_detect_real_conflicts(self):
        self.assertEqual(self.g['retained_backplate_post_probes']['4.0']['overlaps'],0)
        self.assertGreater(self.g['retained_backplate_post_probes']['6.0']['overlaps'],0)

    def test_corrupted_source_pin_fails_closed(self):
        cfg=copy.deepcopy(self.cfg);cfg['baseline_sha256']='0'*64
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'inputs.json';p.write_text(json.dumps(cfg))
            with self.assertRaisesRegex(ValueError,'Baseline SHA'):load_inputs(p)

    def test_service_failures_remain_visible(self):
        s=services(self.cfg,self.layout,self.g['rows'])
        self.assertEqual(s['power_chains_per_disc'],16)
        self.assertEqual(s['local_circuits_per_disc'],10)
        owned=[mid for g in s['template_groups'] for mid in g['module_ids']]
        self.assertEqual(len(owned),112)
        self.assertEqual(len(set(owned)),112)
        self.assertEqual(sum(len(g['power_chains']) for g in s['template_groups']),16)
        for side in ['positive','negative']:
            for name in ['reference','conservative','stress']:
                a=[a for a in s['accumulation'] if a['side']==side and a['scenario']==name]
                self.assertEqual([x['endcap_discs_joined'] for x in a],list(range(9)))
                self.assertTrue(all(x['demand_mm2']<y['demand_mm2'] for x,y in zip(a,a[1:])))
                self.assertEqual(a[-1]['status'],'PASS' if name=='reference' else 'FAIL')

    def test_material_inventory_and_load_path(self):
        m=inventory(self.cfg,self.base,self.g['rows'],self.bodies)
        local=[a for a in m['components'] if a['scope']=='disc']
        self.assertTrue(all(a['volume_mm3']>0 for a in m['components']))
        self.assertAlmostEqual(sum(a['mass_g'] for a in local),m['disc_passive_mass_g'])
        self.assertAlmostEqual(18*m['disc_passive_mass_g']+2*m['shared_support_per_end_g'],1000*m['all_18_discs_passive_plus_two_carriers_kg'])
        tube=next(a for a in local if a['material']=='titanium' and a['component'].startswith('local evaporators'))
        ro=1.4;ri=1.25
        self.assertAlmostEqual(tube['volume_mm3'],math.pi*(ro*ro-ri*ri)*m['local_tube_length_mm'])
        e=m['elastic_screens']
        self.assertGreater(e[0]['closed_shell_sag_mm'],e[-1]['closed_shell_sag_mm'])
        self.assertGreater(e[1]['unsupported_one_rail_sag_mm'],100*e[1]['closed_shell_sag_mm'])


class ThermalControls(unittest.TestCase):
    def test_heat_conservation_inverse_k_and_mirror(self):
        common=(40.,44.,16.,8.)
        a=sheet_resistance(*common,-16.,1500.,.3,1.)
        b=sheet_resistance(*common,-16.,750.,.3,1.)
        c=sheet_resistance(*common,16.,1500.,.3,1.)
        self.assertAlmostEqual(a['sink_power_W'],1.,places=8)
        self.assertAlmostEqual(b['max_K_W'],2*a['max_K_W'],places=8)
        self.assertAlmostEqual(c['max_K_W'],a['max_K_W'],places=8)

    def test_analytic_one_dimensional_solution(self):
        # Analytic discrete 1D limit: full-height central isothermal contact.
        a=sheet_resistance(10.,10.,1.,10.,0.,1000.,1.,1.)
        # Two symmetric halves, with two pinned central columns on the even grid.
        # Heat/column=.1 W, net conductance across height =10 W/K. Four heated
        # columns on either side give .1/10*(1+2+3+4)=.1 K/W.
        self.assertAlmostEqual(a['max_K_W'],.1,places=8)

    def test_stress_failure_and_coolant_energy_balance(self):
        cfg,layout,base=load_inputs();g=run_geometry(layout,cfg)
        b,_,_=proposal(template(layout),cfg);t=thermal_screen(cfg,base,g['rows'],b)
        self.assertFalse(any(v['stress_target_pass'] for v in t['variants']))
        self.assertTrue(all(c['stress_exit_quality']<.45 for c in t['circuits']))
        self.assertAlmostEqual(2*sum(c['nominal_W'] for c in t['circuits']),112*4*2.688)
        self.assertTrue(all(abs(v['sheet']['sink_power_W']-1)<1e-8 for v in t['variants']))
        self.assertTrue(all(g['relative_change']<.05 for g in t['grid_convergence']))

if __name__=='__main__':unittest.main()
