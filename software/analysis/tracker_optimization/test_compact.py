import copy
import math
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as E
from compact import transform,export,length


def fixture():
    root=E.Element("lccdd");det=E.SubElement(root,"detectors")
    pipe=E.SubElement(det,"detector",id="0");E.SubElement(pipe,"dimensions",rmax="27.8*mm")
    barrel=E.SubElement(det,"detector",id="1")
    for layer_id,r in enumerate((34.,60.,106.,182.),1):
        layer=E.SubElement(barrel,"layer",id=str(layer_id))
        for i in (0,1):
            s=E.SubElement(layer,"stave",id=str(i),name=f"L{layer_id}s{i}",phi=f"{math.pi*i}*rad",radius=f"{r+(2*i-1)}*mm",offset_u="0*mm",length="100*mm")
            E.SubElement(s,"slab",name="support",w="1*mm",width="2*mm",thickness="0.1*mm",center_y="0*mm")
            m=E.SubElement(s,"module",name=f"m{i}",id=str(i),z="0*mm")
            E.SubElement(m,"sensor",u="0*mm",width="2*mm",length="10*mm",thickness="0.15*mm")
            E.SubElement(layer,"foot",name=f"f{i}",phi=f"{math.pi*i}*rad",back_radius=f"{r+1}*mm",outer_radius=f"{r+4}*mm",width="0.2*mm",length="1*mm",z="0*mm")
            E.SubElement(barrel,"service",name=f"cable_A-pixel-B{layer_id}-c{i:02d}-test",rmin=f"{r+6}*mm",rmax=f"{r+7}*mm",phi=f"{math.pi*i}*rad",phi_width="0.1*rad",length="10*mm")
        E.SubElement(layer,"ring",rmin=f"{r+4}*mm",rmax=f"{r+5}*mm",length="1*mm",z="0*mm")
    for sy,sign in ((2,-1),(3,1)):
        ec=E.SubElement(det,"detector",id=str(sy))
        for i,z in enumerate((615.,795.,1046.),1):
            disc=E.SubElement(ec,"disc",id=str(i),name=f"d{sy}_{i}",z=f"{sign*z}*mm")
            E.SubElement(disc,"module",name="module",id="0",z="5.75*mm")
    return root


class CompactControls(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"source.xml";E.ElementTree(fixture()).write(self.path)

    def test_noop_bytes_and_fixed_inputs(self):
        output=Path(self.tmp.name)/"candidate.xml"
        export(self.path,{"schema_version":1,"id":"baseline"},output)
        self.assertEqual(self.path.read_bytes(),output.read_bytes())

    def test_radius_moves_complete_structures_and_conserves_cable_volume(self):
        variant={"schema_version":1,"id":"r32","pixel_barrel":{"1":{"radius_mm":32.}}}
        tree,audit=transform(self.path,variant);r=tree.getroot()
        old=E.parse(self.path).getroot()
        before=old.find('./detectors/detector[@id="1"]/layer[@id="1"]')
        after=r.find('./detectors/detector[@id="1"]/layer[@id="1"]')
        self.assertEqual([length(s,"radius") for s in after.findall("stave")],[31.,33.])
        for a,b in zip(before.findall("stave"),after.findall("stave")):
            self.assertEqual(E.tostring(a.find("module")),E.tostring(b.find("module")))
            self.assertEqual(E.tostring(a.find("slab")),E.tostring(b.find("slab")))
        self.assertEqual(length(after.find("ring"),"rmax")-length(after.find("ring"),"rmin"),1.)
        for a,b in zip(before.findall("foot"),after.findall("foot")):
            self.assertAlmostEqual(length(a,"outer_radius")-length(a,"back_radius"),length(b,"outer_radius")-length(b,"back_radius"))
        a=old.find('./detectors/detector[@id="1"]/service');b=r.find('./detectors/detector[@id="1"]/service[@name="'+a.get('name')+'"]')
        vol=lambda n:(length(n,"rmax")**2-length(n,"rmin")**2)*length(n,"phi_width")*length(n,"length")/2
        self.assertAlmostEqual(vol(a),vol(b),places=10)

    def test_count_and_added_pair_preserve_local_coordinates(self):
        variant={"schema_version":1,"id":"count","pixel_barrel":{"1":{"staves":4}},
                 "additional_pixel_disk":{"abs_z_mm":900.,"donor_layer":1,"layer_id":10}}
        root,audit=transform(self.path,variant);root=root.getroot()
        ss=root.findall('./detectors/detector[@id="1"]/layer[@id="1"]/stave')
        self.assertEqual([s.get("id") for s in ss],["0","1","2","3"])
        self.assertEqual(audit["inventory_ratios"]["1:1"],2.)
        for sy,sign in ((2,-1),(3,1)):
            disc=root.find(f'./detectors/detector[@id="{sy}"]/disc[@id="10"]')
            self.assertEqual(length(disc,"z"),sign*900.)
            self.assertEqual(length(disc.find("module"),"z"),5.75)

    def test_pipe_id_collector_and_ring_collisions_fail(self):
        variants=[{"pixel_barrel":{"1":{"radius_mm":27.}}},{"pixel_barrel":{"1":{"staves":66}}},
            {"pixel_barrel":{"2":{"radius_mm":38.}}},
            {"additional_pixel_disk":{"abs_z_mm":800.,"donor_layer":1,"layer_id":10}},
            {"pixel_disks_abs_z_mm":{"1":600.}}]
        for change in variants:
            with self.subTest(change=change),self.assertRaises(ValueError):
                transform(self.path,{"schema_version":1,"id":"bad",**change})


if __name__=="__main__":unittest.main()
