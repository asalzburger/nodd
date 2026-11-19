# SESSION-2026-11-19-ecal-phi-sector — Restrict raw phi to a central sector window

## Scope and evidence

Follow-up to draft PR152, starting clean at3f270c4fc14b2689ebe5bbf67c1c474fc15f3993.
Uses the same source-bound restored-LAr/staggered-SiW10000electron ledgers and
raw observable as the original task. No native runtime or transport was rerun.

## Selected conversation

User, exact: “Make the vs phi restricted to a sector +/- 15 %”.
Assistant asked whether this meant ±15° about phi0 or ±15% of a sector width.
User confirmed, exact: “±15% of a sector width”.
Assistant, paraphrase: use central±15% of22.5°SiWsector width, equivalent to
±3.375°, pooling equivalent sectors; retain inclusive eta and15bins per panel.

## Decisions and outcomes

Added optional --sector-half-width-percent15 to the exact-source-bound analysis.
Phi is signed folded SiWphase,100*folded_phi/(pi/8), restricted to[-15,+15]percent.
The same coordinate is applied to both models; it is not LAr electrode symmetry.
No reflection or response-based selection. Phi retains3009matched events per
model and excludes6991outside the directional window. All selected zeros/tails
remain. Eta retains all10000events; every eta bin record is exactly unchanged.
Shared whole-event bootstrap still samples the original10000IDs before applying
projection masks, preserving correlations between inclusive eta and selected phi.
Fifteen points/panel, LAr solid/SiW dotted and prescribed ECALcolor retained.
Original full-phi figure/data remain at the starting Git revision; omitting the
optional window reproduces that analysis. Updated PNG/PDF/SVG, compact bin data,
covariance, hashes, README recipe and inventory. No detector/design sign-off.

## Commands and validation

- raw_angular.py analyze with --sector-half-width-percent15: exact published
  ledger/receipt/readback/geometry and primary checks pass; new statistics saved.
- raw_angular.py plot: PNG/PDF/SVG regenerated; PNG visually inspected.
- Independent math.degrees/nearest-sector/bisect plus statistics.mean/stdev
  audit: all30updated phi-bin means/SDs/widths/counts/zeros match; each phi
  projection has3009events. All eta bin dictionaries match the original exactly.
- Full60x60covariance finite, symmetric and positive semidefinite.
- test_raw_angular.py:2tests pass, covering equivalent-sector bin matching,
  central-window inclusion/exclusion, unchanged inclusive eta and invalid windows.
- test_compare.py:5existing statistical/identity/contract tests pass.
- Software inventory refresh/check pass. Git whitespace check passes.
- Session/PR interaction validators run at closeout; current per-turn usage
  counters unavailable, not estimated.

## Changes and revision links

See paired JSON inventory. Updated the existing draft PR152; no new PR or merge.
The original full-phi evidence remains in Git, linked from the updated README.

## Token accounting

Exact current-turn counters are unavailable; usage remains empty and totals
unknown. Historical canonical observations and their ownership are unchanged.
No client archives, hidden state or estimates are collected.

## Follow-up

This remains spectrum-averaged raw deposition width in the stated angular
windows and ECAL-onlyB0configuration. No fixed-energy reconstructed resolution
or interpretation of the common SiWphase as LAr symmetry is claimed.

## Draft publication closeout

Updated[PR152](https://github.com/asalzburger/nodd/pull/152) on the existing
task branch with commit3d782850b6de4b931ab0a756743f3ed1ace3475c. The connector
returned403on description update; authenticated ghfallback succeeded, following
the already established standing publication instruction. Connector readback
confirms the updated description, new head and draft status; no comments in the
recorded snapshot.302session records validate. Current task input/output totals
remain unknown, and historical totals are not allocated to this follow-up.
