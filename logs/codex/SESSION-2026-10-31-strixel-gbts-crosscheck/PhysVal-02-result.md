# STRIXEL-GBTS-PhysVal-02 — frozen implementation assessment

Independent read-only PhysVal child `/root/strixel_gbts_physval`, explicit mandate
fallback. Reviewed exact `8c45136098d1e4d407c4d2f96e3590bb78eb6b75` and all ten
pinned hashes. No files changed, native runs started, further agents delegated
or human acceptance inferred. HEAD remained fixed. Coordinator-owned journal
and assignment changes excluded from scientific evidence. Usage unavailable.

## Findings and disposition

**No issue requires native production to stop or restart.** Two analysis-only
corrections remain in the reviewed commit:

1. **Medium:** analyze.py503–510 publishes paired bootstrap[0,0] when there are
   zero discordant success statuses. Independently reproduced with1000synthetic
   paired events. This is empirical degeneracy, not population equivalence.
   Recommended remedy: degeneracy flag, exact one-sided95 upper
   `u=1-0.05^(1/N)` on discordance and conservative pointwise contrast[-u,+u].
   AtN1000,u=.00299125=0.2991percentagepoints. This correction was acknowledged
   but absent in the reviewed commit.
2. **Low:** analyze.py550–551 labels summed per-event total-count deficits and
   excesses as measurementloss/gain. Simultaneous removals/recoveries can cancel.
   Rename as net count differences or implement physical multiset differences.
   Existing index-free physical fingerprints already detect changed event
   payloads correctly. No native rerun needed.

Continue frozen native matrix; correct analysis/reporting and obtain separate
exact committed full-evidence review. Neither this review nor numerical checks
establish full-production outcomes, physical calibration, acceptance or sign-off.

## Scientific assessment

Physical-system/ACTS-volume scaling changes only systems4/5 coordinate1sigma;
source table copied. Baseline equivalence precedes scaling, other configured
widths fixed. Native dimensions/variances checked by unchanged classifier.
Appended writer preserves prior RNG slots. Effective GBTS configuration,
hypotheses/electronone-way policy, all-event counts, active-sensor mapping and
strict ambiguity convergence have explicit gates. Pairing distinguishes native
JSON records, full persistedfloat32hitpayloads, index-bearing ordered seed
inputs and index-free coordinate multisets. Joint event bootstrap, common-success
controls, >=30finite rule, central68.268949% widths, truth-minus-fit signs and
uncut tails are coherent. No unsupported relative-pT pull is fabricated.
Bridge.py20–46 joins unique events and compares every original observable,
shape/NaN mask; production loop records all20seed/profile/reference identities.

## Actual independent checks

- All28new tests passed; all ten pinned input hashes matched.
- Pilot exact--verify reproduced statistics/bootstrap/Markdown.
- Every stored prepared-input/output hash matched for eight native smokes.
- Direct equality for all25ROOT branches across available pitch pairs:
  muon26rows, Fatras electron34, Geant4 electron408. Persisted writer precision
  only, with documentedfloat32limitation.
- Fresh native reductions reproduced all35/42/42 original portable observables
  in muon/Fatras-electron/Geant4-electron0.5mm bridges, includingNaN masks.
- Native target variances exactly match effective tables: Fatras electron
  exercises14system5measurements/case; Geant4electron26system4and140system5.
- Session validator passed217records. Pilot efficiencyPNG inspected.

Smokes record HEAD96748307ef5b0f5bee21051df91e56d8b2c4d99d with explicit dirty
source hashes. Their runtime.py hash equals the reviewed implementation
346e0fe6631e777f271642b5aaa25af7dc7bd271c8bd7961ac9e309d3d7c7ce7.
Two-event muon sample has only pixel measurements: plumbing/pairing check,
not observed strixel sensitivity. Electron smokes do exercise strixels.

Extra uncommitted inputs: native-smoke-v2 runreports/events/hits/native sensor
reports/error tables and recorded manifests; analysis-pilot-v2 inventory,
profiles/results. Inventory hash4b716a4359f467d09d52197ad8d5b05ece22f685e0f057467866f3e317b24323;
profiles hashcbebb76d83cdc48814d139e1814a5fe8080f807f7b5c8a07bc74ba50e940b4e1;
Markdown hashd4395e04fba03380758131ce95df28791da01f620f6628f2ec25bad5298b849e.
Same-revision bridge tests, frozen classifier/campaign/reference inputs inspected.

## Coordinator remediation (after review)

Both findings corrected in analysis-only working files while native HEAD stayed
8c45136: net count fields renamed/qualified; degenerate contrast flag, exact95
zero-discordance probability bound and conservative pointwise contrast added.
Reference-versus-itself is marked identicallyzero. A new adverse test passed;
all18analysis tests pass. These changes are not asserted as part of PhysVal02's
reviewed commit. Final exact-evidence review must verify the corrective revision.
No simulation, response, seeds or reconstruction source changed.
