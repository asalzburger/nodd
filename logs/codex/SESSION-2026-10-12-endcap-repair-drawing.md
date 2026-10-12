# SESSION-2026-10-12-endcap-repair-drawing — Annotated repair drawing

2026-10-12, contemporaneous. User exact request: “Can you make a drawing as well,
please ?”. Clean starting revision4e7f0fc on codex/calorimeter-assemblies;
companion to the preceding endcap diagnosis and existing PR69.

Created a reproducible three-panel technical drawing: actual ECAL packing,
proposed shaped-carrier/board-family arrangement, and existing inner-aperture
fit constraint plus conceptual service grouping/HCAL subarrays. Standard90 mm
silicon, existing300 mm aperture and baseline dimensions are preserved as
context. Illustrative PCB border/gaps, edge allowance, inner clearance and outer
service-bay size are recorded explicitly in the drawing JSON and have no
engineering approval. No detector input, factory, material or native evidence
changed, and no new coverage claim made.

Existing Matplotlib3.11.2/Python3.14.6 used; no dependency installed. Initial
Polygon keyword edge failed, corrected to edgecolor. Visual inspection found
footer overlap, corrected; final PNG inspected. Baseline seam/rail drawing uses
119 mm full width and77 mm clear width; the proposed boards are checked inside
the illustrative carrier/service boundary. That is drawing consistency, not
native detector or mechanical validation. SVG date removed and fixed hash salt
used for reproducibility. PNG/SVG and fixture/source hashes retained.

Proposal companion and project evidence pointer updated. Local record/session/
site checks recorded in paired JSON. Exact client tokens unavailable; usage stays
empty/unknown without estimates, copied counters or duplicate turns.
