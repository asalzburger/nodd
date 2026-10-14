# SESSION-2026-10-14-ecal-layout-review - Single reviewer entry for Si-W and LAr ECAL layouts

## Scope and evidence

Contemporaneous, bounded documentation task, starting from main
`e33ae62ce16592c26c581c5311c4dc493d9714b1`, with a clean dedicated worktree on
`codex/ecal-layout-review-entry`. The repository remains canonical. This task
adds a central reviewer overview of existing proposals; it changes no detector
geometry, response, reconstruction, dependencies or design lifecycle.

## Selected conversation

User request (verbatim):

> For both, the ECAL Si-W and LAr Layouts, make a single documentation PR that links and connects to the barrel / EC PRs and only summarizes the layout:
> - overall envelope viewing and drawing (the layout drawing in rz)
> - summary of the detector (including material, space and support budget)
> - concise description of EC and barrel (with links to the PR)
> - all in the description box of the PR (and separately as a 4 page pdf with identical content)
>
> This is a central entry for the reviewers, not (yet) a TDR

Coordinator interpretation: one documentation PR and four pages total cover both
candidates. A single structured source generates all prose, tables, captions and
public links into the PR description and PDF. Source snapshots retain the exact
main / component PR revisions; no open implementation stack is imported.

## Decisions and outcomes

- Page 1: common tracker/proposed inner 3 T coil and equal-scale RZ illustrations.
- Page 2: Si-W barrel/endcaps, explicit silicon/boards/cooling/support, model
  masses and coverage limits; links PR70/71 and pinned governing documents.
- Page 3: ALLEGRO-style LAr barrel/turbine endcaps, cryostat/cold support/service
  proxies and remaining service/cooling/forward issues; links PR73/74.
- Page 4: comparative material, envelope and space budgets; common pre-ECAL
  material examples, bounded reviewer decisions and source catalogue.

Masses are native model inventories, not installed engineering masses or
performance rankings. HCAL mass and solenoid support/mass remain unassigned;
reserved volumes do not claim routed services or FCal hardware. Separate tracker
and solenoid X0 examples are not a combined material map. Neither a merge nor
recorded native/sparse Geant4 execution supplies engineering or response sign-off.

Verified GitHub snapshot on 2026-10-14: PR64/70/71/73/74 open at their pinned heads;
PR69 and PR72 merged. Reconcile those two existing tracking records with observed
head/merge SHA and timestamps, preserving historical review evidence.

## Specialist handoffs

The repository coordination/evidence/review skills and PDF skill were applied.
Generic child contexts received explicit role instructions; native profile
loading is not claimed. Contract preparation precedes dispatch below.

- `ECAL-REVIEW-PubDoc-draft`, child `/root/layout_main_page`: authored only
  `brief.json` against source commit a53c29867130b4c36658a9aa5f6f14dd5650130f.
  Returned a concise four-page common source, public links and unsigned-state
  wording; schema/table/link/word-count checks passed. Its earlier SoftEng role
  was explicitly replaced by PubDoc. It is the author, not an independent reviewer.
- `ECAL-REVIEW-PhysVal-budget`, child `/root/lar_fit_physval`: read-only exact
  source review. Checked all nine initial hash bindings, primary mass/material
  sums, HCAL corner/envelope derivations, service/heat and coverage limitations.
  Returned corrected LAr both-end mass 131.173 t (the old 139.557 t value is
  superseded), tracker+Be inventory 2.860 t, and missing installed/HCAL budgets.
  An initial statement about a top-level Air inventory entry was withdrawn after
  exact primary-source inspection; no Air claim is retained. This child helped
  earlier LAr design work; that origin overlap is disclosed. No native jobs,
  edits, dependency installs or human sign-off were performed by this assignment.

Coordinator reconciled the facts, included the pinned solenoid material note as
source 10, and changed the endcap support shorthand to wheel support tubes.

## Commands and validation

- `tools/layout_review/draw.py`: regenerates two compact SVG/PNG envelope views
  from verbatim layout snapshots. Same axes/scales; polygon apothems and circular
  radii are distinguished in scope, not presented as a full geometry union.
- `tools/layout_review/build.py --font-dir <existing LiberationSans directory>`:
  existing bundled reportlab/pypdf/Pillow; exactly four PDF pages, 72 common
  text/table/caption blocks and 14 unique clickable links passed. No packages added.
- `build.py --check-sources --check`: all 10 pinned Git source SHA256 values and
  both verbatim layout snapshots matched; generated Markdown/PDF parity passed.
- Bundled Poppler `pdftoppm -scale-to 1500 -png ...`: all four pages rendered and
  visually inspected with no clipping, overlapping labels or missing glyphs.
- Initial relative links and non-ASCII hyphens in the draft were corrected in the
  common source before final generation. A JavaScript orchestration syntax error
  occurred before shell execution and was reissued; no artifact was lost.
- Initial sandboxed `gh pr view` requests could not access api.github.com;
  authorized read requests with network permission succeeded.
- `git diff --check`: passed. Documentation uses recorded component evidence;
  no detector/native/shower jobs were run in this task.

## Changes and revision links

