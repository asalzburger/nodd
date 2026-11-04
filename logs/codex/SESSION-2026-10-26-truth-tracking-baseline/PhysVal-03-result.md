**TRUTH-PhysVal-03 completed, read-only.** Reviewed scientific source/evidence **`f7b14c60c8be613ce9165684d6ef03007ce1a456`**, native execution **`39cd5185d21a0ef47445023000c0381dc4b5360f`**, ACTS **`355ea68493b326956756c9386d2fd9eaf9328568`**. All **44 assigned working files** matched pinned bytes. No files changed, builds, native reruns, installs or nested agents.

**No blocking implementation, reduction or presentation finding was detected for this qualified prototype characterization.** The results show substantial response/model discrepancies and do not establish calibrated pulls, detector acceptance or pattern-recognition performance.

**Independent primary-data checks**

| Case | Generated | Selected / attempted | Finite fits | Native unmatched | Wrong charge |
|---|---:|---:|---:|---:|---:|
| Geant4 1 GeV | 20,000 | 19,998 | 19,994 | 1 | 16 |
| Geant4 10 GeV | 20,000 | 19,999 | 19,999 | 0 | 25 |
| Geant4 100 GeV | 20,000 | 20,000 | 20,000 | 1 | 560 |
| Fatras 1 GeV | 20,000 | 19,992 | 19,992 | 1 | 0 |
| Fatras 10 GeV | 20,000 | 19,998 | 19,998 | 0 | 0 |
| Fatras 100 GeV | 20,000 | 19,999 | 19,999 | 0 | 467 |

- Verified **120,000 unique generated events**, one origin muon each; selected primary barcodes, unique candidate/output identities and every event denominator.
- **119,982 finite fitted tracks**; 14 selection losses and four fit failures remain explicit.
- Independently checked every fitted five-parameter covariance for finite values, positive diagonal, symmetry and **Cholesky positive definiteness**. No invalid fitted covariance found.
- Independently recomputed **17,712 scalar statistics** across every global, signed-eta and absolute-eta bin, including wrapped phi, full theta–q/p propagation of pT uncertainty, means, sample SD, RMS, median, central interval width, mean SE and pull-tail fractions. Maximum absolute discrepancy: **7.28 × 10⁻¹²**.
- Reproduced the first global Geant4 1 GeV d0 residual’s **400 event-bootstrap replicates** and all four retained bootstrap errors. All **8 pinned metrics tests** passed.
- Verified every **3,199,735 measured-coordinate variance** against the frozen table’s squared SD, with exact equality after ROOT dtype conversion. Maximum relative storage roundoff: **5.15 × 10⁻⁸**.
- Actual configurations are identical across six runs: **11,806 pixel 2D**, **12,384 short-strip 2D**, **21,456 long-strip 1D** sensors. Every **1,836,922 recorded measurement dimension** agrees with its sensor entry.
- Generated truth is exactly equal between backends at each momentum.
- Verified all **42 complete native output hashes**, common source/binary identities, map/manifest hashes and six-run geometry/factory/library identities. All **11 retained portable reports** exactly normalize their hashed original reports.

**Guarded association is appropriately narrow**

`export_profiles.py:190–227` checks selected primary identity, one candidate, at most one output at index 0, and distinguishes exact primary barcode from the all-zero sentinel. Nonzero conflicts fail. Upstream `TrackTruthMatcher.cpp:94–134`, with the default ratio **0.5**, explains the native Fake classifications.

Independently confirmed exactly:

- Geant4 1 GeV event **2129**: 3 fitted measurements / 20 primary measurements.
- Geant4 100 GeV event **27**: 7 / 19.
- Fatras 1 GeV event **17622**: 11 / 23.

All three have all-zero native barcode, Fake classification and NaN writer truth, but a verified unique selected primary-derived input. Keeping their **seed-associated** residuals avoids removing poor partial fits. The README correctly distinguishes this from native matching efficiency.

The four Geant4 1 GeV fit failures are **4059, 16435, 19129, 19186**. Their categories are unavailable at recorded WARNING verbosity; no causal diagnosis is justified.

**Control and figure checks**

- Independently compared actual before/after ROOT payloads for all four completed reference-removal controls: **688 branch pairs across 12 file pairs**, exactly equal including NaNs. Verified their report/output hashes. The two crashed historical Geant4 cases remain excluded.
- All **1,440 unique CSV rows**, comprising **21,600 numerical fields**, match retained profiles.
- Visually inspected all **10 pinned PNGs** at original resolution. Titles, legends, units, eta/pT coverage and scales are readable; core widths, full-tail widths and generated-event fractions remain clearly distinguished.

**Scientific interpretation**

The README’s numerical interpretation agrees with the independently checked data. Central 1 GeV pT pulls have full SD **96.20** in Geant4 and **17.90** in Fatras, versus central half-widths **3.43** and **1.51**. At 100 GeV, forward relative-pT central half-widths exceed **100%** for `3.5≤|eta|≤4`, with wrong-charge counts **421/2529** and **401/2529**. These are retained adverse results, without clipping or tuning. Nonlinear pT full SD is appropriately described as a finite-sample tail diagnostic.

Retain the documented qualifications: one-phi-bin/material-locality approximation; ideal binary response; marginal error table without incidence conditioning/correlations; omitted training/model uncertainty; ideal origin truth seeds and constant field. The older five-event lifecycle comparison and training observer end-hash qualifications remain accurately bounded. No full final-executable lifecycle equivalence or exact training observer replay identity is claimed.

This assessment supports publishing the reproducible **first truth-associated baseline**, with its discrepancies and limitations. It grants no human design sign-off or acceptance.
