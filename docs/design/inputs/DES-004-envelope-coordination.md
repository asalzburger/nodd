# DES-004 — Coordinated candidate muon-envelope amendments

- Date: 2026-09-17; status: DRAFT; numerical human approval pending.
- Roles: Project Coordinator and System Architect, reconciled with muon engineer.
- Scope: candidate space for research; no change to the DES-003 reference.
- Context: [DES-004](../DES-004-magnetic-configurations.md), [reference envelopes](../DES-003-global-envelopes.md), [architect input](DES-004-system-architecture.md).

## 1. Coordination decision

**NODD DESIGN CHOICE — proposed:** give all six magnetic options concrete muon
host reservations, allowing the overall detector radius to expand. These are
research amendments, not evidence that a particular magnet is buildable or that
the host is fully sensitive. A fixed E1-R2 outer radius must not predetermine
which topology survives. Keep results obtained with fixed measurement fixtures
separate from results after candidate-specific station changes.

The common tracker, calorimeters, inner-coil or outer-coil hypotheses and detached
forward calorimeter retain their existing definitions. Proposed dimensions below
are not integrated into production or substituted for the reference JSON. No
follow-up issue is created; the human will decide that after comparison.

## 2. Candidate allocations

All numerical entries are **NODD DESIGN CHOICE, unsigned**. Units: metres.
Absolute-z intervals mirror across the interaction point. Host boxes include
chambers, supports, services and candidate magnet/return structures; they must not
be treated as uniformly sensitive volumes or simultaneously available in full
to every owner.

| Candidate | Barrel r min–max | Barrel absolute z | Endcap r min–max | Endcap absolute z |
| --- | --- | --- | --- | --- |
| MAG-01 | 4.350–6.762 | 0–7.200 | 0.400–7.000 | 7.200–10.270 |
| MAG-02 | 4.350–7.500 | 0–8.000 | 0.400–7.500 | 8.000–10.900 |
| MAG-03 | 4.950–7.500 | 0–8.000 | 0.400–7.500 | 8.000–10.900 |
| MAG-04 | 4.950–10.000 | 0–9.000 | 0.400–10.000 | 9.000–10.900 |
| MAG-05 | 4.350–9.000 | 0–9.000 | 0.400–9.000 | 9.000–10.900 |
| MAG-06 | 4.950–8.850 | 0–9.000 | 0.400–8.850 | 9.000–10.900 |

MAG-01 preserves the current host. MAG-02 adds room for an inner-solenoid return
and chambers. MAG-03 restores chamber/support space lost to the outer coil rather
than requiring its earlier compressed host. MAG-04 expands more substantially to
explore return steel and chamber gaps; radius 10 m is a planning scenario, not a
minimum radius derived from saturation. MAG-05 reserves an expanded host for
discrete toroids, their supports and measurement gaps; it does not copy ATLAS
dimensions. MAG-06 carries a return-coil annulus explicitly. Larger hosts incur
material, service, alignment and facility consequences; no candidate receives
those resources for free in the comparison.

### MAG-06 ownership subdivision

**NODD DESIGN CHOICE:** within its barrel host, investigate measurement/return
space r=4.950–8.100 m, return-coil assembly r=8.100–8.600 m, and outer service/
support reservation r=8.600–8.850 m. These subdivisions are not a solved current
configuration or an allocation of iron. The total host, rather than its three
parts added again, defines the global boundary.

An end extension of the return annulus within r=8.100–8.600 m, |z|=8.000–9.000 m
is a possible initial coil-space hypothesis. It does **not** solve axial flux
redirection. Any end coils spanning farther inward must share or displace endcap
measurements explicitly; an endcap host cannot be both entirely available to
chambers and filled by an unrecorded closure structure. The 1.900 m endcap-host length in MAG-04–06 establishes neither sufficient
room nor a demonstrated impossibility for chambers and end closure. Subsequent
field/structure work may require explicit axial expansion and reconsideration of
the forward interface. Keep the required end-field
topology open for a finite-coil study rather than assume a solid disk or an
idealized boundary closes the field.

## 3. Calorimeter, forward and service interfaces

**FACT about the project reference:** DES-003's E1-R2 table places central HCal
out to r=4.200 m and |z|=6.200 m; detached forward instrumented space starts at
|z|=11.200 m, r=0.120–1.500 m. Its shielding, rear readout and supports are not
closed within that box. The architecture input requests outer-coil assembly
r=4.300–4.800 m, |z|≤6.800 m for MAG-03/04 and MAG-06's outer-main variant.

**INFERENCE:** the table preserves a nominal 0.150 m radial interval between
central HCal and inner-family muon hosts, or between the outer-coil assembly and
outer-family muon hosts. Endcaps of MAG-02–06 stop 0.300 m before the detached
forward study volume; MAG-01 leaves 0.930 m. These are rectangle differences,
not proven service, shielding or installation clearances. Services can require
local penetrations or extra length even if no two plotted boxes overlap.

**NODD DESIGN CHOICE:** assign barrel routes toward end/outer patch regions,
endcap routes toward rear outer-annular handoffs, and separate forward-calorimeter
routes and support footprints. Named phi sectors and loads follow; no full annulus
is implicitly filled with cable material. Existing source precedents are
SRC-ATLAS-JINST-2008 §5.5/PDF166, SRC-CMS-JINST-2008 §4.2/PDF119 and
SRC-CMS-TDR-019 §4.5/PDF64–65, retained in the
[calorimeter review](DES-003-calorimeter-review-1.md).

The detached calorimeter remains downstream of these muon hosts. It cannot filter
hadrons before those stations. The upstream endcap calorimeter and actual shower
leakage must justify filtering; expanding muon space does not license additional
absorber steel merely to improve rejection.

## 4. Aperture and physical interpretation

**INFERENCE:** for a prompt straight ray, r=|z|/sinh(|eta|). An eta-3.5 ray has
r≈0.435 m at z=7.200 m and r≈0.544 m at z=9.000 m. The common 0.400 m hole
therefore permits geometric entrance at the stretch direction for these hosts.
It does not establish independent station crossings, inactive-edge clearance,
beam-pipe/shielding fit or field leverage. Moving the endcap out may increase
radial leverage while changing barrel/endcap transitions and required services.

No dedicated yoke still includes the effects of calorimeter/support steel.
For MAG-02/04 the iron fraction, gaps, nonlinear material response and saturation
are unknown. For MAG-05 discrete coil sectors and end transitions are unknown.
For MAG-06 finite return/end currents, forces and fringe-field control are unknown.
These are subsequent model inputs, not reasons to prohibit allocating research
space. They block physical feasibility/performance conclusions, not this exploration.

## 5. Handoffs and next decision

The muon engineer owns host subdivisions and proposed measurements. The architect
owns magnet, calorimeter and service interfaces. Software records candidate bounds,
plots and descriptive clearance/ray checks. Physics defines common comparisons
and distinguishes space from measurement performance. The coordinator preserves
reference-versus-amended results and presents tradeoffs to the human.

Review these allocations as exploration inputs, then calculate candidate-specific
fields and measurement consequences. If further expansion is needed, record the
request explicitly rather than shrinking inactive material or declaring a topology
impossible from the reference envelope. No human sign-off is recorded here.

Verification: reconciled existing candidate cards and reference dimensions with
the muon-engineer requests. No new physical field, material transport, chamber
layout or engineering calculation was executed by this memo. Parent session owns
generated checks, dashboard updates and publication records.
