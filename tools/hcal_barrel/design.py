"""DES037 analytical barrel assembly. All dimensional inputs are mm.

Reuses the unchanged DES036 material/physical unit with no reference absorber.
Core-plane masks describe geometry at local z=2mm, not finite-solid transport.
"""
import argparse
from collections import Counter, defaultdict
import copy
from functools import lru_cache
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CONFIG = Path(__file__).with_name("config.json")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def common_unit():
    path = ROOT / "tools/hcal_readout/readout.py"
    spec = importlib.util.spec_from_file_location("des037_common_readout", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result, _ = module.build(absorber=False)
    reference=json.loads((ROOT/"docs/validation/DES-036/budgets.json").read_text())
    if any(reference["source_sha256"].get(k) != v for k,v in result["source_sha256"].items()):
        raise ValueError("DES036 working module source changed; explicit amendment required")
    return result


def determinant(m):
    return sum(m[0][i] * (m[1][(i+1) % 3] * m[2][(i+2) % 3] -
                          m[1][(i+2) % 3] * m[2][(i+1) % 3]) for i in range(3))


def frame(phi):
    return [[-math.sin(phi), math.cos(phi), 0], [0, 0, 1],
            [math.cos(phi), math.sin(phi), 0]]


def transform(origin, basis, point):
    return [origin[i] + sum(basis[j][i] * point[j] for j in range(3)) for i in range(3)]


def water_ports(placement, common):
    return [dict(name=p["name"], flow_role=p["flow_role"],
                 centre_mm=transform(placement["origin_mm"],placement["frame"],p["centre_mm"]),
                 direction=transform([0,0,0],placement["frame"],p["direction"]))
            for p in common["cooling_handoffs"]]


def encode(sector, layer, carrier, module=0, sensor=0):
    for value, bound in ((sector, 16), (layer, 64), (carrier, 4096), (module, 2), (sensor, 36)):
        if type(value) is not int or not 0 <= value < bound:
            raise ValueError("identifier capacity")
    return 9 | sector << 10 | layer << 14 | carrier << 20 | module << 32 | sensor << 34


def wedge_area(a, b, tangent, inset):
    return tangent * (b*b - a*a) - 2 * inset * (b-a)


def build(config=None):
    c = copy.deepcopy(config if config is not None else json.loads(CONFIG.read_text()))
    unit = common_unit()
    ca = unit["config"]["carrier"]
    w, h, depth = ca["size_mm"]
    for key, value in c.items():
        if isinstance(value, (float, int)) and (not math.isfinite(value) or value <= 0):
            raise ValueError("positive finite configuration " + key)
    if c["sectors"] != 16 or c["layers"] != 36 or c["axial_rows"] % 2 != 1:
        raise ValueError("declared sector/layer/odd-row contract")
    if c["collision_energy_TeV"] != 14:
        raise ValueError("human collision-energy contract")
    pitch = c["steel_mm"] + depth + c["installation_gap_mm"]
    stack = c["layers"] * pitch
    outer = c["inner_apothem_mm"] + stack + c["back_cover_mm"]
    if abs(outer - c["proposed_outer_apothem_mm"]) > 1e-8:
        raise ValueError("depth/envelope closure: do not compress common hardware")
    if c["row_collector_gap_mm"] < 20 or c["edge_rail_mm"] < 20:
        raise ValueError("declared collector/structural allocation")
    if len(c["tangent_phases_mm"]) != len(c["axial_phases_mm"]) or not c["tangent_phases_mm"]:
        raise ValueError("layer phase cycle")
    if any(not math.isfinite(v) for key in ("tangent_phases_mm","axial_phases_mm") for v in c[key]):
        raise ValueError("nonfinite phase")
    tangent = math.tan(math.pi / c["sectors"])
    usable_z = c["half_length_mm"] - c["end_flange_mm"]
    row_step = h + c["row_collector_gap_mm"]
    row_centres = [(i - (c["axial_rows"]-1)/2) * row_step for i in range(c["axial_rows"])]
    layers, placements = [], []
    for layer in range(c["layers"]):
        steel_front = c["inner_apothem_mm"] + layer * pitch
        carrier_front = steel_front + c["steel_mm"]
        half_span = carrier_front * tangent - c["sector_half_seam_mm"] - c["edge_rail_mm"]
        cols = math.floor((2 * half_span + c["tangent_gap_mm"]) / (w + c["tangent_gap_mm"]))
        xs = [(j - (cols-1)/2) * (w + c["tangent_gap_mm"]) for j in range(cols)]
        requested_tx = c["tangent_phases_mm"][layer % len(c["tangent_phases_mm"])]
        margin = half_span - max(abs(x)+w/2 for x in xs)
        # Explicitly bound the phase to the remaining width, retaining the same
        # maximal centred count for every phase/control. No carriers disappear.
        tx = math.copysign(min(abs(requested_tx), max(0,margin-c["phase_edge_clearance_mm"])), requested_tx)
        ay = c["axial_phases_mm"][layer % len(c["axial_phases_mm"])]
        # Preserve row/column count across a phase cycle; drop no hidden edge cells.
        if max(abs(x + tx) + w/2 for x in xs) > half_span + 1e-8:
            raise ValueError("tangent phase exceeds narrow-face carrier fit")
        for offset in (ay, c["adverse_aligned_axial_mm"]):
            if max(abs(y + offset) + h/2 for y in row_centres) > usable_z + 1e-8:
                raise ValueError("axial phase exceeds end-flange clearance")
        layers.append(dict(layer=layer, steel_front_mm=steel_front, carrier_front_mm=carrier_front,
                           columns_mm=xs, rows_mm=row_centres, tangent_phase_mm=tx, axial_phase_mm=ay,
                           requested_tangent_phase_mm=requested_tx, centred_edge_margin_mm=margin,
                           carrier_count_per_sector=cols * len(row_centres),
                           packable_core_face_fraction=cols * len(row_centres) * 72 * 29.7**2 /
                           (4 * half_span * usable_z),
                           core_face_fraction=cols * len(row_centres) * 72 * 29.7**2 /
                           (2 * carrier_front * tangent * 2 * c["half_length_mm"])))
        for sector in range(c["sectors"]):
            phi = sector * 2 * math.pi / c["sectors"]
            basis = frame(phi)
            for row, y in enumerate(row_centres):
                for col, x in enumerate(xs):
                    cid = row * cols + col
                    origin = transform([0, 0, 0], basis, [x + tx, y + ay, carrier_front])
                    placements.append(dict(side=0, sector=sector, layer=layer, carrier=cid,
                                           row=row, column=col, origin_mm=origin, frame=basis,
                                           local_xy_mm=[x + tx, y + ay], parent_id=encode(sector, layer, cid)))
    count = len(placements)
    density = {k: v["density_g_cm3"] for k, v in unit["materials"].items()}
    volumes = Counter()
    for layer in layers:
        a = layer["steel_front_mm"]
        volumes["Steel235"] += c["sectors"] * wedge_area(a, a+c["steel_mm"], tangent,
            c["sector_half_seam_mm"]+c["edge_rail_mm"]) * 2 * usable_z
    sampling_outer = c["inner_apothem_mm"] + stack
    # Rails, flange and cover occupy disjoint strips in radial/axial coordinates.
    rails = c["sectors"] * 2 * c["edge_rail_mm"] * stack * 2 * usable_z
    cover = c["sectors"] * wedge_area(sampling_outer, outer, tangent,
                                     c["sector_half_seam_mm"]) * 2 * usable_z
    flanges = c["sectors"] * wedge_area(c["inner_apothem_mm"], outer, tangent,
                                       c["sector_half_seam_mm"]) * 2 * c["end_flange_mm"]
    volumes["Aluminium"] += rails + cover + flanges
    structural = {k: dict(volume_mm3=v, mass_g=v*density[k]/1000) for k, v in volumes.items()}
    totals = {k: dict(volume_mm3=v["volume_mm3"]*count, mass_g=v["mass_g"]*count)
              for k, v in unit["material_totals"].items()}
    for key, value in structural.items():
        row = totals.setdefault(key, dict(volume_mm3=0, mass_g=0))
        for quantity in row:
            row[quantity] += value[quantity]
    power = [dict(current_A_per_device=p["current_A_per_device"], total_heat_W=count*p["total_heat_W"],
                  ideal_water_kg_s=count*p["ideal_water_g_s"]/1000,
                  LV_input_A_at_12V=count*p["LV_input_A"], bias_current_A=count*p["bias_current_A"])
             for p in unit["budgets"]["power_scenarios"]]
    daq = [dict(accepted_Hz=p["accepted_Hz"], summed_chip_payload_capacity_bps=count*p["carrier_payload_capacity_bps"],
                summed_chip_demand_bps=count*p["carrier_demand_bps"], utilization=p["utilization"], status=p["status"],
                qualification="sum of local chip allocations; no qualified carrier/sector egress or queue")
           for p in unit["budgets"]["daq"]]
    corner = outer / math.cos(math.pi/c["sectors"])
    paths = [Path(__file__), CONFIG, ROOT / "docs/design/DES-037-hcal-barrel-common-module.md"]
    data = dict(status="DRAFT / PROTOTYPE", scope="Analytical barrel layout/material/service budgets and physical core-plane masks; no native assembly, response or engineering qualification",
                config=c, common=dict(source_sha256=unit["source_sha256"], config=unit["config"],
                                      mass_g=unit["carrier_and_modules_mass_g"], material_totals=unit["material_totals"],
                                      budgets=unit["budgets"], cooling_handoffs=unit["services"]["cooling_handoffs"]),
                layers=layers, placements=placements, material_totals=totals, structure_material_totals=structural,
                summary=dict(carriers=count, boards=2*count, tiles=72*count, powered_channels=156*count,
                             unused_ordinary_channels=72*count, auxiliary_channels=12*count,
                             material_mass_g=sum(v["mass_g"] for v in totals.values()),
                             carrier_material_mass_g=count*unit["carrier_and_modules_mass_g"],
                             structural_mass_g=sum(v["mass_g"] for v in structural.values()),
                             sampling_depth_mm=stack, total_depth_mm=stack+c["back_cover_mm"],
                             depth_amendment_mm=stack+c["back_cover_mm"]-c["old_depth_mm"],
                             outer_apothem_mm=outer, corner_radius_mm=corner,
                             ecal_egress_extra_clearance_mm=c["egress_radius_mm"]-corner-c["egress_jacket_radius_mm"]-c["egress_clearance_mm"],
                             min_core_face_fraction=min(p["core_face_fraction"] for p in layers),
                             max_core_face_fraction=max(p["core_face_fraction"] for p in layers)),
                services=dict(cooling_endpoints=4*count, cooling_branches=2*count,
                              local_LV_bias_data_control_connector_envelopes=4*count,
                              DAQ_lanes=4*count, trigger_lanes=8*count,
                              sector_end_handoffs=2*c["sectors"],
                              power_scenarios=power, daq=daq,
                              implementation="20mm row strips are empty reservations; endpoints stop at local/sector interface. Collectors, frame penetrations, cabling, pressure drop and plant are unimplemented and excluded from mass"),
                excluded=["external collectors and cable/plant material", "additional concentrator/regulator losses", "fasteners, bearings, mounting and lifting hardware", "combined field/load/thermal model", "whole-assembly DD4hep/Geant4 and finite-solid tile/recess navigation"],
                source_sha256={str(p.relative_to(ROOT)):sha(p) for p in paths} | unit["source_sha256"])
    validate(data)
    data["services"]["transformed_port_examples"]=[dict(parent_id=p["parent_id"],
        ports=water_ports(p,data["common"])) for p in (placements[0],placements[-1])]
    data["services"]["transform_rule"]="Every local DES036 port is mapped by the recorded carrier origin and row-basis frame. Examples shown; no installed collector connection."
    return data


def validate(data):
    c, layers = data["config"], data["layers"]
    if any(sha(ROOT/path) != value for path,value in data["source_sha256"].items()):
        raise ValueError("source identity changed")
    w, h, depth = data["common"]["config"]["carrier"]["size_mm"]
    seen = set()
    tangent = math.tan(math.pi/c["sectors"])
    for p in data["placements"]:
        if p["parent_id"] != encode(p["sector"], p["layer"], p["carrier"]):
            raise ValueError("corrupt encoded identifier")
        if p["parent_id"] in seen:
            raise ValueError("duplicate carrier identifier")
        seen.add(p["parent_id"])
        basis = p["frame"]
        if abs(determinant(basis)-1) > 1e-10:
            raise ValueError("improper frame")
        for i in range(3):
            for j in range(3):
                if abs(sum(a*b for a,b in zip(basis[i],basis[j])) - (i==j)) > 1e-10:
                    raise ValueError("nonorthogonal frame")
        expected = frame(p["sector"]*2*math.pi/c["sectors"])
        if max(abs(basis[i][j]-expected[i][j]) for i in range(3) for j in range(3)) > 1e-10:
            raise ValueError("wrong carrier orientation")
        x, y = p["local_xy_mm"]
        layer = layers[p["layer"]]
        r = layer["carrier_front_mm"]
        if (not 0 <= p["column"] < len(layer["columns_mm"]) or not 0 <= p["row"] < len(layer["rows_mm"]) or
                p["carrier"] != p["row"]*len(layer["columns_mm"])+p["column"]):
            raise ValueError("row/column/identifier ownership")
        if abs(x-layer["columns_mm"][p["column"]]-layer["tangent_phase_mm"])>1e-8 or abs(y-layer["rows_mm"][p["row"]]-layer["axial_phase_mm"])>1e-8:
            raise ValueError("placement differs from declared phase grid")
        expected_origin = transform([0,0,0], basis, [x,y,r])
        if max(abs(a-b) for a,b in zip(expected_origin,p["origin_mm"])) > 1e-7:
            raise ValueError("wrong global placement")
        for dx in (-w/2,w/2):
            for dy in (-h/2,h/2):
                for dz in (0,depth):
                    if abs(x+dx) > (r+dz)*tangent-c["edge_rail_mm"]-c["sector_half_seam_mm"]+1e-7:
                        raise ValueError("carrier corner outside sector")
                    if abs(y+dy) > c["half_length_mm"]-c["end_flange_mm"]+1e-7:
                        raise ValueError("carrier inside end flange")
    count = len(seen)
    s = data["summary"]
    if s["carriers"] != count or s["tiles"] != 72*count or s["powered_channels"] != 156*count:
        raise ValueError("carrier/physical/powered channel accounting")
    if not math.isclose(s["material_mass_g"],s["carrier_material_mass_g"]+s["structural_mass_g"],abs_tol=1e-5):
        raise ValueError("absorber/structure mass ownership")
    if not math.isclose(sum(v["mass_g"] for v in data["material_totals"].values()),s["material_mass_g"],abs_tol=1e-5):
        raise ValueError("material total conservation")
    if any(not math.isfinite(v["mass_g"]) or v["mass_g"] <= 0 for v in data["material_totals"].values()):
        raise ValueError("invalid material inventory")
    return True


def core(x, y, module_config):
    """Exact physical core rectangle at local z=2; no optical/finite-solid claim."""
    m = module_config["module"]
    pitch, n = m["tile_pitch_mm"], m["rows"]
    for cx, cy in module_config["carrier"]["board_centres_xy_mm"]:
        ix = math.floor((x-cx)/pitch + n/2)
        iy = math.floor((y-cy)/pitch + n/2)
        if 0 <= ix < n and 0 <= iy < n:
            tx, ty = cx+(ix-(n-1)/2)*pitch, cy+(iy-(n-1)/2)*pitch
            if abs(x-tx) <= m["tile_size_mm"][0]/2 and abs(y-ty) <= m["tile_size_mm"][1]/2:
                return True
    return False


def ray(data, eta, phi, scenario="staggered"):
    c = data["config"]
    sector_angle = 2*math.pi/c["sectors"]
    sector = math.floor(phi/sector_angle + .5) % c["sectors"]
    delta = (phi-sector*sector_angle+math.pi) % (2*math.pi)-math.pi
    co, si, sh = math.cos(delta), math.sin(delta), math.sinh(eta)
    w,h,_ = data["common"]["config"]["carrier"]["size_mm"]
    step_x, step_y = w+c["tangent_gap_mm"], h+c["row_collector_gap_mm"]
    active, steel_path = [], 0.0
    usable_z = c["half_length_mm"]-c["end_flange_mm"]
    edge_factor = co*math.tan(math.pi/c["sectors"])-abs(si)
    for layer in data["layers"]:
        a = layer["steel_front_mm"]
        lo, hi = a/co, (a+c["steel_mm"])/co
        if sh:
            hi = min(hi, usable_z/abs(sh))
        if edge_factor <= 1e-14:
            hi = -1
        else:
            lo = max(lo,(c["edge_rail_mm"]+c["sector_half_seam_mm"])/edge_factor)
        steel_path += max(0,hi-lo)*math.cosh(eta)
        t = (layer["carrier_front_mm"]+2)/co
        px, py = t*si, t*sh
        tx, ay = layer["tangent_phase_mm"],layer["axial_phase_mm"]
        if scenario == "aligned_midplane_gap":
            tx,ay = 0,c["adverse_aligned_axial_mm"]
        elif scenario == "aligned_zero":
            tx,ay = 0,0
        elif scenario != "staggered":
            raise ValueError("unknown phase scenario")
        col = math.floor((px-tx-layer["columns_mm"][0])/step_x+.5)
        row = math.floor((py-ay-layer["rows_mm"][0])/step_y+.5)
        hit = False
        if 0 <= col < len(layer["columns_mm"]) and 0 <= row < len(layer["rows_mm"]):
            lx,ly=px-tx-layer["columns_mm"][col],py-ay-layer["rows_mm"][row]
            if abs(lx) <= w/2 and abs(ly) <= h/2:
                hit = core(lx,ly,data["common"]["config"])
        active.append(hit)
    indices=[i for i,v in enumerate(active) if v]
    return dict(active_planes=sum(active), layers=indices, first_plane=min(indices) if indices else None,
                last_plane=max(indices) if indices else None, steel_path_mm=steel_path)


def coverage(data):
    c=data["config"];sc=c["sampling"]
    phis=[2*math.pi*i/sc["phi_bins"] for i in range(sc["phi_bins"])]
    seam_phis=[(i+.5)*2*math.pi/c["sectors"] for i in range(c["sectors"])]
    rows=[]
    for scenario in ("staggered","aligned_zero","aligned_midplane_gap"):
        for i in range(-round(sc["eta_max"]/sc["eta_step"]),round(sc["eta_max"]/sc["eta_step"])+1):
            eta=round(i*sc["eta_step"],8)
            samples=[ray(data,eta,phi,scenario) for phi in phis]
            counts=sorted(s["active_planes"] for s in samples)
            paths=[s["steel_path_mm"] for s in samples]
            rows.append(dict(scenario=scenario,eta=eta,minimum=min(counts),mean=sum(counts)/len(counts),
                             maximum=max(counts),p10=counts[int(.1*(len(counts)-1))],
                             median=counts[len(counts)//2],zero_fraction=counts.count(0)/len(counts),
                             first_active_plane_min=min((s["first_plane"] for s in samples if s["first_plane"] is not None),default=None),
                             last_active_plane_max=max((s["last_plane"] for s in samples if s["last_plane"] is not None),default=None),
                             mean_steel_path_mm=sum(paths)/len(paths),sampled_counts=[s["active_planes"] for s in samples]))
    return dict(scope="IP core-plane samples at localz2mm; actual 29.7mm rectangles; steel-only analytic paths. No full-solid/recess/optical/response/containment claim",
                phi_rad=phis,rows=rows,
                statistics="720 uniform phi probes per eta/scenario; exact boundary probes are separate and do not reweight these statistics",
                seam_probes=[dict(eta=e,phi_rad=p,**ray(data,e,p)) for e in (0,.5,1,1.2) for p in seam_phis])


def export(directory):
    data=build();out=Path(directory);out.mkdir(parents=True,exist_ok=True)
    layout=out/"layout.json"
    layout.write_text(json.dumps(dict(layers=data["layers"],placements=data["placements"]),separators=(",",":"))+"\n")
    masks=coverage(data)
    (out/"coverage.json").write_text(json.dumps(masks,indent=2)+"\n")
    report={k:v for k,v in data.items() if k != "placements"}
    report["execution"]=dict(commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
                             dirty=bool(subprocess.check_output(["git","status","--porcelain"],cwd=ROOT,text=True)))
    report["exports_sha256"]={p.name:sha(p) for p in (layout,out/"coverage.json")}
    (out/"summary.json").write_text(json.dumps(report,indent=2)+"\n")
    print("DES037 PROTOTYPE",data["summary"]["carriers"],"carriers;",data["summary"]["tiles"],"tiles;",
          round(data["summary"]["material_mass_g"]/1e6,3),"tonnes;",
          round(data["services"]["power_scenarios"][0]["total_heat_W"]/1000,3),"kW")


if __name__ == "__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True)
    export(p.parse_args().output)
