# Candidate-specific muon envelope proposals

## Request

Bring the muon engineer and project coordinator together to adapt the muon
system envelopes for the magnetic setups. If one is chosen, create an issue to
update the baseline afterward. Current task covers proposals, not that later issue.
Starting tree was clean on `research/magnetic-configurations` at `6402353`.

## Coordination and outcome

The muon engineer authored the host and internal space budgets. The coordinator,
assisted by the System Architect role, checked common interfaces and agreed the
six-option table. Root integrated machine-readable proposals, report, drawings,
main design, summary, option notes and dashboard updates into PR #6.

MAG-01 preserves the reference. MAG-02/03 propose outer barrel radius 7.50 m;
MAG-04 10.00 m; MAG-05 9.00 m; MAG-06 8.85 m with a distinct return-coil reserve.
The expanded endcaps stop at absolute z=10.90 m, leaving an illustrative 0.30 m
gap to detached forward calorimetry. The initial coordinator suggestion of
11.00 m was reconciled to 10.90 m before retaining any generated proposal.
All dimensions are unsigned NODD design choices with documented rationale.

A new config/tool/report family preserves the earlier two-option drawings and
fixed-host flux screens. E1-R2 JSON, production geometry and TDR submodule are
unchanged. No baseline issue was created. The full muon host includes chambers,
magnet structures, supports and services; its entire volume is not sensitive.
MAG-06 nested reservations are counted within the host, not as extra mothers.

## Numerical and visual checks

Generated six individual plus a combined PNG/SVG drawing. Inspected the combined
view. All six proposed top-level layouts have no positive rectangular intersections;
main-coil reference sheets fit their allocations and internal radial budgets fit
without mutual overlap. Compared both specialist Markdown tables to the JSON.
Forward-gap arithmetic agrees for all expanded candidates. Existing envelope and
logging/documentation tests passed, and the dashboard validated and built.
No magnetic field, material transport, station efficiency or structural check ran.

The MAG-04 radial slot area and MAG-06 return-annulus arithmetic address the
previous space warning only under stated trial assumptions. They do not establish
field closure, saturation margins or performance. In particular, return structures,
measurements and services have not been shown to fit MAG-04/06's 9.0–10.9 m endcap
host. Further stepped/axial amendment may be needed and must remain explicit.

## Provenance and limits

New numbers are project choices and arithmetic inference; existing public source
locators provide context. No new external source, material specification or human
sign-off is introduced. Raw measurement counts/tokens were not exposed; exact
usage remains unknown. Commands and results are in the paired JSON record.
