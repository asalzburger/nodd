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

## Boundary-log anomaly and diagnosis contracts before dispatch

During candidate production, a selected ERROR-marker scan found rare turbine
cellID radial-bound errors. Rechecking the full original reference log found
three cases (18 ERROR lines) previously not rejected by saved-data auditing.
Current example localr774.260466729mm lies1.84e-7mm below wheel1 inner boundary
774.260466913224mm, beyond the existing1e-8mm guard. Deposited-energy impact
is unknown; no smallness, zero-deposit or successful-recovery assumption is
made. Ongoing production is retained as diagnostic until resolved.

This reporting-only narrative edit/commit occurs during an already-started
run at clean b24f9db2; all geometry, protocol, transport/analysis producer and
library bytes remain frozen. Native/source hash evidence is unchanged; do not
claim the reporting worktree stayed globally clean after this point.

Explicit generic role fallback; full contracts recorded before dispatch:

```json
[
  {
    "input_revision": "b24f9db24b52f79c7586a52d0ca9b35e792606b9",
    "inputs": [
      "prototypes/calorimeter/LArEndcap.cpp",
      "software/analysis/lar_response/Audit.cpp",
      "software/analysis/lar_response/transport.py",
      "docs/validation/lar-gap10k/protocol.md",
      "software/analysis/lar_gap/geometry.py"
    ],
    "mode": "read-only",
    "writable_paths": [],
    "deliverable": "Return exact sources/versions examined, actual findings/evidence and bounded correction or integrity interpretation. Root records results. No file edits, native/DDSim jobs, nested delegation, commit or publication.",
    "completion": "Do not relax tolerances or invent missing deposited energy. Distinguish actual dropped-energy/fallback behavior from logger errors; propose concrete next evidence. Existing production continues as diagnostic, no validated response claim yet.",
    "id": "LAR-GAP10K-SoftEng-boundary-diagnosis",
    "role": "SoftEng",
    "task": "Investigate rare LArEndcapsHandler ERROR Hit outside turbine wheel/depth in retained original reference and current400mm production. Baseline log ../nodd-lar-10k-response/build/lar10k-resume/production12/transport.log has18selectedERRORlines=3cases; current corrected/production12 transport.log has at least1case. Example G4local(771.933708,59.980170,63.978882)mm =>r774.260466729mm vswheel1inner774.260466913224mm, deviation-1.84e-7mm; guard1e-8mm. Examine exact installedDD4hep1.38 CalorimeterAction cellID exception/fallback path and whether deposit/contribution is dropped or assigned0/surrogate. Installed headers first; public upstream exact tag primary source fallback if source notinstalled. Determine if only zero-deposit steps can emit this and what rawROOT can prove. Do not implement tolerance changes or launches. Full sources unavailable unless actually found; declare source/version gaps."
  },
  {
    "input_revision": "b24f9db24b52f79c7586a52d0ca9b35e792606b9",
    "inputs": [
      "prototypes/calorimeter/LArEndcap.cpp",
      "software/analysis/lar_response/Audit.cpp",
      "software/analysis/lar_response/transport.py",
      "docs/validation/lar-gap10k/protocol.md",
      "software/analysis/lar_gap/geometry.py"
    ],
    "mode": "read-only",
    "writable_paths": [],
    "deliverable": "Return exact sources/versions examined, actual findings/evidence and bounded correction or integrity interpretation. Root records results. No file edits, native/DDSim jobs, nested delegation, commit or publication.",
    "completion": "Do not relax tolerances or invent missing deposited energy. Distinguish actual dropped-energy/fallback behavior from logger errors; propose concrete next evidence. Existing production continues as diagnostic, no validated response claim yet.",
    "id": "LAR-GAP10K-PhysVal-boundary-diagnosis",
    "role": "PhysVal",
    "task": "Independently assess scientific integrity of rare endcap radial-boundary cellID errors in both original10k reference(3cases) and current400mm production(atleast1case). Example localr min deviation~-1.84e-7mm against1e-8mm guard. Do logs imply lost/corrupted deposited energy or may be zero steps/safelyrecovered? What evidence/bound is required to use comparison, considering worker/root audits currently ignoreerrorlogstrings? Existingnative/serialMT/pilot passed. Source-informed assessment and concrete minimaldiagnostic; no unapproved tolerance relaxation or unsupported smallness claim. Read-only/no native/DDSim."
  }
]
```

## Boundary diagnosis and independent accounting extension

Separate SoftEng and PhysVal source assessments confirm configured
Geant4ScintillatorCalorimeterAction plus positive edep0. Exact upstreamv01-38
commit142cbb7eb29ec4feafb1af9317fac38775872085 catches cellID exceptions and returns
before accumulation/track marking, with no fallback. Installed header/Filter.py
blobs match upstream; installed plugin.cpp sources absent. Public primary
locators are retained in observer-protocol.md; no full source installation.

Full-precision endpoints give reference midpoint radius deficits1.4512e-6,
0.001065619 and1.3589e-6mm, and first two candidate cases4.03445e-8/8.05645e-6mm.
This is the annular midpoint-representative problem, not solely rounding.
All4928 replica frames preserve radius. Whole positive step contributions are
omitted; magnitude and primary identity are missing from old ROOT/logs, so no
negligibility or width-bias bound is inferred. Prior readback integrity does not
prove complete deposited energy. The completed/ongoing initial production and
standard reference remain diagnostic with respect to inclusive deposit energy.

