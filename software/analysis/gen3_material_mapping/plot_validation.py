#!/usr/bin/env python3
"""Overlay only the validated total on the original Geant4 component stacks."""
import argparse
import csv
import json
import os
from pathlib import Path


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--truth',type=Path,required=True)
    ap.add_argument('--validation',type=Path,required=True)
    ap.add_argument('--selection',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    cache=Path(__file__).resolve().parents[3]/'build/gen3-material-map-run/plot-cache'
    os.environ['MPLBACKEND']='Agg';os.environ.setdefault('MPLCONFIGDIR',str(cache/'matplotlib'))
    os.environ.setdefault('XDG_CACHE_HOME',str(cache/'xdg'))
    import matplotlib.pyplot as plt
    from matplotlib.colors import to_rgb,to_hex
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    import numpy as np
    from unrooted.core import Axis,Histogram
    from unrooted.plot import HistogramStyle
    from unrooted.plot.mpl import stack,plot
    truth=json.loads(args.truth.read_text());validation=json.loads(args.validation.read_text());selection=json.loads(args.selection.read_text())
    detectors=['beam_pipe','pixel','short_strip','long_strip'];names=['Beam pipe','Pixel','Short strip','Long strip']
    colors=['#697681','#2171b5','#e58b20','#37815b'];components=[f'{d}_{s}' for d in detectors for s in ('nonsensitive','sensitive')]
    active=[0,2,3,4,5,6,7];styles=[]
    for i in range(8):
        color=colors[i//2]
        if i%2==0:color=to_hex(.62*np.array(to_rgb(color))+.38)
        styles.append(HistogramStyle.as_stack(line_color=color,fill_color=color,fill_alpha=1,line_width=.4,fill_hatch='/' if i%2 else None))
    truth_style=HistogramStyle.as_line(line_color='#202c37',line_width=1,error_display='band',error_color='#202c37',error_alpha=.15)
    validation_style=HistogramStyle.as_line(line_color='#b2182b',line_width=1.8,error_display='band',error_color='#b2182b',error_alpha=.18)
    axes_names={'eta':r'Pseudorapidity $\eta$','abs_eta':r'Absolute pseudorapidity $|\eta|$','phi':r'Azimuth $\phi$ [rad]'}
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'nodd-material-validation'})
    for axis,xlabel in axes_names.items():
        fig,axes=plt.subplots(2,1,figsize=(13,8.4),sharex=True)
        fig.subplots_adjust(left=.09,right=.73,bottom=.10,top=.83,hspace=.12)
        fig.suptitle('nODD Gen3 material map — validation total',x=.09,y=.97,ha='left',fontsize=19,weight='bold')
        fig.text(.09,.92,f"Geant4: {truth['classification']['tracks']:,} geantinos  ·  ACTS: {validation['tracks']:,} new validation rays",color='#52606b')
        fig.text(.09,.88,f"PROTOTYPE · {selection['counts']['unique_surfaces']} native portals · default phi bins: {selection['configuration']['phi_bins']} · user-selected z/r binning",color='#52606b')
        handles=[]
        for q,ax in zip(('X0','L0'),axes):
            g=truth['axes'][axis];vg=validation['axes'][axis]['quantities'][q];edges=np.array(g['edges'])
            np.testing.assert_array_equal(edges,validation['axes'][axis]['edges'])
            def hist(values,variance,name):return Histogram(axes=[Axis(edges.copy())],values=np.array(values),variances=np.array(variance),name=name)
            pieces=[hist(g['quantities'][q][c]['mean'],g['quantities'][q][c]['variance'],c) for c in components]
            total=g['quantities'][q]['total'];np.testing.assert_allclose(sum(p.values for p in pieces),total['mean'],rtol=2e-13,atol=2e-14)
            stack([pieces[i] for i in active],ax=ax,styles=[styles[i] for i in active],uncertainty=False)
            for patch in ax.patches:
                if patch.get_hatch():patch.set_edgecolor('#243747')
            plot(hist(total['mean'],total['variance'],'Geant4 total'),ax=ax,style=truth_style)
            plot(hist(vg['mean'],vg['variance'],'ACTS validation total'),ax=ax,style=validation_style)
            if vg['empty_bins']:raise ValueError('Do not draw unsupported empty validation bins as zero')
            ax.set_ylabel(r'Mean $t/X_0$' if q=='X0' else r'Mean $t/\lambda_{\mathrm{I}}$')
            ax.set_xlim(edges[0],edges[-1]);ax.set_ylim(bottom=0);ax.grid(axis='y',alpha=.25);ax.set_axisbelow(True)
            with (args.output/f'comparison_{axis}_{q}.csv').open('w',newline='') as stream:
                writer=csv.writer(stream,lineterminator='\n');writer.writerow(['low','high','truth_tracks','validation_tracks','truth_mean','truth_sem','validation_mean','validation_sem','relative_difference'])
                relative=validation['comparison'][axis+'_'+q]['relative_difference']
                for b in range(len(edges)-1):writer.writerow([edges[b],edges[b+1],g['counts'][b],vg['counts'][b],total['mean'][b],np.sqrt(total['variance'][b]),vg['mean'][b],np.sqrt(vg['variance'][b]),relative[b]])
        axes[-1].set_xlabel(xlabel)
        handles=[Patch(facecolor=styles[i].fill_color,edgecolor='#243747' if i%2 else styles[i].line_color,hatch=styles[i].fill_hatch,label=f"{names[i//2]} · {'sensitive' if i%2 else 'non-sensitive'}") for i in active]
        handles += [Line2D([],[],color='#202c37',label='Geant4 total ± SEM'),Line2D([],[],color='#b2182b',lw=1.8,label='ACTS validation total ± SEM')]
        fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.745,.84),frameon=False,fontsize=10,labelspacing=1.2)
        fig.text(.09,.025,'All generated rays contribute, including zeros. Validation is shown only as a total; bands are statistical SEM.',fontsize=9,color='#52606b')
        for extension in ('png','pdf','svg'):
            path=args.output/f'material_validation_{axis}.{extension}';fig.savefig(path,dpi=180,bbox_inches='tight')
            if extension=='svg':path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
        plt.close(fig)
    from matplotlib.collections import LineCollection
    fig,ax=plt.subplots(figsize=(14,5.5))
    families={'before':[],'after':[],'extra':[]}
    for surface in selection['surfaces']:
        layer=next((r for r in surface['roles'] if r['kind']=='sensitive_layer'),None)
        category=layer['side'] if layer else 'extra'
        families[category].append([(z,r) for r,z in surface['rz_segment_mm']])
    for key,color,label in [('before','#3366bb','Layer carrier before sensitive'),('after','#bb3355','Pixel barrel carrier after sensitive'),('extra','#009977','Additional gap / pipe / shell carrier')]:
        ax.add_collection(LineCollection(families[key],colors=color,linewidths=1.1,label=label))
    extents=[point for p in selection['surfaces'] for point in p['rz_segment_mm']]
    rmax=max(p[0] for p in extents);zmax=max(abs(p[1]) for p in extents)
    ax.set(xlim=(-1.025*zmax,1.025*zmax),ylim=(0,1.05*rmax),xlabel='z [mm]',ylabel='r [mm]',
           title=f"Selected Gen3 material portals — {selection['counts']['unique_surfaces']} surfaces, {selection['counts']['material_bins']} bins — PROTOTYPE")
    ax.grid(alpha=.15);ax.legend(loc='upper center',bbox_to_anchor=(.5,-.15),ncol=3,frameon=False)
    fig.text(.5,.015,'One carrier per signed sensitive layer. Shared physical portals are deduplicated; resolved binning is recorded in the selection manifest.',ha='center',fontsize=9)
    fig.subplots_adjust(bottom=.24)
    for extension in ('png','pdf','svg'):
        path=args.output/f'selected-portals-rz.{extension}';fig.savefig(path,dpi=180,bbox_inches='tight')
        if extension=='svg':path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    plt.close(fig)
    print('Rendered validation total over Geant4 stack: eta, abs_eta, phi; PNG/PDF/SVG and comparison CSVs')


if __name__=='__main__':main()
