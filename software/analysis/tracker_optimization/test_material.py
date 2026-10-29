import copy
import importlib
import os
from pathlib import Path
import sys
import unittest
from material import transport,remap_errors,select_candidate


class FakeHelper:
    def budget(self,slab):return {"X0":slab["thickness"]/100.,"L0":slab["thickness"]/200.,"areal_mass_g_mm2":slab["thickness"]*.01}


class MaterialControls(unittest.TestCase):
    def setUp(self):
        role={"kind":"sensitive_layer","system":1,"layer":1,"detector":"pixel","side":"after"}
        self.surface={"geometry_id":1,"material_key":"key1","type":"cylinder","rz_segment_mm":[[10.,-1.],[10.,1.]],"roles":[role]}
        self.manifest={"surfaces":[self.surface]}
        self.material={"type":"binned","mappingType":"Default","mapMaterial":True,
            "binUtility":{"binningdata":[{"value":"AxisPhi","bins":1,"min":-3.14,"max":3.14},{"value":"AxisZ","bins":1,"min":-1.,"max":1.}],"transform":None},
            "data":[[{"material":[100.,200.,12.,6.,.001],"thickness":2.}]]}
        self.mapping={"KeyedSurfaces":[{"geometry_id":1,"key":"key1","material":self.material}],"Surfaces":{},"Volumes":{}}

    def test_noop_material_is_semantically_identical(self):
        result,_=transport(self.manifest,copy.deepcopy(self.manifest),self.mapping,{},FakeHelper())
        self.assertEqual(result,self.mapping)

    def test_radius_and_count_inventory_scaling_and_new_keys(self):
        target=copy.deepcopy(self.manifest);s=target["surfaces"][0]
        s.update(geometry_id=9,material_key="candidate9",rz_segment_mm=[[20.,-1.],[20.,1.]])
        result,audit=transport(self.manifest,target,self.mapping,{},FakeHelper())
        self.assertEqual(result["KeyedSurfaces"][0]["key"],"candidate9")
        self.assertEqual(result["KeyedSurfaces"][0]["material"]["data"][0][0]["thickness"],1.)
        result,_=transport(self.manifest,target,self.mapping,{},FakeHelper(),{"1:1":2.})
        self.assertEqual(result["KeyedSurfaces"][0]["material"]["data"][0][0]["thickness"],2.)

    def test_ambiguous_shared_and_missing_roles_fail(self):
        old=copy.deepcopy(self.manifest);old["surfaces"][0]["roles"].append({"kind":"gap_cylinder","volume":"gap","side":"inner"})
        with self.assertRaisesRegex(ValueError,"Conflicting"):
            transport(old,copy.deepcopy(old),self.mapping,{},FakeHelper(),{"1:1":2.})
        target=copy.deepcopy(self.manifest);target["surfaces"][0]["roles"][0]["layer"]=2
        with self.assertRaisesRegex(ValueError,"Missing"):
            transport(self.manifest,target,self.mapping,{},FakeHelper())

    def test_logical_error_remap_and_explicit_added_donor(self):
        old={"volumes":[{"name":"System2Layer1","geometry_id":25<<56}]}
        new={"volumes":[{"name":"System2Layer1","geometry_id":26<<56},{"name":"System2Layer10","geometry_id":27<<56}]}
        table={"entries":[{"volume":25,"value":[{"index":0,"rms":[.01,.02]}]}]}
        result=remap_errors(table,old,new,{(2,10):(2,1)})
        self.assertEqual([e["volume"] for e in result["entries"]],[26,27])
        self.assertEqual(result["entries"][0]["value"],result["entries"][1]["value"])
        with self.assertRaises(ValueError):remap_errors(table,old,new,{})

    def test_nonuniform_radial_profile_uses_per_bin_area_jacobian(self):
        old=copy.deepcopy(self.manifest);old["surfaces"][0].update(type="disc",rz_segment_mm=[[1.,10.],[3.,10.]])
        mapping=copy.deepcopy(self.mapping);m=mapping["KeyedSurfaces"][0]["material"]
        m["binUtility"]["binningdata"][1].update(value="AxisR",bins=2,min=1.,max=3.)
        m["data"]=[[{**m["data"][0][0],"thickness":1.}],[{**m["data"][0][0],"thickness":10.}]]
        target=copy.deepcopy(old);target["surfaces"][0]["rz_segment_mm"]=[[2.,20.],[4.,20.]]
        result,audit=transport(old,target,mapping,{},FakeHelper())
        slabs=result["KeyedSurfaces"][0]["material"]["data"]
        self.assertAlmostEqual(slabs[0][0]["thickness"],3/5)
        self.assertAlmostEqual(slabs[1][0]["thickness"],50/7)
        self.assertTrue(all(abs(v)<1.e-12 for v in audit[0]["relative_inventory_residuals"].values()))
        self.assertIsNone(audit[0]["thickness_scale"])

    def test_native_homogeneous_area_mixture(self):
        path=Path(os.environ.get("NODD_OPT_NATIVE_DIR",Path(__file__).resolve().parents[3]/"build/tracker-resolution-optimization/native"))
        if not list(path.glob("nodd_tracker_material*.so")):self.skipTest("Task native helper not built")
        sys.path.insert(0,str(path))
        try:helper=importlib.import_module("nodd_tracker_material")
        except ImportError:self.skipTest("Task native helper requires activated ACTS runtime")
        a={"material":[100.,200.,12.,6.,.001],"thickness":2.}
        b={**a,"thickness":4.}
        slab=helper.homogenize([a,b],[1.,3.])
        self.assertEqual(slab["thickness"],3.5)
        self.assertAlmostEqual(helper.budget(slab)["X0"],.035,places=7)


if __name__=="__main__":unittest.main()
