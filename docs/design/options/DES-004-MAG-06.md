# MAG-06 — Solenoid with active return coils

**WITHDRAWN FROM STUDY — 2026-09-22:** the magnetic-field expert requested
removal of the active-return configuration. This card and its figures are retained
as historical evidence only; its recommendations and next tests are superseded.
See the [review response](../inputs/DES-004-magnet-expert-review.md).

- Date: 2026-09-17; status: DRAFT, unsigned candidate assessment.
- Parent: [DES-004](../DES-004-magnetic-configurations.md).
- Recommendation: retain for an inexpensive explicit dual-solenoid screen;
  concept evidence now exists, but forward closure and radial space remain open.

## Public precedent and its evidential limit

**FACT — SRC-FOURTH-CONCEPT-2007:** Park et al.,
[arXiv:0708.0142v2](https://arxiv.org/abs/0708.0142v2), §2.3/PDF5 and Fig.5/PDF6,
proposes a second, oppositely driven solenoid returning flux through the annulus
containing muon tracking. End “wall of coils” redirects the field. The illustrated
concept has 3.5 T in the tracker and −1.5 T in the annulus. This is an ILC
**design proposal**, not evidence of an operating collider-detector magnet.

The authors report a bending integral above 0.5 T·m to `cos(theta)=0.975`.
**INFERENCE:** `eta=atanh(0.975)=2.185`; that quoted reach does not substantiate
nODD's eta 3 baseline or 3.5 stretch. Its favourable muon and low-fringe-field
claims cannot be transferred to HL-LHC occupancies, material or geometry.

Shared arithmetic record: [option screen](../../validation/DES-004-option-screen.json).

## Concrete first variant

**NODD DESIGN CHOICE — proposed diagnostic:** choose an outer-main-coil variant
first, retaining MAG-03's R=4.5 m and half-length 6.5 m main sheet. Add a coaxial,
oppositely driven return sheet. Treat its radius, length and end-coil placement
as scan parameters; do not silently assign a physical fit. Report both central
field and exterior-field objective before current optimization. An inner-main
variant is a separate card because its return annulus would include calorimeters
and fundamentally change available muon space.

**INFERENCE — flux sanity:** uniform 3 T bore flux at R=4.5 m is approximately
190.85 Wb. Returning it uniformly through a −1.5 T annulus would require
`R_outer=sqrt(4.5²+3*4.5²/1.5)=7.79 m`, beyond E1-R2's 6.762 m outer barrel
host before coil thickness. This optimistic zero-thickness annulus starts at the
main current sheet, inside its cryostat reservation. Starting usable return space
at 4.95 m instead gives **8.062 m**, still before return-coil thickness. The new 8.10 m annulus edge below responds to this screen. These are
conditional area estimates, not lower bounds for every possible return topology. The −1.5 T is a borrowed screening value, not a
requirement. Nonuniform/end return changes this estimate; it nevertheless exposes
that low-field return is not spatially free. Neither this formula nor two infinite
solenoids establishes finite-coil fringe cancellation.

## Benefits, blockers and follow-up

**INFERENCE:** a gas tracking annulus avoids scattering in a dedicated iron yoke
while preserving an additional bending region. It trades iron for conductors,
cryostats, supports, protection and coupled magnetic forces. Steel in inherited
HCal/supports still requires a material-aware field solution; “no dedicated yoke”
is the accurate description of this nODD option.

**Current blocker to physical ranking:** no finite return/end-coil allocation
has yet demonstrated simultaneous muon measurement space, service exits and
forward bending. There is no evidence-based justification to declare the topology
impossible; there is equally no demonstrated fit or HL-LHC precedent here.

Solve a finite two-coil vacuum control, then explicit end-coil variants, recording
current, field energy, external-field samples and signed bending between muon
stations. Check radial/axial conflicts and sensitivity to a missing or mismatched
coil current. Restore calorimeter steel separately. Assess end supports and
cryogenic routes against tracker/calorimeter exits and detached-forward interfaces.
Advance only if forward measurement information and physically reservable space
survive; otherwise deprioritize before expensive engineering or simulation.

No nODD dual-coil field, forces, quench response or resolution was calculated here.

**Current host request:** barrel r=4.95–8.85 m, |z|≤9 m;
stepped endcap: upstream r=0.4–4.8 m, |z|=6.95–9 m;
wide r=0.4–8.85 m, |z|=9–10.9 m.
[Budget](../inputs/DES-004-muon-envelope-amendments.md),
[PNG](../figures/DES-004-mag-06-muon-envelope-rz.png) /
[SVG](../figures/DES-004-mag-06-muon-envelope-rz.svg). Unsigned; baseline issue after selection.

**Coordinated inner-space reuse (2026-09-18):** barrel ECal r=1.30–1.66 m,
endcap ECal outer r=1.66 m, barrel HCal r=1.76–4.20 m. This preserves nominal
ECal thickness, increases HCal host width by 0.40 m and retains tracker/services,
all axial bounds, outer coil and muon allocations. The [subsystem coordination](../inputs/DES-004-inner-space-reallocation.md)
records requirements, alternatives and the unverified material/field consequences.
