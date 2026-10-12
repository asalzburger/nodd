# Issue #38 — whole-millimetre disc positioning

User requested two separate PRs for issue38, explicitly resumed after a logging pause, authorized acts-nodd and required usage recovery at completion. Later required the positioning PR description to list every disc movement.

Adopted exact positive datums 615,795,1046,1333,1645,1977,2328,2692,3070 mm and negative reflections; support/collector datums and future optimizer integer policy updated. Used implemented ±615.2 mm first datum for the displacement comparison; no double first-disc shift. Historical evidence preserved. Updated DES015, input/config pins, exporter/optimizer regressions, retained native/workflow/comparison evidence and tracking. Design remains DRAFT preliminary PROTOTYPE.

Checked 12 support tests,137 module-layout tests, all six CTests, zero-overlap native geometry and Geant4 initialization (zero events,FTFP_BERT,seed42). Dashboard validates and builds. Source tree and installed ACTS environment differ by existing user changes, left untouched. Spack registry fingerprints are stale; actual DD4hep/ROOT/Geant4 runtime was verified. No shared dependencies changed.

The full 18-disc table is in the retained results and PR description. First-disc/barrel-turn clearance is 2.1 mm; transport volumes/masses change with moved collectors. Inherited thermal/adverse service failures remain open.

Shared app turn usage is assigned once to a canonical shared record, never divided or duplicated across PR tasks. Exact usage recovery is required at completion; active final counters remain unavailable until turn closure.
