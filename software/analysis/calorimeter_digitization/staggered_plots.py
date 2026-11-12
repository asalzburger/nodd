"""Replot compact four-way results as PNG/PDF/vector SVG without event files."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import numpy as np

from angular_sample import ROOT, save, sha
from staggered_results import SERIES


def plot(summary,output,continuous):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patheffects as pe
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                         'savefig.dpi':180,'svg.hashsalt':'nodd-ecal-staggering-tests'})
    output.mkdir(parents=True,exist_ok=True)
    styles=[dict(color='#cccc00',marker='o',ls='-',label='Baseline raw'),
            dict(color='#cccc00',marker='o',ls='--',label='Baseline calibrated'),
            dict(color='#e0e066',marker='s',ls='-',label='Staggered raw'),
            dict(color='#e0e066',marker='s',ls='--',label='Staggered calibrated')]
    def savefig(fig,name):
        for extension in ('png','pdf','svg'):
            path=output/f'{name}.{extension}'
            fig.savefig(path,metadata={'Date':None} if extension=='svg' else None)
            if extension=='svg':path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
        plt.close(fig)
    def value(x):return np.nan if x is None else x
    def curve(ax,x,entries,key,style,factor=1,errors=True):
        y=[value(e[key])*factor for e in entries]
        if errors:
            bounds=np.array([e[key+'_uncertainty']['ci95'] or [np.nan,np.nan] for e in entries])*factor
            ax.vlines(x,bounds[:,0],bounds[:,1],color='#454533',lw=.9)
        line,=ax.plot(x,y,lw=1.7,ms=4.5,markeredgecolor='#555522',**style)
        line.set_path_effects([pe.Stroke(linewidth=2.2,foreground='#777744'),pe.Normal()])
    fig,axes=plt.subplots(2,2,figsize=(13.5,8.5),layout='constrained',gridspec_kw={'height_ratios':[2,1]})
    meanfig,meanaxes=plt.subplots(2,2,figsize=(13.5,7.5),layout='constrained')
    for column,(name,projection) in enumerate(summary['projections'].items()):
        factor=180/math.pi if name=='folded_phi' else 1
        bins=projection['bins'];x=np.array([(b['low']+b['high'])/2*factor for b in bins])
        xlabel=r'$|\eta|$' if name=='abs_eta' else r'Signed sector-folded $\phi$ [deg]'
        for k,label in enumerate(SERIES):
            entries=[b['series'][label] for b in bins]
            curve(axes[0,column],x,entries,'fractional_width',styles[k],100)
            curve(meanaxes[k%2,column],x,entries,'mean',styles[k],100 if k%2==0 else 1)
        if continuous:
            reference=continuous['projections'][name]['bins']
            axes[0,column].plot(x,[b['continuous']['fractional_width']*100 for b in reference],
                'd:',color='#eeee99',markeredgecolor='#777744',lw=1.4,ms=4,label='Continuous Si · raw diagnostic')
        for key,style in (('raw_layout_reduction',styles[0]),('calibrated_layout_reduction',styles[1])):
            entries=[dict(reduction=b['contrasts'][key]['value'],reduction_uncertainty=b['contrasts'][key]) for b in bins]
            st=dict(style);st['label']='Raw' if key.startswith('raw') else 'Calibrated'
            curve(axes[1,column],x,entries,'reduction',st,100)
        axes[0,column].set_ylabel(r'$s(R)/\langle R\rangle$ [%]')
        axes[0,column].set_title('Pseudorapidity' if column==0 else 'Azimuth in one22.5°sector')
        axes[1,column].set_ylabel('Baseline − staggered\n[percentage points]')
        axes[1,column].axhline(0,color='#777777',ls=':',lw=1)
        meanaxes[0,column].set_ylabel('Mean raw silicon response [%]')
        meanaxes[1,column].set_ylabel(r'Mean $E_{cal}/E_{true}$')
        meanaxes[1,column].axhline(1,color='#777777',ls=':',lw=1)
        for ax in (*axes[:,column],*meanaxes[:,column]):
            ax.set_xlabel(xlabel);ax.set_xlim(projection['edges'][0]*factor,projection['edges'][-1]*factor);ax.grid(alpha=.18);ax.set_axisbelow(True)
        axes[0,column].set_ylim(bottom=0);meanaxes[0,column].set_ylim(bottom=0)
    axes[0,0].legend(frameon=False,fontsize=8,loc='upper right')
    axes[1,0].legend(frameon=False,fontsize=8)
    meanaxes[0,0].legend(frameon=False,fontsize=8);meanaxes[1,0].legend(frameon=False,fontsize=8)
    fig.suptitle('nODD ECAL · physical board staggering and held-out calibration\n10,000 identical electron inputs · flat10–80GeV ·12DDSim workers',fontsize=15)
    fig.supxlabel('Raw R=S/Etrue; calibrated R=Ecal/Etrue · All events retained · Approximate95% paired bootstrap\nCalibration preprocessing, tuning and outer-fold models refitted in every replica; continuous Si is a separate diagnostic',fontsize=8)
    savefig(fig,'angular-comparison')
    meanfig.suptitle('Response-scale controls · inclusive held-out predictions',fontsize=15)
    meanfig.supxlabel('Calibration scale bias is retained · Relative gains bounded0.5–3 · No truth position/energy supplied to inference',fontsize=8)
    savefig(meanfig,'mean-response-controls')
    fig,axes=plt.subplots(1,2,figsize=(13.5,5),layout='constrained')
    energy=summary['energy_slices'];x=np.array([(e['low']+e['high'])/2 for e in energy])
    for geometry,name,k in ((0,'baseline',1),(1,'staggered',3)):
        entries=[e['series'][SERIES[k]] for e in energy]
        curve(axes[0],x,entries,'mean',styles[k])
        secondary=[e['prior_sensitivity'][name] for e in energy]
        style=dict(styles[k]);style.update(ls=':',label=name.capitalize()+' ·1/E training prior')
        curve(axes[0],x,secondary,'mean',style,errors=False)
    for k,label in enumerate(SERIES):
        curve(axes[1],x,[e['series'][label] for e in energy],'tail_fraction',styles[k],100,errors=False)
    axes[0].axhline(1,color='#777777',ls=':',lw=1)
    axes[0].set_ylabel(r'Mean $E_{cal}/E_{true}$');axes[1].set_ylabel('Response below half true energy [%]')
    for ax in axes:
        ax.set_xlabel('True-energy slice centre [GeV]');ax.grid(alpha=.18);ax.legend(frameon=False,fontsize=8);ax.set_xlim(10,80)
    axes[1].set_ylim(bottom=0)
    fig.suptitle('Energy closure, training-prior sensitivity and inclusive low-side tails',fontsize=14)
    fig.supxlabel('14fixed5GeV slices; finite-energy-slice checks, not fixed-energy certification\nRaw tail comparator uses cross-fit training-only scale S/R0; prior variants are secondary sensitivity only',fontsize=8)
    savefig(fig,'energy-closure-and-tails')
    fig,axes=plt.subplots(1,2,figsize=(13.5,5),layout='constrained')
    for ax,control,xlabel in ((axes[0],'signed_eta',r'Signed $\eta$ bin'),(axes[1],'sector','Sector index')):
        entries=summary['controls'][control];keys=sorted(entries,key=int);x=np.arange(len(keys))
        for k in (1,3):curve(ax,x,[entries[key][SERIES[k]] for key in keys],'mean',styles[k],errors=False)
        ax.axhline(1,color='#777777',ls=':',lw=1);ax.set_xlabel(xlabel);ax.set_ylabel(r'Mean held-out $E_{cal}/E_{true}$');ax.grid(alpha=.18)
        ax.set_xticks(x[::2] if len(x)>16 else x)
        if control=='signed_eta':ax.set_xticklabels([f'{-3+(int(keys[i])+.5)*.3:.1f}' for i in range(0,len(keys),2)])
    axes[0].legend(frameon=False,fontsize=8)
    fig.suptitle('Signed-direction and sector closure controls',fontsize=14)
    savefig(fig,'direction-sector-closure')
    for calibrated in (False,True):
        pair=(1,3) if calibrated else (0,2)
        histogram_key='calibrated_energy_ratio' if calibrated else 'raw_response_percent'
        edges=summary['histogram_edges'][histogram_key]
        for name,projection in summary['projections'].items():
            fig,axes=plt.subplots(5,2,figsize=(12,14),sharex=True,layout='constrained')
            factor=180/math.pi if name=='folded_phi' else 1
            for ax,entry in zip(axes.flat,projection['bins']):
                for k in pair:
                    p=entry['series'][SERIES[k]];st=styles[k]
                    curve_hist=ax.stairs(p['histogram_counts'],edges,color=st['color'],ls='-' if k<2 else '--',lw=1.5,label=st['label'])
                    curve_hist.set_path_effects([pe.Stroke(linewidth=2.1,foreground='#777744'),pe.Normal()])
                baseline,staggered=[entry['series'][SERIES[k]] for k in pair]
                ax.set_title(f"{entry['low']*factor:.2f} to {entry['high']*factor:.2f}"+('deg' if factor!=1 else ' |η|'),loc='left',fontsize=9)
                ax.text(.98,.95,f"N={baseline['events']}\nwidth:{baseline['fractional_width']*100:.1f}% → {staggered['fractional_width']*100:.1f}%\nzeros:{baseline['zero_events']} → {staggered['zero_events']}",
                    transform=ax.transAxes,ha='right',va='top',fontsize=8,bbox=dict(facecolor='white',alpha=.9,edgecolor='none'))
                maximum=max(max(entry['series'][SERIES[k]]['histogram_counts']) for k in pair)
                ax.set_ylim(0,max(1,maximum*1.3));ax.grid(alpha=.15);ax.set_ylabel('Electrons/bin')
            axes[0,0].legend(frameon=False,fontsize=8,loc='upper left')
            for ax in axes[-1]:ax.set_xlabel(r'$E_{cal}/E_{true}$' if calibrated else 'Raw silicon response [%]')
            label='calibrated' if calibrated else 'raw'
            fig.suptitle(f'Baseline versus physical staggering · {label} · '+('ten |η| populations' if name=='abs_eta' else 'ten foldedφpopulations'),fontsize=14)
            fig.supxlabel('All generated events retained · Shared histogram bins · Widths from unbinned sample SD/mean · No Gaussian fits',fontsize=8)
            savefig(fig,f'distributions-{label}-{name}')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--summary',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--continuous',type=Path,default=ROOT/'docs/validation/ecal10k-untiled/results/comparison.json')
    a=p.parse_args();summary=json.loads(a.summary.read_text());reference=json.loads(a.continuous.read_text()) if a.continuous else None
    plot(summary,a.output,reference)
    save(a.output/'render.json',dict(summary_sha256=sha(a.summary),continuous_sha256=sha(a.continuous) if reference else None,
        plotter_sha256=sha(__file__),source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        outputs={p.name:sha(p) for p in sorted(a.output.iterdir()) if p.suffix in ('.png','.pdf','.svg')}))


if __name__=='__main__':main()
