# SESSION-2026-11-14-lar-gap10k — conditional gap response

## Selected requests and scope

> Can you run the standard 19k electron sample and see if the barrel-Endcap gap improves ?

Correction:

> 10k sample this is

The interrupted 19k turn ran no tools. This bounded task uses10,000 standard
matched primaries. Previous PR143 is standalone at unchanged calorimeter
positions; it has no gap reduction to measure. Coordinator stated the conditional
800→400mm warm-gap test before new showers: translate whole signed endcaps,
keep internal material/readout/local services and fixed barrel, no unresolved
pipe overlay or wall cuts. This is response sensitivity, with physical interface
prerequisites still open. Governing prospective protocol is
`docs/validation/lar-gap10k/protocol.md`; user request authorizes the isolated
experiment, not production adoption or engineering sign-off.

Repository/nodd-coordinate/design-evidence/review-validation and acts-spack
instructions read. Preflight on acts-mac-studio-01.cern.ch exited2 with changed
setup_script/spack_lock fingerprints; user warned before dependencies. Fresh
software/env/run.sh imports verified ROOT6.40.04 and DD4hep/DDG4. Sandbox sysctl/ps
warnings did not prevent this. No shared dependency install/staging/update.
New task worktree/branch codex/lar-gap-10k-response starts at
8dfa8573f4a3e278db4a882d99a25a0df8109dc5 (draftPR143).

Initial discovery mistakenly searched all sibling worktrees and produced bulky
filename output; subsequent searches are bounded to the selected checkout.
No files were changed by that search. Existing full10k LAr and SiW primary
artifacts are present;253GiB free at inspection. Destination was reverified as
the same public asalzburger/nodd repository1361703051 with push permission.

## Assignment contracts recorded before dispatch

Explicit generic role fallback; no native profile-loading claim. Source revision 646b54378fd2d1ae198100174276478509c19e17. Only SoftEng writes the five named new helpers; coordinator owns other files.

