#!/usr/bin/env python3
"""DES-020 isolated barrel: deterministic geometry and engineering ledgers (mm)."""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
INPUT = Path(__file__).with_name("inputs.json")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path=INPUT):
    c = json.loads(Path(path).read_text())
    if c["schema_version"] != 1:
        raise ValueError("Unsupported schema")
    for key, value in c.items():
        values = value if isinstance(value, list) else [value]
        if any(isinstance(x, (int, float)) and not math.isfinite(x) for x in values):
            raise ValueError("Nonfinite input: " + key)
    for key,value in c.items():
        if key in ("bearing_z_mm","tube_w_mm","coolant_C","sensor_limit_C","input_sha256","status","system_id"):
            continue
        values=value if isinstance(value,list) else [value]
        if any(isinstance(x,(int,float)) and x<=0 for x in values):
            raise ValueError("Nonpositive input: "+key)
    for key in ("rows", "sectors", "modules_per_harness", "loops_per_manifold"):
        if type(c[key]) is not int or c[key] <= 0:
            raise ValueError("Positive integer required: " + key)
    if c["rows"] % 2 or c["rows"] < 4 or c["rows"] > 32:
        raise ValueError("Rows must be even, >=4 and fit the ID")
    for key in ("active_mm", "cell_mm", "nominal_radii_mm", "pickup_mm"):
        if any(v <= 0 for v in c[key]):
            raise ValueError("Positive dimensions required: " + key)
    if not 0 < c["phi_fraction"] <= 1 or not 0 < c["packing_fraction"] <= 1:
        raise ValueError("Invalid packing fractions")
    if not 0 < 2*c["tube_wall_mm"] < c["tube_OD_mm"]:
        raise ValueError("Tube wall must leave a coolant bore")
    if type(c["system_id"]) is not int or not 0 <= c["system_id"] < 32:
        raise ValueError("System ID overflow")
    # This first factory fixes the module stack; do not silently apply different
    # footprints to the hard sensor/guard/ASIC and passive-layer contracts.
    for key,value in dict(active_mm=[48,96,.2],guard_mm=.5,stave_width_mm=52,
            stave_half_length_mm=1210,pickup_mm=[20,64],power_bus_width_mm=12,
            power_bus_copper_mm=.2,power_bus_pi_mm=.15,tube_offset_u_mm=12,tube_w_mm=-4.05).items():
        if c[key]!=value:raise ValueError("Unsupported fixture change: "+key)
    if c['cell_mm'] != [.075,.5]:raise ValueError("Keep the agreed strixel readout contract")
    for key in ('collector_mm','trunk_mm'):
        a,b,zlo,zhi=c[key]
        if not (0<a<b and 0<zlo<zhi):raise ValueError('Invalid service bounds')
    if c['collector_mm'][3]!=c['trunk_mm'][2]:raise ValueError('Disconnected collector/trunk boundary')
    if c['loop_start_mm']<=c['tube_offset_u_mm']+c['tube_OD_mm']/2:
        raise ValueError('Central cooling loops intersect')
    if any(a>=b for a,b in zip(c['trunk_pipe_ID_mm'],c['trunk_pipe_OD_mm'])):
        raise ValueError('Cooling trunks need a positive wall')
    for path, digest in c["input_sha256"].items():
        if sha(ROOT/path) != digest:
            raise ValueError("Pinned input changed: " + path)
    return c


def frame(phi, r, xyz):
    u, v, w = xyz
    return [r*math.cos(phi)-u*math.sin(phi)+w*math.cos(phi),
            r*math.sin(phi)+u*math.cos(phi)+w*math.sin(phi), v]


