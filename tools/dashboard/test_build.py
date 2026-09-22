"""Synthetic review fixtures: no test records confer real human approval."""
import copy
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from urllib.parse import unquote, urlsplit

import build


class Page(HTMLParser):
    def __init__(self, content):
        super().__init__()
        self.ids, self.links = set(), []
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if 'id' in values:
            if values['id'] in self.ids:
                raise AssertionError('Duplicate HTML ID')
            self.ids.add(values['id'])
        for key in ('href','src'):
            if key in values:
                self.links.append(values[key])


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        self.root.mkdir()
        for directory in ('project','docs','reference','dashboard','logs','tools'):
            shutil.copytree(build.ROOT / directory, self.root / directory)
        shutil.copy(build.ROOT / 'PROJECT.md', self.root / 'PROJECT.md')
        shutil.copy(build.ROOT / '.gitignore', self.root / '.gitignore')
        # Remove live GitHub/revision records from synthetic history. Real-history
        # integration is tested separately against the actual checkout.
        self.tracking = json.loads((self.root / 'project/tracking.json').read_text())
        self.reviews = json.loads((self.root / 'project/reviews.json').read_text())
        self.tracking['pull_requests'] = []
        self.reviews['rounds'] = []
        self.save()
        self.run_git('init','-q')
        self.run_git('add','.')
        self.run_git('-c','user.name=Synthetic fixture','-c','user.email=fixture@example.invalid',
                     'commit','-qm','Synthetic fixture baseline')
        self.sha = self.run_git('rev-parse','HEAD').strip()
        self.tracking = json.loads((self.root / 'project/tracking.json').read_text())
        self.reviews = json.loads((self.root / 'project/reviews.json').read_text())
        self.doc = self.tracking['documents'][0]
        self.task = next(t for t in self.tracking['tasks'] if t['id']=='TASK-GOVERNANCE')

    def run_git(self,*args):
        return subprocess.check_output(['git','-C',str(self.root),*args]).decode()

    def save(self):
        for name,value in [('tracking',self.tracking),('reviews',self.reviews)]:
            (self.root / f'project/{name}.json').write_text(json.dumps(value))

    def normalize(self):
        self.save()
        return build.normalize(self.root)

    def round(self, **updates):
        review=dict(id='TEST-REVIEW-1',task=self.task['id'],document=self.doc['id'],
                    target_revision=self.sha,type='technical',state='closed',
                    outcome='changes requested',requested_at='2026-09-17',
                    completed_at='2026-09-17',reviewers=[],conditions=[],
                    conditions_resolved=False,evidence=[self.doc['path']],
                    approval_record=None,supersedes=None)
        review.update(updates)
        self.reviews['rounds'].append(review)
        return review

    def approval(self, **updates):
        defaults=dict(type='sign-off',outcome='approved',
                      reviewers=[dict(name='Synthetic reviewer',role='Test role',human=True)],
                      approval_record='docs/signoff/ADR-001-test.md')
        defaults.update(updates)
        review=self.round(**defaults)
        self.write_approval(review)
        return review

    def write_approval(self,review):
        p=self.root / review['approval_record']
        p.write_text(f'''# Synthetic fixture — not real approval
- Design ID: {self.doc['id']}
- Exact reviewed full commit SHA: {self.sha}
- Reviewer name: Synthetic reviewer
- Review date (YYYY-MM-DD): 2026-09-17
- Outcome: {review['outcome']}
- Approval evidence: {self.doc['path']}
''')

    def test_real_initialization_and_unknown_review_state(self):
        data=self.normalize()
        self.assertEqual(data['tracking']['stages'][0]['state'],'completed')
        self.assertIn('NOT RUN',data['tracking']['stages'][0]['disposition'])
        self.assertEqual(data['tracking']['milestones'][0]['state'],'pending')
        self.assertEqual(data['reviews']['rounds'],[])
        self.assertTrue(all(x['state']=='DRAFT' for x in data['tracking']['documents']))

    def test_closed_changes_requested_and_repeated_rounds(self):
        first=self.round()
        self.round(id='TEST-REVIEW-2',state='open',outcome='pending',completed_at=None,
                   supersedes=first['id'])
        data=self.normalize()
        self.assertEqual(len(data['reviews']['rounds']),2)
        self.assertFalse(data['reviews']['rounds'][0]['approval_supported'])

    def test_conditional_approval_does_not_confer_signoff(self):
        self.approval(outcome='conditional',conditions=['Synthetic condition'])
        review=self.normalize()['reviews']['rounds'][0]
        self.assertFalse(review['approval_supported'])
        self.assertIn('Approval conditions remain open.', review['warnings'])

    def test_approval_survives_unrelated_commit_but_not_document_change(self):
        self.approval()
        (self.root / 'unrelated.txt').write_text('Synthetic unrelated change')
        self.run_git('add','unrelated.txt')
        self.run_git('-c','user.name=Synthetic fixture','-c','user.email=fixture@example.invalid',
                     'commit','-qm','Synthetic unrelated change')
        self.assertTrue(self.normalize()['reviews']['rounds'][0]['target_matches_current'])
        with (self.root / self.doc['path']).open('a') as f:
            f.write('\nSynthetic document amendment.\n')
        review=self.normalize()['reviews']['rounds'][0]
        self.assertFalse(review['target_matches_current'])
        self.assertTrue(review['warnings'])

    def test_declared_acceptance_without_signoff_is_visible_discrepancy(self):
        p=self.root / self.doc['path']
        p.write_text(p.read_text().replace('- Status: DRAFT','- Status: ACCEPTED'))
        doc=self.normalize()['tracking']['documents'][0]
        self.assertEqual(doc['state'],'ACCEPTED')
        self.assertEqual(len(doc['warnings']),3)

    def test_merged_or_completed_work_does_not_promote_draft(self):
        self.task.update(state='completed',disposition='Synthetic merged deliverable; no approval.',
                         deliverables=[self.doc['path']])
        self.assertEqual(self.normalize()['tracking']['documents'][0]['state'],'DRAFT')

    def test_missing_criteria_are_preserved_in_source_evidence(self):
        out=self.root / '_site/test'
        build.build(self.root,out,'2026-09-17T12:00:00Z')
        baseline=out / 'evidence' / build.evidence_name('docs/validation/M0-baseline-specification.md')
        self.assertIn('No numerical acceptance limits have been selected', baseline.read_text())

    def pr(self, **updates):
        record=dict(id='TEST-PR-1',number=1,title='Synthetic PR',
                    url='https://github.com/example/synthetic/pull/1',state='merged',
                    head_revision=self.sha,merge_commit=self.sha,
                    merged_at='2026-09-17T10:00:00Z',collected_at='2026-09-17T11:00:00Z',
                    task=self.task['id'],documents=[self.doc['id']],scope='Synthetic test scope')
        record.update(updates)
        self.tracking['pull_requests'].append(record)
        return record

    def test_technical_approval_and_merge_do_not_promote_document(self):
        self.pr()
        self.round(outcome='approved',reviewers=[dict(name='Synthetic reviewer',role='Test role',human=True)])
        data=self.normalize()
        self.assertEqual(data['tracking']['documents'][0]['state'],'DRAFT')
        self.assertIn('Formal sign-off is not established.',data['tracking']['documents'][0]['warnings'][0])
        self.assertFalse(data['reviews']['rounds'][0]['approval_supported'])

    def test_chore_entries_cannot_enter_progress(self):
        self.task['category']='chore'
        with self.assertRaisesRegex(build.Invalid,'Chore tasks'):
            self.normalize()
        self.task['category']='project'
        pr=self.pr(title='chore: synthetic maintenance')
        with self.assertRaisesRegex(build.Invalid,'Chore PRs'):
            self.normalize()
        pr.update(title='Infrastructure: synthetic maintenance')
        with self.assertRaisesRegex(build.Invalid,'Chore PRs'):
            self.normalize()
        pr.update(title='Synthetic project work',category='chore')
        with self.assertRaisesRegex(build.Invalid,'Chore PRs'):
            self.normalize()

    def test_invalid_pr_metadata_rejected(self):
        pr=self.pr(state='closed')
        with self.assertRaisesRegex(build.Invalid,'Unmerged PR'):
            self.normalize()
        pr['state']='merged'
        pr['merge_commit']='0'*40
        with self.assertRaisesRegex(build.Invalid,'Git evidence'):
            self.normalize()
        pr['merge_commit']=self.sha
        pr['collected_at']='2026-09-17T09:00:00Z'
        with self.assertRaisesRegex(build.Invalid,'predates merge'):
            self.normalize()

    def test_formatted_repository_statuses_and_unknowns(self):
        self.assertEqual(build.document_state('- Status: **DRAFT — review round 2**, not approved.'),'DRAFT')
        self.assertEqual(build.document_state('- Status: DRAFT; created: 2026-09-17.'),'DRAFT')
        with self.assertRaises(build.Invalid):
            build.document_state('- Status: **DRAFTED**')

    def test_dependency_cycles_and_unknown_references_rejected(self):
        self.task['dependencies']=[self.task['id']]
        with self.assertRaisesRegex(build.Invalid,'cycle'):
            self.normalize()
        self.task['dependencies']=['TEST-MISSING']
        with self.assertRaisesRegex(build.Invalid,'Unknown dependency'):
            self.normalize()

    def test_blockers_and_completion_require_evidence(self):
        self.task['state']='blocked'
        with self.assertRaisesRegex(build.Invalid,'reason'):
            self.normalize()
        self.task['state']='completed'
        with self.assertRaisesRegex(build.Invalid,'deliverables'):
            self.normalize()

    def test_unsafe_and_template_evidence_rejected(self):
        for path in ('../outside.md','javascript:alert(1)','https://user:secret@example.invalid','docs/design/TEMPLATE.md'):
            with self.subTest(path=path), self.assertRaises(build.Invalid):
                build.evidence_path(self.root,path)

    def test_approval_requires_human_and_formal_record(self):
        review=self.approval()
        review['reviewers'][0]['human']=False
        with self.assertRaisesRegex(build.Invalid,'human'):
            self.normalize()
        review['reviewers'][0]['human']=True
        review['approval_record']=None
        with self.assertRaisesRegex(build.Invalid,'formal record'):
            self.normalize()

    def test_unsupported_schema_and_document_status_fail_visibly(self):
        with self.assertRaisesRegex(build.Invalid,'unsupported schema'):
            build.schema_check('x',{'type':'string','pattern':'x'})
        with self.assertRaisesRegex(build.Invalid,'Unsupported document status'):
            build.document_state('- Status: MAGIC')

    def test_review_open_outcome_and_supersession_cycle_rejected(self):
        review=self.round(state='open')
        with self.assertRaisesRegex(build.Invalid,'Open review'):
            self.normalize()
        review.update(state='closed',supersedes=review['id'])
        with self.assertRaisesRegex(build.Invalid,'cycle'):
            self.normalize()

    def test_deterministic_escaped_build_and_all_internal_links(self):
        self.task['title']='<script>synthetic test</script>'
        self.save()
        first=self.root / '_site/first'
        second=self.root / '_site/second'
        for out in (first,second):
            build.build(self.root,out,'2026-09-17T12:00:00Z')
        files={x.relative_to(first) for x in first.rglob('*') if x.is_file()}
        for rel in files:
            self.assertEqual((first / rel).read_bytes(),(second / rel).read_bytes())
        html=(first / 'index.html').read_text()
        self.assertNotIn('<script>synthetic',html)
        self.assertIn('&lt;script&gt;synthetic',html)
        pages={x.resolve():Page(x.read_text()) for x in first.rglob('*.html')}
        for path,page in pages.items():
            for link in page.links:
                parsed=urlsplit(link)
                if parsed.scheme:
                    continue
                target=(path.parent / unquote(parsed.path)).resolve() if parsed.path else path
                self.assertTrue(target.is_file(),link)
                if parsed.fragment:
                    self.assertIn(unquote(parsed.fragment),pages[target].ids,link)

    def test_output_cannot_overwrite_canonical_files_or_retain_unexpected_files(self):
        with self.assertRaisesRegex(build.Invalid,'inside _site'):
            build.build(self.root,self.root / 'project','2026-09-17T12:00:00Z')
        output=self.root / '_site/test'
        output.mkdir(parents=True)
        (output / 'unexpected.txt').write_text('Synthetic stale output')
        with self.assertRaisesRegex(build.Invalid,'Unexpected/stale'):
            build.build(self.root,output,'2026-09-17T12:00:00Z')


