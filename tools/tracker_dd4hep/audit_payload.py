#!/usr/bin/env python3
"""Independent DES043 artifact, placement, elemental-mixture and probe audit.

No overlap check or general CSG capacity/mass estimate is performed here.
The reference native report binds the exact compact, expected record and five
libraries already executed by the full geometry validator.
"""
import argparse
from array import array
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
BASELINE='d6c4d0ddfa9e14129a3f4c426fced7c4cee0dcc4'
COMPONENTS=dict(beam='beampipe.xml',pixel='pixel-detector.xml',short_barrel='short-strip-barrel.xml',
                short_endcap='short-strip-endcap.xml',long_barrel='long-strip.xml',long_endcap='long-strip.xml')
FACTORIES=('nODDBeamPipe','nODDPixelBarrel','nODDShortStripBarrel','nODDShortStripEndcap','nODDLongStrip')
ASSEMBLY_SOURCES={
    'tools/tracker_dd4hep/'+p for p in ('export.py','services.py','aperture.py','validate.py')
}|{'detector/config/tracker.json','docs/design/inputs/DES-042-strixel-selection.json',
    'detector/config/short-strip-des043.json','tools/short_strip_redesign/inputs.json',
    'tools/short_strip_redesign/integration.py','tools/short_strip_redesign/integrated_services.py',
    'tools/short_strip_redesign/barrel_native.py'}
STRIP_SOURCES={'tools/short_strip_redesign/'+p for p in
    ('integration.py','native.py','barrel_native.py','model.py','diagnostics.py','inputs.json')
}|{'detector/config/short-strip-des043.json','tools/short_strip_barrel/export.py',
    'tools/short_strip_barrel/model.py','tools/short_strip_barrel/inputs-phi-tilted.json',
    'tools/pixel_barrel_dd4hep/materials.py','prototypes/short_strip_barrel/ShortStripBarrel.cpp',
    'prototypes/short_strip_endcap/ShortStripEndcap.cpp'}
PROBE_COUNTS={'Barrel backing window':16128,'Barrel backing retained':8064,
    'Barrel finite pipe saddle':32256,'Barrel titanium surface':32256,'Barrel direct cold window':48384,
    'Cold support retained outside all module windows':432,'Finite backing retained outside window':4752,
    'Backing window':4752,'Finite pipe saddle contact':9504,'Finite titanium contact surface':9504,
    'Direct insert cold window':14256}
SOURCE_DIRS=('tools/beampipe/','tools/short_strip_redesign/','tools/short_strip_barrel/',
    'tools/short_strip_endcap/','tools/long_strip_barrel/','tools/long_strip_endcap/',
    'tools/pixel_barrel_dd4hep/','tools/pixel_detector_dd4hep/','tools/pixel_endcap_support/',
    'tools/pixel_support/','tools/module_layout/','tools/pixel_disc_optimization/',
    'tools/pixel_disc_support_variants/')


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])


def require(condition,message):
    if not condition:raise ValueError(message)


def contract(expected):
    """A missing source/component/probe declaration is a hard failure."""
    require(set(expected.get('assembly_source_hashes',{}))==ASSEMBLY_SOURCES,'Incomplete authoritative assembly source coverage')
    components=expected.get('components',[])
    require([c.get('name') for c in components]==list(COMPONENTS),'Incomplete or reordered six-component contract')
    require(set(expected.get('source_hashes',{}))==set(COMPONENTS),'Incomplete component artifact coverage')
    for component in components:
        name=component['name']
        require(set(expected['source_hashes'][name])=={COMPONENTS[name],'materials.xml','expected.json'},'Incomplete artifact coverage: '+name)
        if name in ('short_barrel','short_endcap'):
            require(set(component.get('provenance',{}).get('source_hashes',{}))==STRIP_SOURCES,'Incomplete DES043 source coverage: '+name)
    require(expected.get('short_strip_integration',{}).get('design')=='DES-043' and expected.get('historical_short_strips') is False,'Require actual selected DES043 baseline')
    entities=expected.get('entities',[])
    require(entities and len({e['name'] for e in entities})==len(entities),'Empty or repeated expected physical names')
    require(sum(e['role']=='sensitive' for e in entities)==46682,'Incomplete 46682-plane contract')
    require(len({(e['ids']['system'],e['ids']['layer']) for e in entities if e['role']=='sensitive'})==54,'Incomplete 54-group contract')
    probes=expected.get('shape_probes',[])
    require(len(probes)==180288 and dict(Counter(p.get('reason') for p in probes))==PROBE_COUNTS,'Incomplete 180288-contact-probe contract')
    solids={e['name'] for e in entities if 'material' in e}
    for probe in probes:
        require(probe.get('name') in solids and type(probe.get('inside')) is bool
            and isinstance(probe.get('point_mm'),list) and len(probe['point_mm'])==3
            and all(math.isfinite(v) for v in probe['point_mm']),'Invalid finite contact probe')


