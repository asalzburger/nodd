# Tracker reconstruction baseline approval — PR107

On 2026-10-30, human reviewer **asalzburger-review** approved revision
`78d22297e2518ef674ebf1601215fd17c6b93b71` as the current tracker reconstruction
baseline. The [public review](https://github.com/asalzburger/nodd/pull/107#pullrequestreview-5713182516)
records approval of the tuning, cross-checks and Geant4/Fatras comparison. The
user separately confirmed the PR and reconstruction tuning/cross-check approval
and requested final merge accounting in the project chat.

The approved setup uses the balanced PR104 tracker, constant 3 T, frozen
Gaussian digitization, measured-hit GBTS with `pt4-nominal-triplet`, hit-estimated
seed parameters, all-system CKF and ambiguity resolution. Its retained evidence
includes the original [Fatras muon benchmark](tracker-reconstruction/results.md)
and [Fatras electron / Geant4 muon, electron and charged-pion comparisons](tracker-reconstruction-species/results.md)
at pT 1/5/10/100 GeV. The original muon-selected seeder configuration remains
frozen across the species comparison.

This is human technical approval of the reconstruction setup and its recorded
benchmark. It does not remove the electron momentum/charge failures, pion tails,
single-particle scope, unmerged Gaussian response, species fit assumptions,
transport limits or detailed-Geant4/effective-ACTS material differences. It does
not assert calibrated electron errors or precision shower validation.

DES041 remains a DRAFT / isolated PROTOTYPE under the separate detector-design
lifecycle. No formal engineering sign-off, whole-detector acceptance or review
of future source changes is inferred. Historical report headers describe their
generation-time review state; this record supplies the current human technical
approval. Merge status remains separate.

The [merge-preparation journal](../../logs/codex/SESSION-2026-10-30-tracker-gbts-merge-preparation.md)
records exact closed-turn token ownership, exclusions, interactions and checks.
