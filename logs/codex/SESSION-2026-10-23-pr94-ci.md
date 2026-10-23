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
checksums. Native checks and1000-event replay follow at a committed source.
No shared dependency installation is changed. Detailed check results and changed
files are in the paired JSON; result commits are recorded only after they exist.

## Accounting and scope

Exact finalized disjoint per-turn counters are unavailable. Usage stays empty,
not zero. Run session validation/summary and token-site validation/build at
closeout; retain prior observed totals without claiming complete coverage.
This fixes software reproducibility for the isolated Air-envelope prototype;
no drift-tube response, engineering sign-off or production integration is added.