```json
[
  {
    "input_revision": "646b54378fd2d1ae198100174276478509c19e17",
    "inputs": [
      "docs/validation/lar-gap10k/protocol.md",
      "docs/validation/lar10k/protocol.md",
      "docs/validation/lar10k/reproduce.md",
      "software/analysis/lar_response/transport.py",
      "software/analysis/lar_response/compare.py",
      "software/analysis/lar_response/steering.py",
      "software/analysis/lar_response/Audit.cpp",
      "tools/lar_calorimeter/endcap_export.py",
      "prototypes/calorimeter/LArEndcap.cpp",
      "tools/lar_calorimeter/combined_native.py",
      "docs/design/inputs/DES-032-routing-dd4hep.md",
      "docs/design/inputs/DES-032-side-rear-routing.md"
    ],
    "deliverable": "Return assignment ID, exact revision, changed files, actual checks, output recipes and limitations. Coordinator owns records/publication and curates result. No nested delegation, shared installs or Git commits/pushes.",
    "completion": "Resolve assigned bounded contribution or report concrete missing evidence. Do not infer engineering acceptance. Source code must be frozen/committed by coordinator before native production; do not mutate source during runs.",
    "id": "LAR-GAP10K-SoftEng",
    "role": "SoftEng",
    "mode": "write",
    "writable_paths": [
      "software/analysis/lar_gap/geometry.py",
      "software/analysis/lar_gap/native.py",
      "software/analysis/lar_gap/compare.py",
      "software/analysis/lar_gap/test_geometry.py",
      "software/analysis/lar_gap/test_compare.py"
    ],
    "task": "Implement isolated conditional gap study helpers per protocol. Source frozen reference sample ../nodd-lar-10k-response/build/lar10k-resume/sample and audited baseline production12 are available. Preserve whole endcap internals: shift ONLY root-relative replicas and root-relative passive pieces +/-400mm toward IP; retain daughter-local poses, wheel pieces/period envelopes, local segmentation tables/IDs, entire barrel and material bytes. No modifications to existing exporters/factories/transport code, no pipe overlay or wall cuts. Prepare candidate sample.json compatible with existing lar_response transport runner; bind original frozen sample/manifests/materials/input/producer sources and explicit allowed XML changes, reject unexpected topology or shifts. Need native audit using unchanged factories: complete ECAL10nm overlaps, count/mass/readout equivalence and native global signed translations versus reference for physical placements (all leaves or demonstrably exhaustive branch proof); raw native ledgers ignored under build/lar-gap10k/softeng only, compact report excludes payloads. Use existing factories or records only after source/library verification. ROOT/DD4hep imports verified fresh by root; acts-spack preflight has setup/lock drift warning already reported. Read skill before any native checks and direct-verify current dependencies; no installs. New compare script loads two verified lar_response runs (reuse load_run/validate_contract with name lar), exact input10k identity/physics, native geometry/source bindings and isolated difference. Standard/fine transition bins and1000 shared-event bootstrap per frozen protocol, covariance and common baseline threshold tails; compact source-bound report and scientific plots in ECAL colour #cccc00 different line styles. Preserve all events. Add meaningful negative/transformation/statistics controls. Root will run native construction and showers after committing code; give exact CLI recipe. You may run pure tests/analysis metadata checks but no competing DDSim jobs or uncommitted scientific production."
  },
  {
    "input_revision": "646b54378fd2d1ae198100174276478509c19e17",
    "inputs": [
      "docs/validation/lar-gap10k/protocol.md",
      "docs/validation/lar10k/protocol.md",
      "docs/validation/lar10k/reproduce.md",
      "software/analysis/lar_response/transport.py",
      "software/analysis/lar_response/compare.py",
      "software/analysis/lar_response/steering.py",
      "software/analysis/lar_response/Audit.cpp",
      "tools/lar_calorimeter/endcap_export.py",
      "prototypes/calorimeter/LArEndcap.cpp",
      "tools/lar_calorimeter/combined_native.py",
      "docs/design/inputs/DES-032-routing-dd4hep.md",
      "docs/design/inputs/DES-032-side-rear-routing.md"
    ],
    "deliverable": "Return assignment ID, exact revision, changed files, actual checks, output recipes and limitations. Coordinator owns records/publication and curates result. No nested delegation, shared installs or Git commits/pushes.",
    "completion": "Resolve assigned bounded contribution or report concrete missing evidence. Do not infer engineering acceptance. Source code must be frozen/committed by coordinator before native production; do not mutate source during runs.",
    "id": "LAR-GAP10K-PhysVal-initial",
    "role": "PhysVal",
    "mode": "read-only",
    "writable_paths": [],
    "task": "Independently assess prospective conditional800->400mm gap10k protocol before candidate results. Check matched raw-response statistics, fixed transition/fine bins, bootstrap/tail definition, reference reuse integrity and scientific boundary distinguishing gap-only sensitivity from engineered routing. Examine retained baseline metadata as useful; no native simulations or writes. Identify concrete changes needed before new production or conclude bounded protocol is defensible with limitations. User explicitly requested10k; default production geometry not being changed."
  },
  {
    "input_revision": "646b54378fd2d1ae198100174276478509c19e17",
    "inputs": [
      "docs/validation/lar-gap10k/protocol.md",
      "docs/validation/lar10k/protocol.md",
      "docs/validation/lar10k/reproduce.md",
      "software/analysis/lar_response/transport.py",
      "software/analysis/lar_response/compare.py",
      "software/analysis/lar_response/steering.py",
      "software/analysis/lar_response/Audit.cpp",
      "tools/lar_calorimeter/endcap_export.py",
      "prototypes/calorimeter/LArEndcap.cpp",
      "tools/lar_calorimeter/combined_native.py",
      "docs/design/inputs/DES-032-routing-dd4hep.md",
      "docs/design/inputs/DES-032-side-rear-routing.md"
    ],
    "deliverable": "Return assignment ID, exact revision, changed files, actual checks, output recipes and limitations. Coordinator owns records/publication and curates result. No nested delegation, shared installs or Git commits/pushes.",
    "completion": "Resolve assigned bounded contribution or report concrete missing evidence. Do not infer engineering acceptance. Source code must be frozen/committed by coordinator before native production; do not mutate source during runs.",
    "id": "LAR-GAP10K-SysArch-initial",
    "role": "SysArch",
    "mode": "read-only",
    "writable_paths": [],
    "task": "Assess physical meaning and transform invariants for isolated400mm inward rigid endcap translation with fixed barrel and unchanged local services/readout. Verify signed pose/daughter-local segmentation handling, gap endpoints, material conservation and ECAL-only overlap prerequisites. Identify likely new internal ECAL contacts, external/forward/routing limits and any reason this cannot be a conditional response sensitivity. Do not enforce proposal integration acceptance against user-authorized isolated experiment; no default or pipe overlay changes. Read retained source/native evidence as useful, no new native jobs or writes."
  }
]
```

