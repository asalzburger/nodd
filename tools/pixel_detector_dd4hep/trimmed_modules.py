"""DES019 radial/tangential modules; preserve frozen source patch identities."""

import math
import xml.etree.ElementTree as ET
from export import mm


def patches(module, radial):
    f = radial["families"][module["family"]]
    du, dv = radial["active_mm"]
    pitchu, pitchv = du + radial["interchip_gap_mm"], dv + radial["interchip_gap_mm"]
    return [
        (
            i * f["rows"] + j,
            (i - (f["columns"] - 1) / 2) * pitchu,
            (j - (f["rows"] - 1) / 2) * pitchv,
        )
        for i in range(f["columns"])
        for j in range(f["rows"])
    ]


def module_xml(parent, m, radial, stack, entities, side, system, disc, datum, die):
    code = m["module_id"] - 200000
    name = f"disc{system}_{disc}_m{code}"
    sign = side * m["mount_face"]
    u = [sign * x for x in m["u"]]
    v = m["v"]
    n = [0, 0, -sign]
    center = [*m["center_mm"][:2], side * m["center_mm"][2]]
    ids = dict(system=system, layer=disc, stave=m["col"], module=code)
    mx = ET.SubElement(
        parent,
        "module",
        name=name,
        id=str(code),
        col=str(m["col"]),
        x=mm(center[0]),
        y=mm(center[1]),
        z=mm(side * m["local_z_mm"]),
        ux=str(u[0]),
        uy=str(u[1]),
        vx=str(v[0]),
        vy=str(v[1]),
        nz=str(n[2]),
    )
    offset = ((0 if side < 0 else 9) + disc - 1) * 10000
    entities.append(
        dict(
            name=name,
            role="module",
            center_mm=center,
            ids=ids,
            family=m["family"],
            source_module_id=m["module_id"] + offset,
            template_module_id=m["module_id"],
            row=m["row"],
        )
    )

    def world(a, b, w):
        return [center[i] + a * u[i] + b * v[i] + w * n[i] for i in range(3)]

    def record(label, role, a, b, w, du, dv, dw, mat, **extra):
        entities.append(
            dict(
                name=name + "_" + label,
                role=role,
                center_mm=world(a, b, w),
                volume_mm3=du * dv * dw,
                material=mat,
                **extra,
            )
        )

    f = radial["families"][m["family"]]
    activeu, activev = radial["active_mm"]
    guard = radial["sensor_guard_mm"]
    su = (
        f["columns"] * activeu
        + (f["columns"] - 1) * radial["interchip_gap_mm"]
        + 2 * guard
    )
    sv = f["rows"] * activev + (f["rows"] - 1) * radial["interchip_gap_mm"] + 2 * guard
    t = stack["sensor_mm"]
    pp = patches(m, radial)
    sx = ET.SubElement(
        mx,
        "sensor",
        u=mm(0),
        v=mm(0),
        width=mm(su),
        length=mm(sv),
        thickness=mm(t),
        material="Silicon",
        vis="Silicon",
    )
    record(
        "substrate",
        "sensor_guard",
        0,
        0,
        0,
        su * sv - len(pp) * activeu * activev,
        1,
        t,
        "Silicon",
    )
    for patch, a, b in pp:
        pid = 4 * code + patch
        a *= sign
        ET.SubElement(
            sx,
            "patch",
            id=str(pid),
            u=mm(a),
            v=mm(b),
            width=mm(activeu),
            length=mm(activev),
        )
        record(
            "sensor_" + str(pid),
            "sensitive",
            a,
            b,
            0,
            activeu,
            activev,
            t,
            "Silicon",
            ids=dict(ids, sensor=pid),
            normal=n,
            u=u,
            v=v,
            size_mm=[activeu, activev, t],
            source_patch_id=300000 + pid + offset,
            template_patch_id=300000 + pid,
        )

    def passive(label, a, b, w, du, dv, dw, mat, role="module_passive"):
        body = f["body_mm"]
        bodyv = f["periphery_offset_mm"]
        if (
            max(
                abs(a) + du / 2 - body[0] / 2,
                abs(b - bodyv) + dv / 2 - body[1] / 2,
                abs(w) + dw / 2 - radial["body_thickness_mm"] / 2,
            )
            > 1e-8
        ):
            raise ValueError("Module component exceeds frozen body: " + label)
        ET.SubElement(
            mx,
            "passive",
            name=label,
            u=mm(a),
            v=mm(b),
            w=mm(w),
            width=mm(du),
            length=mm(dv),
            thickness=mm(dw),
            material=mat,
            vis="Copper" if mat == "PatternedCopper" else mat,
        )
        record(label, role, a, b, w, du, dv, dw, mat)

    w = -t / 2
    for label, dw, mat in [
        ("flex_glue", stack["epoxy_mm"], "Epoxy"),
        ("flex_cu_inner", stack["flex_copper_layer_mm"], "PatternedCopper"),
        ("flex_polyimide", stack["flex_polyimide_mm"], "Polyimide"),
        ("flex_cu_outer", stack["flex_copper_layer_mm"], "PatternedCopper"),
    ]:
        passive(label, 0, 0, w - dw / 2, su, sv, dw, mat)
        w -= dw
    for patch, a, b in pp:
        a *= sign
        periphery = radial["periphery_offset_mm"]
        b += periphery * (1 if len(pp) == 1 or b > 0 else -1)
        w = t / 2 + stack["bump_standoff_mm"] + stack["asic_mm"] / 2
        passive(
            f"asic{patch}",
            a,
            b,
            w,
            die["approximate_die_u_mm"],
            die["approximate_die_v_mm"],
            stack["asic_mm"],
            "Silicon",
            "asic",
        )
        back = w + stack["asic_mm"] / 2
        h = radial["body_thickness_mm"] / 2 - back
        passive(
            f"contact{patch}",
            a,
            b,
            back + h / 2,
            die["approximate_die_u_mm"],
            die["approximate_die_v_mm"],
            h,
            "Graphite",
            "contact_shim",
        )
    return name
