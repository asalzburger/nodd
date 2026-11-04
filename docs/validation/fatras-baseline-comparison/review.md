# Independent PhysVal assessment

- Assignment: FATRASBASE-PhysVal-02.
- Date: 2026-11-03.
- Reviewed evidence/source revision: 795f7861c61abfe9ee69302162f69b8f60dffd62.
- Native execution source: 326fed57a3c3aa75466756f47cee2e69d5d22b9b.
- Reduction source: 14340803427eca12f75b76bb678be407366ad7a5.
- Outcome: no material delivery blocker for qualified PROTOTYPE characterization.

The separate PhysVal agent received the explicit role mandate and a bounded
read-only assignment, recorded in the
[session journal](../../../logs/codex/SESSION-2026-11-03-baseline-fatras-resolutions.md).
It reviewed pinned source/data/report/figures and the local full ROOT samples.
Scientific files matched the target commit; only coordinator journal files were
dirty. The coordinator curates this assessment; it grants no human acceptance.

Actual independent checks reported:

- Eight focused tests passed.
- Reproduced 29,108 scalar statistics exactly from all eight raw samples:
  counts, all seven residual/pull diagnostics, global summaries, eight absolute
  eta bins and 32 signed eta bins.
- Exact old/current generated-event pairing and 224 primary/common-fit ratios
  confirmed. Independently replayed four complete 400-replicate paired-bootstrap
  intervals; assessed the remaining algorithm and valid-replicate accounting.
- Accounted for 160,000 generated/159,985 finite fits. All 15 losses are selection
  losses; no attempted-fit failure or invalid covariance. One old 1 GeV guarded
  zero-barcode partial fit remains included. At 100 GeV, 467 old/419 new wrong-charge
  fits are retained.
- Verified all 4,021,739 measured-coordinate variances against frozen errors.
  Independently reproduced current 107 training groups/94 coordinates and old 106
  groups/90 coordinates, including cluster overflow treatment.
- Rehashed 58 ROOT outputs (56 performance plus 2 training). Checked sources,
  configuration, maps, calibration and actual factory/observer/portal/runtime
  binaries. Old 1/10/100 GeV truth and all five fitted parameter branches exactly
  reproduce frozen references.
- Inspected all six PNGs and verified 18 PNG/PDF/SVG artifact hashes plus plotter
  and data hashes. Profiles SHA256:
  `ef80eb12412962be09901df25637676eaf97e57cb59bdff08e9df45ec77fa395`.

The earlier absent-variant shared-reader condition is resolved by explicit
source/baseline checks and an unconditional calibration audit for every case.

The report accurately describes mixed findings: central d0 narrows, while
central relative-pT cores widen. Forward 100 GeV current residuals have a narrower
core but substantially larger full RMS; this qualification must accompany a
summary. Conditional finite-fit populations, pointwise sampling intervals at
fixed maps/errors, ideal truth seeds, simplified response and material
locality/one-phi-bin/CSG approximations limit interpretation. No isolated
service/pitch effect or pattern-recognition performance is established.

The reviewer did not replay every bootstrap interval or rerun native transport;
no files were edited. This is an independent agent recommendation, not detector
design sign-off, engineering approval or performance acceptance. Subsequent
changes add this record and closeout metadata; scientific source, profiles and
plots remain identical to the reviewed revision.
