# SESSION-2026-11-19-ecal50gev-central — Dedicated central electron response

## Scope and evidence

New bounded user task, separate branch codex/ecal50gev-central and worktree,
starting clean at077696b4da7556a31ad02d656dfa3c0141b07543. Earlier angular plots
and unrelated worktrees preserved. Protocol/primary producer frozen ate3feb05f;
source-level statistical review/correction retained before final analysis. Exact
commits, artifact/library/input hashes and run commands accompany the evidence.
No new dependencies, detector geometry changes or design approval.

## Selected conversation

User, paraphrase: a second set of validation graphs requiring dedicated simulation;
one single-electron central direction,50GeV andeta0.1, in a favourable SiWregion
away from sector cracks; plot raw summed Geant4deposits, deposits/fullenergy and
relative response after accounting for the sampling fraction.

Assistant, paraphrase: run both restoredLAr/staggeredSiW atone geometry-selected
point, sum rawactivebarrel+endcapdeposits, use2000independent calibration and10000
held-out evaluation events/model. Explain the effective response fraction f and
invariance ofSD/mean underconstant scaling before production.

## Assignments and handoffs

[Full bounded assignment records](../../docs/validation/ecal50gev-central/assignments.json)
and [curated technical assessments](../../docs/validation/ecal50gev-central/reviews.json)
retain IDs, explicitfallback roles, exactinput revisions/files, read/write modes,
isolated ownedfiles, questions, deliverables, completion criteria and actualchecks.
No verifiednativeprofileloading or humanexpertapproval is claimed.

CaloTech selectedphi+0.7degree geometrically and later retained its analytical
reproduction CLI. Ateta0.1 this has44/48active reference-ray crossings, tangential
clearance16.797942mm and10.55degree separation from a sector boundary;4axialrowgaps
remain. Phi0wouldcross only22/48. No newshoweroutput was used to choose thepoint.
SoftEng implemented analysis/tests in a disjoint isolatedworktree. Main owned
protocol, preparation, runtime, execution, integration and finalartifactQA.
PhysVal independently assessed protocol, exactstatistical source, seedrepeat
sensitivity and finalnumerical/visual evidence. See separate scopes in reviews.

## Decisions and outcomes

Dedicated origin electrons: totalE50GeV,eta0.1,phi0.7degree. Exactrestored1.8mmPbLAr
and physicallystaggeredSiW ECAL-only compacts/materials and previouslyaudited
nativebinaries reused byte-identically. B0,FTFP_BERT,0.7mmcuts,5mmactivecharged-step
cap,12workers/process. Fourproductioninitial seeds705020/705021LAr and705030/705031
SiW distinguish calibration/evaluation streams. Pilots705019/705029 excluded.

All24000productionevents and200pilotsevents passcomplete saved-primary/canonical-hit
readback, withoutdiskabort orcountreduction. ProductionROOT46,954,104,881bytes
remains ignoredlocally. Both evaluationpopulations retain10000events, allzeros/tails;
neither model haszero-responseevents. NoGaussianfit,digitization,tailcut or
per-eventf smearing. Effectivef=independentmean_cal(S/50), includingcontainment and
deadmaterial; not a separatelyscored materialactive/passivefraction.

LAr:meanrawS8.058386GeV,SD0.217191GeV,f0.1612320463,meanT0.9996010432;
SD(T)2.694143%[2.639379,2.762528]. SiW:meanrawS0.782269GeV,SD0.0251631GeV,
f0.0156327064,meanT1.0008111713;SD(T)3.219290%[3.087020,3.404650].
Intervalsarepointwise95%bootstrap. SD/mean unchanged under1/f; evaluationnotrecentered.
Onlythisfixed-point raw-deposition diagnostic is established, not engineering,
generaltechnology superiority or fullreconstructed-detector precision.

## Commands and actual validation

- acts-spackpreflight warnedoldsetup/lockfingerprints changed; actualrun.shdoctor
  reverifiedDD4hep1.38/Geant411.4.3/ROOT6.40.04,12datasets. ThreefrozenLAr libraries
  load and allSiW/LAr binarySHAchecks pass. Sandboxsysctl/pswarnings retained and
  distinguished from runtimeunavailability. No sharedinstallation modified.
