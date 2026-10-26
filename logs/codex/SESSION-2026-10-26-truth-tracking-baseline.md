# Gen3 truth-tracking baseline

Human requests both Geant4 and Fatras single-muon truth-associated ACTS tracking
at fixed transverse momenta 1,10,100 GeV, PR100 map and Gen3 geometry, geometric
50x50 micrometre pixels and module-default strips, resolutions/pulls versus eta
and pT. Interpret ODD as the exact PR100 Gen3 tracker so map IDs match.

Start clean merged main709d7fe5e5620305812aff502c3e02b9e7be3347 on branch
codex/tracker-truth-baseline, reusing the previous material worktree/runtime.
DES025 amended before implementation; all characterization remains PROTOTYPE.
Main owns campaign, reduction/plots, records and integration. Delegate native
full-chain implementation/execution to SoftEng, then a separate exact-revision
PhysVal assessment. Assignments prepared and retained before dispatch.

Read repository AGENTS/PROJECT, coordinate/review/evidence skills, DES007/008/025
and ADR008. acts-spack preflight warns changed setup/lock fingerprints. A direct
authorized acts run acts-nodd imports ACTS, Geant4, DD4hep and DDG4; Geant4
11.4.3 reports all12 datasets installed. The helper attempts shared ODD asset
copies, denied by sandbox; do not retry that mutation with escalated permission.
ROOT setup also warns about shell detection. Use the already working isolated
nODD native runtime with explicit activation and hashes for actual campaigns;
an import alone is not a native simulation pass.

Draft configuration:20k one-muon events per backend/momentum, uniform eta[-4,4],
full phi, origin, random charge; deterministic seeds. Field optional clarification
requested:2T ODD example,3T ideal fixture,or finite DES026 field. Default2T if no
preference, with sufficient reply time before final generation.
Short strips75umx0.5mm from DES007C01;long strips80um and one measurement per
physical face from DES008C05/measurement contract. No synthetic stereo.
