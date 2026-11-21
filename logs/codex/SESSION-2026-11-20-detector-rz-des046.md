# SESSION-2026-11-20-detector-rz-des046 — Latest tracker, solenoid, ECAL and HCAL r–z view

## Scope and evidence

Small dependent drawing follow-up on draft [PR157](https://github.com/asalzburger/nodd/pull/157), branch `codex/hcal-edge-coverage`, clean starting revision `071041c9cbf991fefebafc4c5747090b5c100412`. Current remote main was refreshed and is `78bef505c4e623739da204ce92e3aa7bc6f931c5`; the selected restored ECAL and latest HCAL proposal remain on this task branch. No user changes were present. The coordinator kept this bounded drawing task sequential under the repository coordination procedure; no new specialist assessment or human sign-off is claimed.

## Selected conversation

Exact user request: “Can you post an up to date rz view of the tracker + solenoid + ECAL + HCAL including the latest changes here ?”

Assistant outcome: generated the composite equal-scale r–z view with the DES043 tracker, conditional DES026 solenoid, selected restored LAr ECAL and independently validated DES045/046 60-layer HCAL. Prepared PNG, SVG and PDF and updated the current layout links in the same draft PR.

## Decisions and outcomes

The old retained overview used the1495.9mm HCAL context and is preserved unchanged. The new named input uses barrel apothems3130/5720mm, halfz6260mm, endcap apothems300/5710mm and |z|6760–9350mm. The physical depth is60×(30mmsteel+12mmcarrier+1mmallowance)+10mmcover=2590mm. DES046 smaller edge modules and2mmguides do not change global r–z bounds; their7.047825mm per-side inactive core-plane strip is stated in the caption.

The renderer first verifies every source hash in the HCAL geometry receipt frozen at7059bf6c and every retained tracker source. It rebuilds the current selected ECAL barrel/endcap envelopes, including local services, and checks them against the prior snapshot. Historical ECAL source hashes are explicitly retained as historical provenance; a separate current source map includes changed service/optional-prototype implementations and the ECAL selector. This is a fact about checked project source, not an additional design choice. No geometry/material/response source is changed.

HCAL striping depicts sampling organization, not continuous sensitive planes. Individual module/sector gaps and tracker passive services are unresolved at this scale. Solenoid hatching, cold-mass allocation and assembly reservation remain conditional. Polygon radii are face apothems, with the maximum barrel corner radius stated separately. FCAL/muons are omitted pending integration. No combined native detector, installed field, structural/service qualification or detector acceptance is inferred.

## Commands and validation

- Current source capture and ECAL reconstruction: PASS. All tracker/HCAL hashes and both2590mm stack closures checked.
- Existing `rsvg-convert`2.62.3 generated PNG/PDF; PNG inspected visually: PASS, no clipped detector bounds or overlapping captions. Python3.14.6, cairo1.18.4 and pango1.58.0 were observed; no software was installed.
- Named-input replay and SVG/PNG byte comparisons: PASS.
- Initial capture checked the absent `variant` specification key; corrected to the actual `id`, also checked against the maintained selector, then reran successfully.
- Initial sandbox `git fetch` failed DNS resolution. Authorized escalated read-only fetch succeeded.
- No new native geometry or transport execution was required for this illustration; existing bound HCAL validation remains the evidence.

## Changes and revision links

Renderer `tools/hcal_response/draw_rz.py`, `docs/layouts/LAYOUT-002-DES046.json`, three figure formats, current root/layout/candidate links, software inventory, existing scientific task deliverables and this paired journal. See the JSON file inventory. Source inputs are DES026/043/045/046 and selected LAr layout; design lifecycle states are unchanged. The existing draft PR remains the publication target.

## Token accounting

Exact client counters are unavailable. `usage` is empty; this means unknown, not zero. No private client archive was read and no token estimate was recorded. Project-wide summary totals are not attributed to this drawing task.

## Follow-up

Engineering qualifications and full-detector integration remain under their existing design gates. The historical view and all scientific response data remain unchanged.

Closeout checks: all session/project/software/interaction/token validators and the token preview build pass; Python3.11 syntax, independent dimensions and SVG canvas assertions pass. Current drawing session has no exposed token counters. The final PNG/SVG/PDF sizes are244712/59986/149942bytes. `git diff --check` passes. Source geometry and response producers remain unchanged.

## Gap correction

Exact user correction: “I thought the 40 mm ECAL gap was already merged & approved ?” The recorded reduced-gap implementation is400mm (40cm), not40mm. Connected GitHub metadata verifies PR151 was merged2026-11-18T14:59:50Z into `codex/restored-lar-em-baseline`, head `0babd0cfcf6f6094e09583abce3a88bfd5f99e8d`, merge `43f8a56cc0f7163ff959e262516ae2db7d21e33e`. PR150 had also merged into its stacked parent. These were stacked-branch merges; current main and the maintained selector had not changed to the400mm recipe. The file `tools/lar_calorimeter/gap400-prototype.json` is byte-identical to PR151's merged head (SHA2561950740f7bed57efd5418a979887cea4d0be9001d341b9f74ce118706da6ad9d).

The initial view incorrectly chose the1m default manifest for the user's latest merged-gap layout. The coordinator acknowledged this drawing-selection error and corrected the composite to explicitly capture the merged400mm recipe. No approval request was needed to display the already requested variant. The former1m named input and three figures remain unchanged; new `LAYOUT-002-DES046-gap400` files hold the corrected view, and current links point to them. The default export manifest and all scientific geometry/response producers are unchanged. No additional formal design acceptance is recorded by this correction.

The corrected endcaps occupy warm |z|4500–5660mm and sampling4610–5260mm. Barrel warm ends4100mm, so the warm gap is400mm while sampling edges have a700mm interval. Both complete endcaps move600mm toward the IP. HCAL remains halfz6260mm/front6760mm; its rear ECAL-to-HCAL interval is1100mm and barrel/endcap exit window500mm. The drawing marks the400mm warm gap directly. Unconstructed external route reservations remain identified, and no calibration is transferred to a new native detector.

Updated renderer supports explicit `--ecal-gap-mm400` (default for capture) and1000. Capture checks the retained variant ID/specification hash and current base selector separately, rebuilds matching ECAL bounds and retains both historical-context and active-variant provenance. The corrected PNG was inspected visually. SVG/PNG replay for400mm is byte-identical; the previous1m SVG also still replays byte-identically. Current root/layout links, software inventory and existing task deliverables are reconciled.

Correction closeout: all307session/112task/56document/24review records,69softwarecomponents and127PRledgers validate; token preview builds. Python3.11 syntax and independent numerical envelope comparisons pass. The earlier1m drawing remains unchanged. Corrected PNG/SVG/PDF publication is on the same draftPR157. No new simulation or scientific-data change.
