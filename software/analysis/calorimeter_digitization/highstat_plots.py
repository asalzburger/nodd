"""Replot compact staggered calibration evidence without ROOT or event arrays."""
import argparse
import json
import math
from pathlib import Path
import numpy as np
from angular_sample import save, sha


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patheffects as pe
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                         'savefig.dpi':180,'svg.hashsalt':'nodd-staggered-highstat'})
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--learning',type=Path,required=True);parser.add_argument('--summary',type=Path)
    parser.add_argument('--output',type=Path,required=True);a=parser.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    outputs={}
    def emit(fig,name):
        for ext in ('png','pdf','svg'):
            p=a.output/f'{name}.{ext}';fig.savefig(p,bbox_inches='tight',pad_inches=.12,metadata={'Date':None} if ext=='svg' else None)
            if ext=='svg':p.write_text('\n'.join(s.rstrip() for s in p.read_text().splitlines())+'\n')
            outputs[p.name]=sha(p)
        plt.close(fig)
    learning=json.loads(a.learning.read_text());rows=learning['rows'];x=[r['training_events_per_outer_fit'] for r in rows]
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
    for ax,key,label,factor in ((axes[0],'fractional_width','Inclusive sample SD/mean [%]',100),(axes[1],'mean',r'Mean $E_{cal}/E_{true}$',1)):
        ci='width_uncertainty' if key=='fractional_width' else 'mean_uncertainty'
        for xx,row in zip(x,rows):
            bounds=np.array(row[ci]['ci95'])*factor;ax.vlines(xx,*bounds,color='#454533')
        ax.plot(x,[r[key]*factor for r in rows],'o-',color='#cccc00',markeredgecolor='#454533',lw=2)
        ax.set_xscale('log',base=2);ax.set_xticks(x,labels=[f'{v:,}' for v in x]);ax.grid(alpha=.18)
        ax.set_xlabel('Training events per outer fit');ax.set_ylabel(label)
    axes[1].axhline(1,color='#555555',ls=':',lw=1);axes[1].set_ylim(.9,1.01)
    fig.suptitle('Staggered ECAL · learning curve of the frozen original calibration',fontsize=14)
    fig.supxlabel('Same 10,000 held-out predictions across five ID folds · Three nested subset orders\n200 joint whole-event bootstrap refits; exploratory approximate 95% intervals · Old sample already informed model design',fontsize=8)
    emit(fig,'learning-curve')
    if a.summary is None:
        save(a.output/'render.json',dict(learning_sha256=sha(a.learning),plotter_sha256=sha(__file__),outputs=outputs));return
    result=json.loads(a.summary.read_text())
    styles={'raw':dict(color='#cccc00',marker='o',ls='-',label='Raw staggered ECAL'),
            'historical_10k':dict(color='#dddd44',marker='^',ls=':',label='Historical 10k model ensemble'),
            'original_closed':dict(color='#e0e066',marker='s',ls='--',label='Original architecture · 85k fit + 15k closure'),
            'spline_closed':dict(color='#eeee99',marker='D',ls='-',label='Spline correction · 85k fit + 15k closure')}
    def curve(ax,x,entries,key,style,factor=1,errors=True):
        if errors:
            bounds=np.array([e[key+'_full']['ci95'] for e in entries])*factor
            ax.vlines(x,bounds[:,0],bounds[:,1],color='#454533',lw=.8)
        line,=ax.plot(x,[e[key]*factor for e in entries],lw=1.6,ms=4,markeredgecolor='#555522',**style)
        line.set_path_effects([pe.Stroke(linewidth=2.1,foreground='#777744'),pe.Normal()])
    fig,axes=plt.subplots(2,2,figsize=(13.5,8.5),layout='constrained',gridspec_kw={'height_ratios':[2,1]})
    meanfig,meanaxes=plt.subplots(2,2,figsize=(13.5,7.5),layout='constrained')
    for col,(name,projection) in enumerate(result['projections'].items()):
        factor=180/math.pi if name=='folded_phi' else 1;bins=projection['bins']
        x=np.array([(b['low']+b['high'])/2*factor for b in bins]);xlabel=r'$|\eta|$' if col==0 else r'Signed sector-folded $\phi$ [deg]'
        for key,style in styles.items():
            entries=[b['series'][key] for b in bins]
            curve(axes[0,col],x,entries,'fractional_width',style,100)
            curve(meanaxes[0 if key=='raw' else 1,col],x,entries,'mean',style,100 if key=='raw' else 1)
        entries=[dict(d=b['contrasts']['original_minus_spline']['value'],d_full=b['contrasts']['original_minus_spline']['full']) for b in bins]
        curve(axes[1,col],x,entries,'d',dict(color='#cccc00',marker='o',ls='-',label='Original − spline'),100)
        axes[0,col].set_ylim(bottom=0);axes[0,col].set_ylabel('Sample SD/mean [%]')
        axes[1,col].axhline(0,color='#777777',ls=':');axes[1,col].set_ylabel('Original − spline\n[percentage points]')
        meanaxes[0,col].set_ylabel('Mean raw Si response [%]');meanaxes[0,col].set_ylim(bottom=0)
        meanaxes[1,col].set_ylabel(r'Mean $E_{estimated}/E_{true}$');meanaxes[1,col].axhline(1,color='#777777',ls=':')
        for ax in (*axes[:,col],*meanaxes[:,col]):
            ax.set_xlabel(xlabel);ax.grid(alpha=.18);ax.set_xlim(projection['edges'][0]*factor,projection['edges'][-1]*factor)
            if col:ax.set_xticks([-10,-5,0,5,10])
    axes[0,0].legend(frameon=False,fontsize=8);meanaxes[1,0].legend(frameon=False,fontsize=8)
    fig.suptitle('Staggered ECAL · independent 20,000-electron validation\n100,000 training electrons · Uniform E = 10–80 GeV, η = −3…3 and full φ',fontsize=14)
    fig.supxlabel('All events retained · Approximate pointwise 95% intervals from 200 complete training/selection/closure + validation refits\nRaw R = Si signal/Etrue; calibrated R = Eestimated/Etrue · Spectrum-averaged widths, not intrinsic fixed-energy resolution',fontsize=8)
    emit(fig,'angular-comparison');meanfig.suptitle('Independent validation · angular mean-response controls',fontsize=14);emit(meanfig,'angular-means')
    energy=result['energy_slices'];x=[(e['low']+e['high'])/2 for e in energy]
    fig,axes=plt.subplots(1,2,figsize=(13.5,5),layout='constrained')
    for key in ('original_closed','spline_closed'):
        curve(axes[0],x,[e['series'][key] for e in energy],'mean',styles[key])
        before=key.replace('_closed','_pre');style=dict(styles[key]);style.update(ls=':',label=style['label'].split(' · ')[0]+' · before global closure')
        curve(axes[0],x,[e['series'][before] for e in energy],'mean',style)
    for key,style in styles.items():curve(axes[1],x,[e['series'][key] for e in energy],'tail_fraction',style,100)
    axes[0].axhline(1,color='#777777',ls=':');axes[0].set_ylabel(r'Mean $E_{estimated}/E_{true}$')
    axes[1].set_ylabel('Estimated energy below half truth [%]');axes[1].set_ylim(bottom=0)
    for ax in axes:ax.set_xlabel('True-energy slice centre [GeV]');ax.grid(alpha=.18);ax.legend(frameon=False,fontsize=7)
    fig.suptitle('Independent energy closure and inclusive tails',fontsize=14)
    fig.supxlabel('Scale closure fitted on separate 15k training events only; global rescaling leaves SD/mean unchanged\n14 five-GeV slices · Raw tail comparator uses training-only global scale · Full-refit intervals',fontsize=8)
    emit(fig,'energy-closure-and-tails')
    fig,axes=plt.subplots(1,2,figsize=(13.5,5),layout='constrained')
    for ax,name,xlabel in ((axes[0],'signed_eta',r'Signed $\eta$'),(axes[1],'sector','Sector index')):
        entries=result['controls'][name];keys=sorted(entries,key=int);x=np.arange(len(keys))
        for key in ('original_closed','spline_closed'):
            curve(ax,x,[entries[k][key] for k in keys],'mean',styles[key],errors=False)
        ax.axhline(1,color='#777777',ls=':');ax.set_xlabel(xlabel);ax.set_ylabel(r'Mean $E_{estimated}/E_{true}$');ax.grid(alpha=.18)
        if name=='signed_eta':ax.set_xticks(x[::2],labels=[f'{-3+(int(keys[i])+.5)*.3:.1f}' for i in range(0,len(keys),2)])
        else:ax.set_xticks(x)
    axes[0].legend(frameon=False,fontsize=8);fig.suptitle('Independent signed-direction and sector closure · point diagnostics',fontsize=14)
    emit(fig,'direction-sector-closure')
    for calibrated in (False,True):
        keys=('original_closed','spline_closed') if calibrated else ('raw',)
        edges=result['histogram_edges']['calibrated' if calibrated else 'raw']
        for name,projection in result['projections'].items():
            fig,axes=plt.subplots(5,2,figsize=(12,14),sharex=True,layout='constrained');factor=180/math.pi if name=='folded_phi' else 1
            for ax,entry in zip(axes.flat,projection['bins']):
                for key in keys:
                    style=styles[key];line=ax.stairs(entry['series'][key]['histogram_counts'],edges,color=style['color'],ls=style['ls'],lw=1.5,label=style['label'])
                    line.set_path_effects([pe.Stroke(linewidth=2.1,foreground='#777744'),pe.Normal()])
                ax.set_title(f"{entry['low']*factor:.2f} to {entry['high']*factor:.2f}"+(' deg' if factor!=1 else ' |η|'),loc='left',fontsize=9)
                info=[f"N={entry['series'][keys[0]]['events']}"]
                for key in keys:
                    p=entry['series'][key];info.append(f"{key.split('_')[0]}: width {100*p['fractional_width']:.1f}%, zeros {p['zero_events']}")
                ax.text(.98,.95,'\n'.join(info),transform=ax.transAxes,ha='right',va='top',fontsize=8,bbox=dict(facecolor='white',alpha=.9,edgecolor='none'))
                maximum=max(max(entry['series'][k]['histogram_counts']) for k in keys)
                ax.set_ylim(0,max(1,maximum*1.3));ax.grid(alpha=.15);ax.set_ylabel('Electrons/bin')
            axes[0,0].legend(frameon=False,fontsize=7,loc='upper left')
            for ax in axes[-1]:ax.set_xlabel(r'$E_{estimated}/E_{true}$' if calibrated else 'Raw Si response [%]')
            fig.suptitle('Independent 20k validation · '+('calibrated' if calibrated else 'raw')+' · '+name,fontsize=14)
            fig.supxlabel('All events retained · Shared histogram bins · Widths from unbinned sample SD/mean · No Gaussian fits',fontsize=8)
            emit(fig,f'distributions-{"calibrated" if calibrated else "raw"}-{name}')
    save(a.output/'render.json',dict(learning_sha256=sha(a.learning),summary_sha256=sha(a.summary),plotter_sha256=sha(__file__),outputs=outputs))


if __name__=='__main__':main()