## Current runtime and reference integrity

Fresh imports, installed package/hash queries and Geant4dataset checks exited0.
ROOT6.40.04, DD4hep1.38, Geant411.4.3, EDM4hep1.1.1 and podio1.8 match the
retained environment. Setup/lock actualSHA fingerprints match the current
recorded run, despite older registry drift. Existing plotting Python observed
{"python": "3.14.5", "numpy": "2.5.4", "matplotlib": "3.11.2"}. No installs or shared changes.

Retained800mm reference production12 has clean execution327dd042b6b3d1be1a4325af3d444c38dd70f720,10,000events,12workers, seed133812341 and5mmcap. validate_contract rehashed actual ROOT and worker audits; load_run verified receipt/event-summary hashes and all10,000IDs. Three actual library hashes, four producer sources and both component source/artifact inventories match current files. Primary/compact/material hashes checked. Reusing these audited reference showers is explicit; candidate showers are fresh. Raw verification details remain ignored at build/lar-gap10k/reference-bindings.json.

## Initial independent assessments before candidate showers

SysArch at646b54378fd2d1ae198100174276478509c19e17 found the conditional study
coherent, with no physical reason to prevent an isolated response experiment.
Expected XML change:4928 signed wheel replicas +36 parentless passive pieces,
4964 z attributes total. Retain all parent-local daughters, proper negative-side
rotation, local readout references/IDs and world constants. Derived warm bounds
4500–5460mm, sampling4610–5060mm and wheel centres±4835mm give400/700mm warm/active
separation from fixed barrel ends4100/3910. Endcap9856 rawIDs/1203200 logical cells
and combined43648 rawcontexts remain unchanged. Complete native union10nm scan
and exhaustive transforms are prerequisites, not inferred passes. External
collar/routing/ports/installation remain unresolved; whole endcap illumination
changes, so this cannot isolate only the transition or prove directional
material-budget invariance. No files changed or native jobs run by SysArch.

PhysVal at the same revision found scope defensible and identified a concrete
analysis prerequisite: the old technology-comparison helper uses bin-local
half-mean tails and lacks paired mean/common-tail differences. New two-gap
analysis must use standard global frozen threshold0.07966135709622409 from
reference mean0.15932271419244817 (183/10000 reference tail events), global-own
thresholds labelled separately, explicit bin numerators/denominators, shared
bootstrap weights and predeclared fine bins. The protocol was clarified before
new showers to hold the common threshold fixed across bootstrap replicates;
intervals condition on it. PhysVal independently verified baseline inputs,
complete IDs/worker policy/libraries/producers, source/map/log bindings and
rehash of full20,961,084,327byteROOT, digest
e64f9e9c2c794cd9d5fbbe43954c0aba0da94a72fa773cde96224bc2eea9054b.
Require exhaustive native branch/leaf transforms, not detector-root centre only.
No candidate results were available for these prospective assessments.

## Coordinator-owned control helper

