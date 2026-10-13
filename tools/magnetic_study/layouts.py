#!/usr/bin/env python3
"""PROTOTYPE: full-detector allocations for DES-004; no physical geometry."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shlex
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from envelope_study.study import validate, report, project_provenance

ROOT = Path(__file__).resolve().parents[2]


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Patch
    plt.rcParams.update({'svg.hashsalt': 'nodd-des-004-layouts', 'font.size': 10})
    config_path = ROOT/'tools/magnetic_study/layouts.json'
    config = json.loads(config_path.read_text())
    baseline_path = ROOT/config['baseline']
    baseline = validate(json.loads(baseline_path.read_text()))
    coils_path = ROOT/'tools/magnetic_study/candidates.json'
    coils = {c['id']: c for c in json.loads(coils_path.read_text())['vacuum_controls']}
    figures = ROOT/'docs/design/figures'
    figures.mkdir(parents=True, exist_ok=True)
    results = []

    def draw(ax, option, data):
        for region in data['regions']:
            for sign in (-1, 1):
                z = region['z_min_m'] if sign > 0 else -region['z_max_m']
                ax.add_patch(Rectangle((z, region['r_min_m']), region['z_max_m']-region['z_min_m'],
                    region['r_max_m']-region['r_min_m'], facecolor=region['color'],
                    edgecolor=region['color'], alpha=.6, hatch='///' if region.get('reservation') else None))
        for name in option['unused_regions']:
            old = next(r for r in baseline['regions'] if r['id'] == name)
            ax.add_patch(Rectangle((-old['z_max_m'], old['r_min_m']), 2*old['z_max_m'],
                old['r_max_m']-old['r_min_m'], facecolor='none', edgecolor='#777777', hatch='...', lw=.8))
        coil = coils[option['id']]
        ax.plot([-coil['half_length_m'], coil['half_length_m']], [coil['radius_m']]*2,
                color='#412050', lw=2.4, zorder=5)
        if option['id'] == 'MAG-03':
            old = next(r for r in baseline['regions'] if r['id'] == 'muon_barrel')
            ax.plot([-old['z_max_m'],old['z_max_m']], [old['r_min_m']]*2,
                    color='#a02d25', ls='--', lw=1)
            ax.annotate('Muon inner edge: 4.35 → 4.95 m (proposed)', xy=(5.2,4.95),
                        xytext=(.0,7.1), ha='center', fontsize=9,
                        arrowprops={'arrowstyle':'->','color':'#333333'})
        ax.text(0, .52, 'TRACKER', ha='center', fontsize=9)
        ax.text(0, 2.95, 'HCAL', ha='center', fontsize=9)
        ax.text(0, 5.9, 'MUON BARREL', ha='center', fontsize=9)
        ax.text(8.7, 3.8, 'MUON\nENDCAP', ha='center', fontsize=8)
        ax.text(-8.7, 3.8, 'MUON\nENDCAP', ha='center', fontsize=8)
        for z in (-12.2,12.2):
            ax.annotate('Forward calo', xy=(z,.9), xytext=(z,2.0), ha='center', fontsize=8,
                        arrowprops={'arrowstyle':'-','color':'#555555'})
        magnet = next(r for r in data['regions'] if r['id'] == 'magnet')
        ax.set_title(f"{option['id']} · {option['title']}\n"
                     f"Coil/cryostat reserve: r = {magnet['r_min_m']:.2f}–{magnet['r_max_m']:.2f} m, "
                     f"|z| ≤ {magnet['z_max_m']:.2f} m; current sheet R = {coil['radius_m']:.3f} m", fontsize=11, pad=12)
        ax.set(xlim=(-14,14), ylim=(0,7.6), xlabel='z [m]', ylabel='r [m]')
        ax.set_aspect('equal', adjustable='box')
        ax.set_xticks(range(-14,15,2)); ax.grid(alpha=.15); ax.set_axisbelow(True)

    legend = [Patch(facecolor=r['color'], alpha=.6, label=r['label'],
                    hatch='///' if r.get('reservation') else None) for r in baseline['regions']]
    from matplotlib.lines import Line2D
    legend += [Line2D([0],[0],color='#412050',lw=2.4,label='Ideal current sheet'),
               Patch(facecolor='none',edgecolor='#777777',hatch='...',label='Unused inner-coil allocation (MAG-03)'),
               Line2D([0],[0],color='#a02d25',ls='--',label='Previous muon inner edge (MAG-03)')]
    footer = ('DRAFT / PROTOTYPE · envelope allocations, not material-filled volumes or active stations\n'
              'No dedicated yoke/toroid drawn; supports, shielding and service routes remain unresolved. '
              'Both options: 3 T centrally.\nMAG-03 keeps calorimeters fixed; the former inner-coil allocation is unused. '
              'Dashed red line is historical, not an extra boundary.')

    def save(fig, stem):
        fig.legend(handles=legend, loc='lower center', bbox_to_anchor=(.5,.07), ncol=4, fontsize=8)
        fig.text(.5,.025,footer,ha='center',fontsize=8)
        fig.savefig(figures/(stem+'.png'),dpi=180,bbox_inches='tight')
        fig.savefig(figures/(stem+'.svg'),metadata={'Date':None},bbox_inches='tight')
        plt.close(fig)

    combined, axes = plt.subplots(2,1,figsize=(15,11))
    combined.subplots_adjust(top=.94,bottom=.23,hspace=.4)
    for option, ax in zip(config['options'],axes):
        data = copy.deepcopy(baseline)
        for name, values in option['overrides'].items():
            next(r for r in data['regions'] if r['id']==name).update(values)
        validate(data)
        diagnostics = report(data)
        if diagnostics['rectangle_overlaps']:
            raise ValueError(diagnostics['rectangle_overlaps'])
        coil = coils[option['id']]
        magnet = next(r for r in data['regions'] if r['id']=='magnet')
        assert magnet['r_min_m'] < coil['radius_m'] < magnet['r_max_m']
        assert coil['half_length_m'] < magnet['z_max_m']
        draw(ax,option,data)
        fig, single = plt.subplots(figsize=(15,6.5))
        fig.subplots_adjust(top=.87,bottom=.31)
        draw(single,option,data)
        stem='DES-004-'+option['id'].lower()+'-system-rz'
        save(fig,stem)
        results.append({'candidate':option['id'],'overrides':option['overrides'],
            'unused_baseline_regions':option['unused_regions'],
            'allocations':[{k:r[k] for k in ('id','r_min_m','r_max_m','z_min_m','z_max_m')} for r in data['regions']],
            'rectangle_overlaps':diagnostics['rectangle_overlaps'],'current_sheet_inside_reserve':True,
            'figure_stem':'docs/design/figures/'+stem})
    save(combined,'DES-004-solenoid-options-system-rz')
    result={'status':'PROTOTYPE allocation drawing; no detector acceptance',
        'provenance':{**project_provenance(),'command':shlex.join([os.path.relpath(sys.executable),*sys.argv]),
            'python':sys.version.split()[0],'matplotlib':matplotlib.__version__,
            'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (config_path,baseline_path,coils_path,Path(__file__).resolve(),ROOT/'tools/envelope_study/study.py')},
            'seed':None,'tolerances':'No physical tolerance; strictly positive rectangle intersections only'},
        'results':results}
    (ROOT/'docs/validation/DES-004-system-layouts.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Two layouts: no rectangular overlaps; sheets within reserves; three PNG/SVG drawings generated.')

if __name__ == '__main__':
    main()
