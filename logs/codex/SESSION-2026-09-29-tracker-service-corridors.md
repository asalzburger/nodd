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
paired JSON. Full numerical/native and final publication results follow below
when actually completed. Source/input hashes and commands accompany retained
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
