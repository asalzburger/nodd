"""Original, dimensioned design-study drawings; no copied literature artwork."""
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle, Wedge
from matplotlib.backends.backend_pdf import PdfPages
from model import polygon, dimensions

COLORS={'plate':'#d6dadd','IP':'#168b86','rear':'#3474b5','foot':'#a84d88','tube':'#357ebd','flex':'#d18b18','mount':'#784f32'}


def render(out,cfg,report,bodies,tiles,feet):
    plt.rcParams.update({'font.size':10,'axes.titlesize':12,'svg.fonttype':'none','svg.hashsalt':'DES014'})
    pages=[]
    def page(name,title):
        fig=plt.figure(figsize=(16.54,11.69),layout='constrained')
        fig.suptitle('nODD   /   DES-014   /   '+title,fontsize=19,fontweight='bold')
        fig.supxlabel('DRAFT PROTOTYPE • proposal B, NOT an adopted layout • dimensions in mm • 2026-10-01',fontsize=10)
        pages.append((name,fig));return fig
    def disc_axes(ax,title):
        ax.set_aspect('equal');ax.set_xlim(-245,245);ax.set_ylim(-245,245)
        ax.set_xlabel('x [mm]');ax.set_ylabel('y [mm]');ax.set_title(title)
        ax.add_patch(Wedge((0,0),cfg['plate']['r_max_mm'],0,360,width=cfg['plate']['r_max_mm']-cfg['plate']['r_min_mm'],facecolor=COLORS['plate'],alpha=.65))
        ax.add_patch(Circle((0,0),25,fill=False,edgecolor='#777',linestyle='--'))
        for angle in cfg['mounting']['angles_deg']:
            a=math.radians(angle);r=np.array([math.cos(a),math.sin(a)]);u=np.array([-math.sin(a),math.cos(a)])
            corners=[rr*r+ss*cfg['mounting']['tab_width_mm']/2*u for rr,ss in [(186,-1),(228,-1),(228,1),(186,1)]]
            ax.add_patch(Polygon(corners,facecolor=COLORS['mount'],alpha=.8))
            ax.plot(*(228*r),'o',color=COLORS['mount'])
        ax.add_patch(Circle((0,0),cfg['mounting']['shell_outer_r_mm'],fill=False,ec='#444',lw=1.4))
        ax.grid(alpha=.14)
    fig=page('disc-xy','Common disc: module faces and mounting points')
    axes=fig.subplots(1,2)
    for ax,side,title in zip(axes,[-1,1],['IP-facing rows 1, 3, 5 — view along +w','Outward-facing rows 2, 4 — same x/y projection']):
        disc_axes(ax,title)
        for b in bodies:
            color=COLORS['IP'] if b['mount_face']==-1 else COLORS['rear']
            ax.add_patch(Polygon(polygon(b),fc=color if b['mount_face']==side else 'none',ec=color,
                                 alpha=.48 if b['mount_face']==side else .13,lw=.7))
            if b['mount_face']==side:
                ax.text(*b['center_mm'][:2],str(round(b['foot_height_mm']/1.65)),ha='center',va='center',fontsize=6)
        for b in feet:
            if b['mount_face']==side:ax.add_patch(Polygon(polygon(b),fc=COLORS['foot'],ec='white',lw=.3))
        ax.text(0,-225,'R27..188.5 plate; 112 quads total\n0/1/2 = 0/1.65/3.30 mm foot height',ha='center',va='center',bbox=dict(fc='white',ec='none',alpha=.9))
    axes[1].annotate('Common three-point coupling\n90° / 210° / 330°',xy=(0,228),xytext=(55,225),arrowprops=dict(arrowstyle='->'),fontsize=10)
    fig=page('sections','Local support sections and staggering')
    ax,bx=fig.subplots(2,1,gridspec_kw={'height_ratios':[1.1,1]})
    half=dimensions(cfg)[0]/2
    ax.add_patch(Rectangle((27,-half),161.5,2*half,fc=COLORS['plate'],ec='#555'))
    ax.plot([27,188.5],[-half,-half],c='#333',lw=2);ax.plot([27,188.5],[half,half],c='#333',lw=2)
    for b,t in zip(bodies,tiles):
        poly=polygon(b);xs=[]
        for a,c in zip(poly,poly[1:]+poly[:1]):
            if (a[1]<=0<=c[1] or c[1]<=0<=a[1]) and abs(c[1]-a[1])>1e-12:
                x=a[0]+(c[0]-a[0])*(-a[1])/(c[1]-a[1]);xs.append(x)
        if len(xs)>=2 and max(xs)>0:
            for item,color in [(b,COLORS['IP'] if b['mount_face']<0 else COLORS['rear']),(t,COLORS['foot'])]:
                ax.add_patch(Rectangle((min(xs),item['center_mm'][2]-item['half_w_mm']),max(xs)-min(xs),2*item['half_w_mm'],fc=color,ec='white',lw=.4))
    for row in report['geometry']['rows']:
        ax.add_patch(Circle((row['cooling_radius_mm'],-1.5),1.4,fc='white',ec=COLORS['tube'],lw=2))
    ax.set(xlim=(20,194),ylim=(-10,11),xlabel='r [mm]',ylabel='w, outward from IP [mm]',title='Actual r–w section at phi = 0°; w scale enlarged for visibility')
    ax.text(30,8,'0.15 CFRP / 6.00 foam core / 0.15 CFRP\nTube-routing planes w = ±1.5; OD 2.8, Ti wall 0.15',fontsize=11)
    ax.grid(alpha=.2)
    for i,h in enumerate([0,1.65,3.30]):
        x=28+58*i
        bx.add_patch(Rectangle((x-25,-half),50,2*half,fc=COLORS['plate'],ec='#555'))
        # Draw one face flipped upward for legibility; same section is mirrored on IP side.
        bx.add_patch(Rectangle((x-22.1,half+h),44.2,.45,fc=COLORS['foot']))
        bx.add_patch(Rectangle((x-22.1,half+h+.45),44.2,1,fc=COLORS['IP']))
        if h:bx.add_patch(Rectangle((x+12,half),8,h,fc=COLORS['foot'],ec='#333'))
        bx.add_patch(Rectangle((x+12,-1.5),8,half+1.5,fc=COLORS['foot'],alpha=.65))
        bx.add_patch(Circle((x+16,-1.5),1.4,fc='white',ec=COLORS['tube'],lw=2))
        bx.annotate(f'{h:.2f} mm foot',xy=(x+16,half+h/2),xytext=(x+3,10.2),arrowprops=dict(arrowstyle='->'),ha='center')
        bx.text(x,-5,'Local radial section',ha='center',fontsize=9)
    bx.text(6,-8.6,'Separate module sections, not neighbouring modules in one plane.\nPickup: 0.30 graphite + 0.075 CFRP cradle + 0.025 isolation + 0.025 TIM + 0.025 bond = 0.45 mm.\n18×8 foot envelope; 16×8 graphite insert + side-flex space. Grain along heat path; contact windows through skins.',fontsize=10)
    bx.set(xlim=(0,174),ylim=(-10,12),xlabel='Separate illustrative local-r sections [mm]',ylabel='Local w [mm]',title='Reusable foot heights and a direct graphite-to-tube thermal path (schematic)')
    bx.grid(alpha=.15)
    fig=page('routing','Cooling and cable hand-off concept')
    ax,bx=fig.subplots(1,2,gridspec_kw={'width_ratios':[1.05,1]})
    disc_axes(ax,'Ten half-ring evaporators; radial exits to the outer rim')
    for row in report['geometry']['rows']:
        r=row['cooling_radius_mm'];color=plt.cm.viridis(.1+.18*row['row'])
        for lo,hi in [(3,177),(183,357)]:
            a=np.linspace(math.radians(lo),math.radians(hi),180)
            ax.plot(r*np.cos(a),r*np.sin(a),color=color,lw=2)
        for sign in [-1,1]:
            # Conceptual radial fan, on second routing plane. No bend-solid claim.
            angle=math.radians(2.5+2.5*row['row'])
            for shift in [-1,1]:
                ax.plot([sign*r,sign*212*math.cos(angle)], [shift*3,shift*212*math.sin(angle)],'--',c=color,lw=1)
    for angle in [60,180,300]:
        a=math.radians(angle);ax.annotate('',xy=(222*math.cos(a),222*math.sin(a)),xytext=(165*math.cos(a),165*math.sin(a)),arrowprops=dict(arrowstyle='->',lw=3,color=COLORS['flex']))
    ax.text(0,-219,'Solid: evaporator arcs; dashed: unqualified transitions/fans\nOrange: cable collection directions (on both disc faces)',ha='center',fontsize=9,bbox=dict(fc='white',ec='none',alpha=.95))
    bx.add_patch(Rectangle((190,-12),44,90,fc='#e5eef4'))
    bx.add_patch(Rectangle((27,11.7),207,50,fc='#f9eed4',alpha=.7))
    bx.add_patch(Rectangle((27,-half),161.5,2*half,fc=COLORS['plate'],ec='#333'))
    for a in [(-7.9,-3.6,27,161),(3.6,6.25,55,105)]:
        lo,hi,r,width=a;bx.add_patch(Rectangle((r,lo),width,hi-lo,fc=COLORS['IP'] if lo<0 else COLORS['rear'],alpha=.5))
    # Cable stays on own face then wraps outside active radius.
    for z in [-half,half]:bx.plot([50,188.5,195,195,212],[z,z,8,24,24],color=COLORS['flex'],lw=2,ls='--')
    bx.plot([65,188.5,202,202,218],[-1.5,1.5,10,40,40],c=COLORS['tube'],ls='--',lw=2)
    bx.plot([212,212],[24,77],c=COLORS['flex'],lw=2,ls='--');bx.plot([218,218],[40,77],c=COLORS['tube'],ls='--',lw=2)
    bx.text(35,51,'Existing 50 mm collector bay\nCable and cooling levels are concepts;\nminimum bends and weld access not verified.',fontsize=10)
    bx.text(196,70,'r190..234\naxial trunk',fontsize=10)
    bx.text(32,-20,'w=0: proposed disc datum. First disc/collector: +3.5 mm.\nLast disc uses existing inner bypass + an adapter.\nLocal flex is configurable, not a completed electrical layout.',fontsize=10)
    bx.set(xlim=(20,246),ylim=(-25,82),xlabel='r [mm]',ylabel='w, outward from disc [mm]',title='Disc → collector → axial services: envelope concept')
    bx.grid(alpha=.15)
    fig=page('carrier','Carrier, rails and installation datum')
    ax,bx=fig.subplots(2,1,gridspec_kw={'height_ratios':[1.25,1]})
    z0,z1=cfg['mounting']['carrier_z_mm']
    ax.add_patch(Rectangle((z0,cfg['mounting']['shell_outer_r_mm']-cfg['mounting']['shell_mm']),z1-z0,cfg['mounting']['shell_mm'],fc='#444'))
    ax.add_patch(Rectangle((z0,cfg['mounting']['rail_inner_r_mm']),z1-z0,cfg['mounting']['rail_depth_mm'],fc=COLORS['mount'],alpha=.7))
    ax.add_patch(Rectangle((555,190),2745,44,fc='#e5eef4',alpha=.3))
    for d in report['geometry']['discs']:
        if d['side']<0:continue
        z=d['proposed_z_mm'];ax.add_patch(Rectangle((z-half,27),2*half,161.5,fc='#626b72'))
        ax.add_patch(Rectangle((z-half,188.5),2*half,39.5,fc=COLORS['mount']))
        ax.plot([d['body_abs_z_min_mm'],d['body_abs_z_max_mm']],[165,165],c=COLORS['IP'],lw=4)
        ax.text(z,14,d['layer'].replace('A-pixel-',''),ha='center',fontsize=10)
    for z in [z0,z1]:ax.plot([z,z],[cfg['mounting']['shell_outer_r_mm']-cfg['mounting']['flange_radial_mm'],cfg['mounting']['shell_outer_r_mm']],c='#222',lw=4)
    ax.annotate('Axial datum at front interface',xy=(z0,231),xytext=(z0+170,268),arrowprops=dict(arrowstyle='->'))
    ax.annotate('Opposite end allows axial motion',xy=(z1,231),xytext=(z1-850,268),arrowprops=dict(arrowstyle='->'))
    ax.set(xlim=(530,3330),ylim=(0,290),xlabel='|z| [mm]',ylabel='r [mm]',title='Nine common discs per end; negative end mirrors outward coordinate w')
    ax.grid(alpha=.2)
    bx.axis('off')
    text=(
        'LOAD PATH\nModule cradle → broad thermal foot → sandwich disc → three tongues → rails → closed shell → end flanges\n\n'
        'REPEATABLE MOUNT\nThree preloaded stations: cone (3 constraints), slot (2), plane (1).\nCommon rail stations at 90°, 210°, 330°. Avoid a second rigid datum; add compliant preload/release access.\n\n'
        'DIMENSIONAL PROPOSAL\nRails: 8×8 mm CFRP boxes, 0.4 mm walls, r223.7..231.7 mm.\nShell: r231.7..232.0 mm, |z|609..3136 mm. Tube closes the global load path.\nThree 10 mm-wide sandwich tongues/disc connect r186..228 mm.\nWhole-cassette axial insertion is assumed; independent extraction around the installed beam pipe is NOT established.\n\n'
        'REVIEW BEFORE CONSTRUCTION\nCone/slot/plane inserts, spring forces, fasteners, thermal travel, shell seam, flange/frame interface,\naccess and swept installation envelope need detailed design. Beam estimates do not qualify these joints.')
    bx.text(.04,.97,text,va='top',fontsize=12,linespacing=1.5)
    fig=page('diagnostics','Thermal and material screening — limits retained')
    ax,bx=fig.subplots(1,2)
    v=[v for v in report['thermal']['variants'] if v['htc_W_m2_K']==20000 and v['periphery_fraction']>0]
    ax.plot([x['k_inplane_W_m_K'] for x in v],[x['nominal_C'] for x in v],'-o',label='Nominal power')
    ax.plot([x['k_inplane_W_m_K'] for x in v],[x['stress_C'] for x in v],'-s',label='1.5× power')
    ax.axhline(-15,c='red',ls='--',label='−15 °C screening target')
    ax.set(xlabel='Assumed in-plane graphite k [W/(m K)]',ylabel='Hottest pickup temperature proxy [°C]',title='−40 °C CO₂; edge-biased heat; unmeasured h = 20 kW/(m² K)')
    ax.legend();ax.grid(alpha=.2)
    comp=[a for a in report['materials_mechanics']['components'] if a['scope']=='disc']
    names=['Faces','Foam','Feet + inserts','Pickup graphite','Cradles','Isolation','TIM + bonds','Internal glue','Ti tubes','Liquid CO₂','Closeouts','Clips allowance','Hardware allowance','Flex polymer','Flex Cu']
    bx.barh(names,[a['mass_g'] for a in comp],color='#488d9a');bx.invert_yaxis()
    bx.set(xlabel='Modelled mass [g/disc]',title='Local passive inventory; liquid fill is a mass bound')
    bx.grid(axis='x',alpha=.2)
    with PdfPages(out/'drawings.pdf',metadata={'Title':'nODD DES014 pixel endcap support proposal','Author':'nODD project','CreationDate':None,'ModDate':None}) as pdf:
        for name,fig in pages:
            pdf.savefig(fig)
            fig.savefig(out/(name+'.svg'),metadata={'Date':None})
            svg=out/(name+'.svg')
            svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
            fig.savefig(out/(name+'.png'),dpi=110)
            plt.close(fig)
