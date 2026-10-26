import json
import os
import sys
import ctypes
import gzip
from pathlib import Path
import tempfile
import unittest
from runtime import load_campaign, material_map


class RuntimeControls(unittest.TestCase):
    def test_frozen_map_publish_and_conflict_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=root/"map.json.gz";target=root/"expanded.json"
            with gzip.open(source,"wb") as stream:stream.write(b'{"material":1}')
            self.assertEqual(material_map(source,target).read_bytes(),b'{"material":1}')
            self.assertEqual(material_map(source,target).read_bytes(),b'{"material":1}')
            with gzip.open(source,"wb") as stream:stream.write(b'{"material":2}')
            with self.assertRaisesRegex(ValueError,"conflicts"):
                material_map(source,target)

    def test_configuration_guards(self):
        source=Path(__file__).with_name("campaign.json")
        baseline=json.loads(source.read_text())
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"campaign.json"
            for field,value in (("particles_per_event",2),("field_Bz_T",float("nan")),
                                ("eta_range",[1.,-1.])):
                config=dict(baseline);config[field]=value;path.write_text(json.dumps(config))
                with self.assertRaises(ValueError):load_campaign(path)
            config=json.loads(source.read_text());config["digitization"]["long_strip_measured_coordinates"]=2
            path.write_text(json.dumps(config))
            with self.assertRaisesRegex(ValueError,"one measured"):load_campaign(path)
            self.assertEqual(load_campaign(source)["field_Bz_T"],3.)

@unittest.skipUnless(os.environ.get("NODD_TRUTH_NATIVE_DIR"),"Native ACTS runtime not selected")
class NativeInterfaceControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ctypes.CDLL("libDDG4.dylib",mode=ctypes.RTLD_GLOBAL)
        import acts
        import acts.examples
        sys.path.insert(0,os.environ["NODD_TRUTH_NATIVE_DIR"])
        import nodd_truth_tracking
        cls.native=nodd_truth_tracking

    def test_root_inventory_uses_latest_cycle(self):
        import ROOT
        from array import array
        from runtime import root_inventory
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"cycles.root"
            output=ROOT.TFile(str(path),"RECREATE")
            tree=ROOT.TTree("measurements","cycle control")
            value=array("i",[1]);tree.Branch("value",value,"value/I")
            tree.Fill();tree.Write();tree.Fill();tree.Write();output.Close()
            self.assertEqual(root_inventory(ROOT,path)["measurements"]["entries"],2)

    def test_direct_simhit_index_and_dedup(self):
        n=self.native
        self.assertEqual(n.order_measurements([0,1,2],{0:5,1:0,2:3},[3.,0.,0.,2.,0.,1.]),[0,2,1])
        self.assertEqual(n.order_measurements([1,0,1],{0:1,1:0},[2.,1.]),[0,1])

    def test_unique_associations_preserve_distinct_labels(self):
        self.assertEqual(self.native.unique_associations([(0,10),(0,10),(0,20),(1,10)]),
                         [(0,10),(0,20),(1,10)])

    def test_cluster_variance_exact_tail_and_zero_guard(self):
        n=self.native
        self.assertEqual(n.cluster_variance([.1,.02],1),.1*.1)
        self.assertEqual(n.cluster_variance([.1,.02],9),.02*.02)
        with self.assertRaises(ValueError):n.cluster_variance([.1],0)

if __name__=="__main__":unittest.main()
