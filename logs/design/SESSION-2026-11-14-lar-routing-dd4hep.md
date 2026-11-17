# SESSION-2026-11-14-lar-routing-dd4hep — native service routing prototype

## Scope and selected requests

User requested a DD4hep version of the routing, allowing bend approximation while
keeping material. On explicit clarification selected existing steel/N2 pipe
materials and retained cable envelopes. New isolated implementation branch/worktree
starts at3fca74b70709345a9440b17cf23acb40aab1f945, stacked on the existing proposal
branch; production geometry and sign-off states remain unchanged.

Read governing AGENTS/PROJECT/design docs. Using nodd-coordinate/design-evidence/
review-validation and acts-spack. Preflight reported changed setup/lock fingerprints;
warned before dependency use and verified current DD4hep/DDG4 imports, ROOT6.40.04,
Geant411.4.3 and installed datasets. Fresh software/env/run.sh activation used;
sandbox sysctl/ps warnings did not prevent successful runtime checks. Fingerprints
are captured in ignored build/lar-routing/environment-observation.json. No shared
installation or source download changed.

Initial design input records the user-selected material boundary, common-endpoint
mass matching, proposed mitered CutTube approximation and separate native versus
integrated-fit gates. No guessed cable/jacket material is introduced.

## Contracts recorded before dispatch

Explicit generic role fallback, not native profile loading. Source ownership is disjoint; only SoftEng writes code, coordinator owns records.

