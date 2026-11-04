#!/usr/bin/env python3
"""Reduce macOS sample call trees to main-thread exclusive/cumulative counts."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re


def summarize(text):
    lines=text.split('Call graph:\n',1)[1].split('Total number in stack',1)[0].splitlines()
    nodes=[]
    stack=[]
    total=None
    for line in lines:
        match=re.match(r'^([ +!:|]*)(\d+) (.*)$',line)
        if not match:
            continue
        indent,count,frame=match.groups()
        if 'Thread_' in frame:
            if total is not None:
                break
            total=int(count)
            continue
        while stack and len(indent)<=stack[-1]['indent']:
            stack.pop()
        name=re.split(r'  \(in ',frame)[0]
        node={'name':name,'count':int(count),'indent':len(indent),'children':0,
              'recursive':any(p['name']==name for p in stack)}
        if stack:
            stack[-1]['children']+=node['count']
        nodes.append(node)
        stack.append(node)
    cumulative=Counter()
    exclusive=Counter()
    for node in nodes:
        if not node['recursive']:
            cumulative[node['name']]+=node['count']
        exclusive[node['name']]+=node['count']-node['children']
    return {'main_thread_samples':total,
        'exclusive_top20':exclusive.most_common(20),
        'cumulative_top40':cumulative.most_common(40)}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path)
    p.add_argument('output',type=Path)
    a=p.parse_args()
    a.output.write_text(json.dumps(summarize(a.input.read_text()),indent=2)+'\n')
