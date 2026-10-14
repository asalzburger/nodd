# SESSION-2026-10-14-idres-submodule — IdRes source and clean builds

The user supplied ssh://git@gitlab.cern.ch:7999/asalzbur/idres.git and directed
using that fork. It clones at the existing intake pin d54d0e3c, so the source
state is preserved. Added its gitlink under software/submodules/IdRes and updated
ADR-008/source ownership. No upstream source is copied into nODD Git history.

make idres builds a disposable source copy with Spack GSL2.8. The adapter's
optional --binary argument accepts the external build product while retaining
its original default behavior. make idres-run supplies an absolute configuration
path and stores new results under build/idres, preserving retained evidence.
The first invocation exposed a working-directory-dependent configuration default;
the explicit absolute path corrected it.22 runs then passed with729 complete
rows each, and4 adapter boundary tests passed. The source gitlink remains clean.

Existing compiler deprecation/unused-variable warnings were not suppressed.
Authenticated access is verified; anonymous access and redistribution licensing
remain separate. Exact per-turn token counters were unavailable; usage is empty.
This is a focused infrastructure completion of the overall software-layout task,
not scientific sign-off or regeneration of an accepted baseline.
