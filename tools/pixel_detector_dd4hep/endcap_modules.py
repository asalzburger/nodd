"""Reusable DES015 modules; parameters supplied by the pinned export configuration."""

import copy
import xml.etree.ElementTree as ET
from export import mm
from module_geometry import describe


def module_xml(parent, b, patches, models, mcfg, entities, system, disc, side, datum):
    """Reuse C++ module factory, with legacy endcap shape and support-facing frame."""
    name = "m" + str(b["module_id"])
    nz = -side * b["mount_face"]
    frame = dict(
        b,
        n=[0, 0, nz],
        v=[nz * v for v in b["v"]],
        center_mm=[*b["center_mm"][:2], datum + side * b["center_mm"][2]],
    )
    # describe() needs original source-relative patch coordinates, before new z.
    source = copy.deepcopy(b)
    source["center_mm"][2] = patches[0]["center_mm"][2]
    shape = describe(source, patches, models, {"metadata": {}})
    uc, vc, su, sv = [shape[k] for k in ("u", "v", "width", "length")]
    vc *= nz
    ids = dict(system=system, layer=disc, stave=b["col"], module=b["module_id"])
    mx = ET.SubElement(
        parent,
        "module",
        name=name,
        id=str(b["module_id"]),
        col=str(b["col"]),
        x=mm(b["center_mm"][0]),
        y=mm(b["center_mm"][1]),
        z=mm(side * b["center_mm"][2]),
        ux=str(frame["u"][0]),
        uy=str(frame["u"][1]),
        vx=str(frame["v"][0]),
        vy=str(frame["v"][1]),
        nz=str(nz),
    )
    entities.append(
        dict(name=name, role="module", center_mm=frame["center_mm"], ids=ids)
    )

    def world(u, v, w):
        return [
            frame["center_mm"][j]
            + u * frame["u"][j]
            + v * frame["v"][j]
            + w * frame["n"][j]
            for j in range(3)
        ]

    def record(n, role, u, v, w, du, dv, dw, mat, **extra):
        entities.append(
            dict(
                name=n,
                role=role,
                center_mm=world(u, v, w),
                volume_mm3=du * dv * dw,
                material=mat,
                **extra,
            )
        )

    t = mcfg["sensor_mm"]
    sx = ET.SubElement(
        mx,
        "sensor",
        u=mm(uc),
        v=mm(vc),
        width=mm(su),
        length=mm(sv),
        thickness=mm(t),
        material="Silicon",
        vis="Silicon",
    )
    active = sum(4 * p["half_u_mm"] * p["half_v_mm"] for p in patches)
    record(
        name + "_substrate",
        "sensor_guard",
        uc,
        vc,
        0,
        su * sv - active,
        1,
        t,
        "Silicon",
    )
    for (u, v), p in zip(shape["local"], patches):
        v *= nz
        pid = p["id"]
        du = 2 * p["half_u_mm"]
        dv = 2 * p["half_v_mm"]
        ET.SubElement(
            sx,
            "patch",
            id=str(pid),
            u=mm(u - uc),
            v=mm(v - vc),
            width=mm(du),
            length=mm(dv),
        )
        record(
            f"{name}_sensor_{pid}",
            "sensitive",
            u,
            v,
            0,
            du,
            dv,
            t,
            "Silicon",
            normal=frame["n"],
            size_mm=[du, dv, t],
            ids=dict(ids, sensor=pid),
        )

    def passive(n, u, v, w, du, dv, dw, mat, role="module_passive"):
        if (
            max(
                abs(u) + du / 2 - b["half_u_mm"],
                abs(v) + dv / 2 - b["half_v_mm"],
                abs(w) + dw / 2 - b["half_w_mm"],
            )
            > 1e-8
        ):
            raise ValueError("Endcap component exceeds source occupied body: " + n)
        ET.SubElement(
            mx,
            "passive",
            name=n,
            u=mm(u),
            v=mm(v),
            w=mm(w),
            width=mm(du),
            length=mm(dv),
            thickness=mm(dw),
            material=mat,
            vis="Copper" if mat == "PatternedCopper" else mat,
        )
        record(name + "_" + n, role, u, v, w, du, dv, dw, mat)

    w = -t / 2
    for n, dw, mat in [
        ("flex_glue", mcfg["epoxy_mm"], "Epoxy"),
        ("flex_cu_inner", mcfg["flex_copper_layer_mm"], "PatternedCopper"),
        ("flex_polyimide", mcfg["flex_polyimide_mm"], "Polyimide"),
        ("flex_cu_outer", mcfg["flex_copper_layer_mm"], "PatternedCopper"),
    ]:
        passive(n, uc, vc, w - dw / 2, su, sv, dw, mat)
        w -= dw
    for i, die in enumerate(shape["dies"]):
        du, dv = die["width"], die["length"]
        u, v = die["u"], nz * die["v"]
        w = t / 2 + mcfg["bump_standoff_mm"] + mcfg["asic_mm"] / 2
        passive(f"asic{i}", u, v, w, du, dv, mcfg["asic_mm"], "Silicon", "asic")
        back = w + mcfg["asic_mm"] / 2
        h = b["half_w_mm"] - back
        passive(
            f"contact{i}", u, v, back + h / 2, du, dv, h, "Graphite", "contact_shim"
        )
