#!/usr/bin/env python3
"""Envelope-only gap and channel-service scenarios; never exports geometry."""
import argparse
import hashlib
import json
import math
from pathlib import Path

from services import budget

ROOT = Path(__file__).resolve().parents[2]


def screen():
    paths = [Path(__file__), *(Path(__file__).with_name(x) for x in
              ('barrel.json', 'endcaps.json', 'services.json', 'services.py'))]
    barrel, endcap, service = [json.loads(p.read_text()) for p in paths[1:4]]
    half_z = barrel['warm_half_z_mm'] - sum(barrel[x] for x in
        ('end_warm_mm', 'end_vacuum_mm', 'end_cold_mm', 'end_bath_mm'))
    r0, r1 = [barrel[x] for x in ('sampling_inner_radius_mm', 'sampling_outer_radius_mm')]
    # Actual outer turbine blade radius, DES033 primary-geometry paragraph.
    outer = 2790.0
    geometry = []
    for shift in (0, 200, 400):
        front = endcap['sampling_front_z_mm'] - shift
        back = front + endcap['sampling_depth_mm']
        geometry.append(dict(inward_shift_mm=shift,
            warm_front_gap_mm=endcap['warm_front_z_mm']-shift-barrel['warm_half_z_mm'],
            active_axial_separation_mm=front-half_z,
            endcap_sampling_front_mm=front, endcap_sampling_back_mm=back,
            endcap_first_envelope_eta=math.asinh(front/outer),
            endcap_full_axial_envelope_eta=math.asinh(back/outer)))
    services = []
    for divisor in (1, 2, 4):
        c = service | {key: service[key]//divisor for key in
                       ('barrel_channel_budget', 'endcap_channel_budget_each')}
        b = budget(c)
        services.append(dict(channel_budget_divisor=divisor,
            planning_channels=c['barrel_channel_budget']+2*c['endcap_channel_budget_each'],
            electronics_power_at_40_mW_kW=(c['barrel_channel_budget']+
                2*c['endcap_channel_budget_each'])*40/1e6,
            barrel_ordinary_station_area_mm2=b['stations']['barrel']['ordinary_occupied_area_mm2'],
            barrel_utility_station_area_mm2=b['stations']['barrel']['utility_occupied_area_mm2'],
            utility_s_bend_envelope_mm=b['bends']['100']['axial_s_bend_envelope_mm']))
    return dict(status='INFERENCE / envelope and service-budget screening only',
        limitations=[
            'Straight IP rays, origin vertex, phi-independent outer envelopes only.',
            'Depth fractions include absorber and liquid; they are not sensitive fractions, X0, containment or response.',
            'Inner wheel boundaries, support strips, inclined sampling, cryostat and service material are omitted.',
            'Inward shifts are unengineered scenarios and fail the existing front S-bend reservation.',
            'Service scaling retains fixed pipe, HV, power, ground and control counts and all diameters.',
            '40mW/channel is a planning hypothesis, not an engineered ASIC or total heat-load prediction.',
            'The4.3million planning channels differ from the3,488,768 logical cells in the current model.'
        ], barrel_sampling_half_z_mm=half_z,
        barrel_sampling_radii_mm=[r0,r1], endcap_outer_blade_radius_mm=outer,
        outer_blade_source='docs/design/DES-033-allegro-lar-endcaps.md: Primary geometry and deliberate adaptations',
        barrel_full_radial_envelope_until_eta=math.asinh(half_z/r1),
        barrel_any_envelope_until_eta=math.asinh(half_z/r0),
        geometry_scenarios=geometry, service_scenarios=services,
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})


def plot(result, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    eta = [1.1+i*.45/600 for i in range(601)]
    r0,r1 = result['barrel_sampling_radii_mm']
    hz,ro = result['barrel_sampling_half_z_mm'], result['endcap_outer_blade_radius_mm']
    clip = lambda x: min(1., max(0.,x))
    fig,ax = plt.subplots(figsize=(9,4.8), layout='constrained')
    ax.plot(eta,[clip((hz/math.sinh(e)-r0)/(r1-r0)) for e in eta],
            color='black',linewidth=2,label='Barrel radial envelope (fixed)')
    for scenario,color in zip(result['geometry_scenarios'],('#b54e25','#2276a5','#308357')):
        front,back = [scenario[x] for x in ('endcap_sampling_front_mm','endcap_sampling_back_mm')]
        shift = scenario['inward_shift_mm']
        label = 'Endcap: current envelope' if not shift else f'Endcap: {shift} mm inward scenario'
        ax.plot(eta,[clip((ro*math.sinh(e)-front)/(back-front)) for e in eta],
                color=color,label=label)
    ax.set(xlabel=r'$|\eta|$ (straight rays from the origin)',
           ylabel='Fraction of own radial / axial envelope depth',xlim=(1.1,1.55),ylim=(-.03,1.06),
           title='LAr barrel/endcap handover: envelope screening')
    ax.grid(alpha=.25)
    ax.legend(fontsize=9,loc='lower right')
    fig.supxlabel('Unengineered shifts; no materials, showers or service-route validation. Fractions must not be added.',fontsize=9)
    path.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(path,dpi=180)
    plt.close(fig)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--figure',type=Path)
    args=p.parse_args()
    result=screen()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    if args.figure:
        plot(result,args.figure)
