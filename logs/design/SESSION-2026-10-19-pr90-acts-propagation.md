# SESSION-2026-10-19-pr90-acts-propagation — PR90 ACTS chamber boundary propagation and momentum coverage

## Scope and evidence

State collection method, available context, limitations, related IDs and starting
revision. Identify uncommitted user changes present before work.

## Selected conversation

Attribute requests to the user and outcomes to the assistant. Mark exact quotes
and paraphrases explicitly. Include corrections and changes in direction.
Exclude private model state, confidential content, and irrelevant system context.

## Decisions and outcomes

State rationale, alternatives, consequences and what remains unresolved. Never
convert implementation authorization into human design sign-off.

## Commands and validation

Record relevant commands, actual exits/results, failed attempts and remedies.
Distinguish structural checks from detector acceptance.

## Changes and revision links

List changed files or refer to the paired JSON inventory. Result commits are
recorded only once they exist; Git history locates this record's enclosing commit.

## Token accounting

Record the client-provided per-turn usage source and import command, or state why
exact counters are unavailable. Report observed input/output sums and missing
coverage from `session_log.py summary`; empty usage means unknown, not zero.
Never copy raw client archives or private model state. Do not duplicate turns
across tasks or add cached/reasoning subsets to the input/output totals.

## Follow-up

List remaining work, missing measurements and any human review needed.

## Assignment A1 recorded before dispatch

```json
{
  "input_revision": "b3ff6a3b2ae111251fbc126d5ad489114877c3c7",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/validation/DES-040/geometry.json",
    "docs/validation/DES-040/results.json",
    "tools/module_layout/acts_validate.py",
    "tools/acts_binding_probe/probe.py",
    "docs/validation/MUON-001/results.md",
    "tools/toroid_prototype/map.py",
    "docs/validation/DES-039/map-metadata.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "id": "A1",
  "role": "SoftEng",
  "task": "Read-only ACTS API feasibility for PR90 reviewer6268359299/6268670798: real ACTS TrackingGeometry of all1560finite chamber prisms and native EigenStepper/Navigator propagation in joint field map; record actual boundary global hits, count only2large faces not4sides. Investigate verified local ACTS checkout /Users/salzburg/Documents/work/dev/acts-nodd at555c66e71d0639665c2fa3d5574a0fe7f3f62cde with unrelated dirty files (preserve all), installed include/library paths. Root is re-verifying acts-spack environment after warningchangedsetup/lock and no DD4hep/Geant4 fullsources; do not run dependent builds/runtime until rootconfirms. Inspect modern C++/Python geometry APIs, dense-volume/BVH or Gen3 per-chamber leaf/portal navigation, GenericCuboid/Trapezoid boundary orientation and custom MagneticFieldProvider. Prior module_layout records gen3singleleaf curved candidate loss; avoidassumingthatapproachworks. Recommend smallest robust native C++ prototype built outside shared ACTS tree, read sources only. No nestedagents/externalmessages/repo writes. Scratch /private/tmp/pr90-acts-A1-*.",
  "deliverable": "Cited exact installed/source API recipe for physical envelope TrackingGeometry+finite boundary hit recorder+3Dfield provider and navigation correctness controls; identify limitations early.",
  "completion": "Actionable verified source/API findings, preserve ACTS dirty tree, no claimed runtime pass without execution."
}
```

## Assignment P1 recorded before dispatch

```json
{
  "input_revision": "b3ff6a3b2ae111251fbc126d5ad489114877c3c7",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/validation/DES-040/geometry.json",
    "docs/validation/DES-040/results.json",
    "tools/module_layout/acts_validate.py",
    "tools/acts_binding_probe/probe.py",
    "docs/validation/MUON-001/results.md",
    "tools/toroid_prototype/map.py",
    "docs/validation/DES-039/map-metadata.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "id": "P1",
  "role": "PhysVal",
  "task": "Read-only design/validation criteria for reviewer PR90 actual ACTS field+chamber propagation, boundary hitXY/RZ and phi-eta coverage at muonsystem entrance, minimum momentum through1TeV, >5segments. Determine correct min5GeVIP vs localafterHCAL interpretation fromMUON001; propose honest primary vacuumgeometry benchmark versus material qualifications withoutinventing eta-dependent eloss. Define2largefaces/chamber as segmentproxies, sidesrecordedbutexcluded, duplicate/reentry/pairedstation counters, denominators including failures/nonentrants, charge andlow/mid/1TeV samples, entranceclosedcylinder withcaps versusbarrel-only cylinder meaning andsampling. Preservefixedgeometry/map. Reviewfield interpolation masks/out-of-map policy andcontrols (zero/constant field analytic, exactfiniteboundary, charge reversal, maxstep/tolerance convergence, navigator misses) needactualACTS intersectionsnotpolylinepostprocess. Laterimmutableimplementationreview separately. No repo edits/nestedagents/externalmessages. Scratch /private/tmp/pr90-acts-P1-*.",
  "deliverable": "Bounded observable/method proposal and adversarial tests, source locators and threshold semantics; not a sign-off.",
  "completion": "Concrete faithful interpretation of >5largeface segments and representative entrance maps, numerical/failure scope explicit, no unmeasured response claims."
}
```