The user was told the readout-integrity issue and next independent observer
replay. New diagnostic protocol is frozen before observer data. It preserves
all physical/readout/guard/physics/RNG settings and measures per-event all-step,
successful-hit and failed-unassigned energy with precision-derived closure.
Both geometries will use the same10,000 primaries; original common tailcut
0.07966135709622409 is retained. No tolerance relaxation or invented cell IDs.
Machine reports24 logical CPUs; independent12-worker replay jobs may run in
separate directories once pilots pass, with actual resource/runtime recorded.

## Observer implementation/protocol contracts before dispatch

Explicit generic roles; only six new observer files owned by author. All existing frozen simulation/geometry/readout sources retained.

```json
[
  {
    "input_revision": "81674f8630ab29c8462d5b88226000e07a2d0641",
    "inputs": [
      "docs/validation/lar-gap10k/observer-protocol.md",
      "docs/validation/lar-gap10k/protocol.md",
      "software/analysis/lar_response/transport.py",
      "software/analysis/lar_response/Audit.cpp",
      "software/analysis/lar_response/steering.py",
      "software/analysis/lar_gap/geometry.py",
      "software/analysis/lar_gap/native.py",
      "software/analysis/lar_gap/compare.py",
      "prototypes/calorimeter/LArEndcap.cpp",
      "prototypes/lar_routing/LArRouting.cpp"
    ],
    "deliverable": "Return exact source revision, changed files, tests/methods, CLI recipe and limits. Root owns publication, records, compiled/native production and final evidence. No nested delegation, Git commits/pushes or shared installs.",
    "completion": "Match source-proven actual filters/contribution/midpoint behavior. Do not alter geometry/readout/guard/cuts/RNG or invent IDs. Root freezes code before native controls/replays; no source writes during runs. Preserve prior runs; no gate weakening.",
    "id": "LAR-GAP10K-SoftEng-step-observer",
    "role": "SoftEng",
    "mode": "write",
    "writable_paths": [
      "software/analysis/lar_gap/CMakeLists.txt",
      "software/analysis/lar_gap/StepAudit.cpp",
      "software/analysis/lar_gap/observed_steering.py",
      "software/analysis/lar_gap/observed_transport.py",
      "software/analysis/lar_gap/observed_compare.py",
      "software/analysis/lar_gap/test_observed.py"
    ],
    "task": "Implement independent all-positive-sensitive-step observer/replay/closure and comparison per new prospective protocol. Existing factories, old lar_response source and old gap geometry/native/compare helpers/protocol MUST remain unchanged (frozen artifact guards); new6files only. New CPP library stepping+event actors record per-event per-collection total accepted contribution A, classified successful per-canonical-cell S, unassigned failures U, plus failure details event/track/step/PDG/rawvolume/prepostmidpointlocal/guard deltas. Exact DD4hep v01-38 scintillator extractContribution(step,true), edep0 and preTouchable midpoint semantics; Birks0/no RNG. Reuse old native mapping preinit+worker-audit library unchanged; standalone steering wrapper can import configure and append step/event actions. Newdriver may reuse old readback helpers but must use own run steering/extra observerlib and explicit new producer/library hashes, never monkeypatch __file__ or mutateoldboundcode. Original sample reference ../nodd-lar-10k-response/build/lar10k-resume/sample; candidate build/lar-gap10k/corrected/sample400 (verified). Retained originals production12 in samebase and corrected/production12 (ongoingdiagnostic). Bind fresh observer runs to native-comparison proof andsame3oldlibs +newobserverlib. Derive actual EDM4hep per-cell rounding/accumulation closure bounds from source/fieldprecision, verify A=H+U per-event/collection and successfulcells. Failurecountslocalpoints must matchoriginalSDlogerrors without duplicate original logging. Record replay saved-cell and event-vector equality with retained runs, else freshmatchedvectors only. Analysis two explicit savedH/E vs totalA/E; keeporiginal commonthreshold0.07966135709622409 frozen acrossbins/bootstrap, same1000seed13001000 andfixedaxes; missingdelta moments/variance identity andeffect statistics. Existing mathhelpers may beimported, no frozenfileedits. Expose cleanCLI prepare/run/audit/analyze/plot orreuseplots withclearlylabelleddata. Add meaningfulnegative integrity/rounding/event/threshold tests. Puretests onlybyyou; rootbuilds/runs afterfreeze. Need exactprimaryupstreamsourcefacts recorded, no fullsourceinstall or SDKchange. Return boundedreadyfiles promptly, no futurefeatures."
  },
  {
    "input_revision": "81674f8630ab29c8462d5b88226000e07a2d0641",
    "inputs": [
      "docs/validation/lar-gap10k/observer-protocol.md",
      "docs/validation/lar-gap10k/protocol.md",
      "software/analysis/lar_response/transport.py",
      "software/analysis/lar_response/Audit.cpp",
      "software/analysis/lar_response/steering.py",
      "software/analysis/lar_gap/geometry.py",
      "software/analysis/lar_gap/native.py",
      "software/analysis/lar_gap/compare.py",
      "prototypes/calorimeter/LArEndcap.cpp",
      "prototypes/lar_routing/LArRouting.cpp"
    ],
    "deliverable": "Return exact source revision, changed files, tests/methods, CLI recipe and limits. Root owns publication, records, compiled/native production and final evidence. No nested delegation, Git commits/pushes or shared installs.",
    "completion": "Match source-proven actual filters/contribution/midpoint behavior. Do not alter geometry/readout/guard/cuts/RNG or invent IDs. Root freezes code before native controls/replays; no source writes during runs. Preserve prior runs; no gate weakening.",
    "id": "LAR-GAP10K-PhysVal-observer-protocol",
    "role": "PhysVal",
    "mode": "read-only",
    "writable_paths": [],
    "task": "Assess frozen observer-protocol before data: exactpositiveedep/Birks0 contribution andfilter/weight semantics, per-event/all-success-failure closure, preciseEDMoutputrounding allowance, replayequivalence, frozenoriginaltailthreshold, rawRvsunassignedreadout claim boundary. Examine exactsource142cbb7 andinstalledmetadata asneeded; codeauthorimplementing in parallel. Identify concrete prerequisites orerrors promptly; no native/DDSim or files. Return usableprecision/formula/source guidance andscientific assessment, not engineeringacceptance."
  }
]
```

