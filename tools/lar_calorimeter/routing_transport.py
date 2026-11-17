"""Serial passive-pipe Geant4 conversion, joint navigation and saved-step smoke."""
import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import resource
import shutil
import subprocess
import sys
import time

from routing import ROOT, add, dot, save, scale, sha, sub
from routing_native import inputs

CONVERSION_CPP = r'''
#include <DDG4/Geant4Mapping.h>
#include <G4Navigator.hh>
#include <G4PhysicalVolumeStore.hh>
#include <G4LogicalVolume.hh>
#include <G4VPhysicalVolume.hh>
#include <G4Material.hh>
#include <G4CutTubs.hh>
#include <G4SystemOfUnits.hh>
#include <nlohmann/json.hpp>
#include <fstream>
#include <cmath>
#include <map>
#include <stdexcept>
void nODDRoutingConversionAudit(const std::string& input,const std::string& output) {
  using nlohmann::json;json model;std::ifstream(input)>>model;
  auto* world=dd4hep::sim::Geant4Mapping::instance().data().m_world;
  if(!world)throw std::runtime_error("Missing converted routing world");
  G4Navigator navigator;navigator.SetWorldVolume(world);
  std::size_t points=0,volumes=0;std::map<std::string,double> totals;
  for(auto* physical:*G4PhysicalVolumeStore::GetInstance()) {
    auto* logical=physical->GetLogicalVolume();const std::string material=logical->GetMaterial()->GetName();
    if(material!="lArCaloSteel"&&material!="PrototypeNitrogenTwoPhase")continue;
    if(logical->GetSensitiveDetector())throw std::runtime_error("Routing pipe unexpectedly sensitive");
    auto* solid=dynamic_cast<G4CutTubs*>(logical->GetSolid());
    if(!solid)throw std::runtime_error("Routing conversion did not retain G4CutTubs");
    if(std::abs(solid->GetDeltaPhiAngle()-2*M_PI)>1e-12)throw std::runtime_error("Partial converted pipe disk");
    totals[material]+=solid->GetCubicVolume()/(CLHEP::mm*CLHEP::mm*CLHEP::mm);++volumes;
  }
  if(volumes!=model.at("physical_material_pieces").get<std::size_t>())throw std::runtime_error("Converted pipe count differs");
  for(const auto& probe:model.at("joint_probes")) {
    const auto& p=probe.at("point_mm");
    auto* located=navigator.LocateGlobalPointAndSetup(G4ThreeVector(p[0].get<double>()*CLHEP::mm,p[1].get<double>()*CLHEP::mm,p[2].get<double>()*CLHEP::mm),nullptr,false);
    if(!located || located->GetLogicalVolume()->GetMaterial()->GetName()!=probe.at("material").get<std::string>())throw std::runtime_error("Converted miter navigation found wrong material");
    ++points;
  }
  for(const auto& entry:totals) {
    const double wanted=model.at("material_totals").at(entry.first).at("volume_mm3");
    if(std::abs(entry.second-wanted)>wanted*1e-10)throw std::runtime_error("Converted constituent volume differs");
  }
  json result={{"status","PASS"},{"physical_material_pieces",volumes},{"joint_material_points_checked",points},{"volume_mm3",totals}};
  std::ofstream stream(output);stream<<result.dump(2)<<'\n';if(!stream)throw std::runtime_error("Cannot retain conversion audit");
}
'''


def cases(model):
    path = next(p for p in model['paths'] if p['side'] == 1 and p['station'] == 0)
    transverse = path['segments'][0]['frame'][0]
    centre = path['segments'][0]['center_mm']; outer = model['adjusted_radii_mm']['outer']
    joint = 6; point = path['vertices_mm'][joint+1]; normal = path['segments'][joint]['high_normal_global']
    wall_radius = (model['adjusted_radii_mm']['inner']+outer)/2
    result = [dict(label='transverse', run=0, position_mm=add(centre, scale(transverse, -outer-1)), direction=transverse),
            dict(label='core_miter', run=1, position_mm=add(point, scale(normal, -5)), direction=normal),
            dict(label='wall_miter', run=2, position_mm=add(add(point, scale(transverse, wall_radius)), scale(normal, -5)), direction=normal)]
    for case in result:
        case['route_name'] = path['name']; case['target_joint'] = joint if case['label'].endswith('miter') else None
        # The installed G4gun position UI serializes six significant digits.
        # Make that test-fixture precision explicit instead of relaxing the
        # observed-versus-requested primary check after transport.
        case['analytic_position_mm'] = case['position_mm']
        case['position_mm'] = [float(format(v, '.6g')) for v in case['position_mm']]
        case['fixture_position_policy'] = 'Six significant digits, matching installed G4gun position UI; route geometry unchanged'
    return result


