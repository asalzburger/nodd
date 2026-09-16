#!/usr/bin/env python3
"""Known-answer retrieval and page-location checks for the two local pilot PDFs."""
import json
import re
import time

import read


def main():
    output = []
    checks = {
        'SRC-ATLAS-TDR-030': [('Breakdown of material budget',224),('Pixel module Hybridization',199)],
        'SRC-RD53A': [('Floorplan and Organization',6),('Power supply limits',8)],
    }
    for source_id, questions in checks.items():
        started = time.perf_counter()
        _, directory, metadata = read.load_cache(read.ROOT,source_id)
        pages = json.loads((directory/'pages.json').read_text())
        if [p['pdf_page'] for p in pages] != list(range(1,metadata['page_count']+1)):
            raise ValueError('Page coverage is incomplete')
        results=[]
        for query, expected in questions:
            hits=read.search(directory,query,1000)
            locations=[hit['pdf_page'] for hit in hits]
            if expected not in locations:
                raise ValueError(f'{source_id}: expected PDF page {expected} for {query}')
            results.append({'query':query,'expected_pdf_page':expected,'found_pdf_pages':locations})
        if source_id=='SRC-RD53A':
            for number in range(2,80):
                text=(directory/f'page-{number:04d}.txt').read_text().strip()
                if not re.search(r'–\s*'+str(number-1)+r'\s*–$',text):
                    raise ValueError('Unexpected RD53A printed-page footer')
        output.append({'source_id':source_id,'source_sha256':metadata['provenance']['source_sha256'],
                       'page_count':len(pages),'queries':results,'elapsed_seconds':time.perf_counter()-started,
                       'status':'PASS'})
    print(json.dumps(output,indent=2))


if __name__=='__main__':
    main()
