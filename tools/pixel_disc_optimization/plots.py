"""Original reproducible DES016 scientific comparison drawings."""
import gzip
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch, Circle
from study import ROOT, rectangle, project


def render(cfg,out,layout):
    source=json.loads(gzip.decompress((ROOT/cfg['baseline']).read_bytes()))
    baseline=[rectangle(b['center_mm'],b['u'],b['v'],20.6,19.8) for b in source['bodies'] if b['layer_id']=='A-pixel-P1']
    new=project(layout['modules'],cfg,cfg['disc_datum_mm'],guard=cfg['sensor_guard_mm'])
    fig,axes=plt.subplots(1,2,figsize=(12,6.4),layout='constrained')
    for ax,polys,title in zip(axes,[baseline,new],['Existing quads: 112 modules / 448 chips','Proposed singles: 328 modules / 328 chips']):
        for p in polys:ax.add_patch(Patch(np.array(p.exterior.coords),facecolor='#1583aa',edgecolor='#064560',linewidth=.35,alpha=.28))
        for r in cfg['annulus_mm']:ax.add_patch(Circle((0,0),r,fill=False,edgecolor='#c52e36',linestyle='--',linewidth=1.4))
        ax.set(xlim=(-218,218),ylim=(-218,218),aspect='equal',xlabel='x [mm]',ylabel='y [mm]',title=title)
        ax.grid(alpha=.15)
    fig.suptitle('DES016 — projected physical sensor silicon; dashed circles delimit unchanged active annulus\nDRAFT prototype: enlarged support envelope and failed inherited service packing',fontsize=11)
    fig.savefig(out/'disc-comparison.svg');fig.savefig(out/'disc-comparison.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,3.7),layout='constrained')
    colors=plt.get_cmap('tab10')
    for m in layout['modules']:
        r=np.linalg.norm(m['center_mm'][:2]);z=m['local_z_mm']
        ax.plot([r-cfg['active_mm'][1]/2,r+cfg['active_mm'][1]/2],[z,z],color=colors(m['level']),alpha=.45,lw=2)
    ax.axhspan(-3.15,3.15,color='gray',alpha=.25,label='Inherited 6.3 mm plate thickness only')
    ax.set(xlabel='Module radius [mm]; radial width schematic for Cartesian modules',ylabel='Local outward z [mm]',title='Five levels give ≥0.2 mm module-body separation; supports and flex routes require redesign')
    ax.legend(fontsize=8);ax.grid(alpha=.2);fig.savefig(out/'module-levels.svg');plt.close(fig)

    # Matplotlib emits path-line trailing spaces; preserve tokens, normalize text.
    for path in out.glob("*.svg"):
        path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines())+"\n")
