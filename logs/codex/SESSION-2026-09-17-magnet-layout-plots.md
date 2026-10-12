# Global solenoid layout drawings and PR executive summaries

## Request and scope

User requested global system r–z plots for the two solenoid options in PR #6,
and an executive summary in every PR description. Work is on the existing
`research/magnetic-configurations` branch; initial tree was clean at `be231e0`.
This is a DES-004 illustration/proposal update, not production geometry work.

## Outcome

Added reproducible individual MAG-01/MAG-03 drawings and a matched-scale combined
PNG/SVG view with tracker, calorimeters, muon hosts and detached forward calorimeters.
MAG-03 shows the documented 4.30–4.80 m outer-coil reservation, 4.95 m muon inner
radius, historical 4.35 m boundary and unused inner-coil allocation. Baseline
DES-003 JSON is unchanged. Reused its validation/intersection functions; recorded
coordinates, hashes, versions and commands in the new layout report.

Updated DES-004, tool README, dashboard evidence, AGENTS.md and PR template.
Executive-summary convention applies to every PR, including chores, and requires
keeping the summary current. Existing architect input supplies all dimensions;
no new external provenance or physical parameter was introduced.

## Validation

Generation passed: both allocations have no positive rectangular intersections,
and both current sheets lie inside the respective coil reservation. Visually
inspected the combined drawing. Envelope tests: 11 passed. Documentation/logging
tests: 15 passed. Dashboard records validated and preview built. These checks do
not establish physical clearance, material, station coverage or service capacity.

## Delivery and limits

Update the existing draft PR #6 with plots and executive summary. No design
selection, sign-off or production change is made. Unresolved supports, services,
shielding and return systems are explicitly omitted in figure captions.
Exact token counts were not exposed; none are estimated.

Delivered drawings in `92264b308d828bc693a5f6c0ad3859abec18f55a`; pushed to PR #6 and updated its description
with an executive summary and commit-pinned inline comparison image. Refreshed
the pending review target to this design revision; no approval recorded.

## Resource synchronization — 2026-10-07

The authorized cleanup imported 1 exact completed turn(s), after dry-run validation, into this canonical owner. Earlier narrative and original inventory sources remain intact; pending/unknown token statements above are historical and superseded for these observations only.

| Client turn | Input | Cached input | Output | Reasoning output | Total | Requests |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 01a0afca-ced1-7822-9b7b-89dfd65a3139 | 1457667 | 1432704 | 8465 | 1232 | 1466132 | 12 |

Persisted turn/usage ordinals, request counts, timestamps, verified usage-event hashes and original recovery sources are retained in [the synchronization inventory](../usage/USAGE-2026-10-07-synchronization.json). Each turn is counted once; cached input and reasoning output are subsets. No scientific input, execution hash or approval state changed. The current cleanup turn, explicitly excluded illustration/history turn and unassigned historical/internal review turns are excluded; this is partial project coverage, not billing.
