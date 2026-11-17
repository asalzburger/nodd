"""Complete A/E and saved H/E comparison with a frozen original tail threshold."""
import argparse
import json
import math
from pathlib import Path
import subprocess

import numpy as np

import compare as gap
from geometry import ROOT,sha,load,save
from observed_transport import evidence,sum_bound

TAIL_THRESHOLD=0.07966135709622409
SERIES=('standard_H','standard_A','candidate_H','candidate_A')
STATISTICS=('mean_response','fractional_width','common_tail_fraction')


def variance(values):
    mean=math.fsum(values)/len(values)
    return math.fsum((x-mean)**2 for x in values)/(len(values)-1)


def variance_identity(a,s,u,h,bounds):
    """Native S + U identity; saved H includes its separately reported rounding."""
    n=len(a);mu=math.fsum(u)/n;ms=math.fsum(s)/n
    cov=math.fsum((x-ms)*(y-mu) for x,y in zip(s,u))/(n-1)
    shift=variance(u)+2*cov;observed=variance(a)-variance(s)
    b=max(bounds)+sum_bound(8,float(max(map(abs,a),default=0.)))
    # Bounded native closure residual e: |var(S+U+e)-var(S+U)|
    residual_bound=n/(n-1)*b*b+2*math.sqrt(variance(s+u))*math.sqrt(n/(n-1))*b
    arithmetic=sum_bound(20*n,abs(observed)+abs(shift)+variance(a)+variance(s)+variance(u))
    if abs(observed-shift)>residual_bound+arithmetic:raise ValueError('Native missing-energy variance identity failed')
    mean_residual=math.fsum(a-s-u)/n
    if abs(mean_residual)>math.fsum(bounds)/n+sum_bound(8,float(max(map(abs,a),default=0.))):raise ValueError('Native missing-energy mean identity failed')
    epsilon=h-s
    return dict(mean_delta_U_over_E=mu,sample_sd_delta=math.sqrt(variance(u)),sample_variance_delta=variance(u),
        covariance_S_over_E_delta=cov,native_variance_shift=observed,predicted_native_variance_shift=shift,
        variance_identity_residual=observed-shift,variance_identity_bound=residual_bound+arithmetic,
        mean_identity_residual=mean_residual,mean_saved_minus_native_rounding=math.fsum(epsilon)/n,
        observed_mean_A_minus_H=math.fsum(a-h)/n,predicted_mean_A_minus_H=mu-math.fsum(epsilon)/n,
        interpretation='A independently accumulated; native A=S+U within derived floating-point bounds. Saved H is float32 cell output; epsilon=H-S is retained explicitly.')


