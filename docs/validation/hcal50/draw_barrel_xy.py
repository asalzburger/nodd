"""True z=0 section of the maintained DES045 barrel-sector placement graph."""
import hashlib
import json
import math
from collections import Counter
from functools import lru_cache
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch, Polygon, Rectangle, Patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools/hcal_response'))
from model import build, common, load, sha
from export import barrel

PALETTE = {
    'Steel absorber': '#f2d2b1',
    'Scintillator core': '#cc6600',
    'PCB / electronics': '#e3a15e',
    'Cooling / thermal contact': '#edbb87',
    'Aluminium supports / skins': '#d9893c',
    'Reflector / insulation': '#fbe9d7',
}


def number(node, key):
    value = node.get(key)
    if not value.endswith('*mm'): raise ValueError('Explicit mm required: ' + key)
    return float(value[:-3])


def rectangle(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def orient(vertices, positive=True):
    area = sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(vertices, vertices[1:]+vertices[:1]))
    return vertices if (area > 0) == positive else list(reversed(vertices))


def primitive_section(part, axial):
    """Return carrier-(u,w) outer boundary and holes; v=axial is fixed."""
    kind = part.get('shape_kind', part.get('kind'))
    dims, center, frame = part['dimensions_mm'], part['center_mm'], part['frame']
    if kind == 'box':
        half = [dims[k]/2 for k in ('sx','sy','sz')]
        ext = [sum(abs(frame[i][j])*half[i] for i in range(3)) for j in range(3)]
        if not center[1]-ext[1] < axial < center[1]+ext[1]: return None
        return [rectangle(center[0]-ext[0], center[0]+ext[0], center[2]-ext[2], center[2]+ext[2])]
    if kind != 'tube': raise ValueError('Unsupported common-unit primitive: ' + kind)
    axis = next(i for i,v in enumerate(frame[2]) if abs(v) == 1)
    radius, inner, length = dims['rmax'], dims['rmin'], dims['length']
    if axis == 1:
        if not abs(axial-center[1]) < length/2: return None
        def circle(r):
            return [(center[0]+r*math.cos(2*math.pi*i/128), center[2]+r*math.sin(2*math.pi*i/128)) for i in range(128)]
        return [circle(radius)] + ([circle(inner)] if inner else [])
    offset = axial-center[1]
    if abs(offset) >= radius: return None
    width = math.sqrt(radius*radius-offset*offset)
    half_inner = math.sqrt(inner*inner-offset*offset) if abs(offset) < inner else None
    if axis == 2:
        result = [rectangle(center[0]-width, center[0]+width, center[2]-length/2, center[2]+length/2)]
        if half_inner is not None: result.append(rectangle(center[0]-half_inner, center[0]+half_inner, center[2]-length/2, center[2]+length/2))
        return result
    result = [rectangle(center[0]-length/2, center[0]+length/2, center[2]-width, center[2]+width)]
    if half_inner is not None: result.append(rectangle(center[0]-length/2, center[0]+length/2, center[2]-half_inner, center[2]+half_inner))
    return result


def part_category(p):
    if p['role'] == 'sensitive': return 'Scintillator core'
    if p['role'] in ('reflector','rear_insulation'): return 'Reflector / insulation'
    if p['role'] in ('cold_plate','cooling_tube','coolant','thermal_contact','thermal_post'):
        return 'Cooling / thermal contact'
    if p['role'] in ('front_skin','rear_skin','side_rail','ported_rail'):
        return 'Aluminium supports / skins'
    return 'PCB / electronics'


