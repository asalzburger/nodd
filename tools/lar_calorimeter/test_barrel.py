"""Standard-library physical tessellation/readout/displacement controls."""
from copy import deepcopy
import math
import unittest
from barrel_geometry import build, canonical_reference, decode, disk_polygon_area, encode, inside_polygon, logical_id, rotate, theta_bounds
from barrel_export import totals


class BarrelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model, cls.materials = build()

    def test_exact_annular_tessellation(self):
        model = self.model
        self.assertEqual(len(model['pieces']), 88)
        self.assertEqual(len(model['replicas']), 1536)
        self.assertEqual(model['physical_sensitive_elements'], 33792)
        self.assertLess(abs(model['sampling']['fill_relative_residual']), 2e-10)
        for layer in range(11):
            pieces = [p for p in model['pieces'] if p['layer'] == layer]
            a, b = model['sampling']['radii_mm'][layer:layer+2]
            full = math.pi*(b*b-a*a)*2*model['sampling']['half_z_mm']
            observed = sum(p['volume_mm3'] for p in pieces)*1536
            self.assertAlmostEqual(observed/full, 1, delta=2e-10)
            self.assertEqual(sum(p['role'] == 'sensitive' for p in pieces), 2)

    def test_full_cryostat_closure_and_disjoint_passive_tubes(self):
        model = self.model
        e = model['envelopes']
        expected = math.pi*(e['outer_radius_mm']**2-e['inner_radius_mm']**2)*2*e['warm_half_z_mm']
        actual = sum(p['volume_mm3'] for p in model['pieces'])*len(model['replicas'])+sum(p['volume_mm3'] for p in model['passive'])
        self.assertAlmostEqual(actual/expected, 1, delta=2e-10)
        for i,a in enumerate(model['passive']):
            da = a['dimensions_mm']; alo, ahi = a['center_mm'][2]-da['length']/2, a['center_mm'][2]+da['length']/2
            for b in model['passive'][i+1:]:
                db = b['dimensions_mm']; blo, bhi = b['center_mm'][2]-db['length']/2, b['center_mm'][2]+db['length']/2
                radial = min(da['rmax'],db['rmax'])-max(da['rmin'],db['rmin'])
                axial = min(ahi,bhi)-max(alo,blo)
                self.assertFalse(radial > 1e-8 and axial > 1e-8,(a['name'],b['name']))

    def test_first_core_is_passive_lar(self):
        p = [p for p in self.model['pieces'] if p['role'] == 'absorber_core']
        self.assertEqual(p[0]['material'], 'LAr')
        self.assertNotIn('gap', p[0])
        self.assertTrue(all(x['material'] == 'Lead' for x in p[1:]))
        self.assertIn('Br', self.model['materials']['PCB']['composition'])
        self.assertAlmostEqual(sum(self.model['materials']['PCB']['composition'].values()), 1)

    def test_path_closure_and_explicit_endwalls(self):
        self.assertAlmostEqual(self.model['sampling']['half_z_mm'], 3910)
        self.assertAlmostEqual(self.model['envelopes']['cold_inner_half_z_mm'], 4017.2)
        self.assertAlmostEqual(self.model['envelopes']['warm_half_z_mm'], 4100)
        self.assertLess(abs(self.model['sampling']['final_segment_remainder_mm']), .001)
        self.assertAlmostEqual(sum(self.model['sampling']['closed_segments_mm']), self.model['sampling']['path_length_mm'])
        for side in (-1, 1):
            p = next(p for p in self.model['passive'] if p['name'] == f'end_cold_{side}')
            self.assertAlmostEqual(abs(p['center_mm'][2])-p['dimensions_mm']['length']/2, 4017.2)
            bath = next(p for p in self.model['passive'] if p['name'] == f'end_bath_{side}')
            self.assertAlmostEqual(abs(bath['center_mm'][2])-bath['dimensions_mm']['length']/2, 3910)
            self.assertAlmostEqual(abs(bath['center_mm'][2])+bath['dimensions_mm']['length']/2, 4017.2)
            self.assertAlmostEqual(bath['dimensions_mm']['rmin'], 2162.8)
            self.assertAlmostEqual(bath['dimensions_mm']['rmax'], self.model['config']['sampling_outer_radius_mm']+self.model['config']['rear_bath_mm'])

    def test_every_raw_id_unique_and_signed_roundtrip(self):
        ro = self.model['readout']; seen = set()
        for plane in range(ro['planes']):
            for layer in range(11):
                for gap in (0, 1):
                    fields = dict(system=ro['system_id'], plane=plane, layer=layer, gap=gap, theta=0)
                    value = encode(fields)
                    self.assertNotIn(value, seen); seen.add(value)
                    self.assertEqual(decode(value), fields)
        self.assertEqual(len(seen), 33792)
        fields = dict(system=10, plane=1535, layer=10, gap=1, theta=-2048)
        self.assertEqual(decode(encode(fields)), fields)
        fields['theta'] = 2048
        with self.assertRaises(ValueError): encode(fields)

    def test_all_grouped_references_in_canonical_gap(self):
        ro = self.model['readout']; count = 0; negative = False
        for layer in ro['layers']:
            piece = next(p for p in self.model['pieces'] if p.get('gap') == 0 and p['layer'] == layer['layer'])
            for row in layer['reference_points']:
                p = row['position_mm']; radius = math.hypot(*p[:2])
                self.assertTrue(inside_polygon(piece['vertices_mm'], p[:2]))
                self.assertLess(piece['clip_annulus_mm']['rmin'], radius)
                self.assertLess(radius, piece['clip_annulus_mm']['rmax'])
                self.assertLess(abs(p[2]), piece['depth_mm']/2)
                theta = math.atan2(radius, p[2]); ids = set()
                for plane in (0, 1, 1534, 1535):
                    for gap in (0, 1):
                        fields = dict(system=ro['system_id'], plane=plane, layer=layer['layer'], gap=gap)
                        value = decode(logical_id(fields, theta, ro))
                        self.assertEqual(value['plane'], plane//2*2)
                        self.assertEqual(value['gap'], 0)
                        self.assertEqual(value['theta'], row['theta_index'])
                        if plane < 2: ids.add(encode(value))
                self.assertEqual(len(ids), 1)
                negative |= row['theta_index'] < 0
                count += ro['planes']//2
        self.assertTrue(negative)
        self.assertEqual(count, self.model['logical_channels'])

    def test_both_theta_boundaries_and_no_ghosts(self):
        ro = self.model['readout']
        for layer in ro['layers']:
            piece = next(p for p in self.model['pieces'] if p.get('gap') == 0 and p['layer'] == layer['layer'])
            step = ro['theta_merging'][layer['layer']]
            for index in (layer['indices'][0]-step, layer['indices'][-1]+step):
                with self.assertRaises(ValueError): canonical_reference(piece, index, ro)
            for index in layer['indices'][1:-1]:
                lo, hi = theta_bounds(index, layer['layer'], ro)
                for theta, want in ((lo+1e-10, index), (hi-1e-10, index), (hi+1e-10, index+step)):
                    fields = dict(system=10, plane=1, layer=layer['layer'], gap=1)
                    self.assertEqual(decode(logical_id(fields, theta, ro))['theta'], want)

    def test_independent_circle_area_controls(self):
        square = [[-3, -3], [3, -3], [3, 3], [-3, 3]]
        self.assertAlmostEqual(disk_polygon_area(square, 2), math.pi*4, delta=1e-12)
        self.assertAlmostEqual(disk_polygon_area(square, 10), 36, delta=1e-12)
        sector = [[0, 0], [3, 0], [3, 3], [0, 3]]
        self.assertAlmostEqual(disk_polygon_area(sector, 2), math.pi, delta=1e-12)
        self.assertAlmostEqual(disk_polygon_area(list(reversed(sector)), 2), math.pi, delta=1e-12)

    def test_geometry_negative_controls(self):
        for key, value in [('electrode_mm', 12), ('planes', 1535), ('front_bath_mm', 11), ('theta_fine_pitch_rad', .1), ('end_bath_mm', 5000)]:
            c = deepcopy(self.model['config']); c[key] = value
            with self.assertRaises(ValueError): build(c)
        c = deepcopy(self.model['config']); c['segments_mm'][-1] += 1
        with self.assertRaises(ValueError): build(c)

    def test_parent_displacement_conservation_and_failures(self):
        report = deepcopy(self.model)
        mother = next(p for p in report['passive'] if p['name'] == 'rear_bath')
        child = deepcopy(mother); child.update(name='test_service', role='test_fixture', parent_name='rear_bath', volume_mm3=100, mass_g=.1396)
        mother['exclusive_volume_mm3'] = mother['volume_mm3']-100
        mother['displaced_volume_mm3'] = 100
        report['passive'].append(child)
        totals(report)
        self.assertAlmostEqual(report['mass_g'], self.model['mass_g'], delta=1e-4)
        # A meaningful negative perturbation exceeds the declared floating-point
        # ledger tolerance even for the enlarged rear-bath mother.
        mother['exclusive_volume_mm3'] += 10000
        with self.assertRaises(ValueError): totals(report)
        child['parent_name'] = 'nonexistent'
        with self.assertRaises(ValueError): totals(report)
        child['parent_name'] = child['name']
        with self.assertRaises(ValueError): totals(report)


if __name__ == '__main__':
    unittest.main()
