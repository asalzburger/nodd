"""Si-W external service/forward envelope allocation, without detector imports."""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "tools/siw_services/inputs.json"
OUTPUT = ROOT / "docs/validation/DES-034/allocations.json"


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def study(data):
    f, c = data["source_facts"], data["choices"]
    n = c["sectors"]
    angle = math.pi / n
    corner = max(f["ecal_barrel_outer_apothem_mm"], f["ecal_endcap_outer_apothem_mm"]) / math.cos(angle)
    rmin = c["lane_centre_radius_mm"] - c["lane_radial_mm"] / 2
    rmax = math.hypot(c["lane_centre_radius_mm"] + c["lane_radial_mm"] / 2, c["lane_tangent_mm"] / 2)
    seam_clearance = rmin * math.sin(angle) - c["lane_tangent_mm"] / 2 * math.cos(angle)
    clearance = c["installation_clearance_mm"]
    require(c["service_inner_radius_mm"] >= corner + clearance, "ECAL corner clearance")
    require(rmin >= c["service_inner_radius_mm"] + clearance, "Lane inner clearance")
    require(rmax <= c["hcal_barrel_front_apothem_mm"] - clearance, "Lane HCAL clearance")
    require(seam_clearance >= clearance, "Adjacent sector lane clearance")
    require(c["barrel_stations"] == 2 * n and c["endcap_stations_each"] == n, "Station ownership")
    require(f["barrel_native_interface_role"] - 9 * 48 * n == f["barrel_powered_interfaces"], "Barrel PCB/interface distinction")
    require(f["endcap_native_interface_role_each"] - 48 * n == f["endcap_powered_interfaces_each"], "Endcap PCB/interface distinction")
    bend = c["bend_radius_OD"] * c["water_jacket_mm"]
    required_turn = bend + c["water_jacket_mm"] / 2 + clearance
    require(c["rear_axial_gap_mm"] >= required_turn, "Single-elbow rear space")
    rear = f["ecal_endcap_back_abs_z_mm"]
    hfront, houter = c["hcal_barrel_front_apothem_mm"], c["hcal_barrel_front_apothem_mm"] + f["hcal_depth_mm"]
    hendfront = rear + c["rear_axial_gap_mm"]
    hendback = hendfront + f["hcal_depth_mm"]
    hcorner = houter / math.cos(angle)
    require(c["egress_radius_mm"] - c["water_jacket_mm"] / 2 - clearance > hcorner, "Egress clears all HCAL corners")
    require(c["forward_outer_radius_mm"] + clearance / 2 <= f["hcal_endcap_inner_apothem_mm"], "Forward fits all-azimuth HCAL aperture")
    require(c["forward_inner_radius_mm"] < c["forward_outer_radius_mm"], "Forward ordering")

    def station(kind):
        barrel = kind == "barrel"
        stations = c["barrel_stations"] if barrel else c["endcap_stations_each"]
        interfaces = f["barrel_powered_interfaces"] if barrel else f["endcap_powered_interfaces_each"]
        require(interfaces % stations == 0, "Interface division")
        chips = interfaces // stations
        heat = f["barrel_heat_W"] if barrel else f["endcap_heat_W_each"]
        count = {"data": chips * c["data_pairs_per_interface"], "fibre": chips * c["fibres_per_interface"],
                 "HV": c["barrel_HV_per_station"] if barrel else c["endcap_HV_per_station"],
                 "power": c["power_conductors_per_station"], "ground": c["grounds_per_station"], "control": c["controls_per_station"]}
        diameter = dict(data=c["data_pair_OD_mm"], fibre=c["fibre_OD_mm"], HV=c["HV_OD_mm"],
                        power=c["power_OD_mm"], ground=c["ground_OD_mm"], control=c["control_OD_mm"])
        cable_area = {key: count[key] * math.pi * diameter[key]**2 / 4 for key in count}
        pipe_area = c["water_jackets_per_station"] * math.pi * c["water_jacket_mm"]**2 / 4
        nominal = (sum(cable_area.values()) + pipe_area) / c["nominal_cable_fill"]
        adverse = (sum(cable_area.values()) + pipe_area + (c["adverse_link_factor"] - 1) * (cable_area["data"] + cable_area["fibre"])) / c["adverse_cable_fill"]
        capacity = c["lane_radial_mm"] * c["lane_tangent_mm"]
        require(nominal <= capacity and adverse <= capacity, "Cable/pipe lane area")
        flow = heat / (c["water_cp_J_kg_K"] * c["water_delta_K"])
        velocity = flow / stations / (c["water_density_kg_m3"] * math.pi * (c["water_bore_mm"] / 2000)**2)
        current = heat / stations / c["power_voltage_V"]  # Heat includes source converter loss.
        resistance = c["copper_resistivity_ohm_m"] * c["power_loop_length_m"] / (c["power_parallel_conductors_each_leg"] * c["power_conductor_mm2"] * 1e-6)
        length = c["barrel_cable_length_m"] if barrel else c["endcap_cable_length_m"]
        return dict(stations=stations, powered_interfaces_per_station=chips, cable_count_per_station=count,
                    cable_length_m={key: value * stations * length for key, value in count.items()},
                    nominal_area_mm2=nominal, adverse_area_mm2=adverse, reserved_area_mm2=capacity,
                    heat_W=heat, water_flow_kg_s=flow, water_speed_m_s=velocity,
                    adverse_water_speed_m_s=velocity*c["adverse_heat_factor"], input_current_A_per_station=current,
                    power_loop_drop_V=current*resistance, power_loop_loss_W_per_station=current**2*resistance,
                    adverse_power_drop_V=current*resistance*c["adverse_heat_factor"],
                    power_copper_kg=c["power_conductors_per_station"]*stations*length*c["power_conductor_mm2"]*1e-6*c["power_copper_density_kg_m3"],
                    filled_water_kg=c["water_jackets_per_station"]*stations*length*math.pi*(c["water_bore_mm"]/2000)**2*c["water_density_kg_m3"])

    # Reserved backbone: straight axial leg, a 200 mm 90-degree elbow, radial egress.
    # Tube sweep includes jacket radius plus installation clearance. The full cable
    # lane additionally occupies the named rear gap; local cassette ports are absent.
    turn_start = rear + c["rear_axial_gap_mm"] / 2 - bend
    sweep = c["water_jacket_mm"] / 2 + clearance
    route = [(c["lane_centre_radius_mm"], z) for z in (0, f["ecal_barrel_flange_half_length_mm"], rear, turn_start)]
    route += [(c["lane_centre_radius_mm"] + bend*(1-math.cos(t)), turn_start + bend*math.sin(t)) for t in [i*math.pi/128 for i in range(65)]]
    route += [(c["egress_radius_mm"], rear+c["rear_axial_gap_mm"]/2)]
    for r, z in route:
        require(r - sweep > corner, "Backbone sweep outside ECAL")
        if z - sweep < rear:
            require(r + sweep < hfront, "Backbone avoids HCAL barrel")
        require(z + sweep < hendfront, "Backbone avoids HCAL endcap")
    barrel, endcap = station("barrel"), station("endcap")
    jmin = c["junction_centre_radius_mm"] - c["junction_radial_mm"] / 2
    jmax = math.hypot(c["junction_centre_radius_mm"] + c["junction_radial_mm"] / 2, c["junction_tangent_mm"] / 2)
    jseam = jmin * math.sin(angle) - c["junction_tangent_mm"] / 2 * math.cos(angle)
    require(jmin >= c["service_inner_radius_mm"] + clearance, "Merged lane inner clearance")
    require(jmax <= hfront - clearance and jseam >= clearance, "Merged lane corner/seam clearance")
    joint_capacity = c["junction_tangent_mm"] * c["junction_radial_mm"]
    joint_nominal = barrel["nominal_area_mm2"] + endcap["nominal_area_mm2"]
    joint_adverse = barrel["adverse_area_mm2"] + endcap["adverse_area_mm2"]
    require(joint_adverse <= joint_capacity, "Merged barrel/endcap cable packing")
    forward_front = rear + c["forward_front_clearance_mm"]
    eta4_r = [z / math.sinh(4) for z in (forward_front, hendback)]
    def polygon_volume(inner, outer, length):
        return n * math.tan(angle) * (outer**2-inner**2) * length / 1e9
    old_inner = f["previous_hcal_barrel_front_apothem_mm"]
    old_barrel = polygon_volume(old_inner, old_inner+f["hcal_depth_mm"], 2*f["previous_hcal_barrel_half_length_mm"])
    old_end = polygon_volume(f["hcal_endcap_inner_apothem_mm"], f["previous_hcal_endcap_outer_apothem_mm"], f["hcal_depth_mm"])
    new_barrel = polygon_volume(hfront, houter, 2*rear)
    new_end = polygon_volume(f["hcal_endcap_inner_apothem_mm"], houter-10, f["hcal_depth_mm"])
    return dict(status="PASS within empty-envelope/packing arithmetic scope", scope=data["scope"],
        checks=dict(ecal_corner_clearance_mm=c["service_inner_radius_mm"]-corner,
                    lane_HCAL_clearance_mm=hfront-rmax, sector_lane_clearance_mm=seam_clearance,
                    single_elbow_required_mm=required_turn, backbone_sweep_points=len(route),
                    classification="Analytic circular/polygon bounds and sampled backbone sweeps; no native detector overlap or local connection qualification."),
        geometry=dict(hcal_barrel_front_apothem_m=hfront/1000,hcal_barrel_outer_apothem_m=houter/1000,
                      hcal_barrel_half_length_m=rear/1000,hcal_endcap_front_abs_z_m=hendfront/1000,
                      hcal_endcap_back_abs_z_m=hendback/1000,hcal_endcap_outer_apothem_m=(houter-10)/1000,
                      max_HCAL_corner_radius_m=hcorner/1000,full_axial_length_m=2*hendback/1000,
                      service_inner_radius_m=c["service_inner_radius_mm"]/1000,service_outer_radius_m=hfront/1000,
                      rear_axial_gap_m=c["rear_axial_gap_mm"]/1000,egress_radius_m=c["egress_radius_mm"]/1000),
        barrel=barrel,endcap_each=endcap,total_heat_W=barrel["heat_W"]+2*endcap["heat_W"],
        merged_station_each_end=dict(nominal_area_mm2=joint_nominal,adverse_area_mm2=joint_adverse,
            reserved_area_mm2=joint_capacity,HCAL_corner_clearance_mm=hfront-jmax,seam_clearance_mm=jseam,
            interpretation="One barrel-end station plus one endcap station; four water jackets counted, no pipe sharing assumed."),
        total_water_flow_kg_s=barrel["water_flow_kg_s"]+2*endcap["water_flow_kg_s"],
        adverse_heat_W=(barrel["heat_W"]+2*endcap["heat_W"])*c["adverse_heat_factor"],
        external_power_copper_kg=barrel["power_copper_kg"]+2*endcap["power_copper_kg"],
        external_filled_water_kg=barrel["filled_water_kg"]+2*endcap["filled_water_kg"],
        external_power_loss_W=barrel["power_loop_loss_W_per_station"]*barrel["stations"]+2*endcap["power_loop_loss_W_per_station"]*endcap["stations"],
        outline_volumes_m3=dict(previous_barrel=old_barrel,previous_endcap_each=old_end,barrel=new_barrel,endcap_each=new_end),
        relative_HCAL_volume_previous_layout=(new_barrel+2*new_end)/(old_barrel+2*old_end),
        route_rz_mm=[list(point) for point in route],forward_reservation=dict(r_min_m=c["forward_inner_radius_mm"]/1000,
            r_max_m=c["forward_outer_radius_mm"]/1000,z_min_abs_m=forward_front/1000,z_max_abs_m=hendback/1000,
            eta4_envelope_r_m=[v/1000 for v in eta4_r],interpretation="Only an empty geometric reservation; no technology, containment or acceptance."))


