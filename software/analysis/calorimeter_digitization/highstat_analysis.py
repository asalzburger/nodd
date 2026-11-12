"""Freeze training-only calibrations, then evaluate an independent campaign split."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
import numpy as np
from angular_sample import ROOT, save, sha
from angular_analyze import ETA_EDGES, PHI_EDGES, bin_index, folded_phi
from staggered_results import moments, interval, population
from highstat_model import stages, fit, restore

SERIES = ('raw', 'historical_10k', 'original_pre', 'original_closed', 'spline_pre', 'spline_closed')
CONTRASTS = ((0,5,'raw_minus_spline'),(1,5,'historical_minus_spline'),(3,5,'original_minus_spline'))
ENERGY_EDGES = np.linspace(10,80,15)


def interval_diagnostics(samples, point):
    result=interval(samples)
    if np.isfinite(samples).all() and point is not None and np.isfinite(point):
        result.update(bootstrap_mean=float(np.mean(samples)),bootstrap_median=float(np.median(samples)),
            bootstrap_mean_minus_point=float(np.mean(samples)-point),
            bootstrap_median_minus_point=float(np.median(samples)-point),
            bootstrap_fraction_below_point=float(np.mean(samples<point)))
    return result


def revision():
    return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()


def feature_signature(receipt):
    keys=('feature_names','producer_sha256','feature_recipe_sha256','geometry_helper_sha256')
    if any(k not in receipt for k in keys):raise ValueError('Incomplete feature semantics signature')
    return {k:receipt[k] for k in keys}


def load_split(campaign, split, expected_signature=None):
    manifest = json.loads((campaign/'campaign.json').read_text()); arrays=[]; receipts=[]; pending=[]
    signature=expected_signature
    for entry in manifest['batches']:
        if entry['split'] != split:continue
        base=campaign/entry['input']; folder=base.parent/'analysis/features'
        receipt=json.loads((folder/'receipt.json').read_text())
        proof=folder.parent/'readback.json'
        if receipt['status']!='PASS' or receipt['feature_sha256']!=sha(folder/'features.npz'):
            raise ValueError('Changed/failed feature batch')
        if receipt['readback_sha256']!=sha(proof) or receipt['sample_sha256']!=entry['sample_sha256']:
            raise ValueError('Changed feature/readback/input binding')
        if receipt['compact_sha256']!=manifest['geometry_hashes']['detector.xml']:
            raise ValueError('Different campaign geometry')
        observed=feature_signature(receipt)
        if signature is None:signature=observed
        if observed!=signature:raise ValueError('Changed feature semantics across campaign or frozen training/validation')
        pending.append((entry,folder,receipt))
    # Check every batch's semantics before opening any validation feature array.
    for entry,folder,receipt in pending:
        with np.load(folder/'features.npz',allow_pickle=False) as source:
            d={k:source[k].copy() for k in source.files}
        expected=np.arange(entry['event_offset'],entry['event_offset']+entry['events'])
        if not np.array_equal(d['event'],expected):raise ValueError('Batch global event identities differ')
        arrays.append(d);receipts.append(receipt)
    data={k:np.concatenate([d[k] for d in arrays]) for k in arrays[0]}
    n=100000 if split=='train' else 20000; offset=0 if split=='train' else 100000
    if not np.array_equal(data['event'],np.arange(offset,offset+n)):
        raise ValueError('Incomplete independent sample')
    return data, receipts


def infer(model,data):
    return model.infer(data['features'],data['signal'],data['region'],data['valid_axis'])


def train(args):
    data,receipts=load_split(args.campaign,'train');role=stages()
    models={kind:fit(data,role,kind) for kind in ('original','spline')}
    result=dict(status='PROTOTYPE frozen before independent validation',source_revision=revision(),
        core_sha256=sha(Path(__file__).with_name('highstat_model.py')),producer_sha256=sha(__file__),
        campaign_sha256=sha(args.campaign/'campaign.json'),training_feature_receipts=receipts,
        feature_semantics=feature_signature(receipts[0]),
        roles=dict(seed=13395200,fit=70000,tuning=15000,closure=15000,response_refit=85000,
                   assignment_sha256=hashlib.sha256(role.tobytes()).hexdigest()),
        models={k:m.record() for k,m in models.items()},
        validation_performance_inspected=False,definition='Training-only selection,85krefit and15k global closure including zeros; fresh20k performance uninspected')
    args.output.mkdir(parents=True,exist_ok=False);save(args.output/'models.json',result)
    print(json.dumps({k:dict(closure=m.closure,choices=[s['choice'] for s in m.selection]) for k,m in models.items()},indent=2),flush=True)


def historical(data,reference):
    records=reference['models']['staggered'];energy=np.zeros(len(data['signal']));clipped=np.zeros(len(energy),bool)
    for outer in range(5):
        pair=[r for r in records if r['outer_fold']==outer]
        value=data['signal']/pair[0]['fallback_global_response']
        for record in pair:
            selected=data['valid_axis']&(data['region']==record['region']);m=record['model']
            predicted=np.column_stack([np.ones(selected.sum()),data['features'][selected]])@np.array(m['coefficient'])
            value[selected]=data['signal'][selected]/m['response_scale']/np.clip(predicted,1/3,2)
            clipped[selected]|=(predicted<1/3)|(predicted>2)
        energy+=value/5
    return energy/data['energy'],clipped


def predictions(data,models,old):
    a,b=[infer(models[k],data) for k in ('original','spline')]
    values=np.array([data['response'],old,a['pre_energy']/data['energy'],a['energy']/data['energy'],
                     b['pre_energy']/data['energy'],b['energy']/data['energy']])
    tails=values.copy();tails[0]=data['signal']/models['original'].fallback_response/data['energy']
    for i,j in ((2,3),(4,5)):
        assert np.isclose(values[i].std(ddof=1)/values[i].mean(),values[j].std(ddof=1)/values[j].mean(),rtol=1e-12)
    return values,tails,a,b


def evaluate(args):
    # Git object equality prevents accidental validation inspection before freeze.
    path=args.models.resolve();relative=path.relative_to(ROOT)
    frozen=subprocess.check_output(['git','show',f'{args.freeze_commit}:{relative}'],cwd=ROOT)
    if hashlib.sha256(frozen).hexdigest()!=sha(path):raise ValueError('Models differ from the committed freeze')
    record=json.loads(frozen)
    if record['core_sha256']!=sha(Path(__file__).with_name('highstat_model.py')):
        raise ValueError('Calibration inference/training source changed after freeze')
    if record['producer_sha256']!=sha(__file__):raise ValueError('Analysis procedure changed after freeze')
    if record['campaign_sha256']!=sha(args.campaign/'campaign.json'):raise ValueError('Campaign changed after fit')
    train_data,train_receipts=load_split(args.campaign,'train')
    if train_receipts!=record['training_feature_receipts']:raise ValueError('Training features changed after freeze')
    data,receipts=load_split(args.campaign,'validation',record['feature_semantics'])
    models={k:restore(v) for k,v in record['models'].items()}
    old,old_clipped=historical(data,json.loads(args.reference.read_text()))
    values,tails,a,b=predictions(data,models,old)
    categories=[np.zeros(20000,int),bin_index(abs(data['eta']),ETA_EDGES),
                bin_index(folded_phi(data['phi']),PHI_EDGES),bin_index(data['energy'],ENERGY_EDGES)]
    def metrics(vv,tt,count):
        out=np.empty((6,4,35))
        for k in range(6):
            means=[];widths=[];tail=[];rms=[]
            for j,c in enumerate(categories):
                n=1 if j==0 else (14 if j==3 else 10)
                m,w=moments(vv[k],c,count,n);means.extend(m);widths.extend(w)
                tail.extend(moments((tt[k]<.5).astype(float),c,count,n)[0])
                rms.extend(np.sqrt(moments((tt[k]-1)**2,c,count,n)[0]))
            out[k]=[means,widths,tail,rms]
        return out
    conditional=np.zeros((args.bootstrap,6,4,35));full=np.zeros((args.training_bootstrap,6,4,35))
    rng=np.random.default_rng(13395300);start=time.monotonic()
    for i in range(args.bootstrap):
        count=np.bincount(rng.integers(20000,size=20000),minlength=20000)
        conditional[i]=metrics(values,tails,count)
    role=stages();training_rng=np.random.default_rng(13395400);closures=[];selection=[]
    for i in range(args.training_bootstrap):
        count=np.zeros(100000)
        for r in range(3):
            ids=np.flatnonzero(role==r)
            count+=np.bincount(training_rng.choice(ids,size=len(ids),replace=True),minlength=100000)
        fitted={k:fit(train_data,role,k,count) for k in ('original','spline')}
        vv,tt,_,_=predictions(data,fitted,old)
        validation_count=np.bincount(training_rng.integers(20000,size=20000),minlength=20000)
        full[i]=metrics(vv,tt,validation_count)
        closures.append({k:m.closure for k,m in fitted.items()})
        selection.append({k:[s['choice'] for s in m.selection] for k,m in fitted.items()})
        if (i+1)%10==0:print(f'Within-role full selection/refit/closure+test bootstrap{i+1}/{args.training_bootstrap}: {time.monotonic()-start:.1f}s',flush=True)
    point_predictions=[None,dict(clipped=old_clipped),a,a,b,b]
    def stats(selected,index=None):
        result={}
        for k,label in enumerate(SERIES):
            entry=population(values[k],tails[k],selected,data,point_predictions[k])
            entry['fractional_error_RMS']=float(np.sqrt(np.mean((tails[k,selected]-1)**2)))
            if k>=2:entry['feature_extrapolated_events']=int(point_predictions[k]['feature_extrapolated'][selected].sum())
            if index is not None:
                for j,key in enumerate(('mean','fractional_width','tail_fraction','fractional_error_RMS')):
                    entry[key+'_conditional']=interval_diagnostics(conditional[:,k,j,index],entry[key])
                    entry[key+'_full']=interval_diagnostics(full[:,k,j,index],entry[key])
            result[label]=entry
        return result
    projections={};hist_edges={'raw':np.linspace(0,max(.5,np.ceil(values[0].max()*200)/2),61),
                                'calibrated':np.linspace(0,max(1,np.ceil(values[1:].max()*2)/2),81)}
    for axis,(name,edges) in enumerate((('abs_eta',ETA_EDGES),('folded_phi',PHI_EDGES))):
        bins=[]
        for j in range(10):
            selected=categories[axis+1]==j;index=1+axis*10+j;ss=stats(selected,index)
            for k,label in enumerate(SERIES):
                key='raw' if k==0 else 'calibrated';vv=values[k,selected]*(100 if k==0 else 1)
                counts,_=np.histogram(vv,bins=hist_edges[key]);assert counts.sum()==selected.sum()
                ss[label]['histogram_counts']=counts.tolist()
            contrasts={}
            for left,right,label in CONTRASTS:
                point=ss[SERIES[left]]['fractional_width']-ss[SERIES[right]]['fractional_width']
                contrasts[label]=dict(value=point,
                    conditional=interval_diagnostics(conditional[:,left,1,index]-conditional[:,right,1,index],point),
                    full=interval_diagnostics(full[:,left,1,index]-full[:,right,1,index],point))
            bins.append(dict(low=float(edges[j]),high=float(edges[j+1]),series=ss,contrasts=contrasts))
        projections[name]=dict(edges=edges.tolist(),unit='dimensionless' if axis==0 else 'rad',bins=bins)
    energy=[dict(low=float(ENERGY_EDGES[j]),high=float(ENERGY_EDGES[j+1]),series=stats(categories[3]==j,21+j)) for j in range(14)]
    controls={}
    for name,c in [('signed_eta',bin_index(data['eta'],np.linspace(-3,3,21))),
                   ('sector',np.floor((data['phi']+np.pi/16)%(2*np.pi)/(np.pi/8)).astype(int)),
                   ('reconstructed_region',data['region'])]:
        controls[name]={str(j):stats(c==j) for j in sorted(set(c))}
    covariance={}
    for name,samples in [('conditional',conditional),('full',full)]:
        widths=samples[:,:,1,1:21].reshape(len(samples),120)
        contrasts=np.concatenate([samples[:,a,1,1:21]-samples[:,b,1,1:21] for a,b,_ in CONTRASTS],axis=1)
        covariance[name]=dict(width=np.cov(widths,rowvar=False).tolist(),contrast=np.cov(contrasts,rowvar=False).tolist())
    result=dict(status='PROTOTYPE independent20k validation',events=20000,training_events=100000,
        freeze_commit=args.freeze_commit,models_sha256=sha(path),source_revision=revision(),producer_sha256=sha(__file__),
        core_sha256=record['core_sha256'],historical_reference_sha256=sha(args.reference),validation_feature_receipts=receipts,
        definition='Inclusive sampleSD/mean; rawR=S/Etrue; all otherR=Eestimated/Etrue. Raw tails/RMS use training-only global scale S/R0.',
        historical_definition='Ensemble of5old10kouter models; any-member gain clipping reported; old training uncertainty conditioned on.',
        uncertainty=dict(conditional_replicates=args.bootstrap,conditional_seed=13395300,
            full_replicates=args.training_bootstrap,full_seed=13395400,
            full_method='Independent within70k/15k/15k role resampling, repeated preprocessing/knots/tuning/85krefit/15kclosure and common20kvalidation resampling; includes model selection.',
            intervals='Approximate pointwise95% percentile; 200full replicas give coarse tail precision'),
        global_statistics=stats(np.ones(20000,bool),0),projections=projections,energy_slices=energy,controls=controls,
        histogram_edges={k:v.tolist() for k,v in hist_edges.items()},covariance=covariance,
        width_covariance_order=[f'{s}:{axis}:{j}' for s in SERIES for axis in projections for j in range(10)],
        contrast_covariance_order=[f'{s}:{axis}:{j}' for _,_,s in CONTRASTS for axis in projections for j in range(10)],
        bootstrap_closure_factors=closures,bootstrap_model_choices=selection)
    args.output.mkdir(parents=True,exist_ok=False);save(args.output/'summary.json',result)
    np.savez_compressed(args.predictions_output,values=values,tails=tails,event=data['event'])
    print('Independent validation comparison completed',flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='stage',required=True)
    a=sub.add_parser('train');a.add_argument('--campaign',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    a=sub.add_parser('evaluate');a.add_argument('--campaign',type=Path,required=True);a.add_argument('--models',type=Path,required=True)
    a.add_argument('--freeze-commit',required=True);a.add_argument('--output',type=Path,required=True)
    a.add_argument('--predictions-output',type=Path,required=True);a.add_argument('--bootstrap',type=int,default=1000)
    a.add_argument('--training-bootstrap',type=int,default=200)
    a.add_argument('--reference',type=Path,default=ROOT/'docs/validation/ecal-staggering/results/summary.json')
    args=parser.parse_args();(train if args.stage=='train' else evaluate)(args)


if __name__=='__main__':main()
