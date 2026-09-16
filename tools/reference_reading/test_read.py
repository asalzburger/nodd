"""Synthetic PDFs test extraction and cache contracts without external documents."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pymupdf
import read


class ReadingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'reference/pdfs').mkdir(parents=True)
        self.pdf = self.root/'reference/pdfs/test.pdf'
        with pymupdf.open() as doc:
            p = doc.new_page()
            p.insert_text((72,72), 'Synthetic title\nTest phrase\nwrapped words')
            doc.new_page()
            doc.set_toc([[1,'Test heading',1]])
            doc.set_page_labels([{'startpage':0,'prefix':'','style':'r','firstpagenum':1}])
            doc.save(self.pdf)
        self.manifest = self.root/'reference/manifest.yaml'
        self.manifest.write_text(json.dumps({'sources':[{'id':'SRC-TEST','local_file':'reference/pdfs/test.pdf','sha256':read.sha(self.pdf)}]}))

    def test_extract_and_reuse(self):
        directory, metadata, hit, _ = read.extract(self.root,'SRC-TEST')
        self.assertFalse(hit)
        self.assertEqual(metadata['page_count'],2)
        self.assertEqual(metadata['empty_text_pages'],[2])
        self.assertEqual(metadata['outline_entries'],1)
        pages=json.loads((directory/'pages.json').read_text())
        self.assertEqual(pages[0]['embedded_label'],'i')
        before=(directory/'metadata.json').read_bytes()
        with patch('read.pymupdf.open', side_effect=AssertionError('must reuse cached extraction')):
            _,_,hit,_=read.extract(self.root,'SRC-TEST')
        self.assertTrue(hit)
        self.assertEqual(before,(directory/'metadata.json').read_bytes())

    def test_literal_search_and_page_number(self):
        directory,_,_,_=read.extract(self.root,'SRC-TEST')
        hits=read.search(directory,'phrase wrapped',10)
        self.assertEqual(hits[0]['pdf_page'],1)
        self.assertEqual(read.search(directory,'absent',10),[])
        with self.assertRaises(ValueError): read.search(directory,'',10)

    def test_corrupt_cache_rejected(self):
        directory,_,_,_=read.extract(self.root,'SRC-TEST')
        (directory/'page-0001.txt').write_text('corrupted')
        with self.assertRaisesRegex(ValueError,'Corrupt'):
            read.extract(self.root,'SRC-TEST')

    def test_search_ligatures(self):
        directory,_,_,_=read.extract(self.root,'SRC-TEST')
        # Synthetic extraction output isolates the pure search function.
        (directory/'page-0001.txt').write_text('A module \ufb02ex with a \ufb01ne trace')
        self.assertEqual(read.search(directory,'module flex',10)[0]['pdf_page'],1)

    def test_source_mismatch_rejected(self):
        self.pdf.write_bytes(self.pdf.read_bytes()+b'changed')
        with self.assertRaisesRegex(ValueError,'Source hash'):
            read.extract(self.root,'SRC-TEST')

    def test_configuration_changes_cache_key(self):
        first,_,_,_=read.extract(self.root,'SRC-TEST')
        with patch.dict(read.SETTINGS, {'text_sort':False}):
            second,_,hit,_=read.extract(self.root,'SRC-TEST')
        self.assertNotEqual(first,second)
        self.assertFalse(hit)
        self.assertTrue(first.exists())

    def test_render_and_bounds(self):
        directory,_,_,_=read.extract(self.root,'SRC-TEST')
        result=read.render(self.pdf,directory,[1])
        self.assertEqual(Path(result[0]['path']).read_bytes()[:8],b'\x89PNG\r\n\x1a\n')
        for invalid in (0,3):
            with self.assertRaises(ValueError): read.render(self.pdf,directory,[invalid])


if __name__=='__main__':
    unittest.main()
