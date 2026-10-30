# RECO-SPECIES-SoftEng-01 — transport adapter

Examined aae262694535523b1e0fd968e4170b061429f0a6 and identified working DES.
Authored only transport.py/test_transport.py; no commits, simulation or shared
dependency changes. Seven dependency-free controls, syntax and scoped diff pass.

Adapter returns effective settings plus idempotent cleanup. Fatras preserves
0.5GeV absolute momentum and EM interactions. Geant4 uses FTFP_BERT, existing
persistent native helper, Silicon/pixel_Silicon mapping, secondary charged hits,
no-hit particles,25ns and outer tracking boundary. Scheduling errors clean up
and preserve the original exception even if cleanup fails. Main must protect
all subsequent scheduling and run operations with try/finally. One Geant4 case
per subprocess. Dataset metadata gives paths/existence, not content verification.

Source: pinned runners/preparation, unchanged lifecycle source, clean matching
ACTS355ea684 helper/manager and retained balanced Geant4 smoke. No native runtime
validation claimed; source preflight warnings remain.
