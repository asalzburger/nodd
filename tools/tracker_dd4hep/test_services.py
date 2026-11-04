import math
import unittest
import xml.etree.ElementTree as ET
from services import reconcile


class SharedServices(unittest.TestCase):
    def fixture(self, payload=2):
        doc = ET.Element("lccdd")
        detectors = ET.SubElement(doc, "detectors")
        barrel = ET.SubElement(detectors, "detector", name="ShortStripBarrel")
        endcap = ET.SubElement(detectors, "detector", name="ShortStripEndcap")
        entities = []
        for parent, name, a, b in (
            (barrel, "short_barrel_trunk_0", 0, 10),
            (endcap, "short_endcap_trunk_0", 5, 10),
        ):
            ET.SubElement(
                parent,
                "piece",
                name=name,
                role="service_cell",
                kind="sector",
                material=name,
                u="0*mm",
                v="0*mm",
                w=f"{(a+b)/2}*mm",
                rmin="10*mm",
                rmax="11*mm",
                start="0*rad",
                angle="1*rad",
                length=f"{b-a}*mm",
            )
            entities.append(
                dict(
                    name=name,
                    role="service_cell",
                    material=name,
                    constituent_volumes_mm3={"Copper": payload},
                    volume_mm3=10.5 * (b - a),
                )
            )
        recipes = {"Copper": {"density_g_cm3": 8.96}, "Air": {"density_g_cm3": 0.0012}}
        return doc, ET.Element("materials"), entities, recipes

    def test_split_and_payload_conservation(self):
        doc, materials, entities, recipes = self.fixture()
        result, actions = reconcile(doc, materials, entities, recipes)
        self.assertEqual(len(result), 2)
        self.assertEqual([e["center_mm"][2] for e in result], [2.5, 7.5])
        self.assertAlmostEqual(
            sum(e["constituent_volumes_mm3"]["Copper"] for e in result), 4
        )
        self.assertAlmostEqual(sum(e["volume_mm3"] for e in result), 105)
        self.assertEqual(
            actions[-1]["payload_before_mm3"], actions[-1]["payload_after_mm3"]
        )
        for recipe in recipes.values():
            if "composition" in recipe:
                self.assertAlmostEqual(sum(recipe["composition"].values()), 1)

    def test_excess_payload_fails(self):
        with self.assertRaisesRegex(ValueError, "exceeds physical corridor"):
            reconcile(*self.fixture(1000))


if __name__ == "__main__":
    unittest.main()


