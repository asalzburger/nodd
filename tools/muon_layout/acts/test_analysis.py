import unittest
import numpy as np
from tools.muon_layout.acts.analyze import HIT_DTYPE,count_events,_availability
from tools.muon_layout.acts.prepare import configuration,entrance,directions


def fixture(events,stations=None):
    """Counter-only fixture: planes normal to x and one side normal to y."""
    stations=stations or {0:1,1:2,2:3};catalog={}
    for p,station in stations.items():
        for face,plane,normal in [(0,4,[-1,0,0]),(1,5,[1,0,0]),(2,0,[0,1,0])]:
            catalog[p,face]=dict(plane=plane,normal=np.array(normal),large=face<2,station=station)
    result=[]
    for i,(panel,face,path,direction) in enumerate(events):
        result.append((0,i,panel,face,face<2,2**60+panel*10+face,path,0.,0.,path,*direction))
    return np.array(result,dtype=HIT_DTYPE),catalog


class CounterControls(unittest.TestCase):
    def test_same_station_cannot_manufacture_three_measurements(self):
        events=[(p,f,1+2*p+f,[1,0,0]) for p in range(3) for f in [0,1]]
        h,c=fixture(events,{0:1,1:1,2:1});r=count_events(h,c,np.ones(len(h),bool))
        self.assertEqual(r['outer_unique_faces'],6);self.assertEqual(r['outer_paired_stations'],1)

    def test_distinct_contiguous_visits_cannot_be_spliced(self):
        h,c=fixture([(0,0,1,[1,0,0]),(0,2,2,[0,1,0]),(0,2,3,[0,-1,0]),(0,1,4,[1,0,0])])
        r=count_events(h,c,np.ones(4,bool));self.assertEqual(r['outer_unique_faces'],2)
        self.assertEqual(r['outer_paired_stations'],0);self.assertEqual(r['reentries'],1);self.assertEqual(r['side_events'],2)

    def test_duplicate_root_does_not_become_reentry_or_extra_segment(self):
        h,c=fixture([(0,0,1,[1,0,0]),(0,0,1,[1,0,0]),(0,1,2,[1,0,0])])
        r=count_events(h,c,np.ones(3,bool));self.assertEqual(r['numerical_duplicates'],1)
        self.assertEqual(r['outer_unique_faces'],2);self.assertEqual(r['outer_paired_stations'],1)
        self.assertEqual(r['orphan_transitions'],0)

    def test_inactive_large_face_is_separate_from_outer_pair(self):
        h,c=fixture([(0,0,1,[1,0,0]),(0,1,2,[1,0,0])]);r=count_events(h,c,[True,False])
        self.assertEqual(r['outer_paired_stations'],1);self.assertEqual(r['active_paired_stations'],0)
        self.assertEqual(r['active_unique_faces'],1)

    def test_failure_bounds_keep_proven_pass_and_every_generated_track(self):
        r=_availability(np.array([True,False,False]),np.array([True,True,False]),np.ones(3))
        self.assertAlmostEqual(r['proven_lower_fraction'],1/3);self.assertAlmostEqual(r['possible_upper_fraction'],2/3)
        self.assertEqual(r['unqualified_below_threshold'],1)

    def test_weighted_display_does_not_claim_iid_binomial_error(self):
        r=_availability(np.array([True,False]),np.array([False,False]),np.array([1.,3.]))
        self.assertIsNone(r['binomial_standard_error_lower'])
        self.assertEqual(r['proven_lower_fraction'],.25)

    def test_unpaired_exit_is_a_navigation_anomaly(self):
        h,c=fixture([(0,1,1,[1,0,0])]);r=count_events(h,c,[True])
        self.assertEqual(r['orphan_transitions'],1);self.assertEqual(r['outer_paired_stations'],0)

    def test_full_64bit_native_ids_are_not_float_rounded(self):
        h,_=fixture([(0,0,1,[1,0,0]),(0,1,2,[1,0,0])])
        self.assertEqual(int(h['geometry_id'][1]),2**60+1)
        self.assertNotEqual(float(h['geometry_id'][1]),int(h['geometry_id'][1]))


class EntranceControls(unittest.TestCase):
    def test_closed_cylinder_barrel_caps_and_outward_offset(self):
        c=configuration()['entrance'];d=np.array([[1,0,0],[0,0,1],[0,0,-1]],float)
        surface,start,kind=entrance(d,c)
        self.assertTrue(np.array_equal(kind,[0,1,2]))
        self.assertTrue(np.allclose(surface,[[4.35,0,0],[0,0,6.5],[0,0,-6.5]]))
        self.assertTrue(np.allclose(np.linalg.norm(start-surface,axis=1),1e-5))

    def test_map_and_full_sphere_denominators_are_distinct(self):
        c=configuration();d=directions(c);grid=d['sample']==0;sphere=~grid
        self.assertAlmostEqual(d['solid_angle_weight_sr'][grid].sum(),4*np.pi*np.tanh(3))
        self.assertAlmostEqual(d['solid_angle_weight_sr'][sphere].sum(),4*np.pi)
        self.assertTrue(np.allclose(np.linalg.norm(d['direction'],axis=1),1))
        self.assertEqual(sphere.sum(),4096)


if __name__=='__main__':unittest.main()
