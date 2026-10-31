#!/usr/bin/env python3
"""Scientific replay figures using unrooted scatter rendering + Matplotlib."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[3]
os.environ.setdefault('MPLBACKEND','Agg')
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'build/strixel-pitch-study/plot-cache/matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME',str(ROOT/'build/strixel-pitch-study/plot-cache/xdg'))
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import unrooted
from unrooted import ScatterData
from unrooted.plot.mpl.scatter import plot as scatter_plot
from unrooted.plot.style import HistogramStyle

COLORS={.5:'#566473',1.:'#007f86',1.5:'#c7771b',2.:'#8b53a2'}
LABELS={'d0':(r'$d_0$','$\mu$m',1000),'z0':(r'$z_0$','$\mu$m',1000),
        'phi':(r'$\phi$','mrad',1000),'theta':(r'$\theta$','mrad',1000),
        'q_over_p':(r'$q/p$',r'$10^{-3}$ GeV$^{-1}$',1000),
        'pt_relative':(r'$\Delta p_T / p_T$','%',100)}


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(fig,output,name,manifest):
    for extension in ('png','pdf'):
        path=output/(name+'.'+extension)
        metadata={'CreationDate':None,'ModDate':None} if extension=='pdf' else None
        fig.savefig(path,dpi=170,bbox_inches='tight',metadata=metadata)
        manifest[path.name]=digest(path)
    plt.close(fig)


def frame(title,subtitle,rows=2,columns=3,footer=None):
    fig,axes=plt.subplots(rows,columns,figsize=(14,8.5 if rows==2 else 5.6),squeeze=False)
    fig.subplots_adjust(left=.075,right=.98,bottom=.18 if rows==2 else .24,
                        top=.77 if rows==2 else .73,wspace=.29,hspace=.42)
    fig.suptitle(title,x=.075,y=.98,ha='left',fontsize=17,weight='bold')
    fig.text(.075,.925 if rows==2 else .90,subtitle,fontsize=10,color='#52606b')
    fig.text(.075,.025,footer or 'PROTOTYPE · PR104 balanced tracker · constant 3 T · native Fatras + truth-associated Kalman fit',
             fontsize=9,color='#52606b')
    return fig,axes


def points(ax,x,y,pitch,label,errors=None):
    color=COLORS[pitch]
    scatter_plot(ScatterData(np.asarray(x,dtype=float),np.asarray(y,dtype=float)),ax=ax,
                 style=HistogramStyle.as_scatter(marker='o',marker_color=color,marker_size=3.3),
                 label=label,set_axis_labels=False)
    ax.plot(x,y,color=color,lw=1.1,alpha=.85)
    if errors is not None:ax.errorbar(x,y,yerr=errors,fmt='none',color=color,lw=.7,capsize=1.4,alpha=.75)


def plot_services(services,output,manifest):
    fig,axes=frame('Strixel pitch: channels, power and service-space sensitivity',
                   'Unqualified load/cable redesign hypotheses; fixed fibres, cooling pipes, local buses and trays.',rows=1,
                   footer='PROTOTYPE · unchanged DES020/021 routes · analytical power and cable-space sensitivities')
    all_channel=[x for x in services['cases'] if x['power_normalization']=='CMS_PS_comparator' and x['channel_dependent_fraction']==1]
    pitch=np.array([x['pitch_v_mm'] for x in all_channel])
    axes[0,0].plot(pitch,[sum(x['channels'].values())/1e6 for x in all_channel],marker='o',color=COLORS[1.],lw=2)
    axes[0,0].set(ylabel='Strixel channels [millions]',title='Same sensor area')
    for fraction,alpha,ls,label in [(1,.22,'-','All FE power channel dependent'),(.5,.10,'--','Half FE power channel dependent')]:
        low=[x['saved_heat_kW'] for x in services['cases'] if x['power_normalization']=='CMS_PS_comparator' and x['channel_dependent_fraction']==fraction]
        high=[x['saved_heat_kW'] for x in services['cases'] if x['power_normalization']=='channel_density_proxy' and x['channel_dependent_fraction']==fraction]
        axes[0,1].fill_between(pitch,low,high,color=COLORS[1.],alpha=alpha)
        axes[0,1].plot(pitch,low,color=COLORS[1.],ls=ls,lw=1.5,label=label)
        axes[0,1].plot(pitch,high,color=COLORS[1.],ls=ls,lw=1.5)
    axes[0,1].set(ylabel='Heat-load reduction [kW]',title='Two existing power proxies')
    axes[0,1].legend(fontsize=8,loc='upper left')
    for fraction,ls,label in [(1,'-','All FE power channel dependent'),(.5,'--','Half FE power channel dependent')]:
        cases=[x for x in services['cases'] if x['power_normalization']=='CMS_PS_comparator' and x['channel_dependent_fraction']==fraction]
        axes[0,2].plot(pitch,[x['saved_power_envelope_L'] for x in cases],marker='o',color=COLORS[1.],ls=ls,label=label)
    axes[0,2].axhline(0,color=COLORS[.5],ls=':',label='Unchanged hardware')
    axes[0,2].set(ylabel='Power cable envelope removed [litres]',title='Conditional harness redesign')
    axes[0,2].legend(fontsize=8,loc='lower right')
    for ax in axes.flat:
        ax.set_xlabel('Short-strip local-v pitch [mm]');ax.set_xticks(pitch)
        ax.grid(alpha=.18);ax.set_axisbelow(True);ax.set_ylim(bottom=0)
    fig.text(.075,.10,'Power bands span comparator normalizations, not confidence bounds. Cable litres include internal void; LV/HV fanout is unqualified.',fontsize=8,color='#52606b')
    save(fig,output,'services-tradeoff',manifest)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data',type=Path,default=ROOT/'docs/validation/DES-042/profiles.json.gz')
    parser.add_argument('--services',type=Path,default=ROOT/'docs/validation/DES-042/services.json')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--services-only',action='store_true')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    manifest={}
    services=json.loads(args.services.read_text())
    for path,expected in services['input_sha256'].items():
        if digest(ROOT/path)!=expected:raise ValueError('Service source changed; regenerate estimate: '+path)
    plot_services(services,args.output,manifest)
    if not args.services_only:
        data=json.loads(gzip.decompress(args.data.read_bytes()))
        if data['provenance']['analyzer_sha256']!=digest(Path(__file__).with_name('analyze.py')):
            raise ValueError('Analysis source changed; replay profiles first')
        for group in data['groups']:
            pt=group['pt_GeV']
            for metric in ('absolute','ratio','common_ratio'):
                title={'absolute':'Track residual widths','ratio':'Resolution ratios to 0.5 mm','common_ratio':'Resolution ratios: common successful events'}[metric]
                events=group['cases'][0]['events']
                fig,axes=frame(f'Strixel pitch study — {title}',f'{pt:g} GeV transverse momentum · {events:,} paired muons per pitch · ideal digital response')
                for ax,(quantity,(label,unit,scale)) in zip(axes.flat,LABELS.items()):
                    for case in group['cases']:
                        pitch=case['pitch_v_mm'];bins=case['eta_profiles']
                        stats=[b['quantities'][quantity]['common_success_residual' if metric=='common_ratio' else 'residual'] for b in bins]
                        x=[(b['low']+b['high'])/2 for b in bins]
                        if metric=='absolute':
                            y=[s['width68']*scale if s['width68'] is not None else np.nan for s in stats]
                            e=[s['width68_se']*scale if s['width68_se'] is not None else np.nan for s in stats]
                        else:
                            if pitch==.5:continue
                            y=[s['ratio_to_baseline'] if s['ratio_to_baseline'] is not None else np.nan for s in stats]
                            e=[s['ratio_se'] if s['ratio_se'] is not None else np.nan for s in stats]
                        points(ax,x,y,pitch,f'{pitch:g} mm',e)
                    ax.set_title(label);ax.set_xlabel('Truth η');ax.set_xlim(-4,4);ax.grid(alpha=.18)
                    if metric=='absolute':
                        ax.set_ylabel(f'Central 68.27% half-width [{unit}]');ax.set_yscale('log')
                    else:
                        ax.axhline(1,color=COLORS[.5],ls='--',lw=1)
                        ax.set_ylabel('Width / 0.5 mm width')
                handles=[Line2D([],[],color=color,marker='o',lw=1.5,label=f'{p:g} mm local-v pitch')
                         for p,color in COLORS.items() if metric=='absolute' or p!=.5]
                fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.068,.88),ncol=4,frameon=False,fontsize=9)
                fig.text(.075,.07,f"Uncut residuals; widths conditional on finite fits. Error bars: paired event-bootstrap SE ({data['bootstrap']['replicates']} resamples). No pattern-recognition claim.",fontsize=8,color='#52606b')
                save(fig,args.output,f'{metric}-pt{pt:g}',manifest)
        fig,axes=frame('Strixel pitch — all-generated fit fractions',
                       'Every generated muon remains in the denominator; native-match fractions are retained separately.',rows=1)
        for ax,group in zip(axes.flat,data['groups']):
            for case in group['cases']:
                bins=case['eta_profiles'];stats=[b['finite_fit_fraction'] for b in bins]
                x=[(b['low']+b['high'])/2 for b in bins]
                y=np.array([s['value'] if s['value'] is not None else np.nan for s in stats])
                e=np.array([[s['value']-s['low'] if s['value'] is not None else np.nan for s in stats],
                            [s['high']-s['value'] if s['value'] is not None else np.nan for s in stats]])
                points(ax,x,y,case['pitch_v_mm'],f"{case['pitch_v_mm']:g} mm",e)
            ax.set(title=f"pT = {group['pt_GeV']:g} GeV",xlabel='Truth η',ylabel='Finite fits / generated muons',xlim=(-4,4),ylim=(0,1.025))
            ax.grid(alpha=.18)
        axes.flat[0].legend(fontsize=8)
        fig.text(.075,.075,'Wilson z=1 intervals. Truth association and truth seeds are used; occupancy and pattern recognition are outside this study.',fontsize=8,color='#52606b')
        save(fig,args.output,'fit-fractions',manifest)
    metadata=dict(schema_version=1,unrooted_version=unrooted.__version__,matplotlib_version=matplotlib.__version__,
                  renderer='unrooted.ScatterData / unrooted.plot.mpl.scatter + Matplotlib lines/errors',
                  plot_source_sha256=digest(__file__),services_sha256=digest(args.services),figures_sha256=manifest)
    if not args.services_only:metadata['profiles_sha256']=digest(args.data)
    (args.output/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print('Rendered',len(manifest),'figure files')


if __name__=='__main__':main()
