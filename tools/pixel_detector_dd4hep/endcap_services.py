"""Reusable DES015 services; parameters supplied by the pinned export configuration."""

import math
from export import read
from model import ROOT, dimensions
from endcap_parts import volume

TAU = 2 * math.pi


def carrier(parts, det, cfg, side, name, discs):
    m = cfg["mounting"]
    z0, z1 = m["carrier_z_mm"]
    r = m["shell_outer_r_mm"]
    ri = r - m["shell_mm"]
    t = m["flange_axial_mm"]
    thick = dimensions(cfg)[0]
    parts.add(
        det,
        "carrier" + name,
        "sector",
        "CFRP",
        "carrier",
        center=(0, 0, side * (z0 + z1) / 2),
        rmin=ri,
        rmax=r,
        dz=z1 - z0,
        angle=TAU,
    )
    for i, z in enumerate([z0 + t / 2, z1 - t / 2]):
        parts.add(
            det,
            f"flange{name}{i}",
            "sector",
            "CFRP",
            "carrier",
            center=(0, 0, side * z),
            rmin=r - m["flange_radial_mm"],
            rmax=ri,
            dz=t,
            angle=TAU,
        )
    lo = m["rail_inner_r_mm"]
    hi = lo + m["rail_depth_mm"]
    w = m["rail_wall_mm"]
    a = m["rail_width_mm"] / ((lo + hi) / 2)
    # Explicit slots for unresolved tongue couplings; partition flange intersections.
    cuts = (
        [(z0, z0 + t)]
        + [
            (abs(d["proposed_z_mm"]) - thick / 2, abs(d["proposed_z_mm"]) + thick / 2)
            for d in discs
        ]
        + [(z1 - t, z1)]
    )
    spans = [(cuts[i][1], cuts[i + 1][0]) for i in range(len(cuts) - 1)]
    for k, phi in enumerate(m["angles_deg"]):
        for j, (a0, b0) in enumerate(spans):
            # Four sector walls give an open hollow rail without Air daughters.
            for edge, rl, rh, ph, angle in [
                ("inner", lo, lo + w, math.radians(phi) - a / 2, a),
                ("outer", hi - w, hi, math.radians(phi) - a / 2, a),
                (
                    "left",
                    lo + w,
                    hi - w,
                    math.radians(phi) - a / 2,
                    w / ((lo + hi) / 2),
                ),
                (
                    "right",
                    lo + w,
                    hi - w,
                    math.radians(phi) + a / 2 - w / ((lo + hi) / 2),
                    w / ((lo + hi) / 2),
                ),
            ]:
                parts.add(
                    det,
                    f"rail{name}_{k}_{j}_{edge}",
                    "sector",
                    "CFRP",
                    "rail",
                    center=(0, 0, side * (a0 + b0) / 2),
                    rotation=(0, 0, ph),
                    rmin=rl,
                    rmax=rh,
                    dz=b0 - a0,
                    angle=angle,
                )