def retained(data):
    result = study(data)
    result["input_sha256"] = hashlib.sha256(INPUT.read_bytes()).hexdigest()
    result["producer_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = retained(json.loads(INPUT.read_text()))
    if args.check:
        saved = json.loads(OUTPUT.read_text())
        if saved != result:
            def differences(old, new, path="root"):
                if isinstance(old, dict) and isinstance(new, dict):
                    for key in old:
                        yield from differences(old[key],new[key],path+"."+key)
                elif isinstance(old, list) and isinstance(new, list):
                    for index,(left,right) in enumerate(zip(old,new)):
                        yield from differences(left,right,path+"["+str(index)+"]")
                elif old != new:
                    yield path,old,new
            print("First differing fields:",list(differences(saved,result))[:8])
            raise SystemExit("Retained allocation differs from source")
        layout = json.loads((ROOT / "docs/layouts/LAYOUT-001.json").read_text())
        for key, value in layout["hcal"].items():
            if "hcal_"+key in result["geometry"]:
                require(math.isclose(value,result["geometry"]["hcal_"+key],abs_tol=1e-12),"Layout HCAL mismatch: "+key)
        for key in ("r_min_m","r_max_m","z_min_abs_m","z_max_abs_m"):
            require(layout["forward_reservations"][0][key] == result["forward_reservation"][key],"Forward layout mismatch")
        print("PASS: retained Si-W service and forward allocations reproduce")
    else:
        OUTPUT.write_text(json.dumps(result, indent=2)+"\n")
        print("Wrote", OUTPUT.relative_to(ROOT))
