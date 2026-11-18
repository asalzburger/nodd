"""Fail closed if a historical LAr model or unmatched physical view is supplied."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path

from draw_restored_sector_comparison import validate


class ComparisonProvenanceTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        (self.folder/'image.png').write_bytes(b'test image bytes')
        image = dict(file='image.png',sha256=hashlib.sha256(b'test image bytes').hexdigest(),bounds_mm=[300,460,1834,1946])
        common = dict(status='PASS',z_mm=0,checked_geometry_revision='a'*40,
                      images=dict(overview=copy.deepcopy(image),zoom=copy.deepcopy(image)))
        self.data = {key:copy.deepcopy(common) for key in ('siw','lar')}
        self.data['siw']['rays'] = dict(boundary=dict(sensitive_segments=0))
        self.data['lar']['rays'] = dict(boundary=dict(sensitive_segments=1))
        self.data['lar']['drawing_geometry'] = dict(lead_mm=1.8,planes=1248,
            sampling_inner_radius_mm=1772.8,sampling_outer_radius_mm=2350,
            warm_outer_radius_mm=2641.7,inclination_deg=50.18)

    def test_matched_inputs(self):
        validate(self.data,self.folder)

    def test_old_variant_rejected(self):
        self.data['lar']['drawing_geometry']['planes'] = 1536
        with self.assertRaisesRegex(ValueError,'Wrong restored LAr variant'):
            validate(self.data,self.folder)

    def test_different_zoom_coordinates_rejected(self):
        self.data['lar']['images']['zoom']['bounds_mm'][0] += 20
        with self.assertRaisesRegex(ValueError,'identical physical XY bounds'):
            validate(self.data,self.folder)

    def test_modified_image_rejected(self):
        (self.folder/'image.png').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'Changed native image'):
            validate(self.data,self.folder)


if __name__=='__main__':
    unittest.main()
