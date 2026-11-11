# SESSION-2026-11-10-ddg4-startup-profile — DDG4 volume manager startup

After reviewing the 100-electron timing, the user said, “I see ... we will
have to investigate the DDG4 startup time”. This follow-up profiles DDG4
1.38 on the same Mac Studio and field-free LAYOUT-001 ECAL geometry.

The full pilot recorded 20.309 seconds for geometry conversion and
3953.835 seconds for 531,936 sensitive paths in the Geant4
volume manager. In the saved two-second process sample, 148 of 173 main
thread stack samples were at the comparison call or its target. The installed
arm64 binary UUID matched the sampled library. Disassembly at address
`0x89cc8` shows the call to `memcmp` followed by the branch to the next
imprint candidate.

DD4hep v01-38 stores [imprints under the outer assembly volume](https://github.com/AIDASoft/DD4hep/blob/v01-38/DDG4/src/Geant4AssemblyVolume.cpp#L80-L83)
and [keeps that parent during recursion](https://github.com/AIDASoft/DD4hep/blob/v01-38/DDG4/src/Geant4AssemblyVolume.cpp#L143-L158).
The [volume manager searches that vector for the exact path](https://github.com/AIDASoft/DD4hep/blob/v01-38/DDG4/src/Geant4VolumeManager.cpp#L229-L243).
The exported XML implies 8,820,848 leaf imprints in the barrel's outer
assembly and 3,686,464 in the endcaps' outer assembly.

Startup-only probes kept the complete layers and hardware of 1, 2 and 4
sectors on both endcaps and in the barrel. They reached the zero-event
macro and exited normally. The same runtime mapped 33,246,
66,492 and 132,984 paths in 19.44,
52.25 and 195.11 seconds, respectively. Single-thread
probes shared the host. The retained full pilot was a separate job.

An isolated full-size experiment duplicated the inner barrel board template
per layer. Normalizing template names and references restored complete XML
equality. Source inspection showed that the outer-assembly key survives
the split, so the experiment was stopped during mapping and supplies no
finished timing. No shared runtime or maintained detector code changed.
The local scripts, logs and compact findings are retained in ignored build
storage. The proposed follow-up is an exact-path index for assembly
imprints, checked against the complete cell-ID mapping.

The preflight warned about changed environment fingerprints and unavailable
staged sources. Source inspection used the upstream release and the matched
installed binary. Exact client usage counters were unavailable.

## 2026-11-11 accounting correction and publication

Exact closed-turn usage is now recorded from the [PR129 recovery inventory](../usage/USAGE-2026-11-11-pr129-siw-wedges.json), using matched app request/turn IDs and verified parent/child metadata. Earlier statements that counters were unavailable describe the active-turn observation at the time. No counters are estimated or shared between canonical owners. The active merge-readiness turn and other-device/reviewer-task history remain excluded.

This original paired record is published with PR129 from the preserved pilot worktree; its original Git provenance, checks and scientific limits remain intact. Only attribution, exact usage and this dated correction are added. The pilot worktree remains unchanged.

This account includes the startup profile and the next geometry-hierarchy recommendation. The latter motivated the separately owned barrel/endcap prototypes.
