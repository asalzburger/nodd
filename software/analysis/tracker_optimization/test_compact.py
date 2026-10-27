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


def attachments(root):
    """Small copy of the retained four-wall/three-sector attachment contract."""
    for sy,sign,label in ((2,-1,"N"),(3,1,"P")):
        detector=root.find(f'./detectors/detector[@id="{sy}"]')
        datums=[615.,795.,1046.]
        for layer,z in enumerate(datums,1):
            for sector in range(3):
                E.SubElement(detector,"part",name=f"collector{label}{layer}_{sector}",shape="sector",
                    material=f"mix{layer}",z=f"{sign*(z+36.7)}*mm",dz="50*mm",rmin="28.8*mm",rmax="190*mm",angle=f"{math.pi/2}*rad")
        cursor=611.;spans=[]
        for z in datums:spans.append((cursor,z-3.15));cursor=z+3.15
        spans.append((cursor,1100.))
        for station in range(3):
            for i,(lo,hi) in enumerate(spans):
                for edge,a,b,angle in (("inner",223.7,224.1,.035), ("outer",231.3,231.7,.035),
                                       ("left",224.1,231.3,.00175),("right",224.1,231.3,.00175)):
                    E.SubElement(detector,"part",name=f"rail{label}_{station}_{i}_{edge}",shape="sector",material="CFRP",
                        z=f"{sign*(lo+hi)/2}*mm",dz=f"{hi-lo}*mm",rmin=f"{a}*mm",rmax=f"{b}*mm",angle=f"{angle}*rad")
        for name in ("carrier","flange","trunk","bypass","rear"):
            E.SubElement(detector,"part",name=name+label,z="800*mm",dz="100*mm",shape="sector",
                         material="fixed",rmin="192*mm",rmax="231.7*mm",angle="1*rad")
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

    def test_collectors_follow_signed_station_and_added_donor(self):
        root=attachments(fixture());E.ElementTree(root).write(self.path)
        fixed={n.get("name"):E.tostring(n) for n in root.findall('./detectors/detector/part')
               if n.get("name").startswith(("carrier","flange","trunk","bypass","rear"))}
        variant={"schema_version":1,"id":"attachments","pixel_disks_abs_z_mm":{"1":700.},
            "additional_pixel_disk":{"abs_z_mm":900.,"donor_layer":2,"layer_id":10}}
        tree,audit=transform(self.path,variant)
        for sy,sign,label in ((2,-1,"N"),(3,1,"P")):
            detector=tree.getroot().find(f'./detectors/detector[@id="{sy}"]')
            for sector in range(3):
                moved=detector.find(f'part[@name="collector{label}1_{sector}"]')
                added=detector.find(f'part[@name="collector{label}10_{sector}"]')
                self.assertAlmostEqual(length(moved,"z"),sign*736.7)
                self.assertAlmostEqual(length(added,"z"),sign*936.7)
                self.assertEqual(added.get("material"),"mix2")
                self.assertEqual(added.get("dz"),"50*mm")
            for node in detector.findall("part"):
                if node.get("name") in fixed:self.assertEqual(E.tostring(node),fixed[node.get("name")])
        for item in audit["endcap_attachments"]:
            self.assertEqual(item["collector_stations_before"],3)
            self.assertEqual(item["collector_stations_after"],4)
            self.assertEqual(item["added_collector_donor"],2)

    def test_rails_keep_crosssection_span_and_recut_every_disc_slot(self):
        E.ElementTree(attachments(fixture())).write(self.path)
        variant={"schema_version":1,"id":"rails","pixel_disks_abs_z_mm":{"1":700.},
            "additional_pixel_disk":{"abs_z_mm":900.,"donor_layer":2,"layer_id":10}}
        tree,audit=transform(self.path,variant)
        for item in audit["endcap_attachments"]:
            self.assertEqual(item["rail_fixed_abs_z_span_mm"],[611.,1100.])
            self.assertAlmostEqual(item["rail_slot_width_mm"],6.3)
            for datum in (700.,795.,900.,1046.):
                self.assertFalse(any(a<datum<b for a,b in item["rail_spans_abs_z_mm"]))
            expected=item["rail_volume_mm3_before"]*(489.-4*6.3)/(489.-3*6.3)
            self.assertAlmostEqual(item["rail_volume_mm3_after"],expected,places=6)
            self.assertGreater(item["material_volume_change_mm3"]["mix2"],0.)
            self.assertLess(item["material_volume_change_mm3"]["CFRP"],0.)

    def test_noop_with_collectors_and_rails_remains_byte_identical(self):
        E.ElementTree(attachments(fixture())).write(self.path)
        output=Path(self.tmp.name)/"same.xml"
        export(self.path,{"schema_version":1,"id":"baseline"},output)
        self.assertEqual(output.read_bytes(),self.path.read_bytes())


if __name__=="__main__":unittest.main()
