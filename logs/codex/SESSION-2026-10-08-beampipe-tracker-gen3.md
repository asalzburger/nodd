# Beryllium beampipe and DD4hep-driven ACTS Gen3 tracker

User request2026-10-08: first PR for a0.8mm Be wall at27mm, then complete
BeamPipe+Tracker DD4hep and derived ACTS Gen3 tracking geometry. Work isolated
from all pre-existing primary/ACTS edits on remote main3e0e706. Optional radius
clarification pending; using inner radius27mm, outer27.8mm and inherited±4m
straight extent. No human engineering sign-off inferred.

The acts-spack skill preflight found changed setup/lock fingerprints. Actual
runtime imports verified ACTS, ROOT6.40.04, DD4hep and DDG4. Component implementation
and failed/successful native and DDSim attempts are retained in DES024 results.
No scientific transforms/services changed. Task remains open for the assembly
and Gen3 conversion. Exact current-turn tokens unavailable, never estimated or
partially recovered. This pair is the one shared task owner across dependent PRs.
