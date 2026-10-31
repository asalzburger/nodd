# SESSION-2026-10-31-strixel-pitch-study

## Selected human request and scope

The user requested: “make a truth taking study, where you change the short strips
to 1 mm and 1.5 mm and 2 mm in the longitudinal direction. Estimate how much
cabling and power that would save in space.” Interpreted as truth-associated
tracking sensitivity, with the current 0.5 mm control. Fine pitch remains75µm;
local-v means barrelz and endcapradial, with both endcaps counted. The explicit
study instruction authorizes isolated PROTOTYPE variants. No baseline change,
merge, external notification or physical design approval was requested.

## Source and environment

Started from main1dff0452ed1e7ac24d7b746fccc02ee15df5258d in a separate task
worktree, branch codex/strixel-pitch-truth-study. Read AGENTS/PROJECT, relevant
DES007/010/020/021/040/041 and repository specialist skills. Spack fingerprint
preflight exit2 means the old registry is unverified; actual existing runtime,
Spack specs and sidecar imports passed. No shared installation was modified.
Native source8b7c147, later main analyzerc2453e9 and Gaussian control58f49b9
remain distinct. Loaded binary/content hashes are retained separately from
ACTS source355ea684 and adapter checkout530080cf. Actual runtime:Python3.14.5,
DD4hep1.38, ROOT6.40.04; installed Geant4 was not used for transport. Analysis
reuses the existing isolated NumPy/Matplotlib/unrooted environment. Full command
arguments and native run-source pins are in retained native inventories.

## Specialist assignments

Explicit role mandates were supplied through prepared prompts, not claimed as
native profile loading. SysArch01 derived services assumptions; PhysVal01 defined
the paired truth benchmark. SoftEng01 implemented and executed the native scan.
SysArch02/PhysVal02 reviewed f8967e9. PhysVal03 examined explicitly uncommitted
immutable analysis blobs, with snapshot hashes preserved. PhysVal04 verified
committed remedies atc2453e9. PhysVal05 investigated the high-pT response effect;
SoftEng02 independently inspected the cluster/covariance code. PhysVal06 checked
the separate Gaussian-control source at58f49b9. SysArch03 independently reproduced
1179numeric service fields across24cases, all9source/input hashes,5service tests
and separate load/rounding/route/material assertions. SoftEng03 implemented and
executed the Gaussian diagnostic after a source-commit barrier. Final retained
result assessment follows the evidence commit. Role results are curated beside
this record; no agent assessment grants human design acceptance.

The first assignment-prepare attempt used an absent DES010filename and exited1;
the existing service-corridors document was used before dispatch.

## Corrections and controls

PhysVal02 caught residual-sign metadata: arrays were always fitted-minus-truth,
while initial reports advertised the reverse. Source/test correction8b7c147
preceded all production. V1/V2pilots remain excluded qualified controls.
SysArch02 requested separate effective Cu/PI/internalvoid litres; implemented
before final service evidence. PhysVal03 caught no-fit flag masking, incomplete
matrix acceptance and empty comparison acceptance. Corrected with regressions,
strict12case/20k gates, canonical source/configuration checks and source-freeze
checks. Added explicit full bootstrap replay and paired fit-fraction auditing.

Native preparation omitted the imported metrics.py fingerprint. The exact
8b7launch blob deaf54c0d2d259738f07b219a5c802e347c4829c has SHA256
 a03568236338706cf59d63d81ab9c76a45ca58493704e4ec679b9806382f7f31.
Launch/completion bytes match. Retention explicitly fingerprints it and exactly
recomputes every residual/pull/flag from full truth/fitted/covariance before
compact retention. Preserve the original metadata gap and supplementary proof.

## Decisions and outcomes

Native scan:12×20000processed case-events, pT1/10/100GeV, constant3T, one origin
muon/event, random charge, uniformeta[-4,4], fullphi. Three concurrent one-thread
processes. All pitches share exact generated/all-hit/primary-hit payloads at each
momentum; native geometry/material/selection stay invariant. Only12384strixel-v
grids differ; all seven sensitive-system counts match the balanced tracker.
Every1GeVcase has19995finite/native-matched fits and the same5selection losses;
every10/100GeVcase has20000. No post-selection fit failure/native invalidcovariance.
Total239980finite/native-matched fits from240000case-events; pitches are paired,
not independent physics samples. Full55file/output hashes and actual per-sensor
configuration comparisons pass.

