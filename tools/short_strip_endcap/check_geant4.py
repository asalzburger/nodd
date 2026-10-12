#!/usr/bin/env python3
"""Inspect independent saved Geant4 events and anisotropic physical volume IDs."""
import argparse
import json
import math
from pathlib import Path
import re
import uproot
from model import sha

def run(root,log,native,expectedfile,out,side):
    geometry=json.loads(native.read_text());expected=json.loads(expectedfile.read_text());text=log.read_text();errors=[]
    sensors={(e['ids']['layer'],e['ids']['petal'],e['ids']['ring'],e['ids']['module']):e for e in expected['entities'] if e['role']=='sensitive'}
    with uproot.open(root) as f:
        events=f['events'];count=events.num_entries
        particle_index=events['_ShortStripEndcapHits_particle/_ShortStripEndcapHits_particle.index'].array(library='np')[0].tolist()
        pdg=events['MCParticles/MCParticles.PDG'].array(library='np')[0].tolist()
        generated=events['MCParticles/MCParticles.generatorStatus'].array(library='np')[0].tolist()
        primary={i for i,(p,g) in enumerate(zip(pdg,generated)) if p==13 and g==1}
        data={k:events['ShortStripEndcapHits/ShortStripEndcapHits.'+k].array(library='np')[0].tolist() for k in ('cellID','eDep','pathLength','position.x','position.y','position.z')}
    expectedlayers=list(range(6)) if side==1 else list(range(6,12));primary_hits=[i for i,p in enumerate(particle_index) if p in primary]
    if len(primary)!=1:errors.append('Expected exactly one generated muon')
    layers=sorted({(data['cellID'][i]>>5)&15 for i in primary_hits})
    if count!=1 or layers!=expectedlayers:errors.append('Expected one event exercising all six selected-side discs')
    if not all((x&31)==4 for x in data['cellID']):errors.append('Wrong system IDs')
    if not data['eDep'] or not all(x>0 for x in data['eDep']):errors.append('Missing positive deposited energy')
    # Gun is normalized by DDSim; verify its actual three-vector from the log.
    match=re.search(r'direction:\(\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s*\)',text)
    if not match:errors.append('Gun direction missing')
    gun=[.195676,.033589,side*.980096];norm=math.sqrt(sum(x*x for x in gun));gun=[x/norm for x in gun]
    if match and math.dist([float(x) for x in match.groups()],gun)>.001:errors.append('Unexpected logged gun direction')
    if sha(expectedfile)!=geometry['execution']['expected_sha256']:errors.append('Expected inventory differs from native report')
    paths=[]
    for x in data['cellID']:
        key=((x>>5)&15,(x>>9)&15,(x>>13)&7,(x>>16)&15)
        s=sensors.get(key)
        if s is None:errors.append('Saved volume ID is not a physical sensor');continue
        paths.append(s['size_mm'][2]/abs(sum(a*b for a,b in zip(gun,s['normal']))))
    if not all(abs(paths[i]-data['pathLength'][i])<.01 for i in primary_hits):errors.append('Hit paths differ from plane thickness')
    if 'Finished run 0 after 1 events' not in text:errors.append('No completed event evidence')
    if not re.search(r'4320\s+sensitive path entries',text):errors.append('Unexpected sensitive path inventory')
    version=re.search(r'Geant4 version Name:\s*(.+)',text)
    result=dict(status='FAIL' if errors else 'PASS',errors=errors,scope='One seeded10GeV mu- event; saved sensitive hits, not acceptance or digitization',
        execution=geometry['execution'],hashes=dict(root=sha(root),runtime_log=sha(log),native_report=sha(native),expected=sha(expectedfile),checker=sha(__file__)),
        geant4_version_log=version.group(1).strip() if version else None,physics_list='FTFP_BERT',random_seed=42,field_T=0,
        side=side,events=count,layers=layers,saved_hits=len(data['cellID']),gun_direction=gun,geometric_path_mm=paths,path_tolerance_mm=.01,hit_data=data,hit_particle_index=particle_index,particle_PDG=pdg,primary_hit_indices=primary_hits,secondary_hits=len(particle_index)-len(primary_hits),
        limitations=['No compact field; curved acceptance is a separate vacuum sample.','Smoke excludes physics performance, noise, radiation and ACTS conversion.'])
    out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],errors,'hits',result['saved_hits']);return not errors

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for k in ('root','log','native','expected','output'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--side',type=int,choices=(-1,1),default=1);a=p.parse_args();raise SystemExit(0 if run(a.root,a.log,a.native,a.expected,a.output,a.side) else 1)
