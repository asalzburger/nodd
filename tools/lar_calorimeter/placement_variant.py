"""Add only optional period-envelope declarations to an existing full LAr compact."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical(element):
    element=deepcopy(element)
    for node in element.iter():
        node.text=(node.text or "").strip() or None
        node.tail=None
    return ET.tostring(element)


def variant(args):
    tree=ET.parse(args.source); before=canonical(tree.getroot())
    count=0
    for system,source,tag in (("10",args.barrel,"period"),("11",args.endcaps,"wheel")):
        templates=ET.parse(source).findall("detectors/detector/"+tag)
        detectors=[d for d in tree.findall("detectors/detector") if d.get("id")==system]
        if len(detectors)!=1: raise ValueError("Missing/duplicate LAr detector")
        parents=detectors[0].findall(tag)
        if len(templates)!=len(parents) or len(parents)!=(1 if system=="10" else 3):
            raise ValueError("Incomplete period/wheel templates")
        for parent,template in zip(parents,templates):
            if parent.find("period_envelope") is not None: raise ValueError("Source already has envelope")
            envelope=template.find("period_envelope")
            if envelope is None or envelope.get("policy")!="real-periods-v1": raise ValueError("Missing qualified envelope")
            parent.append(deepcopy(envelope));count+=1
    restored=deepcopy(tree.getroot())
    for parent in restored.findall("detectors/detector/period")+restored.findall("detectors/detector/wheel"):
        envelope=parent.find("period_envelope")
        if envelope is not None: parent.remove(envelope)
    if canonical(restored)!=before: raise ValueError("Physical XML changed")
    args.output.mkdir(parents=True,exist_ok=False)
    tree.write(args.output/"detector.xml",encoding="utf-8",xml_declaration=True)
    shutil.copyfile(args.source.parent/"materials.xml",args.output/"materials.xml")
    proof={"status":"PASS","added_envelopes":count,"unchanged_after_stripping_only_envelopes":True,
        "comparison":"All original XML attributes, child ordering and text values; indentation whitespace ignored",
        "source_sha256":sha(args.source),"candidate_sha256":sha(args.output/"detector.xml"),
        "materials_sha256":sha(args.output/"materials.xml"),"barrel_template_sha256":sha(args.barrel),
        "endcap_template_sha256":sha(args.endcaps),"producer_sha256":sha(__file__)}
    (args.output/"variant.json").write_text(json.dumps(proof,indent=2)+"\n")
    print(json.dumps(proof,indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("source","barrel","endcaps","output"): p.add_argument("--"+name,type=Path,required=True)
    variant(p.parse_args())
