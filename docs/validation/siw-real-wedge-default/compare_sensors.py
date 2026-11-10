"""Compare actual DDG4 sensor IDs and transforms to the stock compact."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def detector_nodes(compact):
    result = {}
    for _, node in ET.iterparse(compact, events=("end",)):
        if node.tag == "detector":
            if node.get("id") in ("8", "9"):
                result[int(node.get("id"))] = node
            else:
                node.clear()
    if set(result) != {8, 9}:
        raise ValueError("Expected both stock Si-W components")
    return result


def pose(node):
    return tuple(tuple(float(node.get(f"a{i}{j}")) for j in range(3)) +
                 (float(node.get("xyz"[i]).removesuffix("*mm")),) for i in range(3))


def compose(outer, inner):
    return tuple(
        tuple(sum(outer[i][k] * inner[k][j] for k in range(3)) for j in range(3)) +
        (sum(outer[i][k] * inner[k][3] for k in range(3)) + outer[i][3],)
        for i in range(3)
    )


def expected_sensors(detector, system):
    templates = {board.get("name"): board.find("piece[@role='sensitive']") for board in detector.findall("board")}
    regions = {}
    for region in detector.findall("region"):
        sensors = [(int(p.get("module")), pose(p), p.get("material"))
                   for p in region.findall("piece") if p.get("module") is not None]
        for instance in region.findall("board_instance"):
            sensor = templates[instance.get("template")]
            sensors.append((int(instance.get("module")), compose(pose(instance), pose(sensor)), sensor.get("material")))
        regions[region.get("name")] = sensors
    for replica in detector.findall("replica"):
        side, sector, layer = (int(replica.get(key)) for key in ("side", "sector", "layer"))
        transform = pose(replica)
        prefix = system | side << 8 | sector << 10 | layer << 14
        for module, local, material in regions[replica.get("region")]:
            world = compose(transform, local)
            values = tuple(row[3] for row in world) + tuple(v for row in world for v in row[:3])
            yield prefix | module << 20, values, material


def compare(stock, sensors, output):
    expected = detector_nodes(stock)
    actual = {}
    with sensors.open() as stream:
        for line in stream:
            identifier, *values, material = line.rstrip("\n").split("\t")
            identifier = int(identifier)
            if identifier in actual or len(values) != 12:
                raise ValueError("Duplicate or malformed DDG4 sensor")
            actual[identifier] = tuple(map(float, values)), material
    maximum_position = maximum_rotation = 0.
    counts = {}
    for system, detector in expected.items():
        count = 0
        for identifier, values, material in expected_sensors(detector, system):
            observed, observed_material = actual.pop(identifier)
            if material != observed_material:
                raise ValueError(f"Sensor material differs for {identifier}")
            maximum_position = max(maximum_position, *(abs(a-b) for a, b in zip(values[:3], observed[:3])))
            maximum_rotation = max(maximum_rotation, *(abs(a-b) for a, b in zip(values[3:], observed[3:])))
            count += 1
        counts[system] = count
    if actual or counts != {8: 359904, 9: 172032} or maximum_position >= 1e-7 or maximum_rotation >= 1e-12:
        raise ValueError(f"Sensor inventory or world transform differs: {counts}, {maximum_position}, {maximum_rotation}")
    result = dict(sensors_by_system=counts, maximum_position_delta_mm=maximum_position,
                  maximum_rotation_element_delta=maximum_rotation)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("stock", "sensors", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    compare(args.stock, args.sensors, args.output)
