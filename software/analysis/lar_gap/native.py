"""Exhaustive native placement proof and full ECAL overlaps for the gap study."""
import argparse
from collections import defaultdict
import itertools
import json
import math
from pathlib import Path
import subprocess

from geometry import ROOT, SHIFT_MM, FROZEN, load, save, sha, verify, reference_bindings, check_sources, sources


def snapshot(args):
    import ROOT as R
    import dd4hep
    sample=args.sample.resolve();manifest=load(sample/'sample.json')
    if 'gap_experiment' in manifest:
        manifest=verify(sample); binding=manifest['gap_experiment']['reference_binding']
    else:
        binding=reference_bindings(sample,args.reference_run)
    libraries=[args.barrel_library.resolve(),args.endcap_library.resolve()]
    for p in libraries:
        if binding['library_sha256'].get(str(p)) != sha(p): raise ValueError('Unbound native factory library')
    check_sources(binding['scientific_source_sha256'])
    initial_sources={**binding['scientific_source_sha256'],**binding['reference_producers'],**sources()}
    initial_sources[str(Path(__file__).relative_to(ROOT))]=sha(__file__)
    source_state=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).splitlines()
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    R.gROOT.SetBatch(True);R.EnableImplicitMT(1);R.gRandom.SetSeed(43)
    for p in libraries:
        if R.gSystem.Load(str(p))<0:raise RuntimeError('Cannot load unchanged factory')
    detector=dd4hep.Detector.getInstance();mm=float(dd4hep.mm)
    try:
        detector.fromXML(str(sample/'detector.xml'));manager=detector.manager();top=manager.GetTopVolume()
        names=[str(top.GetNode(i).GetVolume().GetName()) for i in range(top.GetNdaughters())]
        if sorted(names)!=['LArBarrel','LArEndcaps']: raise ValueError('Unexpected native roots')
        volumes={};counts=defaultdict(int);totals=defaultdict(lambda:dict(exclusive_volume_mm3=0.,mass_g=0.))
        def properties(volume):
            key=int(R.addressof(volume))
            if key not in volumes:
                assembly=bool(volume.IsAssembly());material=volume.GetMaterial();shape=volume.GetShape()
                if not assembly and not material:raise ValueError('Native material volume has no material')
                capacity=0. if volume.IsAssembly() else float(shape.Capacity())/mm**3
                displaced=sum(0. if volume.GetNode(i).GetVolume().IsAssembly() else float(volume.GetNode(i).GetVolume().GetShape().Capacity())/mm**3 for i in range(volume.GetNdaughters())) if not volume.IsAssembly() else 0.
                exclusive=capacity-displaced
                if exclusive < -max(1e-5,capacity*1e-8):raise ValueError('Negative native exclusive material volume')
                fractions=({str(int(material.GetElement(i).Z())):float(material.GetWmixt()[i]) for i in range(material.GetNelements())}
                           if material.IsMixture() else {str(int(material.GetZ())):1.}) if not assembly else {}
                volumes[key]=dict(volume=str(volume.GetName()),shape=str(shape.ClassName()),assembly=bool(volume.IsAssembly()),
                    sensitive=bool(dd4hep.Volume(volume).isSensitive()), material=str(material.GetName()) if not assembly else '__assembly__',
                    density_g_cm3=float(material.GetDensity()) if not assembly else 0.,mass_fractions_by_Z=fractions,
                    capacity_mm3=capacity,exclusive_volume_mm3=max(0.,exclusive))
            return volumes[key]
        ledger=out/'placements.jsonl'
        with ledger.open('w') as stream:
            def visit(mother,parent,path,root,depth):
                for i in range(mother.GetNdaughters()):
                    node=mother.GetNode(i);volume=node.GetVolume();name=str(node.GetName())
                    native_root=str(volume.GetName()) if depth==1 else root
                    matrix=R.TGeoHMatrix(parent);matrix.Multiply(node.GetMatrix());local=node.GetMatrix()
                    props=properties(volume)
                    row=dict(path=path+'/'+name,root=native_root,depth=depth,root_relative=depth==2,
                        centre_mm=[float(matrix.GetTranslation()[j])/mm for j in range(3)],
                        rotation=[float(matrix.GetRotationMatrix()[j]) for j in range(9)],
                        local_centre_mm=[float(local.GetTranslation()[j])/mm for j in range(3)],
                        local_rotation=[float(local.GetRotationMatrix()[j]) for j in range(9)],**props)
                    stream.write(json.dumps(row,separators=(',',':'),allow_nan=False)+'\n')
                    counts['placements']+=1;counts['sensitive']+=props['sensitive'];counts['leaves']+=not volume.GetNdaughters()
                    if not props['assembly']:
                        totals[props['material']]['exclusive_volume_mm3']+=props['exclusive_volume_mm3']
                        totals[props['material']]['mass_g']+=props['exclusive_volume_mm3']*props['density_g_cm3']/1000
                    visit(volume,matrix,row['path'],native_root,depth+1)
            visit(top,R.TGeoHMatrix(),'/'+str(top.GetName()),'',1)
        if counts['sensitive']!=43648:raise ValueError('Native sensitive placement count differs')
        manager.CheckOverlaps(1e-5*mm)
        overlaps=[dict(description=str(o.GetTitle()),penetration_mm=float(o.GetOverlap())/mm) for o in manager.GetListOfOverlaps()]
        check_sources(initial_sources)
        for p in libraries:
            if binding['library_sha256'][str(p)]!=sha(p):raise ValueError('Factory changed during native audit')
        record=dict(status='FAIL' if overlaps else 'PASS',sample=str(sample),sample_sha256=sha(sample/'sample.json'),
            compact_sha256=sha(sample/'detector.xml'),materials_sha256=sha(sample/'materials.xml'),
            library_sha256={str(p):sha(p) for p in libraries}, scientific_source_sha256=binding['scientific_source_sha256'],
            reference_binding=binding,inventory=manifest['inventory'],counts=dict(counts),material_totals=dict(totals),
            ledger_sha256=sha(ledger),overlap_tolerance_mm=1e-5,overlap_seed=43,overlaps=overlaps,
            execution=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                           source_state=source_state,dirty=bool(source_state),sources_unchanged=True,
                           auditor_sha256=sha(__file__),ROOT=R.gROOT.GetVersion()),
            volume_method='Native full solid Capacity minus direct material daughter capacities; assemblies carry no material. XML shape definitions identical by exhaustive transformation guard.')
        save(out/'snapshot.json',record);print(record['status'],dict(counts),len(overlaps),'overlaps')
        if overlaps:raise ValueError('Full ECAL native overlaps/extrusions')
    finally:
        R.DisableImplicitMT();dd4hep.Detector.destroyInstance()


