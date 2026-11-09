#!/usr/bin/env python3
"""Replot compact PR118 digitizer validation data, without ROOT or event files."""
import argparse
import json
import os
from pathlib import Path
import tempfile

os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'nodd-issue117-matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ECAL='#cccc00'
STYLES={'raw':dict(color=ECAL,linestyle=':',marker='s',markerfacecolor='white',markeredgecolor='black'),
        'off':dict(color=ECAL,linestyle='--',marker='^',markerfacecolor='white',markeredgecolor='black'),
        'on':dict(color=ECAL,linestyle='-',marker='o',markerfacecolor=ECAL,markeredgecolor='black')}
LABELS={'raw':'ECAL raw deposits','off':'ECAL D: pairs/noise off','on':'ECAL PN: pairs + electronics noise'}


def validate_hist(h):
    n=h.get('entries',h.get('n'))
    if len(h['edges'])!=len(h['counts'])+1 or any(x<0 for x in h['counts']):
        raise ValueError('Invalid histogram')
    if n is not None and sum(h['counts'])+h['underflow']+h['overflow']!=n:
        raise ValueError('Histogram denominator does not close')


def axes_style(ax):
    ax.grid(alpha=.18)
    ax.spines[['top','right']].set_visible(False)


def hist(ax,h,denominator=None,*,label='',linestyle='-',filled=False):
    validate_hist(h)
    edges=np.asarray(h['edges'])
    counts=np.asarray(h['counts'],float)
    if denominator is not None:
        counts/=denominator*np.diff(edges)
    ax.stairs(counts,edges,label=label,color=ECAL,linestyle=linestyle,
              fill=filled,alpha=.3 if filled else 1.,linewidth=1.6)


def finish(fig,path,title,caption,handles=None):
    fig.suptitle(title,fontsize=16,y=.992)
    fig.text(.5,.014,caption,ha='center',va='bottom',fontsize=9)
    if handles:
        fig.legend(*handles,loc='lower center',bbox_to_anchor=(.5,.052),ncol=3,frameon=False,fontsize=10)
    fig.tight_layout(rect=(.015,.11 if handles else .075,.99,.958),h_pad=2.,w_pad=2.)
    fig.savefig(path,dpi=170,facecolor='white',metadata={'Software':'nODD compact-summary renderer'})
    plt.close(fig)


