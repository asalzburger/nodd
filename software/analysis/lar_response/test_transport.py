"""Controls for LAr compact extraction, physical cell membership and run audits."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location("lar_transport", Path(__file__).with_name("transport.py"))
t = importlib.util.module_from_spec(spec); spec.loader.exec_module(t)


def encode(fields, descriptor):
    out = 0; offset = 0
    for entry in descriptor.split(","):
        key, count = entry.split(":"); count = int(count); bits = abs(count)
        out |= (fields.get(key, 0) & ((1 << bits)-1)) << offset; offset += bits
    return out


def compact():
    return ET.ElementTree(ET.fromstring('''<lccdd>
      <includes><gdmlFile ref="materials.xml"/></includes>
      <readouts>
        <readout name="TrackerHits"/>
        <readout name="LArBarrelHits"><id>system:8,plane:11,layer:4,gap:1,theta:-12</id>
          <segmentation planes="1536" phi_merge="2" reference_table_mm="0 -4 1 2 3 1 8 4 5 6"/>
        </readout>
        <readout name="LArEndcapHits"><id>system:8,side:2,wheel:2,plane:11,gap:1,rho:6,z:4</id>
          <segmentation reference_table_mm="0 0 0 1 2 3 2 33 9 4 5 6"
            wheel_table_mm="410 764 384 10 774 1460 720 14 1470 2790 1360 34"/>
        </readout>
      </readouts>
      <detectors>
        <detector id="0" name="BeamPipe" readout="TrackerHits"/>
        <detector id="7" name="Tracker" readout="TrackerHits"/>
        <detector id="10" name="LArBarrel" readout="LArBarrelHits"><piece role="sensitive" material="LAr" x="2"/></detector>
        <detector id="11" name="LArEndcaps" readout="LArEndcapHits"><piece role="service" material="Steel" x="3"/></detector>
      </detectors>
    </lccdd>'''))


def worker(thread=0, cap=5.):
    volume = dict(name="gap", density_g_cm3=1.396, Birks_mm_per_MeV=0.,
                  max_step_mm=5. if cap else None, native_max_step_mm=None,
                  numeric_cap_applied=bool(cap))
    return dict(thread_id=thread, events=3, status="complete", maps_initialized_serially=True, maximum_abs_magnetic_field_tesla=0,
                requested_max_step_mm=cap, region_cuts=[dict(mm=[.7]*4)],
                sensitive_lar={role:dict(logical_volumes=1, volumes=[deepcopy(volume)]) for role in t.DETECTORS})


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.inventory = t.compile_inventory(t.cell_inventory(t.ecal_only(compact()).getroot()))

    def test_extraction_preserves_physical_lar_nodes(self):
        before = compact(); after = t.ecal_only(before)
        self.assertEqual([int(d.get('id')) for d in before.findall('detectors/detector')],[0,7,10,11])
        self.assertEqual([int(d.get('id')) for d in after.findall('detectors/detector')],[10,11])
        for a,b in zip(before.findall('detectors/detector')[2:],after.findall('detectors/detector')):
            self.assertEqual(ET.tostring(a),ET.tostring(b))
        self.assertEqual({r.get('name') for r in after.findall('readouts/readout')},set(t.COLLECTIONS))

    def test_extraction_rejects_fields_and_unexpected_roots(self):
        tree=compact(); ET.SubElement(tree.getroot(),'fields')
        with self.assertRaisesRegex(ValueError,'field'):t.ecal_only(tree)
        tree=compact();tree.findall('detectors/detector')[0].set('id','12')
        with self.assertRaisesRegex(ValueError,'Unexpected detector'):t.ecal_only(tree)

    def test_extraction_requires_both_complete_roots(self):
        tree=compact();tree.getroot().find('detectors').remove(tree.findall('detectors/detector')[-1])
        with self.assertRaisesRegex(ValueError,'complete LAr'):t.ecal_only(tree)

    def test_extraction_rejects_readout_and_material_substitution(self):
        tree=compact();tree.findall('detectors/detector')[-1].set('readout','other')
        with self.assertRaisesRegex(ValueError,'readout'):t.ecal_only(tree)
        tree=compact();tree.find('includes/gdmlFile').set('ref','/tmp/other.xml')
        with self.assertRaisesRegex(ValueError,'material include'):t.ecal_only(tree)

    def test_signed_barrel_theta_and_canonical_plane(self):
        desc=self.inventory['LArBarrelHits']['descriptor']
        cell=encode(dict(system=10,plane=1534,layer=0,theta=-4),desc)
        self.assertEqual(t.validate_cell(cell,'LArBarrelHits',self.inventory)['theta'],-4)
        for fields in [dict(system=10,plane=1535,layer=0,theta=-4),dict(system=10,plane=1536,layer=0,theta=-4),dict(system=10,plane=0,layer=0,theta=-3)]:
            with self.assertRaisesRegex(ValueError,'barrel cell'):t.validate_cell(encode(fields,desc),'LArBarrelHits',self.inventory)

    def test_endcap_side_wheel_and_virtual_cell_membership(self):
        desc=self.inventory['LArEndcapHits']['descriptor']
        fields=dict(system=11,side=2,wheel=2,plane=1359,rho=33,z=9)
        self.assertEqual(t.validate_cell(encode(fields,desc),'LArEndcapHits',self.inventory)['side'],2)
        for key,value in [('side',0),('wheel',3),('plane',1360),('rho',34),('z',8)]:
            with self.subTest(key=key):
                bad=dict(fields);bad[key]=value
                with self.assertRaisesRegex(ValueError,'turbine cell'):t.validate_cell(encode(bad,desc),'LArEndcapHits',self.inventory)

    def test_gap_system_high_bits_and_negative_ids_rejected(self):
        name='LArBarrelHits';desc=self.inventory[name]['descriptor'];fields=dict(system=10,layer=0,theta=-4)
        for bad in [encode(dict(fields,gap=1),desc),encode(dict(fields,system=11),desc),encode(fields,desc)|(1<<63),-1]:
            with self.assertRaises(ValueError):t.validate_cell(bad,name,self.inventory)

    def test_duplicate_or_incomplete_reference_tables_rejected(self):
        tree=compact();seg=tree.findall('readouts/readout')[1].find('segmentation')
        seg.set('reference_table_mm','0 -4 1 2 3 0 -4 4 5 6')
        with self.assertRaisesRegex(ValueError,'Duplicate'):t.cell_inventory(t.ecal_only(tree).getroot())
        seg.set('reference_table_mm','0 -4 1 2')
        with self.assertRaisesRegex(ValueError,'Bad barrel'):t.cell_inventory(t.ecal_only(tree).getroot())

    def test_matched_worker_inventory_and_event_totals(self):
        receipt=dict(threads=2,events=6,max_step_mm=5.)
        self.assertEqual(t.check_workers([worker(0),worker(1)],receipt),{'0':3,'1':3})
        for rows in [[worker(0)],[worker(0),worker(0)],[worker(0),dict(worker(1),events=4)]]:
            with self.assertRaises(ValueError):t.check_workers(rows,receipt)

    def test_worker_field_cuts_material_and_step_are_required(self):
        receipt=dict(threads=1,events=3,max_step_mm=5.)
        for mutate in [lambda w:w.update(maps_initialized_serially=False),
                       lambda w:w.update(maximum_abs_magnetic_field_tesla=.1),
                       lambda w:w.update(region_cuts=[dict(mm=[1.]*4)]),
                       lambda w:w['sensitive_lar']['LArBarrel']['volumes'][0].update(density_g_cm3=1.4),
                       lambda w:w['sensitive_lar']['LArBarrel']['volumes'][0].update(max_step_mm=None),
                       lambda w:w['sensitive_lar']['LArEndcaps']['volumes'][0].update(Birks_mm_per_MeV=.1)]:
            w=worker();mutate(w)
            with self.assertRaises(ValueError):t.check_workers([w],receipt)

    def test_native_policy_is_unmodified(self):
        receipt=dict(threads=1,events=3,max_step_mm=0.)
        t.check_workers([worker(cap=0)],receipt)
        w=worker(cap=0);w['sensitive_lar']['LArBarrel']['volumes'][0]['numeric_cap_applied']=True
        with self.assertRaisesRegex(ValueError,'modified'):t.check_workers([w],receipt)

    def test_artifact_hash_and_unsafe_paths(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'file';p.write_bytes(b'unchanged')
            t.verify_hashes(d,{'file':hashlib.sha256(b'unchanged').hexdigest()})
            for name,digest in [('file','bad'),('../file','bad')]:
                with self.assertRaises(ValueError):t.verify_hashes(d,{name:digest})


if __name__=='__main__':unittest.main()