def summarize(primary,values,bounds,failed,replicates=1000,seed=13001000,threshold=TAIL_THRESHOLD):
    if threshold!=TAIL_THRESHOLD:raise ValueError('Original frozen common tail threshold must remain unchanged')
    n=len(primary);categories=gap.categories(primary);bins={axis:1 if axis=='global' else len(gap.AXES[axis])-1 for axis in categories}
    responses={key:values[key.split('_')[0]][key.split('_')[1]] for key in SERIES}
    if any(len(r)!=n or np.any(~np.isfinite(r)) or np.any(r<0) for r in responses.values()):raise ValueError('Invalid observed response vector')
    bootstrap={key:{axis:np.empty((replicates,bins[axis],3)) for axis in categories} for key in SERIES}
    delta_boot={key:{axis:np.empty((replicates,bins[axis],2)) for axis in categories} for key in values}
    rng=np.random.default_rng(seed)
    for b in range(replicates):
        weights=np.bincount(rng.integers(n,size=n),minlength=n)
        for axis,cat in categories.items():
            for key,response in responses.items():
                stats=gap.weighted(response,cat,weights,bins[axis],threshold)
                bootstrap[key][axis][b]=stats[:,[0,2,3]]
            for key,data in values.items():
                mean=gap.weighted(data['U'],cat,weights,bins[axis],threshold)[:,0]
                delta_boot[key][axis][b,:,0]=mean
                with np.errstate(invalid='ignore',divide='ignore'):
                    native_u=gap.weighted(data['U']*primary[:,0],cat,weights,bins[axis],threshold)[:,0]
                    native_a=gap.weighted(data['A']*primary[:,0],cat,weights,bins[axis],threshold)[:,0]
                    delta_boot[key][axis][b,:,1]=native_u/native_a
    models={}
    for key,r in responses.items():
        variant,kind=key.split('_');entry=dict(label=f'LAr {800 if variant=="standard" else 400} mm gap · '+('saved H/E' if kind=='H' else 'complete accepted A/E'),projections={})
        for axis,cat in categories.items():
            rows=[]
            for i in range(bins[axis]):
                selected=r[cat==i];row=gap.statistics(selected,threshold,float(r.mean())*.5)
                for j,stat in enumerate(STATISTICS):row[stat+'_bootstrap']=gap.retained.interval(bootstrap[key][axis][:,i,j])
                rows.append(row)
            if axis=='global':entry['global']=rows[0]
            else:entry['projections'][axis]=dict(edges=gap.AXES[axis].tolist(),bins=rows,unit='GeV' if axis=='energy' else 'rad' if axis=='full_phi' else 'dimensionless')
        edges=np.linspace(0,.6,121);entry['raw_response_histogram']=dict(edges=edges.tolist(),counts=np.histogram(r,edges)[0].tolist(),events=n,
            underflow=int(np.count_nonzero(r<edges[0])),overflow=int(np.count_nonzero(r>edges[-1])))
        models[key]=entry
    def contrasts(left,right):
        result={}
        for axis in categories:
            rows=[]
            for i in range(bins[axis]):
                a=models[left]['global'] if axis=='global' else models[left]['projections'][axis]['bins'][i]
                b=models[right]['global'] if axis=='global' else models[right]['projections'][axis]['bins'][i]
                rows.append({stat:dict(difference=a[stat]-b[stat],**gap.retained.interval(bootstrap[left][axis][:,i,j]-bootstrap[right][axis][:,i,j])) for j,stat in enumerate(STATISTICS)})
            result[axis]=rows
        return result
    missing={}
    for variant,data in values.items():
        output={}
        for axis,cat in categories.items():
            rows=[]
            for i in range(bins[axis]):
                take=cat==i;energy=primary[take,0];u=data['U'][take];a=data['A'][take]
                row=variance_identity(a,data['S'][take],u,data['H'][take],bounds[variant][take])
                row.update(events=int(np.count_nonzero(take)),affected_primaries=int(np.count_nonzero(u>0)),failed_steps=int(np.sum(failed[variant][take])),
                    sum_U_GeV=float(np.dot(u,energy)),sum_A_GeV=float(np.dot(a,energy)),
                    delta_quantiles=dict(zip(('q00','q50','q99','q100'),map(float,np.quantile(u,[0.,.5,.99,1.])))),
                    missing_fraction_sum_U_over_sum_A=float(np.dot(u,energy)/np.dot(a,energy)),
                    mean_delta_bootstrap=gap.retained.interval(delta_boot[variant][axis][:,i,0]),
                    missing_fraction_bootstrap=gap.retained.interval(delta_boot[variant][axis][:,i,1]),
                    projection_coordinate='Frozen PRIMARY '+axis+'; failures retain no invented canonical cell')
                rows.append(row)
            output[axis]=rows
        missing[variant]=output
    order=[];columns=[]
    for key in SERIES:
        for axis in ('global','abs_eta','fine_transition'):
            for i in range(bins[axis]):order.append(f'{key}:{axis}:{i}:fractional_width');columns.append(bootstrap[key][axis][:,i,1])
    matrix=np.asarray(columns)
    if not np.all(np.isfinite(matrix)):raise ValueError('Undefined joint observer covariance')
    views={}
    for kind in ('H','A'):
        views[kind]=dict(models={v:models[v+'_'+kind] for v in ('standard','candidate')},candidate_minus_standard=contrasts('candidate_'+kind,'standard_'+kind),
            common_tail=dict(threshold_R=threshold,definition='Original retained standard saved-hit GLOBAL threshold; fixed across H/A, all bins and bootstrap replicates'))
    return dict(events=n,views=views,missing=missing,within_geometry_A_minus_H={v:contrasts(v+'_A',v+'_H') for v in values},
        bootstrap=dict(replicates=replicates,seed=seed,resampling='One shared whole-primary-event multiplicity vector across both geometries, H/A/U and all projections; pointwise95% percentile'),
        width_covariance_order=order,width_covariance=np.cov(matrix,ddof=1).tolist())


