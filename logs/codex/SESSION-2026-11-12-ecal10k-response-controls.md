# SESSION-2026-11-12-ecal10k-response-controls — Underlying response distributions

User, exact quote: “Do you have the control plot from which the sigma/RMS was drawn ?”

The original PR134 widths came directly from unbinned R values in the retained
event-summary ledger, rather than histogram or Gaussian fits. The mean-response
control was already saved; per-bin population histograms were not. The assistant
stated that distinction and rendered the exact original populations for all ten
|eta| bins and ten signed folded-phi bins.

Starting revision: e0819163d93a936a63fb73b720bf3052899a92f5. Existing draft PR134
was verified open at that revision. The event-ledger SHA-256 matches the published
readback record. This small, tightly dependent visualization task stayed with
the main agent under the repository review/validation workflow; no independent
review or new simulation is claimed.

Every panel shows N, zero count, mean, sample SD (ddof=1) and SD/mean. Forty common
display bins span 0–2 percent response and retain every event. All twenty
unbinned moments and population/zero counts agree with the original summary at
the checked tolerances. The histogram shapes, including the seam-adjacent
low-response component, are retained without fitting, calibration or cuts.
The original summary and width figures are unchanged.

Added a reproducible controls script, two ten-panel PNG/PDF sheets and compact
histogram counts/edges. Updated report, existing task/inventory and this paired
journal. The full event ledger and ROOT sample stay ignored and local. Plotting
uses the existing ACTS Python with NumPy/Matplotlib; no dependency installation
or native runtime activation was needed. Both sheets were visually inspected.

The new controls match all 20 published means, sample SDs and fractional widths.
The task journal/interaction records and repository validators are synchronized
for the existing draft PR134. Only recipes, figures and binwise statistics are
published. No detector/engineering approval or new physics outcome is claimed.

Exact parent per-turn counters are not exposed; usage remains empty. Historical
journal totals are not attributed to this task, and no counts are estimated.

## 2026-11-12 accounting reconciliation

Exact closed-turn counters and selected app-visible task/assignment evidence were recovered into this original owner, using the chain inventory at `logs/usage/USAGE-2026-11-12-ecal-chain-readiness.json`. Earlier missing-counter statements describe the prior collection, not this correction. Cached input/reasoning are subsets; shared PR links are references, never allocations. No active coordinator usage or estimated counters are imported.
