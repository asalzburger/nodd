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