def source_guards(expected,revision):
    contract(expected)
    revision=git('rev-parse','--verify',revision+'^{commit}').decode().strip()
    paths=git('ls-tree','-r','--name-only',revision).decode().splitlines()
    required=set(ASSEMBLY_SOURCES)|STRIP_SOURCES
    required|={p for p in paths if p.startswith(SOURCE_DIRS) and p.endswith(('.py','.json'))}
    required|={p for p in paths if p.startswith('detector/config/') and p.endswith('.json')}
    required|={p for p in paths if p.startswith(('detector/src/Pixel','detector/include/nodd/Pixel')) and p.endswith(('.cpp','.hpp'))}
    required|={'detector/src/BeamPipe.cpp','prototypes/long_strip_barrel/LongStrip.cpp'}
    declared=dict(expected['assembly_source_hashes'])
    for component in expected['components']:
        for key in ('source_hashes','endcap_source_hashes'):
            for path,digest in component.get('provenance',{}).get(key,{}).items():
                if path in declared:require(declared[path]==digest,'Conflicting source declaration: '+path)
                declared[path]=digest;required.add(path)
    hashes={}
    for path in sorted(required):
        pinned=hashlib.sha256(git('show',revision+':'+path)).hexdigest()
        require(sha(ROOT/path)==pinned,'Executing scientific source differs from pin: '+path)
        if path in declared:require(declared[path]==pinned,'Declared source differs from pin: '+path)
        hashes[path]=pinned
    config=json.loads((ROOT/'detector/config/tracker.json').read_text())
    require(expected['config']==config,'Authoritative tracker configuration differs')
    selection=json.loads((ROOT/config['short_strip_config']).read_text())
    require(expected['short_strip_integration']==selection,'Authoritative DES043 selection differs')
    require(expected['pixel_config']==config['pixel_config'] and expected['pixel_config_sha256']==sha(ROOT/config['pixel_config']),'Authoritative pixel configuration differs')
    require(expected['strixel_selection_sha256']==sha(ROOT/config['strixel_selection']),'Authoritative strixel selection differs')
    return dict(source_revision=revision,protected_source_count=len(hashes),
        protected_source_manifest_sha256=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest())


def required_xml():
    result={'tracker.xml','materials.xml','components/pixel/barrel/pixel-barrel.xml','components/pixel/barrel/materials.xml'}
    for component,filename in COMPONENTS.items():result|={f'components/{component}/{filename}',f'components/{component}/materials.xml'}
    return result


def expected_metadata(data,component,revision):
    """Normalize only Git execution identity, never scientific source hashes."""
    if component=='pixel':
        require(data['provenance']['source_revision']==revision,'Unexpected pixel generation revision')
        data['provenance']['source_revision']='<generation-head>'
    elif component in ('short_barrel','short_endcap'):
        require(data['provenance']['generation_source_revision']==revision,'Unexpected DES043 generation revision')
        data['provenance']['generation_source_revision']='<generation-head>'
    elif component in ('long_barrel','long_endcap'):
        execution=data['provenance']['execution']
        require(execution['commit']==revision and type(execution['dirty']) is bool,'Unexpected long-strip execution revision')
        execution['commit']='<generation-head>';execution['dirty']='<working-tree-state>'
    return data


