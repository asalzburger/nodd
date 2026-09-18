#!/usr/bin/env python3
"""Render C1/C2 drawings and two-page briefs from the retained split comparison."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from plot_inclined import layout, text

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/design/figures'


def material(ax, report):
    for cid,color in [('A','#555555'),('C1','#287da8'),('C2','#bf5032')]:
        for zv,ls in [(0.,'-'),(.15,'--')]:
            p=next(p for p in report['profiles'] if p['candidate']==cid and p['pt_GeV']==100 and p['vertex_z_m']==zv)
            mask=[i for i,e in enumerate(report['eta_grid']) if 0<=e<=2.5]
            ax.plot([report['eta_grid'][i] for i in mask],
                    [p['local_material_percent'][i] for i in mask],ls,c=color,label=f'{cid}: vertex {zv:g} m')
    ax.set(xlabel='eta',ylabel='Local material [% X0]',title='3 T, 100 GeV; nominal local fixture, every overlap counted')
    ax.legend(fontsize=7,ncol=3);ax.grid(alpha=.2)


def main():
    config=json.loads((ROOT/'docs/design/DES-006-inclined-split-layouts.json').read_text())
    report=json.loads((ROOT/'docs/validation/DES-006-inclined-split-screen.json').read_text())
    a=config['candidates'][0]
    fig,ax=plt.subplots(figsize=(10,4),layout='constrained');material(ax,report)
    fig.savefig(OUT/'DES-006-C1-C2-comparison.png',dpi=180);plt.close(fig)
    for c in config['candidates'][1:]:
        cid=c['id']; short_only=cid=='C1'
        title='Short strips inclined; long strips cylindrical' if short_only else 'Short and long strips inclined'
        fig,ax=plt.subplots(figsize=(10,3.7),layout='constrained');layout(ax,c,a)
        ax.set_title(f'{cid}: {title} | grey: A barrel reference')
        fig.savefig(OUT/f'DES-006-{cid}-rz.png',dpi=180)
        svg=OUT/f'DES-006-{cid}-rz.svg';fig.savefig(svg);plt.close(fig)
        svg.write_text('\n'.join(l.rstrip() for l in svg.read_text().splitlines())+'\n')
        with PdfPages(ROOT/f'docs/design/DES-006-proposal-{cid}.pdf') as pdf:
            fig=plt.figure(figsize=(8.27,11.69));y=text(fig,.95,f'DES-006 {cid}: {title}',14,True)
            y=text(fig,y,'DRAFT / PROTOTYPE | 2026-09-18 | PR #13 follow-up',10)
            y=text(fig,y,('C1 is the simpler inclined alternative: keep both outer long-strip barrels cylindrical and incline only the four short-strip (strixel) barrel ends.' if short_only else 'C2 is the original C, explicitly renamed. It inclines all four short-strip and both long-strip barrel ends, allowing the incremental outer-barrel benefit to be assessed against C1.'),10)
            y=text(fig,y,'All pixels and endcap disks retain A. Tilted barrel sections keep the original station radii and use six rows per end at |z|=0.65 to 1.15 m in 0.10 m steps. The central |z|<=0.60 m section remains cylindrical. Normals aim toward the origin, capped at 45 degrees; angular edges have 10 mm tangent extensions.',10)
            ax=fig.add_axes([.09,.33,.84,.27]);layout(ax,c,a);ax.set_title(f'{cid}: {title}',fontsize=10)
            y=text(fig,.27,'The drawing shows conical envelopes of planar module rows, not curved silicon or a tiled detector. Overlapping rows contribute their full local material. Phi gaps, actual module dimensions, supports, services and mechanical clearances remain unresolved.',10)
            y=text(fig,y,'Long strips remain double-sided in every option: two scalar faces per paired station, both faces in silicon area, one 2% X0 allowance per pair crossing. The origin/eta=0 reference has 10 stations, 12 silicon-face crossings and 20 ideal scalar coordinates.',10)
            fig.text(.08,.04,f'DES-006 | {cid} | PROTOTYPE | page 1/2',fontsize=8);pdf.savefig(fig);plt.close(fig)
            fig=plt.figure(figsize=(8.27,11.69));y=text(fig,.95,f'{cid}: tradeoffs and optimisation status',14,True)
            y=text(fig,y,('Full-system ideal strixel area is 39.939 m2 versus A 43.953 m2 (-9.13%). Long-strip silicon area stays 111.861 m2, counting both faces. C1 has 48 inclined row envelopes and none in long strips. The sampled local-material ratio C1/A spans 0.779 to 1.117.' if short_only else 'Full-system ideal strixel area is 39.939 m2 (-9.13% versus A). Long-strip silicon area is 109.665 m2 versus 111.861 m2 (-1.96%); both faces are included. C2 adds 24 inclined long-strip row envelopes to C1. The sampled local-material ratio C2/A spans 0.779 to 1.237.'),10)
            y=text(fig,y,'Both alternatives lose no parent station groups relative to A over 21,627 finite-field probes and a finer zero-field vertex scan. These are sampled coverage checks, not efficiency or continuous coverage proof. Area is an ideal proxy, not installed module cost. No C1/C2 IdRes or material-aware fit result is claimed.',10)
            y=text(fig,y,'No systematic radial or axial position optimisation has been performed. Barrel radii are inherited ODD controls; disk positions, annuli and barrel lengths are hand-chosen starting hypotheses. Field/material/vertex sweeps and 0/5/10 mm row-margin checks test feasibility and sensitivity, not an optimum. C1/C2 isolate tilt scope without moving the reference radii or row centres.',10)
            ax=fig.add_axes([.12,.19,.78,.28]);material(ax,report);ax.title.set_fontsize(9)
            text(fig,.135,'Recommendation: investigate C1 first for its simpler outer barrels; retain C2 to quantify whether its small extra area saving can justify stereo support/routing complexity. Review the tradeoff before selecting a layout.',9)
            fig.text(.08,.04,f'Detail: DES-006-C1-C2-review.md | {cid} | page 2/2',fontsize=8);pdf.savefig(fig);plt.close(fig)
    print('Rendered C1/C2 drawings, comparison and two two-page PDFs.')


if __name__=='__main__': main()