class RepositoryReviewTests(unittest.TestCase):
    def test_actual_pr4_history_and_approval_scope(self):
        data=build.normalize(build.ROOT)
        pr=data['tracking']['pull_requests'][0]
        self.assertEqual(pr['number'],4)
        self.assertEqual(pr['state'],'merged')
        self.assertEqual(pr['merge_commit'],'b106610b929cdfa603dd5f1ef2a6e79dbb633a7f')
        rounds=[r for r in data['reviews']['rounds'] if r['document']=='DES-003']
        self.assertEqual([r['outcome'] for r in rounds],['changes requested','changes requested','approved'])
        self.assertEqual(rounds[-1]['target_revision'],pr['head_revision'])
        self.assertTrue(rounds[-1]['target_matches_current'])
        self.assertFalse(rounds[-1]['approval_supported'])
        self.assertIn('later round',rounds[0]['warnings'][0])
        doc=next(d for d in data['tracking']['documents'] if d['id']=='DES-003')
        self.assertEqual(doc['state'],'DRAFT')
        self.assertTrue(any('Formal sign-off is not established' in w for w in doc['warnings']))
        html=build.render(data,{})
        page=Page(html)
        self.assertIn('PR-4',page.ids)
        self.assertTrue(all(r['id'] in page.ids for r in rounds))


if __name__ == '__main__':
    unittest.main()