def mip_plot(data,path):
    fig,axs=plt.subplots(3,2,figsize=(14,14))
    muons=data['muons']['samples']
    for col,sample in enumerate(muons):
        ax=axs[0,col]
        n=sample['counters']['qualified_spectrum_crossings']
        for stage in ['raw','off','on']:
            spectrum=sample['spectra'][stage]
            hist(ax,spectrum['histogram'],n,label=LABELS[stage]+'; prethreshold' if stage!='raw' else LABELS[stage],linestyle=STYLES[stage]['linestyle'])
        pn=sample['spectra']['on']
        hist(ax,pn['actual_thresholded_output'],n,label='PN actual output: >0.6 MIP',filled=True)
        fit=pn['fit']
        ax.plot(fit['curve_x_MIP'],np.asarray(fit['curve_counts_per_bin'])/(n*fit['bin_width_MIP']),color='black',lw=1.,label='PN Landau–Gaussian fit (conditional)')
        ax.axvline(1.,color='black',ls=':',lw=.8)
        snr=sample['SNR']
        flag='; fit diagnostics flagged' if fit['model_diagnostic_flags'] else ''
        ax.set(title=f"{'AB'[col]}. Held-out muons, η={sample['eta']:g}; {n:,} selected crossings",
               xlabel='Path-normalized pulse [MIP at 0.5 mm equivalent path]',ylabel='Density per selected crossing [MIP⁻¹]',xlim=(0,3.0))
        ax.text(.98,.96,f"Landau MPV = {fit['underlying_Landau_MPV']:.3f} ± {fit['MPV_event_cluster_bootstrap_SE']:.3f}\nConvolved mode = {fit['convolved_peak']:.3f}\nSNR = {snr['ratio']:.2f} ± {snr['ratio_SE']:.2f}{flag}",transform=ax.transAxes,ha='right',va='top',fontsize=9)
        ax.legend(fontsize=8,loc='upper right',bbox_to_anchor=(1,.77))
        ax=axs[1,col]
        thresholds=sample['thresholds_MIP']
        for stage in ['off','on']:
            e=sample['efficiency'][stage]
            ci=np.asarray(e['event_cluster_bootstrap_CI95'])
            ax.plot(thresholds,e['efficiency'],label=LABELS[stage]+'; nominal 48N yield',**STYLES[stage],markersize=4)
            ax.fill_between(thresholds,ci[0],ci[1],color=ECAL,alpha=.16)
        for name,style,label in [('identified_single','-.','PN identified single-cell crossings'),('identified_split',':','PN identified split-cell crossings')]:
            e=sample['identified_crossing_categories'][name]
            if not e['denominator']:
                continue
            values=np.asarray(e['efficiency'])[1]
            ci=np.asarray(e['conditional_crossing_Wilson95'])[:,1,:]
            ax.errorbar(thresholds,values,yerr=np.maximum(0,np.array([values-ci[0],ci[1]-values])),color=ECAL,ls=style,marker='x',markersize=4,capsize=2,label=f"{label}; N={e['denominator']:,}")
        ax.axvline(.6,color='black',ls=':',lw=.8)
        counters=sample['counters']
        ax.set(title=f"{'CD'[col]}. Threshold scan, η={sample['eta']:g}; {48*sample['events']:,} nominal opportunities",
               xlabel='Strict per-cell threshold [MIP; actual pulse units]',ylabel='Pass fraction / nominal yield',ylim=(-.02,1.08),xlim=(0,2))
        ax.text(.02,.06,f"Unknown/missing primary layers: {counters['missing_primary_layer']}\nSplit layers: {counters['split_primary_layer']}; spectrum uses no pulse cut",transform=ax.transAxes,fontsize=9)
        ax.legend(fontsize=8,loc='upper right',bbox_to_anchor=(1,.9))
    ax=axs[2,0]
    pedestal=data['pedestal']
    hist(ax,pedestal['signed'],pedestal['n'],label='ECAL signed prethreshold pedestal')
    x=np.linspace(-.65,.65,501)
    ax.plot(x,np.exp(-.5*(x/.13)**2)/(.13*np.sqrt(2*np.pi)),color='black',ls='--',lw=1.,label='Configured Gaussian σ=0.13 MIP')
    ax.set(title=f"E. Electronics-only model pedestal; N={pedestal['n']:,}",xlabel='Signed noise [MIP]',ylabel='Density [MIP⁻¹]')
    ax.text(.98,.96,f"Mean = {pedestal['mean']:.5f} MIP\nRMS = {pedestal['SD']:.5f} MIP\nGaussian mean/RMS/2σ-tail controls: {'pass' if pedestal['gaussian_control']['passed'] else 'FAIL'}",transform=ax.transAxes,ha='right',va='top',fontsize=10)
    ax.legend(fontsize=9,loc='upper left')
    ax=axs[2,1];ax.axis('off')
    text=['F. Frozen study definition','',f"MIP scale: {data['settings']['mip_energy_GeV']*1e6:.2f} keV (historical calibration)",
          'New 10 GeV/c muons: 250 events per direction; all held out.',
          'Near-normal, pure single-primary-cell spectra; local chord path approximation.',
          'D disables pair statistics and electronics; PN enables both.',
          'SNR uses fitted Landau-component MPV / signed pedestal RMS.','',
          'Bands: 95% whole-event bootstrap (nominal opportunity yield).',
          'Crossing bars: conditional Wilson95; layers within an event are correlated.',
          'Sparse split-category bootstrap intervals may be undefined (retained in data).',
          '48N yield is not complete crossing efficiency when truth inventory is unknown.','',
          'Fit errors: 1,000 whole-event bootstrap replicates.',
          'Fit shape is a conditional characterization; flags and empirical modes retained.',
          'No hardware noise, empty-detector occupancy or physics acceptance claim.']
    ax.text(0,1,'\n'.join(text),va='top',fontsize=10,linespacing=1.5)
    for ax in axs.flat:axes_style(ax)
    finish(fig,path,'ODD silicon digitization — held-out muon MIP, SNR and threshold response',
           'PROTOTYPE • Original ODD geometry; frozen 148.75 keV/MIP, 0.13 MIP noise, 0.6 MIP threshold.\nPath normalization is approximate; thresholds use uncorrected channel amplitudes. All rejected/unknown categories remain in the compact data.')


