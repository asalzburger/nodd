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
        model,expanded=generator.templates.from_xml(root.find("./detectors/detector"),generator.SYSTEM_ID)
        residual=generator.templates.compare_expansion(expanded,self.expected["entities"],model["templates"])
        self.assertLessEqual(residual,1e-12)
        self.assertEqual(len(expanded),936)
        self.assertEqual(len(model["templates"]),22)
        self.assertEqual(len(model["orbits"]),21)
        self.assertEqual(sum(len(o["rows"]) for o in model["orbits"]),56)
        self.assertEqual(len(model["explicit"]),0)
        self.assertEqual(len(root.findall(".//toroid")),3)
        self.assertFalse(root.findall(".//readout"))
        elements=ET.parse(self.path/"first/materials.xml").getroot().findall("element")
        self.assertGreater(len(elements),90)
        self.assertTrue({"H","N","O","Ar","U"}.issubset({e.get("name") for e in elements}))

    def test_template_reuse_reduction_and_real_longitudinal_recurrences(self):
        model=self.expected["chamber_templates"]
        self.assertEqual([sum(t["kind"]==kind for t in model["templates"]) for kind in ("barrel","endcap")],[15,7])
        self.assertEqual(sum(t["members"] for t in model["templates"]),936)
        self.assertLessEqual(max(t["maximum_shape_residual_m"] for t in model["templates"]),1e-12)
        self.assertEqual(sum(row["count"]>1 for orbit in model["orbits"] for row in orbit["rows"]),6)
        self.assertEqual(sum(orbit["count"]*row["count"] for orbit in model["orbits"] for row in orbit["rows"] if row["count"]>1),288)
        compact=self.path/"first/muon-system.xml"
        self.assertLess(compact.stat().st_size,583236/10)
        self.assertEqual(len(ET.parse(compact).getroot().findall(".//vertex")),88)
        self.assertTrue(any(t["name"]=="B15" and t["members"]==48 for t in model["templates"]))

    def test_expansion_rejects_bad_templates_and_recurrences(self):
        for change in ("template_ref","template_duplicate","template_depth","template_vertex","count_zero","missing","duplicate_id","phase","pitch","z_pitch","pattern","side"):
            model=copy.deepcopy(self.expected["chamber_templates"])
            orbit=model["orbits"][0];row=orbit["rows"][0]
            if change=="template_ref":row["template"]="does_not_exist"
            if change=="template_duplicate":model["templates"].append(copy.deepcopy(model["templates"][0]))
            if change=="template_depth":model["templates"][0]["depth_m"]=0
            if change=="template_vertex":model["templates"][0]["vertices_m"].reverse()
            if change=="count_zero":orbit["count"]=0
            if change=="missing":orbit["count"]-=1
            if change=="duplicate_id":row["chamber_phi_step"]=0
            if change=="phase":orbit["phi0"]=float("nan")
            if change=="pitch":orbit["dphi"]=0
            if change=="z_pitch":row["dz_m"]=0
            if change=="pattern":row["source_pattern"]="B1/F{bad}/Z{z:02d}"
            if change=="side":orbit["side"]=1
            with self.subTest(change=change),self.assertRaises(ValueError):
                generator.templates.expand(model,generator.SYSTEM_ID)
        # A finite but changedphase/count/pitch must fail source equivalence too.
        for field in ("phi0","dphi"):
            model=copy.deepcopy(self.expected["chamber_templates"])
            model["orbits"][0][field]+=.001
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,"mismatch|differs"):
                generator.templates.compare_expansion(generator.templates.expand(model,generator.SYSTEM_ID),self.expected["entities"],model["templates"])
        model=copy.deepcopy(self.expected["chamber_templates"])
        expanded=generator.templates.expand(model,generator.SYSTEM_ID)
        model["orbits"]=[];model["explicit"]=expanded
        model["explicit"][0]["basis"][0][0]=1
        with self.assertRaisesRegex(ValueError,"basis"):
            generator.templates.expand(model,generator.SYSTEM_ID)

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

    def test_actual_xml_semantics_are_audited_after_rehashing(self):
        for change in ("template_ref","count","missing_row","duplicate_id","phase","pitch","z_pitch","unit","template_vertex"):
            directory=self.path/("xml_"+change)
            expected=generator.export(directory)
            path=directory/"muon-system.xml"
            root=ET.parse(path).getroot()
            orbit=root.find(".//chamber_orbit");row=orbit.find("row")
            if change=="template_ref":row.set("template","B99")
            if change=="count":orbit.set("count","0")
            if change=="missing_row":orbit.remove(row)
            if change=="duplicate_id":row.set("chamber_phi_step","0")
            if change=="phase":orbit.set("phi0","0.001*rad")
            if change=="pitch":orbit.set("dphi","0.001*rad")
            if change=="z_pitch":row.set("dz","0*m")
            if change=="unit":orbit.set("radius","5200*mm")
            if change=="template_vertex":root.find(".//chamber_template/vertex").set("x","-0.6*m")
            generator.write_xml(path,root)
            # Rehash intentionally: this control must reach the semantic audit.
            expected["exported_sha256"][path.name]=generator.sha(path.read_bytes())
            with self.subTest(change=change),self.assertRaises(ValueError):
                audit.verify_manifest(expected,self.source,path)

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
        return [dict(name=e["name"],template=e["template"],ids=copy.deepcopy(e["ids"]),
                     origin_m=copy.deepcopy(e["origin_m"]),basis=copy.deepcopy(e["basis"]),
                     vertices_m=audit.source_vertices(panels[e["source_id"]]),material="Air",sensitive=False)
                for e in self.expected["entities"]]

    def test_native_chamber_comparison_rejects_identifier_transform_vertex_and_sensitivity_errors(self):
        fixture=self.native_fixture()
        self.assertTrue(audit.compare_chambers(fixture,self.source,self.expected,1e-10)["passed"])
        for change in ("missing","duplicate","origin","basis","vertex","id","template","sensitive","material"):
            observed=copy.deepcopy(fixture)
            if change=="missing":observed.pop()
            if change=="duplicate":observed[1]=copy.deepcopy(observed[0])
            if change=="origin":observed[0]["origin_m"][0]+=.001
            if change=="basis":observed[0]["basis"][0][0]+=.001
            if change=="vertex":observed[0]["vertices_m"][0][0]+=.001
            if change=="id":observed[0]["ids"]["chamber"]=2
            if change=="template":observed[0]["template"]="B99"
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
