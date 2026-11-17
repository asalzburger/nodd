# PR145 review response

User: "There,s a new review comment - address it and prepare the PR for merging."

Identified actual comment6951330371 by asalzburger-review,2026-11-17, on PR145. It records discussion with Michael Duehrssen and selects ALLEGRO-style LAr with400mm warm gap as the nODD baseline; requests one SVG comparing sigma(E)/E for ODD, original Si-W, physically staggered Si-W and fine-binned400mmLAr. Record this as attributed human working-baseline selection, preserving integration/engineering limits. No invented design lifecycle acceptance.

Started from report head2872b9cf in separate codex/pr145-review-response worktree. Actual mainf3ece1d6 contains only PR142; the other approved PRs merged into dependency branches. Ordinary local merges bring current side-branch ea7b7647 (including PR146 records and PR144 test correction) plus main into report source bc1c42be. No GitHub PR merged. Prepare existing PR145 against main, preserving approved stack and exact old source/results. Current task is the requested review response/merge preparation of existing PR145; no unrelated new PR or approval request is needed.

## Recorded assignment before dispatch

Explicit generic PhysVal role, not native profile loading.

```json
{
  "id": "PR145-PhysVal-comparison-contract",
  "role": "PhysVal",
  "input_revision": "bc1c42bee37c3eff43bdd56a8d8d2f55566e344d",
  "inputs": [
    "docs/publication/emcal-findings/build_report.py",
    "docs/publication/emcal-findings/README.md",
    "docs/validation/lar10k/summary.json",
    "docs/validation/lar-gap10k/summary.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Assess the new human PR145 comment https://github.com/asalzburger/nodd/pull/145#issuecomment-6951330371 selecting ALLEGRO LAr400mm baseline and requesting one SVG sigma(E)/E for ODD, nODD-SiW, physically staggered nODD-SiW and fine-binned400mmLAr. Determine truthful common observable/axis/cohorts from retained primary data, especially ODD and staggered data at historical3ebafd340b0e084c5e42e57123de115e3f489244 docs/validation/ecal10k/summary.json, ecal-staggering/results/summary.json, ecal-highstat/results/summary.json. Do not call broad-spectrum sigma(R)/mean(R) intrinsic fixed-energy resolution. Recommend how to show four curves, fine LAr bins and intervals without pooling incompatible calibrated/raw samples or inventing data. Independently inspect primary sources before current report conclusions. Identify missing data and whether ignored retained per-event inputs needed for equivalent binning. Baseline selection is an explicit human choice, not full service/collar engineering signoff. No edits, native/MC jobs or delegation. Return source locators and bounded recommendation; later implementation review will be separate.",
  "deliverable": "Short comparison contract: exact source objects, observable, axis/binning, cohort/calibration caveats and review risks.",
  "completion": "Stop when enough primary data is inspected to implement a scientifically honest four-curve SVG; no broad historical audit."
}
```

## Primary-source contribution and implementation

PhysVal comparison-contract contribution at bc1c42be closed with a defensible four-series contract. It independently verified all three ledger hashes and exact10000(event,E,eta,phi) identities; all60uniform0.05bins have136-189primaries. ODD is only odd-zero/e-/20GeV/c eta0/1/2,200events/point, with source5000-bootstrap intervals. Use saved H_GeV for LAr rather than A_GeV; keep all zeros and source cohorts distinct. No agent plots/edits/bootstrap/native work.

Root implemented source-bound rebinning from the three exact retained local ledgers, shared1000 whole-event bootstrap seed13001000, compact bin data and one ReportLab SVG. All prior fine LAr H bins/intervals reproduce. A swapped geometry ledger is rejected by a negative control before computation. No raw event payload committed and no new MC/calibration/fit. NumPy2.5.1 does derivation; preinstalled bundled ReportLab4.4.9/pypdf6.21.4 produce the SVG and PDF. No package installation.

Root records human LAr400 working-baseline selection with actual account/comment/date and reported discussion, not an invented second signature or lifecycle promotion. Selected target and old800mm combined-integration control stay distinct; no geometry/exporter/default dimensions changed. Layout pages identify the selection and retained drawing context. Main currently contains only142; ordinary report-branch merges preserve the approved side-branch143/144/146 stack. PR145 will target main, no GitHub merge performed.

Rendering exposed a clipped SVG y-axis label and one PDF page4 overflow; fixed the label transform and moved the existing startup paragraph to the Si-W page. Eight-page guard passes. Project validator caught fractional seconds in newly collected PR timestamps; corrected to its required UTC whole-second format without changing the validator. Old scientific receipts and design DRAFT states retained.
