# DES-034 - LAYOUT-001 Si-W service and forward envelope prototype

- Status: **DRAFT**
- Type: **PROTOTYPE**
- Date: 2026-10-14
- Human direction: bring LAYOUT-001 service/cooling/HCAL routing and prospective FCal envelopes to the same allocation level as LAYOUT-002; update the central reviewer entry.
- Parent: DES029 layout outline, open Si-W DES030/031; comparison DES032/033.
- Engineering, magnetic and performance approval: pending.

## Scope and evidence

This isolated envelope study retains the open Si-W ECAL package, local sensors,
supports, readout and cooling plates. It adds named external collection, routing,
access and forward reservations and adjusts the rough HCAL envelope to contain
them. It is not a redesign of the cassettes or a detailed HCAL/FCal detector.
Production geometry is unchanged. Source revisions are retained in
[DES-034-sources.json](inputs/DES-034-sources.json).

**FACT:** DES031 records 188.401 kW continuous barrel heat and 9.014 kg/s ideal
water at a 5 K rise, 92,135,424 logical channels, 15,648 shared interfaces and
46,944 local Ti/water pipe runs. It explicitly excludes external headers,
connectors and routed cables and warns that current side/end reservations contain
absorber/support. DES030 provides the corresponding endcap inventory and limits.
These are facts about unsigned earlier prototype choices, not operating approval.

**NODD DESIGN CHOICE:** retain continuous power as the planning case; a low duty
factor is not assumed. Reserve an external route rather than declare existing
material-filled cassette setbacks empty. Define station counts, cable and water
cross sections, bend/access clearances, nominal/adverse scenarios and interfaces
before selecting HCAL bounds. Forward insertion is technology-unassigned and
empty, with no active coverage claim. Quantities and validation follow the
bounded SysArch assessment and reproducible allocation tool.
