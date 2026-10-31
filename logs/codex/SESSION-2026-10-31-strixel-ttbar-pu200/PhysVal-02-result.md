# TTBAR-PU200-PhysVal-02 — committed native assessment

Independent read-only PhysVal child `/root/ttbar_physval` reviewed exact
`aacf2ba0ab6c42e675959a8cb25c43c0ba7b477f`; all12pinned objects match. Explicit
mandate/review-skill fallback, no native profile loading or human acceptance.
No canonical writes or native jobs launched. Offline analysis/plot code is
outside this assessed commit.

No unresolved native-source/smoke blocker found for the frozen100eventrun.
Earlier gates are closed: runtime explicitly selects transport input while
retaining fulltruth; producer interactiontags are joined throughorigParticleIdx,
with cross-origin barcode merger rejection; initialpositions/ct/origins are
retained, while unsupported truthloc0/loc1 are null.

Full replay covers Particle/SimParticle/Hit state fields, parents/process/outcome,
surface andheavyflavour identity, hitfourvectors/index/order. Dump-byte equality
includes signedzero. Direction const_cast affects only a newly owned mutable
object after finite/unitnorm validation, not a shared/originallyconst object.

Actual independent checks:19runtime/controller tests pass; generation/four
development/finalcommittedbaseline outputhashes allmatch;7586/24908selected
particles and exactpayloads recomputed;201origins/HSlabels/initialpositionct
verified throughreplay. Allfive reconstruction smokes exercise7systems,
105960variance marginals,20896float32measuredpixeltransforms, muonhypotheses and
strictambiguitymaxshared2. Pixels/SP/ordered/estimatedseeds match acrosspitches.
Only16strixelvwidthgroupsscale. Exactpybind3.0.4/ABI11andtaskmoduleSHA
7a1a98faac8a5bff042eb4776f5d2a79629c776ca1294cc547cbfccc7757bef6 verified.
Standalone nodepreflight exit2/unverified; no shareddependencies changed.

Finalcommittedbaseline reportSHA
79526610a0bc5e841ffe221ec3cfb58945b625a95d4282d836c18cd4fd5bd362;
auditSHA96f96895b9656e868e3738766c24d987c997026e162edb7d96798056c6b15a4e.
Oldfourpitchsmokes retain dirtyA734/originalmodule provenance; finalbaseline
uses committed source and stricter finalmodule.

Keep frozenGBTSz0±15mm versusvertexsigma55.5mm prominent if that setup is used;
it constrains inclusiveefficiency. Do not retune during comparison. Retain
qqbar-onlyprocess, approximateFatras, muonhypothesis, Gaussianwithoutmerging,
andupstreamPythiaFPEscope. Productionidentity/pairing, exhaustiveclassification,
eventblockuncertainty andfinalanalysis/figureexactreplay stillrequire finalreview.

## Subsequent coordinator action

Beforeproduction, nativepeer reported unchecked upstreamPythia next() status;
coordinator assigned a minimal failure/origin-coverage guard with valid-event
regression. Optionalhumanpreference was requested about adapting the common
GBTSz0window to the guide's luminousregion. Any subsequent source/window change
is outside this assessed revision and requires separate exact-source checks.
