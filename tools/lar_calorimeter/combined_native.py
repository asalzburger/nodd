"""Merge and audit actual barrel + signed endcap LAr ECAL compacts only.

No tracker, magnet, HCAL, FCal, muon geometry or field is included. Component
material/shape/readout audits remain separate; this checks their native union.
"""
import argparse
from collections import defaultdict
from copy import deepcopy
import json
import math
from pathlib import Path
import platform
import subprocess
import xml.etree.ElementTree as ET
from barrel_geometry import ROOT, sha


def signature(node):
    return (node.tag,tuple(sorted(node.attrib.items())),(node.text or '').strip(),tuple(signature(child) for child in node))


def merge_materials(files):
    result=ET.Element('materials');names={}
    for path in files:
        root=ET.parse(path).getroot()
        if root.tag!='materials':raise ValueError('Expected standalone material definitions')
        for node in root:
            key=(node.tag,node.get('name'))
            if not key[1]:raise ValueError('Unnamed material/element')
            sig=signature(node)
            if key in names:
                if names[key]!=sig:raise ValueError('Conflicting shared material/element definition:'+str(key))
            else:names[key]=sig;result.append(deepcopy(node))
    return result


def build(barrel_compact,barrel_expected,endcap_compact,endcap_expected,directory):
    directory.mkdir(parents=True,exist_ok=True)
    components=[];source_hashes={};docs=[]
    for tag,compact,expected in [('barrel',barrel_compact,barrel_expected),('endcap',endcap_compact,endcap_expected)]:
        model=json.loads(expected.read_text());material=compact.parent/'materials.xml'
        for filename,wanted in model.get('artifact_sha256',{}).items():
            if sha(compact.parent/filename)!=wanted:raise ValueError('Stale component artifact:'+tag+'/'+filename)
        for name,wanted in model['source_sha256'].items():
            if sha(ROOT/name)!=wanted:raise ValueError('Stale component source:'+name)
            if name in source_hashes and source_hashes[name]!=wanted:raise ValueError('Conflicting component scientific source pin:'+name)
            source_hashes[name]=wanted
        tree=ET.parse(compact).getroot()
        if tree.find('fields') is not None:raise ValueError('Component unexpectedly contains a field')
        includes=tree.findall('includes/gdmlFile')
        if len(includes)!=1 or includes[0].get('ref')!='materials.xml' or len(tree.find('includes'))!=1:raise ValueError('Unexpected component include dependency')
        components.append(dict(component=tag,compact_path=str(compact.resolve()),compact_sha256=sha(compact),expected_path=str(expected.resolve()),expected_sha256=sha(expected),materials_path=str(material.resolve()),materials_sha256=sha(material),scientific_source_sha256=model['source_sha256'],physical_sensitive_elements=model['physical_sensitive_elements'],logical_channels=model['logical_channels'],envelopes=model['envelopes']))
        docs.append(tree)
    materials=merge_materials([Path(c['materials_path']) for c in components]);ET.indent(materials);ET.ElementTree(materials).write(directory/'materials.xml',encoding='utf-8',xml_declaration=True)
    combined=ET.Element('lccdd');ET.SubElement(combined,'info',name='LAYOUT002LArEcalOnly',title='Actual isolated LAr barrel and turbine endcaps',author='nODD',version='0.1',status='prototype')
    ET.SubElement(ET.SubElement(combined,'includes'),'gdmlFile',ref='materials.xml')
    define=ET.SubElement(combined,'define');definitions={}
    for doc in docs:
        for node in doc.findall('define/*'):
            name=node.get('name')
            if name in ('world_x','world_y','world_z'):continue
            sig=signature(node)
            if name in definitions and definitions[name]!=sig:raise ValueError('Conflicting compact constant:'+str(name))
            if name not in definitions:definitions[name]=sig;define.append(deepcopy(node))
    for name,value in dict(world_x=6500,world_y=6500,world_z=components[1]['envelopes']['warm_back_z_mm']+2000).items():ET.SubElement(define,'constant',name=name,value=f'{value:.17g}*mm')
    readouts=ET.SubElement(combined,'readouts');detectors=ET.SubElement(combined,'detectors');seen_ro=set();seen_det=set();seen_id=set()
    for doc in docs:
        for node in doc.findall('readouts/readout'):
            if node.get('name') in seen_ro:raise ValueError('Duplicate combined readout')
            seen_ro.add(node.get('name'));readouts.append(deepcopy(node))
        for node in doc.findall('detectors/detector'):
            if node.get('name') in seen_det or node.get('id') in seen_id:raise ValueError('Duplicate combined detector name/system ID')
            seen_det.add(node.get('name'));seen_id.add(node.get('id'));detectors.append(deepcopy(node))
    if seen_det!={'LArBarrel','LArEndcaps'}:raise ValueError('Combined scope must be ECAL barrel and endcaps only')
    ET.indent(combined);ET.ElementTree(combined).write(directory/'combined.xml',encoding='utf-8',xml_declaration=True)
    record=dict(status='PROTOTYPE compact union; native audit pending',scope='LAr ECAL only; tracker/magnet/HCAL/forward/muon systems and fields absent',components=components,scientific_source_sha256=source_hashes,combined_sha256=sha(directory/'combined.xml'),materials_sha256=sha(directory/'materials.xml'),builder_sha256=sha(__file__),overlap_seed=43,overlap_tolerance_mm=1e-5)
    (directory/'combined.json').write_text(json.dumps(record,indent=2)+'\n');return record


