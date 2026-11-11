"""Compare every expanded native Geant4 sensor by its DDG4 packed volume ID."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def compare(control, candidate, expected=46682):
    def index(rows):
        result = {r['id']:r for r in rows}
        if len(result) != len(rows) or len(rows) != expected:
            raise ValueError('Incomplete or duplicate Geant4 sensor inventory')
        return result
    left, right = index(control), index(candidate)
    if left.keys() != right.keys():
        raise ValueError('Expanded Geant4 packed IDs differ')
    maximum = dict(center_mm=0., u=0., v=0., normal=0., size_mm=0., density_g_cm3=0.)
    for key, row in left.items():
        other = right[key]
        if row.keys() != other.keys() or row['material'] != other['material'] or row['region'] != other['region']:
            raise ValueError('Geant4 sensor material/region/record fields differ')
        for field in maximum:
            a,b=row[field],other[field]
            if isinstance(a,list):
                if len(a) != len(b):
                    raise ValueError('Malformed sensor vector')
                if not a or not all(math.isfinite(x) for x in a+b):
                    raise ValueError('Nonfinite or empty sensor vector')
                delta=max(abs(x-y) for x,y in zip(a,b))
            else:
                if not math.isfinite(a) or not math.isfinite(b):
                    raise ValueError('Nonfinite sensor quantity')
                delta=abs(a-b)
            maximum[field]=max(maximum[field],delta)
    tolerances = dict(center_mm=1e-7,u=1e-10,v=1e-10,normal=1e-10,size_mm=1e-7,density_g_cm3=1e-12)
    if any(maximum[k] > tolerances[k] for k in maximum):
        raise ValueError('Geant4 sensor transform/dimension/density differs: '+str(maximum))
    return dict(status='PASS', expanded_sensors=expected, unique_packed_ids=expected,
                maximum_absolute_differences=maximum,tolerances=tolerances,
                limitations=['All expanded Geant4 sensitive placements checked; no event response equivalence claim.',
                             'Region names compared before the first run; this does not compare assigned cut couples.'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('control',type=Path)
    parser.add_argument('candidate',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=compare(json.loads(args.control.read_text()),json.loads(args.candidate.read_text()))
    result['sha256']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (args.control,args.candidate)}
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
