#!/usr/bin/env python3
"""Curate bound routing checks without committing raw geometry or event payloads."""
import argparse
import json
import math
from pathlib import Path

from routing import ROOT, save, sha


def load(path):return json.loads(path.read_text())


def curate(directory):
    models={};native={};smokes={};bindings={}
    for variant in ('old','new','refined-new'):
        p=directory/variant;m=load(p/'expected.json');n=load(p/'native.json')
        for name,h in m['source_sha256'].items():
            if sha(ROOT/name)!=h:raise ValueError('Stale source: '+name)
        for name,h in m['artifact_sha256'].items():
            if sha(p/name)!=h:raise ValueError('Stale compact/material')
        if n['status']!='PASS' or n['errors'] or n['overlaps']:
            raise ValueError('Native checks failed: '+variant)
        if n['expected_sha256']!=sha(p/'expected.json') or n['auditor_sha256']!=sha(Path(__file__).with_name('routing_native.py')):
            raise ValueError('Stale native audit')
        if sha(p/'native.root')!=n['root_sha256']:raise ValueError('Stale native ROOT')
        models[variant]=m;native[variant]=n
        bindings[variant]=dict(expected_sha256=sha(p/'expected.json'),native_sha256=sha(p/'native.json'),
            compact_sha256=m['artifact_sha256']['routing.xml'],materials_sha256=m['artifact_sha256']['materials.xml'])
        if variant=='refined-new':continue
        p=directory/(variant+'-smoke');r=load(p/'receipt.json');g=load(p/'readback.json')
        if r['exit_code']!=0 or not r['inputs_unchanged'] or g['status']!='PASS':raise ValueError('Transport failed')
        if g['receipt_sha256']!=sha(p/'receipt.json') or g['auditor_sha256']!=sha(Path(__file__).with_name('routing_transport.py')):
            raise ValueError('Stale transport readback')
        if r['library_sha256']!=n['library_sha256'] or r['expected_sha256']!=n['expected_sha256']:
            raise ValueError('Transport/native input mismatch')
        for name,key in [('steps.jsonl','steps_sha256'),('conversion.json','conversion_sha256'),('transport.log','log_sha256')]:
            if sha(p/name)!=r[key]:raise ValueError('Stale saved transport evidence')
        cases=[];vertex_error=0.;momentum_error=0.;energy_error=0.
        for result in g['results']:
            case=result['case'];observed=result['observed_primary']
            vertex_error=max(vertex_error,*(abs(a-b) for a,b in zip(case['position_mm'],observed['vertex_mm'])))
            momentum_error=max(momentum_error,*(abs(a-b) for a,b in zip(case['direction'],observed['pre_momentum_GeV'])))
            energy_error=max(energy_error,abs(observed['pre_kinetic_energy_GeV']-1.))
            cases.append(dict(label=case['label'],primary_steps=result['primary_steps'],
                material_step_lengths_mm=result['material_step_lengths_mm'],miter_crossings=result['miter_crossings']))
        smokes[variant]=dict(status=g['status'],exit_code=r['exit_code'],inputs_unchanged=r['inputs_unchanged'],
            events=g['events'],miter_crossings=g['miter_crossings'],conversion=g['conversion'],
            primary_vertex_max_error_mm=vertex_error,primary_momentum_max_error_GeV=momentum_error,
            primary_kinetic_energy_max_error_GeV=energy_error,cases=cases,
            saved_event_format=g['saved_event_format'],scope=g['scope'],
            receipt_sha256=sha(p/'receipt.json'),readback_sha256=sha(p/'readback.json'),
            steps_sha256=r['steps_sha256'],log_sha256=r['log_sha256'])
    library=directory/'factory/libnODDLArRoutingPrototype.dylib'
    if any(sha(library)!=n['library_sha256'] for n in native.values()):raise ValueError('Stale final factory')
    revisions={n['source_revision'] for n in native.values()}
    if len(revisions)!=1 or any(m['execution']['commit'] not in revisions or m['execution']['dirty'] for m in models.values()):
        raise ValueError('Native comparison was not exported from one clean candidate')
    if bindings['old']['materials_sha256']!=bindings['new']['materials_sha256']:
        raise ValueError('Old/new material definitions differ')
    context=load(directory/'context-occupancy.json')
    if context['fit_accepted'] or not context['inputs_unchanged']:raise ValueError('Invalid context diagnostic scope')
    if context['execution']['commit'] not in revisions or context['execution']['dirty']:
        raise ValueError('Context and standalone source checkpoints differ')
    for name,h in context['input_path_sha256'].items():
        if sha(ROOT/name)!=h:raise ValueError('Stale context diagnostic input: '+name)
    contrasts={}
    for material in models['old']['material_totals']:
        a=native['old']['material_totals'][material];b=native['new']['material_totals'][material]
        contrasts[material]={key:b[key]-a[key] for key in ('volume_mm3','mass_g')}
        for key in ('volume_mm3','mass_g'):
            if not math.isclose(a[key],b[key],rel_tol=1e-10,abs_tol=1e-6):raise ValueError('Unpreserved constituent inventory')
    scalar_keys=('config','route_count','physical_segments','physical_material_pieces','analytic_length_mm','polyline_length_mm',
                 'radius_scale','nominal_radii_mm','adjusted_radii_mm','max_sagitta_mm','material_totals','materials','empty_envelopes')
    return dict(status='PASS_ISOLATED_COMPONENT / CONTEXT_CONTACTS_IDENTIFIED',
        native_source_revision=native['new']['source_revision'],reporter_sha256=sha(__file__),
        scope='Matched representative steel/N2 cooling pipes only; empty cables/jacket metadata; not a validated combined detector.',
        models={k:{key:v[key] for key in scalar_keys} for k,v in models.items()},
        native=native,geant4=smokes,old_new_constituent_differences=contrasts,context=context,
        evidence_bindings=bindings,
        limitations=['Raw XML/ROOT, expected placement/joint inventories and actual step JSONL/logs remain local/ignored.',
            '10nm overlap tolerance describes the approximate CutTube geometry, not ideal bend error.',
            'Volume/mass preservation does not establish unchanged ray budgets or response.',
            'Refined2.5degree result is native construction/material/navigation evidence; no refined transport or per-ray convergence claim.',
            'Context samples witness occupied space and duplicate existing services; fit_accepted remains false.'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();save(args.output,curate(args.directory));print('Curated bound standalone/transport and context evidence.')