def analyze(args):
    if args.bootstrap!=1000 or args.seed!=13001000:raise ValueError('Frozen1000 bootstrap/seed13001000 required')
    loaded={v:evidence(getattr(args,v),production=True) for v in ('standard','candidate')}
    a,ra,pa=loaded['standard'];b,rb,pb=loaded['candidate']
    if len(a)!=10000 or len(b)!=10000 or ra['variant']!='standard' or rb['variant']!='candidate':raise ValueError('Need both complete labeled10000-primary observed geometries')
    if ra['library_sha256']!=rb['library_sha256'] or ra['native_report_sha256']!=rb['native_report_sha256']:raise ValueError('Observer comparison configuration differs')
    primary=np.array([[r[k] for k in ('energy_GeV','eta','phi')] for r in a])
    if not np.array_equal(primary,np.array([[r[k] for k in ('energy_GeV','eta','phi')] for r in b])):raise ValueError('Unmatched observed primary vectors')
    values={v:{k:np.array([r[k+'_GeV']/r['energy_GeV'] for r in rows]) for k in ('H','A','S','U')} for v,(rows,_,_) in loaded.items()}
    bounds={v:np.array([r['native_closure_bound_GeV']/r['energy_GeV'] for r in rows]) for v,(rows,_,_) in loaded.items()}
    failed={v:np.array([sum(t['failed_steps'] for t in r['collections'].values()) for r in rows]) for v,(rows,_,_) in loaded.items()}
    result=summarize(primary,values,bounds,failed,args.bootstrap,args.seed)
    result.update(status='PROTOTYPE',source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),analysis_sha256=sha(__file__),
        observer_protocol_sha256=sha(ROOT/'docs/validation/lar-gap10k/observer-protocol.md'),
        evidence={v:dict(receipt_sha256=sha(getattr(args,v)/'receipt.json'),observer_readback_sha256=sha(getattr(args,v)/'observer-readback.json'),replay=proof['replay'],failed_steps=proof['failed_steps']) for v,(_,_,proof) in loaded.items()},
        interpretation='Fresh matched H/E and complete accepted A/E vectors; inclusive raw-deposit sensitivity only. A does not validate cell readout. Zero empirical tails do not exclude nonzero population rates. No intrinsic resolution, calibration, engineering acceptance or electronics model.')
    args.output.mkdir(parents=True,exist_ok=False)
    covariance=dict(order=result.pop('width_covariance_order'),matrix=result.pop('width_covariance'))
    save(args.output/'width-covariance.json',covariance);result['width_covariance']=dict(file='width-covariance.json',sha256=sha(args.output/'width-covariance.json'),variables=len(covariance['order']))
    text=json.dumps(result,separators=(',',':'),allow_nan=False)+'\n'
    if len(text.encode())>=1024**2:raise ValueError('Compact observer summary exceeds1MiB')
    (args.output/'summary.json').write_text(text);print(json.dumps({v:result['missing'][v]['global'][0] for v in values},indent=2))


def plot(args):
    result=load(args.summary);args.output.mkdir(parents=True,exist_ok=False)
    for kind,view in result['views'].items():
        path=args.output/('view-'+kind+'.json');save(path,view)
        gap.plot(argparse.Namespace(summary=path,output=args.output/kind))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(12,4.8))
    edges=np.array(gap.AXES['fine_transition']);x=(edges[:-1]+edges[1:])/2
    for variant,style in (('standard',dict(color='#cccc00',ls='-',marker='o',markeredgecolor='#333333')),
                          ('candidate',dict(color='#cccc00',ls='--',marker='s',markeredgecolor='#333333'))):
        rows=result['missing'][variant]['fine_transition'];label='800 mm gap' if variant=='standard' else '400 mm gap'
        for ax,field,ci in ((axes[0],'mean_delta_U_over_E','mean_delta_bootstrap'),(axes[1],'missing_fraction_sum_U_over_sum_A','missing_fraction_bootstrap')):
            gap.draw_percentile(ax,x,np.array([r[field] for r in rows])*100,np.array([r[ci]['ci95'] for r in rows])*100,label=label,**style)
    for ax in axes:ax.set_xlabel('Primary |η|');ax.grid(alpha=.22)
    axes[0].set_ylabel('Mean unassigned U / primary E [%]');axes[1].set_ylabel('Unassigned ΣU / accepted ΣA [%]');axes[0].legend()
    fig.suptitle('Unassigned-deposit accounting · pointwise 95% intervals')
    fig.text(.02,.01,'PROTOTYPE · full matched 10,000 electrons · frozen transport and readout · no canonical cell invented for U',fontsize=8)
    fig.tight_layout(rect=(0,.05,1,.94))
    for ext in ('png','pdf','svg'):
        fig.savefig(args.output/('unassigned-transition.'+ext),dpi=160,metadata={'CreationDate':None,'ModDate':None} if ext=='pdf' else {'Date':None} if ext=='svg' else {})
    plt.close(fig)
    save(args.output/'render.json',dict(summary_sha256=sha(args.summary),plotter_sha256=sha(__file__),
        interpretation='Separate saved H/E and independently observed A/E figures; same frozen original common tail threshold',
        renders={kind:sha(args.output/kind/'render.json') for kind in result['views']},
        unassigned_figures={p.name:sha(p) for p in sorted(args.output.glob('unassigned-transition.*'))}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='stage',required=True)
    a=sub.add_parser('analyze')
    for n in ('standard','candidate','output'):a.add_argument('--'+n,type=Path,required=True)
    a.add_argument('--bootstrap',type=int,default=1000);a.add_argument('--seed',type=int,default=13001000)
    a=sub.add_parser('plot')
    for n in ('summary','output'):a.add_argument('--'+n,type=Path,required=True)
    args=p.parse_args();globals()[args.stage](args)