Observer protocol review confirms unweighted scintillator contribution (trackweights audited1), positive rawedep filter, Birks0/non-optical contract. Installed EDM4hep floatenergy sourcehashes supplied independently. Corrected accounting notation beforeobserverdata: A=S+U in native energy, savedH is per-cell binary32 rounding ofS; derive exactrounding intervals/IEEE64 accumulation bounds, and useS/E in missingenergy varianceidentity. No arbitrary eventepsilon or forced H+U identity. Successfulstep storage is per-cell aggregate/counters; only failedsteps retain full identities/coordinates, preventing oversized per-step dumps. Primary source catalogue entry SRC-DD4HEP-1-38-SENSITIVE-ENERGY added; no upstream fullsource payload or installs.

Independent observer-protocol review found scope defensible, with exact implementation conditions added beforeobserverdata: positive rawedep filter, unweighted contribution, unitweights/Birks0/nonoptical/ordinarypath audit; exactnativeMeV successfulcell accumulation tobinary32output; asymmetricrounding/subnormal andgamma_n bounds ifneeded; independentA=S+U andseparateH≈S; joint84width covariance overH/A variants withsharedbootstraps; fixedoldcut andexplicitmissingfractiondenominators. Supplied installedEDMheaders SHA:c614269d5de245248908f0c15447ee009e4a542e544cb83f722bf460f045577e (SimCalorimeterHitData.h) and0a348ec786c9a7ae8e2e578c3b9afa42ba7c13ce21497af4c61aa71a86a71460 (MutableSimCalorimeterHit.h). No nativejobs/files byreviewer; executable stillrequires exact-revision assessment afterfreeze.

Initial candidate10k transport/readback/pairedsaved-H analysis completed atcleanstartb24f9db2,816.009759s transport,12workers,10000IDs, twoactionerrors. Preliminarysaved-H globalCV17.8428→13.5559%, fixedtransition44.1838→20.9984%,183→0commoncut tails, explicitlydiagnostic untilcomplete-deposit accounting. No geometry/statisticalpolicyretuned fromthesevalues. Newobserverdiagnostic CMakeconfigurePASS; firstcompilefailed nlohmann-json/dd4hep::json namespacealiascollision, authorusedunique StepJson alias, secondcompilePASS. Noevents/native bythatdiagnosticbinary. Existingnloh3.12.0/uecyhyo header/config directlyverified, noinstall. Finalcleanbuild/control/replay stillpending.

Observer six-file handoff frozen:35 integratedpuretestsPASS; diagnosticC++v3PASS. Rootreview caughtduplicate physicsinitializer registration (installedsetupUserPhysics appends), corrected byfreshSIM +singlewrapper; CPPaliasnamespacecollisioncorrected; strictRNEaudit,narrowruntime-errorcatch, unitweight/Birks0/nonopticalpolicy andboundedper-cellstepstorage included. Alloldsimulation/geometry/readout/helperfilesunchanged. Native Aindependent,Ssuccessful,Uunassigned,Hsavedfloat distinction explicit. Exactqfloatcellclosure, precisionderivedeventbounds, originalerrorcorrespondence, optionalfullreplay, frozenoldcutandjoint84covariance areimplemented. Finalcleanbuild andobservercontrols/replayremainrequired, noauthornativejobs.

## Exact observer source review before dispatch

Explicitgeneric nonauthorSoftEng role.

