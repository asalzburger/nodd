#!/usr/bin/env python3
"""Retain DES017 evidence and original, dimensioned proposal drawings."""
import argparse
import copy
import importlib.util
import json
import math
from pathlib import Path
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle
from matplotlib.colors import ListedColormap
import numpy as np

SPEC=importlib.util.spec_from_file_location('variant_model',Path(__file__).with_name('study.py'))
m=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(m)
NAMES=['eight-single','four-single-two-quad']
LABELS=['Eight single rings','Four single + two quad rings']
BLUE='#247ba0';AMBER='#b76516';GREEN='#2f9560';RED='#ba3943'


def save(fig,out,name):
    fig.savefig(out/(name+'.png'),dpi=170)
    fig.savefig(out/(name+'.svg'))
    p=out/(name+'.svg');p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')
    plt.close(fig)


def layouts(run,out,cfg):
    own,_,limits,_=m.inputs()
    control=json.loads((m.ROOT/own['control_layout']).read_text())['modules']
    panels=[control]+[json.loads((run/(n+'-layout.json')).read_text())['modules'] for n in NAMES]
    fig,axes=plt.subplots(1,3,figsize=(16,6),layout='constrained')
    titles=['PR41 frozen control: 296 single modules']+[f'{LABELS[i]}: {len(panels[i+1])} modules' for i in range(2)]
    for ax,modules,title in zip(axes,panels,titles):
        for body in modules:
            p=m.radial.body_polygon(body,cfg)
            ax.add_patch(Polygon(np.asarray(p.exterior.coords),fill=False,edgecolor='#80909b',linewidth=.25))
        for p,body in zip(m.radial.project(modules,cfg,cfg['disc_datum_mm']),m.radial.active_patches(modules,cfg)):
            color=BLUE if body.get('mount_face',1)<0 else AMBER
            ax.add_patch(Polygon(np.asarray(p.exterior.coords),facecolor=color,edgecolor=color,linewidth=.25,alpha=.42))
        for radius in cfg['annulus_mm']:ax.add_patch(Circle((0,0),radius,fill=False,edgecolor=RED,linestyle='--',linewidth=1.))
        ax.add_patch(Circle((0,0),limits['plate_outer_mm'],fill=False,edgecolor='#6f681a',linewidth=1))
        ax.set(xlim=(-205,205),ylim=(-205,205),aspect='equal',xlabel='x [mm]',ylabel='y [mm]',title=title)
        ax.grid(alpha=.12)
    fig.suptitle('DES017 prototype: polar chip axes, explicit inactive quad seams, unchanged service radii\nBlue: IP face; amber: outer face; red dashed: original active target; olive: r188.5 mm plate',fontsize=12)
    save(fig,out,'layout-comparison')


def coverage_map(run,out,cfg):
    from shapely.ops import unary_union
    import shapely
    radii=np.linspace(cfg['annulus_mm'][0],cfg['annulus_mm'][1],600)
    phi=np.linspace(0,2*math.pi,1200,endpoint=False)
    pp,rr=np.meshgrid(phi,radii)
    fig,axes=plt.subplots(2,1,figsize=(13,7),layout='constrained')
    for ax,name,label in zip(axes,NAMES,LABELS):
        modules=json.loads((run/(name+'-layout.json')).read_text())['modules']
        union=unary_union(m.radial.project(modules,cfg,cfg['disc_datum_mm'],vertex=0.))
        covered=shapely.contains_xy(union,rr*np.cos(pp),rr*np.sin(pp))
        ax.pcolormesh(np.degrees(phi),radii,covered,cmap=ListedColormap(['#ce4d53','#dbeef4']),vmin=0,vmax=1,shading='auto',rasterized=True)
        for radius in [110.,140.,181.]:ax.axhline(radius,linewidth=.5,color='#333',linestyle=':')
        ax.set(xlim=(0,360),xlabel='phi [degrees]',ylabel='Radius [mm]',title=label)
    fig.suptitle('Straight rays from z=0 to first disc: red shows uncovered active regions\n600×1200 diagnostic raster; exact polygon area screens and native controls govern the results',fontsize=12)
    save(fig,out,'coverage-map')


