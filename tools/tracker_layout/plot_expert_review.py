#!/usr/bin/env python3
"""Plot retained expert-review evidence; never recompute or select a layout."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from expert_review import segments

ROOT=Path(__file__).resolve().parents[2]
FIG=ROOT/'docs/design/figures'


def main():
    data=json.loads((ROOT/'docs/validation/DES-006-expert-optimisation.json').read_text())
    geometry=json.loads((ROOT/'docs/design/DES-006-reviewed-layouts.json').read_text())
    colors={'pixel':'#b43c46','short_strip':'#e69f00','long_strip':'#0072b2'}
    for c in geometry['candidates']:
        fig,ax=plt.subplots(figsize=(11,3.8),layout='constrained')
        seen=set()
        for layer,a,b in segments(c):
            if max(a[1],b[1])<0: continue
            subsystem=layer['subsystem']
            ax.plot([max(0,a[1])*1000,b[1]*1000],[a[0]*1000,b[0]*1000],color=colors[subsystem],
                    lw=1.4,label=subsystem.replace('_',' ') if subsystem not in seen else None)
            seen.add(subsystem)
        ax.set(xlabel='z [mm]',ylabel='r [mm]',xlim=(0,3150),ylim=(0,1140),
               title=f"{c['id']} — bounded expert-review iteration; PROTOTYPE")
        ax.legend(loc='upper right',fontsize=9);ax.grid(alpha=.2)
        fig.savefig(FIG/f"DES-006-reviewed-{c['id']}-rz.png",dpi=160)
        svg=FIG/f"DES-006-reviewed-{c['id']}-rz.svg"
        fig.savefig(svg)
        svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines())+"\n")
        plt.close(fig)
    styles={'A0':('#555555','--'),'C10':('#a06020','--'),'A':('#0072b2','-'),'C1':('#b43c46','-')}
    names={'A0':'original A','C10':'original C1','A':'iterated A','C1':'iterated C1'}
    for pt in [1.,100.]:
        fig,axes=plt.subplots(3,2,figsize=(11,10),layout='constrained')
        metrics=[('stations','Parent stations'),('local_material_percent','Local material [% X0]'),
                 ('sigma_d0_um','sigma(d0) [µm]'),('sigma_z0_um','sigma(z0) [µm]'),
                 ('sigma_qpt_per_GeV','sigma(q/pT) [GeV⁻¹]'),('last_r_m','Last-hit radius [m]')]
        for ax,(metric,title) in zip(axes.flat,metrics):
            for label,(color,style) in styles.items():
                rows=[r for r in data['profiles'][label] if r['vertex_z_m']==0 and r['pt_GeV']==pt]
                ax.plot([r['eta'] for r in rows],[r[metric] for r in rows],color=color,ls=style,
                        lw=1.4,label=names[label])
            ax.set(xlabel='eta',ylabel=title,xlim=(0,4));ax.grid(alpha=.2)
            if metric.startswith('sigma'): ax.set_yscale('log')
        axes[0,0].legend(fontsize=8)
        fig.suptitle(f'PROTOTYPE • straight-reference Gaussian covariance • pT={pt:g} GeV • 3 T • vertex z=0\n'
                     'Local layer fixtures only; no reconstructed-performance claim',fontsize=12)
        fig.savefig(FIG/f'DES-006-reviewed-profiles-pt{pt:g}.png',dpi=150)
        plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,3.5),layout='constrained')
    for cid,ax in zip(['A','C1'],axes):
        for pt,style in [(1.,'--'),(100.,'-')]:
            old=[r for r in data['profiles'][cid+'0'] if r['vertex_z_m']==0 and r['pt_GeV']==pt]
            new=[r for r in data['profiles'][cid] if r['vertex_z_m']==0 and r['pt_GeV']==pt]
            ax.plot([r['eta'] for r in new],[b['sigma_qpt_per_GeV']/a['sigma_qpt_per_GeV'] for a,b in zip(old,new)],
                    ls=style,label=f'pT={pt:g} GeV')
        ax.axhline(1,color='grey',lw=1);ax.set(xlabel='eta',ylabel='q/pT uncertainty ratio to original',
                                            title=f'{cid}: origin, 3 T',xlim=(.8,1.4));ax.grid(alpha=.2);ax.legend()
    fig.suptitle('Transition recovery and tradeoffs — PROTOTYPE, lower ratio is better')
    fig.savefig(FIG/'DES-006-reviewed-transition.png',dpi=160)
    plt.close(fig)
    print('Rendered A/C1 layouts, 1/100 GeV profiles and transition ratios; Matplotlib',matplotlib.__version__)


if __name__=='__main__': main()
