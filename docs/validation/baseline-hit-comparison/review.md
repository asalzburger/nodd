# Separate PhysVal assessment

HITCOMPARE-PhysVal-02 reviewed0aec2ef08553a2fbc24867a7cff4fd4ada0b67ae
on2026-11-03. No material blocker was found for qualified geometric characterization.
This was a separate agent context with an explicit PhysVal mandate, not human acceptance.

Actual independent checks:

- All5 focused offline tests pass. Live counting/installation, reduction,
  plotting and control sources reviewed; fulltouchable paths and perray sets
  preserve placement identity and zero-crossing denominators.
- Both raw100000-ray CSVs and metrics hashes checked. All80-bin means, zeros,
  componentcovariance and samplingvariances reproduced within1e-13. Generated
  ray fields match exactly between old/current.
- Totalmeans14.07273old/14.93379current; pairedchange+0.86106 ±0.00424096
  finite-raySEM confirmed. Longstrip counts exactlymatch perray.
-300rays×all32materialbranches independently checked exactlyequal; ROOT hashes
  match the noninterference report.
- Independent finitebox controls repeated for256rays perbaseline, no component
  mismatches; geometryhashes and45646/46682 sensor inventories checked.
- Both pinnedPNGs visually inspected: requested stacked/individualmarker
  alternatives, blacktotalmarkers, commonaxes and requiredpalette present.
- Compact, materials and allfivefactory hashes match committed material
  referenceprovenance; executed analysis-source hashes match the pinnedsource.

Direct liveGeant4touchables resolve the earlier rounded-position identity concern.
Fresh matchedsamples avoid inferring the original legacyrecording's unknownseed.

Limits: sensitiveVOLUMEcrossings includechips/overlaps/bothstripfaces and finite
edgegrazes; these are notACTSplanehits or detectorresponse. Observernoninterference
covers300currentrays; finiteboxchecks cover bounded samples. No splitpositive or
zero-lengthsensitive cases occurred, so those paths lack an independent native
fixture. Neither strixelpitch nor services are isolated as causes. No files
changed and no native jobs rerun by the reviewer; no design/human acceptance.
