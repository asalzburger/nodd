# DES037 — Bounded specialist assessments

2026-10-15. **DRAFT / PROTOTYPE.** AI specialist assessments, not human
engineering approval. The [session journal](../../../logs/codex/SESSION-2026-10-15-hcal-barrel-design.md)
retains complete role-prompt assignments; native profile loading was unverified.

| Assessment | Exact source | Outcome |
| --- | --- | --- |
| CaloTech + SysArch design inputs | `abd95bdc64b9d7971561d659bf953e71de4e7e99` | Preserve common hardware, expose depth incompatibility, preserve ECAL routes, distinguish layer/quadrant/readout boundaries and geometric sampling limits |
| PhysVal design review | `871176aeaad8e31dcb1ad3373cf60552b6cf12de` | One matched-count phase-comparison finding below |
| PhysVal implementation review | `c83e6f4eaebdaa354217b79b963df15c6c3c0a96` | Finding closed; no new scoped correctness/claim finding; 15 controls and 3,105 independent global tile probes passed |
| SysArch implementation review | `c83e6f4eaebdaa354217b79b963df15c6c3c0a96` | No blocking physical-interface defect in the analytical scope; disjoint material domains, narrow-face fit and proper frames verified |

The initial design's nominal ±90 mm tangential phases could force a different
column count from a centred control. For example, the outer four-carrier pattern
cannot fit that full shift. The implementation retains the maximal centred
count in every control and explicitly bounds actual shift to remaining margin
minus 1 mm. Requested/actual phases and margins are retained. This closes the
comparison finding without discarding carriers or changing comparison area,
mass or power.

PhysVal independently constructed global points from placement frames and common
tile geometry, converted them to IP rays, and tested tile centres plus points
0.01 mm inside/outside edges: **3,105 probes, zero lookup discrepancies**. Relevant
source/dependency bytes matched the reviewed commit. SysArch independently
evaluated all 16 frame/transform functions. These are analytic source/coordinate
checks; no reviewer ran native geometry, transport or engineering qualification.
Untracked drawings and coordinator report text were outside those code reviews.

Residual sector cracks, partial transition depth, empty/unconnected collection,
missing external services/structural hardware, radiation/response/rate and
thermal/load limitations remain open and are retained in the design/results.
No assessment changes DES037 to SIGNED OFF or ACCEPTED.