def audit(directory):
    receipt = json.loads((directory/'receipt.json').read_text())
    if receipt['exit_code'] or not receipt['inputs_unchanged']: raise ValueError('Incomplete/changed routing transport')
    for name, key in [('transport.log', 'log_sha256'), ('steps.jsonl', 'steps_sha256'), ('conversion.json', 'conversion_sha256'), ('cases.json', 'cases_sha256')]:
        if sha(directory/name) != receipt[key]: raise ValueError('Changed smoke artifact: '+name)
    conversion = json.loads((directory/'conversion.json').read_text())
    if conversion['status'] != 'PASS': raise ValueError('Conversion audit failed')
    requests = json.loads((directory/'cases.json').read_text())
    steps = [json.loads(line) for line in (directory/'steps.jsonl').read_text().splitlines()]
    if {(s['run'], s['event']) for s in steps} != {(c['run'], 0) for c in requests}: raise ValueError('Unexpected or incomplete native event set')
    if any((s['track'], s['parent'], s['pdg']) != (1, 0, 0) for s in steps): raise ValueError('Unexpected smoke track identity')
    results = []; all_crossings = 0
    for case in requests:
        records = [s for s in steps if s['run'] == case['run'] and s['event'] == 0 and s['track'] == 1 and s['parent'] == 0]
        if not records: raise ValueError('Missing observed native primary steps')
        first = records[0]
        for observed, expected in zip(first['vertex_mm'], case['position_mm']):
            if not math.isfinite(observed) or abs(observed-expected) > 1e-7: raise ValueError('Changed observed primary vertex')
        for observed, expected in zip(first['pre_momentum_GeV'], case['direction']):
            if not math.isfinite(observed) or abs(observed-expected) > 1e-7: raise ValueError('Changed observed primary momentum')
        if first['pdg'] != 0 or abs(first['pre_kinetic_energy_GeV']-1.) > 1e-7: raise ValueError('Unexpected observed primary identity/energy')
        material_lengths = {}; miter_crossings = 0; target_crossings = 0
        for step in records:
            length = step['step_mm']
            if not math.isfinite(length) or length < 0 or step['pdg'] != 0: raise ValueError('Invalid geantino step')
            if any(not math.isfinite(v) for v in step['pre_mm']+step['post_mm']): raise ValueError('Nonfinite native step endpoint')
            if abs(math.dist(step['pre_mm'], step['post_mm'])-length) > max(1e-7, length*1e-10): raise ValueError('Nonstraight geantino step')
            if step['pre_material'] in ('lArCaloSteel', 'PrototypeNitrogenTwoPhase'):
                material_lengths[step['pre_material']] = material_lengths.get(step['pre_material'], 0.)+length
                if step['geometry_boundary'] and step['pre_material'] == step['post_material'] and step['pre_volume'] != step['post_volume']:
                    pattern = re.escape(case['route_name'])+r'_s(\d+)_(core|wall)$'
                    a, b = re.fullmatch(pattern, step['pre_volume']), re.fullmatch(pattern, step['post_volume'])
                    if not a or not b or a[2] != b[2] or abs(int(a[1])-int(b[1])) != 1: raise ValueError('Material boundary is not an adjacent shared miter')
                    miter_crossings += 1
                    target_crossings += min(int(a[1]), int(b[1])) == case['target_joint']
        if not records or not material_lengths: raise ValueError('No retained passive-material transport')
        if case['label'] == 'transverse' and any(material_lengths.get(name, 0) <= 0 for name in ('lArCaloSteel', 'PrototypeNitrogenTwoPhase')):
            raise ValueError('Transverse track did not cross wall and core')
        if case['label'].endswith('miter') and not target_crossings: raise ValueError('Track did not cross the aimed shared miter')
        all_crossings += miter_crossings
        file = directory/(case['label']+'.root')
        results.append(dict(case=case, observed_primary={k:first[k] for k in ('run','event','track','parent','pdg','vertex_mm','pre_momentum_GeV','pre_kinetic_energy_GeV')},
                            primary_steps=len(records), material_step_lengths_mm=material_lengths,
                            miter_crossings=miter_crossings, aimed_miter_crossings=target_crossings, diagnostic_root_sha256=sha(file)))
    if len(requests) != 3: raise ValueError('Expected all three smoke cases')
    proof = dict(status='PASS', events=len(results), results=results, miter_crossings=all_crossings,
                 conversion=conversion, receipt_sha256=sha(directory/'receipt.json'), auditor_sha256=sha(__file__),
                 saved_event_format='Actual native Geant4 primary/step JSONL. Purely passive no-HC models do not produce EDM4hep event frames; ROOT outputs are diagnostics only.',
                 scope='Observed geantino primaries and actual passive material/volume step lengths across walls, cores and shared miters; no response or integrated fit')
    save(directory/'readback.json', proof); print(json.dumps(proof, indent=2)); return proof


