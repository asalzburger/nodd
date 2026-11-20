# SESSION-2026-11-20-hcal-compact-screen — HCAL axial compaction feasibility

## Scope and evidence

New bounded investigation on draftPR157, clean scientific source8153129e07d92a17dccca6fa0226ae5142398941, branchcodex/hcal-edge-coverage. Exact user request: “Is there a way to shorten the HCAL barrel to lign up with the ECAL envelope and move the HCAL end caps inwards to compactly the setup - or is this space occupied ?” This asks feasibility; no geometry adoption or transport rerun is performed. The repository is the source of truth.

## Coordination

Under nodd-coordinate/design-evidence/review-validation and AGENTS.md, the coordinator prepared source-pinned read-only HCAL-COMPACT-SYS and HCAL-COMPACT-PHYS assignments, dispatched to /root/hcal_compact_sys and /root/hcal_compact_phys. Full contracts and role prompts are retained in the same-stem directory. This is explicit repository role assignment through generic collaboration, not verified native profile loading. Roles returned independent interface and physics assessments at8153129e; no nested delegation or writes. Curated checks and limits are in assessments.md.

## Outcome and provenance

Existing whole ECAL warm rear5660mm versus HCAL6260/6760mm leaves600mm inherited excess before the500mm radial service-exit reservation. External route material is not constructed. Existing budget passes all three candidate coordinates, retaining490mm rear-elbow bound in500mm exit. Cassette packing matters:43ratherthan47rows, with0mm allowance at exact5660alignment;20mm alternative5680/6180/8770 saves1160mm overall; preserving existing80mm with5740/6240/8830 saves1040mm overall. No final engineering minimum is selected. A full HCAL endcap moved to4600mm to follow the4100mm ECAL barrel would overlap ECAL endcaps4500–5660mm; alignment target is the whole warm package.

The coordinator reproduced finite phi10 steel paths and sampled minima from the independent PhysVal arithmetic. Transition absorber depth changes even with60 layers and2590mm nominal stack; no preservation of resolution is inferred. Current native/response results retain their original geometry. Proposed values are explicitly unadopted design choices, source facts and derived quantities classified in docs/design/inputs/DES-046-axial-compaction-screen.md. No new literature/device specification, formal sign-off or engineering qualification is asserted.

## Commands and checks

Ran current model.validate_config/barrel_layout and moved-ECAL services.budget on deep copies; no detector configuration writes. Ran tools/hcal_response/compact_screen.py to retain compact source-hashed results, actual plate clipping atphi10 and eta0.8–1.25/1e-5 grid. Initial receipt lookup used absentbarrel_tiles key; corrected to total tiles minus unchanged endcap-carriers×unit sensitive-count, then successful complete run. Direct sums reproduced independent assessment numbers. Python is existing3.14.6; no ACTS/DD4hep/Geant4 dependency activation or installation. Native construction/transport were not run and are not claimed.

## Deliverables and remaining work

Proposal doc, compact numerical receipt and reproducible in-memory screening script; links fromDES046/current layout. Existing geometry and drawings remain unchanged. Engineering selection and subsequent native geometry/path/ID/material/overlap/service checks plus matched-primary pion response are needed only if a compact variant is adopted. Scientific task tracking, software inventory, PR interactions and paired journal are maintained on draftPR157.

## Token accounting

No exact current parent/child client turn counters were exposed; usage is empty and unknown, not zero. No private client archive was collected. Project-wide historical observed totals are not assigned to this investigation.

Closeout checks: four in-memory candidates and45001point phi10 grid complete; both invalid-service guards reject. Python3.11 syntax and independent numeric assertions pass; actual detector/prototype/transport sources remain unchanged against8153129e. Project/session/software/interaction checks and token preview/summary pass. Initial project task/stream mismatch was corrected fromWS-CALO toWS-ARCH to match the System Architect role; validator then passes113tasks/56documents/24reviews.308sessions and127PRledgers validate. Current task token coverage remains unobserved. No new native run or all-phi response claim.
