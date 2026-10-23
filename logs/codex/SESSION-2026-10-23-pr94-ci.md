# SESSION-2026-10-23-pr94-ci — PR94 CI failure correction

## Scope and selected request

User: “There’s a comment about CI failure on PR #94”. Read comment
[6361605900](https://github.com/asalzburger/nodd/pull/94#issuecomment-6361605900)
and job120318707307 in run39924882061. Starting revision
5263d48c211eda91191e9c7470dc4c92dfe0f7ba, branch
codex/muon-dd4hep-prototype, clean working tree. Preserve the PR's ready state,
base, reviewer and design DRAFT statuses. No reviewer message/comment is sent.

## Diagnosis and correction

The Ubuntu24.04/Python3.12.15 job failed only its frozen-export byte comparison:
atan2 reconstructed an angle with a different final digit from macOS. Reproduced
this failure by moving atan2 results one ULP. Retain the byte comparison and
all geometry tolerances. Read source angles directly from compartment.phi_deg,
project with the pinned basis, and evaluate expansion trig/residuals with fixed
60-digit Decimal arithmetic before binary64 conversion. No new dependency or
physical geometry choice. Regenerate compact/manifest; source entity and coil
group records remain exactly equal, with22 templates/936 placements. XML becomes
28,907 bytes; historical evidence retains its original bytes and hashes.

The injected-drift regression perturbs sin/cos/atan2/dist by one ULP and requires
all3 export files to stay byte-identical. The 16 focused controls pass on the
current Python. The same16 controls also pass on Python3.11.15, including frozen output bytes.
This tightly dependent CI correction stays with the coordinator under
nodd-review-validation; no independent specialist assessment is claimed.

## Runtime and delivery

Applied acts-spack. Preflight reports changed setup/lock fingerprints (exit2);
fresh installation checks actually pass: DD4hep1.38, ROOT6.40.04, Geant411.4.3,
DD4hep/DDG4 imports and12 present datasets. These are presence checks, not
checksums. Native checks and1000-event replay pass at clean committed source4605ad6ba160c478a324ca1aa30a7cd3c934cd4e.
No shared dependency installation is changed. Detailed check results and changed
files are in the paired JSON; result commits are recorded only after they exist.

## Accounting and scope

Exact finalized disjoint per-turn counters are unavailable. Usage stays empty,
not zero. Run session validation/summary and token-site validation/build at
closeout; retain prior observed totals without claiming complete coverage.
This fixes software reproducibility for the isolated Air-envelope prototype;
no drift-tube response, engineering sign-off or production integration is added.


## Delivery and retained replay

The source correction is pushed as4605ad6. The clean native replay verifies936
stable IDs,22 shared Solids/Volumes,288 coil primitives and25,248 occupancy probes.
No overlaps at0.00001 mm; native vertex maximum1.0087767680389479e-14 m remains
below1e-10 m. All1,000 gamma events persist. ROOT primary banks and particle
multiplicities exactly match the frozen baseline. Reports, hashes, raw logs and
source-entity/group equality are retained under
`docs/validation/DES-040/dd4hep-ci-2026-10-23/`; old evidence is preserved.

Ubuntu workflow39938029454 passed step15, the previously failing muon export
controls, at4605ad6. Token usage workflow39938029888 passed. The final evidence-only
commit triggers another remote run; terminal status is published in GitHub checks.
The PR description now identifies16 controls and the new committed native replay;
readback confirms the human-selected ready state, base and reviewer stay intact.
No PR comment/reviewer message was sent.

Project/session validation, usage summary and token-site validation/build pass.
Observed totals remain251 turns,870,643,545 input,4,670,671 output and875,314,216
total tokens; this turn has missing counters. The paired JSON lists exact checks.
No new independent review, design sign-off or detector response is claimed.

Supplementary local project-record unit suite was interrupted with exit130 during
repeated synthetic-fixture Git adds (docs input897MB). No failed assertion was
observed; no suite pass is claimed. The canonical record validator passes.
The unmodified full suite runs in GitHub CI.
