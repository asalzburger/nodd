# SESSION-2026-10-26-gen3-material-map-run

## Scope and selected user request

Starting clean d6c9ca42ed5499c4d54dbdd61f2856dccfc27d67 on existing PR100,
codex/tracker-gen3-material-mapping. User requested a new trial: pixel barrel
carrier after sensitive;all other layers before;one mapping surface per layer;
extra pipe,gap cylinders,barrel/endcap separators and outer shells. Phi1,
configurable z/r bins250/100/500 and50/100/50/250 by named family. Explicitly
charge SoftEng to enable ProtoSurfaceMaterial on those portals;learn/run
nodd_material_mapping.py/nodd_material_validation.py and overlay only the
validated total on the original stacked material profile.

## Decisions and limits

Literal52 signed sensitive layers plus extras likely gives65 physical carriers
after deduplication;preserve the one-per-layer rule rather than force50.
Full outer cylinder defaults500 z bins,configurable. Mapping full recording
onto portals clears native silicon/pipe slabs in this isolated campaign to
prevent double counting;the preceding native-slab survey remains a control.
No DD4hep geometry/material changes. DES025 records the user-selected prototype
configuration before implementation. Existing ACTS assignment is closest
intersection;carrier side is a placement choice,not a guarantee that each
material step is always assigned forward/backward.

## Runtime

acts-spack preflight warns stale setup/lock fingerprints and unavailable staged
DD4hep/Geant4 full source trees. Direct installed runtime verification is
required. Reuse native adapter source530080cfe16c7513228bf60238b99d4b9938538a
and build ../nodd-software-layout;do not modify shared installs or dependencies.
Pin complete sources/binaries and selected manifest. Existing raw recording
SHA034fe2f6ceb7dad9c4786254b9821777e8db093704a5d77528c47a8a5926b3cf.

## Specialist assignment plan

Explicit SoftEng fallback owns isolated native portal-material support and
mapping/validation steering plus native smoke evidence. Main owns configurable
portal selection/manifest,profile overlay,documentation/integration/accounting.
The complete bounded assignment will be recorded before dispatch. Independent
PhysVal review follows a fixed implementation/evidence revision.

## Token accounting

Current parent turn counters unavailable until closure. Completed specialist
turns will be recovered/imported without overlapping prior PR100 task turns.
Prior task records and evidence remain intact. No estimates or private rollouts.
