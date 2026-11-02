"""Portable checks for explicit redesigned module and cold-petal payloads."""
import copy
import math
import unittest

import native


class NativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = native.load()
        cls.document, unused, cls.expected = native.build(cls.config)

    def test_all_required_physical_parts_and_windows_exist(self):
        counts = self.expected['counts']
        self.assertEqual(counts['sensitive'], 792)
        self.assertEqual(counts['readout'], 1584)
        self.assertEqual(counts['thermal_pickup'], 792)
        self.assertEqual(counts['backing'], 792)
        self.assertEqual(counts['power_bus'], 144)
        self.assertEqual(counts['protection_allocation'], 72)
        self.assertEqual(counts['board_mount'], 96)
        self.assertGreater(counts['cooling_tube'], 500)
        self.assertEqual(self.expected['disc_layers'], [0, 6])
        for e in self.expected['entities']:
            self.assertTrue(all(math.isfinite(x) for x in e['center_mm']))
            if e['role'] in ('backing', 'thermal_pickup', 'core'):
                self.assertGreater(e['cuts'], 0)
            if e['role'] == 'thermal_pickup': self.assertLessEqual(e['height_mm'], 8.)
        self.assertEqual(max(e['height_mm'] for e in self.expected['entities'] if e['role'] == 'thermal_pickup'), 7.725)

    def test_identifiers_grid_and_all_six_source_coverage(self):
        ids = [tuple(sorted(e['ids'].items())) for e in self.expected['entities'] if e['role'] == 'sensitive']
        self.assertEqual(len(ids), len(set(ids)))
        segmentation = self.document.find('./readouts/readout/segmentation')
        self.assertEqual(segmentation.attrib['grid_size_y'], '2*mm')
        self.assertEqual(self.expected['cell_mm'], [.075, 2.])
        self.assertEqual(len(self.expected['source_coverage']['checks']), 18)
        self.assertEqual(sum(c['failed_rays'] for c in self.expected['source_coverage']['checks']), 0)
        self.assertFalse(self.expected['shared_services_instantiated'])

    def test_cooling_uses_two_distinct_ordered_port_pairs(self):
        pipes = native.plumbing(self.config)
        ports = [p for p in pipes if p['kind'] == 'line' and 'port' in p['label']]
        self.assertEqual(len(ports), 4)
        self.assertEqual({p['loop'] for p in ports}, {'inner', 'outer'})
        self.assertEqual([round(math.degrees(math.atan2(p['b'][1], p['b'][0])), 5) for p in ports], self.config['cooling_ports_deg'])
        self.assertTrue(all(math.dist(p['a'], p['b']) > 0 for p in ports))

    def test_thermal_contact_cannot_be_inferred_from_pipe_plane(self):
        # A land remote from every loop cannot pass merely by ending at w=-4.05.
        pipes = native.plumbing(self.config)
        remote = dict(layer=0, petal=0, ring=0, radius_mm=100., phi_rad=0.)
        screen = native.contact_screen(self.config, [remote], pipes)
        self.assertEqual(screen['definite_missing_contacts'], 1)

    def test_central_insert_guard_clearance_and_rejected_18mm_control(self):
        self.assertEqual(self.config['thermal']['endcap_pad_mm'], [16.,60.])
        self.assertGreater(self.expected['guard_clearance']['minimum_other_guard_clearance_mm'], .5)
        self.assertEqual(self.expected['guard_clearance']['intersecting_rectangle_pairs'], 0)
        config = copy.deepcopy(self.config); config['thermal']['endcap_pad_mm'] = [18.,60.]
        modules = native.geometry(self.config)[-1]['modules']
        self.assertGreater(native.guard_clearance(config,modules)['intersecting_rectangle_pairs'], 0)

    def test_obsolete_ring_sketch_is_rejected(self):
        config = copy.deepcopy(self.config); config['ring_centres_mm'] = [289.5, 381., 472.5, 564., 655.5]
        with self.assertRaisesRegex(ValueError, '703 mm'): native.build(config)


if __name__ == '__main__': unittest.main()
