# Tracker module reuse comparison — PR132 follow-up

**PROTOTYPE, unsigned.** The [2026-11-11 review comment](https://github.com/asalzburger/nodd/pull/132#issuecomment-6790854055)
authorizes a tracker comparison prototype. Governing records: DES-025, DES-043,
ADR-003 and issue130. This experiment does not change the maintained detector,
its compact exporter, physical parameters or approval state.

The [initial investigation](README.md) and `results.json` retain their original
baseline-only identity. This follow-up tests the proposed short-strip barrel
experiment, where 8,064 modules have one strict local recipe. It does not apply
ECAL timing ratios to the tracker.

## Experiment definition

Control: unchanged combined DES-025/DES-043 tracker exported at
`d6d2c510cf63209228790a95fd57d155a7b9787a` and built afresh locally.
A: strict module template cache, retaining assembly structure.
B: the same cache with a finite real module mother, subject to containment and
sibling-interface checks. The other tracker factories, materials, readouts,
IDs, cuts, physics, seeds and simulation controls remain matched.

Compare A/control for factory construction and unique-object costs. Compare B/A
for hierarchy, direct world daughters, DDG4 mapping and geometry closure. Do not
sum nested phase intervals. Full subprocess wall time includes inventory JIT,
I/O and teardown. Repeated observations characterize this node; they do not
select a detector acceptance threshold or establish a general speedup.

Required comparisons include all expanded sensors and original constituent
placements, material/shape/transform identity, contact/window probes, packed
IDs and per-instance DetElements. A real mother also needs finite containment,
sibling overlaps and sampled material-ray checks. ACTS and response qualification
remain separately identified; one geantino event cannot establish response
equivalence. Preserve adverse results.
