"""Static ODD hardware-description audit; no DD4hep/Geant4 execution or response.

Whitelist arithmetic evaluator in millimetres, explicit pinned source hashes.
The derived outer radii follow the inspected factory conventions, not a native
solid containment test. Unsupported expressions/recipes fail rather than guess.
"""
import argparse
import ast
import hashlib
import json
import math
import operator
import platform
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
PIN='c167363f3d4ad1540a577af99071283caf54f3a6'
FILES=['xml/detectors/CalorimeterECal.xml','xml/detectors/CalorimeterHCal.xml',
       'xml/OpenDataDetectorEnvelopes.xml','xml/OpenDataDetectorMaterials.xml',
       'xml/OpenDataDetectorCalorimeter.xml',
       'factory/calorimeter/ODDPolyhedraBarrelCalorimeter_geo.cpp',
       'factory/calorimeter/ODDPolyhedraEndcapCalorimeter_geo.cpp']


def quantity(expression,names):
    operators={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv}
    def visit(n):
        if isinstance(n,ast.Constant) and type(n.value) in (int,float):return n.value
        if isinstance(n,ast.Name):return names[n.id]
        if isinstance(n,ast.BinOp) and type(n.op) in operators:return operators[type(n.op)](visit(n.left),visit(n.right))
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub):return -visit(n.operand)
        raise ValueError('unsupported dimensional expression: '+expression)
    value=visit(ast.parse(expression,mode='eval').body)
    if not math.isfinite(value):raise ValueError('nonfinite quantity')
    return value


def names_from(trees):
    values={'mm':1.,'cm':10.,'m':1000.}
    for tree in trees:
        for node in tree.findall('.//define/constant'):
            if node.attrib['name'].startswith(('ecal_','hcal_','ECal_cell','HCal_cell')):
                values[node.attrib['name']]=quantity(node.attrib['value'],values)
    return values


def stack(det,names):
    slices=[];totals={};sensitive=0;depth=0;layers=0
    for layer in det.findall('layer'):
        repeat=int(layer.attrib['repeat'])
        if repeat<=0:raise ValueError('nonpositive layer repeat')
        layers+=repeat
        for s in layer.findall('slice'):
            t=quantity(s.attrib['thickness'],names)
            if t<=0:raise ValueError('nonpositive slice thickness')
            material=s.attrib['material'];active=s.attrib.get('sensitive')=='yes'
            slices.append(dict(material=material,thickness_mm=t,repeat=repeat,sensitive=active))
            totals[material]=totals.get(material,0)+t*repeat;depth+=t*repeat
            if active:sensitive+=repeat
    return dict(layers=layers,sensitive_planes_per_stave=sensitive,slices=slices,
                material_normal_depth_mm=totals,total_normal_depth_mm=depth)


def inventory(odd):
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=odd,text=True).strip()
    if revision!=PIN:raise ValueError('audit requires the documented ODD revision '+PIN)
    hashes={p:hashlib.sha256((odd/p).read_bytes()).hexdigest() for p in FILES}
    for p in FILES:
        original=subprocess.check_output(['git','show',PIN+':'+p],cwd=odd)
        if hashlib.sha256(original).hexdigest()!=hashes[p]:raise ValueError('modified upstream source: '+p)
    trees={p:ET.parse(odd/p).getroot() for p in FILES if p.endswith('.xml')}
    names=names_from([trees['xml/OpenDataDetectorEnvelopes.xml'],
                      trees[FILES[0]],trees[FILES[1]]])
    rows=[]
    for xmlpath in FILES[:2]:
        tree=trees[xmlpath]
        for det in tree.findall('./detectors/detector'):
            row=stack(det,names);dim=det.find('dimensions');isbarrel='Barrel' in det.attrib['name']
            n=int(quantity(dim.attrib['numsides'],names));rmin=quantity(dim.attrib['rmin'],names)
            row.update(name=det.attrib['name'],source=xmlpath,numsides=n,
                       factory=det.attrib['type'],readout=det.attrib['readout'],
                       stave_half_gap_mm=quantity(det.attrib['gap'],names),
                       r_inner_apothem_mm=rmin)
            if isbarrel:
                apothem=rmin+row['total_normal_depth_mm']
                row.update(z_half_length_mm=quantity(dim.attrib['z'],names)/2,
                           r_outer_apothem_mm=apothem,r_outer_corner_mm=apothem/math.cos(math.pi/n))
            else:
                corner=quantity(dim.attrib['rmax'],names);z=quantity(dim.attrib['zmin'],names)
                row.update(r_outer_apothem_mm=corner*math.cos(math.pi/n),r_outer_corner_mm=corner,
                           z_front_mm=z,z_back_from_stack_mm=z+row['total_normal_depth_mm'])
            readout=tree.find("./readouts/readout[@name='"+det.attrib['readout']+"']")
            seg=readout.find('segmentation')
            row['segmentation']=dict(type=seg.attrib['type'],grid_sizes_mm={k:quantity(v,names)
                for k,v in seg.attrib.items() if k.startswith('grid_size')},id=readout.find('id').text.strip())
            rows.append(row)
    mat=trees['xml/OpenDataDetectorMaterials.xml'].find("./materials/material[@name='siPCBMix']")
    if mat is None:mat=trees['xml/OpenDataDetectorMaterials.xml'].find(".//material[@name='siPCBMix']")
    d=mat.find('D')
    if d.attrib['unit']!='g/cm3':raise ValueError('unhandled density unit')
    density=float(d.attrib['value']); fractions={e.attrib['ref']:float(e.attrib['n']) for e in mat.findall('fraction')}
    if not math.isclose(sum(fractions.values()),1,abs_tol=1e-10):raise ValueError('mass fractions not normalized')
    for row in rows:
        depth=row['material_normal_depth_mm'].get('siPCBMix',0)
        row['pcb_normal_areal_mass_g_cm2']=density*depth/10
        row['pcb_copper_normal_areal_mass_g_cm2']=density*depth/10*fractions['Cu']
    return dict(status='DRAFT; static source inspection, not native construction',
                upstream_revision=PIN,source_sha256=hashes,python=platform.python_version(),
                nodd_base_revision='da5c469f4d64a711c4f466cac79ff51e83244859',
                nodd_inspected_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in [ROOT/'detector/CMakeLists.txt',ROOT/'tools/tracker_dd4hep/export.py',
                              *sorted((ROOT/'detector/src').glob('*.cpp')),*sorted((ROOT/'detector/config').glob('*.json'))]},
                auditor_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                radius_convention='Barrel dimensions.rmin is an apothem; stack thickness sets outer apothem. Endcap dimensions.rmax is converted to an apothem by the factory. Outer corner = apothem/cos(pi/numsides).',
                pcb_mixture=dict(density_g_cm3=density,element_mass_fractions=fractions),detectors=rows)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--odd-dir',type=Path,required=True)
    p.add_argument('--output',type=Path,default=ROOT/'docs/validation/DES-027/odd-inventory.json')
    a=p.parse_args();result=inventory(a.odd_dir);a.output.write_text(json.dumps(result,indent=2)+'\n')
    for r in result['detectors']:
        print(r['name'],r['layers'],'layers;',r['total_normal_depth_mm'],'mm; outer corner',round(r['r_outer_corner_mm'],3),'mm; PCB areal mass',round(r['pcb_normal_areal_mass_g_cm2'],3),'g/cm2')