def support_drawings(out,cfg,own):
    fig,axes=plt.subplots(1,3,figsize=(16,6),layout='constrained')
    for ax,family,title in zip(axes[:2],['single','quad'],['Single module: one 6×8 mm thermal stem','Quad module: four 6×8 mm thermal stems']):
        f=cfg['families'][family];u,v=f['body_mm'];offset=f['periphery_offset_mm']
        ax.add_patch(Rectangle((-u/2,-v/2+offset),u,v,fill=False,edgecolor='#363c45',linewidth=1.5,label=f'Occupied body {u:g}×{v:g}'))
        host=dict(family=family,module_id=200000,sensor_id=200000,center_mm=[0.,0.,4.1],local_z_mm=4.1,mount_face=1,row=0,col=0,u=[1.,0.,0.],v=[0.,1.,0.])
        for p in m.radial.active_patches([host],cfg):
            ax.add_patch(Rectangle((p['center_mm'][0]-10,p['center_mm'][1]-9.6),20,19.2,facecolor=BLUE,alpha=.2,edgecolor=BLUE,label='20×19.2 mm active island'))
        for s in m.stem_shapes([host],cfg,own):
            ax.add_patch(Polygon(np.asarray(s['polygon'].exterior.coords),facecolor=GREEN,alpha=.65,edgecolor=GREEN,label='Graphite contact/window'))
        if family=='quad':
            ax.annotate('0.2 mm inactive cross\nFour chips share one sensor',(0,0),xytext=(0,-30),ha='center',fontsize=9,arrowprops=dict(arrowstyle='->',color='#555'))
            ax.text(0,29,'Stem centres u=±10.1, v=±8.7 mm\nChip centres u=±10.1, v=±9.7 mm',ha='center',fontsize=9)
        else:ax.text(0,16,'Periphery/body offset +0.9 mm\nStem centred on active matrix',ha='center',fontsize=9)
        ax.set(xlim=(-30,30),ylim=(-36,36),aspect='equal',xlabel='Tangential u [mm]',ylabel='Radial v [mm]',title=title)
        ax.grid(alpha=.12)
    ax=axes[2]
    for x,face,label in [(-16,1,'Outer face'),(16,-1,'IP face')]:
        centre=face*5.75
        ax.add_patch(Rectangle((x-7,centre-.5),14,1,facecolor=BLUE,alpha=.6))
        pickup_y=centre-.5-.45 if face==1 else centre+.5
        ax.add_patch(Rectangle((x-7,pickup_y),14,.45,facecolor=GREEN))
        stemtop=face*(5.75-.95)
        low,high=sorted([face*3.15,stemtop])
        ax.add_patch(Rectangle((x-3,low),6,high-low,facecolor=GREEN,alpha=.7))
        low,high=sorted([1.5,face*3.15])
        ax.add_patch(Rectangle((x-3,low),6,high-low,facecolor=GREEN,alpha=.35))
        ax.text(x,face*8,label,ha='center',va='center',fontsize=9)
    ax.add_patch(Rectangle((-30,-3),60,6,facecolor='#e9e1c8',alpha=.55,zorder=0))
    for y in [-3.15,3.]:ax.add_patch(Rectangle((-30,y),60,.15,facecolor='#434f59'))
    for x,y in [(-16,1.5),(16,1.5)]:
        ax.add_patch(Circle((x,y),1.4,facecolor='#979da6',edgecolor='#555'))
        ax.add_patch(Circle((x,y),1.25,facecolor='#ccebf1'))
    ax.text(0,0,'6 mm foam\n0.15 mm skins',ha='center',fontsize=9)
    ax.text(0,10.5,'0.45 mm pickup + 1 mm body\n1.65 mm level spacing gives 0.20 mm gap',ha='center',fontsize=9)
    ax.text(0,-10.5,'Evaporators at w=+1.5; radial legs at w=−1.5\nTi OD2.8 / wall0.15; crossing clearance0.20 mm',ha='center',fontsize=9)
    ax.set(xlim=(-32,32),ylim=(-12,12),xlabel='Local transverse coordinate [mm]',ylabel='Plate-normal w [mm]',title='Section: two faces and thermal windows')
    fig.suptitle('Dimensioned local thermal/support proposal — not manufacturing CAD\nTIM and insulation retained; skin/cradle windows bypass poor transverse CFRP conduction',fontsize=12)
    save(fig,out,'local-support')


