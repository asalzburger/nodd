# ADR-009 — LAYOUT-002 ALLEGRO-style LAr alternative and service envelope

- Status: **DRAFT / PROTOTYPE**
- Date:2026-10-13
- Human owner/sign-off: pending
- Instruction: user explicitly requests two LAr replacement PRs and a distinct LAYOUT-002.

**FACT:** the SiW candidate LAYOUT-001 is documented separately. Public ALLEGRO
inclined-barrel/three-wheel turbine inputs and current engineering R&D are
catalogued in DES032/DES033 and reference/manifest.yaml.

**NODD DESIGN CHOICE:** retain tracker and conditional inner3T solenoid;
substitute ALLEGRO-style LAr/Pb-steel/PCB barrel/endcaps, keeping source
sampling radii/period counts and enlarging physical cryostat/service space.
Do not import the source outer2T solenoid or external detector factory.
Prototype own planar taper and readout conventions are explicitly documented.

Allocate HCAL front apothem3.13m, barrel half-length5.86m, endcaps6.36–7.8559m,
and retain1.4959m total depth. Reserve0.30m barrel radial corridor,0.80m before
LAr endcaps and0.50m behind them. Cold electronics are the studied service
option. Warm millions-of-cables alternatives, higher heat scenarios and pressure
vessel/routing details remain redesign/qualification questions.

**INFERENCE:** current LAr wheel aperture does not cover|eta|4. Mark empty,
technology-unassigned forward EM collar and FCal insertions; this grants no
acceptance or machine-interface approval. Full-depth barrel/endcap transition
is also unresolved. Changing the aperture or claiming uniform coverage requires
new physical design and response evidence, not relabelling the envelope.

Consequences: larger detector and HCAL load/iron volume, new magnetic solution
and support design, unresolved adverse cooling. Keep LAYOUT-001 available for
comparison. Production integration, engineering sign-off, calibrated response
and particle flow are later decisions. Repository merge is not human sign-off.

Alternatives considered: shrink ALLEGRO into the SiW envelope (would alter
gaps/mechanics), warm cable extraction (larger feeds), and immediate new forward
LAr wheel (unsupported mechanical/positive-gap assumptions). These remain
separate studies rather than silently changing the retained source baseline.
