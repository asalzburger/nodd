"""Download safety checks using synthetic PDF-like bytes; no network access."""
import hashlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import download


class Response(io.BytesIO):
    def __init__(self, content, length=None):
        super().__init__(content)
        self.headers = {'Content-Length': str(len(content) if length is None else length)}


class DownloadTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'test.pdf'
        self.pdf = b'%PDF-1.7\nSynthetic fixture, not a complete PDF.\n%%EOF\n'

    def test_download_hash_and_no_partial_files(self):
        with patch('download.urllib.request.urlopen', return_value=Response(self.pdf)):
            result = download.download('https://example.invalid/test', self.path)
        self.assertEqual(result['sha256'], hashlib.sha256(self.pdf).hexdigest())
        self.assertEqual(self.path.read_bytes(), self.pdf)
        self.assertEqual(list(self.path.parent.glob('*.part')), [])

    def test_existing_file_preserved_without_network(self):
        self.path.write_bytes(self.pdf)
        with patch('download.urllib.request.urlopen') as request:
            result = download.download('https://example.invalid/test', self.path)
        request.assert_not_called()
        self.assertEqual(result['acquisition'], 'existing-local-file')
        self.assertEqual(self.path.read_bytes(), self.pdf)

    def test_reject_html_and_truncated_responses(self):
        for content, length in ((b'<html>Not a PDF</html>', None), (self.pdf, 999)):
            with self.subTest(content=content), patch('download.urllib.request.urlopen', return_value=Response(content, length)):
                with self.assertRaises(ValueError):
                    download.download('https://example.invalid/test', self.path)
                self.assertFalse(self.path.exists())
                self.assertEqual(list(self.path.parent.glob('*.part')), [])

    def test_sources_require_unique_labels(self):
        source = self.path.with_suffix('.md')
        row = '| TEST-TDR-001 | https://cernbox.cern.ch/s/SyntheticFixture |\n'
        source.write_text(row)
        self.assertEqual(download.sources(source), [('TEST-TDR-001', 'SyntheticFixture')])
        source.write_text(row + row)
        with self.assertRaises(ValueError):
            download.sources(source)


if __name__ == '__main__':
    unittest.main()