```json
[
  {
    "input_revision": "b0d54812e668714c14a3193e57ed4365f2fcbd01",
    "inputs": [
      "docs/design/inputs/DES-032-routing-dd4hep.md",
      "docs/design/inputs/DES-032-side-rear-routing.md",
      "tools/lar_calorimeter/barrel_geometry.py",
      "tools/lar_calorimeter/barrel_services.py",
      "tools/lar_calorimeter/services.json",
      "prototypes/calorimeter/LArBarrel.cpp",
      "prototypes/calorimeter/CMakeLists.txt",
      "software/env/run.sh"
    ],
    "completion": "Return assignment ID, exact input/source versions, conclusions and actual checks/failures/limits. No native engineering acceptance or nested delegation. Do not commit or push; coordinator owns Git/publication.",
    "id": "LAR-ROUTING-SoftEng",
    "role": "SoftEng",
    "mode": "write",
    "writable_paths": [
      "prototypes/lar_routing/CMakeLists.txt",
      "prototypes/lar_routing/LArRouting.cpp",
      "tools/lar_calorimeter/routing.py",
      "tools/lar_calorimeter/routing_config.json",
      "tools/lar_calorimeter/routing_native.py",
      "tools/lar_calorimeter/routing_transport.py",
      "tools/lar_calorimeter/test_routing.py"
    ],
    "task": "Implement the isolated DD4hep routing component and reproducible exporter/native checks per the new design input. User explicitly selected existing20mm-OD18mm-ID steel/N2 construction; cable/jacket envelopes stay unmaterialised metadata, never fake material. Common start |z|3000 R2735.3 and downstreamhand-off4800 produce same4968.343720697463mm analytic path forold/new; preserve both constituent volumes via sqrt(Lanalytic/Lpoly) scaling ofradii at unchanged density/recipe. Prefer mitered CutTube pieces; installed DD4hep Shapes.h confirms CutTube(rmin,rmax,dz,startPhi,endPhi,lx,ly,lz,tx,ty,tz). Exact join normals/proper transforms, 5degree default arcstep, guard degeneracy, XMLunits explicit. Build a standalone factory (no production CMake change), source-bound expected inventory, native count/recipe/mass/overlap/joint-navigation audit and small Geant4conversion/transport smoke. Use scoped meaningful tests, resolution/negative controls. May write ignored build outputs under build/lar-routing/softeng only. Node preflight has changedsetup/lock warnings already shown; currentROOT6.40.04, DD4hep/DDG4 imports, Geant411.4.3/datasets verified by coordinator in fresh software/env/run.sh. Read acts-spack instructions before native use; never install/concretize. Report integration contacts rather than cutting existing calo material. Root owns docs/inventory/tracking/logs; propose interface improvements via message.",
    "deliverable": "Return bounded implementation/assessment to coordinator; tracked source only within owned paths, actual native evidence ignored if generated."
  },
  {
    "input_revision": "b0d54812e668714c14a3193e57ed4365f2fcbd01",
    "inputs": [
      "docs/design/inputs/DES-032-routing-dd4hep.md",
      "docs/design/inputs/DES-032-side-rear-routing.md",
      "tools/lar_calorimeter/barrel_geometry.py",
      "tools/lar_calorimeter/barrel_services.py",
      "tools/lar_calorimeter/services.json",
      "prototypes/calorimeter/LArBarrel.cpp",
      "prototypes/calorimeter/CMakeLists.txt",
      "software/env/run.sh"
    ],
    "completion": "Return assignment ID, exact input/source versions, conclusions and actual checks/failures/limits. No native engineering acceptance or nested delegation. Do not commit or push; coordinator owns Git/publication.",
    "id": "LAR-ROUTING-SysArch",
    "role": "SysArch",
    "mode": "read-only",
    "writable_paths": [],
    "task": "Assess the physical interface boundary of this material-preserving standalone route prototype. Check matched path scope/counts, known20mm cooling-pipe recipe versus100mm emptyjacket, source/header ambiguity, closedwall/board/ring contacts and whether any full-context composition can be called valid. Recommend bounded integration diagnostics without silently cutting/removing existingcalorimeter material. No native runtime needed; no artifact writes.",
    "deliverable": "Return bounded implementation/assessment to coordinator; tracked source only within owned paths, actual native evidence ignored if generated."
  },
  {
    "input_revision": "b0d54812e668714c14a3193e57ed4365f2fcbd01",
    "inputs": [
      "docs/design/inputs/DES-032-routing-dd4hep.md",
      "docs/design/inputs/DES-032-side-rear-routing.md",
      "tools/lar_calorimeter/barrel_geometry.py",
      "tools/lar_calorimeter/barrel_services.py",
      "tools/lar_calorimeter/services.json",
      "prototypes/calorimeter/LArBarrel.cpp",
      "prototypes/calorimeter/CMakeLists.txt",
      "software/env/run.sh"
    ],
    "completion": "Return assignment ID, exact input/source versions, conclusions and actual checks/failures/limits. No native engineering acceptance or nested delegation. Do not commit or push; coordinator owns Git/publication.",
    "id": "LAR-ROUTING-PhysVal",
    "role": "PhysVal",
    "mode": "read-only",
    "writable_paths": [],
    "task": "Assess the scientific/material preservation method before implementation. Independently derive common-endpoint old/new analytic path equality, constituent referencevolumes and radius correction for chordal mitered CutTubes. Check preservation ofcomposition/density versusV/mass/X0 and limits for directional material budget and exactcircularshape, joins/overlaps/resolution guards. User selected existingpipe materials and cableenvelopes; do not infer fullservicebill or physical100mm jacket. Recommend discriminating native/G4 validation, no native runtime or artifact writes needed.",
    "deliverable": "Return bounded implementation/assessment to coordinator; tracked source only within owned paths, actual native evidence ignored if generated."
  }
]
```

## Implementation handoff and candidate cycle

SoftEng completed seven owned files;55LAr controls including16routing tests pass.
Initial native/G4 evidence verifies2752pieces,5376jointpoints/2688crossings,
zero10nm overlaps and three saved native geantino events pervariant with aimed
miters. Retained adverse diagnostics: initial ROOTteardown failure (explicit
Detector.destroyInstance/MTcleanup fixed); no-HC passive ROOT has noeventframes
(actualstepJSONL is evidence); G4gun roundspositionUI (only fixturevertices are
explicitly quantized, strict observed-input check retained). Existing sources
are frozen for a clean candidate build/export/validation cycle.

Root identified direct use of existing nlohmann-json3.12.0 /uecyhyo; made its
CMake target dependency explicit and registered this preinstalled header-only
package in the inventory. No dependency installed. Prior v3 receipts correctly
reject the CMake-only source-binding change; they are diagnostics, not the final
executed candidate. Task record state spelling was corrected to existingactive.

Independent SysArch and PhysVal initial contributions atb0d54812 confirm matched
path/material arithmetic and construction conditions, but explicitly reject any
claim of integrated fit. Full native context sampling already witnesses duplicate
upstream pipes and closed walls, with actualpipe versusemptyenvelope diagnostics
kept separate. Final source-bound results and exact-revision review follow.

