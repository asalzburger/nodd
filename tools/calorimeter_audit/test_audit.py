"""Bounded arithmetic and repeat/material accounting controls; test fixtures only."""
import unittest
import xml.etree.ElementTree as ET
from audit import quantity,stack

class AuditTests(unittest.TestCase):
    def test_unit_conversion(self):
        self.assertEqual(quantity('3*cm + 0.002*m',{'cm':10,'m':1000}),32)
        self.assertEqual(quantity('2*layer',{'layer':5.05}),10.1)

    def test_unsafe_or_unknown_expressions(self):
        for text in ('__import__("os").system("echo bad")','mm.real','[1][0]','2**3'):
            with self.assertRaises(ValueError):quantity(text,{'mm':1})
        with self.assertRaises(KeyError):quantity('unassigned*mm',{'mm':1})
        with self.assertRaises(ValueError):quantity('1e999',{})

    def test_nonuniform_repeated_stacks(self):
        xml='<detector><layer repeat="2"><slice material="A" thickness="2*mm"/><slice material="B" thickness="1*mm" sensitive="yes"/></layer><layer repeat="3"><slice material="A" thickness="4*mm"/><slice material="B" thickness="2*mm" sensitive="yes"/></layer></detector>'
        r=stack(ET.fromstring(xml),{'mm':1})
        self.assertEqual(r['layers'],5);self.assertEqual(r['sensitive_planes_per_stave'],5)
        self.assertEqual(r['material_normal_depth_mm'],{'A':16,'B':8})
        self.assertEqual(r['total_normal_depth_mm'],24)

    def test_invalid_slice_or_repeat(self):
        for repeat,thickness in ((0,1),(1,0),(1,-1)):
            xml=f'<detector><layer repeat="{repeat}"><slice material="A" thickness="{thickness}"/></layer></detector>'
            with self.assertRaises(ValueError):stack(ET.fromstring(xml),{})

if __name__=='__main__':unittest.main()
