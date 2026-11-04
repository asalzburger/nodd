# SESSION-2026-10-15-hcal-common-module — Common HCAL readout module

## Scope and evidence

Contemporaneous curated task record, starting from clean commit
`7243c84c055a5c2817f7eb86727ca7eade2f21c8` on
`codex/hcal-realism-assessment`. Exact conversation start and client per-turn
usage were not exposed. No pre-existing user modifications were overwritten.
This bounded task follows the HCAL investigation in DES035.

## Selected conversation

Exact user direction: “Alright, let’s start: operating contract is 14 TeV hadron
collider, kick it off as suggested with a common readout module.”

Assistant outcome: drafted DES036 before code, implemented a standalone common
readout board and paired service carrier, executed native and saved-event checks,
and retained all unsigned assumptions. The human fixed collision energy only;
25 ns, 750 kHz, latency, current and thermal inputs remain planning choices.

## Decisions and outcomes

One common 184 mm square board has 36 scintillator/SiPM/LED channels. Two boards
share one 380 × 240 × 12 mm carrier, cold plate, service PCB/interface and four
connector envelopes. Each board allocates one H2GCROC-class 78-channel chip:
36 connected ordinary inputs, 36 unused ordinary inputs and six auxiliary inputs.
All channels are continuously powered in the budget. Source-backed SiPM package
and new undoped C8H8 host are distinct from project envelope/material proxies.
The source catalogue records public component/architecture locators.

CaloTech provided component evidence and SysArch bounded physical/service
interfaces. SoftEng implemented the isolated model/export/factory. PhysVal
reviewed the design and later exact implementation snapshots. Main coordinated
source cataloguing, native/transport verification, drawing, records and delivery.
These were explicit role-prompt assignments; native profile loading was not
verified. Full scoped contracts follow below.

PhysVal caught the original 0.9 mm recess failing the sourced upper package
height. DES036 was explicitly amended to 1.1 mm before final code/evidence, with
maximum-height and old-depth controls. Later code review found missing saved-run
provenance and NaN-energy acceptance. Main corrected both, added nine fault
controls and reran native and Geant4. PhysVal closure review at
`97d0bb64c22f63c0680c543a97c5b05ce2acc4b8` confirmed both fixed in source and nine
controls passing. It did not execute the final native/transport rerun. See the
[review record](../../docs/validation/DES-036/review.md).

Final conditional paired-unit mass is 3.018 kg and nominal heat 5.939 W; the
reference steel patch is sector-owned and excluded. Nominal DAQ utilization is
93.75%, while the 1 MHz stress remains visibly overloaded at 125%. No claim of
queue, readout, optical, radiation or thermal qualification follows from these
numbers. Shared carrier egress, actual ASIC/package, manufacturing tolerances
and irradiated sensor operation remain open.

## Commands and validation

Actual final checks and source identities are retained in
[DES036 results](../../docs/validation/DES-036/results.md). Standard-library
module/provenance suite: 44 passed, exit 0. Existing hardware/assembly regression:
14 passed, exit 0. Isolated CMake configure/build succeeded. Native audit passed
395 physical parts, 72 unique sensitive IDs, 360 local cell probes and zero
reported overlaps at 1e−5 mm with ROOT seed 36. Actual coolant centreline rays
find 240 mm water on both branches without solid interruption.

Two saved Geant4 muon events, one aimed at each board, passed saved completion,
primary and hit checks: two hits with finite positive energy and valid IDs.
Runner uses seed42, FTFP_BERT and gun argument10*GeV, no field definition. Saved
primary momentum is10 GeV/c along +z; this is not described as verified kinetic
energy. Recorded actual commands/settings/exit and XML/library/inventory/
DDSim/Python/runner/output hashes bind the smoke to the native passing fixture.

The acts-spack preflight warned of changed setup/lockfile fingerprints. Existing
DD4hep1.38, Geant4 11.4.2, ROOT6.40.04 and Python3.14.5 runtime was independently
activated/rechecked with datasets; no installation. Environment activation used
the node ACTS setup, `unset ACTS_SPACK_SETUP`, `setup_spack`, then view
`thisdd4hep.sh` and `geant4.sh` in the same shell as native commands. Sandboxed
sysctl/ps diagnostics and CMake/CLHEP warnings were retained.