def mounting_drawings(out,report):
    fig,axes=plt.subplots(1,2,figsize=(13,6),layout='constrained')
    ax=axes[0]
    for radius,color,width in [(27,RED,1),(188.5,'#414b55',1.5),(190,'#8a3976',1),(192,'#8a3976',1),(222,'#8a3976',1),(231.7,'#333',1),(232,'#333',1)]:
        ax.add_patch(Circle((0,0),radius,fill=False,edgecolor=color,linewidth=width))
    for angle,label in zip([90,210,330],['Cone: 3 constraints','V-slot: 2 constraints','Plane: 1 constraint']):
        a=math.radians(angle);u=np.array([-math.sin(a),math.cos(a)]);v=np.array([math.cos(a),math.sin(a)])
        corners=[r*v+q*u for r,q in [(186,-5),(228,-5),(228,5),(186,5)]]
        ax.add_patch(Polygon(corners,facecolor='#a3ad89',edgecolor='#4a5437'))
        c=228*v
        ax.scatter(*c,s=35,color='#333');ax.text(*(245*v),label,ha='center',va='center',fontsize=8)
    for index,track in enumerate(report['variants'][NAMES[1]]['cooling']['tracks']):
        ax.add_patch(Circle((0,0),track['radius_mm'],fill=False,edgecolor=BLUE,linewidth=.8,linestyle='--'))
    ax.text(0,0,'Eight cooling tracks\n16 half-ring circuits\n32 feed/return legs',ha='center',va='center',fontsize=10)
    ax.set(xlim=(-285,285),ylim=(-280,285),aspect='equal',title='Common disc mounting and evaporator tracks',xlabel='x [mm]',ylabel='y [mm]');ax.grid(alpha=.1)
    ax=axes[1]
    ax.add_patch(Rectangle((0,0),43.2,44.2,fill=False,linewidth=1.5))
    for c in [(10,10),(33,10),(21.6,34)]:ax.scatter(*c,marker='^',s=80,color=GREEN)
    ax.scatter(7,5,s=70,facecolor='#555');ax.text(7,-2,'Round datum',ha='center',fontsize=9)
    ax.add_patch(Rectangle((34,3),3,4,fill=False,edgecolor='#555'));ax.text(35.5,-2,'Radial slot\n±0.10 mm travel',ha='center',fontsize=9)
    for c in [(3,22),(40.2,22)]:
        ax.annotate('',(c[0],c[1]-3),(c[0],c[1]+3),arrowprops=dict(arrowstyle='->',color=AMBER,lw=2))
    ax.text(21.6,52,'Three plane seats; one round datum + one slot\nSpring preload: 2 N/chip (quad8 N)\nThermal pads allow compliant load sharing',ha='center',fontsize=10)
    ax.text(21.6,-13,'Locator/clip positions schematic; dimensions pending\nThree tongues → rails bonded to closed carrier\nWhole endcap installs axially',ha='center',fontsize=9)
    ax.set(xlim=(-6,50),ylim=(-18,60),aspect='equal',title='Module retention and load path',xlabel='Tangential u [mm]',ylabel='Radial v [mm]');ax.grid(alpha=.1)
    fig.suptitle('Mounting concept: thermal contacts are separate from alignment constraints\nEmbedded tracks fit in the plate; feed bends, manifold connections and flex artwork need CAD validation',fontsize=12)
    save(fig,out,'cooling-mounting')


