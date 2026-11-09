"""Software-only nODD reference contracts; no geometry construction/transport."""
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
import xml.etree.ElementTree as ET

import nodd_reference_validation as n


class ReferenceContracts(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='nodd-reference-contract-');self.addCleanup(self.tmp.cleanup)
        self.work=Path(self.tmp.name).resolve()

    def geometry(self):
        material=self.work/'materials.xml';material.write_text('<lccdd><materials><material name="prefixed_Silicon"/></materials></lccdd>')
        child=self.work/'component.xml'
        tracker=''.join(f'<detector name="tracker-fixture-{i}" id="{i}"/>' for i in range(8))
        child.write_text(f'''<lccdd><readouts>
          <readout name="BARRELHits"><id>{n.DESCRIPTOR}</id></readout>
          <readout name="EDGEHits"><id>{n.DESCRIPTOR}</id></readout>
        </readouts><detectors>{tracker}
          <detector name="barrel" id="8" readout="BARRELHits"/>
          <detector name="endcaps" id="9" readout="EDGEHits"><replica side="1"/><replica side="2"/></detector>
        </detectors></lccdd>''')
        root=self.work/'detector.xml';root.write_text('<lccdd><includes><gdmlFile ref="materials.xml"/></includes><define><constant name="world_x" value="100*mm"/></define><include ref="component.xml"/></lccdd>')
        return root,child,material

    def test_wrapper_preserves_resolved_geometry_and_namespaces(self):
        root,child,material=self.geometry();before={p:p.read_bytes() for p in (root,child,material)}
        output=self.work/'wrapper.xml';proof,files=n.wrapper(root,output)
        self.assertEqual(proof['root_ids'],{'BARRELHits':8,'EDGEHits':9})
        self.assertEqual(proof['configured_endcap_sides'],[1,2]);self.assertEqual(len(files),3)
        self.assertEqual(proof['all_constructed_root_ids'],list(range(10)))
        tree=ET.parse(output);constants=tree.findall('define/constant')
        self.assertEqual(len(constants),3)
        self.assertEqual({c.get('value') for c in constants if c.get('type')=='string'},{n.DESCRIPTOR})
        self.assertEqual(tree.find('include').get('ref'),str(child.resolve()))
        self.assertEqual({p:p.read_bytes() for p in before},before)
        with self.assertRaisesRegex(RuntimeError,'overwrite'):n.wrapper(root,output)

    def test_standalone_root_or_missing_endcap_is_rejected(self):
        root,child,_=self.geometry();data=child.read_text();child.write_text(data.replace('id="9"','id="8"'))
        with self.assertRaisesRegex(RuntimeError,'root ID'):n.wrapper(root,self.work/'wrong.xml')
        child.write_text(data.replace('<replica side="2"/>',''))
        with self.assertRaisesRegex(RuntimeError,'Both configured'):n.wrapper(root,self.work/'missing.xml')
        child.write_text(data.replace('<detector name="tracker-fixture-7" id="7"/>',''))
        with self.assertRaisesRegex(RuntimeError,'Complete maintained'):n.wrapper(root,self.work/'missing-tracker.xml')

    def test_cell_id_namespace_high_bits_and_layers(self):
        cid=9|(2<<8)|(15<<10)|(47<<14)|(1023<<20)|(63<<30)|(63<<36)
        self.assertGreater(cid,2**32);self.assertEqual(n.validate_cell_id(cid,'EDGEHits'),2)
        self.assertEqual(n.validate_cell_id(8,'BARRELHits'),0)
        for invalid,collection in [(cid^1,'EDGEHits'),(9,'EDGEHits'),(8|(1<<8),'BARRELHits'),(cid|(1<<50),'EDGEHits'),(9|(1<<8)|(48<<14),'EDGEHits')]:
            with self.subTest(cid=invalid):
                with self.assertRaises(RuntimeError):n.validate_cell_id(invalid,collection)

    def test_loaded_helper_is_pinned_and_ood_defaults_unchanged(self):
        import reference_validation as old
        previous=list(old.NAMES);before=n.sha(n.HELPER_PATH);helper=n.load_helper()
        self.assertEqual(hashlib.sha256(helper.LOADED_SOURCE).hexdigest(),n.HELPER_PIN)
        self.assertEqual(helper.NAMES,n.COLLECTIONS);self.assertEqual(old.NAMES,previous);self.assertEqual(n.sha(n.HELPER_PATH),before)
        copied=self.work/'helper.py';copied.write_bytes(n.HELPER_PATH.read_bytes()+b'\n# changed\n')
        with self.assertRaisesRegex(RuntimeError,'pinned'):n.load_helper(copied)

    def test_manifest_does_not_assume_twenty_files_and_rejects_changes(self):
        root,_,_=self.geometry();lib=self.work/'factory.dylib';lib.write_text('synthetic fixture')
        item=lambda p:dict(path=str(p),sha256=n.sha(p))
        samples=[]
        for i in range(22):
            raw=self.work/f'input-{i}.root';raw.write_text('synthetic fixture'+str(i))
            samples.append(dict(item(raw),id=f'fixture-{i}',events=250 if i%2 else 200,exit_code=0,particle='mu-',energy_GeV=10,eta=i))
        data=dict(geometry_label='LAYOUT-001',compact=item(root),libraries=[item(lib)],samples=samples)
        self.assertEqual(n.validate_input(data)[0],root.resolve())
        data['samples'][1]['id']=data['samples'][0]['id']
        with self.assertRaisesRegex(RuntimeError,'Repeated'):n.validate_input(data)
        data['samples'][1]['id']='restored';raw.write_text('corrupted')
        with self.assertRaisesRegex(RuntimeError,'Changed declared'):n.validate_input(data)

    def test_prepare_never_replaces_existing_evidence(self):
        sentinel=self.work/'manifest.json';sentinel.write_text('preserved')
        with self.assertRaisesRegex(RuntimeError,'fresh'):n.prepare(SimpleNamespace(work=self.work),None)
        self.assertEqual(sentinel.read_text(),'preserved')

    def test_declared_geometry_source_dependencies_are_actually_verified(self):
        source=self.work/'geometry.cpp';source.write_text('frozen synthetic source')
        receipt=self.work/'geometry-receipt.json';receipt.write_text(json.dumps(dict(immutable={str(source):n.sha(source)})))
        self.assertIn(source,n.receipt_dependencies([receipt]))
        source.write_text('changed source')
        with self.assertRaisesRegex(RuntimeError,'Changed declared'):n.receipt_dependencies([receipt])

    def test_receipt_and_actual_loaded_source_tampering_fail_closed(self):
        log=self.work/'original.log';log.write_text('complete')
        root=self.work/'original.root';root.write_text('synthetic')
        config=self.work/'steering.py';config.write_text('frozen')
        sources=dict(runner_sha256='runner',helper_sha256='helper')
        (self.work/'original.execution.json').write_text(json.dumps(dict(exit_code=0,log=str(log),log_sha256=n.sha(log),loaded_sources=sources,input_files={str(config):n.sha(config)})))
        (self.work/'original-complete.json').write_text(json.dumps(dict(output_sha256=n.sha(root),steering_sha256=n.sha(config))))
        n.verify_case(self.work)
        with self.assertRaisesRegex(RuntimeError,'loaded'):n.verify_case(self.work,dict(runner_sha256='different',helper_sha256='helper'))
        config.write_text('changed')
        with self.assertRaisesRegex(RuntimeError,'command input'):n.verify_case(self.work)

    def test_closed_rng_and_steering_artifacts_are_anchored(self):
        steering=self.work/'steering.py';steering.write_text('frozen steering')
        audit=self.work/'block-rng.json';audit.write_text('synthetic seed audit')
        state=Path(str(audit)+'.state');state.write_text('synthetic complete engine state')
        receipt=self.work/'execution.json'
        receipt.write_text(json.dumps(dict(steering_sha256=n.sha(steering),samples=[dict(
            rng_audit_path=str(audit),rng_audit_sha256=n.sha(audit),rng_state_sha256=n.sha(state))])))
        self.assertTrue({steering,audit,state}.issubset(n.receipt_dependencies([receipt])))
        state.write_text('changed state')
        with self.assertRaisesRegex(RuntimeError,'Changed declared'):n.receipt_dependencies([receipt])


if __name__=='__main__':unittest.main()