def shower_plot(data,species,path):
    fig,axs=plt.subplots(2,3,figsize=(15,8))
    for col,eta in enumerate([0.,1.,2.]):
        samples=sorted([s for s in data['showers']['samples'] if s['particle']==species and s['eta']==eta],key=lambda s:s['nominal_momentum_GeV'])
        for stage in ['raw','off','on']:
            energy=[s['beam_energy_GeV'] for s in samples]
            ys=[s['stages'][stage] for s in samples]
            axs[0,col].errorbar(energy,[100*(s['calibrated_response']-1) for s in ys],yerr=[100*s['calibrated_response_SE'] for s in ys],label=LABELS[stage],**STYLES[stage],markersize=5,capsize=3)
            axs[1,col].errorbar(energy,[100*s['RMS_over_mean'] for s in ys],yerr=[100*s['RMS_over_mean_SE'] for s in ys],label=LABELS[stage],**STYLES[stage],markersize=5,capsize=3)
        reference=data['showers']['calibrations'][str(eta)]
        axs[0,col].axhline(0,color='black',lw=.8)
        axs[0,col].set(title=f"η={eta:g}; N=200 per test point",ylabel='Calibrated response − 1 [%]',xlabel='Generated total energy [GeV]')
        axs[1,col].set(ylabel='All-event sample SD / mean [%]',xlabel='Generated total energy [GeV]')
        axs[0,col].text(.97,.05,f"Independent e⁻ reference: N={reference['n']} at 20 GeV/c\nCη = {reference['factor']:.3f} ± {reference['factor_SE']:.3f}",transform=axs[0,col].transAxes,ha='right',va='bottom',fontsize=9)
        for ax in axs[:,col]:
            ax.set_xticks([5,20,50]);axes_style(ax)
    title='Electrons' if species=='e-' else 'Photons'
    handles=axs[0,0].get_legend_handles_labels()
    finish(fig,path,f'ODD silicon digitization — {title.lower()}: raw versus digitized response and spread',
           'PROTOTYPE • Same events in all three stages; zeros retained. One independent 20 GeV/c electron factor per η is shared across species/energies/stages.\nErrors: 5,000 paired whole-event/reference bootstrap replicates; shared calibration covariance retained. SD/mean is a distribution spread, not a Gaussian core or reconstructed-energy resolution.',handles)