An early checker did not support native TGeoTubeSeg cylinders; full-cylinder
support corrected that failure. A subsequent native run printed PASS but exited
133 during ROOT multithreaded teardown; single-thread overlap operation and
explicit teardown fixed it. Only final zero-exit results are retained as passing
evidence. Initial provenance unit fixtures used an unresolved macOS /var symlink
path; resolving the fixture directory fixed three new control failures without
relaxing checks. The first plot attempt lacked Matplotlib in system Python;
existing ACTS venv Matplotlib3.11.2 rendered successfully. PNG was visually
inspected, and its caption/section annotations corrected before final drawing.

An initial ad hoc source-ID audit parsed the JSON-formatted manifest as YAML
lines and falsely reported missing IDs; using the catalogue JSON reader resolved
it. Project/session/token validators, local token-site build, source/link/hash
checks and whitespace checks passed and are recorded in the paired JSON.
No PR, remote publication, production compact or production CMake change.

## Changes and revision links

`7f354fe20307b6fee996c7043e68e5d80dc23a8a`: draft common-module design before
implementation. `fe477dbb10d29bda34753f0c05dce0edaa6d886a`: isolated prototype,
source ledger, controls and tools. `97d0bb64c22f63c0680c543a97c5b05ce2acc4b8`:
review fixes for saved-run provenance and finiteness. Final evidence, drawing,
tracking and this journal are located by this record's enclosing commit. A final
staged check found445 generated SVG trailing-whitespace lines; the producer now
normalizes them and was rerun, without changing geometry or executed checks.
The paired JSON inventories changed files. No human sign-off was recorded;
DES036 remains DRAFT/PROTOTYPE. Bounded implementation task is completed.

## Token accounting

Exact client-reported counters for this parent task and specialist turns were
not exposed, so `usage` remains empty: unknown, not zero. No raw client archive
was read and no counters were estimated. Project summary observed 620,754,236
input and 3,545,169 output tokens across 210 recorded turns, total624,299,405.
There are184 project session records and66 without usage; these partial project
sums do not measure this task or imply complete project coverage.

## Follow-up

Human review of exact project choices; physical ASIC/package and optical/tolerance
qualification; explicit occupancy/luminosity/radiation/lifetime-temperature
contract; continuous readout queue/framing and carrier-egress model; thermal/
hydraulic validation, then repeated assemblies and shower/digitization studies.
No extra user permission was needed for the authorized isolated prototype.

## Bounded assignments

Workflow/profile instructions at 7243c84c055a5c2817f7eb86727ca7eade2f21c8. Explicit role-prompt fallback; native profile loading unverified.

```json
{
  "id": "HCALMODULE-20261015-CaloTech",
  "role": "CaloTech",
  "input_revision": "7243c84c055a5c2817f7eb86727ca7eade2f21c8",
  "inputs": [
    "docs/design/DES-035-hcal-realism-and-prototype-plan.md",
    "docs/design/DES-028-calorimeter-cassettes.md",
    "tools/calorimeter_hardware/cassettes.json",
    "tools/calorimeter_hardware/model.py",
    "reference/manifest.yaml"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "User now explicitly authorizes starting a common HCAL readout-module prototype for a14TeV hadron collider, following DES035. Recommend a concrete small reusable tile-board baseline with direct SiPM readout and H2GCROC-class continuous acquisition; compare6x6 and6x12 arrays at30mm pitch, and specify correct ordinary sensor-channel capacity versus total chip channels. Verify actual public source sections for chip/package footprint, sensor family/material/SiPM, powered channels, bandwidth/buffers/power requirements. Do not claim an unverified real ASIC package or end-of-life qualification. Suggest a mechanically explicit prototype stack and shared-carrier interfaces with named project-choice dimensions. Existing144-tile four-SPIROC footprint must not silently imply qualified pp readout. Read-only return a concrete recommendation and exact citations within about10minutes; no code edits or delegation.",
  "deliverable": "Return a concrete cited module/interface design input for DES036 and its isolated prototype.",
  "completion": "Report exact source revision/locators, recommendation, checks and unresolved assumptions; no human sign-off."
}
```

