# SESSION-2026-10-14-pr75-transition-question

## Scope and authorization

User asked to answer the review question on PR75 and propose actions if needed.
This authorizes a response on the PR. Starting clean overview revision:
25ae7f2c93f267882702049a92a1b2568c903e39. No geometry, new package, design sign-off
or prototype PR is requested by this question. Reply and proposed follow-up are
bounded separately from implementation.

Review question (verbatim), asalzburger-review, 2026-10-14T07:49:23Z:

> Why does the ALLEGRO style barrel need a spacy gap between LAr Barrel and Endcap - and why is this not necessary for the Si-W prototype?

https://github.com/asalzburger/nodd/pull/75#issuecomment-6163562396

## Evidence and role assignment

Existing DES032/services and DES034 source arithmetic are inspected at pinned
revisions; a bounded SysArch comparison checks route/topology interpretation.
Primary evidence is existing prototype software/documents; no native geometry
or engineering qualification is inferred. Current exact token counters are
unexposed, so usage remains empty and unknown.

## Prepared PR75-GAP-SysArch-review

```json
{
  "id": "PR75-GAP-SysArch-review",
  "role": "SysArch",
  "input_revision": "25ae7f2c93f267882702049a92a1b2568c903e39",
  "inputs": [
    "docs/layouts/review/brief.json",
    "docs/layouts/review/layout001.json",
    "docs/layouts/review/layout002.json",
    "docs/design/DES-034-siw-service-envelopes.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Answer the human PR75 question: why does ALLEGRO-style LAr barrel have a large barrel/endcap gap while Si-W does not? Read the exact sources in sources.json (LAr DES032/services.json/services.py at48e97256f8badd75c022a84ab1c4ff71977c56a2 and DES033 at72d37ee9a56182e4ba974791a848a738c19cf092). Distinguish intrinsic cryostat/services from a selected nODD routing allocation, check the100mm jacket S-bend arithmetic and assumed start radius, compare SiW exterior annulus/400mm rear gap/30mm installation seam, and assess practical proposed follow-ups for reducing the LAr transition. Do not prescribe conclusion: flag unsupported or asymmetric claims. No new geometry, native jobs, edits, installs, external posts or further delegation. Your prior Si-W input is disclosed; this is a bounded comparative assessment, no human approval.",
  "deliverable": "Compact cited facts and action recommendations for the coordinator response, with exact source/revision and limits.",
  "completion": "Review question explained with justified allocation comparison, identified missing route proof and bounded next actions; no unverified technology necessity or performance claim."
}
```

## Assessment and response

PR75-GAP-SysArch-review (/root/siw_services_sysarch) assessed25ae7f2 read-only,
with earlier Si-W input authorship disclosed. The selected LAr100mm jacket
S-bend is739.403mm for293.7mm radial shift,400mm bend radius,20mm clearance
and100mm OD.80mm jacket gives638.216mm; rear100mm quarter-turn requires470mm.
It independently confirmed the missing utility-specific start/port premise:
services.py uses the N2 radius for both jackets.800mm is chosen routing space,
not an intrinsic technology minimum. Si-W's30mm seam is installation-only;
its corresponding external/rear budget is300mm annulus/400mm rear break.
Physical cold/warm closures are already inside the package bounds. No native,
engineering, load/thermal/response job, edit, external post or sign-off by child.

Root added a small clarification to Si-W/LAr overview paragraphs and regenerated
the same four-page PDF. A retained input note records pinned calculations and
proposes actual feedthrough/collector endpoint design, comparison of front vs
side/rear routes, then geometry/transition/collar/FCal checks before reducing the
reservation. No detector geometry or prototype input changes. Selected future
work is proposed, not implemented or approved. The reply will be posted to the
review discussion after checks; the PR body remains exactly common-source text.

## Actual checks

Independent arithmetic and primary-source inspection reproduce739.403mm LAr
S-bend and245mm chosen Si-W single turn; the two have different topology.
PDF builder:4 pages,75 common blocks,16 unique public links. Latest rendered
four pages were inspected with no clipping/glyph/overlap issue; images unchanged.
A lookup of a guessed DES032 input filename failed (not present); the actual
pinned DES032 and services.json/services.py were then read. No source invented.

## Token accounting and open work

Current parent/child completed-turn counters remain unexposed; usage is empty,
unknown rather than zero. No native checks or geometry tests were needed for this
bounded reply/documentation clarification. Proposed service-interface redesign
requires a separate prototype change, actual routes and review.

## Publication and closeout

Published reply:
https://github.com/asalzburger/nodd/pull/75#issuecomment-6163783411

Clarification/source note committed at84c565a2134884cabd790eff159f55af7d6828c2
and pushed ordinarily. The GitHub description exactly equals retained common
Markdown after updating. The PDF remains4 pages/75 matched blocks/16 links;
all12 pinned sources and2 exact layout snapshots match. Latest PDF SHA256
1aedcd496fa72f3c9a4e81e3eb5f88fc0fd21cfdc807bebc9a2806c6d8cd7aa2;
Markdown SHA256f129b3a9a3e8a234a3439c8cdb6348639bdf91e2e590b93d9cdde358a84f97b4.
Root inspected all four fresh page PNGs. No native job, geometry change, additional
prototype PR, external package or human sign-off. Further route optimization is
proposed in the response and project next_action, not silently implemented.

Existing observed usage remains210 disjoint turns:620,754,236 input +3,545,169
output =624,299,405 total, with cached/reasoning counters as subsets. The current
turn has no exact exposed counters and no estimate or duplicate observation is
added. Journal/project/token-site validation and summary are run at closeout.
