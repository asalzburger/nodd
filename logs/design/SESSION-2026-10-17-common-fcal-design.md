# SESSION-2026-10-17-common-fcal-design — Common forward calorimeter design

## Request and scope

User: “Ok design such a forward calorimeter and fit it into the two layouts.”

Isolated DRAFT / PROTOTYPE design and physical integration into both candidate layouts; no production integration or human sign-off. Starting revision 33a607b70214532cd265623241b0c250ca0da361. Clean dedicated worktree codex/common-fcal-design.

## Assignments recorded before dispatch

- FCAL-CaloTech-01 / CaloTech / input 33a607b70214532cd265623241b0c250ca0da361 / write only docs/design/inputs/DES-039-fcal-technology.md. Contract and full role prompt are retained under this session directory.
- FCAL-SysArch-01 / SysArch / input 33a607b70214532cd265623241b0c250ca0da361 / write only docs/design/inputs/DES-039-fcal-layout-interfaces.md. Contract and full role prompt are retained under this session directory.

Main agent coordinates, implements parameterized geometric/material/service checks, integration drawings, records and final design. Separate PhysVal assessment follows a fixed implementation revision.

## Evidence and checks

Pending.

## Token accounting

Exact client per-turn counters unavailable; usage remains empty, including child turns unless exact counters become available.

## Additional assignment before dispatch

FCAL-SoftEng-01 / SoftEng / 33a607b70214532cd265623241b0c250ca0da361 / read-only; establish native runtime capability, no shared-dependency edits. Full contract and role prompt retained.

## Bounded assignment continuation

CaloTech and SysArch retained their single owned files and assessed the additional 02 EM collar and explicit collector/service neck under their original assignments. The amendment was made to close a quantified EM transition gap, without changing ECAL/tracker/magnet source geometry.

## Native construction assignment before dispatch

FCAL-SoftEng-02 / SoftEng / 0964b60a3d19b13b91abc48e30bd18d66feb66d2 / write tools/forward_calorimeter/native.py and docs/validation/DES-039/native.json only; ignored exports allowed. Explicit ROOT-native geometry scope, no DD4hep or shower acceptance claim.
