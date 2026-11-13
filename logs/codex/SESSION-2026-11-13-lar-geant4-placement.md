# SESSION-2026-11-13-lar-geant4-placement — reusable LAr placement investigation

## Scope and selected conversation

User request (exact): “Let's do one thing first: - create a new PR where you inspect the same (re-)placement possibility as done for the Si-W calorimeter also for the ALLIGRO one, aiming at shortening the initialization time of Gean4”.

The assistant treated this as an explicit priority change before the10kresponse
campaign. That unfinished work, its76ed5ce9/221ae331 commits and local uncommitted
records remain preserved in the separate `nodd-lar-10k-response` worktree. No10k
production run was launched. This task uses a new initially-clean worktree,
`codex/lar-geant4-placement`, starting at
`8e99bdb90ca710e07067150a9e34bea3516e9127`.

## Outcome and interpretation

Implemented opt-in `--real-periods` physical mothers for the unchanged inclined
barrel and turbine periods. Legacy assembly export remains the default.
Existing outer negative steel faces, annular clipping and depth bound the new
mothers. No physical leaf, material recipe, replica pose or readout definition
was tuned. Mother material follows the actual enclosing native material; analytic
exclusive-volume residuals are about7e-14 relative or smaller.

The final clean sequential actual-event pair uses the same libraries/probe
source, one worker, B=0, FTFP_BERT,0.7mm range cut and seven20GeV momentum
origin electrons: barrel plus all three wheels on each end. The reference
reaches its first event at522.258406s; the candidate at67.382542s, observed ratio
7.7506486. DDG4 map construction is3.8581236s versus0.1949115s. This is a
single descriptive pair, not a timing uncertainty or stable throughput claim.
The metric includes fixed map/native inventory audit overhead and does not
isolate voxelization. Twelve-worker initialization and response equivalence
remain separate work.

Both probes preserve43648raw sensitive IDs and274689terminal material-leaf
records with identical full-dump hashes. Native shape/material/canonical checks
retain3488768logical cells. Barrel, endcaps and the full ECAL-only union have
zero ROOT overlaps/extrusions at10nm;405union rays are retained. An additional
65matched material rays agree exactly in per-material paths,X0 andinteraction
lengths. Both seven-event samples pass primary/canonical-ID/target-side-and-wheel
checks; cell counts and summed energies also match exactly for these smoke
cases, without a general shower-response claim.

Implementation anchor:8d74a4c1221a19d314881c4deccb2b5986ff425d.
Matched probe anchor:f91578eb3b39e1e2ba52d76af38368bd38501128.
Each clean probe captured launch-time source/configuration/library hashes and
verified them unchanged at exit. Documentation/record edits were in progress.
Compact evidence, source hashes and exact commands are in
`docs/validation/lar-placement/README.md`, `results.json` and `environment.json`.

## Delegation and review

Generic subagents explicitly received prepared SoftEng and PhysVal mandates;
native profile loading was not claimed. SoftEng owned only the two native
factories, two exporters, envelope helper and its controls. PhysVal supplied a
separate prospective assessment and exact8d74 code review, independently
checking partition and face containment and running35controls. The coordinator
owned probing, native execution, material comparisons, result collection,
documentation and publishing. No agent granted human approval or sign-off.
Final exact-revision result review is recorded below when complete.

## Runtime and actual checks

ACTS Spack preflight earlier in this session warned about changed setup/lock
fingerprints. Installed runtime/imports and all Geant4 dataset paths were
reverified before dependent work, rather than trusting the old registry entry.
Existing wrappers were used; shared dependencies were not changed.
Recorded runtime:DD4hep1.38 /3yd4hz3,Geant411.4.3 /wfg55xi,ROOT6.40.04 /szgev3e,
EDM4hep1.1.1 /bsgcccc,podio1.8 /hg64alv.

- Native factories compiled with Release CMake/Ninja and generated component maps.
-37standard-library LAr/helper controls passed.
- `barrel_native.py`, `endcap_native.py` and `combined_native.py audit` passed
  against fresh source-bound opt-in exports.
- The unchanged material-ray tool traced both ECAL-only compacts; all65ray
  differences are0.
