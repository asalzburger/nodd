#!/usr/bin/env python3
"""Plot old/new hit profiles with unrooted, stacked and individual-marker options."""
import argparse
from importlib.metadata import version
import json
import os
from pathlib import Path

from reduce import sha

COLORS={'pixel':'#0066cc','short_strip':'#ff9933','long_strip':'#009999'}
LABELS={'pixel':'Pixels','short_strip':'Short strips','long_strip':'Long strips'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    os.environ['MPLBACKEND']='Agg'
    os.environ['MPLCONFIGDIR']=str(args.output.resolve()/'.mpl-cache')
    os.environ['XDG_CACHE_HOME']=str(args.output.resolve()/'.cache')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    import numpy as np
    from unrooted.core import Axis,Histogram
    from unrooted.plot import HistogramStyle
    from unrooted.plot.mpl import plot,stack
    data=json.loads(args.data.read_text());edges=np.array(data['edges'])
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,
        'axes.spines.right':False,'axes.axisbelow':True,'grid.color':'#e5e5e5','grid.linewidth':.6})
    def hist(case,name):
        p=case['quantities'][name]
        return Histogram(axes=[Axis(edges.copy())],values=np.array(p['mean']),variances=np.array(p['variance']),name=name)
    def markers(color,marker='o',size=3):
        return HistogramStyle.as_markers(marker_color=color,error_color=color,line_color=color,
            marker=marker,marker_size=size,error_capsize=0,line_width=.7)
    maximum=max(max(c['quantities']['total']['mean']) for c in data['baselines'].values())
    files=[]
    for mode in ('stacked','markers'):
        fig,axes=plt.subplots(1,2,figsize=(14.6,6.5),sharey=True)
        fig.subplots_adjust(left=.075,right=.97,bottom=.18,top=.73,wspace=.10)
        fig.suptitle('nODD tracker hits versus η',x=.075,y=.965,ha='left',fontsize=22,weight='bold')
        fig.text(.075,.90,'Geant4 · matched 100,000 neutral straight rays per baseline · Δη = 0.1',fontsize=11,color='#505050')
        for ax,(baseline,case) in zip(axes,data['baselines'].items()):
            if mode=='stacked':
                stack([hist(case,c) for c in COLORS],ax=ax,uncertainty=False,
                    styles=[HistogramStyle.as_stack(fill_color=color,line_color=color,fill_alpha=1.,line_width=.4)
                            for color in COLORS.values()])
            else:
                for c,marker in zip(COLORS,('s','^','v')):
                    plot(hist(case,c),ax=ax,style=markers(COLORS[c],marker,3.6))
            plot(hist(case,'total'),ax=ax,style=markers('black','o',3.5))
            ax.set_title('Old baseline · 0.5 mm strixels' if baseline=='old' else
                         'New baseline · 2 mm strixels, reduced services',fontsize=12,pad=12)
            ax.set_xlim(-4,4);ax.set_ylim(0,maximum*1.15);ax.grid(axis='y')
            ax.set_xlabel(r'Pseudorapidity $\eta$')
        axes[0].set_ylabel('Mean sensitive crossings per ray')
        handles=[Patch(facecolor=color,label=LABELS[c]) if mode=='stacked' else
            Line2D([],[],color=color,marker=marker,linestyle='none',label=LABELS[c],markersize=6)
            for (c,color),marker in zip(COLORS.items(),('s','^','v'))]
        handles.append(Line2D([],[],color='black',marker='o',linestyle='none',label='Total ± sampling SEM',markersize=5))
        fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.07,.86),ncol=4,frameon=False,fontsize=11)
        fig.text(.075,.075,'One crossing per distinct sensitive physical placement; repeated steps count once. Zero-crossing rays are included.',fontsize=9.5,color='#505050')
        fig.text(.075,.035,'Pixel chips, overlaps and both strip faces count separately. Geometric crossings; no digitization or reconstruction response.',fontsize=9.5,color='#505050')
        for ext in ('png','pdf','svg'):
            path=args.output/f'hits-{mode}.{ext}';fig.savefig(path,dpi=180,facecolor='white')
            if ext=='svg':path.write_text('\n'.join(s.rstrip() for s in path.read_text().splitlines())+'\n')
            files.append({'name':path.name,'sha256':sha(path)})
        plt.close(fig)
    report={'data_sha256':sha(args.data),'plotter_sha256':sha(__file__),'unrooted':version('unrooted'),
            'matplotlib':version('matplotlib'),'colors':COLORS,'files':files}
    (args.output/'plot-report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