```json
{
  "id": "LAR-GAP10K-SoftEng-observer-review",
  "role": "SoftEng",
  "input_revision": "37d45a6466c3a9a7384583b0140a1bdc5c61f712",
  "inputs": [
    "docs/validation/lar-gap10k/observer-protocol.md",
    "docs/validation/lar-gap10k/protocol.md",
    "software/analysis/lar_gap/CMakeLists.txt",
    "software/analysis/lar_gap/StepAudit.cpp",
    "software/analysis/lar_gap/compare.py",
    "software/analysis/lar_gap/controls.py",
    "software/analysis/lar_gap/geometry.py",
    "software/analysis/lar_gap/native.py",
    "software/analysis/lar_gap/observed_compare.py",
    "software/analysis/lar_gap/observed_steering.py",
    "software/analysis/lar_gap/observed_transport.py",
    "software/analysis/lar_gap/test_compare.py",
    "software/analysis/lar_gap/test_controls.py",
    "software/analysis/lar_gap/test_geometry.py",
    "software/analysis/lar_gap/test_observed.py",
    "software/analysis/lar_response/steering.py",
    "software/analysis/lar_response/transport.py",
    "software/analysis/lar_response/Audit.cpp"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independent nonauthor exact-revision review of sixnewobserverfiles. Assess direct scintillator positive-step/filter/midpoint/ID semantics, geometry/readout unchanged, non-RNGobserver callbackorder/state, unitweights/Birks/optical/fastsim policy, once-only steeringinitializer, per-cell nativeS plus independentA/U closure, exact binary32 savedcell comparison andderivedIEEE64 event bounds, all-event/cell replay/provenance, errorlogfailurematching, frozenoriginaltailthreshold andsharedH/A/U bootstrap/covariance84. Check meaningfulnegative tests andnew isolatedCMake dependencies. Existingcode/native/physicsheldfixed; raw observed controls may beunderway atbuild/lar-gap10k/observed, read-only onlywhencomplete. No native/DDSim/events orfilewrites/nesteddelegation. Returnconcrete blockers promptly beforeproduction; no style-onlyexpansion.",
  "deliverable": "Return exact revision, prioritized findings orno actionablefindings, actualpure checks andsource/artifact bindingsverified, remaininglimits. Coordinatorrecordsassessment; no acceptance.",
  "completion": "Do not infer relative/absoluteenergyintegrity fromtests alone; auditmatchingdefinition/source carefully. Assess onlyboundedobserverandanalysis, no gateweakening ornewphysics. Rootfreezesallsource andrunscontrols/replays separately."
}
```

## Observer loader interface failure and correction contract

Freshcompiledobserver atclean d31cb719 builtPASS. Bothobservedserial24 jobs exited1 beforegeometry/events becauseDDSim executessteering without__file__, whileourwrapperusedPath(__file__). Failedoutputsremainignored observed/standard andcandidate. Thisissteeringinterfaceonly; no observer physicsdata or source/tolerancechange. SameCPPbinaryhashcanbe reusedsinceonlydriver/steering/testfixneeded. Contractrecordedbeforedispatch:

```json
{
  "id": "LAR-GAP10K-SoftEng-observer-loader-fix",
  "role": "SoftEng",
  "input_revision": "37d45a6466c3a9a7384583b0140a1bdc5c61f712",
  "inputs": [
    "software/analysis/lar_gap/observed_steering.py",
    "software/analysis/lar_gap/observed_transport.py",
    "software/analysis/lar_gap/test_observed.py",
    "docs/validation/lar-gap10k/observer-protocol.md"
  ],
  "mode": "write",
  "writable_paths": [
    "software/analysis/lar_gap/observed_steering.py",
    "software/analysis/lar_gap/observed_transport.py",
    "software/analysis/lar_gap/test_observed.py"
  ],
  "task": "Fix concrete observer-gate loader failure before any geometry/events: DDSimexec steering namespace doesnotdefine __file__; observed_steering line6 Path(__file__) raisesNameError in both serial24 runs. Preserve failed dirs build/lar-gap10k/observed/{standard,candidate}/serial24 and logs. Use explicit bound ROOT path from driver environment orPYTHONPATH; avoidinferringsteeringpathfrom__file__, do not modify oldsteering/transport orCpp/cuts/geometry. Add meaningful native-loader-contract purecontrol executing steering source with __file__ absent and fakeDDSim/oldconfigure deps, checking singleinitializerregistration/originalrunsettings. Rootwillfreshdirs/replay using sameunchanged compiledobserverbinaryCppsourcehash. No native/DDSim/filesoutsideowned, no nesteddelegation, commits/publication.",
  "deliverable": "Return exactfixfiles/sourcehashes, actualmeaningfultests, freezeandCLIunchangedorchanges. Rootcurates.",
  "completion": "Resolveinterfacebugwithouttouchingfrozenphysical/observerCpp policy, no broaderfeatures or gateweakening. No authornativeevents."
}
```

Loaderfix frozen: explicitboundrepositoryenv/PYTHONPATH replaces__file__; installedDDSim alsoexecuteswithseparateglobals/locals, so wrappercallbackimportsdependenciesinternally. Newpuretestexecutesactualwrapperwithsplitnamespaces/no__file__, invokesstoredcallback andprovesonemapinitializer/libraryloadplusoriginalsettings.37integratedpuretestsPASS; CPPsource/binary3a99... unchangedfromcleanbuildd31. Freshobserver-v2 outputs willretainallfirstfailedlaunches.

## Exact loader-fix review contract before dispatch

Explicitgeneric nonauthorSoftEng.

