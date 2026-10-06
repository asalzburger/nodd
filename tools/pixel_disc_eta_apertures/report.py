#!/usr/bin/env python3
"""Retain DES018 results, exclusion drawings and before/after layouts."""
import argparse
import importlib.util
import json
import math
from pathlib import Path
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from matplotlib.lines import Line2D
from shapely.geometry import Point

SPEC=importlib.util.spec_from_file_location('eta_report_model',Path(__file__).with_name('study.py'))
model=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(model)


def save(fig, out, stem):
    for suffix in ['png','svg']:
        path = out/(stem+'.'+suffix)
        fig.savefig(path,dpi=180,bbox_inches='tight')
        if suffix == 'svg':
            path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    plt.close(fig)


def table(headers, rows):
    escape = lambda value: str(value).replace('|', '\\|')
    return '\n'.join(['| '+' | '.join(map(escape, headers))+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(escape,row))+' |' for row in rows])


def figures(report, own, cfg, out):
    fig, axes=plt.subplots(2,1,figsize=(13,8),sharex=True,sharey=True,layout='constrained')
    z=model.np.linspace(500,3150,350)
    for ax,name in zip(axes,model.VARIANTS):
        ax.plot(z/1000,[model.inner_bound(x,own) for x in z],color='#15755d',lw=2,label='Conservative eta4 / pT>=1 GeV lower radius')
        ax.plot(z/1000,[(x-150)/math.sinh(4) for x in z],color='#687482',lw=1,ls='--',label='Straight ray, on axis (control)')
        for index,disc in enumerate(report['variants'][name]['positive_discs']):
            full,rings=model.placed(name,disc['datum_mm'],cfg)
            patches=model.baseline.radial.active_patches(full,cfg)
            for ring in rings:
                selected=[p for p in patches if p['row']==ring['row']]
                shapes=[model.baseline.reference.rectangle(p['center_mm'],p['u'],p['v'],p['half_u_mm'],p['half_v_mm']) for p in selected]
                lo=min(p.distance(Point(0,0)) for p in shapes)
                hi=max(math.hypot(*point[:2]) for p in selected for point in model.corners(p))
                removed=ring['row'] in disc['removed_rows']
                ax.plot([disc['datum_mm']/1000]*2,[lo,hi],color='#cf6b27' if removed else '#2878ac',lw=5,solid_capstyle='butt',alpha=.9)
            ax.text(disc['datum_mm']/1000,196,str(index+1),ha='center',fontsize=10)
        ax.axhline(188.5,color='#714686',ls=':',lw=1.2,label='Fixed support outer radius')
        ax.set_ylabel('Active radius [mm]')
        ax.set_title('Eight single rings' if name=='eight-single' else 'Four single + two quad rings',loc='left',fontweight='bold')
        ax.grid(alpha=.17);ax.set_ylim(0,205);ax.set_xlim(.5,3.17)
    fig.legend(handles=[Line2D([],[],color='#2878ac',lw=4,label='Retained active radial extent'),Line2D([],[],color='#cf6b27',lw=4,label='Removed ring'),*axes[0].get_legend_handles_labels()[0]],loc='outside lower center',fontsize=8,ncol=3)
    axes[1].set_xlabel('|disc datum z| [m] — numbered 1 to 9 on each end')
    fig.suptitle('DES018: whole inner-ring removal; sensor offsets are included in the proof',fontsize=14,fontweight='bold')
    save(fig,out,'eta-apertures-rz')

    fig,axes=plt.subplots(2,2,figsize=(11,10),layout='constrained')
    for row,name in enumerate(model.VARIANTS):
        disc=report['variants'][name]['positive_discs'][-1]
        modules,_=model.placed(name,disc['datum_mm'],cfg)
        for column,ax in enumerate(axes[row]):
            for patch in model.baseline.radial.active_patches(modules,cfg):
                removed=patch['row'] in disc['removed_rows']
                if column==1 and removed:
                    continue
                poly=model.baseline.reference.rectangle(patch['center_mm'],patch['u'],patch['v'],patch['half_u_mm'],patch['half_v_mm'])
                ax.add_patch(Polygon(list(poly.exterior.coords),facecolor='#e1a473' if removed else '#76add0',edgecolor='#9b5428' if removed else '#225777',lw=.25))
            ax.add_patch(Circle((0,0),188.5,fill=False,ec='#714686',lw=1))
            ax.add_patch(Circle((0,0),model.inner_bound(3070.,own),fill=False,ec='#15755d',ls='--',lw=1.4))
            ax.set_aspect('equal');ax.set_xlim(-195,195);ax.set_ylim(-195,195)
            ax.set_xlabel('x [mm]');ax.set_ylabel('y [mm]')
            count=disc['before' if column==0 else 'after']
            ax.set_title(f"{'Before' if column==0 else 'After'}: {count['modules']} modules / {count['chips']} chips",fontsize=11)
        axes[row,0].set_ylabel(('Eight single rings' if row==0 else 'Mixed single + quad')+'\ny [mm]',fontweight='bold')
    fig.suptitle('Last pixel disc, |z|=3.070 m — keep ring 4; remove rings 1–3\nGreen circle: nominal-plane lower bound; proof uses each actual sensor plane',fontsize=12)
    save(fig,out,'outer-disc-before-after')


