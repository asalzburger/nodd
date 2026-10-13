# SESSION-2026-10-13-layout-main-page — Current layout candidates and README entry point

## Scope and selected request

Human requests two PRs: a detailed SiW barrel prototype and a separate Markdown
layout main page accessible directly from README. The main page must list the
current candidate, show a clickable RZ view leading to concise features and
links to decisions/PRs, and be updated after approved layout-prototype changes
merge. This record covers the second bounded task. Starting main revision is
7c6d453fef12c3207b468c4fc99633fb393072a4, with no initial user changes in this
worktree. Source histories are supporting inputs; no combined native geometry
or performance validation is claimed.

## Candidate and approval boundaries

LAYOUT-001 represents the human-selected working candidate: maintained tracker,
proposed inner3T solenoid(PR64 open), SiW ECAL endcaps(PR70 open) and detailed
barrel(PR71 ready/open), rough steel/scintillator HCAL outline, no FCal and no
muon system or muon-system magnets. User selection does not grant engineering
sign-off. Geometry values are facts about pinned repository prototype inputs;
the combined drawing is an inference and the candidate choice is an unsigned
NODD design choice. Polygonal radii are sector-centre apothems.

## Implementation and maintenance

The bounded PubDoc writer authored disjoint page/drawing/workflow files under
an explicit generic role contract. Native profile loading is not claimed.
Root checked the handoff, supplied the observed PR71 ready/head/source links,
pinned the beam-pipe configuration and curated records. The README entry links
the candidate index and its clickable PNG. The feature page has one compact
parallel subsystem table. Named inputs retain16 exact source revisions/hashes
and69 tracker source matches; the diagram shows recorded sensitive group bounds,
both endcaps, magnet allocations and dashed HCAL envelopes on equal R/Z scales.
Detailed passive tracker services and ECAL gaps are omitted, explicitly labelled.

AGENTS and the PR template implement the user's future maintenance instruction:
update candidate features/status/links and regenerate geometry drawings in the
same change, with immediate post-merge reconciliation for final merge metadata.
No recurring task or automation was requested or created. No design lifecycle
was advanced. No additional software packages were adopted: standard-library
Python generates SVG; an already installed rsvg-convert renders PNG.

## Actual checks and limitations

PubDoc checked13 initial pinned source hashes,69 tracker inputs,33 local links
and assembly dimensions. Root's final audit checked16 pinned hashes,69 tracker
inputs and47 local Markdown links/images, after barrel/beam-pipe additions.
SVG XML parses and draw.py --check reproduces the exact retained SVG; the final
PNG was visually inspected with readable labels and no clipping. Project records
validate64 tasks,35 documents and21 review rounds. Final journal/token/whitespace
checks are recorded in the paired JSON after execution.

PR64 remains open at4e44d7c; PR70 remains open at654b85a. The barrel geometry
producer3d95e0b and strengthened validator abb836f are documented in PR71;
this page pins completed design/budget evidence19d20f8. The coordinator's first
publication command used a nonexistent remote alias 'upstream'; the configured
origin is asalzburger/nodd and the ordinary push there succeeded. No force push
or shared dependency modification occurred. Hosted checks are inspected on each
final pushed head; local checks do not imply combined-detector acceptance.

## Token accounting and follow-up

Exact root/child per-turn usage and client version/thread identity are not
exposed. Usage is empty/unknown; no duplicate observations or estimates are
introduced. Session summary distinguishes observed historical input/output sums
from missing current coverage. Further approved layout changes must reconcile
the page and source pins; detector engineering/performance work remains separate.

## Prepared bounded assignment

Explicit generic role assignment; native profile loading not claimed. Workflow instructions from main 7c6d453fef12c3207b468c4fc99633fb393072a4.

```json
{
  "id": "LAYOUT-PubDoc",
  "role": "PubDoc",
  "input_revision": "7c6d453fef12c3207b468c4fc99633fb393072a4",
  "inputs": [
    "README.md",
    "AGENTS.md",
    "docs/design/DES-025-tracker-dd4hep-gen3.md",
    "docs/design/DES-029-calorimeter-assemblies.md",
    "project/tracking.json"
  ],
  "mode": "write",
  "writable_paths": [
    "README.md",
    "AGENTS.md",
    ".github/pull_request_template.md",
    "docs/layouts/README.md",
    "docs/layouts/LAYOUT-001-tracker-3t-siw.md",
    "docs/layouts/LAYOUT-001.json",
    "docs/layouts/figures/LAYOUT-001-rz.svg",
    "docs/layouts/figures/LAYOUT-001-rz.png",
    "tools/layout_overview/draw.py"
  ],
  "task": "Create the separately requested concise Markdown main page of current layout candidates accessible prominently from root README. One human-selected candidate: current tracker, inner3T solenoid (open PR64), SiW ECAL endcap(open PR70) and forthcoming detailed SiW barrel(PR71 requested; coordinator provides final URL), HCAL rough outline only, no FCal or muon system/muon magnets yet. Main page shows clickable RZ preview linking to a very concise feature page with decision/DES/PR links. Show both +/-z, real envelope scales, tracker (prefer actual recorded sensitive planes), distinguish current component geometry from conditional planning outlines and absent systems. Read extra exact sources with git show: solenoid4e44d7c650ac0a2931f7fc1637b5b3f2dfbe4c95 and edge sensors5664d16aea2df36222dc0099ba18594cf506304d; cite their revisions. You may inspect source files needed to obtain original plotted tracker planes, but do not claim new simulation. Preserve open status and no engineering sign-off. No new dependencies or packages. Standard-library SVG is allowed for this engineering drawing, or existing matplotlib if present. Record named geometry inputs and reproducible draw command in LAYOUT-001.json. Add durable future main-page maintenance rule to AGENTS and a focused PR-template checkbox: update candidate page/view/links when approved changes are merged into a layout prototype; merger alone grants no engineering sign-off. Do not conflate inherited ODD full-detector geometry with this selected candidate or show absent systems. Work only in this worktree. Do not commit, push, create PR, message tasks or start other agents.",
  "deliverable": "Owned Markdown/overview inputs and reproducible RZ drawing plus concise cited handoff, changes and actual checks to coordinator. Coordinator owns logging/project records/PR creation and fills PR71 exact link.",
  "completion": "All owned files coherent, sources/revisions pinned and statuses accurate; generated SVG inspected structurally and PNG visually if renderer available, documentation links checked. Clearly report unavailable rendering or source data instead of inventing dimensions."
}
```

## Publication closeout

Page implementation committed asa234dc2140bd70c9d2b058d12b372853a7d650ea; branch codex/layout-main-page
pushed normally to asalzburger/nodd. [PR72](https://github.com/asalzburger/nodd/pull/72)
created against main and attached to the task. This record-only closeout adds
observed PR/source metadata without altering geometry/drawing inputs. Hosted
checks are verified after the final push. Local179 paired journals and token
Pages build pass;210 observations total624299405(input620754236,output3545169),
with61 records missing usage. This task adds no fabricated counters.
