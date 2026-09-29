# SESSION-2026-09-29-tracker-service-corridors — Support and service gaps

## Request and scope

The user explicitly corrected the approval boundary: PR #24 did not approve the
tracker default; use it only as a working hypothesis. They requested TDR-based
support/cable/cooling estimates, actual gaps between pixel/short and short/long
packages, conditional outer long-strip routing, radial barrel exits and mockups.
Layer-position optimization is deferred to a separate follow-up PR.

Start: main at `1aa2aafd381fc37a9da3368686f2ca34d9f4dd0a`, the PR24 merge.
Branch: `study/tracker-service-corridors`. Four pre-existing untracked usage
summary files are preserved and excluded from this task's commits. DES-010 was
drafted before the service overlay. No production geometry, material model,
reconstruction configuration or approval state is changed.

## Research and implementation

Three delegated agents researched pixel and strip services and inspected occupied
geometry. Public catalogue TDR PDFs and three later public pixel engineering
sources provide exact locators, hashes and classifications. No confidential
sources or large PDFs are committed. The strip TDR identity was verified; the
source catalogue records this and the later pixel sources.

Occupied endcap envelopes have no through-annulus between adjacent packages.
The long barrel/first-disc gap is only about7.89mm. The overlay removes complete
original rows after module generation, preserves every retained ID/transform,
and leaves ideal station denominators unchanged. Local support space is reserved
outside the module bodies; the ATLAS6.34–6.54mm sensor-spacing stack cannot be
inserted silently into the current5mm long sandwich. Attachments/thermal bridges
remain undefined. Pixel5mm and strip6.6mm carrier depths are trial keep-outs,
not solid-material thickness or qualified mechanics.

The initial chosen gap removes3898 assemblies: outerpixelendcaprow4; short
endcaprows0,5; longendcaprows0,1; both ends of bothlongbarrels. All retained
module positions stay fixed. The route model reserves axial annuli, radial
barrel/disc collectors and a new conditional rear/vessel interface beyond the
3150mm host. Full-azimuth space exclusion is separate from partial-azimuth
capacity. The root combines source budgets, scans, drawings, provenance and PR.

Power/data grouping rounds within each half-stave or endcap row and family.
Electrical supply/return and hydraulic feed/exhaust are counted distinctly.
The short-strip122880-channel working model cannot inherit an ordinary strip
power requirement; CMS architecture is a comparator and4.068× channel scaling
is an unqualified stress scenario. Nominal cooling remains optimistic in that
stress; no hydraulic pass is claimed.

## Failures and corrections

The first probe cleared route/body/support space and all reference route areas,
but12 computed junctions failed. Some were unintended geometric contacts rather
than flow paths. The explicit directed routing tree now distinguishes required
joins from incidental contact; every required edge must connect and preserve
all upstream source modules. Real constrictions were corrected by extending
axial trunks over complete barrel-turn and vessel-end bays. No tolerances were
weakened. The failed first probe remains retained for review.

Independent review corrected byte-hash provenance (input snapshots now preserve
original bytes), stale plotting constants and transverse routes drawn at the
wrong z. Mockups use retained inputs and label external interface proposals.
The initial dashboard build rejected a Python file in its curated-text evidence;
the tracking link now points to the README and JSON inputs. The corrected build
passed. No scientific evidence was changed by that documentation correction.

## Runtime and validation

The acts-spack skill preflight reports changed setup/lock fingerprints. The
required runtime was directly rechecked using the documented acts run helper and
installed pyvenv; ACTS sensitivity, NumPy2.5.3 and Matplotlib3.11.2 are available.
The initial activation reports a Geant4 data-path warning. No Geant4 transport
is claimed. The sister checkout stays at355ea684 with its existing local changes;
this task does not alter its sources or installation beyond the authorized
runtime helper's normal ODD-data copy.

Focused geometry/budget/driver tests and source-space probes are recorded in the
paired JSON. Completed numerical/native results follow below. Source/input hashes and commands accompany retained
outputs; fresh directories prevent replacement of earlier evidence.

## Token accounting

No exact client-reported completed-turn root or subagent counters are exposed.
The usage array remains empty. Historical inventories are not allocated to this
task, duplicated or estimated. Session summary coverage will be recorded at
completion.

## Review boundary

This is a source-guided service-space working hypothesis. Electronics bandwidth,
voltage drop, thermal runaway, pressure drop, material composition, support
attachments, vessel access and full-detector egress remain unqualified. Failed
adverse scenarios are constraints for later review and optimization, not hidden
by a successful geometric exclusion check.

## Canonical run and retained results

Committed the reproducible source/configuration at
`d3265fa1e52f26b0aac556325eaa6d7a10442720` before execution (clean tracked source).
Ran `tools/module_layout/services.py --coverage --native` using the verified ACTS
runtime and `/tmp/acts-python-step-size-overlay` binding, writing to fresh cache
`reference/cache/DES-010-services-main-20260929`. Exact arguments and hashes are
retained in `docs/validation/DES-010-services/main/summary.json`; the report gives
the complete setup and plotting commands.

The 53,952 evaluations compare identical luminous-region samples before/after
row removal. All geometric exclusions and declared route connectivity pass;
reference capacity passes. Conservative fails 22 routes/14 throats and stress
48/24. The 3,898 removed assemblies cost 40.162 m² of sensor area and raise the
missing eligible-station fraction from 5.3–5.7% to 16.9–17.3%. This is an exposed
coverage cost, not accepted tracking performance. Native ACTS agrees on every
patch set for 48 tracks, with 565 reached patches and maximum residual
9.211e-7 mm. Negative candidate errors/bounds rejections are retained separately.

Full module tests: 80 passed (39 new service tests). Clean-worktree source checks:
27 dashboard tests, 32 logging tests, 14 JavaScript assertions passed. The JS
command was `/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc tools/dashboard/test_app.js`.
Generated and visually checked final routing projections and local support
concept; retained PNG/PDF pairs, view metadata and artifact hashes. Retained the
initial rejected throat-capacity probe separately. Public PDFs, raw trajectory
files and ACTS intermediates remain in ignored cache. No layer optimization,
production detector change or human approval is recorded.

Independent final report audit matched all numerical tables and exact snapshots;
clarified that the common route lies inside the vessel bore, and that support
area is equivalent volume/depth rather than projected area. No numerical source
or result changed. Final dashboard validation/build and session validation pass.
The local journal summary has 134,594,309 observed input and 674,111 output tokens
across 79 turns in 42/57 sessions; this task has no available counters. These are
partial historical totals, not the current task's usage or complete project cost.
The local denominator includes the unrelated, preserved usage-summary pair.

The final audit also identified the limiting reference rear/common-bore join:
97.86% utilization (2.14% headroom). This is now prominent beside the reference
capacity pass, preventing a larger downstream section from hiding the bottleneck.