def compare_artifacts(actual,fresh,expected,source_revision,fresh_revision):
    """Exact XML bytes plus exact expected data with narrow Git-only metadata."""
    actual,fresh=Path(actual),Path(fresh)
    ax={p.relative_to(actual).as_posix() for p in actual.rglob('*.xml')}
    fx={p.relative_to(fresh).as_posix() for p in fresh.rglob('*.xml')}
    require(ax==fx==required_xml(),'Incomplete or unexpected XML artifact set')
    xml={}
    for name in sorted(ax):
        first,second=sha(actual/name),sha(fresh/name)
        require(first==second,'Producer/XML byte mismatch: '+name);xml[name]=first
    for component,files in expected['source_hashes'].items():
        for name,digest in files.items():
            require(sha(actual/'components'/component/name)==digest,'Component artifact declaration mismatch: '+component+'/'+name)
    actual_json={p.relative_to(actual).as_posix() for p in actual.rglob('expected.json')}
    fresh_json={p.relative_to(fresh).as_posix() for p in fresh.rglob('expected.json')}
    required={'expected.json','components/pixel/barrel/expected.json'}|{f'components/{c}/expected.json' for c in COMPONENTS}
    require(actual_json==fresh_json==required,'Incomplete expected-record artifact set')
    records={};normalized=[]
    for name in sorted(required-{'expected.json'}):
        a,b=sha(actual/name),sha(fresh/name);records[name]=dict(actual_sha256=a,regenerated_sha256=b)
        if a!=b:
            component='pixel' if name=='components/pixel/barrel/expected.json' else name.split('/')[1]
            one=expected_metadata(json.loads((actual/name).read_text()),component,source_revision)
            two=expected_metadata(json.loads((fresh/name).read_text()),component,fresh_revision)
            require(one==two,'Regenerated expected payload mismatch: '+name)
            normalized.append(name)
    a,b=sha(actual/'expected.json'),sha(fresh/'expected.json')
    records['expected.json']=dict(actual_sha256=a,regenerated_sha256=b)
    if a!=b:
        one=json.loads((actual/'expected.json').read_text());two=json.loads((fresh/'expected.json').read_text())
        for obj,revision in ((one,source_revision),(two,fresh_revision)):
            for component in obj['components']:
                expected_metadata(component,component['name'],revision)
            for component in COMPONENTS:obj['source_hashes'][component]['expected.json']='<separately-checked-record>'
        require(one==two,'Regenerated combined expected payload mismatch')
        normalized.append('expected.json')
    return dict(xml_count=len(xml),xml_sha256=xml,expected_record_count=len(records),expected_records=records,
        git_metadata_only_normalized=normalized,
        normalization_scope='Only declared generation revision and dirty state, plus separately checked expected-record link hashes; all scientific payload/source hashes are exact')


def resolve_recipe(name,recipes,elements,cache=None,trail=()):
    """Resolve nested mass fractions and natural-element atom counts to Z."""
    cache={} if cache is None else cache
    if name in cache:return cache[name]
    require(name not in trail,'Cyclic material recipe: '+name)
    if name in elements:return {int(elements[name]['Z']):1.}
    require(name in recipes,'Unknown material/element reference: '+name)
    recipe=recipes[name];composition=recipe.get('composition',{});basis=recipe.get('basis')
    require(composition and all(math.isfinite(v) and v>=0 for v in composition.values()),'Invalid material composition: '+name)
    if basis=='atom_count':
        require(all(k in elements and v>0 for k,v in composition.items()),'Atom-count recipe must use explicit natural elements: '+name)
        weights={k:v*elements[k]['A'] for k,v in composition.items()};total=sum(weights.values())
        fractions={k:v/total for k,v in weights.items()}
    else:
        require(basis=='mass_fraction' and math.isclose(sum(composition.values()),1.,rel_tol=0,abs_tol=1e-10),'Invalid mass-fraction recipe: '+name)
        fractions=composition
    result=defaultdict(float)
    for ref,fraction in fractions.items():
        for z,value in resolve_recipe(ref,recipes,elements,cache,trail+(name,)).items():result[z]+=fraction*value
    cache[name]=dict(result);return cache[name]


