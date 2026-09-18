# SESSION-2026-09-18-inner-space-reallocation

## Selected request

The user requests reusing absent inner-solenoid space and asks the system engineer
to coordinate with subsystem engineers so new allocations respect their requirements.

## Coordination and outcome

System Architect discussed tracker/calorimeter requirements directly with their
agents; muon engineer conditionally concurred. Recommended MAG-03/04/06 ECal
barrel1.30–1.66m, endcap outer1.66m, HCal barrel1.76–4.20m. Tracker and service
bounds, axial coordinates, HCal endcaps, outer magnet and stepped muon hosts stay
fixed. ECal depth is preserved, HCal assembly capacity grows400mm. ECal endcap
radius changes to avoid overlap with inward HCal. Tracker growth and compact
outer-coil alternatives are documented but deferred. No baseline replacement,
human sign-off, production geometry or material prescription.

## Evidence and limitations

Coordinated memo: docs/design/inputs/DES-004-inner-space-reallocation.md.
Revised input JSON, plotter, three affected cards and current summaries, numerical
report and all comparison drawings record the optimized layout separately from
historical fixed-layout controls. New dimensions are unsigned project choices;
no new external sources. Report retains exact source hashes and tool versions.
Six allocation tests plus11 envelope and15 documentation tests passed. Dense
prompt-ray comparison found no reduced summed ECal/HCal host lengths; this is not
shower containment, service adequacy, sensitive coverage or a physical field map.
Material additions can change muon scattering/filtering and magnetic flux.
Exact token counts unavailable; no estimates recorded. No private model state.

## Delivery

Update PR #6 executive summary with coordinated allocation and regenerated images.
Other magnetic-performance review requests remain open. Baseline issue awaits
human layout selection. Commands/results and changed files are in paired JSON.
