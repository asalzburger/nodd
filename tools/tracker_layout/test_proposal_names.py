"""Ensure renaming cannot alter physical layers or silently drop a candidate."""
import json
import unittest
from name_proposals import SOURCE, OUTPUT, NAMES, named_catalogue


class ProposalNamesTests(unittest.TestCase):
    def test_named_catalogue_preserves_physics_and_source(self):
        original = json.loads(SOURCE.read_text())
        frozen = json.dumps(original, sort_keys=True)
        result = named_catalogue(original)
        self.assertEqual(json.dumps(original, sort_keys=True), frozen)
        self.assertEqual(result['active_options'], ['cobe', 'pint'])
        self.assertEqual(result['host'], original['host'])
        self.assertEqual(result['units'], original['units'])
        for before, after in zip(original['candidates'], result['candidates']):
            self.assertEqual(after['layers'], before['layers'])
            self.assertEqual(after['legacy_id'], before['id'])
            self.assertEqual((after['id'], after['name']), NAMES[before['id']])
        retained = json.loads(OUTPUT.read_text())
        retained.pop('naming_provenance')
        self.assertEqual(retained, result)

    def test_unexpected_option_fails(self):
        source = json.loads(SOURCE.read_text())
        source['candidates'].pop()
        with self.assertRaises(ValueError):
            named_catalogue(source)


if __name__ == '__main__':
    unittest.main()
