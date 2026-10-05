#!/usr/bin/env python3
"""Losslessly archive bulky generated JSON after validation, keeping review diffs small."""
import argparse
import gzip
from pathlib import Path


def archive(root):
    files=list(root.glob('*/summary.json'))+list(root.glob('*/acts*/native-target-audit.json'))
    for path in files:
        raw=path.read_bytes();output=path.with_suffix(path.suffix+'.gz')
        compressed=gzip.compress(raw,mtime=0)
        if gzip.decompress(compressed)!=raw:raise RuntimeError('Archive round-trip failed')
        output.write_bytes(compressed)
        if gzip.decompress(output.read_bytes())!=raw:raise RuntimeError('Written archive differs')
        path.unlink()  # Only the verified, losslessly archived generated source.
    print('Losslessly archived',len(files),'generated JSON files')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);a=p.parse_args();archive(a.run)
