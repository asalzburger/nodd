# SESSION-2026-11-10-siw-ecal-compute-pilot — Si–W ECAL compute pilot

The user asked, “Can you run a test sim of 100 events and estimate the
necessary compute?” The preceding discussion specified a single-electron
scan at fixed 50 GeV transverse energy, with zero field and the inner tracker
removed. The assistant chose to omit the beam pipe for the ECAL-only
reference and to split the pilot over four representative directions at
the same azimuth.

The clean source checkout was `a8630d48baee5b17c8b0dee387b3f47d34c8ae49`.
GitHub confirmed PR #118 merged at `0bc37ca08fed0bd7b121d6eebd5794dd3b584877`.
A dedicated worktree based on the merge commit records the pilot. A path
diff verified that the detector factories, calorimeter exporters and native
steering match the timed source.

The acts-spack registry preflight returned 2 because the setup and lock
fingerprints changed. In the existing Spack environment, DD4hep, DDG4, ROOT,
podio and EDM4hep imported, and Geant4 reported its datasets installed.
The Si–W factory was rebuilt in Release mode. DDSim converted the geometry
and proceeded to populate the sensitive-volume lookup. A brief macOS
process sample found it inside DDG4's physical-volume traversal with one
core busy.

The original timing report and reproduction files remain local in the pilot worktree. See the [maintained implementation validation recipe](../../docs/validation/siw-real-wedge-default/README.md) for the integrated follow-up.
The benchmark estimates transport and raw EDM4hep storage. The uncertainty
in scaling to other azimuths or simultaneous workers requires a separate
measurement. Exact counters for the active client turn were unavailable.

DDSim exited 0 after all four groups. The initial saved-event audit rejected
a 1.54 keV deviation from the nominal 50 GeV transverse momentum under its
1 keV absolute check. An independent first-event readback for all four groups
identified six-significant-figure rounding by the native gun command. The
updated audit verifies the exact effective momenta and preserves the nominal
residuals. All 100 saved events pass the effective-momentum, angular, hit-ID
and count checks. The largest nominal transverse-momentum deviation is
57.3 keV. The transport files used in both audits are identical.

Measured total wall time was 78.9 minutes, with
72.8 minutes to the first event and
10.1 GiB peak resident memory. The projection
is 77.4 worker-hours and 464 GB for
110,000 events, including four process startups in the compute estimate.
The timing and all four ROOT files remain in ignored local build storage.

## 2026-11-11 accounting correction and publication

Exact closed-turn usage is now recorded from the [PR129 recovery inventory](../usage/USAGE-2026-11-11-pr129-siw-wedges.json), using matched app request/turn IDs and verified parent/child metadata. Earlier statements that counters were unavailable describe the active-turn observation at the time. No counters are estimated or shared between canonical owners. The active merge-readiness turn and other-device/reviewer-task history remain excluded.

This original paired record is published with PR129 from the preserved pilot worktree; its original Git provenance, checks and scientific limits remain intact. Only attribution, exact usage and this dated correction are added. The pilot worktree remains unchanged.

This account includes the initial sample-design advice, the 100-event run and the two immediate event-count/startup clarifications. All four complete turns belong to this bounded sample/compute task.
