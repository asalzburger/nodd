import unittest
from placement_report import first_event_time
from placement_variant import canonical
import xml.etree.ElementTree as ET


class PlacementProbeControls(unittest.TestCase):
    def test_first_event_uses_first_run_and_requires_real_event(self):
        log="[ 8.1] LAR_PLACE_STARTUP_DONE\n[ 60.123456] ParticleHandler INFO +++ Event 0 Begin event action.\n[ 61.7] ParticleHandler INFO +++ Event 0 Begin event action.\n"
        self.assertEqual(first_event_time(log),60.123456)
        with self.assertRaises(ValueError): first_event_time("[ 10.1] LAR_PLACE_STARTUP_DONE\n")

    def test_xml_equivalence_ignores_only_indentation(self):
        a=ET.fromstring('<a id="10">\n <b> 1,2 </b>\n</a>')
        b=ET.fromstring('<a id="10"><b>1,2</b></a>')
        self.assertEqual(canonical(a),canonical(b))
        b.find('b').text='1,3'
        self.assertNotEqual(canonical(a),canonical(b))
        b.find('b').text='1,2';b.set('id','11')
        self.assertNotEqual(canonical(a),canonical(b))


if __name__=="__main__": unittest.main()
