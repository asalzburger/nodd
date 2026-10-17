# DES039 — Separate PhysVal assessment

- Assignment: FCAL-PhysVal-01; explicitly supplied PhysVal mandate.
- Reviewed revision: `3c5eded29c1186e7dbd213ac5aab913376babc05`.
- Mode: read-only; assessment returned to coordinator, who retained this report.
- Reviewer: separate Codex agent context; no human expertise or sign-off inferred.
- Date: 2026-10-17.

## Conclusion

No blocking numerical or scientific interpretation error was found for the **scoped prototype envelope-fit claim**. The common body fits both pinned contexts, with the02collar and explicit aperture/service amendments. This does not establish a complete installed or functioning calorimeter, engineering acceptance or performance.

## Findings and coordinator dispositions

| ID | Priority | Finding at reviewed revision | Disposition |
| --- | --- | --- | --- |
| PV01 | P3 | Technology input line59 retained stale R270–276 support / R276–288 service intervals, unlike the authoritative R278 sampling-shell boundary. | Corrected the table to R270–278 cradle, R278–290 sampling housing, R281–287 rear pipe bay and R288–290 rear housing. Distinct axial bays remain explicit. |
| PV02 | P3 | Technology input line77 described the negative assembly as reflected. The implementation uses the correct determinant+1 rotation. | Replaced wording with proper Rx(180°) rotation of the whole assembly. Geometry unchanged. |

Both corrections are editorial; reviewed scientific input/model/native bytes are unchanged. Formal document lifecycle remains DRAFT.

## Actual separate checks

The reviewer read exact inputs with `git show`, verified analytical/native source hashes against the reviewed commit (including both child manifests), and compared both layout context snapshots with their full historical source revisions. All matched.

The10unit controls passed after confirming current science bytes matched the target. A separately written distance-parameter quadratic calculation checked38random/adverse finite-cylinder rays against the implementation; maximum discrepancy1.11e-9mm. Independent material volumes, partial masses, heat and flow calculations agreed:4840.200kg/body/end,1105.167kg/collar/end;109.472/458.488W and0.008722/0.036527kg/s per component/end. PDG tungsten/quartz values and sensor package/pixel geometry were checked against primary sources.

The reviewer inspected native evidence without rerunning ROOT/Spack/DD4hep/Geant4. Recorded successful exits, zero overlaps and path residuals were consistent with the exact source hashes and disclosed scope. There is no claim of a second native execution.

## Qualifications retained

R50 replaces the former R80 reservation; downstream pipe and machine protection remain unspecified beyond four metres. The collar R444 local lines, R435→294 collector and complete manifold connections are not a completed continuous native network. The source and results disclose this omission.

Long/short fibres are overlapping depth weightings. Average nuclear interaction length, direct fibre crossings and solid paths are distinct from optical response, efficiency, containment and pion interaction length. The offset phi grid excludes aligned joints; the explicit zero-matrix seam control is retained.

Complete optical loom collisions, shower/edge leakage, radiation lifetime, beam heat, circuit/DAQ, thermal/hydraulic, structural and access qualification remain open. This separate AI assessment grants no human approval or acceptance.
