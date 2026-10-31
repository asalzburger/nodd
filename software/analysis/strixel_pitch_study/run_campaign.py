#!/usr/bin/env python3
"""Run the DES042 native pitch matrix or separate Gaussian diagnostic control."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
SUPPLIERS=('nodd_dir','build_dir','native_module_dir','observer_module_dir',
           'material_module_dir','comparison_dir')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign',type=Path,default=Path(__file__).with_name('campaign.json'))
    parser.add_argument('--output',type=Path,default=ROOT/'build/strixel-pitch-study')
    parser.add_argument('--tag',required=True,help='Fresh filename-safe run label; existing results are never overwritten')
    parser.add_argument('--jobs',type=int,default=3)
    parser.add_argument('--events',type=int,help='Default20000 geometric or5000 Gaussian-control events/case')
    parser.add_argument('--response',choices=('geometric','gaussian-control'),default='geometric')
    parser.add_argument('--dry-run',action='store_true')
    for name in SUPPLIERS:parser.add_argument('--'+name.replace('_','-'),type=Path,required=True)
    args=parser.parse_args()
    if args.events is None:args.events=5000 if args.response=='gaussian-control' else 20000
    if not args.tag or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in args.tag):
        parser.error('Use letters, numbers, dash or underscore in the fresh tag')
    if args.jobs<1 or args.events<1:parser.error('Positive jobs and events required')
    config=json.loads(args.campaign.read_text())
    cases=[]
    momenta=[100.] if args.response=='gaussian-control' else config['pt_GeV']
    prefix='gaussian' if args.response=='gaussian-control' else 'full'
    script='nodd_strixel_gaussian_control.py' if args.response=='gaussian-control' else 'nodd_strixel_pitch_truth.py'
    for pt in momenta:
        for pitch in config['short_strip_local_v_pitch_mm']:
            label=f'{prefix}-{args.tag}-pitch{pitch:g}-pt{pt:g}'.replace('.','p')
            output=args.output.resolve()/label
            if output.exists() or output.with_suffix('.log').exists():
                parser.error('Select a fresh tag; existing output '+str(output))
            command=[sys.executable,str(ROOT/'software/running'/script),
                     '--campaign',str(args.campaign.resolve()),'--pitch',str(pitch),'--pt',str(pt),
                     '--events',str(args.events),'--threads','1','--output',str(output)]
            for name in SUPPLIERS:command+=['--'+name.replace('_','-'),str(getattr(args,name).resolve())]
            cases.append((label,output,command))
    if args.dry_run:
        print(json.dumps([dict(case=label,command=command) for label,_,command in cases],indent=2));return
    args.output.mkdir(parents=True,exist_ok=True)
    def run(item):
        label,output,command=item
        with output.with_suffix('.log').open('w') as stream:
            result=subprocess.run(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
        print(label,'exit',result.returncode,flush=True)
        return result.returncode
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:codes=list(pool.map(run,cases))
    if any(codes):raise SystemExit('One or more native cases failed; keep logs and choose fresh output for repairs')


if __name__=='__main__':main()