def run(run_dir, native_dir, out):
    own,support,cfg,limits=model.inputs()
    report=json.loads((run_dir/'screening.json').read_text())
    native=json.loads((native_dir/'acts.json').read_text())
    if native['provenance']['screening_sha256']!=model.digest(run_dir/'screening.json'):
        raise ValueError('Native evidence belongs to a different study')
    if report['provenance']['hashes']['tools/pixel_disc_eta_apertures/study.py']!=model.digest(Path(__file__).with_name('study.py')):
        raise ValueError('Study producer changed since execution')
    out.mkdir(parents=True,exist_ok=True)
    for source,name in [(run_dir/'screening.json','screening.json'),(native_dir/'acts.json','acts.json'),(Path(__file__).with_name('inputs.json'),'inputs.json')]:
        shutil.copyfile(source,out/name)
    overlap={}
    for name in model.VARIANTS:
        rows=[]
        for d in report['variants'][name]['positive_discs']:
            full,_=model.placed(name,d['datum_mm'],cfg)
            kept=[m for m in full if m['row'] not in d['removed_rows']]
            before=model.baseline.reference.metrics(model.baseline.radial.project(full,cfg,d['datum_mm'],guard=cfg['sensor_guard_mm']),cfg)
            after=model.baseline.reference.metrics(model.baseline.radial.project(kept,cfg,d['datum_mm'],guard=cfg['sensor_guard_mm']),cfg)
            rows.append(dict(datum_mm=d['datum_mm'],before=before,after=after))
        overlap[name]=rows
        worst=max(max(row['after']['overlap_over_union_percent'],row['after']['annular_overlap_over_union_percent']) for row in rows)
        if worst>cfg['overlap_limit_percent']:
            raise ValueError(f'Removal raises normalized silicon overlap above the retained limit: {name} {worst}')
    (out/'overlap.json').write_text(json.dumps(overlap,indent=2,allow_nan=False)+'\n')
    figures(report,own,cfg,out)
    mixed=report['variants']['four-single-two-quad']
    single=report['variants']['eight-single']
    rows=[]
    for i,(a,b) in enumerate(zip(single['positive_discs'],mixed['positive_discs']),1):
        removed=', '.join(str(r+1) for r in a['removed_rows']) or 'None'
        margin=min((p['minimum_exclusion_margin_mm'] for p in a['proof'] if p['row'] in a['removed_rows']),default=None)
        rows.append([i,f"{a['datum_mm']:.3f}",removed,a['after']['chips'],f"{b['after']['modules']} / {b['after']['chips']}",a['after']['cooling']['number_circuits'],f"{margin:.3f}" if margin is not None else '—'])
    lines=['# DES018 — Eta-limited pixel-disc apertures','',
        '- Status: DRAFT / isolated PROTOTYPE; no production change or human design sign-off.',
        '- Governing [DES018](../../design/DES-018-pixel-disc-eta-apertures.md), frozen [DES017 control](../DES-017/results.md).',
        '- Source baseline: PR42 merge `f2af2714dadd30a722f5ece11d0fd04e92cbfd39` on the prototype branch; exact executed producer/input hashes remain in screening/native evidence.','',
        '**Recommendation:** remove ring 1 on discs 5–6, rings 1–2 on disc 7 and rings 1–3 on discs 8–9, identically on both ends and in both module variants. Retain all rings on discs 1–4. Preserve every surviving placement and stable identifier.','',
        '![Eta aperture schedule](eta-apertures-rz.png)','',
        '## Exact per-disc schedule','',
        table(['Disc on either end','Datum |z| [mm]','Removed original rings','Eight-single chips','Mixed modules / chips','Cooling circuits','Smallest removed-ring margin [mm]'],rows),'',
        'Margins are before the additional 0.10 mm retention buffer; every selected removal exceeds it. The smallest margin over both variants is 1.574 mm. Datums are the unchanged DES017 values, not rounded/repositioned by this study. Ring numbers and survivor IDs keep their original meaning. The RZ figure shows aggregated radial extents, not gap-free coverage at every phi.','',
        '![Last-disc before/after](outer-disc-before-after.png)','',
        '## Why this preserves the requested coverage','',
        'The user selected **pT>=1 GeV** and tracker **|eta|<4**. Selection includes the closed eta4 boundary. Luminous z is±150 mm; transverse x/y are conservatively bounded by±1 mm (a superset of the earlier0..1 mm fixture). The field is a uniform axial0..4 T hypothesis, with charges0 and±1 and first host exit/half-turn as in the inherited oracle.','',
        'From PDG section49.5.2, page8, Eq49.48, `sinh(eta)=cot(theta)`. The smallest transverse arc to each actual sensor plane is `s=(|z_sensor|-150)/sinh(4)`. With `k=0.000299792458*4/1 mm^-1`, the corresponding minimum chord is `2*sin(k*s/2)/k`. Subtracting sqrt(2) mm bounds the transverse vertex displacement. This is an inference from the [PDG definition](https://pdg.lbl.gov/2025/reviews/rpp2025-rev-kinematics.pdf) and the explicit uniform-field helix, not a fitted efficiency.','',
        'On the first outward half-turn, chord increases with arc and decreases with curvature. Consequently the eta4/1 GeV/4 T choice bounds the full continuous specified domain. Every active rectangle corner is tested at its own plane; a convex rectangle has its largest radial norm at a corner. Quad islands and inactive seams stay separate. A whole ring is removed only when all its patches are strictly below the envelope with the extra buffer. Positive/negative reflection preserves this proof.','',
        'The retained fourth ring of disc9 is required: its limiting margin is−0.363 mm (single) or−0.372 mm (mixed). Straight, on-axis geometry would remove it, but omits the transverse vertex envelope. Each first retained ring also has an explicit finite-patch witness; both1 GeV charge signs in4 T reach those witnesses natively. Removing the next ring would therefore lose an in-scope baseline hit. This is a maximal contiguous-prefix removal within the frozen ring catalogue, not a global tiling optimum.','',
        'The all-pT first-half-turn control uses the weaker chord factor2/pi and removes only ring1 on discs8–9. It is deliberately not the selected1 GeV schedule. Lower-pT or recurling/secondary/scattered tracks, nonuniform fields and energy loss require a new study.','',
        '## Savings and unchanged support','',
        f"Both variants remove **{mixed['removed_chips_all_18']} single-chip modules/chips over all18 discs**, saving **{mixed['nominal_heat_saved_all_18_W']:.3f} W nominal** and {1.5*mixed['nominal_heat_saved_all_18_W']:.3f} W in the inherited1.5× heat control. Active chip area removed is{mixed['removed_chips_all_18']*384/1e6:.6f} m²; this is installed area, not projected union or a qualified material budget.",'',
        'Eight-single totals change5328→4904 modules/chips. Mixed totals change2736→2312 modules and5436→5012 chips (15.50% fewer physical assemblies,7.80% fewer chips). Both cooling inventories change288→248 circuits and576→496 feed/return legs. Retained half-ring populations, per-chip heat/contact paths and circuit loads are unchanged; whole empty tracks are deleted. Actual cooling flow and tube-length estimates are retained per disc in screening.json.','',
        'Keep the common6.3 mm sandwich, r27..188.5 mm plate, three tongues/kinematic mounts and carrier. Remove only the omitted modules/pickups and their cooling tracks; retain survivor mounting heights and xy compensation. No support bore enlargement, recolouring, remounting or disc movement is proposed. Empty pickup windows need engineering closeouts before manufacturing; full plate/skin/rail mass is not claimed as saved. All nominal survivor body/stem/core bounds pass. CAD, hydraulics, tolerance/laminate/coupon/FEA qualification remain open.','',
        '## Matched analytic and native checks','']
    for name in model.VARIANTS:
        c=report['variants'][name]['matched_coverage'];n=native['variants'][name]
        lines.append(f"- {name}: {c['tracks']} matched analytic tracks, unchanged exact hit-ID sets ({c['baseline_patch_hits']} hits before and after); {n['in_scope_tracks']} matched native tracks preserve every in-scope hit. Two out-of-scope eta controls expose intended hit losses. Last-disc exhaustive all-plane controls before/after pass.")
    lines += ['',
        'Seeded off-grid tracks include neutral cases, pT1..100 GeV, continuous eta/phi/vertices and0/2/3/4 T. Boundary probes and straight/bent first-retained-ring witnesses supplement them. Native ACTS uses EigenStepper supporting-plane targets, actual RectangleBounds and returned sensitive IDs; neutral motion is checked analytically and by equivalent charged zero-field controls. The native binding accepts±1 only. This is vacuum finite-plane validation, not global navigation, passive transport or fitted resolution.','',
        'Preserving every in-scope baseline hit does **not** make the baseline hermetic: original quad seams, transition holes and outer-edge misses remain. Original full-annulus demand is kept in old evidence; the new eta-limited task justifies these specific inner removals. No acceptance loss is hidden by a smaller denominator or additional hits elsewhere.','',
        '## Heterogeneous service demand','',
        'Counts are recomputed for each disc. The trunk sums the actual first8 disc cable/pipe demands plus the unchanged barrel rather than multiplying one disc by8. The inherited last-disc bypass is reported separately; an all-nine-disc flange-neck control includes it conservatively. Fixed trunk r192..231.7 and neck outer222 mm are retained.','']
    svc=[]
    for name in model.VARIANTS:
        for scenario in report['variants'][name]['accumulated_services']['scenarios']:
            s=scenario['sides'][0]
            svc.append([name,scenario['scenario'],f"{s['trunk_utilization']:.3f}×",f"{s['inherited_neck_utilization']:.3f}×",f"{s['all_nine_neck_control_utilization']:.3f}×",'FAIL' if not s['trunk_pass'] or not s['inherited_neck_pass'] else 'PASS'])
    lines += [table(['Variant','Scenario','Positive trunk','Inherited neck','All-nine neck control','Screen'],svc),'',
        'Mixed reference trunk utilization improves1.089→1.032× and inherited neck1.474→1.397×. Negative-side results and all actual local inventories are retained in screening.json. This optimization improves services but does not close their packing failures. Reference link aggregation remains optimistic; adverse bandwidth scenarios and bypass/manifold routing are unresolved.','',
        'The new overlap.json recomputes silicon overlap on the unchanged original annulus and full projected union. Removing only existing rings creates no new physical neighbour intersections. Maximum selected overlap remains below20%; unchanged first discs retain the original0.5 mm-guard failure. Thermal per-chip interfaces and qualified operating margins are not redefined; the inherited−35°C warm-coolant failures remain.','',
        'Source classifications and the new public PDG catalogue entry are in DES018. Artifact/producer SHA-256 values are in artifacts.json. Draft status is unchanged; technical review should assess the removal schedule and remaining field/material/routing assumptions before adoption.']
    (out/'results.md').write_text('\n'.join(lines)+'\n')
    files=sorted(p for p in out.iterdir() if p.is_file() and p.name!='artifacts.json')
    producers=[Path(__file__),Path(__file__).with_name('study.py'),Path(__file__).with_name('native_audit.py'),Path(__file__).with_name('inputs.json')]
    manifest=dict(status=own['status'],artifact_sha256={p.name:model.digest(p) for p in files},producer_sha256={str(p.relative_to(model.ROOT)):model.digest(p) for p in producers},scope='Actual hashes at execution; enclosing commits never substituted for run source/native hashes.')
    (out/'artifacts.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--native',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();run(args.run,args.native,args.output)