def transport(parts, det, mats, cfg, config, baseline, bc, side, name, discs):
    """Volume-normalized reference service cells; endpoint connectivity is schematic."""
    cells = []
    necks = []
    fractions = config["cable_volume_fractions"]
    tr = config["transport"]
    reference = next(
        x
        for x in baseline["services"]["local_disc_scenarios"]
        if x["scenario"] == "reference"
    )
    summary = read(ROOT / bc["service_summary"])
    barrel = [
        s
        for s in summary["sectors"]
        if s["side"] == ("positive" if side > 0 else "negative")
    ]
    # Feed/return wall follows the existing barrel transport convention.
    wall = read(ROOT / "tools/pixel_support/services.json")["transport_wall_mm"]
    cable = sum(
        sum(s["scenarios"]["reference"]["terminal_cable_footprint_mm2"].values())
        for s in barrel
    )
    ti = sum(
        2 * math.pi * ((s["pair_OD_mm"] / 2) ** 2 - (s["pair_OD_mm"] / 2 - wall) ** 2)
        for s in barrel
    )
    coolant = sum(2 * math.pi * (s["pair_OD_mm"] / 2 - wall) ** 2 for s in barrel)
    rad = cfg["cooling"]["transport_OD_mm"] / 2
    discTi = 20 * math.pi * (rad**2 - (rad - wall) ** 2)
    discCO2 = 20 * math.pi * (rad - wall) ** 2

    def cell(label, rlo, rhi, zlo, zhi, wireV, tiV, co2V):
        # Three free 90-degree sectors between 30-degree reserved mounting sectors.
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

    # Hand-off at |z|605, outside the unchanged barrel cells. Common trunk stays
    # below the shell and within reserved service radii, until rear turn at3150.
    joins = [abs(d["proposed_z_mm"]) + config["collector_w_mm"][1] for d in discs[:-1]]
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
        if neck:
            raw = cable + ti + coolant + i * reference["bare_total_mm2"]
            available = (
                len(tr["free_sector_start_deg"])
                * math.radians(tr["free_sector_width_deg"])
                / 2
                * (high**2 - tr["trunk_r_mm"][0] ** 2)
            )
            packing = read(ROOT / cfg["service_inputs"])["scenarios"]["reference"][
                "packing_fraction"
            ]
            necks.append(
                dict(
                    abs_z_mm=[a, b],
                    bare_footprint_mm2=raw,
                    geometric_area_mm2=available,
                    packing_fraction=packing,
                    utilization=raw / (available * packing),
                    status="PASS" if raw <= available * packing else "FAIL",
                )
            )
        L = b - a
        cell(
            f"trunk{name}{j}_",
            tr["trunk_r_mm"][0],
            high,
            a,
            b,
            (cable + i * reference["cables_mm2"]) * L,
            (ti + i * discTi) * L,
            (coolant + i * discCO2) * L,
        )
    # Each collector preserves the radial path length from each cooling row;
    # cable allocation follows row module/chain/link demand, not a full disc PCB.
    rows = baseline["geometry"]["rows"]
    budget = read(ROOT / cfg["service_inputs"])
    scenario = budget["scenarios"]["reference"]
    radialCable = radialTi = radialCO2 = 0.0
    for row in rows:
        n = row["modules"]
        chains = 2 * math.ceil(n / 16)
        links = n * (
            scenario["pixel_uplinks_per_module"]
            + 4 * scenario["pixel_uplinks_per_chip"]
            + scenario["pixel_commands_per_module"]
        )
        wire = (
            chains * budget["pixel"]["ancillary_chain_area_mm2"]
            + links * budget["pixel"]["differential_link_area_mm2"]
        )
        length = tr["trunk_r_mm"][0] - row["cooling_radius_mm"]
        radialCable += wire * length
        radialTi += 4 * math.pi * (rad * rad - (rad - wall) ** 2) * length
        radialCO2 += 4 * math.pi * (rad - wall) ** 2 * length
    for i, d in enumerate(discs):
        z = abs(d["proposed_z_mm"])
        a, b = config["collector_w_mm"]
        # Stop at r190, leaving the DES010 2mm trunk boundary allowance empty.
        cell(
            f"collector{name}{i+1}_",
            *tr["collector_r_mm"],
            z + a,
            z + b,
            radialCable,
            radialTi,
            radialCO2,
        )
    # Last-disc axial bypass occupies r27..188, after its collector and before rear turn.
    last = abs(discs[-1]["proposed_z_mm"]) + config["collector_w_mm"][1]
    L = tr["rear_turn_abs_z_mm"][0] - last
    cell(
        f"bypass{name}_",
        *tr["bypass_r_mm"],
        last,
        tr["rear_turn_abs_z_mm"][0],
        reference["cables_mm2"] * L,
        discTi * L,
        discCO2 * L,
    )
    # Rear turn is a distinct effective inventory, ending at the r680 interface.
    L = tr["rear_r_mm"][1] - tr["trunk_r_mm"][0]
    cell(
        f"rear{name}_",
        *tr["rear_r_mm"],
        *tr["rear_turn_abs_z_mm"],
        (cable + 9 * reference["cables_mm2"]) * L,
        (ti + 9 * discTi) * L,
        (coolant + 9 * discCO2) * L,
    )

    return dict(cells=cells, flange_necks=necks)
