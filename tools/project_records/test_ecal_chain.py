"""Synthetic Git controls for ECAL source/history retention; no native runtime."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import check_ecal_chain as guard


class EcalChainTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'
        self.root.mkdir()
        self.git('init', '-q', '-b', 'main')
        self.git('config', 'user.name', 'Synthetic fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.base = self.commit('test baseline')
        self.heads = {}
        for number in (133, 134, 135, 136):
            self.heads[number] = self.commit('synthetic source PR' + str(number))
        self.core = b'# synthetic numerical core, no detector model\n'
        self.write(guard.CORE, self.core)
        self.coefficients = json.dumps(dict(core_sha256=hashlib.sha256(self.core).hexdigest(), models={})).encode()
        self.write(guard.ARTIFACT + '/models.json', self.coefficients)
        self.freeze = self.commit('test calibration freeze')
        self.validated = self.commit('test independent validation')
        self.heads[137] = self.commit('synthetic source PR137')
        self.manifest = dict(schema_version=1, coefficients_file='models.json',
            coefficients_sha256=hashlib.sha256(self.coefficients).hexdigest(),
            freeze_commit=self.freeze, validated_results_commit=self.validated)
        self.tracking = dict(pull_requests=[dict(number=n, state='open', head_revision=self.heads[n],
            merge_commit=None, merged_at=None) for n in guard.CHAIN])
        self.ledgers = {n: dict(github=dict(pull_request=dict(number=n, head_sha=self.heads[n])),
            derived=dict(token_accounts=[dict(id='SESSION-FIXTURE',record='logs/codex/SESSION-FIXTURE.json',
                scope='canonical_session; shared PR references are not allocations')])) for n in guard.CHAIN}
        self.save('logs/codex/SESSION-FIXTURE.json',dict(session_id='SESSION-FIXTURE',title='Explicit software fixture',
            usage=[dict(input_tokens=0,total_tokens=None),dict(input_tokens=10,total_tokens=12)]))
        self.save_records()
        self.checked = self.commit('test retained records')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], text=True, stderr=subprocess.PIPE).strip()

    def write(self, path, data):
        p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)

    def save(self, path, value):
        self.write(path,(json.dumps(value)+'\n').encode())

    def save_records(self):
        self.save('project/tracking.json',self.tracking)
        self.save(guard.ARTIFACT+'/manifest.json',self.manifest)
        for n,d in self.ledgers.items():self.save(f'interactions/pr-{n:04d}.json',d)

    def commit(self, label):
        self.write('fixture.txt',(label+'\n').encode())
        self.git('add','.')
        self.git('commit','-qm',label)
        return self.git('rev-parse','HEAD')

    def detached(self, parent=None):
        # Deliberately unreferenced descendant/sibling; object exists, but HEAD
        # does not contain it. No branch/history rewriting is needed.
        return self.git('commit-tree',self.git('rev-parse','HEAD^{tree}'),'-p',parent or self.checked,'-m','detached test evidence')

    def test_good_chain_is_read_only_and_owners_are_not_multiplied(self):
        before=self.git('status','--porcelain')
        report=guard.check(self.root)
        self.assertEqual(report['checked_head'],self.checked)
        self.assertEqual(len(report['chain']),5)
        owners=report['work_coverage']['canonical_owners']
        self.assertEqual(len(owners),1)
        self.assertEqual(owners[0]['pull_requests'],list(guard.CHAIN))
        self.assertEqual(owners[0]['observed_turns'],2)
        self.assertEqual(owners[0]['counters_known']['input_tokens'],2) # Observed zero counts as known.
        self.assertEqual(owners[0]['counters_known']['total_tokens'],1)
        self.assertEqual(self.git('status','--porcelain'),before)

    def test_missing_tracking_and_interaction_evidence_rejected(self):
        saved=self.tracking['pull_requests'].pop(0);self.save_records()
        with self.assertRaisesRegex(ValueError,'PR133'):guard.check(self.root)
        self.tracking['pull_requests'].insert(0,saved);self.save_records()
        (self.root/'interactions/pr-0135.json').unlink()
        with self.assertRaises(FileNotFoundError):guard.check(self.root)

    def test_duplicate_and_reordered_heads_rejected(self):
        self.tracking['pull_requests'].append(dict(self.tracking['pull_requests'][0]));self.save_records()
        with self.assertRaisesRegex(ValueError,'exactly one'):guard.check(self.root)
        self.tracking['pull_requests'].pop();self.tracking['pull_requests'][2]['head_revision']=self.heads[133];self.save_records()
        with self.assertRaisesRegex(ValueError,'reordered or incomplete'):guard.check(self.root)

    def test_unreachable_tracking_and_interaction_heads_rejected(self):
        self.tracking['pull_requests'][2]['head_revision']=self.detached(self.base);self.save_records()
        with self.assertRaisesRegex(ValueError,'tracking head is not retained'):guard.check(self.root)
        self.tracking['pull_requests'][2]['head_revision']=self.heads[135]
        self.ledgers[135]['github']['pull_request']['head_sha']=self.detached(self.base);self.save_records()
        with self.assertRaisesRegex(ValueError,'interaction head is not retained'):guard.check(self.root)

    def test_reordered_interaction_chain_rejected(self):
        self.ledgers[135]['github']['pull_request']['head_sha']=self.heads[133];self.save_records()
        with self.assertRaisesRegex(ValueError,'Interaction chain'):guard.check(self.root)

    def test_lost_freeze_and_validation_evidence_rejected(self):
        self.manifest['freeze_commit']=self.detached(self.base);self.save_records()
        with self.assertRaisesRegex(ValueError,'calibration freeze'):guard.check(self.root)
        self.manifest['freeze_commit']=self.freeze;self.manifest['validated_results_commit']=self.detached();self.save_records()
        with self.assertRaisesRegex(ValueError,'Validated results are not retained'):guard.check(self.root)

    def test_changed_coefficients_cannot_be_reblessed_by_manifest_hash(self):
        changed=self.coefficients+b' '
        self.write(guard.ARTIFACT+'/models.json',changed)
        with self.assertRaisesRegex(ValueError,'coefficient hash'):guard.check(self.root)
        self.manifest['coefficients_sha256']=hashlib.sha256(changed).hexdigest();self.save_records()
        with self.assertRaisesRegex(ValueError,'coefficient bytes differ'):guard.check(self.root)

    def test_changed_core_rejected(self):
        self.write(guard.CORE,self.core+b'# changed\n')
        with self.assertRaisesRegex(ValueError,'numerical core'):guard.check(self.root)

    def test_recorded_merge_must_include_head_and_be_in_checked_history(self):
        pr=self.tracking['pull_requests'][-1];pr.update(state='merged',merge_commit=self.base,merged_at='2026-01-01T00:00:00Z');self.save_records()
        with self.assertRaisesRegex(ValueError,'merge does not include its head'):guard.check(self.root)
        pr['merge_commit']=self.detached();self.save_records()
        with self.assertRaisesRegex(ValueError,'merge is detached'):guard.check(self.root)

    def test_require_merged_and_no_future_merge_metadata(self):
        with self.assertRaisesRegex(ValueError,'not recorded merged'):guard.check(self.root,require_merged=True)
        self.tracking['pull_requests'][0]['merge_commit']=self.checked;self.save_records()
        with self.assertRaisesRegex(ValueError,'despite an unmerged state'):guard.check(self.root)

    def test_ordinary_merge_closeout_passes_strict_mode(self):
        # Merge each source head into a main-like branch without squashing.
        self.git('switch','-q','-c','integrated',self.base)
        for pr in self.tracking['pull_requests']:
            self.git('merge','-q','--no-ff',pr['head_revision'],'-m','Synthetic ordinary merge')
            pr.update(state='merged',merge_commit=self.git('rev-parse','HEAD'),merged_at='2026-01-01T00:00:00Z')
        self.save('logs/codex/SESSION-FIXTURE.json',dict(session_id='SESSION-FIXTURE',title='Explicit software fixture',usage=[]))
        self.save_records();self.commit('test actual merge closeout records')
        self.assertEqual(guard.check(self.root,require_merged=True)['status'],'PASS')

    def absorbed_dependent_history(self, merged=True):
        # Model the real fast-forward absorption: dependent134 is merged at its
        # source head into133's branch, followed by two corrective commits.
        self.git('switch','-q','-c','corrected-133',self.heads[134])
        for label in ('restore133','restore134'):
            self.write(label+'.txt',(label+' synthetic corrective tree\n').encode())
            self.git('add','.')
            self.git('commit','-qm',label)
        corrected133=self.git('rev-parse','HEAD')
        self.git('switch','-q','main')
        self.git('merge','-q','--no-ff','corrected-133','-m','Retain corrective history in successors')
        self.tracking['pull_requests'][0]['head_revision']=corrected133
        self.ledgers[133]['github']['pull_request']['head_sha']=corrected133
        if merged:
            self.tracking['pull_requests'][1].update(state='merged',merge_commit=self.heads[134],merged_at='2026-01-01T00:00:00Z')
        for number in (135,136,137):
            propagated=self.commit('propagated source PR'+str(number))
            self.tracking['pull_requests'][number-133]['head_revision']=propagated
            self.ledgers[number]['github']['pull_request']['head_sha']=propagated
        self.save_records();self.checked=self.commit('record absorbed dependent history')

    def test_absorbed_merged_dependent_with_corrective_commits_passes(self):
        self.absorbed_dependent_history()
        report=guard.check(self.root)
        self.assertEqual(report['chain_links'][0],dict(earlier=133,later=134,
            tracking='absorbed_dependent',interaction='absorbed_dependent'))
        self.assertTrue(all(link['tracking']=='forward' and link['interaction']=='forward'
                            for link in report['chain_links'][1:]))
        self.assertEqual(report['chain'][1]['merge_commit'],self.heads[134])
        self.assertEqual(report['calibration']['freeze_commit'],self.freeze)

    def test_absorbed_history_without_recorded_merge_rejected(self):
        self.absorbed_dependent_history(merged=False)
        with self.assertRaisesRegex(ValueError,'reversed heads require a recorded merged dependent'):
            guard.check(self.root)

    def test_absorbed_history_with_detached_merge_rejected(self):
        self.absorbed_dependent_history()
        self.tracking['pull_requests'][1]['merge_commit']=self.detached();self.save_records()
        with self.assertRaisesRegex(ValueError,'recorded merge is detached'):guard.check(self.root)

    def test_reversed_heads_with_merge_not_absorbed_by_predecessor_rejected(self):
        self.absorbed_dependent_history()
        self.tracking['pull_requests'][1]['merge_commit']=self.checked;self.save_records()
        with self.assertRaisesRegex(ValueError,'merge was not absorbed by the earlier head'):guard.check(self.root)

    def test_absorbed_dependent_capture_must_be_in_actual_merge(self):
        self.absorbed_dependent_history()
        self.ledgers[134]['github']['pull_request']['head_sha']=self.tracking['pull_requests'][0]['head_revision']
        self.save_records()
        with self.assertRaisesRegex(ValueError,'captured interaction head'):guard.check(self.root)

    def test_cli_report_is_optional_and_never_overwrites(self):
        out=Path(self.tmp.name)/'report.json'
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(guard.main(['--repo',str(self.root),'--output',str(out)]),0)
        before=out.read_bytes()
        with contextlib.redirect_stderr(io.StringIO()),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(guard.main(['--repo',str(self.root),'--output',str(out)]),1)
        self.assertEqual(out.read_bytes(),before)
        self.assertEqual(json.loads(before)['status'],'PASS')


if __name__=='__main__':unittest.main()
