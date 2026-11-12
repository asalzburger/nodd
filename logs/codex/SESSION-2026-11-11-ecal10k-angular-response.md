# SESSION-2026-11-11-ecal10k-angular-response — 10k-electron angular response

## Scope and selected request

User request, paraphrase: replace the earlier large-sample estimate with 10,000
electrons at E approximately 10–80 GeV, flat phi and eta -3 to 3; use 12 threads
on the 24-core local CPU; check disk and reduce the count only if necessary;
plot sigma(E)/E in ten |eta| bins and ten folded-phi bins.

The coordinator interpreted energy and eta as independent uniform distributions,
retained the thread's ECAL-only, zero-field PR133 prototype boundary, and stated
the event-normalized response definition before production. No geometry,
materials, readout, sensitivity or design approval state was changed.

## Sources, revisions and execution

The dedicated task clone starts at 7ba71eeedc00c497bd4dc4168a9272039b300d8b.
It preserves all existing source checkouts. The retained compact/materials from
PR133 were generated at 3dab2346c4a08fd24898a7842906601884708a7d and verified
by their original hashes. The freshly built geometry library is byte-identical
to PR133 (SHA-256 c0098ae4b5e7a453f46d8d118a82ac6a9c6a57a219f2af641e1c4e653b1e1dab).
The runtime doctor reverified DD4hep/DDG4 1.38, Geant4 11.4.3 and all 12 datasets
after the Spack registry's setup/lock fingerprint warning. No shared dependency
was installed or modified.

Commit 48d1b1b09ccbd10cf8862152054244bff543536e freezes the prospective
protocol and producers. Review corrections were committed at
a53895fa47d0452fd031f51e54c7a2288861838c before production. A fresh production
input manifest records that revision; it reproduces the exact same primary bytes
as the pilot. Analysis provenance/replot support was committed at
e097af85513247dfdd93207b00914ee0cab50156. Results and figures reviewed at
d7cae98616dac99b9459055aeb54525082405c08 retain both distinct source revisions.

The input is one stable PDG-11 electron at the origin per event, independent
uniform total energy 10–80 GeV, eta -3 to 3 and phi -pi to pi. Python input seed
is 13310000. A short-format uppercase `.HEPEvt` file stores momentum computed
from total energy and the declared electron mass. DDSim uses 12 workers,
FTFP_BERT, 0.7 mm cuts, the retained 5 mm sensitive-silicon step policy,
MixMaxRng seed 133812341 and event-ID-based reseeding. Native worker begin/end
records verify each worker's SD roles, limits, cuts, field, RNG and event count.
One fixed ROOT output is used; readback is indexed by event ID, not entry order.

A 24-event MT pilot passed with every worker used. A separate serial control
produced exactly equal per-event summarized deposited energies, responses and
collection counts by ID. Maximum signal difference was zero. This does not
assert byte-identical ROOT files or equality of every individual cell payload.

Production completed 10,000 events in 585.693669 s wall and 6066.616829 child CPU
seconds. Peak child RSS was 2,546,319,360 bytes (2.371 GiB). Compressed ROOT output
is 12,604,492,755 bytes (12.604 GB). All twelve complete workers processed
812–868 events each. Complete readback passed for IDs 0–9999, 6,289,322 valid
ECAL cells and all primary inputs; maximum primary energy error was 4.3e-14 GeV.
The exact ROOT, receipt, primary and event-ledger hashes are in the compact result.

## Analysis and outcome

Define R=sum(all raw BARRELHits and EDGEHits silicon deposits)/primary total
energy. Report sample SD(R)/mean(R), retaining valid zero responses and all
geometric losses. Ten |eta| bins cover 0–3. Sixteen identical azimuthal replicas
give a signed modulo-22.5-degree fold into [-11.25,+11.25) degrees, with ten bins.
No additional reflection fold, angular calibration or response cut is applied.
This is spectrum-averaged raw visible-response width, not intrinsic fixed-energy
reconstructed calorimeter resolution.

Five thousand joint whole-event bootstrap replicas, seed 1335000, give finite
95% percentile intervals and a finite symmetric positive-definite 20x20 width
covariance. Every projection counts all 10,000 events. Forty-two valid zero
responses are retained, all in the seam-adjacent phi bins. Their association
with low mean response and large inclusive width is reported without attributing
the full effect to those zeros or to a specific mechanical component.

Main and mean-response control figures were visually inspected. The final PNG
includes its applicability caption within the image bounds. Pure plotting uses
the existing ACTS-nODD Python 3.14.5, NumPy 2.5.4 and Matplotlib 3.11.2; native
Spack Python handles ROOT/EDM4hep readback. No reconstruction or digitizer was run.

## Bounded specialist assignments and handoffs

The `nodd-coordinate`, `nodd-review-validation` and `acts-spack` instructions
were read. PhysVal and SoftEng received explicit complete repository profile
instructions through generic subagents; native profile loading is not claimed.
Both worked read-only with no owned write files or nested delegation. Assignment
contracts were recorded in this journal before dispatch; earlier committed
versions retain the original detailed source/file/completion contracts.

