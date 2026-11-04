"""Retained map identity and unsafe carrier/grid substitutions."""
import copy
import gzip
import json
import unittest

from verify_record import DATA, verify, verify_grid


class MapRecord(unittest.TestCase):
    def test_current_retained_map_matches_native_evidence(self):
        self.assertEqual(verify(), (67, 8650, 2003))

    def test_wrong_carrier_or_grid_is_rejected(self):
        material = json.loads(gzip.decompress((DATA / 'material_map.json.gz').read_bytes()))
        selection = json.loads((DATA / 'selection.json').read_text())
        reload = json.loads((DATA / 'current-mapping-report.json').read_text())['serialized_reload']
        for corruption in ('id', 'key', 'grid'):
            wrong = copy.deepcopy(material)
            entry = wrong['KeyedSurfaces'][0]
            if corruption == 'id':
                entry['geometry_id'] = wrong['KeyedSurfaces'][1]['geometry_id']
            elif corruption == 'key':
                entry['key'] = 'historical-map-carrier'
            else:
                entry['material']['data'].pop()
            with self.subTest(corruption=corruption), self.assertRaises(ValueError):
                verify_grid(wrong, selection, reload)


if __name__ == '__main__':
    unittest.main()
