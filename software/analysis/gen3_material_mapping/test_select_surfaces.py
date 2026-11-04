"""Controls for the user-selected layer side, binning and shared native portals."""
import copy
import json
from pathlib import Path
import unittest
from select_surfaces import select

ROOT=Path(__file__).resolve().parents[3]


class SelectionControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geometry=json.loads((ROOT/'docs/validation/gen3-material-mapping/geometry-summary.json').read_text())
        cls.config=json.loads(Path(__file__).with_name('mapping_config.json').read_text())

    def test_one_layer_role_each_and_extras_deduplicate(self):
        m=select(self.geometry,self.config)
        self.assertEqual(m['counts']['unique_surfaces'],65)
        self.assertEqual(m['counts']['logical_roles'],66)
        roles=[r for p in m['surfaces'] for r in p['roles'] if r['kind']=='sensitive_layer']
        self.assertEqual(len({(r['system'],r['layer']) for r in roles}),52)
        self.assertEqual(len(roles),52)
        self.assertEqual(m['counts']['cylinders'],15)
        self.assertEqual(m['counts']['discs'],50)

    def test_side_is_relative_to_outgoing_flight_on_both_endcaps(self):
        m=select(self.geometry,self.config)
        volumes={v['name']:v for v in self.geometry['volumes']}
        for p in m['surfaces']:
            for role in p['roles']:
                if role['kind']!='sensitive_layer':continue
                sy=role['system'];v=volumes[f"System{sy}Layer{role['layer']}"]
                (r,z),(r2,z2)=p['rz_segment_mm']
                if sy==1:
                    self.assertEqual(role['side'],'after');self.assertAlmostEqual(r,v['r_max_mm'])
                elif sy in (4,6):self.assertAlmostEqual(r,v['r_min_mm'])
                else:self.assertAlmostEqual(z,v['z_min_mm'] if v['z_min_mm']>0 else v['z_max_mm'])

    def test_all_requested_bins_and_shared_exception_retained(self):
        m=select(self.geometry,self.config)
        for p in m['surfaces']:
            self.assertEqual(p['bins']['phi'],1)
            axis='z' if p['type']=='cylinder' else 'r'
            requested=[r['requested_bins'][axis] for r in p['roles']]
            self.assertEqual(p['bins'][axis],max(requested))
        self.assertEqual(len(m['binning_conflicts']),1)
        shared=next(p for p in m['surfaces'] if len(p['roles'])>1)
        self.assertEqual(sorted(r['requested_bins']['z'] for r in shared['roles']),[250,500])
        self.assertEqual(shared['bins']['z'],500)

    def test_counts_are_configurable_and_invalid_values_rejected(self):
        c=copy.deepcopy(self.config);c['phi_bins']=3;c['bins']['pixel_endcap']=7
        m=select(self.geometry,c)
        for p in m['surfaces']:
            self.assertEqual(p['bins']['phi'],3)
            if any(r['binning_family']=='pixel_endcap' for r in p['roles']):self.assertEqual(p['bins']['r'],7)
        c['phi_bins']=True
        with self.assertRaises(ValueError):select(self.geometry,c)
        c['phi_bins']=1;c['bins']['beam_pipe']=0
        with self.assertRaises(ValueError):select(self.geometry,c)

    def test_missing_face_and_duplicate_ids_fail(self):
        g=copy.deepcopy(self.geometry);g['volumes'][next(i for i,v in enumerate(g['volumes']) if v['name']=='System1Layer1')]['portal_surface_ids']=[]
        with self.assertRaises(ValueError):select(g,self.config)
        g=copy.deepcopy(self.geometry);g['portals'].append(g['portals'][0])
        with self.assertRaises(ValueError):select(g,self.config)

    def test_shared_conflict_can_fail_or_be_explicitly_overridden(self):
        c=copy.deepcopy(self.config);c['shared_portal_binning']='error'
        with self.assertRaises(ValueError):select(self.geometry,c)
        c=copy.deepcopy(self.config);c['surface_overrides']={'144678138029277184':{'phi':1,'z':333}}
        p=next(p for p in select(self.geometry,c)['surfaces'] if p['geometry_id']==144678138029277184)
        self.assertEqual(p['bins']['z'],333)
        self.assertTrue(p['explicit_binning_override'])


if __name__=='__main__':unittest.main()
