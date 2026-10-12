"""Independent dimension audit of the persisted, fully overlap-checked ROOT file."""
import argparse,json,math,platform,subprocess
from pathlib import Path
from model import ROOT,sha

def check(args):
    import ROOT as R,dd4hep
    R.gROOT.SetBatch(True);native=json.loads(args.native.read_text());expected=json.loads(args.expected.read_text());mm=float(dd4hep.mm);errors=[]
    if sha(args.root)!=native['root_sha256'] or sha(args.expected)!=native['execution']['expected_sha256']:raise ValueError('Audited geometry/inventory hash differs')
    manager=R.TGeoManager.Import(str(args.root.resolve()));volumes={str(v.GetName()):v for v in manager.GetListOfVolumes()}
    parts=[p for u in expected['units'] for p in u['parts'] if p['owner']=='cassette']+[p for r in expected['regions'] for p in r['parts']]
    def agree(a,b,label):
        if not math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-7):errors.append(label)
    def primitive(shape,p):
        kind=p['shape_kind'] if 'shape_kind' in p else p['kind'];q=p.get('dimensions_mm',{})
        if kind=='box':
            if str(shape.ClassName())!='TGeoBBox':errors.append('primitive type');return
            for a,b in zip((shape.GetDX(),shape.GetDY(),shape.GetDZ()),(q['sx']/2,q['sy']/2,q['sz']/2)):agree(a/mm,b,'box dimension')
        elif kind=='tube':
            if str(shape.ClassName()) not in ('TGeoTube','TGeoTubeSeg'):errors.append('primitive type');return
            for a,b in zip((shape.GetRmin(),shape.GetRmax(),shape.GetDz()),(q['rmin'],q['rmax'],q['length']/2)):agree(a/mm,b,'tube dimension')
            if str(shape.ClassName())=='TGeoTubeSeg':agree(shape.GetPhi2()-shape.GetPhi1(),360,'tube angle')
        elif kind=='xtru':
            if str(shape.ClassName())!='TGeoXtru':errors.append('primitive type');return
            points=[(shape.GetX(i)/mm,shape.GetY(i)/mm) for i in range(shape.GetNvert())]
            if len(points)!=len(p['vertices_mm']):errors.append('polygon vertex count')
            for x,y in p['vertices_mm']:
                if not any(abs(x-a)<1e-7 and abs(y-b)<1e-7 for a,b in points):errors.append('polygon vertex')
            agree(shape.GetZ(0)/mm,-p['depth_mm']/2,'polygon lower section');agree(shape.GetZ(shape.GetNz()-1)/mm,p['depth_mm']/2,'polygon upper section')
        else:errors.append('unsupported primitive')
    cuts_checked=0
    for p in parts:
        volume=volumes.get(p['name'])
        if volume is None:errors.append('missing volume:'+p['name']);continue
        shape=volume.GetShape()
        for cut in reversed(p.get('cuts',[])):
            if str(shape.ClassName())!='TGeoCompositeShape':errors.append('missing cutter');break
            node=shape.GetBoolNode()
            if str(node.ClassName())!='TGeoSubtraction':errors.append('non-subtraction CSG');break
            primitive(node.GetRightShape(),cut);matrix=node.GetRightMatrix();translation=matrix.GetTranslation();rotation=matrix.GetRotationMatrix()
            for i in range(3):
                agree(translation[i]/mm,cut['center_mm'][i],'cutter translation')
                for j in range(3):agree(rotation[3*i+j],1 if i==j else 0,'cutter rotation')
            shape=node.GetLeftShape();cuts_checked+=1
        primitive(shape,p)
    return dict(status='FAIL' if errors else 'PASS',errors=errors,scope='Dimensions/vertices/CSG cutter transforms for every unique material volume in the persisted full ROOT geometry, tied to the completed overlap audit by SHA256.',unique_material_shapes_checked=len(parts),cutters_checked=cuts_checked,tolerance_mm=1e-7,execution=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),python=platform.python_version(),ROOT=R.gROOT.GetVersion(),root_sha256=sha(args.root),native_sha256=sha(args.native),expected_sha256=sha(args.expected),checker_sha256=sha(__file__)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--native',type=Path,required=True);p.add_argument('--expected',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=check(a);a.output.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['unique_material_shapes_checked'],r['cutters_checked'],r['errors'][:5]);raise SystemExit(1 if r['errors'] else 0)