def close(a,b,tolerance=1e-7):
    return len(a)==len(b) and all(math.isfinite(x) and math.isfinite(y) and abs(x-y)<=tolerance for x,y in zip(a,b))


def compare_rows(a,b):
    keys=set(a)-{'centre_mm','local_centre_mm'}
    if keys!=set(b)-{'centre_mm','local_centre_mm'} or any(a[k]!=b[k] for k in keys):
        raise ValueError('Native topology/material/shape/rotation mismatch: '+a['path'])
    shifted=a['root']=='LArEndcaps' and a['depth']>1
    delta=-math.copysign(SHIFT_MM,a['centre_mm'][2]) if shifted else 0.
    if shifted and abs(a['centre_mm'][2])<4000:raise ValueError('Ambiguous native signed endcap descendant')
    target=[*a['centre_mm'][:2],a['centre_mm'][2]+delta]
    local=list(a['local_centre_mm'])
    if shifted and a['root_relative']:local[2]-=math.copysign(SHIFT_MM,local[2])
    if not close(target,b['centre_mm']) or not close(local,b['local_centre_mm']):
        raise ValueError('Unexpected native global/local translation: '+a['path'])
    return shifted


def verify_report(path):
    path=Path(path);report=load(path)
    if report['status']!='PASS' or report['execution']['auditor_sha256']!=sha(__file__):raise ValueError('Failed/stale native audit')
    for label,item in report['snapshots'].items():
        directory=Path(item['directory']); snapshot=load(directory/'snapshot.json')
        if snapshot['execution']['dirty'] or not snapshot['execution']['sources_unchanged']:raise ValueError('Unfrozen native snapshot')
        if sha(directory/'snapshot.json')!=item['sha256'] or sha(directory/'placements.jsonl')!=snapshot['ledger_sha256']:
            raise ValueError('Changed native snapshot/ledger')
        sample=Path(snapshot['sample'])
        if sha(sample/'sample.json')!=snapshot['sample_sha256'] or sha(sample/'detector.xml')!=snapshot['compact_sha256'] or sha(sample/'materials.xml')!=snapshot['materials_sha256']:
            raise ValueError('Changed native sample artifact')
        check_sources(snapshot['scientific_source_sha256'])
        for p,digest in snapshot['library_sha256'].items():
            if sha(p)!=digest:raise ValueError('Changed native library')
        if label=='candidate':verify(sample)
    return report