The paired JSON holds the final file inventory and actual check results. Frozen
source snapshots were committed at a53c29867130b4c36658a9aa5f6f14dd5650130f.
Root README and layout index link the central entry; review tooling and source
catalogue preserve reproducibility. Project task TASK-PUB-ECAL-LAYOUT-REVIEW is
bounded publication work, not a new DES/ADR or detector approval.

## Token accounting

Current parent/child completed-turn token counters are not exposed to this task.
Usage remains empty and unknown. No cumulative total, subset or estimated count
is assigned. Existing observed project counters remain separate; session summary
and token-site build are required at closeout.

## Follow-up

Freeze the authored content, obtain a bounded exact-revision assessment, finish
journal/tracking validation, publish one documentation PR and verify its body
against the common-source Markdown. Human component/engineering decisions remain
with the component PRs; this summary grants no sign-off.

## Prepared ECAL-REVIEW-PubDoc-draft

```json
{
  "id": "ECAL-REVIEW-PubDoc-draft",
  "role": "PubDoc",
  "input_revision": "a53c29867130b4c36658a9aa5f6f14dd5650130f",
  "inputs": [
    "docs/layouts/review/layout001.json",
    "docs/layouts/review/layout002.json",
    "docs/layouts/review/sources.json"
  ],
  "mode": "write",
  "writable_paths": [
    "docs/layouts/review/brief.json"
  ],
  "task": "Prepare concise central reviewer entry for BOTH Si-W and LAr layouts, totalFOUR pages, not aTDR. Read AGENTS/PROJECT and yourPubDocprofile fully; priorSoftEngrole is replaced for this assignment. Author only brief.json using schema {title,date,subtitle,pages:[{title,blocks:[{type:\"paragraph\",text}, {type:\"heading\",text}, {type:\"table\",headers:[str],rows:[[str]]}, {type:\"figure\",path,alt,caption}]}]}. Markdown inline links allowed intext/tablecells; otheremphasis okay but avoid newsourcecitationsnotinrecord. Page1 concise sharedtracker/3Tcontext plusTWOcompact RZ figures (paths docs/layouts/review/figures/layout001-rz.png and layout002-rz.png), verylittletext (max100words, captions). Page2 SiW barrel/endcaps, material/support/coolingchoices andPR70/71links. Page3 LAr barrel/endcaps/material/support/services andPR73/74links. Page4 overallenvelopes/material/space/support budget comparison andboundedreviewpriorities/status/source links. Total~1000words target, pages2\u20134 max350words/tableequivalent each. Onlysummarize verifiedexisting designs; no geometry/recochanges,no newperformanceclaims/noapproval. Sourceinputlookup e33main layout001, SiW71head2776266 and70head654b85, LAr74head72d37/73head48e972, magnet64head4e44; exactfullrevs in sources.json. CurrentPRtitleson2026-10-14 are Si-WECALbarrelprototype/Si-WECALendcapprototype, LArECALbarrel andserviceinterfacesprototype/LArECALendcaps andlayoutprototype; allopen. Facts aboutunsignedchoicesvsqualifiedengineering separated; massesmodelonly, gapsallocations,forwardSiWseamsvsLAruncovered. PhysValindependentlygathersbudgetcorrections concurrently; incorporate root handoff. Root owns renderer/figures/logs/tracking/PR/PDF. No furtherdelegation/nativejobs/commits/push/PR. Return JSONready andexactsourceclaimreferences/remaininglimits.",
  "deliverable": "Common four-page structured content brief.json for identicalMarkdownPRbodyandPDF. ClearreviewerscopeandallfourcomponentPRlinks.",
  "completion": "Concisecoveragetablesandphysicalclaimsaretraceable; noTDRnarrative, no duplicatedversions, fourpagecontentstructure ready."
}
```

## Prepared ECAL-REVIEW-PhysVal-budget

```json
{
  "id": "ECAL-REVIEW-PhysVal-budget",
  "role": "PhysVal",
  "input_revision": "a53c29867130b4c36658a9aa5f6f14dd5650130f",
  "inputs": [
    "docs/layouts/review/layout001.json",
    "docs/layouts/review/layout002.json",
    "docs/layouts/review/sources.json",
    "docs/validation/DES-025/native.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Audit concise reviewer-entry budget facts for both existinglayouts, no designchange. Identify trustworthy commontracker/solenoid mass/material/supportvalues; collect ECALmass/material/support/space/heatbudgets frompinnedPR70/71/73/74primarydocs/reports (fullrevs insources.json). DeriveHCALmaxcylindricalcornerradius,totalaxialenvelopes andradial/axialservicegaps, distinguishapothemsvsradii. Clarifywhichquantitiesarecomparable, whichmassesaremodelproxies, absentHCALoverallmass, material-before-ECALsupport/infrastructurestatus, eta4/seam/transitionlimits. Four-pagetotal targetonlycentralreviewentry notTDR. Return compactcitedfacttable suitableforPubDoc; do not runnative/build/install/edit/newliterature/delegate/signoff. ExistingroleinstructionsscontinuebutpreviousLArdesign contribution acknowledged. Use gitshowexactprimarycommits; no dirtysource substitutions.",
  "deliverable": "Read-only budget/envelope/claim facttable and corrections withexactrevision/file/locators.",
  "completion": "Concretefacts/derivations/missingbudgetsidentified forbothlayouts without falseengineering/performanceapproval."
}
```
