"""Bounded DES038 analytical fault controls; no detector-runtime dependencies."""
import copy
import hashlib
import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path

from design import (CONFIG, ROOT, build, carrier_volume_id, common_readout,
                    determinant, hit_core, inside_polygon, make_pattern,
                    polygon, polygon_area, quarter_polygon, ray_counts,
                    regular_area, rotate_xy, separated, validate, verify_common_sources)


class EndcapDesign(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=build();cls.c=cls.data['config']

    def changed(self):
        out=copy.copy(self.data);out['config']=copy.deepcopy(self.c);return out

    def test_depth_and_whole_end_counts(self):
        d=self.data;s=d['summary'];self.assertEqual(s['sampling_depth_mm'],1548)
        self.assertEqual(s['total_depth_mm'],1558)
        self.assertEqual(s['carriers'],472*36*2)
        self.assertEqual(s['boards'],67968);self.assertEqual(s['tiles'],2446848)
        self.assertEqual(s['powered_channels'],5301504)
        self.assertEqual(s['first_active_plane_abs_z_mm'],4915.2)
        self.assertEqual(d['placements'][0]['origin_mm'][2],4913.2)
        self.assertNotIn('center_mm',d['placements'][0])
        self.assertIn('center_mm',d['common']['parts'][0])
        self.assertEqual(s['last_active_plane_abs_z_mm'],6420.2)

    def test_old_outline_depth_rejected(self):
        c=copy.deepcopy(self.c);c['envelope']['back_abs_z_mm']=6379.1
        with self.assertRaisesRegex(ValueError,'depth budget'):build(c)

    def test_adaptive_inner_repair_separate_from_phases(self):
        d=self.data['summary']['pattern_diagnostics'];self.assertEqual(d['uniform']['carriers_per_layer_per_end'],468)
        self.assertEqual(d['adaptive']['carriers_per_layer_per_end'],472)
        self.assertEqual(d['narrow_wedge']['carriers_per_layer_per_end'],304)
        self.assertLess(d['adaptive']['first_core_radius_mm'],d['uniform']['first_core_radius_mm'])
        self.assertEqual(d['adaptive'],d['staggered'])
        self.assertAlmostEqual(d['adaptive']['full_face_core_fraction'],.5503079449325103)
        self.assertLess(d['adaptive']['full_face_core_fraction'],self.data['summary']['common_face_core_fraction'])
        self.assertLess(d['adaptive']['full_face_core_fraction'],d['adaptive']['packable_face_core_fraction'])

    def test_exact_outer_corners_and_inner_sat(self):
        d=self.data;e=self.c['envelope'];inner=polygon(310)
        for q in d['patterns']['staggered']['carriers']:
            self.assertTrue(separated(inner,q['corners_xy_mm']))
            for phase in self.c['packing']['phases_deg']:
                self.assertTrue(all(inside_polygon(rotate_xy(v,phase),4128) for v in q['corners_xy_mm']))

    def test_inner_overlap_fault_rejected(self):
        d=self.changed();d['patterns']=copy.deepcopy(self.data['patterns']);d['patterns']['adaptive']['carriers'][0]['center_xy_mm']=[200,120]
        with self.assertRaisesRegex(ValueError,'containment'):validate(d)

    def test_clipped_outer_corner_fault_rejected(self):
        d=self.changed();d['patterns']=copy.deepcopy(self.data['patterns']);d['patterns']['adaptive']['carriers'][0]['center_xy_mm']=[4000,1000]
        with self.assertRaisesRegex(ValueError,'containment'):validate(d)

    def test_overlapping_grid_fault_rejected(self):
        c=copy.deepcopy(self.c);c['packing']['row_pitch_mm']=240
        with self.assertRaisesRegex(ValueError,'grid or quarter'):build(c)

    def test_polygon_areas_and_shared_ownership(self):
        s=self.data['summary'];g=s['shared_geometry'];area=4*(polygon_area(g['steel_quarter_outer'])-polygon_area(g['steel_quarter_inner_hole']))
        self.assertAlmostEqual(area,s['areas_mm2']['steel_per_layer'])
        self.assertLess(area,regular_area(4128)-regular_area(310))
        self.assertTrue(math.isclose(s['steel_mass_g'],area*30*36*2*7.85/1000,rel_tol=1e-14))
        self.assertAlmostEqual(s['mass_g'],s['common_hardware_mass_g']+s['steel_mass_g']+s['shared_frame_mass_g']+s['back_cover_mass_g'])
        self.assertEqual(g['frame_ownership'],'once per end, continuous annuli')
        self.assertFalse(g['empty_collector_strips_remove_steel'])

    def test_duplicate_reference_absorber_rejected(self):
        d=self.changed();d['common']=copy.deepcopy(self.data['common']);d['common']['parts'].append(dict(role='absorber_reference',owner='sector'))
        with self.assertRaisesRegex(ValueError,'duplicated absorber'):validate(d)

    def test_powered_count_and_heat_doubling_rejected(self):
        d=self.changed();d['summary']=copy.deepcopy(self.data['summary']);d['summary']['powered_channels']*=2
        with self.assertRaisesRegex(ValueError,'conservation'):validate(d)
        d=self.changed();d['summary']=copy.deepcopy(self.data['summary']);d['summary']['power_scenarios'][0]['total_heat_W']*=2
        with self.assertRaisesRegex(ValueError,'conservation'):validate(d)

    def test_power_and_stress_scaling_separate_data_trigger(self):
        s=self.data['summary'];u=self.data['common'];n=s['carriers']
        for a,b in zip(s['power_scenarios'],u['budgets']['power_scenarios']):
            self.assertEqual(a['current_A_per_device'],b['current_A_per_device'])
            self.assertAlmostEqual(a['total_heat_W'],b['total_heat_W']*n)
        self.assertEqual(s['trigger']['lanes'],8*n)
        self.assertEqual(s['daq'][1]['status'],'OVERLOAD')
        self.assertEqual(s['daq'][1]['utilization'],1.25)
        self.assertEqual(s['local_water_ports'],4*n)

    def test_proper_negative_end_frames_and_water_ports(self):
        pos={(q['layer'],q['prototype']):q for q in self.data['placements'] if q['side']==1}
        for q in self.data['placements']:
            self.assertAlmostEqual(determinant(q['frame']),1)
            if q['side']==2:
                p=pos[q['layer'],q['prototype']]
                self.assertEqual(q['origin_mm'],[p['origin_mm'][0],-p['origin_mm'][1],-p['origin_mm'][2]])
                for a,b in zip(q['water_ports'],p['water_ports']):
                    self.assertEqual(a['center_mm'],[b['center_mm'][0],-b['center_mm'][1],-b['center_mm'][2]])
                    self.assertEqual(a['direction'],[b['direction'][0],-b['direction'][1],-b['direction'][2]])

    def test_improper_reflection_rejected(self):
        c=copy.deepcopy(self.c);c['negative_end_frame']=[[1,0,0],[0,1,0],[0,0,-1]]
        with self.assertRaisesRegex(ValueError,'proper Rx'):build(c)
        d=self.changed();d['placements']=self.data['placements'][:];d['placements'][0]=copy.deepcopy(d['placements'][0]);d['placements'][0]['frame'][2][2]=-1
        with self.assertRaisesRegex(ValueError,'improper carrier'):validate(d)

    def test_id_uniqueness_and_capacity(self):
        ids=[q['volume_id'] for q in self.data['placements']];self.assertEqual(len(ids),len(set(ids)))
        for q in self.data['placements']:
            self.assertLess(q['carrier'],4096);self.assertEqual(q['volume_id']&255,9)
        with self.assertRaisesRegex(ValueError,'capacity'):carrier_volume_id(1,0,0,4096)
        d=self.changed();d['placements']=self.data['placements'][:];d['placements'][1]=copy.deepcopy(d['placements'][0])
        with self.assertRaisesRegex(ValueError,'duplicate carrier'):validate(d)

    def test_port_transform_corruption_rejected(self):
        d=self.changed();d['placements']=self.data['placements'][:];d['placements'][0]=copy.deepcopy(d['placements'][0]);d['placements'][0]['water_ports'][0]['center_mm'][0]+=1
        with self.assertRaisesRegex(ValueError,'water port'):validate(d)

    def test_core_rectangle_lookup_independently(self):
        d=self.data;q=d['patterns']['staggered']['carriers'][0];cx,cy=q['center_xy_mm'];tile=d['common']['channel_map'][0]['tile_center_mm']
        for phase in (0,22.5,45,67.5):
            point=rotate_xy([cx+tile[0],cy+tile[1]],phase)
            self.assertTrue(hit_core(d,*point,phase,'staggered'))
            # The inter-board seam remains empty; a carrier is not a sheet.
            seam=rotate_xy([cx,cy-12],phase)
            self.assertFalse(hit_core(d,*seam,phase,'staggered'))
            edge=rotate_xy([cx+tile[0]+14.86,cy+tile[1]],phase)
            self.assertFalse(hit_core(d,*edge,phase,'staggered'))

    def test_core_plane_forward_gap_and_negative_rotation(self):
        for eta in (3.8,4.,5.):
            self.assertTrue(all(ray_counts(self.data,eta,2*math.pi*i/72)['count']==0 for i in range(72)))
        for eta in (1.2,2.,3.,3.5):
            for phi in (0,.1,math.pi/8,math.pi/2,2.7):
                self.assertEqual(ray_counts(self.data,eta,phi)['layers'],ray_counts(self.data,-eta,-phi)['layers'])
        self.assertEqual(ray_counts(self.data,2.,0,'adaptive')['count'],0)
        self.assertGreater(ray_counts(self.data,2.,0,'staggered')['count'],0)

    def test_common_source_baseline_mismatch_rejected(self):
        report=copy.copy(self.data['common']);report['source_sha256']=dict(report['source_sha256'])
        report['source_sha256']['tools/hcal_readout/config.json']='0'*64
        with self.assertRaisesRegex(ValueError,'retained DES036 source'):verify_common_sources(report)
        self.assertTrue(verify_common_sources(self.data['common']))

    def test_source_binding_and_deterministic_rebuild(self):
        d=self.data
        for path,digest in d['source_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest)
        # Cheap deterministic geometry/ledger rebuild, independent of coverage.
        other=build()
        self.assertEqual(json.dumps(d,sort_keys=True),json.dumps(other,sort_keys=True))
        self.assertFalse(d['common']['fixture']['absorber_present'])
        self.assertNotIn('Steel235',d['common']['material_totals'])
        self.assertEqual(d['summary']['steel_path_screening']['status'],'NOT_RUN')


if __name__=='__main__':unittest.main()
