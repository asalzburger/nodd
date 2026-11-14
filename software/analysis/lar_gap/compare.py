"""Paired standard800 / conditional400 mm gap raw-response comparison."""
import argparse
import json
from pathlib import Path
import subprocess

import numpy as np

from geometry import ROOT, FROZEN, PROTOCOL, sha, load, save, verify, check_sources
from native import verify_report
from software.analysis.lar_response import compare as retained
from software.analysis.lar_response import transport as response

AXES={k:v for k,v in retained.AXES.items() if k!='siw_folded_phi'}
AXES['fine_transition']=np.arange(110,161,5)/100
LABELS={'standard':'LAr standard 800 mm gap','candidate':'LAr conditional 400 mm gap'}
STATISTICS=('mean_response','sample_sd','fractional_width','common_tail_fraction')


def categories(primary):
    coords={'abs_eta':np.abs(primary[:,1]),'fine_transition':np.abs(primary[:,1]),
            'broad_eta':np.abs(primary[:,1]),'signed_eta':primary[:,1],
            'energy':primary[:,0],'full_phi':primary[:,2]}
    result={'global':np.zeros(len(primary),dtype=int)}
    for axis,edges in AXES.items():
        values=coords[axis]
        if axis=='fine_transition':
            inside=(values>=edges[0]) & (values<=edges[-1]);cat=np.full(len(values),-1,dtype=int)
            cat[inside]=retained.index(values[inside],edges);result[axis]=cat
        else:result[axis]=retained.index(values,edges)
    return result


def weighted(response_values,cat,weights,bins,threshold):
    take=cat>=0;ids=cat[take];r=response_values[take];w=weights[take]
    n=np.bincount(ids,weights=w,minlength=bins)
    sums=np.bincount(ids,weights=w*r,minlength=bins)
    squares=np.bincount(ids,weights=w*r*r,minlength=bins)
    mean=np.divide(sums,n,out=np.full(bins,np.nan),where=n>0)
    variance=np.divide(squares-sums*mean,n-1,out=np.full(bins,np.nan),where=n>1)
    sd=np.sqrt(np.maximum(variance,0))
    width=np.divide(sd,mean,out=np.full(bins,np.nan),where=mean>0)
    tail=np.divide(np.bincount(ids,weights=w*(r<threshold),minlength=bins),n,out=np.full(bins,np.nan),where=n>0)
    return np.column_stack((mean,sd,width,tail))


def statistics(values,common_threshold,own_global_threshold):
    row=retained.moments(values)
    # The retained comparison's half-bin-mean diagnostic has different semantics.
    del row['below_half_mean_events'];del row['below_half_mean_fraction']
    for prefix,threshold in (('common_tail',common_threshold),('own_global_tail',own_global_threshold)):
        numerator=int(np.count_nonzero(values<threshold))
        row.update({prefix+'_threshold_R':float(threshold),prefix+'_events':numerator,
                    prefix+'_denominator':len(values),prefix+'_fraction':numerator/len(values)})
    return row


