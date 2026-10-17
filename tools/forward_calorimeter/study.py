#!/usr/bin/env python3
"""Generate/check retained DES039 FCAL design evidence and optional detailed model."""
import argparse
import json
from pathlib import Path
from model import HERE, ROOT, build, report, collar_config, service_screen


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true')
    p.add_argument('--model',type=Path,help='Optional detailed model for native construction (ignored build directory recommended)')
    p.add_argument('--output',type=Path,default=ROOT/'docs/validation/DES-039/geometry.json')
    a=p.parse_args()
    model=build();contexts=json.loads((HERE/'layout-contexts.json').read_text())
    result=report(model,contexts)
    collar=build(collar_config(model["config"]))
    result["collar"]=report(collar,contexts)
    result["service_interfaces"]=service_screen(model["config"],contexts)
    result["aggregate_layout_budgets"]={}
    for name in model["config"]["layouts"]:
        n=2 if name=="LAYOUT-002" else 1
        result["aggregate_layout_budgets"][name]={"bodies":2,"collars":2 if n==2 else 0,"optical_tower_signals":192*n,"physical_sipm_pixels":3072*n,"partial_mass_kg":2*(result["inventory"]["partial_mass_per_end_kg"]+(result["collar"]["inventory"]["partial_mass_per_end_kg"] if n==2 else 0)),"nominal_electronics_heat_w":2*n*result["thermal"]["nominal"]["local_heat_per_end_w"],"stress_electronics_heat_w":2*n*result["thermal"]["stress"]["local_heat_per_end_w"],"beam_heat_w":None}
    result["collar"]["role"]="LAYOUT-002 EM transition; distinct short component in the same technology family"
    if a.model:
        collar_path=a.model.with_name("collar-model.json")
        collar_path.parent.mkdir(parents=True,exist_ok=True)
        collar_path.write_text(json.dumps(collar,indent=2)+"\n")
    content=json.dumps(result,indent=2)+'\n'
    if a.check:
        if a.output.read_text()!=content:raise SystemExit('FAIL: retained design evidence differs from inputs/model')
        print('PASS: deterministic finite geometry/material/service report for both layouts')
    else:
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(content)
        print('Wrote',a.output.relative_to(ROOT))
    if a.model:
        a.model.parent.mkdir(parents=True,exist_ok=True);a.model.write_text(json.dumps(model,indent=2)+'\n')
    print(json.dumps({'inventory':result['inventory'],'routing':result['routing'],'thermal':result['thermal']},indent=2))


if __name__=='__main__':main()
