"""Focused controls for reuse identity and the dangerous backing-notch case."""
import copy
import unittest
import xml.etree.ElementTree as ET

from prepare_comparison import inspect, verify_mother


def fixture():
    doc = ET.fromstring('''<lccdd><detectors><detector type="nODDShortStripBarrel" id="4">
      <layer id="0"><stave id="0"><module name="m0" id="0" z="0*mm" lift="0*mm">
        <piece name="m0_sensor" kind="box" sensitive="true" sensor="0" material="Silicon"
          u="0*mm" v="0*mm" w="0*mm" sx="48*mm" sy="96*mm" sz=".2*mm"/>
      </module></stave></layer></detector></detectors></lccdd>''')
    stave = doc.find('.//stave')
    other = copy.deepcopy(stave[0]);other.set('name','m1');other.set('id','1');other.set('z','100*mm')
    other[0].set('name','m1_sensor');stave.append(other)
    return doc


class ComparisonControls(unittest.TestCase):
    def test_instance_pose_and_names_may_differ(self):
        _, report = inspect(fixture())
        self.assertEqual(report['module_instances'],2)
        self.assertEqual(report['instances'][1]['pieces'],{'m0_sensor':'m1_sensor'})

    def test_physics_id_and_cut_changes_rejected(self):
        for key,value in (('sensor','1'),('material','Copper'),('sz','.21*mm'),('w','.01*mm')):
            doc=fixture();doc.find('.//stave')[1][0].set(key,value)
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'recipes differ'):
                inspect(doc)
        doc=fixture();ET.SubElement(doc.find('.//stave')[1][0],'cut',kind='box')
        with self.assertRaisesRegex(ValueError,'recipes differ'):inspect(doc)

    def test_notch_requires_removed_physical_material(self):
        module = fixture().find('.//module')
        backing=ET.SubElement(module,'piece',name='backing',kind='box',material='CFRP',
            u='0*mm',v='0*mm',w='-.925*mm',sx='48*mm',sy='96*mm',sz='.2*mm')
        with self.assertRaisesRegex(ValueError,'removes physical'):verify_mother(module)
        for u in ('-12*mm','12*mm'):
            ET.SubElement(backing,'cut',kind='box',u=u,v='0*mm',w='0*mm',sx='20.1*mm',sy='64.1*mm',sz='.4*mm')
        verify_mother(module)
        module[0].set('sx','50*mm')
        with self.assertRaisesRegex(ValueError,'exceeds'):verify_mother(module)


if __name__ == '__main__':unittest.main()