- `placement_probe.py --smoke` and `placement_smoke.py` completed both final
  seven-event samples. `placement_report.py` rehashed logs, input compacts,
  inventories, native ROOT geometry and all smoke ROOT files before collection.
- Project, software-inventory, session and token-site checks are recorded in the
  paired JSON; final publishing checks follow the last metadata update.

## Retained failures and corrections

Initial probe steering assumed `__file__`, which DDSim's steering execution does
not provide. An explicit header path in the child environment fixed this. A
subsequent environment-variable ordering error was fixed before measured runs;
both failed attempts remain under ignored build output.

Early exports were produced while the specialist was still finishing source
controls. Native source-binding guards rejected those stale expected manifests
before geometry validation. The complete implementation was committed, fresh
exports generated, and all native checks rerun successfully. No gate was weakened.

The first timing attempt measured a cached volume-manager getter; actual DDG4
map begin/end messages were then parsed separately. PhysVal identified that
`/run/initialize` misses deferred first-run work. The diagnostic `/run/beamOn 0`
was also much shorter than startup of an actual event. The final comparison
therefore uses real first-event messages. The preliminary zero-event pairs and
candidate smoke are retained as diagnostics, not substituted for the clean pair.
The previously failed twelve-worker515s pilot is not a matched baseline.

## Changes, provenance and accounting

Changed files are listed in the paired JSON. Physical source configs and
`reference/manifest.yaml` are unchanged: no new normative external parameter was
adopted. DES032/DES033 remain DRAFT/PROTOTYPE. Project/software records identify
the bounded placement task and its reproducible tools. Large XML/ROOT files,
per-leaf inventories and full logs remain local and ignored. Only compact
results, recipes, code and curated records are published.

Exact client per-turn token counters are unavailable; usage is empty, not zero.
No hidden client state or raw rollouts were collected. The journal summary's
historical observed totals must not be attributed to this task.

## Assignments recorded before dispatch

- {"input_revision": "8e99bdb90ca710e07067150a9e34bea3516e9127", "inputs": ["docs/design/DES-032-allegro-lar-barrel.md", "docs/design/DES-033-allegro-lar-endcaps.md", "prototypes/calorimeter/LArBarrel.cpp", "prototypes/calorimeter/LArEndcap.cpp", "tools/lar_calorimeter/barrel_geometry.py", "tools/lar_calorimeter/endcap_geometry.py", "docs/validation/siw-real-wedge-default/README.md", "prototypes/calorimeter/SiWWedgeEnvelope.h"], "id": "LARPLACE-SoftEng", "role": "SoftEng", "mode": "write", "writable_paths": ["prototypes/calorimeter/LArBarrel.cpp", "prototypes/calorimeter/LArEndcap.cpp", "tools/lar_calorimeter/placement.py", "tools/lar_calorimeter/test_placement.py", "tools/lar_calorimeter/barrel_export.py", "tools/lar_calorimeter/endcap_export.py"], "task": "User explicitly requests separate PR inspecting SiW-like reusable physical placement optimization to shorten Geant4 initialization before10kresponse. Implement bounded opt-in real-period mother prototype for unchanged barrel and turbine geometries. Derive exact envelope from outermost negative absorber skin face to corresponding next-period negative skin face, clipped to full sampling annulus/depth; turbine uses negative outer steel lower face and final gap1 upperface. Verify feasibility, partition and containment. Reuse shape primitives; preserve all leaf shapes/poses/materials, replica poses, raw/canonical IDs. Mother uses actual enclosing material, with zero added material in filled domain; quantify residual. Keep legacy assembly default and expose --real-periods on standalone exporters. Configs unchanged, fail closed unsupported input. Parent owns benchmark/docs and runs native jobs. No commits/publication/nesteddelegation. Communicate API/obstacles early.", "deliverable": "Owned opt-in implementation and focused preservation/partition/negative controls, exact usage returned to parent.", "completion": "Existing28controls and new meaningful controls pass, or concrete geometric impossibility evidenced."}
- {"input_revision": "8e99bdb90ca710e07067150a9e34bea3516e9127", "inputs": ["docs/design/DES-032-allegro-lar-barrel.md", "docs/design/DES-033-allegro-lar-endcaps.md", "prototypes/calorimeter/LArBarrel.cpp", "prototypes/calorimeter/LArEndcap.cpp", "tools/lar_calorimeter/barrel_geometry.py", "tools/lar_calorimeter/endcap_geometry.py", "docs/validation/siw-real-wedge-default/README.md", "prototypes/calorimeter/SiWWedgeEnvelope.h"], "id": "LARPLACE-PhysVal-plan", "role": "PhysVal", "mode": "read-only", "writable_paths": [], "task": "Independently assess whether LAr assemblies can benefit from SiW-like reusable solid mothers without changing leaves/material/IDs. Parent considers exact per-period domain between outer negative absorber skin face0 and corresponding next-absorberface, clipped to annulus; tessellation should mean fully filled. Challenge this hypothesis using actual sources. Identify feasible barrel/turbine candidates and minimum conservation/containment, native/touchable, material and initialization benchmarks. Same-material boundaries may alter shower histories. Read only, no native jobs/edits/nesteddelegation. Final exact-revision review later.", "deliverable": "Cited prospective scientific assessment and minimum adequate equivalence/performance controls to parent.", "completion": "Identify feasible alternatives, evidence required and physical blockers without humanapproval."}

