# SESSION-2026-09-30-baseline-recommendation — Next tracker working baseline

## Scope and selected request

User asks for a recommendation from PR #28 and says larger silicon area is no
longer a concern at this stage. This is design advice, not an instruction to
integrate geometry or record human approval. Starting revision and four unrelated
untracked usage files are identified in the paired JSON and preserved.

## Recommendation and evidence

Recommend the exact validated original-pocket control,
`p190-s680-b1-l1287.33-front_loaded-original-pockets`, as the next working baseline.
This is a proposed NODD DESIGN CHOICE, with no human approver recorded.
Source: [DES-011 results](../../docs/validation/DES-011-service-constrained-optimization.md)
and [PR #28](https://github.com/asalzburger/nodd/pull/28), observed at
`17ae47f6d18e132eb539f30ef8323114963f8588` with no new comments.

It has197.250m² physical silicon,9.0182mean usable stations and1009.57mm
worst-mode p95 maximum inter-station gap. Relative to PR25 it adds9.60% mean
stations and reduces that gap statistic26.77%. Compared with the compact coverage
candidate it sacrifices0.635% mean stations while retaining more routing depth
and avoiding increased zero-hit fractions in every measured structured/random
eta bin. This does not prove pointwise non-regression or continuum hermeticity.
The area candidate is not preferred because its extra silicon does not improve
these coverage/gap metrics. The spacing candidate fails the frozen coverage gate.

Retain the unshifted barrel radii, front-loaded discs, constant trunks44/73/25mm,
original service pockets and inherited23-row long-strip pitch including the
central row. Keep exact inherited modules/staggering/local tilt; no new inclined
section. Retained layout inspection confirms pixel radii34/60/106/182mm,
short-strip260/340/480/660mm, long-strip840/1060mm; positive first-disc centres
611.7/1295.5/1403.65mm. Existing long-strip local module tilt is12degrees, distinct
from an inclined barrel section. Original-pocket baseline retains the tested
last-disc bypass. A simpler no-bypass variant is a follow-up proposal, requiring
matched dense/native validation; the paired training-only evidence must not be
presented as a validated hybrid baseline. Focus follow-up on physical service
engineering and local acceptance weaknesses before further mean-hit optimization.
Conservative/stress budgets, connectors, bends and vessel access remain open.

## Validation and changes

Read current PR metadata, governing design/report and retained layout; computed
relative comparisons from reported numerical values. No ACTS runtime or new
physics tests used. Only this paired discussion record is added locally; production
geometry, design lifecycle, review approval and tracking state remain unchanged.
Final session-log and dashboard checks are recorded in the paired JSON.

## Token accounting

Exact client-reported counters are unavailable, so usage remains empty. Historical
project summary totals do not measure this task. No usage observations duplicated.
