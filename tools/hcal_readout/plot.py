"""Render the source-bound DES036 board/carrier and local physical sections."""
import argparse
import hashlib
import json
from pathlib import Path


def draw(expected_path, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Rectangle

    data = json.loads(expected_path.read_text())
    config = data["config"]
    parts = data["parts"]
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "svg.fonttype": "none"})
    fig = plt.figure(figsize=(14, 9), layout="constrained", facecolor="#fcfcfa")
    grid = fig.add_gridspec(3, 2, width_ratios=(1.6, 1), height_ratios=(1.15, 1, .65))
    face = fig.add_subplot(grid[:, 0])
    tile = fig.add_subplot(grid[0, 1])
    thermal = fig.add_subplot(grid[1, 1])
    note = fig.add_subplot(grid[2, 1])
    fig.suptitle("HCAL common readout module   |   14 TeV study   |   PROTOTYPE", fontsize=18, fontweight="bold")
    width, height, _ = data["fixture"]["carrier_size_mm"]
    face.add_patch(Rectangle((-width/2, -height/2), width, height,
                             fc="#eef0ee", ec="#485550", lw=1.5))
    for module in data["modules"]:
        x, y = module["centre_xy_mm"]
        board_w, board_h, _ = config["module"]["pcb_size_mm"]
        face.add_patch(Rectangle((x-board_w/2, y-board_h/2), board_w, board_h,
                                 fc="#dce9dc", ec="#49715c", lw=1.2))
        face.text(x, -111, "Board " + str(module["module"]) + " · 36 tiles", ha="center", fontsize=11)
        asic = next(p for p in parts if p["owner"] == "module:" + str(module["module"]) and p["role"] == "frontend")
        sx, sy = asic["dimensions_mm"]["sx"], asic["dimensions_mm"]["sy"]
        face.add_patch(Rectangle((x-sx/2, y-sy/2), sx, sy, fc="none", ec="#5b5874", ls="--", lw=1.2, zorder=5))
    for part in parts:
        if part["role"] == "sensitive":
            x, y, _ = part["center_mm"]
            sx, sy = part["dimensions_mm"]["sx"], part["dimensions_mm"]["sy"]
            face.add_patch(Rectangle((x-sx/2, y-sy/2), sx, sy, fc="#75b9a6", ec="white", lw=.5))
    face.add_patch(Rectangle((-3.15, -101.85), 6.3, 179.7, fc="#bd584e", alpha=.6))
    for part in parts:
        if part["name"] == "carrier_service_pcb_G10":
            x, y, _ = part["center_mm"]
            sx, sy = part["dimensions_mm"]["sx"], part["dimensions_mm"]["sy"]
            face.add_patch(Rectangle((x-sx/2, y-sy/2), sx, sy, fc="#c9dcef", ec="#6085a4"))
        if part["role"].startswith("connector_"):
            x, y, _ = part["center_mm"]
            face.add_patch(Rectangle((x-10, y-6), 20, 12, fc="#7d92a4", ec="#40566b"))
            label = part["role"].split("_", 1)[1]
            face.text(x, y-15, label, ha="center", va="center", fontsize=8)
    for x in config["carrier"]["tube_x_mm"]:
        face.plot([x, x], [-120, 120], "--", color="#158bb0", lw=1.1, alpha=.8)
        face.scatter([x, x], [-120, 120], marker="o", s=30, color="#158bb0", zorder=7)
    face.text(0, 132, "Shared service bay / four external cooling handoffs", ha="center", fontsize=10)
    face.text(0, -131, "380 × 240 mm carrier · two 184 mm boards\n6.3 mm active seam · dashed: rear ASICs and buried tubes",
              ha="center", va="top", fontsize=10, linespacing=1.5)
    face.set(xlim=(-200, 200), ylim=(-157, 144), xlabel="Carrier x [mm]", ylabel="Carrier y [mm]",
             title="Physical tile layout and shared services")
    face.set_aspect("equal")

    # Actual first-tile x–z cross section; front sensor and LED share its recess.
    first = next(p for p in parts if p["name"] == "m0_t0_active")
    tx = first["center_mm"][0]
    for name, color in (("m0_t0_active", "#75b9a6"), ("m0_t0_sipm", "#5867a0"),
                        ("m0_t0_solder", "#c59059"), ("m0_t0_led", "#d3b749")):
        part = next(p for p in parts if p["name"] == name)
        x, _, z = part["center_mm"]
        sx, sz = part["dimensions_mm"]["sx"], part["dimensions_mm"]["sz"]
        tile.add_patch(Rectangle((x-tx-sx/2, z-sz/2), sx, sz, fc=color, ec="white", lw=.6))
        if name.endswith("active"):
            cut = part["cuts"][0]
            radius = cut["dimensions_mm"]["rmax"]
            cut_z = z + cut["center_mm"][2]
            depth = cut["dimensions_mm"]["length"]
            tile.add_patch(Rectangle((-radius, cut_z-depth/2), 2*radius, depth, fc="#fcfcfa", ec="none"))
    tile.add_patch(Rectangle((-16, 3.7), 32, 1.2, fc="#b9c79b", ec="#6f7b50", lw=.7))
    tile.text(-15.5, 1.6, "3 mm PS host", fontsize=9)
    tile.text(8, 3.0, "SiPM + LED\nin rear recess", ha="left", fontsize=8)
    tile.text(0, 4.35, "PCB / equivalent copper", ha="center", fontsize=9)
    tile.set(xlim=(-16.5, 16.5), ylim=(5.3, 0), xlabel="Tile-local x [mm]", ylabel="Depth z [mm]",
             title="One tile: nominal optical-package geometry")

    colors = {"pcb": "#b9c79b", "bond": "#dbc7a8", "frontend": "#7c76a5",
              "thermal_contact": "#8e989f", "thermal_post": "#bcc8d0", "cold_plate": "#c8996a"}
    for role in ("pcb", "bond", "frontend", "thermal_contact", "thermal_post", "cold_plate"):
        choices = [p for p in parts if p["role"] == role and
                   (p["owner"] == "module:0" or role == "cold_plate")]
        if role == "pcb":
            # Display complete board thickness, independent of its dielectric split.
            thermal.add_patch(Rectangle((-12, 3.7), 24, 1.2, fc=colors[role], ec="white", lw=.7))
            continue
        part = choices[0]
        z = part["center_mm"][2]
        depth = part["dimensions_mm"]["sz"]
        width = 24 if role == "cold_plate" else part["dimensions_mm"]["sx"]
        thermal.add_patch(Rectangle((-width/2, z-depth/2), width, depth,
                                    fc=colors[role], ec="white", lw=.7))
        if role in ("frontend", "cold_plate"):
            thermal.text(0, z if role == "frontend" else 9.7, "Front-end envelope" if role == "frontend" else "Shared Cu plate", ha="center", va="center", fontsize=9)
    thermal.add_patch(Circle((0, config["carrier"]["tube_z_mm"]), config["carrier"]["tube_outer_radius_mm"], fc="#a2b5c1", ec="#6d858e", lw=.8))
    thermal.add_patch(Circle((0, config["carrier"]["tube_z_mm"]), config["carrier"]["tube_inner_radius_mm"], fc="#49a8cf", ec="none"))
    thermal.text(2, 8.5, "Ti / water", va="center", fontsize=8)
    thermal.set(xlim=(-15, 15), ylim=(10.4, 3.4), xlabel="Board-centre section x [mm]", ylabel="Depth z [mm]",
                title="ASIC contact path to common cold plate")
    note.axis("off")
    power = data["budgets"]["power_scenarios"][0]
    text = ("72 tiles · 156 powered ASIC channels\n"
            f"Carrier + boards: {data['carrier_and_modules_mass_g']/1000:.3f} kg\n"
            f"Planning heat: {power['total_heat_W']:.3f} W · ideal water: {power['ideal_water_g_s']:.3f} g/s\n"
            "DAQ screen: 93.75% at 750 kHz; overload at 1 MHz\n"
            "Nominal fixture · package/cooling/rate qualification pending")
    note.text(0, .95, text, va="top", fontsize=10, linespacing=1.5, color="#37453e")
    for suffix in ("svg", "png"):
        fig.savefig(output / ("common-module." + suffix), dpi=170, facecolor=fig.get_facecolor())
    plt.close(fig)
    (output / "inputs.json").write_text(json.dumps({"expected_sha256": hashlib.sha256(expected_path.read_bytes()).hexdigest(),
                                                  "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                                                  "scope": "Source-bound prototype schematic; no engineering or response acceptance"}, indent=2) + "\n")
    print("Rendered common-module.svg and .png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    draw(args.expected, args.output)
