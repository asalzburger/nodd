# SESSION-2026-11-21-hcal-gap-services — Annotated ECAL–HCAL service-space plot

## Scope and selected request

Exact user request: “This new, compact design is great, can you label what the gaps between ECAL and HCAL are for in a second plot, outlining what needs to go in there ?” Clean starting revision645cfc9dfd419450f0382bbd9ccd0adad8f9db8b, branchcodex/hcal-edge-coverage, draftPR157. This bounded annotation follow-up uses the existing compact envelope; it does not implement a new detector or assign missing engineering interfaces. Kept sequential with the coordinator under the small dependent task rule; no new independent specialist assessment claimed. Previous geometry/feasibility assessments remain in their own source-pinned journal.

## Source facts, inferences and outcome

Four numbered bands match four callout cards: barrel radial488.3mm; endcap radial181mm with140mm lane and20.5mm each face; rear580mm=80mm axial offset+500mm exit; separate400mm ECAL warm barrel/endcap break. Source facts are from the compact named input, moved-ECAL spec and service budget. The500mm exit stays5.740–6.240m; its490mm largest elbow allowance is not an engineered installed route. The80mm axial offset is not claimed as another equipment compartment.

Callouts identify jacketed nitrogen/LAr utility pipes, warm water, power/HV, data/fibres, control/grounding, pipe/cable turns, connectors/access and outer handoff. Side-neck band3–4m and radial bounds follow the recorded unconstructed reservation. Cold boards/supports/local cooling are already inside the warm ECAL package; they are not duplicated in the outside gaps. Buses are sectorized inphi, not continuous service rings. Suggested placement/connection requirements are unsigned engineering inferences; wall penetrations, board/ring clearance and connected headers remain unresolved. HCAL external collectors/manifolds and shared supports are explicitly unassigned rather than silently placed in the ECAL bus. Sources/classification and exact recipe are retained in the proposal note. No new public device claims or design sign-off.

## Implementation and actual checks

New tools/hcal_response/draw_services_rz.py reads the checked compact parent and screen, validates source hashes/dimensions, retains label text/source hashes in a compact JSON and appends annotations/cards to the existing SVG. The old comparison outline is omitted in this second plot. The first compact drawing and all detector/native/transport inputs remain unchanged.

Existing Python3.14.6 XML/stdlib and rsvg-convert2.62.3 (cairo1.18.4,pango1.58.0) generated PNG/SVG/PDF. PNG inspected visually for label/card fit. SVG/PNG replay byte-identically. Python3.11 syntax and dimension/rectangle/path comparisons pass; all original direct geometry primitives match after excluding the old comparison outline/background. Four cards and580=80+500 arithmetic checked. No dependency installation, native runtime activation, new geometry/transport execution or performance claim.

## Deliverables and reproduction

Second annotatedPNG/SVG/PDF, compact named label/dimension/source JSON, generator and recipe in docs/design/inputs/DES-046-axial-compaction-screen.md; linked from layouts main page. Current compact plot is preserved. Existing feasibility task deliverables, inventory, PR interactions and this paired record updated.

## Token accounting

Exact current client/thread/model/turn counters are unavailable. Usage is empty and unknown, not zero. No private client archive was read; global observed project totals are not attributed to this task.

Closeout: all project/software/session/interaction validators, token preview and session summary pass (113tasks/56documents/24reviews,310sessions,69components and127PRledgers). Final PNG/card/footer layout inspected. Current task usage remains unobserved. Geometry/first-plot source guard and whitespace checks pass. Only compact plots, label metadata and curated records are added; no event or native data.
