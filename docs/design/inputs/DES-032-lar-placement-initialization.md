# DES032/DES033 — reusable LAr period placement investigation

Date: 2026-11-13. **PROTOTYPE**, explicitly requested by the user as a separate
PR before the first 10k LAr response campaign. No physical design sign-off.

**FACT:** the existing barrel and turbine factories repeat DD4hep assemblies.
The [Si–W placement study](../../validation/siw-real-wedge-default/README.md)
replaced repeated assemblies with physical mother volumes and measured a much
shorter Geant4 volume-ID map build, while retaining physical leaves and IDs.

**INFERENCE:** real logical period volumes may give a similar benefit for LAr.
Their boundaries cannot be ordinary radial wedges: absorbers/electrodes are
inclined. The proposed envelope follows the outer negative steel face of one
absorber to the corresponding face of its neighbour, with the original annular
and axial clipping. Existing pieces theoretically fill this domain completely.

**NODD DESIGN CHOICE — investigation:** introduce an opt-in real-period export
alongside the legacy assembly export. Preserve each leaf's shape, material,
local transform, parent field IDs, replica transform and readout definition.
Use the actual enclosing material for the new mothers and quantify exclusive
mother volume. No source parameter, active-gap shape or segmentation is tuned.
Any new boundary is a numerical navigation boundary; shower-history equality is
not assumed merely from placement equivalence.

Before recommending adoption, require:

- daughter containment, adjacent-period partition and exclusive-volume checks;
- matching full native geometry, raw/canonical IDs and all physical leaf poses;
- native overlap checks at the retained 10 nm tolerance and matched material rays;
- serial initialization benchmarks of legacy and candidate on the same runtime,
  measuring geometry setup, Geant4 volume-ID map, native map and audit separately;
- saved-hit smoke evidence before any later response comparison.

Use complete ECAL-only zero-field models, identical libraries except the explicit
hierarchy option, Geant4 FTFP_BERT and 0.7 mm production cuts. Startup-only
probes use zero events and explicitly initialize both volume managers serially
before the audit. This avoids mistaking a first-hit multithreading lookup race
for hierarchy timing. The previously failed LAr pilot remains separate evidence.
Timing is descriptive, with run count and order reported; no speedup or geometry
equivalence is asserted until measured. Full artifacts stay local and ignored.

## Maintained export adoption, 2026-11-13

The [executed investigation](../../validation/lar-placement/README.md) retains
the opt-in comparison and its measured scope. The user's subsequent instruction,
"Great, go ahead - and update the DD4hep description of the ALLIGRO calorimeter",
authorizes using this hierarchy in the maintained LAYOUT-002 prototype export.
The [integration contract](ECAL-baseline-integration-2026-11-04.md#lar-geant4-hierarchy)
records that software choice; the [default-export report](../../validation/lar-placement-default/README.md)
records its checks. Standalone component defaults remain the legacy controls.
DES032/DES033 remain DRAFT / PROTOTYPE, with no human design sign-off inferred.
