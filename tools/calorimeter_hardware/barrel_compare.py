"""Independent finite-box intersections versus actual native barrel ray layers."""
import argparse
import json
import math
from pathlib import Path
from barrel_layout import crossings
from model import sha


def intersects(bounds,direction):
    low,high=0.,float('inf')
    for (a,b),v in zip(bounds,direction):
        if abs(v)<1e-15:
            if not a<=0<=b:return False
            continue
        first,last=sorted((a/v,b/v));low=max(low,first);high=min(high,last)
        if high<=low:return False
    return True


def finite_layers(report,eta,phi):
    angle=(phi+math.pi/16)%(2*math.pi/16)-math.pi/16;d=[math.cos(angle)/math.cosh(eta),math.sin(angle)/math.cosh(eta),math.tanh(eta)];e=report['ecal'];half=e['sensor_active_mm']/2;result=[]
    for p in report['layers']:
        r=p['front_mm']+e['absorber_mm']+e['sensor_center_z_mm']
        for m in p['modules']:
            t,z=m['center_mm'];bounds=[(r-e['sensor_mm']/2,r+e['sensor_mm']/2),(t-half,t+half),(z-half,z+half)]
            if intersects(bounds,d):result.append(p['index']);break
    return result


def compare(expected,native):
    e=json.loads(expected.read_text());n=json.loads(native.read_text());report=e['layout_report'];errors=[];rays=[]
    if n['execution']['expected_sha256']!=sha(expected):raise ValueError('native/expected identity mismatch')
    for q in n['material_rays']:
        finite=finite_layers(report,q['eta'],q['phi']);plane=crossings(report,q['eta'],q['phi']);actual=sorted(int(k) for k in q['hits_by_layer'])
        if actual!=finite:errors.append(dict(eta=q['eta'],phi=q['phi'],native=actual,finite=finite))
        rays.append(dict(eta=q['eta'],phi=q['phi'],native_layers=actual,finite_volume_layers=finite,center_plane_layers=plane,finite_thickness_changes=len(actual)-len(plane)))
    return dict(status='PASS' if not errors else 'FAIL',errors=errors,scope='Independent finite0.5mm silicon box intersections agree with native ROOT rays; centre-plane approximation differs at boundary crossings. Not efficiency or shower response.',rays_checked=len(rays),plane_boundary_difference_cases=sum(q['native_layers']!=q['center_plane_layers'] for q in rays),native_sha256=sha(native),expected_sha256=sha(expected),checker_sha256=sha(__file__),rays=rays)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--expected',type=Path,required=True);p.add_argument('--native',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=compare(a.expected,a.native);a.output.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['rays_checked'],'rays',r['plane_boundary_difference_cases'],'plane boundary differences');raise SystemExit(0 if r['status']=='PASS' else 1)
