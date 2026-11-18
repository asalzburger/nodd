import unittest
from transport import raw_sensitive_count


class InventoryTests(unittest.TestCase):
    def inventory(self, planes):
        return {'LArBarrelHits':{'planes':planes,'keys':[[i,0] for i in range(11)]},
                'LArEndcapHits':{'wheel_planes':[384,720,1360]}}

    def test_old_and_compact_counts_are_distinct(self):
        self.assertEqual(raw_sensitive_count(self.inventory(1536)),43648)
        self.assertEqual(raw_sensitive_count(self.inventory(1408)),40832)

    def test_missing_layer_rejected(self):
        item=self.inventory(1408);item['LArBarrelHits']['keys'].pop(3)
        with self.assertRaises(ValueError):raw_sensitive_count(item)


if __name__=='__main__':unittest.main()
