"""Transformation and exhaustive-native comparison failure controls."""
from copy import deepcopy
import unittest
import xml.etree.ElementTree as ET

from geometry import transform,verify_transform,dimension,endcap
from native import compare_rows,solid_signature,solid_digest,matrix_signature,retained_accounting


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
                    local_rotation=[1.]*9,material='test',solid_sha256='test-solid',sensitive=True)

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
        for key,value in (('centre_mm',[1.,2.,-5200.]),('local_centre_mm',[0.,0.,18.]),('material','other'),('rotation',[0.]*9),('solid_sha256','other-solid')):
            b=deepcopy(a);b['centre_mm'][2]+=400;b[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):compare_rows(a,b)


class NativeDouble:
    """Native API fixture whose stochastic-capacity API is explicitly forbidden."""
    def __init__(self,kind,**methods):self.kind=kind;self.methods=methods
    def ClassName(self):return self.kind
    def __getattr__(self,name):
        if name=='Capacity':raise AssertionError('Stochastic Boolean Capacity must never be invoked')
        try:return object.__getattribute__(self,'methods')[name]
        except KeyError:raise AttributeError(name)


class NativeSolidControls(unittest.TestCase):
    def box(self,half=1.):
        return NativeDouble('TGeoBBox',GetDX=lambda:half,GetDY=lambda:2.,GetDZ=lambda:3.,GetOrigin=lambda:[0.,0.,0.])

    def matrix(self,x=0.,scale=1.):
        return NativeDouble('TGeoHMatrix',GetTranslation=lambda:[x,0.,0.],GetRotationMatrix=lambda:[0.,-1.,0.,1.,0.,0.,0.,0.,1.],GetScale=lambda:[scale,1.,1.])

    def composite(self,operation='TGeoSubtraction',left=None,right=None,matrix=None):
        boolean=NativeDouble(operation,GetLeftShape=lambda:left or self.box(4.),GetRightShape=lambda:right or self.box(),
                             GetLeftMatrix=lambda:None,GetRightMatrix=lambda:matrix)
        return NativeDouble('TGeoCompositeShape',GetBoolNode=lambda:boolean)

    def test_boolean_capacity_is_forbidden_and_native_parameters_are_deterministic(self):
        shape=self.composite(left=self.composite('TGeoIntersection'),matrix=self.matrix(2.))
        a=solid_signature(shape,10.);b=solid_signature(deepcopy(shape),10.)
        self.assertEqual(solid_digest(a),solid_digest(b))
        self.assertEqual(a['right_matrix']['translation_mm'],[.2,0.,0.])
        self.assertEqual(a['right_matrix']['rotation'],[0.,-1.,0.,1.,0.,0.,0.,0.,1.])
        self.assertEqual(a['left']['operation'],'TGeoIntersection')

    def test_primitive_boolean_operator_and_operand_pose_changes_have_distinct_signatures(self):
        baseline=solid_digest(solid_signature(self.composite(matrix=self.matrix()),1.))
        for shape in (self.composite(right=self.box(1.01),matrix=self.matrix()),
                      self.composite(matrix=self.matrix(.01)),self.composite('TGeoUnion',matrix=self.matrix())):
            self.assertNotEqual(solid_digest(solid_signature(shape,1.)),baseline)

    def test_all_factory_primitive_parameters_including_sections_are_retained(self):
        tube=NativeDouble('TGeoTubeSeg',GetRmin=lambda:1.,GetRmax=lambda:2.,GetDz=lambda:3.,GetPhi1=lambda:5.,GetPhi2=lambda:95.)
        arb=NativeDouble('TGeoArb8',GetDz=lambda:3.,GetVertices=lambda:list(range(16)))
        xtru=NativeDouble('TGeoXtru',GetNvert=lambda:3,GetNz=lambda:2,GetX=lambda i:i,GetY=lambda i:i+1,
            GetZ=lambda i:2*i-1,GetXOffset=lambda i:i,GetYOffset=lambda i:0.,GetScale=lambda i:1.+i)
        self.assertEqual(solid_signature(tube,1.)['phi_degrees'],[5.,95.])
        self.assertEqual(solid_signature(arb,1.)['vertices_mm'][-1],[14.,15.])
        self.assertEqual(solid_signature(xtru,1.)['sections'][1],dict(z_mm=1.,offset_mm=[1.,0.],scale=2.))
        self.assertEqual(matrix_signature(None,1.),dict(translation_mm=[0.,0.,0.],rotation=[1.,0.,0.,0.,1.,0.,0.,0.,1.],scale=[1.,1.,1.]))

    def test_non_unit_operand_and_placement_matrix_scales_fail_closed(self):
        with self.assertRaisesRegex(ValueError,'non-unit'):matrix_signature(self.matrix(scale=1.001),1.)
        with self.assertRaisesRegex(ValueError,'non-unit'):solid_signature(self.composite(matrix=self.matrix(scale=1.001)),1.)

    def test_nonfinite_or_unknown_shapes_and_operators_fail_closed(self):
        for shape in (self.box(float('nan')),NativeDouble('UnknownSolid'),self.composite('UnknownOperator')):
            with self.subTest(kind=shape.ClassName()),self.assertRaises(ValueError):solid_signature(shape,1.)

    def test_retained_mass_accounting_is_bound_and_not_labeled_native_measurement(self):
        binding=dict(components={'barrel':dict(expected_sha256='bound-fixture',material_totals={'test':dict(volume_mm3=2.,mass_g=3.)})})
        accounting=retained_accounting(binding)['barrel']
        self.assertEqual(accounting['expected_sha256'],'bound-fixture')
        self.assertEqual(accounting['material_totals'],binding['components']['barrel']['material_totals'])
        self.assertIn('Not a new whole-native',accounting['interpretation'])


if __name__=='__main__':unittest.main()