def reference_plot(data,path):
    fig,axs=plt.subplots(3,3,figsize=(15,12))
    deterministic=data['deterministic']['samples']
    h=dict(deterministic[0]['normalized_residual'])
    h['counts']=np.sum([s['normalized_residual']['counts'] for s in deterministic],axis=0).tolist()
    h['underflow']=sum(s['normalized_residual']['underflow'] for s in deterministic)
    h['overflow']=sum(s['normalized_residual']['overflow'] for s in deterministic)
    hist(axs[0,0],h,label='ECAL per-cell residuals')
    axs[0,0].set(title='A. Noise-off exact-cell check',xlabel='(native − original) / declared numerical tolerance',ylabel='Matched cells',xlim=(-.4,.4),yscale='log')
    comparisons=data['stochastic']['comparisons']
    ax=axs[0,1];ax.axis('off')
    n=sum(s['events'] for s in deterministic);matched=sum(s['matched_cells'] for s in deterministic)
    ax.set_title('B. Software gates and seed checks',loc='left')
    lines=['Original full Gaudi processor versus native adapter','',f"D: {len(deterministic)} samples; {n:,} events",
           f"Matched accepted cells: {matched:,}",
           f"Exact accepted-cell sets: {'PASS' if data['deterministic']['passed'] else 'FAIL'}",
           'Input SimHits/contributions/MC/EventHeaders retained.','',
           f"P/PN gates: {'PASS' if data['stochastic']['passed'] else 'FAIL'} (four conditional replay cases)",
           'Each case: 1,000 ROOT + 1,000 CLHEP draws.',
           'Means ≤5 combined SE; event-CDF permutation p≥0.001;',
           'energy-SD ratio95% bootstrap interval inside [0.85,1.15].','',
           'Effective ROOT low32 seeds distinct and nonzero.',
           'No event-level stochastic bitwise equality expected.',
           'Two repeated source events are not independent showers.']
    ax.text(0,.96,'\n'.join(lines),va='top',fontsize=9,linespacing=1.4)
    endcap=[s for s in comparisons if s['mode']=='PN' and 'gamma' in s['fixture']][0]
    for side,style in [('original','--'),('native','-')]:
        measure=endcap[side]['accepted_cell_amplitude_MIP']
        hist(axs[0,2],measure['histogram'],measure['n'],label='ECAL '+('original Key4hep' if side=='original' else 'native nODD adapter'),linestyle=style)
    axs[0,2].set(title='C. Endcap photon replay PN: cell amplitudes',xlabel='Accepted cell pulse [MIP]',ylabel='Density per accepted cell [MIP⁻¹]',xscale='log',yscale='log',xlim=(.6,1000))
    handles=axs[0,2].get_legend_handles_labels()
    for row,fixture in enumerate(['held-out central muon','endcap gamma20'],start=1):
        cases=[s for s in comparisons if s['fixture']==fixture]
        for col,mode in enumerate(['P','PN']):
            sample=[s for s in cases if s['mode']==mode][0]
            ax=axs[row,col]
            for side,style in [('original','--'),('native','-')]:
                measure=sample[side]['event_energy_MIP']
                hist(ax,measure['histogram'],measure['n'],label='ECAL '+('original Key4hep' if side=='original' else 'native nODD adapter'),linestyle=style)
            test=sample['tests']['event_energy_MIP'];ci=test['width']['percentile95']
            ax.set(title=f"{fixture}; {'pairs only' if mode=='P' else 'pairs + electronics'}",xlabel='Total accepted event signal [MIP]',ylabel='Density per replay event [MIP⁻¹]')
            ax.text(.98,.96,f"CDF p={test['cdf']['p_value']:.3f}\nSD ratio95%: [{ci[0]:.3f}, {ci[1]:.3f}]",transform=ax.transAxes,ha='right',va='top',fontsize=9)
            ax.set_ylim(top=ax.get_ylim()[1]*1.15)
        ax=axs[row,2]
        sample=[s for s in cases if s['mode']=='PN'][0]
        for side,style in [('original','--'),('native','-')]:
            measure=sample[side]['accepted_cell_count']
            hist(ax,measure['histogram'],measure['n'],label='ECAL '+('original Key4hep' if side=='original' else 'native nODD adapter'),linestyle=style)
        ax.set(title=f'{fixture}; PN accepted multiplicity',xlabel='Accepted cells / event',ylabel='Probability per integer bin')
        ax.text(.98,.96,f"CDF p={sample['tests']['accepted_cell_count']['cdf']['p_value']:.3f}",transform=ax.transAxes,ha='right',va='top',fontsize=9)
        ax.set_ylim(top=ax.get_ylim()[1]*1.15)
    for ax in axs.flat:axes_style(ax)
    finish(fig,path,'Silicon digitizer reference validation — original Key4hep and native nODD adapter',
           'PROTOTYPE • Deterministic: pair statistics/noise off. Stochastic: pair energy 3.6 eV, electronics σ=0 or 0.13 MIP; strict threshold 0.6 MIP.\nUnbinned gates use events as exchange/resampling units; pooled cell-amplitude curves are descriptive. Original/ROOT and native/CLHEP streams are independent.',handles)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--response',type=Path)
    parser.add_argument('--reference',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.titlesize':11,'axes.labelsize':10})
    if args.response:
        data=json.loads(args.response.read_text())
        mip_plot(data,args.output/'digitized-mip.png')
        shower_plot(data,'e-',args.output/'digitized-electron.png')
        shower_plot(data,'gamma',args.output/'digitized-photon.png')
    if args.reference:
        reference_plot(json.loads(args.reference.read_text()),args.output/'digitization-reference.png')


if __name__=='__main__':
    main()