class Des043SharedServices(unittest.TestCase):
    def fixture(self):
        import json
        from pathlib import Path
        root=Path(__file__).resolve().parents[2]
        s=json.loads((root/'detector/config/short-strip-des043.json').read_text())
        c=json.loads((root/s['input']).read_text())
        doc=ET.fromstring('<lccdd><detectors><detector name="ShortStripBarrel"/><detector name="ShortStripEndcap"/><detector name="LongStripBarrel"/></detectors></lccdd>')
        barrel=doc.find(".//detector[@name='ShortStripBarrel']")
        # Exact source staves per layer: the fixture uses the physical layout,
        # without needing to generate every passive module for service checks.
        import importlib.util
        spec=importlib.util.spec_from_file_location('service_fixture_barrel',root/'tools/short_strip_barrel/model.py')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        layout=m.build(m.load())
        for info in layout['layers']:
            layer=ET.SubElement(barrel,'layer',id=str(info['layer']))
            for stave in [x for x in layout['staves'] if x['layer']==info['layer']]:
                ET.SubElement(layer,'stave',id=str(stave['stave']),radius=f"{stave['radius_mm']}*mm")
        endcap=doc.find(".//detector[@name='ShortStripEndcap']")
        old=json.loads((root/'tools/short_strip_endcap/inputs.json').read_text())
        entities=[]
        for side in (1,-1):
            for station,z in enumerate(old['disc_z_mm']):
                layer=station+(0 if side>0 else 6)
                ET.SubElement(endcap,'disc',id=str(layer),side=str(side),z=f'{z}*mm')
                for petal in range(12):
                    entities.extend(dict(name=f'sensor{layer}_{petal}_{j}',role='sensitive',component='short_endcap',ids=dict(layer=layer,petal=petal)) for j in range(33))
        for parent,name in [(barrel,'short_barrel_collector_legacy_wall0'),(barrel,'short_barrel_trunk_legacy'),(endcap,'short_endcap_fan_legacy'),(endcap,'short_endcap_trunk_legacy_wall0'),(doc.find(".//detector[@name='LongStripBarrel']"),'long_barrel_trunk_legacy')]:
            ET.SubElement(parent,'piece',name=name)
            entities.append(dict(name=name,role='service_cell'))
        recipes={k:dict(density_g_cm3=v) for k,v in dict(Copper=8.96,Polyimide=1.42,Air=.0012,Titanium=4.51,CO2=1.,Silica=2.2,Aluminium=2.7).items()}
        return doc,ET.Element('materials'),entities,recipes,s,c

    def test_new_routes_conserved_and_every_cell_wall_disjoint(self):
        import importlib.util
        from pathlib import Path
        root=Path(__file__).resolve().parents[2]
        spec=importlib.util.spec_from_file_location('new_services',root/'tools/short_strip_redesign/integrated_services.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        doc,mat,entities,recipes,s,c=self.fixture()
        result,actions=module.replace(doc,mat,entities,recipes,s,c)
        action=actions[0]
        self.assertEqual(action['route_totals'],dict(power_feeds=1008,optical_groups=1584,leaf_loops=864,physical_boards=720,bulk_pipe_pairs_at_both_end_handoffs=136,leaf_ports=1728))
        self.assertEqual(len(action['removed_names']),5)
        self.assertFalse(any(p.get('name','').endswith('legacy') or 'legacy_wall' in p.get('name','') for p in doc.findall('.//piece')))
        for material,value in action['allocated_payload_mm3'].items():
            self.assertAlmostEqual(value/action['new_route_payload_oracle_mm3'][material],1.,places=10)
        spine_litres=dict(Copper=45.803085872,Polyimide=42.954663886,Air=18.194454936,Silica=15.662981482,Titanium=14.724403520,CO2=27.812762204)
        for material,value in spine_litres.items():
            self.assertAlmostEqual(action['spine_only_payload_mm3'][material]/1e6,value,places=8)
        final=[r for r in action['ledger'] if r['joined_stations']==6]
        self.assertEqual(max(r['power_feeds'] for r in final),43)
        self.assertEqual(max(r['optical_groups'] for r in final),68)
        self.assertEqual(max(r['bulk_pipe_pairs'] for r in final),6)
        placed=[e for e in result if e.get('component')=='shared_short_services']
        for index,first in enumerate(placed):
            for second in placed[index+1:]:
                if (first['side'],first['sector'])!=(second['side'],second['sector']):continue
                a,b=first['bounds_rz_mm'],second['bounds_rz_mm']
                self.assertFalse(min(a[1],b[1])-max(a[0],b[0])>1e-9 and min(a[3],b[3])-max(a[2],b[2])>1e-9,(first['name'],second['name']))
        self.assertTrue(any(e.get('source_petal')==11 and e['side']==-1 and e['sector']==0 for e in placed))
        self.assertTrue(all(e['constituent_volumes_mm3']['Copper']<e['volume_mm3'] for e in placed if e['role']=='service_cell'))

    def test_oversized_cable_and_old_handoff_fail(self):
        import importlib.util
        from pathlib import Path
        root=Path(__file__).resolve().parents[2]
        spec=importlib.util.spec_from_file_location('adverse_services',root/'tools/short_strip_redesign/integrated_services.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        doc,mat,entities,recipes,s,c=self.fixture();c['power_cable_OD_mm']=10.
        with self.assertRaisesRegex(ValueError,'packing fails'):module.replace(doc,mat,entities,recipes,s,c)
        doc,mat,entities,recipes,s,c=self.fixture();c['collector_mm'][1]=750.
        with self.assertRaisesRegex(ValueError,'handoff'):module.replace(doc,mat,entities,recipes,s,c)
