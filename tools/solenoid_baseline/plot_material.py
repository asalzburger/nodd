"""Plot the DES026 assumed incremental material budget and scenario spread."""
import gzip
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
summary=ROOT/'docs/validation/DES-026/material.json'
r=json.loads(summary.read_text());profile=ROOT/r['profile_file']
if hashlib.sha256(profile.read_bytes()).hexdigest()!=r['profile_sha256']:raise ValueError('profile hash mismatch')
data=json.loads(gzip.decompress(profile.read_bytes()))
# Retain dense0.002 sampling at the finite ends;0.01 is sufficient for the
# smooth central curves. All2001 calculation samples remain in the data product.
full=data['reference']
indices=[i for i,x in enumerate(full) if (1.5<=x['eta']<=1.95) or (x['eta']<1.5 and i%5==0) or i==len(full)-1]
ref=[full[i] for i in indices];eta=np.array([x['eta'] for x in ref])
lo=np.array([data['lean'][i]['total'] for i in indices]);hi=np.array([data['heavier'][i]['total'] for i in indices])
plt.rcParams.update({'svg.fonttype':'none','svg.hashsalt':'DES-026-material','font.size':10})
fig,axes=plt.subplots(1,2,figsize=(12,5.8),layout='constrained',gridspec_kw={'width_ratios':[2.3,1]})
components=['cold_mass','vessel','shield'];colors=['#d99732','#909ba5','#4d93bb']
for ax in axes:
    ax.stackplot(eta,*[[x[k] for x in ref] for k in components],colors=colors,alpha=.8)
    ax.fill_between(eta,lo,hi,facecolor='#555555',alpha=.12,hatch='///',edgecolor='#666666',linewidth=0)
    ax.plot(eta,[x['total'] for x in ref],color='#282828',linewidth=1.8)
    ax.plot(eta,lo,color='#555555',ls='--',lw=1);ax.plot(eta,hi,color='#555555',ls='--',lw=1)
    ax.set(xlabel=r'$|\eta|$',ylim=(0,6.2));ax.grid(alpha=.18)
axes[0].set(xlim=(0,4),ylabel=r'Added material $t/X_0$',title='Straight IP rays • incremental solenoid material')
axes[1].set(xlim=(1.50,1.95),title='Finite-length transition')
axes[0].text(.10,5.1,r'$\eta=0$: 1.40 $X_0$ reference'+'\n'+r'1.00–2.10 $X_0$ illustrative scenarios',fontsize=11,bbox={'facecolor':'white','edgecolor':'#bbbbbb','alpha':.9})
axes[0].annotate(r'Reference peak ≈ 3.75 $X_0$'+'\n'+r'at $|\eta|\approx1.67$',xy=(1.67,3.7506),xytext=(2.2,4.25),arrowprops={'arrowstyle':'->'},fontsize=10)
axes[0].text(2.25,.5,'At larger |η| these finite annuli are missed.\nLocal/forward services are not included.',fontsize=9)
handles=[Patch(facecolor=c,label=l) for c,l in zip(colors,['Cold mass: ATLAS-equivalent proxy','Al vessel walls and annular ends','Al thermal shield'])]
handles.append(Patch(facecolor='#888888',alpha=.3,hatch='///',label='Lean/heavier scenarios, not a confidence band'))
fig.legend(handles=handles,loc='outside lower center',ncol=2,fontsize=9,
           title='Assumed inventory; tracker, calorimeter and local services omitted. No native scan.',title_fontsize=9)
fig.suptitle('nODD DES-026 • Added material before ECAL • DRAFT estimate',fontsize=15)
outputs=[]
for ext in ('png','svg'):
    p=ROOT/f'docs/design/figures/DES-026-solenoid-material-vs-eta.{ext}'
    fig.savefig(p,dpi=180,metadata={'Creator':'nODD plot_material.py','Date':None} if ext=='svg' else {})
    if ext=='svg':p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')
    outputs.append(p)
info=dict(status='DRAFT scientific estimate figure',matplotlib=matplotlib.__version__,numpy=np.__version__,
          input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (summary,profile,Path(__file__))},
          output_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in outputs})
(ROOT/'docs/validation/DES-026/material-figure.json').write_text(json.dumps(info,indent=2)+'\n')
print('Rendered added t/X0 versus eta; PNG/SVG and hashes retained.')
