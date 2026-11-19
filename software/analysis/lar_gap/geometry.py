"""Conditional 400 mm gap PROTOTYPE; rigid signed endcap translations only."""
import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from software.analysis.lar_response import transport as response

SHIFT_MM = 400.
FROZEN = {
    'detector.xml': '11143ea1f9aa03383b184ab7fb66b2f25a41525f124d4658f588376ada4d4040',
    'materials.xml': '1e3828ce911d4d91cc50f097cece2139e37e2a008b201a7cb8e6cf410e6a487d',
    'particles.HEPEvt': '44bf93acf342ccfd9f461423ea12992ab1cab9046f84841ff8853ed763aad389',
    'truth-input.jsonl': 'b53199a644e659eb6efdd4684b824c6b85f66e0968686b0af3482e93b56c30b1',
}
PROTOCOL = ROOT/'docs/validation/lar-gap10k/protocol.md'
sha, load, save = response.sha, response.load, response.save


def signature(node):
    return node.tag, tuple(sorted(node.attrib.items())), (node.text or '').strip(), tuple(signature(c) for c in node)


def dimension(text):
    if not re.fullmatch(r'[-+0-9.eE]+\*mm', text or ''):
        raise ValueError('Expected explicit numeric millimetres')
    number = float(text[:-3])
    if not math.isfinite(number): raise ValueError('Nonfinite placement')
    return number


def endcap(root):
    detectors = root.findall('detectors/detector')
    if (len(detectors) != 2 or {d.get('name') for d in detectors} != response.DETECTORS or
            {d.get('id') for d in detectors} != {'10', '11'} or root.find('fields') is not None):
        raise ValueError('Need exactly the frozen two ECAL roots and no field')
    d = next(d for d in detectors if d.get('name') == 'LArEndcaps')
    if d.attrib != dict(name='LArEndcaps', id='11', type='nODDLArEndcapPrototype', readout='LArEndcapHits'):
        raise ValueError('Ambiguous endcap root')
    if {n.tag for n in d} != {'sensitive', 'wheel', 'replica', 'piece'}:
        raise ValueError('Unexpected endcap topology')
    wheels = d.findall('wheel')
    if len(wheels) != 3 or {w.get('index') for w in wheels} != {'0','1','2'}:
        raise ValueError('Missing/duplicate turbine wheels')
    if any(len(w.findall('period_envelope')) != 1 or w.find('period_envelope').get('policy') != 'real-periods-v1' for w in wheels):
        raise ValueError('Expected unchanged real-period hierarchy')
    pieces = d.findall('piece'); names = {p.get('name'): p for p in pieces}
    if None in names or len(names) != len(pieces): raise ValueError('Duplicate/unnamed passive')
    for p in pieces:
        visited = {p.get('name')}; q = p
        while q.get('parent_name') is not None:
            name = q.get('parent_name')
            if name not in names or name in visited: raise ValueError('Unknown/cyclic passive parent')
            visited.add(name); q = names[name]
    replicas = d.findall('replica'); roots = [p for p in pieces if p.get('parent_name') is None]
    if len(replicas) != 4928 or len(roots) != 36 or len(pieces)-len(roots) != 38210:
        raise ValueError('Unexpected frozen placement counts')
    keys = [(r.get('side'),r.get('wheel'),r.get('plane')) for r in replicas]
    # Wheel periods are read from the frozen readout rather than inferred from order.
    table = root.find("readouts/readout[@name='LArEndcapHits']/segmentation").get('wheel_table_mm')
    values = list(map(float, table.split()))
    if len(values) != 12: raise ValueError('Invalid wheel table')
    wanted = {(str(side),str(w),str(p)) for side in (1,2) for w in range(3) for p in range(int(values[4*w+2]))}
    if len(set(keys)) != len(keys) or set(keys) != wanted: raise ValueError('Incomplete signed wheel replicas')
    for n in [*replicas,*roots]:
        z = dimension(n.get('z'))
        if abs(z) < 4000 or (n.tag == 'replica' and (z > 0) != (n.get('side') == '1')):
            raise ValueError('Ambiguous placement side')
    return d, replicas, roots


