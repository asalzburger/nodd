# DES038 — Bounded specialist assessments

2026-10-15. **DRAFT / PROTOTYPE.** AI specialist contributions and independent
assessments; no human engineering sign-off. The
[session journal](../../../logs/codex/SESSION-2026-10-15-hcal-endcap-design.md)
retains contracts and role prompts; native profile loading was unverified.

| Assessment | Exact source | Outcome |
| --- | --- | --- |
| CaloTech + SysArch design inputs | `abd95bdc64b9d7971561d659bf953e71de4e7e99` | Broad mechanical quarters, intact common hardware, explicit aperture-adaptive origin comparison and depth/service boundaries |
| SoftEng analytical implementation | `516151c6e962d481efffde95eea9a9ab0f162098` | Four owned model/config/test/guide files; no production/native changes |
| PhysVal design review | `516151c6e962d481efffde95eea9a9ab0f162098` | No additional endcap design finding; rigid whole-layer rotation preserves area/count under the stated polygon symmetry |
| PhysVal implementation review | `7c7f0ba96b69dd754d6e25bd97cef4cfe502bcae` | No new scoped correctness/claim finding; 19 controls and 3,105 independent global tile probes passed |
| SysArch implementation review | `7c7f0ba96b69dd754d6e25bd97cef4cfe502bcae` | No blocking physical-interface defect in the analytical scope; specific unconnected-route caveat retained below |

Before the implementation snapshot, the coordinator requested explicit front
`origin_mm` naming (component centres remain `center_mm`), a check against the
retained DES036 source hashes, and precise wording for the angular-boundary
filter control. SoftEng applied these changes, added the source-mismatch control
and passed all 19 tests. Geometry/counts/masses were unchanged.

PhysVal independently constructed global tile centres and near-edge points,
converted them to IP rays and checked **3,105 probes with zero lookup
discrepancies**. The 0.01 mm inside/outside edge controls verify the physical
rectangle lookup rather than a filled carrier sheet. Relevant source/dependency
bytes matched the review snapshot. Proper Rx(pi) placement/mask consistency,
shared steel/frame ownership, all-powered channels and separate DAQ/trigger
budgets were consistent. Endcap steel-ray screening remains NOT_RUN.

SysArch independently checked four endcap phases and the proper rotation of
origins, bases and all four water ports. **Interface caveat:** row reservations
follow outward quadrant `sy`, while the unchanged connector bay faces local +y.
Negative-y/aperture-adjacent carriers therefore cannot automatically be treated
as connected to those strips. Annular frame penetrations and endpoint-to-route
checks remain necessary. The explicit `connected=False` and excluded external
material prevent a present connectivity/feasibility claim.

No reviewer ran whole-endcap native geometry, transport, thermal, structural or
response qualification. Untracked drawings and coordinator report text were
outside code review. Residual forward and partial-sampling losses remain open;
no assessment grants human sign-off or detector acceptance.
