"""DES029 annotated repair sketch, using the actual ECAL for comparison.

Only the left panel is generated detector geometry. Proposed PCB border/gap,
edge reservation, inner clearance and service-bay height are named illustrative
sketch choices, not engineered or validated detector dimensions. Sensor size
and aperture/sector/outer envelope use the existing DES028/029 inputs.
"""
import argparse,json,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle,FancyBboxPatch
from assembly import inventory,wedge
from model import ROOT,sha

SKETCH=dict(pcb_border_mm=2,sensor_gap_mm=2,board_gap_mm=2,
            illustrative_edge_mm=5,inner_clearance_mm=30,outer_bay_mm=120)
COLOR=dict(absorber='#ead7b2',board='#cbd3dc',sensor='#31845c',bay='#7d66ad',
           coolant='#2183b3',power='#d08732',rib='#707986',blind='#b9423e')

def footprint(ax,x,y,w,h,color,edge='white',lw=.7,**kw):
    ax.add_patch(Rectangle((x,y),w,h,facecolor=color,edgecolor=edge,lw=lw,**kw))

def annotate(ax,text,xy,xytext,color='#303b46'):
    ax.annotate(text,xy=xy,xytext=xytext,fontsize=9.2,color=color,ha='center',va='center',
                bbox=dict(boxstyle='round,pad=.3',facecolor='white',edgecolor='none',alpha=.95),
                arrowprops=dict(arrowstyle='->',color=color,lw=1.2))

