# Conditional LAr barrel/endcap gap: matched 10k electrons

2026-11-14. **PROTOTYPE / prospective response-sensitivity study.**
Governing inputs: DES-032/DES-033, the side-neck proposal in PR142 and the
standalone material-preserving routing prototype in PR143. User requested the
standard electron comparison and corrected the population to **10,000**.

## Physical question and authorization boundary

**FACT about the current prototype:** PR143 retains the existing calorimeter
coordinates. It validates standalone cooling-pipe shapes and material, while
its unchanged-ECAL diagnostic finds existing-pipe and closed-wall contacts.
It does not implement a smaller calorimeter gap.

**NODD DESIGN CHOICE — isolated numerical experiment:** test the proposal's
400 mm front warm gap against the existing 800 mm gap. Translate each complete
endcap 400 mm towards the interaction point, at both signs of z. Preserve its
internal dimensions, frames, constituent materials, sensitive sampling, local
readout coordinates/IDs and local services. The barrel stays fixed. This reduces
the active axial separation from 1100 to 700 mm. No default or production layout
changes. The user's response-study request authorizes this conditional geometry
experiment; the proposal's unresolved engineering prerequisites still apply to
integrating or adopting the shift.

Do not cut walls, delete service material, fabricate cable/jacket constituents,
or place the unresolved PR143 pipe overlay. This is a gap-only ECAL response
study with the current local service representation. It cannot establish the
performance of a fully engineered rerouting, an attainable minimum gap or a
complete detector. Tracker, beam pipe, solenoid, HCAL and FCAL remain absent,
and B=0, consistently with the retained standard sample. The prospective forward
collar, external pipes and installation interfaces are outside this experiment.

Only top-level endcap placements may change. Parent-relative daughter placements
and local segmentation reference tables must remain unchanged. Verify the exact
allowed XML differences, component material inventories, transformed native
centres, root identities and complete ECAL overlap scan at 10 nm before showers.
Reject missing/ambiguous roots, unexpected pose changes, stale artifacts and
overlaps. Moving an endcap is a declared sensitivity parameter, not a material
or response tuning exercise.

## Frozen input and transport

Reuse the exact standard 10,000 origin-electron primary records: independent
uniform total E=10–80 GeV, eta −3…3, phi −pi…pi. HEPEvt SHA256
`44bf93acf342ccfd9f461423ea12992ab1cab9046f84841ff8853ed763aad389`;
truth-ledger SHA256
`b53199a644e659eb6efdd4684b824c6b85f66e0968686b0af3482e93b56c30b1`.
Reference: [standard LAr protocol](../lar10k/protocol.md).

Retain Geant4 11.4.3 / DD4hep 1.38 / ROOT 6.40.04, FTFP_BERT, 0.7 mm
production range cuts, MixMaxRng, event seeding, seed 133812341, twelve workers
and the predeclared maximum charged step of 5 mm in active LAr (preserving any
tighter native limit). No quenching, noise, calibration or digitization added.
Verify actual native material/cuts/field/process/readout audits and saved
primaries/hits. Serially preinitialise both volume managers before MT workers.

Use the published standard LAr 10k run as the reference only after verifying
its complete receipt, actual ROOT and event ledgers, worker audits, exact input
hashes, physical compact and library/source identity. Reusing verified reference
events is distinct from rerunning them. Otherwise regenerate the reference with
the same declared policy. Before the candidate production run, require serial
and twelve-worker 24-event controls with exact event/cell/deposit/position
agreement, plus a 100-event production-policy pilot and saved-data readback.
Any failure is retained and corrected before production; no gate or physical
parameter is changed to select a favourable shower result.

## Observables and inference fixed before new showers

Per event use R = summed sensitive ECAL deposit / primary total energy. Keep all
10,000 events, including empty/zero signal, identified by primary ID. The
principal comparison is standard 800 mm versus conditional 400 mm gap; do not
label this as a new LAr-versus-Si–W technology test.

Report raw mean, sample SD, SD/mean, quantiles, zeros and tail fractions globally,
in the original ten equal |eta| bins, fourteen 5 GeV energy bins, sixteen full-phi
bins, twelve signed-eta bins and broad |eta| regions [0,1.2), [1.2,1.5), [1.5,3].
The fixed transition region [1.2,1.5) contains the same 999 primary records and
must be reported regardless of where the smaller gap moves the response dip.
Add a fixed 0.05-wide |eta| projection from 1.1 to 1.6 to resolve that movement;
do not select its edges after seeing candidate results.

Report tails at the common fixed threshold R < 0.5 * standard global mean(R),
alongside the older diagnostic R < 0.5 * each model's own global mean. Name the
denominator and threshold explicitly. Use 1,000 shared whole-primary-event
bootstrap replicates, analysis seed 13001000, for pointwise 95% percentile
intervals and paired differences in means, widths and common-threshold tail
fractions. Evaluate the common standard-global threshold once and hold it fixed
across bootstrap replicates; these tail intervals condition on that frozen
threshold. Preserve covariance across principal global, standard |eta| and fine
transition width observables, with explicit variable order. Matching primaries
does not make the different-geometry showers the same stochastic history.
Zero observed tails, including a degenerate empirical-bootstrap interval, do not
establish exclusion of a nonzero population tail rate.

Widths mix the primary-energy spectrum, angular response, dead material,
leakage and non-Gaussian tails; they are not fixed-energy intrinsic resolution.
Intervals condition on the frozen transport and omit engineering, geometry,
physics-list and electronics systematics. No technology selection, integrated
fit, design sign-off or production acceptance follows from this experiment.

## Retained evidence

Bind generated compacts, native reports, input manifests, libraries, producer
sources, transport receipts, ROOT readbacks and event ledgers with hashes and
exact execution revisions. Keep raw XML/ROOT/events/logs ignored locally. Commit
only code, this prospective protocol, compact results/uncertainties/covariance,
scientific figures, environment and exact reproduction commands. Use the fixed
ECAL colour for both variants, distinguished by line style and clear labels.
Track the bounded task, separate role assessments and available exact usage in
its own paired session and separate stacked draft PR.
