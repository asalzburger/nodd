#!/usr/bin/env python3
"""Static scientific drawings of the DES039 proposal and its pinned layout fit."""
import json
import math
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/nodd-fcal-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/nodd-fcal-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from model import ROOT, HERE, build, collar_config, sha

COLOURS={'matrix':'#bf6a50','case':'#b63e4c','fanout':'#d8b4e2','sensors':'#356dad','electronics_cooling':'#6ab7c5','service_interface':'#bddad9','front':'#a4aeb7','rear':'#a4aeb7','sampling':'#bf6a50'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','svg.hashsalt':'DES039','axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})


def save(fig,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    for ext in ('svg','png'):
        fig.savefig(path.with_suffix('.'+ext),dpi=180,bbox_inches='tight',metadata={'Creator':'nODD DES039 parametric prototype','Date':'2026-10-17'})
    plt.close(fig)


def rect(ax,z0,z1,r0,r1,colour,side=1,**kwargs):
    x0=z0 if side>0 else -z1
    ax.add_patch(Rectangle((x0,r0),z1-z0,r1-r0,facecolor=colour,**kwargs))


def base_layout(ax,context,full=True):
    h,e,s=context['hcal'],context['ecal'],context['solenoid']
    for side in (-1,1):
        rect(ax,0,h['barrel_half_length_m'],h['barrel_front_apothem_m'],h['barrel_outer_apothem_m'],'#e5e8ec',side,edgecolor='#8491a1',linestyle='--')
        rect(ax,h['endcap_front_abs_z_m'],h['endcap_back_abs_z_m'],h['endcap_inner_apothem_m'],h['endcap_outer_apothem_m'],'#e5e8ec',side,edgecolor='#8491a1',linestyle='--')
        if 'barrel_front_apothem_m' in e:
            rect(ax,0,e['barrel_flange_half_length_m'],e['barrel_front_apothem_m'],e['barrel_outer_apothem_m'],'#e9b551',side,edgecolor='#b17c24')
            rect(ax,e['endcap_front_abs_z_m'],e['endcap_back_abs_z_m'],e['endcap_inner_apothem_m'],e['endcap_outer_apothem_m'],'#e9b551',side,edgecolor='#b17c24')
        else:
            rect(ax,0,e.get('barrel_half_length_m',4.1),e.get('barrel_inner_radius_m',2.0738),e.get('barrel_outer_radius_m',2.83),'#f4dab0',side,edgecolor='#bc985b')
            rect(ax,0,e.get('barrel_active_half_length_m',3.91),e['barrel_sampling_inner_radius_m'],e['barrel_sampling_outer_radius_m'],'#e9b551',side)
            rect(ax,e['endcap_front_abs_z_m'],e['endcap_back_abs_z_m'],e['endcap_inner_radius_m'],e['endcap_outer_radius_m'],'#f4dab0',side,edgecolor='#bc985b')
            for lo,hi in e['endcap_wheels_m']:
                rect(ax,e['endcap_sampling_front_abs_z_m'],e['endcap_sampling_back_abs_z_m'],lo,hi,'#e9b551',side)
    if full:
        for side in (-1,1):
            rect(ax,0,s['vessel_half_length_m'],s['vessel_inner_radius_m'],s['vessel_outer_radius_m'],'#bc9bdb',side,edgecolor='#82629d',hatch='///',alpha=.8)
        for group in context['tracker']['sensitive_groups']:
            colour='#8552a5' if group['component']=='pixel' else ('#367bad' if group['component'].startswith('short') else '#419f80')
            ax.add_patch(Rectangle((group['z_min_m'],group['r_min_m']),group['z_max_m']-group['z_min_m'],group['r_max_m']-group['r_min_m'],facecolor=colour,alpha=.8))
        ax.plot([-4,4],[.0278,.0278],color='#465468',lw=1)
    ax.set_xlabel('z [m]');ax.set_ylabel('r [m]');ax.grid(alpha=.17);ax.set_axisbelow(True)


def module_rects(ax,model,front,side=1):
    c=model['config'];m=c['module']
    rect(ax,front/1000,(front+m['length_mm'])/1000,m['bore_radius_mm']/1000,m['outer_radius_mm']/1000,'#fff0ed',side,edgecolor=COLOURS['case'],lw=1.2)
    for zone,(a,b) in model['zones_mm'].items():
        lo,hi=m['sampling_inner_radius_mm'],m['sampling_outer_radius_mm']
        if zone!='sampling':lo,hi=m['bore_radius_mm']+5,m['rear_shell_inner_mm']
        rect(ax,(front+a)/1000,(front+b)/1000,lo/1000,hi/1000,COLOURS[zone],side,alpha=.94)


def layout_figure(name,core,collar,context,report):
    fig,(a,b)=plt.subplots(2,1,figsize=(15,9.2),gridspec_kw={'height_ratios':[1.9,1.]})
    base_layout(a,context)
    p=core['config']['layouts'][name];fr=p['package_front_abs_z_mm']
    for side in (-1,1):
        module_rects(a,core,fr,side)
        if name=='LAYOUT-002':module_rects(a,collar,4400.,side)
        route=report['layouts'][name]['service_route'];z0,z1=route['radial_handoff_abs_z_mm']
        rect(a,z0/1000,z1/1000,.29,route['handoff_radius_mm']/1000,'#b7e0e6',side,edgecolor='#4a919e',alpha=.8,hatch='//')
    a.set_xlim(-8.35,8.35);a.set_ylim(0,5.15);a.set_aspect('equal',adjustable='box')
    a.set_title(name+' · '+('Si–W ECAL' if name=='LAYOUT-001' else 'LAr ECAL')+' + common tungsten/quartz FCAL',loc='left',fontsize=16,weight='bold')
    a.text(.5,4.7,'HCAL envelope',ha='center',color='#596779')
    a.text(0,1.,'Tracker',ha='center',color='#244059')
    a.text(0,1.7,'Inner solenoid allocation',ha='center',color='#73508c')
    base_layout(b,context,False);module_rects(b,core,fr)
    if name=='LAYOUT-002':
        module_rects(b,collar,4400.)
        b.add_patch(Rectangle((4.84,.291),.05,.147,facecolor='none',edgecolor='#0b7f86',lw=1.3))
        b.plot([4.883,7.9059],[.294,.294],color='#0b7f86',lw=1.5,label='Collar service neck R ≤ 298 mm')
        b.annotate('Short EM collar',xy=(4.46,.39),xytext=(4.42,.57),arrowprops={'arrowstyle':'-','color':'#6d3c35'},color='#6d3c35')
        b.annotate('Collector before cryostat',xy=(4.865,.35),xytext=(5.15,.58),arrowprops={'arrowstyle':'-','color':'#0b7f86'},color='#0b7f86')
    for eta,colour in [(4.,'#44586b'),(5.,'#cf3e55')]:
        xx=[4.25,6.85];b.plot(xx,[x/math.sinh(eta) for x in xx],ls='--',lw=1.2,color=colour,label=f'Prompt straight ray |η| = {eta:g}')
    b.set_xlim(4.28,6.78);b.set_ylim(.02,.64)
    b.set_title('Positive-side forward detail · negative assembly uses proper Rx(π)',loc='left',fontsize=11)
    b.legend(loc='upper right',fontsize=8,frameon=False)
    fig.text(.075,.025,'DRAFT / PROTOTYPE · coloured FCAL zones are a component proposal; neighbouring systems are pinned envelope context.\nSampling: brown · fibre fan-out: purple · SiPM: blue · cooling/electronics: cyan. Pipe beyond |z| = 4 m, full-detector response and engineering remain open.',fontsize=9,color='#4f5f70')
    fig.subplots_adjust(hspace=.34,bottom=.13,top=.93)
    save(fig,ROOT/'docs/layouts/figures'/f'{name}-FCAL-rz')


def package_figure(core,collar,result):
    fig,axes=plt.subplots(2,2,figsize=(14,10),gridspec_kw={'height_ratios':[.85,1.15]})
    a=axes[0,0]
    for label,model,y in [('Common body',core,1.),('02 EM collar',collar,0.)]:
        for zone,(lo,hi) in model['zones_mm'].items():
            a.add_patch(Rectangle((lo,y),hi-lo,.65,facecolor=COLOURS[zone],edgecolor='white'))
            if hi-lo>=80:a.text((lo+hi)/2,y+.325,f'{int(hi-lo)}',ha='center',va='center',fontsize=9,rotation=90 if hi-lo<120 else 0,color='white' if zone in ('sampling','sensors') else '#293a4a')
        a.text(-30,y+.325,label,ha='right',va='center',fontsize=10)
    a.set_xlim(-320,1820);a.set_ylim(-.15,1.95);a.set_yticks([]);a.set_xlabel('Local axial distance [mm]');a.set_title('Complete package allocation',loc='left',weight='bold')
    handles=[Rectangle((0,0),1,1,facecolor=COLOURS[k]) for k in ('sampling','fanout','sensors','electronics_cooling')]
    a.legend(handles,['W/fibre sampling','Fibre fan-out','SiPM cassette','FE / cooling'],fontsize=8,ncol=2,loc='upper right',frameon=False)
    a=axes[0,1]
    for name,colour in [('LAYOUT-001','#ad4d3f'),('LAYOUT-002','#267b9c')]:
        rows=result['layouts'][name]['directional_sampling'];x=[r['abs_eta'] for r in rows]
        a.plot(x,[r['fcal_nuclear_lambda_mean'] for r in rows],color=colour,label=name+' body')
        a.fill_between(x,[r['fcal_nuclear_lambda_min'] for r in rows],[r['fcal_nuclear_lambda_max'] for r in rows],color=colour,alpha=.15)
    rows=result['collar']['layouts']['LAYOUT-002']['directional_sampling'];a.plot([r['abs_eta'] for r in rows],[r['fcal_nuclear_lambda_mean'] for r in rows],color='#8c62a6',ls='--',label='02 collar')
    a.axhline(0,color='#8a8f96',ls=':',lw=1);a.set_xlabel('|η|');a.set_ylabel('FCAL material path [nuclear λ]');a.set_xlim(3,5.2);a.grid(alpha=.2);a.legend(fontsize=8,frameon=False)
    a.set_title('Finite-material paths · sampled φ range / mean',loc='left',weight='bold')
    a.text(.02,.035,'Aligned clamshell seams have zero matrix depth.\nNo shower containment or efficiency is inferred.',transform=a.transAxes,fontsize=8,color='#657185',bbox={'facecolor':'white','alpha':.85,'edgecolor':'none'})
    a=axes[1,0];f=core['fibres']
    a.scatter([x['x_mm'] for x in f],[x['y_mm'] for x in f],s=.35,c=['#be6b50' if x['population']==0 else '#6b85b5' for x in f],rasterized=True)
    for radius in (50,55,125,195,270,290):a.add_patch(Circle((0,0),radius,fill=False,lw=.7,color='#7c8898',ls='--' if radius in (125,195) else '-'))
    a.set_aspect('equal');a.set_xlim(-300,300);a.set_ylim(-300,300);a.set_xlabel('x [mm]');a.set_ylabel('y [mm]');a.set_title(f'Core face · {len(f):,} finite fibre passages',loc='left',weight='bold')
    a=axes[1,1]
    for ch in core['channels']:
        a.add_patch(plt.Polygon(ch['vertices_mm'],closed=True,facecolor='#447eb6' if ch['population']==0 else '#a278b5',edgecolor='white',lw=.5))
    for radius in (50,288,290):a.add_patch(Circle((0,0),radius,fill=False,lw=.8,color='#657185'))
    a.set_aspect('equal');a.set_xlim(-300,300);a.set_ylim(-300,300);a.set_xlabel('x [mm]');a.set_ylabel('y [mm]');a.set_title('Rear readout · 96 × 30 mm cartridge allocations',loc='left',weight='bold')
    fig.suptitle('DES039 · Common tungsten–quartz forward calorimeter',fontsize=18,weight='bold',x=.08,ha='left')
    fig.text(.08,.025,'DRAFT / PROTOTYPE · L/S are overlapping depth weightings. SiPM lifetime, beam heat, optical response, full fan-out and load paths remain unqualified.',fontsize=9,color='#5f6c7c')
    fig.subplots_adjust(hspace=.42,wspace=.3,top=.9,bottom=.08)
    save(fig,ROOT/'docs/design/figures/DES-039/common-fcal')


def main():
    core=build();collar=build(collar_config(core['config']))
    contexts=json.loads((HERE/'layout-contexts.json').read_text())
    result=json.loads((ROOT/'docs/validation/DES-039/geometry.json').read_text())
    for name in core['config']['layouts']:
        layout_figure(name,core,collar,contexts[name],result)
        named={'layout_id':name,'status':'DRAFT / PROTOTYPE, DES039 conditional integration','context_source_revision':contexts[name]['source_revision'],'context_source_path':contexts[name]['source_path'],
               'context_input':'tools/forward_calorimeter/layout-contexts.json','context_sha256':sha(HERE/'layout-contexts.json'),
               'fcal_input':'tools/forward_calorimeter/inputs.json','fcal_input_sha256':sha(HERE/'inputs.json'),'generator':'tools/forward_calorimeter/draw.py','generator_sha256':sha(__file__),
               'body_package_abs_z_mm':result['layouts'][name]['package_abs_z_mm'],'collar_included':name=='LAYOUT-002','source_scope':'Pinned component envelopes plus proposed physical FCAL; no combined native detector, field or response result.'}
        (ROOT/f'docs/layouts/{name}-FCAL.json').write_text(json.dumps(named,indent=2)+'\n')
    package_figure(core,collar,result)
    print('Wrote two integrated layout views, common package drawing and named inputs')


if __name__=='__main__':main()