def summarize(primary,responses,replicates=1000,seed=13001000):
    """Shared whole-event resampling; observed global thresholds remain frozen."""
    if set(responses)!=set(LABELS):raise ValueError('Need standard and candidate labels')
    n=len(primary)
    if any(len(r)!=n or not np.all(np.isfinite(r)) or np.any(r<0) for r in responses.values()):
        raise ValueError('Invalid/incomplete raw response')
    cat=categories(primary);bins={a:1 if a=='global' else len(AXES[a])-1 for a in cat}
    threshold=float(np.mean(responses['standard']))*.5
    own={name:float(np.mean(r))*.5 for name,r in responses.items()}
    boot={name:{axis:np.empty((replicates,bins[axis],4)) for axis in cat} for name in responses}
    rng=np.random.default_rng(seed)
    for b in range(replicates):
        w=np.bincount(rng.integers(n,size=n),minlength=n)
        for name,r in responses.items():
            for axis,c in cat.items():boot[name][axis][b]=weighted(r,c,w,bins[axis],threshold)
    models={}
    for name,r in responses.items():
        model=dict(label=LABELS[name],global_own_threshold_R=own[name],projections={})
        for axis,c in cat.items():
            rows=[]
            for i in range(bins[axis]):
                values=r[c==i]
                if len(values)<2:raise ValueError('Insufficient fixed-bin population: '+axis)
                row=statistics(values,threshold,own[name])
                for j,stat in enumerate(STATISTICS):row[stat+'_bootstrap']=retained.interval(boot[name][axis][:,i,j])
                rows.append(row)
            if axis=='global':model['global']=rows[0]
            else:model['projections'][axis]=dict(edges=AXES[axis].tolist(),bins=rows,unit='GeV' if axis=='energy' else 'rad' if axis=='full_phi' else 'dimensionless')
        edges=np.linspace(0,.6,121)
        model['raw_response_histogram']=dict(edges=edges.tolist(),counts=np.histogram(r,edges)[0].tolist(),events=n,
            underflow=int(np.count_nonzero(r<edges[0])),overflow=int(np.count_nonzero(r>edges[-1])),normalization='All generated events; R=active deposited energy / primary total energy')
        models[name]=model
    contrasts={}
    for axis in cat:
        rows=[]
        for i in range(bins[axis]):
            a=models['standard']['global'] if axis=='global' else models['standard']['projections'][axis]['bins'][i]
            b=models['candidate']['global'] if axis=='global' else models['candidate']['projections'][axis]['bins'][i]
            row={}
            for j,stat in enumerate(STATISTICS):
                row[stat]=dict(difference=b[stat]-a[stat],**retained.interval(boot['candidate'][axis][:,i,j]-boot['standard'][axis][:,i,j]))
            rows.append(row)
        contrasts[axis]=rows
    order=[];columns=[]
    for name in responses:
        for axis in ('global','abs_eta','fine_transition'):
            for i in range(bins[axis]):
                order.append(f'{name}:{axis}:{i}:fractional_width');columns.append(boot[name][axis][:,i,2])
    matrix=np.asarray(columns)
    if not np.all(np.isfinite(matrix)):raise ValueError('Undefined principal width covariance')
    return dict(events=n,models=models,candidate_minus_standard=contrasts,
        common_tail=dict(threshold_R=threshold,definition='R < 0.5 * observed standard GLOBAL mean(R)',
            bootstrap_threshold_policy='Numerically fixed observed standard global threshold in every replicate and every bin',denominator='All generated events in the stated projection bin, including zeros'),
        own_global_tail=dict(definition='R < 0.5 * each model observed GLOBAL mean(R); same threshold in every bin',intervals='Descriptive diagnostic only'),
        bootstrap=dict(replicates=replicates,seed=seed,resampling='Shared whole-primary-event multiplicities across both variants and all projections',intervals='Pointwise 95% percentile; threshold held fixed; showers remain distinct stochastic histories'),
        width_covariance_order=order,width_covariance=np.cov(matrix,ddof=1).tolist())


def run_binding(run,sample,manifest):
    run=Path(run);receipt=load(run/'receipt.json');proof=load(run/'readback.json')
    if receipt['sample_sha256']!=sha(Path(sample)/'sample.json') or proof['sample']!=manifest:
        raise ValueError('Run/sample manifest mismatch')
    if receipt.get('source_state') or not receipt.get('producers_unchanged') or not receipt.get('libraries_unchanged'):
        raise ValueError('Unfrozen transport producers')
    check_sources(receipt['producer_sha256'])
    if sha(run/'transport.log')!=receipt['log_sha256']:raise ValueError('Changed transport log')
    if sha(run/'audit/maps-initialized.json')!=receipt['maps_audit_sha256'] or proof['maps_audit_sha256']!=receipt['maps_audit_sha256']:
        raise ValueError('Changed serial map audit')
    maps=load(run/'audit/maps-initialized.json')
    if maps!=proof['maps_audit'] or maps['status']!='PASS' or maps['thread_id']>=0 or maps['raw_sensitive_ids']!=43648 or maps['native_contexts_checked']!=43648:
        raise ValueError('Incomplete native maps')
    for path,digest in receipt['library_sha256'].items():
        if sha(path)!=digest:raise ValueError('Changed executed library')
    for filename,digest in proof['worker_audit_sha256'].items():
        if sha(run/'audit'/filename)!=digest:raise ValueError('Changed worker receipt')
    response.check_workers(proof['workers'],receipt)
    return receipt


