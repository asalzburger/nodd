# SESSION-2026-10-12-calorimeter-cassettes — Physical cassette prototypes

2026-10-12, contemporaneous curated record; starting main ed30e63fb0ab30b66d4084a9058906929006f792.
Clean managed worktree reused on codex/calorimeter-cassettes. Unrelated primary
checkout changes preserved. Exact source/library/compact hashes accompany native
execution; dirty starting revision is not represented as a committed execution.

User (selected exact request): “design one realistic ECAL cassette and one HCAL
cassette; then build sectors and complete barrel/endcap assemblies with
reproducible geometry, mass and material checks”. User technology answer:
“Retain Si–W ECAL and steel/scintillator HCAL (recommended)”. First bounded
PR supplies units; sectors and full assemblies follow on dependent branches.

Assistant retained ODD sampling technology, replaced unrealistically bulk PCB
representation with explicit boards/packages, provided guards/tile recesses,
containment/frame, thermal paths, water pipes and service allocations. DES028
classifies CALICE precedents separately from chosen nODD dimensions/continuous
operating budgets. No design sign-off inferred. No production entry point edited.

Public CALICE PDFs downloaded into ignored reference storage, selected pages
read with pypdf6.10.0, source hashes registered. MDPI429/arXiv HTML cache miss
retained as access limitations; public PDFs supplied the evidence without
bypassing restrictions. PDG PET page checked. No external software installed.

acts-spack preflight reported changed setup/lockfile fingerprints. User warned;
actual setup/imports/DD4hep/ROOT/Geant4 versions and13 installed datasets passed.
CMake policy/CLHEP path warnings retained. Initial exporter syntax error fixed;
initial deterministic test imported tracker export due path precedence, corrected
local import order. Initial factory named create collided with DD4hep macro
member lookup; renamed createCalorimeter. Native capacity reader extended to
actual TGeoTubeSeg. DDSim direct launch failed plugin any-cast; invoking script
with the verified active Python resolved it. Missing tracker region contract
then required documented fixture-only particle-handler disablement. Final unit
native checks and transport checks rerun on final factory/configuration.

Executed:7 physical negative/conservation controls; isolated CMake compile;
DD4hep/ROOT859 material parts,148 sensitive IDs,1168 cells, capacity/mass/
constituent equality, zero overlaps at10 nm;10 bounded material rays. Saved
seeded muon hits are separately audited. Figure regenerated and visually checked.
Relevant source choices, exact hashes and remaining thermal/electrical/optical/
structural limits appear in DES028 and its validation report.

Changed-file inventory and check exits are in the paired JSON. Exact client turn
counters are not exposed for this work; usage stays empty/unknown, not zero.
No token observations are copied, divided, estimated or duplicated.

Next: physical sector plates/support and cassette packing, complete barrels and
both endcaps, conditional solenoid-envelope interface, aggregate service and
material checks. Continuous HCAL electronics power, PCB/package and coolant
assumptions require expert review; geometry checks are not engineering acceptance.
