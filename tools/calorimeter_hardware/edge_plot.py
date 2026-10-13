"""Four requested ECAL coverage stages, eta contours and edge-mask details."""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Patch, Polygon

from edge_layout import ROOT, area, build, contains, regular

GREEN='#38866c';EDGE='#dc8a34';BOARD='#becbd3';DEAD='#efdfba';BLUE='#246baa'


def rotate(p,theta):
    co,si=math.cos(theta),math.sin(theta)
    return [[co*x-si*y,si*x+co*y] for x,y in p]


def global_polygon(m,key):return [[x+m['center_mm'][0],y+m['center_mm'][1]] for x,y in m[key]]


def baseline_masks(base):
    r=next(q for q in base['regions'] if q['name']=='ecal_endcap');u=next(q for q in base['units'] if q['name']=='ecal');masks=[];boards=[]
    for p in r['placements']:
        if p['layer']!=0:continue
        x,y,_=p['center_mm'];w,h=u['width_mm'],u['height_mm'];boards.append([[x-h/2,y-w/2],[x+h/2,y-w/2],[x+h/2,y+w/2],[x-h/2,y+w/2]])
        for s in u['parts']:
            if s['role']!='sensitive':continue
            sx,sy,_=s['center_mm'];sw,sh=s['dimensions_mm']['sx'],s['dimensions_mm']['sy'];X,Y=x+sy,y-sx;masks.append([[X-sh/2,Y-sw/2],[X+sh/2,Y-sw/2],[X+sh/2,Y+sw/2],[X-sh/2,Y+sw/2]])
    return masks,boards


def directional(report,layouts,base):
    masks,_=baseline_masks(base);result=[]
    for eta in (1.3,1.35,1.4,1.45,1.5,1.75,2.,2.25,2.5,2.75,3.,3.25,3.5,3.75,3.9,4.):
        counts={k:[] for k in ('odd','first','squares','edges')}
        for i in range(360):
            phi=(i+.5)*2*math.pi/360;theta=phi%(math.pi/2);delta=(phi+math.pi/16)%(math.pi/8)-math.pi/16
            for kind in counts:
                n=48;hits=0
                for layer in range(n):
                    z=(3200+2.4+5.05*layer) if kind=='odd' else report['front_mm']+2.5+report['layer_pitch_mm']*layer;r=z/math.sinh(eta)
                    if kind=='odd':
                        x,y=r*math.cos(delta),r*math.sin(delta);hit=315<=x<=1500*math.cos(math.pi/16) and abs(y)<=x*math.tan(math.pi/16)-2.5
                    elif kind=='first':
                        x,y=r*math.cos(delta),r*math.sin(delta);hit=any(contains(p,x,y) for p in masks)
                    else:hit=layouts[kind]['hit'](r*math.cos(theta),r*math.sin(theta))
                    hits+=hit
                counts[kind].append(hits)
        result.append(dict(eta=eta,phi_bins=360,layouts={k:dict(min_layers=min(v),max_layers=max(v),mean_layers=sum(v)/len(v),phi_fraction_at_least_one_layer=sum(x>0 for x in v)/len(v),phi_fraction_at_least_40_layers=sum(x>=40 for x in v)/len(v)) for k,v in counts.items()}))
    return result