```json
{
  "id": "LAR-GAP10K-SoftEng-observer-loader-review",
  "role": "SoftEng",
  "input_revision": "5d23317538bde89c3caf2e16c574679bed332b47",
  "inputs": [
    "software/analysis/lar_gap/observed_steering.py",
    "software/analysis/lar_gap/observed_transport.py",
    "software/analysis/lar_gap/test_observed.py",
    "docs/validation/lar-gap10k/observer-protocol.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Close priorP1 loaderbug on exactcorrectedrevision: explicitROOTenv/PYTHONPATH, no __file__ dependency, callbacksownimportsunderDDSimsplitglobal/localexec, oneoriginalmapinitializer/restoredrunseed; newmeaningfulexec regression. Compareto37d45a..., allCPP/geometry/physics/statsunchanged. Read-only, no native/DDSim/files/nesteddelegation. Rootfreshcontrolsarestartingunderobserved-v2.",
  "deliverable": "Return exacttarget/fixclosure orconcreteissues, actualtestsandlimitations, incorporatewithongoingfullobserverreview.",
  "completion": "No broaderexpansion/retestingoldnativewithoutconcretecause; reviewactualsourceandloadercontract. No acceptance."
}
```

Allsix observed-v2 short runs (serial24/MT24/pilot100 inbothgeometries) completedwithcell-levelobserverclosureandmatchedserialMTcontrols atd3c3cfc6/5d233175 sources. NonauthorreviewP1loaderclosed37exacttests; P2missinglate serial-maprevalidation remains. CoordinatornowownsONLYobserved_transport.py/test_observed.py forread-onlyartifactguardandadversetests; authorhasnomorewrites. CPP/binary/steering/runfunction/physics/mathwillstaybyteidentical. Reviewerexplicitlyaccepts reusingcompletedshortMC withoriginalreceiptsplusaseparatehash-boundnewguardverificationrecord; no producerhashes/auditorclaimsrewritten orcheck_sourcesweakened. Productionwillusecorrectedguardcheckpoint.

CoordinatorP2fix addsverify_serial_maps tobothfreshauditandcached evidencepaths, requiringdualreceipt/readback hashes, exactparsedrecordequality, PASS/mainthread/raw43648/context43648. Fifteenobserverprecision/loader/mapadversetestsPASS, includingmissing/mutated/stale/parsedmismatch/nonserial/incompletecases. No C++/steering/run/mathchanges, no tolerancerelaxation. Separate actualsix-run correctionverification willbindnewverifier tooldcontrol/pilotartifactswithoutrewritingthem.

Sixrealcompletedobservercontrol/pilotchains reverifiedwithnewguard; codeASToflaunch/accounting methods andCPP/build/steering/statistics byte-identicalto5d233175. Compactnewguardverificationrecordretainsoldsourceclaims/fullartifacthashes; no producer/readbackrewrite. ExactP2closurecontractbeforedispatch:

```json
{
  "id": "LAR-GAP10K-SoftEng-map-guard-review",
  "role": "SoftEng",
  "input_revision": "9f8aac37c5e5949d3104ec447a3fa89f7a1d5252",
  "inputs": [
    "software/analysis/lar_gap/observed_transport.py",
    "software/analysis/lar_gap/test_observed.py",
    "docs/validation/lar-gap10k/controls-map-verification.json",
    "docs/validation/lar-gap10k/observer-protocol.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "CloseP2exactguard: dual receipt/readbackmapsSHA, parsedrecordequality, PASS/mainthread/43648raw&contexts, freshauditandcached.evidence paths. Fifteenobserverpuretests passcoordinator, inclmissing/mutation/stale/equality/nonserial/incomplete. Verifyseparatecontrols-map-verification record source0034eb0f oldsixshortMCretainedunchanged d3c3cfc6; sourceASTandCpp/build/steering/statistics unchanged from5d233175. ConfirmnoMCrerunneededforonlypostprocessingguardchangeaspreviousassessment, no sourceguardsrelaxed oroldreceiptsrewritten. Read-only/noMC/native/files/nesteddelegation. Productionwillfreshcorrectedcheckpointafterclosure.",
  "deliverable": "Return exactrevision,P2closureorfinding, actualchecks/artifactbindings, limits. Coordinatorcurates.",
  "completion": "Assessboundedfixonlyandall sixrealretainedmaps ifuseful; no broadretuning. No acceptance."
}
```

## Logical/physical name-schema observation during full replays

Actualcompletedobserverfailuresrecordlogicalw1_gap1/w2_gap0, whileoriginalSDlogsphysicalw1_gap1_7/w2_gap0_6. Currentliteralname matcher rejects these unlikeidentities; rootreproducedValueError onbothpartiallycompletedstreams. RawIDs/localpoints/positiveenergy areavailableandunchanged. No MCfileoroldruntimeproducerwillbeedited. Separatepostprocessingauditor/readbackaddendum resolvesnamesfromhash-boundnativephysicalplacementcatalog, preservingexactrawID/point/count/closure andsourceguards. Itwillwritenewderivedoutputs/proofswithownauditorrevision, retainingalloriginalraw/failedreadbacks. Thisavoidsrerunningunchangedphysicsforreader-schemaerror anddoesnotweakenidentification.

