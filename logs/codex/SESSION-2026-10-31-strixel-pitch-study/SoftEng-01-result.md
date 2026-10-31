# SoftEng-01 — implementation and native execution assessment

- Assignment input: `1dff0452ed1e7ac24d7b746fccc02ee15df5258d`.
- Executed native source snapshot: `8b7c147b3b0da4bd40dcd9ad06c98abcb2de58f9`.
- Later parent analysis/documentation snapshot: `c2453e91255c023f724028f2eb5f1b0f365106c3`; committed after all native subprocesses captured launch provenance. This is a separate source identity.
- Status: bounded **PROTOTYPE** completed; no detector design sign-off or production baseline change.
- Scope: DES-042 / DES-007 short-strip pitch sensitivity using DES-025 maintained PR104 balanced geometry. This assessment is from the implementation author, not an independent review.

## Implemented source

Owned files: `software/analysis/strixel_pitch_study/truth.py`, `campaign.json`, `test_truth.py`, and `software/running/nodd_strixel_pitch_truth.py`. The coordinator committed the snapshots. No shared dependency, accepted baseline or existing workflow source was modified by this assignment. The coordinator subsequently authorized this result record.

The runner reuses native ACTS generation, Fatras interactions, geometric digitization/clustering, unique associations, corrected truth proto tracks and Kalman fitting. It reuses maintained reconstruction material transport, omitting that workflow's Gaussian calibration. Local-v pitches are 0.5/1/1.5/2 mm at fixed 75 µm local-u; system4 local-v is barrel z, system5 local-v is endcap radial. Pixel and one-dimensional long-strip responses remain fixed. Native covariance is pitch-derived clustered covariance; the single-cell limit is p²/12. No old 0.5 mm calibrated width table is applied.

## Executed checks and outcome

All six pinned input blob SHA256 values matched the assignment and working bytes. Actual runtime/native sidecar imports passed after the required ACTS examples base bindings were loaded. One early direct sidecar import without those base bindings failed; using the established native_imports order resolved the import setup without dependency changes.

Five source regression tests pass: only short-strip second-coordinate configs change; all pitches tile 96 mm; exact unique event joins; balanced geometry comparison tolerance; residual/pull sign contract. The combined parent test suite had 10 tests at the first combined check and later 16 tests in the parent analysis review; those scopes remain distinct.

One 100-event v1control and four 100-event v2controls completed. All four v2controls had100selected/fitted events, identical generated and 1,511 simulated-hit payloads, and exact stored single-cell variance checks for both measured strixel coordinates. Cluster-size/local residual diagnostics are retained with those controls. V1/v2report residual-sign metadata was wrong while arrays were fitted−truth; metadata and regression test were corrected before v3production. These are qualified controls, not production results.

All twelve v3 cases completed 20,000 events each: 240,000 generated case-events from three paired 20,000-event samples replayed over four pitches. Every 1 GeV case retained 19,995 selected, attempted, finite, native-matched fits; five events failed the unchanged seven-measurement selection. All 10/100 GeV cases retained 20,000/20,000. There were zero native fit failures after selection, zero native invalid-covariance counts and no native-unmatched fits. Per-case wall time was 293.956–311.347 seconds; summed case wall time 3,600.393 seconds with three concurrent one-thread processes.

The final validator passed: all native output SHA256 values; all requested cases and launch revisions; all 55 source/binary/input fingerprints identical; every generated denominator; exact per-pT generator/all-hit/primary-hit serialized payload pairing; material-map, native geometry report and selected portals byte invariant; every sensitive digitization entry unchanged except system4/5local-v grid; stored d0 residual sign. Native sensor counts were 6,794 / 2,808 / 2,808 / 8,064 / 4,320 / 13,968 / 7,488 for systems 1–7. Both balanced material/selection comparison checks passed; the current map has 67 keys. The registry's exact registered compact SHA256 is 81e2d439a66f0978d0613929842cf6aa4658cd0e0300ede7513d30caae296023.

## Commands and retained local evidence

```sh
source software/env/truth_tracking.sh
python build/strixel-pitch-study/run-campaign.py full
python build/strixel-pitch-study/verify-campaign.py
python3 -m unittest discover -s software/analysis/strixel_pitch_study -p 'test_*.py' -v
```

The ignored original launcher ran `nodd_strixel_pitch_truth.py` with explicit supplier arguments, recorded per case in `run-report.json`. Native directories are `build/strixel-pitch-study/full-v3-pitch{0p5,1,1p5,2}-pt{1,10,100}`. Each contains all-event `events.npz`, original ROOT files, generated inputs and complete native provenance. Arrays retain unsuccessful events, truth/fitted 5-vectors, full 5×5 covariance, stage counts, matching/validity flags and every residual/pull. Coordinates are d0/z0 [mm], phi/theta [rad], q/p [GeV⁻¹]; residuals and pulls are fitted−truth. Relative pT is dimensionless.

`campaign-summary.json`, `verify-campaign.log`, `metrics-source-supplement.json` and `environment-supplement.json` under the same ignored base summarize the executed evidence. Parent retention/plot integration is outside this file ownership.

## Runtime identity and limitations

Actual runtime verification found DD4hep 1.38 `/3yd4hz3`, Geant4 installed 11.4.3 `/wfg55xi` (not used as transport), ROOT 6.40.04 `/szgev3e`, Python 3.14.5 / Clang 21. Native-adapter checkout source was 530080cfe16c7513228bf60238b99d4b9938538a; ACTS source 355ea68493b326956756c9386d2fd9eaf9328568 had a clean source tree. Loaded binary/factory hashes are recorded separately from these source revisions.

acts-spack preflight correctly warned that old setup/lock fingerprints changed and full DD4hep/Geant4 sources were not staged. Actual required runtime capability was reverified; no shared package install/update/build was performed. Sandbox sysctl/ps warnings did not establish activation success; imports, active Spack environment/spec queries and executed native jobs did. Fingerprints are in the environment supplement.

The native runner omitted `truth_tracking/metrics.py` from its initial 55-file fingerprint list. Its launch-commit blob was deaf54c0d2d259738f07b219a5c802e347c4829c and SHA256 a03568236338706cf59d63d81ab9c76a45ca58493704e4ec679b9806382f7f31; working bytes were checked identical before and after production. The parent separately recomputes all observables from full native inputs during retention. Preserve this metadata gap; do not present it as originally captured by the runner.

This is ideal uncalibrated truth-associated fitting with fixed effective material, not occupancy/pattern-recognition/calibrated electronics performance. Power/cable redesign assumptions and numerical interpretation belong to the coordinator and independent physical assessments. No hardware feasibility or engineering acceptance is granted.