def compare(args):
    records={};directories={'standard':args.reference.resolve(),'candidate':args.candidate.resolve()}
    for label,d in directories.items():
        r=load(d/'snapshot.json')
        if r['status']!='PASS' or r['overlaps'] or r['overlap_tolerance_mm']!=1e-5 or sha(d/'placements.jsonl')!=r['ledger_sha256']:
            raise ValueError('Incomplete/changed native snapshot')
        if r['execution']['auditor_sha256']!=sha(__file__) or r['execution']['dirty'] or not r['execution']['sources_unchanged']:
            raise ValueError('Native auditor changed or unfrozen source')
        records[label]=r
    a,b=records['standard'],records['candidate']
    if a['compact_sha256']!=FROZEN['detector.xml'] or b['compact_sha256']==a['compact_sha256']:
        raise ValueError('Native variant label mismatch')
    for key in ('materials_sha256','library_sha256','scientific_source_sha256','reference_binding','inventory','counts','material_totals'):
        if a[key]!=b[key]:raise ValueError('Native equivalence mismatch: '+key)
    seen=shifted=0
    with (directories['standard']/'placements.jsonl').open() as left,(directories['candidate']/'placements.jsonl').open() as right:
        for x,y in itertools.zip_longest(left,right):
            if x is None or y is None:raise ValueError('Incomplete native placement ledger')
            shifted+=compare_rows(json.loads(x),json.loads(y));seen+=1
    if seen!=a['counts']['placements'] or not shifted:raise ValueError('Native placement coverage differs')
    report=dict(status='PASS',counts=a['counts'],physical_placements_compared=seen,signed_translated_placements=shifted,
        material_totals=a['material_totals'],inventory_equal=True,barrel_fixed=True,shift_toward_IP_mm=SHIFT_MM,
        native_evidence_method='Every physical placement including material mothers and leaves compared; same native class/capacity/material/recipe/rotation; daughter-local poses fixed; exact XML proof preserves all shape and readout definitions',
        snapshots={label:dict(directory=str(d),sha256=sha(d/'snapshot.json'),sample_sha256=records[label]['sample_sha256'],compact_sha256=records[label]['compact_sha256'],library_sha256=records[label]['library_sha256']) for label,d in directories.items()},
        execution=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),auditor_sha256=sha(__file__)),
        limitations='Complete ECAL-only construction and 10 nm overlap proof; no integrated detector, engineering fit or response acceptance')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists():raise ValueError('Refusing native report overwrite')
    save(args.output,report);verify_report(args.output);print('PASS',seen,'physical placements compared')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='stage',required=True)
    a=sub.add_parser('snapshot')
    for n in ('sample','reference-run','barrel-library','endcap-library','output'):a.add_argument('--'+n,type=Path,required=True)
    a=sub.add_parser('compare')
    for n in ('reference','candidate','output'):a.add_argument('--'+n,type=Path,required=True)
    args=p.parse_args();globals()[args.stage](args)
