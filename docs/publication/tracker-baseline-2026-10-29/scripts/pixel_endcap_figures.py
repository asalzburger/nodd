"""Current mixed/trimmed endcap drawings, driven by the bundled baseline snapshot."""
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, Wedge, Arc, Patch
from matplotlib.lines import Line2D

B = '#174382'; C = '#0479C1'; O = '#ba6928'; G = '#65717d'
L = '#dae2ea'; K = '#7ca084'; V = '#934c67'


def render(S, D, root):
    def box(ax, x, y, w, h, color, **kw):
        ax.add_patch(Rectangle((x, y), w, h, facecolor=color,
                               edgecolor=kw.pop('edgecolor', color),
                               linewidth=kw.pop('lw', .5), **kw))

    def save(fig, name):
        fig.savefig(root / 'figures' / (name + '.pdf'), bbox_inches='tight', pad_inches=.05,
                    metadata={'Creator': 'nODD pixel_endcap_figures.py', 'CreationDate': None, 'ModDate': None})
        plt.close(fig)

    def polygon(m, du, dv, a=0, b=0):
        return [[m['center_mm'][j] + (a+s*du/2)*m['u'][j] + (b+t*dv/2)*m['v'][j]
                 for j in range(2)] for s,t in [(-1,-1),(1,-1),(1,1),(-1,1)]]

    def plan(ax, disc, face=None, active=True):
        ax.add_patch(Circle((0,0),188.5,facecolor='#f3f5f6',edgecolor=G,lw=.6))
        ax.add_patch(Circle((0,0),27,facecolor='white',edgecolor=G,lw=.5))
        for m in disc['bodies']:
            if face is not None and m['mount_face'] != face:
                continue
            color = B if m['mount_face'] < 0 else O
            ax.add_patch(Polygon(polygon(m,2*m['half_u_mm'],2*m['half_v_mm'],
                                       b=m['body_radial_offset_mm']),facecolor=color,
                                 alpha=.13+.08*m['level'],edgecolor=color,lw=.45))
            if active:
                f=S['radial']['families'][m['family']]
                for i in range(f['columns']):
                    for j in range(f['rows']):
                        a=(i-(f['columns']-1)/2)*20.2
                        b=(j-(f['rows']-1)/2)*19.4
                        ax.add_patch(Polygon(polygon(m,20,19.2,a,b),facecolor=color,
                                             edgecolor='white',lw=.18,alpha=.43))
        for deg in D['endcap']['mounting']['angles_deg']:
            t=math.radians(deg)
            ax.plot([186*math.cos(t),228*math.cos(t)],
                    [186*math.sin(t),228*math.sin(t)],lw=3,color=G)
        ax.add_patch(Circle((0,0),190,fill=False,edgecolor=G,lw=.4,ls=':'))
        ax.set(aspect='equal',xlim=(-237,237),ylim=(-237,237),xlabel='x [mm]',ylabel='y [mm]')
        ax.set_xticks([-200,-100,0,100,200]);ax.set_yticks([-200,-100,0,100,200])

    fig,aa=plt.subplots(1,2,figsize=(6.1,3.5))
    for ax,disc in zip(aa,[S['discs'][0],S['discs'][-1]]):
        plan(ax,disc)
        ax.set_title(f"Disc {disc['index']}: {disc['families']['single']} singles + 50 quads",fontsize=8)
    fig.legend(handles=[Patch(facecolor=B,alpha=.5,label='IP-facing modules'),
                        Patch(facecolor=O,alpha=.5,label='Outward-facing modules'),
                        Line2D([0],[0],color=G,lw=3,label='Mounting tongues')],
               loc='lower center',bbox_to_anchor=(.5,0),ncol=3,fontsize=6.8)
    fig.tight_layout(rect=(0,.13,1,1));save(fig,'pixel-endcap')

    # Actual radial projections: radial body offset is included; both faces/levels
    # are overlaid, rather than pretending they lie in a single azimuthal cut.
    fig,ax=plt.subplots(figsize=(6.1,3.35))
    box(ax,27,-3,161.5,6,K,alpha=.25)
    box(ax,27,-3.15,161.5,.15,G);box(ax,27,3,161.5,.15,G)
    first=S['discs'][0]
    for row in S['rings']:
        modules=[m for m in first['bodies'] if m['row']==row['row']]
        for face,level in sorted({(m['mount_face'],m['level']) for m in modules}):
            ms=[m for m in modules if m['mount_face']==face and m['level']==level]
            r=sum(math.hypot(*m['center_mm'][:2]) for m in ms)/len(ms)
            m=ms[0];v=m['half_v_mm'];z=m['local_z_mm'];h=level*1.65
            color=B if face<0 else O
            box(ax,r+m['body_radial_offset_mm']-v,z-.5,2*v,1,color,alpha=.30+.20*level)
            f=S['radial']['families'][m['family']]
            for chip in range(f['rows']):
                b=(chip-(f['rows']-1)/2)*19.4
                lo,hi=sorted([face*(3.15+h),face*(3.60+h)])
                box(ax,r+b-9.6,lo,19.2,hi-lo,G,alpha=.35)
                # Per-chip stem moves toward the common module centre on quads.
                stem_r=r+b-(math.copysign(1,b) if b else 0)
                if h:
                    lo,hi=sorted([face*3.15,face*(3.15+h)])
                    box(ax,stem_r-4,lo,8,hi-lo,G,alpha=.35)
        ax.text(row['radius_mm'],7.5,str(row['row']+1),ha='center',fontsize=7)
    for track in first['cooling']['tracks']:
        r=track['radius_mm']
        ax.add_patch(Circle((r,1.5),1.4,facecolor=G,lw=.3))
        ax.add_patch(Circle((r,1.5),1.25,facecolor=C,lw=.3))
    ax.axhline(0,color=G,lw=.4,ls=':')
    ax.set(xlim=(23,193),ylim=(-7.3,8.4),xlabel='radial coordinate [mm]',ylabel='local outward z [mm]')
    ax.text(190,-6.9,'IP side',ha='right',fontsize=7,color=B)
    ax.legend(handles=[Patch(facecolor=B,alpha=.5,label='IP-facing bodies'),Patch(facecolor=O,alpha=.5,label='Outward-facing bodies'),
                       Patch(facecolor=K,alpha=.3,label='Foam core'),Patch(facecolor=G,label='Pickup, stems / skins'),
                       Patch(facecolor=C,label='CO₂ in Ti tube')],loc='upper center',bbox_to_anchor=(.5,1.30),ncol=3,fontsize=6.8)
    fig.tight_layout();save(fig,'pixel-disc-section')

    fig,aa=plt.subplots(2,2,figsize=(6.1,6.0))
    for ax,face,title in zip(aa[0],[-1,1],['Disc 1: IP-facing modules','Disc 1: outward-facing modules']):
        plan(ax,first,face,active=False)
        for row in S['rings']:
            radius=sum(math.hypot(*m['center_mm'][:2]) for m in first['bodies'] if m['row']==row['row'])/row['modules']
            ax.add_patch(Circle((0,0),radius,fill=False,edgecolor=O,lw=.7,ls='--'))
        for deg in [0,120,240]:
            t=math.radians(deg);ax.plot([34*math.cos(t),190*math.cos(t)],
                                      [34*math.sin(t),190*math.sin(t)],color=O,lw=.7,ls='--')
        for deg in [90,210,330]:
            ax.add_patch(Wedge((0,0),234,deg-15,deg+15,width=44,facecolor=G,alpha=.2))
        ax.set_title(title,fontsize=8)
    for ax,disc in zip(aa[1],[first,S['discs'][-1]]):
        for k,track in enumerate(disc['cooling']['tracks']):
            r=track['radius_mm'];color=C if k%2==0 else B
            for a,b in [(8,172),(188,352)]:
                ax.add_patch(Arc((0,0),2*r,2*r,theta1=a,theta2=b,color=color,lw=1.05))
                for angle,marker,c in [(a,'o',K),(b,'s',V)]:
                    t=math.radians(angle);ax.plot(r*math.cos(t),r*math.sin(t),marker,ms=2,color=c)
            ax.plot([r,188.5],[0,0],color=color,lw=.5,ls=':')
        ax.add_patch(Circle((0,0),188.5,fill=False,edgecolor=G,lw=.5))
        ax.set(aspect='equal',xlim=(-205,205),ylim=(-205,205),xlabel='x [mm]',ylabel='y [mm]',
               title=f"Disc {disc['index']}: {disc['cooling']['number_circuits']} half-ring circuits")
    fig.tight_layout();save(fig,'pixel-endcap-routing')

    fig,aa=plt.subplots(2,1,figsize=(6.1,3.8));cells=S['transport_P']['cells']
    for ax,zlim in zip(aa,[(595,690),(3050,3320)]):
        for cell in cells:
            a,b=cell['abs_z_mm'];lo,hi=cell['radial_mm']
            if b<zlim[0] or a>zlim[1]:continue
            color=O if cell['name'].startswith('trunk') else V if cell['name'].startswith('collector') else C
            box(ax,a,lo,b-a,hi-lo,color,alpha=.3,edgecolor=color)
        for disc in S['discs']:
            if zlim[0]<disc['z_mm']<zlim[1]:ax.plot([disc['z_mm']]*2,[27,188.5],color=B,lw=2)
        for a,b in [(609,611),(3134,3136)]:
            if zlim[0]<a<zlim[1]:box(ax,a,222,b-a,10,G)
        ax.set(xlim=zlim,ylim=(0,700 if zlim[0]>1000 else 260),xlabel='z [mm]',ylabel='r [mm]');ax.grid(alpha=.12)
    aa[0].set_title('First-disc collector and barrel handoff: effective-cell bounds',fontsize=8)
    aa[1].set_title('Last-disc collector, inner bypass and rear turn: effective-cell bounds',fontsize=8)
    aa[0].text(641,165,'collector P1',fontsize=7,color=V);aa[0].text(655,213,'trunk',fontsize=7,color=O)
    aa[1].text(3200,530,'rear turn',fontsize=7,color=C);aa[1].text(3086,85,'P9 collector',fontsize=6,color=V)
    aa[1].annotate('bypass',xy=(3140,120),xytext=(3210,290),fontsize=7,arrowprops={'arrowstyle':'->','color':G})
    aa[1].annotate('rear flange neck',xy=(3135,225),xytext=(3058,590),fontsize=7,arrowprops={'arrowstyle':'->','color':G})
    fig.tight_layout();save(fig,'pixel-service-interfaces')

    disc_rows=[]
    for disc in S['discs']:
        singles=', '.join(str(i+1) for i in disc['retained_rows'] if i<4)
        disc_rows.append(f"{disc['index']} & {disc['z_mm']:.0f} & {singles} & {disc['families']['single']} & 50 & {disc['chips']} & {disc['cooling']['number_circuits']} " + r'\\')
    (root/'generated/pixel-disc-rows.tex').write_text('\n'.join(disc_rows)+'\n')
    ring_rows=[]
    for ring in S['rings']:
        chips=ring['modules']*(4 if ring['family']=='quad' else 1)
        ring_rows.append(f"{ring['row']+1} & {ring['family'].capitalize()} & {ring['radius_mm']:.3f} & {ring['modules']} & {chips} " + r'\\')
    (root/'generated/pixel-ring-rows.tex').write_text('\n'.join(ring_rows)+'\n')
