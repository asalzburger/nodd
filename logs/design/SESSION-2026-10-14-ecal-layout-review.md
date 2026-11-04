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
- The first staged whitespace check treated the ReportLab PDF as text and
  reported PDF stream/xref whitespace. Mark the scoped PDF artifact as binary
  using `docs/layouts/review/.gitattributes`; do not rewrite binary PDF bytes.
- `git diff --check` for authored text passed. Documentation uses recorded component evidence;
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

Review PR75 and the linked component/engineering choices. Maintain the entry
after approved component changes merge. HCAL installed budgets, service routing,
thermal qualification and forward acceptance remain separate work; this summary
grants no sign-off.

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

## Prepared ECAL-REVIEW-PhysVal-final

```json
{
  "id": "ECAL-REVIEW-PhysVal-final",
  "role": "PhysVal",
  "input_revision": "b67b0fc2f611e0a0e93984199f92173ebd1ca0d1",
  "inputs": [
    "docs/layouts/review/brief.json",
    "docs/layouts/review/ecal-layout-review.md",
    "docs/layouts/review/ecal-layout-review.pdf",
    "docs/layouts/review/content-check.json",
    "docs/layouts/review/sources.json",
    "docs/layouts/review/layout001.json",
    "docs/layouts/review/layout002.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Review the frozen authored four-page reviewer overview of BOTH ECAL candidates for factual and scientific scope errors. Inspect primary inputs at the pinned source revisions before conclusions. Check material/support/envelope/space/heat and coverage claims in the final brief and Markdown against component DES/reports; review figures as envelope illustrations. Assess if the user-requested central entry connects both barrel/endcap PRs with clear limits and identical four-page PDF content. Use exact Git objects at assigned revision; no dirty substitutions, edits, native geometry jobs, installs or further delegation. Existing PhysVal profile instructions apply. Your earlier LAr contribution and budget assessment are disclosed; this final check is of PubDoc/root-authored documentation, not independent re-approval of your prior design work. Return findings with severity and exact file/source locators, actual checks, revision, limitations. Do not prescribe a conclusion or grant human approval.",
  "deliverable": "Bounded final claim/content review returned to coordinator and curated in session record.",
  "completion": "All material findings and missing evidence reported for the exact supplied snapshot; no silently changed design or approval."
}
```

## Publication checkpoint

PR75 created as a documentation-only draft against main:
https://github.com/asalzburger/nodd/pull/75, head
`512dca36d8467b401345ff78e9bf0c8d86aa4b06`. It is attached to the calling task;
PDF preview request queued in Codex. GitHub body is exactly equal (including final
newline) to retained Markdown: 8,984 characters. The PDF remains four pages with
72 matched text blocks and 14 public clickable links. Ordinary branch push;
no merge, force-push or new software dependency.

Regenerating both SVG/PNG views and the PDF from retained inputs produced no
artifact diff. PDF SHA256
`4d79bf9b111a86128fcb70321f872c5286e217572665998aac218574365939a8`;
Markdown SHA256
`fb31627f9270e9f968e451a819a25c87578a174ce629454d7db0fc1787bea057`.

Repository checks at this checkpoint: 65 tasks / 35 documents / 21 review rounds;
180 paired session records. Token-site build passed with 210 disjoint dated
turns and 624,299,405 observed tokens (620,754,236 input + 3,545,169 output).
Cached 599,210,880 input and 1,177,538 reasoning output are subsets, not added.
This current task has no exact completed-turn counters and contributes no invented
usage; session counts are coverage, not a complete lifetime token measurement.

### Artifact runtime

Existing bundled runtime: reportlab 4.4.9, pypdf 6.10.0, Pillow 12.3.0;
no installation. Embedded font files are LiberationSans-Regular.ttf
(SHA256 f8ace1f892b2bd9dc1792ba7f097fa7588f84fed48321480e04de5390828221f)
and LiberationSans-Bold.ttf
(SHA256 361c61b82d575c5c35fd9157fda8b0194bcfcd0d88ea8521a4fb5dd53d33dddc).
Font source is the existing bundled pdfjs-dist standard_fonts directory.

## Final claim review and correction