## Separate corrected readback contract before dispatch

ExplicitgenericSoftEng, threeNEWfilesonly; allruntimeproducers/protocolfrozen.

```json
{
  "id": "LAR-GAP10K-SoftEng-separate-reaudit",
  "role": "SoftEng",
  "input_revision": "a9b34ed3208624ff37ce04bac6826c1af3b8bc95",
  "inputs": [
    "docs/validation/lar-gap10k/readback-addendum.md",
    "docs/validation/lar-gap10k/observer-protocol.md",
    "software/analysis/lar_gap/observed_transport.py",
    "software/analysis/lar_gap/observed_compare.py",
    "software/analysis/lar_gap/StepAudit.cpp",
    "software/analysis/lar_gap/native.py",
    "software/analysis/lar_gap/geometry.py"
  ],
  "mode": "write",
  "writable_paths": [
    "software/analysis/lar_gap/observed_reaudit.py",
    "software/analysis/lar_gap/observed_recompare.py",
    "software/analysis/lar_gap/test_reaudit.py"
  ],
  "task": "Implement ONLY3newpostprocessingfiles perreadback-addendum; everyoldruntimeproducer/protocol MUSTremainunchanged (full20kMCongoing source2860f262). ActualCPPfailurevolume islogical(w1_gap1,w2_gap0), SDlogphysical(w1_gap1_7,w2_gap0_6); oldliteralcomparisonwrong. Buildexactaliascatalogfromboundnative snapshotplacements.jsonl sensitiverecords volume=>pathlastnode, verifyledgerhash viaexistingnativeproof; matchrawIDexact, physicalnameincatalogforactuallogicalname, sameprintprecisionpoint/count. No regex-onlyforgiveness, no guard/tolerancechanges. NewreauditorrepeatsALL per-event/per-cellq/nativeA=S+U/savedrounding/weight/ID/worker/maps/source/library/log/primary/rawartifactchecks, reusingunchangedpurehelperswherepossible. OriginalMCsourceguardcheck_sources(receipt.producer_sha256) remainsvalidbecauseold6filestayexact; doNOTmutate/monkeypatcholdmodulesor__file__, doNOTalterproducerhashes. Ownfreshoutputdirectory forderivedevents/proof, explicitnewauditorpath/sourceSHA/revision/helperbindings. Preserveoldreadback/observed-events partialledger. Canreuseoldcommonreadbackonlyafterallhashchecksincludingnewserialmaps, orcreateifabsent. Fullretained10k replayasold. New.evidence mustvalidateNEWproofandledgerwithitsownauditor identity ratherthanforgeoldauditSHA. Recompareloadsnew.evidence andcallsUNCHANGEDobserved_compare.summarize/statistics/plot(data-onlywrapper) preservingalloriginalbins/tailcut/bootstrap84cov. Newanalyzerhash/sourceexplicit; compactoutputs<1MiB. Addrealisticlogical/physicalalias positivefixture andnegativewrongraw,wrongname/copy,missingnativealias,point/count/tamperchecks. rootrunsnewauditorafterMCreceipts; noCpp/native/DDSim/authordelegation/commits. Needboundedreadyfilesquickly, notrearchitecture/generalhistorysupport.",
  "deliverable": "Return3newfrozenfiles, meaningfultests, exactCLI audit--sample--run--output--retained-run optional/native-report fromreceipt, andnewanalyze/plotrecipe; sourcebindings/limits. Rootownsrecords/runtime/publication.",
  "completion": "Noeditsanyoldfileorartifact. Nativealiascatalogactualnodeidentitycorrect; no tolerance/gateweakening or fakeoldproof. Rootcommit beforecorrecteddataassessment, noauthorMC. Independentreviewwillcheckexactnewrevision."
}
```

## Corrected postprocessing frozen and nonauthor contract

Author froze only three new files at d3f49420d6bd776b6b6891071801bf8dd6cd1216. Root independently ran all47 pure tests PASS. All old runtime source bytes stay frozen. Both full10k transports reached readback; original literal-name mismatch remains preserved. Explicit generic SoftEng independent review contract recorded before dispatch:

```json
{
  "id": "LAR-GAP10K-SoftEng-reaudit-review",
  "role": "SoftEng",
  "input_revision": "d3f49420d6bd776b6b6891071801bf8dd6cd1216",
  "inputs": [
    "software/analysis/lar_gap/observed_reaudit.py",
    "software/analysis/lar_gap/observed_recompare.py",
    "software/analysis/lar_gap/test_reaudit.py",
    "docs/validation/lar-gap10k/readback-addendum.md",
    "docs/validation/lar-gap10k/observer-protocol.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Review ONLY separate three-file postprocessing correction against frozen previous producer. Logical failure volume w1_gap1/w2_gap0 versus physical SD-log w1_gap1_7/w2_gap0_6 must resolve via hash-bound native sensitive placement catalog, with exact raw ID and same printed local point/count gates. Verify original six runtime files/protocol unchanged, no source hash forgery or monkeypatching, all original raw/library/worker/map/precision/ROOT/primary checks maintained, own fresh derived proof and explicit new auditor/helper identity enforced by evidence. New analyzer uses frozen summarize/statistics with original bins/cut/1000 bootstrap/84 covariance. Root ran47 tests PASS. No native/MC/edits/delegation. Reuse live full transports at2860f262 valid because postprocessing only; old literal-name audit failure preserved. Return exact-target findings or closure and actual narrow checks.",
  "deliverable": "Independent exact d3f49420 three-new-file review, severity/line for issues, source/precision/identity gate assessment and limits; do not claim physical acceptance.",
  "completion": "Bounded read-only assessment, no broader redesign or rerunning old native jobs. Coordinator owns runtime/data/records."
}
```

