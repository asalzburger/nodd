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

## Prepared implementation assignment

```json
{
  "id": "LAYOUT002-SoftEng-barrel",
  "role": "SoftEng",
  "input_revision": "706b78923125d6573af6fc15d7400683da5df4fd",
  "inputs": [
    "docs/design/DES-032-allegro-lar-barrel.md",
    "tools/lar_calorimeter/barrel.json",
    "prototypes/calorimeter/Calorimeter.cpp",
    "prototypes/calorimeter/CMakeLists.txt",
    "tools/calorimeter_hardware/model.py"
  ],
  "mode": "write",
  "writable_paths": [
    "tools/lar_calorimeter/barrel_geometry.py",
    "tools/lar_calorimeter/barrel_export.py",
    "tools/lar_calorimeter/barrel_native.py",
    "tools/lar_calorimeter/test_barrel.py",
    "prototypes/calorimeter/LArBarrel.cpp",
    "prototypes/calorimeter/CMakeLists.txt"
  ],
  "task": "Implement the authorized isolated DES032 LAr barrel prototype from the committed draft, with real1536 inclined absorber/electrode periods,11 physical longitudinal segments and two active gaps per electrode, full square physical material recipes and explicit split radial/axial warm/vacuum/cold walls. Use own geometry derived from straight-line/circle/adjacent rotated plate face mathematics, not copied external factory/code. Public ALLEGRO source facts only; source XMLs/temp correct driver available in /tmp/nodd-allegro-source for dimensional verification. No new externals/install. Do not silently use older different ECalBarrel_o1_v03 driver. Root owns shared services, Cryostat rear-bath amendments, support/service extras and docs/records/PRs; JSON config may be amended by root while you write, retain parameter-driven generation and coordinate interfaces. Minimum half-z3817.2 derived from explicit endwall/vacuum stack. Tabulated path sum closes named final remainder; preserve first-compartment Pb replaced by passiveLAr, steel/glue totals0.1each, PCB1.2 recipe1.7g/cm3 with source fractions (includingBr). Theta readout is layer1 fine, restregular, two-electrodephi grouping. Raw physical volume IDs distinct, grouped cell ID canonicalization explicit. Any canonical positions must be genuinely inside canonical active volume; avoid ghost/theta boundary cells. Native volume-ID and segmentation checks must distinguish raw physical and logical merged IDs. A simpler unmerged diagnostic readout can accompany but must not be passed off as correct grouped mapping or counts. Create exporter expected inventories/materials/hash bindings and standalone C++ factory with meaningful standard-library negative controls; consider generic piece/replica protocol so root can append service/support volumes without editing factory. Write native audit with actual shapes, proper transforms, containment, material density/composition/analytic mass, raw IDs, per-layer channel references/boundaries and full overlaps at10nm seed37, plus signedeta/phi material/LAr crossings if feasible with existing audited ray helper. Source/tool/input hashes explicit. No native runtime jobs or commits/push/PR creation; root runs native checks and records exact evidence. You may run standard-library tests and inspect installedheaders afterskill; no furtheragents. Newcode stays isolated fromproduction. Update coordinator quickly with exported inventory schema/factory CLI/readout semantics so root can build on it.",
  "deliverable": "Owned geometry/export/native/test/factory code, actual standard-library checks, readout semantics/counts/provenance and pending native commands returned to coordinator. Root curates design, service integration, evidence and PR.",
  "completion": "Owned code coherent from fixed draft and root config amendments, physical geometry/readout not replaced by uniform envelope estimates. Report any material modeling/segmentation blocker early; no engineering/performance approval."
}
```

## Source/interface handoffs and coordinated amendment

LAYOUT002-PhysVal-input read e33ae62 and a3dffd3 plus official k4geo e1ba7bc3.
It independently verifies1536planes,11compartments,2172.8–2578.3mm and573.937mm
path, two LAr gaps and readout merging. Source unsignedtheta10 cannot hold new
negative bins; own signedtheta12 and native end-boundary controls are required.
Pinned0.1mm total steel differs from published100um-per-face cold-test baseline;
root selects0.2mm total as an explicit unsigned adaptation, with smaller derived
gaps. Source nominal endcap radii differ from constructed410–2790mm blades;
eta4 is uncovered and a marked FCal reservation is necessary. Scope/envelope
rays are not native efficiency or shower performance.

LAYOUT002-SysArch-input read the same revisions and actual primary PDFs. It
recommends retaining ALLEGRO sampling radii, larger cold electronics baths,
300mm external radial lane,800mm front/500mm rear axial routing gaps, and
explicit FCal/collar reservations. Its512-channel/350×75×35mm board assumptions,
pipe jackets, fills and bend radii are choices. Two140mm rear banks and flat
sector corner/ring interactions need concrete placement checks. Root enlarges
barrel rear bath to170mm: rings with120mm radial H-sections plus a separate20mm
exchanger lane must clear the outer corners of flat boards. These differ from
the read-only proposal and require actual native/independent review.

Root amends warm half-length4100mm,107.2mm cold end-access/bath and3910mm active
half-length. Parent LAr baths contain support/electronics/pipe daughters; actual
shape and exclusive displaced-material accounting stay distinct. This is an
authorized prototype amendment to the original draft, not acceptance.

