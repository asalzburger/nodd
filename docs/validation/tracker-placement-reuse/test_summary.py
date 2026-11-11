"""Reject scientific timing comparisons whose controls are not matched."""
import json
from pathlib import Path
import tempfile
import unittest
from summarize_comparison import summarize


class TimingIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.runs=[]
        # Receipt fixtures, not measured times or geometry payloads.
        for variant_index,variant in enumerate(('baseline','cache','mother')):
            for repeat in (1,2):
                directory=Path(self.temp.name)/f'{variant}-{repeat}';directory.mkdir()
                def write(name,value):
                    (directory/name).write_text(json.dumps(value))
                write('timing.json',dict(exit_code=0,sensitive_paths=46682,mapping_seconds=1.,
                      wall_including_inventory_seconds=2.,peak_child_rss_bytes=3))
                write('provenance.json',dict(sha256={'tracker.xml':str(variant_index)*64,
                      'materials.xml':'a'*64,'libFactory.dylib':'b'*64},
                      command=['test_ddsim','--compactFile',variant,'--macroFile',str(directory/'macro'),
                               '--outputFile',str(directory/'output'),'--random.seed','130001']))
                write('inventory.json',dict(tgeo={},geant4={}))
                phases=['xerces_dom_parse_path','g4_initialize','g4_close_geometry_voxelization',
                        'g4_update_couple_table','g4_event_transport_and_recording']
                (directory/'native-phases.jsonl').write_text('\n'.join(json.dumps(dict(name=n,wall_s=1.)) for n in phases))
                (directory/'probe.log').write_text('test fixture')
                write('geant4-sensors.json',[])
                self.runs.append((variant,directory))

    def test_matched_receipts_pass(self):
        self.assertEqual(summarize(self.runs)['summary']['cache']['runs'],2)

    def test_rejects_binary_seed_or_compact_change(self):
        path=self.runs[-1][1]/'provenance.json'
        original=json.loads(path.read_text())
        for mutation in ('binary','seed','compact'):
            value=json.loads(json.dumps(original))
            if mutation=='binary':value['sha256']['libFactory.dylib']='c'*64
            elif mutation=='seed':value['command'][-1]='130002'
            else:value['sha256']['tracker.xml']='d'*64
            path.write_text(json.dumps(value))
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                summarize(self.runs)
        path.write_text(json.dumps(original))

    def test_rejects_missing_repeat(self):
        with self.assertRaises(ValueError):summarize(self.runs[:-1])


if __name__=='__main__':unittest.main()
