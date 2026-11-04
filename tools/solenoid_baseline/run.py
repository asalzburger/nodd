"""Reproduce DES-026 calculation from committed inputs; no geometry export."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import numpy as np
from model import solve, validate_config

ROOT = Path(__file__).resolve().parents[2]

def main():
    paths = ['tools/solenoid_baseline/baseline.json', 'detector/config/tracker.json',
             'tools/solenoid_baseline/model.py', 'tools/solenoid_baseline/run.py']
    c = json.loads((ROOT / paths[0]).read_text())
    tracker = json.loads((ROOT / paths[1]).read_text())
    validate_config(c, tracker)
    out = dict(status='PROTOTYPE / DRAFT; vacuum sizing only',
               base_revision='da5c469f4d64a711c4f466cac79ff51e83244859',
               execution_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
               execution_dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),
               python=platform.python_version(), numpy=np.__version__,
               input_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
               configuration=c, tracker_reservation=tracker, result=solve(c))
    historic = dict(c, cold_mass_length_m=6.6)
    out['historic_6p6m_control'] = solve(historic)
    path = ROOT / 'docs/validation/DES-026/sizing.json'
    path.write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(out['result'], indent=2))

if __name__ == '__main__':
    main()