```json
{
  "id": "HCALMODULE-20261015-SysArch",
  "role": "SysArch",
  "input_revision": "7243c84c055a5c2817f7eb86727ca7eade2f21c8",
  "inputs": [
    "docs/design/DES-035-hcal-realism-and-prototype-plan.md",
    "docs/design/DES-028-calorimeter-cassettes.md",
    "tools/calorimeter_hardware/cassettes.json",
    "tools/calorimeter_hardware/model.py",
    "reference/manifest.yaml"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "User authorizes a common HCAL readout-module isolated prototype at14TeV. Independently specify a bounded physical/service interface contract for a small standard tileboard (6x6or6x12 at30mm pitch) and optional2-board common carrier. Assess absorber ownership, local frames, cooling-contact and connector/collector boundaries, data/bias/LV and maintainability. Use DES035/DES028 constraints and leave current detector outline unchanged. Distinguish modeling fixture choices from connected or engineered services; recommend validation and no-duplicate-material invariants. Read-only; return within about10minutes; no delegation.",
  "deliverable": "Return a concrete cited module/interface design input for DES036 and its isolated prototype.",
  "completion": "Report exact source revision/locators, recommendation, checks and unresolved assumptions; no human sign-off."
}
```

```json
{
  "id": "HCALMODULE-20261015-SoftEng",
  "role": "SoftEng",
  "input_revision": "7f354fe20307b6fee996c7043e68e5d80dc23a8a",
  "inputs": [
    "docs/design/DES-036-hcal-common-readout-module.md",
    "tools/calorimeter_hardware/model.py",
    "tools/calorimeter_hardware/export.py",
    "prototypes/calorimeter/Calorimeter.cpp"
  ],
  "mode": "write",
  "writable_paths": [
    "tools/hcal_readout/config.json",
    "tools/hcal_readout/readout.py",
    "tools/hcal_readout/export.py",
    "tools/hcal_readout/test_readout.py",
    "tools/hcal_readout/README.md",
    "prototypes/hcal_readout/CMakeLists.txt",
    "prototypes/hcal_readout/Readout.cpp"
  ],
  "task": "Implement the user-authorized isolated PROTOTYPE exactly following DES036. Common6x6/36tile board,2boards on shared380x240x12mm carrier. One H2GCROC-class78paid/72ordinary chip per board,36unused+6aux each. Source-backed nominal S14160-1315PS package2.1x2.63x.85, yoffset-.26 toward package so opticalcentre tilecentre; SiPMz2.70..3.55 and solder3.55..3.70. Direct-front LED1x1x.6 at each tile(x+2.4,y),z3.10..3.70, withinr3.5,d.9 recess and reflectoropening. Use 184mm PCBs1.2 with.105equivCu,20x20x1.5 ASIC envelopes and statedstack. Frontend connections are functional proxy, no emulation. Two true cylindrical cooling cuts (r1,length236,yaxis,x+-93,z8.5) displaceCu,240mmTi/water tubes through2.2mm square railports. Carrier serviceboard and4connector proxies fit suppliedDES. Sector-owned absorber30mm referencepatch only standalonefixture. Preserve all existing hardware code/evidence; add standalone CMakefactory only, never production. Reuse Materials helper but no legacy model import collision; new PSHost C8H8 at1.06. Explicit proxy package constituents and roles. Make deterministic source-hashed expected.json/materials.xml/readout.xml export. Expected inventory must list all flat physical parts (unique names,center_mm,frame,shape_kind,dimensions_mm,cuts withframe,volume_mm3,mass_g,owner,role, material and module/sensor for sensitive) and material_totals/channel_map/services/budgets. Factory can flatplaceparts and attach module,sensor on each sensitivevolume, pluszero side/sector/layer/carrier andsystem9. IDs descriptor system:8,side:2,sector:4,layer:6,carrier:12,module:2,sensor:6,x:-1,y:-1; CartesianGridXY30mm offset0 onecellpertile. DistinctmoduleIDs0,1, sens0..35. Source map preserves interboardseam. Analytic CSG capacities require contained,disjoint transformedcuts; implement own checks for shapes used. Budget all78/chip at15mW, .5W support/board,2W sharedinterface,12V90%eff,42Vbias2uA; stress100uA/1mA. DAQ2x1.28Gb/s/chip,payload.8,32bit/all78+64header,750kHz vs1MHzstress; trigger4x1.28/chip separately; report overload not certifiedPASS. Latency512*25ns vs12.5us. Add meaningful negative controls for bad channels/aux, hidden dutyfactor, capacitylatency, wrapping/module/connector overlap, duplicate sharedownership, blockedports/cuts/mass. Provide no claim of optical/readout/hydraulic engineering qualification. Main writes native checker, transport smoke, drawing, documentation/manifest/tracking. You may run only standard-library tests/export; do not set up runtime or commit. Send schema/commands promptly after first export then finish bounded implementation.",
  "deliverable": "Seven owned source/config/test/guide files; tested deterministic export and controls. Message main expected schema and commands for native audit.",
  "completion": "All owned code complete and standard-library controls pass; no production edits; report actual commands/counts and unresolved physics/engineering assumptions; no delegation/signoff."
}
```

