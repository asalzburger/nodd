"""Run and bind the sparse fixture's exact requested DDSim command."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from barrel_geometry import sha
def run(directory):
    m=json.loads((directory/'fixture.json').read_text())
    if sha(directory/'fixture.xml')!=m['fixture_sha256']:raise ValueError('Stale fixture metadata')
    exe=shutil.which('ddsim')
    if not exe:raise ValueError('Installed DDSim script unavailable')
    command=[sys.executable,exe,'--compactFile',str(directory/'fixture.xml'),'--runType','batch','--numberOfEvents','1',
        '--enableGun','--gun.particle','mu-','--gun.energy','10*GeV','--gun.position',' '.join(map(str,m['position_mm'])),
        '--gun.direction',' '.join(map(str,m['direction'])),'--random.seed','42','--part.userParticleHandler','','--outputFile',str(directory/'smoke.root')]
    with (directory/'smoke.log').open('w') as log:
        r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
    record=dict(command=command,requested=dict(particle='mu-',energy='10*GeV',seed=42,events=1),
        exit_code=r.returncode,fixture_sha256=sha(directory/'fixture.xml'),root_sha256=sha(directory/'smoke.root'),
        log_sha256=sha(directory/'smoke.log'),runner_sha256=sha(__file__),ddsim_script_sha256=sha(exe))
    (directory/'run.json').write_text(json.dumps(record,indent=2)+'\n')
    if r.returncode:raise RuntimeError('DDSim failed')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);a=p.parse_args();run(a.directory)
