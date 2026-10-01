# Preliminary combined pixel detector implementation

## Selected request and authorization

On 2026-10-01 the maintainer requested: “assume the pixel barrel baseline + the
design of PR #36 - and make this a preliminary baseline. Make the corresponding
dd4hep and nodehammer implementations out of it. We want to learn how to run
Geant4 next then.” This authorizes a preliminary isolated combined baseline and
implementation, not formal engineering sign-off. One bounded implementation
request is recorded; no clarification/approval question was needed for the design.

## Starting state and preservation

Started from PR36 head `6a07da7cd3096e6482bae4e96ccabe9b4facf0a3` in isolated
`detector/preliminary-pixel-detector`. The original main checkout contained
unrelated display-colour/opacity edits and usage-summary files; all were preserved.
PR36's hosted dashboard build was successful. Its design/support evidence remains
frozen. No shared dependency, ACTS checkout or main-branch history was modified.

## Work and provenance

Read AGENTS/PROJECT, DES012/014, the logging/tracking workflows and the
[acts-spack skill](../../skills/acts-spack/SKILL.md). Preflight reported changed
setup/lock fingerprints; actual DD4hep1.38, ROOT6.40.04, DDG4 and Geant4 11.4.2
runtime/datasets were checked. No dependency installation was performed.

DES015 was written before implementation. It records preliminary selection,
reusable module/disc/service factories, signed frame conventions, new endcap
system IDs and explicit inventory-normalized approximations. Endcap module
shapes retain their original radial periphery; the barrel stays identical.
Source facts/material assumptions remain the public sources catalogued by
DES012/014. New representation choices are labelled NODD DESIGN CHOICE.

The exporter builds 5066 modules and 14858 active patches. Native validation checks
all centres, normals, IDs, pixel-cell corners, exclusive masses and overlaps. The
nodehammer workflow audits the semantic/NHB round trip, every rendered placement
and portable full/subassembly projects. A repeatable driver and retained report
connect these steps, with optional Geant4 initialization and no event transport.

## Failures, corrections and limits

- Spack preflight exited2 for changed fingerprints. Actual runtime worked; sandbox
  sysctl/ps warnings were not treated as evidence of missing libraries.
- First native geometry found12 flange/trunk overlaps. DES015 PD-C09 partitions
  service cells through r192..222mm flange necks, retaining all flange dimensions
  and transported material. The corrected check found zero overlaps at the same
  1e-5mm tolerance. Rear-neck reference packing is1.310 and remains FAILED.
- Nodehammer's GLB conversion rounded long translations by up to0.143µm. A
  verified exact float32-conversion repair rescales only JSON translations,
  preserves mesh bytes and retains the original audit tolerance. Wrong-unit
  negative controls still fail.
- Splitting new Python helpers initially collided with an existing `services`
  module. Endcap-specific module names fixed import resolution; all5 source and
  material-conservation tests then passed.
- `ddsim` first lost the plugin path through macOS shebang launching. Explicit
  active-Python invocation fixed loading. A second attempt found missing tracker
  region constants. Adding explicit r680/|z|3300mm truth-handler bounds fixed
  initialization without disabling that handler. Geant4 conversion registered
  14858 sensitive paths; no beamOn command or transported events were used.
- Initial dashboard validation found a task/workstream role mismatch; the tracking
  role was corrected to the workstream's established Tracker technician role.
- Thermal stress, adverse service packing, routed transitions/flex artwork,
  detailed couplings, ACTS re-evaluation and physics validation remain open.

## Commands and observed checks

Commands are retained in the paired checks and DES015 workflow report. They include
Spack preflight/imports, CMake build, CTest (6/6), pure endcap tests (5), nodehammer
safeguards (8), native export/round trip and DDSim initialization. Final source
revision, workflow replay, dashboard and session validation are recorded at closeout.

## Usage and interactions

Exact client-reported per-turn token counters are unavailable; paired `usage` is
empty. This is missing coverage, not zero tokens. No usage from an earlier task
or cumulative client counter was reassigned. No subagents were spawned for this
task. The project summary is run at closeout and reports observed totals separately
from missing coverage.

## Final replay

Code revision `d2a0f3e23449e06b75fb0717263dfbc7010c55a0` passed the one-shot
workflow: six CTests, seven packed/audited nodehammer views and Geant4 initialization
with14858 sensitive paths and zero events. Six repeated export artifacts are
byte-identical under the same Python runtime. The initial host-Python comparison
differed only in its correctly recorded interpreter version. Dashboard27 tests,
validation/build and session73 validation passed. Retained evidence is under
`docs/validation/DES-015/`. New downstream service material is148.151kg; the full
modeled scope is193.682kg, not comparable to former local-only mass totals.

Canonical paired-log summary:134594309 observed input and674111 observed output
tokens across79 recorded turns in42/73 sessions.31 sessions lack usage observations;
this task contributes no fabricated counters. These historical observed sums are
not the complete project total or this task's usage.

## Pull request and closeout

Created draft [PR37](https://github.com/asalzburger/nodd/pull/37), stacked on PR36,
with implementation revision d2a0f3e and evidence revision aed99ce. The original
main working changes were rechecked and preserved. Git staging encountered a
sandbox index-lock denial and PR creation a sandbox network failure; authorized
retries succeeded. Hosted checks are distinct from the completed local native
workflow. No force push, merge, design approval or event transport was performed.
An initial closeout activity record lacked required version/evidence fields;
those schema fields were filled and session validation passed.