- Additional assignment before dispatch: {"id": "LARPLACE-PhysVal-code", "role": "PhysVal", "input_revision": "8d74a4c1221a19d314881c4deccb2b5986ff425d", "inputs": ["tools/lar_calorimeter/placement.py", "tools/lar_calorimeter/test_placement.py", "prototypes/calorimeter/LArBarrel.cpp", "prototypes/calorimeter/LArEndcap.cpp", "tools/lar_calorimeter/placement_probe.py", "tools/lar_calorimeter/placement_audit.hpp", "docs/design/inputs/DES-032-lar-placement-initialization.md"], "mode": "read-only", "writable_paths": [], "task": "Assess exact optional placement implementation and benchmark/audit scope against prospective conclusions. Challenge envelope/material/ID conservation and whether measured phases support initialization claims. Existing firstpair stock/candidate dump hashes are identical for43648rawIDs and274689materialleaves; nativecomponent/combined validation pending. Do not grant acceptance or claim finalresultreview yet. Run meaningful standard-library tests if useful; no expensive nativejobs/edits. Return any material issues early. Final results report will be reviewed separately.", "deliverable": "Exact-revision findings and actual controls to parent for journal.", "completion": "Concrete correctness/claim issues resolved or identified; distinguish sourceinspection from executednativeevidence."}

- Final assignment before dispatch: {"id": "LARPLACE-PhysVal-final", "role": "PhysVal", "inputs": ["docs/validation/lar-placement/results.json", "docs/validation/lar-placement/README.md", "docs/validation/lar-placement/environment.json", "tools/lar_calorimeter/placement_probe.py", "tools/lar_calorimeter/placement_report.py", "tools/lar_calorimeter/placement_audit.hpp"], "task": "Final scientific/claim review of committed result and implementation. Inspect primary code and local stock-smoke1/candidate-smoke2 receipts/logs/readbacks under build/lar-placement before author conclusion. Independently reproduce first-event times/mapratio and relevant guards; assess onepairscope and native/material evidence. Identify any material incorrect claim, missing control or provenance mismatch. No new large simulation/edits; no humanacceptance. Earlier scope/provenance findings were addressed by actual7eventpair and launchidentity guards.", "deliverable": "Exact-revision final cited assessment with actual checks and unresolvedlimitations.", "input_revision": "b1d325f339888876c45be68417f66c23f1ab0dc3", "mode": "read-only", "writable_paths": [], "completion": "Return final assessment or concrete material corrections; distinguish actually rerun checks from retained execution evidence."}

- Final assignment before dispatch: {"id": "LARPLACE-SoftEng-final", "role": "SoftEng", "inputs": ["tools/lar_calorimeter/placement_probe.py", "tools/lar_calorimeter/placement_report.py", "tools/lar_calorimeter/placement_smoke.py", "tools/lar_calorimeter/placement_variant.py", "docs/validation/lar-placement/README.md", "docs/validation/lar-placement/results.json"], "task": "Independent software review of coordinator-authored probing, report collection and reproduction recipe. Do not independently certify your own geometry implementation. Verify meaningful source/receipt/primary/ID consistency and offlinecollector reproducibility using existing local raw outputs, and catch recipe/metadata guard defects. No edits or new heavy simulations. Report material issues with fix suggestions; do not grant humanapproval.", "deliverable": "Exact-revision software findings and actual targeted checks, with self-authorship boundary explicit.", "input_revision": "b1d325f339888876c45be68417f66c23f1ab0dc3", "mode": "read-only", "writable_paths": [], "completion": "Return final assessment or concrete material corrections; distinguish actually rerun checks from retained execution evidence."}

