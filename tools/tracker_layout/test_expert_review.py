"""Independent limits and geometric failure cases for the R-C09 prototype."""
import copy
import math
import unittest
import numpy as np
from expert_review import covariance, geometry_errors, intersect, rows_from, sample
from study import KAPPA
from covariance_control import transverse_covariance


def synthetic_hits(eta=0.):
    return [(dict(id=f'TEST-{i}',kind='cylinder',subsystem='pixel',sigma_rphi_m=1e-5,
                  sigma_second_m=2e-5,x0_percent=1.,r_m=r,z_min_m=-2.,z_max_m=2.),
             (r,r*math.sinh(eta),r*math.cosh(eta),math.cosh(eta)))
            for i,r in enumerate([.1,.2,.3])]


class ReviewControlTests(unittest.TestCase):
    def test_three_measurement_known_answer(self):
        # Quadratic through equidistant samples: intercept weights (3,-3,1),
        # curvature weights (1,-2,1)/spacing^2, independent analytic answers.
        result=covariance(synthetic_hits(),0.,100.,material_scale=0.)
        self.assertAlmostEqual(result['sigma_d0_um'],math.sqrt(19)*10,places=8)
        self.assertAlmostEqual(result['sigma_qpt_per_GeV'],math.sqrt(6)*1e-5/.1**2/(KAPPA*3),places=12)

    def test_zero_material_matches_existing_independent_control(self):
        hits=synthetic_hits()
        control=transverse_covariance([dict(r_m=h[0],sigma_rphi_m=l['sigma_rphi_m']) for l,h in hits])
        result=covariance(hits,0.,100.,material_scale=0.)
        self.assertAlmostEqual(result['sigma_d0_um'],control['sigma_d0_m']*1e6,places=8)
        self.assertAlmostEqual(result['sigma_qpt_per_GeV'],control['sigma_kappa_per_m']/(KAPPA*3),places=12)

    def test_pipe_before_all_hits_has_analytic_ip_variance(self):
        # Single kick before every hit changes intercept and slope, not curvature.
        hits=synthetic_hits()
        for l,h in hits: l['x0_percent']=0
        hits=[(l,(*h[:3],0.)) for l,h in hits]
        base=covariance(hits,0.,1.,beam_x0=0.)
        pipe=covariance(hits,0.,1.,beam_x0=.002)
        self.assertAlmostEqual(pipe['sigma_d0_um']**2-base['sigma_d0_um']**2,
                               (.025*.0136)**2*.002*1e12,places=6)
        self.assertAlmostEqual(pipe['sigma_qpt_per_GeV'],base['sigma_qpt_per_GeV'],places=12)

    def test_material_increases_uncertainty_and_field_scales_curvature(self):
        hits=synthetic_hits()
        low=covariance(hits,0.,1.,material_scale=.5)
        high=covariance(hits,0.,1.,material_scale=2.)
        for key in ['sigma_d0_um','sigma_z0_um','sigma_qpt_per_GeV']:
            self.assertGreater(high[key],low[key])
        b2=covariance(hits,0.,1.,field=2.)
        b4=covariance(hits,0.,1.,field=4.)
        self.assertAlmostEqual(b2['sigma_qpt_per_GeV'],2*b4['sigma_qpt_per_GeV'])
        self.assertAlmostEqual(b2['sigma_d0_um'],b4['sigma_d0_um'])

    def test_intersections_and_exclusion_fail(self):
        self.assertTrue(intersect((.1,0),(.2,1),(.2,0),(.1,1)))
        self.assertFalse(intersect((.1,0),(.1,1),(.2,0),(.2,1)))
        self.assertTrue(intersect((.1,0),(.1,1),(.1,.5),(.1,2)))
        candidate={'layers':[synthetic_hits()[0][0]]}
        candidate['layers'][0]['r_m']=.029
        self.assertTrue(geometry_errors(candidate))

    def test_eta_spacing_grows_in_z_and_reflects(self):
        layer=dict(synthetic_hits()[0][0],id='A-short_strip-B1',subsystem='short_strip',r_m=.4)
        c=rows_from(dict(id='A',layers=[layer]),mode='eta',shift=0.,margin=0.)
        pos=[l['z0_m'] for l in c['layers'] if l['kind']=='inclined_ring' and l['z0_m']>0]
        self.assertTrue(np.all(np.diff(np.diff(pos))>0.))
        for e in [1.,1.5,2.]:
            from inclined_study import crossings
            hp=crossings(c,e,.1,10,3); hn=crossings(c,-e,-.1,10,3)
            self.assertEqual(len(hp),len(hn))
            for (_,a),(_,b) in zip(hp,hn):
                np.testing.assert_allclose([a[0],a[1],a[3]],[b[0],-b[1],b[3]],rtol=1e-10)


if __name__=='__main__': unittest.main()
