# TTBAR-PU200-SoftEng-03 — generation success and origin guards

SoftEng child /root/ttbar_native, inputaacf2ba0ab6c42e675959a8cb25c43c0ba7b477f,
changedonly5ownednative/runtime files. Sharedsources/dependencies/frozenhelpers
andseeder/CKF unchanged in this assignment. Noactivejobafterhandoff.

CMake hash-checks source355ea Pythia8ProcessGenerator and creates a task-owned
copy with one change: uncheckednext() becomes sharedsuccess-or-throw guard.
False aborts the wholeevent, no retry/filter/resampling. Native/Python require
all201origins in fullunfiltered generatedtruth withcomplete labels. This check
uses the existingposttransport SampleWriter slot to preserve valid-event RNG
algorithmnumbers; it assesses fullpreselection truth before sampleacceptance.

17runtime tests and actualnative adverseguard/origin tests pass. Same-seed
oneevent generation is byte-identical tosample2, includingcompletegzip payload
SHAaacdfa5addacd7472e33792290205f31838f6b38fd52b99db695b8c0a55c6d53.
Allparticle/hit/originfields match,201convertedorigins verified. Total47.117s,
sequencer8.459s, peakRSS6193037312bytes; allimmutability/diffchecks pass.
[Regression](generation-guard-regression.json) and[adverseproof](generation-guard-adverse.json).
NativeartifactSHAa14291d5d18edda59c5f15258002afcc2daadbf106dfc028dbee020fc8797b7e.
No100eventproduction, commits, publication or delegation. Coordinator'slater
commonvertexwindow adaptation is outside this handoff and needs newchecks.
