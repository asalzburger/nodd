"""Explicit corrected-proof entry point; frozen observer statistics and plots."""
import argparse
import json
from pathlib import Path
import subprocess

import numpy as np

import observed_compare as frozen
from observed_reaudit import evidence
from geometry import ROOT,sha,load,save


def analyze(args):
    if args.bootstrap!=1000 or args.seed!=13001000:raise ValueError('Frozen1000 bootstrap and seed13001000 required')
    loaded={variant:evidence(getattr(args,variant),production=True) for variant in ('standard','candidate')}
    a,ra,pa=loaded['standard'];b,rb,pb=loaded['candidate']
    if len(a)!=10000 or len(b)!=10000 or ra['variant']!='standard' or rb['variant']!='candidate':raise ValueError('Need two complete correctly labeled10000-event corrected proofs')
    if ra['library_sha256']!=rb['library_sha256'] or ra['native_report_sha256']!=rb['native_report_sha256']:raise ValueError('Corrected comparison configuration differs')
    primary=np.array([[r[k] for k in ('energy_GeV','eta','phi')] for r in a])
    if not np.array_equal(primary,np.array([[r[k] for k in ('energy_GeV','eta','phi')] for r in b])):raise ValueError('Unmatched corrected primary vectors')
    values={variant:{key:np.array([r[key+'_GeV']/r['energy_GeV'] for r in rows]) for key in ('H','A','S','U')}
            for variant,(rows,_,_) in loaded.items()}
    bounds={variant:np.array([r['native_closure_bound_GeV']/r['energy_GeV'] for r in rows]) for variant,(rows,_,_) in loaded.items()}
    failed={variant:np.array([sum(t['failed_steps'] for t in r['collections'].values()) for r in rows]) for variant,(rows,_,_) in loaded.items()}
    result=frozen.summarize(primary,values,bounds,failed,args.bootstrap,args.seed)
    result.update(status='PROTOTYPE',analyzer=dict(path=str(Path(__file__).relative_to(ROOT)),sha256=sha(__file__),
        revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()),
        statistical_helper=dict(path=str(Path(frozen.__file__).relative_to(ROOT)),sha256=sha(frozen.__file__),unchanged=True),
        readback_addendum_sha256=sha(ROOT/'docs/validation/lar-gap10k/readback-addendum.md'),
        observer_protocol_sha256=sha(ROOT/'docs/validation/lar-gap10k/observer-protocol.md'),
        evidence={variant:dict(reaudit_sha256=sha(getattr(args,variant)/'reaudit.json'),receipt_sha256=proof['receipt_sha256'],
            corrected_auditor=proof['auditor'],derived_ledger_sha256=proof['derived_ledger_sha256'],native_alias_catalog=proof['native_alias_catalog'],
            replay=proof['replay'],failed_steps=proof['failed_steps']) for variant,(_,_,proof) in loaded.items()},
        interpretation='Separate corrected readback of immutable observed transport; fresh matched H/E and independent A/E. Logical/physical names use the exact native catalog; physics, guard and RNG are unchanged. Complete A does not validate cell readout. No intrinsic-resolution, engineering acceptance or digitization claim.')
    args.output.mkdir(parents=True,exist_ok=False)
    covariance=dict(order=result.pop('width_covariance_order'),matrix=result.pop('width_covariance'))
    save(args.output/'width-covariance.json',covariance)
    result['width_covariance']=dict(file='width-covariance.json',sha256=sha(args.output/'width-covariance.json'),variables=len(covariance['order']))
    text=json.dumps(result,separators=(',',':'),allow_nan=False)+'\n'
    if len(text.encode())>=1024**2:raise ValueError('Corrected compact summary exceeds1MiB')
    (args.output/'summary.json').write_text(text)
    print(json.dumps({variant:result['missing'][variant]['global'][0] for variant in values},indent=2))


def plot(args):
    frozen.plot(args)
    save(args.output/'reaudit-render.json',dict(summary_sha256=sha(args.summary),
        entrypoint=dict(path=str(Path(__file__).relative_to(ROOT)),sha256=sha(__file__)),
        frozen_plotter=dict(path=str(Path(frozen.__file__).relative_to(ROOT)),sha256=sha(frozen.__file__)),
        render_sha256=sha(args.output/'render.json')))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='stage',required=True)
    a=sub.add_parser('analyze')
    for name in ('standard','candidate','output'):a.add_argument('--'+name,type=Path,required=True)
    a.add_argument('--bootstrap',type=int,default=1000);a.add_argument('--seed',type=int,default=13001000)
    a=sub.add_parser('plot')
    for name in ('summary','output'):a.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args();globals()[args.stage](args)