def native_fractions(material):
    """Read TGeoMixture's flattened elemental mass weights, including A/Z."""
    if material.IsMixture():
        count=int(material.GetNelements())
        return [(float(material.GetZmixt()[i]),float(material.GetAmixt()[i]),float(material.GetWmixt()[i])) for i in range(count)]
    return [(float(material.GetZ()),float(material.GetA()),1.)]


def compare_material(name,density,components,recipes,elements,cache=None):
    require(name in recipes,'Undeclared native material: '+name)
    recipe=recipes[name];target=resolve_recipe(name,recipes,elements,cache)
    require(math.isfinite(density) and math.isclose(density,recipe['density_g_cm3'],rel_tol=1e-6,abs_tol=1e-9),'Native density differs: '+name)
    table={int(e['Z']):e for e in elements.values()};observed=defaultdict(float);max_a=0.
    require(components and all(all(math.isfinite(v) for v in row) for row in components),'Nonfinite native mixture: '+name)
    for z,a,fraction in components:
        require(z==round(z) and int(z) in table and fraction>=0,'Unexpected native elemental constituent: '+name)
        natural=table[int(z)]['A'];delta=abs(a-natural)/natural;max_a=max(max_a,delta)
        require(math.isclose(a,natural,rel_tol=1e-9,abs_tol=1e-8),'Native natural-element atomic mass differs: '+name)
        observed[int(z)]+=fraction
    require(math.isclose(sum(observed.values()),1.,rel_tol=0,abs_tol=1e-9),'Native elemental weights are not normalized: '+name)
    maximum=max(abs(observed.get(z,0.)-target.get(z,0.)) for z in set(observed)|set(target))
    require(maximum<=1e-9,'Native elemental mass fractions differ: '+name)
    return dict(maximum_element_mass_fraction_residual=maximum,maximum_relative_atomic_mass_residual=max_a,
        relative_density_residual=abs(density-recipe['density_g_cm3'])/recipe['density_g_cm3'])


def material_contract(expected,materials_path):
    elements={e['name']:e for e in json.loads((ROOT/'detector/config/elements.json').read_text())['elements']}
    doc=ET.parse(materials_path).getroot();xml_elements={}
    for node in doc.findall('element'):
        require(node.get('name') not in xml_elements,'Repeated XML natural element')
        xml_elements[node.get('name')]=dict(Z=int(node.get('Z')),A=float(node.find('atom').get('value')))
    require(xml_elements=={k:dict(Z=v['Z'],A=v['A']) for k,v in elements.items()},'XML natural elements differ from centralized A/Z table')
    xml_recipes={}
    for node in doc.findall('material'):
        name=node.get('name');require(name not in xml_recipes,'Repeated XML material: '+name)
        fractions=node.findall('fraction');atoms=node.findall('composite')
        require(bool(fractions)!=bool(atoms),'Mixed or empty XML recipe: '+name)
        density=node.find('D');require(density is not None and density.get('unit')=='g/cm3','Unsupported material density unit: '+name)
        xml_recipes[name]=dict(density_g_cm3=float(density.get('value')),basis='mass_fraction' if fractions else 'atom_count',
            composition={child.get('ref'):float(child.get('n')) for child in fractions+atoms})
    recipes=dict(expected['materials'])
    # The passive BeamPipe has a separate expected schema. Its two exact names
    # and Be recipe are audited explicitly, never exempted as unknown payload.
    require(set(xml_recipes)==set(recipes)|{'Beryllium'},'Unexpected/absent generated material recipe')
    recipes['Beryllium']=dict(density_g_cm3=expected['beam']['config']['density_g_cm3'],basis='mass_fraction',composition={'Be':1.})
    cache={};xml_cache={}
    for name in recipes:
        require(math.isclose(recipes[name]['density_g_cm3'],xml_recipes[name]['density_g_cm3'],rel_tol=1e-12,abs_tol=1e-15),'Expected/XML density differs: '+name)
        a=resolve_recipe(name,recipes,elements,cache);b=resolve_recipe(name,xml_recipes,elements,xml_cache)
        require(set(a)==set(b) and all(abs(a[k]-b[k])<=1e-12 for k in a),'Expected/XML elemental recipe differs: '+name)
    return recipes,elements