## Exact candidate/evidence reviews recorded before dispatch

Explicit generic roles; separate scientific, physical-interface and nonauthor software review. Nativeexecution8210fbcc was clean; later commits only curate evidence/reporter/recipe.

```json
[
  {
    "input_revision": "f4c15efeb3e0c62bbe5611b53df56b57fb7bc199",
    "inputs": [
      "docs/design/inputs/DES-032-routing-dd4hep.md",
      "docs/validation/lar-routing-dd4hep/README.md",
      "docs/validation/lar-routing-dd4hep/reproduce.md",
      "docs/validation/lar-routing-dd4hep/results.json",
      "docs/validation/lar-routing-dd4hep/environment.json",
      "tools/lar_calorimeter/routing.py",
      "tools/lar_calorimeter/routing_config.json",
      "tools/lar_calorimeter/routing_native.py",
      "tools/lar_calorimeter/routing_transport.py",
      "tools/lar_calorimeter/routing_context.py",
      "tools/lar_calorimeter/routing_report.py",
      "tools/lar_calorimeter/test_routing.py",
      "prototypes/lar_routing/LArRouting.cpp",
      "prototypes/lar_routing/CMakeLists.txt"
    ],
    "mode": "read-only",
    "writable_paths": [],
    "deliverable": "Return concise prioritized findings or no findings, actual checked evidence/commands, exact target/source revisions and remaining limits. No file edits or nested delegation. Coordinator retains review in paired session.",
    "completion": "Review source/curatedresults bindings rather than infer acceptance from PASS; disclose any missing checks. Native re-execution not required absent a concrete concern; if needed follow acts-spack current verification. Do not modify artifacts, commit or publish.",
    "id": "LAR-ROUTING-PhysVal-final",
    "role": "PhysVal",
    "task": "Independently assess final constituent conservation, CutTube/miter invariants and resolution, native/G4 conversion plus actual saved-step proof, source cleancheckpoint8210/filehashbinding to later reporter code, selectedprimary versus rawdata interpretation, uncertainty/claim scope. Replay scalar arithmetic and local bound evidence as useful; no response/integratedfit acceptance."
  },
  {
    "input_revision": "f4c15efeb3e0c62bbe5611b53df56b57fb7bc199",
    "inputs": [
      "docs/design/inputs/DES-032-routing-dd4hep.md",
      "docs/validation/lar-routing-dd4hep/README.md",
      "docs/validation/lar-routing-dd4hep/reproduce.md",
      "docs/validation/lar-routing-dd4hep/results.json",
      "docs/validation/lar-routing-dd4hep/environment.json",
      "tools/lar_calorimeter/routing.py",
      "tools/lar_calorimeter/routing_config.json",
      "tools/lar_calorimeter/routing_native.py",
      "tools/lar_calorimeter/routing_transport.py",
      "tools/lar_calorimeter/routing_context.py",
      "tools/lar_calorimeter/routing_report.py",
      "tools/lar_calorimeter/test_routing.py",
      "prototypes/lar_routing/LArRouting.cpp",
      "prototypes/lar_routing/CMakeLists.txt"
    ],
    "mode": "read-only",
    "writable_paths": [],
    "deliverable": "Return concise prioritized findings or no findings, actual checked evidence/commands, exact target/source revisions and remaining limits. No file edits or nested delegation. Coordinator retains review in paired session.",
    "completion": "Review source/curatedresults bindings rather than infer acceptance from PASS; disclose any missing checks. Native re-execution not required absent a concrete concern; if needed follow acts-spack current verification. Do not modify artifacts, commit or publish.",
    "id": "LAR-ROUTING-SysArch-final",
    "role": "SysArch",
    "task": "Assess exact final contextdiagnostic and physical claims. Verify nativeunchanged ECAL witnesses reflect existingpipe continuation, bathdisplacement, closedwalls/vacuum and separate100mm/20mm envelopes; no placedoverlay, no400mmshift orHCAL/magnetclaim. Check32route multiplicity/materialreference and sourcebindings. Review finalintegration limits/recipe."
  },
  {
    "input_revision": "f4c15efeb3e0c62bbe5611b53df56b57fb7bc199",
    "inputs": [
      "docs/design/inputs/DES-032-routing-dd4hep.md",
      "docs/validation/lar-routing-dd4hep/README.md",
      "docs/validation/lar-routing-dd4hep/reproduce.md",
      "docs/validation/lar-routing-dd4hep/results.json",
      "docs/validation/lar-routing-dd4hep/environment.json",
      "tools/lar_calorimeter/routing.py",
      "tools/lar_calorimeter/routing_config.json",
      "tools/lar_calorimeter/routing_native.py",
      "tools/lar_calorimeter/routing_transport.py",
      "tools/lar_calorimeter/routing_context.py",
      "tools/lar_calorimeter/routing_report.py",
      "tools/lar_calorimeter/test_routing.py",
      "prototypes/lar_routing/LArRouting.cpp",
      "prototypes/lar_routing/CMakeLists.txt"
    ],
    "mode": "read-only",
    "writable_paths": [],
    "deliverable": "Return concise prioritized findings or no findings, actual checked evidence/commands, exact target/source revisions and remaining limits. No file edits or nested delegation. Coordinator retains review in paired session.",
    "completion": "Review source/curatedresults bindings rather than infer acceptance from PASS; disclose any missing checks. Native re-execution not required absent a concrete concern; if needed follow acts-spack current verification. Do not modify artifacts, commit or publish.",
    "id": "LAR-ROUTING-SoftEng-final-review",
    "role": "SoftEng",
    "task": "Independent software review (you did not author this implementation): assess exporter/native C++/Python guards, source/artifact binding, actual vs expected material/shape validation, savedG4step/event controls, reporter/provenance/reproduction and isolatedbuild/dependency boundary. Identify concretecorrectness issues; avoid style-only scope expansion. All nativecomponent outputs at build/lar-routing/final are available read-only ifneeded."
  }
]
```

