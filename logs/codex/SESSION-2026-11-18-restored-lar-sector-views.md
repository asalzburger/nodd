# SESSION-2026-11-18-restored-lar-sector-views — Updated native sector views

## Scope and selected request

Contemporaneous bounded redraw, starting from clean drawing revision
`cf4403cecf187c61f0f2835a6ecc31559e6639f3` in a new dedicated worktree/branch.
User request (paraphrase): redraw the earlier Si-W/LAr sector views using the
updated LAr prototype and retain the illustration of particle passage.
No unrelated local changes were present. Relevant governing context: DES-030,
DES-031, DES-032, existing PR147 illustration and PR148 restored prototype.
No geometry implementation, transport, design approval or production change.

## Decisions and evidence

Kept the maintained Si-W input used in the previous published drawing, and
used the exact restored1.8mmPb/1248period barrel compact and factory used by
the PR14810k control. Model sources are respectively
`f3ece1d6a6816c8172dfa841d63e5424730e8228` and
`53797385c374118838b2ade1ec3362328683cf75`. Every model-declared geometry source
was checked against its declared commit and the updated prototype revision
`8f7a7c8bd86f4d9c67c11b37d91aea76790feee4`.

The native C++ navigator/integration code is unchanged. Added declared-dimension
metadata, optional physical zoom coordinates, current-geometry byte checking and
validated-library hash checking. Both overviews share the earlier axes; both
zooms now share exact XY bounds300–460/1834–1946mm. Kept the old published
figure intact and added SVG/PNG/PDF plus compact provenance in a separate folder.
The SVG contains native raster geometry with vector annotations. Scalar labels
identify Si-W apothems separately from LAr circular radii.

Both Si-W rasters reproduced the previous published hashes. The marked78.75°
IP ray has0 sensitive Si segments and110 sensitive LAr segments; near±.001rad
probes give0/0 and107/109. These are geometric sensitive path segments, not
independent layers or shower/energy-resolution observations. Detailed limits,
input hashes and pinned detached-checkout recipe are in the new validation note.

## Commands and checks

- acts-spack preflight warned that setup/lock fingerprints changed. Reported this
  before native work; software/env/run.sh then verified ROOT6.40.04, DD4hep/DDG4
  imports and Geant411.4.3. Existing dependencies were used without installation.
- Fresh native extraction of both exact local compact/library pairs passed;
  `--library-sha256` matched prior validated artifacts and `--geometry-revision`
  checked all source hashes. Full models/libraries/logs stay local and ignored.
- Four portable tests reject old LAr variants, different zoom coordinates and
  changed rasters while admitting a matched input fixture: PASS.
- Existing native analytic subpixel-film/chord fixture:1test PASS.
- Existing librsvg2.62.3 with Cairo1.18.4/Pango1.58.0 rendered PNG/PDF. Final PNG
  inspected: panels, guide rays, same-scale zooms and legend readable.
- One read-only diagnostic used an unmatched shell glob and a missing optional
  README path; corrected by reading the existing restored reproduce.md and
  agent-workflow documentation. No scientific execution or output was affected.

## Independent assessment and publication

Exact-candidate PhysVal review, final validation, draft publication and artifact
links are recorded below when completed. Generic explicit-profile fallback is
used if native role selection is unavailable; this does not imply human review.
The drawing depends on PR147 tools and PR148 geometry, without copying their
raw data or changing their approval state.

## Token accounting

This parent turn is active and excluded: no finalized counters are available.
No usage is estimated. Separately closed review-turn observations may be added
only with verified exact IDs and unique ownership. Historical task records and
existing usage owners remain untouched. The current task gets its own session,
PR interaction record, project evidence and token preview validation.

### RESTORED-SECTOR-PhysVal assignment

Role: PhysVal, explicit full-profile generic fallback, prepared with
`tools/agent_workflow/workflow.py prepare`. Source:
`bd01e692e513215a301a2493a37736da9acee876`. Inputs: new native provenance,
PNG/SVG, validation note, extractor, restored renderer and portable guards.
Read-only; no owned write paths, native rerun, transport, private-state access,
publication or further delegation. Question: independently assess exact model
identity, sensitivity/path interpretation, preserved Si-W, matched coordinates,
dimensions/angle conventions and visual clarity. Return findings, actual checks
and limits; completion requires reporting any material blocker to presenting
this geometry illustration. Coordinator retains findings here.

### Publication and record checks

Published [draft PR149](https://github.com/asalzburger/nodd/pull/149), stacked on
PR147's drawing branch; PR148 supplies separately pinned geometry objects.
Labels: documentation, campaign:calorimeters. Attached PR to this task. Reviewed
all introduced Git blobs: largest is the1.13MB PNG; no raw models/events,
libraries or private payloads. Copied four matching figure/provenance artifacts
to the task visualization output directory.

Project, software inventory, session, interaction historical-retention and token
validators passed locally, as did the token preview build. Initial session
validation rejected lowercase status values; corrected to schema `PASS` and
revalidated. A README trailing blank line was removed in a normal follow-up.
Initial remote token-site failed because PR149's newly assigned interaction
record was not yet on the first published candidate. The new per-PR record is
included in this follow-up; scientific fixtures passed. No gate was weakened.

### Independent review and accounting closeout

RESTORED-SECTOR-PhysVal, separate `/root/ecal10k_physval` context, reviewed
`bd01e692e513215a301a2493a37736da9acee876`: no material scientific or visual
blocker. Checked restored variant/source identity, all declared geometry hashes,
preserved Si-W raster/input identities, actual0/110 sensitive segments, same
physical overview/zoom scale, embedded image/source hashes and final PNG. Four
portable guards passed independently. No native or transport rerun, files changed
or human acceptance granted. Review source/result retained in PR149's selected
visible-turn record; final figure bytes are unchanged from reviewed candidate.

Strict token-only recovery and exact app-visible review boundaries matched
child turn01a1ee98-4c30-7b10-9fa0-806d70cc013d. Imported only this completed
review into the new session:8requests,3,088,802input +7,909output =3,096,711
observed tokens (cached/reasoning subsets not added). Historical turns retain
their owners; active parent excluded. Inventory:
`logs/usage/USAGE-2026-11-18-restored-sector-review.json`. Native operation counts
from the selected visible review describe the same operations as the journal,
not additional activity. Execution model/client version remain unknown.

The follow-up remote token-site gate passed after the PR-specific interaction
record was published. Other remote checks were still running at observation;
this remains a draft. All requested figure products and reproducibility records
are delivered. Human review/merge and engineering approval remain separate.
