#!/usr/bin/env python3
"""DES043 combined adapters; historical standalone producers stay unchanged."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

from model import ROOT, HERE, geometry, load, sha
from barrel_native import adapt, budget
import native

CONFIG=ROOT/'detector/config/short-strip-des043.json'


def selection(path=CONFIG):
    path=Path(path)
    s=json.loads(path.read_text())
    if (s.get('schema_version')!=1 or s.get('design')!='DES-043'
            or s.get('classification')!='NODD DESIGN CHOICE'
            or s.get('expected_sensitive')!={'short_barrel':8064,'short_endcap':4752}
            or s.get('expected_combined_sensitive')!=46682 or s.get('expected_logical_groups')!=54):
        raise ValueError('Unsupported DES043 integration selection')
    c=load(ROOT/s['input'])
    return s,c


def write(path,node):
    ET.indent(node,space='  ')
    ET.ElementTree(node).write(path,encoding='utf-8',xml_declaration=True)


def export(component, output, config_path=CONFIG):
    s,c=selection(config_path); output=Path(output);output.mkdir(parents=True,exist_ok=True)
    if component=='short_endcap':
        doc,materials,expected=native.build(c,full=True)
        detector=doc.find('./detectors/detector')
        detector.set('name','ShortStripEndcap');detector.set('readout','ShortStripEndcapHits')
        doc.find('./readouts/readout').set('name','ShortStripEndcapHits')
        expected['shape_probes']=expected.pop('probes')
        nodes={p.get('name'):p for p in doc.findall('.//piece')}
        for entity in expected['entities']:budget(entity,nodes[entity['name']],expected['materials'])
        expected['readout']='ShortStripEndcapHits'
        filename='short-strip-endcap.xml'
    elif component=='short_barrel':
        # Independent subprocess avoids contaminating historical "model" imports.
        subprocess.run([sys.executable,'-B',str(ROOT/'tools/short_strip_barrel/export.py'),'--output',str(output)],check=True,stdout=subprocess.DEVNULL)
        filename='short-strip-barrel.xml';doc=ET.parse(output/filename).getroot()
        materials=ET.parse(output/'materials.xml').getroot()
        expected=json.loads((output/'expected.json').read_text())
        bc,ec,lc,bl,old,ll,selected=geometry(c)
        adapt(doc,expected,c,bc,bl)
        node=ET.SubElement(materials,'material',name='InsulatingTIM')
        ET.SubElement(node,'D',value=str(c['material']['TIM_density_upper_g_cm3']),unit='g/cm3')
        ET.SubElement(node,'fraction',n='1',ref='Epoxy')
    else:raise ValueError('Unsupported component '+component)
    count=sum(e['role']=='sensitive' for e in expected['entities'])
    if count!=s['expected_sensitive'][component]:raise ValueError('DES043 component sensor inventory mismatch')
    expected['counts']=dict(Counter(e['role'] for e in expected['entities']))
    expected['integration_design']='DES-043'
    expected['provenance']=dict(selection_sha256=sha(config_path),input_sha256=sha(ROOT/s['input']),
        source_hashes={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),HERE/'native.py',HERE/'barrel_native.py',
            HERE/'model.py',HERE/'diagnostics.py',ROOT/s['input'],Path(config_path),
            ROOT/'tools/short_strip_barrel/export.py',ROOT/'tools/short_strip_barrel/model.py',
            ROOT/'tools/short_strip_barrel/inputs-phi-tilted.json',ROOT/'tools/pixel_barrel_dd4hep/materials.py',
            ROOT/'prototypes/short_strip_barrel/ShortStripBarrel.cpp',ROOT/'prototypes/short_strip_endcap/ShortStripEndcap.cpp']},
        generation_source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
    write(output/filename,doc);write(output/'materials.xml',materials)
    expected['generated_artifact_sha256']={name:sha(output/name) for name in (filename,'materials.xml')}
    (output/'expected.json').write_text(json.dumps(expected,separators=(',',':'),allow_nan=False)+'\n')
    print(json.dumps(dict(component=component,sensitive=count,shape_probes=len(expected['shape_probes']))))
    return expected


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--component',choices=['short_barrel','short_endcap'],required=True)
    p.add_argument('--config',type=Path,default=CONFIG);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();export(a.component,a.output,a.config)
