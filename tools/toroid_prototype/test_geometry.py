"""Geometry controls for the isolated twelvefold-toroid prototype."""
import copy
import json
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np

try:
    from . import geometry as g
except ImportError:
    import geometry as g


class GeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=g.load_design()

    def test_exact_loop_distance_and_closed_polygon(self):
        group=self.c['coil_groups']['barrel']; a=group['center_r_m']-group['half_r_m']
        d=g.rounded_rectangle_distance([[a,0],[a+.1,0],[group['center_r_m'],0]],group)
        np.testing.assert_allclose(d,[0,.1,group['half_r_m']],atol=1e-12)
        p=g.loop_polyline(group)
        np.testing.assert_array_equal(p[0],p[-1])
        np.testing.assert_allclose(g.rounded_rectangle_distance(p[:,[0,2]],group),0,atol=2e-15)

    def test_masks_nested_finite_boundaries(self):
        p=np.array([[4.6+x,0,0] for x in [0,.099,.1,.101,.149,.151,.249,.251]])
        pack=g.coil_mask(p,self.c,'pack'); cold=g.coil_mask(p,self.c,'cold'); warm=g.coil_mask(p,self.c,'warm')
        self.assertEqual(pack.tolist(),[True,True,True,False,False,False,False,False])
        self.assertTrue(np.all(pack<=cold)); self.assertTrue(np.all(cold<=warm))
        self.assertFalse(warm[-1]); self.assertTrue(warm[-2])
        np.testing.assert_array_equal(g.coil_mask([[4.6,.300,0],[4.6,.301,0]],self.c),[True,False])

    def test_c12_and_z_reflection(self):
        rng=np.random.default_rng(43); p=rng.uniform([-8.6,-8.6,-11.4],[8.6,8.6,11.4],(10000,3))
        ph=math.pi/6; rot=np.array([[math.cos(ph),-math.sin(ph),0],[math.sin(ph),math.cos(ph),0],[0,0,1]])
        a=g.coil_mask(p,self.c); np.testing.assert_array_equal(a,g.coil_mask(p@rot.T,self.c))
        p[:,2]*=-1; np.testing.assert_array_equal(a,g.coil_mask(p,self.c))

    def test_no_hcal_warm_collision(self):
        c=self.c; b=c['coil_groups']['barrel']; e=c['coil_groups']['endcap_plus']; hw=c['warm']['normal_m']/2
        # Analytic sufficient inequalities, including actual HCAL corners.
        self.assertGreater(b['center_r_m']-b['half_r_m']-hw,c['hcal']['barrel_corner_radius_m']+.10)
        self.assertGreater(b['center_r_m']-b['half_r_m']-hw,c['hcal']['endcap_outer_corner_radius_m']+.10)
        self.assertGreater(e['center_z_m']-e['half_z_m']-hw,c['hcal']['endcap_back_abs_z_m']+.10)
        # Dense extreme HCAL outer surfaces independently exercise full mask.
        ph=np.linspace(0,2*math.pi,721); z=np.linspace(-c['hcal']['barrel_half_z_m'],c['hcal']['barrel_half_z_m'],31)
        r=c['hcal']['barrel_corner_radius_m']
        p=np.stack(np.broadcast_arrays(r*np.cos(ph[:,None]),r*np.sin(ph[:,None]),z[None,:]),axis=-1)
        self.assertFalse(g.coil_mask(p.reshape(-1,3),c).any())

    def test_three_m_spans_nested_and_mixed_hits(self):
        st=self.c['stations']; self.assertAlmostEqual(st['barrel_radii_m'][-1]-st['barrel_radii_m'][0],3.)
        self.assertAlmostEqual(st['disk_abs_z_m'][-1]-st['disk_abs_z_m'][0],3.)
        for eta,phi,kind in [(0,15,'BBB'),(1.10,7.5,'BBD'),(1.14,7.5,'BDD'),(2.,0,'DDD')]:
            r=g.station_intersections(eta,phi,self.c)
            self.assertEqual(r['hit_types'],kind); self.assertTrue(r['valid'],r)
        self.assertFalse(g.station_intersections(0,0,self.c)['valid'])
        self.assertFalse(g.station_intersections(3.1,0,self.c)['three_hits'])

    def test_path_crosses_coil_between_clear_stations(self):
        fixture=copy.deepcopy(self.c)
        fixture['stations'].update(outline_thickness_m=.05,barrel_end_shortening_m=.05)
        r=g.station_intersections(1.,12.,fixture)
        self.assertTrue(r['three_hits']); self.assertFalse(r['excluded_hits'])
        self.assertTrue(r['path_intervals']); self.assertFalse(r['valid'])
        # Ray through the central barrel inner leg; interval contains known x4.6.
        intervals=g.path_intersections([4,0,0],[5,0,0],self.c,width='pack',step_m=.002)
        self.assertEqual(len(intervals),1); self.assertLessEqual(intervals[0][0],.5); self.assertGreaterEqual(intervals[0][1],.7)

    def test_shared_ect_case_is_union_and_current_packs_separate(self):
        ph=np.linspace(0,math.pi/3,301); r=np.linspace(.5,1.2,151)
        p=np.stack(np.broadcast_arrays(r[None,:]*np.cos(ph[:,None]),r[None,:]*np.sin(ph[:,None]),np.full((len(ph),len(r)),8.7)),axis=-1).reshape(-1,3)
        e=self.c['coil_groups']['endcap_plus']
        pack=g.group_mask(p,e,12,**{'normal_m':.2,'tangent_m':.3},return_count=True)
        cold=g.group_mask(p,e,12,normal_m=.3,tangent_m=.4,return_count=True)
        self.assertEqual(pack.max(),1); self.assertEqual(cold.max(),2)
        # Deliberately broader TEST sleeve exercises the shared-allocation path;
        # the energy-sized candidate may legitimately have zero cold overlap.
        fixture=copy.deepcopy(self.c);fixture['cold']={'normal_m':.3,'tangent_m':.4}
        v=g.sweep_union_volumes(fixture,samples=131072)
        self.assertFalse(v['cross_group_overlap_detected'])
        for name in ['endcap_plus','endcap_minus']:
            x=v['groups'][name]
            self.assertGreater(x['overlap_correction_m3'],0)
            self.assertLess(x['overlap_correction_m3'],.01*x['summed_sleeve_volume_m3'])

    def test_outlines_are_only_clear_external_boundaries(self):
        outlines=g.chamber_outline_polylines(self.c,phi_step_deg=3,longitudinal_step_m=.25,radial_step_m=.25)
        self.assertEqual(len(outlines),9)
        for o in outlines:
            seg=o['segments_m']; self.assertGreater(len(seg),0)
            # Endpoints and intermediates clear BOTH coil families at nominal gap.
            points=np.concatenate([((1-t)*seg[:,0]+t*seg[:,1]) for t in np.linspace(0,1,7)])
            self.assertFalse(g.coil_mask(points,self.c,clearance=.05).any(),o['name'])
            # Independently inspect both outer envelope faces through exact coil
            # masks, so a centre-surface-only clipping mistake cannot pass.
            for offset in [-self.c['stations']['outline_thickness_m']/2,
                           self.c['stations']['outline_thickness_m']/2]:
                q=points.copy()
                if o['kind']=='disk': q[:,2]+=offset
                else:
                    radius=np.linalg.norm(q[:,:2],axis=1)
                    q[:,:2]*=(1+offset/radius[:,None])
                self.assertFalse(g.coil_mask(q,self.c,clearance=.05).any(),o['name'])
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'outlines.json'; r=g.export_outlines(p,self.c,phi_step_deg=6,longitudinal_step_m=.4,radial_step_m=.4)
            self.assertEqual(len(json.loads(p.read_text())['outlines']),9)
            self.assertIn('outlines',r)
            from xml.etree.ElementTree import parse
            v=Path(td)/'outlines.vtp'; result=g.export_vtp(v,self.c,outlines)
            piece=parse(v).find('./PolyData/Piece')
            self.assertEqual(int(piece.attrib['NumberOfLines']),result['lines'])
            self.assertEqual(len(result['objects']),45)

    def test_analytic_union_refinement_and_independent_multiplicity_mc(self):
        fixture=copy.deepcopy(self.c);fixture['cold']={'normal_m':.3,'tangent_m':.4}
        # Frozen numerical TEST geometry for independent overlap control.
        fixture['coil_groups']['barrel']['half_z_m']=10.8
        for name,side in [('endcap_plus',1),('endcap_minus',-1)]:
            fixture['coil_groups'][name]['half_z_m']=1.9
            fixture['coil_groups'][name]['center_z_m']=side*8.7
        low=g.analytic_sweep_union_volumes(fixture,order=32)
        high=g.analytic_sweep_union_volumes(fixture,order=128)
        self.assertAlmostEqual(high['sum_group_union_volume_m3'],128.8778104360228,places=8)
        self.assertLess(abs(high['sum_group_union_volume_m3']-low['sum_group_union_volume_m3']),3e-9)
        mc=g.sweep_union_volumes(fixture,samples=524288)
        error=math.sqrt(sum(x['one_sigma_statistical_error_m3']**2 for x in mc['groups'].values()))
        self.assertLess(abs(mc['sum_group_union_volume_m3']-high['sum_group_union_volume_m3']),5*error)
        for proof in high['cross_group_separation_proofs']:
            self.assertGreater(proof['separation_lower_bound_m'],0)
        with self.assertRaises(ValueError):
            g.analytic_sweep_union_volumes(self.c,width_override={'normal_m':.8,'tangent_m':1.2})

    def test_axial_disk_depth_does_not_inflate_radial_clearance(self):
        fixture=copy.deepcopy(self.c);fixture['stations']['outline_thickness_m']=.50
        # Interior of a barrel straight leg: disk depth moves along z, so its
        # available radial clearance stays fixed through all 500mm of depth.
        point=[[5.10,0,0]]
        self.assertTrue(g.coil_mask(point,fixture,'warm',clearance=.05+.25)[0])
        self.assertFalse(g.chamber_depth_mask(point,fixture,'disk',clearance=.05)[0])
        self.assertTrue(g.chamber_depth_mask(point,fixture,'barrel',clearance=.05)[0])

    def test_depth_guard_detects_crossing_between_samples(self):
        fixture=copy.deepcopy(self.c);fixture['stations']['outline_thickness_m']=.50
        point=np.array([[4.6,0,0.]])
        # Full depth is checked, even when the chamber centre is clear.
        point[0,0]=5.10
        self.assertFalse(g.coil_mask(point,fixture,'warm',clearance=.05)[0])
        self.assertTrue(g.chamber_depth_mask(point,fixture,'barrel',clearance=.05)[0])
        for step in [.025,.0125]:
            self.assertFalse(g.chamber_depth_mask([[5.20,0,0]],fixture,'barrel',clearance=.05,depth_step_m=step)[0])


if __name__=='__main__':
    unittest.main()