- ECAL10K-PHYSVAL at 7ba71eee: prospective estimator, uncertainty/zero treatment
  and actual fold symmetry from DES-030/031, existing response protocols and
  replica/folding code. Returned the adopted R-width contract, bootstrap and
  signed-fold rules; no human approval was inferred.
- ECAL10K-SOFTENG at 7ba71eee: installed/pinned DD4hep input, locking, event
  seeding and worker audit/output route. Returned HEPEvt and worker-audit plan;
  no simulation was delegated. Its trailing-true CLI suggestion was corrected
  from actual parser evidence before the successful pilot.
- ECAL10K-REVIEW-PHYSVAL at 48d1b1b, remediation verified at a53895fa:
  reviewed protocol, angular_analyze.py and mathematical controls. Identified
  nullable mean-plot guards and audited-receipt binding; both were fixed.
  Five tests and a separate synthetic joint-bootstrap control passed.
- ECAL10K-REVIEW-SOFTENG at 48d1b1b: reviewed runner, steering, native audit,
  CMake and pilot records. Independently checked hashes, twelve worker totals,
  shuffled output identities and exact serial/MT summary equality. Identified
  fresh-input provenance and receipt binding; both resolved before production.
- ECAL10K-FINAL-PHYSVAL at d7cae986: independently recomputed all 20 point
  statistics/quantiles and assignments from the hash-bound event ledger;
  checked intervals/covariance, denominators, zeros and both committed figures.
  No actionable findings. Did not rerun Geant4 or all bootstrap replicas.
- ECAL10K-FINAL-SOFTENG at d7cae986: independently checked input/geometry/source/
  receipt/ledger bindings, all worker audits, all 10,000 ledger identities,
  bin moments, resource values and exclusion of raw data from new Git objects.
  No actionable findings. Did not repeat native ROOT readback or its 12.6-GB hash.

Child task addresses are `/root/ecal10k_physval` and `/root/ecal10k_softeng`;
these are exposed assignment addresses, not invented persistent client IDs.
All advice/reviews are agent technical assessments, not engineering sign-off.

## Disk policy and retained artifacts

Initial df reported about 408 GiB; preparation's Python disk query exposed about
412 GiB. The pilot projected 11.98 GB. A doubled projection plus 30 GiB reserve
required 52.31 GiB, so all 10,000 events were retained. The runtime reserve was
never breached. Post-run df reports about 401 GiB free.

Raw ROOT data, HEPEvt/input/event ledgers, logs, builds, caches and control plots
stay local and ignored under build/ecal10k. Only recipes, a 45.7-KB binwise
summary/covariance, final figures, project/software records and this curated
journal are proposed for publication. No local sample is uploaded to Sites.

## Checks, failed attempts and corrections

Exact results are in the paired JSON. Initial native-audit compilation required
its DD4hep factory namespace correction. The first pilot rejected the CLI's
trailing `true` before generating events; the failed receipt/log remain in
pilot12, while successful evidence is in pilot12-v2. No failure was erased.

The native Python's first pilot analysis computed statistics but failed only
at Matplotlib import. The existing ACTS plotting environment rendered that same
summary, including undefined-bin controls, and performed production analysis.
The initial font-cache warning was resolved with task-local MPL/XDG cache paths.
A system-Python image check lacked Pillow; the existing plotting Python supplied
it without installation. These were tooling corrections, not physics changes.

The project-record gate first found the pre-existing missing historical commit
78bc60bb. Its actual object exists in another local nODD object store; this task
clone now reads that store through an additional Git alternate. No source
checkout or branch was changed. The next gate found PR129's existing fractional
collection timestamp; normalization from 2026-11-11T07:24:35.326845Z to the
required whole-second UTC format retained its original value in Git history.
Full project validation passed 104 tasks, 54 documents and 24 review rounds.

Software inventory refresh/check passed. The first token-site output path was
outside the allowed _site location, then corrected. A stale interaction gate
was resolved by refreshing PR133/issue131 via connected GitHub reads, capturing
only public schema-selected fields, and synchronizing derived journal links.
Session, interaction and token checks/build are repeated after final curation.

## Publication and accounting

The completed review package is [draft PR134](https://github.com/asalzburger/nodd/pull/134),
stacked on the still-open PR133 branch. The new-object scan inspected 28 blobs,
largest 284,709 bytes, and excluded all ROOT/HEPEvt/event-ledger/build/log paths.
The initial default-sandbox SSH push failed DNS; the authorized network push
succeeded. The connected GitHub integration returned403 when creating the PR;
the existing authenticated gh CLI created the draft successfully. A connected
read verified draft=true at published head a5c17c5f2e7b6c50e9dc7528f602305ae8baa207.
The final metadata/interaction closeout is a normal fast-forward; the captured
head is a dated snapshot, and Git history locates the subsequent closing commit.
No ready-for-review transition, merge or full-sample upload was performed.

Exact client-reported per-turn counters and stable turn IDs are unavailable for
parent and specialist contexts. Usage remains empty, meaning unknown rather
than zero. The historical project summary has 511 observed turns; those totals
are not allocated to this task. No model usage is estimated or duplicated.