def transform(tree):
    result = deepcopy(tree)
    _, replicas, roots = endcap(result.getroot())
    for n in [*replicas,*roots]:
        z = dimension(n.get('z')); n.set('z', format(z-math.copysign(SHIFT_MM,z), '.17g')+'*mm')
    verify_transform(tree, result)
    return result


def verify_transform(reference, candidate):
    """Normalize only allowed z fields, then compare the entire XML structure."""
    normal = deepcopy(candidate)
    _, a_reps, a_roots = endcap(reference.getroot())
    _, b_reps, b_roots = endcap(normal.getroot())
    changed = []
    for a,b in zip([*a_reps,*a_roots], [*b_reps,*b_roots]):
        old, new = dimension(a.get('z')), dimension(b.get('z'))
        if abs(new-(old-math.copysign(SHIFT_MM,old))) > 1e-10:
            raise ValueError('Wrong signed rigid translation')
        b.set('z',a.get('z')); changed.append((a.tag,a.get('name'),a.get('side'),a.get('wheel'),a.get('plane')))
    if signature(reference.getroot()) != signature(normal.getroot()):
        raise ValueError('Unexpected XML difference outside allowed root-relative z')
    return dict(replicas=len(a_reps), passive_roots=len(a_roots), unchanged_passive_daughters=38210,
                shift_toward_IP_mm=SHIFT_MM, allowed_change='Only z attributes on all root-relative endcap replicas and parentless passive pieces',
                all_other_XML_attributes_text_topology_unchanged=True)


def sources():
    paths = [Path(__file__).with_name(n) for n in ('geometry.py','native.py','compare.py')]
    paths += [PROTOCOL, ROOT/'software/analysis/lar_response/compare.py']
    return {str(p.relative_to(ROOT)):sha(p) for p in paths}


def check_sources(hashes):
    for path,digest in hashes.items():
        p = (ROOT/path).resolve()
        if not p.is_relative_to(ROOT) or sha(p) != digest: raise ValueError('Changed producer/source: '+path)


def archived_producer(manifest):
    path='software/analysis/lar_response/transport.py';declared=manifest['source_revision']
    revisions=[declared,'e2222482eb6c267fe1db4e4a871280469d49f7f9']
    for revision in dict.fromkeys(revisions):
        content=subprocess.check_output(['git','show',revision+':'+path],cwd=ROOT)
        if hashlib.sha256(content).hexdigest()==manifest['producer_sha256']:
            return dict(declared_generation_HEAD=declared,exact_producer_blob_locator=revision+':'+path,
                        producer_sha256=manifest['producer_sha256'],producer_matches_declared_HEAD=revision==declared,
                        note='Exact retained producer bytes; matching later commit is source recovery, not a claim that original generation was clean')
    raise ValueError('Original sample producer bytes unavailable in retained Git history')


def reference_bindings(sample, run):
    sample, run = sample.resolve(), run.resolve()
    m = load(sample/'sample.json'); response.verify_hashes(sample, FROZEN)
    if m['hashes'] != FROZEN or m['events'] != 10000 or m['collections'] != response.COLLECTIONS:
        raise ValueError('Unexpected frozen sample manifest')
    if response.cell_inventory(ET.parse(sample/'detector.xml').getroot()) != m['inventory']:
        raise ValueError('Readout inventory differs')
    original_producer=archived_producer(m)
    receipt, proof = load(run/'receipt.json'), load(run/'readback.json')
    if (receipt['exit_code'] or receipt['disk_abort'] or receipt['sample_sha256'] != sha(sample/'sample.json') or
            proof['status'] != 'PASS' or proof['sample'] != m or proof['receipt_sha256'] != sha(run/'receipt.json') or
            proof['event_summary_sha256'] != sha(run/'event-summary.jsonl') or not receipt['producers_unchanged'] or not receipt['libraries_unchanged']):
        raise ValueError('Unbound/unsuccessful standard reference run')
    check_sources(receipt['producer_sha256'])
    for path,digest in receipt['library_sha256'].items():
        if sha(path) != digest: raise ValueError('Changed reference library')
    for name,digest in proof['worker_audit_sha256'].items():
        if sha(run/'audit'/name) != digest: raise ValueError('Changed reference worker')
    baseline = sample.parent/'layout002'; b = load(baseline/'baseline.json')
    if b != m['source_baseline'] or sha(baseline/'baseline.json') != m['source_baseline_sha256']:
        raise ValueError('Unbound original baseline manifest')
    response.verify_hashes(baseline, {'detector.xml':m['source_compact_sha256'], 'materials.xml':FROZEN['materials.xml']})
    components = {}; scientific = {}
    for tag in ('lar-barrel','lar-endcaps'):
        d=baseline/'components'/tag; expected=d/'expected.json'; model=load(expected)
        check_sources(model['source_sha256']); response.verify_hashes(d, model['artifact_sha256'])
        scientific.update(model['source_sha256'])
        components[tag]=dict(expected_sha256=sha(expected),artifact_sha256=model['artifact_sha256'], source_sha256=model['source_sha256'],original_export_execution=model['execution'],
                             material_totals=model['material_totals'], physical_sensitive_elements=model['physical_sensitive_elements'])
    return dict(reference_sample=str(sample),reference_run=str(run),reference_manifest_sha256=sha(sample/'sample.json'),original_sample_producer=original_producer,
                reference_receipt_sha256=sha(run/'receipt.json'), reference_readback_sha256=sha(run/'readback.json'),
                reference_root_sha256=proof['root_sha256'], reference_producers=receipt['producer_sha256'],
                library_sha256=receipt['library_sha256'], scientific_source_sha256=scientific, components=components)