Coordinator additionally owns software/analysis/lar_gap/controls.py and
test_controls.py, disjoint from specialist ownership (sent before editing).
The helper rechecks candidate input/receipt/root/worker bindings and requires
exact24-event serial/MT saved primary and canonical cell/energy/position
equality by event ID. Five meaningful adverse/invariant controls passed.
No root event data is retained in the compact control proof.

## Implementation handoff and provenance correction

SoftEng supplied isolated geometry/native/statistical helpers and meaningful
negative controls; integrated pure discovery including coordinator controls
passed18 tests. Actual frozen reference and normalized XML transformation checks
passed4928 replicas+36 passive roots, preserving38210 daughter-local pieces.
No native/DDSim run by author. Root review requested null-material assembly
handling and explicit native dirty/source-unchanged guards; these were included
before the final candidate freeze. Dynamic history lookup was replaced by a
verified immutable producer locator to avoid false provenance drift from refs.

The original retained sample reports generation HEAD
5ef3db386436f063f944d36e784ad918e176cd0f, while its actual producer SHA is
60708dbf990268027c0490309a7a4213c1f7457aa22d6f4df5872ddcdfeb4120.
Those exact bytes were recovered and pinned at
e2222482eb6c267fe1db4e4a871280469d49f7f9:software/analysis/lar_response/transport.py.
Both original component export records declare5ef3db3,dirty:true. These facts
remain separate from the clean327dd042 reference transport and the current
matching actual source/compact/material/library hashes. No claim of clean
original sample generation is made, and no frozen artifact is changed. Current
native reconstruction provides an independent bound geometry check before
new showers. This correction strengthens provenance rather than substituting
an assumed HEAD for observed source bytes.

## Independent source review contract before dispatch

Explicit generic SoftEng fallback; reviewer is not implementation author.

```json
{
  "id": "LAR-GAP10K-SoftEng-review",
  "role": "SoftEng",
  "input_revision": "c7de169d3df360e3e3c55fc14e232002532366f1",
  "inputs": [
    "docs/validation/lar-gap10k/protocol.md",
    "docs/validation/lar-gap10k/environment.json",
    "software/analysis/lar_gap/compare.py",
    "software/analysis/lar_gap/controls.py",
    "software/analysis/lar_gap/geometry.py",
    "software/analysis/lar_gap/native.py",
    "software/analysis/lar_gap/test_compare.py",
    "software/analysis/lar_gap/test_controls.py",
    "software/analysis/lar_gap/test_geometry.py",
    "software/analysis/lar_response/transport.py",
    "software/analysis/lar_response/compare.py",
    "prototypes/calorimeter/LArEndcap.cpp"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independent nonauthor software review of committed conditional gap exporter/native comparator/statistics/serial-MT helper and adverse tests. Assess exact signed root-only translations preserving local daughters/world/readout/materials, exhaustive native-leaf proof (assembly materials handled), immutable frozen-reference/producers/library/source binding, stale/failure guards, sample/receipt/readback transport compatibility, paired fixed-global tails and bootstrap semantics. Existing raw artifacts may become available under build/lar-gap10k/final as root runs gates; do not touch or infer their readiness. Review source/pure controls now, return concrete prioritized correctness findings promptly. No native/DDSim runs needed, no file edits/nested delegation or commits/publication. This is a conditional response experiment, not engineering fit.",
  "deliverable": "Return assignment ID, exact revision, findings or no actionable findings, actual checks, any missing evidence and limitations. Coordinator curates result in session.",
  "completion": "Assess source at exact revision independently from author conclusions. Concrete blockers immediately; no style-only scope expansion or acceptance. Read-only; no changes to ongoing artifacts."
}
```

## Adverse native audit and bounded correction