## Final results and exact-revision assessment

Native execution source was **8210fbcca843d385103dcc14367d0587f9d85ba3**,
clean throughout matched runs. Later commits add the reporter, compact evidence
and recipe; their file hashes bind the retained implementation. Final review
source was **f4c15efeb3e0c62bbe5611b53df56b57fb7bc199**.

Old and new routes retain 4968.343720697463 mm analytic path per representative
route. Across32 routes each has 74.401406957 kg steel and0.809145269 kg N2.
Native material volumes agree to numerical precision. Both standalone models
have2752 wall/core pieces and zero overlaps/extrusions at10 nm; each checks5376
joint material points and2688 boundary crossings. Finer2.5degree construction
has5184 pieces, zero overlaps and10240 joint probes; sagitta falls from0.380711
to0.095189 mm. This establishes geometric refinement, not directional material
budget convergence. Material recipes/densities and both constituent volumes
are preserved by the common radius correction. The existing provisional N2
density and illustrative32-route count remain explicit.

Six actual saved serial geantino events pass conversion, observed-primary and
native step audits. JSONL is actual event/step evidence; the passive no-hit ROOT
outputs are diagnostics. Each variant has5 observed shared-miter transitions,
including2 aimed wall/core crossings. No fake sensitivity was introduced.

Final independent reviews, read-only, files changed:none:

- **PhysVal** (`LAR-ROUTING-PhysVal-final`) found no material scientific issue.
  Independently replayed constituent conservation and intersected observed rays
  with every finite CutTube, including both miter planes. Maximum discrepancy
  from saved material step lengths was6.89e-11 mm old /4.45e-10 mm new. Exactly3
  observed primaries per variant, contiguous steps and zero deposited energy.
  Checked source/fixture/steering/macro/conversion/step hashes, replayed the
  compact report exactly and passed16 routing tests. Did not rerun native jobs.
- **SysArch** (`LAR-ROUTING-SysArch-final`) found no actionable interface/claim
  issue within the stated diagnostic scope. Verified14 assignment input hashes,
  31 context bindings,15 scientific source hashes and old/new/refined/native/G4
  artifact bindings. Confirmed existing-pipe continuation, bath displacement,
  closed walls/vacuum and separate pipe/envelope interpretation. No native rerun.
