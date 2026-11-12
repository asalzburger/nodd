"""Curate aggregate campaign provenance and resources without event payloads."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import numpy as np
from angular_sample import save, sha


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--campaign',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    manifest=json.loads((a.campaign/'campaign.json').read_text());rows=[];common=None
    for entry in manifest['batches']:
        base=(a.campaign/entry['input']).parent;run=base/'run';analysis=base/'analysis'
        receipt=json.loads((run/'receipt.json').read_text());proof=json.loads((analysis/'readback.json').read_text())
        feature=json.loads((analysis/'features/receipt.json').read_text())
        if proof['status']!='PASS' or feature['status']!='PASS' or receipt['exit_code'] or receipt['disk_abort']:
            raise ValueError('Incomplete campaign')
        if receipt['events']!=10000 or receipt['threads']!=12:raise ValueError('Different event/worker budget')
        if proof['receipt_sha256']!=sha(run/'receipt.json') or feature['readback_sha256']!=sha(analysis/'readback.json'):
            raise ValueError('Changed audit binding')
        if feature['feature_sha256']!=sha(analysis/'features/features.npz'):raise ValueError('Changed features')
        if receipt['sample_sha256']!=entry['sample_sha256'] or sha(base/'input/sample.json')!=entry['sample_sha256']:
            raise ValueError('Changed campaign input')
        for worker in proof['workers']:
            if worker['begin_run_rng_seed']!=receipt['seed']:raise ValueError('Worker seed differs')
            policy={k:v for k,v in worker.items() if k not in ('thread_id','events','begin_run_rng_seed')}
            if common is None:common=policy
            if policy!=common:raise ValueError('Worker physical policies differ across campaign')
        rows.append(dict(entry=entry,execution={k:v for k,v in receipt.items() if k!='command'},
            readback={k:v for k,v in proof.items() if k not in ('sample','workers')},feature_receipt=feature))
    if sum(r['execution']['events'] for r in rows)!=120000:raise ValueError('Incomplete120kcampaign')
    times=[datetime.fromisoformat(r['execution'][k]) for r in rows for k in ('started_at','ended_at')]
    result=dict(status='PROTOTYPE complete audited120k staggered campaign',campaign=manifest,
        campaign_sha256=sha(a.campaign/'campaign.json'),producer_sha256=sha(__file__),batches=rows,
        common_native_worker_policy=common,scope='Unchanged staggered geometry; no detector acceptance',
        total_events=120000,total_ROOT_bytes=sum(r['execution']['output_bytes'] for r in rows),
        summed_transport_wall_seconds=sum(r['execution']['wall_seconds'] for r in rows),
        transport_campaign_elapsed_seconds=(max(times)-min(times)).total_seconds(),
        summed_transport_cpu_seconds=sum(r['execution']['cpu_seconds'] for r in rows),
        peak_transport_child_rss_bytes=max(r['execution']['peak_rss_bytes'] for r in rows),
        minimum_recorded_free_bytes_after=min(r['execution']['free_bytes_after'] for r in rows))
    # Old10k comparison is a regression control; never use new validation labels.
    old=Path('build/ecal-staggering/staggered-features/features.npz')
    control=Path('build/ecal-highstat/legacy-fast-frozen/features/features.npz')
    if old.exists() and control.exists():
        differences={}
        with np.load(old) as x,np.load(control) as y:
            for key in x.files:
                if x[key].dtype.kind in 'biu':
                    if not np.array_equal(x[key],y[key]):raise ValueError('Legacy identity/axis regression')
                    differences[key]=0.
                else:
                    np.testing.assert_allclose(x[key],y[key],rtol=1e-10,atol=1e-10)
                    differences[key]=float(np.max(abs(x[key]-y[key])))
        result['legacy_full10k_regression']=dict(status='PASS',events=10000,relative_tolerance=1e-10,
            absolute_tolerance=1e-10,maximum_absolute_differences=differences,
            old_feature_sha256=sha(old),new_feature_sha256=sha(control),
            new_readback_sha256=sha(control.parent.parent/'readback.json'))
    if len(json.dumps(result))>500000:raise ValueError('Unexpectedly large aggregate')
    a.output.parent.mkdir(parents=True,exist_ok=True);save(a.output,result)


if __name__=='__main__':main()
