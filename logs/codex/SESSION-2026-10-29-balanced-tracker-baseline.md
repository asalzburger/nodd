# Adopt the expert-selected balanced tracker baseline

User requests registration of the expert-selected baseline, proper maintained
DD4hep implementation, pixel TDR update, token accounting and merge preparation.
No merge, external message or Overleaf publication is requested. PR104 is open,
ready and expert-approved. Exact observed review: noemina5701456683, APPROVED,
2026-10-29T16:40:21Z, targetcfd15cb1c0a195a73a8204400b115a2635a52e2a. Selection is
balanced, not the coordinator's earlier mild preference. Human explicitly
authorizes implementation in this existing PR; no new engineering sign-off.

Read repository AGENTS/PROJECT, coordinate/design-evidence/review-validation,
acts-spack skill, workflow and TDR writing guide. New bounded account starts at
cfd15cb; prior task counters remain in their canonical owner. Current turn is
active/excluded. Need recover only finalized unmatched prior task/root turns.
Spack preflight warns changed setup/lock fingerprints; verify native capabilities
before dependent execution. Do not alter shared installs or old frozen evidence.

Main owns design/selection, project/review records, layout main-page figures,
validation integration, logging/accounting and PR preparation. Bounded SoftEng
owns maintained source/config implementation and focused controls. PubDoc
initially inventories actual current full-tracker TDR source (not retained
preliminary edition); later edits a scoped review artifact. SysArch initially
assesses physical interfaces and source contract, then reviews final source.
Separate PhysVal equivalence assessment follows implementation. Explicit role
mandates are passed; native profile loading is not claimed.


## Decisions and outcomes — source implementation and native checks

BAL-SoftEng-01 implemented maintained balanced source configs/placement contract,
with changes frozen at888069bb7c0ec04760ff8ea2288316b6cbf86835. Source generation
uses original donor datums before rigid placement; donor2 becomes stableID10 on
both ends. Existing explicit trimmed/quad controls remain. Actual focused tests:
17barrel,16pixel,7tracker and5balanced subset checks passed. One fixture initially
mixed standalone27mm and integrated28.8mm collector apertures; corrected fixture
matches its representation, without changing geometry or loosening tolerances.
C++ factories already parameterize the schema; fresh CMake/Ninja built all five
libraries and canonical exports, rather than mutating prototype XML at runtime.

BAL-SysArch-01 read the complete physical relocation contract: fixed envelopes,
82staves, ten mirrored disks, collectors follow stations, three rail slots per
station; added disk repeats donor2 modules/passives/cooling. Global trunks,
bypass and rear payloads stay frozen with capacity/connectivity unqualified.
BAL-SysArch-02 independently assessed source888069b, TDRccdafc8 and completed
native/Gen3 reports. It compared3566global pixel attachments,88848material-bearing
nodes in4184correspondence groups, expanded elemental mixtures/densities,
world/readout trees and every pipe/strip semantic token, with no physical
finding. Native audit hashes, inventory and frames matched actual files. Two
TDR wording findings were fixed by the coordinator: standalone27mm aperture and
204.747kg mass versus integrated28.8mm passive aperture; ring0.5mm reference
clearance versus current0.474/0.488/0.440/0.500mm gaps. Geometry was unchanged.
Separate agent assessment does not confer human engineering approval.

BAL-PubDoc-01 established that docs/tdr points to current full-tracker source
7625cf6054f5761228be6d8d2de24d43f155bd19, while docs/publication/tdr is an older
preliminary report. Main imported exactly65tracked current TDR files as a
parent-owned review artifact in bf0e9e3. BAL-PubDoc-02 updated only current pixel
and tracker-overview prose, generated barrel/disc rows, six dependent figures,
wrappers and explicit balanced extraction recipes. Source-import manifest and
historical snapshots stay controls. Strip chapters, six strip figures and their
table are byte-preserved. Final extraction uses native evidence and canonical
888069b producer hashes, source_dirty=false. Full module-centre checks cover3050
barrel and1308positive-endcap modules. No Overleaf publication/submodule change.

Native runtime: changed Spack setup/lock fingerprints were warned and recorded;
DD4hep1.38, ROOT6.40.04, Geant411.4.3, Python3.14.5 imports and all12G4datasets
verified in a fresh existing runtime, with no shared dependency changes. Full
external source access remains unverified. Fresh native fulltracker audit passes
46250unique VolumeIDs,1168exclusive material inventories,687724placements,
zero ROOT overlaps/extrusions,27sparse rays and1mm passive pipe clearance.
Native Gen3 export passes46250sensors/54groups/120volumes and exact complete JSON
round trip. Native binary/input/checker fingerprints identify execution;
documentation changes and external source HEAD are not substituted for them.
DDSim passed three1GeV geantino events with explicit local factory search path;
ROOT independently has3events. This is construction/transport smoke, not a
material recording or field/performance campaign. Retained results and exact
reproduction are in docs/validation/DES-040-baseline/.

