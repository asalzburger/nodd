# PR #13 — Inclined C and double-sided strip review

## Selected request and scope

User: “There are comments on PR#13 - address them (not the one towards noemi)”.
The technical comment requests explicit double-sided long-strip measurement accounting and a more aggressive inclined C with TrackTech/PhysVal cost–benefit. No response or change is made to the Noemi-directed comment.

## Outcome

Independently delegated TrackTech and PhysVal as requested by the review. Added concrete C layer endpoints, original drawings and a two-page A4 brief, separate A/C geometric/material screen and independent audit. Kept A/B retained inputs and IdRes evidence. Made two faces/one stereo station/one paired material allowance explicit, distinguishing overlap material and physical measurements from conservative parent-station counts.

C reduces full-system ideal strixel area9.13% and double-sided long-strip silicon area1.96%. The21627-probe finite-field scan shows no nominal parent-station loss, but C/A material ranges0.7794–1.2371; adverse overlaps are retained. A denser independent scan reveals narrow5mm-margin losses. Recommendation remains conditional, prioritizing strixel tiling/material studies; no C IdRes fit, resolution or efficiency improvement claimed. Both role documents explain engineering costs and remaining interfaces.

## Provenance and design state

Added SRC-CMS-OUTER-TRACKER-2018 as a public tilted-barrel engineering precedent with precise locations; no CMS dimensions/savings imported. New numerical recipe is unsigned NODD DESIGN CHOICE C07; areas and crossing results are derived inferences. DES-006 remains DRAFT/PROTOTYPE, with human review pending. No production geometry or sign-off changed. Dashboard and review records accompany the extension.

## Validation and corrections

Eighteen prototype,25dashboard and15logging/documentation tests passed. Initial dashboard/doc tests ran before the linked independent audit artifact existed; rerunning after generation passed. PhysVal's independent harness first needed forward-reach guards, then an explicit first-turn reach check when strict Newton convergence exposed unreachable targets. Those diagnostic corrections did not alter the shared solver. Final209952-query audit agrees; denser signed-eta and margin controls are retained with executable code.

C figures/PDF rendered with Matplotlib3.11.0/NumPy2.4.3; pdfinfo confirms2A4pages, both visually inspected. Dashboard validates/builds; retained input/code hashes match. Node unavailable in this local environment, so hosted CI handles browser tests. Publication and final session validation are recorded once observed.

## Traceability and limitations

Starting revision and branch, selected commands and changed paths are in the paired JSON. Token counts, client identity and conversation start timestamp are unavailable; no estimates recorded. Module masks, phi tiling, detailed stereo transforms, support/services, scattering fits and physical acceptance remain future work. The Noemi-directed comment remains untouched.

## Publication and review

Published d32da2541415f4730297601e0779594f08f5beaf on the existing PR #13 branch. Updated its executive summary and posted the technical response at https://github.com/asalzburger/nodd/pull/13#issuecomment-5732103962. The Noemi-directed comment was not answered or altered. Preserved the original review target and requested a superseding technical round at the exact C revision; no human approval recorded.

Hosted CI35361596731 succeeded on d32da25, including browser checks. Final local dashboard validation/build passed with28tasks,9documents,7reviewrounds;36sessionrecords validated. The remaining commit records publication and review metadata only.

## Token-accounting update — 2026-09-25

Imported 4 disjoint completed-turn entries already attributed to this session
in the retained `logs/usage/USAGE-2026-09-24-local.json` or
`USAGE-2026-09-25-device.json` inventory. Exact source and counters are in the
paired JSON. This supersedes earlier missing-usage wording for those turns;
no new raw client-state recovery or estimated attribution was performed.