def generate_section():
    report = build(); unit,_ = common()
    module = load('_hcal_xy_unit', 'tools/hcal_readout/readout.py')
    root = ET.Element('detector'); barrel(root, report, unit)
    templates = {n.get('name'): n for n in root.findall('template')}
    sector = templates['BarrelSector']; depth = report['depth']['total_mm']
    center_r = report['config']['barrel']['front_apothem_mm'] + depth/2
    regions = []; counts = Counter(); carriers = Counter(); steel_layers = set()

    @lru_cache(maxsize=None)
    def unit_section(axial):
        result = []
        for p in unit['parts']:
            loops = primitive_section(p, axial)
            if loops is None: continue
            for cut in p['cuts']:
                sliced = primitive_section(module.global_cut(p, cut), axial)
                if sliced:
                    if len(sliced) != 1: raise ValueError('Annular cutters are outside the common-unit contract')
                    loops.append(sliced[0])
            result.append((part_category(p), loops, p['name']))
        return result

    def prism(shape, center, axial=0.):
        if shape.get('kind') != 'arb8': raise ValueError('Expected actual exported barrel arb8')
        vertices = [(number(n,'x'), number(n,'y')) for n in shape.findall('vertex')]
        if not min(y for _,y in vertices) < axial-center[1] < max(y for _,y in vertices): return None
        half = number(shape,'half_z'); front,back = vertices[:4],vertices[4:]
        return [(center[2]-half,min(x for x,_ in front)), (center[2]+half,min(x for x,_ in back)),
                (center[2]+half,max(x for x,_ in back)), (center[2]-half,max(x for x,_ in front))]

    outline = prism(sector.find('shape'), [0,0,center_r])
    for p in sector.findall('place'):
        xyz = [number(p,k) for k in ('x','y','z')]
        for i in range(3):
            for j in range(3):
                if abs(float(p.get(f'a{i}{j}'))-(i==j)) > 1e-12: raise ValueError('Unexpected sector-child rotation')
        name = p.get('ref'); xyz[2] += center_r
        if name == 'BarrelCarrier':
            if not abs(xyz[1]) < unit['fixture']['carrier_size_mm'][1]/2: continue
            layer = int(p.get('layer')); carriers[layer] += 1
            # Exported carrier Box is centred; original hardware is front-based.
            radial_front = xyz[2]-unit['fixture']['carrier_size_mm'][2]/2
            for category,loops,part_name in unit_section(-xyz[1]):
                world = [[(radial_front+w, xyz[0]+u) for u,w in loop] for loop in loops]
                regions.append((category,world,layer,part_name)); counts[category] += 1
        else:
            boundary = prism(templates[name].find('shape'),xyz)
            if boundary is None: continue
            category = 'Steel absorber' if name.startswith('BarrelSteel') else 'Aluminium supports / skins'
            layer = int(name.removeprefix('BarrelSteel')) if name.startswith('BarrelSteel') else None
            if layer is not None: steel_layers.add(layer)
            regions.append((category,[boundary],layer,name)); counts[category] += 1
    if steel_layers != set(range(60)): raise ValueError('Section must contain all60 actual absorber layers')
    if set(carriers) != steel_layers: raise ValueError('Missing cut readout row')
    if any(carriers[q['layer']] != len(q['columns_mm']) for q in report['barrel_layers']):
        raise ValueError('Section includes a projection rather than one intersected axial row')
    return report, regions, outline, counts, carriers


def paint(ax, regions, radial_zero=0, scale=1, extent=None):
    for category,loops,_,_ in regions:
        flat = loops[0]
        if extent:
            x0,x1,y0,y1=extent
            if max(x for x,y in flat)<x0 or min(x for x,y in flat)>x1 or max(y for x,y in flat)<y0 or min(y for x,y in flat)>y1: continue
        vertices=[];codes=[]
        for index,loop in enumerate(loops):
            xy=[((x-radial_zero)*scale,y*scale) for x,y in loop]
            xy=orient(xy,positive=index==0)
            vertices.extend(xy+[xy[0]])
            codes.extend([MPath.MOVETO]+[MPath.LINETO]*(len(xy)-1)+[MPath.CLOSEPOLY])
        edge='#bf925f' if category=='Steel absorber' else 'none'
        ax.add_patch(PathPatch(MPath(vertices,codes),facecolor=PALETTE[category],edgecolor=edge,lw=.25))


