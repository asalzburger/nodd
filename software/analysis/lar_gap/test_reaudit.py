"""Native logical/physical alias and separate-auditor integrity controls."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

import observed_transport as frozen
from observed_reaudit import catalog_rows,read_catalog,match_catalog_failures,proof_identity,helpers
from geometry import ROOT,sha


class NativeAliasControls(unittest.TestCase):
    def setUp(self):
        self.rows=[dict(sensitive=True,volume='w1_gap1',path='/world/LArEndcaps_1/TurbineWheel1_3/w1_gap1_7'),
                   dict(sensitive=True,volume='w2_gap0',path='/world/LArEndcaps_1/TurbineWheel2_4/w2_gap0_6'),
                   dict(sensitive=False,volume='w1_gap1',path='/world/unrelated/w1_gap1_99')]
        self.aliases,self.count=catalog_rows(self.rows)
        self.failure=dict(raw_volume=10679563,volume='w1_gap1',mid_local_mm=[771.93370812,59.9801701,63.9788821])
        self.logged=[(10679563,'w1_gap1_7',[771.933708,59.980170,63.978882])]

    def test_real_logical_and_physical_names_match_only_native_sensitive_catalog(self):
        self.assertEqual(self.count,2);self.assertEqual(self.aliases['w1_gap1'],{'w1_gap1_7'})
        match_catalog_failures([self.failure],self.logged,self.aliases)
        with self.assertRaises(ValueError):frozen.match_failures([self.failure],self.logged)

    def test_second_actual_wheel_gap_alias_is_supported_without_suffix_inference(self):
        f=dict(raw_volume=477707,volume='w2_gap0',mid_local_mm=[1458.307706,186.895740,212.881009])
        match_catalog_failures([f],[(477707,'w2_gap0_6',f['mid_local_mm'])],self.aliases)

    def test_wrong_raw_id_wrong_copy_and_unsupported_name_fail(self):
        for raw,physical in ((10679564,'w1_gap1_7'),(10679563,'w1_gap1_6'),(10679563,'w1_gap1_99'),(10679563,'w1_gap1')):
            with self.subTest(raw=raw,physical=physical),self.assertRaises(ValueError):
                match_catalog_failures([self.failure],[(raw,physical,self.logged[0][2])],self.aliases)

    def test_missing_native_alias_and_physical_name_used_as_logical_fail(self):
        with self.assertRaises(ValueError):match_catalog_failures([self.failure],self.logged,{})
        f=deepcopy(self.failure);f['volume']='w1_gap1_7'
        with self.assertRaises(ValueError):match_catalog_failures([f],self.logged,self.aliases)

    def test_point_and_count_gates_are_preserved(self):
        bad=deepcopy(self.logged);bad[0][2][0]+=.00001
        for logged in (bad,[],self.logged*2):
            with self.assertRaises(ValueError):match_catalog_failures([self.failure],logged,self.aliases)
        with self.assertRaises(ValueError):match_catalog_failures([self.failure]*2,self.logged,self.aliases)

    def test_changed_native_ledger_rejected_before_alias_use(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'placements.jsonl';path.write_text('\n'.join(map(json.dumps,self.rows))+'\n');digest=sha(path)
            aliases,count=read_catalog(path,digest);self.assertEqual(aliases,self.aliases);self.assertEqual(count,2)
            path.write_text(path.read_text().replace('w1_gap1_7','w1_gap1_8'))
            with self.assertRaisesRegex(ValueError,'Changed native'):read_catalog(path,digest)

    def test_own_auditor_identity_cannot_be_replaced_by_legacy_hash(self):
        path=ROOT/'software/analysis/lar_gap/observed_reaudit.py'
        proof=dict(status='PASS',auditor=dict(path=str(path.relative_to(ROOT)),sha256=sha(path)),helper_sha256=helpers())
        proof_identity(proof)
        missing=deepcopy(proof);missing['helper_sha256']={}
        with self.assertRaisesRegex(ValueError,'missing'):proof_identity(missing)
        proof['auditor']['sha256']=sha(frozen.__file__)
        with self.assertRaisesRegex(ValueError,'foreign'):proof_identity(proof)


if __name__=='__main__':unittest.main()
