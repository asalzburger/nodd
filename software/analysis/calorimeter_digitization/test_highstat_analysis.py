import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from angular_sample import sha
from highstat_analysis import feature_signature, load_split


class FreezeBoundary(unittest.TestCase):
    def test_missing_semantics_rejected(self):
        with self.assertRaisesRegex(ValueError,'feature semantics'):
            feature_signature({'feature_names':['a']})

    def test_later_batch_semantics_checked_before_any_arrays_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);entries=[]
            for i in range(2):
                base=root/f'batch-{i}';folder=base/'analysis/features';folder.mkdir(parents=True)
                (folder/'features.npz').write_bytes(b'not an array: must remain unopened')
                proof=folder.parent/'readback.json';proof.write_text('{}')
                receipt=dict(status='PASS',feature_sha256=sha(folder/'features.npz'),
                    readback_sha256=sha(proof),sample_sha256='sample',compact_sha256='geometry',
                    feature_names=['x']*10,producer_sha256=f'producer-{i}',
                    feature_recipe_sha256='recipe',geometry_helper_sha256='geometry-helper')
                (folder/'receipt.json').write_text(json.dumps(receipt))
                entries.append(dict(split='validation',input=f'batch-{i}/input',
                    sample_sha256='sample',event_offset=100000+i*10000,events=10000))
            (root/'campaign.json').write_text(json.dumps(dict(batches=entries,geometry_hashes={'detector.xml':'geometry'})))
            with patch('highstat_analysis.np.load') as read:
                with self.assertRaisesRegex(ValueError,'feature semantics'):
                    load_split(root,'validation')
                read.assert_not_called()


if __name__=='__main__':unittest.main()
