#!/usr/bin/env python3
"""PROTOTYPE candidate-specific composite muon hosts, not baseline geometry."""
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import shlex
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from envelope_study.study import validate, report, project_provenance, ray_interval

ROOT = Path(__file__).resolve().parents[2]


def allocation_comparison(baseline, data):
    """Deterministic prompt-ray host-length comparison; no material or response."""
    old = {r['id']: r for r in baseline['regions']}
    new = {r['id']: r for r in data['regions']}
    output = {'scope': 'Host path lengths only; no X0, interaction lengths or shower containment.',
              'eta_grid': {'min': 0., 'max': 5.2, 'step': .001, 'count': 5201},
              'path_comparison_tolerance_m': 1e-10,
              'families': {}}
    for family in ('ecal', 'hcal'):
        names = (family+'_barrel', family+'_endcap')
        def length(regions, eta):
            return sum(interval[1]-interval[0] for name in names
                       if (interval := ray_interval(regions[name], eta)))
        rows = [(i/1000, length(old, i/1000), length(new, i/1000)) for i in range(5201)]
        worst = min(rows, key=lambda row: row[2]-row[1])
        output['families'][family] = {
            'decreased_path_samples': sum(after < before-1e-10 for _, before, after in rows),
            'new_miss_samples': sum(before > 1e-10 and after <= 1e-10 for _, before, after in rows),
            'worst_change': {'eta': worst[0], 'baseline_m': worst[1], 'candidate_m': worst[2],
                             'delta_m': worst[2]-worst[1]},
            'samples': [{'eta': eta, 'baseline_m': length(old, eta), 'candidate_m': length(new, eta)}
                        for eta in baseline['study']['eta_samples']]}
    output['nominal_depths_m'] = {
        name: {version: regions[name][axis+'_max_m']-regions[name][axis+'_min_m']
               for version, regions in (('baseline', old), ('candidate', new))}
        for name, axis in (('ecal_barrel', 'r'), ('ecal_endcap', 'z'),
                           ('hcal_barrel', 'r'), ('hcal_endcap', 'z'))}
    output['tracker_and_service_bounds_preserved'] = all(
        old[name][key] == new[name][key] for name in ('tracker', 'tracker_services')
        for key in ('r_min_m', 'r_max_m', 'z_min_m', 'z_max_m'))
    output['interface_gaps_m'] = {
        'tracker_services_to_ecal': new['ecal_barrel']['r_min_m']-new['tracker_services']['r_max_m'],
        'ecal_to_hcal_barrel': new['hcal_barrel']['r_min_m']-new['ecal_barrel']['r_max_m'],
        'tracker_to_ecal_endcap': new['ecal_endcap']['z_min_m']-new['tracker']['z_max_m']}
    return output


def assemble(baseline, option):
    data = copy.deepcopy(baseline)
    for name, change in option['overrides'].items():
        next(r for r in data['regions'] if r['id'] == name).update(change)
    template = next(r for r in data['regions'] if r['id'] == 'muon_endcap')
    data['regions'].remove(template)
    if not option.get('endcap_sections'):
        raise ValueError('Explicit endcap sections required')
    for section in option['endcap_sections']:
        data['regions'].append(dict(template, **section))
    ids = [r['id'] for r in data['regions']]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate region identifiers')
    validate(data)
    intersections = report(data)['rectangle_overlaps']
    if intersections:
        raise ValueError(intersections)
    regions = {r['id']: r for r in data['regions']}
    host = regions['muon_barrel']
    previous = host['r_min_m']
    for band in option.get('barrel_radial_budgets', []):
        a,b = band['r_min_m'],band['r_max_m']
        if not (previous <= a < b <= host['r_max_m']):
            raise ValueError('Radial budgets overlap or exceed composite host')
        previous = b
    return data, regions


