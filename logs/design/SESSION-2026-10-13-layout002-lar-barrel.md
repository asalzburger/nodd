# SESSION-2026-10-13-layout002-lar-barrel — LAYOUT-002 LAr barrel

Human requests two new PRs replacing SiW with an ALLEGRO-style LAr ECAL,
allowing larger HCAL envelopes and routing gaps for cables/cooling. Forward
regions beyond the LAr design are to be explicitly marked for later FCal.
LAYOUT-002 is a separate candidate beside LAYOUT-001 on the merged main page.
This journal covers the barrel, shared service budget and first PR; endcap and
complete candidate integration have a separate follow-up record. No new external
software is adopted. Explicit isolated PROTOTYPE work; no human design sign-off.
Starting main e33ae62 includes mergedPR72; PR64/70/71 remain open. Exact current
root/child counters are unavailable; usage remains unknown.

Coordination/evidence/review skills read. Native role loading is not claimed;
these generic bounded read-only assignments apply complete prepared profiles
from the working checkout at main e33ae62. Primary-source verification follows
prior fit assessment a3dffd3; earlier facts are not engineering qualification.

## Prepared bounded assignments

```json
{
  "id": "LAYOUT002-SysArch-input",
  "role": "SysArch",
  "input_revision": "e33ae62ce16592c26c581c5311c4dc493d9714b1",
  "inputs": [
    "docs/layouts/LAYOUT-001.json",
    "docs/design/DES-029-calorimeter-assemblies.md",
    "tools/calorimeter_hardware/assemblies.json",
    "reference/manifest.yaml"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Assess the LAYOUT-002 physical integration of ALLEGRO-style LAr/Pb-steel ECAL in nODD with existing inner3T magnet and tracker retained. User authorizes increasing HCAL envelopes and barrel/endcap gaps for cable/cooling services, and leaving a marked forward FCal insertion if LAr cannot cover it. Read prior comparative assessment at extra exact revision a3dffd327e47cc65dfacb33cf6b7219923683166:docs/design/inputs/DES-030-allegro-ecal-fit.md and its scalar report, but independently verify primary ALLEGRO source dimensions/ownership using public published sources and official k4geo source e1ba7bc3e0d7291ebe3f6a02abfa784f879e36cb. Compare retaining ALLEGRO active radii against compact repackaging; recommend one physically coherent prototype preserving absorber/electrode geometry rather than silently shrinking LAr gaps. Quantify parameterized signal/HV/power/fibre/cooling/cryogenic pipe allocations, lane counts, feedthrough/cold-bath access and bend allowances; distinguish sourced facts from explicit unsigned design choices with uncertainty. Derive HCAL barrel radial envelope, ECAL-HCAL radial services space, HCAL barrel/endcap axial routing gaps, endcap front/back/radial envelope and required reserved forward insertion. Route pipes/cables in genuinely empty allocations with continuity/access, not material-filled reservations. Do not adopt external software, install, edit files, message other tasks or delegate. Return a concrete cited interface/ownership/service-area budget with formulas and actual checks, not engineering approval.",
  "deliverable": "Read-only quantitative interface proposal and uncertainties returned to root for DES032/DES033 and journal.",
  "completion": "Return exact-revision findings and primary-source locators, explicit missing evidence, formulas and actual checks. No design/performance acceptance or implementation writes."
}
```

```json
{
  "id": "LAYOUT002-PhysVal-input",
  "role": "PhysVal",
  "input_revision": "e33ae62ce16592c26c581c5311c4dc493d9714b1",
  "inputs": [
    "docs/layouts/LAYOUT-001.json",
    "docs/design/DES-029-calorimeter-assemblies.md",
    "tools/calorimeter_hardware/assemblies.json",
    "reference/manifest.yaml"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independently establish ALLEGRO barrel/endcap physical design facts and prototype response/coverage limits for replacing SiW in LAYOUT-002. Read prior assessment at extra exact revision a3dffd327e47cc65dfacb33cf6b7219923683166 and independently inspect primary publications and official k4geo source e1ba7bc3e0d7291ebe3f6a02abfa784f879e36cb. Determine inclined-plate/turbine geometry constraints, legitimate nODD adaptations, longitudinal segmentation, active gaps/readout identities, cryostat/electronics maturity and forward angular coverage after moving endcap front to nODD. User permits more HCAL space and a later marked FCal insertion; no resolution/acceptance claim implied. Quantify eta band/first usable wheel, sampling along rays and boundary issues; distinguish nominal XML radii from actually built blade bounds and paper vs XML versions. Investigate primary-source front-end/channel/power/cabling/cryogenic data if available; report what is not published, so estimates remain labeled choices. Do not retune requirements, adopt external software, install, edit files, message other tasks or delegate. Return cited findings, formulas/checks and bounded validation criteria to root. No human sign-off.",
  "deliverable": "Read-only primary-source fact ledger, independent geometry/forward/claim assessment and minimum validation requirements.",
  "completion": "Return exact-revision findings and primary-source locators, explicit missing evidence, formulas and actual checks. No design/performance acceptance or implementation writes."
}
```