def expected_solids(expected):
    result=Counter(e['name'] for e in expected['entities'] if 'material' in e)
    require('BeamPipe_wall' not in result and 'BeamPipe_bore' not in result,'BeamPipe schema changed; remove explicit bridge before reuse')
    result.update({'BeamPipe_wall':1,'BeamPipe_bore':1})
    return result


def compare_placements(expected_counts,observed_counts):
    errors=[]
    for name in sorted(set(expected_counts)|set(observed_counts)):
        if expected_counts.get(name,0)!=observed_counts.get(name,0):
            errors.append(f'Native solid multiplicity differs: {name} ({observed_counts.get(name,0)} versus {expected_counts.get(name,0)})')
    return errors


def native_audit(compact,expected,libs,recipes,elements):
    import ROOT as R
    import dd4hep
    R.gROOT.SetBatch(True)
    for lib in libs:
        require(R.gSystem.Load(str(lib.resolve()))>=0,'Cannot load native factory: '+lib.name)
    detector=dd4hep.Detector.getInstance();errors=[];observed=Counter();shape_map={};used={};cache={};maxima=defaultdict(float)
    expected_counts=expected_solids(expected);expected_by_name={e['name']:e for e in expected['entities'] if 'material' in e}
    expected_by_name.update(BeamPipe_wall=dict(material='Beryllium',role='passive'),BeamPipe_bore=dict(material='Vacuum',role='passive'))
    world_count=assemblies=solid_count=0
    try:
        detector.fromXML(str(compact.resolve()))
        def visit(node,depth):
            nonlocal world_count,assemblies,solid_count
            volume=node.GetVolume();name=str(volume.GetName());assembly=bool(volume.IsAssembly())
            if depth==0:
                require(not assembly and name=='world_volume','World exemption requires the unique DD4hep root container')
                require(str(volume.GetMaterial().GetName())=='Air','World container must use declared Air')
                world_count+=1
            elif assembly:assemblies+=1
            else:
                solid_count+=1;observed[name]+=1
                if name not in expected_counts:errors.append('Unexpected non-assembly native solid: '+name)
                else:
                    shape_map[name]=volume.GetShape()
                    target=expected_by_name[name]
                    if str(volume.GetMaterial().GetName())!=target['material']:errors.append('Native placement material differs: '+name)
                    if bool(dd4hep.Volume(volume).isSensitive())!=(target['role']=='sensitive'):errors.append('Native sensitivity differs: '+name)
            if not assembly:
                material=volume.GetMaterial();mname=str(material.GetName())
                if mname not in used:
                    used[mname]=True
                    try:
                        result=compare_material(mname,float(material.GetDensity()),native_fractions(material),recipes,elements,cache)
                        for key,value in result.items():maxima[key]=max(maxima[key],value)
                    except ValueError as error:errors.append(str(error))
            for index in range(volume.GetNdaughters()):visit(volume.GetNode(index),depth+1)
        visit(detector.manager().GetTopNode(),0)
        errors.extend(compare_placements(expected_counts,observed))
        checked=0
        for probe in expected['shape_probes']:
            shape=shape_map.get(probe['name'])
            if shape is None:errors.append('Missing probed native solid: '+probe['name']);continue
            contains=bool(shape.Contains(array('d',[v*float(dd4hep.mm) for v in probe['point_mm']])))
            if contains!=probe['inside']:errors.append('Finite contact/window probe differs: '+probe['name'])
            checked+=1
        require(world_count==1,'Require exactly one explicitly exempt world container')
        return dict(errors=errors,solid_placements=solid_count,expected_solid_placements=sum(expected_counts.values()),
            distinct_solid_names=len(observed),assembly_placements=assemblies,world_container_exemptions=world_count,
            world_exemption_reason='Only the DD4hep root Air container; subsystem solids, including both passive BeamPipe solids, require exact named multiplicities',
            explicit_beampipe_bridge=['BeamPipe_wall','BeamPipe_bore'],materials_checked=len(used),
            shape_probes_checked=checked,probe_counts=dict(Counter(p['reason'] for p in expected['shape_probes'])),mixture_tolerances=dict(mass_fraction_absolute=1e-9,density_relative=1e-6,density_absolute_g_cm3=1e-9,atomic_mass_relative=1e-9,atomic_mass_absolute_g_mol=1e-8),
            **dict(maxima),root_version=str(R.gROOT.GetVersion()))
    finally:
        dd4hep.Detector.destroyInstance()
        if R.gGeoManager:R.gGeoManager.Delete()


