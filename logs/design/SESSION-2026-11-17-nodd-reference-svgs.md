# Standalone nODD response SVGs

User: "Looks good - leave the report as is, but make two separate SVGs: SD(R)/mean(R) as is, but remove the ODD, only keep nODD versions; Underneath: reference plots in [0,1][1,2][2,3] over the same width, showing where the SD(R)/mean(R) was drawn from."

Start source d04614575e8fc3aed41ed79798def3fc461e3dc6; separate codex/nodd-reference-svgs worktree. Existing PR145 remains open/ready on main; this is its authorized figure follow-up, without another geometry/report edit or GitHub merge. Freeze every existing tracked report-directory file and the PDF byte-for-byte. New outputs live in a standalone/ subdirectory.

Interpret the three intervals as absolute primary pseudorapidity bands [0,1),[1,2),[2,3], covering all matched10000primaries once. FirstSVG preserves the original three fine0.05-bin nODD curves/pointwise intervals and axes, removes only ODD reference elements, and repacks the legend. SecondSVG has the same1000unitwidth, three adjacent band reference histograms of R divided by its own model/band mean; raw meanR/sampleSD and CV/zero/overflow counts are reported. Unit-mean rescaling preserves each bandCV; no calibration/fits, no newMC/bootstrap. All-event normalization, explicit tails/overflow; log-y displays sparse tails without replacing empty bins with events. Broad-band referenceCVs are context, not the fine-curve point estimates.

Derive histograms from the exact original/staggered Si-W saved-signal and LAr400savedH ledgers already hash-bound in response_comparison.py. Preserve H/Etrue and every zero. Fixed display edges of normalized response0..3 in0.025steps; explicit overflow above3, no truncation in moments. Bin3 includes endpoint3. No accepted report/figure/source/provenance files are changed.
