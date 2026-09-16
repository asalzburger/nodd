# Literature coverage assessment

- Date: 2026-09-16
- Phase: M0; planning only
- Related: ADR-005 (DRAFT); no linked issue or detector design approval
- Evidence: local PDF title text and selected bookmarks, not full scientific review

The two experimental RD53 inputs are ATLAS and CMS integration into their
respective designs. The RD53A manual supplies shared device context, rather than
a third experimental design. Later experiment-specific manuals are also local.

## Available locally

| Area | ATLAS | CMS |
| --- | --- | --- |
| Pixels | SRC-ATLAS-TDR-030; SRC-RD53C-ATLAS | SRC-CMS-TDR-014; SRC-RD53C-CMS |
| Strips / outer tracker | SRC-ATLAS-TDR-025 | SRC-CMS-TDR-014 |
| Calorimeters | SRC-ATLAS-TDR-027 (LAr), SRC-ATLAS-TDR-028 (Tile) | SRC-CMS-TDR-015 (barrel), SRC-CMS-TDR-019 (endcap) |
| Muons | SRC-ATLAS-TDR-026 | SRC-CMS-TDR-016 |

Source IDs resolve through [the catalogue](../../reference/manifest.yaml).
The previously unidentified report titles above were read from PDF page 1 except
ATLAS-TDR-026, whose title is on PDF page 3. These are text-level identity checks;
the catalogue's stricter verification states have not been advanced. The two
RD53C title pages say version 1.92, 2024-09-18, and contain a placeholder report
identifier. Their canonical public publication identity remains unresolved.

Bookmarked contents were inspected for ATLAS LAr/Tile and CMS barrel calorimeter
and muon upgrade reports. This confirms useful subsystem coverage, but does not
establish completeness of mechanical/material detail. The LAr implementation
chapters emphasize electronics, power and controls; CMS barrel chapters cover
component longevity, readout and cooling. Upgrade documentation needs to be read
with sources describing the retained structures.

## Assessment and acquisition priorities

Enough material is available to begin comparative extraction in each area.
Complete resources for equal construction-level detail are not yet established.
Recommended gap-filling, subject to the technologies actually chosen:

1. Original/as-built calorimeter and muon construction references for structures
   retained through upgrades: absorbers, active layers, cryostats, chambers,
   supports and interfaces. The official
   [ATLAS TDR index](https://twiki.cern.ch/twiki/bin/view/AtlasPublic/AtlasTechnicalDesignReports)
   lists the original LAr/Tile reports separately from Phase-II upgrades.
2. Public component documentation for sensor/readout assemblies, hybrids,
   mechanical stacks, cooling and power/data interfaces. Strip modules need
   comparable evidence to the RD53 module reading; a chip manual alone is
   insufficient. Select specific electronics documents after mapping the TDRs.
3. Later production, qualification and integration publications to distinguish
   original design targets from demonstrated construction and performance.
4. Public material budgets, composition/density information, masses, clearances,
   service routing and validation results sufficient for reproducible modelling.
   Record unresolved dimensions or effective-material approximations explicitly.
5. Detector-wide magnet/yoke, support and service-envelope references when global
   integration is proposed. These interfaces cannot be inferred from chip manuals.

Equal detail means tracing active elements, readout, passive construction,
supports/services and validation for each chosen technology. It does not require
modelling every electronic function or copying either experiment.

Next suggested extraction: ATLAS Strip TDR plus CMS Outer Tracker chapters, then
calorimeter and muon maps with a missing-evidence table for each. No new PDF
acquisition is needed to start. Original construction sources are the highest-value
addition before claiming complete calorimeter/muon geometry evidence. No detector
scope expansion or implementation is authorized by this assessment.

## Human clarification: simulation realism (2026-09-16)

The user clarified that the target is realistic use of components within the
full detector, at a level appropriate for simulation. CAD/manufacturing accuracy
is not a project objective. The intended later output is automatically generated
DD4hep factory and XML code for a detector validated with Geant4. Generator
architecture and quantitative accuracy criteria will be discussed later.

Consequently, the acquisition priorities above are selective: seek construction
references only where they resolve simulation-relevant dimensions, segmentation,
material, placement, interfaces or services. Detailed manufacturing drawings are
not a prerequisite. Effective representations should preserve the relevant
physical quantities and document what was omitted, as PROJECT.md already requires.

Whole-detector descriptions provide the architectural context for subsystem TDRs.
The two additions below were subsequently acquired and mapped on 2026-09-16;
see [the intake report](overview-reading.md). Full scientific review remains pending:

- [The ATLAS Experiment at the CERN Large Hadron Collider](https://jinst.sissa.it/LHC/ATLAS/2008_JINST_3_S08003.pdf),
  JINST 3 (2008) S08003.
- [The CMS experiment at the CERN LHC](https://cds.cern.ch/record/1129810/),
  JINST 3 (2008) S08004.

These are detector-description papers, distinct from TDRs. Use them for the
whole-detector picture, and date-tagged subsystem/upgrade TDRs for subsequent
changes. They are catalogued references, not normative parameter evidence yet.
Whole-detector TDRs and technical proposals are also useful for design rationale.
No single historical document is assumed to describe the entire upgraded detector.

A proposed later workflow is public evidence -> reviewed component/system
specification -> generated DD4hep factories and XML -> Geant4 validation.
This is a planning sketch, not an accepted generator architecture. Geometry
construction success alone will not establish physical accuracy; material,
coverage and response checks will need explicit targets.
