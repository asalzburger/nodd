"""Aggregate-only original/dense/restored LAr overlays; no new inference.

Consumes six frozen paired summaries, never event files. Pairwise intervals are
copied from their source comparison, not formed by subtracting error bars.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import re

import numpy as np

PAIRS = {'original_dense':('original','dense'), 'original_restored':('original','restored'),
         'dense_restored':('dense','restored')}
MODELS = ('original','dense','restored')
AXES = dict(abs_eta=np.linspace(0,3,11), siw_folded_phi=np.linspace(-math.pi/16,math.pi/16,11),
            energy=np.linspace(10,80,15), full_phi=np.linspace(-math.pi,math.pi,17),
            signed_eta=np.linspace(-3,3,13), broad_eta=np.array([0.,1.2,1.5,3.]))
FIXED_AXES = tuple(AXES) + ('broad_eta_energy',)
POINT_FIELDS = ('events','mean_response','sample_sd','fractional_width','width_status','zero_events',
                'below_half_mean_events','below_half_mean_fraction','central_quantile_width','quantiles')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def equal(a,b,where):
    """Check repeated stored statistics; never refit or reconstruct an interval."""
    if isinstance(a,dict) and isinstance(b,dict):
        if a.keys()!=b.keys(): raise ValueError('Inconsistent aggregate keys: '+where)
        for key in a: equal(a[key],b[key],where+'/'+key)
    elif isinstance(a,list) and isinstance(b,list):
        if len(a)!=len(b): raise ValueError('Inconsistent aggregate length: '+where)
        for i,(x,y) in enumerate(zip(a,b)): equal(x,y,where+'/'+str(i))
    elif isinstance(a,(float,int)) and not isinstance(a,bool) and isinstance(b,(float,int)) and not isinstance(b,bool):
        if not math.isfinite(a) or not math.isfinite(b) or not math.isclose(a,b,rel_tol=2e-12,abs_tol=2e-14):
            raise ValueError('Inconsistent repeated statistic: '+where)
    elif a!=b: raise ValueError('Inconsistent repeated value: '+where)


def digest(value,where,length=64):
    if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{'+str(length)+'}',value):
        raise ValueError('Invalid source hash/revision: '+where)
    return value


def population(value,where):
    if type(value) is not int or value<0:raise ValueError('Invalid event count: '+where)
    return value


def histogram(h,events,where):
    if h is None:return
    if not isinstance(h,dict):raise ValueError('Invalid histogram: '+where)
    edges=np.asarray(h['edges'],dtype=float)
    if len(edges)!=len(h['counts'])+1 or not np.all(np.isfinite(edges)) or np.any(np.diff(edges)<=0):
        raise ValueError('Invalid histogram edges: '+where)
    counts=[population(x,where) for x in h['counts']]
    total=sum(counts)+population(h['underflow'],where)+population(h['overflow'],where)
    if h['events']!=events or total!=events:raise ValueError('Histogram loses denominator/overflow: '+where)


def row_check(row,where):
    n=population(row['events'],where)
    for key in ('zero_events','below_half_mean_events'):
        if population(row[key],where+'/'+key)>n:raise ValueError('Count exceeds all-event denominator: '+where)
    for key in ('mean_response','sample_sd','fractional_width'):
        v=row[key]
        if v is not None and (not isinstance(v,(float,int)) or not math.isfinite(v) or v<0):
            raise ValueError('Invalid stored statistic: '+where+'/'+key)
    if n and not math.isclose(row['below_half_mean_fraction'],row['below_half_mean_events']/n,rel_tol=2e-12,abs_tol=2e-14):
        raise ValueError('Tail denominator differs: '+where)
    for key,value in row.items():
        if key.endswith('_histogram'):histogram(value,n,where+'/'+key)
        elif key.endswith('_bootstrap'):
            undefined=population(value['undefined'],where+'/'+key)
            if undefined>1000:raise ValueError('Invalid undefined-bootstrap count: '+where)
            ci=value['ci95']
            if ci is not None and (len(ci)!=2 or not np.all(np.isfinite(ci)) or ci[0]>ci[1]):
                raise ValueError('Invalid stored interval: '+where)


def identity(summary,role):
    contract=summary['contract'];model=summary['models'][role];evidence=model['evidence'];sample=evidence['input']
    label=model['label']
    if not isinstance(label,str) or not label:raise ValueError('Missing physical model label')
    if contract.get(role+'_label')!=label:raise ValueError('Contract/model label differs: '+role)
    ident=dict(label=label)
    for key in ('compact_sha256','materials_sha256','primary_manifest_sha256','primary_revision'):
        expected=digest(contract[role+'_'+key],role+'/'+key,40 if key=='primary_revision' else 64)
        observed=sample.get('source_'+key) if key in ('primary_manifest_sha256','primary_revision') else sample.get('hashes',{}).get('detector.xml' if key=='compact_sha256' else 'materials.xml')
        if observed!=expected:raise ValueError('Physical model binding differs: '+role+'/'+key)
        ident[key]=expected
    for key,file in (('input_sha256','particles.HEPEvt'),('truth_sha256','truth-input.jsonl')):
        expected=digest(contract[key],key)
        if sample.get(key)!=expected or sample.get('hashes',{}).get(file)!=expected:
            raise ValueError('Physical primary identity differs: '+key)
        ident[key]=expected
    for key in ('receipt_sha256','readback_sha256','ledger_sha256','root_sha256'):
        ident[key]=digest(evidence[key],role+'/'+key)
    if sample.get('events')!=10000 or sample.get('collections')!={'LArBarrelHits':10,'LArEndcapHits':11}:
        raise ValueError('Unexpected physical primary/collection scope')
    ident['generation']={key:sample[key] for key in ('input_seed','distributions','electron_mass_GeV')}
    checks=summary['native_contract_checks'][role]
    if checks['transport'].get('status')!='PASS' or not checks['transport'].get('root_rehashed') or checks['maps'].get('status')!='PASS':
        raise ValueError('Missing successful aggregate physical gates')
    workers=checks['transport']['worker_audit_sha256']
    if set(workers)!={f'worker-{i}.json' for i in range(12)}:raise ValueError('Incomplete stored worker-gate evidence')
    for key,value in workers.items():digest(value,key)
    digest(checks['maps']['maps_sha256'],'serial map proof')
    if checks['maps']['raw_sensitive_ids']!=contract[role+'_raw_sensitive_ids']:
        raise ValueError('Native inventory differs from frozen contract')
    ident['native_checks']=checks
    return ident


def check_summary(summary,kind):
    if summary.get('events')!=10000 or set(summary['models'])!={'reference','candidate'}:
        raise ValueError('Need complete 10000-event paired summaries')
    b=summary['bootstrap'];expected_seed=13001000 if kind=='raw' else 14865018
    if b.get('replicates')!=1000 or b.get('seed')!=expected_seed or b.get('noninferiority_margin') is not None:
        raise ValueError('Unexpected paired bootstrap policy')
    if kind=='raw':
        if 'algorithm' in summary or not summary.get('observable','').startswith('R=active ECAL deposited energy'):
            raise ValueError('Raw/held-out summary identity differs')
    elif summary.get('algorithm')!='forward-mean-R-60-abseta-bins-v1' or not summary.get('observable','').startswith('Held-out C=Ehat/Etrue'):
        raise ValueError('Raw/held-out summary identity differs')
    else:
        f=summary['fold_assignment']
        if f.get('folds')!=5 or f.get('seed')!=14865017 or f.get('populations')!=[2000]*5 or not b.get('folds_fixed'):
            raise ValueError('Unexpected held-out fold policy')
        digest(f['assignment_ids_and_labels_sha256'],'fold assignment')
    ids={role:identity(summary,role) for role in ('reference','candidate')}
    equal(ids['reference']['generation'],ids['candidate']['generation'],'generation metadata')
    for role,model in summary['models'].items():
        row_check(model['global'],role+'/global')
        if model['global']['events']!=10000:raise ValueError('Global denominator differs')
        for axis in FIXED_AXES:
            p=model['projections'][axis]
            if axis in AXES:
                equal(p['edges'],AXES[axis].tolist(),axis+'/edges')
                unit='GeV' if axis=='energy' else 'rad' if 'phi' in axis else 'dimensionless'
                if p.get('unit')!=unit:raise ValueError('Projection unit differs: '+axis)
                bins=len(AXES[axis])-1
            else:
                equal(p['energy_edges'],AXES['energy'].tolist(),axis+'/energy edges')
                equal(p['abs_eta_edges'],AXES['broad_eta'].tolist(),axis+'/eta edges');bins=42
                if p['ordering']!='broad eta region first, energy bin second':raise ValueError('Energy-region axis order differs')
            if len(p['bins'])!=bins or sum(population(r['events'],axis) for r in p['bins'])!=10000:
                raise ValueError('Projection loses all-event denominator: '+axis)
            for i,r in enumerate(p['bins']):row_check(r,role+'/'+axis+'/'+str(i))
    for axis in ('global',)+FIXED_AXES:
        rows=summary['candidate_minus_reference'][axis]
        ref=[summary['models']['reference']['global']] if axis=='global' else summary['models']['reference']['projections'][axis]['bins']
        new=[summary['models']['candidate']['global']] if axis=='global' else summary['models']['candidate']['projections'][axis]['bins']
        if len(rows)!=len(ref):raise ValueError('Paired contrast axis differs')
        for r,a,b in zip(rows,new,ref):
            if a['events']!=b['events'] or r['events']!=a['events']:raise ValueError('Paired contrast denominator differs')
            expected=a['fractional_width']-b['fractional_width'] if a['fractional_width'] is not None and b['fractional_width'] is not None else None
            equal(r['difference'],expected,'stored contrast point identity')
            ci=r['ci95']
            if ci is not None and (len(ci)!=2 or not np.all(np.isfinite(ci)) or ci[0]>ci[1]):raise ValueError('Invalid paired interval')
    return ids


def fixed_stats(model):
    return dict(global_statistics=model['global'],projections={key:model['projections'][key] for key in FIXED_AXES})


def point_stats(row):
    return {key:row[key] for key in POINT_FIELDS}


def build_overlay(summaries):
    """Check and select stored aggregates. Never recompute uncertainty or events."""
    joined={kind:{} for kind in ('raw','calibrated')};identities={}
    fold=None;primary=None
    for kind in joined:
        for key,(ref,new) in PAIRS.items():
            s=summaries[kind][key];ids=check_summary(s,'raw' if kind=='raw' else 'calibrated')
            if kind=='calibrated':
                if fold is None:fold=s['fold_assignment']
                else:equal(fold,s['fold_assignment'],'repeated held-out folds')
            for role,name in (('reference',ref),('candidate',new)):
                ident=ids[role]
                physical_primary={key:ident[key] for key in ('input_sha256','truth_sha256','generation')}
                if primary is None:primary=physical_primary
                else:equal(primary,physical_primary,'common physical primaries')
                if name in identities:equal(identities[name],ident,'repeated model identity/'+name)
                else:identities[name]=ident
                stats=fixed_stats(s['models'][role])
                if name in joined[kind]:equal(joined[kind][name]['statistics'],stats,'repeated '+kind+' statistics/'+name)
                else:joined[kind][name]=dict(label=ident['label'],statistics=copy.deepcopy(stats))
                if kind=='calibrated':
                    raw=joined['raw'][name]['statistics']['global_statistics']
                    equal(point_stats(s['models'][role]['raw_global']),point_stats(raw),'raw vs held-out source moment/'+name)
    contrasts={kind:{key:copy.deepcopy(summaries[kind][key]['candidate_minus_reference'])
                     for key in ('original_restored','dense_restored')} for kind in joined}
    return dict(status='PROTOTYPE aggregate overlay',events=10000,identities=identities,models=joined,
                primary_identity=primary,fold_assignment=fold,paired_restored_contrasts=contrasts,
                limits=['Stored raw and exploratory held-out statistics only; no new fit, resampling or three-model covariance.',
                        'Pointwise paired intervals are copied from the appropriate restored-minus-comparator source; error-bar endpoints are never subtracted.',
                        'Input summaries assert completed physical gates; this aggregate helper does not re-read or rehash native/event files.',
                        'Only fixed common projections are joined; pair-specific transition unions remain in their original summaries.'])


def summary_bindings(summary,file_sha):
    allowed={file_sha}
    private=summary.get('publication',{}).get('full_private_summary_sha256')
    if private is not None:allowed.add(digest(private,'published private-summary binding'))
    return allowed


def add_diagnoses(overlay,summaries,diagnoses,sources):
    """Attach fixed-region histograms with ledger, source-file and moment checks."""
    if set(diagnoses)!={'original_dense','original_restored'}:raise ValueError('Provide both diagnostic summaries or neither')
    joined={};regions=None
    for key in ('original_dense','original_restored'):
        diag=diagnoses[key];source=diag['source']
        for kind,field in (('raw','raw_summary_sha256'),('calibrated','calibrated_summary_sha256')):
            if source[field] not in summary_bindings(summaries[kind][key],sources[kind+'_'+key]['sha256']):
                raise ValueError('Diagnostic source summary binding differs: '+key+'/'+kind)
        if regions is None:regions=diag['regions']
        else:equal(regions,diag['regions'],'diagnostic region boundaries')
        if diag['energy_slice_GeV']!=[45.,50.]:raise ValueError('Diagnostic energy slice differs')
        for role,name in zip(('reference','candidate'),PAIRS[key]):
            model=diag['models'][role];identity=overlay['identities'][name]
            if model['label']!=identity['label'] or model['ledger_sha256']!=identity['ledger_sha256']:
                raise ValueError('Diagnostic model/ledger identity differs: '+name)
            for i,region in enumerate(('barrel','transition','endcap')):
                for kind,field in (('raw','raw'),('calibrated','heldout')):
                    target=overlay['models'][kind][name]['statistics']['projections']['broad_eta']['bins'][i]
                    equal(point_stats(model['regions'][region][field]),point_stats(target),'diagnostic region statistic/'+name+'/'+region+'/'+kind)
            for region,record in model['regions'].items():
                for field in ('raw','heldout'):row_check(record[field],name+'/'+region+'/'+field)
                for field in ('raw_histogram','shape_histogram','heldout_histogram'):
                    histogram(record[field],record['raw']['events'],name+'/'+region+'/'+field)
                    if record[field].get('normalization')!='counts / all selected events, not renormalized to displayed range':
                        raise ValueError('Diagnostic histogram normalization differs')
                if record.get('shape_definition')!='Raw R / own regional mean(R); display normalization only, not calibrated precision':
                    raise ValueError('Diagnostic display normalization differs')
            selected={field:model[field] for field in ('regions','barrel_energy_slice')}
            if name in joined:equal(joined[name],selected,'repeated diagnostic aggregates/'+name)
            else:joined[name]=copy.deepcopy(selected)
    # Every displayed histogram uses common edges and explicit complete counts.
    for region in regions:
        for field in ('raw_histogram','shape_histogram','heldout_histogram'):
            reference=joined['original']['regions'][region][field]['edges']
            for name in MODELS:equal(reference,joined[name]['regions'][region][field]['edges'],'regional histogram edges')
    overlay['regional_diagnostics']=dict(regions=regions,models=joined,
        normalization='raw_histogram: absolute R; shape_histogram: raw R / own regional mean, display only; heldout_histogram: absolute Ehat/Etrue; all denominators include out-of-range events')


def plot(overlay,output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'svg.hashsalt':'nodd-restored-overlay-v1'})
    styles=dict(original=dict(color='#e5e580',ls=':',marker='s',markeredgecolor='#666666'),
                dense=dict(color='#dada66',ls='--',marker='^',markeredgecolor='#555555'),
                restored=dict(color='#cccc00',ls='-',marker='o',markeredgecolor='#333333'))
    labels=dict(abs_eta='|η|',siw_folded_phi='φ folded with legacy Si–W sector period [rad]',energy='Primary total energy [GeV]')
    files=[]
    def export(fig,stem,kind):
        footer='Raw primary response' if kind=='raw' else 'Exploratory fixed-family 5-fold ideal-η calibration; raw study remains primary'
        fig.text(.02,.012,'PROTOTYPE · same 10k electrons, E=10–80 GeV, η=−3…3 · '+footer+' · no digitization',fontsize=8)
        fig.tight_layout(rect=(0,.05,1,.94))
        for ext in ('png','pdf','svg'):
            p=output/f'{stem}.{ext}';fig.savefig(p,dpi=160,metadata={'CreationDate':None,'ModDate':None} if ext=='pdf' else {'Date':None} if ext=='svg' else {})
            if ext=='svg':p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')
            files.append(p)
        plt.close(fig)
    def projection(ax,kind,axis,field='fractional_width',region=None):
        for name in MODELS:
            model=overlay['models'][kind][name];p=model['statistics']['projections'][axis]
            edges=np.array(p['energy_edges'] if region is not None else p['edges'])
            rows=p['bins'][14*region:14*(region+1)] if region is not None else p['bins'];x=(edges[:-1]+edges[1:])/2
            scale=100 if field=='fractional_width' else 1;y=np.array([r[field] if r[field] is not None else np.nan for r in rows])*scale
            err=np.array([[max(0,y[i]-r[field+'_bootstrap']['ci95'][0]*scale),max(0,r[field+'_bootstrap']['ci95'][1]*scale-y[i])]
                          if r[field+'_bootstrap']['ci95'] else [np.nan,np.nan] for i,r in enumerate(rows)]).T
            ax.errorbar(x,y,yerr=err,label=model['label'],capsize=2,markersize=4,**styles[name])
        ax.grid(alpha=.22);ax.set_xlabel(labels.get(axis,'Primary total energy [GeV]'))
        ax.set_ylabel('SD(R)/mean(R) [%]' if kind=='raw' else 'SD(Ehat/Etrue)/mean [%]')
        if field=='mean_response':ax.set_ylabel('Mean active fraction R' if kind=='raw' else 'Held-out mean Ehat/Etrue')
        if kind=='calibrated' and field=='mean_response':ax.axhline(1,color='#777777',lw=1)
    for kind in ('raw','calibrated'):
        fig,axs=plt.subplots(1,2,figsize=(13,4.8))
        for ax,axis in zip(axs,('abs_eta','siw_folded_phi')):projection(ax,kind,axis)
        axs[0].legend(fontsize=8);fig.suptitle('Three LAr geometries · '+('raw widths' if kind=='raw' else 'held-out calibrated widths'));export(fig,kind+'-three-model-angular',kind)
        fig,axs=plt.subplots(1,3,figsize=(16,4.9))
        for i,ax in enumerate(axs):
            projection(ax,kind,'broad_eta_energy',region=i);ax.set_title(f'{AXES["broad_eta"][i]:g} ≤ |η| < {AXES["broad_eta"][i+1]:g}')
        axs[0].legend(fontsize=8);fig.suptitle('Energy widths in fixed broad angular regions · '+kind);export(fig,kind+'-three-model-energy-regions',kind)
        fig,axs=plt.subplots(1,3,figsize=(16,4.9))
        for ax,axis in zip(axs,('abs_eta','siw_folded_phi','energy')):
            edges=AXES[axis];x=(edges[:-1]+edges[1:])/2
            for key,marker,ls,label in [('original_restored','o','-','Restored − original'),('dense_restored','^','--','Restored − dense compact')]:
                rows=overlay['paired_restored_contrasts'][kind][key][axis]
                y=np.array([r['difference'] if r['difference'] is not None else np.nan for r in rows])*100
                err=np.array([[max(0,y[i]-r['ci95'][0]*100),max(0,r['ci95'][1]*100-y[i])] if r['ci95'] else [np.nan,np.nan] for i,r in enumerate(rows)]).T
                ax.errorbar(x,y,yerr=err,color='#cccc00',marker=marker,ls=ls,markeredgecolor='#333333',label=label,capsize=2)
            ax.axhline(0,color='#777777',lw=1);ax.grid(alpha=.22);ax.set_xlabel(labels[axis]);ax.set_ylabel('Paired width difference [percentage points]')
        axs[0].legend(fontsize=8);fig.suptitle('Stored paired restored-minus-comparator contrasts · pointwise 95% intervals');export(fig,kind+'-restored-paired-differences',kind)
    fig,axs=plt.subplots(1,3,figsize=(16,4.9))
    for i,ax in enumerate(axs):
        projection(ax,'calibrated','broad_eta_energy','mean_response',i);ax.set_title(f'{AXES["broad_eta"][i]:g} ≤ |η| < {AXES["broad_eta"][i+1]:g}')
    axs[0].legend(fontsize=8);fig.suptitle('Held-out energy closure · no evaluation-mean recentering');export(fig,'calibrated-three-model-closure-regions','calibrated')
    if 'regional_diagnostics' in overlay:
        d=overlay['regional_diagnostics']
        for region,meta in d['regions'].items():
            fig,axs=plt.subplots(1,3,figsize=(16,4.9))
            for ax,field,xlabel in zip(axs,('raw_histogram','shape_histogram','heldout_histogram'),
                    ('Absolute raw R','Raw R / own regional mean · display only','Absolute held-out Ehat/Etrue')):
                for name in MODELS:
                    record=d['models'][name]['regions'][region];h=record[field]
                    if not h['events']:continue
                    style={k:v for k,v in styles[name].items() if k in ('color','ls')}
                    ax.stairs(np.array(h['counts'])/h['events'],h['edges'],label=overlay['identities'][name]['label'],**style)
                ax.set_yscale('log');ax.grid(alpha=.22);ax.set_xlabel(xlabel);ax.set_ylabel('Fraction of all region events / bin')
            axs[0].legend(fontsize=8);fig.suptitle(meta['label']+' · regional distributions, zeros and overflow retained');export(fig,'regional-three-model-'+region,'calibrated')
    return files


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for kind in ('raw','calibrated'):
        for key in PAIRS:p.add_argument('--'+key.replace('_','-')+'-'+kind,type=Path,required=True)
    for key in ('original_dense','original_restored'):p.add_argument('--'+key.replace('_','-')+'-diagnosis',type=Path)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    summaries={kind:{} for kind in ('raw','calibrated')};sources={}
    for kind in summaries:
        for key in PAIRS:
            path=getattr(args,key+'_'+kind);summaries[kind][key]=json.loads(path.read_text())
            sources[kind+'_'+key]=dict(file=path.name,sha256=sha(path))
    overlay=build_overlay(summaries)
    paths={key:getattr(args,key+'_diagnosis') for key in ('original_dense','original_restored')}
    if any(paths.values()):
        if not all(paths.values()):raise ValueError('Provide both diagnostic summaries or neither')
        diagnoses={key:json.loads(path.read_text()) for key,path in paths.items()};add_diagnoses(overlay,summaries,diagnoses,sources)
        for key,path in paths.items():sources['diagnosis_'+key]=dict(file=path.name,sha256=sha(path))
    args.output.mkdir(parents=True,exist_ok=False)
    overlay['sources']=sources;overlay['producer_sha256']=sha(__file__)
    result=args.output/'overlay.json';result.write_text(json.dumps(overlay,indent=2,allow_nan=False)+'\n')
    files=plot(overlay,args.output)
    import matplotlib
    (args.output/'render.json').write_text(json.dumps(dict(overlay_sha256=sha(result),producer_sha256=sha(__file__),
        numpy_version=np.__version__,matplotlib_version=matplotlib.__version__,sources=sources,
        figures={f.name:sha(f) for f in files}),indent=2)+'\n')


if __name__=='__main__':main()
