"""DES019 heterogeneous inventories inside unchanged DES015 service bounds."""

import math
from export import read
from model import ROOT
from endcap_parts import volume


def transport(parts, det, mats, cfg, config, schedule, bc, side, name, discs, rings):
    tr = config["transport"]
    fractions = config["cable_volume_fractions"]
    budget = read(ROOT / cfg["service_inputs"])
    scenario = budget["scenarios"]["reference"]
    barrel = [
        s
        for s in read(ROOT / bc["service_summary"])["sectors"]
        if s["side"] == ("positive" if side > 0 else "negative")
    ]
    wall = read(ROOT / "tools/pixel_support/services.json")["transport_wall_mm"]
    cable = sum(
        sum(s["scenarios"]["reference"]["terminal_cable_footprint_mm2"].values())
        for s in barrel
    )
    ti = sum(
        2 * math.pi * ((s["pair_OD_mm"] / 2) ** 2 - (s["pair_OD_mm"] / 2 - wall) ** 2)
        for s in barrel
    )
    co2 = sum(2 * math.pi * (s["pair_OD_mm"] / 2 - wall) ** 2 for s in barrel)
    rad = cfg["cooling"]["transport_OD_mm"] / 2
    tiA = math.pi * (rad**2 - (rad - wall) ** 2)
    co2A = math.pi * (rad - wall) ** 2
    local = []
    for d in discs:
        ref = next(s for s in d["after"]["services"] if s["scenario"] == "reference")
        legs = d["after"]["cooling"]["feed_return_legs"]
        local.append(dict(cable=ref["cables_mm2"], ti=legs * tiA, co2=legs * co2A))
    cells = []
    necks = []

    def cell(label, rlo, rhi, zlo, zhi, wireV, tiV, co2V):
        angle = math.radians(tr["free_sector_width_deg"])
        cap = len(tr["free_sector_start_deg"]) * volume(
            "sector", dict(rmin=rlo, rmax=rhi, dz=zhi - zlo, angle=angle)
        )
        volumes = {k: wireV * f for k, f in fractions.items()}
        volumes.update(Titanium=tiV, CO2=co2V)
        mat = mats.effective("EC_Service_" + label, volumes, cap)
        cells.append(
            dict(
                name=label,
                radial_mm=[rlo, rhi],
                abs_z_mm=[zlo, zhi],
                cable_footprint_mm3=wireV,
                Ti_mm3=tiV,
                CO2_mm3=co2V,
                capacity_mm3=cap,
                material=mat,
            )
        )
        for k, start in enumerate(tr["free_sector_start_deg"]):
            parts.add(
                det,
                label + str(k),
                "sector",
                mat,
                "transport_services",
                center=(0, 0, side * (zlo + zhi) / 2),
                rotation=(0, 0, math.radians(start)),
                rmin=rlo,
                rmax=rhi,
                dz=zhi - zlo,
                angle=angle,
            )

    joins = [d["datum_mm"] + config["collector_w_mm"][1] for d in discs[:-1]]
    z0, z1 = cfg["mounting"]["carrier_z_mm"]
    ft = cfg["mounting"]["flange_axial_mm"]
    edges = sorted(
        [
            tr["handoff_abs_z_mm"],
            *joins,
            z0,
            z0 + ft,
            z1 - ft,
            z1,
            tr["rear_turn_abs_z_mm"][0],
        ]
    )
    for j, (a, b) in enumerate(zip(edges, edges[1:])):
        i = sum(join <= a for join in joins)
        neck = z0 <= a < z0 + ft or z1 - ft <= a < z1
        high = (
            cfg["mounting"]["shell_outer_r_mm"] - cfg["mounting"]["flange_radial_mm"]
            if neck
            else tr["trunk_r_mm"][1]
        )
        wire = cable + sum(s["cable"] for s in local[:i])
        titanium = ti + sum(s["ti"] for s in local[:i])
        coolant = co2 + sum(s["co2"] for s in local[:i])
        if neck:
            area = (
                len(tr["free_sector_start_deg"])
                * math.radians(tr["free_sector_width_deg"])
                / 2
                * (high**2 - tr["trunk_r_mm"][0] ** 2)
            )
            raw = wire + titanium + coolant
            packing = scenario["packing_fraction"]
            necks.append(
                dict(
                    abs_z_mm=[a, b],
                    bare_footprint_mm2=raw,
                    geometric_area_mm2=area,
                    packing_fraction=packing,
                    utilization=raw / (area * packing),
                    status="PASS" if raw <= area * packing else "FAIL",
                )
            )
        cell(
            f"trunk{name}{j}_",
            tr["trunk_r_mm"][0],
            high,
            a,
            b,
            wire * (b - a),
            titanium * (b - a),
            coolant * (b - a),
        )
    for i, d in enumerate(discs):
        wireV = tiV = co2V = 0.0
        retained = [r for r in rings if r["row"] in d["retained_rows"]]
        for ring in retained:
            n = ring["modules"]
            chips = 1 if ring["family"] == "single" else 4
            chain_limit = min(
                budget["pixel"]["max_chain_modules"],
                budget["pixel"]["max_chain_chips"] // chips,
            )
            chains = math.ceil(math.ceil(n / 2) / chain_limit) + math.ceil(
                math.floor(n / 2) / chain_limit
            )
            links = n * (
                scenario["pixel_uplinks_per_module"]
                + scenario["pixel_commands_per_module"]
                + chips * scenario["pixel_uplinks_per_chip"]
            )
            wire = (
                chains * budget["pixel"]["ancillary_chain_area_mm2"]
                + links * budget["pixel"]["differential_link_area_mm2"]
            )
            tracks = [
                t
                for t in d["after"]["cooling"]["tracks"]
                if t["physical_ring"] == ring["row"] + 1
            ]
            # The circuit row is the collector takeoff radius; two chip rows in a quad.
            length = tr["trunk_r_mm"][0] - sum(t["radius_mm"] for t in tracks) / len(
                tracks
            )
            wireV += wire * length
            tiV += 4 * tiA * sum(tr["trunk_r_mm"][0] - t["radius_mm"] for t in tracks)
            co2V += 4 * co2A * sum(tr["trunk_r_mm"][0] - t["radius_mm"] for t in tracks)
        a, b = config["collector_w_mm"]
        z = d["datum_mm"]
        cell(
            f"collector{name}{i+1}_",
            *tr["collector_r_mm"],
            z + a,
            z + b,
            wireV,
            tiV,
            co2V,
        )
    last = discs[-1]["datum_mm"] + config["collector_w_mm"][1]
    L = tr["rear_turn_abs_z_mm"][0] - last
    cell(
        f"bypass{name}_",
        *tr["bypass_r_mm"],
        last,
        tr["rear_turn_abs_z_mm"][0],
        local[-1]["cable"] * L,
        local[-1]["ti"] * L,
        local[-1]["co2"] * L,
    )
    L = tr["rear_r_mm"][1] - tr["trunk_r_mm"][0]
    cell(
        f"rear{name}_",
        *tr["rear_r_mm"],
        *tr["rear_turn_abs_z_mm"],
        (cable + sum(s["cable"] for s in local)) * L,
        (ti + sum(s["ti"] for s in local)) * L,
        (co2 + sum(s["co2"] for s in local)) * L,
    )
    return dict(
        cells=cells,
        flange_necks=necks,
        disc_footprints=local,
        inherited_scenario_screens=schedule["accumulated_services"],
        note="Constructible effective inventory does not establish packing, routing or hydraulic qualification.",
    )