```json
{
  "id": "HCALMODULE-20261015-PhysVal",
  "role": "PhysVal",
  "input_revision": "7f354fe20307b6fee996c7043e68e5d80dc23a8a",
  "inputs": [
    "docs/design/DES-036-hcal-common-readout-module.md",
    "docs/design/DES-035-hcal-realism-and-prototype-plan.md",
    "reference/manifest.yaml"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independently assess the fixed DES036 common-module design for scientific/operating claim consistency. User confirms14TeV hadron collider only and asks startcommonmodule. Check explicit25ns/750kHz/latency planning choices,78paid vs72sensor capacities,packetbudget limitations,SiPMbulkproxy and stresscurrents,forward applicability and native/smoke-vs-response boundaries. Read actualprimary references where needed. Report concrete corrections prior to nativeimplementation claims; this is not a code review yet. New sourceIDs namedDES036 are being catalogued by coordinator, so do not treat temporary unregisteredIDs alone as scientificblocker. No edits/runtime/delegation. Later exact code snapshot will be separately provided if needed.",
  "deliverable": "Read-only findings with precise source locators and actionable corrections for DES036; no human signoff.",
  "completion": "Report reviewedrevision, findings or no findings, actualchecks and limitations."
}
```

```json
{
  "id": "HCALMODULE-20261015-PhysVal-code",
  "role": "PhysVal",
  "input_revision": "fe477dbb10d29bda34753f0c05dce0edaa6d886a",
  "inputs": [
    "docs/design/DES-036-hcal-common-readout-module.md",
    "tools/hcal_readout/config.json",
    "tools/hcal_readout/readout.py",
    "tools/hcal_readout/test_readout.py",
    "tools/hcal_readout/native.py",
    "tools/hcal_readout/transport.py",
    "prototypes/hcal_readout/Readout.cpp"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Review fixed common HCAL module implementation and scientific claims after earlier designreview. Assess channel/aux/power ownership, realgeometry/opticalproxy limits, servicegraph/overload honesty, and independence/coverage of native/transport checks. Sourceheight recess amended1.1; check limitation is correctly handled. Run only appropriate standard-library checks if useful. Main now executes native and savedmuons, reports will be sourcebound but not yetcommitted. Identify realbugs or misleadingacceptanceclaims; no genericrequests for finished engineering beyond scopedprototype. No edits/delegation/runtime setup. Return within about5minutes if possible.",
  "deliverable": "Independent code/claim findings at exactrevision with actionable corrections and actualchecks.",
  "completion": "Return concrete findings or nofindings with limits; no engineering/humanapproval."
}
```


### Closure review extension

Read-only PhysVal follow-up at `97d0bb64c22f63c0680c543a97c5b05ce2acc4b8`,
bounded to the two checker findings, `smoke.py`, `transport.py`,
`test_transport.py` and guide changes. No writable paths. Completion: report
exact snapshot, controls actually run, closure or remaining findings, without
engineering sign-off. Both findings closed in source; nine controls passed.
