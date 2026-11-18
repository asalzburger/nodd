"""Synthetic aggregate checks; no event payload or actual restored response read."""
import copy
import hashlib
import json
import unittest

import numpy as np
import restored_overlay as o


def h(text):return hashlib.sha256(text.encode()).hexdigest()


def counts(n,bins):
    return [n//bins+(i<n%bins) for i in range(bins)]


def histogram(n,shape=False):
    edges=np.linspace(0,3,601) if shape else np.linspace(0,.4,401)
    values=[0]*(len(edges)-1);values[200 if shape else 150]=n
    return dict(edges=edges.tolist(),counts=values,events=n,underflow=0,overflow=0,
                normalization='counts / all selected events, not renormalized to displayed range')


def row(name,n,kind):
    i=o.MODELS.index(name);mean=[.15,.07,.14][i] if kind=='raw' else 1.
    width=([.05,.065,.055] if kind=='raw' else [.03,.04,.032])[i]
    out=dict(events=n,mean_response=mean,sample_sd=mean*width,fractional_width=width,width_status='defined',
             zero_events=0,below_half_mean_events=0,below_half_mean_fraction=0.,central_quantile_width=width,
             quantiles=dict(q01=mean*.9,q16=mean*.95,q50=mean,q84=mean*1.05,q99=mean*1.1))
    for field in ('mean_response','fractional_width'):out[field+'_bootstrap']=dict(ci95=[out[field]-.001,out[field]+.001],undefined=0)
    return out


def sample(name):
    return dict(events=10000,source_primary_manifest_sha256=h(name+' primary manifest'),
                source_primary_revision=h(name+' primary revision')[:40],input_sha256=h('physical HEPEvt'),truth_sha256=h('physical truth'),
                input_seed=13310000,distributions=dict(total_energy_GeV=[10,80],eta=[-3,3],phi_rad=[-np.pi,np.pi],independent_uniform=True),
                electron_mass_GeV=.00051099895,collections={'LArBarrelHits':10,'LArEndcapHits':11},
                hashes={'detector.xml':h(name+' compact'),'materials.xml':h(name+' materials'),
                        'particles.HEPEvt':h('physical HEPEvt'),'truth-input.jsonl':h('physical truth')})


def physical(name):
    return dict(receipt_sha256=h(name+' receipt'),readback_sha256=h(name+' readback'),ledger_sha256=h(name+' ledger'),
                root_sha256=h(name+' root'),input=sample(name))


def model(name,kind):
    out=dict(label=name+' synthetic LAr',evidence=physical(name),global_statistics=None,projections={})
    out['global']=row(name,10000,kind);del out['global_statistics']
    for axis,edges in o.AXES.items():
        n=counts(10000,len(edges)-1)
        if axis=='broad_eta':n=[4000,1000,5000]
        out['projections'][axis]=dict(edges=edges.tolist(),unit='GeV' if axis=='energy' else 'rad' if 'phi' in axis else 'dimensionless',bins=[row(name,x,kind) for x in n])
    out['projections']['broad_eta_energy']=dict(energy_edges=o.AXES['energy'].tolist(),abs_eta_edges=o.AXES['broad_eta'].tolist(),ordering='broad eta region first, energy bin second',bins=[row(name,x,kind) for n in (4000,1000,5000) for x in counts(n,14)])
    if kind=='calibrated':out['raw_global']=o.point_stats(row(name,10000,'raw'))
    return out


def pair_summary(key,kind):
    a,b=o.PAIRS[key];contract=dict(input_sha256=h('physical HEPEvt'),truth_sha256=h('physical truth'))
    native={}
    for role,name in [('reference',a),('candidate',b)]:
        s=sample(name)
        for field in ('compact_sha256','materials_sha256','primary_manifest_sha256','primary_revision'):
            value=s['source_'+field] if field in ('primary_manifest_sha256','primary_revision') else s['hashes']['detector.xml' if field=='compact_sha256' else 'materials.xml']
            contract[role+'_'+field]=value
        contract[role+'_label']=name+' synthetic LAr';contract[role+'_raw_sensitive_ids']=20+o.MODELS.index(name)
        native[role]=dict(transport=dict(status='PASS',root_rehashed=True,worker_audit_sha256={f'worker-{i}.json':h(name+' worker '+str(i)) for i in range(12)}),maps=dict(status='PASS',raw_sensitive_ids=contract[role+'_raw_sensitive_ids'],maps_sha256=h(name+' maps')))
    summary=dict(events=10000,contract=contract,models=dict(reference=model(a,kind),candidate=model(b,kind)),
                 bootstrap=dict(replicates=1000,seed=13001000 if kind=='raw' else 14865018,noninferiority_margin=None),
                 native_contract_checks=native,candidate_minus_reference={})
    if kind=='raw':summary['observable']='R=active ECAL deposited energy / primary total energy; sample SD(R)/mean(R)'
    else:
        summary['observable']='Held-out C=Ehat/Etrue; sample SD(C)/mean(C)';summary['algorithm']='forward-mean-R-60-abseta-bins-v1'
        summary['bootstrap']['folds_fixed']=True
        summary['fold_assignment']=dict(folds=5,seed=14865017,populations=[2000]*5,assignment_ids_and_labels_sha256=h('fixed primary fold assignment'))
    for axis in ('global',)+o.FIXED_AXES:
        ref=[summary['models']['reference']['global']] if axis=='global' else summary['models']['reference']['projections'][axis]['bins']
        new=[summary['models']['candidate']['global']] if axis=='global' else summary['models']['candidate']['projections'][axis]['bins']
        summary['candidate_minus_reference'][axis]=[dict(events=x['events'],difference=y['fractional_width']-x['fractional_width'],ci95=[y['fractional_width']-x['fractional_width']-.002,y['fractional_width']-x['fractional_width']+.002],undefined=0) for x,y in zip(ref,new)]
    return summary


def inputs():
    return {kind:{key:pair_summary(key,kind) for key in o.PAIRS} for kind in ('raw','calibrated')}


def diagnostics(summaries):
    sources={kind+'_'+key:dict(sha256=h(kind+' '+key)) for kind in summaries for key in o.PAIRS}
    out={}
    for key in ('original_dense','original_restored'):
        regions={name:dict(abs_eta_interval=interval,upper_inclusive=name=='endcap',label=name+' synthetic region') for name,interval in zip(('barrel','transition','endcap'),([0.,1.2],[1.2,1.5],[1.5,3.]))}
        diag=dict(regions=regions,energy_slice_GeV=[45.,50.],source=dict(raw_summary_sha256=sources['raw_'+key]['sha256'],calibrated_summary_sha256=sources['calibrated_'+key]['sha256']),models={})
        for role,name in zip(('reference','candidate'),o.PAIRS[key]):
            m=dict(label=name+' synthetic LAr',ledger_sha256=h(name+' ledger'),regions={},barrel_energy_slice={})
            for region,n in zip(regions,(4000,1000,5000)):
                m['regions'][region]=dict(raw=o.point_stats(row(name,n,'raw')),heldout=o.point_stats(row(name,n,'calibrated')),
                    raw_histogram=histogram(n),shape_histogram=histogram(n,True),heldout_histogram=histogram(n,True),
                    shape_definition='Raw R / own regional mean(R); display normalization only, not calibrated precision')
            diag['models'][role]=m
        out[key]=diag
    return out,sources


class OverlayChecks(unittest.TestCase):
    def test_identity_join_keeps_stored_pairwise_intervals(self):
        s=inputs();result=o.build_overlay(s)
        self.assertEqual(set(result['identities']),set(o.MODELS));self.assertEqual(result['events'],10000)
        self.assertEqual(result['paired_restored_contrasts']['raw']['dense_restored'],s['raw']['dense_restored']['candidate_minus_reference'])
        self.assertEqual(result['models']['raw']['restored']['statistics']['global_statistics']['zero_events'],0)
        json.dumps(result,allow_nan=False)

    def test_mismatched_physical_identity_and_labels_are_rejected(self):
        for field in ('compact_sha256','materials_sha256','primary_manifest_sha256'):
            with self.subTest(field=field):
                s=inputs();s['raw']['original_restored']['contract']['candidate_'+field]=h('wrong '+field)
                with self.assertRaisesRegex(ValueError,'binding differs'):o.build_overlay(s)
        s=inputs();s['raw']['dense_restored']['models']['reference']['label']='incorrect dense label'
        with self.assertRaisesRegex(ValueError,'label differs'):o.build_overlay(s)
        s=inputs();s['raw']['original_restored']['models']['reference']['evidence']['ledger_sha256']=h('wrong ledger')
        with self.assertRaisesRegex(ValueError,'repeated'):o.build_overlay(s)

    def test_axis_unit_and_population_mismatch_are_rejected(self):
        s=inputs();s['raw']['original_restored']['models']['candidate']['projections']['abs_eta']['edges'][1]+=.01
        with self.assertRaisesRegex(ValueError,'statistic'):o.build_overlay(s)
        s=inputs();s['raw']['original_restored']['models']['candidate']['projections']['energy']['unit']='MeV'
        with self.assertRaisesRegex(ValueError,'unit differs'):o.build_overlay(s)
        s=inputs();s['raw']['original_restored']['models']['candidate']['projections']['abs_eta']['bins'][0]['events']-=1
        with self.assertRaisesRegex(ValueError,'denominator'):o.build_overlay(s)

    def test_repeated_statistics_and_raw_calibration_types_are_checked(self):
        s=inputs();s['raw']['original_restored']['models']['reference']['global']['mean_response']+=.01
        with self.assertRaisesRegex(ValueError,'repeated statistic'):o.build_overlay(s)
        s=inputs();s['calibrated']['original_restored']=copy.deepcopy(s['raw']['original_restored'])
        with self.assertRaisesRegex(ValueError,'bootstrap policy|summary identity'):o.build_overlay(s)
        s=inputs();s['calibrated']['original_restored']['fold_assignment']['seed']+=1
        with self.assertRaisesRegex(ValueError,'fold policy'):o.build_overlay(s)

    def test_diagnostics_are_bound_and_keep_overflow_denominators(self):
        s=inputs();d,source=diagnostics(s);overlay=o.build_overlay(s)
        o.add_diagnoses(overlay,s,d,source)
        self.assertEqual(set(overlay['regional_diagnostics']['models']),set(o.MODELS))
        bad=copy.deepcopy(d);bad['original_restored']['source']['raw_summary_sha256']=h('wrong source')
        with self.assertRaisesRegex(ValueError,'source summary binding'):o.add_diagnoses(o.build_overlay(s),s,bad,source)
        bad=copy.deepcopy(d);bad['original_restored']['models']['candidate']['regions']['barrel']['raw_histogram']['counts'][150]-=1
        with self.assertRaisesRegex(ValueError,'denominator/overflow'):o.add_diagnoses(o.build_overlay(s),s,bad,source)
        # Moving a histogram count to overflow preserves the stated denominator.
        hist=copy.deepcopy(d['original_restored']['models']['candidate']['regions']['barrel']['raw_histogram'])
        hist['counts'][150]-=1;hist['overflow']+=1;o.histogram(hist,4000,'test')


if __name__=='__main__':unittest.main()