At100GeV, |eta|<1, the native geometric z0core ratio at2mm is0.769±0.014,
while its uncut SD ratio is~0.939 and pull SD falls0.543→0.458. All5036events
fit at everypitch, so this is not survivor bias. Source/pilot inspection shows
native merged-cell path weights couple both coordinate covariances: fine-u
positions stay bitwise identical but mean fine-u variance changes~12.8% asv
coarsens. Digital flags do not establish an independent binary response after
merging. Coupling is demonstrated; its complete causal contribution is not.
These results do not show improved physical sensor performance.

Separate, prospectively frozen Gaussian diagnostic:4×5000cases at100GeV,
all measured-coordinate widths=pitch/sqrt(12), no merging, 1D long strips.
Native source58f49b9 captured by all4launches before parent advancedHEAD.
Everycase has5000finite/native-matched fits,73907simhits/measurements,0lost,
0nativeinvalidcovariance. All517888stored marginal variance checks pass.
Exact truth/simhits match acrosscontrols and original geometric first5000events;
original twelve-case outputs/fingerprints remain unchanged. Native edge draws
have at most11attempts; actual retry counts unavailable, so0lost is not0retries.
All-axis response replacement tests model dependence, not a single causal term.

Gaussian central100GeV width ratios (paired400-draw SE):z0=1.106±0.019,
1.117±0.022,1.132±0.024 for1/1.5/2mm;theta=1.159±0.023,1.216±0.028,
1.229±0.031. Central longitudinal pull widths are near1; momentum pulls retain
substantial nonclosure. Native geometric1/10GeVlongitudinal changes are small;
momentum-width summary changes stay percent-scale. No physical calibration,
occupancy/pattern-recognition claim, or smaller-service-material benefit enters
the fixed-material study. No preferred baseline is selected.

Service scan:channel reduction50/66.7/75%. Existing unqualified electronics
comparators7.8W and31.7288W/module, channel-dependent fractionf=0/0.5/1,
fixed2W/moduleHVleakage and5W/network boards, recomputed local12Vrail loss.
Forf=1 modeled heat savings49–201/65–268/73–301kW; these spans compare proxy
normalizations, not physical bounds. Longer-cell capacitance/ASIC power unknown.
Withf=0.5 heat savings24–101/32–135/36–151kW; withf=0 zero.

Unchanged hardware saveszero installed cable/cooling/tray/electronics space.
Conditional redesigned power harnesses remove gross242.734/273.421/273.421L
for1/1.5/2mm atf=1, keeping fibres/pipes/trays fixed. Envelope includes internal
void; Cu/PI/void reported separately. Requires new conductors/fanouts/connectors/
LV-HV-control topology and engineering. Area-equivalent worst-sector demand
75.590mm baseline already exceeds actual73mm allocation; conditional demands
46.717/41.000mm leave26.3/32.0mm area-only headroom before installation reserves.
No qualified current capacity, narrower corridor or reduced pipe diameter follows.

## Checks and evidence

Paired JSON lists actual checks. All22portable tests pass. Full native retention
replays every observable/flag exactly; point audit checks76032uncut quantities,
all fractions/differences and24servicecases. Full deterministic400-draw bootstrap
replay passes for both native and Gaussian evidence. Twenty-sixPNG/PDF scientific
figures use actual unrooted ScatterData rendering plus Matplotlib. Visual QA:
services,100GeVnative absolute/ratio,fit fractions andGaussian ratio. RawROOT/full
covariance remain ignored; compact all-generated event arrays, native inventories,
CSV/profiles, source/runtime/verification supplements and figures are retained in
DES042. Repeatable native launcher has explicit suppliers, fresh tags, two modes
and dry-run checks. Source, data, report replay and scientific records remain
under final exact-revision assessment before delivery.

## Usage

No exact client-reported per-turn or subagent token observations were exposed.
Usage remains empty, with missing coverage explicit; no estimate or allocation.
This bounded task does not reuse historical PR97 counters. The client/thread
identity and actual conversation start remain unavailable. Session summary and
interaction synchronization are recorded at closeout.