def build(c):
    """A straight column is a real stave; candidate-local IDs never reuse old IDs."""
    pitch = (2*c["active_half_length_mm"]-c["active_mm"][1])/(c["rows"]-1)
    body_v = c["active_mm"][1]+2*c["guard_mm"]+6
    if c["pickup_mm"][1]+body_v >= 2*pitch:
        raise ValueError("Thermal pickup intersects neighbouring module envelope")
    if c["row_lift_mm"] < 1.2 or c["lane_step_mm"] <= c["row_lift_mm"]+9:
        raise ValueError("Lane separation cannot clear complete support/module depth")
    staves, modules, routes = [], [], []
    sector_counts = Counter()
    layers = []
    for layer, r in enumerate(c["nominal_radii_mm"]):
        outer = r+c["lane_step_mm"]+c["row_lift_mm"]
        angle = 2*math.atan((c["active_mm"][0]-c["phi_margin_mm"])/(2*outer))
        n = 2*math.ceil(math.pi/angle)
        if n > 128:
            raise ValueError("Stave ID overflow")
        layers.append(dict(layer=layer, nominal_radius_mm=r, staves=n,
                           module_radius_mm=[r, outer], modules=n*c["rows"]))
        for stave in range(n):
            phi = 2*math.pi*stave/n
            radius = r+(stave%2)*c["lane_step_mm"]
            sector = min(c["sectors"]-1, int(stave*c["sectors"]/n))
            name = f"L{layer}_S{stave}"
            staves.append(dict(name=name, layer=layer, stave=stave, phi_rad=phi,
                               radius_mm=radius, sector=sector))
            for row in range(c["rows"]):
                z = (row-(c["rows"]-1)/2)*pitch
                lift = (row%2)*c["row_lift_mm"]
                center = frame(phi, radius, [0,z,lift])
                mid = f"{name}_M{row}"
                modules.append(dict(name=mid, layer=layer, stave=stave, row=row,
                    phi_rad=phi, radius_mm=radius+lift, center_mm=center,
                    u=[-math.sin(phi),math.cos(phi),0], v=[0,0,1],
                    n=[math.cos(phi),math.sin(phi),0], lift_mm=lift,
                    half_u_mm=c["active_mm"][0]/2, half_v_mm=c["active_mm"][1]/2,
                    id=len(modules), module_id=len(modules), sensor_id=len(modules),
                    layer_id=layer, station_id=layer))
            for side in (-1,1):
                members = [f"{name}_M{i}" for i in range(c["rows"])
                           if (i<c["rows"]//2)==(side<0)]
                harnesses = math.ceil(len(members)/c["modules_per_harness"])
                sector_counts[sector] += (side==1)
                routes.append(dict(id=f"{name}_{'P' if side>0 else 'N'}",
                    side=side, layer=layer, stave=stave, sector=sector, modules=members,
                    harnesses=harnesses, cooling_loops=1,
                    graph=["module flex", "half-stave bus/loop", "end board",
                           "sector collector/manifold", "longitudinal trunk", "downstream handoff"],
                    waypoints_rz_mm=[[radius,side*1210],[radius,side*1230],
                                     [radius,side*1260],[750,side*1260],
                                     [750,side*c['trunk_mm'][2]],[750,side*c['trunk_mm'][3]]]))
    return dict(layers=layers, staves=staves, modules=modules, routes=routes,
                row_pitch_mm=pitch, body_v_mm=body_v,
                sectors=[dict(sector=i, loops=sector_counts[i],
                    manifolds=math.ceil(sector_counts[i]/c["loops_per_manifold"]))
                    for i in range(c["sectors"])])


def screen(c, layout):
    count=len(layout["modules"])
    channels=round(c["active_mm"][0]/c["cell_mm"][0])*round(c["active_mm"][1]/c["cell_mm"][1])
    harnesses=sum(x["harnesses"] for x in layout["routes"] if x["side"]==1)
    manifolds=sum(x["manifolds"] for x in layout["sectors"])
    cable_area=math.pi/4*(c["power_cable_OD_mm"]**2+c["fibre_cable_OD_mm"]**2)
    pipe_area=math.pi/4*sum(x*x for x in c["trunk_pipe_OD_mm"])
    rin,rout,_,_=c["trunk_mm"]
    packing=[]
    for name,phi,pack,spare,scale in (("reference",.75,.5,1,1),
            ("conservative",.5,.4,1.25,1), ("channel_scaled_cables",.75,.5,1,channels/30208)):
        hs=[math.ceil(sum(r["harnesses"] for r in layout["routes"]
                if r["side"]==1 and r["sector"]==i)*scale) for i in range(c["sectors"])]
        cap=phi*math.pi*(rout*rout-rin*rin)*pack/c["sectors"]
        demands=[spare*(h*cable_area+s["manifolds"]*pipe_area) for h,s in zip(hs,layout["sectors"])]
        packing.append(dict(scenario=name,harnesses=sum(hs),per_sector_demand_mm2=demands,
            per_sector_capacity_mm2=cap,maximum_fill_ratio=max(demands)/cap,
            passed=max(demands)<=cap,scope="barrel only; endcap demand excluded"))
    scenarios=[]
    taps=[(m["center_mm"][2],m["lift_mm"]) for m in layout["modules"]
          if m["layer"]==0 and m["stave"]==0 and m["center_mm"][2]>0]
    busarea=c["power_bus_width_mm"]*c["power_bus_copper_mm"]
    # Exact discrete uniformly spaced load: integrate resistance segment currents.
    for name,p in (("CMS_PS_comparator",7.8),("channel_scaled_proxy",7.8*channels/30208)):
        q=p+c["leakage_W_module"]
        # Leakage is an HV comparator, not an additional LV bus current.
        current=p/c["supply_V"]
        last=1210.0
        drop=loss=0.0
        for k,(z,_) in enumerate(sorted(taps,reverse=True)):
            rr=2*c["resistivity_ohm_mm2_m"]*(last-z)/1000/busarea
            segment_current=(len(taps)-k)*current
            drop+=rr*segment_current
            loss+=rr*segment_current**2
            last=z
        # SB-C10 conservative one-dimensional heat path, including spreading.
        area=c["pickup_mm"][0]*c["pickup_mm"][1]*2*1e-6
        baseR=(.0002/(.5*area)+.000025/(.12*area)+.0002/(1*area)+.005/(20*area)
               +.006/(400*.0002*.064*2)+c["contact_R_K_W"])
        for lift in (0,c["row_lift_mm"]):
            R=baseR+(lift+.4)/1000/(100*area)
            for coolant in c["coolant_C"]:
                temp=coolant+q*R
                scenarios.append(dict(load=name,module_W=q,lift_mm=lift,coolant_C=coolant,
                    thermal_R_K_W=R,sensor_C=temp,thermal_passed=temp<=c["sensor_limit_C"],
                    half_stave_W=q*len(taps)+c["end_board_W"]+loss,
                    round_trip_drop_V=drop,return_drop_V=drop/2,bus_loss_W=loss,
                    electrical_passed=drop<1 and drop/2<.2,
                    flow=[dict(g_s=g,heat_capacity_W=g*c["latent_J_g"]*c["quality_rise"],
                        passed=q*len(taps)+c["end_board_W"]+loss<=g*c["latent_J_g"]*c["quality_rise"])
                        for g in c["flow_g_s"]]))
    turns=[]
    available=c["collector_mm"][3]-c["collector_mm"][2]
    for bend in c["bend_radius_mm"]:
        for name,od in (("power",c["power_cable_OD_mm"]),("return",12)):
            needed=max(bend+od/2,c["connector_reserve_mm"])
            turns.append(dict(component=name,bend_mm=bend,required_mm=needed,
                              available_mm=available,passed=needed<=available))
    data=[]
    for rate in (1e6,40e6):
        for occupancy in (1e-5,1e-4,1e-3):
            payload_Gbps=channels*(c['rows']//2)*occupancy*rate*32*1.2/1e9
            links=math.ceil(payload_Gbps/8.96)
            data.append(dict(accepted_events_s=rate,cell_occupancy=occupancy,
                bits_per_hit=32,packet_margin=1.2,half_stave_payload_Gbps=payload_Gbps,
                usable_Gbps_link=8.96,required_uplinks=links,
                ATLAS_two_uplink_comparator_passed=links<=2,
                qualified_fibres_per_3p6mm_cable=None))
    return dict(status="SCREEN; engineering acceptance separate",layers=layout["layers"],
        modules=count,staves=len(layout["staves"]),channels_per_module=channels,
        channels=count*channels,active_area_m2=count*48*96/1e6,
        physical_sensor_area_m2=count*49*97/1e6,row_pitch_mm=layout["row_pitch_mm"],
        pickup_neighbour_clearance_mm=layout["row_pitch_mm"]-(layout["body_v_mm"]+c["pickup_mm"][1])/2,
        loops_per_end=len(layout["staves"]),harnesses_per_end=harnesses,manifolds_per_end=manifolds,
        packing=packing,thermal_electrical_flow=scenarios,turns=turns,data_link_sensitivity=data,
        limitations=["No ASIC compatibility or electronics power/bandwidth qualification.",
            "Enthalpy balance omits two-phase pressure drop and dry-out.",
            "Thermal paths use screening conductivities, no FEA or contact qualification.",
            "Collector/trunk transport cells are not bends, fittings or installation clearance.",
            "No endcap budget or full-detector integration claim."])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,default=INPUT)
    p.add_argument("--output",type=Path,default=ROOT/"build/short-strip-barrel")
    args=p.parse_args()
    c=load(args.input); layout=build(c); result=screen(c,layout)
    args.output.mkdir(parents=True,exist_ok=True)
    result["execution"]=dict(commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        dirty=bool(subprocess.check_output(["git","status","--porcelain"],cwd=ROOT,text=True).strip()),
        input_sha256=sha(args.input),producer_sha256=sha(__file__),command=["model.py",*__import__('sys').argv[1:]])
    (args.output/"screening.json").write_text(json.dumps(result,indent=2)+"\n")
    with gzip.GzipFile(filename=str(args.output/"layout.json.gz"),mode="wb",mtime=0) as f:
        f.write(json.dumps(layout,separators=(",",":")).encode())
    print(f"{result['modules']} modules; {result['staves']} staves; {result['channels']} channels")


if __name__=="__main__":main()
