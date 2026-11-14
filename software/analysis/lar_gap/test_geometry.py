"""Transformation and exhaustive-native comparison failure controls."""
from copy import deepcopy
import unittest
import xml.etree.ElementTree as ET

from geometry import transform,verify_transform,dimension,endcap
from native import compare_rows


def fixture():
    root=ET.Element('lccdd');ET.SubElement(ET.SubElement(root,'define'),'constant',name='world_z',value='7860*mm')
    ros=ET.SubElement(root,'readouts')
    ro=ET.SubElement(ros,'readout',name='LArEndcapHits')
    ET.SubElement(ro,'segmentation',wheel_table_mm='400 1000 704 1 1000 2000 400 1 2000 2800 1360 1',reference_table_mm='0 0 0 400 0 0')
    ds=ET.SubElement(root,'detectors')
    ET.SubElement(ds,'detector',name='LArBarrel',id='10',readout='LArBarrelHits')
    d=ET.SubElement(ds,'detector',name='LArEndcaps',id='11',type='nODDLArEndcapPrototype',readout='LArEndcapHits')
    ET.SubElement(d,'sensitive',type='calorimeter')
    for w in range(3):
        wheel=ET.SubElement(d,'wheel',index=str(w));ET.SubElement(wheel,'period_envelope',policy='real-periods-v1')
        ET.SubElement(wheel,'piece',z='17*mm',a22='1',material='test-fixture')
    for side in (1,2):
        for w,n in enumerate((704,400,1360)):
            for plane in range(n):ET.SubElement(d,'replica',side=str(side),wheel=str(w),plane=str(plane),z=f'{5235 if side==1 else -5235}*mm',a22='1' if side==1 else '-1')
    for i in range(36):ET.SubElement(d,'piece',name=f'root{i}',z=f'{5380 if i<18 else -5380}*mm',material='test-fixture')
    for i in range(38210):ET.SubElement(d,'piece',name=f'child{i}',parent_name=f'root{i%36}',z='7*mm',material='test-fixture')
    return ET.ElementTree(root)


class TransformationControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.original=fixture();cls.candidate=transform(cls.original)

    def test_all_top_level_branches_move_both_signs(self):
        a=endcap(self.original.getroot());b=endcap(self.candidate.getroot())
        self.assertEqual(verify_transform(self.original,self.candidate)['replicas'],4928)
        for old,new in zip(a[1]+a[2],b[1]+b[2]):
            self.assertAlmostEqual(abs(dimension(old.get('z')))-abs(dimension(new.get('z'))),400)
        self.assertEqual(a[0].find('wheel/piece').attrib,b[0].find('wheel/piece').attrib)
        self.assertEqual(a[0].find("piece[@name='child0']").attrib,b[0].find("piece[@name='child0']").attrib)
        self.assertEqual(self.original.getroot().find('define/constant').attrib,self.candidate.getroot().find('define/constant').attrib)

    def test_wrong_negative_side_translation_is_rejected(self):
        c=deepcopy(self.candidate);c.find("detectors/detector[@id='11']/replica[@side='2']").set('z','-5635*mm')
        with self.assertRaisesRegex(ValueError,'signed rigid'):verify_transform(self.original,c)

    def test_local_readout_barrel_dimensions_and_rotation_changes_rejected(self):
        targets=[("detectors/detector[@id='11']/piece[@name='child0']",'z','8*mm'),
                 ("detectors/detector[@id='11']/replica[@side='2']",'a22','1'),
                 ('readouts/readout/segmentation','reference_table_mm','changed'),
                 ("detectors/detector[@id='10']",'extra','changed'),
                 ('define/constant','value','7460*mm')]
        for path,key,value in targets:
            with self.subTest(path=path):
                c=deepcopy(self.candidate);c.find(path).set(key,value)
                with self.assertRaisesRegex(ValueError,'Unexpected XML'):verify_transform(self.original,c)

    def test_missing_replica_unknown_parent_and_ambiguous_root_rejected(self):
        for mode in ('replica','parent','root'):
            c=deepcopy(self.original);d=c.find("detectors/detector[@id='11']")
            if mode=='replica':d.remove(d.find('replica'))
            if mode=='parent':d.find("piece[@name='child0']").set('parent_name','missing')
            if mode=='root':d.set('id','12')
            with self.subTest(mode=mode),self.assertRaises(ValueError):transform(c)


class NativeLedgerControls(unittest.TestCase):
    def row(self,root='LArEndcaps',depth=3,z=-5200):
        return dict(path='/world/root/period/leaf',root=root,depth=depth,root_relative=depth==2,
                    centre_mm=[1.,2.,float(z)],local_centre_mm=[0.,0.,17.],rotation=[1.,0.,0.,0.,-1.,0.,0.,0.,-1.],
                    local_rotation=[1.]*9,material='test',capacity_mm3=7.,sensitive=True)

    def test_all_descendants_have_signed_global_shift_and_fixed_local_pose(self):
        a=self.row();b=deepcopy(a);b['centre_mm'][2]+=400
        self.assertTrue(compare_rows(a,b))
        a=self.row(depth=2,z=5235);a['local_centre_mm'][2]=5235;b=deepcopy(a)
        b['centre_mm'][2]-=400;b['local_centre_mm'][2]-=400
        self.assertTrue(compare_rows(a,b))

    def test_fixed_barrel_and_endcap_root_assembly(self):
        for a in (self.row(root='LArBarrel'),self.row(depth=1,z=0)):
            self.assertFalse(compare_rows(a,deepcopy(a)))

    def test_native_missing_shift_rotation_or_material_change_rejected(self):
        a=self.row()
        for key,value in (('centre_mm',[1.,2.,-5200.]),('local_centre_mm',[0.,0.,18.]),('material','other'),('rotation',[0.]*9)):
            b=deepcopy(a);b['centre_mm'][2]+=400;b[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):compare_rows(a,b)


if __name__=='__main__':unittest.main()
