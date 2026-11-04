# TRUTH-PhysVal-01 — preliminary independent assessment

Reviewer: separate read-only PhysVal context; no native execution or source edits.
Pinned nODD eb86998ad5d42c37bf7d244063c575f93b0c42a3 and ACTS
355ea68493b326956756c9386d2fd9eaf9328568. Concurrent dirty native work excluded.

Benchmark/reduction definitions suitable for proceeding conditional on correcting
and auditing the independently trained hit-error table. No human acceptance.

High findings in ACTS Examples/Scripts/Digitization/error_parameterisation.py:
lines153–158 append exact-size populationSD before lines174–184 pool the tail;
the stored value is never recomputed. Default cap5 stops at exactsize4 while
native GeometricConfig.cpp20–24 applies final entry to every size>=4. Missing
internal cluster size can produce NaN. Executing exact loop with I/O stubbed:
early-break1.0 versus correct pooled2.9154759474; capped4.0 versus pooled4.5276925691;
missinginternalgroupNaN.

Recommended repair: retain raw table,traininginput/source/config hashes; preserve
vectorlengthK and recompute exact sizes belowK and pooled>=K finalgroup. Explicitly
merge unsupportedtails or reject; preservecounts,means,populationSD anduncenteredRMS.
No residual clipping or trackpull tuning. Native JSONreader squares rms once.
Post-clustering adapter must prove actual writtenvariance equals frozen lookup
RMS² includingoverflow and1D,with IDs/positions/associations unchanged. ModuleClusters
recomputes geometricvariance; loadingtablealone is insufficient evidence.

The script's rms is centered populationSD,not sqrt(mean(residual²)); retain bias
separately. Per-volume/cluster marginals omit incidence dependence and correlations;
neither backend is guaranteed unittrackingpulls. Eventbootstrap conditions on frozen
table and excludes training/detector-model systematics.

Checks actually run: all7 pinned metric tests; independent finite-difference pT
Jacobian for both charges; synthetic6-event attrition with4selected,3attempts,
2tracks and1invalidcovariance preserves2/6 denominator,1fitfailure,2unselected.
Verified ROOTwriter branches and writeCovMat requirement. Existing analysis Python
NumPy2.4.6/pandas2.3.3. RequiredSpacksourcepreflight unverified; no dependence on native
runtime in this assessment.

Final exact-revision native/data/figure assessment remains outstanding: map/geometry
hashes,3T consistency,dimensions,corrected association/dedup,actual trained covariance,
all six outputs and numerical summaries. Origintruth,phiwrapping,pTcrosscovariance,
failuredenominators,uncutSD/RMS/central68 and nullundersampled bins were consistent
with the stated definitions. No acceptance threshold or design approval invented.
