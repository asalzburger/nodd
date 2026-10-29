# SESSION-2026-10-29-issue105-toroid-redesign

## Scope and selected request

The user requested handling new issue105, which quotes mgtmentink's expert
review and requests a separated short-barrel/long-endcap toroid redesign with
realistic field limits and a high-coverage three-station chamber suggestion.
This is a contemporaneous curated project record, not a raw chat export.

Initially inspected main04b5ee2e408803eac836eee0b48a1635dcbbe201. The existing
nodd checkout had unrelated changes and was preserved. Created a clean new
worktree, fetched current remote design heads, then switched to a new branch
based on PR90 mergecae3a72f3b1c98edaf9bc28a84d019142606ba25 to reuse its
field/energy tools. PR87 remains an unmerged parent; this change is stacked.

## Outcome and limitations

DES039/DES040 amendment: BT12m, ECT6m,0.8m complete warm axial gap; fixed
3T solenoid. New uniform pack and currents are recomputed with the joint vacuum
field and all-space self/mutual energy. Exterior3.5T is a screening diagnostic,
not a conductor peak certificate. Global vacuum30MJ/m3 closure is distinct
from installed nonlinear sizing and per-magnet engineering.

Three nested schematic station pairs improve geometric availability over
shortening every barrel chamber, but finite panels, seams/borders, frame,
services, coil-following ECT vessel and material transport remain open.
No3station cells survive eta3–3.5; the stretch target is not met. No lifecycle
state is advanced and no production geometry is changed.

## Specialist handoffs

Explicit generic-agent role instructions were prepared and read; native profile
loading is not claimed. /root/sysarch (I105-SysArch) independently checked PR87
fe372194038ed2af9617c27defffba09ae6d683f, PR90db88f594ab29a2a509b4308fdfddf14ffe5f822e,
PR9452922c71a58a4d799abeccc716a716fa2ba52521, and the updatedcae3 merge.
It recommended the12m/6m hosts, derived0.8m warm separation, and identified
S2-vessel, rear support, coil-force and HCAL/service interfaces.

/root/muontech (I105-MuonTech) checked the same revisions and identified
full-depth transition inequalities, orthogonal host separation, distinct-station
counting, finite-aperture stretch loss, and the need to repack actual chambers.
The coordinator selected wheel radii6.1/7.5/9m and lengths6.4456/10/13.8m
using those inequalities. The different schematic shell model cannot be directly
ranked against the historical936-panel results.

## Commands, controls and corrections

Read repository mandates, PROJECT, governing DES/ADR, issue and attachment.
Used nodd-coordinate, nodd-design-evidence, nodd-review-validation and PDF
reading skills. The public PDF downloaded directly after web retrieval failed;
pdfplumber extracted seven pages, with page2/6/7 visual inspection. Catalogue
includes source URL, hash and precise locators; ignored PDF is not committed.
Bundled PyMuPDF and matplotlib were unavailable; pdfplumber and deterministic
SVG plus existingrsvg-convert supplied reading and visualization without installs.

Plain network fetch failed DNS once; authorized sandbox escalation succeeded.
Two GitHub PR connector reads failed transport; local fetched full refs and the
successful PR94 read supplied exact source identities. No external messages sent.

Initial full-depth coil-free assertion failed aboveeta3.48 due the explicit0.4m
aperture; retained the aperture and reported stretch shortfall, then gated ideal
closure beloweta3 only. The old0.20x0.30 pack required more physical winding
volume than the low-current30MJ/m3 target; sizing-control.json retains this
rejected trial. A0.14x0.20 trial also failed cold containment. Selected0.12x0.18
pack after re-solving fields, currents and complete energy; no old matrix reused.
Added actual within-cassette ray-chord checks after normal-depth checks to avoid
false clear paths across depth. Final results are generated from that code.

Ran25 focused tests successfully, the full numerical study, SVG/PNG rendering
and visual inspection, project-record validation, agent-workflow validation,
session validation/summary, token-site validation/build and git diff --check.
Detailed commands and additional review checks remain in the paired JSON/report.
No native ACTS/DD4hep/Geant4 run was performed for the new schematic geometry.

## Usage and follow-up

No exact client per-turn input/output counters were exposed. usage is empty;
unknown counters are not zero. No hidden client stores were accessed and no
parent/child estimates were created. Session summary reports aggregate observed
repository usage separately; this task has no measured tokens.

Human magnet and muon/system review is required before production integration.
Resolve conductor-interior peak, NbTi operating margin, mechanical/thermal pack
allowance, installed nonlinear energy, vessel design, finite panels/frame/services
and signed-bending/material transport before performance claims.

## Specialist assignment contracts

{
  "id": "I105-SysArch",
  "role": "SysArch",
  "input_revision": "04b5ee2e408803eac836eee0b48a1635dcbbe201",
  "inputs": [
    "docs/design/DES-004-magnetic-configurations.md",
    "docs/decisions/ADR-006-global-envelope-and-field-hypotheses.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Assess issue 105 magnet redesign interfaces. Read latest unmerged toroid PR 87 branch codex/twelvefold-toroid-prototype (fe37219) and muon PR90/94 branches using git show, identify exact full revisions. Propose separated short barrel/long endcap toroid hosts and realistic field constraints, preserving 3T solenoid and calorimeter. Return dimensions and risks. Do not edit or delegate.",
  "deliverable": "Return cited technical proposal to coordinator; retain curated handoff in the issue105 session narrative.",
  "completion": "Report exact source revisions, findings, actual checks and limitations; no sign-off."
}

{
  "id": "I105-MuonTech",
  "role": "MuonTech",
  "input_revision": "04b5ee2e408803eac836eee0b48a1635dcbbe201",
  "inputs": [
    "docs/design/inputs/DES-004-muon.md",
    "docs/decisions/ADR-006-global-envelope-and-field-hypotheses.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Assess schematic chamber placements for issue105 separated short barrel and long endcap toroids. Read unmerged PR87/90/94 local branches with git show; identify full revisions. Propose three independent stations across barrel/transition/endcap, with eta/phi ray acceptance definitions, coil and service exclusions, and controls. Do not edit or delegate.",
  "deliverable": "Return cited technical proposal to coordinator; retain curated handoff in the issue105 session narrative.",
  "completion": "Report exact source revisions, findings, actual checks and limitations; no sign-off."
}
