#!/usr/bin/env python3
"""Regenerate DES014 support proposal and screening; never modifies active geometry."""
import argparse
import csv
import datetime
import json
import platform
import os
import shlex
import subprocess
from pathlib import Path
import sys
import numpy as np
from model import ROOT, digest, load_inputs, template, proposal, run_geometry
from thermal import thermal_screen
from budget import inventory, services


def results_text(r):
    g,t,m,s=r['geometry'],r['thermal'],r['materials_mechanics'],r['services']
    nominal=next(v for v in t['variants'] if v['k_inplane_W_m_K']==1500 and v['periphery_fraction']>0 and v['htc_W_m2_K']==20000)
    lines=['# DES-014 — Pixel endcap support screening','',
           '- Status: DRAFT / PROTOTYPE. **Mechanical concept B is proposed for development; thermal stress target FAILS.**',
           '- No baseline sensor or DD4hep geometry was changed. B is an explicit placement amendment requiring review and a subsequent coverage/ACTS study.',
           '- Reproduce with `MPLCONFIGDIR=/tmp/nodd-endcap-mpl python3 -B tools/pixel_endcap_support/report.py`.',
           '- Exact inputs, source/code hashes, versions, timestamp and scope: [screening.json](screening.json).',
           '- [Design and approval boundary](../../design/DES-014-pixel-endcap-support.md), [literature dossier](../../design/inputs/DES-014-literature.md), [drawing book](drawings.pdf).','',
           '## Geometry and commonality','',
           f'All 18 baseline discs share the same x/y pattern: {g["baseline_module_count"]//18} quads/disc, five rows with '+', '.join(str(x['modules']) for x in g['rows'])+' modules. '+
           f'Total: {g["baseline_module_count"]} modules and {g["baseline_chip_count"]} active chip patches. No modules are removed.',
           '', 'A single backplate retaining current positions needs narrow central posts: the 4×4 mm trial clears by '+f'{g["retained_backplate_post_probes"]["4.0"]["minimum_gap_mm"]:.3f} mm; the 6×6 mm trial has '+str(g['retained_backplate_post_probes']['6.0']['overlaps'])+' post/body conflicts per positive template. This is a test of those two centred-post designs, not a proof that no support retaining the layout could work.',
           '', 'B uses a common 6.3 mm carbon sandwich and short, broad outboard thermal feet. Rows 0/2/4 face the IP; rows 1/3 face away. Three heights on row 0 avoid next-nearest-neighbour body collisions; two suffice on other rows. The first-disc and collector datum comes from the explicit disc table when supplied; otherwise the legacy 3.5 mm outward shift applies **only in the proposal**.', '',
           '| Envelope comparison | Overlaps | Minimum gap [mm] |','| --- | ---: | ---: |']
    lines += [f'| {k} | {v["overlaps"]} | {v["minimum_gap_mm"]:.3f} |' for k,v in g['comparisons'].items()]
    lines += ['',f'Tube-plane clearance is {g["tube_plane_gap_mm"]:.3f} mm; nominal tube-to-skin clearance {g["tube_to_skin_clearance_mm"]:.3f} mm. These are tight fabrication targets, not qualified tolerances. First-disc clearance to the barrel extraction bay is {g["first_disc_barrel_turn_clearance_mm"]:.3f} mm; module-to-pixel-trunk radial clearance remains {g["body_to_trunk_radial_clearance_mm"]:.3f} mm.',
              '', 'The OBB checks cover pickup and foot envelopes against modules and each other. Pipe transitions, tabs/pockets, clips and a fully routed flex/harness remain outside that proof. [Proposed module positions](proposed-module-placements.csv) retain old/new z and unchanged x/y; they are not an ACTS input baseline.', '',
              '| Disc | Old nominal z [mm] | Proposed nominal z [mm] | Occupied absolute z [mm] |', '| --- | ---: | ---: | --- |']
    lines += [f'| {d["layer"]} | {d["old_z_mm"]:.3f} | {d["proposed_z_mm"]:.3f} | {d["body_abs_z_min_mm"]:.3f}–{d["body_abs_z_max_mm"]:.3f} |' for d in g['discs']]
    lines += ['', '## Cooling and the thermal blocker','',
              f'Ten independently metered half-ring circuits/disc carry {t["disc_nominal_W"]:.3f} W nominal; the 18-disc total is {t["all_endcaps_nominal_W"]/1000:.3f} kW. Proposed flow is {t["disc_flow_g_s"]:.1f} g/s/disc ({t["all_endcaps_flow_g_s"]:.1f} g/s total). These do not include the separate barrel flow.', '',
              '| Row | Modules/circuit | Nominal/stress power [W] | Flow [g/s] | Stress exit quality |', '| --- | ---: | ---: | ---: | ---: |']
    lines += [f'| {c["row"]+1} | {c["modules_per_circuit"]} | {c["nominal_W"]:.3f} / {c["stress_W"]:.3f} | {c["flow_g_s"]:.1f} | {c["stress_exit_quality"]:.3f} |' for c in t['circuits']]
    lines += ['',f'All ten circuits pass the 0.45 quality arithmetic ceiling at 1.5× load; this does not establish boiling stability or pressure drop. The thermal bottleneck is the module pickup, not the available latent heat. At −40 °C coolant, the edge-biased 1500 W/(m K), h=20 kW/(m² K) screen gives **{nominal["nominal_C"]:.1f} °C nominal and {nominal["stress_C"]:.1f} °C stress**, against a −15 °C target. Total resistance is {nominal["R_total_K_W"]:.3f} K/W; it needs to be ≤{t["required_total_R_K_W"]:.3f} K/W ({100*(1-t["required_total_R_K_W"]/nominal["R_total_K_W"]):.1f}% lower). Do not solve this failure by declaring higher graphite conductivity or a better boiling coefficient without measurements.', '',
              'Two-dimensional finite-volume heat spreading is coupled to explicit graphite c-axis, foot, contact and tube resistances. The uniform map is also retained; the edge-biased map is a hot-region sensitivity, not an RD53 power map. The coarser/finer 1.0/0.5 mm grids differ by '+f'{100*max(a["relative_change"] for a in t["grid_convergence"]):.2f}% in sheet resistance. Heat balance is checked separately. No irradiated-sensor feedback or thermal-runaway claim is made.', '',
              'The retained-position case A already reaches '+f'{t["retained_A_optimistic_stress_C"]:.1f} °C in an optimistic post-plus-bond-only stress lower bound, before adding the spreader, electrical isolation or tube/boiling drop. It is not selected for development.', '',
              'Next thermal step: a full-size powered quad/foot coupon, then a two-module overlap demonstrator, measuring the full resistance and the effective contact area. Test an additional thermal pickup path or revised local overlap; retain the 0.2 mm neighbour gap. Both require a geometry/material update and repeat of this screen. Raising flow alone cannot eliminate pickup spreading resistance.', '',
              '## Material and stiffness','',
              f'Per disc: **{m["disc_passive_mass_g"]:.1f} g** modelled local passive assembly, including full-liquid tube mass, provisional flex and clip/hardware allowances. Annulus-normalized equivalent passive inventory (including outer hardware) is **{m["disc_equivalent_normal_X0_percent"]:.3f}% X0**. This exceeds the historic ideal-layer 1% proxy before silicon: do not reuse that proxy as a material validation result.', '',
              f'Shared rails, closed carrier shell and two end flanges add **{m["shared_support_per_end_g"]/1000:.3f} kg/end**. The 18 local assemblies plus two carriers total {m["all_18_discs_passive_plus_two_carriers_kg"]:.3f} kg. Sensors/ASICs, external service trunks, real fittings and connector material are not included in this passive total. The stiffness screen adds the 4 g/module payload and a separate 5 kg/end service load allowance.', '',
              '| Local component | Mass [g/disc] | Equivalent X0 [%] |','| --- | ---: | ---: |']
    lines += [f'| {a["component"]} | {a["mass_g"]:.2f} | {a["annulus_normalized_X0_percent"]:.4f} |' for a in m['components'] if a['scope']=='disc']
    lines += ['', '| Laminate E [GPa] | Disc distributed/central-load beam [mm] | Closed-shell sag [mm] |', '| ---: | ---: | ---: |']
    lines += [f'| {e["E_GPa"]:.0f} | {e["disc_beam_distributed_mm"]:.3f} / {e["disc_beam_central_load_mm"]:.3f} | {e["closed_shell_sag_mm"]:.3f} |' for e in m['elastic_screens']]
    lines += ['', 'These beam estimates support a **closed carrier shell with rails bonded to it**. Standalone 8×8 mm rails over the full length leave the small-deflection regime and are rejected; metre-scale linear-model deflections are a failure indicator, not predictions. The disc beam bracket straddles the provisional 0.1 mm screen in some cases. No claim of stiffness qualification follows from the shell sag estimate: annular geometry, core shear, joints, shell ovalization, torsion and thermal-cycle/eigenmode FEA remain required.', '',
              '## Cabling, collectors and mounting interfaces','',
              f'Each disc has {s["power_chains_per_disc"]} independently grouped power chains (≤8 quads), separate from its ten cooling circuits. Front-face modules stay on front-face buses; rear modules stay on rear buses. Both wrap around the outer rim to the existing 50 mm collection bay. Keep clamps/lugs out of those routes. The last disc retains its conditional inner bypass and needs a dedicated routing adapter; a common mechanical disc does not make this external route identical.', '',
              '| Pixel trunk after eight discs, positive end | Demand [mm²] | Capacity [mm²] | Utilization |', '| --- | ---: | ---: | ---: |']
    lines += [f'| {a["scenario"]}: {a["status"]} | {a["demand_mm2"]:.1f} | {a["capacity_mm2"]:.1f} | {100*a["utilization"]:.1f}% |' for a in s['accumulation'] if a['side']=='positive' and a['endcap_discs_joined']==8]
    lines += ['', 'This includes the current PR35 barrel handoff inventory, not the older PR25 module counts. Negative-end results are also retained. The reference passes only as an aggregate area inequality and has little headroom; the adverse scenarios fail. Fixed-sector redistribution and connector/weld pockets are not validated. No additional detector row is silently removed.', '',
              'Use three disc tongues at 90°, 210°, 330° on common box rails. A cone/slot/plane coupling supplies 3+2+1 constraints; a spring latch provides preload without a second rigid datum. The carrier has one axial datum and a sliding opposite end interface. No six rigid bolts or unsupported long rails are assumed. The one-piece disc/cassette is installed axially; beam-pipe access and an eventual shell split need a separate swept-envelope review.', '',
              '## Advance conditions','',
              '1. Review the proposed z/face amendment and the first-disc/collector shift; then run matched straight/helical coverage plus ACTS audit. No adoption is inferred from this design PR.',
              '2. Close the thermal resistance gap with measured interfaces and 3D electrothermal analysis, including irradiated-sensor feedback and hydraulic/pressure tests.',
              '3. Complete pipe transitions, flex artwork, cable voltage-drop/bandwidth and last-disc adapter; resolve the adverse service-capacity failures.',
              '4. Verify annular-disc/core-shear and carrier modes/thermal motion with FEA and metrology; qualify assembly clearances.',
              '5. Only after review, implement a separate DD4hep prototype and run overlaps, masses, directional material scans and material-aware tracking.', '',
              '## Drawings','',
              '- [Common disc, front and rear](disc-xy.svg)',
              '- [Stagger and local support section](sections.svg)',
              '- [Cooling/cable routing concept](routing.svg)',
              '- [Nine-disc carrier and mounting rails](carrier.svg)',
              '- [Thermal/material diagnostics](diagnostics.svg)', '',
              'All are original nODD drawings generated from the same input file. Dashed service paths are routing concepts, not validated fabrication centrelines.']
    return '\n'.join(lines)+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'docs/validation/DES-014-pixel-endcap-support')
    args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
    cfg,layout,base=load_inputs();g=run_geometry(layout,cfg);bb,tiles,feet=proposal(template(layout),cfg)
    report=dict(status='DRAFT / PROTOTYPE design; thermal stress FAIL; no baseline adoption',geometry=g,
                thermal=thermal_screen(cfg,base,g['rows'],bb),materials_mechanics=inventory(cfg,base,g['rows'],bb),
                services=services(cfg,layout,g['rows']))
    paths=[Path(__file__).parent/p for p in ['inputs.json','model.py','thermal.py','budget.py','report.py','drawings.py']]
    paths += [ROOT/cfg[p] for p in ['baseline','inherited_materials','service_inputs','barrel_services']]
    report['provenance']=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                              dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),
                              generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                              python=platform.python_version(),numpy=np.__version__,
                              hashes={str(p.relative_to(ROOT)):digest(p) for p in paths},
                              command=shlex.join(['python3','-B',*sys.argv]),
                              matplotlib_config=os.environ.get('MPLCONFIGDIR'),
                              random_seed=None,numerical_overlap_tolerance_mm=cfg['numerical_overlap_tolerance_mm'])
    with (out/'proposed-module-placements.csv').open('w') as f:
        w=csv.writer(f,lineterminator="\n");w.writerow(['module_id','layer','row','col','unchanged_x_mm','unchanged_y_mm','baseline_z_mm','proposed_z_mm','proposed_mount_face_outward_sign','status'])
        for disc in g['discs']:
            src=[b for b in layout['bodies'] if b['layer_id']==disc['layer']]
            new=proposal(src,cfg)[0]
            for a,b in zip(src,new):
                w.writerow([a['module_id'],a['layer_id'],a['row'],a['col'],*a['center_mm'][:2],a['center_mm'][2],disc['proposed_z_mm']+disc['side']*b['center_mm'][2],b['mount_face'],'PROPOSED NOT ADOPTED'])
    from drawings import render
    render(out,cfg,report,bb,tiles,feet)
    import matplotlib
    report['provenance']['matplotlib']=matplotlib.__version__
    (out/'screening.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    (out/'results.md').write_text(results_text(report))
    artifacts={p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file() and p.name!='artifacts.json'}
    (out/'artifacts.json').write_text(json.dumps(dict(producer=report['provenance'],files=artifacts),indent=2)+'\n')
    print(json.dumps(dict(geometry_overlaps=sum(x['overlaps'] for x in g['comparisons'].values()),
                         thermal_stress_passes=sum(v['stress_target_pass'] for v in report['thermal']['variants']),
                         thermal_cases=len(report['thermal']['variants']),passive_mass_g=report['materials_mechanics']['disc_passive_mass_g'],
                         output=str(out)),indent=2))

if __name__=='__main__':main()
