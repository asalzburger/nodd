# SESSION-2026-11-19-ecal-sector-padding — Full folded sector with display margins

## Scope and evidence

Follow-up to draft PR152, clean source f121349eb99cfb94b5e2ec4c6bc8c7c8d49733c8.
Same source-bound restored-LAr/staggered-SiW10000electron ledgers, geometry and
raw width observable. No new transport, runtime installation or detector change.

## Selected conversation

User, exact: “Sorry, I was not clear: show everything folded into Si-W sector,
but with +15 % of sector with on each side”.
Assistant, paraphrase: one complete folded SiWsector with15%of its full width
added on each side; display−65…+65percent, repeat the boundary regions, eta unchanged.

## Decisions and outcomes

Current recipe is --sector-padding-percent15. All10000unique primaries/model
contribute once to15equal bins over one full sector[-50,+50]percent. The22.5°
period is the same reference coordinate for both models, not LAr symmetry.
The axis extends to±65percent (±14.625°); shaded margins show periodic copies
of the same15bin curve and error bars, with dashed boundaries at±50percent.
No extra statistical bin/event is introduced and no directional cut remains.
Copies reuse the same statistical estimates and are fully correlated. Shared
bootstrap remains1000whole-event replicates on the original10000IDs, seed13001000.
Eta bin records exactly unchanged. Shared y range expanded to include the full
SiWseam peaks and their intervals. SolidLAr/dottedSiW and ECALcolor retained.
Original full-phi and prior narrow-window evidence remain at named Git revisions.
No new calibration, fit, response cut or design sign-off.

## Commands and validation

- raw_angular.py analyze --sector-padding-percent15 passes frozen published
  source/geometry/ledger/receipt/readback and matched-primary checks.
- Independent degrees/nearest-sector/bisect plus statistics.mean/stdev audit:
  all30phi bin counts/means/SDs/widths/zeros agree; exactly10000unique events
  per model,0LArzeros/42SiWzeros, no exclusions. Eta bin dictionaries identical.
- Full60x60covariance finite, symmetric, positive semidefinite.
- test_raw_angular.py:3tests pass, including every-event-once full-sector
  binning independent of display padding, sector periodicity and invalid ranges.
- Existing test_compare.py:5tests pass.
- PNG/PDF/SVG regenerated and PNG visually inspected. Initial preview exposed
  shared-y clipping of newly visible seam peaks; plot now includes all intervals
  with an explicitly computed common maximum and a centred legend.
- Inventory refresh/check and Git whitespace check pass. Session/PR interaction
  validation and summary run at closeout. Current task usage is unknown.

## Changes and revision links

See paired JSON inventory; existing draft PR152 updated, no new PR or merge.
Recipe and aggregate/provenance files updated; full event files stay ignored.

## Token accounting

Exact active-turn counters/client identity unavailable. Usage remains empty;
observed task input/output totals are unknown, not zero. Historical owners stay
unchanged; no estimates or raw client history are retained.

## Follow-up

Spectrum-averaged raw response includes geometrical losses/leakage and within-bin
variation. Periodic margins are display repetition, not independent measurements.
