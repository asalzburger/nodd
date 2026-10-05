#!/usr/bin/env python3
"""PROTOTYPE cumulative cable geometry and sector cooling; no detector integration."""
import argparse
from collections import defaultdict
import gzip
import json
import math
from pathlib import Path
import subprocess
import sys

from mounting import make_mounts
from outward import ROOT, load_layout, sha, corners, stave_span
from services_geometry import body_envelope, _intersects
import services_budget as budget

HERE = Path(__file__).resolve().parent


def sector_index(phi, count):
    return int(math.floor((phi % (2*math.pi))*count/(2*math.pi)+.5)) % count


def cable_area(modules, chips, chains, inputs, scenario):
    p, s = inputs['pixel'], inputs['scenarios'][scenario]
    return dict(ancillary=chains*p['ancillary_chain_area_mm2'],
                links=(modules*(s['pixel_uplinks_per_module']+s['pixel_commands_per_module'])
                       +chips*s['pixel_uplinks_per_chip'])*p['differential_link_area_mm2'])


def outer_radius(inner, area, angle):
    return math.sqrt(inner*inner+2*area/angle)


def build(layout, config, mount_settings, inputs, settings):
    count = settings['sectors']
    if settings['drawing_scenario'] != 'reference':
        raise ValueError('Drawings describe the reference scenario; adverse cases remain numerical screens')
    if not isinstance(count, int) or count < 1:
        raise ValueError('Positive integer sector count required')
    if settings['ring_clearance_mm'] <= 0 or settings['transport_wall_mm'] <= 0:
        raise ValueError('Positive ring clearance and transport wall required')
    if settings['cable_composition_volume_fractions'] is not None:
        raise ValueError('Cable composition needs a separately reviewed material amendment')
    assembly, boxes, rings, feet, layers = make_mounts(layout, config, mount_settings)
    by_layer = {l['layer']: l for l in layers}
    bodies = {b['module_id']: b for b in layout['bodies']}
    groups = [g for g in budget._groups(layout, inputs) if g['subsystem'] == 'pixel' and g['region'] == 'barrel']
    routes = layout['metadata']['services']['routes']
    turn = [q for q in routes if q['subsystem'] == 'pixel' and q['role'] == 'barrel_turn' and q['side'] == 'positive']
    trunk = next(q for q in routes if q['id'] == 'pixel-trunk-P')
    boundary = inputs['capacity']['boundary_allowance_mm']
    bay = [min(q['z_min_mm'] for q in turn), max(q['z_max_mm'] for q in turn)]
    handoff = settings['handoff_radius_mm']
    if not trunk['r_min_mm']+boundary < handoff < trunk['r_max_mm']-boundary:
        raise ValueError('Handoff must be inside the axial trunk with boundary allowances')
    group_records, longitudinal = [], []
    for g in groups:
        bs = sorted((bodies[mid] for mid in g['module_ids']), key=lambda b: abs(b['center_mm'][2]))
        b = bs[0]; lid = g['layer_id']; layer = by_layer[lid]
        phi = math.atan2(b['center_mm'][1], b['center_mm'][0]) % (2*math.pi)
        gid = f"{lid}-c{g['local_index']:02d}-{g['side']}"
        ri = layer['ring_outer_radius_mm']+settings['ring_clearance_mm']
        family = config['families'][g['family']]
        record = dict(id=gid, layer_id=lid, col=g['local_index'], side=g['side'],
                      sector=sector_index(phi, count), phi_rad=phi, family=g['family'],
                      modules=g['modules'], chips=g['chips'], chains=g['power_chains'],
                      module_ids=[b['module_id'] for b in bs], inner_radius_mm=ri,
                      flow_per_leg_g_s=family['flow_g_s'], stave_power_W=sum(
                          family['chips']*config['power_per_chip_W'] for m in layout['bodies']
                          if m['layer_id']==lid and m['col']==g['local_index']),
                      scenarios={})
        ncols = layer['staves']
        for scenario, s in inputs['scenarios'].items():
            if not 0 < s['packing_fraction'] <= 1 or not 0 < s['available_phi_fraction'] <= 1:
                raise ValueError('Packing and phi fractions must be in (0,1]')
            angle = 2*math.pi/ncols*s['available_phi_fraction']
            steps = []
            raw_volumes = dict(ancillary=0., links=0.)
            for i, body in enumerate(bs):
                z0 = abs(body['center_mm'][2])
                z1 = abs(bs[i+1]['center_mm'][2]) if i+1 < len(bs) else bay[0]
                if z0 >= z1:
                    raise ValueError('Distinct module pickup positions before the bay required')
                chains = i//g['chain_capacity_modules']+1
                areas = cable_area(i+1, (i+1)*family['chips'], chains, inputs, scenario)
                raw = sum(areas.values())
                envelope = raw*s['demand_multiplier']/s['packing_fraction']
                ro = outer_radius(ri, envelope, angle)
                step = dict(id=f'{gid}-{scenario}-s{i:02d}', group_id=gid, layer_id=lid,
                            side=g['side'], scenario=scenario, pickup_module_id=body['module_id'],
                            abs_z_min_mm=z0, abs_z_max_mm=z1, r_min_mm=ri, r_max_mm=ro,
                            phi_center_rad=phi, phi_width_rad=angle, counts=dict(modules=i+1, chips=(i+1)*family['chips'], chains=chains),
                            footprint_mm2=areas, envelope_area_mm2=envelope,
                            connects_to=f'{gid}-{scenario}-s{i+1:02d}' if i+1<len(bs) else f"radial-{g['side']}-s{record['sector']:02d}-{scenario}")
                steps.append(step)
                for key, area in areas.items(): raw_volumes[key] += area*(z1-z0)
            longitudinal.extend(steps)
            record['scenarios'][scenario] = dict(terminal_footprint_mm2=steps[-1]['footprint_mm2'],
                terminal_outer_radius_mm=steps[-1]['r_max_mm'], footprint_volume_mm3=raw_volumes,
                reserve_multiplier=s['demand_multiplier'], packing_fraction=s['packing_fraction'],
                envelope_volume_mm3=sum(raw_volumes.values())*s['demand_multiplier']/s['packing_fraction'])
        group_records.append(record)

    # A ring overflight is conservative in radius. All-phi body radial bounds
    # provide a sufficient no-intersection check; failed bounds are potential,
    # not proven 3-D collisions. No obsolete inward pixel support shell is used.
    shell_checks = []
    other_bounds = [(b, body_envelope(b)) for b in layout['bodies'] if b['region']=='barrel']
    for lid, layer in by_layer.items():
        for scenario in inputs['scenarios']:
            gs = [g for g in group_records if g['layer_id']==lid]
            ri = gs[0]['inner_radius_mm']
            ro = max(g['scenarios'][scenario]['terminal_outer_radius_mm'] for g in gs)
            next_inner = min(e['r_min_mm'] for b,e in other_bounds if b['layer_id']!=lid and e['r_min_mm']>ri)
            shell_checks.append(dict(layer_id=lid, scenario=scenario, r_min_mm=ri, r_max_mm=ro,
                                     next_body_inner_mm=next_inner, radial_margin_mm=next_inner-ro,
                                     passes=ro<=next_inner-settings['numerical_tolerance_mm']))

    radial, sectors = [], []
    collector_z = sum(bay)/2
    branch_od = inputs['pixel']['feed_outer_diameter_mm']
    if branch_od != inputs['pixel']['return_outer_diameter_mm']:
        raise ValueError('Area-preserving paired collectors require equal inherited OD')
    if 2*settings['transport_wall_mm'] >= branch_od:
        raise ValueError('Transport wall closes the branch bore')
    for side in ['negative','positive']:
        for sector in range(count):
            gs = [g for g in group_records if g['side']==side and g['sector']==sector]
            if not gs: raise ValueError('Empty cooling sector: revise sector count')
            nodes = sorted(set(g['inner_radius_mm'] for g in gs))
            if nodes[-1] >= handoff:
                raise ValueError('Local services extend past the chosen radial handoff')
            sr = dict(side=side, sector=sector, staves=len(gs), groups=[g['id'] for g in gs],
                      feed_g_s=sum(g['flow_per_leg_g_s'] for g in gs),
                      exhaust_g_s=sum(g['flow_per_leg_g_s'] for g in gs),
                      nominal_exhaust_heat_W=sum(g['stave_power_W']/2 for g in gs),
                      stress_imbalanced_exhaust_heat_W=sum(g['stave_power_W']*config['stress_factor']*config['heat_fraction_max'] for g in gs),
                      pair_OD_mm=branch_od*math.sqrt(len(gs)), scenarios={})
            for scenario, s in inputs['scenarios'].items():
                angle = 2*math.pi/count*s['available_phi_fraction']
                segments=[]; wall_volume=liquid_volume=0.; cable_volumes=dict(ancillary=0.,links=0.)
                for index, r0 in enumerate(nodes):
                    r1 = nodes[index+1] if index+1<len(nodes) else handoff
                    incoming=[g for g in gs if g['inner_radius_mm']<=r0]
                    a={k:sum(g['scenarios'][scenario]['terminal_footprint_mm2'][k] for g in incoming) for k in ['ancillary','links']}
                    od=branch_od*math.sqrt(len(incoming)); wall=settings['transport_wall_mm']
                    pipes=2*math.pi*od**2/4
                    demand=(sum(a.values())+pipes)*s['demand_multiplier']
                    capacity=r0*angle*(bay[1]-bay[0]-2*boundary)*s['packing_fraction']
                    depth=demand/(r0*angle*s['packing_fraction'])
                    seg=dict(id=f"radial-{side}-s{sector:02d}-{scenario}-r{index}",
                             r_min_mm=r0, r_max_mm=r1, phi_center_rad=2*math.pi*sector/count,
                             phi_width_rad=angle, abs_z_center_mm=collector_z,
                             required_z_depth_mm=depth, capacity_mm2=capacity, demand_mm2=demand,
                             utilization=demand/capacity, staves=len(incoming), footprint_mm2=a,
                             cooling_pair_OD_mm=od, cooling_pair_footprint_mm2=pipes)
                    segments.append(seg)
                    for k in a: cable_volumes[k]+=a[k]*(r1-r0)
                    wall_volume+=2*math.pi*(od*od-(od-2*wall)**2)/4*(r1-r0)
                    liquid_volume+=2*math.pi*(od-2*wall)**2/4*(r1-r0)
                # Disjoint continuation after the collector centre. This ends at
                # the bay exit: DES-010 owns all subsequent endcap accumulation.
                a=segments[-1]['footprint_mm2']; pipes=segments[-1]['cooling_pair_footprint_mm2']
                demand=(sum(a.values())+pipes)*s['demand_multiplier']
                tr0,tr1=trunk['r_min_mm']+boundary,trunk['r_max_mm']-boundary
                capacity=.5*(tr1*tr1-tr0*tr0)*angle*s['packing_fraction']
                required_ro=outer_radius(tr0,demand/s['packing_fraction'],angle)
                # Material integral uses route centrelines, not overlapping corner boxes.
                length=bay[1]-collector_z
                for k in a: cable_volumes[k]+=a[k]*length
                od=sr['pair_OD_mm'];wall=settings['transport_wall_mm']
                wall_volume+=2*math.pi*(od*od-(od-2*wall)**2)/4*length
                liquid_volume+=2*math.pi*(od-2*wall)**2/4*length
                sr['scenarios'][scenario]=dict(radial_peak_utilization=max(x['utilization'] for x in segments),
                    axial_utilization=demand/capacity, axial_required_outer_radius_mm=required_ro,
                    cable_radial_and_handoff_footprint_volume_mm3=cable_volumes,
                    grouped_transport_Ti_volume_mm3=wall_volume, grouped_transport_full_liquid_volume_mm3=liquid_volume,
                    radial_pass=all(x['utilization']<=1 for x in segments), axial_pass=demand<=capacity,
                    terminal_cable_footprint_mm2=a, terminal_pipe_footprint_mm2=pipes)
                radial.append(dict(id=f'radial-{side}-s{sector:02d}-{scenario}', side=side,
                                   sector=sector, scenario=scenario, segments=segments,
                                   axial=dict(abs_z_min_mm=collector_z,abs_z_max_mm=bay[1],
                                              r_min_mm=tr0,r_max_mm=tr1,minimum_required_outer_radius_mm=required_ro,phi_width_rad=angle),
                                   connects_to=f'pixel-trunk-{side[0].upper()}'))
            sectors.append(sr)

    # Gathering stubs omitted from the idealized wedges but retained as inventory
    # lengths: each incoming cable rises in z, then takes the shortest phi arc.
    gathering=[]
    for g in group_records:
        delta=abs((g['phi_rad']-2*math.pi*g['sector']/count+math.pi)%(2*math.pi)-math.pi)
        cable_length=collector_z-bay[0]+g['inner_radius_mm']*delta
        bs=[bodies[mid] for mid in g['module_ids']]
        zend=max(abs(b['center_mm'][2])+b['half_v_mm'] for b in bs)
        if 'passive_stave_z_mm' in config:
            column=[b for b in layout['bodies'] if b['layer_id']==g['layer_id'] and b['col']==g['col']]
            span=stave_span(column,config)
            zend=span[1] if g['side']=='positive' else -span[0]
        pipe_r=math.hypot(*bs[0]['center_mm'][:2])+bs[0]['half_w_mm']+sum(config['stack_mm'][k] for k in ['interface','insulation','graphite','top_skin'])+config['stack_mm']['core']/2
        pipe_length=collector_z-zend+abs(g['inner_radius_mm']-pipe_r)+g['inner_radius_mm']*delta
        gathering.append(dict(group_id=g['id'], cable_path_length_mm=cable_length,
                              cooling_branch_length_per_leg_mm=pipe_length,
                              path_policy='axial plus radial (cooling) plus shortest phi arc; no bend excess',
                              phi_delta_rad=delta))
    totals=dict(modules=sum(g['modules'] for g in groups),chips=sum(g['chips'] for g in groups),
                chains=sum(g['power_chains'] for g in groups),staves=len(assembly[0]),
                local_evaporators=2*len(assembly[0]),cooling_sectors_per_end=count,
                total_sector_pairs=len(sectors),flow_g_s=sum(s['feed_g_s'] for s in sectors))
    summary=dict(status='PROTOTYPE effective service geometry; cable composition and hydraulics unqualified',
                 totals=totals, bay_abs_z_mm=bay, trunk_r_mm=[trunk['r_min_mm'],trunk['r_max_mm']],
                 handoff_radius_mm=handoff, section_z_mm=mount_settings['section_z_mm'],
                 reference_phi_fraction=inputs['scenarios']['reference']['available_phi_fraction'],
                 shell_checks=shell_checks, sectors=sectors, layers=[], scenarios={})
    for lid in by_layer:
        gs=[g for g in group_records if g['layer_id']==lid]
        summary['layers'].append(dict(layer_id=lid,modules=sum(g['modules'] for g in gs),chips=sum(g['chips'] for g in gs),
                                      chains=sum(g['chains'] for g in gs),staves=len(gs)//2))
    for scenario in inputs['scenarios']:
        values=defaultdict(float)
        for g, gather in zip(group_records,gathering):
            q=g['scenarios'][scenario]
            for k in ['ancillary','links']:
                values[k+'_footprint_volume_mm3']+=q['footprint_volume_mm3'][k]+q['terminal_footprint_mm2'][k]*gather['cable_path_length_mm']
            length=gather['cooling_branch_length_per_leg_mm']; od=branch_od; wall=settings['transport_wall_mm']
            values['Ti_volume_mm3']+=2*math.pi*(od*od-(od-2*wall)**2)/4*length
            values['full_liquid_volume_mm3']+=2*math.pi*(od-2*wall)**2/4*length
        for sec in sectors:
            q=sec['scenarios'][scenario]
            for k in ['ancillary','links']: values[k+'_footprint_volume_mm3']+=q['cable_radial_and_handoff_footprint_volume_mm3'][k]
            values['Ti_volume_mm3']+=q['grouped_transport_Ti_volume_mm3']
            values['full_liquid_volume_mm3']+=q['grouped_transport_full_liquid_volume_mm3']
        values['transport_Ti_mass_g']=values['Ti_volume_mm3']*config['density_g_cm3']['titanium']/1000
        values['transport_full_liquid_mass_g']=values['full_liquid_volume_mm3']*config['density_g_cm3']['liquid_CO2']/1000
        summary['scenarios'][scenario]=dict(values,
            barrel_envelope_pass=all(c['passes'] for c in shell_checks if c['scenario']==scenario),
            radial_peak_utilization=max(s['scenarios'][scenario]['radial_peak_utilization'] for s in sectors),
            axial_peak_utilization=max(s['scenarios'][scenario]['axial_utilization'] for s in sectors),
            cable_mass_g=None,cable_composition_volume_fractions=None,
            inventory_scope='Module pickup to |z|=605 mm; no local evaporator double count, manifold/clip/flex/connector/bend excess omitted')
    circuits=[]
    for g in group_records:
        if g['side']!='positive': continue
        for inlet,exhaust in [('positive','negative'),('negative','positive')]:
            circuits.append(dict(id=f"{g['layer_id']}-c{g['col']:02d}-inlet-{inlet}",
                layer_id=g['layer_id'],col=g['col'],sector=g['sector'],inlet_side=inlet,exhaust_side=exhaust,
                flow_g_s=g['flow_per_leg_g_s'],nominal_heat_W=g['stave_power_W']/2))
    export=dict(schema_version=1, circuits=circuits, units='mm, mm2, mm3, g, s, W, rad', groups=group_records,
                longitudinal=longitudinal, radial=radial, gathering=gathering,
                material_contract=dict(cable_composition_volume_fractions=None,
                    rule='component fraction in envelope = packing/demand_multiplier * supplied cable component fraction; reserve is empty until populated',
                    missing=['cable bill of materials','local pickup flex','manifold blocks','clips/trays','connectors','bend excess']),
                geometry_contract='Sector primitives plus centreline gathering inventory; union turns before volume construction; no cable mass or complete solid-model overlap claim')
    summary['reference_extraction_body_conflicts']=extraction_body_conflicts(layout,export)
    return summary,export,(assembly,boxes,rings,feet,layers)



def extraction_body_conflicts(layout, export, scenario='reference'):
    """Sufficient all-phi r-z check of finite radial and axial envelopes.

    Gathering paths, fittings and manifolds have inventory but no solid model;
    they are deliberately outside this check.
    """
    bounds=[(b['module_id'],body_envelope(b)) for b in layout['bodies']]
    conflicts=[]
    for route in export['radial']:
        if route['scenario']!=scenario: continue
        volumes=[]
        for seg in route['segments']:
            a=seg['abs_z_center_mm']-seg['required_z_depth_mm']/2
            b=seg['abs_z_center_mm']+seg['required_z_depth_mm']/2
            z0,z1=(a,b) if route['side']=='positive' else (-b,-a)
            volumes.append(dict(seg,z_min_mm=z0,z_max_mm=z1))
        axial=route['axial'];a=axial['abs_z_min_mm'];b=axial['abs_z_max_mm']
        z0,z1=(a,b) if route['side']=='positive' else (-b,-a)
        volumes.append(dict(axial,id=route['id']+'-axial',z_min_mm=z0,z_max_mm=z1))
        for volume in volumes:
            conflicts.extend([volume['id'],mid] for mid,box in bounds if _intersects(volume,box))
    return conflicts


def draw(summary, export, mounts, config, settings, layout, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Wedge, Polygon, Rectangle, Circle, Patch
    plt.rcParams.update({'font.size':10,'svg.fonttype':'none','pdf.fonttype':42,'svg.hashsalt':'DES002-services'})
    scenario=settings['drawing_scenario']
    assembly,boxes,rings,feet,layers=mounts
    bodies,sensors,parts,tubes=assembly
    blue,orange,purple='#087ea4','#d78225','#7950a1'
    colors={l['layer']:c for l,c in zip(layers,['#0072b2','#009e73','#cc79a7','#d55e00'])}
    def save(fig,name):
        for ext in ['png','pdf','svg']:
            p=output/f'{name}.{ext}'
            metadata={'Date':None} if ext=='svg' else ({'CreationDate':None,'ModDate':None} if ext=='pdf' else {})
            fig.savefig(p,dpi=180,metadata=metadata)
            if ext=='svg':p.write_text('\n'.join(s.rstrip() for s in p.read_text().splitlines())+'\n')
        plt.close(fig)
    def axes(ax):
        ax.grid(alpha=.16);ax.set_xlabel('x [mm]');ax.set_ylabel('y [mm]');ax.set_aspect('equal')
    def xy(ax,lids,z):
        for b in bodies:
            if b['layer_id'] in lids:ax.add_patch(Polygon(corners(b),fc='#d7e7d8',ec='#64836b',lw=.3))
        for p in boxes:
            if p['layer_id'] in lids:ax.add_patch(Polygon(corners(p),fc='#cebd98',ec='#5e6059',lw=.3))
        from mounting import foot_polygon
        for f in feet:
            if f['layer_id'] in lids and abs(f['center_mm'][2]-z)<f['half_v_mm']:
                ax.add_patch(Polygon(foot_polygon(f),fc='#9aadc2',ec='none'))
        for r in rings:
            if r['layer_id'] in lids and r['z_min_mm']<=z<r['z_max_mm']:
                ax.add_patch(Wedge((0,0),r['r_max_mm'],0,360,width=r['r_max_mm']-r['r_min_mm'],fc=purple))
        for t in tubes:
            if t['layer_id'] in lids:ax.add_patch(Circle(t['center_mm'],t['outer_radius_mm'],fc=blue,ec='#33434e',lw=.3))
        # Use the actual active patches at this section (mounts are cut at +110).
        for m in sensors:
            if m['layer_id'] in lids:
                p=[[m['center_mm'][i]+sign*m['half_u_mm']*m['u'][i] for i in range(2)] for sign in [-1,1]]
                ax.plot([v[0] for v in p],[v[1] for v in p],color='#187943',lw=.8)
        for step in export['longitudinal']:
            if step['layer_id'] in lids and step['scenario']==scenario and step['side']=='positive' and step['abs_z_min_mm']<=z<step['abs_z_max_mm']:
                angle=math.degrees(step['phi_center_rad']);width=math.degrees(step['phi_width_rad'])
                ax.add_patch(Wedge((0,0),step['r_max_mm'],angle-width/2,angle+width/2,
                                   width=step['r_max_mm']-step['r_min_mm'],fc=orange,ec='#9c591b',lw=.3))
        axes(ax)
    for layer in layers+[None]:
        chosen=[layer] if layer else layers;lids={l['layer'] for l in chosen};tag=layer['layer'].split('-')[-1] if layer else 'all'
        fig,ax=plt.subplots(figsize=(10,10));fig.subplots_adjust(bottom=.17,top=.88)
        xy(ax,lids,summary['section_z_mm'])
        r=max(c['r_max_mm'] for c in summary['shell_checks'] if c['layer_id'] in lids and c['scenario']==scenario)*1.07
        ax.set_xlim(-r,r);ax.set_ylim(-r,r)
        ax.set_title(f'Candidate A | {tag} | actual x–y cut at z = +{summary["section_z_mm"]:g} mm\nCumulative electrical bundles outside mounting rings',pad=15)
        fig.legend(handles=[Patch(fc='#d7e7d8',label='Module / fixed sensor plane'),Patch(fc='#cebd98',label='Stave with two CO₂ tubes'),
                            Patch(fc=purple,label='Mounting ring / feet'),Patch(fc=orange,label='Cable envelope, 50% packing')],
                   loc='lower center',bbox_to_anchor=(.5,.055),ncol=2,frameon=False)
        fig.text(.09,.025,'PROTOTYPE · reference cable scenario · ring overflight simplified · cable composition remains unspecified',fontsize=8)
        save(fig,'barrel-'+tag)
    # Longitudinal envelope and per-stave cumulative area use exact pickup steps.
    fig,axs=plt.subplots(2,2,figsize=(13,9),sharex=True)
    for ax,layer in zip(axs.flat,layers):
        lid=layer['layer']
        for side in ['negative','positive']:
            g=next(g for g in export['groups'] if g['layer_id']==lid and g['col']==0 and g['side']==side)
            steps=[s for s in export['longitudinal'] if s['group_id']==g['id'] and s['scenario']==scenario]
            sign=1 if side=='positive' else -1
            for st in steps:
                z0,z1=sorted([sign*st['abs_z_min_mm'],sign*st['abs_z_max_mm']])
                anc=st['footprint_mm2']['ancillary'];links=st['footprint_mm2']['links']
                ax.add_patch(Rectangle((z0,0),z1-z0,anc,fc=purple,ec='none'))
                ax.add_patch(Rectangle((z0,anc),z1-z0,links,fc=orange,ec='none'))
        ymax=max(sum(g['scenarios'][scenario]['terminal_footprint_mm2'].values()) for g in export['groups'] if g['layer_id']==lid)
        ax.set_xlim(-570,570);ax.set_ylim(0,ymax*1.2);ax.grid(alpha=.15)
        ax.set_title(lid.split('-')[-1]+' | one stave, both exits');ax.set_xlabel('z [mm]');ax.set_ylabel('Cable outer footprint [mm²]')
    fig.suptitle('Cables accumulate at every module; ancillary bundles at each chain start\nReference: 1 uplink + 1 command / module; supply AND return already counted',fontsize=14)
    fig.legend(handles=[Patch(fc=purple,label='Ancillary power / HV / monitoring'),Patch(fc=orange,label='Data + command')],loc='lower center',ncol=2,frameon=False)
    fig.tight_layout(rect=(0,.04,1,.92));save(fig,'cable-accumulation')
    fig,ax=plt.subplots(figsize=(14,7))
    for layer in layers:
        lid=layer['layer'];col=colors[lid]
        for b in bodies:
            if b['layer_id']==lid:
                # Azimuthal projection: draw one column per radial stagger level.
                if b['col']>1:continue
                allb=[q for q in layout['bodies'] if q['layer_id']==lid and q['col']==b['col']]
                lo=min(q['center_mm'][2]-q['half_v_mm'] for q in allb)
                hi=max(q['center_mm'][2]+q['half_v_mm'] for q in allb)
                for p in boxes:
                    if p['layer_id']==lid and p['col']==b['col']:
                        e=body_envelope(p)
                        ax.add_patch(Rectangle((lo,e['r_min_mm']),hi-lo,e['r_max_mm']-e['r_min_mm'],fc='#cebd98',alpha=.55))
                for t in tubes:
                    if t['module_id']==b['module_id']:
                        radius=math.hypot(*t['center_mm'])
                        ax.plot([lo,hi],[radius,radius],color=blue,lw=.55,alpha=.7)
                for q in allb:
                    e=body_envelope(q)
                    ax.add_patch(Rectangle((e['z_min_mm'],e['r_min_mm']),e['z_max_mm']-e['z_min_mm'],e['r_max_mm']-e['r_min_mm'],fc=col,alpha=.7))
        for r in rings:
            if r['layer_id']==lid:ax.add_patch(Rectangle((r['z_min_mm'],r['r_min_mm']),r['z_max_mm']-r['z_min_mm'],r['r_max_mm']-r['r_min_mm'],fc=purple))
        for st in export['longitudinal']:
            if st['layer_id']!=lid or st['scenario']!=scenario or '-c00-' not in st['group_id']:continue
            sign=1 if st['side']=='positive' else -1
            z0,z1=sorted([sign*st['abs_z_min_mm'],sign*st['abs_z_max_mm']])
            ax.add_patch(Rectangle((z0,st['r_min_mm']),z1-z0,st['r_max_mm']-st['r_min_mm'],fc=orange,alpha=.8))
        ax.text(0,layer['ring_outer_radius_mm']-8,lid.split('-')[-1],ha='center',fontsize=10)
    for sign in [-1,1]:
        z0,z1=sorted([sign*z for z in summary['bay_abs_z_mm']])
        ax.add_patch(Rectangle((z0,30),z1-z0,204,fc=blue,alpha=.12))
        ax.annotate('radial collection', (sign*580,210),(sign*465,227),ha='center',fontsize=9,arrowprops=dict(arrowstyle='->'))
    ax.set(xlim=(-625,625),ylim=(20,240),xlabel='z [mm]',ylabel='|r| [mm]',title='Mounted pixel barrels with stepped longitudinal service envelopes\nAll-phi projection; individual phi sectors are not continuous material shells')
    ax.grid(alpha=.15)
    fig.text(.12,.02,'Orange: cable envelopes above ring radius. Blue ends: existing 555–605 mm service bays. Stave stacks lie between modules and rings.\nRadial scale enlarged for readability. No module positions moved; CAD bends and local pickup flex are omitted.',fontsize=9)
    fig.subplots_adjust(bottom=.17);save(fig,'barrels-rz')
    # Separate radial routing drawing: topology over all sectors + dimensional bay.
    fig=plt.figure(figsize=(15,9));ax=fig.add_axes([.045,.16,.48,.72]);detail=fig.add_axes([.59,.51,.37,.32]);loads=fig.add_axes([.59,.15,.37,.24])
    for r in [l['ring_outer_radius_mm'] for l in layers]:ax.add_patch(Circle((0,0),r,fill=False,ec='#999999',lw=.7))
    ax.add_patch(Wedge((0,0),234,0,360,width=44,fc=blue,alpha=.10))
    for sec in [s for s in summary['sectors'] if s['side']=='positive']:
        phi=2*math.pi*sec['sector']/settings['sectors']
        angle=math.degrees(phi);width=360/settings['sectors']*summary['reference_phi_fraction']
        ax.add_patch(Wedge((0,0),settings['handoff_radius_mm'],angle-width/2,angle+width/2,width=settings['handoff_radius_mm']-layers[0]['ring_outer_radius_mm'],fc=orange,alpha=.12))
        ax.plot([44*math.cos(phi),212*math.cos(phi)],[44*math.sin(phi),212*math.sin(phi)],color=blue,lw=2)
        for g in export['groups']:
            if g['side']!='positive' or g['sector']!=sec['sector']:continue
            r=g['inner_radius_mm'];p=g['phi_rad'];delta=(phi-p+math.pi)%(2*math.pi)-math.pi
            arc=[p+delta*i/20 for i in range(21)]
            ax.plot([r*math.cos(a) for a in arc],[r*math.sin(a) for a in arc],color=colors[g['layer_id']],lw=1)
            ax.plot(r*math.cos(p),r*math.sin(p),'o',color=colors[g['layer_id']],ms=3)
        ax.text(246*math.cos(phi),246*math.sin(phi),f"{sec['sector']+1}\n{sec['staves']} staves",ha='center',va='center',fontsize=8)
    axes(ax);ax.set_xlim(-270,270);ax.set_ylim(-270,270);ax.set_title('+z bay, viewed along beam\n12 sector pairs; coloured arcs collect actual stave populations',fontsize=11)
    detail.add_patch(Rectangle((555,30),50,204,fc='#edf3f6',ec='#9caab5'))
    detail.add_patch(Rectangle((555,190),70,44,fc=blue,alpha=.15))
    for l in layers:
        ri=l['ring_outer_radius_mm']+.5
        detail.annotate('',(580,ri),(545,ri),arrowprops=dict(arrowstyle='->',color=orange,lw=2))
    detail.annotate('',(580,212),(580,44),arrowprops=dict(arrowstyle='->',color=blue,lw=2))
    detail.annotate('',(622,212),(580,212),arrowprops=dict(arrowstyle='->',color=blue,lw=2))
    detail.axvline(605,color='#48545d',ls='--',lw=1)
    detail.text(607,175,'endcap\ntrunk',fontsize=9)
    detail.text(565,65,'cumulative radial bundle',rotation=90,fontsize=9)
    detail.set(xlim=(540,628),ylim=(20,242),xlabel='|z| [mm]',ylabel='r [mm]',title='Radial bay → outer pixel endcap trunk (schematic)');detail.grid(alpha=.15)
    positives=[s for s in summary['sectors'] if s['side']=='positive'];xs=list(range(1,len(positives)+1))
    loads.bar(xs,[s['feed_g_s'] for s in positives],color=blue)
    loads.set(xticks=xs,xlabel='Cooling sector at one end',ylabel='Flow per leg [g/s]',title='Supply and exhaust carry equal total flow');loads.grid(axis='y',alpha=.15)
    fig.suptitle('Separate extraction model | cable bundles and grouped CO₂ pairs\nExisting radial bay |z| = 555–605 mm → axial annulus r = 190–234 mm',fontsize=16,y=.98)
    fig.text(.06,.035,'PROTOTYPE topology: each blue radial line represents ONE supply + ONE exhaust, not a single pipe. Both ends use the same 12-sector partition.\nCable ribbons share the sector corridors; bends/manifold detail omitted. Downstream endcap pickups stay in DES-010 and are not replaced.',fontsize=10)
    save(fig,'radial-extraction')
    return matplotlib.__version__


def report(summary,output):
    rows=[]
    for l in summary['layers']:
        c=next(c for c in summary['shell_checks'] if c['layer_id']==l['layer_id'] and c['scenario']=='reference')
        rows.append(f"| {l['layer_id'].split('-')[-1]} | {l['staves']} | {l['modules']} | {l['chains']} | {c['r_min_mm']:.3f}–{c['r_max_mm']:.3f} | {c['radial_margin_mm']:.3f} |")
    checks=[]
    for name,s in summary['scenarios'].items():
        checks.append(f"| {name} | {'pass' if s['barrel_envelope_pass'] else 'FAIL / potential overlap'} | {100*s['radial_peak_utilization']:.1f}% | {100*s['axial_peak_utilization']:.1f}% |")
    sectors=[s for s in summary['sectors'] if s['side']=='positive']
    s=summary['scenarios']['reference']
    text=f'''# DES-002 — Cumulative cables and sector cooling

Status: **PROTOTYPE**, 2026-09-30. [Routing request](https://github.com/asalzburger/nodd/pull/29#issuecomment-5911262892).
Governing choices: [DES-002 PS-C15–C19 / PS-I09](../../../design/DES-002-pixel-barrel-support-cooling.md#cable-bundles-and-twelve-sector-cooling-extraction).

## Recommendation and limits

Use outward stepped bundles, with **12 cooling sectors per end (24 feed/exhaust
pairs total)**. Keep the existing 164 independent counterflow evaporators; each
stave contributes one feed and one exhaust at each end. Module positions, rings,
feet and the selected baseline remain unchanged. This is a repeatable simulation
geometry proposal, not a complete solid model or engineering qualification.

**The reference cable scenario fits the sufficient radial envelope screen and
sector capacity screens. Conservative and stress scenarios fail.** In particular,
B1 has only 1.778 mm nominal reference clearance to B2. Do not approve these
spaces without settling cable aggregation/composition and cooling hydraulics.
A failed all-phi bound denotes a potential overlap, not an exact wedge/body
intersection. The adverse scenarios also exceed finite route capacity, a separate
failure. No gap or module placement was changed to hide it.

## Drawings

![Cumulative cable footprint along all four barrels](cable-accumulation.png)

![Barrel projection with cables](barrels-rz.png)

![Dedicated radial extraction drawing](radial-extraction.png)

| View | PNG | PDF | SVG |
| --- | --- | --- | --- |
'''
    for name in ['barrel-B1','barrel-B2','barrel-B3','barrel-B4','barrel-all','cable-accumulation','barrels-rz','radial-extraction']:
        text+=f'| {name} | [PNG]({name}.png) | [PDF]({name}.pdf) | [SVG]({name}.svg) |\n'
    text+='''
The x–y cuts are at z=+110 mm and show actual accumulated load there, not the
larger end bundle. The ring overflight extends along the whole stave in this
effective geometry. The all-phi |r|–z projection is not a solid cable annulus;
radial scale is enlarged. The extraction drawing shows shortest azimuthal
collection arcs and the existing radial bay; lines represent bundles. It is a
topology view, not a packing proof or a manifold CAD model.

## Counts and geometry

All 2,750 physical barrel modules / 6,206 chips are assigned exactly once to
164 half-stave groups and 328 ancillary chains. Modules at z≥0 route to +z.
Ancillary supply AND return are already included in the 35 mm² chain footprint.
The 47-row single-chip staves have unequal 23/24-module halves; there is no
assumed perfect end symmetry for electrical loads. Chains start at the inner
module and are capped at 16 modules and 32 chips. A chain's full transport bundle
starts at its first pickup; serial jumpers and local module flex are not resolved.
Each module adds data and command links. Modules are not pooled across staves.

| Layer | Staves | Modules | Chains, both ends | Reference cable radii, maximum [mm] | Gap to next barrel body [mm] |
| --- | --- | --- | --- | --- | --- |
'''+ '\n'.join(rows)+'''

An annular sector covers the inherited available fraction of each stave pitch.
Its transverse area is exactly raw cable footprint × demand multiplier / packing.
Ring radii +0.5 mm define its inner edge. Ring/foot/stave radial containment and
next-layer minimum body radii prove the nominal reference envelope clear; the
obsolete inward DES-010 pixel support reservations are not actual outward-A
structures. The unresolved global end brackets and new clips are not checked. The finite
reference radial and axial extraction envelopes also have zero intersections
with all baseline module r–z bounds. This excludes the unmodeled gathering
solids and manifold hardware; it is not a full solid-model overlap claim.

## Finite extraction capacity

Capacity uses actual sector populations, not a total divided by twelve. Each
successive radial interval adds the layer that joins there. Available radial
area is r_min × sector angle × (50−2×2) mm; axial capacity uses the exact sector
area of the 190–234 mm trunk after 2 mm boundary allowances. Cable and both pipe
legs are included, with the inherited packing, phi and spare-demand scenario.
The following axial figures are **barrel contribution only at the bay exit**,
not certification of downstream endcap plus barrel loading.

| Scenario | Barrel radial bound | Worst radial capacity used | Worst axial capacity used |
| --- | --- | --- | --- |
'''+ '\n'.join(checks)+f'''

The most populated sector has {max(q['staves'] for q in sectors)} staves; the least has
{min(q['staves'] for q in sectors)}. Each grouped feed/exhaust outer diameter is
4√N mm: {min(q['pair_OD_mm'] for q in sectors):.3f}–{max(q['pair_OD_mm'] for q in sectors):.3f} mm at the outer handoff.
This preserves the upstream 4 mm branch footprints; it does **not** establish a
two-phase exhaust bore, pressure drop or pressure-vessel wall.

Total circulation remains {summary['totals']['flow_g_s']:.1f} g/s. Each end supplies and returns
{sum(q['feed_g_s'] for q in sectors):.1f} g/s; individual sector legs carry
{min(q['feed_g_s'] for q in sectors):.1f}–{max(q['feed_g_s'] for q in sectors):.1f} g/s.
Nominal sector exhaust heat is {min(q['nominal_exhaust_heat_W'] for q in sectors):.1f}–{max(q['nominal_exhaust_heat_W'] for q in sectors):.1f} W;
the +50% / 2:1 imbalance screen gives up to {max(q['stress_imbalanced_exhaust_heat_W'] for q in sectors):.1f} W at one exhaust.
Do not sum the worst imbalance at both ends as an extra physical heat source.
The earlier local energy balance is unchanged; collection does not qualify flow
sharing. Twelve sectors are a routing partition, not twelve independent detector
evaporators or an established failure-isolation system.

## Material accounting for later full simulation

Integrate footprint × route length by cable class. The reference model gives
**{s['ancillary_footprint_volume_mm3']/1e6:.4f} litres ancillary footprint and
{s['links_footprint_volume_mm3']/1e6:.4f} litres data/command footprint**, through
|z|=605 mm, including idealized collection paths. These are cable outer-envelope
volumes, **not solid copper volumes or masses**. The reserve multiplier adds
space, not unobserved matter. Longitudinal envelopes preserve these volumes with
component fraction packing/demand_multiplier × the supplied cable composition.
For radial wedges, normalize each component by its integrated footprint volume
divided by the actual sector volume; constant upstream depth reserves extra area
as radius grows. Wedge turns must be unioned/partitioned before solid construction.

Cable composition and mass are deliberately null in the export: the inherited
35 mm² prototype bundle gives no conductor or insulation inventory. Assigning the
unrelated 9 µm Cu / 35 µm polyimide local flex to it would invent material. Supply a
cable bill of materials before creating a production effective material. This
missing input prevents a qualified full-simulation material result today.

A separate provisional 0.15 mm Ti wall screen for the transport network gives
**{s['transport_Ti_mass_g']:.2f} g Ti** and **{s['transport_full_liquid_mass_g']:.2f} g full-liquid CO₂ upper bound**.
These additions exclude the already-counted 164 local evaporators. The grouped
pair wall area is recalculated from its larger OD, not copied from the sum of
branch walls. The idealized length inventory includes axial stubs, shortest phi
arcs, radial branches/collectors and the axial handoff. Manifold blocks, fittings,
local module flex, clips/trays, connectors and bend excess remain additional;
this is not total service mass. Liquid filling is a mass bound, not operating
mixture density. The wall is not warm-pressure certified.

## Reproduction and validation scope

```sh
MPLCONFIGDIR=/tmp/nodd-des002-mpl python3 -B tools/pixel_support/services.py
python3 -B -m unittest discover -s tools/pixel_support -p 'test_*.py' -v
```

[screening.json](screening.json) holds numerical results, source revision, exact
hashes, versions and command. [routing.json.gz](routing.json.gz) contains stable
IDs, module ownership, all three longitudinal scenarios, finite radial segments,
gathering path lengths, flow and material-accounting contracts. Its geometry is
an additive prototype, not wired into DD4hep. [artifacts.json](artifacts.json)
identifies the producer and every generated artifact. Earlier three evidence
sets remain unchanged. Checks cover module conservation, chain rounding,
monotonic accumulation, independent volume integration, uneven sector loading,
counterflow totals, envelope-area inversion and explicit failing scenarios.
No Geant4, ACTS, tracking gain, complete solid-model overlap check, material scan,
FEA or hydraulic test is claimed.
'''
    (output/'results.md').write_text(text)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'docs/validation/DES-002/outward-A-services')
    args=parser.parse_args()
    config=json.loads((HERE/'inputs.json').read_text());mount=json.loads((HERE/'mounting.json').read_text())
    settings=json.loads((HERE/'services.json').read_text());inputs=json.loads((ROOT/'tools/module_layout/services_budget_inputs.json').read_text())
    layout=load_layout(config)
    summary,export,mounts=build(layout,config,mount,inputs,settings)
    args.output.mkdir(parents=True,exist_ok=True)
    version=draw(summary,export,mounts,config,settings,layout,args.output)
    paths=['tools/pixel_support/'+name for name in ['services.py','services.json','inputs.json','mounting.json','mounting.py','outward.py']]
    paths+=['tools/module_layout/'+name for name in ['services_budget_inputs.json','services_budget.py','services_geometry.py','geometry.py']]
    import numpy
    summary['provenance']=dict(baseline=config['baseline'],baseline_sha256=config['baseline_sha256'],
        producer_files_sha256={p:sha(ROOT/p) for p in paths},python=sys.version,numpy=numpy.__version__,matplotlib=version,
        source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command='python3 -B '+' '.join(sys.argv),random_seed=None)
    export['provenance']=summary['provenance']
    (args.output/'screening.json').write_text(json.dumps(summary,indent=2)+'\n')
    (args.output/'routing.json.gz').write_bytes(gzip.compress((json.dumps(export,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
    report(summary,args.output)
    artifacts=[p for p in args.output.iterdir() if p.name!='artifacts.json']
    (args.output/'artifacts.json').write_text(json.dumps(dict(producer_files_sha256=summary['provenance']['producer_files_sha256'],artifacts_sha256={p.name:sha(p) for p in sorted(artifacts)}),indent=2)+'\n')
    print(json.dumps(dict(totals=summary['totals'],scenarios=summary['scenarios']),indent=2))


if __name__=='__main__': main()
