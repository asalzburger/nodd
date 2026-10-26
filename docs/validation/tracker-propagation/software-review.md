# Software assessment and corrections

Read-only assignment `TRKPROP-SoftEng-02` reviewed
`b78f754dc15eaa408492aae3e50e8e9fed0ce443` on 2026-10-23. It ran all five then-existing
pure controls in the isolated unrooted environment, independently inspected the
128-probe smoke ROOT files and verified all six recorded artifact hashes. All 128
unique generated identities, source-system sums and requested 1 GeV pT matched.
Core 64-bit mapping and zero-inclusive profile accounting were sound in those checks.
No native runtime was activated and no source files were changed by this reviewer.

| Finding | Impact | Coordinator correction |
| --- | --- | --- |
| P1: `run.py` resolves the venv executable symlink | System interpreter lacks isolated plotting packages; accounting/plot stages fail | `.absolute()` preserves the environment in `e894ded`; subsequent complete native accounting and plotting passed. |
| P2: replot does not verify run status/configuration/artifact hashes | Failed, stale, altered or mixed native samples can receive current labels | `b1edb9c` requires PASS, exact counts hash, matching configuration and common geometry/field/runtime identities; native-start invalidation prevents an interrupted rerun retaining prior PASS. |

The P2 reproduction used valid smoke counts plus an explicitly failed run report
and reached ROOT creation at the reviewed revision. This adverse result remains
part of the record. Later regression controls reject failed reports, altered
counts and mixed geometry. Endpoint controls also reject an interior step/path
abort even when generated identity coverage is complete. All eight final pure
controls passed under the coordinator; these remediation checks are not claimed
as another independent SoftEng review. PhysVal02 separately checked final native
accounting and corrected identity/kinematic contracts.

The earlier write assignment `TRKPROP-SoftEng-01` targeted main
`fbf81c4c72469c1bda0cd6122f9912af6f17228d`. It supplied source-level API findings,
but wrote no files and completed no runtime tests because its escalation waited
about 36 minutes before interruption. Ownership was explicitly suspended and the
coordinator implemented the three originally assigned files. This distinction
preserves the actual authorship and execution boundary.
