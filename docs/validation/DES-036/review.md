# DES036 — Bounded specialist review record

2026-10-15. **PROTOTYPE / DRAFT.** These are AI specialist contributions and
findings. They are not human engineering approval or a design-status change.
The [session record](../../../logs/codex/SESSION-2026-10-15-hcal-common-module.md)
retains role assignments and input revisions.

| Contribution | Input revision | Outcome |
| --- | --- | --- |
| CaloTech source/component assessment | `7243c84c055a5c2817f7eb86727ca7eade2f21c8` | Recommended a bounded 36-tile board; distinguished 72 ordinary inputs from 78 total channels, qualified chip power and package/optical evidence |
| SysArch physical/service assessment | `7243c84c055a5c2817f7eb86727ca7eade2f21c8` | Explicit module/carrier/sector ownership, shared service material, local frames, collector handoffs and removal limits |
| SoftEng implementation assignment | `7f354fe20307b6fee996c7043e68e5d80dc23a8a` plus explicit recess amendment | Isolated exporter, model, factory and controls; 35 module tests passed; no production integration |
| PhysVal initial design review | `7f354fe20307b6fee996c7043e68e5d80dc23a8a` | Found that original 0.9 mm recess failed the sourced 1.0 mm upper package-height case. Amended to 1.1 mm before final evidence; old-depth negative control retained |
| PhysVal implementation review | `fe477dbb10d29bda34753f0c05dce0edaa6d886a` | Two checker findings below; independently ran 35 controls, exit 0 |
| PhysVal closure review | `97d0bb64c22f63c0680c543a97c5b05ce2acc4b8` | Both findings closed in source; nine provenance/finiteness controls passed, exit 0 |

## Findings and resolution

**P1 — saved transport execution provenance.** The first checker could accept
saved files from another configuration with the same IDs and asserted seed,
physics and field settings without binding them to execution. The runner now
records actual commands, exit status, Git revision, settings, native-input and
saved-output hashes. The checker verifies current input/output identities,
passing native fixture/library agreement and executed argv, then independently
inspects saved MC primaries. The report distinguishes recorded settings from
measurements in saved events. Substituted ROOT output, changed compact, another
library, wrong recorded/executed seeds and failed/duplicate jobs are rejected.

**P2 — nonfinite hit values.** `energy <= 0` did not reject NaN. The final checker
requires finite, strictly positive energy and finite saved positions; direct
negative controls exercise NaN and infinity.

The reviewer found no further scoped correctness issue in channel/power
ownership, separated trigger/DAQ budgets, exposed stress overload, native shape
checking or stated engineering limits. Closure review assessed source and
standard-library controls; it did not execute native DD4hep/Geant4. The
coordinator's subsequent source-bound native/two-event execution is recorded
separately in [results.md](results.md).