Nonauthor SoftEng closed the d3f49420 identity correction with no actionable findings:47 exact-source tests, all frozen runtime/protocol bytes unchanged from2860f262, both actual43648-sensitive native catalogs hash-verified, and actual3standard/2candidate failure correspondence PASS with exact raw IDs/catalog aliases/printed points/counts. This does not substitute for full corrected per-cell/energy/replay audits. Full transports both exited0 with10000 events/12workers, clean source-state and unchanged producer/library guards.

## Completed transports, short controls and current usage recovery

Both observed full transports at2860f2620ef84e12c21e3d6108876dd7e0609f5e exited0:10000events/12workers each, clean source_state[], unchanged producer/library bytes. Wall times1013.970544s standard /1056.324751s candidate reflect simultaneous24-worker observation load, not an initialization/performance benchmark. Complete common saved-primary/canonical-hit readback reached10000events each. Separate corrected full auditors are running into fresh build/lar-gap10k/reaudit/{standard,candidate}; original literal-name audit outputs remain preserved.

Curated exact usage-only recovery selected17 completed current-task child turns by recorded assignment/followup sequence and exact turn IDs;61,185,035 total observed tokens =60,963,099 input +221,936 output, cached/reasoning subsets not additive. Active root and all old tasks/cumulative thread totals excluded. Models/providers/client version unavailable. Sole canonical owner is this paired session. Final PhysVal turn will be added after completion. Current records validate:110tasks/54documents/24rounds,295session records,119PR interaction records; token site564disjoint dated turns. All introduced history blobs examined so far are below1MiB with no raw ROOT/XML/HEPEvt/event payloads.

Both original full observer audits exited1 exactly at the anticipated logical/physical literal-name matcher, after completing full common saved readback and per-cell/native-energy loops. Raw ROOT/workers/receipts and old complete derived ledgers are retained unchanged. Separate corrected auditors use native-catalog aliases with the independent reviewed source identity and fresh outputs; no simulation rerun or producer relabeling. Original lar10k README receives an additive saved-H completeness annotation rather than regenerated tables/artifacts.

## Final full-population closure and conditional result

Both separate corrected audits exited0/PASS at e8450d753b4378520d1f5daa98433a7fc85f40a9:10000 primaries each,3standard/2candidate failed steps fully accounted; every saved event/cell/energy/position fingerprint and primary/signal vector equals the retained geometrically identical10k reference, zero differing events. Per-cell exact binary32 output and native A=S+U bounds pass; U sums1.188391019896783MeV standard and0.14899656686392543MeV candidate. No segmentation guard/readout change or invented cells.

Corrected analysis and plots at unchanged e8450d75 exit0 with frozen1000 shared whole-primary bootstrap/seed13001000. Complete-A global SD/mean17.8427835%→13.5559382%, fixed999transition44.1838377%→20.9983524%. Paired candidate-standard width−4.2868453pp (95%[−4.8021389,−3.7776309]) global and−23.1854853pp ([−25.9333327,−20.6036906]) transition; fixed threshold183→0 tails, zeros0both. Eight direct NumPy global/transition A/H moment/population/tail checks independently match summary. All84 covariance variables retained/hash-bound. Full scalar precision/identity/failed-step information stays in ignored raw ledgers; only477202byte compact summary,215586byte covariance,33604byte execution bindings and selected scientific figures curated.

Root visually inspected complete-A angular widths/means/common tails and signed/full-phi/energy controls: labels/intervals readable, ECAL palette and variant styles retained. Fontconfig unwritable shared-cache warning did not prevent successful Matplotlib local-cache rendering. Native/readout physical source bytes remain frozen. Interpretation stays conditional gap sensitivity, not intrinsic resolution, engineered400mm fit or LAr/SiW technology selection. Nonauthor SoftEng review did not author the new three-file correction, but had authored older unchanged common transport helpers; separate final PhysVal assessment follows.

## Separate final PhysVal contract before dispatch

Explicit generic PhysVal, exact completed result evidence; no human sign-off.

