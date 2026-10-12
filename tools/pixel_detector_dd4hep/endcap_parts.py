"""Reusable DES015 parts; parameters supplied by the pinned export configuration."""

import math
import xml.etree.ElementTree as ET
from export import mm, rad

TAU = 2 * math.pi


def volume(shape, d):
    if shape == "box":
        return d["dx"] * d["dy"] * d["dz"]
    if shape == "sector":
        return d["angle"] / 2 * (d["rmax"] ** 2 - d["rmin"] ** 2) * d["dz"]
    if shape == "torus":
        return TAU * d["radius"] * math.pi * (d["rmax"] ** 2 - d["rmin"] ** 2)
    if shape == "tongue":
        y = d["width"] / 2
        R = d["radius"]
        return (
            d["width"] * d["end"]
            - y * math.sqrt(R * R - y * y)
            - R * R * math.asin(y / R)
        ) * d["dz"]
    raise ValueError(shape)


class Parts:
    """One source for XML and independent expected exclusive-material accounting."""

    def __init__(self, entities):
        self.entities = entities
        self.owners = {}

    def add(
        self,
        parent,
        name,
        shape,
        mat,
        role,
        center=(0, 0, 0),
        rotation=(0, 0, 0),
        datum=0,
        **dims,
    ):
        style = "Service" if mat.startswith("EC_Service_") else mat
        if mat.startswith("EC_"):
            style = mat.split("_")[1]
        x = ET.SubElement(
            parent,
            "part",
            name=name,
            shape=shape,
            material=mat,
            vis=style,
            **{k: mm(v) for k, v in zip(("x", "y", "z"), center)},
            **{k: rad(v) for k, v in zip(("rx", "ry", "rz"), rotation)},
            **{k: (rad(v) if k == "angle" else mm(v)) for k, v in dims.items()},
        )
        cap = volume(shape, dims)
        # Child frames here are translations only (torus in disc core; rail void).
        host = self.owners.get(id(parent))
        global_center = [center[0], center[1], datum + center[2]]
        if host:
            host["volume_mm3"] -= cap
            global_center = [host["center_mm"][i] + center[i] for i in range(3)]
        e = dict(
            name=name, role=role, center_mm=global_center, volume_mm3=cap, material=mat
        )
        self.entities.append(e)
        self.owners[id(x)] = e
        return x