def run(args):
    model = inputs(args.compact, args.expected); output = args.output.resolve(); output.mkdir(parents=True, exist_ok=False)
    requests = cases(model); save(output/'cases.json', requests)
    cpp = output/'conversion.hpp'; cpp.write_text(CONVERSION_CPP)
    steering = output/'steering.py'
    steering.write_text('''from DDSim.DD4hepSimulation import DD4hepSimulation
def configure(kernel):
    import ROOT, subprocess
    from pathlib import Path
    ROOT.gInterpreter.AddIncludePath(str(Path(subprocess.check_output(['geant4-config','--prefix'],text=True).strip())/'include/Geant4'))
    if not ROOT.gInterpreter.Declare(Path('conversion.hpp').read_text()): raise RuntimeError('Cannot compile routing conversion audit')
    def inspect(): ROOT.nODDRoutingConversionAudit(EXPECTED, 'conversion.json')
    ROOT._routing_callback=inspect
    kernel.get().register_initialize(inspect)
SIM=DD4hepSimulation()
SIM.action.step='nODDLArRoutingStepAudit/RoutingSteps'
SIM.physics.setupUserPhysics(configure)
'''.replace('EXPECTED', repr(str(args.expected.resolve()))))
    macro = '/run/initialize\n'
    for case in requests:
        macro += f'/ddg4/EDM4hepOutput/Output {output/(case["label"]+".root")}\n/gun/particle geantino\n/gun/momentumAmp 1 GeV\n/gun/position '+ ' '.join(format(v, '.17g') for v in case['position_mm'])+' mm\n/gun/direction '+' '.join(format(v, '.17g') for v in case['direction'])+'\n/run/beamOn 1\n'
    (output/'smoke.mac').write_text(macro)
    env = os.environ.copy(); env['NODD_ROUTING_STEPS'] = str(output/'steps.jsonl')
    for key in ('DD4HEP_LIBRARY_PATH', 'DYLD_LIBRARY_PATH', 'LD_LIBRARY_PATH'): env[key] = str(args.library.resolve().parent)+os.pathsep+env.get(key, '')
    command = [sys.executable, '-u', shutil.which('ddsim'), '--compactFile', str(args.compact.resolve()), '--steeringFile', str(steering),
               '--runType', 'run', '--enableG4Gun', '--macroFile', str(output/'smoke.mac'), '--numberOfEvents', '0', '--numberOfThreads', '1',
               '--random.seed', '1442026', '--physics.list', 'FTFP_BERT', '--physics.rangecut', '.7', '--part.userParticleHandler', '',
               '--outputConfig.forceEDM4HEP', '--outputFile', str(output/'unused.root')]
    def identity():
        return dict(compact_sha256=sha(args.compact), expected_sha256=sha(args.expected), materials_sha256=sha(args.compact.parent/'materials.xml'),
                    library_sha256=sha(args.library), runner_sha256=sha(__file__), generated_steering_sha256=sha(steering),
                    generated_conversion_sha256=sha(cpp), generated_macro_sha256=sha(output/'smoke.mac'))
    initial = identity(); started = time.monotonic(); before = resource.getrusage(resource.RUSAGE_CHILDREN)
    with (output/'transport.log').open('w') as log:
        result = subprocess.run(command, env=env, cwd=output, stdout=log, stderr=subprocess.STDOUT)
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt = dict(status='PASS' if result.returncode == 0 else 'FAIL', exit_code=result.returncode, command=command,
                   inputs_unchanged=identity() == initial, **initial, wall_seconds=time.monotonic()-started,
                   cpu_seconds=usage.ru_utime+usage.ru_stime-before.ru_utime-before.ru_stime,
                   completed_at=datetime.now(timezone.utc).isoformat(), log_sha256=sha(output/'transport.log'),
                   cases_sha256=sha(output/'cases.json'))
    for name, key in [('steps.jsonl', 'steps_sha256'), ('conversion.json', 'conversion_sha256')]:
        receipt[key] = sha(output/name) if (output/name).exists() else None
    save(output/'receipt.json', receipt)
    if result.returncode: raise RuntimeError('Routing smoke failed; diagnostics retained')
    audit(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); subparser = parser.add_subparsers(dest='stage', required=True)
    p = subparser.add_parser('run')
    for name in ('compact', 'expected', 'library', 'output'): p.add_argument('--'+name, type=Path, required=True)
    p = subparser.add_parser('audit'); p.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()
    run(args) if args.stage == 'run' else audit(args.directory)