```json
{
  "id": "LAR-GAP10K-PhysVal-final",
  "role": "PhysVal",
  "input_revision": "777452601a742aa267f63c2cfd37d71aba830893",
  "inputs": [
    "docs/validation/lar-gap10k/README.md",
    "docs/validation/lar-gap10k/summary.json",
    "docs/validation/lar-gap10k/width-covariance.json",
    "docs/validation/lar-gap10k/execution.json",
    "docs/validation/lar-gap10k/native-validation.json",
    "docs/validation/lar-gap10k/protocol.md",
    "docs/validation/lar-gap10k/observer-protocol.md",
    "docs/validation/lar-gap10k/readback-addendum.md",
    "docs/validation/lar-gap10k/reproduce.md",
    "software/analysis/lar_gap/observed_reaudit.py",
    "software/analysis/lar_gap/observed_recompare.py",
    "software/analysis/lar_gap/observed_compare.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independent final scientific assessment ONLY of the exact curated completed conditional10k gap result. Both corrected full audits PASS,10000 events each; all native A=S+U/exact cell float32 gates and full retained every-event/cell/energy/position replay exact0differences. Original3/2 positive-step errors remain explicitly U=1.188391019896783/0.14899656686392543MeV, no guard/cell change. Assess source/proof/native/input/library bindings, primary denominators including fixed999 transition and fixed originalcut; independently rederive A/H global/broad/fine point moments/counts and U metrics from actual bound ignored build/lar-gap10k/reaudit/{standard,candidate}/derived-events.jsonl. Root8 NumPy direct moment checks pass. Inspect frozen1000 seed13001000 shared-primary bootstrap intervals/contrasts and separate84covariance/hash/order; bounded re-inference if useful, no newMC/native or broad old-code audit. Judge if improvement is robust to missing deposits/float32, and claims/plots/reproduction correctly scoped ECAL-only conditional800->400 warmgap, unchangedmaterials/localservices/readout; no engineeredfit/intrinsicresolution/technologyacceptance. Root visual QA four principal charts complete. All47 pure tests and nonauthor SoftEng newreader source/identity review closed. Nonauthor SoftEng authored older unchanged shared transport helpers; you provide separate scientific assessment. Read exact pinned revision then actual raw ledgers via curated hashes. No writes, no native/MC, no delegation, no approvals/signoff.",
  "deliverable": "Exact target revision, actual independent data/statistical/identity checks and findings/severity or no actionable finding; summarize key estimates/CI/U totals, scoped conclusion and remaining physical/readout limitations. Coordinator curates return.",
  "completion": "Bounded final result assessment, not general redesign: enough to finalize draft PR and honest user result. Existing native/precision source reviews need not be repeated absent concrete concern. No human approval or acceptance."
}
```

DraftPR144 created/attached: https://github.com/asalzburger/nodd/pull/144, title Calorimeter: measure10k electron response with a smallerLAr gap; campaign:calorimeters and scope:baseline-design. ParentPR143 reverified open/draft at8dfa8573; base codex/lar-routing-dd4hep. First published head d5c612cf. Same public project destination/authorized curated artifacts; no raw data/new recipient/readiness/merge. Authenticated gh fallback because connector write permission was unavailable; no automatic approval rejection. Final result assessment and current-task usage/PR-ledger closeout continue.

## Independent final assessment and accounting

PhysVal exact777452601a742aa267f63c2cfd37d71aba830893: no actionable findings. Rehashed both derived ledgers/proofs and source/helper/library/sample/native-ledger/map/worker bindings; checked every event/collection closure bound and retained primary/saved-signal replay. Independently rederived ALL A/H projection moments/populations/zeros/tails and U metrics, fixed broad populations3999/999/5002. Independent1000 direct-index resampling (different arithmetic from weighted raw moments) reproduces global/10|eta|/10fine/3broad intervals with max endpointdifference9.72e-14 and all84 covariance elements within8.64e-17. Missing/quantization correction changes global gap-width contrast by~0.00000336pp, so it cannot explain the observed4.28685pp improvement. Assessed conditional ECAL-only sensitivity; no full ROOT cell reparsing or separate visualQA by reviewer, clearly distinguished from coordinator runtime/QA. No files/native/MC/human acceptance by reviewer.

Usage-only recovery appended final completed PhysVal turn01a1db38-2f77-7951-a0b7-9c1a26b65062, matched to explicit final dispatch. Canonical current-task scope now18 completed child turns:64,106,016 input +230,280 output =64,336,296 total; cached62,756,480 input and reasoning110,342 output are subsets. Model/provider/client version unknown; active root unfinalized, no estimate, all oldtask turns excluded. Task labelled M1/StageB/WS-CALO/calorimetry and bounded TASK-LAR-GAP10K completion; no design or engineering approval advance.

## Draft PR and bounded task closeout

DraftPR144 is attached and stacked on the still-open routing branch; final body includes exact77745260 independent result assessment, conditional bounds and18 completed-turn coverage. Public interaction capture at2026-11-14T18:05:39.669678Z records published head d5c612cf; subsequent record-only closeout preserves the executed/audited source and all scientific artifacts. Own current journal is the sole usage owner, referenced by pr-0144.

Final local project/session/inventory/interaction/token validations PASS:110tasks,54documents,24review rounds;295paired sessions;69components/104families/55inputs/12pins;120interaction ledgers;565unique dated token turns. Token preview and session coverage summary build successfully. History inspection excludes raw simulation/input/native data and every new blob is below1MiB; largest is477202byte binwise summary. No tolerances, source guards or reference outputs weakened. Paired session closes with partial coverage because active coordinator counters remain unavailable. The dedicated branch final record commit/push and draft-head/hosted-CI status verification are operational closeout; no merge/ready action or human approval is inferred.
