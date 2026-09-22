# DES-004 — Coordinated candidate muon-envelope amendments

**2026-09-22 scope update:** MAG-06 is withdrawn from active study following
[expert review](DES-004-magnet-expert-review.md). New main-solenoid studies use
finite homogeneous winding packs; the earlier sheet calculations and MAG-06
recommendations below are historical. Enclosure allowances remain unverified.

- Date: 2026-09-18; status: DRAFT; numerical human approval pending.
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

Tracker, coil hypotheses and detached forward calorimeter retain their definitions.
The [subsequent subsystem coordination](DES-004-inner-space-reallocation.md)
reallocates central ECal/HCal radial bounds for MAG-03/04/06 only. Proposed dimensions below
are not integrated into production or substituted for the reference JSON. No
follow-up issue is created; the human will decide that after comparison.

## 2. Candidate allocations

All numerical entries are **NODD DESIGN CHOICE, unsigned**. Units: metres.
Absolute-z intervals mirror across the interaction point. Host boxes include
chambers, supports, services and candidate magnet/return structures; they must not
be treated as uniformly sensitive volumes or simultaneously available in full
to every owner.

| Candidate | Barrel r [m]; max absolute z [m] | Upstream endcap r [m]; absolute z [m] | Wide endcap r [m]; absolute z [m] |
| --- | --- | --- | --- |
| MAG-01 | 4.35–6.762; 7.2 | 0.4–4.2; 6.35–7.2 | 0.4–7; 7.2–10.27 |
| MAG-02 | 4.35–7.5; 8 | 0.4–4.2; 6.35–8 | 0.4–7.5; 8–10.9 |
| MAG-03 | 4.95–7.5; 8 | 0.4–4.8; 6.95–8 | 0.4–7.5; 8–10.9 |
| MAG-04 | 4.95–10; 9 | 0.4–4.8; 6.95–9 | 0.4–10; 9–10.9 |
| MAG-05 | 4.35–9; 9 | 0.4–4.2; 6.35–9 | 0.4–9; 9–10.9 |
| MAG-06 | 4.95–8.85; 9 | 0.4–4.8; 6.95–9 | 0.4–8.85; 9–10.9 |

MAG-01 preserves its outer bounds and adds an upstream step. MAG-02 adds room for an inner-solenoid return
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
chambers and filled by an unrecorded closure structure. The 1.900 m full-radius part in MAG-04–06 now has an upstream inner-radius extension. Neither the stepped union nor the extra space demonstrates chamber/end-closure fit. Keep the required end-field
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

### Stepped-endcap revision — 2026-09-18

**NODD DESIGN CHOICE — unsigned:** following PR #6 comments
[4040667425](https://github.com/asalzburger/nodd/pull/6#discussion_r4040667425),
[4040694164](https://github.com/asalzburger/nodd/pull/6#discussion_r4040694164) and
[4040721189](https://github.com/asalzburger/nodd/pull/6#discussion_r4040721189),
and the user's explicit instruction, decouple the endcap front from barrel length.
Represent each endcap as the union of two non-overlapping radial/axial sections.
The narrower upstream section sits inside the barrel; the downstream section
widens to the previous outer radius. Their common face is a bookkeeping boundary
inside one composite host, not two coincident physical solids.

The proposed inner-solenoid front is |z|=6.35 m: HCal back 6.20 m plus a trial
0.15 m interface allowance. Its outer radius 4.20 m leaves 0.15 m to the barrel
inner radius 4.35 m. Outer-solenoid options start at |z|=6.95 m: coil-assembly
back 6.80 m plus the same trial allowance; r=4.80 m leaves 0.15 m to their
4.95 m barrel. These allowances are project choices, not validated routing,
shielding or installation clearances. The upstream face is now independent of
barrel length; the wide section currently starts at the barrel back because it
shares its radial range. Moving either requires checking actual intersections,
not enforcing equality. Outer radii, barrel lengths and endcap back faces stay
at the prior candidate values for this isolated comparison.

**INFERENCE:** the former HCal-to-endcap gaps of 1.0–2.8 m become 0.15 m for
inner-solenoid options. Outer-solenoid options retain 0.75 m from HCal back to
endcap front, determined here by the coil's axial extent plus 0.15 m; this is
not a claim that the coil fills the entire intervening bore. Shared services and
end structures still need explicit allocations. The new host is not automatically
available in full for both chambers and magnetic closure.

Keep the 0.40 m aperture. For a straight prompt eta=3.5 ray, r=6.35/sinh(3.5)
≈0.384 m at the inner-family front: it enters the radial host only at
|z|=0.4*sinh(3.5)≈6.617 m. Thus the earlier front does not guarantee a first
station at that eta. The outer-family front gives r≈0.420 m. Eta=3 rays enter
both families at their upstream face. These are allocation crossings, not hit
counts, detector efficiency or a validated beam-line/shielding aperture.

MAG-04/06 still have only 1.90 m of **full-radius** endcap space, but now also
have an upstream inner-radius extension. No end-flux solution has yet been shown
to fit their stepped union. More space alone does not resolve field topology,
material or measurement leverage. Earlier rectangular requests remain in Git at
`10a918e835eb2d74a16990980bdc68bcebb99e58`; E1-R2 is unchanged.

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
