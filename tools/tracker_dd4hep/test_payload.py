"""ROOT-free adversarial controls for the supplementary native payload audit."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

from audit_payload import (ASSEMBLY_SOURCES, COMPONENTS, PROBE_COUNTS, STRIP_SOURCES,
    compare_artifacts, compare_material, compare_placements, contract, expected_metadata,
    native_audit, required_xml, resolve_recipe, sha, bind_reference, native_fractions)

ELEMENTS={e['name']:e for e in json.loads((Path(__file__).resolve().parents[2]/'detector/config/elements.json').read_text())['elements']}
RECIPES={
    'Air':dict(density_g_cm3=.0012,basis='mass_fraction',composition={'N':.754,'O':.234,'Ar':.012}),
    'Vacuum':dict(density_g_cm3=1e-12,basis='mass_fraction',composition={'H':1.}),
    'Beryllium':dict(density_g_cm3=1.848,basis='mass_fraction',composition={'Be':1.}),
    'Copper':dict(density_g_cm3=8.96,basis='mass_fraction',composition={'Cu':1.}),
    'CO2':dict(density_g_cm3=1.,basis='atom_count',composition={'C':1.,'O':2.}),
    'Nested':dict(density_g_cm3=2.,basis='mass_fraction',composition={'CO2':.75,'Copper':.25})}


class Shape:
    def Contains(self,point):return all(abs(x)<=1 for x in point)


class Material:
    def __init__(self,name):self.name=name
    def GetName(self):return self.name
    def GetDensity(self):return RECIPES[self.name]['density_g_cm3']
    def rows(self):
        fractions=resolve_recipe(self.name,RECIPES,ELEMENTS)
        table={int(e['Z']):e['A'] for e in ELEMENTS.values()}
        return [(z,table[z],w) for z,w in fractions.items()]
    def IsMixture(self):return True
    def GetNelements(self):return len(self.rows())
    def GetZmixt(self):return [r[0] for r in self.rows()]
    def GetAmixt(self):return [r[1] for r in self.rows()]
    def GetWmixt(self):return [r[2] for r in self.rows()]


class Volume:
    def __init__(self,name,material='Copper',assembly=False,children=()):
        self.name=name;self.material=Material(material);self.assembly=assembly
        self.children=[Node(child) for child in children]
    def GetName(self):return self.name
    def GetMaterial(self):return self.material
    def GetShape(self):return Shape()
    def IsAssembly(self):return self.assembly
    def GetNdaughters(self):return len(self.children)
    def GetNode(self,index):return self.children[index]
    def isSensitive(self):return False


class Node:
    def __init__(self,volume):self.volume=volume
    def GetVolume(self):return self.volume


class PayloadControls(unittest.TestCase):
    def test_nested_atom_counts_resolve_to_mass_not_atom_fraction(self):
        result=resolve_recipe('Nested',RECIPES,ELEMENTS)
        carbon=ELEMENTS['C']['A']/(ELEMENTS['C']['A']+2*ELEMENTS['O']['A'])
        self.assertAlmostEqual(result[6],.75*carbon)
        self.assertAlmostEqual(result[8],.75*(1-carbon))
        self.assertAlmostEqual(result[29],.25)
        self.assertNotAlmostEqual(result[6],.75/3)
        native=Material('Nested')
        self.assertLessEqual(compare_material('Nested',2.,native.rows(),RECIPES,ELEMENTS)['maximum_element_mass_fraction_residual'],1e-15)

    def test_density_fraction_and_atomic_mass_perturbations_fail(self):
        native=Material('Nested');rows=native.rows()
        with self.assertRaisesRegex(ValueError,'density'):compare_material('Nested',2.01,rows,RECIPES,ELEMENTS)
        changed=list(rows);z,a,w=changed[0];changed[0]=(z,a,w+.001)
        z,a,w=changed[1];changed[1]=(z,a,w-.001)
        with self.assertRaisesRegex(ValueError,'mass fractions'):compare_material('Nested',2.,changed,RECIPES,ELEMENTS)
        changed=list(rows);z,a,w=changed[0];changed[0]=(z,a+.001,w)
        with self.assertRaisesRegex(ValueError,'atomic mass'):compare_material('Nested',2.,changed,RECIPES,ELEMENTS)
        bad=copy.deepcopy(RECIPES);bad['Nested']['composition']={'Nested':1.}
        with self.assertRaisesRegex(ValueError,'Cyclic'):resolve_recipe('Nested',bad,ELEMENTS)
        pure=types.SimpleNamespace(IsMixture=lambda:False,GetZ=lambda:29.,GetA=lambda:ELEMENTS['Cu']['A'])
        self.assertEqual(native_fractions(pure),[(29.,ELEMENTS['Cu']['A'],1.)])

    def native_fixture(self,extra=False):
        children=[Volume('known'),Volume('BeamPipe_wall','Beryllium'),Volume('BeamPipe_bore','Vacuum')]
        if extra:children.append(Volume('unexpected_copper'))
        top=Node(Volume('world_volume','Air',children=children))
        manager=types.SimpleNamespace(GetTopNode=lambda:top)
        detector=types.SimpleNamespace(fromXML=lambda path:None,manager=lambda:manager)
        root=types.SimpleNamespace(gROOT=types.SimpleNamespace(SetBatch=lambda value:None,GetVersion=lambda:'FAKE-CONTROL'),
            gSystem=types.SimpleNamespace(Load=lambda path:0),gGeoManager=None)
        dd4hep=types.SimpleNamespace(mm=1.,Volume=lambda volume:volume,
            Detector=types.SimpleNamespace(getInstance=lambda:detector,destroyInstance=lambda:None))
        expected=dict(entities=[dict(name='known',role='passive',material='Copper')],
            shape_probes=[dict(name='known',point_mm=[0,0,0],inside=True,reason='test fixture finite contact')])
        return root,dd4hep,expected

    def test_every_native_solid_including_unexpected_copper_is_audited(self):
        root,dd4hep,expected=self.native_fixture()
        with patch.dict(sys.modules,ROOT=root,dd4hep=dd4hep):
            result=native_audit(Path('fixture.xml'),expected,[],RECIPES,ELEMENTS)
        self.assertEqual(result['errors'],[])
        self.assertEqual(result['solid_placements'],3)
        self.assertEqual(result['world_container_exemptions'],1)
        root,dd4hep,expected=self.native_fixture(extra=True)
        with patch.dict(sys.modules,ROOT=root,dd4hep=dd4hep):
            result=native_audit(Path('fixture.xml'),expected,[],RECIPES,ELEMENTS)
        self.assertTrue(any('Unexpected non-assembly native solid: unexpected_copper' in e for e in result['errors']))
        self.assertTrue(compare_placements({'known':1},{'known':2}))
        self.assertTrue(compare_placements({'known':1},{}))

    def test_probe_is_executed_on_the_actual_shape(self):
        root,dd4hep,expected=self.native_fixture();expected['shape_probes'][0]['point_mm']=[2,0,0]
        with patch.dict(sys.modules,ROOT=root,dd4hep=dd4hep):
            result=native_audit(Path('fixture.xml'),expected,[],RECIPES,ELEMENTS)
        self.assertTrue(any('Finite contact/window probe differs' in e for e in result['errors']))

    def complete_contract(self):
        entities=[dict(name=f'sensor{i}',role='sensitive',material='Copper',ids=dict(system=1,layer=i%54)) for i in range(46682)]
        components=[dict(name=name,provenance=dict(source_hashes={key:'fixture' for key in STRIP_SOURCES}) if name in ('short_barrel','short_endcap') else {}) for name in COMPONENTS]
        probes=[dict(name='sensor0',point_mm=[0,0,0],inside=True,reason=reason) for reason,count in PROBE_COUNTS.items() for _ in range(count)]
        return dict(assembly_source_hashes={key:'fixture' for key in ASSEMBLY_SOURCES},components=components,
            source_hashes={key:{name:'fixture' for name in (filename,'materials.xml','expected.json')} for key,filename in COMPONENTS.items()},
            short_strip_integration=dict(design='DES-043'),historical_short_strips=False,entities=entities,shape_probes=probes)

    def test_empty_or_incomplete_source_and_probe_contracts_fail(self):
        with self.assertRaisesRegex(ValueError,'source coverage'):contract(dict(assembly_source_hashes={},components=[]))
        data=self.complete_contract();contract(data)
        data['shape_probes']=[]
        with self.assertRaisesRegex(ValueError,'probe contract'):contract(data)
        data=self.complete_contract();data['components'][2]['provenance']['source_hashes']={}
        with self.assertRaisesRegex(ValueError,'DES043 source coverage'):contract(data)

    def artifacts(self,root):
        for name in required_xml():
            path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('<fixture name="'+name+'"/>')
        names={'expected.json','components/pixel/barrel/expected.json'}|{f'components/{c}/expected.json' for c in COMPONENTS}
        for name in names:(root/name).write_text('{}')
        return dict(source_hashes={component:{name:sha(root/'components'/component/name) for name in (filename,'materials.xml','expected.json')} for component,filename in COMPONENTS.items()})

    def test_regeneration_detects_xml_tampering_and_missing_component(self):
        with tempfile.TemporaryDirectory() as temporary:
            first=Path(temporary)/'actual';second=Path(temporary)/'fresh'
            expected=self.artifacts(first);self.artifacts(second)
            result=compare_artifacts(first,second,expected,'fixture','fixture')
            self.assertEqual(result['xml_count'],16)
            (first/'tracker.xml').write_text('<fixture><piece name="extra_copper"/></fixture>')
            with self.assertRaisesRegex(ValueError,'byte mismatch'):compare_artifacts(first,second,expected,'fixture','fixture')
            (first/'tracker.xml').write_bytes((second/'tracker.xml').read_bytes())
            (first/'components/short_endcap/materials.xml').unlink()
            with self.assertRaisesRegex(ValueError,'artifact set'):compare_artifacts(first,second,expected,'fixture','fixture')

    def test_expected_record_tampering_is_not_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            first=Path(temporary)/'actual';second=Path(temporary)/'fresh'
            expected=self.artifacts(first);self.artifacts(second)
            (first/'expected.json').write_text('{"extra_material":"Copper"}')
            with self.assertRaises((ValueError,KeyError)):compare_artifacts(first,second,expected,'fixture','fixture')
        record=dict(provenance=dict(generation_source_revision='old',source_hashes={'source.py':'binding'}))
        normalized=expected_metadata(record,'short_endcap','old')
        self.assertEqual(normalized['provenance']['source_hashes'],{'source.py':'binding'})
        with self.assertRaisesRegex(ValueError,'generation revision'):
            expected_metadata(dict(provenance=dict(generation_source_revision='wrong')),'short_endcap','old')

    def test_exact_native_library_binding_rejects_replaced_binary(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);compact=root/'tracker.xml';expected=root/'expected.json'
            libs=[root/f'libFixture{i}.so' for i in range(5)]
            for path in [compact,expected,*libs]:path.write_text('unchanged fixture bytes '+path.name)
            report=dict(status='PASS',execution=dict(revision='fixture',hashes={p.name:sha(p) for p in [compact,expected,*libs]}))
            self.assertEqual(bind_reference(report,compact,expected,libs,'fixture')['status'],'PASS')
            libs[0].write_text('different installed factory')
            with self.assertRaisesRegex(ValueError,'artifact/library differs'):bind_reference(report,compact,expected,libs,'fixture')


if __name__=='__main__':unittest.main()