def main():
    report,regions,outline,counts,carriers = generate_section()
    out=Path(__file__).resolve().parent/'barrel-xy';out.mkdir(exist_ok=True)
    b=report['config']['barrel']; front=b['front_apothem_mm'];back=b['outer_apothem_mm']
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':200,'svg.hashsalt':'nodd-hcal-barrel-xy'})
    fig,(overview,detail)=plt.subplots(1,2,figsize=(13.5,8.6),gridspec_kw={'width_ratios':[2,1]},layout='constrained')
    paint(overview,regions,scale=.001)
    overview.add_patch(Polygon([(x/1000,y/1000) for x,y in outline],fill=False,edgecolor='#8d5528',lw=1.1))
    overview.set(xlim=(2.95,5.96),ylim=(-1.43,1.39),aspect='equal',xlabel='Global x [m] — radial direction',ylabel='Global y [m]',title='Complete sector · 60 sampling layers')
    overview.annotate('',xy=(front/1000,-1.31),xytext=(back/1000,-1.31),arrowprops={'arrowstyle':'<->','color':'#555555'})
    overview.text((front+back)/2000,-1.36,'2.590 m total depth · 3.130 → 5.720 m face apothems',ha='center',fontsize=9)
    roi=(front,front+5*43,-220,220)
    overview.add_patch(Rectangle((front/1000,-.22),.215,.44,fill=False,edgecolor='#654421',lw=1.2,ls='--'))
    paint(detail,regions,radial_zero=front,extent=roi)
    detail.set(xlim=(0,215),ylim=(-220,220),aspect='equal',ylabel='Global y [mm]',title='Front five layers\nBoxed region, equal scales')
    detail.set_xlabel('x − 3130 mm [mm]\n30 mm steel + 12 mm carrier\n+ 1 mm installation gap per layer',fontsize=9)
    for i in range(5):detail.text(i*43+15,205,str(i+1),ha='center',fontsize=9,color='#785535')
    for ax in (overview,detail):ax.set_axisbelow(True);ax.grid(alpha=.13,lw=.6)
    handles=[Patch(facecolor=color,edgecolor='#c99d70',label=label) for label,color in PALETTE.items()]
    fig.legend(handles=handles,loc='outside lower center',ncol=3,fontsize=9,frameon=False)
    fig.suptitle('HCAL barrel sector · actual x–y section at z = 0\nSector 0 centred on +x · 22.5° mechanical pitch · DES-045 prototype',fontsize=16)
    for ext in ('png','pdf'):
        p=out/f'hcal-barrel-sector-xy.{ext}'
        fig.savefig(p)
    plt.close(fig)
    sources=[Path(__file__),ROOT/'tools/hcal_response/model.py',ROOT/'tools/hcal_response/config.json',ROOT/'tools/hcal_response/export.py',ROOT/'tools/hcal_readout/readout.py',ROOT/'prototypes/hcal_response/HCAL.cpp']
    proof={'status':'PASS','scope':'Exact transverse z=0 cut of one exported barrel sector; finite primitive sections and original contained CSG cuts, no geometry change or depth exaggeration. Circular tube sections polygonized for rendering.',
           'source_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
           'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sources},
           'geometry_sources':report['source_sha256'],'z_mm':0,'sector':0,'sector_width_deg':360/report['config']['sectors'],
           'steel_layers':60,'carriers_in_cut':sum(carriers.values()),'carriers_per_layer':dict(carriers),
           'visible_part_sections_by_category':dict(counts),'front_apothem_mm':front,'back_apothem_mm':back,
           'detail_global_bounds_mm':list(roi),'render_sha256':{p.name:sha(p) for p in sorted(out.iterdir()) if p.suffix in ('.png','.pdf','.svg')}}
    (out/'provenance.json').write_text(json.dumps(proof,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:proof[k] for k in ('steel_layers','carriers_in_cut','visible_part_sections_by_category')},indent=2))


if __name__=='__main__':main()