def draw(out):
    r,_=inventory();u=next(u for u in r['units'] if u['name']=='ecal');c=r['config']
    reg=next(g for g in r['regions'] if g['name']=='ecal_endcap');tan=math.tan(math.pi/c['sectors'])
    plate=next(p for p in reg['parts'] if p['role']=='absorber')
    fig=plt.figure(figsize=(14,9.6));a=fig.add_axes([.055,.17,.245,.67]);b=fig.add_axes([.34,.17,.245,.67]);d=fig.add_axes([.635,.18,.33,.65]);d.set(xlim=(0,1),ylim=(0,1));d.axis('off')
    for ax,title in ((a,'A  Current ECAL endcap'),(b,'B  Proposed carrier approach')):
        vertices=plate['vertices_mm'] if ax is a else wedge(c['endcap_inner_apothem_mm'],reg['outer_apothem_mm'],tan,c['seam_half_gap_mm']+SKETCH['illustrative_edge_mm'])
        ax.add_patch(Polygon([[y/1000,x/1000] for x,y in vertices],facecolor=COLOR['absorber'],edgecolor=COLOR['rib'],lw=1.8))
        ax.set(xlim=(-.55,.55),ylim=(.25,2.31),xlabel='tangent [m]',ylabel='radial [m]',title=title)
        ax.set_aspect('equal')
    for p in reg['placements']:
        if p['layer']!=0:continue
        x,y,_=p['center_mm'];w,h=u['width_mm'],u['height_mm']
        footprint(a,(y-w/2)/1000,(x-h/2)/1000,w/1000,h/1000,COLOR['board'],edge='#83909c')
        for s in u['parts']:
            if s['role']!='sensitive':continue
            sx,sy,_=s['center_mm'];sw,sh=s['dimensions_mm']['sx'],s['dimensions_mm']['sy']
            footprint(a,(y-sx-sw/2)/1000,(x+sy-sh/2)/1000,sw/1000,sh/1000,COLOR['sensor'],lw=.35)
    first=min(p['center_mm'][0]+s['center_mm'][1]-s['dimensions_mm']['sy']/2 for p in reg['placements'] if p['layer']==0 for s in u['parts'] if s['role']=='sensitive')
    a.axhline(first/1000,c=COLOR['blind'],ls='--',lw=1.3)
    annotate(a,'Large inner region\nwithout sensors',(.02,.57),(-.26,.76),COLOR['blind'])
    annotate(a,'Repeated service strip\ninside cassette footprint',(-.080,1.31),(-.32,1.11))
    a.text(.5,-.13,'31.9% sensitive plate area\nFirst sensitive radius: 0.909 m',transform=a.transAxes,ha='center',fontsize=10,color=COLOR['blind'])
    # An illustrative regular grid of intact90 mm sensors, grouped into full,
    # half and single boards. Every board is inside the sketched carrier, but
    # its mechanics/electronics/thermal interfaces have not been engineered.
    from model import build
    model,_=build();sensor_side=model['config']['ecal']['sensor_outer_mm'];active=model['config']['ecal']['sensor_active_mm']
    pitch=sensor_side+SKETCH['sensor_gap_mm'];single=sensor_side+2*SKETCH['pcb_border_mm']
    step=single+SKETCH['board_gap_mm'];low=c['endcap_inner_apothem_mm']+SKETCH['inner_clearance_mm'];high=reg['outer_apothem_mm']-SKETCH['outer_bay_mm']
    rows=[]
    for j in range(int((high-low+SKETCH['board_gap_mm'])//step)):
        front=low+j*step;span=2*(front*tan-c['seam_half_gap_mm']-SKETCH['illustrative_edge_mm']);n=int((span+SKETCH['board_gap_mm'])//step)
        rows.append(dict(front=front,n=n,used=False))
    groups=[]
    # Pair equal-width adjacent rows into2-high boards; leftovers become singles.
    j=0
    while j<len(rows):
        row=rows[j];ny=2 if j+1<len(rows) and rows[j+1]['n']==row['n'] else 1;n=row['n'];start=-(n*step-SKETCH['board_gap_mm'])/2;col=0
        while col<n:
            nx=2 if col+1<n else 1;x0=start+col*step;y0=row['front'];w=nx*sensor_side+(nx-1)*SKETCH['sensor_gap_mm']+2*SKETCH['pcb_border_mm'];h=ny*sensor_side+(ny-1)*SKETCH['sensor_gap_mm']+2*SKETCH['pcb_border_mm']
            footprint(b,x0/1000,y0/1000,w/1000,h/1000,COLOR['board'],edge='#8897a5',lw=.8)
            for ix in range(nx):
                for iy in range(ny):
                    sx=x0+SKETCH['pcb_border_mm']+ix*pitch+(sensor_side-active)/2;sy=y0+SKETCH['pcb_border_mm']+iy*pitch+(sensor_side-active)/2
                    footprint(b,sx/1000,sy/1000,active/1000,active/1000,COLOR['sensor'],lw=.35)
            groups.append(dict(sensors=[nx,ny],front_mm=y0,tangent_mm=x0,board_size_mm=[w,h]));col+=nx
        j+=ny
    for group in groups:
        for dx in (0,group['board_size_mm'][0]):
            for dy in (0,group['board_size_mm'][1]):
                x=group['tangent_mm']+dx;y=group['front_mm']+dy
                if abs(x)>y*tan-c['seam_half_gap_mm']-SKETCH['illustrative_edge_mm']+1e-7 or y>high+1e-7:raise ValueError('sketch board outside illustrative carrier/service boundary')
    # Shared peripheral service bay: kept explicit, with no active fill implied.
    top=reg['outer_apothem_mm'];start=high;inset=c['seam_half_gap_mm']+SKETCH['illustrative_edge_mm']
    bay=[[-start*tan+inset,start],[start*tan-inset,start],[top*tan-inset,top],[-top*tan+inset,top]]
    b.add_patch(Polygon([[x/1000,y/1000] for x,y in bay],facecolor=COLOR['bay'],edgecolor='white',lw=1))
    b.text(0,(start+top)/2000,'Shared service bay',ha='center',va='center',fontsize=8.5,color='white')
    # A supported inner rim is a symbol; its section/fasteners are not dimensioned.
    y0=c['endcap_inner_apothem_mm'];y1=low;b.add_patch(Polygon([[-y0*tan/1000,y0/1000],[y0*tan/1000,y0/1000],[y1*tan/1000,y1/1000],[-y1*tan/1000,y1/1000]],facecolor=COLOR['rib'],edgecolor='none',hatch='///',alpha=.7))
    annotate(b,'Small inner boards\nwith intact sensors',(.005,.395),(.29,.48))
    annotate(b,'Full / half / single\nboard families',(.07,1.51),(.32,1.33))
    b.text(.5,-.13,'Concept only: board grouping and service routing\nRibs, clearances and coverage still to qualify',transform=b.transAxes,ha='center',fontsize=9.4)
    d.text(0,1,'C  Hardware constraints and services',fontsize=12,weight='bold',va='top')
    # Actual tangential section at the baseline aperture.
    width=2*c['endcap_inner_apothem_mm']*tan;clear=width-2*c['edge_rail_mm']-2*c['seam_half_gap_mm'];scale=.78/width;left=.11;right=left+.78;bottom=.78;height=.09;rail=c['edge_rail_mm']*scale;seam_width=c['seam_half_gap_mm']*scale
    footprint(d,left,bottom,.78,height,'#f4f5f7',edge=COLOR['rib']);footprint(d,left+seam_width,bottom,rail,height,COLOR['rib']);footprint(d,right-rail-seam_width,bottom,rail,height,COLOR['rib'])
    footprint(d,(left+right)/2-sensor_side*scale/2,bottom+.005,sensor_side*scale,height-.01,'none',edge=COLOR['blind'],lw=1.5)
    d.annotate('',xy=(left,.92),xytext=(right,.92),arrowprops=dict(arrowstyle='<->',color='#344352'));d.text(.5,.94,f'Current 16-sector width at aperture: {width:.0f} mm',ha='center',fontsize=9)
    d.text(.5,.755,f'Two 20 mm rails + seam leave {clear:.0f} mm clear',ha='center',fontsize=9);d.text(.5,.717,'A 90 mm silicon sensor cannot fit this section.',ha='center',fontsize=9.3,color=COLOR['blind'])
    d.text(.5,.658,'Inner-ring and rib topology must change\nbefore adding small inner boards.',ha='center',fontsize=10,weight='bold')
    # Functional service architecture, deliberately not a fabricated section.
    d.text(0,.582,'Keep ASICs and heat paths behind the active face',fontsize=10,weight='bold')
    for x,label,color in ((.015,'Sensor / tile\nboards',COLOR['sensor']),(.35,'Local ASICs +\nheat spreader',COLOR['board']),(.71,'Shared edge\ninterfaces',COLOR['bay'])):
        d.add_patch(FancyBboxPatch((x,.43),.27,.105,boxstyle='round,pad=.007',facecolor=color,edgecolor='white'));d.text(x+.135,.482,label,ha='center',va='center',fontsize=9,color='white' if color in (COLOR['sensor'],COLOR['bay']) else '#27313d')
    for x0,x1 in ((.285,.35),(.62,.71)):d.annotate('',xy=(x1,.482),xytext=(x0,.482),arrowprops=dict(arrowstyle='->',color='#344352',lw=1.4))
    for y,label,color in ((.39,'Cooling supply / return',COLOR['coolant']),(.35,'Power and data collection',COLOR['power'])):
        d.plot([.08,.97],[y,y],c=color,lw=2);d.text(.52,y-.025,label,ha='center',fontsize=8.5,color=color)
    # Suggested HCAL family: this is a new-board design choice, not a HBU cut.
    d.text(0,.265,'HCAL: apply the same carrier approach',fontsize=10,weight='bold')
    for x0,nx,ny,label in ((.03,6,6,'6×6 tiles\n36 channels'),(.40,12,6,'6×12 tiles\n72 channels')):
        tile=.031;y0=.06
        footprint(d,x0-.009,y0-.009,nx*tile+.018,ny*tile+.018,COLOR['board'],edge='#83909c')
        for ix in range(nx):
            for iy in range(ny):footprint(d,x0+ix*tile,y0+iy*tile,tile*.94,tile*.94,COLOR['sensor'],lw=.2)
        d.text(x0+nx*tile/2,.025,label,ha='center',va='top',fontsize=9)
    fig.suptitle('Endcap coverage repair · current geometry and proposed hardware approach',fontsize=17,y=.965)
    fig.text(.5,.913,'Retain Si–W ECAL and steel/scintillator HCAL; change carrier, board families and service placement.',ha='center',fontsize=11)
    fig.text(.5,.052,'DRAFT concept drawing · proposed margins, ribs and service bays are illustrative; no new coverage or engineering qualification claimed.',ha='center',fontsize=10,color='#47515d')
    fig.text(.5,.025,'Green = sensitive material     Grey = PCB / support footprint     Beige = absorber without sensors     Purple = shared service region',ha='center',fontsize=9.6)
    out.mkdir(parents=True,exist_ok=True);plt.rcParams['svg.hashsalt']='DES029-repair-concept';fig.savefig(out/'endcap-repair-concept.png',dpi=180);fig.savefig(out/'endcap-repair-concept.svg',metadata={'Date':None});plt.close(fig)
    p=out/'endcap-repair-concept.svg';p.write_text('\n'.join(s.rstrip() for s in p.read_text().splitlines())+'\n')
    note=dict(status='DRAFT concept illustration; no detector geometry change',baseline_source_sha256=r['source_sha256'],drawing_source_sha256=sha(__file__),sketch_choices_mm=SKETCH,proposed_groups=groups,meaning='Only panelA is actual model geometry. PanelB includes new illustrative board/edge/service assumptions. PanelC separates the measured baseline fit constraint from proposed functional services and HCAL families.')
    (out/'endcap-repair-concept.json').write_text(json.dumps(note,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'docs/design/figures/DES-029');draw(p.parse_args().output)