def verify(sample):
    sample=Path(sample).resolve(); m=load(sample/'sample.json'); response.verify_hashes(sample,m['hashes'])
    gap=m['gap_experiment']; check_sources(gap['source_sha256'])
    binding=reference_bindings(Path(gap['reference_sample']),Path(gap['reference_run']))
    if binding != gap['reference_binding']: raise ValueError('Changed frozen reference binding')
    proof=verify_transform(ET.parse(Path(gap['reference_sample'])/'detector.xml'),ET.parse(sample/'detector.xml'))
    if proof != gap['XML_changes']: raise ValueError('Changed transformation contract')
    for n in ('materials.xml','particles.HEPEvt','truth-input.jsonl'):
        if m['hashes'][n] != FROZEN[n]: raise ValueError('Changed fixed input/material bytes')
    if response.cell_inventory(ET.parse(sample/'detector.xml').getroot()) != m['inventory']:
        raise ValueError('Changed local readout inventory')
    return m


def prepare(args):
    reference=args.reference_sample.resolve(); binding=reference_bindings(reference,args.reference_run)
    m=deepcopy(load(reference/'sample.json')); tree=ET.parse(reference/'detector.xml'); shifted=transform(tree)
    out=args.output.resolve(); out.mkdir(parents=True,exist_ok=False)
    shifted.write(out/'detector.xml',encoding='utf-8',xml_declaration=True)
    for name in ('materials.xml','particles.HEPEvt','truth-input.jsonl'): shutil.copyfile(reference/name,out/name)
    m['original_geometry_revision']=m['source_revision'];m['source_revision']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    m['geometry_extraction']='Conditional gap PROTOTYPE: only whole-endcap root-relative placements translated 400 mm toward IP; all internals and barrel unchanged'
    m['hashes']={n:sha(out/n) for n in FROZEN};m['producer_sha256']=sha(__file__)
    m['gap_experiment']=dict(reference_sample=str(reference),reference_run=str(args.reference_run.resolve()), reference_binding=binding,
        source_sha256=sources(), XML_changes=verify_transform(tree,shifted), baseline_warm_gap_mm=800, candidate_warm_gap_mm=400,
        baseline_active_separation_mm=1100,candidate_active_separation_mm=700,
        limitations='Gap-only ECAL response sensitivity; unresolved routing overlay absent; no integration or engineering acceptance')
    save(out/'sample.json',m);verify(out);print('Prepared and verified conditional 400 mm gap sample:',out)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='stage',required=True)
    a=sub.add_parser('prepare')
    for n in ('reference-sample','reference-run','output'): a.add_argument('--'+n,type=Path,required=True)
    a=sub.add_parser('verify');a.add_argument('--sample',type=Path,required=True)
    args=p.parse_args();prepare(args) if args.stage=='prepare' else print('PASS',verify(args.sample)['gap_experiment']['XML_changes'])
