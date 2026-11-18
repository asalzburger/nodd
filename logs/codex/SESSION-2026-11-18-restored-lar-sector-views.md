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
