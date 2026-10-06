# SESSION-2026-10-05-pixel-disc-support-variants — Compare eight single rings and four single plus two quad rings with local support, cooling and mounting

## Scope and evidence

Contemporaneous bounded task started in app thread01a10c6a-664d-72b1-afad-926c2c57312b,
implementation turn01a10db9-36a0-7922-971e-3730adf8d4b8. Usage-only recovery metadata
exposes actual start2026-10-05T20:20:04Z; the turn remains active. Execution model,
client version and final counters are unknown. No partial counters were imported.
Related: DES017, DES016, DES014 and issue38. Starting revision
8e593e32a97acc36b9a7850e1dfabc11d2175180, clean isolated worktree on
codex/pixel-disc-support-variants, stacked on PR41. Existing primary uncommitted
logging copies and sister ACTS modifications were preserved.

## Selected conversation

User request (paraphrase): replace the outer four of eight single-module rings by
two quad rings; develop support, cooling and mounting for both and explain the
recommended next working prototype in a new PR. Earlier instructions continue:
keep service radii fixed, radial/tangential axes and20% overlap ceiling; log work
and recover actual resources after completion. “4+4” is recorded as four single
rings plus two quad rings/eight radial chip rows.

## Decisions and outcomes

DES017 contract preceded modelling. Retained comparison:296 singles versus102
singles plus22/28 quads at nominal124/161 mm (152 assemblies/302 chips).
All source disc datums and first four nominal rings preserved; new two-face
mounting changes local sensor z and explicit luminous-vertex xy compensation.
Two-face construction was chosen after outward central/offset stem failures.
Quad contacts move1 mm inward toward their module centre; single contacts stay
centred. Common6.3 mm sandwich, per-chip graphite pickups,8 cooling tracks/16
half-ring circuits/32 feed-return legs, proposed spring/slot module retention and
three-point disc coupling to rails/closed carrier documented with provenance.

All18 body/stem/core bounds pass; maximum radii182.337/185.503 mm. Small-guard
overlap≤20% conditional;0.5 mm guard control fails. Original-annulus coverage fails
for both; mixed area gaps improve but native probes miss more transitions (92/540
versus54/540). Recommend mixed as next working prototype, retain singles for
modularity/yield comparison. No acceptance improvement or design sign-off claimed.
Refined thermal results pass the−40°C screening hypothesis but fail degraded
−35°C cases. Fixed service trunk/flange packing still fails. CAD routing, actual
clamps, cold coupons, hydraulic/pressure/laminate/FEA and passive transport are open.

## Commands and validation

- acts-spack node preflight exits2: setup/lock fingerprints differ. Warned user;
  actual installed DD4hep1.38/7deaacd and Geant411.4.2/cpge6jj verified. Initial
  runtime import fails for Shapely; reused the existing isolated local target.
  ACTS Python3.14, NumPy2.5.3, Shapely2.1.2, Matplotlib3.11.2, sensitivity API verified.
  Sister source HEAD355ea68493b326956756c9386d2fd9eaf9328568 and dirty files preserved.
- `study.py --output build/disc-support-variants/run-01`: interrupted during slow
  high-resolution ranking (exit130). Changed only candidate-ranking circle grid
  to128 segments; retained full2048-segment station bounds.
- run-02 completes outward proposal with failed central stems (18 single,76 mixed
  conflicts at first station). An exploratory uniform offset trial also failed.
  run-03 explores two-face mounting; not retained as authoritative output because
  producer/input files changed during it. Final run-04 executes unchanged files,
  exits0; hashes identify the actual dirty producer/configuration at parent HEAD.
- `native_audit.py --run .../run-04 --output .../native-04 --acts-source .../acts-nodd`
  exits0: two540-track native/oracle audits and two6-track exhaustive controls pass,
  with expected target misses retained. Vacuum finite-plane audit only.
- `report.py --run .../run-04 --native .../native-04 --output docs/validation/DES-017`
  exits0. Reviewed layout, support and mounting drawings; added coverage-gap map.
  Refined0.25/0.125 mm heat calculations conserve1 W and change worst stress
  temperatures by at most0.005789 K between those grids.
- Seven new conservation/geometry/retained-evidence tests pass (exit0).
- Initial recover_usage output failed because ignored output directory did not
  exist; created it and reran successfully. Only metadata/token_count events read.
  A sandbox read-only process listing failed; no scientific result depended on it.
  Final logger/dashboard/diff and hosted checks will be added when observed.

Closeout checks observed2026-10-06:7 new and20 inherited disc controls pass;
31 dashboard controls pass. Logger validates101 records; summary has44/101
sessions with81 observed turns, not a full-project/current-turn total. Dashboard
validates42 tasks/23 documents/19 reviews and builds under_site/disc-support-variants.
The first logger check used an incorrect lower-case status enum; corrected to
PASS. The first dashboard output underbuild/ was rejected by the output guard;
corrected to_site/ without weakening validation. Full staged and parent-relative
whitespace checks pass. Generated probe bytecode was excluded before commit.

## Changes and revision links

See paired JSON for actual file inventory. New DES017 document, isolated tools,
retained evidence and CI controls, project tracking and this logger pair. Prior
scientific inputs/reports, native hashes, production detector and PR40 movement
table unchanged. Result commits will be listed after they exist.

Scientific deliverable committed asdb4a47a5c19198dc641a31b89c467e3c392c83a4,
normally pushed and published in[PR42](https://github.com/asalzburger/nodd/pull/42),
basecodex/issue38-disc-overlap (PR41). PR42 attached to this app chat. Description
contains comparison/drawings/reasons, explicit sensor-placement amendment and
coverage/guard/thermal/service gates. A rounded gap value and report hyperlink
were corrected in the hosted description. Public source IDs were reused with
precise locators; no external paper or old evidence was overwritten.

## Token accounting

This canonical task owns only turn01a10db9-36a0-7922-971e-3730adf8d4b8. It is active;
final counters and client completion boundary cannot yet be recovered. `usage`
stays empty, meaning unknown. Earlier app/shared/radial/service-radius turns keep
their existing canonical attribution. A bounded self-pausing follow-up will
recover only this exact closed implementation turn after completion, validate
increments, import once and push logging-only evidence. That follow-up's own
bookkeeping counters are separate/unknown. Older project coverage remains partial.
Never query conversation items, retain raw conversations/private model state,
duplicate turn observations or claim a self-inclusive/current all-project total.

## Follow-up

Scientific follow-up: resolve coverage, guard feasibility and fixed service demand;
cold thermal/expansion/load-sharing coupons and swept CAD/FEA before adoption.
Resource follow-up: exact completed-turn accounting only. Formal DRAFT unchanged.