## Final reviews and evidence-guard corrections

PhysVal independently reviewed b1d325f339888876c45be68417f66c23f1ab0dc3, parsed
the raw logs and reproduced522.258406s/67.382542s and19.7942329mapratio. It
verified input/source/library, native/template, inventory,65ray and14smokeROOT
hashes and recollected the result in memory. No material scientific/claim issue
remained for a bounded draft, with the serial/onepair/noresponse limits retained.

SoftEng's separate review of coordinator-authored tooling (not its own geometry)
found P2 evidence-guard gaps. A temporary-copy negative control could substitute
a0.25partition residual while reusing the old nativePASS. The collector now binds
component compact/expected/library identities, combined manifest/components,
variant templates and nativeROOT. A source/model/library-bound wrapper reran
the same65material rays for both models; differences remain0 and the collector
recomputes them from bound inputs rather than trusting old scalar maxima.
The canonical smoke audit now parses the executed readout tables, rejects unused
high bits and requires complete barrel theta and turbine rho/z membership.
Both seven-event filesets were re-audited successfully with these stronger
guards. Initial readback metadata remains locally as smoke-readback-initial.json
and the previous compact result remains in b1d325f history.

Two new regression controls cover stale expected/library bindings and invalid
virtual/high-bit IDs; the full LAr/helper suite now has39controls. A misplaced
fixture assertion initially failed after the test extension and was restored
to its original test before the passing run. No transport output, geometry,
seed, numerical tolerance or measured timing was changed by these corrections.

- Guard follow-up assignment before dispatch: {"id": "LARPLACE-SoftEng-guards", "role": "SoftEng", "input_revision": "242518707422e11c4919d1058e9d71067ca35a8c", "inputs": ["tools/lar_calorimeter/placement_report.py", "tools/lar_calorimeter/placement_smoke.py", "tools/lar_calorimeter/placement_rays.py", "tools/lar_calorimeter/test_placement_probe.py", "docs/validation/lar-placement/README.md", "docs/validation/lar-placement/results.json"], "mode": "read-only", "writable_paths": [], "task": "Verify remediation of your twoP2guard findings at this exactrevision. Native component/combined/template/library bindings added; source-bound raywrapper reran65raysbothmodels; collector recomputesdifferences. Canonicalsmoke nowparsesexecutedreference tables/highbits and both7eventfilesets re-audited. Re-run temporary-copy staleexpected0.25 control and ghostcell/highbit controls; reproducecollectoroutput without editingretainedsources. No newheavy simulation or acceptance. Check reproductionrecipe and reportfieldconsistency. Stop once findingsresolved or concrete remainingP2+ identified.", "deliverable": "Exact-revision guard-remediation assessment and targeted actualchecks to parent.", "completion": "Report whether each priorguardfindingisaddressed; clearly note anyunresolvedmaterialissue."}

## Guard-review closeout

SoftEng rechecked242518707422e11c4919d1058e9d71067ca35a8c read-only. The exact
0.25stale-expected negative control now fails with the nativebinding error.
All39controls pass, and collector replay is byte-identical to the committed
result SHA25693fad4ecf75511712362f542df4568068edcf88fdd5f12f31b2850772e3dc3a4.
No remaining P2-or-higher issue was found in this bounded remediation review.
This independently assesses coordinator tooling, not SoftEng's own geometry
implementation; the separate PhysVal assessment covers scientific claims and
geometry/evidence consistency. Source/metrics and all approval limits remain
explicit. Five baseline-composition controls also passed.

The session summary reports284sessions,187with usage observations and511recorded
turns; this task has no exposed usage counters and no historical totals are
attributed to it. Publishing/PR metadata follows only after it exists.