First source comparison was scheduled before its generated compact existed; it
failed on missing file and passed after the build completed. The old material
exporter rejected new counts by its historical guard after native conversion;
its guard stays intact and a separate current exporter passed. Initial DDSim
missed local factory lookup; explicit library path fixed the invocation. The
built-in Tectonic compiler failed at the house-style pdfLaTeX primitive; the
correct pinned pdfLaTeX CI40937210453 succeeded (31pages). Final corrected source
receives another compilation and visual review. Initial token CI atccdafc8
reported stale interaction/accounting evidence before the planned reconciliation;
final sync and final-head checks are required before merge preparation completes.

## Interaction and accounting reconciliation

Exact read_thread prompts identify three finalized prior-root turns: original
optimisation01a17c93-3e49-7ac1-a25a-3b6fae03b727 and recommendation followups
01a17e35-d59a-7493-937f-ffdf06f54de3 /01a1871e-89db-71e0-ba3e-06c784519560.
Their finalized usage belongs only to original SESSION-2026-10-27-tracker-resolution-optimization.
That account now has12completed turns and93,425,056 observed tokens; current
integration does not reimport its nine already-owned specialist turns.
New BAL specialist closed turns belong only to this Oct29 account. Exact child
thread identities are verified through the root subAgentActivity relationship.
The active Oct29 root01a188fc-bf3e-7ce0-9305-6bcea4db3657 stays excluded.
Execution model/client version are unknown, not inferred. Recovery queries usage
metadata and token_count events only. Visible records retain allowlisted text
and operation counts, excluding reasoning, tool arguments/results and private
client state. Public GitHub discussion/review snapshot is refreshed separately.


## Decisions and outcomes — final source/physics and PDF review

BAL-PhysVal-01 independently compares734367detector/readout nodes,9260387
attributes and656138material references with the approved balanced compact.
All1168used material recipe pairs are equivalent; all46250physical readout-ID
tuples retain centre, signed u/v/n axes and bounds (1420242values, maximum
1.137e-13 floating difference). All120volumes,124portals,250link subsurfaces and
54logical groups correspond. Exactly602ACTS sensitive IDs permute within added
layer10 due to source-path ordering. Existing layers retain IDs. Checked
per-physical-sensor digitization,54geometric/54pooled calibration groups and
67material keys/68roles/8552bins preserve semantics. Homogeneous donor2 layers
remain at signed956.825mm,1mm beyond farthest sensor face. No universal ACTS
sensor-ID byte identity or arbitrary per-sensor payload compatibility is claimed.
The final TDR explicitly distinguishes standalone inventory from integrated
passive clipping; independently quantified difference11.243043g across152parts.
Historical four confirmation matrices remain unchanged from original pins.

Final corrected TDR source b19a12b5e48f16d689087875e98d1a5a01003675 compiled in
successful pdfLaTeX CI40937879945. It is32pages, with no overfull boxes or
unresolved references/citations. Coordinator rendered every page at110dpi,
inspected all32via four contact sheets, and inspected detailed pixel pages9,
10,13,15,17,18,19. Tables, stableID10physical ordering, radii, module/circuit
counts, aperture/reference-clearance wording and material qualifications are
readable. No clipping, missing figures or overlapping labels observed. Compiled
PDF/log and exact source-tree/manifest fingerprints are retained. Both updated
main layout PNGs also visually inspected; old FCAL physics context is unchanged.


## User-visible outcome — prepublication closeout

Balanced is the registered maintained working baseline, with proper parameterized
DD4hep generation and updated current pixel TDR. All scoped native/source/Gen3/
smoke checks and both separate technical assessments pass with their explicit
limits. Corrected TDR PDF/log and32page review are retained. Final PhysVal
assessment atb19a12b found no remaining blocker in its assigned scope.

All six completed BAL specialist turns now total38,143,337observed tokens;
PR104 canonical accounts total131,568,393across18closed turns. Input/cache/output/
reasoning subsets remain distinct. Original optimisation root/followup usage
remains solely in its original owner. The active integration coordinator
01a188fc-bf3e-7ce0-9305-6bcea4db3657 is excluded, not estimated. Public expert
review/comment and all available account-matched completed turns are recorded;
current available root input/comments are retained as an active prefix snapshot.

Final push follows this prepublication journal freeze. Hosted final-head CI is
then observed in the public PR checks, not predeclared here. PR remains open and
ready; no merge, external discussion message or Overleaf publication performed.

Execution boundary: Gen3 wrapper file was new/uncommitted at generator HEAD888069b during export; its exact executed hash was subsequently committed inccdafc8. All retained input/binary/checker hashes identify the actual execution. TDR producer sourceclean888069b refers specifically to its maintained geometry producers.


## Accounting correction after completion — 2026-10-29

The preceding coordinator turn01a188fc-bf3e-7ce0-9305-6bcea4db3657 is now
finalized. Its exact usage-only counters and matched visible messages were
imported once into this original baseline owner. The subsequent explicit
Overleaf push request belongs to SESSION-2026-10-29-balanced-tdr-overleaf; its
active turn is excluded. The earlier prepublication totals remain dated
observations; the canonical JSON now contains finalized preceding-root usage.
