import unittest
from material import select_candidate


class RuntimeControls(unittest.TestCase):
    def test_only_added_disk_material_changes_to_downstream(self):
        geometry={"volumes":[],"portals":[]}
        original={"surfaces":[],"counts":{}}
        for sy,sign in ((2,-1),(3,1)):
            ids=[]
            for j,z in enumerate((894.*sign,906.*sign)):
                identity=sy*10+j;ids.append(identity)
                geometry["portals"].append({"surface_id":identity,"geometry_id":identity,"type":"disc","z_mm":z,"rz_segment_mm":[[30.,z],[180.,z]],"owners":[]})
            geometry["volumes"].append({"name":f"System{sy}Layer10","portal_surface_ids":ids,"z_min_mm":min(894.*sign,906.*sign),"z_max_mm":max(894.*sign,906.*sign)})
            original["surfaces"].append({"geometry_id":ids[0],"roles":[{"kind":"sensitive_layer","system":sy,"layer":10,"side":"before"}]})
        variant={"additional_pixel_disk":{"layer_id":10}}
        result=select_candidate(geometry,{},variant,lambda g,c:original)
        self.assertEqual(len(result["surfaces"]),2)
        for s in result["surfaces"]:
            self.assertEqual(s["roles"][0]["side"],"after")
            self.assertEqual(abs(s["rz_segment_mm"][0][1]),906.)
            self.assertEqual(s["bins"],{"phi":1,"r":1})


if __name__=="__main__":unittest.main()
