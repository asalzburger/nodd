# SESSION-2026-10-14-ecal-review-envelope-update - reviewer entry parity

## Scope and user direction

User directed an additional LAYOUT-001 service/cooling/HCAL-routing/FCal envelope
PR, then an update to the central overview and existing PR75. This companion
record covers the overview synchronization only; DES034 prototype work has the
distinct SESSION-2026-10-14-siw-service-envelopes pair. Exact current counters
are unexposed for both scopes, not allocated or estimated.

Starting overview head was 0ef45de107ece197291c0df5e1f9bb0fca4c405f, clean.
An ordinary merge imports the additional prototype branch at
78cfa3fe8ac56e4b48a11870ca2758bdae25ed6c (PR76). Tracking conflict was reconciled
three-way by stable record IDs: retain PR75/task/session and PR69/72 merge
metadata from the overview, and append DES034/task/report/session/CI controls
from the envelope branch. Both contributions are retained, no force-push or
approval inferred. Result has 66 tasks and 36 documents, 21 review rounds.

## Common overview changes

The LAYOUT-001 snapshot now pins PR76 at78cfa3fe and includes its external
annulus, rear HCAL radial egress and empty FCal reservation. The same common
JSON regenerates the Markdown PR body and four-page PDF. Both RZ views use
same axes; Si-W now shows cyan service and red future-forward space like LAr.
The HCAL bounds and relative-volume comparison use the amended Si-W outline:
LAr total HCAL envelope volume is x1.43 of this version, rather than x1.77 of the
prior version. ECAL model masses and isolated component coverage are unchanged.
Partial Si-W power-feed Cu/water estimates are identified separately from native
ECAL mass and from missing other cables/supports.

## Artifact checks

Existing PDF skill applied to edit the same four-page artifact, with the required
operation marker before regeneration. Existing bundled reportlab/pypdf/Pillow and
LiberationSans fonts reused; no externals installed. Generation checks four
pages, 75 common prose/table/caption blocks and 16 unique hyperlinks. All four
latest Poppler-rendered PNG pages were visually inspected and fit without
clipping or glyph errors. The final source/hash checks and PR-body exact equality
will be run after role reconciliation and publication.

## Roles and remaining limits

Root authored the synchronization. A PubDoc delta assessment follows a frozen
commit; existing source authorship is disclosed. PhysVal assesses the DES034
prototype in its separate contract/session. Neither supplies human engineering
sign-off. Local collector/ports, actual balanced routing, pipe/connector packing,
support loads, complete field/response and forward hardware remain unresolved.

## Token accounting

No current parent/child completed-turn counters are exposed. Existing observed
input/output totals and missing coverage will be reported from session summary;
this task's usage remains empty and unknown.

## Prepared SIW-PARITY-PubDoc-delta

```json
{
  "id": "SIW-PARITY-PubDoc-delta",
  "role": "PubDoc",
  "input_revision": "6c99721c01096c87244db38bf1307b8299ab83f0",
  "inputs": [
    "docs/layouts/review/brief.json",
    "docs/layouts/review/ecal-layout-review.md",
    "docs/layouts/review/ecal-layout-review.pdf",
    "docs/layouts/review/content-check.json",
    "docs/layouts/review/sources.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Assess only root-authored parity-update delta to the existing reviewer overview: new SiW service/HCAL/forward reservations linked to PR76, changed HCAL extent/volume comparison, partial material estimates and paired RZ views. Check concise same four-page Markdown/PR/PDF correspondence against pinned DES034 and retained inputs; no TDR expansion or claim of engineering/FCal acceptance. Your prior brief authorship is disclosed; this is assessment of the root-authored delta, not independent approval of your prior source content. Exact committed sources, no dirty substitutes. No edits/native jobs/installs/PR actions/delegation/sign-off. Return concrete findings and checked revisions/locators/limits.",
  "deliverable": "Bounded claim/source/version and four-page parity delta assessment to root for the session record.",
  "completion": "Material correspondence/scope/format issues identified for changed content and exact four-page source; no approval claimed."
}
```

## PubDoc delta result

SIW-PARITY-PubDoc-delta, /root/layout_main_page, reviewed6c99721c01096c87244db38bf1307b8299ab83f0.
No material correspondence/format defect. All12 source bindings and2 snapshots,
both SVG reproductions and embedded image pixels match. Four pages/75 canonical
blocks/16 links agree with retained Markdown and checker. All pages rendered and
visually fit. Independently recomputed Si-W443.936120m3 vsLAr634.774425m3 HCAL
outline, ratio1.42987785. Its earlier base-brief authorship is disclosed; no
independent re-approval of that text, native job or sign-off.

The391-word page4 exceeds the earlier350 drafting target, but this updated
four-page brief stays concise and legible; the user imposes four pages, not that
initial drafting target. Retain the added space/support budget context.

Following PhysVal's DES034 P2/P3, source pins move to0a26796518d690bf26934d2864d63ecad7582675:
feed lengths are consistent, reporting precision is declared and negative-control
wording is accurate. Overview geometry/mass/cross-section claims do not change;
partial Cu/water remain0.918/1.005t. The old78cfa3fe source remains historical
review provenance, not the final service report source. Ordinary follow-up merge
retains all prototype corrections.

## Closeout and validation

DES034 P2/P3 closure was completed read-only at0a267965; exact service source pins
were updated without changing the overview's geometry/partial-mass numbers.
The final PDF remains4 pages/75 common blocks/16 public links; all12 source
bindings and both layout snapshots match. Latest PDF hash
2d00dbe00e61a71eec444389c695fcf93e7308b7b4516be8e5a3f54a32d38910;
Markdown hashfa0c551b437d75cac87bc2b4521e3af01bf2213ca7eddc5f1c8fc80c2f9993f5.
Latest four Poppler-rendered pages were inspected cleanly. No new dependency.

Existing branch contribution was integrated through ordinary merges, preserving
separate session pairs, prototype evidence, PR75 and its prior merge metadata.
PR75 is made dependent on PR76 for a documentation-focused diff; review/merge
PR76 first. No human merge/sign-off performed. Exact remote PR-body parity is
verified after the final push; CI pending statuses are not preclaimed.

Project/session/token-site checks passed:66 tasks/36 documents/21 review rounds,
182 paired session records,210 disjoint dated token turns. Observed620,754,236
input +3,545,169 output =624,299,405 total. Cached599,210,880 input and1,177,538
reasoning output are subsets. Current two task records have no exposed usage;
64 session records lack observations, and no totals were estimated or duplicated.
