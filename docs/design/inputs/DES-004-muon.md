# DES-004 — Muon measurement and magnet comparison

**2026-09-24 sizing amendment:** [Current constraints and dimensions](DES-004-magnet-sizing-review.md)
supersede earlier winding/vessel and MAG-03/04 radial allocations below.
Earlier numerical results remain historical; complete-system engineering is open.

- Date: 2026-09-17; status: DRAFT, unsigned research advice.
- Context: [candidate cards](../DES-004-magnetic-configurations.md),
  [research plan](../../MAGNET_RESEARCH_PLAN.md),
  [reference envelopes](../DES-003-global-envelopes.md),
  [physics comparison contract](DES-004-physics-validation.md).
- Scope: first increment; no station, material or magnet implementation.

## Conditional preference, not a numerical ranking

**NODD DESIGN CHOICE — proposed:** for genuinely unconstrained standalone
momentum, prioritize the **MAG-05 air-core toroid** investigation alongside the
instrumented-return alternatives **MAG-02/MAG-04**. These place intended bending
among muon measurements. The preference concerns the measurement principle, not
proven fit, performance or engineering superiority. MAG-05 must demonstrate its
coil/cryostat/support allocation within the ODD-like outer scale or request an
explicit expansion.

For **combined tracker–muon measurement**, MAG-03 is an important alternative:
its larger bore can increase bending before the first outer station. MAG-01
remains the lower-radius control. Neither is ruled out for standalone measurement;
the external field and its observability must be calculated before making that
claim. MAG-06 remains exploratory until its return-coil arrangement exists.

**INFERENCE:** measuring an outgoing segment after a bending region does not,
by itself, determine both an unknown incoming direction and momentum. An inner
tracker supplies additional information; a vertex prior supplies a different
constraint. Consequently, report independently:

1. Muon-only fit, with neither tracker measurements nor interaction-point prior.
2. Muon-only fit with a specified vertex prior, including its uncertainty.
3. Combined tracker–muon fit, stating any additional vertex prior.

Use prompt and displaced samples. Do not transfer a vertex-constrained result to
unconstrained standalone, or attribute combined performance to the muon system
alone. Vacuum deflections and exact surface intersections are not resolutions.

## Immediate MAG-03 station conflict

**FACT about the proposed cards:** the MAG-03 assembly occupies
`r=4.300–4.800 m, |z|≤6.800 m`. The architect requests a muon host inner radius
of **4.950 m**, while retaining outer radius **6.762 m**. The available radial
host therefore falls from **2.412 m** in E1-R2 to **1.812 m**. These are unsigned
project allocations, not experimental facts.

**INFERENCE:** the common diagnostic cylinder at **r=4.500 m** lies inside this
assembly wherever `|z|≤6.800 m`, coincident in radius with its ideal current sheet
where `|z|≤6.500 m`. It cannot represent a physical muon station there. Near-sheet
numerics also require the software's explicit singularity/domain policy.

**NODD DESIGN CHOICE — proposed:** retain common probes only for clearly labelled
field diagnostics and flag the incompatible region. Do not count it as a viable
MAG-03 measurement in fits. A subsequent physical-layout comparison must publish
revised station radii outside the assembly, their reduced lever arm, material and
service allowances. Do not silently move the common cylinder and call the result
a fixed-layout comparison. MAG-04 adds return plates/gaps to the same restricted
host; their fit is presently unknown.

## Forward, material and service obligations

**INFERENCE:** at fixed forward direction the useful quantity is transverse
bending between independently measured surfaces, not central Bz. Axial solenoid
fields and forward trajectories can be nearly parallel. Toroid field orientation
can offer leverage there, but discrete sectors, coil obstructions, barrel/endcap
transition and field cancellations require three-dimensional treatment.

Keep the **|η|<3 baseline / 3.5 stretch** objectives separate from demonstrated
coverage. The [earlier aperture analysis](DES-003-muon-review-1.md) shows that
station inner edges must be redesigned; an enlarged parent host alone does not
provide active measurements. Sample coil and inter-coil azimuths, forward apertures
and transition regions before interpreting missing crossings.

For yoked candidates, evaluate signed return-field bending together with
multiple scattering, energy loss, stopping and alignment. Useful bending and
added material are coupled; neither an empty-return field nor a steel-only
material addition is a fair physical comparison. Do not select extra steel before
calorimeter leakage/punch-through evidence. Detached forward calorimetry remains
downstream of the present muon hosts and cannot filter particles before those
stations.

Reserve named sectors/routes for magnet current, cryogenics, chamber power/data,
gas and cooling; distinguish station-owned material from common supports. Coil
supports and return plates cannot consume nominal measurement space unnoticed.
Alignment references and access paths must remain visible even when represented
effectively. No additional dimensions are selected here.

## Public evidence and next gate

- **FACT — SRC-ATLAS-JINST-2008**, §6.1, printed p.164/PDF194 and
  Figs.6.1–6.2/PDF195: barrel/endcap toroids and separated muon stations provide
  an engineered precedent; service gaps and its different scale preclude copying
  performance to nODD.
- **FACT — SRC-CMS-YOKE-COSMICS-2010**, §§1–2/PDF3–5: operational tracker-to-muon
  bending and yoke-field studies distinguish vertex-constrained and independent
  measurement and identify alignment limitations.
- **FACT — SRC-CMS-FIELD-MAP-2023**, §§1–2/PDF2–3: the field map represents
  iron/air interfaces and geometrical asymmetries; one nominal outer field is
  insufficient. All sources are in the [catalogue](../../../reference/manifest.yaml).

First accept the candidate/domain and measurement definitions, then examine
verified vector fields and propagation; material/measurement fits follow. No
magnet performance, field solution or propagation was evaluated for this memo.
Source-located earlier inputs and current allocation arithmetic were reviewed;
parent-session logging and project tracking cover this contribution. Human
selection remains pending.
