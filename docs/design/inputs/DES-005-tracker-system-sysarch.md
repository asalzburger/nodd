# DES-005 input — System Architect

- Status: DRAFT planning input; no layout sign-off.
- Date: 2026-09-18.
- Role: `SysArch`, performed by the coordinating agent with independent
  `TrackTech`, `PhysVal` and `SoftEng` contributions.
- Context: [DES-003](../DES-003-global-envelopes.md),
  [allocation record](../DES-003-envelopes.json),
  [ADR-006](../../decisions/ADR-006-global-envelope-and-field-hypotheses.md),
  [project scope](../../../PROJECT.md).

## Position

**NODD DESIGN CHOICE — human-directed:** retain the tracker envelope as the
starting constraint and require system tracking coverage `|eta| < 4`. Use pixels,
short strips/strixels and stereo outer long strips as the ODD-guided architecture.
Permit documented, performance-motivated changes, including timing-capable layers.
The current request fixes coverage; the earlier tracker input's reduced-coverage
alternative is historical and is not a candidate for this study.

**NODD DESIGN CHOICE — inherited allocation:** DES-003 E1-R2 reserves
`0.025 <= r <= 1.140 m`, `|z| <= 3.150 m` for the tracker assembly, with the
shared interface reservation `1.140 <= r <= 1.240 m` over the same longitudinal
extent. Exact locators are regions `tracker` and `tracker_services` in the
allocation JSON. These are host boundaries with recorded baseline technical
approval, not active sensor dimensions or proof of available service capacity.
The 25 mm inner host must not become an assumed sensitive radius.

**NODD DESIGN CHOICE — proposed:** keep the full assembly allocation fixed for
the first comparison, while allowing the internal pixel/short-strip/long-strip
boundaries to vary. A layout requiring more host space must identify the conflict
and request an amendment; optimization must not silently consume magnet,
calorimeter or common-service space. Earlier ODD subdivision dimensions are a
comparison input, not extra fixed nODD requirements.

The architect's primary argument is that a layer radius has meaning only with
its occupied module/support envelope, routes and neighboring interfaces. A
performance optimum based on unoccupied ideal cylinders can be a useful screen;
it cannot establish the physical system layout.

## Interfaces and ownership

All proposed interfaces below carry a stable ID, owner at both ends, units and
coordinate frame, source/configuration revision, assumptions, uncertainty,
reserved/occupied bounds and a checkable handoff. Detailed dimensions remain open.

| Interface | Owners | Required handoff before layout selection |
| --- | --- | --- |
| Beam pipe to innermost pixel | SysArch / TrackTech | Pipe profile, supports and motion/installation allowances; active sensor clearance, forward aperture and material before first hit |
| Pixel to short-strip; short-strip to long-strip | TrackTech / SysArch | Active and occupied bounds, overlap/transition coverage, shared support boundaries and service crossings |
| Module to local support | Pixel/strip component author / TrackTech | Physical outline and inactive periphery, attachment and thermal path, electrical termination, tolerances and material ownership |
| Local to common cooling/power/data | TrackTech / SysArch | Loads, routes and cross-sections, manifolds/connectors/conversion, exits and one owner per physical constituent |
| Tracker to magnet/calorimeters | SysArch / relevant subsystem owner | Retained host and reserved routes, mechanical support handoffs, forward service space, material before calorimetry and field domain |
| Layout to study tools | TrackTech + SysArch / SoftEng | One versioned sensor/module/layout identity, local measurement axes, active masks, pairing, material and field scenario references |
| Timing to tracker and physics | TrackTech + SysArch / PhysVal | Barrel/forward scope, hardware and services, response assumptions, material cost and measurable association benefit |

The magnetic research branch currently preserves tracker and interface bounds
even in its outer-solenoid space-reallocation studies:
[DES-004, revision 040337c2d6129014655a7534e0ea79c6ef693bc2](https://github.com/asalzburger/nodd/blob/040337c2d6129014655a7534e0ea79c6ef693bc2/docs/design/DES-004-magnetic-configurations.md#reuse-of-the-absent-inner-solenoid-space--2026-09-18).
That is an unsigned study choice, not permission to enlarge the tracker if a
different topology is selected. The field interface can develop independently
of a final magnet choice; record which candidate and field approximation was used.

## Candidate strategy and review argument

Start from an extracted ODD control with its actual measurement conventions.
Then define an ODD-like nODD candidate with explicit provisional component and
service scenarios. Vary a small set of questions: pixel extent; barrel/endcap
transition and disk spacing; strixel/strip partition; stereo measurement geometry;
module staggering; integrated or separate timing. Keep a ledger of the physical
reason for each change and the expected observable it should affect.

Use cheap screens to discard poor candidates before module-aware ACTS studies,
but retain rejected alternatives and the reason for rejection. Optimize jointly
with field/material uncertainty rather than selecting a layout for an ideal
central field that may not be available forward. Reopen comparisons when module
outlines, service loads or credible fields change enough to invalidate assumptions.

| Tension between roles | Proposed resolution |
| --- | --- |
| TrackTech needs unfinished module/support inputs; SoftEng can start with surfaces | Begin with bounded, named estimates and interface contracts. Require module masks, component inventories and route closure for the physical shortlist. |
| PhysVal needs meaningful performance evidence; full simulation arrives later | Separate covariance screens, module coverage, fast fits, pattern recognition and full transport. State what each stage demonstrates and require unresolved claims at the next gate. |
| Final beamspot validation was requested; layout design starts at the origin | Origin rays debug geometry. Add vertex stress tests immediately and the agreed luminous distribution before layer freeze; repeat with detailed geometry at the final gate. |
| Timing may help pile-up association but consumes tracking material and services | Compare no timing, timing hardware with time disabled, and the same hardware with time enabled; include forward coverage and realistic resource costs. |
| Magnetic topology is undecided | Use verified controls first, then versioned candidate fields as they arrive; retain fixed-layout attribution tests before candidate-specific optimization. |

Final human sign-off where required is by `asalzburger-review`. The plan prepares
the interfaces and evidence for that decision. No detector study, numerical
optimization or engineering fit validation was executed for this input.