def drawing():
    report,layouts,base=build();masks,boards=baseline_masks(base);out=ROOT/'docs/design/figures/DES-030';out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'svg.hashsalt':'DES030-four-stages','font.size':9})
    fig=plt.figure(figsize=(14,16));grid=fig.add_gridspec(4,6,height_ratios=[1,1,.55,.5],left=.07,right=.97,top=.89,bottom=.08,hspace=.42,wspace=.52);axes=[fig.add_subplot(grid[r,c:c+3]) for r in (0,1) for c in (0,3)]
    titles=['A  ODD: idealized continuous sheets','B  First nODD: rectangular cassettes','C  Optimized compact squares','D  Squares + custom edge sensors']
    captions=['98.59% of original ODD nominal face\nz = 3.20 m; aperture apothem 315 mm', '31.85% of original nODD absorber plate\nz = 3.95 m; aperture apothem 300 mm', f"{100*report['summary']['squares']['active_face_fraction']:.2f}% of new nominal face\nz = 3.95 m; aperture square apothem 90 mm", f"{100*report['summary']['edges']['active_face_fraction']:.2f}% of the same new nominal face\n39 edge sensors / quadrant / layer"]
    for j,ax in enumerate(axes):
        ax.set_title(titles[j]+'\n'+captions[j],loc='left',fontsize=10.5,weight='bold');ax.set(xlim=(-2.34,2.34),ylim=(-2.34,2.34),xlabel='x [m]',ylabel='y [m]');ax.set_aspect('equal');ax.spines[['top','right']].set_visible(False)
        if j==0:
            ri,ro,g=315,1500*math.cos(math.pi/16),2.5;t=math.tan(math.pi/16)
            for k in range(16):
                p=[[ri,-ri*t+g],[ro,-ro*t+g],[ro,ro*t-g],[ri,ri*t-g]];p=rotate(p,k*math.pi/8);ax.add_patch(Polygon([[x/1000,y/1000] for x,y in p],facecolor=GREEN,edgecolor='white',lw=.3))
        elif j==1:
            region=next(q for q in base['regions'] if q['name']=='ecal_endcap');plate=next(q['vertices_mm'] for q in region['parts'] if q['role']=='absorber')
            for k in range(16):
                for p in (plate,):ax.add_patch(Polygon([[x/1000,y/1000] for x,y in rotate(p,k*math.pi/8)],facecolor=DEAD,edgecolor='#74716a',lw=.3))
                for p in boards:ax.add_patch(Polygon([[x/1000,y/1000] for x,y in rotate(p,k*math.pi/8)],facecolor=BOARD,edgecolor='#7f929d',lw=.2))
                for p in masks:ax.add_patch(Polygon([[x/1000,y/1000] for x,y in rotate(p,k*math.pi/8)],facecolor=GREEN,edgecolor='white',lw=.15))
        else:
            ax.add_patch(Polygon([[x/1000,y/1000] for x,y in report['outer_polygon_mm']],facecolor=DEAD,edgecolor='#74716a',lw=.7));hole=report['config']['inner_square_apothem_mm']/1000;ax.add_patch(Polygon([[-hole,-hole],[hole,-hole],[hole,hole],[-hole,hole]],facecolor='white',edgecolor='#74716a',lw=.5))
            for k in range(4):
                for m in layouts['squares' if j==2 else 'edges']['modules']:
                    for key,color in (('board',BOARD),('sensor','#e4e6e6'),('active',GREEN if m['full'] else EDGE)):
                        ax.add_patch(Polygon([[x/1000,y/1000] for x,y in rotate(global_polygon(m,key),k*math.pi/2)],facecolor=color,edgecolor='#76868b' if key=='board' else 'none',lw=.2))
        front=3200 if j==0 else report['front_mm']
        for eta,style in ((2,':'),(3,'--'),(4,'-')):
            radius=front/math.sinh(eta)/1000;ax.add_patch(Circle((0,0),radius,fill=False,edgecolor=BLUE,linestyle=style,lw=.9));angle=.4 if eta!=4 else -.45;ax.text(radius*math.cos(angle),radius*math.sin(angle),f' η={eta}',fontsize=8,color=BLUE,bbox=dict(facecolor='white',alpha=.85,edgecolor='none',pad=.5))
        if j<2:ax.text(.5,.035,'η = 4 is inside the historical aperture',transform=ax.transAxes,ha='center',fontsize=9,color='#a44737',bbox=dict(facecolor='white',alpha=.9,edgecolor='none'))
        else:ax.text(.5,.035,'Same aperture, supports, services and square grid in C/D',transform=ax.transAxes,ha='center',fontsize=8.5,bbox=dict(facecolor='white',alpha=.9,edgecolor='none'))
    for col,family in enumerate(('trapezoid','chamfered','triangle')):
        ax=fig.add_subplot(grid[2,2*col:2*col+2]);p=max((q for q in report['edge_profiles'] if q['family']==family),key=lambda q:area(q['sensor_mm']))
        ax.add_patch(Polygon(p['board_mm'],facecolor=BOARD,edgecolor='#63737d'));ax.add_patch(Polygon(p['sensor_mm'],facecolor='#b68145',edgecolor='#63737d'));ax.add_patch(Polygon(p['active_mm'],facecolor=EDGE,edgecolor='#63737d'))
        from edge_layout import pad_mask
        for pad in pad_mask(p['active_mm'],5.5,report['config']['minimum_pad_fraction']*5.5**2):
            # Remove shared internal boundaries of merged electrodes.
            from collections import Counter
            segments=Counter()
            for polygon in pad['polygons']:
                for u,v in zip(polygon,polygon[1:]+polygon[:1]):
                    segments[tuple(sorted((tuple(round(x,6) for x in u),tuple(round(x,6) for x in v))))]+=1
            for (u,v),count in segments.items():
                if count==1:ax.plot([u[0],v[0]],[u[1],v[1]],color='white',lw=.25)
        label=family
        v=p['sensor_mm']
        if len(v)==4 and all(abs((b[0]-a[0])*(c[0]-b[0])+(b[1]-a[1])*(c[1]-b[1]))<1e-6 for a,b,c in zip(v,v[1:]+v[:1],v[2:]+v[:2])):label='rectangular edge'
        ax.set(xlim=(-48,48),ylim=(-48,48),xlabel='sensor-local x [mm]',ylabel='y [mm]');ax.set_aspect('equal');ax.set_title(f"{p['id']} · {label}\n{p['pad_channels']} channels · {p['asic_packages']} ASICs",fontsize=10)
    ax=fig.add_subplot(grid[3,:]);ax.axis('off');delta=100*(report['summary']['edges']['active_face_fraction']-report['summary']['squares']['active_face_fraction'])
    ax.text(.015,1,f'Custom masks: 22 distinct oriented profiles; 39 placements/quadrant/layer;\n+{delta:.2f} percentage points of sensitive face.',va='top',fontsize=10.5,weight='bold')
    ax.text(0,.77,'New sensors: ≤90×90 mm blanks, 0.5 mm Si, explicit 2 mm passive edge guard, shaped PCB and custom boundary electrodes.',va='top',fontsize=10)
    ax.text(0,.54,'|η| = 4 target: r = 144.74 mm at z = 3.95 m. New supported aperture corner: 134.35 mm. Narrow seams/pad guards remain.',va='top',fontsize=10)
    ax.text(0,.31,'DRAFT / PROTOTYPE · A uses the smaller original ODD envelope; B preserves original nODD geometry and denominator.\nC/D use the same new full-face denominator including support/service losses. Percentages are geometry, not particle efficiency.\nCustom masks, machine aperture, cooling/manifolds, mechanics and sensor response require engineering qualification.',va='top',fontsize=9.5,color='#4d565c')
    fig.suptitle('ECAL endcap packing: from idealized sheets to custom physical edge sensors\nAll endcap views use the same physical x/y scale; blue circles show η at each front plane.',fontsize=15,y=.985)
    fig.legend(handles=[Patch(facecolor=GREEN,label='Square/continuous sensitive material'),Patch(facecolor=EDGE,label='Custom edge sensitive material'),Patch(facecolor=BOARD,label='PCB/cassette footprint'),Patch(facecolor=DEAD,label='Passive or uncovered face')],loc='lower center',bbox_to_anchor=(.5,.015),ncol=4,frameon=False,fontsize=9)
    fig.savefig(out/'four-stage-coverage.svg',metadata={'Date':None});fig.savefig(out/'four-stage-coverage.png',dpi=170);plt.close(fig)
    p=out/'four-stage-coverage.svg';p.write_text('\n'.join(q.rstrip() for q in p.read_text().splitlines())+'\n')
    profiles=ROOT/'docs/design/inputs/DES-030-edge-profiles.json';profiles.parent.mkdir(parents=True,exist_ok=True);profiles.write_text(json.dumps(report,indent=2)+'\n')
    result=directional(report,layouts,base);data=ROOT/'docs/validation/DES-030/directional-coverage.json';data.parent.mkdir(parents=True,exist_ok=True);data.write_text(json.dumps(dict(status='DRAFT geometrical straight-ray samples, not efficiency; repeated masks, no seam staggering',phi_sampling='360 half-degree-centred azimuth bins per eta; both ends are symmetric',source_sha256=report['source_sha256'],samples=result),indent=2)+'\n');print('SVG/PNG and profiles written; directional eta4:',result[-1])


if __name__=='__main__':drawing()
