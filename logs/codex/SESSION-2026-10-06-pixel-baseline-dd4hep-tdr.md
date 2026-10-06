# Selected trimmed pixel baseline in DD4hep and TDR

## Requests and scope

On2026-10-06 the user requested two separate follow-up PRs: update DD4hep for
the new trimmed endcap with single/quad modules, then update the TDR. The user
selected self-contained TDR sources in nodd rather than an Overleaf push.
Original pT>=1GeV/eta/luminous-region assumptions remain those of DES018.
This is a new bounded task, canonical token owner once for both PRs.

## Starting state and actions

Started client turn01a11051-efc0-75e1-8080-8c9c88d42e24 at2026-10-06T08:26:07Z,
thread01a10c6a-664d-72b1-afad-926c2c57312b. PR43 merged at08:23:13Z into prototype
parent codex/issue38-disc-overlap at7057861fa3c8c137833ecedddcae0856ebd91e4c.
Created separate codex/pixel-baseline-dd4hep checkout from that merge. Original
main and preexisting untracked primary logs preserved. Initialized clean TDR
submodule at7783ea3e3235c0fe9da641db3d303a6f211b3073 for template inspection.

Read root AGENTS, PROJECT, logging and relevant DES/ADR/publication contracts,
TDR README and ACTS sister instructions. Created DES019 before implementation.
New default config preserves frozen legacy pins. Implemented source adapter,
radial/tangential proper frames and reversible source-ID mapping, chip pickups,
retained cooling rows, disjoint effective support and heterogeneous transport.

## Actual checks and corrections

ACTS Spack preflight failed changed setup/lock fingerprints; user warned before
runtime work. Actual imports verified DD4hep1.38/ROOT6.40.04/Geant411.4.2. Missing
local TeX commands caused the availability shell exit1 after successful runtime
imports; no shared dependencies installed/changed. Existing sister edits preserved.
Usage-recovery first failed because the output parent was absent, then succeeded
into ignored build/issue38; current turn remains active, so no partial usage import.
Some exploratory reads used wrong filenames/globs or inspected integer `stems`
as a list; corrected from actual directory/files/schema. No scientific changes
followed these read errors.

Pure export and9 focused tests passed. First native workflow passed6/6 CTest and
Geant4 initialization. After source parameter centralization, final workflow
passed6/6 CTest, portable nodehammer/display audits and Geant4 initialization,
zero events, seed42, FTFP_BERT. It contained8 exporter tests; the added ninth
Ti/CO2 conservation check passed separately. Retained DES019 artifacts record
actual dirty producer/input/plugin hashes at starting merge7057861; never replace
those hashes by an enclosing commit. No legacy evidence regenerated.

## Limitations and accounting

DES019 remains DRAFT/PROTOTYPE despite human preliminary-baseline selection.
Coverage holes, warm-thermal/guard failure, service packing failures and
manufacturing interfaces remain open. Current turn final resource counters are
unknown until closure; recover only this exact turn once into this record.
Execution model/client version unknown; older project coverage partial. No
all-project or self-inclusive current total claim. TDR work and publication
closeout will be appended here; no duplicate token owner.