SoftEng returned six owned files from draft706b789 with9 standard-library
controls passed,33792 raw sensitives and2262528 grouped cells for the prior
3817.2mm active half-length. No native jobs or compilation were performed by
the role. Root now requires the explicit end-bath/config amendment in the same
owned files before full geometry export; readout totals will be recomputed.
The current config/doc dirty amendment is identified here and never presented
as a fixed-revision independent review.

Actual source PDFs downloaded via normal HTTP to ignored reference/cache;
web retrieval gave403 but ordinary public retrieval succeeded. Bundled pypdf
extracts and PDFium renders the selected slides; no packages installed. FitZ
was unavailable and system Poppler absent; bundled alternatives used. Spack
registry preflight returned2 for changed fingerprints; root warned before
dependent commands and actually verified installed DD4hep1.38 /7deaacd,
Geant411.4.2 /cpge6jj, ROOT6.40.04, Matplotlib3.11.2 and all listed datasets.
Full source staging and new external framework adoption were not performed.

## Prepared fixed-revision SysArch review

```json
{
  "id": "LAYOUT002-SysArch-barrel-review",
  "role": "SysArch",
  "input_revision": "ced5a39183f4335b426a6b10fd03eb83a603df42",
  "inputs": [
    "docs/design/DES-032-allegro-lar-barrel.md",
    "tools/lar_calorimeter",
    "prototypes/calorimeter/LArBarrel.cpp"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independently review actual barrel support/electronics/pipe placements, service arithmetic, HCAL/service-envelope interfaces, ownership and dimensional/power claims. Check choices versus primary facts; no filled-space route/engineering acceptance claim. Read the fixed revision in nodd-lar-barrel using git show. Previous native run source hashes matched geometry but later budget code changed; exact-revision rerun is now underway. Do not claim final native evidence until coordinator supplies it. Do not edit, install, adopt dependencies, delegate or approve/signoff. Existing profile instructions continue. Return severity findings with files/lines and exact source commit; root integrates corrections.",
  "deliverable": "Exact-revision independent findings and bounded actual checks, no engineering sign-off.",
  "completion": "Concrete defects resolved or explicitly retained bounded limitations before PR ready."
}
```

## Prepared fixed-revision PhysVal review

```json
{
  "id": "LAYOUT002-PhysVal-barrel-review",
  "role": "PhysVal",
  "input_revision": "ced5a39183f4335b426a6b10fd03eb83a603df42",
  "inputs": [
    "docs/design/DES-032-allegro-lar-barrel.md",
    "tools/lar_calorimeter",
    "prototypes/calorimeter/LArBarrel.cpp"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independently review inclined plate/material/readout geometry, exact circle capacity and native audit/gates, signed theta/merged canonical mappings, sparse hit checker, service material accounting and scientific claims. Identify actual implementation defects or unsupported conclusions. Read the fixed revision in nodd-lar-barrel using git show. Previous native run source hashes matched geometry but later budget code changed; exact-revision rerun is now underway. Do not claim final native evidence until coordinator supplies it. Do not edit, install, adopt dependencies, delegate or approve/signoff. Existing profile instructions continue. Return severity findings with files/lines and exact source commit; root integrates corrections.",
  "deliverable": "Exact-revision independent findings and bounded actual checks, no engineering sign-off.",
  "completion": "Concrete defects resolved or explicitly retained bounded limitations before PR ready."
}
```

## Actual independent results and remediation

At ced5a39183f4335b426a6b10fd03eb83a603df42, SysArch found no P1 default
placement defect; PhysVal independently integrated88 shapes with4.88e-11
maximum relative capacity disagreement. Both ran12 standard-library tests
from fixed Git blobs in memory. They did not run native jobs. Their prior
input contributions are acknowledged; this is a distinct-role check of root's
implementation, not a claim of fully independent design origin.

P2 corrections: reject unsupported fixed board/ring/tube packing parameters;
reconcile20m one-way cables with40m electrical loop; distinguish source1.246mm
gap from prototype1.196mm; use50k maxtrigger/hit rate and64-bit payload choice;
record639.4mm centreline-plus-clearance versus739.4mm inflated S-bend envelope.
Saved hits now require real canonical theta membership, bound successful
DDSim run/artifacts and observed seed/physics. Ghosttheta2047 is rejected.
Rays enforce finite/nonnegative material, active path bounds and expected
finite-volume/full-depth crossings. The258kW adverse case versus200kW cooling,
fully populated slot power, converter location/loss and missing thermal
contact remain explicit unmet engineering scenarios. No tolerance/gate relaxed.
A PR metadata timestamp initially included fractional seconds; validator
correctly rejected it; canonical UTC second timestamps now pass.

## Bounded closeout

Final scientific producer source5f8c505e26f0f325f17d801583042849f06f62a2,
clean tracked tree, successfully re-exported full geometry and re-ran native
gates, sparse DDSim fixture and bound saved-hit checker.13 standard-library
controls pass. Figures were visually inspected. PR73 is pushed to the requested
asalzburger/nodd repository. Task completion denotes delivered prototype
scope, not design acceptance. Actual current root/child token counts remain
unexposed; usage stays empty, historical observations are neither guessed nor
duplicated. Exact endcap follow-up reviews also recheck these corrections.
