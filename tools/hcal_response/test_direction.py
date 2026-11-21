"""Finite-solid selection math, physical gaps and source-binding controls."""
import copy
import csv
import hashlib
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from direction import (active_paths, box_interval, compile_geometry, core_intersection,
                       recess_interval, select, slab, steel_path)
from native import part_contains, part_boundary

I=[[1,0,0],[0,1,0],[0,0,1]]


def core(center=(0.,0.,2.),size=(29.7,29.7,3.),cuts=True):
    return dict(name='fixture_core',role='sensitive',module=0,sensor=0,shape_kind='box',frame=I,
                center_mm=list(center),dimensions_mm=dict(zip(('sx','sy','sz'),size)),
                cuts=[dict(kind='tube',frame=I,center_mm=[0.,0.,.95],dimensions_mm=dict(rmin=0.,rmax=3.5,length=1.1))] if cuts else [])


class FiniteDirectionMath(unittest.TestCase):
    def test_box_interior_and_grazing_surface(self):
        self.assertEqual(slab((1.,3.),0.,-1.,1.),(1.,3.))
        self.assertIsNone(slab((1.,3.),0.,0.,1.))
        self.assertIsNone(slab((1.,3.),1.,4.,5.))
        self.assertEqual(box_interval(1.,0.,[10.,0.,10.],dict(sx=2.,sy=2.,sz=4.)),(9.,11.))

    def test_recess_axis_and_oblique_exit(self):
        part=core(center=(0.,0.,10.))
        span,clearance=core_intersection(0.,0.,part['center_mm'],part)
        self.assertAlmostEqual(span,1.9)
        self.assertAlmostEqual(clearance,14.85)
        # The ray exits the cylindrical side after1radialmm, before its end.
        part=core(center=(10.,0.,10.),size=(6.,6.,6.),cuts=False)
        part['cuts']=[dict(kind='tube',frame=I,center_mm=[0.,0.,1.],dimensions_mm=dict(rmin=0.,rmax=1.,length=2.))]
        self.assertEqual(recess_interval(1.,0.,[10.,0.,11.],1.,2.,(7.,13.)),(10.,11.))
        span,clearance=core_intersection(1.,0.,part['center_mm'],part)
        self.assertAlmostEqual(span,5.)
        self.assertEqual(clearance,0.)

    def test_finite_crossing_with_no_reference_plane_intersection(self):
        part=core(center=(0.,0.,10.),size=(2.,2.,4.),cuts=False)
        span,clearance=core_intersection(.12,0.,part['center_mm'],part)
        self.assertAlmostEqual(span,1/.12-8.)
        self.assertEqual(clearance,0.)

    def test_source_domain_recess_and_reflector_gap(self):
        part=core()
        self.assertTrue(part_contains([0.,0.,2.],part,0.))
        self.assertFalse(part_contains([0.,0.,3.],part,0.))
        self.assertTrue(part_contains([3.5001,0.,3.],part,0.))
        self.assertFalse(part_contains([14.8501,0.,2.],part,0.))
        self.assertFalse(part_contains([0.,14.8501,2.],part,0.))
        self.assertTrue(part_boundary([-3.5,0.,3.5],part,0.))
        self.assertFalse(part_boundary([-3.4999,0.,3.4999],part,0.))

    def test_steel_depth_is_finite_and_pointing_seam_remains(self):
        c=dict(sectors=16,layers=60,steel_mm=30.,installation_gap_mm=1.,
               barrel=dict(front_apothem_mm=3130.,half_z_mm=6260.,end_flange_mm=20.,sector_half_seam_mm=1.,edge_rail_mm=2.))
        depth,full=steel_path(0.,0.,c)
        self.assertEqual(depth,1800.);self.assertTrue(full)
        depth,full=steel_path(math.tan(math.pi/16),0.,c)
        self.assertEqual(depth,0.);self.assertFalse(full)
        p=math.tan(math.pi/16)-3/3230
        depth,full=steel_path(p,0.,c)
        self.assertGreater(depth,0.);self.assertLess(depth,1800*math.sqrt(1+p*p));self.assertFalse(full)
        self.assertEqual(steel_path(0.,100.,c),(0.,False))

    def test_actual_core_path_counts_a_layer_once(self):
        part=core(cuts=False)
        definition=dict(rows=[0.],parts_by_row={0.:[part]},half_size=[20.,120.,6.],
                        max_core_half_y=14.85,max_core_half_z=1.5,core_z_values=[2.])
        layers={0:dict(rows=[0.],carriers_by_row={0.:[dict(unit=1,carrier=0,origin=[3160.,0.,0.])]},front=3160.,max_half_y=120.,max_half_z=6.)}
        result=active_paths(0.,0.,{1:definition},layers)
        self.assertEqual(result['active_layers'],[0]);self.assertAlmostEqual(result['core_path_mm'],3.)
        self.assertEqual(active_paths(0.,1.,{1:definition},layers)['active_layers'],[])
        self.assertEqual(active_paths(.1,0.,{1:definition},layers)['active_layers'],[])

    def test_ranking_preserves_primary_criteria_and_clearance_ties(self):
        a=dict(eta=0.,phi_rad=0.,minimum_active_layer_count=58,active_layer_count_sum=530,minimum_core_reference_clearance_mm=5.)
        b=dict(a,eta=.02,minimum_active_layer_count=59,active_layer_count_sum=531,minimum_core_reference_clearance_mm=1.)
        c=dict(b,eta=-.02,minimum_core_reference_clearance_mm=1.+.5e-6)
        self.assertIs(select([a,b,c]),b)
        c['minimum_core_reference_clearance_mm']=1.+2e-6
        self.assertIs(select([a,b,c]),c)
        with self.assertRaisesRegex(ValueError,'no candidate'):select([])

    def test_changed_export_is_rejected_before_geometry_selection(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/'placements.csv';p.write_text('original')
            (root/'expected.json').write_text(json.dumps(dict(export_sha256={'placements.csv':hashlib.sha256(p.read_bytes()).hexdigest()})))
            p.write_text('changed')
            with self.assertRaisesRegex(ValueError,'changed exported'):compile_geometry(root)


if __name__=='__main__':unittest.main()
