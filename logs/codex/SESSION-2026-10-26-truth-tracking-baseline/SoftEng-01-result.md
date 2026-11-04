TRUTH-SoftEng-01 complete. All six final campaigns exited 0 at scientific source pin `39cd5185d21a0ef47445023000c0381dc4b5360f`, using constant 3 T and the frozen RMS table SHA256 `4d637137a64ae5854fc795634a4fdffae8ece4d081220ef143de907f219b460c`.

| Simulation | pT GeV | Generated | Selected | Fitted | Invalid covariance | Seconds |
|---|---:|---:|---:|---:|---:|---:|
| Fatras | 1 | 20,000 | 19,992 | 19,992 | 0 | 316.02 |
| Fatras | 10 | 20,000 | 19,998 | 19,998 | 0 | 319.87 |
| Fatras | 100 | 20,000 | 19,999 | 19,999 | 0 | 317.94 |
| Geant4 | 1 | 20,000 | 19,998 | 19,994 | 0 | 442.41 |
| Geant4 | 10 | 20,000 | 19,999 | 19,999 | 0 | 457.63 |
| Geant4 | 100 | 20,000 | 20,000 | 20,000 | 0 | 448.95 |

Outputs and complete native provenance are under `build/truth-tracking-baseline/{fatras,geant4}-pt{1,10,100}/`.

Native build passed; my activated runtime tests passed **7/7**, digitization tests **6/6**. Coordinator independently confirmed **24 combined tests passed without skips**. Native source/binaries remained frozen throughout final production.

The read-only truth-matching investigation confirms exactly three fitted tracks have native unmatched sentinel barcodes:

- Fatras pT1: event 17622, fitted 11 of 23 primary measurements.
- Geant4 pT1: event 2129, fitted 3 of 20.
- Geant4 pT100: event 27, fitted 7 of 19.

All have one generated primary, matching selected primary barcode `(1,0,1,0,0)`, one candidate, one fitted track numbered 0, and native classification `Fake=3`. ACTS double matching requires ≥0.5 completeness; failure deliberately removes the optional truth ID, causing zero barcode and NaN writer truth. No nonzero incorrect barcodes occur in any final case. The proposed narrowly guarded association to the unique primary-derived proto track is supported by native scheduling and ROOT evidence; retain native unmatched counts separately.

The four Geant4 pT1 fit-loss events are **4059, 16435, 19129, 19186**. Their error categories are unavailable because pinned native code logs fit errors at DEBUG while production used WARNING. No reruns or tuning performed.

Retained controls establish:

- Standard/persistent Geant4 lifecycle payloads agree exactly across 210 branches.
- Removing the unsafe reference finder leaves all particle, measurement and track-summary branch payloads exactly equal for all three Fatras cases and completed Geant4 pT1.
- Failed initial Geant4 pT10/100 and all other historical controls remain explicitly excluded.

Comparison files are `native/lifecycle-equivalence.json` and `native/reference-removal-payload-check.json`. The independent 50k Fatras training sample and training observer-provenance qualification remain preserved. No further source/output changes were made during the final matching investigation.

Coordinator follow-up: after adding the guarded absent-match analytic control, all25combinedcontrols passed in the native environment; native production source remains39cd5185.