def validate_winding_containment(winding, magnet):
    if not (magnet['r_min_m'] < winding['r_min_m'] < winding['r_max_m'] < magnet['r_max_m']
            and 0 < winding['half_length_m'] < magnet['z_max_m']):
        raise ValueError('Finite winding outside main-coil reserve')


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Patch
    from matplotlib.lines import Line2D
    plt.rcParams.update({'svg.hashsalt':'nodd-des-004-muon-hosts','font.size':9})
    paths = [ROOT/'tools/magnetic_study/muon-layouts.json',ROOT/'docs/design/DES-003-envelopes.json',
             ROOT/'tools/magnetic_study/windings.json']
    config, baseline, controls = [json.loads(p.read_text()) for p in paths]
    baseline_regions = {r['id']:r for r in baseline['regions']}
    coils = {c['id']:c for c in controls['windings']}
    out = ROOT/'docs/design/figures'
    fig, axes = plt.subplots(3,2,figsize=(18,13))
    fig.subplots_adjust(top=.95,bottom=.18,hspace=.42,wspace=.18)
    result = []

    def rectangle(ax, region, **style):
        for sign in (-1,1):
            z = region['z_min_m'] if sign>0 else -region['z_max_m']
            ax.add_patch(Rectangle((z,region['r_min_m']),region['z_max_m']-region['z_min_m'],
                                  region['r_max_m']-region['r_min_m'],**style))

    def draw(ax, option, regions):
        for r in regions.values():
            rectangle(ax,r,facecolor=r['color'],edgecolor=r['color'],alpha=.55,
                      hatch='///' if r.get('reservation') else None,lw=.6)
        for name in ('muon_barrel','muon_endcap'):
            rectangle(ax,baseline_regions[name],facecolor='none',edgecolor='#a02d25',ls='--',lw=.85)
        host = regions['muon_barrel']
        for band in option.get('barrel_radial_budgets',[]):
            if not option.get('draw_radial_budgets') or band['kind']=='measurement': continue
            region = dict(host, r_min_m=band['r_min_m'],r_max_m=band['r_max_m'])
            rectangle(ax,region,facecolor='none',edgecolor='#542c70' if band['kind']=='coil' else '#555555',
                      hatch='xxx' if band['kind']=='coil' else '...',lw=.6)
        c = coils[option['main_coil_control']]
        rectangle(ax, dict(c, z_min_m=0., z_max_m=c['half_length_m']),
                  facecolor='#412050', edgecolor='#412050', alpha=.9)
        inner, end = [regions[s['id']] for s in option['endcap_sections']]
        ax.set_title(f"{option['id']} · {option['title']}\n"
                     f"Barrel r {host['r_min_m']:g}–{host['r_max_m']:g}, |z| ≤ {host['z_max_m']:g} m\n"
                     f"Endcap inner: r ≤ {inner['r_max_m']:g}, |z| {inner['z_min_m']:g}–{inner['z_max_m']:g}; "
                     f"wide: r ≤ {end['r_max_m']:g}, |z| {end['z_min_m']:g}–{end['z_max_m']:g} m",fontsize=9,pad=8)
        rectangle(ax,inner,facecolor='none',edgecolor='#135b65',lw=1.1)
        ax.text(0,(host['r_min_m']+host['r_max_m'])/2,'COMPOSITE MUON HOST',ha='center',fontsize=7)
        if option.get('inner_space_reallocated'):
            ax.text(0, .2, 'ECal inward 0.40 m · HCal host +0.40 m', ha='center', fontsize=7)
        ax.set(xlim=(-14,14),ylim=(0,10.4),xlabel='z [m]',ylabel='r [m]')
        ax.set_aspect('equal',adjustable='box'); ax.grid(alpha=.16); ax.set_axisbelow(True)

    handles = [Patch(facecolor=r['color'],alpha=.55,label=r['label']) for r in baseline['regions']]
    handles += [Line2D([0],[0],color='#a02d25',ls='--',label='E1-R2 muon host'),
                Patch(facecolor='none',edgecolor='#135b65',label='Upstream endcap step (r ≥ 0.4 m)'),
                Patch(facecolor='#412050',label='Finite homogeneous main winding (vacuum control)')]
    footer=('DRAFT / PROTOTYPE · candidate composite hosts include magnets, chambers, supports and routes; not fully sensitive volumes\n'
            'Steel plates, discrete toroid sectors and end-return closure are not solved or drawn. Winding pack is a vacuum control, not a solved total field.\n'
            'E1-R2 baseline stays unchanged. Forward calorimetry: |z| = 11.2–13.2 m; MAG-02–05 leave a provisional 0.30 m gap (MAG-01: 0.93 m).')

    def save(figure,stem):
        figure.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,.063),ncol=4,fontsize=7)
        figure.text(.5,.018,footer,ha='center',fontsize=8)
        for ext in ('png','svg'):
            figure.savefig(out/(stem+'.'+ext),dpi=160,bbox_inches='tight',metadata={'Date':None} if ext=='svg' else None)
            if ext == 'svg':
                path = out/(stem+'.svg')
                path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
        plt.close(figure)

    for ax, option in zip(axes.flat,config['options']):
        data, regions = assemble(baseline,option)
        c = coils[option['main_coil_control']]; magnet = regions['magnet']
        validate_winding_containment(c, magnet)
        draw(ax,option,regions)
        single, sax = plt.subplots(figsize=(15,8))
        single.subplots_adjust(top=.87,bottom=.28)
        draw(sax,option,regions)
        stem='DES-004-'+option['id'].lower()+'-muon-envelope-rz'
        save(single,stem)
        sections = [regions[s['id']] for s in option['endcap_sections']]
        e = sections[-1]; b = regions['muon_barrel']
        row={'candidate':option['id'],'allocations':[{k:r[k] for k in ('id','r_min_m','r_max_m','z_min_m','z_max_m')} for r in regions.values()],
             'positive_rectangle_intersections':[], 'main_finite_winding_contained':True, 'main_winding':c,
             'barrel_radial_budgets':option.get('barrel_radial_budgets',[]),
             'forward_host_axial_gap_m':regions['forward_calorimeter']['z_min_m']-e['z_max_m'],
             'barrel_composite_radial_depth_m':b['r_max_m']-b['r_min_m'],
             'endcap_sections':[{k:s[k] for k in ('id','r_min_m','r_max_m','z_min_m','z_max_m')} for s in sections],
             'endcap_upstream_clearance_m':sections[0]['z_min_m']-(magnet['z_max_m'] if option['main_coil_control']=='MAG-03' else regions['hcal_endcap']['z_max_m']),
             'endcap_step_to_barrel_radial_gap_m':b['r_min_m']-sections[0]['r_max_m'],
             'endcap_front_ray_radius_m':{str(eta):sections[0]['z_min_m']/math.sinh(eta) for eta in (3.,3.5)},
             'endcap_ray_entries_z_m':{str(eta):{s['id']:(interval[0]*math.tanh(eta) if (interval:=ray_interval(s,eta)) else None) for s in sections} for eta in (3.,3.5)},
             'figure_stem':'docs/design/figures/'+stem}
        row['inner_space_reallocated'] = option.get('inner_space_reallocated', False)
        row['allocation_comparison'] = allocation_comparison(baseline, data)
        if 'trial_steel_radial_bands_m' in option:
            bands = option['trial_steel_radial_bands_m']
            if any(not b['r_min_m']<=lo<hi<=b['r_max_m'] for lo,hi in bands):
                raise ValueError('Trial steel band outside host')
            if any(right[0]<left[1] for left,right in zip(bands,bands[1:])):
                raise ValueError('Trial steel bands overlap')
            area = math.pi*sum(hi*hi-lo*lo for lo,hi in bands)
            flux = 3*math.pi*4.5**2
            row['trial_return_area']={'bands_m':bands,'area_m2':area,'mean_T_if_all_flat_bore_flux_returns':flux/area,
                                     'scope':'Midplane radial area screen only, no endcap flux neck, nonlinear steel or material prescription'}
        result.append(row)
    for ax in list(axes.flat)[len(config['options']):]:
        ax.axis('off')
        ax.text(.5,.5,'MAG-06 withdrawn from study\nExpert review, 2026-09-22\nHistorical evidence retained',
                ha='center',va='center',transform=ax.transAxes,fontsize=12)
    save(fig,'DES-004-muon-envelopes-comparison-rz')
    provenance={**project_provenance(),'command':shlex.join([os.path.relpath(sys.executable),*sys.argv]),
        'python':sys.version.split()[0],'matplotlib':matplotlib.__version__,
        'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths+[Path(__file__).resolve(),ROOT/'tools/envelope_study/study.py']},
        'random_seed':None,'tolerances':'Strict positive rectangle intersection check; no physical tolerances selected'}
    report_path=ROOT/'docs/validation/DES-004-muon-envelope-proposals.json'
    report_path.write_text(json.dumps({'status':'PROTOTYPE; proposed hosts, no baseline amendment or physical acceptance',
        'withdrawn_candidates':[o['id'] for o in config.get('withdrawn_options',[])],
        'provenance':provenance,'limitations':['Composite hosts include non-sensitive magnet/support/service volumes.',
        'No muon stations, nonlinear flux closure, coil forces, phi-sector coverage or material were validated.',
        'Straight-ray aperture samples are not hit efficiency or standalone momentum reach.'], 'results':result},indent=2)+'\n')
    print(f"{len(result)} active candidate allocations: rectangle and finite-winding containment checks passed; {len(result)+1} PNG/SVG drawings generated.")

if __name__ == '__main__': main()