- **Independent nonauthor SoftEng** (`LAR-ROUTING-SoftEng-final-review`) found no
  actionable software issue. Rebuilt old/new/refined expectations in memory,
  ran9 material/geometry/negative controls, replayed the report exactly and
  re-audited both saved3-event G4 step sets without writing. Verified generated
  and source bindings; no native rerun.

The unchanged-ECAL occupancy diagnostic has54016 samples per variant and
**fit_accepted:false**. Positive existing-pipe and closed-wall contacts require
circuit continuation, ports, daughter displacement and mechanical engineering.
No combined routing overlay,400mm calorimeter shift, HCAL/magnet/forward fit,
response gain, complete cable model or engineering acceptance is claimed.
Cables and100mm jackets remain labelled unmaterialised metadata/envelopes as
selected by the user. Full raw XML/ROOT/placement/event/step/log payloads stay
local under ignored build/. Source-bound compact results, environment and exact
commands are in docs/validation/lar-routing-dd4hep/.

## Selected usage recovery and ownership

[Usage-only inventory](../usage/RECOVERY-2026-11-14-lar-routing-dd4hep.json)
retains exactly six completed current-task child turns with exposed parent/thread
identities and assignment IDs. Reused child threads' earlier task turns are
excluded. The current coordinator turn has not closed and is excluded; it is
neither zero nor estimated. No conversation items, raw private state or provider
model identity were collected. Configured model defaults were not substituted.

Canonical owner is this paired session. Observed input30,678,748 + output88,742
= **30,767,490 tokens** for these six turns only. Cached input29,336,064 and
reasoning output40,827 are included subsets. This is incomplete task coverage,
not a complete task or billing total. All five counters were observed for each
selected turn; execution model/provider/client version remain unknown. Finalized
coordinator usage may be recovered by a later bounded task without duplicating
these turns. Work labelling derives from the retained exact completion dates.

## Publication preparation

Parent proposal PR142 was rechecked open/draft with head
3fca74b70709345a9440b17cf23acb40aab1f945 on2026-11-14. Implementation remains a
separate stacked draft based on codex/lar-gap-hadron-options. Publication is to
the verified public user project asalzburger/nodd (repository1361703051), with
curated project logs authorized by the ongoing repository policy. No new
recipient, raw event payload or private client state is included. No readiness,
merge, design sign-off or accepted-document state is requested or inferred.

Prepublication project/inventory checks passed. Session/token validation first
rejected a qualitative review entry marked PASS without a shell exit code; it
was removed from executable checks and retained in the assessment narrative.
Review outcomes do not invent process exit codes. Subsequent validation recorded
below. Introduced Git objects were inspected relative to the proposal base;
no raw payload extensions and all blobs below1 MiB. Whitespace check passed.

## Selected literal user inputs

> Can you make a DD4hep version out of it? The bent cable can be approximated but the material kept the same.

Material clarification response:

> Reuse existing pipe materials; retain cable envelopes

## Draft publication and closure

Created and attached [draft PR143](https://github.com/asalzburger/nodd/pull/143),
`Calorimeter: add material-preserving DD4hep service routing`, stacked on
`codex/lar-gap-hadron-options` (proposal PR142). Initial published head was
5d92e869ff163ee49897fa1bff24f5a5b1314cf2. Captured public PR metadata and
curated its own interaction record; no public messages sent beyond the authorized
PR. The final bookkeeping commit updates only this task's records/tracking.

Task deliverables are complete for the bounded standalone prototype. Remaining
integration contacts and acceptance are future engineering work, not a passing
fit claim. Reviewers found no actionable issue at the stated reviewed revision.
Repository-wide remote CI may still be pending; local native and governance
checks are the executed evidence, not a claim of remote green status. The paired
session closes with incomplete coordinator-token coverage explicitly retained.

Final local closeout:294 paired sessions and119 PR ledgers validated; token
preview built successfully with547 uniquely owned dated turns. The preview
includes this task's six closed observations and work label, without counting
active coordinator usage. Project validation rejected fractional seconds in the
new PR collection timestamp; normalized that field to its required whole-second
UTC format, preserving the precise original public capture time in the PR ledger.
Project validation then passed109 tasks,54 documents and24 review rounds.
No scientific input or result changed during closeout. Remote CI status is
reported separately from these local passes.
