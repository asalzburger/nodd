# DES039 — Separate PhysVal assessment

- Assignment: FCAL-PhysVal-01; explicitly supplied PhysVal mandate.
- Reviewed revision: `3c5eded29c1186e7dbd213ac5aab913376babc05`.
- Mode: read-only; assessment returned to coordinator, who retained this report.
- Reviewer: separate Codex agent context; no human expertise or sign-off inferred.
- Date: 2026-10-17.

## Conclusion

No blocking numerical or scientific interpretation error was found for the **scoped prototype envelope-fit claim**. The common body fits both pinned contexts, with the 02 collar and explicit aperture/service amendments. This does not establish a complete installed or functioning calorimeter, engineering acceptance or performance.

## Findings and coordinator dispositions

| ID | Priority | Finding at reviewed revision | Disposition |
| --- | --- | --- | --- |
| PV01 | P3 | Technology input line 59 retained stale R270–276 support / R276–288 service intervals, unlike the authoritative R278 sampling-shell boundary. | Corrected the table to R270–278 cradle, R278–290 sampling housing, R281–287 rear pipe bay and R288–290 rear housing. Distinct axial bays remain explicit. |
| PV02 | P3 | Technology input line 77 described the negative assembly as reflected. The implementation uses the correct determinant+1 rotation. | Replaced wording with proper Rx(180°) rotation of the whole assembly. Geometry unchanged. |

Both corrections are editorial; reviewed scientific input/model/native bytes are unchanged. Formal document lifecycle remains DRAFT.

## Actual separate checks

The reviewer read exact inputs with `git show`, verified analytical/native source hashes against the reviewed commit (including both child manifests), and compared both layout context snapshots with their full historical source revisions. All matched.

The 10 unit controls passed after confirming current science bytes matched the target. A separately written distance-parameter quadratic calculation checked 38 random/adverse finite-cylinder rays against the implementation; maximum discrepancy 1.11e-9 mm. Independent material volumes, partial masses, heat and flow calculations agreed: 4,840.200 kg/body/end, 1,105.167 kg/collar/end; 109.472/458.488 W and 0.008722/0.036527 kg/s per component/end. PDG tungsten/quartz values and sensor package/pixel geometry were checked against primary sources.

The reviewer inspected native evidence without rerunning ROOT/Spack/DD4hep/Geant4. Recorded successful exits, zero overlaps and path residuals were consistent with the exact source hashes and disclosed scope. There is no claim of a second native execution.

## Qualifications retained

R50 replaces the former R80 reservation; downstream pipe and machine protection remain unspecified beyond four metres. The collar R444 local lines, R435→294 collector and complete manifold connections are not a completed continuous native network. The source and results disclose this omission.

Long/short fibres are overlapping depth weightings. Average nuclear interaction length, direct fibre crossings and solid paths are distinct from optical response, efficiency, containment and pion interaction length. The offset phi grid excludes aligned joints; the explicit zero-matrix seam control is retained.

Complete optical loom collisions, shower/edge leakage, radiation lifetime, beam heat, circuit/DAQ, thermal/hydraulic, structural and access qualification remain open. This separate AI assessment grants no human approval or acceptance.

## Follow-up: portable report representation

FCAL-PhysVal-02 independently reviewed exact commit `f6e1ef9433c06f4ca274fb0c912c383b6d846e5f`, read-only. No blocking finding was returned. Model, configuration, context, native implementation and native report bytes are identical to the original assessed scientific revision.

The revised report equals the earlier output rounded to twelve significant digits, plus declared serialization metadata and a generator hash. Across 459 floating values, maximum relative rounding change is 4.81e-12; maximum spatial dimension/path change is 4.95e-9 mm, more than 2,000 times smaller than the unchanged 1e-5 mm native tolerance. Integer counts, identifiers and source hashes remain exact. The strict retained-file comparison remains active; physical computations retain full precision.

Actual follow-up checks: all 11 controls and `study.py --check` passed; the reviewer independently rejected NaN and both infinities, verified the generator hash and confirmed rejection of the 1 micrometre adverse change. No native simulation was rerun because its source/input bytes were unchanged. The coordinator separately observed the corrected FCAL step succeed in Linux run 39030964508. Whole-workflow completion is a separate hosted observation.
