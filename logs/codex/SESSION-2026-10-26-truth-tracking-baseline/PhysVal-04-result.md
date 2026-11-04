**TRUTH-PhysVal-04 completed, read-only**, at **`c3d037afe086146fb8e91b146654dc036ee81dc6`**. All 19 assigned working files matched pinned bytes. No files changed, simulations/builds, installations or further delegation.

**No blocking finding.** The new distributions implement the requested truth-minus-reconstructed convention and retain the complete fitted cohort and observed tails.

**Independent checks performed**

- Derived all six bound-parameter pulls directly from the original ROOT fitted parameters, generated truth and covariances, without using the new exporter/helper.
- Verified shortest-angle phi wrapping and the reversed sign relative to the earlier profiles.
- Recomputed derived pT pulls through the full theta–q/p covariance, including its cross term and charge dependence.
- Independently checked **all 119,982 fitted tracks** for finite six-parameter values and symmetric, positive-definite **6×6 covariance**, using Cholesky decomposition.
- All tracks enter every quantity: **839,874 entries across 42 histograms**, with **zero nonfinite entries, underflow or overflow**.
- Every histogram’s bin counts exactly match independent raw-ROOT calculations. Shared edges contain all finite extrema; core and full views use the same normalization.
- Recomputed all **210 retained mean/SD/central-width/extrema values**. Maximum absolute difference: **1.16 × 10⁻¹⁰**, associated with the extreme derived-pT calculation.
- Full variable-bin density integrals agree with 1 within **2.22 × 10⁻¹⁶**. Every core integral equals the retained fraction inside ±5.
- All **42 CSV rows / 462 numerical fields** exactly match the independently checked retained data.
- Verified **24 complete ROOT file hashes**, case identities and retained source/configuration hashes.

The largest observed absolute pulls are:

| Quantity | Maximum absolute pull |
|---|---:|
| d0 | 531.113 |
| z0 | 631.429 |
| phi | 759.690 |
| theta | 578.950 |
| q/p | 1,353.964 |
| time | 0.131151 |
| derived pT | **806,908.415281** |

The extreme pT value remains in the full histogram and moments. No additional quality, residual or tail cut was introduced.

**Identity and time checks**

The same three native Fake partial fits remain included: Geant4 1 GeV event **2129**, Geant4 100 GeV event **27**, and Fatras 1 GeV event **17622**. I rechecked their unique selected-primary/candidate association, zero native barcode/Fake sentinel and finite contributions to all seven quantities.

Pinned ACTS `RootParticleWriter.cpp:133–140`, `RootTrackSummaryWriter.cpp:454–493` and `Units.hpp:26–35,83–85,118–126` establish compatible native time coordinates: **ct expressed in mm**. Generated time is zero throughout. Fitted time sigma is approximately **2,997.925 native units**, about **10 ns**. Its narrow pull distribution is a seed/fitter-prior diagnostic, with no timing measurement; the source, README and figure labels correctly state this.

**Presentation and controls**

All six PNGs were visually inspected at original resolution. They clearly overlay **1/10/100 GeV**, integrate **−4≤eta≤4**, label the pull sign, distinguish core/full ranges, show omitted-core fractions and identify time as unmeasured. Full views visibly retain sparse extreme tails. The N(0,1) curve is accurately presented as a reference.

All **four analytic histogram controls** passed. Portable read-only source/cohort/training/count/normalization audits also passed. Earlier numerical profiles, figures, native source, campaign, digitization, reports and frozen error table are unchanged from **`f7b14c60c8be613ce9165684d6ef03007ce1a456`**.

The previous material-locality, ideal-response, truth-seed, training-provenance and omitted-uncertainty qualifications remain. Full SDs remain finite-sample tail diagnostics; these plots establish neither Gaussian widths nor detector acceptance.