def validate_ray(ray):
    for key in ('eta','phi_rad','distance_mm','x_over_x0','l_over_lambda','LAr_path_mm','active_barrel_path_mm','active_endcap_path_mm'):
        if not math.isfinite(ray[key]):raise ValueError('Nonfinite combined material ray:'+key)
    for key in ('distance_mm','x_over_x0','l_over_lambda','LAr_path_mm','active_barrel_path_mm','active_endcap_path_mm'):
        if ray[key]<0:raise ValueError('Negative combined material ray:'+key)
    active=ray['active_barrel_path_mm']+ray['active_endcap_path_mm']
    if active>ray['LAr_path_mm']+1e-6:raise ValueError('Active path exceeds actual LAr path')
    if math.isclose(abs(ray['eta']),4,abs_tol=1e-12) and active>1e-7:raise ValueError('Unexpected eta4 active LAr path')


def audit(directory,barrel_library,endcap_library,output):
    import ROOT as R
    import dd4hep
    metadata=json.loads((directory/'combined.json').read_text())
    for name,key in [('combined.xml','combined_sha256'),('materials.xml','materials_sha256')]:
        if sha(directory/name)!=metadata[key]:raise ValueError('Combined artifact binding changed:'+name)
    if sha(__file__)!=metadata['builder_sha256']:raise ValueError('Combined builder identity changed')
    for name,wanted in metadata['scientific_source_sha256'].items():
        if sha(ROOT/name)!=wanted:raise ValueError('Combined scientific source changed:'+name)
    for c in metadata['components']:
        for prefix in ('compact','expected','materials'):
            if sha(Path(c[prefix+'_path']))!=c[prefix+'_sha256']:raise ValueError('Combined component artifact changed')
    R.gROOT.SetBatch(True);R.EnableImplicitMT(1);R.gRandom.SetSeed(43)
    for library in (barrel_library,endcap_library):
        if R.gSystem.Load(str(library.resolve()))<0:raise RuntimeError('Combined factory load failed')
    detector=dd4hep.Detector.getInstance();mm=float(dd4hep.mm);errors=[];rays=[]
    try:
        detector.fromXML(str((directory/'combined.xml').resolve()));manager=detector.manager()
        roots={str(manager.GetTopVolume().GetNode(i).GetVolume().GetName()):str(manager.GetTopVolume().GetNode(i).GetName()) for i in range(manager.GetTopVolume().GetNdaughters())}
        if set(roots)!={'LArBarrel','LArEndcaps'}:errors.append('Unexpected combined native systems')
        manager.CheckOverlaps(1e-5*mm)
        overlaps=[dict(description=str(x.GetTitle()),penetration_mm=float(x.GetOverlap())/mm) for x in manager.GetListOfOverlaps()]
        if overlaps:errors.append('Combined native overlaps/extrusions:'+str(len(overlaps)))
        sensitive_cache={}
        for ie in range(81):
            eta=-4+ie*.1
            for phi in (.001,.017,.37,1.11,2.29):
                direction=[math.cos(phi)/math.cosh(eta),math.sin(phi)/math.cosh(eta),math.tanh(eta)];manager.InitTrack(0,0,0,*direction);nav=manager.GetCurrentNavigator()
                distance=x0=nuclear=lar=barrel=endcap=0.;steps=0;materials=defaultdict(float);hits={'barrel':set(),'endcap':set()}
                while not nav.IsOutside() and distance<9000:
                    node=nav.GetCurrentNode()
                    if not node:raise RuntimeError('Missing native combined navigation node')
                    volume=node.GetVolume();name=str(volume.GetName());path=str(nav.GetPath());mat=volume.GetMaterial();material_name=str(mat.GetName());world=name==str(manager.GetTopVolume().GetName())
                    if name not in sensitive_cache:sensitive_cache[name]=bool(dd4hep.Volume(volume).isSensitive())
                    sensitive=sensitive_cache[name];nav.FindNextBoundaryAndStep((9000-distance)*mm);length=float(nav.GetStep())/mm
                    if not math.isfinite(length) or length<=0:raise RuntimeError('Invalid native combined boundary step')
                    distance+=length;steps+=1
                    if steps>100000:raise RuntimeError('Combined ray did not terminate')
                    if not world:
                        materials[material_name]+=length
                        radiation,nuclear_length=float(mat.GetRadLen())/mm,float(mat.GetIntLen())/mm
                        if radiation>0:x0+=length/radiation
                        if nuclear_length>0:nuclear+=length/nuclear_length
                    if material_name=='LAr':lar+=length
                    if sensitive:
                        if material_name!='LAr':raise ValueError('Combined active ECAL is not LAr')
                        chunks=path.split('/')
                        if roots['LArBarrel'] in chunks:barrel+=length;hits['barrel'].add(path)
                        elif roots['LArEndcaps'] in chunks:endcap+=length;hits['endcap'].add(path)
                        else:raise ValueError('Sensitive material outside combined ECAL')
                row=dict(eta=eta,phi_rad=phi,origin_mm=[0,0,0],direction=direction,distance_mm=distance,x_over_x0=x0,l_over_lambda=nuclear,LAr_path_mm=lar,active_barrel_path_mm=barrel,active_endcap_path_mm=endcap,barrel_sensitive_crossings=len(hits['barrel']),endcap_sensitive_crossings=len(hits['endcap']),material_path_mm=dict(materials),boundary_steps=steps)
                validate_ray(row);rays.append(row)
        output.parent.mkdir(parents=True,exist_ok=True);root_file=output.with_suffix('.root');manager.Export(str(root_file.resolve()))
        report=dict(status='FAIL' if errors else 'PASS',errors=errors,scope='Actual native union of LAr barrel and both turbine endcaps, including component services. ECAL only; no tracker, magnet, HCAL, forward/muon detector or field. Directional material/sensitive path scan, not efficiency/performance.',execution=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),python=platform.python_version(),ROOT=R.gROOT.GetVersion(),barrel_library_sha256=sha(barrel_library),endcap_library_sha256=sha(endcap_library),tool_sha256=sha(__file__),combined_record_sha256=sha(directory/'combined.json')),components=metadata['components'],scientific_source_sha256=metadata['scientific_source_sha256'],native_detector_roots=roots,overlap_seed=43,overlap_tolerance_mm=1e-5,overlaps=overlaps,material_rays=rays,ray_count=len(rays),ray_grid=dict(eta_min=-4,eta_max=4,eta_step=.1,phi_rad=[.001,.017,.37,1.11,2.29]),root_sha256=sha(root_file),combined_sha256=metadata['combined_sha256'],materials_sha256=metadata['materials_sha256'],limitations=['Component shape/material/readout validations remain their separate exact-artifact audits.','Sparse endcap saved-hit transport is separately recorded; no whole-ECAL Geant4 run is claimed.','Eta4 active path is required to be zero for this ECAL-only candidate; an empty forward reservation supplies no acceptance.'])
        output.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(overlaps),'overlaps;',len(rays),'native rays');return bool(errors)
    finally:R.DisableImplicitMT();dd4hep.Detector.destroyInstance()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='mode',required=True)
    b=sub.add_parser('build');b.add_argument('--barrel-compact',type=Path,required=True);b.add_argument('--barrel-expected',type=Path,required=True);b.add_argument('--endcap-compact',type=Path,required=True);b.add_argument('--endcap-expected',type=Path,required=True);b.add_argument('--directory',type=Path,required=True)
    a=sub.add_parser('audit');a.add_argument('--directory',type=Path,required=True);a.add_argument('--barrel-library',type=Path,required=True);a.add_argument('--endcap-library',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.mode=='build':build(args.barrel_compact,args.barrel_expected,args.endcap_compact,args.endcap_expected,args.directory);print('Built actual ECAL compact union')
    else:raise SystemExit(audit(args.directory,args.barrel_library,args.endcap_library,args.output))
