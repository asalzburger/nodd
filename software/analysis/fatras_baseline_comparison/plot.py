#!/usr/bin/env python3
"""Export measured-parameter resolution comparisons and loss diagnostics."""
import argparse
import gzip
from importlib.metadata import version
import json
import os
from pathlib import Path

from analyze import sha, MOMENTA

PANELS={
    'd0':(r'$d_0$',r'68.27% half-width [µm]',1000.),
    'z0':(r'$z_0$',r'68.27% half-width [µm]',1000.),
    'phi':(r'$\phi$',r'68.27% half-width [mrad]',1000.),
    'theta':(r'$\theta$',r'68.27% half-width [mrad]',1000.),
    'q_over_p':(r'$q/p$',r'68.27% half-width [$e$/GeV]',1.),
    'pt_relative':(r'$(p_\mathrm{T}^{fit}-p_\mathrm{T}^{true})/p_\mathrm{T}^{true}$',r'68.27% half-width [%]',100.)}
BASELINES={'old':('#777777','--','s','Old baseline · 0.5 mm strixels'),
           'current':('black','-','o','New baseline · 2 mm, reduced services')}
PT_COLORS={1:'#5e3c99',5:'#2166ac',10:'#00876c',100:'#d95f02'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    os.environ['MPLBACKEND']='Agg';os.environ['MPLCONFIGDIR']=str(args.output.resolve()/'.mpl-cache')
    os.environ['XDG_CACHE_HOME']=str(args.output.resolve()/'.cache')
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    with (gzip.open(args.data,'rt') if args.data.suffix=='.gz' else args.data.open()) as f:data=json.load(f)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
        'axes.spines.right':False,'axes.axisbelow':True,'grid.color':'#e5e5e5','grid.linewidth':.6})
    files=[]
    def save(fig,name):
        for extension in ('png','pdf','svg'):
            target=args.output/f'{name}.{extension}';fig.savefig(target,dpi=180,facecolor='white')
            if extension=='svg':target.write_text('\n'.join(s.rstrip() for s in target.read_text().splitlines())+'\n')
            files.append({'name':target.name,'sha256':sha(target)})
        plt.close(fig)
    def frame(title,subtitle):
        fig,axes=plt.subplots(2,3,figsize=(14.2,8.8),sharex=True)
        fig.subplots_adjust(left=.075,right=.975,top=.79,bottom=.13,hspace=.34,wspace=.31)
        fig.suptitle(title,x=.075,y=.965,ha='left',fontsize=21,weight='bold')
        fig.text(.075,.917,subtitle,fontsize=11,color='#505050')
        for ax,(parameter,(label,unit,scale)) in zip(axes.flat,PANELS.items()):
            ax.set_title(label,fontsize=12);ax.set_xlim(0,4);ax.set_xlabel(r'$|\eta|$');ax.grid(axis='y')
        return fig,axes
    baseline_handles=[Line2D([],[],color=color,linestyle=line,marker=marker,markerfacecolor='white' if b=='old' else color,
                     markersize=4,label=label) for b,(color,line,marker,label) in BASELINES.items()]
    for momentum in MOMENTA:
        if not all(f'{b}-pt{momentum}' in data['cases'] for b in BASELINES):continue
        fig,axes=frame('nODD Fatras truth-tracking resolutions',
            rf'$p_\mathrm{{T}}={momentum}$ GeV · 20,000 matched generated muons per baseline · 3 T · Δη = 0.5 in |η|')
        fig.legend(handles=baseline_handles,loc='upper left',bbox_to_anchor=(.07,.875),ncol=2,frameon=False,fontsize=10.5)
        for ax,(parameter,(label,unit,scale)) in zip(axes.flat,PANELS.items()):
            for baseline,(color,line,marker,_) in BASELINES.items():
                rows=data['cases'][f'{baseline}-pt{momentum}']['abs_eta']
                valid=[r for r in rows if r['parameters'][parameter]['residual']['width68'] is not None]
                x=[.5*(r['low']+r['high']) for r in valid]
                y=[r['parameters'][parameter]['residual']['width68']*scale for r in valid]
                error=[r['parameters'][parameter]['residual']['width68_se']*scale for r in valid]
                ax.errorbar(x,y,yerr=error,color=color,linestyle=line,marker=marker,markersize=3.7,
                    markerfacecolor='white' if baseline=='old' else color,linewidth=1.1,capsize=2)
            ax.set_ylabel(unit);ax.set_yscale('log')
        fig.text(.075,.059,'Widths use all finite fits, including tails and wrong-charge fits. Error bars: 400 event-bootstrap sampling SE.',fontsize=9,color='#505050')
        fig.text(.075,.028,'Truth-associated Kalman fits, ≥7 unique measurements. Selection/fitting losses and full SD/RMS are retained separately; time is unmeasured.',fontsize=9,color='#505050')
        save(fig,f'resolutions-pt{momentum}')
    fig,axes=frame('New / old track-parameter resolution',
        'Fatras truth tracking · ratio of central 68.27% half-widths · paired generated-event bootstrap, pointwise 95% intervals')
    handles=[]
    for momentum,marker in zip(MOMENTA,('o','s','^','D')):
        if str(momentum) not in data['paired']:continue
        color=PT_COLORS[momentum];handles.append(Line2D([],[],color=color,marker=marker,label=f'pT = {momentum} GeV'))
        for ax,parameter in zip(axes.flat,PANELS):
            rows=data['paired'][str(momentum)]['abs_eta']
            valid=[r for r in rows if r['parameters'][parameter]['ratio_bootstrap95'] is not None]
            if not valid:continue
            x=np.array([.5*(r['low']+r['high']) for r in valid])
            y=np.array([r['parameters'][parameter]['ratio'] for r in valid])
            intervals=np.array([r['parameters'][parameter]['ratio_bootstrap95'] for r in valid])
            # Percentile intervals need not contain the plug-in estimate.
            ax.vlines(x,intervals[:,0],intervals[:,1],color=color,linewidth=.9)
            ax.plot(x,y,color=color,marker=marker,markersize=3.5,linewidth=1.0)
    for ax in axes.flat:
        ax.axhline(1,color='#777777',linestyle=':',linewidth=.8);ax.set_ylabel('Current / old width')
        ax.set_ylim(bottom=0)
    fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.07,.875),ncol=4,frameon=False,fontsize=10.5)
    fig.text(.075,.059,'Below 1: narrower fitted core; above 1: wider fitted core. Each baseline retains its own missing-fit outcomes when resampling paired events.',fontsize=9,color='#505050')
    fig.text(.075,.028,'Whole baseline comparison: geometry, material and 0.5→2 mm short-strip response change together. Sampling errors omit model/calibration systematics.',fontsize=9,color='#505050')
    save(fig,'resolution-ratios')
    fig,axes=plt.subplots(2,4,figsize=(15,7.5),sharex=True)
    fig.subplots_adjust(left=.07,right=.98,top=.77,bottom=.12,hspace=.20,wspace=.27)
    fig.suptitle('Generated-muon accounting and charge-sign errors',x=.07,y=.965,ha='left',fontsize=20,weight='bold')
    fig.text(.07,.915,'Fatras truth tracking · fixed pT · generated-event denominators retained · pointwise 95% Wilson intervals',fontsize=11,color='#505050')
    fig.legend(handles=baseline_handles,loc='upper left',bbox_to_anchor=(.065,.875),ncol=2,frameon=False,fontsize=10.5)
    for col,momentum in enumerate(MOMENTA):
        axes[0,col].set_title(f'pT = {momentum} GeV')
        for baseline,(color,line,marker,_) in BASELINES.items():
            key=f'{baseline}-pt{momentum}'
            if key not in data['cases']:continue
            rows=data['cases'][key]['abs_eta'];x=np.array([.5*(r['low']+r['high']) for r in rows])
            for row,field in enumerate(('finite_fit_fraction','wrong_charge_fraction_of_finite_fits')):
                estimates=[r['counts'][field] for r in rows]
                valid=np.array([r['value'] is not None for r in estimates])
                y=np.array([r['value'] for r in estimates if r['value'] is not None]);low=np.array([r['low'] for r in estimates if r['value'] is not None]);high=np.array([r['high'] for r in estimates if r['value'] is not None])
                axes[row,col].errorbar(x[valid],y,yerr=[y-low,high-y],color=color,linestyle=line,marker=marker,
                    markerfacecolor='white' if baseline=='old' else color,markersize=3.5,linewidth=1,capsize=2)
        axes[0,col].set_ylim(0,1.05)
        for ax in axes[:,col]:ax.set_xlim(0,4);ax.set_xlabel(r'$|\eta|$');ax.grid(axis='y')
        axes[1,col].set_ylim(bottom=0)
    axes[0,0].set_ylabel('Finite primary fits / generated')
    axes[1,0].set_ylabel('Wrong sign / finite fits')
    fig.text(.07,.035,'Truth-associated reconstruction with ideal truth seeds; this is not a pattern-recognition efficiency or fake-rate measurement.',fontsize=9,color='#505050')
    save(fig,'fit-accounting')
    (args.output/'plot-report.json').write_text(json.dumps({'data_sha256':sha(args.data),'plotter_sha256':sha(__file__),
        'matplotlib':version('matplotlib'),'numpy':version('numpy'),'files':files},indent=2)+'\n')


if __name__=='__main__':main()