def analyze(args):
    if args.bootstrap!=1000 or args.seed!=13001000:raise ValueError('Frozen protocol requires 1000 replicates and seed 13001000')
    if sha(args.protocol)!=sha(PROTOCOL):raise ValueError('Unexpected prospective protocol')
    manifest=verify(args.sample);gap=manifest['gap_experiment'];binding=gap['reference_binding']
    if args.standard.resolve()!=Path(gap['reference_run']).resolve():raise ValueError('Wrong standard reference run')
    native=verify_report(args.native_report)
    paths={'standard':args.standard,'candidate':args.candidate}
    samples={'standard':Path(gap['reference_sample']),'candidate':args.sample}
    loaded={};contracts={}
    for name,path in paths.items():
        m=load(samples[name]/'sample.json');response.verify_hashes(samples[name],m['hashes'])
        receipt=run_binding(path,samples[name],m)
        contracts[name]=retained.validate_contract(path,'lar');loaded[name]=retained.load_run(path)
        if receipt['library_sha256']!=binding['library_sha256']:raise ValueError('Gap study executed different libraries')
        snapshot=native['snapshots'][name]
        if snapshot['sample_sha256']!=sha(samples[name]/'sample.json') or snapshot['compact_sha256']!=m['hashes']['detector.xml']:
            raise ValueError('Native audit does not bind executed geometry')
        for key,file in (('input_sha256','particles.HEPEvt'),('truth_sha256','truth-input.jsonl')):
            if m[key]!=FROZEN[file]:raise ValueError('Wrong frozen 10k primary input')
    base=loaded['standard'][1]
    if len(base)!=10000 or loaded['candidate'][1].shape!=base.shape or not np.allclose(base[:,:3],loaded['candidate'][1][:,:3],rtol=0,atol=1e-9):
        raise ValueError('Unmatched complete 10000 primary illumination')
    result=summarize(base,{name:value[1][:,4] for name,value in loaded.items()},args.bootstrap,args.seed)
    if [r['events'] for r in result['models']['standard']['projections']['broad_eta']['bins']] != [3999,999,5002]:
        raise ValueError('Frozen transition population differs')
    for name in paths:
        result['models'][name]['evidence']=loaded[name][2];result['models'][name]['comparison_contract']=contracts[name]
    result.update(status='PROTOTYPE',observable='Raw ECAL deposit fraction R; means, sample SD, SD/mean and fixed-threshold tails including all zeros',
        interpretation='Gap-only sensitivity; spectrum/direction/dead-material/leakage mixed. Zero empirical tails do not exclude nonzero population rates. No intrinsic resolution, engineering fit, digitization or technology-selection claim.',
        source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        analysis_sha256=sha(__file__),source_sha256=gap['source_sha256'],protocol_sha256=sha(args.protocol),
        native_report_sha256=sha(args.native_report),native_geometry=retained.portable(native),
        candidate_sample_sha256=sha(args.sample/'sample.json'),reference_binding=retained.portable(binding))
    args.output.mkdir(parents=True,exist_ok=False);save(args.output/'summary.json',result)
    print(json.dumps({n:m['global'] for n,m in result['models'].items()},indent=2))


