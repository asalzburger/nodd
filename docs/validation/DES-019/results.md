# DES019 — Trimmed mixed preliminary DD4hep pixel baseline

Date: 2026-10-06. **DRAFT / isolated PROTOTYPE**; user-selected preliminary default.
Governing contract: [DES019](../../design/DES-019-trimmed-mixed-pixel-dd4hep.md).

The default export implements the frozen DES017 mixed template and DES018
whole-inner-ring removal schedule at both ends. The barrel remains exactly
unchanged. The old DES015 config and evidence remain legacy controls.

| Disc at each end | Datum | Removed rings | Modules | Active chips |
|---|---:|---|---:|---:|
| 1 | 615.200000 mm | none | 152 | 302 |
| 2 | 794.414241 mm | none | 152 | 302 |
| 3 | 1046.270150 mm | none | 152 | 302 |
| 4 | 1333.096392 mm | none | 152 | 302 |
| 5 | 1645.287829 mm | 1 | 134 | 284 |
| 6 | 1977.807586 mm | 1 | 134 | 284 |
| 7 | 2327.479444 mm | 1, 2 | 112 | 262 |
| 8 | 2692.090910 mm | 1, 2, 3 | 84 | 234 |
| 9 | 3070.000000 mm | 1, 2, 3 | 84 | 234 |

Both endcaps: **2312 modules,5012 active chips,248 cooling circuits**. With the
unchanged3050/6794 barrel: **5362 modules and11806 sensitive areas**. Relative to
the untrimmed mixed template,424 single modules/chips and1139.712W nominal heat
are removed; the structural annulus and carrier stay full size.

## Actual checks

- Standard-library exporter:9 tests passed, including5 legacy controls, frozen
  survivor transforms/source-ID mapping, barrel identity, heterogeneous cooling
  and transport demand, independent Ti/CO2 conservation, and pin/composition
  negative controls.
- CMake/Ninja and6/6 CTest checks passed. The final runtime CTest contained the
  earlier8-test exporter suite; the ninth material-conservation test passed
  separately after it was added.
- DD4hep/ROOT:11806 sensitive placements; signed tangential/radial axes, normals,
  dimensions, source centres, IDs and readouts checked. No overlaps at1e-5mm.
  Exclusive material volumes/masses and sampled X0/interaction-length navigation
  passed at the unchanged tolerances. Native scans are sampled, not exhaustive
  physical acceptance or reconstruction validation.
- ROOT export roundtrip passed. Portable nodehammer import/roundtrip and all
  generated selections passed.
- Geant4 geometry conversion and FTFP_BERT initialization passed with seed42 and
  **zero events**. No transported-hit, field-map or performance claim.

Maximum sensor centre residual: 4.55856e-13 mm. Simulation inventory mass: 202.751036 kg; this includes effective shared services and is not a manufactured BOM. DD4hep 1.38, ROOT 6.40.04, nodehammer nodehammer 0.0.0.

## Evidence and qualifications

[Native checks](native.json), [workflow](workflow.json), [display](nodehammer.json),
[summary](summary.json), [material/service ledger](service-accounting.json),
[executed inputs/producer hashes](manifest.json), [retained artifact hashes](artifacts.json).
The native execution revision is the starting merge7057861 with a dirty
implementation tree. Producer, compact, expected and plugin hashes identify what
actually ran; enclosing deliverable commits must never replace execution hashes.

The DES019 full sandwich/effective insert allocation is documented separately
from DES017's approximate budget. Full tori preserve summed evaporator length,
not hydraulic connectivity. Removed rows delete their pickups/circuits and
service demand, without shrinking structural plate/cable/service bounds.

DES018 eta/pT exclusion and analytic/ACTS evidence remain inherited. Coverage
holes remain;0.5mm guard and warm−35°C thermal controls fail. Uniform-field
vacuum first-traversal bounds do not establish full physical acceptance.
Reference positive-end trunk utilization remains1.031659 and neck1.397216;
negative1.028227 and1.392568. Conservative/stress screens also fail. Effective
cells can be built despite these packing failures. Fittings, manifolds, bypass
routing, mount couplings, unused thermal-window closure and manufacturing
qualification remain unresolved. No production integration or sign-off.
