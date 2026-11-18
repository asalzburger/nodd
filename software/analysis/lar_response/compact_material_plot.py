"""Aggregate deterministic native material rays and draw compact prototype envelopes."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/lar_calorimeter'))
from compact_prototype import configs


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def aggregate(a):
    _,bc,ec,sc=configs()
    result=dict(scope='Native deterministic ray-grid material profiles, not shower efficiency or confidence intervals.',
                candidate_envelopes=dict(barrel=bc,endcap=ec),models={})
    for label,path in [('reference',a.reference),('candidate',a.candidate)]:
        raw=json.loads(path.read_text());model=dict(raw_native_report_sha256=sha(path),compact_sha256=raw['compact_sha256'],materials_sha256=raw['materials_sha256'],profiles=[],phase=[],summary=raw['summary'])
        for eta in sorted({r['eta'] for r in raw['rays'] if r['grid']=='angular'}):
            rows=[r for r in raw['rays'] if (r['grid']=='angular' or r['grid'].startswith('period_')) and r['eta']==eta]
            entry=dict(abs_eta=eta,rays=len(rows))
            for field in ('sampling','barrel','endcap','upstream','downstream','between_or_no_sampling'):
                vals=np.array([r['sampling_x0'] if field=='sampling' else r['x0'].get(field,0.) for r in rows])
                entry[field]=dict(min=float(vals.min()),mean=float(vals.mean()),max=float(vals.max()))
            model['profiles'].append(entry)
        phase=[r for r in raw['rays'] if r['grid']=='barrel_phase']
        model['phase']=[dict(electrode_phase=i/len(phase),sampling_x0=r['sampling_x0']) for i,r in enumerate(phase)]
        selected=[r['x0'].get('endcap',0.) for r in raw['rays'] if r['grid']=='endcap_phase']
        model['endcap_selected_minmax_x0']=[min(selected),max(selected)]
        result['models'][label]=model
    result['extractor_sha256']=sha(__file__)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')


def plot(a):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    d=json.loads(a.summary.read_text());a.output.mkdir(parents=True,exist_ok=True)
    def export(fig,name):
        fig.tight_layout(rect=(0,.035,1,.94));fig.text(.02,.01,'PROTOTYPE · deterministic native material scan; no shower/engineering acceptance',fontsize=9)
        for ext in ('png','pdf','svg'):fig.savefig(a.output/(name+'.'+ext),dpi=160)
        plt.close(fig)
    styles={'reference':dict(color='#dada66',ls='--',label='Original LAr'),'candidate':dict(color='#cccc00',ls='-',label='Compact / deepened LAr')}
    fig,axs=plt.subplots(1,2,figsize=(12,4.5))
    for key,m in d['models'].items():
        x=[r['abs_eta'] for r in m['profiles']];y=[r['sampling']['mean'] for r in m['profiles']]
        axs[0].plot(x,y,**styles[key]);axs[0].fill_between(x,[r['sampling']['min'] for r in m['profiles']],[r['sampling']['max'] for r in m['profiles']],color=styles[key]['color'],alpha=.2)
        axs[1].plot([r['electrode_phase'] for r in m['phase']],[r['sampling_x0'] for r in m['phase']],**styles[key])
    axs[0].axhline(25,color='#777777',lw=1,label='25 X₀ interior screening target');axs[0].set(xlabel='|η|',ylabel='Sampling material depth [X₀]');axs[0].legend(fontsize=9)
    axs[1].set(xlabel='Fraction of own electrode period at η=0',ylabel='Sampling material depth [X₀]');axs[1].legend()
    for ax in axs:ax.grid(alpha=.2)
    fig.suptitle('Actual native sampling depth · bands span the sampled azimuths');export(fig,'sampling-depth')
    fig,axs=plt.subplots(1,2,figsize=(12,4.5))
    for ax,(key,m) in zip(axs,d['models'].items()):
        x=[r['abs_eta'] for r in m['profiles']]
        for field,color,ls in [('sampling','#cccc00','-'),('upstream','#888888','--'),('downstream','#bbbbbb',':')]:ax.plot(x,[r[field]['mean'] for r in m['profiles']],color=color,ls=ls,label=field)
        ax.set(title=styles[key]['label'],xlabel='|η|',ylabel='Material depth [X₀]');ax.grid(alpha=.2);ax.legend()
    fig.suptitle('Sampling separated from walls, baths and services');export(fig,'material-partition')
    b=d['candidate_envelopes']['barrel'];e=d['candidate_envelopes']['endcap'];fig,axs=plt.subplots(1,2,figsize=(12,4.5))
    for ax,new in zip(axs,(False,True)):
        outer=b['sampling_outer_radius_mm']+sum(b[k] for k in ('rear_bath_mm','rear_cold_mm','rear_vacuum_mm','rear_warm_mm'))
        front,back,outer=(b['sampling_inner_radius_mm'],b['sampling_outer_radius_mm'],outer) if new else (2172.8,2578.3,2830)
        ef,eb,es=(e['warm_front_z_mm'],e['warm_back_z_mm'],e['sampling_front_z_mm']+e['sampling_depth_mm']) if new else (4900,5860,5460)
        def rect(z0,z1,r0,r1,**kw):ax.add_patch(Rectangle((z0/1000,r0/1000),(z1-z0)/1000,(r1-r0)/1000,**kw))
        rect(0,3600,0,1200,color='#009999',alpha=.2,label='Tracker truth envelope')
        rect(0,3850,1240,1640,color='#999999',alpha=.6,label='Solenoid assembly reservation')
        rect(0,4100,1700 if new else 2100,outer,facecolor='none',edgecolor='#cccc00',label='ECAL warm envelope')
        rect(0,3910,front,back,color='#cccc00',alpha=.65,label='ECAL sampling envelope')
        rect(ef,eb,301,2949,facecolor='none',edgecolor='#cccc00')
        rect(5210 if new else 5010,es,410,2790,color='#cccc00',alpha=.65)
        ax.set(xlim=(0,6.5),ylim=(0,3.2),xlabel='|z| [m]',ylabel='r [m]',title='Compact candidate' if new else 'Original model');ax.grid(alpha=.15)
    axs[0].legend(fontsize=8,loc='lower right');fig.suptitle('Model envelopes · radial proportions retained; services and wall budgets preserved');export(fig,'compact-envelopes')


if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='stage',required=True)
    q=sub.add_parser('aggregate');q.add_argument('--reference',type=Path,required=True);q.add_argument('--candidate',type=Path,required=True);q.add_argument('--output',type=Path,required=True)
    q=sub.add_parser('plot');q.add_argument('--summary',type=Path,required=True);q.add_argument('--output',type=Path,required=True)
    a=p.parse_args();globals()[a.stage](a)
