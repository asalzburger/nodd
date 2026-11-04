#!/usr/bin/env python3
"""Create an ODD comparison compact retaining every tracker constituent."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def prepare(source, output):
    source = source.resolve()
    root = ET.Element('lccdd')
    # Definitions must be at the top level: DD4hep creates the world before
    # processing ordinary includes and therefore needs the material includes here.
    for child in ET.parse(source/'OpenDataDetectorDefs.xml').getroot():
        for entry in child.iter():
            if entry.tag in ('include', 'gdmlFile') and 'ref' in entry.attrib:
                entry.set('ref', str(source/entry.attrib['ref']))
        root.append(child)
    tracker = ET.parse(source/'OpenDataDetectorTracker.xml').getroot()
    removed = []
    for child in tracker:
        if child.tag == 'include':
            ref = child.attrib['ref']
            if ref == 'detectors/Solenoid.xml':
                removed.append(ref)
                continue
            child.set('ref', str(source/ref))
        root.append(child)
    if removed != ['detectors/Solenoid.xml']:
        raise ValueError('Expected exactly one explicit solenoid include')
    ET.indent(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(output, encoding='unicode')
    # Hash the complete XML tree, including definitions that reference further files.
    manifest = {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(source.rglob('*.xml'))}
    output.with_suffix('.provenance.json').write_text(json.dumps({
        'source_xml_sha256': manifest, 'removed_tracker_includes': removed,
        'omitted_subsystems': ['calorimeter', 'muon', 'solenoid', 'field'],
        'world_policy': 'native ODD 12 m half sizes; no physical model retuning',
        'wrapper_sha256': hashlib.sha256(output.read_bytes()).hexdigest()}, indent=2)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    prepare(args.source, args.output)