def refine_thermal(report,cfg,own,out):
    result={}
    for name in NAMES:
        modules=json.loads((out/(name+'-layout.json')).read_text())['modules']
        refined=copy.deepcopy(own);refined['thermal'].update(fine_grid_mm=.25,coarse_grid_mm=.5)
        value=m.thermal(modules,cfg,refined)
        fine=[]
        for family,offset in [('single',0.),('quad',own['stem_offsets_mm']['quad_toward_center_v'])]:
            if not any(x['family']==family for x in modules):continue
            for fraction in [0.,own['thermal']['edge_fraction']]:
                a=m.sheet_reference.sheet_resistance(*cfg['active_mm'],*own['stem_mm'],offset,1500.,own['pickup_mm']['graphite'],.25,fraction,own['thermal']['edge_width_mm'])
                b=m.sheet_reference.sheet_resistance(*cfg['active_mm'],*own['stem_mm'],offset,1500.,own['pickup_mm']['graphite'],.125,fraction,own['thermal']['edge_width_mm'])
                fine.append(dict(family=family,edge_fraction=fraction,grid_mm=[.25,.125],sheet_K_W=[a['max_K_W'],b['max_K_W']],
                                 worst_stress_temperature_change_K=abs(a['max_K_W']-b['max_K_W'])*3*own['power_W_chip']*own['stress_multiplier'],sink_power_W=b['sink_power_W']))
        value['fine_control']=fine;value['retained_grid_mm']=.25
        result[name]=value
    (out/'thermal-refined.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def run(run_dir,native_dir,out):
    own,cfg,limits,prior=m.inputs();out.mkdir(parents=True,exist_ok=True)
    report=json.loads((run_dir/'screening.json').read_text());native=json.loads((native_dir/'acts.json').read_text())
    if not all(report['variants'][n]['all_18_interface_overlap_pass'] and report['variants'][n]['all_18_support_pass'] for n in NAMES):raise ValueError('Failed body/stem/overlap bounds')
    if not all(v['passed'] for n,v in native.items() if n!='provenance'):raise ValueError('Failed native evidence')
    if native['provenance']['screening_sha256']!=m.reference.digest(run_dir/'screening.json'):raise ValueError('Stale native evidence')
    for n in NAMES:shutil.copyfile(run_dir/(n+'-layout.json'),out/(n+'-layout.json'))
    for src in [run_dir/'screening.json',native_dir/'acts.json',Path(__file__).with_name('inputs.json'),Path(__file__).with_name('mounting-inputs.json')]:shutil.copyfile(src,out/src.name)
    refined=refine_thermal(report,cfg,own,out)
    failures={}
    central=copy.deepcopy(own);central['stem_offsets_mm']={k:0. for k in central['stem_offsets_mm']}
    for name in NAMES:
        raw=json.loads((run_dir/(name+'-layout.json')).read_text())['raw_modules']
        failures[name]=m.support_screen(m.radial.stagger(raw,cfg,cfg['disc_datum_mm']),cfg,limits,central)
    (out/'failed-outward-controls.json').write_text(json.dumps(dict(status='Reproduced central-contact outward-face rejection controls; not selected',controls=failures),indent=2)+'\n')
    layouts(run_dir,out,cfg);coverage_map(run_dir,out,cfg);support_drawings(out,cfg,own);mounting_drawings(out,report)
    rows=[];ringrows=[];svcrows=[];flowrows=[]
    annulus_area=math.pi*(cfg['annulus_mm'][1]**2-cfg['annulus_mm'][0]**2)
    for name,label in zip(NAMES,LABELS):
        v=report['variants'][name];checks=v['per_disc_screens'];T=refined[name]
        gap=max(c['worst_gap_mm2'] for c in checks);rmax=max(c['body']['maximum_radius_mm'] for c in checks)
        rows.append(f"| {label} | {v['modules']} | {v['chips']} | {max(c['overlap_percent'] for c in checks):.3f}% | {100*gap/annulus_area:.3f}% | {rmax:.3f} | {188.5-rmax:.3f} | {v['cooling']['nominal_W']:.3f} |")
        for r in v['rings']:ringrows.append(f"| {label} | {r['row']+1} | {r['family']} | {r['modules']} | {r['radius_mm']:.6f} | {r['phase_cells']:g} |")
        for s in v['services']['scenarios']:
            trunk=max(x['utilization'] for x in s['end_trunks']);neck=max(x['flange_neck_utilization'] for x in s['end_trunks'])
            svcrows.append(f"| {label} | {s['scenario']} | {v['services']['power_chains']} | {s['uplink_command_links']} | {trunk:.3f}× | {neck:.3f}× | FAIL |")
        for c in v['cooling']['circuits']:flowrows.append(f"| {label} | {c['physical_ring']} | {c['chip_row']+1} | {c['half']+1} | {c['chips']} | {c['nominal_W']:.3f} | {c['stress_W']:.3f} | {c['flow_g_s']:.1f} | {c['outlet_quality']:.4f} |")
    text=f'''# DES017 — Layout, local support, cooling and mounting comparison

- Status: DRAFT / isolated PROTOTYPE. Both original-annulus hermeticity and adverse engineering cases remain unresolved.
- Governing design: [DES017](../../design/DES-017-pixel-disc-support-variants.md); inputs and exact geometry are retained alongside this report.
- Source revision: `{report['provenance']['revision']}` plus the recorded dirty producer/input hashes. These locate the actual prototype; a later enclosing commit is not substituted as its execution revision.

![Layouts](layout-comparison.png)

## Geometric comparison

| Option | Physical modules/disc | Chips/disc | Worst silicon overlap/union | Worst sampled original-annulus gap | Max body/stem radius [mm] | Margin to188.5 plate [mm] | Nominal heat [W] |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

The mixed option retains102 inner singles and adds50 quads (22 at124 mm,28 at161 mm),
for152 modules and302 chips. It reduces separate module installations by48.65%,
while chip count/power rises2.03%. “4 + 4” refers to chip rows; there are six physical rings.
First four nominal rings and their radial/tangential frames are identical across options.
The new two-face placement changes local sensor z and its explicit xy compensation;
it does not claim to preserve PR41 survivor transforms. All18 source plate datums remain unchanged.

| Option | Physical ring | Family | Population | Nominal radius [mm] | Phase [cells] |
| --- | ---: | --- | ---: | ---: | ---: |
{chr(10).join(ringrows)}

324 candidates were ranked on a128-segment annulus approximation, with full2048-segment
circle bounds for retained station metrics. These finite grids are numerical settings,
not manufacturing tolerances. Ranking favours the smallest worst vertex gap among
bounded,≤20% overlap candidates; then chips and overlap. This is a bounded exploration,
not a global optimum or a certificate of continuous luminous-vertex coverage.
Active areas are four separate20×19.2 mm islands per quad; the0.2 mm inactive cross
is never filled. One shared silicon outline per assembly counts once. The0.1 mm
guard remains conditional; the retained0.5 mm guard control is separately reported.
At0.5 mm guard, full-disc silicon overlap becomes28.037% (single) and24.787%
(mixed), so both fail the20% limit. The small-guard sensor requires technology review.
**Full original-annulus hermeticity fails for both**, despite improvement in the mixed case.
Do not reduce the original target to redefine these failures as coverage success.

## Local support and mounting

![Local support](local-support.png)

Use a common r27..188.5 mm carbon sandwich,0.15 mm skins/6 mm foam. Alternate phi
columns between its faces, then colour the padded physical-body conflicts separately
on each face. First sensor offset is±4.1 mm; each further level adds1.65 mm.
This includes a1 mm occupied module,0.45 mm pickup and0.20 mm nominal gap.
The single option needs up to three levels per face; the mixed option two.
All18 tested stations have zero body/stem or core-insert conflicts at the stated
nominal gap. The nearest plate clears the605 mm barrel-turn end by
{report['variants'][NAMES[0]]['per_disc_screens'][0]['support']['nearest_plate_barrel_turn_gap_mm']:.3f} mm (single)
and{report['variants'][NAMES[1]]['per_disc_screens'][0]['support']['nearest_plate_barrel_turn_gap_mm']:.3f} mm (mixed).
Both give at least5.450 mm body clearance to the outward collector starting at w11.7 mm.
The0.20 mm pickup gap and0.10 mm tube-to-skin margin have no tolerance qualification.

Single pickups use one6×8 mm stem. Quads use four, one per chip, with contacts1 mm
radially toward the module centre; their two cooling tracks therefore follow
nominal v±8.7 mm. The0.30 mm graphite pickup is anisotropic; the stem's grain is
specified axially. Skin/cradle windows give a direct thermal path to machined
180° Ti saddles. Treat these as procurement and coupon requirements.
The reproduced outward-face central-stem controls fail and are retained in
[failed-outward-controls.json](failed-outward-controls.json), rather than concealed by body-only checks.

![Cooling and mounting](cooling-mounting.png)

Use one round datum plus a radial slot, three plane seats and spring retention.
Proposed preload is2 N/chip (single2 N,quad8 N), with compliant quad thermal pads
rather than four rigid alignment constraints. A±0.10 mm slot has nominal margin
over51.84 µm differential expansion in the explicit20 µm/(m K),60 K control.
Spring/contact pressure (equal-load proxy41.7 kPa), friction, pad flatness and clip
envelopes require coupon/FEA review. Locator positions in the drawing are schematic.

At disc scale, three10 mm tongues from r186..228 couple at90°,210°,330° to8×8 mm
CFRP box rails (0.4 mm walls,r223.7..231.7) bonded to the0.3 mm closed carrier
(r231.7..232,|z|609..3136). Cone/slot/plane coupling gives3+2+1 constraints.
The closed shell completes the load path; thin rails alone are not the recommendation.
Whole-endcap insertion is axial. A removable half-disc, installation around an
installed beam pipe, shell split and last-disc connector access are not qualified.

## Cooling, thermal and services

Both options need eight radial evaporator tracks and16 independently served
half-ring circuits, with32 feed/return legs. Quads reduce physical module count,
not cooling rows. OD2.8/wall0.15 mm Ti tubes occupy w±1.5 mm routing planes;
nominal crossing gap is0.20 mm and skin clearance0.10 mm. Track radii follow
the actual thermal contacts; all retained radial saddles fit their8 mm stem width.
Circuit arc length plus both radial legs and30 mm/leg bend allowance is an
inventory estimate. A10 mm bend-radius target, branch junctions, manifold and
pressure/leak tests need swept CAD and hydraulic verification. No tube-flow claim
is inferred from a geometric reservation.

Azimuthal evaporators use the+1.5 mm plane and radial fan-outs the−1.5 mm plane;
end-of-arc risers connect them. Separating them avoids nominal radial/azimuthal
crossings in one plane. The front pads have the longest path to the evaporator.
Thermal and insert-mass screens conservatively use that far-plane reach for both
faces. Actual risers, port separation, sector redistribution and weld access remain
unqualified; the drawing is a route concept, not a swept pipe collision certificate.

| Option | Ring | Chip row | Half | Chips | Nominal W | Stress W | Flow g/s | Stress outlet quality |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(flowrows)}

The flows sum to16.2 g/s (single) and16.4 g/s (mixed); rounded upward from1.5×
power/quality arithmetic, with1 g/s floor. They use the inherited313.18 J/g latent
heat proxy and0.10→0.45 quality window; neither pressure drop nor stable boiling
has been established, especially at the floor flow.

Thermal screening adds finite-volume sheet spreading to normal graphite,
stem/core, two bonds, insulating TIM, Ti saddle and h=10/20/30 kW/(m² K).
Uniform and edge-concentrated power, k=1500/1000/500 W/(m K),−40/−35°C coolant
and1.5× power are retained. Refined0.25 mm solutions and0.125 mm controls are
in [thermal-refined.json](thermal-refined.json);0.5/1 mm exploratory convergence
remains visible in screening.json. Full-circumference boiling area is optimistic;
h10k is the half-area sensitivity to h20k. Quad cross-talk, irradiated leakage
feedback, coolant temperature variation and interface ageing remain unmodelled.

| Option | Worst stress at−40°C [°C] | Worst stress at−35°C [°C] | −15°C screen |
| --- | ---: | ---: | --- |
{chr(10).join(f"| {label} | {max(x['stress_C'] for x in refined[name]['variants']):.3f} | {max(x['warm_stress_C'] for x in refined[name]['variants']):.3f} | −40 passes; −35 FAILS |" for name,label in zip(NAMES,LABELS))}

| Option | Bandwidth scenario | Power chains | Links/commands | Trunk utilization | Flange neck utilization | Result |
| --- | --- | ---: | ---: | ---: | ---: | --- |
{chr(10).join(svcrows)}

Homogeneous chains obey both16-module and32-chip limits (quad maximum8).
Both4 mm-OD feed/return transports count, giving402.124 mm²/disc before packing.
Eight preceding discs and barrel demand accumulate in the fixed r192..231.7 trunk
and r222 flange neck. **The mixed layout improves reference cable demand but does
not close the inherited packing failures**. Reference aggregation per physical
module is optimistic; conservative/stress per-chip links remain visible.
Thin8×0.20 mm buses route on each face around pickup windows, with8×0.12 mm tails
and three radial fan corridors between reserved mounting sectors. Actual bus
artwork, connectors, branch-end bends and flex sweeps require a routing study;
they are not part of the body/stem collision pass or a complete mass estimate.

## Material and structural scope

Estimated local dry subsets are{report['variants'][NAMES[0]]['budget']['local_dry_screen_g']:.2f} g
(single) and{report['variants'][NAMES[1]]['budget']['local_dry_screen_g']:.2f} g (mixed),
plus1 g/chip payload proxies of296/302 g. Component tables in screening.json
subtract reserved pipe/insert/glue volumes from foam and contact windows from skins,
including a180° saddle correction. These are conditional inventory estimates,
**not total disc masses**: flexes, liquid CO2, edge closeouts, tongue details,
manifolds and the shared carrier are excluded. Tube/insert routing intersections
and clipping these solids to the foam require CAD union-volume verification.
Do not infer a measured material reduction from the10 g difference.
The inherited diametral-beam proxy spans326.49 mm. Distributed/point load brackets
over E70..140 GPa are only gravity screens; they ignore laminate layup, windows,
shear, tabs, vibration, joints, preload and alignment. No qualified disc stiffness,
directional X0 map or passive DD4hep/Geant4 model is claimed.

## Native evidence and recommendation

{chr(10).join(f"- {key}: {v['tracks_requested']} tracks, {v['active_patches']} patches, native/oracle agreement={v['passed']}, {len(v['tracks_missing_target_disc'])} target-disc misses retained." for key,v in native.items() if key!='provenance')}

Matched native ACTS EigenStepper supporting-plane targets and native finite
RectangleBounds test all18 reflected discs, both charge signs,0/2 T, luminous
vertices and seam/edge probes, with exhaustive first-disc controls. Expected
misses are acceptance evidence, not transport mismatches.
The mixed layout has92 target misses against54 for eight singles in the540-track
sample:36 misses at r110,18 at r140,36 at r181 and2 curved probes at r175 mm.
Eight singles miss only the54 r181 edge probes. These deliberately sparse probes
are not efficiencies, but demonstrate why a smaller uncovered area is insufficient
to claim better tracking acceptance. The original-annulus holes remain a review gate.

![Coverage gaps](coverage-map.png)

This is vacuum transport,
not global navigation, passive-material transport or fitted resolution. The
rectangular25×100 µm binary covariance control is geometric only; polar axes
avoid global-xy pitch modulation at module centres, with finite-corner variation retained.

**Recommendation: use the four-single + two-quad variant as the next working
prototype**, with the common two-face sandwich and per-chip pickups. It nearly
halves mounting/handling operations, requires fewer axial levels, improves sampled
coverage and lowers reference cable demand, while keeping the radius within the
same fixed services. Keep the eight-single option as a modularity/yield control:
single-chip replacement is simpler and a failed module loses less area. Quad
yield, handling and replacement cost need vendor/assembly input.

Before adoption, prioritize: restore the remaining original-annulus holes without
increasing the service radius; measure thermal contacts and pressure drop at cold
and warm conditions; solve trunk/neck service demand; then qualify clip/flexure,
laminate/tolerance and swept routing with CAD/FEA and passive transport. Neither
formal sign-off nor production integration follows from this PR.
'''
    (out/'results.md').write_text(text)
    code=[Path(__file__),Path(__file__).with_name('study.py'),Path(__file__).with_name('native_audit.py'),Path(__file__).with_name('mounting-inputs.json')]
    files=[p for p in out.iterdir() if p.is_file() and p.name!='artifacts.json']
    manifest=dict(status='Curated DES017 PROTOTYPE evidence; source files/outputs identified, no acceptance',producer_hashes={str(p.relative_to(m.ROOT)):m.reference.digest(p) for p in code},artifact_hashes={p.name:m.reference.digest(p) for p in sorted(files)})
    (out/'artifacts.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(outputs=len(files),thermal_max_stress={n:max(x['stress_C'] for x in v['variants']) for n,v in refined.items()},fine_control_max_delta=max(x['worst_stress_temperature_change_K'] for v in refined.values() for x in v['fine_control'])),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--native',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.run,a.native,a.output)
