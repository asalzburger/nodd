"""Synthetic update-policy cases, independent of actual PR classifications."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import check_update


class UpdatePolicyTests(unittest.TestCase):
    def test_project_pr_requires_record_update(self):
        with self.assertRaisesRegex(ValueError, 'must update'):
            check_update.check('Define synthetic architecture', ['docs/design/TEST.md'])
        self.assertIn('includes a tracking update', check_update.check(
            'Define synthetic architecture', ['docs/design/TEST.md','project/tracking.json']))
        self.assertIn('includes a tracking update', check_update.check(
            'Review synthetic design', ['project/reviews.json']))

    def test_chore_convention_and_non_chore_near_matches(self):
        for title in ('chore: publish synthetic site', 'chore(ci): synthetic cleanup'):
            self.assertIn('excluded',check_update.check(title,['.github/workflows/TEST.yml']))
        for title in ('chore-ish change','chore:','choreography: new design'):
            self.assertFalse(check_update.is_chore(title))
            with self.assertRaises(ValueError):
                check_update.check(title,['.github/workflows/TEST.yml'])

    def test_chore_cannot_bypass_scientific_work(self):
        for path in ('docs/design/TEST.md','docs/signoff/TEST.md','docs/validation/TEST.json',
                     'PROJECT.md','reference/manifest.yaml','src/TEST.cpp','xml/TEST.xml'):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError,'project/scientific'):
                check_update.check('chore: synthetic exemption attempt',[path,'project/tracking.json'])

    def test_metadata_correction_does_not_track_chore(self):
        self.assertIn('excluded',check_update.check('chore: correct synthetic metadata',
                                                   ['project/tracking.json','project/reviews.json']))

    def test_cli_uses_real_git_diff_not_only_title(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            def git(*args):
                return subprocess.check_output(['git','-C',str(root),*args]).decode().strip()
            git('init','-q')
            (root / 'seed.txt').write_text('Synthetic fixture')
            git('add','.')
            git('-c','user.name=Synthetic fixture','-c','user.email=fixture@example.invalid',
                'commit','-qm','Synthetic base')
            base=git('rev-parse','HEAD')
            (root / 'test.txt').write_text('Synthetic project change without records')
            git('add','.')
            git('-c','user.name=Synthetic fixture','-c','user.email=fixture@example.invalid',
                'commit','-qm','Synthetic head')
            event=root / 'event.json'
            data={'pull_request':{'title':'Synthetic project PR','base':{'sha':base},
                                 'head':{'sha':git('rev-parse','HEAD')}}}
            event.write_text(json.dumps(data))
            command=['python3','-B',str(Path(check_update.__file__)),'--event',str(event),'--repo',str(root)]
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(result.returncode,1)
            self.assertIn('must update',result.stderr)
            data['pull_request']['title']='chore: synthetic maintenance'
            event.write_text(json.dumps(data))
            self.assertEqual(subprocess.run(command,capture_output=True).returncode,0)


if __name__ == '__main__':
    unittest.main()
