#!/usr/bin/env python3
"""Render C review figures and a two-page PDF from the retained inclined screen."""
import json
from pathlib import Path
import textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/design/figures'
COLORS=dict(pixel='#1565a8',short_strip='#be7c12',long_strip='#7c429a')


def layout(ax,candidate,baseline):
    for layer in baseline['layers']:
        if layer['kind']=='cylinder':
            ax.plot([0,layer['z_max_m']],[layer['r_m']]*2,c='#aaaaaa',lw=3,alpha=.4)
    for l in candidate['layers']:
        color=COLORS[l['subsystem']]
        if l['kind']=='inclined_ring':
            if l['z0_m']>0: ax.plot([l['z1_m'],l['z2_m']],[l['r1_m'],l['r2_m']],c=color,lw=2)
        elif l['kind']=='cylinder': ax.plot([0,l['z_max_m']],[l['r_m']]*2,c=color,lw=1.5)
        elif l['z_m']>0: ax.plot([l['z_m']]*2,[l['r_min_m'],l['r_max_m']],c=color,lw=1)
    for key,color in COLORS.items(): ax.plot([],[],c=color,label=key.replace('_',' '))
    ax.axhline(1.14,c='black',lw=.6);ax.axvline(3.15,c='black',lw=.6)
    ax.set(xlim=(0,3.25),ylim=(0,1.2),xlabel='z [m]; negative side reflected',ylabel='r [m]')
    ax.legend(fontsize=7,ncol=3,loc='upper right')
    ax.set_title('C: inclined strip rows | grey: A barrel reference',fontsize=10)


def comparison(axes,report):
    for cid,color in [('A','#444444'),('C','#b23a36')]:
        for zv,ls in [(0.,'-'),(.15,'--')]:
            p=next(x for x in report['profiles'] if x['candidate']==cid and x['vertex_z_m']==zv and x['pt_GeV']==100)
            rows=[r for r in p['rows'] if 0<=r['eta']<=3]
            for ax,key in zip(axes,['stations','local_material_percent']):
                ax.plot([r['eta'] for r in rows],[r[key] for r in rows],ls,c=color,label=f'{cid}, z={zv:g} m')
                ax.grid(alpha=.2);ax.set_xlabel('eta')
    axes[0].set_ylabel('Parent station groups'); axes[1].set_ylabel('Local material [% X0]')
    axes[0].legend(fontsize=7)


def text(fig,y,content,size=10,bold=False):
    lines=textwrap.wrap(content,width=92 if size==10 else 78)
    fig.text(.08,y,'\n'.join(lines),ha='left',va='top',fontsize=size,
             fontweight='bold' if bold else 'normal',linespacing=1.4)
    return y-len(lines)*.0175-.018


def main():
    config=json.loads((ROOT/'docs/design/DES-006-inclined-layouts.json').read_text())
    base=json.loads((ROOT/'docs/design/DES-006-layouts.json').read_text())['candidates'][0]
    report=json.loads((ROOT/'docs/validation/DES-006-inclined-screen.json').read_text())
    fig,ax=plt.subplots(figsize=(10,3.7),layout='constrained');layout(ax,config['candidate'],base)
    fig.savefig(OUT/'DES-006-C-rz.png',dpi=180)
    fig.savefig(OUT/'DES-006-C-rz.svg');plt.close(fig)
    fig,axes=plt.subplots(2,1,figsize=(9,6),layout='constrained');comparison(axes,report)
    fig.suptitle('A vs C | 3 T, 100 GeV | ideal row envelopes, nominal local material')
    fig.savefig(OUT/'DES-006-inclined-comparison.png',dpi=180);plt.close(fig)
    with PdfPages(ROOT/'docs/design/DES-006-proposal-C.pdf') as pdf:
        fig=plt.figure(figsize=(8.27,11.69))
        y=text(fig,.95,'DES-006 C: inclined strip barrel ends',14,True)
        y=text(fig,y,'DRAFT / PROTOTYPE | 2026-09-18 | Review response to PR #13',10)
        y=text(fig,y,'Recommendation: retain C as a targeted material and engineering study alongside baseline A. Its benefit is conditional: less ideal sensor area and lower oblique path length compete with extra row overlaps, routing and assembly complexity. No layout is selected.',10)
        y=text(fig,y,'Construction: keep A pixels, endcap disks and six strip barrel station radii. Keep each strip barrel flat for |z| <= 0.60 m. Replace each end by six rows centered at |z| = 0.65, 0.75, 0.85, 0.95, 1.05, 1.15 m. Tilt each normal toward the origin, capped at 45 degrees. Match origin angular edges, then add 10 mm along each row at both ends.',10)
        ax=fig.add_axes([.09,.33,.84,.27]);layout(ax,config['candidate'],base)
        y=text(fig,.27,'These conical ring segments approximate the r-z envelope of inclined planar module rows. Phi tiling, active masks, module sizes, finite thickness and actual clearances remain to be designed. The normal material allowance is unchanged; every overlapping row contributes material.',10)
        y=text(fig,y,'Long strips are double-sided: one stereo module has two scalar sensor faces, one paired station and one 2% X0 local allowance. At eta=0, A and C each give 10 stations, 12 sensor-face crossings and 20 ideal scalar coordinates. Raw IdRes hit counts use a different convention.',10)
        fig.text(.08,.04,'DES-006 | PROTOTYPE | C proposal | page 1/2',fontsize=8,color='#666666');pdf.savefig(fig);plt.close(fig)
        fig=plt.figure(figsize=(8.27,11.69));y=text(fig,.95,'Cost-benefit and review decision',14,True)
        y=text(fig,y,'Full-system ideal strixel area: A 43.953, C 39.939 m2 (-9.1%). Long-strip silicon area counts both faces: A 111.861, C 109.665 m2 (-2.0%). Pixel area stays 4.902 m2. These are ideal area proxies, not installed module counts, money, power or complete material budgets.',10)
        y=text(fig,y,'Across 21,627 signed-eta / field / momentum / vertex probes, nominal C loses no parent station groups relative to A. Its local material ratio C/A spans 0.779 to 1.237: overlapping rows can increase material by about 24%. Zero and 5 mm row margins expose gaps; 10 mm is a study allowance, not a qualified clearance.',10)
        y=text(fig,y,'TrackTech: investigate strixel ends first; the small long-strip area gain may not justify double-sided routing and mechanical complexity. PhysVal: retain both gains and penalties, test tiled coverage before claiming efficiency or lower multiple scattering. C keeps the far-forward pixel system unchanged and does not repair its curvature limitation.',10)
        axes=[fig.add_axes([.12,.35,.78,.15]),fig.add_axes([.12,.13,.78,.15])];comparison(axes,report)
        fig.text(.08,.075,'3 T, 100 GeV, local material only. No C IdRes or scattering-fit result.\nDetail: DES-006-proposal-C.md; inclined TrackTech/PhysVal inputs; inclined-screen.json.',fontsize=8)
        fig.text(.08,.035,'DES-006 | PROTOTYPE | C proposal | page 2/2',fontsize=8,color='#666666');pdf.savefig(fig);plt.close(fig)
    svg=OUT/'DES-006-C-rz.svg';svg.write_text('\n'.join(l.rstrip() for l in svg.read_text().splitlines())+'\n')
    print('Rendered C layout, comparison and two-page reviewer PDF.')


if __name__=='__main__': main()
