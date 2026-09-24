# SESSION-2026-09-18-stepped-endcaps

## Selected user request

“Break the paradigm that endcaps need to start at barrel length, allow stepped
muon endcaps and redraw the designs.” Scope: PR #6 comments on growing gaps
and stepped hosts, not the other open magnetic-performance review questions.

## Outcome and decisions

DES-004 now defines two endcap sections per candidate. Narrower upstream hosts
start at 6.35 m (inner-solenoid family) or 6.95 m (outer family), then widen
downstream. The JSON carries explicit independent coordinates. Trial 0.15 m
interfaces and retained 0.40 m aperture are unsigned project choices. Eta=3.5
rays enter inner-family hosts at about 6.617 m, later than the new front.
Updated six cards, both interface memos, summary, main design, input JSON,
prototype plotter, checks report and all seven PNG/SVG drawings. Prior rectangular
artifacts remain traceable in Git. E1-R2 and TDR are unchanged.

## Verification and provenance

Commands and results are in the paired JSON. Four new prototype tests and the
11 envelope/15 documentation tests passed. All six layouts have no positive
rectangle intersections. Drawing inspected. Initial whitespace check found SVG
trailing spaces; the generator now normalizes them, and the repeat check passed.
Source hashes and tool versions are recorded in the regenerated report. No new
external facts or sources were added. Exact token counts are unavailable.

## Review and limitations

Recorded the actual adverse review at revision 71f1cab, with reviewer identity
and GitHub evidence. No approval inferred, no review threads resolved. End-return
structure, services, shielding and stations still require shared allocations;
these drawings do not validate magnetic fields or performance. No baseline issue
until human selection. The review's other requests remain outstanding.
