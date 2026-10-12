# SESSION-2026-10-12-endcap-coverage-review — Diagnosis and repair proposal

2026-10-12. User exact request: “Explain the issue with the Endcap coverage and
propose how to fix it”. Scope: analytical/design review of PR69; no geometry
change. Starting revision61ab5a4, branch codex/calorimeter-assemblies, clean.

Inspection decomposed the existing single-layer plate-area fraction into
cassette footprint coverage times cassette sensitive fill. ECAL44.93%×70.88%
=31.85%; HCAL46.45%×83.57%=38.82%. Fixed230×190/400×380 mm rectangles in
16sectors,40mm edge allocations and floor-rounded radial rows leave empty inner
rows, lateral wedges and outer remainders. First sensitive radii908.9/1483.15 mm
are substantially larger than the nominal300 mm aperture. Area fraction is not
particle efficiency; repeated masks explain the recorded high-eta blind rays.

Five unchanged-cassette counterfactuals varied sector count/edge allocation;
all logical corner-containment checks pass. Reducing allocation to20mm gives
ECAL42.47%/HCAL38.82%; 8sectors/40mm gives43.81%/49.84%; 8/20 gives48.67%/
52.10%. These are packing arithmetic, not native/engineering qualification.
Changing sector count also changes polygon corners, supports and material.

Proposal: define eta/aperture/forward handover; separate shaped mechanical
carriers from modular readout; study full/single/1x2 silicon sensor arrays and
HCAL small tile subarrays; move shared interfaces to explicitly modeled carrier
service zones; design inner-ring/rib topology jointly; fill complete layers and
only then stagger seams. Preserve semiconductor shapes, realistic guard regions,
material/heat ledgers and the technology/sampling baseline. No promised coverage
percentage, human sign-off or implemented repair is recorded.

Primary public CALICE PDFs checked through browser tools. SiW PDF4 describes
quarter endcaps/multiple ASUs; PDF6 describes shared SL-board readout. This is a
hardware architecture precedent, not adoption of pulsed operation. New facts
added to the existing source catalogue entry. AHCAL PDF web retrieval failed;
its already registered local/source architecture remains the limited precedent.

Reproducible standard-library analysis endcap_review.py emits the exact result
JSON with source/method hashes; existing Matplotlib3.11.2 generated a new face
plot from actual sensitive/footprint coordinates, visually inspected. Existing
geometry JSON/C++ and native evidence are unchanged. Proposal, diagnosis data,
figure and journal are added to existing PR69 for versioning. Checks and changed
files are in the paired JSON.

Exact current token counters are unavailable; usage remains empty/unknown, not
zero. No estimates, copied totals or duplicate turns. Session validator/summary
and token-site checks retain existing observations and missing coverage.
