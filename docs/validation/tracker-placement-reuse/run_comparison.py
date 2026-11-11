"""Run fresh-process control/cache/mother observations sequentially on one node."""
import argparse
from pathlib import Path
import subprocess
import sys


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True,help='Build directory containing baseline/cache/mother, tracker/detector and reuse')
    parser.add_argument('--ddg4-library',type=Path,required=True)
    parser.add_argument('--repeats',type=int,default=2)
    args=parser.parse_args()
    if args.repeats<2:
        parser.error('Use at least two observations per variant')
    work=args.work.resolve()
    here=Path(__file__).resolve().parent
    extension='.dylib' if sys.platform=='darwin' else '.so'
    prototype=work/'reuse'/('libnODDShortStripBarrelReuse'+extension)
    runs=[]
    # Alternate direction by round to expose coarse order/warm-cache effects.
    for n in range(1,args.repeats+1):
        order=['baseline','cache','mother'] if n%2 else ['mother','cache','baseline']
        for mode in order:
            output=work/'matched-runs'/f'{mode}-{n}'
            # Existing output is an error: no silent reuse of old measurements.
            command=[sys.executable,'-B',str(here/'probe.py'),str(work/mode/'tracker.xml'),
                     str(work/'tracker/detector'),str(output),'--native-timing',
                     str(work/('libNativeTiming'+extension)),'--ddg4-library',
                     str(args.ddg4_library.resolve()),'--expected-sensors','46682',
                     '--extra-library',str(prototype),'--sensor-snapshot']
            print('Running',mode,n,flush=True)
            subprocess.run(command,check=True)
            runs+=['--run',f'{mode}={output}']
    subprocess.run([sys.executable,'-B',str(here/'summarize_comparison.py'),*runs,
                    '--output',str(work/'comparison-timings.json')],check=True)


if __name__=='__main__':
    main()