At clean execution0d11cf9c, first baseline native snapshot constructed290217nodes but stopped before showers on negative capacity-minus-daughter volume at the first period mother. Independent nonauthor SoftEng source review separately flagged ROOT stochastic BooleanCapacity as unsuitable for exact exclusive-volume subtraction; existing native auditors explicitly avoid it. Raw failed outputs stay ignored under build/lar-gap10k/final/. No geometry, overlap or shower pass is inferred from failure.

Coordinator initially sent supplemental author/PhysVal research followups before durably recording these detailed contracts; this timing omission is retained, and full prepared contracts were supplied before correction acceptance or further native execution. Existing role fallback still applied. No tolerance relaxation is authorized.

```json
[
  {
    "input_revision": "c7de169d3df360e3e3c55fc14e232002532366f1",
    "inputs": [
      "docs/validation/lar-gap10k/protocol.md",
      "software/analysis/lar_gap/native.py",
      "software/analysis/lar_gap/geometry.py",
      "software/analysis/lar_gap/test_geometry.py",
      "tools/lar_calorimeter/barrel_native.py",
      "tools/lar_calorimeter/endcap_native.py"
    ],
    "deliverable": "Return exact revision, actual method/checks/findings and limitations; root curates adverse evidence and makes fresh source-bound runs. No nested delegation, commit or publication.",
    "completion": "Do not weaken or clamp tolerance failures. Distinguish invalid stochastic-volume accounting from geometry/overlap proof; no new showers until correction validated. No shared changes.",
    "id": "LAR-GAP10K-SoftEng-volume-correction",
    "role": "SoftEng",
    "mode": "write",
    "writable_paths": [
      "software/analysis/lar_gap/native.py",
      "software/analysis/lar_gap/test_geometry.py"
    ],
    "task": "Investigate confirmed first baseline native gate failure: negative material-exclusive volume from Boolean Capacity subtraction; independent source reviewer flagged same. Propose scientifically sound shape/material conservation proof using existing analytical/native methods, rigid transforms and bound constituent inventory rather than stochastic Boolean Capacity. Research method first, then implement bounded correction once reconciled. Other files frozen. No native/DDSim by author; root retains build/lar-gap10k/final failed artifacts and will rerun fresh after commit."
  },
  {
    "input_revision": "c7de169d3df360e3e3c55fc14e232002532366f1",
    "inputs": [
      "docs/validation/lar-gap10k/protocol.md",
      "software/analysis/lar_gap/native.py",
      "software/analysis/lar_gap/geometry.py",
      "software/analysis/lar_gap/test_geometry.py",
      "tools/lar_calorimeter/barrel_native.py",
      "tools/lar_calorimeter/endcap_native.py"
    ],
    "deliverable": "Return exact revision, actual method/checks/findings and limitations; root curates adverse evidence and makes fresh source-bound runs. No nested delegation, commit or publication.",
    "completion": "Do not weaken or clamp tolerance failures. Distinguish invalid stochastic-volume accounting from geometry/overlap proof; no new showers until correction validated. No shared changes.",
    "id": "LAR-GAP10K-PhysVal-volume-method",
    "role": "PhysVal",
    "mode": "read-only",
    "writable_paths": [],
    "task": "Independently assess a valid material-inventory conservation proof after native BooleanCapacity subtraction failure, with unchanged shapes/materials/local placements and exhaustive signed native transforms. Are analytic component inventories plus exact XML/native shape dimensions/topology/recipes sufficient for rigid-translation conservation, without claiming a noisy exclusiveCapacity as exact? Identify required native checks. Read-only, no native job or artifact writes."
  }
]
```

PhysVal and nonauthor SoftEng independently recommend deterministic recursive native solid signatures with all primitive/Boolean parameters and operand matrices. Exact shape/material/topology/pose bijection under translations proves relative inventory preservation; inherited analytical component inventory must be labelled separately from absolute native mass. Software review also identified clamped CI plotting endpoints; corrected source must draw exact percentile intervals even when the estimate lies outside them. Amended bounded ownership contract recorded before the plotting correction dispatch:

```json
{
  "input_revision": "c7de169d3df360e3e3c55fc14e232002532366f1",
  "inputs": [
    "docs/validation/lar-gap10k/protocol.md",
    "software/analysis/lar_gap/native.py",
    "software/analysis/lar_gap/geometry.py",
    "software/analysis/lar_gap/test_geometry.py",
    "tools/lar_calorimeter/barrel_native.py",
    "tools/lar_calorimeter/endcap_native.py"
  ],
  "deliverable": "Return exact revision, actual method/checks/findings and limitations; root curates adverse evidence and makes fresh source-bound runs. No nested delegation, commit or publication.",
  "completion": "Do not weaken or clamp tolerance failures. Distinguish invalid stochastic-volume accounting from geometry/overlap proof; no new showers until correction validated. No shared changes.",
  "id": "LAR-GAP10K-SoftEng-volume-and-CI-correction",
  "role": "SoftEng",
  "mode": "write",
  "writable_paths": [
    "software/analysis/lar_gap/native.py",
    "software/analysis/lar_gap/test_geometry.py",
    "software/analysis/lar_gap/compare.py"
  ],
  "task": "Investigate confirmed first baseline native gate failure: negative material-exclusive volume from Boolean Capacity subtraction; independent source reviewer flagged same. Propose scientifically sound shape/material conservation proof using existing analytical/native methods, rigid transforms and bound constituent inventory rather than stochastic Boolean Capacity. Research method first, then implement bounded correction once reconciled. Other files frozen. No native/DDSim by author; root retains build/lar-gap10k/final failed artifacts and will rerun fresh after commit. Independent software review also found percentile-CI drawing clamps negative error lengths to zero when observed point lies outside interval, silently altering endpoint rendering. In compare.py plot only, draw exact percentile CI segments plus estimate markers; no interval/data/statistics or protocol change. Add meaningful adverse CI rendering check if needed without broad tests. Complete this before sample re-prepare because all helper source hashes are frozen."
}
```

Correction re-frozen: native.py plus test_geometry.py implement deterministic solid definitions; compare.py plotting and test_compare.py retain exact percentile-CI endpoints (statistics unchanged). Complete primitive/Boolean operands and matrices are recorded; non-unit scale rejected. All25 pure controls pass, including Capacity-forbidden Boolean/CSG mutation and outside-CI fixtures. Native report names1e-7mm transform tolerance and10nm overlap tolerance. No native or showers by author. No source writes during subsequent execution; fresh ignored corrected/ outputs will replace no prior evidence.

## Exact correction-review contract before dispatch

Explicit generic nonauthor SoftEng review.

```json
{
  "id": "LAR-GAP10K-SoftEng-correction-review",
  "role": "SoftEng",
  "input_revision": "19d9bc03a6beffd3c6d6dd845b2251ec22c64060",
  "inputs": [
    "docs/validation/lar-gap10k/protocol.md",
    "software/analysis/lar_gap/native.py",
    "software/analysis/lar_gap/compare.py",
    "software/analysis/lar_gap/test_geometry.py",
    "software/analysis/lar_gap/test_compare.py",
    "software/analysis/lar_gap/geometry.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Reassess exact correction to your P1 stochasticCapacity and P2 clamped-CI findings from c7de169d. Check deterministic native primitive/Boolean parameters and both operand matrices, unsupported/scaled shape rejection, all-native placement/recipe/topology bijection, inherited analytic inventory/period-mother residual scope, same10nm overlaps and source guards. Verify CI plot draws exact stored percentile endpoints with separate estimate. Statistics/geometry transform remain unchanged. Review adversarial tests. Root will run fresh native/controls at clean checkpoint; read-only ongoing build/lar-gap10k/corrected artifacts if complete. No native/DDSim or writes/nested delegation.",
  "deliverable": "Return exact revision, findings or closure of both prior issues, actual checks and remaining limits. Root retains assessment in session.",
  "completion": "Report concrete correctness blockers promptly; assess only material correction without broad restyling. No acceptance or fresh absolute mass claim."
}
```
