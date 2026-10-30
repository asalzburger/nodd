"""Synthetic native-core smoke: no simulated measurements/performance claim."""
import argparse
import json
import math
from pathlib import Path
import sys


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--module-dir',type=Path,required=True)
    parser.add_argument('--config-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    import acts
    import acts.examples
    sys.path.insert(0,str(args.module_dir.resolve()))
    import nodd_gbts
    algorithm=nodd_gbts.GbtsSeeding(str(args.config_dir),acts.logging.ERROR)
    layers=json.loads((args.config_dir/'audit.json').read_text())['layers']
    results=[]
    for pt in (1.,5.,10.,100.):
        for eta in (0.,2.,-2.,3.5,-3.5):
            for charge in (-1,1):
                radius=pt/(0.000299792458*3)
                tau=math.sinh(eta)
                points=[]
                for layer in layers:
                    if layer['type']=='barrel':
                        r=layer['ref_coord_mm']
                        arc=2*radius*math.asin(r/(2*radius))
                        z=tau*arc
                        if not layer['min_bound_mm']<=z<=layer['max_bound_mm']:
                            continue
                    else:
                        z=layer['ref_coord_mm']
                        if tau==0 or z*tau<=0:
                            continue
                        arc=z/tau
                        r=2*radius*math.sin(arc/(2*radius))
                        if not layer['min_bound_mm']<=r<=layer['max_bound_mm']:
                            continue
                    phi=charge*arc/(2*radius)
                    points.append([r*math.cos(phi),r*math.sin(phi),z,layer['id']])
                points.sort(key=lambda p:math.hypot(p[0],p[1]))
                seeds=algorithm._test_points(points)
                results.append({'pt_GeV':pt,'eta':eta,'charge':charge,'fixture_points':len(points),
                                'native_seeds':len(seeds),'seed_lengths':[len(s) for s in seeds]})
    report={'status':'PASS' if all(r['native_seeds']>0 for r in results) else 'FAIL',
            'synthetic_fixture_only':True,'acts_source_revision':nodd_gbts.acts_source_revision,
            'pybind11_internals_version':nodd_gbts.pybind11_internals_version,
            'native_geometry':algorithm.statistics(),
            'effective_configuration':json.loads(algorithm.effective_configuration_json()),'results':results}
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(report))
    if report['status']!='PASS':
        raise SystemExit(1)


if __name__=='__main__':
    main()
