"""Pinned source, unit, transform, CSG and fail-closed negative controls."""
import copy
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from tools.muon_dd4hep import export as generator
from tools.muon_dd4hep import validate as audit


class ExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=generator.load_source()
        cls.temp=tempfile.TemporaryDirectory()
        cls.path=Path(cls.temp.name)
        cls.expected=generator.export(cls.path/"first")

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_checked_in_compact_matches_frozen_export(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            generator.export(out)
            for name in ("muon-system.xml", "materials.xml", "expected.json"):
                self.assertEqual((out / name).read_bytes(),
                                 (generator.ROOT / "prototypes/muon/compact" / name).read_bytes())

    def test_deterministic_export_and_exact_inventory(self):
        generator.export(self.path/"second")
        for name in ("muon-system.xml","materials.xml","expected.json"):
            self.assertEqual((self.path/"first"/name).read_bytes(),(self.path/"second"/name).read_bytes())
        self.assertEqual(self.expected["counts"],dict(chambers=936,warm_groups=3,warm_coil_definitions=36,sensitive=0))
        self.assertEqual(sum(self.expected["chamber_counts"].values()),936)
        self.assertEqual(len({e["ids"]["chamber"] for e in self.expected["entities"]}),936)
        audit.verify_manifest(self.expected,self.source,self.path/"first/muon-system.xml")

    def test_all_xml_vertices_and_transforms_preserve_source_metres(self):
        root=ET.parse(self.path/"first/muon-system.xml").getroot()
        panels={p["id"]:p for p in self.source["panels"]}
        def m(node,key):
            text=node.get(key)
            self.assertTrue(text.endswith("*m"))
            return float(text[:-2])
        for node in root.findall(".//chamber"):
            p=panels[node.get("source_id")]
            self.assertEqual([m(node,axis) for axis in "xyz"],p["origin_m"])
            self.assertEqual(m(node,"depth"),p["depth_m"])
            self.assertEqual([[float(node.get(f"a{i}{j}")) for j in range(3)] for i in range(3)],p["basis"])
            vertices=[[m(v,"x"),m(v,"y")] for v in node.findall("vertex")]
            self.assertEqual(vertices,[p["vertices_m"][i] for i in (0,3,2,1)])
        self.assertEqual(len(root.findall(".//chamber")),936)
        self.assertEqual(len(root.findall(".//toroid")),3)
        self.assertFalse(root.findall(".//readout"))
        elements=ET.parse(self.path/"first/materials.xml").getroot().findall("element")
        self.assertGreater(len(elements),90)  # Complete Z table avoids sparse registration failures.
        self.assertTrue({"H","N","O","Ar","U"}.issubset({e.get("name") for e in elements}))

    def test_source_export_refuses_missing_duplicate_or_invalid_panels(self):
        for change in ("missing","duplicate","basis","depth","vertices"):
            source=copy.deepcopy(self.source)
            if change=="missing":source["panels"].pop()
            if change=="duplicate":source["panels"][1]["id"]=source["panels"][0]["id"]
            if change=="basis":source["panels"][0]["basis"][0][0]=1
            if change=="depth":source["panels"][0]["depth_m"]=0
            if change=="vertices":source["panels"][0]["vertices_m"].reverse()
            with self.subTest(change=change),self.assertRaises(ValueError):
                generator.export(self.path/change,source)

    def test_manifest_cannot_substitute_panel_geometry_or_source_identity(self):
        for change in ("source","vertex","id","toroid"):
            expected=copy.deepcopy(self.expected)
            if change=="source":expected["source"]["revision"]="0"*40
            if change=="vertex":expected["entities"][0]["vertices_m"][0][0]+=.01
            if change=="id":expected["entities"][0]["ids"]["chamber"]=2
            if change=="toroid":expected["groups"][0]["configuration"]["corner_radius_m"]+=.01
            with self.subTest(change=change),self.assertRaises(ValueError):
                audit.verify_manifest(expected,self.source,self.path/"first/muon-system.xml")
        compact=self.path/"second/muon-system.xml"
        generator.export(compact.parent)
        compact.write_text(compact.read_text()+"\n")
        with self.assertRaisesRegex(ValueError,"hash mismatch"):
            audit.verify_manifest(self.expected,self.source,compact)

    def native_fixture(self):
        panels={p["id"]:p for p in self.source["panels"]}
        return [dict(name=e["name"],ids=copy.deepcopy(e["ids"]),
                     origin_m=copy.deepcopy(e["origin_m"]),basis=copy.deepcopy(e["basis"]),
                     vertices_m=audit.source_vertices(panels[e["source_id"]]),material="Air",sensitive=False)
                for e in self.expected["entities"]]

    def test_native_chamber_comparison_rejects_identifier_transform_vertex_and_sensitivity_errors(self):
        fixture=self.native_fixture()
        self.assertTrue(audit.compare_chambers(fixture,self.source,self.expected,1e-10)["passed"])
        for change in ("missing","duplicate","origin","basis","vertex","id","sensitive","material"):
            observed=copy.deepcopy(fixture)
            if change=="missing":observed.pop()
            if change=="duplicate":observed[1]=copy.deepcopy(observed[0])
            if change=="origin":observed[0]["origin_m"][0]+=.001
            if change=="basis":observed[0]["basis"][0][0]+=.001
            if change=="vertex":observed[0]["vertices_m"][0][0]+=.001
            if change=="id":observed[0]["ids"]["chamber"]=2
            if change=="sensitive":observed[0]["sensitive"]=True
            if change=="material":observed[0]["material"]="Aluminium"
            with self.subTest(change=change):
                self.assertFalse(audit.compare_chambers(observed,self.source,self.expected,1e-10)["passed"])

    def test_native_csg_comparison_rejects_missing_wrong_sized_or_transformed_piece(self):
        magnetic=self.source["magnetic_configuration"]
        pieces=audit.expected_primitives(magnetic["coil_groups"]["endcap_plus"],magnetic["warm"])
        self.assertEqual(len(pieces),96)
        self.assertTrue(audit.compare_primitives(pieces,pieces,1e-10)["passed"])
        for change in ("missing","dimension","center","basis"):
            observed=copy.deepcopy(pieces)
            if change=="missing":observed.pop()
            if change=="dimension":observed[0]["dimensions"][0]+=.001
            if change=="center":observed[0]["center_m"][0]+=.001
            if change=="basis":observed[0]["basis"][0][0]+=.001
            with self.subTest(change=change):
                self.assertFalse(audit.compare_primitives(observed,pieces,1e-10)["passed"])

    def test_analytic_occupancy_includes_shared_endcap_inner_sleeves(self):
        magnetic=self.source["magnetic_configuration"];warm=magnetic["warm"]
        for key,group in magnetic["coil_groups"].items():
            # Every first-coil outer straight leg is occupied at its centre.
            phi=math.radians(group["phi_offset_deg"])
            r=group["center_r_m"]+group["half_r_m"]
            self.assertTrue(audit.analytic_contains([r*math.cos(phi),r*math.sin(phi),group["center_z_m"]],group,warm))
            self.assertFalse(audit.analytic_contains([0,0,group["center_z_m"]],group,warm))
            points=audit.occupancy_points(group,warm)
            self.assertEqual(points,audit.occupancy_points(group,warm))
            self.assertTrue(any(audit.analytic_contains(p,group,warm) for p in points))
            self.assertTrue(any(not audit.analytic_contains(p,group,warm) for p in points))
        # Midway between two neighbouring inner ECT legs: union occupies shared stock.
        group=magnetic["coil_groups"]["endcap_plus"]
        r=group["center_r_m"]-group["half_r_m"]
        phi=math.radians(group["phi_offset_deg"]+15)
        self.assertTrue(audit.analytic_contains([r*math.cos(phi),r*math.sin(phi),group["center_z_m"]],group,warm))

    def test_missing_runtime_input_writes_failure_report_and_exits_nonzero(self):
        report=self.path/"missing-library.json"
        result=subprocess.run([sys.executable,"-B",str(generator.ROOT/"tools/muon_dd4hep/validate.py"),
            "--compact",str(self.path/"first/muon-system.xml"),
            "--expected",str(self.path/"first/expected.json"),
            "--library",str(self.path/"missing-factory.dylib"),"--output",str(report)],
            capture_output=True,text=True)
        self.assertEqual(result.returncode,1)
        value=json.loads(report.read_text())
        self.assertEqual(value["status"],"FAIL")
        self.assertIn("FileNotFoundError",value["errors"][0])


if __name__=="__main__":
    unittest.main()
