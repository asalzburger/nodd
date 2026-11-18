import json
from pathlib import Path
import tempfile
import unittest
from compact_public import publish


class PublicEvidenceTests(unittest.TestCase):
    def test_covariance_metadata_follows_selected_variables(self):
        source={'width_covariance':{
            'order':['reference:global:0','reference:energy:0','candidate:abs_eta:0'],
            'matrix':[[1,2,3],[2,5,7],[3,7,11]],
            'undefined_replicates':[2,4,8]},'point_statistic':.125}
        with tempfile.TemporaryDirectory() as temp:
            original=Path(temp)/'private.json';result=Path(temp)/'public.json'
            original.write_text(json.dumps(source));publish(original,result)
            value=json.loads(result.read_text())
        self.assertEqual(value['width_covariance']['order'],['reference:global:0','candidate:abs_eta:0'])
        self.assertEqual(value['width_covariance']['matrix'],[[1,3],[3,11]])
        self.assertEqual(value['width_covariance']['undefined_replicates'],[2,8])
        self.assertEqual(value['point_statistic'],.125)


if __name__=='__main__':unittest.main()
