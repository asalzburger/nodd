"""Numerical controls for compact scientific diagnostics (no simulation)."""
import math
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

import numpy as np

from digitized_response import bootstrap_sample,covariance,histogram,sha,uncertainty,verify_run


class DiagnosticStatistics(unittest.TestCase):
    def test_histogram_boundary_and_zero_denominators(self):
        h=histogram([-1,0,.5,1,2],[0,1,2],'MIP')
        self.assertEqual(h['counts'],[2,1])
        self.assertEqual(h['underflow'],1)
        self.assertEqual(h['overflow'],1)
        self.assertEqual(sum(h['counts'])+h['underflow']+h['overflow'],h['entries'])
        with self.assertRaises(ValueError):
            histogram([math.nan],[0,1],'MIP')

    def test_bootstrap_keeps_paired_events(self):
        x=np.arange(1.,41.)
        sample=np.array([x,2*x,3*x]).T
        means,widths,_=bootstrap_sample(sample,np.random.Generator(np.random.PCG64(117)))
        np.testing.assert_allclose(means[:,1],2*means[:,0],rtol=1e-14)
        np.testing.assert_allclose(widths[:,0],widths[:,1],rtol=1e-14)
        np.testing.assert_allclose(widths[:,0],widths[:,2],rtol=1e-14)

    def test_zero_response_width_is_explicitly_undefined(self):
        means,widths,events=bootstrap_sample(np.zeros((10,3)),np.random.default_rng(117))
        self.assertTrue(np.all(means==0))
        self.assertTrue(np.all(events==0))
        self.assertTrue(np.isnan(widths).all())
        self.assertEqual(uncertainty(widths[:,0]),dict(SE=None,CI95=None,undefined_replicates=5000))
        self.assertEqual(covariance(widths),[[None]*3 for _ in range(3)])

    def test_changed_execution_identity_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ['binary','backend','input.root','native.log','diagnostics.jsonl']:
                (root/name).write_text(name)
            config={'noise_MIP':.13}
            (root/'config.json').write_text(json.dumps(config))
            receipt=dict(exit_code=0,identity=dict(input_sha256=sha(root/'input.root'),
                binary_sha256=sha(root/'binary'),backend_sha256=sha(root/'backend'),configuration=config),
                config_sha256=sha(root/'config.json'),log_sha256=sha(root/'native.log'),output_sha256=sha(root/'diagnostics.jsonl'))
            (root/'execution.json').write_text(json.dumps(receipt))
            row=dict(diagnostics=str(root/'diagnostics.jsonl'),receipt=receipt,
                sample=dict(path=str(root/'input.root'),sha256=sha(root/'input.root')))
            args=SimpleNamespace(binary=root/'binary',backend=root/'backend')
            verify_run(row,args)
            (root/'backend').write_text('different executable')
            with self.assertRaisesRegex(ValueError,'binary/backend'):
                verify_run(row,args)
            (root/'backend').write_text('backend')
            (root/'native.log').write_text('different log')
            with self.assertRaisesRegex(ValueError,'log/output'):
                verify_run(row,args)

    def test_landau_gaussian_mpv_convention(self):
        try:
            import ROOT
        except ImportError:
            self.skipTest('Activated ROOT required for the fit control')
        from muon_response import fit_landau_gaussian
        rng=ROOT.TRandom3(119499)
        # ROOT's Landau location is above its actual mode by 0.22278298*width.
        values=[rng.Landau(1.+.22278298*.07,.07)+rng.Gaus(0,.13) for _ in range(20000)]
        h=histogram(values,np.linspace(0,5,201),'MIP')
        result=fit_landau_gaussian(h,'synthetic_control')
        self.assertLess(abs(result['underlying_Landau_MPV']-1.),.025)
        self.assertEqual(result['fit_status'],0)
        self.assertGreater(result['convolved_peak'],result['underlying_Landau_MPV'])
        in_range=sum(h['counts'][10:100])
        self.assertLess(abs(result['range_expected_entries']-in_range),.01*in_range)


if __name__=='__main__':
    unittest.main()
