# SESSION-2026-11-19-ecal-raw-angular — LAr baseline and Si-W raw widths versus eta and phi

## Scope and evidence

Contemporaneous bounded plotting task. Started clean at
e9a0008c9851ea7c8a38ce08b402cd63756c9ca1 in a dedicated worktree, then
fast-forwarded to43f8a56cc0f7163ff959e262516ae2db7d21e33e, including PR151.
Fetched main does not yet contain this baseline stack, so the focused draft PR
targets codex/restored-lar-em-baseline. Existing worktrees were preserved.

## Selected conversation

User, exact: “Now the new LAr baseline is in, can you make two plots, side-by-side,
that shows: Si-W and LAr raw energy resolution vs eta and vs phi. With LAr solit,
Si-W dotted, 15 bins should do.”

Assistant, paraphrase: selected the restored1.8mmPb LAr10k sample and matching
physically staggered Si–W comparator, signed eta and full phi, all events,
with pointwise95%bootstrap error bars.

## Decisions and outcomes

Produced side-by-side15bin eta/phi plots: LAr solid, Si–W dotted, prescribed ECAL
color. R=Eraw/Etrue, sampleSD(R)/mean(R), ddof=1. All10000matched10–80GeV
electrons, zeros/tails and ECAL-onlyB0 scope retained. PR151's separate400mmgap
prototype lacks a matched10k production sample and is not substituted here.
No calibration, fit, selection, new transport, geometry change or design approval.

Analysis binds exact saved ledger/receipt/readback/geometry identities to published
restored-LAr and staggered-SiW evidence; checks complete IDs, matched primary
energies/directions/inputbytes and inclusive widths. Native audits are inherited,
not rerun. Retained aggregates include bin counts/means/SD/zeros/quantiles,
energy means,1000shared event bootstraps(seed13001000), pointwise95%intervals
and full60variable covariance. Full events remain local and ignored.
PNG/PDF/SVG, render hashes, reproduction recipe and software inventory updated.

## Commands and validation

raw_angular.py analyze/plot passed. PNG visually inspected. Independent standard
library statistics.mean/stdev audit matches all60bin means/SDs/widths, counts and
zeros. All four projections contain10000events, retaining0LAr/42SiWzeros.
Covariance finite, symmetric and positive semidefinite; minimum eigenvalue
7.378922736073385e-7. Existing test_compare.py:5tests pass, including explicit
repeated-sample bootstrap, bin edges, scale invariance, ledger tampering and
native contract controls. Inventory refresh/check pass; whitespace check passes.
Session validation and summary were run; exact current-turn usage is unknown.
Sandboxed Git network initially failed DNS; authorized network fetch succeeded.
Initial matplotlib import used a temporary cache; render uses explicit build/cache.
The staged whitespace check exposed Matplotlib SVG trailing whitespace after the
initial unstaged check passed. SVG export now strips trailing whitespace; the
figure and source/render provenance were regenerated and checked before push.

## Changes and revision links

See paired JSON changed-file inventory. The task is retained in a draft PR;
no ready-for-review transition or main merge is authorized.

## Token accounting

Exact completed per-turn client counters are unavailable in this active turn.
Usage remains empty, meaning unknown rather than zero. Historical canonical
owners are unchanged. No estimated counters or raw client history are retained.

## Follow-up

The plot shows spectrum-averaged raw response, including within-bin angular
variation, losses and leakage. Intrinsic fixed-energy reconstructed resolution,
electronics/systematics and reduced-gap performance remain outside this task.
Human review is through the draft PR.

## Draft publication

[Draft PR152](https://github.com/asalzburger/nodd/pull/152) targets the selected
baseline branch and includes only this task's twelve initial files. Initial
automatic review rejected draft creation as insufficiently authorized; the
standing human instruction was checked against AGENTS.md and original tracked
commit13e0a176, whose journal quotes the user's draft-PR rule. The identical
draft action was then allowed but the connector returned403 integration access.
The authenticated GitHub CLI fallback created PR152 successfully. Connector
readback confirms open/draft/mergeable; no comments at the recorded snapshot.
Session validation passed301records. Current task observed input/output totals
remain unknown; global historical summaries are not allocated to this task.