def plot(args):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    result=load(args.summary);args.output.mkdir(parents=True,exist_ok=False)
    plt.rcParams.update({'font.size':10,'svg.hashsalt':'nodd-lar-gap10k-v1'})
    styles={'standard':dict(color='#cccc00',ls='-',marker='o',markeredgecolor='#333333'),
            'candidate':dict(color='#cccc00',ls='--',marker='s',markeredgecolor='#333333')}
    labels={'abs_eta':'|η|','fine_transition':'|η|','broad_eta':'|η|','energy':'Primary total energy [GeV]','signed_eta':'η','full_phi':'φ [rad]'}
    def export(fig,name):
        fig.text(.02,.01,'PROTOTYPE · same 10,000 origin electrons · E=10–80 GeV, η=−3…3 · ECAL only, B=0 · raw deposits; no digitization',fontsize=8)
        fig.tight_layout(rect=(0,.05,1,.94))
        for ext in ('png','pdf','svg'):
            fig.savefig(args.output/(name+'.'+ext),dpi=160,metadata={'CreationDate':None,'ModDate':None} if ext=='pdf' else {'Date':None} if ext=='svg' else {})
        plt.close(fig)
    def projection(ax,axis,field):
        for name,model in result['models'].items():
            p=model['projections'][axis];edges=np.array(p['edges']);x=(edges[:-1]+edges[1:])/2
            y=np.array([r[field] for r in p['bins']]);ci=np.array([r[field+'_bootstrap']['ci95'] for r in p['bins']])
            factor=100 if field in ('fractional_width','common_tail_fraction') else 1
            ax.errorbar(x,y*factor,yerr=np.maximum([y-ci[:,0],ci[:,1]-y],0)*factor,label=model['label'],capsize=2,markersize=4,**styles[name])
        ax.set_xlabel(labels[axis]);ax.set_ylabel({'fractional_width':'SD(R) / mean(R) [%]','mean_response':'Mean deposited fraction R','common_tail_fraction':'Below fixed standard global threshold [%]'}[field]);ax.grid(alpha=.22)
    for field,name in (('fractional_width','angular-widths'),('mean_response','angular-means'),('common_tail_fraction','angular-common-tails')):
        fig,axs=plt.subplots(1,2,figsize=(12,4.6))
        for ax,axis in zip(axs,('abs_eta','fine_transition')):projection(ax,axis,field)
        axs[0].legend();fig.suptitle('Standard 800 mm versus conditional 400 mm gap · pointwise 95% intervals');export(fig,name)
    fig,axs=plt.subplots(2,3,figsize=(15,8))
    for col,axis in enumerate(('energy','signed_eta','full_phi')):
        projection(axs[0,col],axis,'fractional_width');projection(axs[1,col],axis,'mean_response')
    axs[0,0].legend();fig.suptitle('Energy and signed-direction controls');export(fig,'direction-energy-controls')
    fig,axs=plt.subplots(1,3,figsize=(15,4.8))
    for ax,field in zip(axs,('mean_response','fractional_width','common_tail_fraction')):
        edges=np.array(AXES['fine_transition']);x=(edges[:-1]+edges[1:])/2
        rows=[r[field] for r in result['candidate_minus_standard']['fine_transition']]
        y=np.array([r['difference'] for r in rows]);ci=np.array([r['ci95'] for r in rows]);factor=100 if field!='mean_response' else 1
        ax.errorbar(x,y*factor,yerr=np.maximum([y-ci[:,0],ci[:,1]-y],0)*factor,color='#cccc00',marker='o',markeredgecolor='#333333',capsize=2)
        ax.axhline(0,color='#555555',lw=.7);ax.set(xlabel='|η|',ylabel=field.replace('_',' ')+(' [percentage points]' if factor==100 else ''));ax.grid(alpha=.22)
    fig.suptitle('Conditional minus standard · paired transition differences');export(fig,'transition-differences')
    fig,ax=plt.subplots(figsize=(9,5))
    for name,model in result['models'].items():
        h=model['raw_response_histogram'];ax.stairs(np.array(h['counts'])/h['events'],h['edges'],color='#cccc00',ls=styles[name]['ls'],label=model['label'])
    ax.axvline(result['common_tail']['threshold_R'],color='#555555',ls=':',label='Fixed common global tail threshold')
    ax.set(xlabel='R = active deposited energy / primary total energy',ylabel='Fraction of all generated events / bin',yscale='log',ylim=(5e-5,.3));ax.legend();ax.grid(alpha=.22)
    fig.suptitle('Raw response distributions including zeros');export(fig,'raw-response-distributions')
    save(args.output/'render.json',dict(summary_sha256=sha(args.summary),plotter_sha256=sha(__file__),figures={p.name:sha(p) for p in sorted(args.output.iterdir()) if p.suffix in ('.png','.pdf','.svg')}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='stage',required=True)
    a=sub.add_parser('analyze')
    for n in ('standard','candidate','sample','native-report','output'):a.add_argument('--'+n,type=Path,required=True)
    a.add_argument('--protocol',type=Path,default=PROTOCOL);a.add_argument('--bootstrap',type=int,default=1000);a.add_argument('--seed',type=int,default=13001000)
    a=sub.add_parser('plot')
    for n in ('summary','output'):a.add_argument('--'+n,type=Path,required=True)
    args=p.parse_args();globals()[args.stage](args)