def bind_reference(report,compact,expected_path,libs,revision):
    execution=report.get('execution',{})
    require(execution.get('revision')==revision,'Reference native report executed a different source revision')
    hashes=execution.get('hashes',{})
    for path in [compact,expected_path,*libs]:
        require(hashes.get(path.name)==sha(path),'Reference native artifact/library differs: '+path.name)
    return dict(status=report.get('status'),source_revision=revision,
        artifact_sha256={p.name:sha(p) for p in [compact,expected_path,*libs]})


def run(args):
    expected_path=args.compact.with_name('expected.json')
    expected=json.loads(expected_path.read_text());source=source_guards(expected,args.source_revision)
    revision=source['source_revision'];suffix='.dylib' if sys.platform=='darwin' else '.so'
    libs=[args.library_dir/('lib'+name+suffix) for name in FACTORIES]
    reference=bind_reference(json.loads(args.native_report.read_text()),args.compact,expected_path,libs,revision)
    originals={p:sha(p) for p in [args.compact,expected_path,args.compact.with_name('materials.xml'),*libs,Path(__file__)]}
    fresh_revision=git('rev-parse','HEAD').decode().strip()
    with tempfile.TemporaryDirectory(prefix='des043-payload-') as temporary:
        fresh=Path(temporary)/'tracker'
        subprocess.run([sys.executable,'-B',str(ROOT/'tools/tracker_dd4hep/export.py'),'--output',str(fresh)],check=True,stdout=subprocess.DEVNULL)
        artifacts=compare_artifacts(args.compact.parent,fresh,expected,revision,fresh_revision)
    recipes,elements=material_contract(expected,args.compact.with_name('materials.xml'))
    native=native_audit(args.compact,expected,libs,recipes,elements)
    source_guards(expected,revision)
    require(all(sha(path)==digest for path,digest in originals.items()),'Checker/input/library changed during supplementary audit')
    return dict(status='PASS' if not native['errors'] else 'FAIL',errors=native.pop('errors'),source=source,
        artifacts=artifacts,reference_native=reference,native=native,
        checker=dict(sha256=sha(__file__),python=platform.python_version(),execution_revision=fresh_revision,
            working_tree_dirty=bool(git("status","--porcelain").strip()),
            source_scope="The frozen revision pins geometry sources; the checker SHA identifies its separately introduced working-tree bytes."),
        scope='Supplementary payload audit only. General CSG mass remains bounded; overlaps are not rerun. No engineering acceptance.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--compact',type=Path,required=True);p.add_argument('--library-dir',type=Path,required=True)
    p.add_argument('--native-report',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--source-revision',default=BASELINE)
    a=p.parse_args()
    try:report=run(a)
    except Exception as error:
        message=str(error).replace(str(ROOT)+'/', '').replace(str(ROOT),'<repo>')
        message=re.sub(r"(?<![\w.])/(?:[^\s'\"]+)",'<local-path>',message)
        report=dict(status='FAIL',errors=[message],checker=dict(sha256=sha(__file__)),scope='Supplementary payload audit did not complete')
    report['error_count']=len(report['errors']);report['errors']=report['errors'][:40]
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(status=report['status'],errors=report['errors'][:5])))
    return report['status']!='PASS'


if __name__=='__main__':raise SystemExit(main())
