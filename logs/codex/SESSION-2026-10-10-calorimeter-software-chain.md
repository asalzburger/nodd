# SESSION-2026-10-10-calorimeter-software-chain — Calorimeter software-chain usage

## Scope and evidence

Retrospective token-only record for eight closed research and prototype turns
on 2026-10-10, from 2026-10-10T04:50:41Z to 2026-10-10T08:40:14Z UTC.
On 2026-10-12 the user requested a separate PR accounting the recent calorimeter
software-chain work. These entries were already included in main via PR59,
but grouped with material-tool work in a general desktop backfill record.

The [dated accounting inventory](../usage/USAGE-2026-10-12-calorimeter-accounting.json)
records the move from that owner and references the unchanged original recovery
inventory. Every counter and request digest also matches a fresh read-only
usage recovery. No private conversation/model state or local client path retained.

## Selected work and exact counters

The user requested a reconstruction/particle-flow plan, ActsExamples execution,
and manageable prototype PRs. The observed work covers research, framework
feasibility, foundation, seeded clustering, jets and EDM4hep input/persistence.
Software deliverables are [ACTS PR4](https://github.com/asalzburger/acts/pull/4),
[PR5](https://github.com/asalzburger/acts/pull/5),
[PR6](https://github.com/asalzburger/acts/pull/6),
[PR7](https://github.com/asalzburger/acts/pull/7) and
[PR8](https://github.com/asalzburger/acts/pull/8).

| Closed task turn | Input | Output | Total |
| --- | ---: | ---: | ---: |
| Research plan for nODD calorimeter reconstruction and particle flow in ACTS | 3,484,215 | 16,995 | 3,501,210 |
| ActsExamples framework feasibility for the nODD calorimeter prototype | 290,190 | 2,005 | 292,195 |
| nODD calorimeter foundation in ACTS, asalzburger/acts PR4 | 4,069,072 | 30,969 | 4,100,041 |
| nODD seeded calorimeter clustering in ACTS, asalzburger/acts PR5 | 3,403,714 | 23,378 | 3,427,092 |
| nODD calorimeter FastJet jets in ACTS, asalzburger/acts PR6 | 2,988,047 | 24,854 | 3,012,901 |
| nODD optional calorimeter EDM4hep IO preparation in ACTS | 3,607,585 | 34,559 | 3,642,144 |
| nODD calorimeter simulated-hit IO in ACTS, asalzburger/acts PR7 | 2,890,740 | 13,707 | 2,904,447 |
| nODD persistent calorimeter clusters/jets in ACTS, asalzburger/acts PR8 | 7,148,740 | 48,753 | 7,197,493 |
| **Observed subtotal** | **27,882,303** | **195,220** | **28,077,523** |

Cached input: 27,035,136; reasoning output:
69,214. Both are subsets, not extra usage.

## Ownership and validation

Eight complete original usage entries are transferred byte-for-byte in value,
including stable thread/turn IDs and source descriptions. The former owner keeps
the two material-tool turns. Imports passed dry-run before writing. All five
project totals are preserved; the observed project subtotal remains 552,937,331
across 183 disjoint turns. No part of a turn is divided by estimated task effort.

## Limitations and follow-up

Only confirmed calorimeter research/development turns are included. October 12
accounting/dashboard work and this active accounting turn are excluded from
this development subtotal. Actual model/client version and other project gaps
remain unknown. No scientific source, approval, dependency or dashboard code
changes. Git start revision describes this bookkeeping checkout; original
software history remains in the linked ACTS PRs. Validation is accounting only.
