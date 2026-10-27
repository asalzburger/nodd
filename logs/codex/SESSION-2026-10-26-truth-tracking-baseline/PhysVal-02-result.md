# TRUTH-PhysVal-02 — independent native/training assessment

Read-only at nODD8b7254cfc36e1462088e7d390577a4a29dbf1075 and
ACTS355ea68493b326956756c9386d2fd9eaf9328568. No files changed, native reruns,
builds or nested agents. No blocking finding in frozen table or reviewed native
contracts; final six-run performance assessment remains outstanding.

Independently recomputed all106groups from699273measurements with direct
selections and math.fsum means/centered sums of squares,without reconcile_table.
Counts,exact/tail boundaries,mean,populationSD,uncenteredRMS andtable agree;
maximumSD/RMS residual2.78e-17mm. Complete rawACTS table independently reproduced
exactly. TrainingROOT SHA256:
57432af7115b3ec5a113ac3fd2d5a2f9c82cb187cd4cf8048c5b0504aa030cdc.
Alltable/reporthashes checked.52volumes/90measuredcoordinatepairs match45646
native sensors. Groupcounts3346–44400;no unsupportedtailmerge required. Largest
correctionvolume38loc1:raw0.01020946mm to pooled0.03904524mm.

Actual ROOTlifecycle comparison:210branches in5trees exactlyequal withpairedNaNs.
Generated5,simhits95,measurements80,tracksummary5,audit5. Allcompleteoutput/report
hashes match retained provenance. This comparison predates finalassociation/
covariance changes and usesolderobserverhash; boundedlifecycle evidence,not
full finalexecutable equivalence. Static review supports currentlifecycle.

Reviewed source contracts:
- TruthTracking.cpp119–149:oneordinaryG4run initialization,ProcessOneEvent/
  TerminateOneEvent perACTSevent,serialBeamOn guard,runtermination. Upstream
  Geant4Simulation.cpp110–147 resetsstore/reseedsbeforeeachcall. CLI112–116
  closesinfinally.
- CPP30–64:directresolvedsimhitindex,uniquephysicalmeasurement,timeordering.
- CPP151–169:onlymeasurement/particlepairdedup,before7unique-selection andtruth
  matching; fullmeasurementsimhit contributionsintact.
- CPP73–108:overflowclamp,RMSsquaredonce,independentmarginalvariances; copied
  positions/IDs/indices checkedunchanged; actual1D supported.
- digitization.py26–65:requestedpitches,fullunmeasuredsecondaxisbin,longstrip
  indices=[0],nativephysicalstereo unchanged.
- material_runtime106–149 andPortalMaterial135–145:exactmapreload,originalACTS
  slabsremoved,Geant4DD4hep physicalmaterial retained.
- Same3T providerfortransport/fit;fixedpTperformance,independentloguniformtraining.
  NativeTrackFittingAlgorithm88–103 targetsoriginperigee.
- Exporter independentlychecks everywrittenmarginal againsttable andstates
  uncertaintyconditionalonfrozentraining/model.

Qualifications:trainingobserver/sourceendhashes arelaterinventory,notexecuted
observerbinaryidentity. Trainingpositionsprecededdownstreamobserver/tracking
steps; numericalgroupauditvalid,exactobserverreplayqualified. Table omits
incidenceconditioning/correlations andtraining/modeluncertainty; unitpulls are
not anacceptancetest. Calibratedrunreports retain a native-defaultvariance
string; actualpostclustertable/hash/measurementaudit describeappliederrors.
