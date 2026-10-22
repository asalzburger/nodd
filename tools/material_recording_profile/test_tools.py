"""Offline controls for source selection and profiler accounting."""
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from prepare_odd import prepare
from sample_summary import summarize


class ToolsTest(unittest.TestCase):
    def test_selection_preserves_tracker_and_passive_support(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            (base/'OpenDataDetectorDefs.xml').write_text('''<lccdd>
              <includes><gdmlFile ref="materials.xml"/></includes>
              <define><constant name="world_x" value="12*m"/></define>
              <include ref="identifiers.xml"/></lccdd>''')
            (base/'OpenDataDetectorTracker.xml').write_text('''<lccdd>
              <include ref="detectors/BeamPipe.xml"/>
              <include ref="detectors/TrackerPixels.xml"/>
              <include ref="detectors/TrackerShortStrips.xml"/>
              <include ref="detectors/TrackerLongStrips.xml"/>
              <include ref="detectors/Solenoid.xml"/>
              <detectors><detector id="1000" name="OpenDataTracker">
              <composite name="PST"/></detector></detectors>
              <plugins><plugin name="DD4hepVolumeManager"/></plugins></lccdd>''')
            output=base/'out.xml'
            prepare(base,output)
            root=ET.parse(output).getroot()
            refs=[p.attrib['ref'] for p in root.findall('include')]
            self.assertEqual(len(refs),5)
            self.assertFalse(any('Solenoid' in ref for ref in refs))
            self.assertTrue(all(Path(ref).is_absolute() for ref in refs))
            self.assertEqual(root.find('detectors/detector/composite').attrib['name'],'PST')
            self.assertEqual(root.find('define/constant').attrib['value'],'12*m')
            self.assertEqual(root.find('plugins/plugin').attrib['name'],'DD4hepVolumeManager')
            self.assertTrue(root.find('includes/gdmlFile').attrib['ref'].endswith('materials.xml'))
            evidence=json.loads(output.with_suffix('.provenance.json').read_text())
            self.assertEqual(evidence['removed_tracker_includes'],['detectors/Solenoid.xml'])

    def test_unrecognized_tracker_structure_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            (base/'OpenDataDetectorDefs.xml').write_text('<lccdd/>')
            (base/'OpenDataDetectorTracker.xml').write_text('<lccdd><include ref="new.xml"/></lccdd>')
            with self.assertRaisesRegex(ValueError,'exactly one'):
                prepare(base,base/'out.xml')

    def test_main_thread_recursive_accounting_excludes_idle_thread(self):
        sample='''Call graph:
    10 Thread_1 main
    + 10 caller  (in lib)
    +   8 recurse  (in lib)
    +     5 recurse  (in lib)
    +       3 leaf  (in lib)
    +   2 output  (in lib)
    10 Thread_2 worker
    + 10 idle  (in lib)
Total number in stack
'''
        result=summarize(sample)
        self.assertEqual(result['main_thread_samples'],10)
        cumulative=dict(result['cumulative_top40'])
        exclusive=dict(result['exclusive_top20'])
        self.assertEqual(cumulative['recurse'],8)
        self.assertEqual(exclusive['recurse'],5)
        self.assertEqual(sum(exclusive.values()),10)
        self.assertNotIn('idle',cumulative)


if __name__=='__main__':
    unittest.main()
