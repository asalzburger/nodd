# ADR-010 — Common forward calorimeter technology and candidate interfaces

- Status: **DRAFT**
- Date: 2026-10-17
- Human owner / technical sign-off: unassigned / pending
- Direction: design and fit the recommended forward calorimeter into layouts 01 and 02.
- Governing proposal: [DES039](../design/DES-039-common-forward-calorimeter.md).

## Context and proposed decision

The two layouts reserve narrow forward volumes; the LAr alternative also has an upstream EM collar reservation. A technology recommendation alone does not establish installed readout space or acceptance. The current downstream beam pipe ends at four metres.

**NODD DESIGN CHOICE — proposed:** use a common 1.8 m warm tungsten/longitudinal-quartz-fibre body, rear cooled SiPM arrays and independently read long/short populations. Add the short, wider module needed for the LAYOUT-002 EM transition. Preserve the independently developed tracker, solenoid, Si–W and LAr sources and label their exact revisions in the candidate drawing inputs.

Explicitly amend the former empty R80 mm aperture to a R50 mm physical bore, and add the LAYOUT-002 collar collector/service neck and rear handoff planes detailed in DES039. These are draft interface choices, not machine, magnetic or engineering approval. A same-radius beam-pipe extension is a clearance control only.

## Alternatives and consequences

CASTOR-style tilted plates retain a tungsten/quartz precedent but require side optics exceeding the narrow envelope. Separate front/rear fibre compartments require an extraction tray or conduit through the rear absorber. Cu/W–LAr adds a dedicated cryostat. Rear long/short fibres provide two depth weightings while preserving a continuous tungsten matrix; calibrated EM/hadronic separation remains a response hypothesis.

The common body reduces component variation, but the added collar increases LAYOUT-002 sensor, power and service counts. Cherenkov-only readout is noncompensating. Local SiPM selection is conditional on irradiation/background/circuit tests; remote photosensors remain a possible redesign. The narrowed aperture, small eta5 edge margins, multi-tonne masses and new rear routes require joint beamline/calorimeter/magnet/muon review.

No existing design state is advanced. Production construction, full-detector optical/shower response and all human sign-offs remain outside this prototype decision.
