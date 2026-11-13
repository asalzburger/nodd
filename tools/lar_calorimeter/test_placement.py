"""Preservation and negative controls for opt-in real LAr period mothers."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

import barrel_export
import endcap_export
from barrel_geometry import build as barrel
from endcap_geometry import build as endcaps
from placement import barrel_envelope, endcap_envelope


class PlacementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.barrel, cls.bmaterials = barrel()
        cls.endcaps, cls.ematerials = endcaps()
        cls.barrel['materials'] = cls.bmaterials.recipes
        cls.endcaps['materials'] = cls.ematerials.recipes

    def test_barrel_envelope_exact_partition_and_no_report_mutation(self):
        before = deepcopy(self.barrel)
        envelope, proof = barrel_envelope(self.barrel)
        self.assertEqual(before, self.barrel)
        self.assertEqual(proof['physical_mothers'], 1536)
        self.assertEqual(proof['material_leaf_count'], 88)
        self.assertLess(abs(proof['unfilled_relative_residual']), 1e-11)
        self.assertEqual(envelope['clip_annulus_mm'], {'rmin': 2172.8, 'rmax': 2578.3})
        self.assertEqual(envelope['depth_mm'], 7820.)

    def test_all_turbine_envelopes_partition_without_report_mutation(self):
        before = deepcopy(self.endcaps)
        for wheel in self.endcaps['wheels']:
            envelope, proof = endcap_envelope(wheel, self.ematerials)
            self.assertEqual(proof['physical_mothers'], 2*wheel['periods'])
            self.assertEqual(proof['material_leaf_count'], 8)
            self.assertLess(abs(proof['unfilled_relative_residual']), 1e-11)
            self.assertEqual(envelope['clip_annulus_mm'], {'rmin': wheel['inner_radius_mm'], 'rmax': wheel['outer_radius_mm']})
        self.assertEqual(before, self.endcaps)

    def test_export_changes_only_optional_envelopes(self):
        for source, exporter, filename, count in ((self.barrel, barrel_export, 'barrel.xml', 1),
                                                  (self.endcaps, endcap_export, 'endcaps.xml', 3)):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as tmp:
                old, new = Path(tmp)/'old', Path(tmp)/'new'
                old.mkdir(); new.mkdir()
                baseline, candidate = deepcopy(source), deepcopy(source)
                exporter.compact(baseline, old)
                exporter.compact(candidate, new, real_periods=True)
                a, b = ET.parse(old/filename), ET.parse(new/filename)
                envelopes = b.findall('.//period_envelope')
                self.assertEqual(len(envelopes), count)
                self.assertFalse(a.findall('.//period_envelope'))
                for parent in b.iter():
                    for node in list(parent):
                        if node.tag == 'period_envelope': parent.remove(node)
                # Indentation whitespace belongs to the added nodes, not to
                # the physical detector description.
                for tree in (a, b):
                    for node in tree.iter(): node.text = node.tail = None
                self.assertEqual(ET.tostring(a.getroot()), ET.tostring(b.getroot()))
                candidate.pop('placement')
                self.assertEqual(baseline, candidate)

    def test_barrel_missing_leaf_and_moved_boundaries_rejected(self):
        bad = deepcopy(self.barrel); bad['pieces'].pop()
        with self.assertRaisesRegex(ValueError, 'Unsupported'): barrel_envelope(bad)
        bad = deepcopy(self.barrel)
        next(p for p in bad['pieces'] if p['name'] == 'gap_1_0')['upper_face'][1] += .01
        with self.assertRaisesRegex(ValueError, 'boundary'): barrel_envelope(bad)
        bad = deepcopy(self.barrel)
        next(p for p in bad['pieces'] if p['name'] == 'pcb_0')['lower_face'][1] += .01
        with self.assertRaisesRegex(ValueError, 'boundary'): barrel_envelope(bad)

    def test_barrel_depth_radial_partition_and_volume_fail_closed(self):
        bad = deepcopy(self.barrel); bad['pieces'][0]['depth_mm'] += 1
        with self.assertRaisesRegex(ValueError, 'depth'): barrel_envelope(bad)
        bad = deepcopy(self.barrel); bad['pieces'][0]['clip_annulus_mm']['rmin'] += 1
        with self.assertRaisesRegex(ValueError, 'boundary'): barrel_envelope(bad)
        bad = deepcopy(self.barrel); bad['pieces'][0]['volume_mm3'] *= 1.01
        with self.assertRaisesRegex(ValueError, 'fill'): barrel_envelope(bad)
        bad = deepcopy(self.barrel); bad['pieces'][0]['clip_annulus_mm']['rmin'] = float('nan')
        with self.assertRaisesRegex(ValueError, 'Nonfinite'): barrel_envelope(bad)

    def test_turbine_missing_leaf_and_internal_gap_rejected(self):
        bad = deepcopy(self.endcaps['wheels'][0]); bad['pieces'].pop()
        with self.assertRaisesRegex(ValueError, 'Unsupported'): endcap_envelope(bad, self.ematerials)
        bad = deepcopy(self.endcaps['wheels'][0])
        next(p for p in bad['pieces'] if p['name'].endswith('_pcb'))['lower_face']['bound'] += .01
        with self.assertRaisesRegex(ValueError, 'boundary'): endcap_envelope(bad, self.ematerials)

    def test_turbine_depth_boundaries_and_volume_fail_closed(self):
        bad = deepcopy(self.endcaps['wheels'][0]); bad['pieces'][0]['half_z_mm'] += 1
        with self.assertRaisesRegex(ValueError, 'depth'): endcap_envelope(bad, self.ematerials)
        bad = deepcopy(self.endcaps['wheels'][0]); bad['pieces'][0]['clip_annulus_mm']['rmin'] += 1
        with self.assertRaisesRegex(ValueError, 'boundary'): endcap_envelope(bad, self.ematerials)
        bad = deepcopy(self.endcaps['wheels'][0]); bad['pieces'][0]['volume_mm3'] *= 1.01
        with self.assertRaisesRegex(ValueError, 'fill'): endcap_envelope(bad, self.ematerials)
        bad = deepcopy(self.endcaps['wheels'][0]); bad['pieces'][0]['clip_annulus_mm']['rmin'] = float('nan')
        with self.assertRaisesRegex(ValueError, 'Nonfinite'): endcap_envelope(bad, self.ematerials)


if __name__ == '__main__': unittest.main()
