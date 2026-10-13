# SESSION-2026-10-13-siw-barrel — Detailed SiW barrel prototype

## Scope and selected request

Human requests two PRs: a detailed SiW barrel prototype following PR70, and a
separate README-linked layout main page with one current candidate. They also
require future approved/merged prototype changes to update that page.
This record covers the barrel and necessary parent integration; the main-page
work has its own journal/worktree. Exact current usage is unavailable.

## Initial dependency integration

Starting scientific source: PR70 at5664d16aea2df36222dc0099ba18594cf506304d,
clean before this assistant's new journal pair. PR69 is observed merged at
2026-10-13T09:47:08Z as7c6d453fef12c3207b468c4fc99633fb393072a4. PR70 still
targeted its old parent branch. Ordinary main merge has one tracking conflict;
records are reconciled by stable IDs and later observed revisions, retaining
source and log contributions. Actual PR69 merge metadata replaces stale open
metadata. Geometry remains the existing endcap prototype in this phase.

## Runtime and approval boundaries

Read the acts-spack skill and node workflow. Registry preflight returned2:
setup/lockfile fingerprints changed. Reported this before dependent execution.
Fresh approved shell actually activates the existing environment, verifies
DD4hep1.38 /7deaacd, Geant411.4.2 /cpge6jj, ROOT6.40.04, Python/runtime imports
and all listed datasets. This re-verifies needed installed capabilities,
not staged full sources or detector performance. No package installation.
Human request authorizes isolated prototype work, not production sign-off.

## Work status

Bounded SysArch contribution is read-only at the exact inherited source below.
Root implements the detailed barrel and owns project/journal/PR integration.
Independent PhysVal review follows a fixed implementation revision. Full
source/config/native hashes and checks will be appended after execution.

## Token accounting

Current per-turn counters and child counters are unavailable. Usage stays
empty/unknown; no estimated identifiers or counters are entered.

## Prepared bounded assignment

Explicit generic role assignment; native profile loading not claimed. Workflow instructions from main 7c6d453fef12c3207b468c4fc99633fb393072a4.

```json
{
  "id": "BARREL-SysArch",
  "role": "SysArch",
  "input_revision": "5664d16aea2df36222dc0099ba18594cf506304d",
  "inputs": [
    "docs/design/DES-030-ecal-edge-sensors.md",
    "docs/design/DES-029-calorimeter-assemblies.md",
    "tools/calorimeter_hardware/assemblies.json",
    "tools/calorimeter_hardware/edge_sensors.json",
    "tools/calorimeter_hardware/cassettes.json",
    "docs/decisions/ADR-008-prototype-ecal-forward-aperture.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Assess a detailed SiW ECAL barrel prototype matching PR70 detail while retaining DES029 radial/axial/16-sector/layer envelopes. Read public inherited choices from commit5664. Propose concrete physically manufacturable per-sector/layer board/slab packing with compact full square90mm sensors, explicit inactive guards, PCB/ASIC/thermal stack, shared interface bays and common cooling. Determine whether custom edge/short boards are needed for barrel and where seams/service/end losses remain. No performance acceptance or new envelope/technology choices. Consider assembly support/service routing and absorber ownership rather than just active area. Provide independent interface constraints/checks to root, who implements. Extra governing instructions from main7c6d453. Do not edit files, install dependencies, message tasks or create further agents.",
  "deliverable": "Cited bounded interface proposal with coordinates, retained dimensions, uncertainties and minimum validation checks; return to coordinator for DES031/journal.",
  "completion": "Concrete candidate packed inside existing envelope with alternatives and explicit mechanical/thermal/service limitations. Identify any unavoidable change needing human choice; do not infer design approval."
}
```

## SysArch handoff and implementation choices

BARREL-SysArch read5664d16 and primary CALICE source under main7c6d453
instructions. Independent checks support retained sixteen-sector/48-layer
geometry, compact94 mm boards,6/7/8 columns, seven1000 mm slabs and short ends;
minimum PCB side clearance1.440 mm. A centered short grid collided with the
40 mm bay when preserving5 mm frames;5 mm inward shift leaves3 mm clearance.
359904 sensors,92135424 channels,15648 complete-lane interfaces give188.40 kW
under inherited continuous hypotheses. Headers/ports cannot be inferred from
material-filled allocations. The sector-centre eta0 ray samples only22 layers.
No native/thermal/performance qualification was supplied by that contribution.

Coordinator's aligned control exposed an entirely blind eta0.25 band. Before
extending implementation, DES031 records an unsigned physical-joint staggering
choice:alternate−96/+96 mm slab phases, retaining board count and envelope,
with276/468 mm end-slab families exchanged between ends. The central sensor row
remains present. This is a separate coordinator amendment, not an independently
reviewed SysArch conclusion. Native checks and separate PhysVal review follow.

Initial script/export failures were corrected before any scientific evidence:
a duplicated center_mm keyword prevented export; a unit test confused radial
cold-plate thickness with axial prism extrusion, and a zero-shift negative fixture
failed generic positivity before its intended bay check. The tests now check
actual radial vertices and a positive1 mm inward shift that physically overlaps
its bay. No tolerance or production input was relaxed.

All30 hardware controls pass, including eight new packing/cooling/ownership/
crack controls. The new standalone factory compiles against verified DD4hep1.38;
CMake reports upstream policy/CLHEP warnings, preserved without suppression.
No new dependencies. Native execution remains pending at this initial source
commit; results are not claimed from successful compilation.