- central_sample.py generatednewfixed primaries on exact auditedmodels; oneprimary
  generator test passes. Both100eventpilots/readbacks pass. Twicepilot-extrapolated
  productionbytesplus30GiBreserve fit; fullsamplesretained. Exactcommands and hashes
  are in protocol/README and executioncontrols. Source/session/analysis additions
  made during transport do not modify monitorednativeproducers or librarybytes;
  actualsource revisions/dirty-state metadata remain in native receipts.
- lar_response/transport.py and angular_sample.py run the six nativejobs;
  lar_response/transport.py audit and angular_analyze.py audit verify all saved
  primaries/hits/workers. Allnative receipts exit0, nodiskabort. Nativeevent logs
  contain noG4Exception/FATAL/ERROR/stuckmarkers in thefourproductionruns.
- Centralanalysis8tests + primarygenerator1 + existingcomparison5:14tests pass.
- Source review foundbootstrap CLI overrides could disagreewithfrozenprotocol;
  a20ae153addsstrictcount/seedbinding and a regressiontest. PhysVal rechecked it.
- Mainindependently recomputed18scalars,6histograms/counts/flows againstlocalledgers;
  allmatch.18x18covariancefinite,symmetric,positive-semidefinite tonumericalprecision.
- IndependentPhysValfinalreview at6d4343d7rehashedall4receipt/ledgerpairs; checked
  all24000populationIDs/points/seeds,18metrics,6histograms and independently
  reproduced18bootstrapintervals,fullcovariance andbothcontrasts. BothPNGs inspected,
  all6exports/hashbindings verified. RawROOThitrechecking is inherited fromfull
  nativeaudits, notclaimed repeatedbythe statisticalreviewer.
- Replotfromcommittedcompactsummary reproducesall6PNG/PDF/SVGexports byte-for-byte.
  Mainvisuallyinspected bothfigures. Softwareinventory andprojectrecord validators pass.
  Session/interaction/whitespace/new-object-size checks performed at publicationcloseout.

## Native seed diagnostic and response

Allfourinitialproductionseeds differ.24,000generatedevents have23,999distinctlogged
internaleventseeds: SiWevaluationevents1920/6331share one, withidenticalsavedresponse
summaries. No cross-calibration/evaluation orcross-detectorseedoverlap wasobserved.
All10000events remain andnominalprespecifiedevent-bootstrapinference isunchanged.
PhysValassessed an explicitlypost-hoc conservative first-order fullydependent-pair
sensitivity: resolution-widthSEchanges below0.0002%relative. This doesnotjustify
resimulation ordroppingrows. It isnot a replacementCI orproof ofPRNGindependence.
TheimmutableRNGdiagnostic hash andseparate sensitivityare retained. Rawhit-by-hit
identityofthispair wasnotclaimed; the relevant savedsignal summarieswerecompared.

## Changed artifacts and tracking

Newprotocol/pointgenerator, analyticaldirectioncheck, compactinference/replot code
andtests, figures/aggregatehistograms/covariance, runtime/direction/seed/execution
controls, independentreview/assignmentrecords and reproductionREADME. FullROOT,
eventledgers,exportedXML,verbose logs andcaches stayignored. See pairedJSONinventory.
TASK-ECAL50GEV-CENTRAL operationallycompleted, DES030/031/032/033 validationreport
linksupdated; theirlifecycle andsignoffstates unchanged. DedicateddraftPRrequired
bythe standinghumanrepository instruction; no ready-for-review ormerge action.

## Token accounting

Exactclientper-turnparent/child token counters andclientidentity areunavailable.
Usageisempty andtaskobservedinput/outputtotals areunknown, notzero. Historical
canonicalowners areunchanged. No estimates, rawclientarchives orprivate modelstate
arecollected. The separate session summary isvalidatedand doesnotallocatehistorical
projecttotals tothis task.

## Draft publication closeout

[Draft PR154](https://github.com/asalzburger/nodd/pull/154) created on the dedicated
branch, stacked on still-open draftPR152. The earlier verified GitHub connector
write limitation uses the established authenticated ghfallback; standing human
publication instruction retained inAGENTS.md. Connector readback confirms draft
state and the exact publishedhead; captured discussion has no comments. No merge
or ready-for-review action. Source/newobject inspection confirms only code,
compactaggregates,curatedmetadata and figures; largestnewpayloads are ordinary
trackingmetadata/PNG files below0.32MB.304sessionrecords validate. Exacttaskinput/output
totalsremainunknown; unrelatedhistorical usage and raw simulationfiles unchanged.
