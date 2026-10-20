# SESSION-2026-10-17-common-fcal-recommendation — Common FCAL technology for layouts 01 and 02

## Scope and evidence

Bounded recommendation requested by the user; no detector implementation,
technology adoption or design sign-off. The journal checkout starts at
`a54df714d20e1a5249b1e5ba7d54286eeca15f20`; pre-existing changes are inventoried
in the paired JSON and preserved. Current layout evidence was read in other
local checkouts at exact revisions:

- LAYOUT-001 / DES034: `c1f11013b03391a4f09d86b39dff57e6c3f58ab2`,
  `docs/layouts/LAYOUT-001-tracker-3t-siw.md` and
  `docs/design/DES-034-siw-service-envelopes.md`, Forward reservation.
- LAYOUT-002 / DES033: `72d37ee9a56182e4ba974791a848a738c19cf092`,
  `docs/design/DES-033-allegro-lar-endcaps.md`, Forward region and response
  limits, and `docs/layouts/LAYOUT-002.json`, forward_reservations.
- DES038 at the first revision confirms its proposed HCAL extension does not
  enlarge the FCAL reservation. Historical DES003 detached envelopes are not
  substituted for these candidate-specific insertions.

The local `nodd-design-evidence` procedure informed a read-only calorimeter
assessment. This small, closely coupled recommendation was kept with the main
agent; no separate specialist assessment is claimed.

## Selected conversation

User, exact request: “Suggest a FCAL technology that we can fit into both 01 and 02 layouts”.

Assistant outcome: recommend warm tungsten–quartz Cherenkov sampling as the
common technology to prototype, subject to compact optical-readout packaging
and coverage redesign. This recommendation is not human selection or approval.

## Evidence, inference and recommendation

**FACT about draft layouts:** both reserve R=80–290 mm. LAYOUT-001 allocates
absolute z=4.5332–6.3791 m; LAYOUT-002 allocates 4.8500–7.8559 m. The latter
also has a separate upstream collar; copying that collar into 01 intersects its
Si–W endcap. Neither contains FCAL hardware.

**FACT from public sources:** [SRC-CMS-CASTOR-2021](../../reference/manifest.yaml),
section 3, printed pages 6–7, establishes a built tungsten/quartz precedent with
1.6 m length, 20 X0 EM depth and 10 interaction lengths total. Its installed
400 mm outer radius exceeds the 290 mm reservation. Sections 1 and 3 describe
pileup and photosensor limitations. No high-luminosity qualification transfers.

**INFERENCE:** a 1.6 m candidate leaves 245.9 mm axial allowance in 01 and
1,405.9 mm in 02, with different placements. This establishes longitudinal
plausibility only. The same absolute-z overlap is just 1.5291 m, so a 1.6 m
package cannot have identical global coordinates in the two current layouts.
Installed radial fit, rearward optical routing, support, shielding, cooling,
beam-pipe clearance and light yield require a new design. The precedent's
interaction-length total does not establish nODD containment.

**NODD DESIGN CHOICE — recommendation, unsigned:** start with a common warm
tungsten–quartz unit, separately read out in electromagnetic and hadronic depth.
Avoiding a cryostat is an integration advantage in the small shared radial
reservation. Investigate compact optical routing and protected/remote sensors;
their fit is unverified. New transverse segmentation, pileup response and
noncompensation calibration need study. Assess leakage jointly with ECAL/HCAL.

**Alternative:** Cu/W–LAr tubular sampling has built precedent
([SRC-ATLAS-FCAL-CALOR2008](https://inspirehep.net/files/260162e2f20b6a80ef517847fd7378f3),
section 1). A dedicated narrow cryostat makes common integration more demanding;
this has not been proven impossible. A silicon/tungsten alternative would
require explicit forward radiation, electronics and cooling inputs.

**INFERENCE — acceptance limit:** for prompt straight rays, r=z/sinh(eta).
At eta=5, R=80 mm is reached only at absolute z=5.936256846 m. Thus 01 provides
at most 0.44288 m of ray path inside its reservation, even if entirely filled.
The full rectangular-envelope traversal intervals are approximately
3.7846–4.7304 (01) and 3.9926–4.7979 (02), before inactive boundaries. At eta=4,
01 front/back radii are 166.11/233.75 mm; 02 gives 177.72/287.87 mm. The latter
has only 2.13 mm rear radial margin. These are geometry calculations, not
efficiency or containment. Achieving the eta=5 coverage direction needs an
aperture/position/envelope decision, with the downstream machine interface.

## Commands and validation

Read repository instructions, PROJECT, DES/ADR/layout inputs and source catalogue.
Inspected public scientific PDFs. A failed arXiv HTML fetch was resolved by
opening its public PDF. Early broad searches included absent paths; subsequent
reads used the exact existing files and separate branches.

Ran Python standard-library geometry calculations; results above. No DD4hep,
Geant4, optical, thermal, field, overlap or shower test was run. Journal and
dashboard validation results are recorded in the paired JSON after execution.
An invalid journal replacement patch made no Markdown change; corrected with
a single-file update.

## Changes and follow-up

Changed only this journal pair and added the two inspected public sources to
`reference/manifest.yaml`. No DES/ADR state, candidate drawing, geometry or
scientific progress status was changed; no commit or PR was created.

Next work, if requested: a bounded packaging proposal including actual readout,
beam-pipe extension, services, two layout placements, transition coverage and
shower-response validation. Technology and integration remain unsigned.

## Token accounting

Exact client per-turn counters were unavailable; `usage` remains empty.
Observed input/output sums for this session are unavailable, not zero.
Repository summary coverage is reported by the executed logging summary.

## Token-accounting correction — 2026-10-20

Recovered 1 disjoint completed client turns for this bounded task: **1,592,557 input + 13,860 output = 1,606,417 observed tokens**. Cached input (1,468,800) and reasoning output (4,182) are subsets, not additional usage. The initial unknown-usage statement above is historical and is superseded only for these now-observed turns. The [curated recovery inventory](../usage/USAGE-2026-10-20-pr88-accounting.json) retains exact boundaries, event hashes, parent/role attribution and exclusions; dry-run/import/replay found no duplicate ownership. No counters were estimated and the current accounting/readiness turn remains excluded while active.