`ECAL-REVIEW-PhysVal-final`, `/root/lar_fit_physval`, read-only review of
`b67b0fc2f611e0a0e93984199f92173ebd1ca0d1`: no P1/P2 numerical or scope defect;
one P3 on overview line 36/PDF page 2 requested the sample basis of the 68.89%
endcap geometric coverage. Coordinator added 360 one-degree-centred azimuth
rays and the at-least-one-layer condition, matching pinned DES030 results.md.
This is a source clarification, not a new efficiency or acceptance claim.

Reviewer checks: four PDF pages, all 72 text blocks/14 links, exact Markdown
rendering, matching retained source/renderer/figure hashes and both embedded PNG
pixel arrays; all 10 primary Git source hashes; ECAL mass sums, polygon corner
radii/full axial lengths and 1.7743 HCAL outline-volume ratio recalculated.
Existing four rendered page previews were inspected. No native jobs, edits or
human approval. Earlier LAr author involvement remains explicitly disclosed.

## Prepared ECAL-REVIEW-PhysVal-P3

```json
{
  "id": "ECAL-REVIEW-PhysVal-P3",
  "role": "PhysVal",
  "input_revision": "e7ab36eb660b83e91d42356b915e22c33c81c071",
  "inputs": [
    "docs/layouts/review/brief.json",
    "docs/layouts/review/ecal-layout-review.md",
    "docs/layouts/review/ecal-layout-review.pdf",
    "docs/layouts/review/content-check.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Check only the P3 sample-basis clarification introduced after your final review of b67b0fc2f611e0a0e93984199f92173ebd1ca0d1. Compare the frozen page-2 paragraph with pinned DES030 results.md at654b85a48abeb38735ad7fe0866c5d1082882df7, and verify regenerated Markdown/PDF still correspond. Do not repeat the full source audit. Read-only exact Git objects; no edits, installs, native jobs or delegation. Return the actual correction assessment, reviewed revision and any remaining material finding; no human sign-off.",
  "deliverable": "Narrow closure or remaining finding for P3 against this new exact revision, returned for the session record.",
  "completion": "Sample basis and at-least-one-layer condition assessed against the same source; regenerated four-page common content checked."
}
```

## Closeout

`ECAL-REVIEW-PhysVal-P3` reviewed
`e7ab36eb660b83e91d42356b915e22c33c81c071`: the added 360-ray sampling basis and
at-least-one-layer condition match DES030; P3 is addressed with no remaining
finding in the narrow scope. Reviewer verified the corrected PDF sentence on
page 2, four pages, all 72 text blocks / 14 links, exact Markdown correspondence
and retained hashes; updated page 2 visually fits. Coordinator rendered and
inspected all four latest pages after correction. No new physics run or sign-off.

Final common content: PDF SHA256
`624ff5f20163b25d7f1d8b5417f6d6f6a21450edc8e1d36005d9f02a08618718`,
Markdown SHA256
`faed177c9f629f67e52d4ad972d1193b25343e25b5062e5d330c8567d346f98a`.
The PR description is updated from the corrected Markdown; PR75 is marked ready
for review. Retained source/rendering checks and paired journal/project checks
pass. GitHub CI results are read from the PR after the final ordinary branch
push; pending checks are not preclaimed here. The documentation completion state
covers this bounded deliverable, not implementation merge or detector acceptance.

### Closeout-format correction

Initial closeout journal validation rejected two PASS entries without observed
zero exit codes: subagent assessments have no shell exit code. Retain those role
results in the narrative/activity evidence and remove them from command checks.
The first publication of this metadata correction happened despite the error
because the shell block continued; preserve that ordinary Git history. Standalone
validator then reproduced exit 1. Token-site building in that block also stopped
on the invalid journal. Correct the schema rather than fabricate exit codes, then
rerun paired-session validation, token summary/site build and project checks.

Correction verified: paired-session validator exit 0 (180 records), token-site
build exit 0 (210 disjoint dated turns, 624,299,405 observed tokens), project
validator exit 0 (65 tasks / 35 documents / 21 review rounds), and whitespace
check exit 0. Session summary has 118 records with observations / 62 without;
this task stays unknown. The final correction changes only the curated journal;
reviewed PDF/content bytes and detector sources are unchanged.
