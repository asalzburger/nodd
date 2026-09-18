# MAG-03 — Outer solenoid without a dedicated return yoke

- Date: 2026-09-17; status: DRAFT; human approval pending.
- Parent: [DES-004](../DES-004-magnetic-configurations.md); reference: E1-R2.
- Assessment: **retain as the principal large-solenoid comparison; any demonstrated measurement benefit must justify its space and resource costs.**

## Proposal and evidence

**NODD DESIGN CHOICE:** surround barrel and endcap **central** calorimeters with
a diagnostic sheet R=4.500 m, half-length 6.500 m, normalized to +3 T centrally.
Detached forward calorimetry is excluded. The [architect input](../inputs/DES-004-system-architecture.md),
§3, requests assembly r=4.300–4.800 m, |z|≤6.800 m and muon barrel inner host
4.950 m rather than 4.350 m. The coordinated layout now reuses the inner-coil space as described below;
the original fixed-calorimeter configuration remains a historical control.

**FACT:** SRC-CMS-JINST-2008, §2.1/PDF33 and Table 2.1/PDF35, describes the built
4 T external NbTi solenoid. It establishes a technology/topology anchor, not an
iron-free precedent or proof that nODD's proposed 500 mm assembly fits. Source
identities are in the [catalogue](../../../reference/manifest.yaml).

## Technical assessment

**INFERENCE — tracker:** the [vacuum benchmark](../../validation/DES-004-solenoid-benchmark.json),
`results[candidate.id].checks`, gives Bz=2.743 T on axis at z=3.150 m and
(Br,Bz)=(0.101,2.767) T at the outer tracker corner. The smaller end variation
than MAG-01 motivates propagation studies. It does not establish better momentum
resolution: forward trajectories, measurement leverage, material and resource
differences remain relevant.

**INFERENCE — calorimetry:** removing the inner coil avoids its pre-ECal material,
but the larger solenoid exposes central calorimeters to a different field and
requires external supports/services. Downstream coil material influences leakage
and muon transport. Calorimeter steel inside the bore makes the vacuum field a
control rather than a physical map; “no yoke” cannot mean ignoring this steel.

**INFERENCE — muons:** substantial bending between tracker and outer segments
can aid combined measurements, yet stations beyond the main field may mainly
measure an outgoing direction. SRC-CMS-YOKE-COSMICS-2010, §§1–2/PDF3–5, supports
separating tracker-combined, vertex-constrained and unconstrained standalone
measurements. It does not prove this yoke-free arrangement provides standalone
leverage. The original fixed-outer-radius trial shrank the host to 1.812 m. The current
request below expands it to 2.550 m, leaving station/support feasibility open.

**INFERENCE — resources/services:** vacuum central-field normalization requires
37.747 MA-turn versus MAG-01's 17.144, from the finite-sheet equation in the
architect input. These are ampere-turns, not conductor-current or feasibility
results. Larger radius/length increases the magnetic volume and changes forces,
protection and cryogenic demands. Neither 3 T normalization nor a reserved shell
establishes equal resources or sufficient structural margin.

## Blocking conditions versus missing evidence

**Historical integration conflict, addressed at envelope level:** the assembly
intersects E1-R2's unchanged muon barrel host. The current amended barrel entrance
at 4.950 m and stepped endcaps resolve that coarse overlap; the coordinated
calorimeter redesign below reuses the absent inner-coil space. This does not
establish physical integration. Conductor/cryostat fit, nonlinear field, stray-field acceptability,
station feasibility and standalone performance remain **missing evidence**.
Insufficient standalone information would block that particular requirement.

## Next discriminating tests

**NODD DESIGN CHOICE:** compare common-surface vector-field propagation first,
then separately show the amended muon layout; do not silently exchange layouts.
Evaluate pre-ECal material benefit against resources, field-through-steel and
downstream material costs. Review support/cryogenic routes and station room.
MAG-03-B, a barrel-only outer coil, remains a reserve variant with length and end
interfaces TBD; it cannot borrow this full-central model's forward results.
No new simulation, engineering validation or sign-off is supplied by this note.

**Current host request:** barrel r=4.95–7.5 m, |z|≤8 m;
stepped endcap: upstream r=0.4–4.8 m, |z|=6.95–8 m;
wide r=0.4–7.5 m, |z|=8–10.9 m.
[Budget](../inputs/DES-004-muon-envelope-amendments.md),
[PNG](../figures/DES-004-mag-03-muon-envelope-rz.png) /
[SVG](../figures/DES-004-mag-03-muon-envelope-rz.svg). Unsigned; baseline issue after selection.

**Coordinated inner-space reuse (2026-09-18):** barrel ECal r=1.30–1.66 m,
endcap ECal outer r=1.66 m, barrel HCal r=1.76–4.20 m. This preserves nominal
ECal thickness, increases HCal host width by 0.40 m and retains tracker/services,
all axial bounds, outer coil and muon allocations. The [subsystem coordination](../inputs/DES-004-inner-space-reallocation.md)
records requirements, alternatives and the unverified material/field consequences.
