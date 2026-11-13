import unittest
from pathlib import Path
import tempfile
from placement_probe import sha
from placement_report import first_event_time, bind_component
from placement_smoke import canonical_cell
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

    def test_native_binding_rejects_stale_expected_and_different_library(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'barrel.xml').write_text('<detector/>');(root/'expected.json').write_text('{"partition":0}')
            report={'execution':{'compact_sha256':sha(root/'barrel.xml'),'expected_sha256':sha(root/'expected.json'),'library_sha256':'tested-library'}}
            bind_component(report,root,'barrel.xml','tested-library')
            with self.assertRaisesRegex(ValueError,'factory'): bind_component(report,root,'barrel.xml','other-library')
            (root/'expected.json').write_text('{"partition":0.25}')
            with self.assertRaisesRegex(ValueError,'Stale'): bind_component(report,root,'barrel.xml','tested-library')

    def test_canonical_cells_reject_high_bits_and_ghost_virtual_indices(self):
        barrel={'descriptor':'system:8,plane:11,layer:4,gap:1,theta:-12','keys':{(0,-2)},'planes':1536,'phi_merge':2}
        cell=10+(((-2)&4095)<<24)
        self.assertEqual(canonical_cell(cell,'LArBarrelHits',barrel)['theta'],-2)
        for bad in (cell|(1<<60),10+(3<<24),cell|(1<<8)):
            with self.assertRaises(ValueError): canonical_cell(bad,'LArBarrelHits',barrel)
        turbine={'descriptor':'system:8,side:2,wheel:2,plane:11,gap:1,rho:6,z:4','keys':{(0,1,2)},'wheel_planes':[384,720,1360]}
        cell=11+(1<<8)+(1<<24)+(2<<30)
        canonical_cell(cell,'LArEndcapHits',turbine)
        with self.assertRaises(ValueError): canonical_cell(cell+(1<<24),'LArEndcapHits',turbine)


if __name__=="__main__": unittest.main()
